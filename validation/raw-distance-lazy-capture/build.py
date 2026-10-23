#!/usr/bin/env python3
"""Bounded correctness-only build of frozen eager/lazy receipt implementations."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path.cwd()
HERE = ROOT / "target/raw-distance-lazy-capture-candidate"


def sha(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def verify(bindings):
    for relative, digest in bindings.items():
        assert sha(ROOT / relative) == digest, f"changed input: {relative}"


def main():
    attempt = HERE / ("build-" + sys.argv[1])
    attempt.mkdir(exist_ok=False)
    manifest = read(HERE / "source-manifest.json")
    review = read(HERE / "review/final-review.json")
    assert review["status"] == "passed", "source review required before compilation"
    assert review["source_manifest_sha256"] == sha(HERE / "source-manifest.json")
    bindings = dict(manifest["bindings"])
    for relative in ["source-manifest.json", "review/final-review.json"]:
        path = HERE / relative
        bindings[str(path.relative_to(ROOT))] = sha(path)
    verify(bindings)
    supplemental_path = ROOT / "target/core-fused-cse-census/supplemental-deps.json"
    supplemental = read(supplemental_path)
    metadata = ROOT / "target/core-fused-cse-census/thiserror-metadata.txt"
    fingerprint = ROOT / "target/core-fused-cse-census/thiserror-cargo-fingerprint.json"
    assert sha(metadata) == supplemental["metadata_sha256"]
    assert sha(fingerprint) == supplemental["fingerprint_sha256"]
    assert json.loads(read(fingerprint)["features"]) == ["default", "std"]
    assert "thiserror_impl-415c566ab8174dc4" in metadata.read_text()
    event = next(e for e in supplemental["completed_metadata_and_proc_macro_events"] if e["target"]["name"] == "thiserror")
    assert event["package_id"].endswith("thiserror@2.0.21")
    assert event["features"] == ["default", "std"]
    deps = ROOT / "target/e6-direct-n2/deps"
    extra = ROOT / "target/core-fused-cse-census/supplemental-deps"
    native = ROOT / "target/e6-direct-n2/native"
    externs = {name: deps / filename for name, filename in {
        "iregi_masters": "libiregi_masters-f07797f04e91954e.rlib",
        "symbolica": "libsymbolica-06e42762cabb77d9.rlib",
        "serde": "libserde-b04ba25115fa19f8.rlib",
        "serde_json": "libserde_json-d657c5438f354a41.rlib",
    }.items()}
    externs["thiserror"] = extra / "libthiserror-0527e2191ec3561c.rlib"
    objects = subprocess.check_output(["ar", "t", str(externs["thiserror"])], text=True).splitlines()
    native_object = next(name for name in objects if name.endswith(".o"))
    native_bytes = subprocess.check_output(["ar", "p", str(externs["thiserror"]), native_object])
    assert native_bytes.startswith(b"\x7fELF")
    common = ["taskset", "-c", "6,7", "rustc", "--edition=2024", "-C", "opt-level=0", "-C", "debuginfo=0", "-C", "strip=debuginfo", "-L", f"dependency={deps}", "-L", f"dependency={extra}", "-L", f"native={native}"]
    started = time.monotonic()
    record = {
        "status": "building", "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "compiler": subprocess.check_output(["rustc", "-vV"], text=True), "overall_timeout_seconds": 180,
        "scope": "Correctness-only opt0/native-object dependency reuse. No optimization/performance equivalence claim. Supplemental thiserror has metadata/proc-macro events and native ELF evidence, but no completed rlib Cargo event.",
        "inputs": bindings, "steps": [],
        "supplemental_native_object": {"name": native_object, "sha256": hashlib.sha256(native_bytes).hexdigest(), "magic_hex": native_bytes[:4].hex()},
    }
    save(attempt / "build.json", record)

    def build(label, args, envadd):
        remaining = 180 - (time.monotonic() - started)
        assert remaining > 0, "overall compilation bound exhausted"
        env = os.environ.copy()
        env.update(envadd)
        step = {"label": label, "command": args, "environment": envadd, "timeout_seconds": remaining}
        record["steps"].append(step)
        save(attempt / "build.json", record)
        step_start = time.monotonic()
        with open(attempt / (label + ".log"), "w") as log:
            process = subprocess.Popen(args, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                step["returncode"] = process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                step.update(returncode=process.returncode, timeout=True)
        step["seconds"] = time.monotonic() - step_start
        step["log_sha256"] = sha(attempt / (label + ".log"))
        save(attempt / "build.json", record)
        assert step["returncode"] == 0 and not step.get("timeout"), f"{label} failed; retained log"

    try:
        outputs = []
        for variant in ["baseline", "candidate"]:
            core = HERE / variant / "crates/iregi-rust"
            name = "receipt_lazy_" + variant
            output = attempt / ("lib" + name + ".rlib")
            args = common + ["--crate-name", name, "--crate-type", "rlib", str(core / "src/lib.rs"), "-o", str(output)]
            for key, path in externs.items():
                args += ["--extern", f"{key}={path}"]
            build(variant, args, {"CARGO_CRATE_NAME": name, "CARGO_MANIFEST_DIR": str(core)})
            outputs.append(output)
        core = HERE / "test-source/crates/iregi-rust"
        output = attempt / "receipt-tests"
        args = common + ["--crate-name", "receipt_lazy_tests", "--test", str(core / "src/lib.rs"), "-o", str(output)]
        for key, path in externs.items():
            args += ["--extern", f"{key}={path}"]
        build("unit-tests", args, {"CARGO_CRATE_NAME": "receipt_lazy_tests", "CARGO_MANIFEST_DIR": str(core)})
        outputs.append(output)
        output = attempt / "snapshots"
        args = common + ["--crate-name", "receipt_lazy_snapshots", str(HERE / "snapshots.rs"), "-o", str(output), "-L", f"dependency={attempt}"]
        for variant in ["baseline", "candidate"]:
            name = "receipt_lazy_" + variant
            args += ["--extern", f"{name}={attempt / ('lib' + name + '.rlib')}"]
        args += ["--extern", f"symbolica={externs['symbolica']}"]
        build("snapshots", args, {"CARGO_CRATE_NAME": "receipt_lazy_snapshots"})
        outputs.append(output)
        record.update(status="passed", outputs={str(p.relative_to(ROOT)): sha(p) for p in outputs})
    except Exception as error:
        record.update(status="failed", error=str(error))
    finally:
        # Persist terminal outcome before potentially failing provenance checks.
        record.update(seconds=time.monotonic() - started, finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        save(attempt / "build.json", record)
        try:
            verify(bindings)
            record["inputs_unchanged"] = True
        except Exception as error:
            record.update(status="failed", inputs_unchanged=False, provenance_error=str(error))
        save(attempt / "build.json", record)
    print(json.dumps({key: record[key] for key in ["status", "seconds", "steps"]}))
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
