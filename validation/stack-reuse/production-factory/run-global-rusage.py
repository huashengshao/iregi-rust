from pathlib import Path
import hashlib,json,os,resource,subprocess,sys,time
root=Path.cwd(); base=root/'target/stack-reuse-production'
variant,stage,filter_text,limit=sys.argv[1:]; assert variant in ['baseline','candidate']; assert stage in ['core_tests','master_tests','e6']
folder=base/variant; binary=folder/('shifted_pentagon' if stage=='e6' else stage)
name=f'{stage}-{filter_text.replace("::","_") or "all"}'
args=[str(binary),filter_text,'--nocapture','--test-threads=1']
env=os.environ.copy();env['RUST_TEST_THREADS']='1'
start=time.monotonic(); status=None; expired=False
with (folder/f'{name}.log').open('w') as log:
    try:status=subprocess.call(args,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=float(limit))
    except subprocess.TimeoutExpired:expired=True
usage=resource.getrusage(resource.RUSAGE_CHILDREN)
report={'variant':variant,'stage':stage,'filter':filter_text,'command':args,'timeout_seconds':float(limit),'exit_code':status,'timed_out':expired,'elapsed_seconds':time.monotonic()-start,'max_rss_kib':usage.ru_maxrss,'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'diagnostic_only':True,'performance_gate':'Not a controlled statistical benchmark; elapsed time and peak RSS are diagnostic observations.'}
(folder/f'{name}.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
if expired or status:print((folder/f'{name}.log').read_text()[-12000:],flush=True)
sys.exit(124 if expired else status)
