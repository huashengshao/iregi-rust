"""Build both optimized timing executables and retain source/build provenance."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from run import source_hashes


def main():
    root = Path.cwd()
    out = root / "target/benchmark"
    out.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CARGO_TARGET_DIR"] = str(root / "target/optimized")
    env["CARGO_BUILD_BUILD_DIR"] = str(root / "target/optimized/cargo-build")
    command = ["cargo", "build", "--offline", "--locked", "--release", "-p", "iregi-rust", "--example", "kernel_benchmark"]
    before = source_hashes()
    subprocess.run(command, check=True, env=env)
    after = source_hashes()
    if before != after:
        raise SystemExit("Sources changed during build; rebuild a stable source snapshot before publishing timings")
    binary = root / "target/optimized/release/examples/kernel_benchmark"
    data = {"command": command, "environment": {k: env.get(k) for k in ["RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "CARGO_TARGET_DIR", "CARGO_BUILD_BUILD_DIR"]},
            "rustc": subprocess.check_output(["rustc", "--version", "--verbose"], text=True).strip(),
            "source_sha256": after, "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "profile": "release: opt-level=3, thin LTO, codegen-units=1 (workspace Cargo.toml)"}
    (out / "rust-build.json").write_text(json.dumps(data, indent=2) + "\n")
    subprocess.run([sys.executable, "validation/benchmark/build_reference.py"], check=True)


if __name__ == "__main__":
    main()
