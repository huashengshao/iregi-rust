#!/usr/bin/env python3
import pathlib,json,hashlib,subprocess,os,time,datetime,sys
R=pathlib.Path.cwd();H=R/'target/public-highpoint/thin-n6-generic-fixed';B=H/'build-001';mode=sys.argv[1];bound=180
def sha(p):return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
build=json.loads((B/'build.json').read_text());assert build['status']=='passed'
files={pathlib.Path(p):h for p,h in build['inputs'].items()};files[B/'build.json']=sha(B/'build.json');files[pathlib.Path(__file__).resolve()]=sha(__file__)
for name,h in build['outputs'].items():files[B/name]=h
fixture=R/'validation/public-highpoint/fixture-conditioned_masses.json';files[fixture]=sha(fixture)
if mode!='exact':
 exact_path=H/'exact-001/run.json';exact=json.loads(exact_path.read_text());assert exact['status']=='passed' and exact['inputs_unchanged'] and len(exact['steps'])==5
 files[exact_path]=sha(exact_path)
 for name,digest in exact['outputs'].items():files[H/'exact-001'/name]=digest
def verify():
 for p,h in files.items():assert sha(p)==h,f'changed input {p}'
verify();prefix='exact-001' if mode=='exact' else f'n6-rank3-{mode}-001';a=H/prefix;a.mkdir(exist_ok=False)
extra={'RAYON_NUM_THREADS':'1','RUST_TEST_THREADS':'1','IREGI_PREPARATION_PROFILE':'1','IREGI_PV_PREPARATION_PROFILE':'1'};env=os.environ.copy();env.update(extra)
commands=[['taskset','-c','14',str(B/'tests'),filter,'--nocapture','--test-threads=1'] for filter in ['generic_thin','planar_mask','thin_n6::tests','types::primal_envelope_tests','plan::tests::final_uv_power_counting_preserves_ir_and_dimension_shifted_residues']] if mode=='exact' else [['taskset','-c','14',str(B/'driver'),str(fixture), '6','3','pv',mode,'53','1',str(a/'result.json')]]
record={'status':'started','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bound_seconds':bound,'environment_additions':extra,'license_scope':'User-supplied license sourced privately, contents excluded.','inputs':{str(p):h for p,h in files.items()},'steps':[],'scope':'Private correctness/diagnostic qualification; no performance gate.'};save(a/'run.json',record);start=time.monotonic()
try:
 for i,cmd in enumerate(commands):
  verify();step={'command':cmd};record['steps'].append(step);save(a/'run.json',record);t=time.monotonic();remaining=bound-(t-start);assert remaining>0,'bound exhausted'
  with open(a/f'step-{i}.log','w') as log:
   try:step['exit_code']=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=remaining).returncode
   except subprocess.TimeoutExpired:step.update(exit_code=None,timeout=True)
  step['seconds']=time.monotonic()-t;save(a/'run.json',record);verify();assert step['exit_code']==0,f'child exited {step["exit_code"]}'
 record.update(status='passed',inputs_unchanged=True)
except Exception as e:record.update(status='failed',error=str(e));verify();record['inputs_unchanged']=True
record.update(elapsed_seconds=time.monotonic()-start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),outputs={p.name:sha(p) for p in a.iterdir() if p.name!='run.json'});save(a/'run.json',record);print(json.dumps({k:record[k] for k in ['status','elapsed_seconds','steps']}));sys.exit(0 if record['status']=='passed' else 1)
