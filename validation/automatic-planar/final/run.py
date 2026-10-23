"""Run named automatic-planar/accounting tests with a source-bound time limit."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,signal,subprocess,time
p=argparse.ArgumentParser();p.add_argument('group',choices=['all']);p.add_argument('--timeout',type=int,default=180);a=p.parse_args();assert 0<a.timeout<=600
root=Path.cwd();base=root/'target/planar-counter-followup';source=base/'test-source';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
build=json.loads((base/'build.json').read_text());binary=base/'core-tests';assert build['exit_code']==0 and build['binary_sha256']==sha(binary)
for path,digest in build['source_hashes'].items():assert sha(source/path)==digest
name=''
command=[str(binary),'--nocapture','--test-threads=1'];listing=[str(binary),'--list']
def tests(args):return [x[:-6] for x in subprocess.check_output(args,text=True).splitlines() if x.endswith(': test')]
selected=tests(listing);ignored=tests(listing+['--ignored']);expected=len(selected)-len(ignored)
assert expected==18
dest=base/'runs';dest.mkdir(exist_ok=True);report=dest/(a.group+'.json');log_path=dest/(a.group+'.log');assert not report.exists() and not log_path.exists()
env=os.environ.copy();env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',IREGI_PREPARATION_PROFILE='1')
r={'status':'running','command':command,'timeout_seconds':a.timeout,'selected_tests':selected,'ignored_tests':ignored,'expected_passed_tests':expected,
 'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cpu_affinity':sorted(os.sched_getaffinity(0)),
 'binary_sha256':sha(binary),'build_manifest_sha256':sha(base/'build.json'),'runner_sha256':sha(Path(__file__)),
 'environment':{k:env[k] for k in ['RAYON_NUM_THREADS','OMP_NUM_THREADS','IREGI_PREPARATION_PROFILE']}}
def save_report():
 temporary=report.with_suffix('.json.tmp')
 with temporary.open('w') as output:
  output.write(json.dumps(r,indent=2)+'\n');output.flush();os.fsync(output.fileno())
 temporary.replace(report)
save_report();start=time.monotonic()
with log_path.open('w') as log:
 child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
 try:code=child.wait(timeout=a.timeout)
 except subprocess.TimeoutExpired:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
  code=124
r.update(status='passed' if code==0 else 'timeout' if code==124 else 'failed',exit_code=code,elapsed_seconds=time.monotonic()-start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
r['source_hashes_unchanged']=all(sha(source/path)==digest for path,digest in build['source_hashes'].items());r['binary_unchanged']=sha(binary)==build['binary_sha256']
if code==0:
 result=re.search(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',log_path.read_text())
 if not result or tuple(map(int,result.groups()))!=(expected,0,len(ignored)):r['status']='invalid-membership';code=1
if not r['source_hashes_unchanged'] or not r['binary_unchanged']:r['status']='invalid-provenance';code=1
print(json.dumps({k:r[k] for k in ['status','exit_code','expected_passed_tests','elapsed_seconds']}),flush=True);save_report();print(log_path.read_text()[-8000:],flush=True)
raise SystemExit(code)
