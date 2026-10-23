from pathlib import Path
import datetime,hashlib,json,os,re,signal,subprocess,sys,time
root=Path.cwd();base=root/'target/core-stack-reuse';variant,filter_text=sys.argv[1:3]
assert variant in ['baseline','candidate','capture']
limit=float(sys.argv[3]) if len(sys.argv)>3 else 180
name=filter_text.replace('::','_') if variant!='capture' else 'complete-corpus'
out=base/'runs'/f'{variant}-{name}-{datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")}'
out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
if variant=='capture':
 binary=base/'capture';record=json.loads((base/'capture-compile.json').read_text());expected=record['binary_sha256'];args=['taskset','-c','0',str(binary),str(out/'outputs.json')]
else:
 binary=base/variant/'core_tests';record=json.loads((base/variant/'compile.json').read_text());expected=record['binary_sha256'];args=['taskset','-c','0',str(binary),filter_text,'--nocapture','--test-threads=1']
assert sha(binary)==expected
before=sha(binary);env=os.environ.copy();env['IREGI_CORE_STACK_PROOF_DIR']=str(out/'graphs');env['RUST_TEST_THREADS']='1'
start=time.monotonic();expired=False
with (out/'run.log').open('w') as log:
 child=subprocess.Popen(args,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  while True:
   pid,status,usage=os.wait4(child.pid,os.WNOHANG)
   if pid: child.returncode=os.waitstatus_to_exitcode(status);break
   if time.monotonic()-start>=limit:
    expired=True;os.killpg(child.pid,signal.SIGKILL);_,status,usage=os.wait4(child.pid,0);child.returncode=os.waitstatus_to_exitcode(status);break
   time.sleep(.1)
 finally:
  if child.returncode is None:
   try:os.killpg(child.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   _,status,usage=os.wait4(child.pid,0);child.returncode=os.waitstatus_to_exitcode(status)
log=(out/'run.log').read_text();match=re.search(r'test result: (?:ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored;',log)
counts=None if not match else dict(zip(['passed','failed','ignored'],map(int,match.groups())))
graphs=[json.loads(l) for p in (out/'graphs').rglob('graphs.jsonl') for l in p.read_text().splitlines()]
report={'variant':variant,'command':args,'binary_sha256_before':before,'binary_sha256_after':sha(binary),'timeout_seconds':limit,'timed_out':expired,'exit_code':child.returncode,'elapsed_seconds':time.monotonic()-start,'max_rss_kib':usage.ru_maxrss,'test_counts':counts,'graph_count':len(graphs),'graphs_with_reduced_temporaries':sum(g['after_temporaries']<g['before_temporaries'] for g in graphs),'structural_proof_all_passed':bool(graphs) and all(g['unchanged_provenance'] and g['unchanged_helpers'] for g in graphs),'diagnostic_only':'Instrumented proof; no performance or preparation-memory claim.','runner_sha256':sha(Path(__file__))}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True);print(out,flush=True)
if child.returncode or expired:print(log[-12000:],flush=True)
qualified=before==report['binary_sha256_after'] and report['structural_proof_all_passed'] and (len(json.loads((out/'outputs.json').read_text()))==12 if variant=='capture' and child.returncode==0 else counts and counts['passed']+counts['failed']>0)
raise SystemExit(124 if expired else child.returncode or (0 if qualified else 2))
