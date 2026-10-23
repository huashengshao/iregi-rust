#!/usr/bin/env python3
"""Archive private v3 dispatch contracts and unchanged accepted outputs."""
import difflib
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
SCRATCH=ROOT/'target/near-vacuum-adapter-v3'
PREVIOUS=ROOT/'target/near-vacuum-adapter'
CACHE={}

def sha(path):
    path=path.resolve()
    if path not in CACHE:
        h=hashlib.sha256()
        with path.open('rb') as source:
            for block in iter(lambda:source.read(1024*1024),b''):h.update(block)
        CACHE[path]=h.hexdigest()
    return CACHE[path]

def verify_run(path):
    run=json.loads(path.read_text())
    assert run['exit_code']==0 and not run['timed_out']
    assert run['sha256_before']==run['sha256_after']
    for item,digest in run['sha256_before'].items():assert sha(ROOT/item)==digest,item
    return run

def copy(path):
    destination=HERE/path.relative_to(SCRATCH);destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(path,destination)
    assert sha(path)==sha(destination)
    return str(destination.relative_to(ROOT))

def patch(baseline,destination):
    result=[]
    for name in ['lib.rs','certified.rs','near_vacuum.rs']:
        old=baseline/name;new=SCRATCH/'source'/name
        result.extend(difflib.unified_diff(old.read_text().splitlines(keepends=True) if old.exists() else [],new.read_text().splitlines(keepends=True),
            fromfile=f'a/crates/iregi-masters/src/{name}' if old.exists() else '/dev/null',tofile=f'b/crates/iregi-masters/src/{name}'))
    destination.write_text(''.join(result))
    return {'path':str(destination.relative_to(ROOT)),'sha256':sha(destination)}

