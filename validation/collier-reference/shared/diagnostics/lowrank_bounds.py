"""Diagnose the retained generic low-rank call with a checked upstream object.

No accepted integral result or performance evidence is produced.  The original
COLLIER library and all original source files remain unchanged.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time


ROOT = Path.cwd()
HERE = ROOT / "validation/collier-reference/shared"
SPEC = importlib.util.spec_from_file_location("collier_shared_support", HERE / "support.py")
support = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(support)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def bounded(command, *, cwd, log, timeout, input_bytes=None):
    started = time.monotonic()
    with log.open("wb") as stream:
        child = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
                                 stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            child.communicate(input_bytes, timeout=timeout)
            status = "exited"
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.communicate()
            status = "timeout"
    return {"command": command, "status": status, "exit_code": child.returncode,
            "elapsed_seconds": time.monotonic() - started, "cap_seconds": timeout,
            "log_sha256": digest(log)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cpu", type=int, default=26)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "target") or args.cpu not in os.sched_getaffinity(0):
        parser.error("new project target directory and available CPU required")
    original_path = ROOT / "validation/collier-reference/ready-initial8-v3/build.json"
    original = json.loads(original_path.read_text())
    library = ROOT / original["library"]["path"]
    if digest(library) != original["library"]["sha256"]:
        raise ValueError("immutable COLLIER archive differs")
    upstream = ROOT / "target/reference/collier/source/collier-COLLIER-1.2.10/src/collier_tensors.F90"
    driver = HERE / "attempt002/producer/driver.f90"
    input_path = ROOT / "target/collier-reference/shared-inputs-attempt001/inputs.json"
    inputs = support.load_document(input_path)
    case = next(c for c in inputs["cases"] if c["id"] == "n6-r0-conditioned-cycle32")
    request = support.collier_request(case, case["samples"][:1], 1) + "QUIT\n"
    sources = [Path(__file__).resolve(), HERE / "support.py", ROOT / "validation/collier-reference/run.py",
               ROOT / "validation/benchmark/run.py", original_path, library, upstream, driver, input_path,
               *sorted((library.parent / "modules").glob("*.mod"))]
    guards = {str(p.relative_to(ROOT)): digest(p) for p in sources}
    output.mkdir(parents=True)
    private = output / "source"
    private.mkdir()
    shutil.copyfile(upstream, private / upstream.name)
    shutil.copyfile(driver, private / driver.name)
    (output / "request.txt").write_text(request)
    record = {"kind": "collier-lowrank-bounds-diagnostic", "performance_evidence": False,
              "accepted_integral_evidence": False, "library_rebuilt": False,
              "library_modified": False, "cpu": args.cpu, "guards": guards,
              "case_id": case["id"], "batch_width": 1, "mode": 1,
              "initialization_capacity": 0, "requested_rank": 0,
              "request_sha256": digest(output / "request.txt"),
              "compile_link_cap_seconds": 60, "execution_cap_seconds": 20,
              "status": "running", "stages": []}
    receipt = output / "receipt.json"
    save(receipt, record)
    previous = os.sched_getaffinity(0)
    try:
        os.sched_setaffinity(0, {args.cpu})
        compiler = original["compiler_path"]
        flags = original["requested_flags"]
        modules = library.parent / "modules"
        checked_object = output / "checked-collier-tensors.o"
        binary = output / "lowrank-bounds"
        started = time.monotonic()
        commands = [
            [compiler, *flags, "-fcheck=bounds", "-g", "-I", str(modules), "-J", str(private),
             "-c", str(private / upstream.name), "-o", str(checked_object)],
            [compiler, *flags, "-I", str(modules), str(private / driver.name), str(checked_object),
             str(library), "-o", str(binary)],
        ]
        for index, command in enumerate(commands):
            remaining = 60 - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError("fixed compile/link cap exhausted")
            stage = bounded(command, cwd=private, log=output / f"build-{index}.log", timeout=remaining)
            record["stages"].append(stage)
            save(receipt, record)
            if stage["status"] != "exited" or stage["exit_code"] != 0:
                raise RuntimeError("checked-object compile/link did not complete successfully")
        record["binary_sha256"] = digest(binary)
        stage = bounded([str(binary)], cwd=output, log=output / "execution.log", timeout=20,
                        input_bytes=request.encode())
        record["stages"].append(stage)
        log = (output / "execution.log").read_text(errors="replace")
        record["observed_binomtable_bounds_trap"] = (stage["exit_code"] != 0
            and "binomtable" in log.lower() and "above upper bound" in log.lower())
        record["result_lines"] = sum(line.startswith("RESULT ") for line in log.splitlines())
        record["status"] = "diagnostic-complete"
    except Exception as error:
        record.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        os.sched_setaffinity(0, previous)
        record["guards_unchanged"] = all(digest(ROOT / p) == sha for p, sha in guards.items())
        if not record["guards_unchanged"]:
            record.update(status="failed", error="source/library/input guard changed")
        save(receipt, record)
    print(receipt)
    if record["status"] != "diagnostic-complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
