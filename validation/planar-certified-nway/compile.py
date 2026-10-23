from pathlib import Path
import json,hashlib,subprocess,time,os
base=Path.cwd()/'target/planar-certified';old=json.loads((base/'compile-phase.json').read_text()); cmd=[s.replace('/phase-source/','/nway-normalized-source/').replace('metadata=planar_phase','metadata=planar_nway_normalized').replace('/core-tests-phase','/core-tests-nway-normalized') for s in old['command']]
source=base/'nway-normalized-source'; hash_sources=lambda:{str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.rglob('*.rs'))}; before=hash_sources()
for dep in old['dependencies'].values():assert hashlib.sha256(Path(dep['path']).read_bytes()).hexdigest()==dep['sha256'],dep['path']
env=os.environ.copy();env.update(CARGO_MANIFEST_DIR=str(Path.cwd()/'crates/iregi-rust'),CARGO_CRATE_NAME='iregi_rust');start=time.monotonic()
with (base/'compile-nway-normalized.log').open('w') as f:r=subprocess.run(['taskset','--cpu-list','16,17']+cmd,stdout=f,stderr=subprocess.STDOUT,env=env)
record={'command':cmd,'environment':{k:env[k] for k in ['CARGO_MANIFEST_DIR','CARGO_CRATE_NAME']},'cpu_affinity':[16,17],'source_hashes':before,'source_hashes_after':hash_sources(),'dependencies':old['dependencies'],'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-start}
assert before==record['source_hashes_after'];record['dependencies_unchanged']=all(hashlib.sha256(Path(d['path']).read_bytes()).hexdigest()==d['sha256'] for d in old['dependencies'].values())
if r.returncode==0:record['binary_sha256']=hashlib.sha256((base/'core-tests-nway-normalized').read_bytes()).hexdigest()
(base/'compile-nway-normalized.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k] for k in ['exit_code','elapsed_seconds','dependencies_unchanged','binary_sha256'] if k in record}),flush=True);print((base/'compile-nway-normalized.log').read_text()[-6000:]);raise SystemExit(r.returncode)
