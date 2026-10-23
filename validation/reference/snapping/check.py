"""Check legacy snapping against original Fortran without any Rust runtime.

The original and harness mass-reference policies are inserted verbatim into
the same probe. The scalar-product implementation is the untouched original.
All generated files and executables stay under target/snapping-reference.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path.cwd()
HERE = ROOT / "validation/reference/snapping"
SOURCE = ROOT.parent / "references/madgraph/vendor/IREGI/src"
OUT = ROOT / "target/snapping-reference/policy-check"


def run(command):
    return subprocess.check_output(command, cwd=ROOT, text=True, stderr=subprocess.STDOUT)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-snapshot", action="store_true")
    parser.add_argument("--fc", default=os.environ.get("FC") or shutil.which("gfortran"))
    args = parser.parse_args()
    if not args.fc:
        raise SystemExit("Source scripts/env.sh or provide --fc before running this check")
    if not HERE.is_dir() or not SOURCE.is_dir():
        raise SystemExit("Run from the iregi-rust repository root")
    OUT.mkdir(parents=True, exist_ok=True)
    flags = ["-O3", "-std=legacy", "-J", str(OUT), "-I", str(OUT)]
    objects = []
    for name in ["global", "kinematics"]:
        obj = OUT / f"{name}.o"
        run([args.fc, *flags, "-c", str(SOURCE / f"{name}.f90"), "-o", str(obj)])
        objects.append(str(obj))
    interface = (SOURCE / "IREGI4ML5_interface.f90").read_text()
    original = interface[interface.index("  nnonzeromass=0"):interface.index("     IF(i.EQ.1)THEN")]
    original += "  ENDDO\n  NMASS=nnonzeromass\n"
    driver = (HERE.parent / "driver.f90").read_text()
    harness = driver[driver.index("    nmass=0"):driver.index("    count=(rank+1)")]
    template = (HERE / "probe.f90").read_text()
    results = {}
    for label, policy, complex_flag in [
        ("original", original, "comp_mass_scheme"),
        ("harness", harness, "complex_mass"),
    ]:
        code = template.replace("! POLICY_INSERTION", policy).replace(
            "! COMPLEX_RESULT_INSERTION", f"complex_mode={complex_flag}"
        )
        path = OUT / f"{label}.f90"
        path.write_text(code)
        executable = OUT / label
        run([args.fc, *flags, str(path), *objects, "-o", str(executable)])
        output = run([str(executable)])
        (OUT / f"{label}.txt").write_text(output)
        results[label] = {
            fields[0]: [float(value) for value in fields[1:]]
            for line in output.splitlines()
            if (fields := line.split())
        }
    if results["original"] != results["harness"]:
        raise AssertionError("Harness mass-reference/complex policy differs from original IMLOOP")
    data = {
        "schema_version": 1,
        "compiler": run([args.fc, "--version"]).splitlines()[0],
        "source_sha256": {
            name: sha256(SOURCE / name)
            for name in ["global.f90", "kinematics.f90", "IREGI4ML5_interface.f90"]
        },
        "driver_sha256": sha256(HERE.parent / "driver.f90"),
        "probe_sha256": sha256(HERE / "probe.f90"),
        "checks": results["original"],
    }
    snapshot = HERE / "snapshot.json"
    if args.write_snapshot:
        snapshot.write_text(json.dumps(data, indent=2) + "\n")
    else:
        expected = json.loads(snapshot.read_text())
        if data["source_sha256"] != expected["source_sha256"]:
            raise AssertionError("Original reference changed; review snapping behavior before updating")
        if data["checks"] != expected["checks"]:
            raise AssertionError("Snapping behavior differs from the committed snapshot")
    (OUT / "validation.json").write_text(json.dumps(data, indent=2) + "\n")
    print(f"PASS: {len(data['checks'])} snapping/dispatch snapshots; harness equals original policy exactly")


if __name__ == "__main__":
    main()
