#!/usr/bin/env python3
import pathlib,json,hashlib,subprocess,os,time,datetime,sys
R=pathlib.Path.cwd();H=R/'target/public-highpoint/thin-n6-generic-fixed';B=H/'build-001';mode=sys.argv[1];assert mode in ['128','256'];bound=180
def sha(p):return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
build=json.loads((B/'build.json').read_text());assert build['status']=='passed'
files={pathlib.Path(p):h for p,h in build['inputs'].items()};files[B/'build.json']=sha(B/'build.json');files[pathlib.Path(__file__).resolve()]=sha(__file__)
for name,h in build['outputs'].items():files[B/name]=h
for name in ['run.py','compare.py','numerical-protocol.json']:files[H/name]=sha(H/name)
protocol=json.loads((H/'numerical-protocol.json').read_text())
assert protocol['schema_version']==1 and protocol['source_review_status']=='approved_source_only' and '/root' in protocol['reviewers']
for key,value in {'rank':3,'propagators':6,'working_bits':[128,256],'requested_bits':53,'fixture_rows':[0],'moments':35,'native_complex_slots':140,'runtime_bound_seconds':180,'normalized_original_tolerance':'1e-10','convergence_tolerance':'2^-80'}.items():assert protocol[key]==value,f'wrong protocol {key}'
protocol_paths=[H/name for name in ['compare.py','run-numeric.py','build-001/build.json','exact-001/run.json',*[f'exact-001/step-{i}.log' for i in range(5)],'proposed-protocol.json','source-review.json','base.json','test-fix.json','driver.rs','run.py']]
protocol_paths += [R/'validation/public-highpoint'/name for name in ['fixture-conditioned_masses.json','reference-conditioned_masses.json','compare_public.py']]
assert set(protocol['artifacts'])=={str(path.relative_to(R)) for path in protocol_paths},'protocol inventory differs'
for path in protocol_paths:
 digest=protocol['artifacts'][str(path.relative_to(R))];assert sha(path)==digest,f'changed protocol artifact {path}'
 assert path not in files or files[path]==digest;files[path]=digest
if mode=='256':
 previous_path=H/'comparison-128.json';previous=json.loads(previous_path.read_text());assert previous['status']=='passed'
 for name,digest in previous['input_sha256'].items():
  path=pathlib.Path(name);assert path not in files or files[path]==digest;files[path]=digest
 files[previous_path]=sha(previous_path)
fixture=R/'validation/public-highpoint/fixture-conditioned_masses.json';files[fixture]=sha(fixture)
if mode!='exact':
 exact_path=H/'exact-001/run.json';exact=json.loads(exact_path.read_text());assert exact['status']=='passed' and exact['inputs_unchanged'] and len(exact['steps'])==5
 files[exact_path]=sha(exact_path)
 for name,digest in exact['outputs'].items():files[H/'exact-001'/name]=digest
def verify():
 for p,h in files.items():assert sha(p)==h,f'changed input {p}'
verify();prefix='exact-001' if mode=='exact' else f'n6-rank3-{mode}-001';a=H/prefix;a.mkdir(exist_ok=False)
extra={'RAYON_NUM_THREADS':'1','RUST_TEST_THREADS':'1','IREGI_PREPARATION_PROFILE':'1','IREGI_PV_PREPARATION_PROFILE':'1'};env=os.environ.copy();env.update(extra)
commands=[['taskset','-c','14',str(B/'driver'),str(fixture),'6','3','pv',mode,'53','1',str(a/'result.json')]]
record={'status':'started','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bound_seconds':bound,'environment_additions':extra,'license_scope':'User-supplied license sourced privately, contents excluded.','inputs':{str(p):h for p,h in files.items()},'steps':[],'scope':'Frozen private rank3 numerical gate only, conditioned retained base fixture, all35moments and140native Laurent slots, requested53; independently reviewed source/protocol required before capture. No rank7 workspace, production adoption or performance gate.'};save(a/'run.json',record);start=time.monotonic()
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
