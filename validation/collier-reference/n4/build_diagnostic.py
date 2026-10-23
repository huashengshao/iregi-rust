"""Link only the reviewed diagnostic driver against the immutable COLLIER archive."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time


ROOT = Path.cwd()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    args = parser.parse_args()
    source = ROOT / "validation/collier-reference/n4/diagnostic-driver.f90"
    upstream = ROOT / "validation/collier-reference/ready-initial8-v3/build.json"
    original = json.loads(upstream.read_text())
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "target"):
        raise SystemExit("Use a new attempt directory inside the project target/")
    review = json.loads(args.review.read_text())
    reviewed = review.get("sources_sha256", {})
    source_key = str(source.relative_to(ROOT))
    original_key = "validation/collier-reference/driver.f90"
    if (review.get("status") != "source_review_passed" or review.get("blockers") != []
            or reviewed.get(source_key) != digest(source)
            or reviewed.get(original_key) != digest(ROOT / original_key)):
        raise SystemExit("A passing source-bound diagnostic review is required")
    library = ROOT / original["library"]["path"]
    if digest(library) != original["library"]["sha256"]:
        raise SystemExit("Immutable COLLIER library changed")
    output.mkdir(parents=True)
    frozen = output / "driver.f90"
    shutil.copyfile(source, frozen)
    binary = output / "collier-diagnostic"
    command = [original["compiler_path"], *original["requested_flags"], "-I", str(library.parent / "modules"),
               str(frozen), str(library), "-o", str(binary)]
    record = {"kind": "collier-diagnostic-driver-only-link", "status": "running", "timeout_seconds": 60,
              "command": command, "cwd": str(ROOT), "compiler": original["compiler"],
              "original_library": original["library"], "original_build_manifest_sha256": digest(upstream),
              "review": {"path": str(args.review), "sha256": digest(args.review)},
              "source_sha256": digest(frozen), "builder_sha256": digest(Path(__file__)),
              "numerical_source_changed": False, "library_rebuilt": False, "performance_claim": None}
    started = time.monotonic()
    with (output / "link.log").open("wb") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = process.wait(timeout=60)
            record.update(status="built" if code == 0 else "failed", exit_code=code)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            record.update(status="timeout", exit_code=process.returncode)
    record["elapsed_seconds"] = time.monotonic() - started
    record["link_log_sha256"] = digest(output / "link.log")
    record["library_unchanged"] = digest(library) == original["library"]["sha256"]
    if record["status"] == "built":
        record["binary"] = {"path": str(binary.relative_to(ROOT)), "sha256": digest(binary)}
    (output / "build.json").write_text(json.dumps(record, indent=2) + "\n")
    if record["status"] != "built" or not record["library_unchanged"]:
        raise SystemExit("Diagnostic link failed; retained receipt")
    print(output / "build.json")


if __name__ == "__main__":
    main()
