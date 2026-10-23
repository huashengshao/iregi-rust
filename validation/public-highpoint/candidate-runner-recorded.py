"""Run one bounded public probe after acquiring ROOT's Symbolica runtime lease."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import signal
import subprocess
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("n", type=int, choices=[6, 7])
    parser.add_argument("--rank", type=int, default=7, choices=range(8))
    parser.add_argument("--algorithm", default="pv", choices=["ibp", "pv", "hybrid"])
    parser.add_argument("--working-bits", type=int, default=128, choices=[128, 256, 384])
    parser.add_argument("--requested-bits", type=int, default=53)
    parser.add_argument("--rows", type=int, default=1, choices=[1, 2, 3])
    parser.add_argument("--limit", type=float, required=True)
    parser.add_argument("--variant", default="baseline", choices=["baseline", "candidate"])
    args = parser.parse_args()
    if not args.name.replace("-", "").replace("_", "").isalnum() or not 0 < args.limit <= 600:
        parser.error("name must be alphanumeric; timeout must be positive and at most 600 seconds")
    root = Path.cwd()
    here = root / "validation/public-highpoint"
    build_path = here / ("build.json" if args.variant == "baseline" else "candidate-build.json")
    build = json.loads(build_path.read_text())
    assert build["status"] == "passed"
    binary = root / ("target/public-highpoint/highpoint_public" if args.variant == "baseline"
                     else "target/public-highpoint/candidate/highpoint_public")
    source = root / "crates/iregi-rust/examples/highpoint_public.rs"
    fixture = here / "fixture-conditioned_masses.json"
    output = here / (args.name + ".json")
    log = here / (args.name + ".log")
    manifest_path = here / (args.name + "-run.json")
    assert not any(p.exists() for p in [output, log, manifest_path]), "Use a distinct evidence name"
    assert sha(binary) == build["binary_sha256"]
    assert sha(source) == build["source_sha256"]
    frozen_sources = {}
    if args.variant == "candidate":
        snapshot = root / build["frozen_core_source"]
        for path, expected in build["library_source_hashes"].items():
            frozen = snapshot / Path(path).relative_to("crates/iregi-rust")
            assert sha(frozen) == expected
            frozen_sources[frozen] = expected
    command = ["taskset", "-c", "0", str(binary), str(fixture.relative_to(root)), str(args.n),
               str(args.rank), args.algorithm, str(args.working_bits), str(args.requested_bits),
               str(args.rows), str(output.relative_to(root))]
    env = os.environ.copy()
    env["IREGI_PV_PREPARATION_PROFILE"] = "1"
    profile_environment = {"IREGI_PV_PREPARATION_PROFILE": "1"}
    if args.variant == "candidate":
        env["IREGI_PREPARATION_PROFILE"] = "1"
        profile_environment["IREGI_PREPARATION_PROFILE"] = "1"
    record = {"schema_version": 1, "status": "started", "started_utc": datetime.now(timezone.utc).isoformat(),
              "command": command, "timeout_seconds": args.limit, "binary_sha256": sha(binary),
              "fixture_sha256": sha(fixture), "build_manifest_sha256": sha(build_path),
              "probe_source_sha256": sha(source), "runner_source_sha256": sha(Path(__file__)),
              "variant": args.variant, "environment_additions": profile_environment,
              "timing_status": "diagnostic only; not an optimized controlled performance comparison"}
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
    record["frozen_source_files_unchanged"] = len(frozen_sources)
    if output.exists():
        record["result_sha256"] = sha(output)
        record["last_public_stage"] = json.loads(output.read_text())["status"]
    else:
        record["last_public_stage"] = "no_ledger_written"
    manifest_path.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2), flush=True)


if __name__ == "__main__":
    main()
