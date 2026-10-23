#!/usr/bin/env python3
"""Archive the frozen private adapter experiment without promoting its patch."""
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
SCRATCH=ROOT/'target/near-vacuum-adapter'
CACHE={}

def sha(path):
    path=path.resolve()
    if path not in CACHE:
        h=hashlib.sha256()
        with path.open('rb') as source:
            for block in iter(lambda:source.read(1024*1024),b''):h.update(block)
        CACHE[path]=h.hexdigest()
    return CACHE[path]

def copy(path):
    destination=HERE/path.relative_to(SCRATCH)
    destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(path,destination)
    assert sha(path)==sha(destination)
    return str(destination.relative_to(ROOT))

def verify(record):
    assert record['exit_code']==0 and not record['timed_out']
    assert record['sha256_before']==record['sha256_after']
    for path,digest in record['sha256_before'].items():
        assert sha(ROOT/path)==digest,path

def archive_sources():
    paths=sorted((SCRATCH/'source').rglob('*.rs'))
    paths += [SCRATCH/x for x in ['adapter_validate.rs','adapter_validate_v2.rs','run.py','run_v2.py']]
    paths += sorted((SCRATCH/'oracle').glob('*.rs'))
    output=io.BytesIO()
    with gzip.GzipFile(fileobj=output,mode='wb',mtime=0) as compressed:
        with tarfile.open(fileobj=compressed,mode='w') as archive:
            for path in paths:
                content=path.read_bytes();info=tarfile.TarInfo(str(path.relative_to(SCRATCH)))
                info.size=len(content);info.mtime=0;info.mode=0o644
                archive.addfile(info,io.BytesIO(content))
    destination=HERE/'private-sources.tar.gz';destination.write_bytes(output.getvalue())
    return {'archive':str(destination.relative_to(ROOT)),'sha256':sha(destination),
            'members':{str(p.relative_to(SCRATCH)):sha(p) for p in paths}}

