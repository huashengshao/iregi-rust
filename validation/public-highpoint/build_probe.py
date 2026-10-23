"""Compile the public probe against the preserved ordinary-stack-adoption build.

No Cargo process or Symbolica runtime is started. The preserved library manifest
identifies the historical sources; this does not label later live edits tested.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path.cwd()
    evidence = root / "validation/public-highpoint"
    build = root / "target/public-highpoint"
    build.mkdir(exist_ok=True)
    manifest_path = root / "target/stack-reuse-current-workspace/build-result.json"
    manifest = json.loads(manifest_path.read_text())
    assert manifest["status"] == "passed" and not manifest["sources_changed_during_build"]
    libraries = {Path(x["preserved_path"]).name: root/x["preserved_path"]
                 for x in manifest["preserved_dependencies"]}
    for item in manifest["preserved_dependencies"]:
        assert digest(root / item["preserved_path"]) == item["sha256"]
    stable = root / "target/stack-reuse-current-workspace/deps"
    shared = root / "target/cargo-build/debug/deps"
    source = root / "crates/iregi-rust/examples/highpoint_public.rs"
    extern = {
        "iregi_rust": libraries["libiregi_rust-b0667c2d807d11b6.rlib"],
        "iregi_masters": libraries["libiregi_masters-0d5459afd211649c.rlib"],
        "symbolica": libraries["libsymbolica-5cca42ee48491872.rlib"],
        "serde_json": shared / "libserde_json-3b583d0e8aa0facc.rlib",
    }
    command = ["taskset", "-c", "14,15", "rustc", "--crate-name", "highpoint_public",
               "--edition=2024", str(source), "-C", "opt-level=2", "-C", "metadata=highpoint_public_adoption",
               "-L", f"dependency={stable}", "-L", f"dependency={shared}",
               "-L", f"native={root}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib"]
    for name, path in extern.items():
        command += ["--extern", f"{name}={path}"]
    command += ["-o", str(build / "highpoint_public")]
    # Include transitive registry dependencies and proc macros; reject a moving
    # shared dependency set rather than infer its exact use from filenames.
    guards = [source, manifest_path, *libraries.values(),
              *(p for p in shared.iterdir() if p.suffix in [".rlib", ".so"])]
    before = {str(p.relative_to(root)): digest(p) for p in guards}
    start = time.monotonic()
    with (evidence / "build.log").open("w") as log:
        status = subprocess.call(command, cwd=root, env=os.environ.copy(), stdout=log, stderr=subprocess.STDOUT)
    after = {str(p.relative_to(root)): digest(p) for p in guards}
    changed = {key: [value, after.get(key)] for key, value in before.items() if after.get(key) != value}
    result = {"status": "passed" if status == 0 and not changed else "failed",
              "exit_code": status, "elapsed_seconds": time.monotonic()-start, "command": command,
              "source_sha256": before[str(source.relative_to(root))],
              "source_library_manifest_sha256": digest(manifest_path),
              "library_source_hashes": manifest["source_hashes_after"],
              "library_artifacts": manifest["preserved_dependencies"],
              "changed_inputs": changed, "guarded_shared_artifact_count": len(guards),
              "explicit_extern_sha256": {name: digest(path) for name, path in extern.items()},
              "limitations": "Preserved adoption-build core predates generalized-PV integration; the high-point ordinary path is unchanged. This compiles an external public-API driver, not a numeric-specialized private compiler test."}
    if status == 0:
        result["binary_sha256"] = digest(build / "highpoint_public")
    (evidence / "build.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["status", "exit_code", "elapsed_seconds", "changed_inputs"]}), flush=True)
    if status:
        print((evidence / "build.log").read_text())
    sys.exit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
