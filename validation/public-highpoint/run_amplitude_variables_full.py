"""Fixed-scope bounded public N6 probe after exact collector qualification."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import resource
import signal
import subprocess
import time
from compare_public import validate


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('name');parser.add_argument('--cpu',type=int,default=14)
    parser.add_argument('--limit',type=float,default=600)
    args=parser.parse_args()
    if not args.name.replace('-','').replace('_','').isalnum() or not 0<args.limit<=600:
        parser.error('Use a unique alphanumeric capture name and a positive bound <=600 s')
    root=Path.cwd();here=root/'validation/public-highpoint'
    build_path=here/'amplitude-vars-build-final.json';build=json.loads(build_path.read_text())
    checks_path=here/'amplitude-vars-checks.json';checks=json.loads(checks_path.read_text())
    assert build['status']==checks['status']=='passed'
    assert checks['build_manifest_sha256']==sha(build_path)
    assert [r['checked_cases'] for r in checks['runs']]==[82,38,35]
    assert [(r['label'],r['status'],r['exit_code']) for r in checks['runs']]==[
        ('exact','passed',0),('stability','passed',0),('execution','passed',0)]
    assert checks['environment']['IREGI_AMPLITUDE_VARIABLE_MODE']=='verify'
    assert checks['environment']['IREGI_PRIMAL_SUM_MODE']=='verify'
    frozen=root/build['frozen_source_root']
    protected=dict(checks['protected_input_hashes'])
    protected.update(build['toolchain_dependency_hashes'])
    for row in checks['runs']:
        protected[row['log_path']]=row['log_sha256']
        if row['label']=='exact':protected[row['result_path']]=row['result_sha256']
    protected[str((here/'amplitude-vars-tests-list.txt').relative_to(root))]=checks['test_listing_sha256']
    for p in [Path(__file__),build_path,checks_path,root/build['binary_path'],here/'fixture-conditioned_masses.json',here/'compare_public.py']:
        protected[str(p.relative_to(root))]=sha(p)
    assert protected[build['binary_path']]==build['binary_sha256']
    assert all(sha(root/n)==v for n,v in protected.items())
    assert all(sha(frozen/n)==v for n,v in build['source_hashes'].items())
    output=here/(args.name+'.json');log=here/(args.name+'.log');manifest=here/(args.name+'-run.json')
    assert not any(p.exists() for p in [output,log,manifest])
    fixture=here/'fixture-conditioned_masses.json'
    command=['taskset','-c',str(args.cpu),str(root/build['binary_path']),str(fixture.relative_to(root)),
             '6','7','pv','128','53','1',str(output.relative_to(root))]
    env=os.environ.copy()
    additions={'IREGI_PRIMAL_SUM_MODE':'nway','IREGI_AMPLITUDE_VARIABLE_MODE':'candidate',
               'IREGI_PV_PREPARATION_PROFILE':'1','IREGI_PREPARATION_PROFILE':'1','RAYON_NUM_THREADS':'1'}
    env.update(additions)
    removals=['IREGI_ALIAS_USE_VERIFY','IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE','IREGI_MASTER_AMPLITUDE_MODE']
    for name in removals:env.pop(name,None)
    record=dict(status='started',started_utc=datetime.now(timezone.utc).isoformat(),command=command,
                timeout_seconds=args.limit,build_manifest_sha256=sha(build_path),semantic_qualification_sha256=sha(checks_path),fixture_sha256=sha(fixture),
                environment_additions=additions,environment_removals=removals,protected_input_hashes=protected,
                frozen_source_hashes=build['source_hashes'],license_scope='Private licensed Symbolica; license contents excluded; one thread, pinned CPU.',
                scope='Historical matched development-profile N6 ordinary coordinate-input public plan/workspace/reduce_batch, full330 moments, Float128/request53. Only candidate amplitude-variable collector differs from previous collector+nway preparation algorithm. Debug sections stripped at final link; fine instrumentation retained. No controlled timing or numerical reference claim.')
    manifest.write_text(json.dumps(record,indent=2)+'\n')
    started=time.monotonic()
    with log.open('wb') as stream:
        child=subprocess.Popen(command,cwd=root,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            code=child.wait(timeout=args.limit);status='completed'
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGKILL);code=child.wait();status='timeout'
    record.update(status=status,exit_code=code,elapsed_seconds=time.monotonic()-started,
                  finished_utc=datetime.now(timezone.utc).isoformat(),log_sha256=sha(log),
                  peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    record['changed_inputs']={n:[v,sha(root/n)] for n,v in protected.items() if sha(root/n)!=v}
    record['frozen_sources_unchanged']=all(sha(frozen/n)==v for n,v in build['source_hashes'].items())
    record['numerical_reduction_entered']=False;record['complete_successful_array_captured']=False
    if output.exists():
        record['result_sha256']=sha(output)
        try:
            result=json.loads(output.read_text())
            record['last_public_stage']=result['status']
            record['numerical_reduction_entered']=result['status'] in ['reducing','all_lanes_success','lanes_rejected']
            if result['status']=='all_lanes_success':
                validate(result,json.loads(fixture.read_text()))
                assert status=='completed' and code==0
                assert result['settings']['propagators']==6 and result['settings']['algorithm']=='PassarinoVeltman'
                assert result['algorithm_used']=='PassarinoVeltman'
                assert (result['working_bits'],result['requested_bits'],result['rows'])==(128,53,1)
                assert result['fixture']==str(fixture.relative_to(root))
                record['complete_successful_array_captured']=True
        except (ValueError,KeyError,TypeError,AssertionError,IndexError,ArithmeticError) as error:
            record['result_validation_error']=f'{type(error).__name__}: {error}'
            record.setdefault('last_public_stage','unparseable_or_incomplete_ledger')
    else:record['last_public_stage']='no_ledger_written'
    record['numerical_reference_agreement_qualified']=False;record['controlled_performance_qualified']=False
    manifest.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if not isinstance(v,(dict,list))}),flush=True)
    assert not record['changed_inputs'] and record['frozen_sources_unchanged']


if __name__=='__main__':main()
