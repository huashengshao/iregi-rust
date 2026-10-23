#!/usr/bin/env python3
import pathlib,json,hashlib,subprocess,os,time,datetime,sys
R=pathlib.Path.cwd();H=R/'target/public-highpoint/thin-n6-mask';B=H/'build-001';A=H/'lifecycle-build-001'
def sha(p):return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
build=json.loads((B/'build.json').read_text());assert build['status']=='passed'
files={pathlib.Path(p):h for p,h in build['inputs'].items()}
for name,h in build['outputs'].items():files[B/name]=h
for p in [B/'build.json',H/'lifecycle_driver.rs',pathlib.Path(__file__).resolve(),H/'lifecycle-protocol.json']:files[p]=sha(p)
def verify():
 for p,h in files.items():assert sha(p)==h,f'changed {p}'
verify();A.mkdir(exist_ok=False)
old=next(step['command'] for step in build['steps'] if step['name']=='driver')
args=[str(H/'lifecycle_driver.rs') if a==str(H/'driver.rs') else str(A/'driver') if a==str(B/'driver') else 'thin_n6_lifecycle_driver' if a=='thin_n6_driver' else a for a in old]
record={'status':'started','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bound_seconds':30,'inputs':{str(p):h for p,h in files.items()},'command':args,'scope':'Link only source-reviewed lifecycle driver against unchanged frozen mask core/native closure; no core rebuild or performance claim.'};save(A/'build.json',record);start=time.monotonic()
try:
 env=os.environ.copy();env.update(CARGO_CRATE_NAME='iregi_rust',CARGO_MANIFEST_DIR=str(H/'core/crates/iregi-rust'))
 with open(A/'driver.log','w') as log:
  try:record['exit_code']=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30).returncode
  except subprocess.TimeoutExpired:record.update(exit_code=None,timeout=True)
 verify();record['inputs_unchanged']=True;assert record['exit_code']==0,'driver link failed'
 record.update(status='passed',outputs={'driver':sha(A/'driver'),'driver.log':sha(A/'driver.log')})
except Exception as error:record.update(status='failed',error=str(error))
record['elapsed_seconds']=time.monotonic()-start;save(A/'build.json',record);print(json.dumps({k:record.get(k) for k in ['status','elapsed_seconds','exit_code','error']}));sys.exit(0 if record['status']=='passed' else 1)
