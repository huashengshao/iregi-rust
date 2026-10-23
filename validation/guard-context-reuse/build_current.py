#!/usr/bin/env python3
"""Compile isolated baseline/candidate cores against identical frozen dependencies."""
from pathlib import Path
import os,json,hashlib,subprocess,time,datetime,concurrent.futures
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'target/guard-context-reuse'; EVIDENCE=ROOT/'validation/guard-context-reuse'
DEPS=ROOT/'target/stack-reuse-current-workspace/deps'; SHARED=ROOT/'target/cargo-build/debug/deps'
externs={'symbolica':DEPS/'libsymbolica-5cca42ee48491872.rlib','iregi_masters':DEPS/'libiregi_masters-0d5459afd211649c.rlib','serde':SHARED/'libserde-fc3dcd4b8c210596.rlib','thiserror':SHARED/'libthiserror-b877110d28821624.rlib'}
common=['--edition=2024','-C','opt-level=3','-C','codegen-units=16','-L',f'dependency={DEPS}','-L',f'dependency={SHARED}','-L',f'native={ROOT}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
for name,path in externs.items():common+=['--extern',f'{name}={path}']
def build(variant):
 name='iregi_guard_current_'+variant;lib=OUT/f'lib{name}.rlib';src=OUT/('current-'+variant)/'crates/iregi-rust/src/lib.rs'
 cmd=['rustc','--crate-name',name,'--crate-type','rlib',str(src),*common,'-o',str(lib)]
 env=dict(os.environ,CARGO_MANIFEST_DIR=str(src.parent.parent),CARGO_PKG_NAME='iregi-rust',CARGO_CRATE_NAME='iregi_rust',CARGO_PKG_VERSION='0.1.0')
 start=time.monotonic()
 with (EVIDENCE/f'current-{variant}-compile.log').open('w') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 rec={'command':cmd,'exit_code':r.returncode,'seconds':time.monotonic()-start,'binary':str(lib.relative_to(ROOT)),'binary_sha256':hashlib.sha256(lib.read_bytes()).hexdigest() if r.returncode==0 else None}
 (EVIDENCE/f'current-{variant}-compile.json').write_text(json.dumps(rec,indent=2)+'\n');print(variant,r.returncode,flush=True);return rec
os.sched_setaffinity(0,{10,11})
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=dict(zip(['baseline','candidate'],pool.map(build,['baseline','candidate'])))
record={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'compiled_not_run' if all(r['exit_code']==0 for r in results.values()) else 'compile_failed','cpu_affinity':[10,11],'scope':'current d1a4b8e baseline versus adopted guard-context source; frozen full-feature dependencies; matching flags','dependencies_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in externs.values()},'variants':results}
(EVIDENCE/'current-build.json').write_text(json.dumps(record,indent=2)+'\n');raise SystemExit(0 if record['status']=='compiled_not_run' else 1)
