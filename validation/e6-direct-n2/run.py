from pathlib import Path
import hashlib,json,os,signal,subprocess,time

root=Path.cwd();base=root/'target/e6-direct-n2'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
build=json.loads((base/'build.json').read_text());prep=json.loads((base/'preparation.json').read_text())
assert build['exit_code']==0 and build['sources_unchanged'] and build['closure_unchanged']
assert sha(base/'validate')==build['binary_sha256']
assert not (base/'run.json').exists(), 'preserve numerical attempts'
for path,digest in build['sources'].items():assert sha(root/path)==digest,path
for x in prep['files']:assert sha(root/x['frozen'])==x['sha256'],x['frozen']
assert sha(base/'series-oracle.json')==prep['oracle_sha256']
cmd=['taskset','-c','18',str(base/'validate'),str(base/'series-oracle.json'),str(base/'output.json')]
env=os.environ.copy();env['RAYON_NUM_THREADS']='1';env['OMP_NUM_THREADS']='1'
record={'scope':'Private correctness only; no performance benchmark or public/core qualification',
        'command':cmd,'timeout_seconds':120,'build_sha256':sha(base/'build.json'),
        'binary_sha256':build['binary_sha256'],'source_manifest_sha256':sha(base/'source-manifest.json'),
        'oracle_sha256':sha(base/'series-oracle.json'),'runner_sha256':sha(Path(__file__)),
        'started_unix_time':time.time(),'environment_overrides':{'RAYON_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}}
start=time.monotonic()
with (base/'run.log').open('w') as log:
    p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
    record['pid']=p.pid
    try:record['exit_code']=p.wait(timeout=120)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid,signal.SIGTERM)
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
        record.update(exit_code=p.returncode,timed_out=True)
record.update(elapsed_seconds_diagnostic=time.monotonic()-start,
              sources_unchanged=all(sha(root/path)==digest for path,digest in build['sources'].items()),
              closure_unchanged=all(sha(root/x['frozen'])==x['sha256'] for x in prep['files']),
              run_log_sha256=sha(base/'run.log'))
if (base/'output.json').exists():record['output_sha256']=sha(base/'output.json')
(base/'run.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
raise SystemExit(0 if record['exit_code']==0 and record['sources_unchanged'] and record['closure_unchanged'] else 1)
