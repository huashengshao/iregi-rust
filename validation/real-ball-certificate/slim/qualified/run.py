from pathlib import Path
import hashlib,json,os,re,subprocess,time
root=Path.cwd();out=Path(__file__).resolve().parent;build_path=out/'build.json';build=json.loads(build_path.read_text());assert build['status']=='compiled' and build['returncode']==0
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
closure_manifest=root/build['dependency_closure_manifest'];closure=json.loads(closure_manifest.read_text());records=closure['files']+closure['native_files'];binary=out/'certificate_slim_tests'
def verify():
 assert sha(closure_manifest)==build['dependency_closure_manifest_sha256'];assert sha(binary)==build['binary_sha256']
 for record in records:
  p=Path(record['retained']);assert p.stat().st_size==record['bytes'] and sha(p)==record['sha256'],str(p)
 for filename,digest in build['source_sha256'].items():assert sha(root/filename)==digest,filename
state={'schema':1,'status':'verifying','binary_sha256':build['binary_sha256'],'build_manifest_sha256':sha(build_path),'source_sha256':build['source_sha256'],'closure_manifest_sha256':build['dependency_closure_manifest_sha256'],'cpu_affinity':sorted(os.sched_getaffinity(0)),'command':[str(binary),'--test-threads=1','--nocapture'],'performance_gate':False}
path=out/'run.json';save=lambda:path.write_text(json.dumps(state,indent=2)+'\n');save();verify();state['verified_before']=True;state['status']='running';save();start=time.monotonic()
with (out/'tests.log').open('w') as log:
 try:
  r=subprocess.run(state['command'],stdout=log,stderr=subprocess.STDOUT,timeout=120)
  state['returncode']=r.returncode
 except subprocess.TimeoutExpired:
  state['returncode']=None;state['timeout_seconds']=120
state['wall_seconds']=time.monotonic()-start;verify();state['verified_after']=True
text=(out/'tests.log').read_text();match=re.search(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored;',text)
if match:state['test_result']={'status':match[1],'passed':int(match[2]),'failed':int(match[3]),'ignored':int(match[4])}
state['status']='passed' if state['returncode']==0 and state.get('test_result')=={'status':'ok','passed':23,'failed':0,'ignored':0} else 'failed';state['log_sha256']=sha(out/'tests.log');save();print(json.dumps(state,indent=2));raise SystemExit(0 if state['status']=='passed' else 1)
