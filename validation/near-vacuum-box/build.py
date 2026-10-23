#!/usr/bin/env python3
"""Freeze and compile optional validation examples against retained dependencies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ARCHIVES={
    "oneloop":"target/d0-node-probe/liboneloop_baseline.rlib",
    "symbolica":"target/d0-node-probe/deps/libsymbolica-5cca42ee48491872.rlib",
    "serde_json":"target/d0-node-probe/deps/libserde_json-6ed7d47d62d32cd7.rlib",
}

def sha(path):
    digest=hashlib.sha256()
    with (ROOT/path).open("rb") as source:
        for block in iter(lambda:source.read(1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("variant")
    parser.add_argument("--driver",choices=["validate","heterogeneous","unequal"],default="validate")
    parser.add_argument("--record-only",action="store_true")
    args=parser.parse_args()
    if not args.variant.replace("_","").isalnum():parser.error("use an alphanumeric variant name")
    snapshot=Path(f"target/near-vacuum-validation/stage-{args.variant}-source")
    binary=Path(f"target/near-vacuum-validation/near_vacuum_{args.variant}")
    driver=f"near_vacuum_{args.driver}.rs"
    sources=[driver,"support/near_vacuum_box.rs","support/d0_near_vacuum_oracle.rs"]
    if not args.record_only:
        if (ROOT/snapshot).exists() or (ROOT/binary).exists():parser.error("frozen variant already exists")
        (ROOT/snapshot/"support").mkdir(parents=True)
        for source in sources:shutil.copyfile(ROOT/"crates/iregi-rust/examples"/source,ROOT/snapshot/source)
    name=f"near_vacuum_{args.variant}"
    command=["taskset","-c","4,5","rustc","--crate-name",name,"--edition=2024",str(snapshot/driver),
      "-L","dependency=target/d0-node-probe/deps","-L","dependency=target/cargo-build/debug/deps",
      "-L","native=target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib"]
    for crate,path in ARCHIVES.items():command.extend(["--extern",f"{crate}={path}"])
    command.extend(["-o",str(binary)])
    if not args.record_only:
        with (HERE/f"{args.variant}-build.log").open("w") as log:
            subprocess.run(command,cwd=ROOT,env=os.environ|{"CARGO_CRATE_NAME":name},stdout=log,stderr=subprocess.STDOUT,check=True)
    paths=[str(snapshot/source) for source in sources]+list(ARCHIVES.values())+[str(binary)]
    record={"rustc":subprocess.check_output(["rustc","--version"],text=True).strip(),
      "source_scope":"Frozen validation-only example; baseline nofeatures oneloop and pre-default-stack Symbolica retained dependencies.",
      "driver":args.driver,"build_command":command,"build_environment":{"CARGO_CRATE_NAME":name},"sha256":{path:sha(path) for path in paths},
      "parent_dependency_provenance":"target/d0-node-probe/source-inputs.json"}
    path=HERE/f"{args.variant}-build.json"
    if path.exists():parser.error("build manifest already exists")
    path.write_text(json.dumps(record,indent=2)+"\n")
    print(str(path.relative_to(ROOT)))

if __name__=="__main__":main()
