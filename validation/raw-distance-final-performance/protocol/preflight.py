from pathlib import Path
import os,json,hashlib,subprocess,time,datetime,re,signal
root=Path.cwd();out=root/'target/raw-distance-final-performance';closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds';os.sched_setaffinity(0,{6,7});sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
perf=out/'protocol'
build=json.loads((perf/'build.json').read_text());assert build['exit_code']==0 and build['source_unchanged'] and build['externs_unchanged'];assert build['dependency_closure_manifest_sha256']==sha(closure/'manifest.json');binary=perf/'probe';assert sha(binary)==build['binary_sha256'];source=perf/'probe.rs';assert sha(source)==build['source_sha256']
m=json.loads((closure/'manifest.json').read_text());records=m['files']+m['native_files']
def verify():
 assert build['cohort_bindings_unchanged']
 for name,digest in build['cohort_bindings'].items():assert sha(root/name)==digest,name
 assert sha(closure/'manifest.json')==build['dependency_closure_manifest_sha256']
 for variant in ['baseline','candidate']:
  library=json.loads((out/(variant+'-lib-build.json')).read_text());assert library['closure_manifest_sha256']==sha(closure/'manifest.json');assert sha(out/('libreceipt_final_'+variant+'.rlib'))==library['binary_sha256']
 for rec in records:
  p=Path(rec['retained']);assert p.stat().st_size==rec['bytes'] and sha(p)==rec['sha256'],str(p)
 assert sha(source)==build['source_sha256']
 for p,h in build['extern_sha256'].items():assert sha(root/p)==h,p
verify();cmd=[str(binary)];path=perf/'preflight.json';assert not path.exists();state={'status':'running','command':cmd,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timeout_seconds':120,'cpu_affinity':[6,7],'binary_sha256':sha(binary),'build_manifest_sha256':sha(perf/'build.json'),'dependency_closure_manifest_sha256':sha(closure/'manifest.json'),'closure_files_verified_before':len(records),'source_sha256':sha(source),'scope':'New final implementation cohort,14 workload pairs: exact input/output/context/status/flags/publicstats parity and inactiveN5 counters; validation duration only'};path.write_text(json.dumps(state,indent=2)+'\n');start=time.monotonic()
with (perf/'preflight.log').open('w') as log:
 child=subprocess.Popen(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:code=child.wait(timeout=120);timeout=False
 except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait();timeout=True
state.update(exit_code=code,timed_out=timeout,seconds=time.monotonic()-start);verify();state['closure_files_verified_after']=len(records);state['binary_unchanged']=sha(binary)==state['binary_sha256'];text=(perf/'preflight.log').read_text();match=re.search(r'PASS (\d+) fixed-loop cases; mode=correctness-only',text);state['cases_passed']=int(match[1]) if match else 0;state['status']='passed' if code==0 and not timeout and state['binary_unchanged'] and state['cases_passed']==14 else 'failed';state['log_sha256']=sha(perf/'preflight.log');path.write_text(json.dumps(state,indent=2)+'\n');print(json.dumps({k:state[k] for k in ['status','exit_code','seconds','cases_passed','binary_unchanged']}));raise SystemExit(0 if state['status']=='passed' else 1)
