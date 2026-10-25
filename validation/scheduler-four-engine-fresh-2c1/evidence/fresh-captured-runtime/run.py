"""Proposed untimed numerical stage; execution requires a separate root grant."""
from pathlib import Path
import datetime,hashlib,json,os,sys
sys.dont_write_bytecode=True
import admission as a
from lifecycle import Budget,digest,freeze_binary
from interactive import Session,close_all
ROOT=Path('/shared/external/iregi/iregi-rust');HERE=ROOT/'target/guard-performance-review/optimized-performance-proposal/fresh-captured-runtime'
def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def payload(case,rows):return json.dumps({'id':case['id'],'n':case['n'],'rank':case['rank'],'algorithm':'Hybrid','samples':case['samples'][:rows]},allow_nan=False)+'\n'
def main():
 assert Path.cwd()==ROOT and len(sys.argv)==2
 protocol_path=HERE/'protocol.json';reviewed=sys.argv[1];assert digest(protocol_path)==reviewed
 protocol=read(protocol_path);folder=HERE/'qualification-001';folder.mkdir(exist_ok=False)
 cases=read(protocol['inputs']);shape=read(HERE/'control-shapes.json')
 assert len(cases)==4 and len({(c['n'],c['rank'])for c in cases})==4
 coords=[(case,rows)for case in cases for rows in [1,32]]
 budget=Budget(protocol['aggregate_budget_seconds']);budget.work_deadline=budget.deadline-protocol['cleanup_postguard_reserve_seconds']
 bindings={Path(p)if Path(p).is_absolute()else ROOT/p:v for p,v in protocol['protected_sha256'].items()}
 record={'status':'preparing','scope':protocol['scope'],'protocol_sha256':reviewed,'runner_sha256':digest(Path(__file__)),
  'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_sha256':{str(p):v for p,v in bindings.items()},
  'build_receipt':protocol['build_receipt'],'build_receipt_sha256':protocol['build_receipt_sha256'],
  'aggregate_budget_seconds':protocol['aggregate_budget_seconds'],'cleanup_postguard_reserve_seconds':protocol['cleanup_postguard_reserve_seconds'],
  'rows':[{'id':c['id'],'batch':n,'status':'unrun'}for c,n in coords],
  'retained_rows':[{'id':c['id'],'batch':n,'status':'unrun'}for c,n in coords],
  'controls':{'status':'unrun'},'invalid_request_controls':{'status':'unrun'},'processes':[],'executed_executables':{},'cleanup_errors':[],
  'license_environment_present':any('SYMBOLICA'in name and'LICENSE'in name for name in os.environ),
  'performance_measurement':False,'production_adoption_qualified':False}
 receipt=folder/'results.json';save(receipt,record);sessions=[];raw=None;serial=0
 def verify():
  assert digest(protocol_path)==reviewed,'Protocol changed'
  for p,v in bindings.items():budget.remaining();assert digest(p)==v,'Changed input: '+str(p)
  for p,v in protocol['tool_sha256'].items():budget.remaining();assert digest(p)==v,'Changed tool: '+p
 def executable_guards():
  budget.remaining();assert digest(protocol_path)==reviewed
  assert digest(Path(protocol['build_receipt']))==protocol['build_receipt_sha256']
  for item in record['executed_executables'].values():assert digest(Path(item['path']))==item['sha256']
 def ask(session,text,stage,key):
  nonlocal serial
  executable_guards();serial+=1;item={'serial':serial,'stage':stage,'key':key,'engine':session.label,'payload':text}
  raw.write(json.dumps({**item,'event':'request'},allow_nan=False)+'\n');raw.flush()
  response=session.request(text,budget)
  raw.write(json.dumps({**item,'event':'response','response':response},allow_nan=False)+'\n');raw.flush()
  executable_guards();return response
 budget.arm()
 try:
  verify();record['guard_before']=True;raw=(folder/'responses.jsonl').open('x')
  for label in ['baseline','candidate']:
   item=protocol['probes'][label];copy=freeze_binary(Path(item['path']),item['sha256'],folder/(label+'-frozen'),budget)
   bindings[copy]=item['sha256'];record['executed_executables'][label]={'path':str(copy),'sha256':item['sha256']};save(receipt,record)
   session=Session(label);sessions.append(session)
   session.start(copy,protocol['taskset'],folder,budget,lambda event:(record['processes'].append(event),save(receipt,record)))
  baseline,candidate=sessions;initial={}
  for index,(case,rows)in enumerate(coords):
   row=record['rows'][index];row['status']='running';save(receipt,record);key=[case['id'],rows];text=payload(case,rows)
   left=ask(baseline,text,'initial',key);right=ask(candidate,text,'initial',key)
   checks=[a.response(value,case,rows)for value in [left,right]]
   assert a.exact(left,right),'Complete cross-archive record differs'
   for session,expected in [(baseline,left),(candidate,right)]:
    repeated=ask(session,text,'own-repeat',key);a.response(repeated,case,rows)
    assert a.exact(a.canonical(repeated),a.canonical(expected)),'Own complete response changed'
   row.update(status='passed',comparison=checks[0],cross_archive_complete_record_exact=True,own_complete_repeats_exact=True)
   initial[tuple(key)]=left;save(receipt,record)
  left=ask(baseline,'CONTROLS\n','controls',['controls',0]);right=ask(candidate,'CONTROLS\n','controls',['controls',0])
  details=[a.controls(v,shape)for v in [left,right]];assert a.exact(left,right),'Complete controls differ across archives'
  for session,expected in [(baseline,left),(candidate,right)]:
   repeated=ask(session,'CONTROLS\n','controls-repeat',['controls',1]);a.controls(repeated,shape)
   assert a.exact(repeated,expected),'Own complete controls changed'
  record['controls']={'status':'passed','comparison':details[0],'cross_archive_complete_record_exact':True,'own_complete_repeats_exact':True};save(receipt,record)
  for index,(case,rows)in enumerate(coords):
   key=[case['id'],rows];text=payload(case,rows);left=ask(baseline,text,'retained',key);right=ask(candidate,text,'retained',key)
   for value in [left,right]:a.response(value,case,rows);assert a.exact(a.canonical(value),a.canonical(initial[tuple(key)])),'Retained complete output changed'
   assert a.exact(left,right),'Retained complete cross-archive response differs'
   record['retained_rows'][index]['status']='passed';save(receipt,record)
  checks=[];base=json.loads(payload(cases[0],1))
  for field,value in [('engine','baseline'),('warmup',1),('repeats',1),('iterations',1)]:
   text=json.dumps({**base,field:value})+'\n'
   for session in sessions:
    response=ask(session,text,'invalid-request',[field,value])
    assert response=={'status':'invalid_request','error':'qualification is untimed; engine and timing counts are forbidden'}
   checks.append({'field':field,'value':value,'status':'passed'})
  record['invalid_request_controls']={'status':'passed','cases':checks};record['status']='completed-awaiting-cleanup'
 except Exception as error:record.update(status='failed',error=repr(error))
 finally:
  record['process_terminals']=close_all(sessions,budget,record['cleanup_errors'])
  if raw is not None:
   try:raw.close()
   except Exception as error:record['cleanup_errors'].append('raw close: '+repr(error))
  record['request_count']=serial;record['elapsed_seconds_diagnostic']=budget.elapsed()
  record['deadline_exceeded']=record['elapsed_seconds_diagnostic']>protocol['aggregate_budget_seconds']
  save(receipt,record) # terminal/cleanup precedes all post-execution hashes
 try:
  verify();executable_guards();record['guard_after']=True
  record['raw_sha256']=digest(folder/'responses.jsonl')
  record['stderr_sha256']={s.label:digest(folder/(s.label+'.stderr.log'))for s in sessions}
  record['stdout_sha256']={s.label:digest(folder/(s.label+'.stdout.log'))for s in sessions}
 except Exception as error:record.update(guard_after=False,guard_error=repr(error))
 record['elapsed_seconds_diagnostic']=budget.elapsed();record['deadline_exceeded']|=record['elapsed_seconds_diagnostic']>protocol['aggregate_budget_seconds']
 if budget.cancelled:record['cancellation']=budget.cancelled
 success=all(r['status']=='passed'for r in record['rows']+record['retained_rows'])and record['controls']['status']=='passed'and record['invalid_request_controls']['status']=='passed'
 success=success and len(record['process_terminals'])==2 and all(p['returncode']==0 and p['owned_group_gone']and p['received_responses']==30 for p in record['process_terminals'])
 success=success and record.get('guard_after')is True and not record['cleanup_errors']and not record['deadline_exceeded']and'error'not in record and not budget.cancelled and serial==60
 record['status']='passed-awaiting-independent-saved-data-review'if success else'failed'
 record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(receipt,record);budget.disarm()
 print(json.dumps({'status':record['status'],'receipt_sha256':digest(receipt),'requests':serial,'elapsed_seconds_diagnostic':record['elapsed_seconds_diagnostic']}))
 return 0 if success else 1
if __name__=='__main__':raise SystemExit(main())
