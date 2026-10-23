"""Synthetic quartet direction/gating checks; never runs numerical kernels."""
import copy,json,math
from pathlib import Path
import analyze as s
import admission_v3 as a
rates={'baselineTIRust':3.,'candidateTIRust':2.,'iregi':4.,'collier':1.}
n=110000000
row={'id':'synthetic','outer_batch':1,'status':'completed','before_after_qualification':'passed','iterations':n,'blocks':[{'index':i,'order':list(order),'engines':[{'engine':e,'iterations':n,'elapsed_ns':rates[e]*n,'ns_per_call':rates[e]}for e in order]}for i,order in enumerate(s.ORDERS)]}
result=s.summarize_family(row)
for r,names in zip(result['ratios'],s.RATIOS):
    expected=rates[names[0]]/rates[names[1]]
    assert r['statistics']['median']==expected and r['statistics']['ci99']==[expected,expected]
    assert r['statistics']['gate']==('improvement'if expected<1 else'regression')
    for value in [r['statistics'],*r['order_strata'].values()]:assert value['definition'].startswith(names[0]+' / '+names[1])and value['gate']in['improvement','regression']
failed=s.summarize_family(row,admitted=False)
for r in failed['ratios']:
    assert r['gate']=='correctness-or-cohort-failed'
    assert r['statistics']['gate']=='correctness-failed'
    assert all(v['gate']=='correctness-failed'for v in r['order_strata'].values())
mutations=[('missing_engine',lambda x:x['blocks'][0]['engines'].pop()),('wrong_order',lambda x:x['blocks'][0]['order'].reverse()),('duplicate_index',lambda x:x['blocks'][1].update(index=0)),('changed_iterations',lambda x:x['blocks'][0]['engines'][0].update(iterations=n+1)),('nonfinite_elapsed',lambda x:x['blocks'][0]['engines'][0].update(elapsed_ns=float('nan'))),('inconsistent_elapsed',lambda x:x['blocks'][0]['engines'][0].update(elapsed_ns=1.))]
checks=[]
for name,change in mutations:
    value=copy.deepcopy(row);change(value)
    try:s.summarize_family(value)
    except(AssertionError,KeyError,TypeError,ValueError):checks.append({'mutation':name,'rejected':True})
    else:raise AssertionError(name)
terminal={'mode':'timing','status':'completed','cleanup_errors':[],'deadline_exceeded':False,'numerical_elapsed_seconds':1.,'cleanup_finished_elapsed_seconds':2.,'elapsed_seconds':3.}
s.validate_terminal(terminal)
terminal_mutations=[('preflight_mode',lambda x:x.update(mode='preflight')),('incomplete_status',lambda x:x.update(status='inconclusive-or-failed')),('cleanup_failure',lambda x:x.update(cleanup_errors=['synthetic close failure'])),('deadline_exceeded',lambda x:x.update(deadline_exceeded=True)),('nonfinite_elapsed',lambda x:x.update(elapsed_seconds=float('nan'))),('boolean_elapsed',lambda x:x.update(elapsed_seconds=True)),('over_cap',lambda x:x.update(elapsed_seconds=701.)),('nonchronological_cleanup',lambda x:x.update(cleanup_finished_elapsed_seconds=.5)),('negative_numerical_elapsed',lambda x:x.update(numerical_elapsed_seconds=-1.))]
terminal_checks=[]
for name,change in terminal_mutations:
    value=copy.deepcopy(terminal);change(value)
    try:s.validate_terminal(value)
    except(AssertionError,KeyError,TypeError,ValueError):terminal_checks.append({'mutation':name,'rejected':True})
    else:raise AssertionError(name)
record={'status':'passed','scope':'synthetic statistics and admission tests; no kernel timing','constant_ratio_checks':5,'global_failed_admission_checks':5,'nested_failed_admission_checks':15,'mutations':checks,'terminal_mutations':terminal_checks,'source_sha256':{str(p):a.sha(p)for p in [a.V3/'statistics_controls.py',a.V3/'analyze.py',a.ROOT/'validation/benchmark/run.py']}}
(a.V3/'statistics-controls.json').write_text(json.dumps(record,indent=2)+'\n')
print('five TIRust-numerator directions, nested failure propagation six malformed quartet controls and nine terminal-failure controls passed')
