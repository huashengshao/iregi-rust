"""AST and pure mock transport/admission checks; no kernel or clock measurement."""
from pathlib import Path
import ast
from collections import Counter
import copy
import hashlib
import json
import sys
import tempfile
sys.dont_write_bytecode=True
import common as c
import analyze
ROOT=Path('/shared/external/iregi/iregi-rust')
HERE=Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 assert Path.cwd()==ROOT
 parsed=[]
 for path in HERE.glob('*.py'):ast.parse(path.read_text(),filename=str(path));parsed.append(path.name)
 origins=c.read(HERE/'source-origins.json')
 for name,item in origins.items():assert sha(ROOT/item['path'])==item['sha256']and sha(HERE/name)==item['new_sha256']
 assert len(c.ORDERS)==48 and len(Counter(c.ORDERS))==24 and set(Counter(c.ORDERS).values())=={2}
 assert all(numerator in ['baselineTIRust','candidateTIRust']for numerator,_ in c.RATIOS)and len(c.RATIOS)==5
 cases=c.read(ROOT/'validation/native-master-replay/inputs.json');payloads=0
 for case in cases:
  for batch in[1,32]:
   for engine in c.TIRUST:
    payload=json.loads(c.request_payload(engine,case,batch,'before'))
    assert set(payload)=={'id','n','rank','algorithm','samples'};assert len(payload['samples'])==batch;payloads+=1
   for engine in c.ENGINES[:2]:
    payload=json.loads(c.request_payload(engine,case,batch,'acceptance',17,0))
    assert payload['iterations']==17 and payload['repeats']==1 and payload['warmup']==0 and payload['engine']==c.variant(engine);payloads+=1
 assert c.next_count(1,10_000_000)==11
 try:c.next_count(c.MAX_COUNT,1)
 except AssertionError:pass
 else:raise AssertionError('signed32 overflow admitted')
 # Resource-gate fixtures are in-memory only and confer no real authorization.
 protocol={'mode':'timing','pinned_source_revision':c.PIN,'run_id':'pure-mock-one',
  'attempt_directory':'/pure-mock-context/attempt-one','cpu':34,'source_manifest_sha256':'0'*64,
  'aggregate_budget_seconds':900,'cleanup_postguard_reserve_seconds':30,'quiet_grant':{'grant_id':'pure-mock-not-a-grant'}}
 grant={'mode':'timing','pinned_source_revision':c.PIN,'run_id':protocol['run_id'],
  'attempt_directory':protocol['attempt_directory'],'one_shot':True,'root_authority':'pure mock only; no resource authorization',
  'grant_id':'pure-mock-not-a-grant','status':'granted','cpu':34,'allowed_process_labels':c.LABELS,
  'source_manifest_sha256':'0'*64,'aggregate_budget_seconds':900,'cleanup_postguard_reserve_seconds':30,
  'cpu_exclusive':True,'no_other_project_compilers_or_numerics':True,'smt_siblings':[290]}
 assert c.validate_quiet_grant(protocol,grant)is True
 lease_negative=[]
 for field,value in[('attempt_directory','/pure-mock-context/attempt-two'),('run_id','pure-mock-two'),('one_shot',False),('root_authority','  '),('grant_id','different'),('cpu',35),('source_manifest_sha256','1'*64),('no_other_project_compilers_or_numerics',False)]:
  changed=copy.deepcopy(grant);changed[field]=value
  try:c.validate_quiet_grant(protocol,changed)
  except AssertionError:lease_negative.append(field)
  else:raise AssertionError('Bad lease admitted: '+field)
 log_negative=[]
 with tempfile.TemporaryDirectory(prefix='pure-log-custody-',dir=HERE)as temporary:
  folder=Path(temporary);receipt={'stdout_sha256':{},'stderr_sha256':{}}
  for label in c.LABELS:
   for stream in['stdout','stderr']:
    path=folder/(label+'.'+stream+'.log');path.write_text('pure fixture only '+label+' '+stream+'\n');receipt[stream+'_sha256'][label]=sha(path)
  assert analyze.verify_saved_logs(folder,receipt)is True
  for stream in['stdout','stderr']:
   for extra in[False,True]:
    changed=copy.deepcopy(receipt)
    if extra:changed[stream+'_sha256']['extra-label']='0'*64
    else:changed[stream+'_sha256'].pop(c.LABELS[0])
    try:analyze.verify_saved_logs(folder,changed)
    except AssertionError:log_negative.append(stream+('-extra'if extra else'-missing'))
    else:raise AssertionError('Wrong log inventory admitted')
  path=folder/(c.LABELS[0]+'.stdout.log');path.write_text('changed pure fixture bytes')
  try:analyze.verify_saved_logs(folder,receipt)
  except AssertionError:log_negative.append('changed-saved-bytes')
  else:raise AssertionError('Changed saved log admitted')
 original=c.ref.h.ratio_summary
 def mock_ratio(numerator,denominator,correctness):
  assert len(numerator)==len(denominator)and len(numerator)in[24,48]
  return{'median':0.9,'ci99':[0.89,0.91],'relative_ci_width':0.02,'gate':'improvement'if correctness['status']=='passed'else'correctness-failed','mock_only':True}
 c.ref.h.ratio_summary=mock_ratio
 try:
  row={'id':'pure-mock-no-measured-data','outer_batch':1,'status':'completed','iterations':1,'blocks':[]}
  for index,order in enumerate(c.ORDERS):
   row['blocks'].append({'index':index,'order':list(order),'engines':[{'engine':engine,'iterations':1,'elapsed_ns':100_000_001,'ns_per_call':100_000_001}for engine in order]})
  result=analyze.summarize(row,True);assert all(item['gate']=='improvement'for item in result['ratios'])
  changed=copy.deepcopy(row);changed['blocks'][0]['engines'][0]['elapsed_ns']=99_999_999;changed['blocks'][0]['engines'][0]['ns_per_call']=99_999_999;changed['status']='short-block-inconclusive'
  short=analyze.summarize(changed,True);assert short['short_blocks']==1 and all(item['gate']=='inconclusive-short-block'for item in short['ratios'])
  failed=analyze.summarize(row,False);assert all(item['gate']=='correctness-or-cohort-failed'for item in failed['ratios'])
  incomplete=copy.deepcopy(row);incomplete['blocks']=[]
  assert all(item['gate']=='inconclusive-incomplete-family'for item in analyze.summarize(incomplete,False)['ratios'])
 finally:c.ref.h.ratio_summary=original
 assert sha(HERE/'lifecycle.py')=='c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824'
 transport=(HERE/'interactive.py').read_text();assert "command=[taskset,'-c',str(cpu),str(binary)]"in transport and"command=[taskset,'-c','32',str(binary)]"not in transport
 template=c.read(HERE/'protocol-template.json')
 assert template['processes']is None and template['qualifications']is None and template['quiet_grant']is None
 assert template['request_policy']['orders']==[list(order)for order in c.ORDERS]
 for mode,cap,reserve in[('preflight',180,20),('timing',900,30)]:assert template['fixed_stage_bounds'][mode]=={'aggregate_budget_seconds':cap,'cleanup_postguard_reserve_seconds':reserve}
 output={'status':'passed-source-asts-and-pure-mock-tests-only','source_asts':parsed,'serialized_fresh_request_payloads':payloads,'balanced_permutations':24,'quartets':48,'ratios_all_TIRust_numerator':5,'mock_gate_paths_checked':['complete','row-local-short','global-failure','incomplete'],'one_shot_lease_negative_cases':lease_negative,'saved_log_negative_cases':log_negative,'bootstrap_executed':False,'actual_timing_or_numeric_data_generated':False,'compiler_probe_preparer_runner_launched':False,'source_sha256':{path.name:sha(path)for path in[HERE/'test_sources.py',HERE/'run.py',HERE/'analyze.py',HERE/'common.py',HERE/'prepare.py']}}
 (HERE/'pure-source-tests.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
if __name__=='__main__':main()
