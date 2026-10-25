"""Reviewed-protocol six-process preflight/timing runner; import launches nothing."""
from pathlib import Path
import datetime
import json
import math
import os
import sys
sys.dont_write_bytecode=True
from lifecycle import Budget,digest,freeze_binary
from interactive import Session,close_all
import common as c
ROOT=Path('/shared/external/iregi/iregi-rust')

def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def main():
 assert Path.cwd()==ROOT and len(sys.argv)==3,'run.py protocol-path reviewed-protocol-sha256'
 protocol_path=Path(sys.argv[1]).resolve();reviewed=sys.argv[2];assert digest(protocol_path)==reviewed
 p=c.read(protocol_path);assert p['mode']in['preflight','timing']and p['pinned_source_revision']==c.PIN
 assert p['request_policy']['orders']==[list(order)for order in c.ORDERS]
 cpu=p['cpu'];assert type(cpu)is int and cpu in os.sched_getaffinity(0)
 if p['mode']=='timing':
  grant=c.read(p['quiet_grant']['path']);assert digest(p['quiet_grant']['path'])==p['quiet_grant']['sha256']
  c.validate_quiet_grant(p,grant)
 folder=Path(p['attempt_directory']);folder.mkdir(exist_ok=False)
 budget=Budget(p['aggregate_budget_seconds']);budget.work_deadline=budget.deadline-p['cleanup_postguard_reserve_seconds']
 bindings={Path(path):wanted for path,wanted in p['protected_sha256'].items()}
 record={'schema_version':1,'status':'preparing','mode':p['mode'],'run_id':p['run_id'],'scope':p['scope'],'pinned_source_revision':c.PIN,
  'protocol':str(protocol_path),'protocol_sha256':reviewed,'runner_sha256':digest(Path(__file__)),
  'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cpu':cpu,
  'aggregate_budget_seconds':p['aggregate_budget_seconds'],'cleanup_postguard_reserve_seconds':p['cleanup_postguard_reserve_seconds'],
  'orders':[list(order)for order in c.ORDERS],'ratio_inventory':[{'numerator':a,'denominator':b}for a,b in c.RATIOS],
  'initialization':{'status':'unrun','schedule':p['initialization_schedule'],'raw_serials':[]},
  'controls_before':{'status':'unrun','raw_serials':[]},'controls_after':{'status':'unrun','raw_serials':[]},
  'rows':[{'id':case['id'],'outer_batch':batch,'status':'unrun','before_raw_serials':[],'after_raw_serials':[],'calibration':[],'blocks':[]}for case in c.read(p['inputs'])for batch in[1,32]],
  'processes':[],'executed_executables':{},'cleanup_errors':[],'input_sha256':{str(path):wanted for path,wanted in bindings.items()},
  'quiet_grant':p.get('quiet_grant'),'license_environment_present':any('SYMBOLICA'in name and'LICENSE'in name for name in os.environ),
  'production_adoption_qualified':False}
 receipt=folder/'receipt.json';save(receipt,record);sessions=[];by_label={};raw=None;serial=0
 def verify():
  assert digest(protocol_path)==reviewed
  for path,wanted in bindings.items():budget.remaining();assert digest(path)==wanted,'Changed input: '+str(path)
  for path,wanted in p['tool_sha256'].items():budget.remaining();assert digest(path)==wanted,'Changed tool: '+path
 def ask(label,payload,meta):
  nonlocal serial
  budget.remaining();assert digest(protocol_path)==reviewed
  executable=record['executed_executables'][label];assert digest(executable['path'])==executable['sha256']
  serial+=1;item={'serial':serial,'engine':label,'payload':payload,**meta}
  raw.write(json.dumps({**item,'event':'request'},allow_nan=False)+'\n');raw.flush()
  answer=by_label[label].request(payload,budget)
  raw.write(json.dumps({**item,'event':'response','response':answer},allow_nan=False)+'\n');raw.flush()
  return answer,serial
 def controls(stage,context):
  answers={};serials=[]
  for label in c.TIRUST:
   answer,index=ask(label,'CONTROLS\n',{'stage':stage,'kind':'controls'})
   context.controls_check(label,answer);answers[label]=answer;serials.append(index)
  context.cross_roles(answers)
  return {'status':'passed','raw_serials':serials}
 def family(stage,context,case,batch):
  answers={};serials=[]
  for label in c.LABELS:
   answer,index=ask(label,c.request_payload(label,case,batch,stage),{'stage':stage,'kind':'qualification','id':case['id'],'batch':batch})
   answers[label]=answer;serials.append(index)
  context.check_family(answers,case,batch)
  return answers,serials
 def measured(context,label,case,batch,n,warmup,stage,index,expected):
  assert type(n)is int and 0<n<=c.MAX_COUNT
  answer,serial=ask(label,c.request_payload(label,case,batch,stage,n,warmup),{'stage':stage,'kind':'timing','id':case['id'],'batch':batch,'iterations':n,'warmup':warmup,'block':index})
  elapsed,ns=context.timed(label,answer,expected,n,case,batch)
  return {'engine':label,'iterations':n,'elapsed_ns':elapsed,'ns_per_call':ns,'raw_serial':serial,
          'elapsed_provenance':'integer Rust Instant nanoseconds'if label in c.TIRUST else'reconstructed floating reference ns/call times integer iterations; raw integer clock ticks not exported'}
 budget.arm()
 try:
  verify();record['guard_before']=True
  context=c.Context(p,budget.remaining)
  os.sched_setaffinity(0,{cpu})
  raw=(folder/'raw.jsonl').open('x')
  for label in c.LABELS:
   item=p['processes'][label];binary=freeze_binary(Path(item['path']),item['sha256'],folder/(label+'-frozen'),budget)
   bindings[binary]=item['sha256'];record['input_sha256'][str(binary)]=item['sha256']
   record['executed_executables'][label]={'path':str(binary),'sha256':item['sha256']};save(receipt,record)
   session=Session(label);sessions.append(session);by_label[label]=session
   session.start(binary,p['taskset'],folder,budget,lambda event:(record['processes'].append(event),save(receipt,record)),cpu)
  record['initialization']['status']='running'
  for case,batch in context.coords:
   answers={}
   for label in c.TIRUST:
    for repeat in [0,1]:
     answer,index=ask(label,c.request_payload(label,case,batch,'initialization'),{'stage':'initialization','kind':'initialization','id':case['id'],'batch':batch,'repeat':repeat})
     context.normal_check(label,answer,case,batch,'initial'if repeat==0 else'own-repeat')
     record['initialization']['raw_serials'].append(index);answers[(label,repeat)]=answer
   for repeat in [0,1]:context.cross_roles({label:answers[(label,repeat)]for label in c.TIRUST})
  assert len(record['initialization']['raw_serials'])==64
  record['initialization']['status']='passed';record['controls_before']=controls('controls-before',context)
  stop=False
  for row,(case,batch)in zip(record['rows'],context.coords):
   row['status']='running';save(receipt,record)
   try:
    before,row['before_raw_serials']=family('before',context,case,batch)
    if p['mode']=='preflight':row['status']='admitted-without-timings'
    else:
     n=1;calibrated=False
     for round_index in range(8):
      values=[measured(context,label,case,batch,n,10 if round_index==0 else 0,'calibration',round_index,before)for label in c.ENGINES]
      row['calibration'].append(values);minimum=min(value['elapsed_ns']for value in values)
      if minimum>=c.MINIMUM_NS:calibrated=True;break
      if round_index<7:n=c.next_count(n,minimum)
     row['iterations']=n
     if not calibrated:row['status']='calibration-inconclusive'
     else:
      predicted=48*sum(value['elapsed_ns']for value in values)/1e9;row['estimated_acceptance_seconds']=predicted
      row['remaining_work_seconds']=budget.remaining()
      if predicted+2>row['remaining_work_seconds']:row['status']='budget-inconclusive';stop=True
      else:
       for index,order in enumerate(c.ORDERS):
        block={'index':index,'order':list(order),'engines':[]};row['blocks'].append(block)
        for label in order:block['engines'].append(measured(context,label,case,batch,n,0,'acceptance',index,before))
       row['short_blocks']=sum(value['elapsed_ns']<c.MINIMUM_NS for block in row['blocks']for value in block['engines'])
       row['status']='short-block-inconclusive'if row['short_blocks']else'completed'
    after,row['after_raw_serials']=family('after',context,case,batch)
    for label in c.TIRUST:assert c.exact(c.canonical(before[label]),c.canonical(after[label]))
    assert c.exact(c.ref.reference(before['iregi'],case,case['samples'][:batch]),c.ref.reference(after['iregi'],case,case['samples'][:batch]))
    assert c.exact(c.ref.canonical_collier(before['collier']),c.ref.canonical_collier(after['collier']))
    row['before_after_qualification']='passed'
   except Exception as error:
    row.update(status='failed',error=repr(error));raise
   save(receipt,record)
   if stop:break
  record['controls_after']=controls('controls-after',context)
 except Exception as error:record['error']=repr(error)
 finally:
  record['numerical_elapsed_seconds']=budget.elapsed()
  record['process_terminals']=close_all(sessions,budget,record['cleanup_errors'])
  if raw is not None:
   try:raw.close()
   except Exception as error:record['cleanup_errors'].append('raw close: '+repr(error))
  record['raw_request_count']=serial;record['cleanup_finished_elapsed_seconds']=budget.elapsed()
  record['status']='terminal-awaiting-postguards';save(receipt,record)
 try:
  verify();record['guard_after']=True
  record['raw_sha256']=digest(folder/'raw.jsonl')
  record['stderr_sha256']={session.label:digest(folder/(session.label+'.stderr.log'))for session in sessions}
  record['stdout_sha256']={session.label:digest(folder/(session.label+'.stdout.log'))for session in sessions}
 except Exception as error:record.update(guard_after=False,guard_error=repr(error))
 record['elapsed_seconds']=budget.elapsed();record['deadline_exceeded']=record['elapsed_seconds']>p['aggregate_budget_seconds']
 if budget.cancelled:record['cancellation']=budget.cancelled
 clean=record.get('guard_before')is True and record.get('guard_after')is True and not record['cleanup_errors']and not record['deadline_exceeded']and not budget.cancelled and all(key not in record for key in ['error','guard_error'])
 clean=clean and len(record['process_terminals'])==6 and all(value['returncode']==0 and value['owned_group_gone']is True for value in record['process_terminals'])
 clean=clean and record['initialization']['status']==record['controls_before']['status']==record['controls_after']['status']=='passed'
 record['global_lifecycle_clean']=clean
 complete=all(row.get('before_after_qualification')=='passed'and row['status']in(['admitted-without-timings']if p['mode']=='preflight'else['completed','short-block-inconclusive'])for row in record['rows'])
 record['status']=('completed-preflight'if p['mode']=='preflight'else'completed-with-inconclusive-rows'if any(row['status']=='short-block-inconclusive'for row in record['rows'])else'completed')if clean and complete else'inconclusive-or-failed'
 record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(receipt,record);budget.disarm()
 print(json.dumps({'status':record['status'],'receipt_sha256':digest(receipt),'raw_requests':serial,'elapsed_seconds':record['elapsed_seconds']}))
 return 0 if clean and complete else 1
if __name__=='__main__':raise SystemExit(main())
