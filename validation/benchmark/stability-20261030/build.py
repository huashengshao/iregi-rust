#!/usr/bin/env python3
"""Build and freeze the binaries of the binary64 stability study.

TIRust: release example `stability_driver` (same features as the timing
driver of direct-engine-20261030). COLLIER: `drivers/collier_physical.f90`
linked against the unmodified COLLIER 1.2.10 archive. Original IREGI
(binary64) reuses the frozen timing driver of direct-engine-20261030; the
reference is the quadruple-precision original IREGI build
target/quad-iregi-source-audit/build-v6-001. Binaries go to
target/stability-20261030/bin; SHA-256 sums, toolchains and the TIRust git
head are recorded in build.json. Run from the repository root after
`source scripts/env.sh`.
"""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "target/stability-20261030"
BIN = OUT / "bin"
FFLAGS = ["-O3", "-std=legacy", "-fallow-argument-mismatch"]
IREGI = ROOT / "target/direct-engine-20261030/bin/iregi-general"
QUAD = ROOT / "target/quad-iregi-source-audit/build-v6-001/iregi-reference-quad"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(argv, **kwargs):
    started = time.monotonic()
    subprocess.run(argv, check=True, cwd=ROOT, **kwargs)
    return round(time.monotonic() - started, 3)


def main() -> None:
    BIN.mkdir(parents=True, exist_ok=True)
    record = {"host": platform.node(), "machine": platform.machine(), "steps": {}}
    gfortran = subprocess.run(["gfortran", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    rustc = subprocess.run(["rustc", "--version"], capture_output=True, text=True).stdout.strip()
    record["toolchains"] = {"gfortran": gfortran, "rustc": rustc}

    collier_source = ROOT / "target/reference/collier/build-attempt001/source"
    collier_dir = OUT / "collier"
    collier_dir.mkdir(exist_ok=True)
    collier = BIN / "collier-physical"
    driver = HERE / "drivers/collier_physical.f90"
    record["steps"]["collier_link_s"] = run(["gfortran", *FFLAGS, "-Wtabs", "-J", str(collier_dir), "-I",
                                             str(collier_source / "modules"), str(driver),
                                             str(collier_source / "libcollier.a"), "-o", str(collier)])
    record["collier"] = {"binary": str(collier.relative_to(ROOT)), "sha256": sha256(collier),
                         "flags": FFLAGS + ["-Wtabs"], "driver_sha256": sha256(driver),
                         "archive_sha256": sha256(collier_source / "libcollier.a")}
    record["iregi"] = {"binary": str(IREGI.relative_to(ROOT)), "sha256": sha256(IREGI),
                       "provenance": "validation/benchmark/direct-engine-20261030/build.json"}
    record["quad_reference"] = {"binary": str(QUAD.relative_to(ROOT)), "sha256": sha256(QUAD),
                                "provenance": "target/quad-iregi-source-audit/build-v6-001/build.json"}

    env = dict(os.environ, CARGO_TARGET_DIR=str(ROOT / "target/optimized-build"))
    cargo = ["cargo", "build", "--release", "--offline", "-p", "iregi-rust", "--example", "stability_driver",
             "--features", "native-f64-abc"]
    record["steps"]["tirust_cargo_s"] = run(cargo, env=env)
    built = ROOT / "target/optimized-build/release/examples/stability_driver"
    tirust = BIN / "tirust-stability"
    shutil.copy2(built, tirust)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, capture_output=True,
                           text=True).stdout.strip()
    record["tirust"] = {"binary": str(tirust.relative_to(ROOT)), "sha256": sha256(tirust), "git_head": head,
                        "tracked_changes": bool(dirty), "cargo": " ".join(cargo)}
    (HERE / "build.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record, indent=1))


if __name__ == "__main__":
    main()
