"""Retain a bounded private run and every frozen input/output hash."""
from pathlib import Path
import hashlib,json,os,signal,subprocess,sys,time

def sha(p):
    with p.open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()

root=Path.cwd(); here=root/'validation/highpoint-rank-lowering'
label=sys.argv[1]; limit=int(sys.argv[2]); command=sys.argv[3:]
assert label.replace('-','').replace('_','').isalnum() and 0<limit<=600
assert command[:3]==['taskset','-c','14']
manifest=here/(label+'-run.json'); log=here/(label+'.log')
assert not manifest.exists() and not log.exists()
build_path=here/'build.json'; build=json.loads(build_path.read_text()); assert build['status']=='passed'
guarded=dict(build['protected_input_hashes'])
for row in build['runs']: guarded[row['output_path']]=row['output_sha256']
for p in [Path(__file__),build_path,root/command[3]]:
    guarded[str(p.relative_to(root))]=sha(p)
for arg in command[4:]:
    p=root/arg
    if p.is_file(): guarded[str(p.relative_to(root))]=sha(p)
assert all(sha(root/n)==h for n,h in guarded.items())
env=dict(os.environ,IREGI_PREPARATION_PROFILE='1',IREGI_PV_PREPARATION_PROFILE='1')
started=time.monotonic()
record=dict(status='running',command=command,timeout_seconds=limit,protected_input_hashes=guarded,
            environment={'IREGI_PREPARATION_PROFILE':'1','IREGI_PV_PREPARATION_PROFILE':'1'},
            build_manifest_sha256=sha(build_path),scope='Private correctness/preparation diagnostic; no performance gate.')
manifest.write_text(json.dumps(record,indent=2)+'\n')
with log.open('wb') as out:
    child=subprocess.Popen(command,cwd=root,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
    try: code=child.wait(timeout=limit); status='completed' if code==0 else 'failed'
    except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL);code=child.wait();status='timeout'
changed={n:[h,sha(root/n)] for n,h in guarded.items() if sha(root/n)!=h}
record.update(status=status,exit_code=code,elapsed_seconds=time.monotonic()-started,changed_inputs=changed,
              log_path=str(log.relative_to(root)),log_sha256=sha(log))
if command[-1].endswith('.json'):
    result=root/command[-1]
    record.update(result_path=str(result.relative_to(root)),result_sha256=sha(result) if result.exists() else None)
    if result.exists():
        try: record['last_public_stage']=json.loads(result.read_text())['status']
        except (ValueError,KeyError): record['last_public_stage']='malformed_output'
manifest.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['status','exit_code','elapsed_seconds','changed_inputs']}),flush=True)
raise SystemExit(code!=0 or bool(changed))
