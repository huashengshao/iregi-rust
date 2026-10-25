"""Shared pure/schema helpers; importing launches no executable."""
from pathlib import Path
import copy
import itertools
import json
import math
import random
import admission as unc
import captured_admission as cap
import projection
import reference_admission as ref
import wrapper_adapters as wrap
ENGINES=list(wrap.ENGINES)
RATIOS=list(wrap.RATIOS)
LABELS=['baseline-captured','candidate-captured','baselineTIRust','candidateTIRust','iregi','collier']
TIRUST=LABELS[:4]
ORDERS=list(itertools.permutations(ENGINES))*2
random.Random(173).shuffle(ORDERS)
MINIMUM_NS=100_000_000
TARGET_NS=110_000_000
MAX_COUNT=2**31-1
PIN='2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2'

def exact(left,right):return cap.exact(left,right)
def read(path):return json.loads(Path(path).read_text())
def raw(path):return[json.loads(line)for line in Path(path).read_text().splitlines()]
def variant(label):return 'baseline'if label.startswith('baseline')else'candidate'
def captured(label):return label.endswith('-captured')
def canonical(value):
 result=copy.deepcopy(value);result['result'].pop('plan_reused');return result

def next_count(n,elapsed):
 assert type(n)is int and 0<n<=MAX_COUNT
 assert type(elapsed)in(int,float)and math.isfinite(elapsed)and elapsed>0
 result=max(n+1,math.ceil(n*TARGET_NS/elapsed))
 assert result<=MAX_COUNT,'shared signed32 iteration count overflow'
 return result

def request_payload(label,case,batch,stage,n=1,warmup=0):
 samples=case['samples'][:batch]
 if label in TIRUST:
  if stage in ['calibration','acceptance']:
   assert label in ENGINES
   return wrap.timed_payload(case,batch,label,n,warmup)
  return wrap.untimed_payload(case,batch)
 if label=='iregi':return ref.h.fortran_request(case,samples,'Hybrid',warmup,n)
 assert label=='collier'
 return ref.c.collier_request(case,samples,1,warmup,n,check=stage not in ['calibration','acceptance'])

class Context:
 def __init__(self,protocol,remaining=lambda:None):
  self.protocol=protocol;self.cases=read(protocol['inputs']);self.shapes=read(protocol['control_shapes'])
  self.coords=[(case,batch)for case in self.cases for batch in [1,32]]
  assert len(self.coords)==8 and len({(case['id'],batch)for case,batch in self.coords})==8
  self.case_by_id={case['id']:case for case in self.cases};self.normal={};self.controls={}
  cp=protocol['qualifications']['captured'];up=protocol['qualifications']['uncaptured']
  cr,ur=read(cp['receipt']),read(up['receipt']);cx,ux=raw(cp['raw']),raw(up['raw'])
  saved=projection.SavedCapture(cr,cx,self.cases,self.shapes,remaining)
  assert ur['status']=='passed-awaiting-independent-saved-data-review'
  assert ur['guard_before']is True and ur['guard_after']is True and ur['cleanup_errors']==[] and ur['deadline_exceeded']is False
  assert ur['request_count']==60 and len(ux)==120
  assert ur['captured_projection']['status']=='passed'and ur['captured_projection']['normal_responses_checked']==52
  assert all(key not in ur for key in ['error','guard_error','cancellation'])
  assert len(ur['process_terminals'])==2 and{item['label']for item in ur['process_terminals']}=={'baseline','candidate'}and all(item['returncode']==0 and item['owned_group_gone']is True and item['received_responses']==30 for item in ur['process_terminals'])
  coordinates=[(case['id'],batch)for case,batch in self.coords]
  for field in['rows','retained_rows']:
   assert[(item['id'],item['batch'])for item in ur[field]]==coordinates and all(item['status']=='passed'for item in ur[field])
  assert ur['controls']['status']==ur['invalid_request_controls']['status']=='passed'
  for serial in range(1,61):
   remaining();request,response=ux[2*serial-2:2*serial]
   assert set(request)=={'serial','stage','key','engine','payload','event'}
   assert request['event']=='request'and response['event']=='response'and request['serial']==response['serial']==serial
   assert set(response)==set(request)|{'response'}
   for field in ['serial','stage','key','engine','payload']:assert exact(request[field],response[field])
   anchor=saved.records[serial]
   assert all(exact(request[field],anchor[field])for field in ['serial','stage','key','engine','payload'])
   if request['stage']!='invalid-request':
    saved.compare(serial,request['stage'],request['key'],request['engine'],request['payload'],response['response'])
   else:
    expected=({'id':self.cases[0]['id'],'result':{'error':'timing requires own variant and one positive signed32 fixed-count block'}}if request['key'][0]=='engine'else{'status':'invalid_request','error':'untimed request must not carry timing counts'})
    assert response['response']==expected
   for capture,body in [(True,anchor['response']),(False,response['response'])]:
    label=request['engine']+('-captured'if capture else'TIRust')
    if request['stage']in['initial','own-repeat','retained']:
     self.normal[(label,request['key'][0],request['key'][1],request['stage'])]=body
    elif request['stage']=='controls':self.controls[label]=body
  assert len(saved.compared)==52
 def normal_check(self,label,response,case,batch,phase=None):
  (cap if captured(label)else unc).response(response,case,batch)
  expected=self.normal[(label,case['id'],batch,'initial'if phase is None else phase)]
  assert exact(canonical(response),canonical(expected))if phase is None else exact(response,expected)
  return response['result']
 def controls_check(self,label,response):
  (cap if captured(label)else unc).controls(response,self.shapes)
  assert exact(response,self.controls[label]),'Complete own controls changed'
 def cross_roles(self,values):
  for selected in ['baseline','candidate']:
   assert exact(projection.project(values[selected+'-captured']),projection.project(values[selected+'TIRust'])),'Captured/uncaptured current phase differs'
  assert exact(values['baseline-captured'],values['candidate-captured'])
  assert exact(values['baselineTIRust'],values['candidateTIRust'])
 def check_family(self,values,case,batch):
  samples=case['samples'][:batch]
  for label in TIRUST:self.normal_check(label,values[label],case,batch)
  self.cross_roles(values)
  ref.reference(values['iregi'],case,samples)
  ref.check_collier(values['collier'],case,samples,pole_check=True)
  for label in TIRUST:
   for oracle in ['iregi','collier']:
    assert ref.h.compare(values[label]['result'],values[oracle],case,samples)['status']=='passed'
  assert ref.h.compare(values['collier'],values['iregi'],case,samples)['status']=='passed'
 def timed(self,label,response,expected,n,case,batch):
  samples=case['samples'][:batch]
  if label in TIRUST:
   value=wrap.unwrap(response,case,batch,capture=False,timed=True,iterations=n)
   assert exact(wrap.semantic_projection(value),wrap.semantic_projection(expected[label]['result']))
   assert ref.h.compare(value,expected[label]['result'],case,samples)['status']=='passed'
   return value['elapsed_ns'][0],value['total_ns'][0]
  if label=='iregi':elapsed=ref.timed_reference(response,expected[label],n,case,samples)
  else:elapsed=ref.timed_collier(response,expected[label],n,case,samples)
  assert type(elapsed)in(int,float)and math.isfinite(elapsed)and elapsed>0
  return elapsed,response['total_ns'][0]
