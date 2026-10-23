#!/usr/bin/env python3
"""Bounded, provenance-pinned isolated supplied-G diagnostic/precision probe."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parent
ORACLE_SHA256 = "a821a4b523245bc4c7d3c01de486cc9197b6f8d4444a2eb3069b626dc0ff17c4"


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def checked_oracle():
    path = ROOT / "independent-n6/result.json"
    assert digest(path) == ORACLE_SHA256, "independent oracle changed; review required"
    oracle = json.loads(path.read_text())
    expected = {
        "shifts": [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0],
                   [0, 0, 1, 0], [0, 0, 0, 1], [1, 1, 1, 1]],
        "mass_squared": [30, 31, 32, 33, 34, 35],
        "mu": 3, "mu_squared": 9, "powers": [1] * 6,
        "dimension_shift": 0, "rank": 0, "metric": "+---",
        "normalization_scale_squared": 35, "normalization_factor": 1_500_625,
        "native_laurent_order": ["UV single", "IR single", "IR double", "finite"],
    }
    for key, value in expected.items():
        assert oracle["input"][key] == value, f"oracle fixture mismatch: {key}"
    assert oracle["status"] == "estimated_converged"
    assert oracle["integrand_oneloop"] == "6/F^4"
    value = oracle["comparison"]["oneloop_finite"]
    uncertainty = oracle["comparison"]["estimated_uncertainty_oneloop"]
    assert math.isfinite(value) and value > 0
    assert math.isfinite(uncertainty) and 0 < uncertainty < 1e-19
    for key, filename in [("input_sha256", "input.json"), ("script_sha256", "oracle.py")]:
        assert digest(ROOT / "independent-n6" / filename) == oracle["provenance"][key]
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("variant", choices=["alias", "vector"])
    parser.add_argument("kind", choices=["status", "float"])
    parser.add_argument("--limit", type=int, required=True)
    args = parser.parse_args()
    assert re.fullmatch(r"[a-zA-Z0-9_]+", args.name)
    assert 1 <= args.limit <= 600
    build = json.loads((ROOT / f"{args.variant}-probe-build.json").read_text())
    binary = ROOT / f"{args.variant}-probe-tests"
    assert build["code"] == 0 and build["archives_unchanged"]
    assert digest(binary) == build["binary_sha256"]
    source = ROOT / f"{args.variant}-probe-source"
    assert all(digest(source / name) == checksum for name, checksum in build["source_files"].items())
    suffix = "binary64_status_before_comparator" if args.kind == "status" else "float_converges_and_matches_parameter_integral"
    command = [str(binary), f"public_precision_probe::public_certified_n6_{suffix}",
               "--exact", "--nocapture", "--test-threads=1"]
    env = os.environ.copy()
    env["IREGI_PREPARATION_PROFILE"] = "1"
    record = {"variant": args.variant, "kind": args.kind, "command": command,
              "binary_sha256": build["binary_sha256"], "timeout_seconds": args.limit,
              "scope": "Binary64 status-only diagnostic; Float verifies independent oracle and convergence. No performance qualification."}
    if args.kind == "float":
        oracle = checked_oracle()
        env["IREGI_N6_PARAMETER_ORACLE"] = str(oracle)
        record.update(oracle=str(oracle), oracle_sha256=ORACLE_SHA256,
                      working_bits=[128, 256], requested_accuracy_bits=53)
    destination = ROOT / "runs" / args.name
    assert not destination.with_suffix(".json").exists(), "preserve previous evidence"
    started = time.monotonic()
    with destination.with_suffix(".log").open("w") as log:
        try:
            result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT,
                                    timeout=args.limit)
            record.update(code=result.returncode, status="passed" if result.returncode == 0 else "failed")
        except subprocess.TimeoutExpired:
            record.update(code=124, status="timed_out")
    record["elapsed_seconds"] = time.monotonic() - started
    text = destination.with_suffix(".log").read_text()
    record["log_sha256"] = digest(destination.with_suffix(".log"))
    record["events"] = [json.loads(line.split("PROBE_RECORD ", 1)[1])
                        for line in text.splitlines() if "PROBE_RECORD " in line]
    if record["status"] == "passed" and "1 passed;" not in text:
        record["status"] = "invalid_no_test_count"
    destination.with_suffix(".json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    print(text[-4000:])
    raise SystemExit(record["code"] if record["status"] != "invalid_no_test_count" else 2)


if __name__ == "__main__":
    main()
