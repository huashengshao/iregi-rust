#!/usr/bin/env python3
"""One immutable rank7 capture; no implicit retries or numerical specialization."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, time
R=Path.cwd();H=R/'target/public-highpoint/thin-n6-rank7-phase';B=H/'build-001'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
assert sys.argv[1:] in [['128'],['256']];bits=int(sys.argv[1]);protocol=json.loads((H/'protocol.json').read_text())
assert protocol['status']=='approved_source_only' and '/root' in protocol['reviewers']
assert protocol['runtime_bound_seconds']==300 and protocol['rank']==7 and protocol['complex_slots']==1320
build=json.loads((B/'build.json').read_text());assert build['status']=='passed' and build['inputs_unchanged']
files={Path(n):d for n,d in build['inputs'].items()}
for n,d in protocol['artifacts'].items():assert files[R/n]==d
assert files[H/'protocol.json']==sha(H/'protocol.json')
files[B/'build.json']=sha(B/'build.json')
for n,d in build['outputs'].items():files[B/n]=d
if bits==256:
 p=H/'comparison-128.json';previous=json.loads(p.read_text())
 assert previous['status']=='passed' and previous['full_array_original_agreement_qualified'] and not previous['precision_convergence_qualified']
 assert [r['working_bits'] for r in previous['records']]==[128]
 for n,d in previous['input_sha256'].items():
  p0=Path(n);assert p0 not in files or files[p0]==d;files[p0]=d
 files[p]=sha(p)
def verify():
 for p,d in files.items():assert sha(p)==d,f'changed input {p}'
verify();a=H/f'n6-rank7-{bits}-001';a.mkdir(exist_ok=False)
fixture=R/'validation/public-highpoint/fixture-conditioned_masses.json';assert fixture in files
command=['taskset','-c','14',str(B/'driver'),str(fixture),'6','7','pv',str(bits),'53','1',str(a/'result.json')]
extra={'RAYON_NUM_THREADS':'1','RUST_TEST_THREADS':'1','IREGI_PREPARATION_PROFILE':'1','IREGI_PV_PREPARATION_PROFILE':'1'}
env=os.environ.copy();env.update(extra)
record={'status':'started','bound_seconds':300,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'environment_additions':extra,'license_scope':'User-supplied license sourced privately; contents excluded.','inputs':{str(p):d for p,d in files.items()},'steps':[],'scope':'Private retained N6 rank7, one base lane, all330moments/1320native complex Laurent slots. No retries, production adoption, other domains, numerical Dual/lifecycle or timing gate.'}
save(a/'run.json',record);start=time.monotonic()
try:
 verify();step={'command':command};record['steps'].append(step);save(a/'run.json',record);t=time.monotonic();remaining=300-(t-start);assert remaining>0,'runtime bound exhausted'
 with (a/'step-0.log').open('w') as log:
  try:step['exit_code']=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=remaining).returncode
  except subprocess.TimeoutExpired:step.update(exit_code=None,timeout=True)
 step['seconds']=time.monotonic()-t;save(a/'run.json',record);verify();assert step['exit_code']==0,f'child failed with {step["exit_code"]}'
 record.update(status='passed',inputs_unchanged=True)
except Exception as error:
 record.update(status='failed',error=str(error))
 try:verify();record['inputs_unchanged']=True
 except Exception as guard:record.update(inputs_unchanged=False,guard_error=str(guard))
record.update(elapsed_seconds=time.monotonic()-start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),outputs={p.name:sha(p) for p in a.iterdir() if p.name!='run.json'});save(a/'run.json',record)
print(json.dumps({k:record[k] for k in ['status','elapsed_seconds','steps']}));sys.exit(0 if record['status']=='passed' else 1)
