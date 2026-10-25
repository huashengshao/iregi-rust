"""Exact full-record admission; importing performs no build/kernel/timing."""
from fractions import Fraction
import copy,json,math,re,struct
ORDER=['finite','total_single','ir_double','uv_single','ir_single','derivative_discriminant']
ARITY={'A0':2,'B0':4,'C0':7,'dB0':4,'D0':11}
def exact(a,b):return json.dumps(a,sort_keys=True,allow_nan=False,separators=(',',':'))==json.dumps(b,sort_keys=True,allow_nan=False,separators=(',',':'))
def array(v,n):assert type(v)is list and len(v)==n;return v
def integer(v,n=None):
 assert type(v)is int and v>=0
 if n is not None:assert v==n
 return v
def number(v,allow_nonfinite=False,*,finite_field=True,domain=None):
 fields={'rational','precision','negative_sign'}|({'finite'}if finite_field else set())
 assert type(v)is dict and set(v)==fields
 bits=integer(v['precision']);assert 0<bits<2**32 and type(v['negative_sign'])is bool
 if domain in('f64','DoubleFloat'):assert bits=={'f64':53,'DoubleFloat':106}[domain]
 else:assert domain in(None,'Float')
 if 'finite'in v:
  assert type(v['finite'])is bool
  if not v['finite']:
   assert allow_nonfinite and v['rational']is None;return None
 assert type(v['rational'])is str and re.fullmatch(r'-?\d+(?:/[1-9]\d*)?',v['rational'])
 q=Fraction(v['rational']);assert q.denominator&(q.denominator-1)==0
 if q:assert(q<0)==v['negative_sign']
 return q
def complex_value(v,allow_nonfinite=False,*,finite_field=True,domain=None):
 return tuple(number(x,allow_nonfinite,finite_field=finite_field,domain=domain)for x in array(v,2))
def numeric_domain(label):
 return 'DoubleFloat'if label.startswith('DoubleFloat')else'Float'if label.startswith('Float')else'f64'
def snapshot(v,spec,domain='f64'):
 assert set(v)=={'rows','components','lanes'}
 integer(v['rows'],spec['rows']);integer(v['components'],spec['components'])
 successful=0
 for lane,error in zip(array(v['lanes'],spec['rows']),spec['errors']):
  assert set(lane)=={'error','six_outputs'}and lane['error']==error
  if error is not None:assert lane['six_outputs']is None
  else:
   for z in array(lane['six_outputs'],6*spec['components']):complex_value(z,finite_field=False,domain=domain)
   successful+=1
 return successful*6*spec['components']
def captures(v,n,rank,rows,components,domain='f64'):
 # Whole-core observation only; direct six-output master snapshots are unchanged.
 assert type(v)is list and v==[],'Capture-free core unexpectedly recorded masters'
 return 0
def execution(v,n,rank,rows):
 groups,mult={(2,0):(1,1),(2,1):(2,3),(3,0):(1,1),(3,1):(2,4)}[(n,rank)]
 expected={'input_rows':rows,'argument_rows':rows,'master_family_batches':groups,'master_rows':rows*mult,'pentagon_box_rows':0,'reduction_rows':rows,'fallback_rows':0,'fallback_successes':0,'analytic_rows':0}
 assert exact(v,expected)
def moment_lane(lane,moments,components,has_native,domain='f64'):
 required={'status','represented','fallback_used','analytic_used'}|({'moments'}if has_native else set())
 assert set(lane)==required and lane['status']=='success'and lane['fallback_used']is False and lane['analytic_used']is False
 values=array(lane['represented'],moments*4*components)
 for z in values:complex_value(z,domain=domain)
 if has_native:
  native=[z for m in array(lane['moments'],moments)for z in array(m,4)]
  for z,w in zip(values,native):
   for part,observed in zip(z,array(w,2)):
    assert type(observed)in[int,float]and math.isfinite(observed)
    q=number(part,domain='f64');x=float(q)
    assert math.isfinite(x)and Fraction.from_float(x)==q
    if not q:x=math.copysign(0.,-1. if part['negative_sign']else 1.)
    assert struct.pack('>d',x)==struct.pack('>d',observed)
 return len(values)
