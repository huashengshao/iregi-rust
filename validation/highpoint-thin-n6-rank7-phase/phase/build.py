#!/usr/bin/env python3
"""Build the frozen logging-only candidate; never changes the source/dependency tree."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, time
R=Path.cwd(); H=R/'target/public-highpoint/thin-n6-rank7-phase'; C=H/'core/crates/iregi-rust'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
protocol_path=H/'protocol.json';protocol=json.loads(protocol_path.read_text())
assert protocol['status']=='approved_source_only' and '/root' in protocol['reviewers']
assert protocol['build_bound_seconds']==90 and protocol['runtime_bound_seconds']==300
files={R/n:d for n,d in protocol['artifacts'].items()};files[protocol_path]=sha(protocol_path)
compiler=Path(protocol['compiler_path']);assert compiler in files
assert sha(H/'driver.rs')==files[R/'validation/highpoint-thin-n6-generic/fixed/driver.rs']
def verify():
 for p,d in files.items():assert sha(p)==d,f'changed input {p}'
verify();a=H/'build-001';a.mkdir(exist_ok=False)
D=R/'target/e6-direct-n2/deps';N=R/'target/e6-direct-n2/native';E=R/'target/core-fused-cse-census/supplemental-deps'
externs={'iregi_masters':D/'libiregi_masters-f07797f04e91954e.rlib','symbolica':D/'libsymbolica-06e42762cabb77d9.rlib','serde':D/'libserde-b04ba25115fa19f8.rlib','serde_json':D/'libserde_json-d657c5438f354a41.rlib','thiserror':E/'libthiserror-0527e2191ec3561c.rlib'}
common=['taskset','-c','14,15',str(compiler),'--edition=2024','-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo','-L',f'dependency={D}','-L',f'dependency={E}','-L',f'native={N}']
commands=[('core',common+['--crate-name','iregi_rust','--crate-type','rlib',str(C/'src/lib.rs'),'-o',str(a/'libiregi_rust.rlib')]+[arg for n,p in externs.items() for arg in ['--extern',f'{n}={p}']]),('driver',common+['--crate-name','thin_n6_driver',str(H/'driver.rs'),'-o',str(a/'driver'),'--extern',f'iregi_rust={a}/libiregi_rust.rlib']+[arg for n in ['symbolica','iregi_masters','serde_json'] for arg in ['--extern',f'{n}={externs[n]}']])]
record={'status':'building','bound_seconds':90,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiler_path':str(compiler),'compiler':subprocess.check_output([str(compiler),'-vV'],text=True),'inputs':{str(p):d for p,d in files.items()},'steps':[],'scope':'Private rank7 logging-only candidate; existing25 exact tests reused only after byte-restoration and independent source review. Frozen source/native closure; no mutable production source or live dependency search.'}
save(a/'build.json',record);start=time.monotonic()
try:
 for name,command in commands:
  verify();step={'name':name,'command':command};record['steps'].append(step);save(a/'build.json',record)
  env=os.environ.copy();env.update(CARGO_CRATE_NAME='iregi_rust',CARGO_MANIFEST_DIR=str(C));t=time.monotonic();remaining=90-(t-start);assert remaining>0,'build bound exhausted'
  with (a/f'{name}.log').open('w') as log:
   try:step['exit_code']=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=remaining).returncode
   except subprocess.TimeoutExpired:step.update(exit_code=None,timeout=True)
  step['seconds']=time.monotonic()-t;save(a/'build.json',record);verify();assert step['exit_code']==0,f'{name} failed'
 record.update(status='passed',inputs_unchanged=True,outputs={n:sha(a/n) for n in ['libiregi_rust.rlib','driver']})
except Exception as error:
 record.update(status='failed',error=str(error))
 try:verify();record['inputs_unchanged']=True
 except Exception as guard:record.update(inputs_unchanged=False,guard_error=str(guard))
record.update(elapsed_seconds=time.monotonic()-start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(a/'build.json',record)
print(json.dumps({k:record[k] for k in ['status','elapsed_seconds','steps']}));sys.exit(0 if record['status']=='passed' else 1)
