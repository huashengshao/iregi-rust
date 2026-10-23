"""Bind exact witness and immutable n-way build; makes no numerical acceptance claim."""
from pathlib import Path
import hashlib
import json


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    root=Path.cwd(); here=root/'validation/public-highpoint'
    build_path=here/'nway-build.json'; run_path=here/'nway-exact-run.json'
    build=json.loads(build_path.read_text()); run=json.loads(run_path.read_text())
    assert build['status']=='passed' and build['exit_codes']==[0,0,0]
    assert build['changed_inputs']=={} and build['frozen_core_sources_verified_after_build'] is True
    assert run['status']=='passed' and run['exit_code']==0 and run['exact_equal_cases']==20
    assert run['build_manifest_sha256']==sha(build_path)
    assert run['environment_additions']=={'IREGI_PRIMAL_SUM_MODE':'nway','RAYON_NUM_THREADS':'1'}
    assert run['binary_sha256']==build['exact_binary_sha256']==sha(root/build['exact_binary_path'])
    assert run['command']==['taskset','-c','14',str(root/build['exact_binary_path'])]
    assert run['runner_sha256']==sha(here/'run_nway_exact.py')
    for name,expected in build['protected_input_hashes'].items():assert sha(root/name)==expected
    frozen=root/build['frozen_core_source']
    for name,expected in build['library_source_hashes'].items():
        assert sha(frozen/Path(name).relative_to('crates/iregi-rust'))==expected
    baseline=json.loads((here/'build.json').read_text())
    matching={}
    for name in ['iregi_masters','symbolica']:
        paths=[part.split('=',1)[1] for part in build['commands'][0] if part.startswith(name+'=')]
        assert len(paths)==1
        path=Path(paths[0]); observed=sha(path)
        assert build['dependency_hashes'][str(path.relative_to(root))]==observed==baseline['explicit_extern_sha256'][name]
        matching[name]=observed
    source=(frozen/'src/stability.rs').read_text()
    a=source.index('fn master_amplitude_legacy(\n');b=source.index('\nfn collect_amplitude_variables(',a)
    legacy=source[a:b].strip().replace('master_amplitude_legacy(', 'master_amplitude(')
    parent=json.loads((here/'phase-build.json').read_text())
    parent_source=(root/parent['frozen_core_source']/'src/stability.rs').read_text()
    a=parent_source.index('fn master_amplitude(\n');b=parent_source.index('\nfn collect_amplitude_variables(',a)
    assert legacy==parent_source[a:b].strip()
    results=here/'nway-exact-results.json'; log=here/'nway-exact.log'
    assert run['result_sha256']==sha(results) and run['log_sha256']==sha(log)
    expressions=dict(json.loads(results.read_text()));assert len(expressions)==20
    assert expressions['polynomial_empty']=='0'
    for name,expression in expressions.items():
        assert expression.startswith('ERROR: ')==name.endswith('_error')
        assert run['canonical_expression_sha256'][name]==hashlib.sha256(expression.encode()).hexdigest()
    record=dict(status='exact-expression-qualified-only',case_count=20,legacy_function_matches_parent=True,matching_baseline_dependencies=matching,scope='The complete canonical amplitude expressions and rejection errors agree on 20 asserted cases. This does not establish high-point numerical coverage, full-plan equality, a production change, or a performance gate.',artifacts={str(p.relative_to(root)):sha(p) for p in [build_path,run_path,results,log,here/'nway_exact_cases.rs',here/'nway_exact_probe.rs',here/'nway-instrumentation.patch',Path(__file__)]})
    (here/'nway-qualification.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
