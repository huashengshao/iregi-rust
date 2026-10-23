#!/usr/bin/env python3
"""Compile independent unit binaries from copies; original archives stay frozen."""
from pathlib import Path
import os,json,hashlib,subprocess,shutil,time,concurrent.futures
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'target/monitor-roundoff-cache';E=ROOT/'validation/monitor-roundoff-cache';D=ROOT/'target/stack-reuse-current-workspace/deps';S=ROOT/'target/cargo-build/debug/deps'
os.sched_setaffinity(0,{10,11})
base=['rustc','--test','--edition=2024','-C','opt-level=0','-L',f'dependency={D}','-L',f'dependency={S}','-L',f'native={ROOT}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
for name,path in [('iregi_masters',D/'libiregi_masters-0d5459afd211649c.rlib'),('oneloop',D/'liboneloop-8562c3cbbf948c0e.rlib'),('symbolica',D/'libsymbolica-5cca42ee48491872.rlib'),('serde',S/'libserde-fc3dcd4b8c210596.rlib'),('serde_json',S/'libserde_json-3b583d0e8aa0facc.rlib'),('thiserror',S/'libthiserror-b877110d28821624.rlib')]:base+=['--extern',f'{name}={path}']
def build(variant):
 copy=OUT/(variant+'-tests-source')
 if copy.exists():raise RuntimeError(f'refusing to replace {copy}; inspect previous build first')
 shutil.copytree(OUT/variant,copy)
 src=copy/'crates/iregi-rust/src/lib.rs'
 if variant=='candidate':
  stability=src.parent/'stability.rs';text=stability.read_text();assert text.rstrip().endswith('}')
  stability.write_text(text.rstrip()[:-1]+'\n'+(E/'cache_tests.rs').read_text()+'\n}\n')
 binary=OUT/(variant+'-unit');cmd=base+['--crate-name','cache_'+variant+'_unit',str(src),'-o',str(binary)]
 env=dict(os.environ,CARGO_CRATE_NAME='iregi_rust',CARGO_MANIFEST_DIR=str(src.parent.parent),CARGO_PKG_NAME='iregi-rust',CARGO_PKG_VERSION='0.1.0');start=time.monotonic()
 with (E/f'{variant}-unit-compile.log').open('w') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 rec={'command':cmd,'exit_code':r.returncode,'seconds':time.monotonic()-start,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest() if r.returncode==0 else None,'stability_source_sha256':hashlib.sha256((src.parent/'stability.rs').read_bytes()).hexdigest()};(E/f'{variant}-unit-compile.json').write_text(json.dumps(rec,indent=2)+'\n');print(variant,r.returncode,flush=True);return r.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:codes=list(pool.map(build,['baseline','candidate']))
raise SystemExit(max(codes))
