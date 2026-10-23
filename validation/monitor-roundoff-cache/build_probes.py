#!/usr/bin/env python3
from pathlib import Path
import os,json,subprocess,hashlib,time,datetime,concurrent.futures
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'target/monitor-roundoff-cache';E=ROOT/'validation/monitor-roundoff-cache';D=ROOT/'target/stack-reuse-current-workspace/deps';S=ROOT/'target/cargo-build/debug/deps'
os.sched_setaffinity(0,{10,11})
base=['rustc','--edition=2024','-C','opt-level=3','-C','codegen-units=16','-L',f'dependency={OUT}','-L',f'dependency={D}','-L',f'dependency={S}','-L',f'native={ROOT}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
for name,path in [('iregi_cache_baseline',OUT/'libiregi_cache_baseline.rlib'),('iregi_cache_candidate',OUT/'libiregi_cache_candidate.rlib'),('iregi_masters',D/'libiregi_masters-0d5459afd211649c.rlib'),('symbolica',D/'libsymbolica-5cca42ee48491872.rlib')]:base+=['--extern',f'{name}={path}']
def build(pair):
 name,source=pair;cmd=base+['--crate-name','cache_'+name,str(source),'-o',str(OUT/name)];start=time.monotonic()
 env=dict(os.environ,CARGO_CRATE_NAME='monitor_cache_probe',CARGO_MANIFEST_DIR=str(ROOT/'crates/iregi-rust'))
 with (E/f'{name}-compile.log').open('w') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 d={'command':cmd,'exit_code':r.returncode,'seconds':time.monotonic()-start,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'binary_sha256':hashlib.sha256((OUT/name).read_bytes()).hexdigest() if not r.returncode else None};(E/f'{name}-compile.json').write_text(json.dumps(d,indent=2)+'\n');print(name,r.returncode,flush=True);return r.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:codes=list(pool.map(build,[('protocol',OUT/'protocol.rs'),('performance',E/'performance_probe.rs')]))
raise SystemExit(max(codes))
