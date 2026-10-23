"""Bind the private collector proofs to a bounded public capture, including failures."""
from pathlib import Path
import argparse
import hashlib
import json
from compare_public import validate


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('name');args=parser.parse_args()
    assert args.name.replace('-','').replace('_','').isalnum()
    root=Path.cwd();here=root/'validation/public-highpoint'
    paths={name:here/file for name,file in {
        'build':'amplitude-vars-build-final.json','checks':'amplitude-vars-checks.json',
        'source':'amplitude-vars-source.json','run':args.name+'-run.json','log':args.name+'.log',
        'fixture':'fixture-conditioned_masses.json','driver':'run_amplitude_variables_full.py',
        'validator':'compare_public.py','qualifier':Path(__file__).name,
        'independent_audit':'amplitude-vars-independent-audit.json',
    }.items()}
    build,checks,source,run=[json.loads(paths[k].read_text()) for k in ['build','checks','source','run']]
    assert build['status']==checks['status']=='passed'
    assert source['status']=='source_prepared_only'
    assert build['source_hashes']==source['source_hashes']==run['frozen_source_hashes']
    assert checks['build_manifest_sha256']==run['build_manifest_sha256']==sha(paths['build'])
    audit=json.loads(paths['independent_audit'].read_text())
    assert audit['status']=='independent_artifact_audit_passed'
    assert audit['build_manifest_sha256']==sha(paths['build']) and audit['semantic_checks_sha256']==sha(paths['checks'])
    assert run['semantic_qualification_sha256']==sha(paths['checks'])
    assert [r['checked_cases'] for r in checks['runs']]==[82,38,35]
    assert [(r['status'],r['exit_code']) for r in checks['runs']]==[('passed',0)]*3
    assert build['core_build_exit_code']==0 and sha(root/build['rebuilt_core_path'])==build['rebuilt_core_sha256']
    assert run['status'] in ['completed','timeout'] and 0<run['timeout_seconds']<=600
    assert not run['changed_inputs'] and run['frozen_sources_unchanged']
    assert run['environment_additions']['IREGI_AMPLITUDE_VARIABLE_MODE']=='candidate'
    assert run['environment_additions']['IREGI_PRIMAL_SUM_MODE']=='nway'
    assert checks['environment']['IREGI_AMPLITUDE_VARIABLE_MODE']=='verify'
    assert checks['environment']['IREGI_PRIMAL_SUM_MODE']=='verify'
    assert run['fixture_sha256']==sha(paths['fixture']) and run['log_sha256']==sha(paths['log'])
    assert run['protected_input_hashes'][build['binary_path']]==build['binary_sha256']
    frozen=root/build['frozen_source_root']
    assert all(sha(frozen/n)==v for n,v in source['source_hashes'].items())
    assert all(sha(root/n)==v for n,v in run['protected_input_hashes'].items())
    command=run['command']
    assert command[:2]==['taskset','-c'] and command[3]==str(root/build['binary_path'])
    assert command[4:]==[str(paths['fixture'].relative_to(root)),'6','7','pv','128','53','1',
                         str((here/(args.name+'.json')).relative_to(root))]
    result_path=here/(args.name+'.json')
    if result_path.exists():
        assert run['result_sha256']==sha(result_path);paths['result']=result_path
    if run['complete_successful_array_captured']:
        assert run['status']=='completed' and run['exit_code']==0 and not run.get('result_validation_error')
        result=json.loads(result_path.read_text());validate(result,json.loads(paths['fixture'].read_text()))
        assert result['fixture']==str(paths['fixture'].relative_to(root))
        assert result['settings']['propagators']==6 and result['settings']['algorithm']=='PassarinoVeltman'
        assert result['algorithm_used']=='PassarinoVeltman'
        assert (result['working_bits'],result['requested_bits'],result['rows'])==(128,53,1)
    ledger=[line for line in paths['log'].read_text(errors='replace').splitlines() if line.startswith('HIGHPOINT_PHASE')]
    record=dict(status='bounded_capture_qualified',outcome=run['status'],exit_code=run['exit_code'],
                timeout_seconds=run['timeout_seconds'],elapsed_seconds=run['elapsed_seconds'],
                last_public_stage=run['last_public_stage'],phase_ledger=ledger,
                exact_variable_sets=48,exact_full_amplitude_or_error_cases=34,stability_tests=38,execution_tests=35,
                numerical_reduction_entered=run['numerical_reduction_entered'],
                complete_successful_array_captured=run['complete_successful_array_captured'],
                complete_complex_slots=1320 if run['complete_successful_array_captured'] else 0,
                numerical_reference_agreement_qualified=False,controlled_performance_qualified=False,
                result_validation_error=run.get('result_validation_error'),
                artifact_hashes={str(p.relative_to(root)):sha(p) for p in paths.values()},
                scope='Frozen historical matched ordinary public N6 rank7 PV Float128/request53. Existing Symbolica IF-free amplitude-variable traversal is independently exact-qualified against retained recursive legacy semantics. Full successful arrays require separate independent-reference and higher-precision qualification. Instrumented development profile with final-link debug stripping; no controlled performance claim.')
    output=here/(args.name+'-qualification.json');assert not output.exists()
    output.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if not isinstance(v,(dict,list))}),flush=True)


if __name__=='__main__':main()