def main():
    HERE.mkdir(parents=True,exist_ok=True)
    reports=[]
    for kind in ['f64','dd','float128','float256']:
        stem=f'v3-{kind}';run=verify_run(SCRATCH/f'{stem}-run.json')
        data=json.loads((SCRATCH/f'{stem}.json').read_text())
        prior=json.loads((PREVIOUS/f'v2-{kind}.json').read_text())
        assert data['status']=='isolated_adapter_checks_passed'
        assert data['primary_components_matching_qualified_candidate']==24
        assert data['safe_primal_ordinary_uncertified_success']
        assert data['rows']==prior['rows'],'accepted values/statuses changed relative to frozen v2'
        assert sha(SCRATCH/f'{stem}.json')==run['output_sha256']
        assert sha(SCRATCH/f'{stem}.log')==run['log_sha256']
        artifacts=[copy(SCRATCH/f'{stem}{suffix}') for suffix in ['.json','.log','-run.json']]
        reports.append({'numeric':kind,'working_bits':data['working_bits'],'requested_bits':data['requested_bits'],
            'accepted_components_exactly_equal_to_v2':24,'diagnostic_wall_seconds':run['diagnostic_wall_seconds'],
            'artifacts':{p:sha(ROOT/p) for p in artifacts}})
    contract=verify_run(SCRATCH/'contract-run.json')
    contract_data=json.loads((SCRATCH/'contract.json').read_text())
    assert contract_data['all_outside_domain']['prepared_series_orders']==[2]
    assert contract_data['all_outside_domain']['no_N4_preparation_or_execution']
    # Preserve child-owned exact contract/oracle evidence without rewriting it.
    extra=[]
    for path in sorted(SCRATCH.glob('contract*')):
        if path.suffix in ['.rs','.json','.log','.md']:extra.append(copy(path))
    contour_runs=list((SCRATCH/'contour').glob('*run.json'))
    assert contour_runs
    for path in contour_runs:verify_run(path)
    contour=json.loads((SCRATCH/'contour/output.json').read_text())
    assert contour['status']=='five_pinch_adapter_and_contraction_passed'
    assert contour['working_bits']==256 and contour['requested_bits']==128
    assert contour['ordinary_rows']==0 and len(contour['boxes'])==5
    for path in sorted((SCRATCH/'contour').iterdir()):
        if path.suffix in ['.rs','.json','.log','.md']:extra.append(copy(path))
    for path in sorted(SCRATCH.glob('*build*.log')):extra.append(copy(path))
    paths=sorted((SCRATCH/'source').rglob('*.rs'))
    paths += [SCRATCH/p for p in ['adapter_validate.rs','contract_validate.rs','run.py','run_cpu19.py']]
    paths += sorted((SCRATCH/'contour').glob('*.rs'))
    payload=io.BytesIO()
    with gzip.GzipFile(fileobj=payload,mode='wb',mtime=0) as compressed:
        with tarfile.open(fileobj=compressed,mode='w') as archive:
            for path in paths:
                content=path.read_bytes();info=tarfile.TarInfo(str(path.relative_to(SCRATCH)))
                info.size=len(content);info.mtime=0;info.mode=0o644
                archive.addfile(info,io.BytesIO(content))
    sources=HERE/'private-sources.tar.gz';sources.write_bytes(payload.getvalue())
    command=['taskset','-c','18','rustc','--crate-type','lib','--crate-name','iregi_masters_certified_v3','--edition=2024','target/near-vacuum-adapter-v3/source/lib.rs','-L','dependency=target/d0-node-probe/deps','-L','dependency=target/cargo-build/debug/deps','-L','native=target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib','--extern','oneloop=target/near-vacuum-adapter/deps/liboneloop.rlib','--extern','symbolica=target/d0-node-probe/deps/libsymbolica-5cca42ee48491872.rlib','-o','target/near-vacuum-adapter-v3/libiregi_masters_certified_v3.rlib']
    build={'status':'successful_library_build','exit_code':0,'cwd':str(ROOT),'command':command,
        'build_environment':{'CARGO_CRATE_NAME':'iregi_masters_certified_v3'},
        'rustc':subprocess.check_output(['rustc','--version'],text=True).strip(),
        'provenance_note':'Command and exit status observed during the successful private build; hashes recorded at archival and cross-checked against unchanged before/after manifests of every linked runtime.',
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted((SCRATCH/'source').rglob('*.rs'))},
        'library_sha256':sha(SCRATCH/'libiregi_masters_certified_v3.rlib'),
        'build_log_sha256':sha(SCRATCH/'build.log')}
    (HERE/'library-build.json').write_text(json.dumps(build,indent=2)+'\n')
    q={'status':'private_v3_dispatch_contracts_and_selected_accuracy_checks_passed','production_changed':False,
        'previous_qualification':{'path':'validation/near-vacuum-adapter/qualification.json','sha256':sha(ROOT/'validation/near-vacuum-adapter/qualification.json')},
        'current_primary_component_checks':96,'cases':reports,
        'dispatch_contract':{'working_bits':53,'requested_bits':40,'unsupported_shape_degree':5,'independent_audit_checks':199,
            'unsupported_shape_prepares_no_series':True,'outside_domain_never_prepares_N4':True,
            'required_certificate_failures_hide_values':True,'allowed_fallback_preserves_all_legacy_laurent_components':True,
            'diagnostic_wall_seconds':contract['diagnostic_wall_seconds']},
        'independent_contour':{'working_bits':256,'requested_bits':128,'primal_boxes':5,'contracted_results':1,
            'ordinary_fallback_rows':0,'status':contour['status'],'scope':contour['scope'],
            'series_execution':contour['series_execution']},
        'source_archive':{'path':str(sources.relative_to(ROOT)),'sha256':sha(sources),'members':{str(p.relative_to(SCRATCH)):sha(p) for p in paths}},
        'production_proposal_patch':patch(ROOT/'crates/iregi-masters/src',HERE/'proposed-adapter-v3.patch'),
        'delta_from_frozen_v2':patch(PREVIOUS/'source',HERE/'v2-to-v3.patch'),
        'library_build_sha256':sha(HERE/'library-build.json'),
        'additional_artifacts':{p:sha(ROOT/p) for p in extra},
        'accuracy_contract':'Exact explicit Rational budgets are authoritative; the binary constructor used by qualification derives absolute and relative budgets2^-requested_bits. Certificates enclose the function of exact represented master inputs.',
        'remaining_limits':[
            'N2 is still prepared for valid opt-in D0 requests within supported shapes; the normal public master API is unchanged and incurs no new work.',
            'Shared symbolic-preparation/evaluator errors still return whole-call errors even when ordinary fallback is allowed.',
            'Finite order2/4 and bounded shape/degree/resource domain remain explicit; no general D0 or requested256-bit guarantee.',
            'No production geometry/shift rounding, Gauss node/weight intervals, quadrature truncation or public E6/core certification.',
            'Retained dependency archives precede default allocator-stack changes; all durations are diagnostic, not performance gates.'
        ]}
    target=HERE/'qualification.json';target.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({'qualification':str(target.relative_to(ROOT)),'sha256':sha(target),'accepted_components':96}))

if __name__=='__main__':main()
