"""Read-only mutation controls against the exact frozen qualification parser."""
from pathlib import Path
from fractions import Fraction
import ast, copy, hashlib, importlib.util, json, math, struct

ROOT=Path.cwd();HERE=ROOT/'target/selected-native-reduction'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
raw=HERE/'qualification-001/results.json';records=json.loads(raw.read_text())
runner=HERE/'run.py';assert sha(runner)==records['input_bindings'][str(runner.relative_to(ROOT))]
helper=ROOT/'validation/benchmark/run.py';assert sha(helper)==records['helper_sha256']
spec=importlib.util.spec_from_file_location('admission_helper',helper);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
names=['finite_complex','master_compare','validate_response','canonical']
tree=ast.parse(runner.read_text());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
assert len(functions)==len(names)
namespace={'Fraction':Fraction,'math':math,'struct':struct,'json':json,'h':h}
exec(compile(ast.Module(body=functions,type_ignores=[]),str(runner),'exec'),namespace)
cases=json.loads((ROOT/'validation/native-master-replay/inputs.json').read_text())
expected=[(c['id'],b) for c in cases for b in [1,32]]
assert [(r['id'],r['outer_batch']) for r in records['rows']]==expected
for row in records['rows']:
    case=next(c for c in cases if c['id']==row['id']);samples=case['samples'][:row['outer_batch']]
    assert namespace['validate_response'](row['response'],case,samples)==row['comparison']
    assert namespace['canonical'](row['response'])==namespace['canonical'](row['repeat_response'])

row=next(r for r in records['rows'] if r['id']=='n3-r1-massive' and r['outer_batch']==32)
case=next(c for c in cases if c['id']==row['id']);samples=case['samples'][:32]
mutations={
    'missing_whole_lane':lambda r:r['candidate']['lanes'].pop(),
    'missing_tensor_moment':lambda r:r['candidate']['lanes'][0]['moments'].pop(),
    'missing_Laurent_coefficient':lambda r:r['candidate']['lanes'][0]['moments'][0].pop(),
    'nonfinite_whole_coefficient':lambda r:r['candidate']['lanes'][0]['moments'][0][0].__setitem__(0,float('nan')),
    'missing_representation':lambda r:r['candidate']['lanes'][0]['represented'].pop(),
    'changed_representation':lambda r:r['candidate']['lanes'][0]['represented'][0][0].__setitem__('rational','123456789'),
    'wrong_private_policy':lambda r:r['candidate'].__setitem__('private_selected_native',False),
    'wrong_status':lambda r:r['candidate']['lanes'][0].__setitem__('status','unstable'),
    'hidden_fallback':lambda r:r['candidate']['lanes'][0].__setitem__('fallback_used',True),
    'hidden_analytic_path':lambda r:r['candidate']['lanes'][0].__setitem__('analytic_used',True),
    'changed_diagnostics':lambda r:r['candidate'].__setitem__('diagnostics',[]),
    'changed_counts':lambda r:r['candidate']['execution'].__setitem__('master_rows',0),
    'missing_master_group':lambda r:r['candidate']['master_captures'].pop(),
    'wrong_master_family':lambda r:r['candidate']['master_captures'][0].__setitem__('family','B0'),
    'wrong_selected_backend':lambda r:r['candidate']['master_captures'][0].__setitem__('backend','SymbolicaBatch'),
    'reordered_requests':lambda r:r['candidate']['master_captures'][0]['requests'].reverse(),
    'changed_master_inputs':lambda r:r['candidate']['master_captures'][0]['input'][0][0].__setitem__('rational','123456'),
    'missing_sixth_output':lambda r:r['candidate']['master_captures'][0]['output'][0].pop(),
    'failed_master_claimed_success':lambda r:r['candidate']['master_captures'][0]['errors'].__setitem__(0,'failure'),
    'nonfinite_master_output':lambda r:r['candidate']['master_captures'][0]['output'][0][0][0].__setitem__('finite',False),
    'wrong_master_precision':lambda r:r['candidate']['master_captures'][0]['output'][0][0][0].__setitem__('precision',128),
    'boolean_precision':lambda r:r['candidate']['master_captures'][0]['output'][0][0][0].__setitem__('precision',True),
    'wrong_numeric_sign':lambda r:r['candidate']['master_captures'][0]['output'][0][0][0].__setitem__('negative_sign',not r['candidate']['master_captures'][0]['output'][0][0][0]['negative_sign']),
    'whole_batch_error':lambda r:r['candidate']['master_captures'][0].__setitem__('whole_batch_error','failure'),
}
results=[]
for name,mutate in mutations.items():
    value=copy.deepcopy(row['response']);mutate(value)
    try:namespace['validate_response'](value,case,samples)
    except (AssertionError,KeyError,ValueError,TypeError,IndexError):results.append({'control':name,'rejected':True})
    else:raise AssertionError('malformed output accepted: '+name)
receipt={'status':'passed','scope':'parser controls only; no numerical kernel rerun','runner_sha256':sha(runner),'raw_sha256':sha(raw),'valid_complete_cases':len(records['rows']),'malformed_controls':results}
(HERE/'admission-controls.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'passed','valid_cases':8,'rejected_malformed_cases':len(results)}))
