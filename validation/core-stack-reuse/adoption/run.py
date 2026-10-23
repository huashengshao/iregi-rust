from pathlib import Path
import hashlib,json,os,re,subprocess,sys,time
root=Path.cwd();base=root/'target/core-stack-adoption';binary=base/'core_tests'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
compiled=json.loads((base/'compile.json').read_text());assert compiled['exit_code']==0
assert sha(binary)==compiled['binary_sha256']
filter=sys.argv[1];expected=int(sys.argv[2]);assert expected>0
name=filter.replace('::','_').strip('_');folder=base/'runs'/name;folder.mkdir(parents=True,exist_ok=False)
command=['taskset','-c','18',str(binary),filter,'--nocapture','--test-threads=1']
record={'filter':filter,'command':command,'expected_tests':expected,'binary_sha256_before':sha(binary),'source_manifest_sha256':sha(base/'preparation.json'),'compile_manifest_sha256':sha(base/'compile.json'),'runner_sha256':sha(Path(__file__)),'timeout_seconds':180,'performance_scope':'Correctness only; concurrent project work is permitted.'}
start=time.monotonic();timed_out=False
with (folder/'output.log').open('w') as log:
    try: code=subprocess.call(command,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    except subprocess.TimeoutExpired: code=None;timed_out=True
text=(folder/'output.log').read_text();m=re.search(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored;',text)
counts=None if m is None else dict(zip(['passed','failed','ignored'],map(int,m.groups()[1:])))
record.update(exit_code=code,timed_out=timed_out,elapsed_seconds=time.monotonic()-start,binary_sha256_after=sha(binary),test_counts=counts,log_sha256=sha(folder/'output.log'))
record['status']='passed' if code==0 and counts=={'passed':expected,'failed':0,'ignored':0} and record['binary_sha256_before']==record['binary_sha256_after'] else 'failed'
(folder/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2),flush=True)
if record['status']!='passed': print(text[-20000:],flush=True);raise SystemExit(1)