def observe(v,components,has_native):
 assert set(v)=={'stable','lanes','diagnostics','master_captures','execution'}and v['stable']is True
 array(v['lanes'],1);count=moment_lane(v['lanes'][0],5,components,has_native)
 assert v['diagnostics']==[[]];execution(v['execution'],2,1,1)
 masters=captures(v['master_captures'],2,1,1,components)
 return {'tensor_complex_values':count,'master_complex_values':masters}
def response(v,case,rows):
 assert set(v)=={'id','result'}and v['id']==case['id'];r=v['result']
 expected={'stable','lanes','diagnostics','master_captures','execution','id','n','rank','batch','plan_reused','degrees','requested_master_backend','scope','total_ns','elapsed_ns','iterations','capture_enabled','profiling_enabled','own_repeated_outputs_exact','input_unchanged'}
 assert set(r)==expected and r['id']==case['id']and r['stable']is True
 integer(r['n'],case['n']);integer(r['rank'],case['rank']);integer(r['batch'],rows)
 assert type(r['plan_reused'])is bool and exact(r['degrees'],[0]if case['rank']==0 else[0,1,1,1,1])
 assert r['requested_master_backend']=='SymbolicaBatch'and r['scope']=='untimed capture-free scheduler whole-reduction qualification'
 assert r['capture_enabled']is False and r['profiling_enabled']is False and r['own_repeated_outputs_exact']is True and r['input_unchanged']is True
 assert r['total_ns']==[]and r['elapsed_ns']==[];integer(r['iterations'],0)
 total=0
 for lane in array(r['lanes'],rows):total+=moment_lane(lane,len(r['degrees']),1,True)
 assert r['diagnostics']==[[]for _ in range(rows)];execution(r['execution'],case['n'],case['rank'],rows)
 masters=captures(r['master_captures'],case['n'],case['rank'],rows,1)
 return{'tensor_complex_values':total,'master_complex_values':masters}
def canonical(v):
 result=copy.deepcopy(v);result['result'].pop('plan_reused');return result
def core_control(v,spec):
 assert set(v)=={'label','components','input','result','own_repeated_outputs_exact','input_unchanged'}
 assert v['label']==spec['label']and exact(v['input'],spec['input']);integer(v['components'],spec['components']);domain=numeric_domain(spec['label'])
 assert v['own_repeated_outputs_exact']is True and v['input_unchanged']is True
 for z in v['input']:complex_value(z,domain=domain)
 r=v['result'];assert set(r)=={'values','statuses','diagnostics','fallback_used','analytic_used','execution','master_captures'}
 assert r['statuses']=='[Success]'and r['diagnostics']==[[]]and exact(r['fallback_used'],[False])and exact(r['analytic_used'],[False])
 for z in array(r['values'],spec['complex_output_count']):complex_value(z,domain=domain)
 execution(r['execution'],2,1,1)
 return{'tensor_complex_values':len(r['values']),'master_complex_values':captures(r['master_captures'],2,1,1,spec['components'],domain)}
def selected(v,spec):
 assert set(v)=={'family','status','layout_and_overflow_errors_checked','ordinary_dual_adapter_rejected','warm_clone_checked','cases'}
 assert v['family']==spec['family']and v['status']=='passed'
 for field in ['layout_and_overflow_errors_checked','ordinary_dual_adapter_rejected','warm_clone_checked']:assert v[field]is True
 total=0
 for case,expected in zip(array(v['cases'],len(spec['cases'])),spec['cases']):
  assert set(case)=={'label','family','status','baseline_backend','candidate_backend','independent_generic_instances_exact','own_repeated_outputs_exact','input_metadata','input_unchanged','baseline','candidate'}
  assert case['label']==expected['label']and case['family']==spec['family']and case['status']=='passed'
  assert case['baseline_backend']==case['candidate_backend']=='SymbolicaBatch'and case['independent_generic_instances_exact']is True
  assert case['input_unchanged']is True and case['own_repeated_outputs_exact']is True and exact(case['input_metadata'],expected['input_metadata'])
  for z in array(case['input_metadata'],expected['rows']*ARITY[spec['family']]):complex_value(z,True,domain='f64')
  total+=snapshot(case['baseline'],expected);snapshot(case['candidate'],expected)
  assert exact(case['baseline'],case['candidate'])
 return total
