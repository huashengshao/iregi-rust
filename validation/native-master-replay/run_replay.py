from pathlib import Path
import argparse,hashlib,json,os,subprocess,time
from replay_parser import validate_rows
root=Path.cwd();base=root/'target/native-master-replay';p=argparse.ArgumentParser();p.add_argument('--benchmark',action='store_true');p.add_argument('--cpus',default='20,21');p.add_argument('--phase',choices=['initial','before','after'],default='initial');p.add_argument('--quiet-window');args=p.parse_args()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();build=json.loads((base/'replay-build.json').read_text());capture=json.loads((base/'capture-results.json').read_text());binary=base/'replay'
assert build['exit_code']==0 and build['sources_before']==build['sources_after'] and sha(binary)==build['binary_sha256']
for path,digest in build['sources_before'].items():assert sha(base/path)==digest,path
for item in build['archives'].values():assert sha(Path(item['path']))==item['sha256']
capture_qualification=json.loads((base/'capture-qualification.json').read_text());assert capture_qualification['captures_sha256']==sha(base/'capture-results.json') and capture_qualification['status']=='actual-master-capture-qualified-replay-unrun'
initial=None
if args.benchmark or args.phase!='initial':
 initial=json.loads((base/'replay-qualification-initial.json').read_text());assert initial['status']=='passed' and initial['binary_sha256']==build['binary_sha256']
 assert initial['capture_sha256']==sha(base/'capture-results.json') and initial['jsonl_sha256']==sha(base/'replay-qualification-initial.jsonl')
if args.benchmark:
 assert args.quiet_window and Path(args.quiet_window).is_file(),'requires explicit parent-granted quiet window'
 assert ',' not in args.cpus and '-' not in args.cpus,'timings require one CPU'
stem='replay-timing' if args.benchmark else f'replay-qualification-{args.phase}';assert not (base/f'{stem}.json').exists(),'preserve previous attempt'
cmd=['taskset','-c',args.cpus,str(binary)]+(['--benchmark'] if args.benchmark else [])
record={'scope':'Raw native versus Symbolica master kernels on actual whole-core request bundles; excludes adapter validation/output allocation and complete reduction','command':cmd,'binary_sha256':build['binary_sha256'],'build_sha256':sha(base/'replay-build.json'),'capture_sha256':sha(base/'capture-results.json'),'runner_sha256':sha(Path(__file__)),'parser_sha256':sha(base/'replay_parser.py'),'sources':build['sources_before'],'started_unix_time':time.time(),'license_environment_present':any('SYMBOLICA' in k and 'LICENSE' in k for k in os.environ)}
if args.benchmark:record.update(quiet_window=args.quiet_window,quiet_window_sha256_at_start=sha(Path(args.quiet_window)))
start=time.monotonic()
with (base/f'{stem}.jsonl').open('w') as out,(base/f'{stem}.log').open('w') as err:
 try:
  process=subprocess.run(cmd,stdout=out,stderr=err,timeout=180);record.update(exit_code=process.returncode,status='passed' if process.returncode==0 else 'failed')
 except subprocess.TimeoutExpired:record.update(exit_code=None,status='timeout')
record.update(finished_unix_time=time.time(),elapsed_seconds=time.monotonic()-start,binary_unchanged=sha(binary)==build['binary_sha256'],sources_unchanged=all(sha(base/path)==digest for path,digest in build['sources_before'].items()),capture_unchanged=sha(base/'capture-results.json')==record['capture_sha256'],archives_unchanged=all(sha(Path(item['path']))==item['sha256'] for item in build['archives'].values()),jsonl_sha256=sha(base/f'{stem}.jsonl'),log_sha256=sha(base/f'{stem}.log'))
record.update(runner_unchanged=sha(Path(__file__))==record['runner_sha256'],parser_unchanged=sha(base/'replay_parser.py')==record['parser_sha256'])
rows=[];errors=[]
try:
 rows=[json.loads(line) for line in (base/f'{stem}.jsonl').read_text().splitlines()]
 validate_rows(rows,capture,args.benchmark)
 if initial is not None:
  baseline=[json.loads(line) for line in (base/'replay-qualification-initial.jsonl').read_text().splitlines()]
  validate_rows(baseline,capture,False)
  assert len(rows)==len(baseline)
  for actual,original in zip(rows,baseline):
   assert actual['result']['represented_outputs']==original['result']['represented_outputs'],'represented outputs changed since initial qualification'
  record['initial_qualification_sha256']=sha(base/'replay-qualification-initial.json')
  record['initial_outputs_bitwise_unchanged']=True
except Exception as error:errors.append(str(error));record['status']='failed'
record.update(rows=len(rows),validation_errors=errors)
if not all(record[k] for k in ['binary_unchanged','sources_unchanged','capture_unchanged','archives_unchanged','runner_unchanged','parser_unchanged']):record['status']='failed'
(base/f'{stem}.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
raise SystemExit(0 if record['status']=='passed' else 1)
