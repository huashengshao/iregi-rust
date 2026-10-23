"""Link the separate timing driver to the already audited IREGI object copy."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def main():
    root = Path.cwd()
    reference = root / "target/reference"
    output = root / "target/benchmark"
    output.mkdir(parents=True, exist_ok=True)
    source = root / "validation/benchmark/driver.f90"
    provenance = json.loads((reference / "provenance.json").read_text())
    compiler = os.environ.get("FC") or shutil.which("gfortran")
    if not compiler:
        raise SystemExit("Source scripts/env.sh before building the timing driver")
    compiler_version = subprocess.check_output([compiler, "--version"], text=True).splitlines()[0]
    if compiler_version != provenance["compiler"]:
        raise SystemExit("Rebuild the reference with this compiler before timing")
    objects = sorted((reference / "objects").glob("*.o"))
    objects = [p for p in objects if p.name not in {"driver.o", "factorial_table.o", "funlib.o"}]
    objects.append(reference / "patched/funlib.o")
    if len(objects) < 20 or not all(p.is_file() for p in objects):
        raise SystemExit("Run scripts/build-reference.sh before building the timing driver")
    flags = ["-O3", "-std=legacy", "-fallow-argument-mismatch"]
    binary = output / "iregi-benchmark"
    command = [compiler, *flags, "-I", str(reference / "objects"), str(source),
               *map(str, objects), "-o", str(binary)]
    subprocess.run(command, check=True, cwd=root)
    data = {
        "compiler": compiler_version, "flags": flags, "reference": provenance,
        "driver_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "object_sha256": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in objects},
        "timing_scope": "wall clock around repeated batches of tensor_integral_reduce, input mass-reference setup, finiteness/status checks, and IREGI_FREE_PS; no setup, transport, or I/O",
        "cache_policy": "IREGI initialization reused; numerical caches freed after every sample",
    }
    (output / "reference-build.json").write_text(json.dumps(data, indent=2) + "\n")
    print(binary)


if __name__ == "__main__":
    main()
