#!/usr/bin/env python3
"""Build the frozen private v3 source using only the retained current closure."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent/'thin-lto'
CLOSURE=ROOT/'target/benchmark/dependency-closures/6b24c03-complete-kinds'
SCRATCH=ROOT/'target/near-vacuum-adapter-current-thin-lto'
BASE=ROOT/'target/near-vacuum-adapter-v3'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda:source.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def closure_hashes():
    files=sorted(p for p in CLOSURE.rglob('*') if p.is_file())
    hashes={str(p.relative_to(ROOT)):sha(p) for p in files}
    manifest=json.loads((CLOSURE/'manifest.json').read_text())
    for row in manifest['files']:
        retained=Path(row['retained']);assert retained.is_relative_to(CLOSURE)
        assert hashes[str(retained.relative_to(ROOT))]==row['sha256']
    completion=json.loads((CLOSURE/'workspace-completion.json').read_text())
    assert completion['cargo_returncode']==0
    assert completion['dependency_closure_manifest_sha256']==sha(CLOSURE/'manifest.json')
    assert completion['workspace_manifest_sha256']==sha(CLOSURE/'completed-workspace-build.json')
    return hashes

def main():
    HERE.mkdir(parents=True,exist_ok=True)
    assert not SCRATCH.exists(), 'Never overwrite a frozen current-dependency build'
    before=closure_hashes()
    (HERE/'closure-before.json').write_text(json.dumps(before,indent=2)+'\n')
    events=json.loads((CLOSURE/'cargo-library-events.json').read_text())
    selected={}
    for name in ['oneloop','symbolica','serde_json']:
        rows=[e for e in events if e['target']['name']==name and e['profile']['opt_level']=='3' and e['profile']['test'] is False]
        assert len(rows)==1,(name,len(rows))
        artifacts=[x for x in rows[0]['filenames'] if x.endswith('.rlib')]
        assert len(artifacts)==1
        retained=CLOSURE/'deps'/Path(artifacts[0]).name
        assert str(retained.relative_to(ROOT)) in before
        selected[name]={'event':rows[0],'retained_archive':str(retained.relative_to(ROOT)),'sha256':sha(retained)}
    native=['build/blake3-be485904775d6e47/out','build/gmp-mpfr-sys-575ed8ab5d02dcec/out/lib','build/gmp-mpfr-sys-e9fd89ef30e561a9/out/lib','build/psm-3e52beb8ea08afba/out','build/psm-a698b6f3f5aee778/out']
    for path in native:assert (CLOSURE/path).is_dir()
    shutil.copytree(BASE/'source',SCRATCH/'source')
    for name in ['adapter_validate.rs','contract_validate.rs']:
        shutil.copyfile(BASE/name,SCRATCH/name)
    shutil.copyfile(BASE/'contour/five_pinch_compare.rs',SCRATCH/'five_pinch_compare.rs')
    paths=sorted((SCRATCH/'source').rglob('*.rs'))+sorted(SCRATCH.glob('*.rs'))
    sources={str(p.relative_to(ROOT)):sha(p) for p in paths}
    search=['-L',f'dependency={CLOSURE}/deps']
    for path in native:search += ['-L',f'native={CLOSURE/path}']
    common=['taskset','-c','18','rustc','--edition=2024','-C','opt-level=3','-C','lto=thin','-C','embed-bitcode=yes','-C','codegen-units=1']+search
    external=[]
    for name in ['oneloop','symbolica']:external += ['--extern',f'{name}={ROOT/selected[name]["retained_archive"]}']
    library=SCRATCH/'libiregi_masters_certified_v3.rlib'
    builds=[]
    def build(name,command):
        started=time.monotonic()
        with (HERE/f'{name}-build.log').open('w') as log:
            result=subprocess.run(command,cwd=ROOT,env=os.environ|{'CARGO_CRATE_NAME':name},stdout=log,stderr=subprocess.STDOUT)
        record={'crate_name':name,'command':command,'cwd':str(ROOT),'environment':{'CARGO_CRATE_NAME':name},'exit_code':result.returncode,'diagnostic_build_seconds':time.monotonic()-started}
        builds.append(record)
        (HERE/'build-progress.json').write_text(json.dumps(builds,indent=2)+'\n')
        assert result.returncode==0,name
    build('iregi_masters_certified_v3',common+['--crate-type','lib','--crate-name','iregi_masters_certified_v3',str(SCRATCH/'source/lib.rs')]+external+['-o',str(library)])
    for source,name,alias in [('adapter_validate.rs','near_vacuum_adapter_validate_v3','iregi_masters_certified_v3'),('contract_validate.rs','near_vacuum_contract_current','iregi_masters_certified_v3'),('five_pinch_compare.rs','five_pinch_compare_current','iregi_masters_certified')]:
        build(name,common+['--crate-name',name,str(SCRATCH/source)]+external+['--extern',f'{alias}={library}','--extern',f'serde_json={ROOT/selected["serde_json"]["retained_archive"]}','-o',str(SCRATCH/name)])
    after=closure_hashes();assert after==before
    assert all(sha(ROOT/path)==digest for path,digest in sources.items())
    (HERE/'closure-after-build.json').write_text(json.dumps(after,indent=2)+'\n')
    binary_paths=[library]+[SCRATCH/p for p in ['near_vacuum_adapter_validate_v3','near_vacuum_contract_current','five_pinch_compare_current']]
    record={'status':'private_v3_current_closure_build_passed','production_changed':False,'dependency_closure':str(CLOSURE.relative_to(ROOT)),
        'closure_files_verified':len(before),'closure_before_sha256':sha(HERE/'closure-before.json'),'closure_after_build_sha256':sha(HERE/'closure-after-build.json'),
        'selection_rule':'Unique profile.opt_level==3 and profile.test==false; target.test is not the filter.',
        'selected':selected,'native_search_directories':[str((CLOSURE/p).relative_to(ROOT)) for p in native],
        'native_note':'Duplicate retained GMP and psm archive contents have identical hashes; both retained directories are included without guessing a host/target mapping.',
        'rustc':subprocess.check_output(['rustc','--version'],text=True).strip(),'builds':builds,'source_sha256':sources,
        'output_sha256':{str(p.relative_to(ROOT)):sha(p) for p in binary_paths},
        'scope':'Private v3 only, current complete-kinds closure with successful whole-workspace Cargo provenance. No shared optimized or older dependency directory is searched.'}
    destination=HERE/'build.json';destination.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'manifest':str(destination.relative_to(ROOT)),'sha256':sha(destination),'closure_files_verified':len(before)}))

if __name__=='__main__':main()
