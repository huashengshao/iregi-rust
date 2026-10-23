#!/usr/bin/env python3
"""Exact-only census, two conventions within one 120s topology budget."""
import datetime, hashlib, json, pathlib, subprocess, sys, time
ROOT=pathlib.Path.cwd();HERE=ROOT/'target/core-fused-cse-census'
def sha(p): return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
build=HERE/'build-002';proof=json.loads((build/'build.json').read_text());assert proof['status']=='passed'
n,rank=map(int,sys.argv[1:]);assert (n,rank) in [(2,0),(2,1),(3,0),(3,1),(4,2)]
out=HERE/'runs'/f'n{n}-r{rank}';out.mkdir(parents=True,exist_ok=False)
bindings={ROOT/p:h for p,h in proof['inputs'].items()}
bindings.update({build/p:h for p,h in proof['outputs'].items()})
bindings[build/'build.json']=sha(build/'build.json');bindings[HERE/'run.py']=sha(HERE/'run.py')
def verify():
 for p,h in bindings.items():assert sha(p)==h,f'changed bound input {p}'
verify()
record={'status':'running','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'topology':[n,rank],'budget_seconds':120,'inputs':{str(p.relative_to(ROOT)):h for p,h in bindings.items()},'processes':[],'scope':'Exact-only Rational graph census, no numerical evaluation or timing qualification'}
save(out/'run.json',record);start=time.monotonic()
try:
 for convention in ['native','oneloop']:
  remaining=120-(time.monotonic()-start)
  p={'convention':convention,'timeout_seconds':max(0,remaining)};record['processes'].append(p)
  if remaining<=0:p['status']='not_run_budget_exhausted';continue
  command=['taskset','-c','8',str(build/'census'),str(n),str(rank),convention,str(out/convention)]
  p['command']=command;save(out/'run.json',record)
  began=time.monotonic()
  with open(out/(convention+'.log'),'w') as log:
   try:p['returncode']=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=remaining).returncode;p['status']='passed' if p['returncode']==0 else 'failed'
   except subprocess.TimeoutExpired:p.update(returncode=None,status='timeout')
  p['seconds']=time.monotonic()-began
  result=out/convention/'result.json'
  if result.exists():p['result']=json.loads(result.read_text())
  save(out/'run.json',record)
 verify();record['inputs_unchanged']=True
 record['status']='passed' if len(record['processes'])==2 and all(p['status']=='passed' for p in record['processes']) else 'incomplete_or_failed'
except Exception as error:record.update(status='failed',error=str(error))
record['seconds']=time.monotonic()-start;record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
record['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and p.name!='run.json'}
save(out/'run.json',record)
print(json.dumps({'topology':[n,rank],'status':record['status'],'seconds':record['seconds'],'results':[p.get('result',{'status':p['status']}) for p in record['processes']]}))
sys.exit(0 if record['status']=='passed' else 1)
