"""Bind an intentional reverse-pass profile stop without claiming numeric success."""
from pathlib import Path
import hashlib
import json
import re


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    root=Path.cwd();here=root/'validation/public-highpoint';stem='n6-rank7-reverse-profile-128-53'
    build_path=here/'reverse-profile-build.json';run_path=here/(stem+'-run.json');result_path=here/(stem+'.json');log_path=here/(stem+'.log')
    build=json.loads(build_path.read_text());run=json.loads(run_path.read_text());result=json.loads(result_path.read_text());log=log_path.read_text()
    assert build['status']=='passed' and build['exit_codes']==[0,0] and build['changed_inputs']=={}
    assert build['frozen_core_sources_verified_after_build'] is True
    assert run['status']=='completed' and run['exit_code']==2 and run['last_public_stage']=='workspace_failed'
    assert result['status']=='workspace_failed' and result['error'].endswith('diagnostic stop after unchanged reverse pass')
    assert 'HIGHPOINT_PHASE local checks START' not in log and 'HIGHPOINT_PHASE primal amplitudes START' not in log
    assert run['numerical_reduction_executed'] is False
    assert run['environment_additions']['IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE']=='1'
    assert run['environment_additions']['RAYON_NUM_THREADS']=='1'
    assert run['build_manifest_sha256']==sha(build_path)
    assert run['result_sha256']==sha(result_path) and run['log_sha256']==sha(log_path)
    assert run['runner_source_sha256']==sha(here/'run_reverse_profile.py')
    assert run['binary_sha256']==build['binary_sha256']==sha(root/build['binary_path'])
    assert run['fixture_sha256']==sha(here/'fixture-conditioned_masses.json')
    frozen=root/build['frozen_core_source']
    for path,value in build['library_source_hashes'].items():assert sha(frozen/Path(path).relative_to('crates/iregi-rust'))==value
    for path,value in build['protected_input_hashes'].items():assert sha(root/path)==value
    baseline=json.loads((here/'build.json').read_text());matching={}
    for name in ['iregi_masters','symbolica']:
        paths=[Path(p.split('=',1)[1]) for p in build['commands'][0] if p.startswith(name+'=')];assert len(paths)==1
        path=paths[0];value=sha(path)
        assert value==build['dependency_hashes'][str(path.relative_to(root))]==baseline['explicit_extern_sha256'][name]
        matching[name]=value
    total=re.findall(r'^HIGHPOINT_REVERSE TOTAL (.+)$',log,re.M);assert len(total)==1
    totals={k:float(v) if k.endswith('_seconds') else int(v) for k,v in (field.split('=') for field in total[0].split())}
    raw=re.findall(r'^HIGHPOINT_REVERSE COUNTERS ReverseCounts \{ (.+) \}$',log,re.M);assert len(raw)==1
    counters={k:int(v) for k,v in (field.split(': ') for field in raw[0].split(', '))}
    assert counters['duplicate_insertions']<=counters['alias_occurrences']
    assert totals['max_paths']==4 and totals['max_union_bytes']==27
    record=dict(status='intentional_diagnostic_stop_no_numerics',raw_process_status=run['status'],raw_exit_code=run['exit_code'],public_status=result['status'],stop_reason=result['error'],plan_seconds=result['diagnostic_plan_seconds'],instrumented_reverse_seconds=152.994985325,substage_totals=totals,collector_counts=counters,matching_baseline_dependencies=matching,interpretation='Alias traversal and repeated insertions dominate this instrumented pass. The measured unions are small, so suffix interning is not prioritized. Added counters/set lookups increase collector cost; these are diagnostic timings, not unchanged performance or numerical qualification.',artifacts={str(p.relative_to(root)):sha(p) for p in [build_path,run_path,result_path,log_path,here/'reverse-profile-instrumentation.patch',Path(__file__)]})
    (here/'reverse-profile-qualification.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))

if __name__=='__main__':main()
