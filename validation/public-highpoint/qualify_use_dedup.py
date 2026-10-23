"""Require exact-map witnesses and complete paired N6 reverse proof, without numeric claims."""
from pathlib import Path
import hashlib
import json
import re


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    root=Path.cwd();here=root/'validation/public-highpoint';stem='n6-rank7-use-dedup-verify-128-53'
    build_path=here/'use-dedup-build.json';build=json.loads(build_path.read_text())
    exact_path=here/'use-dedup-exact-run.json';exact=json.loads(exact_path.read_text())
    run_path=here/(stem+'-run.json');run=json.loads(run_path.read_text())
    result_path=here/(stem+'.json');result=json.loads(result_path.read_text())
    log_path=here/(stem+'.log');log=log_path.read_text()
    assert build['status']=='passed' and build['exit_codes']==[0,0,0] and build['changed_inputs']=={}
    assert build['frozen_core_sources_verified_after_build'] is True
    assert build['instrumentation_patch_sha256']==sha(here/'use-dedup-instrumentation.patch')
    # This is an explicit post-runtime build-manifest check, in addition to the
    # raw public runner's recorded pre-run hash.
    post_build_hash=sha(build_path)
    assert run['build_manifest_sha256']==exact['build_manifest_sha256']==post_build_hash
    assert exact['status']=='passed' and exact['exit_code']==0 and exact['checked_cases']==20
    assert exact['environment_additions']=={'IREGI_ALIAS_USE_VERIFY':'1','RAYON_NUM_THREADS':'1'}
    assert exact['environment_removals']==['IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE']
    assert exact['runner_sha256']==sha(here/'run_use_dedup_exact.py')
    assert exact['binary_sha256']==build['exact_binary_sha256']==sha(root/build['exact_binary_path'])
    assert run['status']=='diagnostic_stop_after_reverse_verification' and run['exit_code']==2
    assert run['last_public_stage']==result['status']=='workspace_failed'
    assert result['error'].endswith('diagnostic stop after alias-use reverse pass')
    assert run['environment_additions']['IREGI_ALIAS_USE_VERIFY']=='1'
    assert run['environment_additions']['IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE']=='1'
    assert run['environment_additions']['RAYON_NUM_THREADS']=='1'
    assert run['numerical_reduction_executed'] is False
    assert 'HIGHPOINT_PHASE local checks START' not in log and 'lanes' not in result
    assert run['binary_sha256']==build['binary_sha256']==sha(root/build['binary_path'])
    assert run['runner_source_sha256']==sha(here/'run_use_dedup.py')
    assert run['result_sha256']==sha(result_path) and run['log_sha256']==sha(log_path)
    assert run['fixture_sha256']==sha(here/'fixture-conditioned_masses.json')
    assert run['command']==['taskset','-c','14',str(root/build['binary_path']),'validation/public-highpoint/fixture-conditioned_masses.json','6','7','pv','128','53','1',str(result_path.relative_to(root))]
    assert exact['command']==['taskset','-c','14',str(root/build['exact_binary_path'])]
    baseline_ledger=json.loads((here/'n6-rank7-pv-current-128-53.json').read_text())
    assert result['input_exact_rational']==baseline_ledger['input_exact_rational']
    assert result['basis']==baseline_ledger['basis'] and len(result['basis'])==330
    assert result['alias_count']==31670 and result['master_count']==56
    matches=re.findall(r'^HIGHPOINT_USE_DEDUP reverse_verified=(\d+) reachable=(\d+) predicate_aliases=(\d+) legacy_collect_seconds=([0-9.e+-]+) candidate_collect_seconds=([0-9.e+-]+)$',log,re.M)
    assert len(matches)==1
    verified,reachable,predicates,old,new=matches[0]
    assert int(verified)==int(reachable)==25700 and int(verified)>0 and int(predicates)==15
    exact_results=here/'use-dedup-exact-results.json';exact_log=here/'use-dedup-exact.log'
    assert exact['result_sha256']==sha(exact_results) and exact['log_sha256']==sha(exact_log)
    rows=dict(json.loads(exact_results.read_text()));assert len(rows)==20
    assert rows['polynomial_num_ignored']==''
    for name,text in rows.items():assert exact['result_text_sha256'][name]==hashlib.sha256(text.encode()).hexdigest()
    frozen=root/build['frozen_core_source']
    for name,value in build['library_source_hashes'].items():assert sha(frozen/Path(name).relative_to('crates/iregi-rust'))==value
    for name,value in build['protected_input_hashes'].items():assert sha(root/name)==value
    for part in build['commands'][0]:
        if part.startswith('dependency='):
            directory=Path(part.split('=',1)[1])
            assert all(str(p.relative_to(root)) in build['dependency_hashes'] for p in directory.iterdir() if p.suffix in ['.rlib','.so'])
    baseline=json.loads((here/'build.json').read_text());matching={}
    for name in ['iregi_masters','symbolica','oneloop']:
        entries=[entry for entry in baseline['library_artifacts'] if Path(entry['preserved_path']).name.startswith('lib'+name+'-')]
        assert len(entries)==1
        entry=entries[0];observed=sha(root/entry['preserved_path'])
        assert observed==entry['sha256']==build['dependency_hashes'][entry['preserved_path']]
        matching[name]=observed
    record=dict(status='exact_alias_use_and_full_reverse_map_qualified',checked_cases=20,full_reverse_aliases_verified=int(verified),predicate_aliases=int(predicates),post_runtime_build_manifest_sha256=post_build_hash,diagnostic_collect_seconds={'legacy':float(old),'candidate':float(new)},matching_baseline_dependencies=matching,scope='17 exact normalized-use cases, three retained numeric/activation semantics tests, and all25700 reachable N6rank7 aliases have exact normalized predicates, root identities, predicate definitions, cache and final reachable-map agreement. No full high-point numerical array or controlled performance gate is claimed; paired development timing is diagnostic.',artifacts={str(p.relative_to(root)):sha(p) for p in [build_path,exact_path,exact_results,exact_log,run_path,result_path,log_path,here/'use-dedup-instrumentation.patch',here/'use-dedup-production.patch',here/'build.json',here/'n6-rank7-pv-current-128-53.json',here/'use_dedup_cases.rs',here/'use_dedup_patch.py',Path(__file__)]})
    (here/'use-dedup-qualification.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))

if __name__=='__main__':main()
