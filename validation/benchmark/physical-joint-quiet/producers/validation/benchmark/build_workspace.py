"""Retain both optimized benchmark binaries from one immutable workspace build.

Run from the project root after sourcing scripts/env.sh. This builds two named
examples, never executes them, and reuses an already validated reference binary.
The running builder and its helpers are copied before the build, independently
of the requested source revision. Failed attempts retain their own manifest and
never replace the standard successful-build manifests.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
EXAMPLES = {"kernel_benchmark", "physical_benchmark"}
IMPORTANT_LIBRARIES = {"iregi_rust", "iregi_masters", "oneloop", "symbolica"}


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def timestamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def freeze_builder(output):
    """Retain actual running helpers, which need not belong to the source commit."""
    output.mkdir(parents=True, exist_ok=False)
    bundle = output / "builder"
    bundle.mkdir()
    files = []
    for name in ["build_workspace.py", "build_physical.py", "run.py"]:
        original = Path(__file__).resolve().with_name(name)
        content = original.read_bytes()
        retained = bundle / name
        retained.write_bytes(content)
        files.append({"original_path": str(original), "retained_path": str(retained),
                      "sha256": hashlib.sha256(content).hexdigest()})
    save(output / "builder.json", {"files": files, "python": sys.version,
                                  "executable": sys.executable})
    return bundle / "build_workspace.py"


def verify_builder(output):
    data = json.loads((output / "builder.json").read_text())
    for entry in data["files"]:
        if digest(entry["retained_path"]) != entry["sha256"]:
            raise ValueError("retained builder source changed: " + entry["retained_path"])
    return data


def verify_snapshot_tree(root, revision):
    """The archive helper verifies tracked bytes; reject extra build inputs too."""
    tracked = set(subprocess.check_output(
        ["git", "ls-tree", "-rz", "--name-only", revision],
    ).decode().rstrip("\0").split("\0"))
    actual = {str(path.relative_to(root)) for path in root.rglob("*")
              if path.is_file() or path.is_symlink()}
    if actual != tracked:
        raise ValueError("snapshot file inventory differs from Git: " + repr({
            "extra": sorted(actual - tracked), "missing": sorted(tracked - actual),
        }))


def build_command(source, jobs, cpus, native_batch):
    if jobs < 1 or not re.fullmatch(r"\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*", cpus):
        raise ValueError("jobs must be positive and cpus must be a taskset CPU list")
    command = ["taskset", "-c", cpus, "cargo", "build", "--workspace",
               "--example", "kernel_benchmark", "--example", "physical_benchmark",
               "--release", "--locked", "--offline", "--jobs", str(jobs),
               "--manifest-path", str(source / "Cargo.toml"),
               "--message-format=json-render-diagnostics", "--timings", "-vv"]
    if native_batch:
        command += ["--features", "iregi-masters/native-batch"]
    return command


def build_environment(root):
    env = os.environ.copy()
    # These flags can override the explicit profile and invalidate comparison.
    for key in ["RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS"]:
        if re.search(r"(?:opt-level|codegen-units|lto)(?:[\s=]|$)",
                     env.get(key, "").replace("\x1f", " ")):
            raise ValueError(f"{key} overrides the required release profile")
    env.update(CARGO_TARGET_DIR=str(root / "target/optimized"),
               CARGO_BUILD_BUILD_DIR=str(root / "target/optimized/cargo-build"),
               CARGO_PROFILE_RELEASE_OPT_LEVEL="3", CARGO_PROFILE_RELEASE_LTO="thin",
               CARGO_PROFILE_RELEASE_CODEGEN_UNITS="1")
    keys = ["RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "CARGO_TARGET_DIR",
            "CARGO_BUILD_BUILD_DIR", "CARGO_BUILD_TARGET", "CARGO_HOME", "RUSTC",
            "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "CC", "CXX", "FC",
            "CARGO_PROFILE_RELEASE_OPT_LEVEL", "CARGO_PROFILE_RELEASE_LTO",
            "CARGO_PROFILE_RELEASE_CODEGEN_UNITS"]
    return env, {key: env.get(key) for key in keys}


def reference_manifest(root, source):
    path = root / "target/benchmark/reference-build.json"
    data = json.loads(path.read_text())
    binary = root / "target/benchmark/iregi-benchmark"
    if digest(binary) != data["binary_sha256"]:
        raise ValueError("existing reference binary does not match its build manifest")
    if digest(source / "validation/benchmark/driver.f90") != data["driver_sha256"]:
        raise ValueError("reference timing driver does not match the selected source revision")
    return path, binary, data


def run_build(command, env, output):
    """Wait for this Cargo process only; record per-child resources on Linux."""
    start = time.monotonic()
    with (output / "cargo.jsonl").open("w") as stdout, (output / "cargo.log").open("w") as stderr:
        child = subprocess.Popen(command, env=env, stdout=stdout, stderr=stderr,
                                 start_new_session=True)
        try:
            _, status, usage = os.wait4(child.pid, 0)
            child.returncode = os.waitstatus_to_exitcode(status)
        finally:
            if child.returncode is None:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                _, status, _ = os.wait4(child.pid, 0)
                child.returncode = os.waitstatus_to_exitcode(status)
    return {"returncode": child.returncode, "wall_seconds": time.monotonic() - start,
            "user_seconds": usage.ru_utime, "system_seconds": usage.ru_stime,
            "max_rss_kib": usage.ru_maxrss,
            "resource_scope": "per-child os.wait4 for Cargo and its descendants; build cost only"}


def inspect_artifacts(path, native_batch):
    examples, libraries, finished = {}, [], False
    for line in path.read_text().splitlines():
        # Cargo -vv forwards build-script stdout as `[package version] text`
        # even when compiler messages use JSON. Preserve it in the raw log;
        # only JSON-object records can carry artifact/finished evidence.
        if not line.lstrip().startswith("{"):
            if not line.strip() or re.match(r"^\[[\w-]+ \d+\.\d+\.\d+[^\]]*\] ", line):
                continue
            raise ValueError("unrecognized text in Cargo artifact stream: " + line[:160])
        event = json.loads(line)
        if event.get("reason") == "build-finished":
            finished = event.get("success") is True
        if event.get("reason") != "compiler-artifact":
            continue
        target = event["target"]
        if "example" in target["kind"] and target["name"] in EXAMPLES:
            if not event.get("executable") or event["profile"]["opt_level"] != "3":
                raise ValueError("benchmark artifact lacks an optimized executable")
            examples[target["name"]] = event
        if "lib" in target["kind"] and target["name"] in IMPORTANT_LIBRARIES:
            libraries.append(event)
    if not finished or set(examples) != EXAMPLES:
        raise ValueError("Cargo did not finish both requested benchmark executables")
    masters = [event for event in libraries if event["target"]["name"] == "iregi_masters"]
    if not masters or any(("native-batch" in event["features"]) != native_batch for event in masters):
        raise ValueError("actual scalar-master Cargo features differ from requested backend")
    return examples, libraries


def retain_file(source, target, expected=None):
    source, target = Path(source), Path(target)
    before = digest(source)
    if expected is not None and before != expected:
        raise ValueError("artifact changed before retention: " + str(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if digest(target) != before or digest(source) != before:
        raise ValueError("artifact changed during retention: " + str(source))
    return {"original_path": str(source), "path": str(target), "sha256": before}


def require_unchanged(data):
    for field in ["source_sha256", "assets_sha256"]:
        if data[field] != data[field + "_before"]:
            raise ValueError(field + " changed during build")


def compatibility_manifest(data, name):
    returncode = data.get("resources", {}).get("returncode")
    if type(returncode) is not int or returncode != 0:
        raise ValueError("compatible manifest requires recorded successful Cargo completion")
    artifact = data["binaries"][name]
    keys = ["status", "started_at", "finished_at", "command", "requested_revision",
            "source_revision", "source_root", "master_backend", "backend_qualification",
            "environment", "profile", "rustc", "cargo", "source_sha256", "assets_sha256",
            "provenance_qualified"]
    result = {key: data[key] for key in keys}
    result.update(schema_version=1, kind="physical-rust-build" if name == "physical_benchmark"
                  else "kernel-rust-build", binary_path=artifact["path"],
                  binary_sha256=artifact["sha256"], returncode=returncode,
                  workspace_build_manifest=data["manifest_path"])
    return result


def publish(root, output, data):
    if data.get("status") != "complete" or data.get("provenance_qualified") is not True:
        raise ValueError("refusing to publish an incomplete build")
    for name, standard in [
        ("kernel_benchmark", root / "target/benchmark/rust-build.json"),
        ("physical_benchmark", root / "target/benchmark/physical/physical-rust-build.json"),
    ]:
        manifest = compatibility_manifest(data, name)
        save(output / (name + "-build.json"), manifest)
        save(standard, manifest)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, help="New retained attempt directory")
    parser.add_argument("--native-batch", action="store_true")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--cpus", default="2,3")
    parser.add_argument("--frozen", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = Path.cwd()
    if not (root / "crates/iregi-cli/Cargo.toml").is_file():
        parser.error("run from the iregi-rust project root")
    output = (args.output or root / "target/benchmark/workspace-builds" /
              (datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
               + f"-{os.getpid()}")).resolve()
    if not output.is_relative_to(root):
        parser.error("retain build artifacts inside the project")
    if not args.frozen:
        frozen = freeze_builder(output)
        command = [sys.executable, str(frozen), "--frozen", "--revision", args.revision,
                   "--output", str(output), "--jobs", str(args.jobs), "--cpus", args.cpus]
        if args.native_batch:
            command.append("--native-batch")
        os.execv(sys.executable, command)

    # Imports resolve from the retained script directory, not the changing worktree.
    from build_physical import physical_asset_hashes, retained_source
    from run import source_hashes
    manifest = output / "workspace-build.json"
    data = {"schema_version": 1, "kind": "workspace-benchmark-build", "status": "preparing",
            "started_at": timestamp(), "finished_at": None, "requested_revision": args.revision,
            "manifest_path": str(manifest), "provenance_qualified": False,
            "master_backend": "RustBatch" if args.native_batch else "SymbolicaBatch",
            "backend_qualification": "Cargo feature fingerprint; runtime backend must also agree.",
            "profile": "release: opt-level=3, lto=thin, codegen-units=1",
            "timing_claim": "Compilation resource usage only; no numerical execution or performance gate."}
    save(manifest, data)
    try:
        data["builder"] = verify_builder(output)
        source, revision = retained_source(root, args.revision)
        verify_snapshot_tree(source, revision)
        data.update(source_root=str(source), source_revision=revision)
        data["command"] = build_command(source, args.jobs, args.cpus, args.native_batch)
        env, data["environment"] = build_environment(root)
        data["rustc"] = subprocess.check_output(["rustc", "--version", "--verbose"], text=True).strip()
        data["cargo"] = subprocess.check_output(["cargo", "--version"], text=True).strip()
        data["source_sha256_before"] = source_hashes(source)
        data["assets_sha256_before"] = physical_asset_hashes(source)
        reference_path, reference_binary, reference = reference_manifest(root, source)
        data["reference"] = retain_file(reference_binary, output / "bin/iregi-benchmark",
                                        reference["binary_sha256"])
        retain_file(reference_path, output / "reference-build.json")
        data["status"] = "building"
        save(manifest, data)
        print(f"Building {revision}; logs and manifest: {output}", flush=True)
        data["resources"] = run_build(data["command"], env, output)
        data["source_sha256"] = source_hashes(source)
        data["assets_sha256"] = physical_asset_hashes(source)
        require_unchanged(data)
        retained_source(root, revision)
        verify_snapshot_tree(source, revision)
        verify_builder(output)
        if data["resources"]["returncode"]:
            raise RuntimeError(f"Cargo failed: {data['resources']['returncode']}")
        examples, libraries = inspect_artifacts(output / "cargo.jsonl", args.native_batch)
        data["cargo_artifacts"] = {"examples": examples, "libraries": libraries}
        data["cargo_verbose_stdout_lines"] = sum(
            bool(line.strip()) and not line.lstrip().startswith("{")
            for line in (output / "cargo.jsonl").read_text().splitlines()
        )
        data["binaries"] = {name: retain_file(event["executable"], output / "bin" / name)
                            for name, event in examples.items()}
        data["archives"] = [retain_file(path, output / "deps" / Path(path).name)
                            for path in sorted({filename for event in libraries
                                                for filename in event["filenames"]
                                                if filename.endswith(".rlib")})]
        data.update(status="complete", provenance_qualified=True, finished_at=timestamp())
        save(manifest, data)
        publish(root, output, data)
    except Exception as error:
        # Preserve a failed attempt even for malformed Cargo/reference metadata.
        data.update(status="failed", error=f"{type(error).__name__}: {error}", provenance_qualified=False)
        print(f"Workspace benchmark build failed: {error}", file=sys.stderr)
    except KeyboardInterrupt:
        data.update(status="interrupted", error="build interrupted", provenance_qualified=False)
    finally:
        data["finished_at"] = timestamp()
        save(manifest, data)
    print(manifest, flush=True)
    return 0 if data["provenance_qualified"] else 1


if __name__ == "__main__":
    def terminated(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, terminated)
    sys.exit(main())
