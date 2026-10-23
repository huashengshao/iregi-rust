"""Qualify candidate/original agreement while retaining the failed old path."""
from pathlib import Path
from decimal import Decimal,localcontext
import hashlib,importlib.util,json
root=Path.cwd();here=root/'validation/highpoint-rank-lowering'
module_path=here/'compare_lowrank.py';spec=importlib.util.spec_from_file_location('lowrank_comparison',module_path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sha=module.sha
destination=here/'n6-rank1-qualification.json';assert not destination.exists()
build_path=here/'build.json';build=json.loads(build_path.read_text());assert build['status']=='passed' and not build['changed_inputs']
fixture_path=root/'validation/public-highpoint/fixture-conditioned_masses.json';fixture=json.loads(fixture_path.read_text())
reference_path=root/'validation/public-highpoint/reference-conditioned_masses.json';reference=json.loads(reference_path.read_text())
module.shared.validate_reference(reference,fixture,sha(fixture_path))
exe=root/'target/reference/iregi-reference-original';assert sha(exe)==reference['executable_sha256']
historical_path=root/'validation/public-highpoint/qualification.json';historical=json.loads(historical_path.read_text())
assert historical['artifacts'][reference_path.name]==sha(reference_path) and historical['artifacts'][fixture_path.name]==sha(fixture_path)
exact_files=module.exact_chain()
candidate_path=here/'n6-rank1-candidate-128.json';baseline_path=here/'n6-rank1-baseline-128.json'
candidate,candidate_run=module.read_capture(candidate_path,build,'candidate',fixture)
baseline,baseline_run=module.validate_run(baseline_path,build,'baseline')
for key in ['settings','input_exact_rational','basis','working_bits','requested_bits','rows','components']:assert baseline[key]==candidate[key],key
assert candidate['settings']['propagators']==6 and candidate['settings']['rank']==1 and candidate['rows']==1
assert candidate['working_bits']==128 and candidate['requested_bits']==53
failed=json.loads(baseline_run.read_text());assert failed['status']=='failed' and failed['exit_code']==2
assert baseline['status']=='lanes_rejected' and baseline['lane_statuses']==['Unstable("reduction has nonfinite coefficients at this kinematic point")']
assert baseline['lanes']==[dict(row=0,status=baseline['lane_statuses'][0],moments=None)]
assert failed['last_public_stage']=='lanes_rejected'
expected_old_command=['taskset','-c','14','target/public-highpoint/rank-lowering/baseline_public','validation/public-highpoint/fixture-conditioned_masses.json','6','1','pv','128','53','1',str(baseline_path.relative_to(root))]
assert failed['command']==expected_old_command and baseline['fixture']==expected_old_command[4]
matches=[case for case in reference['cases'] if case['id']=='n6_base_mode0'];assert len(matches)==1
original=matches[0];assert original['status']=='captured' and original['response']['stable'] is True
errors=[];maximum=Decimal(0);failures=[]
with localcontext() as ctx:
    ctx.prec=160;q=module.shared.scale(fixture['samples'][0],6)
    for index,monomial in enumerate(candidate['basis']):
        normalization=q**(sum(monomial)+4-12)
        for slot in range(4):
            actual=tuple(module.shared.decimal_rational(candidate['lanes'][0]['moments'][index][slot][k])/normalization for k in ['real','imaginary'])
            old=tuple(Decimal(str(v))/normalization for v in original['response']['moments'][index][slot])
            error=module.shared.norm(tuple(x-y for x,y in zip(actual,old)))/max(Decimal(1),module.shared.norm(old))
            location=dict(moment=index,monomial=monomial,slot=slot,normalized_error=str(error));errors.append(location)
            maximum=max(maximum,error)
            if error>Decimal('1e-10'):failures.append(location)
assert len(errors)==20
files=[Path(__file__),module_path,module.shared_path,build_path,fixture_path,reference_path,exe,historical_path,candidate_path,baseline_path,candidate_run,baseline_run]+exact_files
record=dict(status='passed' if not failures else 'failed',candidate_original_agreement=not failures,
            paired_baseline_candidate_agreement=False,paired_gate_status='unavailable_baseline_rejected',
            candidate_successful_lanes=1,baseline_successful_lanes=0,baseline_failure=baseline['lane_statuses'][0],
            propagators=6,rank=1,working_bits=128,requested_bits=53,compared_complex_laurent_slots=20,
            reference_tolerance='1e-10',maximum_original_error=str(maximum),slot_errors=errors,failures=failures,
            input_sha256={str(p.relative_to(root)):sha(p) for p in files},
            scope='Complete private-candidate ordinary public N6 rank1 arrays versus untouched original IREGI stable IBP rank7 prefix, with exact input/routing/native ordering and guarded source/build/reference provenance. Independently compiled old public path failed with nonfinite coefficients and returned no arrays; no paired numerical agreement, full-rank acceptance, second-precision convergence, or performance claim.')
destination.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['status','candidate_original_agreement','paired_gate_status','compared_complex_laurent_slots','maximum_original_error']},indent=2))
raise SystemExit(bool(failures))