def main():
    HERE.mkdir(parents=True,exist_ok=True)
    reports=[]
    for stem in ['f64','float256','v2-f64','v2-dd','v2-float128','v2-float256']:
        run=json.loads((SCRATCH/f'{stem}-run.json').read_text());verify(run)
        output=SCRATCH/f'{stem}.json';log=SCRATCH/f'{stem}.log'
        assert sha(output)==run['output_sha256'] and sha(log)==run['log_sha256']
        data=json.loads(output.read_text())
        assert data['status']=='isolated_adapter_checks_passed'
        assert data['primary_components_matching_qualified_candidate']==24
        for row in data['rows']:
            if row['error'] is not None:assert row['values'] is None
        if stem.startswith('v2-'):assert data['safe_primal_ordinary_uncertified_success']
        paths=[copy(output),copy(log),copy(SCRATCH/f'{stem}-run.json')]
        reports.append({'case':stem,'working_bits':data['working_bits'],'requested_bits':data['requested_bits'],
            'matched_primary_components':data['primary_components_matching_qualified_candidate'],
            'safe_primal_ordinary_uncertified_success':data.get('safe_primal_ordinary_uncertified_success',False),
            'seeded_overlap_ordinary_error':data['ordinary_overlap_error'],
            'diagnostic_wall_seconds':run['diagnostic_wall_seconds'],
            'artifacts':{p:sha(ROOT/p) for p in paths}})
    for name in ['run.json','comparison-run.json']:
        verify(json.loads((SCRATCH/'oracle'/name).read_text()))
    oracle_paths=[]
    for path in sorted((SCRATCH/'oracle').iterdir()):
        if path.suffix in ['.json','.log','.md','.rs']:oracle_paths.append(copy(path))
    for path in sorted(SCRATCH.glob('*build*.log')):copy(path)
    sources=archive_sources()
    patch=[]
    for name in ['lib.rs','certified.rs','near_vacuum.rs']:
        baseline=ROOT/'crates/iregi-masters/src'/name;candidate=SCRATCH/'source'/name
        old=baseline.read_text().splitlines(keepends=True) if baseline.exists() else []
        patch.extend(difflib.unified_diff(old,candidate.read_text().splitlines(keepends=True),
            fromfile=f'a/crates/iregi-masters/src/{name}' if baseline.exists() else '/dev/null',
            tofile=f'b/crates/iregi-masters/src/{name}'))
    patch_path=HERE/'proposed-adapter.patch';patch_path.write_text(''.join(patch))
    base={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'crates/iregi-masters/src').rglob('*.rs')}
    build={
      'rustc':subprocess.check_output(['rustc','--version'],text=True).strip(),
      'repository_head_at_archival':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'baseline_master_source_sha256':base,
      'adapter_features':[],
      'oneloop_archive_note':'Retained rust-codegen-enabled archive copied from liboneloop-8562c3cbbf948c0e.rlib; private adapter native-batch feature disabled.',
      'library_build_environment':{'CARGO_CRATE_NAME':'iregi_masters_certified'},
      'library_build_command':['rustc','--crate-type','lib','--crate-name','iregi_masters_certified','--edition=2024','target/near-vacuum-adapter/source/lib.rs','-L','dependency=target/d0-node-probe/deps','-L','dependency=target/cargo-build/debug/deps','-L','native=target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib','--extern','oneloop=target/near-vacuum-adapter/deps/liboneloop.rlib','--extern','symbolica=target/d0-node-probe/deps/libsymbolica-5cca42ee48491872.rlib','-o','target/near-vacuum-adapter/libiregi_masters_certified.rlib'],
      'driver_build_note':'Use the same dependency/native search paths, CARGO_CRATE_NAME=near_vacuum_adapter_validate_v2, adapter_validate_v2.rs, --extern iregi_masters_certified=target/near-vacuum-adapter/libiregi_masters_certified.rlib, the same oneloop/Symbolica archives, and --extern serde_json=target/d0-node-probe/deps/libserde_json-6ed7d47d62d32cd7.rlib. Exact source/archive/executable hashes are retained in each run manifest.'
    }
    (HERE/'build-provenance.json').write_text(json.dumps(build,indent=2)+'\n')
    comparison=json.loads((SCRATCH/'oracle/comparison.json').read_text())
    qualification={
      'status':'private_adapter_selected_families_and_exact_contour_probe_passed',
      'production_changed':False,
      'scope':'Explicit accuracy-aware private master adapter; four numeric types and six mixed components. Five primal boxes and their exact-coefficient contour contraction agree with independent parameter-series oracles at working256/requested128. No public E6, quadrature, general production or performance claim.',
      'primary_current_runs':4,'current_primary_components_matching_previously_qualified_candidate':96,
      'retained_initial_runs':2,'retained_initial_matched_components':48,
      'cases':reports,
      'source_archive':sources,
      'proposed_patch':{'path':str(patch_path.relative_to(ROOT)),'sha256':sha(patch_path)},
      'oracle_artifacts':{p:sha(ROOT/p) for p in oracle_paths},
      'build_provenance_sha256':sha(HERE/'build-provenance.json'),
      'independent_review':'No false-success or physical-guard defect in supported-family dispatch. Five D0 and contracted J5^D4 numerical, full-rectangle and independent-oracle budgets independently recomputed exactly.',
      'known_promotion_gaps':[
        'Series preparation currently starts for every valid opt-in D0 row; all rejected rows are retried at N4. Add eligibility/refinement filtering before production promotion.',
        'Unsupported series shapes currently cause whole-call preparation failure even under explicitly permitted ordinary fallback; preserve that fallback in a later revision.',
        'Contour probe uses exact input masses and exact Matrix-derived coefficients; production geometry and shifted-input rounding are not covered.',
        'Gauss node/weight intervals, quadrature truncation and full public E6/core error propagation remain unimplemented.',
        'Retained dependency archives precede the default allocator-stack change; no performance or current optimized-backend qualification is claimed.'
      ],
      'durations_are_diagnostic_only':True,
      'comparison_status':comparison.get('status')
    }
    destination=HERE/'qualification.json';destination.write_text(json.dumps(qualification,indent=2)+'\n')
    print(json.dumps({'qualification':str(destination.relative_to(ROOT)),'sha256':sha(destination),'current_matched_components':96,'independent_contour_results':6}))

if __name__=='__main__':main()
