"""Build both optimized timing executables and retain source/build provenance."""
import argparse
import hashlib
import json
import os
import io
from pathlib import Path
import subprocess
import sys
import tarfile

from run import source_hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-batch", action="store_true", help="Build the opt-in generated Rust scalar-master backend")
    parser.add_argument("--revision", help="Build an isolated committed snapshot while development continues")
    args = parser.parse_args()
    root = Path.cwd()
    out = root / "target/benchmark"
    out.mkdir(parents=True, exist_ok=True)
    source_root = root
    source_revision = None
    if args.revision:
        source_revision = subprocess.check_output(["git", "rev-parse", "--verify", args.revision + "^{commit}"], text=True).strip()
        source_root = out / "sources" / source_revision
        archive_bytes = subprocess.check_output(["git", "archive", source_revision])
        with tarfile.open(fileobj=io.BytesIO(archive_bytes)) as archive:
            if source_root.exists():
                # Never overwrite a modified retained benchmark snapshot.
                for member in archive.getmembers():
                    if member.isfile():
                        path = source_root / member.name
                        if not path.is_file() or path.read_bytes() != archive.extractfile(member).read():
                            raise SystemExit(f"Retained source snapshot differs from {source_revision}: {member.name}")
            else:
                source_root.mkdir(parents=True)
                archive.extractall(source_root, filter="data")
    env = os.environ.copy()
    env["CARGO_TARGET_DIR"] = str(root / "target/optimized")
    env["CARGO_BUILD_BUILD_DIR"] = str(root / "target/optimized/cargo-build")
    command = ["cargo", "build", "--offline", "--locked", "--release", "-p", "iregi-rust", "--example", "kernel_benchmark"]
    if args.revision:
        command += ["--manifest-path", str(source_root / "Cargo.toml")]
    if args.native_batch:
        command += ["--features", "iregi-masters/native-batch"]
    before = source_hashes(source_root)
    subprocess.run(command, check=True, env=env)
    after = source_hashes(source_root)
    if before != after:
        raise SystemExit("Sources changed during build; rebuild a stable source snapshot before publishing timings")
    binary = root / "target/optimized/release/examples/kernel_benchmark"
    data = {"command": command, "master_backend": "RustBatch" if args.native_batch else "SymbolicaBatch", "source_root": str(source_root), "source_revision": source_revision, "environment": {k: env.get(k) for k in ["RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "CARGO_TARGET_DIR", "CARGO_BUILD_BUILD_DIR"]},
            "rustc": subprocess.check_output(["rustc", "--version", "--verbose"], text=True).strip(),
            "source_sha256": after, "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "profile": "release: opt-level=3, thin LTO, codegen-units=1 (workspace Cargo.toml)"}
    (out / "rust-build.json").write_text(json.dumps(data, indent=2) + "\n")
    subprocess.run([sys.executable, "validation/benchmark/build_reference.py"], check=True)


if __name__ == "__main__":
    main()
