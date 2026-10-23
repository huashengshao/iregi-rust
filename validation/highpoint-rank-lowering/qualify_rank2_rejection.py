"""Preserve the bounded rank-two rejection without numerical-agreement claims."""
from pathlib import Path
import importlib.util,json,hashlib
root=Path.cwd();here=root/'validation/highpoint-rank-lowering'
module_path=here/'compare_lowrank.py';spec=importlib.util.spec_from_file_location('lowrank_comparison',module_path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sha=module.sha;build_path=here/'build.json';build=json.loads(build_path.read_text());assert build['status']=='passed'
path=here/'n6-rank2-candidate-128.json';record,runpath=module.validate_run(path,build,'candidate');run=json.loads(runpath.read_text())
assert run['status']=='failed' and run['exit_code']==2 and run['timeout_seconds']==180
assert run['elapsed_seconds']<180 and not run['changed_inputs']
expected=['taskset','-c','14','target/public-highpoint/rank-lowering/candidate_public','validation/public-highpoint/fixture-conditioned_masses.json','6','2','pv','128','53','1',str(path.relative_to(root))]
assert run['command']==expected and run['last_public_stage']=='lanes_rejected'
rank1_path=here/'n6-rank1-candidate-128.json';rank1=json.loads(rank1_path.read_text())
settings=dict(rank1['settings'],rank=2);assert record['settings']==settings
for key in ['input_exact_rational','working_bits','requested_bits','components','rows']:assert record[key]==rank1[key]
assert record['basis']==module.shared.canonical_basis(2) and len(record['basis'])==15
status='Unstable("reduction has nonfinite coefficients at this kinematic point")'
assert record['status']=='lanes_rejected' and record['lane_statuses']==[status]
assert record['lanes']==[dict(row=0,status=status,moments=None)]
assert record['execution']['reduction_rows']==1
v4path=here/'exact-v4-qualification.json';v4=json.loads(v4path.read_text());assert v4['status']=='passed'
assert v4['actual_dispatch_cases']==12 and v4['actual_dispatch_laurent_slots']==48
assert all(sha(root/n)==h for n,h in v4['input_sha256'].items())
files=[Path(__file__),module_path,build_path,path,runpath,root/run['log_path'],rank1_path,v4path]
output=here/'n6-rank2-rejection-qualification.json';assert not output.exists()
result=dict(status='captured_rejection',numerical_agreement=False,complete_numerical_arrays=False,
            propagators=6,rank=2,requested_moments=15,working_bits=128,requested_bits=53,
            timeout_seconds=180,elapsed_seconds=run['elapsed_seconds'],reached_numeric_reduction=True,
            rejection=status,exact_dispatch_witnesses_passed=True,
            input_sha256={str(p.relative_to(root)):sha(p) for p in files},
            scope='Same frozen candidate and represented base fixture as the successful rank1 capture; rank2 completed preparation and numerical reduction then rejected nonfinite coefficients. No output-array or original-reference comparison. The specific nonfinite denominator has not been instrumentally localized; tensor-pentagon geometry is a source-derived hypothesis. No longer bound or rank7 retry was used.')
output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','numerical_agreement','elapsed_seconds','reached_numeric_reduction']}))
