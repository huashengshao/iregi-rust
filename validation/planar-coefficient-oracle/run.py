"""Bounded coefficient oracle with reversible, hash-verified generated output isolation."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, signal, subprocess, time
root=Path.cwd();base=root/'target/planar-coefficient-oracle';candidate=root/'target/planar-adoption'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
load=lambda p:json.loads(p.read_text())
build=load(candidate/'build.json');binary=candidate/'core-tests'
assert build['exit_code']==0 and sha(binary)==build['binary_sha256']
source=candidate/'source-snapshot'
for p,digest in build['source_hashes'].items():assert sha(source/p)==digest
assert Path(build['environment']['CARGO_MANIFEST_DIR']).resolve()==root/'crates/iregi-rust'
reference=root/'target/reference/iregi-reference-original';assert reference.is_file()
variants=['base','translated','order_reversed','loop_reversed']
output=root/'validation/pv-high-rank/oracle-runs'
paths=[output/f'n{n}-{v}-rank2.json' for n in range(1,6) for v in variants]
backups=base/'originals';captured=base/'results'
assert not backups.exists() and not captured.exists() and not (base/'run.json').exists()
backups.mkdir();captured.mkdir();output.mkdir(parents=True,exist_ok=True)
original={str(p):sha(p) if p.exists() else None for p in paths}
for p in paths:
 if p.exists():shutil.copy2(p,backups/p.name)
for p in paths:
 if p.exists():assert sha(backups/p.name)==original[str(p)]
command=[str(binary),'pv::tests::original_iregi_cartesian_moments','--exact','--ignored','--nocapture','--test-threads=1']
env=os.environ.copy();env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',IREGI_PV_ORACLE_N='1,2,3,4,5',IREGI_PV_ORACLE_RANK='2',IREGI_PV_ORACLE_VARIANT=','.join(variants))
record={'status':'running','command':command,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'timeout_seconds':180,'cpu_affinity':sorted(os.sched_getaffinity(0)),'binary_sha256':sha(binary),
 'build_manifest_sha256':sha(candidate/'build.json'),'reference_binary_sha256':sha(reference),
 'runner_sha256':sha(Path(__file__)),'original_hashes':original,
 'environment':{k:env[k] for k in ['RAYON_NUM_THREADS','OMP_NUM_THREADS','IREGI_PV_ORACLE_N','IREGI_PV_ORACLE_RANK','IREGI_PV_ORACLE_VARIANT']},
 'scope':'Exact numeric-specialized Symbolica PV coefficients with original Fortran scalar master leaves, compared with original IREGI IBP tensor arrays; not the public Rust Workspace or native master path.'}
(base/'run.json').write_text(json.dumps(record,indent=2)+'\n')
child=None;code=1;error=None;start=time.monotonic()
try:
 for p in paths:
  if p.exists():assert sha(p)==original[str(p)];p.unlink()
 with (base/'run.log').open('w') as log:
  child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
  try:code=child.wait(timeout=180)
  except subprocess.TimeoutExpired:
   os.killpg(child.pid,signal.SIGTERM)
   try:child.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
   code=124
 for p in paths:
  if p.exists():shutil.copy2(p,captured/p.name)
except BaseException as e:
 error=repr(e)
finally:
 if child is not None and child.poll() is None:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
 for p in paths:
  old=backups/p.name
  if original[str(p)] is not None:shutil.copy2(old,p)
  elif p.exists():p.unlink()
 record['original_hashes_restored']=all((sha(p) if p.exists() else None)==original[str(p)] for p in paths)
 record['source_hashes_unchanged']=all(sha(source/p)==digest for p,digest in build['source_hashes'].items())
 record['binary_unchanged']=sha(binary)==record['binary_sha256']
 record['reference_unchanged']=sha(reference)==record['reference_binary_sha256']
 record.update(exit_code=code,error=error,elapsed_seconds=time.monotonic()-start,
  finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
valid=code==0 and error is None
rows=[]
for n in range(1,6):
 for variant in variants:
  p=captured/f'n{n}-{variant}-rank2.json'
  if not p.exists():valid=False;continue
  r=load(p)
  valid=valid and r['status']=='passed' and r['propagators']==n and r['rank']==2 and r['variant']==variant and r['moments']==15
  valid=valid and r['reference']['stable'] is True and len(r['rust_original_master_moments_normalized'])==15 and r['discrepancies']==[]
  rows.append({'file':p.name,'sha256':sha(p),'status':r['status'],'max_mixed_error':r.get('max_mixed_error')})
record['results']=rows
record['status']='passed' if valid and len(rows)==20 else 'timeout' if code==124 else 'failed'
if not all(record[k] for k in ['original_hashes_restored','source_hashes_unchanged','binary_unchanged','reference_unchanged']):record['status']='invalid-provenance'
(base/'run.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['status','exit_code','elapsed_seconds','original_hashes_restored']}),flush=True)
print((base/'run.log').read_text()[-3000:],flush=True)
raise SystemExit(0 if record['status']=='passed' else 1)
