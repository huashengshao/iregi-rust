#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,time,os,datetime
R=Path.cwd();H=R/'target/public-highpoint/thin-n6';B=H/'build-002';L=H/'mixed-cofactor';A=L/'attempt-001';A.mkdir(exist_ok=False)
def sha(p):return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
build=json.loads((B/'build.json').read_text());assert build['status']=='passed';files={Path(p):h for p,h in build['inputs'].items()}
for p in [B/'build.json',B/'libiregi_rust.rlib',L/'proof.rs',L/'run.py',R/'validation/public-highpoint/fixture-conditioned_masses.json',R/'dependencies/symbolica/lib/numerica/src/tensors/matrix.rs']:files[p]=sha(p)
def verify():
 for p,h in files.items():assert sha(p)==h,f'changed {p}'
verify();deps=R/'target/e6-direct-n2/deps';native=R/'target/e6-direct-n2/native';extra=R/'target/core-fused-cse-census/supplemental-deps'
record={'status':'started','scope':'Exact mixed-Dual cofactor negative/positive controls; no numerical master evaluation.','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':{str(p):h for p,h in files.items()},'steps':[]};save(A/'run.json',record)
commands=[('compile',['taskset','-c','14,15','rustc','--edition=2024','-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo','--crate-name','thin_n6_mixed_cofactor',str(L/'proof.rs'),'-o',str(A/'census'),'-L',f'dependency={deps}','-L',f'dependency={extra}','-L',f'native={native}','--extern',f'iregi_rust={B}/libiregi_rust.rlib','--extern',f'symbolica={deps}/libsymbolica-06e42762cabb77d9.rlib','--extern',f'serde_json={deps}/libserde_json-d657c5438f354a41.rlib']),('exact',['taskset','-c','14',str(A/'census'),str(A/'result.json')])]
env=os.environ.copy();env['RAYON_NUM_THREADS']='1'
try:
 for name,cmd in commands:
  verify();step={'label':name,'command':cmd,'bound_seconds':30};record['steps'].append(step);save(A/'run.json',record);t=time.monotonic()
  with open(A/(name+'.log'),'w') as log:
   try:step['exit_code']=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30).returncode
   except subprocess.TimeoutExpired:step.update(exit_code=None,timeout=True)
  step['seconds']=time.monotonic()-t;save(A/'run.json',record);assert step['exit_code']==0,f'{name} failed';verify()
  if name=='compile':files[A/'census']=sha(A/'census');record['binary_sha256']=sha(A/'census')
 record.update(status='passed',inputs_unchanged=True)
except Exception as e:record.update(status='failed',error=str(e))
record.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),outputs={p.name:sha(p) for p in A.iterdir() if p.name!='run.json'});save(A/'run.json',record);print(json.dumps({'status':record['status'],'steps':record['steps']}))