def unchanged(v,spec):
 assert set(v)=={'label','family','status','backend','shape','components','cases'}
 assert v['label']==spec['label']and v['family']==spec['family']and exact(v['shape'],spec['shape']);integer(v['components'],spec['components']);domain=numeric_domain(spec['label'])
 assert v['status']=='passed'and v['backend']=='SymbolicaBatch';total=0
 for case,expected in zip(array(v['cases'],len(spec['cases'])),spec['cases']):
  assert set(case)=={'label','status','represented_outputs','baseline','candidate','candidate_exactly_matches_baseline','own_repeated_outputs_exact','input_metadata','input_unchanged'}
  assert case['label']==expected['label']and case['status']=='passed'and case['input_unchanged']is True
  assert case['own_repeated_outputs_exact']is True and case['candidate_exactly_matches_baseline']is True
  assert exact(case['input_metadata'],expected['input_metadata'])
  for z in array(case['input_metadata'],expected['rows']*ARITY[spec['family']]*spec['components']):complex_value(z,True,domain=domain)
  total+=snapshot(case['represented_outputs'],expected,domain)
  for field in ['baseline','candidate']:snapshot(case[field],expected,domain);assert exact(case[field],case['represented_outputs'])
 return total
def controls(v,spec):
 assert set(v)=={'id','status','core','extended_core','masters','cache_interleaving','backend'}
 assert v['id']=='controls'and v['status']=='passed'and v['backend']=='SymbolicaBatch'
 whole=[]
 for name in ['core','extended_core']:
  for actual,expected in zip(array(v[name],len(spec[name])),spec[name]):whole.append(core_control(actual,expected))
 masters=v['masters'];assert set(masters)=={'status','scope','comparison','unchanged_comparison','failed_lane_output_policy','selected_families','unchanged_paths','extended_unchanged_paths','extended_inventory'}
 assert masters['unchanged_comparison']=='exact represented rational, component precision and sign; explicit expected errors'
 assert masters['status']=='passed'and masters['failed_lane_output_policy']=='null, never successful zero-valued evidence'
 assert masters['scope']=='untimed generic-only master adapter controls; no performance claim'
 assert masters['comparison']=='exact represented rational, precision and sign of all six successful outputs; external cross-archive comparison required'
 count=0
 for actual,expected in zip(array(masters['selected_families'],len(spec['selected_families'])),spec['selected_families']):count+=selected(actual,expected)
 for group in ['unchanged_paths','extended_unchanged_paths']:
  for actual,expected in zip(array(masters[group],len(spec[group])),spec[group]):count+=unchanged(actual,expected)
 assert exact(masters['extended_inventory'],spec['extended_inventory'])
 cache=v['cache_interleaving'];assert set(cache)=={'status','same_immutable_plan','expected_current_process_records','steps'}
 assert cache['status']=='passed'and cache['same_immutable_plan']is True
 expected_records=array(cache['expected_current_process_records'],4)
 for record,dual in zip(expected_records,spec['cache_shapes']):observe(record,2 if dual else 1,not dual)
 for step,index in zip(array(cache['steps'],len(spec['cache_indices'])),spec['cache_indices']):
  assert set(step)=={'workspace_case','backend','dual','result'};integer(step['workspace_case'],index)
  assert step['backend']=='SymbolicaBatch'and step['dual']is spec['cache_shapes'][index]
  assert exact(step['result'],expected_records[index])
 return{'core_controls':whole,'direct_master_complex_values':count,'cache_steps':len(cache['steps'])}
