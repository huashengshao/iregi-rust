"""Build two isolated original-IREGI oracles; never edit the reference checkout."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path.cwd()
HERE = ROOT / "validation/reference"
SOURCE = ROOT.parent / "references/madgraph/vendor/IREGI/src"
OUT = ROOT / "target/reference"
DEFAULT_FC = "/nix/store/5km6kqfhjr16939ak9l1crzsh6x96f68-gfortran-wrapper-15.2.0/bin/gfortran"
MODULES = ["global", "funlib", "linear_algebra", "kinematics", "matrix_base", "cmatrix_base",
           "binary_tree", "matrices", "mis_warp", "special_fun", "pave_reduce", "cpave_reduce",
           "si_reduce", "csi_reduce", "ti_reduce", "cti_reduce", "gti_reduce", "IREGI4ML5_interface"]
OLD = """          factorial_pair(i,j)=DBLE(factorial(i+j-1))&
               /DBLE(factorial(i-1))/DBLE(factorial(j))"""
NEW = """          ! Same binomial coefficient, without overflowing 32-bit factorial.
          factorial_pair(i,j)=factorial_pair(i,j-1)&
               *DBLE(i+j-1)/DBLE(j)"""

def run(command):
    result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        print(result.stdout, file=sys.stderr)
        raise RuntimeError(f"command failed: {command}")
    return result.stdout

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fc", default=os.environ.get("FC") or shutil.which("gfortran") or DEFAULT_FC)
    parser.add_argument("--jobs", type=int, default=min(os.cpu_count() or 1, 8))
    args = parser.parse_args()
    if not (HERE / "driver.f90").is_file() or not SOURCE.is_dir():
        raise SystemExit("Run from the iregi-rust root beside ../references/madgraph")
    source = OUT / "source"
    objects = OUT / "objects"
    patched = OUT / "patched"
    objects.mkdir(parents=True, exist_ok=True)
    patched.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, source, dirs_exist_ok=True)
    original = (source / "funlib.f90").read_text()
    if original.count(OLD) != 1:
        raise SystemExit("Reference factorial function changed; audit the repair before building")
    repaired = original.replace(OLD, NEW)
    actual_patch = "".join(difflib.unified_diff(original.splitlines(keepends=True),
                                             repaired.splitlines(keepends=True),
                                             fromfile="original/funlib.f90", tofile="patched/funlib.f90"))
    if actual_patch != (HERE / "factorial_pair.patch").read_text():
        raise SystemExit("Recorded repair patch does not match the generated source edit")
    (patched / "funlib.f90").write_text(repaired)
    flags = ["-O3", "-fPIC", "-std=legacy", "-fallow-argument-mismatch", "-J", str(objects),
             "-I", str(objects), "-I", str(source)]
    def compile_file(src, obj, includes=()):
        command = [args.fc, *flags]
        for include in includes:
            command += ["-I", str(include)]
        run([*command, "-c", str(src), "-o", str(obj)])
    qcd_objects = []
    tasks = []
    for subdir in ["ff", "ql"]:
        folder = source / "qcdloop" / subdir
        makefile = (folder / "makefile").read_text()
        block = re.search(r"^OBJS\s*=(.*?)(?:\n\s*\n)", makefile, re.M | re.S).group(1)
        for name in re.findall(r"(?:\./)?([A-Za-z0-9_]+)\.o", block):
            obj = objects / f"{subdir}_{name}.o"
            qcd_objects.append(obj)
            tasks.append((folder / f"{name}.f", obj, (folder,)))
    print(f"Building {len(tasks)} QCDLoop/FF dependency objects", flush=True)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        list(pool.map(lambda task: compile_file(*task), tasks))
    olo_object = objects / "avh_olo_foriregi.o"
    print("Building bundled OneLOop", flush=True)
    compile_file(source / "oneloop/avh_olo_foriregi.f90", olo_object)
    main_objects = []
    for name in MODULES:
        print(f"Building {name}", flush=True)
        obj = objects / f"{name}.o"
        compile_file(source / f"{name}.f90", obj)
        main_objects.append(obj)
    driver_object = objects / "driver.o"
    compile_file(HERE / "driver.f90", driver_object)
    common = [str(driver_object), *map(str, main_objects), str(olo_object), *map(str, qcd_objects)]
    run([args.fc, "-O3", *common, "-o", str(OUT / "iregi-reference-original")])
    compile_file(patched / "funlib.f90", patched / "funlib.o")
    patched_common = [str(patched / "funlib.o") if x == str(objects / "funlib.o") else x for x in common]
    run([args.fc, "-O3", *patched_common, "-o", str(OUT / "iregi-reference")])
    compile_file(HERE / "factorial_table.f90", objects / "factorial_table.o")
    run([args.fc, str(objects / "factorial_table.o"), str(objects / "global.o"),
         str(patched / "funlib.o"), "-o", str(OUT / "factorial-table-check")])
    hashes = {str(p.relative_to(SOURCE)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in SOURCE.rglob("*") if p.is_file() and p.suffix in {".f", ".f90", ".h", ".inc"}}
    provenance = {"madgraph_commit": run(["git", "-C", str(SOURCE), "rev-parse", "HEAD"]).strip(),
                  "compiler": run([args.fc, "--version"]).splitlines()[0], "flags": flags,
                  "source_sha256": hashes,
                  "patch_sha256": hashlib.sha256((HERE / "factorial_pair.patch").read_bytes()).hexdigest(),
                  "driver_sha256": hashlib.sha256((HERE / "driver.f90").read_bytes()).hexdigest()}
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(f"Built {OUT / 'iregi-reference'} and untouched companion", flush=True)

if __name__ == "__main__":
    main()
