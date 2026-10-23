#!/usr/bin/env python3
"""One separately approved256-bit diagnostic; cannot authorize acceptance."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,time
R=Path.cwd();H=R/'target/public-highpoint/thin-n6-rank7-phase';B=H/'build-001'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
assert len(sys.argv)==1
p=H/'diagnostic-protocol.json';protocol=read(p)
assert protocol['status']=='approved_source_only' and '/root' in protocol['reviewers']
for k,v in {'runtime_bound_seconds':300,'rank':7,'complex_slots':1320,'working_bits':256,'requested_bits':53,'acceptance_qualified':False}.items():assert protocol[k]==v
files={R/n:d for n,d in protocol['artifacts'].items()};files[p]=sha(p)
build=read(B/'build.json');assert build['status']=='passed' and build['inputs_unchanged']
for n,d in build['inputs'].items():assert files[Path(n)]==d
for n,d in build['outputs'].items():assert files[B/n]==d
assert files[B/'build.json']==sha(B/'build.json')
failed_path=H/'comparison-128.json';failed=read(failed_path)
assert failed['status']=='failed' and failed['full_array_original_agreement_qualified'] is False
assert sha(failed_path)==protocol['prior_acceptance_sha256']==files[failed_path]
prior=read(H/'n6-rank7-128-001/run.json');assert prior['status']=='passed' and prior['inputs_unchanged']
assert read(H/'n6-rank7-128-001/result.json')['status']=='all_lanes_success'
for inventory in ['failure_audit_artifacts','supplemental_artifacts']:
 for n,d in protocol[inventory].items():assert files[R/n]==d
assert R/protocol['failure_audit_path'] in files
assert R/protocol['supplemental_summary_path'] in files
def verify():
 for path,d in files.items():assert sha(path)==d,f'changed diagnostic input {path}'
verify();a=H/'n6-rank7-256-diagnostic-001';a.mkdir(exist_ok=False)
fixture=R/'validation/public-highpoint/fixture-conditioned_masses.json';assert fixture in files
command=['taskset','-c','14',str(B/'driver'),str(fixture),'6','7','pv','256','53','1',str(a/'result.json')]
extra={'RAYON_NUM_THREADS':'1','RUST_TEST_THREADS':'1','IREGI_PREPARATION_PROFILE':'1','IREGI_PV_PREPARATION_PROFILE':'1'}
env=os.environ.copy();env.update(extra)
record={'status':'started','acceptance_qualified':False,'bound_seconds':300,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'environment_additions':extra,'license_scope':'User-supplied license sourced privately; contents excluded.','inputs':{str(path):d for path,d in files.items()},'steps':[],'scope':'Separate256-bit diagnostic after failed128 original-reference agreement. Same binary/input/rank/accuracy. Full saved-array precision/original-mode analysis only; cannot upgrade the failed acceptance or change either tolerance.'}
save(a/'run.json',record);start=time.monotonic()
try:
 verify();step={'command':command};record['steps'].append(step);save(a/'run.json',record);t=time.monotonic();remaining=300-(t-start);assert remaining>0,'diagnostic bound exhausted'
 with (a/'step-0.log').open('w') as log:
  try:step['exit_code']=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=remaining).returncode
  except subprocess.TimeoutExpired:step.update(exit_code=None,timeout=True)
 step['seconds']=time.monotonic()-t;save(a/'run.json',record);verify();assert step['exit_code']==0,f'diagnostic child failed with {step["exit_code"]}'
 record.update(status='passed',inputs_unchanged=True)
except Exception as error:
 record.update(status='failed',error=str(error))
 try:verify();record['inputs_unchanged']=True
 except Exception as guard:record.update(inputs_unchanged=False,guard_error=str(guard))
record.update(elapsed_seconds=time.monotonic()-start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),outputs={path.name:sha(path) for path in a.iterdir() if path.name!='run.json'});save(a/'run.json',record)
print(json.dumps({k:record[k] for k in ['status','acceptance_qualified','elapsed_seconds','steps']}));sys.exit(0 if record['status']=='passed' else 1)
