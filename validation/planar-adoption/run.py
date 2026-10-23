"""Run only named, bounded qualification tests with complete artifact joins."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,signal,subprocess,time

p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
g.add_argument('--small-suite',action='store_true');g.add_argument('--mixed',action='store_true')
g.add_argument('--precision',type=int,choices=[128,256]);p.add_argument('--timeout',type=float,default=120)
a=p.parse_args();assert 0<a.timeout<=600
base=Path.cwd()/'target/planar-adoption';source=base/'source-snapshot'
sha=lambda path:hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
load=lambda path:json.loads(path.read_text())
build=load(base/'build.json');binary=base/'core-tests'
assert build['exit_code']==0 and sha(binary)==build['binary_sha256']
for path,digest in build['source_hashes'].items():assert sha(source/path)==digest
tag='small-suite' if a.small_suite else 'rank7-mixed' if a.mixed else f'rank7-{a.precision}'
dest=base/'runs';dest.mkdir(exist_ok=True);report_path=dest/(tag+'.json');log_path=dest/(tag+'.log')
assert not report_path.exists() and not log_path.exists()
name='certified_planar::tests::'
if a.mixed:name+='public_planar_rank7_rectangular_mixed_artifact'
elif a.precision:name+='public_planar_rank7_precision_artifacts_and_convergence'
command=[str(binary),name,'--nocapture','--test-threads=1']
listing=[str(binary),name,'--list']
if not a.small_suite:command+=['--exact','--ignored'];listing+=['--exact','--ignored']
members=subprocess.check_output(listing,text=True)
selected=[line[:-6] for line in members.splitlines() if line.endswith(': test')]
ignored=[]
if a.small_suite:
 ignored_output=subprocess.check_output(listing+['--ignored'],text=True)
 ignored=[line[:-6] for line in ignored_output.splitlines() if line.endswith(': test')]
assert selected and (a.small_suite or selected==[name])
expected=len(selected)-len(ignored)
env=os.environ.copy();env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',IREGI_PREPARATION_PROFILE='1')
artifact=None;previous=None;previous_sha=None
if a.mixed:
 artifact=base/'mixed-rank7.json';env['IREGI_PLANAR_MIXED_OUTPUT']=str(artifact)
elif a.precision:
 artifact=base/f'precision-{a.precision}.json'
 env.update(IREGI_PLANAR_PRECISION=str(a.precision),IREGI_PLANAR_OUTPUT=str(artifact))
 if a.precision==256:
  previous=base/'precision-128.json';previous_sha=sha(previous);prior=load(dest/'rank7-128.json')
  assert prior['status']=='passed' and prior['output_artifact_sha256']==previous_sha
  assert prior['binary_sha256']==build['binary_sha256'] and load(previous)['status']=='passed'
  env['IREGI_PLANAR_PREVIOUS']=str(previous)
if artifact:assert not artifact.exists()
record={'status':'running','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'command':command,'timeout_seconds':a.timeout,'cpu_affinity':sorted(os.sched_getaffinity(0)),
 'binary_sha256':build['binary_sha256'],'build_manifest_sha256':sha(base/'build.json'),
 'runner_sha256':sha(Path(__file__)),'selected_tests':selected,'ignored_tests':ignored,
 'expected_passed_tests':expected,'previous_artifact_sha256':previous_sha,
 'environment':{k:v for k,v in env.items() if k in ('RAYON_NUM_THREADS','OMP_NUM_THREADS') or k.startswith('IREGI_PLANAR') or k=='IREGI_PREPARATION_PROFILE'}}
report_path.write_text(json.dumps(record,indent=2)+'\n');start=time.monotonic()
with log_path.open('w') as log:
 child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
 try:code=child.wait(timeout=a.timeout)
 except subprocess.TimeoutExpired:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
  code=124
record.update(status='passed' if code==0 else 'timeout' if code==124 else 'failed',exit_code=code,
 elapsed_seconds=time.monotonic()-start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
if artifact and artifact.exists():
 record.update(output_artifact_sha256=sha(artifact),output_artifact_status=load(artifact)['status'])
 if code==0 and record['output_artifact_status']!='passed':record['status']='invalid-artifact';code=1
if previous:record['previous_artifact_unchanged']=sha(previous)==previous_sha
record['source_hashes_unchanged']=all(sha(source/path)==digest for path,digest in build['source_hashes'].items())
record['binary_unchanged']=sha(binary)==build['binary_sha256']
if code==0:
 result=re.search(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',log_path.read_text())
 if not result or tuple(map(int,result.groups()))!=(expected,0,len(ignored)):
  record['status']='invalid-test-membership';code=1
if not record['source_hashes_unchanged'] or not record['binary_unchanged'] or record.get('previous_artifact_unchanged') is False:
 record['status']='invalid-provenance';code=1
report_path.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True);print(log_path.read_text()[-10000:],flush=True)
raise SystemExit(code)
