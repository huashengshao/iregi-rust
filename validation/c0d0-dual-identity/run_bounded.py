"""Source-only supervisor: exact reviewed lifecycle; ROOT runtime lease required."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import time
import traceback


HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
LIFECYCLE_SHA256 = "c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, document):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n")
    temporary.replace(path)


def main():
    entered = time.monotonic()
    parser = argparse.ArgumentParser()
    parser.add_argument("family", choices=("C0", "D0"))
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    if not args.attempt.isalnum():
        raise ValueError("Attempt name must be alphanumeric")
    if Path.cwd().resolve() != REPO:
        raise ValueError("Run from the project directory")

    # Load precisely the reviewed stdlib-only helper even under Python -I.
    helper = HERE / "lifecycle.py"
    if digest(helper) != LIFECYCLE_SHA256:
        raise RuntimeError("Reviewed lifecycle helper changed")
    spec = importlib.util.spec_from_file_location("c0d0_reviewed_lifecycle", helper)
    lifecycle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lifecycle)

    config = json.loads((HERE / "inputs.json").read_text())
    manifest_path = HERE / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    directory = HERE / args.attempt / args.family
    directory.mkdir(parents=True, exist_ok=False)
    output = directory / "results.json"
    summary = directory / "capture.json"
    terminal_path = directory / "process-terminal.json"
    logpath = directory / "runtime.log"
    work_bound = config["families"][args.family]["wall_bound_seconds"]
    total_bound = work_bound + 20
    if (work_bound, total_bound) != ((180, 200) if args.family == "C0" else (360, 380)):
        raise RuntimeError("Unexpected family bound")
    budget = lifecycle.Budget(total_bound)
    # Keep the reviewed helper byte-for-byte unchanged. Its public deadline
    # attributes permit the larger explicit cleanup/bookkeeping reserve here.
    budget.started = entered
    budget.deadline = entered + total_bound
    budget.work_deadline = budget.deadline - 20
    command = ["taskset", "-c", "0", str(REPO / manifest["venv"] / "bin/python"),
               "-I", str(HERE / "probe.py"), args.family, "--output", str(output)]
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    for key in ("IREGI_DUAL_CASE_FILTER", "IREGI_DUAL_SKIP_CASE"):
        environment.pop(key, None)
    environment.update(PYTHONNOUSERSITE="1", RAYON_NUM_THREADS="1", OMP_NUM_THREADS="1",
                       OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", RUST_MIN_STACK="67108864")
    bindings = {REPO / name: expected for name, expected in manifest["guarded_files_sha256"].items()}
    bindings[REPO / manifest["installed_native"]] = manifest["installed_native_sha256"]
    bindings[manifest_path] = digest(manifest_path)
    record = {
        "command": command, "cwd": str(REPO), "family": args.family,
        "work_bound_seconds": work_bound, "total_bound_seconds": total_bound,
        "cleanup_and_bookkeeping_reserve_seconds": 20,
        "status": "preparing", "passed": False, "cleanup_errors": [],
        "manifest_sha256": bindings[manifest_path], "lifecycle_sha256": LIFECYCLE_SHA256,
        "numerical_evidence": str(output.relative_to(REPO)),
        "guarded_inputs": {str(path.relative_to(REPO)): expected for path, expected in bindings.items()},
        "environment": {key: environment.get(key) for key in (
            "PYTHONPATH", "PYTHONNOUSERSITE", "RAYON_NUM_THREADS", "OMP_NUM_THREADS",
            "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "RUST_MIN_STACK",
            "IREGI_DUAL_CASE_FILTER", "IREGI_DUAL_SKIP_CASE")},
    }
    save(summary, record)

    def verify(stage):
        checks = {}
        record[stage] = checks
        for path, expected in bindings.items():
            if stage == "guards_before":
                budget.remaining()
            elif time.monotonic() >= budget.deadline:
                raise TimeoutError("Total budget exhausted during post-run guards")
            key = str(path.relative_to(REPO))
            try:
                actual = digest(path)
                checks[key] = {"actual": actual, "expected": expected, "match": actual == expected}
            except Exception as error:
                checks[key] = {"expected": expected, "match": False, "error": repr(error)}
        return len(checks) == len(bindings) and all(check["match"] for check in checks.values())

    def persist_process(result):
        # execute() calls this from its finally after whole-process-group
        # cleanup. Persist terminal state before any post-run reads or hashes.
        record["process"] = dict(result)
        if result["status"] in ("exited", "failed"):
            record["status"] = "terminal_awaiting_guards"
            save(terminal_path, {"process": result, "cleanup_errors": record["cleanup_errors"],
                                 "elapsed_seconds": budget.elapsed()})
        else:
            record["status"] = result["status"]
        save(summary, record)

    print(json.dumps({"phase": "start", "family": args.family,
                      "work_bound_seconds": work_bound, "total_bound_seconds": total_bound}), flush=True)
    budget.arm()
    try:
        record["pre_run_unchanged"] = verify("guards_before")
        save(summary, record)
        if not record["pre_run_unchanged"]:
            raise RuntimeError("Frozen historical wheel/source inputs changed before execution")
        lifecycle.execute(command, logpath, budget, work_bound, record["cleanup_errors"],
                          persist_process, environment)
    except BaseException as error:
        record["capture_error"] = {"phase": "execution", "type": type(error).__name__,
                                   "message": str(error), "traceback": traceback.format_exc()}
    finally:
        # execute() has already cleaned its owned group even if cancellation
        # interrupted the leader, or the leader exited before its descendants.
        # Stop the work alarm; reserve the last20s for guards and evidence.
        signal.setitimer(signal.ITIMER_REAL, 0)
        record["status"] = "terminal_awaiting_guards"
        record["elapsed_seconds"] = budget.elapsed()
        if not terminal_path.exists():
            save(terminal_path, {"status": "not_launched_or_terminal_capture_failed",
                                 "process": record.get("process"),
                                 "capture_error": record.get("capture_error"),
                                 "elapsed_seconds": budget.elapsed()})
        save(summary, record)

    # Keep post-run hashing bounded even after a work-deadline cancellation.
    # TERM/INT are deferred during this final accounting stage; an aggregate
    # deadline interrupts it and the already-saved terminal remains durable.
    def defer(number, frame):
        budget.cancelled = "cancelled by signal " + str(number) + " during final accounting"

    def deadline(number, frame):
        budget.cancelled = "aggregate deadline during final accounting"
        raise TimeoutError(budget.cancelled)

    for number in (signal.SIGTERM, signal.SIGINT):
        signal.signal(number, defer)
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, max(0.001, budget.deadline - time.monotonic()))
    try:
        record["post_run_unchanged"] = verify("guards_after")
        save(summary, record)
        if output.exists():
            evidence = json.loads(output.read_text())
            record["probe_status"] = evidence.get("status")
            record["probe_complete"] = evidence.get("complete", False)
            record["probe_passed"] = evidence.get("passed", False)
            record["counts"] = evidence.get("counts")
            record["last_event"] = (evidence.get("events") or [None])[-1]
        record["evidence_sha256"] = {
            path.name: digest(path) for path in (output, logpath, terminal_path) if path.exists()
        }
    except BaseException as error:
        record["final_accounting_error"] = {"type": type(error).__name__,
                                            "message": str(error), "traceback": traceback.format_exc()}
    # The final admission boundary is the pending-signal/deadline check after
    # the atomic summary save. Block the three relevant signals only across
    # that commit, so cancellation cannot race a previously computed pass.
    # The aggregate alarm remains armed until the post-save check finishes.
    admission_signals = {signal.SIGTERM, signal.SIGINT, signal.SIGALRM}
    previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, admission_signals)
    try:
        process = record.get("process", {})
        candidate_pass = (
            process.get("status") == "exited" and process.get("returncode") == 0
            and process.get("owned_group_gone") is True and not process.get("timeout", False)
            and record.get("pre_run_unchanged") is True and record.get("post_run_unchanged") is True
            and record.get("probe_complete") is True and record.get("probe_passed") is True
            and record.get("probe_status") == "passed" and not record["cleanup_errors"]
            and "capture_error" not in record and "final_accounting_error" not in record
        )

        def admission():
            record["elapsed_seconds"] = budget.elapsed()
            record["deadline_exceeded"] = record["elapsed_seconds"] > total_bound
            record["cancellation"] = budget.cancelled
            record["pending_admission_signals"] = sorted(
                int(number) for number in signal.sigpending() & admission_signals
            )
            return bool(candidate_pass and not record["deadline_exceeded"]
                        and not budget.cancelled and not record["pending_admission_signals"])

        record["admission_boundary"] = "Pending signals and total elapsed time checked again after this atomic save"
        record["passed"] = admission()
        record["status"] = "passed" if record["passed"] else "failed"
        save(summary, record)
        # A signal or deadline during the save revokes the provisional pass.
        # The successful qualification ends exactly at this protected check;
        # no evidence read, hash, save, or reporting remains on its pass path.
        final_pass = admission()
        if not final_pass:
            record["passed"] = False
            record["status"] = "failed"
            save(summary, record)
    finally:
        budget.disarm()
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
    return 0 if final_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
