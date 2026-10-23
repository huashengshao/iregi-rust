"""Bound a full public reduction of the separately frozen collector candidate."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import resource
import signal
import subprocess
import time


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu", type=int, default=0)
    parser.add_argument("name")
    parser.add_argument("n", type=int, choices=[6, 7])
    parser.add_argument("--rank", type=int, default=7, choices=range(8))
    parser.add_argument("--algorithm", default="pv", choices=["ibp", "pv", "hybrid"])
    parser.add_argument("--working-bits", type=int, default=128, choices=[128, 256, 384])
    parser.add_argument("--requested-bits", type=int, default=53)
    parser.add_argument("--rows", type=int, default=1, choices=[1, 2, 3])
    parser.add_argument("--limit", type=float, required=True)
    parser.add_argument("--variant", default="use-dedup-full", choices=["use-dedup-full"])
    args = parser.parse_args()
    if not args.name.replace("-", "").replace("_", "").isalnum() or not 0 < args.limit <= 600:
        parser.error("name must be alphanumeric; timeout must be positive and at most 600 seconds")
    root = Path.cwd()
    here = root / "validation/public-highpoint"
    build_path = here / "use-dedup-full-build.json"
    build = json.loads(build_path.read_text())
    assert build["status"] == "passed"
    binary = root / build["binary_path"]
    source = root / build["frozen_source_root"] / "crates/iregi-rust/examples/highpoint_public.rs"
    fixture = here / "fixture-conditioned_masses.json"
    output = here / (args.name + ".json")
    log = here / (args.name + ".log")
    manifest_path = here / (args.name + "-run.json")
    assert not any(p.exists() for p in [output, log, manifest_path]), "Use a distinct evidence name"
    assert sha(binary) == build["binary_sha256"]
    assert sha(source) == build["frozen_source_hashes"]["crates/iregi-rust/examples/highpoint_public.rs"]
    semantic_path = here / "use-dedup-full-tests-qualification.json"
    semantic = json.loads(semantic_path.read_text())
    assert semantic["status"] == "passed" and semantic["build_manifest_sha256"] == sha(build_path)
    frozen_sources = {}
    if args.variant != "baseline":
        snapshot = root / build["frozen_source_root"]
        for path, expected in build["frozen_source_hashes"].items():
            frozen = snapshot / path
            assert sha(frozen) == expected
            frozen_sources[frozen] = expected
    command = ["taskset", "-c", str(args.cpu), str(binary), str(fixture.relative_to(root)), str(args.n),
               str(args.rank), args.algorithm, str(args.working_bits), str(args.requested_bits),
               str(args.rows), str(output.relative_to(root))]
    env = os.environ.copy()
    env["IREGI_PV_PREPARATION_PROFILE"] = "1"
    env["RAYON_NUM_THREADS"] = "1"
    profile_environment = {"IREGI_PV_PREPARATION_PROFILE": "1", "RAYON_NUM_THREADS": "1"}
    if args.variant != "baseline":
        env["IREGI_PREPARATION_PROFILE"] = "1"
        profile_environment["IREGI_PREPARATION_PROFILE"] = "1"
    removed_environment = ["IREGI_ALIAS_USE_VERIFY", "IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE", "IREGI_MASTER_AMPLITUDE_MODE"]
    for name in removed_environment:
        env.pop(name, None)
    record = {"schema_version": 1, "status": "started", "started_utc": datetime.now(timezone.utc).isoformat(),
              "command": command, "timeout_seconds": args.limit, "binary_sha256": sha(binary),
              "fixture_sha256": sha(fixture), "build_manifest_sha256": sha(build_path),
              "probe_source_sha256": sha(source), "runner_source_sha256": sha(Path(__file__)),
              "variant": args.variant, "environment_additions": profile_environment,
              "environment_removals": removed_environment, "semantic_qualification_sha256": sha(semantic_path),
              "timing_status": "diagnostic only; not an optimized controlled performance comparison",
              "license_scope": "Private user-supplied Symbolica license; license contents excluded from evidence. CPU affinity and RAYON_NUM_THREADS=1 retained."}
    manifest_path.write_text(json.dumps(record, indent=2) + "\n")
    start = time.monotonic()
    with log.open("wb") as stream:
        child = subprocess.Popen(command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        try:
            status = child.wait(timeout=args.limit)
            record["status"] = "completed"
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            status = child.wait()
            record["status"] = "timeout"
    record.update(exit_code=status, elapsed_seconds=time.monotonic()-start, log_sha256=sha(log),
                  finished_utc=datetime.now(timezone.utc).isoformat())
    assert sha(binary) == record["binary_sha256"]
    assert sha(fixture) == record["fixture_sha256"]
    assert sha(source) == record["probe_source_sha256"]
    assert sha(Path(__file__)) == record["runner_source_sha256"]
    assert all(sha(path) == expected for path, expected in frozen_sources.items())
    assert sha(build_path) == record["build_manifest_sha256"]
    assert sha(semantic_path) == record["semantic_qualification_sha256"]
    record["numerical_reduction_entered"] = False
    record["scope"] = "Full ordinary public reduction candidate; result status and complete successful lane arrays determine numerical coverage. No controlled performance claim."
    record["peak_child_rss_kib"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    record["frozen_source_files_unchanged"] = len(frozen_sources)
    if output.exists():
        record["result_sha256"] = sha(output)
        ledger = json.loads(output.read_text())
        record["last_public_stage"] = ledger["status"]
        record["numerical_reduction_entered"] = ledger["status"] in ["reducing", "all_lanes_success", "lanes_rejected"]
    else:
        record["last_public_stage"] = "no_ledger_written"
    manifest_path.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2), flush=True)


if __name__ == "__main__":
    main()
