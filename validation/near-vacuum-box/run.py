#!/usr/bin/env python3
"""Bounded validation-only runs. Numerical use requires the ROOT runtime lease."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = [
    "target/near-vacuum-validation/stage1-source/near_vacuum_validate.rs",
    "target/near-vacuum-validation/stage1-source/support/near_vacuum_box.rs",
    "target/near-vacuum-validation/stage1-source/support/d0_near_vacuum_oracle.rs",
    "docs/research/near-vacuum-box-plan.md",
]
ARCHIVES = [
    "target/d0-node-probe/liboneloop_baseline.rlib",
    "target/d0-node-probe/deps/libsymbolica-5cca42ee48491872.rlib",
    "target/d0-node-probe/deps/libserde_json-6ed7d47d62d32cd7.rlib",
]
BINARY = "target/near-vacuum-validation/near_vacuum_validate"


def sha(path):
    digest = hashlib.sha256()
    with (ROOT / path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("order", choices=["2", "4"])
    parser.add_argument("shape", choices=["primal", "mixed"])
    parser.add_argument("numeric", choices=["f64", "dd", "float128", "float256"])
    parser.add_argument("bits", type=int)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--label")
    parser.add_argument("--variant", default="stage1")
    parser.add_argument("--cpu", type=int, default=0)
    args = parser.parse_args()
    if not args.variant.replace("_", "").isalnum():parser.error("use an alphanumeric variant name")
    label = args.label or f"n{args.order}-{args.shape}-{args.numeric}-{args.bits}"
    if not label.replace("-", "").replace("_", "").isalnum():
        parser.error("label must use letters, numbers, hyphens or underscores")
    output = HERE / f"{label}.json"
    log = HERE / f"{label}.log"
    run = HERE / f"{label}-run.json"
    if any(path.exists() for path in [output, log, run]):
        parser.error("retained evidence exists; choose a new label")
    binary = BINARY if args.variant == "stage1" else f"target/near-vacuum-validation/near_vacuum_{args.variant}"
    sources = SOURCE if args.variant == "stage1" else [path.replace("stage1-source", f"stage-{args.variant}-source") for path in SOURCE]
    manifest = HERE / f"{args.variant}-build.json"
    build = json.loads(manifest.read_text())
    driver = build.get("driver", "validate")
    sources = [path.replace("near_vacuum_validate.rs", f"near_vacuum_{driver}.rs") for path in sources]
    arguments = [args.order, args.shape, args.numeric, str(args.bits)]
    if driver == "heterogeneous": arguments = [args.order]
    if driver == "unequal": arguments = [args.numeric, str(args.bits)]
    command = ["taskset", "-c", str(args.cpu), binary] + arguments + [str(output.relative_to(ROOT))]
    paths = sources + ARCHIVES + [binary, str(Path(__file__).relative_to(ROOT))]
    before = {path: sha(path) for path in paths}
    if any(before.get(path) != expected for path, expected in build["sha256"].items()):
        parser.error("frozen sources, binary, or dependencies differ from stage1 build manifest")
    started = time.monotonic()
    timed_out = False
    with log.open("w") as stream:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        try:
            exit_code = process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                exit_code = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                exit_code = process.wait()
    runtime_seconds = time.monotonic()-started
    after = {path: sha(path) for path in paths}
    record = {
        "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "command": command, "timeout_seconds": args.timeout, "timed_out": timed_out,
        "exit_code": exit_code, "diagnostic_wall_seconds": runtime_seconds,
        "sha256_before": before, "sha256_after": after, "inputs_unchanged": before == after,
        "build_manifest": str(manifest.relative_to(ROOT)), "build_manifest_sha256": sha(str(manifest.relative_to(ROOT))),
        "output": str(output.relative_to(ROOT)) if output.exists() else None,
        "output_sha256": sha(str(output.relative_to(ROOT))) if output.exists() else None,
        "log": str(log.relative_to(ROOT)), "log_sha256": sha(str(log.relative_to(ROOT))),
        "scope": "Validation-only candidate, frozen baseline DNS archive and pre-default-stack Symbolica. Diagnostic timing, not a benchmark.",
    }
    run.write_text(json.dumps(record, indent=2)+"\n")
    print(json.dumps({key: record[key] for key in ["timed_out", "exit_code", "diagnostic_wall_seconds", "inputs_unchanged", "output", "log"]}))
    raise SystemExit(0 if exit_code == 0 and not timed_out and before == after else 1)


if __name__ == "__main__":
    main()
