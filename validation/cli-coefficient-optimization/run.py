from pathlib import Path
import hashlib,json,os,subprocess,sys,time
root=Path.cwd();base=root/'target/cli-coefficient-optimization';output=base/'qualification';output.mkdir(exist_ok=True)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
build=json.loads((base/'compile.json').read_text());assert build['exit_code']==0
assert sha(base/'probe')==build['binary_sha256']
files=sorted((base/'source').glob('*.rs'))+sorted(p for p in (base/'assets').rglob('*') if p.is_file())
expected={str(p.relative_to(base)):sha(p) for p in files}
assert {str(p.relative_to(base)):sha(p) for p in (base/'source').glob('*.rs')}==build['source_after']
record={'protocol':'Deterministic coefficient CSE/common-pair correctness and single preparation diagnostics; no warm timing','preparation_sha256':sha(base/'preparation.json'),'build_sha256':sha(base/'compile.json'),'binary_sha256':sha(base/'probe'),'runner_sha256':sha(Path(__file__)),'source_and_assets':expected,'cases':[],'status':'running'}
manifest=output/'runtime-manifest.json'
if manifest.exists():
 old=json.loads(manifest.read_text());assert all(old[k]==record[k] for k in ['build_sha256','binary_sha256','runner_sha256','source_and_assets']);record=old
for case in sys.argv[1:] or ['ggh','gghh','gghhh','gggg-up']:
 assert case not in [r['case'] for r in record['cases']]
 command=['taskset','-c','8','timeout','--signal=TERM','--kill-after=10','300',str(base/'probe'),case,str(output/case)]
 started=time.time();log=output/f'{case}.log'
 item={'case':case,'command':command,'started_unix_time':started,'status':'running'};record['cases'].append(item);manifest.write_text(json.dumps(record,indent=2)+'\n')
 with log.open('w') as stream: code=subprocess.call(command,stdout=stream,stderr=subprocess.STDOUT)
 item.update(returncode=code,finished_unix_time=time.time(),elapsed_seconds=time.time()-started,status='passed' if code==0 else 'failed',log_sha256=sha(log))
 result=output/case/'outputs.json'
 if result.exists():
  data=json.loads(result.read_text());item.update(result_sha256=sha(result),result_status=data['status'],failed_comparisons=data['failed_comparisons']);assert (code==0)==(data['status']=='passed')
 elif code==0:raise AssertionError('successful process omitted final output artifact')
 assert sha(base/'probe')==record['binary_sha256'];assert {str(p.relative_to(base)):sha(p) for p in files}==expected
 item['artifacts']={str(p.relative_to(output)):sha(p) for p in sorted((output/case).rglob('*')) if p.is_file()}
 manifest.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:item[k] for k in ['case','returncode','elapsed_seconds','status']}),flush=True)
record['status']='passed' if all(r['status']=='passed' for r in record['cases']) else 'failures_retained';manifest.write_text(json.dumps(record,indent=2)+'\n')
