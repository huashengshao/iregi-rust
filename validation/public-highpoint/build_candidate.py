"""Freeze and compile the promoted core against the baseline's exact masters.

The baseline Cargo core used the default workspace dev profile. Its fingerprint
is retained; the original verbose rustc invocation was not recorded, so matching
opt0/debug flags are inferred from Cargo's recorded profile, not observed argv.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path.cwd()
    here = root / "validation/public-highpoint"
    target = root / "target/public-highpoint/candidate"
    target.mkdir(exist_ok=True)
    snapshot = target / "source/crates/iregi-rust"
    if snapshot.exists():
        raise ValueError("Use the existing immutable snapshot or a new build name; never overwrite it")
    original = root / "crates/iregi-rust"
    script_hash = sha(Path(__file__))
    source_hashes = {str(p.relative_to(root)): sha(p) for p in (original / "src").rglob("*.rs")}
    snapshot.parent.mkdir(parents=True)
    shutil.copytree(original / "src", snapshot / "src")
    shutil.copyfile(original / "Cargo.toml", snapshot / "Cargo.toml")
    for name, expected in source_hashes.items():
        assert sha(root/name) == expected
        assert sha(snapshot / Path(name).relative_to("crates/iregi-rust")) == expected
    baseline = json.loads((here / "build.json").read_text())
    stable = root / "target/stack-reuse-current-workspace/deps"
    shared = root / "target/cargo-build/debug/deps"
    fingerprint = shared.parent / ".fingerprint/iregi-rust-b0667c2d807d11b6/lib-iregi_rust.json"
    shutil.copyfile(fingerprint, here / "baseline-core-fingerprint.json")
    extern = {
        "iregi_masters": stable / "libiregi_masters-0d5459afd211649c.rlib",
        "symbolica": stable / "libsymbolica-5cca42ee48491872.rlib",
        "serde": shared / "libserde-fc3dcd4b8c210596.rlib",
        "thiserror": shared / "libthiserror-b877110d28821624.rlib",
    }
    for name in ["iregi_masters", "symbolica"]:
        assert sha(extern[name]) == baseline["explicit_extern_sha256"][name]
    guards = [*(p for p in shared.iterdir() if p.suffix in [".rlib", ".so"]), *extern.values()]
    before = {str(p.relative_to(root)): sha(p) for p in guards}
    native = root / "target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib"
    core_library = target / "libiregi_rust.rlib"
    command = ["taskset", "-c", "14,15", "rustc", "--crate-name", "iregi_rust", "--crate-type", "rlib",
               "--edition=2024", str(snapshot / "src/lib.rs"), "-C", "opt-level=0", "-C", "debuginfo=2",
               "-C", "debug-assertions=on", "-C", "overflow-checks=on", "-C", "embed-bitcode=no",
               "-C", "metadata=public_highpoint_promoted", "-L", f"dependency={stable}",
               "-L", f"dependency={shared}", "-L", f"native={native}"]
    for name, path in extern.items():
        command += ["--extern", f"{name}={path}"]
    command += ["-o", str(core_library)]
    env = os.environ.copy()
    env.update(CARGO_MANIFEST_DIR=str(snapshot), CARGO_CRATE_NAME="iregi_rust")
    started = time.monotonic()
    with (here / "candidate-core-build.log").open("w") as log:
        code = subprocess.call(command, env=env, cwd=root, stdout=log, stderr=subprocess.STDOUT)
    result = {"status": "failed", "core_exit_code": code, "core_command": command,
              "library_source_hashes": source_hashes, "frozen_core_source": str(snapshot.relative_to(root)),
              "baseline_core_fingerprint_sha256": sha(here / "baseline-core-fingerprint.json"),
              "profile_scope": "Core opt0/debuginfo2/assertions/overflow flags inferred from retained Cargo profile and rustflags=[]; original Cargo verbose rustc argv not retained. Probe flags and master/Symbolica archive bytes match baseline.",
              "master_and_symbolica_match_baseline": True}
    if code == 0:
        probe = root / "crates/iregi-rust/examples/highpoint_public.rs"
        assert sha(probe) == baseline["source_sha256"]
        binary = target / "highpoint_public"
        probe_extern = {**extern, "iregi_rust": core_library,
                        "serde_json": shared / "libserde_json-3b583d0e8aa0facc.rlib"}
        probe_command = ["taskset", "-c", "14,15", "rustc", "--crate-name", "highpoint_public",
                         "--edition=2024", str(probe), "-C", "opt-level=2", "-C", "metadata=highpoint_public_adoption",
                         "-L", f"dependency={target}", "-L", f"dependency={stable}",
                         "-L", f"dependency={shared}", "-L", f"native={native}"]
        for name, path in probe_extern.items():
            probe_command += ["--extern", f"{name}={path}"]
        probe_command += ["-o", str(binary)]
        with (here / "candidate-probe-build.log").open("w") as log:
            probe_code = subprocess.call(probe_command, cwd=root, stdout=log, stderr=subprocess.STDOUT)
        result.update(probe_exit_code=probe_code, probe_command=probe_command, source_sha256=sha(probe),
                      core_library_sha256=sha(core_library), explicit_extern_sha256={k: sha(v) for k, v in probe_extern.items()})
        if probe_code == 0:
            result.update(binary_sha256=sha(binary), binary_path=str(binary.relative_to(root)), status="passed")
    after = {str(p.relative_to(root)): sha(p) for p in guards}
    changed = {key: [value, after.get(key)] for key, value in before.items() if after.get(key) != value}
    frozen_source_changes = {
        name: [expected, sha(snapshot / Path(name).relative_to("crates/iregi-rust"))]
        for name, expected in source_hashes.items()
        if sha(snapshot / Path(name).relative_to("crates/iregi-rust")) != expected
    }
    result.update(frozen_core_sources_verified_after_build=not frozen_source_changes,
                  frozen_core_source_changes=frozen_source_changes,
                  build_script_sha256=script_hash)
    result.update(changed_inputs=changed, elapsed_seconds=time.monotonic()-started)
    if changed or frozen_source_changes or sha(Path(__file__)) != script_hash:
        result["status"] = "failed"
    (here / "candidate-build.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["status", "core_exit_code", "elapsed_seconds", "changed_inputs"]}), flush=True)
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
