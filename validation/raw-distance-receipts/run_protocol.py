from pathlib import Path
import os,json,hashlib,subprocess,time,datetime,re,signal
root=Path.cwd();out=root/'target/raw-distance-receipts';closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds';os.sched_setaffinity(0,{6,7});sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
build=json.loads((out/'protocol-build.json').read_text());assert build['exit_code']==0;binary=out/'protocol';assert sha(binary)==build['binary_sha256'];source=out/'protocol.rs';assert sha(source)==build['source_sha256']
m=json.loads((closure/'manifest.json').read_text());records=m['files']+m['native_files']
def verify():
 for rec in records:
  p=Path(rec['retained']);assert p.stat().st_size==rec['bytes'] and sha(p)==rec['sha256'],str(p)
 assert sha(source)==build['source_sha256']
 for p,h in build['extern_sha256'].items():assert sha(root/p)==h,p
verify();cmd=[str(binary)];path=out/'protocol-run.json';assert not path.exists();state={'status':'running','command':cmd,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timeout_seconds':120,'cpu_affinity':[6,7],'binary_sha256':sha(binary),'build_manifest_sha256':sha(out/'protocol-build.json'),'dependency_closure_manifest_sha256':sha(closure/'manifest.json'),'closure_files_verified_before':len(records),'source_sha256':sha(source),'scope':'exact paired public snapshots; validation timing only, no performance measurement'};path.write_text(json.dumps(state,indent=2)+'\n');start=time.monotonic()
with (out/'protocol-run.log').open('w') as log:
 child=subprocess.Popen(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:code=child.wait(timeout=120);timeout=False
 except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait();timeout=True
state.update(exit_code=code,timed_out=timeout,seconds=time.monotonic()-start);verify();state['closure_files_verified_after']=len(records);state['binary_unchanged']=sha(binary)==state['binary_sha256'];text=(out/'protocol-run.log').read_text();match=re.search(r'PASS (\d+) sequential batch snapshots',text);state['snapshots_passed']=int(match[1]) if match else 0;state['status']='passed' if code==0 and not timeout and state['binary_unchanged'] and state['snapshots_passed']==120 else 'failed';state['log_sha256']=sha(out/'protocol-run.log');path.write_text(json.dumps(state,indent=2)+'\n');print(json.dumps({k:state[k] for k in ['status','exit_code','seconds','snapshots_passed','binary_unchanged']}));raise SystemExit(0 if state['status']=='passed' else 1)
