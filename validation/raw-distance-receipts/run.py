#!/usr/bin/env python3
from pathlib import Path
import argparse,os,hashlib,json,subprocess,time,datetime,re,signal
root=Path.cwd();out=root/'target/raw-distance-receipts';closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds'
p=argparse.ArgumentParser();p.add_argument('variant',choices=['baseline','candidate']);p.add_argument('label');p.add_argument('filter');p.add_argument('--timeout',type=int,default=120);a=p.parse_args()
os.sched_setaffinity(0,{6,7});sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
build=json.loads((out/(a.variant+'-unit-build.json')).read_text());assert build['exit_code']==0
binary=out/('receipt_'+a.variant+'-unit');assert sha(binary)==build['binary_sha256']
m=json.loads((closure/'manifest.json').read_text());records=m['files']+m['native_files']
def verify():
 for rec in records:
  path=Path(rec['retained']);assert path.stat().st_size==rec['bytes'] and sha(path)==rec['sha256'],str(path)
 for path,digest in build['source_sha256'].items():assert sha(root/path)==digest,path
verify()
cmd=[str(binary),a.filter,'--nocapture','--test-threads=1'];logpath=out/(a.label+'.log');path=out/(a.label+'.json');assert not path.exists(),'Preserve existing runtime evidence'
state={'status':'running','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd,'timeout_seconds':a.timeout,'cpu_affinity':[6,7],'binary_sha256':sha(binary),'build_manifest_sha256':sha(out/(a.variant+'-unit-build.json')),'source_sha256':build['source_sha256'],'dependency_closure_manifest_sha256':sha(closure/'manifest.json'),'closure_files_verified_before':len(records),'license_capabilities':'validation/concurrent-workspaces/license-capabilities.json','timing_scope':'validation_only_not_benchmark'}
path.write_text(json.dumps(state,indent=2)+'\n');started=time.monotonic()
with logpath.open('w') as log:
 child=subprocess.Popen(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:code=child.wait(timeout=a.timeout);timed_out=False
 except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait();timed_out=True
state.update(exit_code=code,timed_out=timed_out,wall_seconds=time.monotonic()-started,status='passed' if code==0 and not timed_out else 'failed')
text=logpath.read_text();match=re.search(r'test result: (?:ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored;',text)
if match:state.update(tests_passed=int(match[1]),tests_failed=int(match[2]),tests_ignored=int(match[3]))
try:verify();state['closure_files_verified_after']=len(records);state['source_unchanged']=True
except Exception as error:state.update(status='provenance_failure',provenance_error=str(error))
state['log_sha256']=sha(logpath);state['binary_unchanged']=sha(binary)==state['binary_sha256'];path.write_text(json.dumps(state,indent=2)+'\n');print(json.dumps({k:v for k,v in state.items() if k in ['status','exit_code','wall_seconds','timed_out','tests_passed','tests_failed','source_unchanged','binary_unchanged']}));raise SystemExit(0 if state['status']=='passed' and state['binary_unchanged'] else 1)
