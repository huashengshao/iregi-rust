#!/usr/bin/env python3
"""Bind reviewed source, accepted common adapter, exact commands and closure."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path.cwd()
HERE = ROOT / "target/raw-distance-lazy-capture-optimized"
COMMON = ROOT / "target/selected-native-optimized"


def sha(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


audit = read(COMMON / "closure-audit.json")
assert sha(COMMON / "closure-audit.json") == "7faf196a9b4befa33cb7d55d3dc3dd4d8917c6ddba0ee1a5a93716b6086c72c8"
accepted = read(COMMON / "shared/accepted.json")
assert accepted["status"] == "accepted-shared-opt3-adapter"
shared_build = read(ROOT / accepted["build_record"])
assert sha(ROOT / accepted["build_record"]) == accepted["build_sha256"]
assert shared_build["status"] == "passed" and shared_build["inputs_unchanged"]
assert sha(ROOT / accepted["artifact"]["path"]) == accepted["artifact"]["sha256"]
assert accepted["artifact"]["sha256"] == "6926f3342ac36e0dead8f3d0534da6dd44609d0281a8c9e79c4b5b8b3b302572"
qualified = ROOT / "validation/raw-distance-lazy-capture/source-manifest.json"
prior = read(qualified)["bindings"]
bindings = dict(shared_build["inputs"])
source_files = {}
for variant in ["baseline", "candidate"]:
    for path in sorted((HERE / variant).rglob("*")):
        if path.is_file():
            original = "target/raw-distance-lazy-capture-candidate/" + str(path.relative_to(HERE))
            assert sha(path) == prior[original], path
            source_files[str(path.relative_to(HERE))] = sha(path)
            bindings[str(path.relative_to(ROOT))] = sha(path)
compiler = str(Path(shutil.which("rustc")).resolve())
version = subprocess.check_output([compiler, "-vV"], text=True).strip()
assert version == audit["compiler"]
bindings[compiler] = sha(compiler)
linker = str(Path(shutil.which("cc")).resolve())
bindings[linker] = sha(linker)
for path in [
    qualified, ROOT / "validation/raw-distance-lazy-capture/qualification.json",
    ROOT / "validation/raw-distance-lazy-capture/review/final-review.json",
    ROOT / "validation/raw-distance-lazy-capture/review/runtime-review.json",
    ROOT / "validation/raw-distance-final-performance/protocol/probe.rs",
    COMMON / "closure-audit.json", COMMON / "plan-binding.json", COMMON / "plan.md",
    COMMON / "build_shared.py", COMMON / "shared/accepted.json",
    ROOT / accepted["build_record"], ROOT / accepted["artifact"]["path"],
    (ROOT / accepted["build_record"]).parent / "compiler.log",
    HERE / "build.py", HERE / "preflight.py", HERE / "freeze.py", HERE / "probe.rs",
    ROOT / "scripts/env.sh",
]:
    bindings[str(path.relative_to(ROOT))] = sha(path)
for path, digest in bindings.items():
    assert sha(ROOT / path) == digest, path
deps = ROOT / "target/benchmark/dependency-closures/6b24c03-complete-kinds/deps"
runtime = audit["runtime_artifacts"]
externs = {name: ROOT / runtime[name]["path"] for name in ["symbolica", "serde", "serde_json", "thiserror"]}
externs["iregi_masters"] = ROOT / accepted["artifact"]["path"]
common = ["taskset", "-c", "6,7", compiler, "--edition=2024", "-C", "opt-level=3", "-C", "codegen-units=16", "-C", "embed-bitcode=yes", "-C", "debuginfo=0", "-C", "debug-assertions=no", "-C", "overflow-checks=no", "-C", f"linker={linker}", "-L", f"dependency={deps}", "-L", f"dependency={(ROOT / accepted['artifact']['path']).parent}", "-L", f"native={ROOT / audit['native_search_path']}"]
attempt = HERE / "build-001"
steps = []
for variant, suffix in [("baseline", "eager"), ("candidate", "lazy")]:
    crate = "receipt_opt_" + suffix
    core = HERE / variant / "crates/iregi-rust"
    output = attempt / ("lib" + crate + ".rlib")
    command = common + ["--crate-name", crate, "--crate-type", "rlib", str(core / "src/lib.rs"), "-C", "metadata=" + crate, "-o", str(output)]
    for name, path in externs.items():
        command += ["--extern", f"{name}={path}"]
    steps.append({"label": suffix, "command": command, "environment": {"CARGO_CRATE_NAME": "iregi_rust", "CARGO_MANIFEST_DIR": str(core), "CARGO_PKG_NAME": "iregi-rust", "CARGO_PKG_VERSION": "0.1.0"}, "timeout_seconds": 180, "output": str(output.relative_to(ROOT))})
command = common + ["--crate-name", "receipt_lazy_optimized_probe", "-C", "lto=thin", str(HERE / "probe.rs"), "-L", f"dependency={attempt}", "-o", str(attempt / "probe")]
for suffix in ["eager", "lazy"]:
    crate = "receipt_opt_" + suffix
    command += ["--extern", f"{crate}={attempt / ('lib' + crate + '.rlib')}"]
for name in ["symbolica", "iregi_masters"]:
    command += ["--extern", f"{name}={externs[name]}"]
steps.append({"label": "probe", "command": command, "environment": {"CARGO_CRATE_NAME": "receipt_lazy_optimized_probe", "CARGO_MANIFEST_DIR": str(HERE)}, "timeout_seconds": 600, "output": str((attempt / "probe").relative_to(ROOT))})
manifest = {
    "status": "source_and_commands_frozen_pending_independent_review",
    "scope": "New optimized eager-final-e23 versus lazy comparison; identical current selected-capable master adapter with selection disabled and default Symbolica. No arity2 numerical dependency or global native feature. No timing grant.",
    "bindings": bindings, "source_files": source_files, "compiler_path": compiler,
    "compiler_version": version, "linker_path": linker,
    "linker_version": subprocess.check_output([linker, "--version"], text=True).splitlines()[0],
    "shared_adapter_receipt": accepted, "runtime_artifacts": runtime,
    "build_steps": steps,
    "preflight": {"timeout_seconds": 120, "cases": 14, "calls_per_side_per_case": 7, "time_argument": False},
    "future_timing_protocol": {"authorized": False, "cases": 14, "warm_calls": 5, "pairs": 41, "faster_side_minimum_block_ms": 200, "overall_bound_seconds": 600, "bootstrap_draws": 20000, "confidence": 0.99, "relative_interval_width_maximum": 0.02, "repeat_policy": "No repeats or case dropping based on observed intervals"},
    "important_distinctions": ["Runtime numerical dependencies retain original opt3/cgu1 release profile; new core/adapter/probe cgu16 commands are explicit.", "Ordinary core CARGO_CRATE_NAME=iregi_rust for both sides; actual Rust crate disambiguators differ.", "The accepted shared adapter includes an unrelated opt-in native selector, but neither receipt core invokes it and probe asserts SymbolicaBatch default.", "Older opt3 final14 cohort and newer debug26+14 qualification remain separately frozen; neither is replaced by this new cohort."],
}
(HERE / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(sha(HERE / "source-manifest.json"))
