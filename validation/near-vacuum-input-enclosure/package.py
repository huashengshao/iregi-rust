#!/usr/bin/env python3
"""Bind successful private validation and independent audit without broad claims."""
import json
from pathlib import Path
from build_candidate import HERE,SCRATCH,BINARY,SOURCE_NAMES,sha

def main():
    assert not (HERE/'qualification.json').exists(),'Do not replace settled qualification'
    build=json.loads((HERE/'build.json').read_text());run=json.loads((HERE/'run.json').read_text())
    output=json.loads((HERE/'output.json').read_text())
    assert build['status']=='private_input_enclosure_driver_built' and run['exit_code']==0
    assert output['status']=='non_dyadic_input_enclosure_passed'
    assert run['output_sha256']==sha(HERE/'output.json')
    assert build['binary_sha256']==run['binary_sha256']==sha(BINARY)
    assert all(sha(HERE/name)==sha(SCRATCH/name)==build['source_sha256'][name] for name in SOURCE_NAMES)
    oracle_run=json.loads((HERE/'oracle/run.json').read_text())
    assert oracle_run['exit_code']==0 and oracle_run['output_sha256']==sha(HERE/'oracle/output.json')
    assert run['oracle_sha256']==oracle_run['output_sha256']
    oracle_audit_path=HERE/'oracle/oracle-audit.json'
    oracle_audit=json.loads(oracle_audit_path.read_text())
    assert oracle_audit['status']=='passed' and not oracle_audit['failures']
    # The independent oracle child writes its audit receipt. Use the exact path
    # supplied on completion rather than silently accepting an arbitrary JSON.
    audit_path=HERE/'oracle/candidate-audit.json'
    audit=json.loads(audit_path.read_text())
    assert audit['status']=='passed' and not audit['failures']
    assert any(digest==sha(HERE/'output.json') for digest in audit['input_hashes'].values())
    assert any(digest==sha(HERE/'oracle/output.json') for digest in audit['input_hashes'].values())
    provenance_path=HERE/'oracle/candidate-provenance-audit.json'
    provenance=json.loads(provenance_path.read_text())
    assert provenance['status']=='passed' and not provenance['failures']
    inventory={str(p.relative_to(HERE)):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.suffix not in {'.pyc'}}
    report={'schema_version':1,'status':'private_non_dyadic_input_enclosure_qualified','production_changed':False,
        'working_bits':256,'requested_bits':128,'numeric_type':'Symbolica Float','series_order':2,
        'accepted_primal_boxes':5,'accepted_contractions':2,'rounded_mass_argument_slots':20,
        'contour_output_rectangles_independently_checked':40,'primary_input_rows':9,'primary_active_rows':6,
        'rejection_controls':4,'exact_vacuum_degree3_interval_tail_control':True,
        'source_sha256':build['source_sha256'],'binary_sha256':build['binary_sha256'],
        'build_manifest_sha256':sha(HERE/'build.json'),'run_manifest_sha256':sha(HERE/'run.json'),
        'output_sha256':sha(HERE/'output.json'),'oracle_output_sha256':sha(HERE/'oracle/output.json'),
        'independent_audit_path':str(audit_path.relative_to(HERE)),'independent_audit_sha256':sha(audit_path),
        'independent_audit':{key:audit[key] for key in ['status','checks','failures','scope','limits']},
        'oracle_audit_sha256':sha(oracle_audit_path),'oracle_audit':{key:oracle_audit[key] for key in ['status','checks','failures']},
        'candidate_provenance_audit_sha256':sha(provenance_path),'candidate_provenance_audit':{key:provenance[key] for key in ['status','checks','failures']},'closure_files_verified':build['closure_files_verified'],
        'files_sha256':inventory,'historical_attempts':['attempt001-metadata-failure retains a missing trait-import compile failure; no runtime or link occurred.','attempt002-user-interrupted retains the user-requested SIGTERM during ThinLTO; metadata passed, no candidate runtime occurred.','attempt003-storage-failure retains shared filesystem ENOSPC; final executable absent and link exit record unavailable.'],
        'scope':'Private physical-input rectangle extension, one exact non-dyadic contour point with exact supplied unshifted Cayley geometry. Includes contour mapping, shifted masses, coefficient updates, D0 normalization/truncation, contraction and Jacobian uncertainty. Degree3 interval-tail rejection checked separately.',
        'limitations':['No production integration of input rectangles','No general or rounded geometry certificate','No Gauss nodes/weights or quadrature truncation certificate','No E6 result qualification','No accepted mixed-jet input rectangle family','No performance qualification'],
        'timing_note':'Build and runtime durations remain diagnostic observations; both oracle and candidate compiler pauses are explicitly recorded.'}
    (HERE/'qualification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'qualification':str((HERE/'qualification.json')),'sha256':sha(HERE/'qualification.json')}))
if __name__=='__main__':main()
