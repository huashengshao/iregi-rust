from pathlib import Path
import json,hashlib,subprocess,time,os
root=Path.cwd();base=root/'target/planar-integrated';source=base/'source-snapshot';deps=json.loads((base/'frozen-dependencies.json').read_text())
cmd=['rustc','--test','--crate-name','iregi_rust','--edition=2024','-C','opt-level=2','-C','metadata=planar_integrated_01',str(source/'crates/iregi-rust/src/lib.rs'),'-L','dependency='+str(base/'frozen-deps'),'-L','dependency='+str(root/'target/stack-reuse-current-workspace/deps'),'-L','dependency='+str(root/'target/cargo-build/debug/deps'),'-L','native='+str(root/'target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib')]
for name,dep in deps.items():assert hashlib.sha256(Path(dep['path']).read_bytes()).hexdigest()==dep['sha256'];cmd.extend(['--extern',name+'='+dep['path']])
cmd.extend(['-o',str(base/'core-tests')]);env=os.environ.copy();env.update(CARGO_MANIFEST_DIR=str(root/'crates/iregi-rust'),CARGO_CRATE_NAME='iregi_rust')
hashes=lambda:{str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.rglob('*')) if p.is_file()}
record={'command':cmd,'environment':{k:env[k] for k in ['CARGO_MANIFEST_DIR','CARGO_CRATE_NAME']},'cpu_affinity':[16,17],'source_hashes':hashes(),'dependencies':deps}
start=time.monotonic()
with (base/'build.log').open('w') as f:r=subprocess.run(['taskset','--cpu-list','16,17']+cmd,stdout=f,stderr=subprocess.STDOUT,env=env)
record.update(exit_code=r.returncode,elapsed_seconds=time.monotonic()-start,source_hashes_after=hashes());assert record['source_hashes']==record['source_hashes_after'];record['dependencies_unchanged']=all(hashlib.sha256(Path(d['path']).read_bytes()).hexdigest()==d['sha256'] for d in deps.values())
if r.returncode==0:record['binary_sha256']=hashlib.sha256((base/'core-tests').read_bytes()).hexdigest()
(base/'build.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k] for k in ['exit_code','elapsed_seconds','dependencies_unchanged','binary_sha256'] if k in record}),flush=True);print((base/'build.log').read_text()[-7000:]);raise SystemExit(r.returncode)
