#!/usr/bin/env python3
"""Bounded diagnostic execution; durations are not performance measurements."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import time
from build_candidate import ROOT,HERE,SCRATCH,BINARY,SOURCE_NAMES,sha,closure,write

def main():
    assert Path.cwd()==ROOT
    for name in ['run.json','run.log','output.json']:
        assert not (HERE/name).exists(),f'Never overwrite evidence: {name}'
    build=json.loads((HERE/'build.json').read_text())
    assert build['status']=='private_input_enclosure_driver_built'
    assert build['binary_sha256']==sha(BINARY)
    assert all(sha(SCRATCH/name)==sha(HERE/name)==build['source_sha256'][name] for name in SOURCE_NAMES)
    oracle=HERE/'oracle/output.json';oracle_run=HERE/'oracle/run.json'
    reference=json.loads(oracle.read_text());reference_run=json.loads(oracle_run.read_text())
    assert reference_run['exit_code']==0 and reference_run['output_sha256']==sha(oracle)
    assert reference['status']=='exact_five_pinch_oracle_generated' and reference['fixture']['x_exact_rational']=='2/5'
    before=closure();write('closure-before-run.json',before)
    assert before==json.loads((HERE/'closure-after-build.json').read_text())
    command=['taskset','-c','18','timeout','--signal=TERM','--kill-after=5s','60s',str(BINARY),str(oracle),str(HERE/'output.json')]
    env=os.environ|{'RAYON_NUM_THREADS':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();start=time.monotonic()
    with (HERE/'run.log').open('w') as log:
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    record={'command':command,'cwd':str(ROOT),'cpu':18,'runtime_limit_seconds':60,'exit_code':result.returncode,
        'started_utc':started,'diagnostic_seconds':time.monotonic()-start,'run_log_sha256':sha(HERE/'run.log'),
        'binary_sha256':sha(BINARY),'build_manifest_sha256':sha(HERE/'build.json'),'source_sha256':build['source_sha256'],
        'oracle_sha256':sha(oracle),'oracle_run_sha256':sha(oracle_run),'license':'Privately inherited; never recorded',
        'timing_scope':'Diagnostic observation only; no performance qualification'}
    if (HERE/'output.json').exists():record['output_sha256']=sha(HERE/'output.json')
    write('run.json',record)
    after=closure();write('closure-after-run.json',after);assert after==before
    assert record['binary_sha256']==build['binary_sha256']
    assert all(sha(SCRATCH/name)==sha(HERE/name)==build['source_sha256'][name] for name in SOURCE_NAMES)
    record['closure_before_run_sha256']=sha(HERE/'closure-before-run.json')
    record['closure_after_run_sha256']=sha(HERE/'closure-after-run.json')
    record['closure_files_verified']=len(before);write('run.json',record)
    assert result.returncode==0,result.returncode
    report=json.loads((HERE/'output.json').read_text())
    assert report['status']=='non_dyadic_input_enclosure_passed'
    assert report['rounded_shifted_mass_components']==20 and len(report['boxes'])==5
    assert all(row['comparison']['all_bounds_within_requested_budget'] for row in report['boxes'])
    assert report['five_box_contraction_vs_independent_J5_D4']['all_bounds_within_requested_budget']
    assert report['mapped_integrand_vs_independent_oracle']['all_bounds_within_requested_budget']
    assert all(row['values_hidden'] for row in report['rejection_controls'])
    assert report['exact_vacuum_jet_uncertainty_control']['uncertain_values_hidden']
    print(json.dumps({'status':report['status'],'output_sha256':sha(HERE/'output.json'),'run_sha256':sha(HERE/'run.json')}))
if __name__=='__main__':main()
