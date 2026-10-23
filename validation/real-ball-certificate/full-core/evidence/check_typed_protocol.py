"""Validate failure-closed typed joins against retained numerical preflight rows."""
import ast,copy,json
from pathlib import Path
import verify_artifacts as p
import witness_inputs as inputs
out=Path(__file__).resolve().parent
runner=out/'run_pair.py';tree=ast.parse(runner.read_text());function=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='validate_typed');namespace={'inputs':inputs};exec(compile(ast.Module(body=[function],type_ignores=[]),str(runner),'exec'),namespace);validate=namespace['validate_typed']
source=out/'typed-preflight/preflight.json';records={row['case']:row['record'] for row in json.loads(source.read_text())['rows']}
rows=[]
for case,record in records.items():
 validate(record,case);rows.append({'case':'valid/'+case,'passed':True})
case='lightlike_mixed_static_dd'
mutations={
 'wrong_case':lambda x:x.update(case='lightlike_mixed_static_f64'),
 'wrong_bits':lambda x:x.update(working_bits=53),
 'wrong_carrier':lambda x:x.update(carrier='dynamic_hyperdual'),
 'swapped_taylor_axes':lambda x:x.update(dual_shape=[[0,0],[1,0],[0,1],[1,1]]),
 'wrong_algorithm':lambda x:x['settings'].update(algorithm='Ibp'),
 'wrong_policy':lambda x:x['settings'].update(input_policy={'LegacyOnShell':{'threshold':'1e-6'}}),
 'missing_input_argument':lambda x:x['inputs'][0].pop(),
 'missing_input_component':lambda x:x['inputs'][0][0].pop(),
 'rounded_input_metadata':lambda x:x['inputs'][0][0][0][0].update(precision_bits=53),
 'missing_output_lane':lambda x:x['lanes'].pop(),
 'missing_laurent_slot':lambda x:x['lanes'][0]['moments'][0].pop(),
 'missing_taylor_slot':lambda x:x['lanes'][0]['moments'][0][0].pop(),
 'failed_lane_outputs':lambda x:x['lanes'][2].update(moments=[]),
 'nonfinite_output':lambda x:x['lanes'][0]['moments'][0][0][0][0].update(decimal='NaN'),
 'invalid_lane_mislabeled':lambda x:x['lanes'][2].update(status={'kind':'success'}),
 'wrong_counter_width':lambda x:x['execution'].update(input_rows=4),
}
for label,mutate in mutations.items():
 record=copy.deepcopy(records[case]);mutate(record)
 try:validate(record,case)
 except (ValueError,KeyError,TypeError,IndexError) as error:rows.append({'case':'reject/'+label,'passed':True,'rejection':str(error)})
 else:rows.append({'case':'reject/'+label,'passed':False})
result={'schema':1,'scope':'plain Python protocol checks only; uses retained candidate preflight records without rerunning Symbolica','runner_sha256':p.sha(runner),'helper_sha256':p.sha(out/'witness_inputs.py'),'input_preflight_sha256':p.sha(source),'rows':rows,'passed':all(row['passed'] for row in rows)};(out/'typed-protocol-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(len(rows),'checks',result['passed']);raise SystemExit(0 if result['passed'] else 1)
