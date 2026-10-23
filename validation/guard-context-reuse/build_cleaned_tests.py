#!/usr/bin/env python3
from pathlib import Path
import os,json,time,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2];E=ROOT/'validation/guard-context-reuse';OUT=ROOT/'target/guard-context-reuse';source=OUT/'current-cleaned'
os.sched_setaffinity(0,{10,11});cmd=json.loads((E/'cleaned-unit-command.json').read_text());env=dict(os.environ,CARGO_CRATE_NAME='iregi_rust',CARGO_MANIFEST_DIR=str(source/'crates/iregi-rust'),CARGO_PKG_NAME='iregi-rust',CARGO_PKG_VERSION='0.1.0');start=time.monotonic()
with (E/'cleaned-unit-compile.log').open('w') as log:code=subprocess.run(cmd,env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
r={'command':cmd,'exit_code':code,'seconds':time.monotonic()-start,'binary_sha256':hashlib.sha256((OUT/'current-cleaned-unit').read_bytes()).hexdigest() if not code else None,'source_sha256':{str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}}
(E/'cleaned-unit-compile.json').write_text(json.dumps(r,indent=2)+'\n');print('current unit',code,flush=True);raise SystemExit(code)
