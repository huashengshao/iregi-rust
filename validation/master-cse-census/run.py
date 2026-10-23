from pathlib import Path
import hashlib,json,os,signal,subprocess,time
root=Path.cwd();base=root/'target/master-cse-census';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();build=json.loads((base/'build.json').read_text());prep=json.loads((base/'preparation.json').read_text())
assert build['exit_code']==0 and build['source_unchanged'] and build['archives_unchanged']
assert sha(base/'census')==build['binary_sha256'] and sha(base/'source/census.rs')==build['source_sha256']
assert not (base/'qualification.json').exists(),'preserve previous run'
for item in prep['artifacts'].values():assert sha(Path(item['archive']))==item['sha256']
cmd=['taskset','-c','20,21',str(base/'census')]
record={'scope':'Exact symbolic root/control identity census conditional on trusted Symbolica structured SSA/liveness/CSE dominance; no floating evaluation, independent branch-definedness proof, numerical or performance qualification','command':cmd,'build_sha256':sha(base/'build.json'),'binary_sha256':build['binary_sha256'],'source_sha256':build['source_sha256'],'preparation_sha256':sha(base/'preparation.json'),'reuse_checks_sha256':sha(base/'REUSE-CHECKS.md'),'runner_sha256':sha(Path(__file__)),'timeout_seconds':120,'started_unix_time':time.time(),'license_environment_present':any('SYMBOLICA' in name and 'LICENSE' in name for name in os.environ)}
start=time.monotonic()
with (base/'results.jsonl').open('w') as output,(base/'run.log').open('w') as errors:
 process=subprocess.Popen(cmd,stdout=output,stderr=errors,start_new_session=True)
 try:record['exit_code']=process.wait(timeout=120)
 except subprocess.TimeoutExpired:
  os.killpg(process.pid,signal.SIGTERM)
  try:process.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
  record.update(exit_code=process.returncode,timed_out=True)
record.update(elapsed_seconds=time.monotonic()-start,binary_unchanged=sha(base/'census')==build['binary_sha256'],source_unchanged=sha(base/'source/census.rs')==build['source_sha256'],archives_unchanged=all(sha(Path(item['archive']))==item['sha256'] for item in prep['artifacts'].values()),raw_sha256=sha(base/'results.jsonl'),log_sha256=sha(base/'run.log'))
rows=[];failures=[]
try:
 rows=[json.loads(line) for line in (base/'results.jsonl').read_text().splitlines()]
 assert [row['family'] for row in rows]==['A0','B0','C0']
 for row in rows:
  assert row['status']=='passed',row
  assert type(row['exact_outputs_proved']) is int and row['exact_outputs_proved']==6
  assert row['registered_descriptors_unchanged'] is True
  assert row['before']['inputs']==row['after']['inputs']==len(row['parameters'])
  assert row['before']['outputs']==row['after']['outputs']==6
  assert 'conditional on trusted Symbolica' in row['scope']
except Exception as error:failures.append(str(error))
record.update(status='passed' if record['exit_code']==0 and not failures and all(record[k] for k in ['binary_unchanged','source_unchanged','archives_unchanged']) else 'failed',failures=failures,rows=rows,production_changed=False,numerical_and_performance_qualification='unrun')
(base/'qualification.json').write_text(json.dumps(record,indent=2,allow_nan=False)+'\n');print(json.dumps(record,indent=2))
raise SystemExit(0 if record['status']=='passed' else 1)
