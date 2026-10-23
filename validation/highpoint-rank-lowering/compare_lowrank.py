"""Complete-array comparison of paired public low-rank runs and original IREGI."""
from pathlib import Path
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib, importlib.util, json, sys

root=Path.cwd();here=root/'validation/highpoint-rank-lowering'
shared_path=root/'validation/public-highpoint/compare_public.py'
spec=importlib.util.spec_from_file_location('shared_comparison',shared_path);shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def validate_run(path,build,variant):
    data=json.loads(path.read_text()); runpath=path.with_name(path.stem+'-run.json');run=json.loads(runpath.read_text())
    binary=next(x for x in build['runs'] if x['variant']==variant and x['label']=='public')
    assert run['status'] in ['completed','failed'] and not run['changed_inputs']
    assert run['result_sha256']==sha(path) and run['log_sha256']==sha(root/run['log_path'])
    assert run['build_manifest_sha256']==sha(here/'build.json')
    assert run['command'][3]==binary['output_path'] and sha(root/binary['output_path'])==binary['output_sha256']
    inventory=dict(build['protected_input_hashes'])
    inventory.update({x['output_path']:x['output_sha256'] for x in build['runs']})
    for item in [here/'run.py',here/'build.json',root/binary['output_path'],root/'validation/public-highpoint/fixture-conditioned_masses.json']:
        inventory[str(item.relative_to(root))]=sha(item)
    assert run['protected_input_hashes']==inventory, 'Incomplete or changed execution guard inventory'
    assert all(sha(root/n)==h for n,h in run['protected_input_hashes'].items())
    return data,runpath

def exact_chain():
    qualification_path=here/'exact-qualification.json';qualification=json.loads(qualification_path.read_text())
    assert qualification['status']=='passed' and qualification['cartesian_directions']==60 and qualification['exact_mixed_dual_constraint_slots']==576
    assert all(sha(root/n)==h for n,h in qualification['input_sha256'].items())
    build_path=here/'exact-v3-build.json';run_path=here/'exact-v3-run.json'
    build=json.loads(build_path.read_text());run=json.loads(run_path.read_text())
    assert build['status']=='passed' and run['status']=='completed' and run['exit_code']==0
    assert not build['changed_inputs'] and not run['changed_inputs']
    assert sha(root/build['binary_path'])==build['binary_sha256']==run['protected_input_hashes'][build['binary_path']]
    assert all(sha(root/n)==h for n,h in build['protected_input_hashes'].items())
    source=json.loads((here/'exact-v3-source.json').read_text());original=json.loads((here/'source-final.json').read_text())
    a=root/original['candidate_root'];b=root/source['source_root'];marker='#[cfg(test)]\nmod highpoint_rank_lowering_tests {'
    for name,h in source['source_hashes'].items():
        assert sha(b/name)==h and sha(a/name)==original['candidate_source_hashes'][name]
        if name=='crates/iregi-rust/src/pv.rs':assert (a/name).read_text().split(marker)[0]==(b/name).read_text().split(marker)[0]
        else:assert (a/name).read_bytes()==(b/name).read_bytes()
    return [qualification_path,build_path,run_path,here/'exact-v3-source.json',here/'exact-v3.log']

def read_capture(path,build,variant,fixture):
    data,runpath=validate_run(path,build,variant);run=json.loads(runpath.read_text())
    binary=next(x for x in build['runs'] if x['variant']==variant and x['label']=='public')
    assert run['status']=='completed' and run['exit_code']==0
    settings=data['settings']; n=settings['propagators'];rank=settings['rank'];rows=data['rows'];basis=shared.canonical_basis(rank)
    assert n in [6,7] and 0<=rank<=7 and 1<=rows<=3 and data['components']==1
    assert settings==dict(propagators=n,rank=rank,powers=[1]*n,dimension_shift=0,algorithm='PassarinoVeltman',convention='IregiNative',tensor_weights='Components',invariants='FromShifts',input_policy='Preserve')
    assert data['status']=='all_lanes_success' and data['lane_statuses']==['Success']*rows and data['basis']==basis
    expected=[]
    for sample in fixture['samples'][:rows]:
        ps=sample['propagators'][:n]
        expected.append([[str(Fraction(v)),'0'] for p in ps for v in p['shift']]+[[str(Fraction(v)) for v in p['mass_squared']] for p in ps]+[[str(Fraction(sample['mu'])),'0']])
    assert data['input_exact_rational']==expected and len(data['lanes'])==rows
    expected_command=['taskset','-c','14',binary['output_path'],'validation/public-highpoint/fixture-conditioned_masses.json',str(n),str(rank),'pv',str(data['working_bits']),str(data['requested_bits']),str(rows),str(path.relative_to(root))]
    assert run['command']==expected_command and data['fixture']==expected_command[4]
    for row,lane in enumerate(data['lanes']):
        assert lane['row']==row and lane['status']=='Success' and len(lane['moments'])==len(basis)
        for moment in lane['moments']:
            assert len(moment)==4
            for slot in moment:
                assert set(slot)=={'real','imaginary','real_precision','imaginary_precision'}
                assert all(shared.decimal_rational(slot[k]).is_finite() for k in ['real','imaginary'])
    return data,runpath

