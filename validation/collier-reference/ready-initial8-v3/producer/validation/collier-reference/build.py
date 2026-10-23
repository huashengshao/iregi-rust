"""Build the optional, isolated COLLIER reference with comparable strict flags.

No benchmark runs here. All upstream sources remain unchanged; a generated
copy changes only CMake's hardcoded release flags (removing fast-math).
"""
import argparse
import datetime
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time


ROOT = Path.cwd()
HERE = ROOT / "validation/collier-reference"
SOURCE = ROOT / "target/reference/collier/source/collier-COLLIER-1.2.10"
FLAGS = ["-O3", "-std=legacy", "-fallow-argument-mismatch", "-Wtabs"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def run_bounded(command, output, timeout, commands):
    started = time.monotonic()
    entry = {"command": list(map(str, command)), "cwd": str(ROOT), "timeout_seconds": timeout,
             "log": str(output.relative_to(ROOT)), "status": "running"}
    commands.append(entry)
    with output.open("wb") as log:
        process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        entry["pid"] = process.pid
        try:
            code = process.wait(timeout=timeout)
            entry.update(status="passed" if code == 0 else "failed", exit_code=code)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            entry.update(status="timeout", exit_code=process.returncode)
            raise RuntimeError(f"Build command timed out; log retained at {output}")
        finally:
            entry["elapsed_seconds"] = time.monotonic() - started
            entry["log_sha256"] = digest(output)
    if code:
        raise RuntimeError(f"Build command failed ({code}); log retained at {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New attempt directory inside target/")
    parser.add_argument("--cpus", required=True, help="Comma-separated CPU affinity, e.g. 26,27")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--cmake", default="cmake", help="CMake executable (absolute path accepted)")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "target") or output.exists():
        parser.error("use a new output directory inside the project's target/")
    cpus = {int(cpu) for cpu in args.cpus.split(",")}
    if not cpus or not cpus <= os.sched_getaffinity(0) or args.jobs < 1 or args.timeout <= 0:
        parser.error("invalid CPU affinity, job count or timeout")
    os.sched_setaffinity(0, cpus)
    compiler = shutil.which(os.environ.get("FC", "gfortran"))
    cmake = shutil.which(args.cmake)
    if not compiler or not cmake:
        parser.error("source scripts/env.sh; gfortran and cmake are required")
    manifest = json.loads((ROOT / "docs/research/collier-1.2.10-manifest.json").read_text())
    original_hashes = {row["path"]: row["sha256"] for row in manifest["source_files"]}
    if any(digest(SOURCE / name) != expected for name, expected in original_hashes.items()):
        raise SystemExit("The original extracted COLLIER source differs from its source manifest")
    output.mkdir(parents=True)
    generated = output / "source"
    shutil.copytree(SOURCE, generated)
    cmake_file = generated / "CMakeLists.txt"
    before = cmake_file.read_text()
    old = 'set (opt_RELEASE "-O2 -funroll-loops -ffast-math -Wtabs")'
    new = 'set (opt_RELEASE "' + " ".join(FLAGS) + '")'
    if before.count(old) != 1:
        raise SystemExit("Unexpected upstream CMake release flag definition")
    after = before.replace(old, new)
    cmake_file.write_text(after)
    patch = output / "cmake-flags.patch"
    patch.write_text("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                               fromfile="upstream/CMakeLists.txt", tofile="generated/CMakeLists.txt")))
    driver = output / "driver.f90"
    shutil.copyfile(HERE / "driver.f90", driver)
    data = {"schema_version": 1, "kind": "collier-reference-build", "status": "running",
            "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "version": "1.2.10", "license": "GPL-3.0 (upstream source headers/COPYING)",
            "archive": manifest["archive"], "upstream_source_sha256": original_hashes,
            "generated_source_root": str(generated.relative_to(ROOT)),
            "patch": {"path": str(patch.relative_to(ROOT)), "sha256": digest(patch),
                      "scope": "Only upstream GNU Fortran release flags; no numerical source edits"},
            "compiler": subprocess.check_output([compiler, "--version"], text=True).splitlines()[0],
            "compiler_path": compiler, "cmake_path": cmake,
            "cmake": subprocess.check_output([cmake, "--version"], text=True).splitlines()[0],
            "requested_flags": FLAGS, "fast_math": False, "cpus": sorted(cpus), "jobs": args.jobs,
            "driver_sha256": digest(driver), "builder_sha256": digest(Path(__file__)), "commands": [],
            "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "cache_policy": "COLLIER local-only recurrence memoization reset per root; no cross-sample/event cache",
            "timing_scope": "Public full Cartesian tensor call, input invariant setup, native normalization and status/finiteness checks; no transport or symbolic preparation",
            "qualified_domain": "Ordinary unit powers, unshifted D=4-2epsilon, N=2..4, rank=0..3; zero-origin real spatial shifts, squared masses Re>0 and Im<=0; IR finite"}
    proof = output / "build.json"
    save(proof, data)
    started = time.monotonic()
    try:
        run_bounded([cmake, "-S", str(generated), "-B", str(output / "cmake"), "-Dstatic=ON",
                     "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_Fortran_COMPILER={compiler}"],
                    output / "configure.log", min(60, args.timeout), data["commands"])
        remaining = max(1, args.timeout - (time.monotonic() - started))
        run_bounded([cmake, "--build", str(output / "cmake"), "--parallel", str(args.jobs)],
                    output / "compile.log", remaining, data["commands"])
        library = generated / "libcollier.a"
        binary = output / "collier-benchmark"
        remaining = max(1, args.timeout - (time.monotonic() - started))
        run_bounded([compiler, *FLAGS, "-I", str(generated / "modules"), str(driver), str(library),
                     "-o", str(binary)], output / "link.log", remaining, data["commands"])
        source_after = {name: digest(SOURCE / name) for name in original_hashes}
        if source_after != original_hashes:
            raise RuntimeError("Original COLLIER source changed during the isolated build")
        data.update(status="built", binary={"path": str(binary.relative_to(ROOT)), "sha256": digest(binary)},
                    library={"path": str(library.relative_to(ROOT)), "sha256": digest(library)},
                    generated_source_sha256={name: digest(generated / name) for name in original_hashes},
                    original_source_unchanged=True,
                    object_sha256={str(p.relative_to(output)): digest(p) for p in sorted((output / "cmake").rglob("*.o"))},
                    compile_flags={str(p.relative_to(output)): p.read_text() for p in (output / "cmake").rglob("flags.make")})
    except BaseException as error:
        data.update(status="failed", error=str(error))
        raise
    finally:
        data["elapsed_seconds"] = time.monotonic() - started
        data["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save(proof, data)
    print(proof)


if __name__ == "__main__":
    main()
