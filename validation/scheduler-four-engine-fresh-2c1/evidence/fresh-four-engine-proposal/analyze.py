"""Saved-raw admission/statistics only; never launches an executable-under-test."""
from pathlib import Path
import argparse
from collections import Counter
import json
import math
import sys
sys.dont_write_bytecode=True
import common as c

def verify_saved_logs(folder,receipt):
 # Exact inventories plus actual persisted bytes: producer hash declarations
 # alone are not evidence that stdout/stderr custody survived after cleanup.
 for stream in['stdout','stderr']:
  wanted=receipt[stream+'_sha256']
  assert type(wanted)is dict and set(wanted)==set(c.LABELS),'Saved '+stream+' label inventory differs'
  for label in c.LABELS:
   path=folder/(label+'.'+stream+'.log')
   assert path.is_file()and not path.is_symlink(),'Saved log is missing or is a symlink'
   assert c.ref.sha(path)==wanted[label],'Saved '+stream+' bytes changed: '+label
 return True

def summarize(row,admitted):
 blocks=row.get('blocks',[]);timings={engine:[]for engine in c.ENGINES};short=0
 for index,block in enumerate(blocks):
  assert block['index']==index and block['order']==list(c.ORDERS[index])
  assert[value['engine']for value in block['engines']]==list(c.ORDERS[index])
  for value in block['engines']:
   assert type(value['iterations'])is int and value['iterations']==row['iterations']
   ns=value['ns_per_call'];elapsed=value['elapsed_ns']
   assert type(ns)in(int,float)and math.isfinite(ns)and ns>0
   assert type(elapsed)in(int,float)and math.isfinite(elapsed)and elapsed>0
   timings[value['engine']].append(ns);short+=elapsed<c.MINIMUM_NS
 complete=admitted and len(blocks)==48 and short==0
 result={'id':row['id'],'batch':row['outer_batch'],'status':row['status'],'quartets':len(blocks),'short_blocks':short,'engine_samples_ns':timings,'ratios':[]}
 for numerator,denominator in c.RATIOS:
  item={'numerator':numerator,'denominator':denominator,'definition':numerator+' / '+denominator,'gate':'inconclusive-incomplete-family','statistics':None}
  if len(blocks)==48:
   def ratio(indices):
    value=c.ref.h.ratio_summary([timings[numerator][index]for index in indices],[timings[denominator][index]for index in indices],{'status':'passed'if complete else'failed'})
    value['definition']=numerator+' / '+denominator+' paired quartet latency;99% bootstrap median CI;relative width<=2%'
    return value
   statistics=ratio(range(48));item['statistics']=statistics
   item['gate']=statistics['gate']if complete else'inconclusive-short-block'if admitted and short else'correctness-or-cohort-failed'
   item['order_strata']={}
   for first in [True,False]:
    indices=[index for index,block in enumerate(blocks)if(block['order'].index(numerator)<block['order'].index(denominator))is first]
    assert len(indices)==24
    item['order_strata']['numerator_first'if first else'denominator_first']=ratio(indices)
   item['slower_pairs']=sum(left>right for left,right in zip(timings[numerator],timings[denominator]))
  result['ratios'].append(item)
 return result

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('attempt',type=Path)
 parser.add_argument('--quiet-release',type=Path);parser.add_argument('--quiet-release-sha256')
 args=parser.parse_args();folder=args.attempt.resolve();receipt_path=folder/'receipt.json';receipt=c.read(receipt_path)
 p=c.read(receipt['protocol']);raw_path=folder/'raw.jsonl';events=c.raw(raw_path);global_errors=[];family_errors={};used=set()
 assert c.ref.sha(receipt['protocol'])==receipt['protocol_sha256']
 if p['mode']=='timing':
  assert args.quiet_release is not None and args.quiet_release_sha256 is not None,'Statistics wait for root quiet-lease release'
  assert c.ref.sha(args.quiet_release)==args.quiet_release_sha256
  release=c.read(args.quiet_release);assert release['status']=='released'and release['receipt_sha256']==c.ref.sha(receipt_path)
  assert release['quiet_grant_sha256']==p['quiet_grant']['sha256']and release['cpu']==p['cpu']
 try:
  assert receipt['global_lifecycle_clean']is True and receipt['guard_before']is True and receipt['guard_after']is True
  verify_saved_logs(folder,receipt)
  assert str(folder)==p['attempt_directory']and receipt['run_id']==p['run_id'],'Actual attempt/run ID differs from prepared one-shot context'
  if p['mode']=='timing':
   assert c.exact(receipt['quiet_grant'],p['quiet_grant'])
   assert c.ref.sha(p['quiet_grant']['path'])==p['quiet_grant']['sha256']
   c.validate_quiet_grant(p,c.read(p['quiet_grant']['path']))
  assert not any(key in receipt for key in ['error','guard_error','cancellation'])and receipt['cleanup_errors']==[]and receipt['deadline_exceeded']is False
  assert receipt['pinned_source_revision']==p['pinned_source_revision']==c.PIN and receipt['cpu']==p['cpu']
  elapsed=[receipt[key]for key in['numerical_elapsed_seconds','cleanup_finished_elapsed_seconds','elapsed_seconds']]
  assert all(type(value)in(int,float)and math.isfinite(value)for value in elapsed)
  assert 0<=elapsed[0]<=elapsed[1]<=elapsed[2]<=p['aggregate_budget_seconds']
  assert receipt['aggregate_budget_seconds']==p['aggregate_budget_seconds']and receipt['cleanup_postguard_reserve_seconds']==p['cleanup_postguard_reserve_seconds']
  assert receipt['orders']==p['request_policy']['orders']==[list(order)for order in c.ORDERS]
  assert[(value['numerator'],value['denominator'])for value in receipt['ratio_inventory']]==c.RATIOS
  for path,wanted in {**p['protected_sha256'],**p['tool_sha256'],**receipt['input_sha256']}.items():assert c.ref.sha(path)==wanted,path
  assert c.ref.sha(raw_path)==receipt['raw_sha256']
  assert len(events)==receipt['raw_request_count']*2
  assert[entry['event']for entry in events]==['request','response']*receipt['raw_request_count']
  assert[entry['serial']for entry in events]==[serial for serial in range(1,receipt['raw_request_count']+1)for _ in range(2)]
  counts=Counter(entry['engine']for entry in events[::2]);terminals=receipt['process_terminals']
  assert len(terminals)==6 and{item['label']for item in terminals}==set(c.LABELS)
  for item in terminals:assert item['returncode']==0 and item['owned_group_gone']is True and item['received_responses']==counts[item['label']]
  assert set(receipt['executed_executables'])==set(c.LABELS)
  for item in receipt['executed_executables'].values():assert c.ref.sha(item['path'])==item['sha256']
 except Exception as error:global_errors.append('global terminal/hash admission: '+repr(error))
 context=None
 try:context=c.Context(p)
 except Exception as error:global_errors.append('fresh qualification context: '+repr(error))
 coordinates=[(case,batch)for case in c.read(p['inputs'])for batch in[1,32]]
 def answer(serial,label,payload,meta):
  assert type(serial)is int and 1<=serial<=receipt['raw_request_count']and serial not in used
  request,response=events[2*serial-2:2*serial]
  wanted={'serial':serial,'engine':label,'payload':payload,**meta}
  assert c.exact(request,{**wanted,'event':'request'})
  assert set(response)==set(wanted)|{'event','response'}and response['event']=='response'
  for field,value in wanted.items():assert c.exact(response[field],value)
  used.add(serial);return response['response']
 try:
  assert receipt['initialization']['status']=='passed'and receipt['initialization']['schedule']==p['initialization_schedule']
  indices=iter(receipt['initialization']['raw_serials']);sequence=[]
  for case,batch in coordinates:
   values={}
   for label in c.TIRUST:
    for repeat in[0,1]:
     index=next(indices);sequence.append(index)
     value=answer(index,label,c.request_payload(label,case,batch,'initialization'),{'stage':'initialization','kind':'initialization','id':case['id'],'batch':batch,'repeat':repeat})
     context.normal_check(label,value,case,batch,'initial'if repeat==0 else'own-repeat');values[(label,repeat)]=value
   for repeat in[0,1]:context.cross_roles({label:values[(label,repeat)]for label in c.TIRUST})
  assert sequence==list(range(1,65))and list(indices)==[]
  for stage,key in[('controls-before','controls_before'),('controls-after','controls_after')]:
   control=receipt[key];assert control['status']=='passed'and len(control['raw_serials'])==4
   assert control['raw_serials']==(list(range(65,69))if key=='controls_before'else list(range(receipt['raw_request_count']-3,receipt['raw_request_count']+1)))
   values={}
   for label,index in zip(c.TIRUST,control['raw_serials']):
    values[label]=answer(index,label,'CONTROLS\n',{'stage':stage,'kind':'controls'});context.controls_check(label,values[label])
   context.cross_roles(values)
 except Exception as error:global_errors.append('initialization/controls: '+repr(error))
 if[(row['id'],row['outer_batch'])for row in receipt['rows']]!=[(case['id'],batch)for case,batch in coordinates]:global_errors.append('eight-family row inventory differs')
 cursor=69
 for row,(case,batch)in zip(receipt['rows'],coordinates):
  errors=[];family_errors[(case['id'],batch)]=errors
  try:
   assert row['before_after_qualification']=='passed'and'error'not in row
   sequence=row['before_raw_serials']+[value['raw_serial']for group in row['calibration']for value in group]+[value['raw_serial']for block in row['blocks']for value in block['engines']]+row['after_raw_serials']
   assert sequence==list(range(cursor,cursor+len(sequence))),'Family/calibration/quartet stages reordered'
   cursor+=len(sequence)
   stages={}
   for stage in['before','after']:
    indices=row[stage+'_raw_serials'];assert len(indices)==6;values={}
    for label,index in zip(c.LABELS,indices):values[label]=answer(index,label,c.request_payload(label,case,batch,stage),{'stage':stage,'kind':'qualification','id':case['id'],'batch':batch})
    context.check_family(values,case,batch);stages[stage]=values
   before,after=stages['before'],stages['after']
   for label in c.TIRUST:assert c.exact(c.canonical(before[label]),c.canonical(after[label]))
   assert c.exact(c.ref.reference(before['iregi'],case,case['samples'][:batch]),c.ref.reference(after['iregi'],case,case['samples'][:batch]))
   assert c.exact(c.ref.canonical_collier(before['collier']),c.ref.canonical_collier(after['collier']))
   if p['mode']=='preflight':assert row['status']=='admitted-without-timings'and row['blocks']==row['calibration']==[];continue
   n=1;assert 1<=len(row['calibration'])<=8
   allgroups=[('calibration',index,group)for index,group in enumerate(row['calibration'])]+[('acceptance',index,block['engines'])for index,block in enumerate(row['blocks'])]
   for stage,index,group in allgroups:
    order=c.ENGINES if stage=='calibration'else list(c.ORDERS[index]);assert[value['engine']for value in group]==order
    current=n if stage=='calibration'else row['iterations'];assert type(current)is int and 0<current<=c.MAX_COUNT
    intervals=[]
    for value in group:
     label=value['engine'];warmup=10 if stage=='calibration'and index==0 else 0
     assert type(value['iterations'])is int and value['iterations']==current
     response=answer(value['raw_serial'],label,c.request_payload(label,case,batch,stage,current,warmup),{'stage':stage,'kind':'timing','id':case['id'],'batch':batch,'iterations':current,'warmup':warmup,'block':index})
     elapsed,ns=context.timed(label,response,before,current,case,batch)
     assert value['elapsed_ns']==elapsed and value['ns_per_call']==ns;intervals.append(elapsed)
    if stage=='calibration':
     if index+1<len(row['calibration']):assert min(intervals)<c.MINIMUM_NS;n=c.next_count(n,min(intervals))
     else:assert min(intervals)>=c.MINIMUM_NS and n==row['iterations']
   assert len(row['blocks'])==48,'Incomplete family retained but cannot qualify complete cohort'
   short=sum(value['elapsed_ns']<c.MINIMUM_NS for block in row['blocks']for value in block['engines'])
   assert type(row['short_blocks'])is int and row['short_blocks']==short
   assert row['status']==('short-block-inconclusive'if short else'completed')
  except Exception as error:errors.append(repr(error))
 if cursor!=receipt['raw_request_count']-3:global_errors.append('controls-after must immediately follow the eight declared families')
 if used!=set(range(1,receipt['raw_request_count']+1)):global_errors.append('omitted/extra/duplicate raw response accounting')
 if any(family_errors.values()):global_errors.append('one or more complete eight-family numerical/cohort gates failed')
 expected=('completed-preflight'if p['mode']=='preflight'else'completed-with-inconclusive-rows'if any(row['status']=='short-block-inconclusive'for row in receipt['rows'])else'completed')
 if receipt['status']!=expected:global_errors.append('aggregate terminal status unexplained by raw-derived row status')
 rows=[]
 for row in receipt['rows']:
  try:
   value=summarize(row,not global_errors and not family_errors[(row['id'],row['outer_batch'])])
   if p['mode']=='preflight':
    for ratio in value['ratios']:ratio['gate']='not-measured-preflight'
   value['admission_errors']=global_errors+family_errors[(row['id'],row['outer_batch'])];rows.append(value)
  except Exception as error:rows.append({'id':row['id'],'batch':row['outer_batch'],'status':'analysis-admission-failed','admission_errors':global_errors+[repr(error)],'ratios':[{'numerator':a,'denominator':b,'gate':'analysis-admission-failed','statistics':None}for a,b in c.RATIOS]})
 output={'status':'passed-preflight-admission'if p['mode']=='preflight'and not global_errors else'analyzed-all-eight-families','mode':p['mode'],'scope':'Fresh same-quartet ratios only; no historical cohort pooling or production adoption','global_admission_errors':global_errors,'receipt_sha256':c.ref.sha(receipt_path),'raw_sha256':c.ref.sha(raw_path),'analysis_source_sha256':c.ref.sha(Path(__file__)),'rows':rows,'quiet_release':None if args.quiet_release is None else{'path':str(args.quiet_release.resolve()),'sha256':args.quiet_release_sha256}}
 (folder/'summary.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'status':output['status'],'families':len(rows),'global_admission_errors':global_errors}))
 return 0 if not global_errors else 1
if __name__=='__main__':raise SystemExit(main())
