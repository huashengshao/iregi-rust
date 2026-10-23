#!/usr/bin/env python3
import pathlib,json,hashlib,subprocess,os,time,datetime,shutil,sys
R=pathlib.Path.cwd();H=R/'target/public-highpoint/thin-n6';C=H/'core/crates/iregi-rust'
def sha(p):return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
a=H/('build-'+sys.argv[1]);a.mkdir(exist_ok=False)
closure=R/'target/e6-direct-n2/preparation.json';supp=R/'target/core-fused-cse-census/supplemental-deps.json'
files={R/f['frozen']:f['sha256'] for f in json.loads(closure.read_text())['files']+json.loads(supp.read_text())['files']}
files.update({p:sha(p) for p in C.rglob('*') if p.is_file()});files.update({H/n:sha(H/n) for n in ['snapshot.json','driver.rs','build.py']})
files[closure]=sha(closure);files[supp]=sha(supp)
compiler=pathlib.Path(shutil.which('rustc')).resolve();files[compiler]=sha(compiler)
production={p:sha(p) for p in (R/'crates/iregi-rust/src').rglob('*.rs')}
files.update(production)
start=time.monotonic();record={'status':'building','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bound_seconds':180,'compiler':subprocess.check_output(['rustc','-vV'],text=True),'compiler_path':str(compiler),'inputs':{str(p):v for p,v in files.items()},'steps':[],'scope':'Private thin N6 child composition; native-object debug closure. opt0/debuginfo0/stripdebuginfo; no live dependency fallback; all source including production guard frozen. No performance claim.'};save(a/'build.json',record)
def verify():
 for p,h in files.items():assert sha(p)==h,f'changed {p}'
D=R/'target/e6-direct-n2/deps';N=R/'target/e6-direct-n2/native';E=R/'target/core-fused-cse-census/supplemental-deps'
externs={'iregi_masters':D/'libiregi_masters-f07797f04e91954e.rlib','symbolica':D/'libsymbolica-06e42762cabb77d9.rlib','serde':D/'libserde-b04ba25115fa19f8.rlib','serde_json':D/'libserde_json-d657c5438f354a41.rlib','thiserror':E/'libthiserror-0527e2191ec3561c.rlib'}
common=['taskset','-c','14,15','rustc','--edition=2024','-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo','-L',f'dependency={D}','-L',f'dependency={E}','-L',f'native={N}']
def step(name,args):
 verify();env=os.environ.copy();env.update(CARGO_CRATE_NAME='iregi_rust',CARGO_MANIFEST_DIR=str(C));s={'name':name,'command':args};record['steps'].append(s);save(a/'build.json',record)
 t=time.monotonic();remaining=180-(t-start);assert remaining>0,'total build bound exhausted'
 with open(a/(name+'.log'),'w') as log:
  try:s['exit_code']=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=remaining).returncode
  except subprocess.TimeoutExpired:s.update(exit_code=None,timeout=True)
 s['seconds']=time.monotonic()-t;save(a/'build.json',record);assert s['exit_code']==0,f'{name} failed';verify()
try:
 args=common+['--crate-name','iregi_rust','--crate-type','rlib',str(C/'src/lib.rs'),'-o',str(a/'libiregi_rust.rlib')]
 for n,p in externs.items():args+=['--extern',f'{n}={p}']
 step('core',args)
 args=common+['--crate-name','iregi_rust','--test',str(C/'src/lib.rs'),'-o',str(a/'tests')]
 for n,p in externs.items():args+=['--extern',f'{n}={p}']
 step('tests',args)
 args=common+['--crate-name','thin_n6_driver',str(H/'driver.rs'),'-o',str(a/'driver'),'--extern',f'iregi_rust={a}/libiregi_rust.rlib']
 for n in ['symbolica','iregi_masters','serde_json']:args+=['--extern',f'{n}={externs[n]}']
 step('driver',args)
 record.update(status='passed',inputs_unchanged=True,outputs={p.name:sha(p) for p in [a/'libiregi_rust.rlib',a/'tests',a/'driver']})
except Exception as e:record.update(status='failed',error=str(e))
record.update(elapsed_seconds=time.monotonic()-start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(a/'build.json',record);print(json.dumps({'status':record['status'],'seconds':record['elapsed_seconds'],'steps':record['steps']}));sys.exit(0 if record['status']=='passed' else 1)
