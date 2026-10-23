"""Build the optimized in-process physical benchmark and retain provenance.

Run from the project root after sourcing scripts/env.sh. This script builds
only the Rust adapter; it neither runs Symbolica nor times a reference process.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile

sys.dont_write_bytecode = True
from run import source_hashes  # noqa: E402


PHYSICAL_GRAPHS = {
    "ggh": "ggh_top_triangle",
    "gghh": "gghh_top_box",
    "gghhh": "gghhh_top_pentagon",
    "gggg-up": "gggg_up_box",
}


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def physical_asset_hashes(root):
    """Inputs and physical-reference helpers missing from run.source_hashes.

    Benchmark Python helpers are already covered by source_hashes. Require all
    four fixed physical inputs, even if a later timing run selects a subset.
    """
    root = Path(root)
    files = {
        root / "fixtures/models/sm.json",
        root / "validation/physical/canonical-reference-audit.json",
        root / "validation/physical/gghhh-madloop-reference-modes.json",
        root / "validation/reference/capture.py",
    }
    for case, graph in PHYSICAL_GRAPHS.items():
        files.update({
            root / f"examples/graphs/{graph}.dot",
            root / f"validation/physical/{case}-cli-input.json",
            root / f"validation/physical/madloop/fixtures/{case}-helicity-1.json",
        })
    files.update((root / "validation/physical").rglob("*.py"))
    missing = sorted(str(path.relative_to(root)) for path in files if not path.is_file())
    if missing:
        raise ValueError("physical benchmark assets are missing: " + ", ".join(missing))
    return {str(path.relative_to(root)): digest(path) for path in sorted(files)}


def retained_source(root, revision):
    """Materialize or verify the same immutable Git snapshots as build.py."""
    source_revision = subprocess.check_output(
        ["git", "rev-parse", "--verify", revision + "^{commit}"], text=True,
    ).strip()
    source_root = root / "target/benchmark/sources" / source_revision
    archive_bytes = subprocess.check_output(["git", "archive", source_revision])
    with tarfile.open(fileobj=io.BytesIO(archive_bytes)) as archive:
        if source_root.exists():
            for member in archive.getmembers():
                path = source_root / member.name
                if member.isfile():
                    if (path.is_symlink() or not path.is_file()
                            or path.read_bytes() != archive.extractfile(member).read()):
                        raise ValueError(
                            f"Retained source snapshot differs from {source_revision}: {member.name}"
                        )
                elif member.issym():
                    if not path.is_symlink() or os.readlink(path) != member.linkname:
                        raise ValueError(
                            f"Retained source snapshot differs from {source_revision}: {member.name}"
                        )
        else:
            source_root.mkdir(parents=True)
            archive.extractall(source_root, filter="data")
    return source_root, source_revision


def save(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def timestamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-batch", action="store_true",
                        help="Build the opt-in generated Rust scalar-master backend")
    parser.add_argument("--revision",
                        help="Build a retained committed snapshot while development continues")
    args = parser.parse_args(argv)
    root = Path.cwd()
    if not (root / "crates/iregi-cli/Cargo.toml").is_file():
        parser.error("run this script from the iregi-rust project root")
    out = root / "target/benchmark/physical"
    out.mkdir(parents=True, exist_ok=True)
    manifest = out / "physical-rust-build.json"
    binary = root / "target/optimized/release/examples/physical_benchmark"
    env = os.environ.copy()
    env["CARGO_TARGET_DIR"] = str(root / "target/optimized")
    env["CARGO_BUILD_BUILD_DIR"] = str(root / "target/optimized/cargo-build")
    command = ["cargo", "build", "--offline", "--locked", "--release",
               "-p", "iregi-cli", "--example", "physical_benchmark"]
    data = {
        "schema_version": 1, "kind": "physical-rust-build", "status": "preparing",
        "started_at": timestamp(), "finished_at": None, "command": command,
        "requested_revision": args.revision, "source_revision": None,
        "source_root": str(root), "binary_path": str(binary), "binary_sha256": None,
        "master_backend": "RustBatch" if args.native_batch else "SymbolicaBatch",
        "backend_qualification": "Build configuration; runtime output identifies the selected backend.",
        "environment": {key: env.get(key) for key in [
            "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "CARGO_TARGET_DIR",
            "CARGO_BUILD_BUILD_DIR", "CARGO_BUILD_TARGET", "CARGO_PROFILE_RELEASE_OPT_LEVEL",
            "CARGO_PROFILE_RELEASE_LTO", "CARGO_PROFILE_RELEASE_CODEGEN_UNITS",
        ]},
        "profile": "release; workspace Cargo.toml and recorded environment define compiler settings",
        "provenance_qualified": False,
    }
    save(manifest, data)
    source_root = root
    try:
        if args.revision:
            source_root, source_revision = retained_source(root, args.revision)
            data.update(source_root=str(source_root), source_revision=source_revision)
            command += ["--manifest-path", str(source_root / "Cargo.toml")]
        else:
            data["source_revision"] = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True,
            ).strip()
        if args.native_batch:
            command += ["--features", "iregi-masters/native-batch"]
        if env.get("CARGO_BUILD_TARGET"):
            # Explicit cross/native target selection changes Cargo's output path.
            binary = (root / "target/optimized" / env["CARGO_BUILD_TARGET"]
                      / "release/examples/physical_benchmark")
            data["binary_path"] = str(binary)
        example = source_root / "crates/iregi-cli/examples/physical_benchmark.rs"
        if not example.is_file():
            raise ValueError(f"physical benchmark example is absent from {source_root}")
        data["rustc"] = subprocess.check_output(
            ["rustc", "--version", "--verbose"], text=True,
        ).strip()
        data["cargo"] = subprocess.check_output(["cargo", "--version"], text=True).strip()
        data["source_sha256_before"] = source_hashes(source_root)
        data["assets_sha256_before"] = physical_asset_hashes(source_root)
        data["status"] = "building"
        save(manifest, data)
        completed = subprocess.run(command, env=env, check=False)
        data["returncode"] = completed.returncode
        data["source_sha256"] = source_hashes(source_root)
        data["assets_sha256"] = physical_asset_hashes(source_root)
        data["source_changed_during_build"] = (
            data["source_sha256_before"] != data["source_sha256"]
        )
        data["assets_changed_during_build"] = (
            data["assets_sha256_before"] != data["assets_sha256"]
        )
        if completed.returncode:
            raise RuntimeError(f"Cargo build failed with exit code {completed.returncode}")
        data["binary_sha256"] = digest(binary)
        if data["source_changed_during_build"] or data["assets_changed_during_build"]:
            raise RuntimeError(
                "Sources or physical assets changed during build; rebuild a stable snapshot "
                "before publishing timings"
            )
        data["status"] = "complete"
        data["provenance_qualified"] = True
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, tarfile.TarError) as error:
        data["status"] = "failed"
        data["error"] = str(error)
        print(f"physical benchmark build failed: {error}", file=sys.stderr)
    except KeyboardInterrupt:
        data["status"] = "interrupted"
        data["error"] = "build interrupted"
    finally:
        data["finished_at"] = timestamp()
        save(manifest, data)
    print(manifest)
    return 0 if data["provenance_qualified"] else 1


if __name__ == "__main__":
    sys.exit(main())