def main():
    baseline_path,candidate_path,output=[root/p for p in sys.argv[1:]]; assert not output.exists()
    build=json.loads((here/'build.json').read_text()); assert build['status']=='passed' and not build['changed_inputs']
    fixture_path=root/'validation/public-highpoint/fixture-conditioned_masses.json';fixture=json.loads(fixture_path.read_text())
    reference_path=root/'validation/public-highpoint/reference-conditioned_masses.json';reference=json.loads(reference_path.read_text())
    shared.validate_reference(reference,fixture,sha(fixture_path))
    original_executable=root/'target/reference/iregi-reference-original'
    assert sha(original_executable)==reference['executable_sha256']
    historical_path=root/'validation/public-highpoint/qualification.json';historical=json.loads(historical_path.read_text())
    assert historical['artifacts'][reference_path.name]==sha(reference_path)
    assert historical['artifacts'][fixture_path.name]==sha(fixture_path)
    exact_files=exact_chain()
    a,ar=read_capture(baseline_path,build,'baseline',fixture);b,br=read_capture(candidate_path,build,'candidate',fixture)
    for key in ['settings','input_exact_rational','basis','working_bits','requested_bits','rows','components']:assert a[key]==b[key],key
    failures=[];count=0;max_pair=Decimal(0);max_reference=Decimal(0);n=a['settings']['propagators']
    with localcontext() as ctx:
        ctx.prec=160
        for row,sample in enumerate(fixture['samples'][:a['rows']]):
            matches=[case for case in reference['cases'] if case['id']==f"n{n}_{sample['id']}_mode0"]
            assert len(matches)==1 and matches[0]['status']=='captured' and matches[0]['response']['stable'] is True
            original=matches[0]['response']['moments'];q=shared.scale(sample,n)
            for index,monomial in enumerate(a['basis']):
                normalization=q**(sum(monomial)+4-2*n)
                for slot in range(4):
                    left,right=[tuple(shared.decimal_rational(data['lanes'][row]['moments'][index][slot][part])/normalization for part in ['real','imaginary']) for data in [a,b]]
                    old=tuple(Decimal(str(v))/normalization for v in original[index][slot])
                    paired=shared.norm(tuple(x-y for x,y in zip(left,right)))/max(Decimal(1),shared.norm(left))
                    errors=[shared.norm(tuple(x-y for x,y in zip(value,old)))/max(Decimal(1),shared.norm(old)) for value in [left,right]]
                    max_pair=max(max_pair,paired);max_reference=max(max_reference,*errors)
                    if max(paired,*errors)>Decimal('1e-10'): failures.append(dict(row=row,moment=index,monomial=monomial,slot=slot,paired=str(paired),old_reference=list(map(str,errors))))
                    count+=1
    files=[baseline_path,candidate_path,ar,br,here/'build.json',fixture_path,reference_path,original_executable,historical_path,shared_path,Path(__file__)]+exact_files
    result=dict(status='passed' if not failures else 'failed',rank=a['settings']['rank'],propagators=n,rows=a['rows'],
                compared_complex_laurent_slots=count,tolerance='1e-10',maximum_paired_error=str(max_pair),maximum_original_error=str(max_reference),failures=failures,
                input_sha256={str(p.relative_to(root)):sha(p) for p in files},
                scope='Every requested raw Cartesian moment and native Laurent slot compared for complete successful public baseline/candidate arrays at identical represented inputs; both compared independently with untouched original stable IBP rank7 prefix. No high-rank, general-domain, precision-convergence or performance claim.')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(bool(failures))
if __name__=='__main__':main()
