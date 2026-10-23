"""Link the reviewed generic tensor driver; never rebuild either library."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

import support


ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--cpu", type=int, default=26)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "target"):
        parser.error("new project target/ directory required")
    if args.cpu not in os.sched_getaffinity(0):
        parser.error("CPU unavailable")
    original_path = ROOT / "validation/collier-reference/ready-initial8-v3/build.json"
    original = json.loads(original_path.read_text())
    review = json.loads(args.review.read_text())
    sources = sorted(HERE.glob("*.py"))
    sources += [HERE / "driver.f90"]
    bindings = {str(p.relative_to(ROOT)): support.kernel.digest(p) for p in sources}
    if (review.get("status") != "source_review_passed" or review.get("blockers") != []
            or any(review.get("sources_sha256", {}).get(p) != sha for p, sha in bindings.items())):
        raise ValueError("passing review must bind the complete source/protocol candidate")
    library = ROOT / original["library"]["path"]
    if support.kernel.digest(library) != original["library"]["sha256"]:
        raise ValueError("immutable COLLIER archive changed")
    modules = sorted((library.parent / "modules").glob("*.mod"))
    module_bindings = {str(p.relative_to(ROOT)): support.kernel.digest(p) for p in modules}
    output.mkdir(parents=True)
    frozen = output / "source"
    frozen.mkdir()
    for p in sources:
        shutil.copyfile(p, frozen / p.name)
    binary = output / "collier-shared"
    command = [original["compiler_path"], *original["requested_flags"], "-I", str(library.parent/"modules"),
               str(frozen/"driver.f90"), str(library), "-o", str(binary)]
    data = {"kind": "collier-shared-driver-only-link", "status": "running", "timeout_seconds": 60,
            "command": command, "cpu": args.cpu, "compiler": original["compiler"],
            "source_sha256": bindings, "module_sha256": module_bindings,
            "original_build": {"path": str(original_path.relative_to(ROOT)), "sha256": support.kernel.digest(original_path)},
            "library": original["library"], "review": {"path": str(args.review), "sha256": support.kernel.digest(args.review)},
            "library_rebuilt": False, "iregi_rebuilt": False, "fast_math": False,
            "performance_qualified": False}
    support.kernel.save(output/"build.json", data)
    old = os.sched_getaffinity(0)
    started = time.monotonic()
    try:
        os.sched_setaffinity(0, {args.cpu})
        with (output/"link.log").open("wb") as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = process.wait(timeout=60)
                data.update(status="built" if code == 0 else "failed", exit_code=code)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                data.update(status="timeout", exit_code=process.returncode)
    except Exception as error:
        data.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        os.sched_setaffinity(0, old)
        data["elapsed_seconds"] = time.monotonic()-started
        data["link_log_sha256"] = support.kernel.digest(output/"link.log") if (output/"link.log").exists() else None
        data["guards_unchanged"] = (all(support.kernel.digest(ROOT/p) == sha for p, sha in bindings.items())
                                    and all(support.kernel.digest(ROOT/p) == sha for p, sha in module_bindings.items())
                                    and support.kernel.digest(library) == original["library"]["sha256"])
        if data["status"] == "built":
            data["binary"] = {"path": str(binary.relative_to(ROOT)), "sha256": support.kernel.digest(binary)}
        if not data["guards_unchanged"]:
            data.update(status="failed", error="source/module/library guard changed")
        support.kernel.save(output/"build.json", data)
    print(output/"build.json")
    if data["status"] != "built":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
