"""Bind the corrected exact witnesses to the independently built public code."""
from pathlib import Path
import hashlib,json,re
root=Path.cwd();here=root/'validation/highpoint-rank-lowering'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=[here/n for n in ['build.json','source-final.json','exact-v3-source.json','exact-v3-build.json','exact-v3-run.json','exact-v3.log','exact-initial-run.json','exact-initial.log','exact-v2-build.json','exact-v2-build.log']]
records={p.name:json.loads(p.read_text()) for p in paths if p.suffix=='.json'}
build=records['build.json'];exactbuild=records['exact-v3-build.json'];run=records['exact-v3-run.json']
assert build['status']==exactbuild['status']=='passed' and not build['changed_inputs'] and not exactbuild['changed_inputs']
assert run['status']=='completed' and run['exit_code']==0 and not run['changed_inputs']
assert run['command']==['taskset','-c','14',exactbuild['binary_path'],'highpoint_rank_lowering_tests','--nocapture','--test-threads=1']
assert sha(root/exactbuild['binary_path'])==exactbuild['binary_sha256']
assert run['protected_input_hashes'][exactbuild['binary_path']]==exactbuild['binary_sha256']
assert run['log_sha256']==sha(here/'exact-v3.log')
bindings={}
for record in [build,exactbuild,run]:
    for name,value in record['protected_input_hashes'].items():
        assert bindings.get(name,value)==value
        bindings[name]=value
assert all(sha(root/n)==h for n,h in bindings.items())
original=records['source-final.json'];corrected=records['exact-v3-source.json']
a=root/original['candidate_root'];b=root/corrected['source_root'];marker='#[cfg(test)]\nmod highpoint_rank_lowering_tests {'
production_equal=[]
for name,value in original['candidate_source_hashes'].items():
    assert sha(a/name)==value and sha(b/name)==corrected['source_hashes'][name]
    if name=='crates/iregi-rust/src/pv.rs':
        left=(a/name).read_text().split(marker)[0];right=(b/name).read_text().split(marker)[0]
        assert left==right and len(left)>10000
    else: assert (a/name).read_bytes()==(b/name).read_bytes()
    production_equal.append(name)
log=(here/'exact-v3.log').read_text()
assert '4 passed; 0 failed;' in log
assert 'exact Cartesian integrand fixtures=15, directions=60' in log
assert 'exact lazy chart identities: 4 offsets × 4 directions × 6 equations × 6 mixed Taylor components' in log
expected=['cartesian_integrand_identity_all_directions_and_routes','direct_supplied_distances_keep_policy_disabled','lazy_seven_point_charts_preserve_exact_mixed_dual_identities','structural_deficiency_retains_old_constant_identity']
assert sorted(re.findall(r'test pv::highpoint_rank_lowering_tests::(\w+) \.\.\.',log))==sorted(expected)
assert records['exact-initial-run.json']['exit_code']==101 and '2 passed; 1 failed' in (here/'exact-initial.log').read_text()
assert records['exact-v2-build.json']['status']=='failed' and 'trait bounds were not satisfied' in (here/'exact-v2-build.log').read_text()
output=here/'exact-qualification.json';assert not output.exists()
record=dict(status='passed',tests=expected,regular_integrand_fixtures=15,cartesian_directions=60,
            exact_mixed_dual_constraint_slots=4*4*6*6,guarded_inputs=len(bindings),production_equivalent_files=production_equal,
            input_sha256={str(p.relative_to(root)):sha(p) for p in paths+[Path(__file__)]},
            retained_failures=['Initial exact test mislabeled the retained N6 m0²+1 singular fixture as regular; preserved 2PASS/1FAIL. Corrected witnesses retain this input as explicit no-solution control and separately add m0²+1/2 regular deformation.',
                               'Test-only v2 used unavailable Real evaluation for Complex<Rational>; preserved compile failure. V3 uses existing Symbolica map_to_ring(Q) and evaluate_in_ring, with exact rational equality.'],
            scope='Exact integrand and lazy chart/second-order mixed-Taylor identities; no integrated full-rank numerical or performance qualification. Test-only corrections leave the paired public recurrence implementation byte-identical outside the added cfg(test) module.')
output.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k] for k in ['status','regular_integrand_fixtures','exact_mixed_dual_constraint_slots','guarded_inputs']}))
