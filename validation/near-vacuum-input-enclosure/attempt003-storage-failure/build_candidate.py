#!/usr/bin/env python3
"""Build one private input-enclosure driver against the retained release closure."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
SCRATCH=ROOT/'target/near-vacuum-input-enclosure'
CLOSURE=ROOT/'target/benchmark/dependency-closures/6b24c03-complete-kinds'
BINARY=SCRATCH/'input_enclosure_compare'
SOURCE_NAMES=['input_enclosure_compare.rs','source/near_vacuum.rs']
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def write(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
def closure():
    hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted(CLOSURE.rglob('*')) if p.is_file()}
    manifest=json.loads((CLOSURE/'manifest.json').read_text())
    for row in manifest['files']:
        path=Path(row['retained']);assert path.is_relative_to(CLOSURE)
        assert hashes[str(path.relative_to(ROOT))]==row['sha256']
    completion=json.loads((CLOSURE/'workspace-completion.json').read_text())
    assert completion['cargo_returncode']==0
    assert completion['dependency_closure_manifest_sha256']==sha(CLOSURE/'manifest.json')
    assert completion['workspace_manifest_sha256']==sha(CLOSURE/'completed-workspace-build.json')
    return hashes
def main():
    assert Path.cwd()==ROOT
    assert not BINARY.exists()
    assert not (HERE/'build.json').exists()
    sources={name:sha(SCRATCH/name) for name in SOURCE_NAMES}
    assert all(sha(HERE/name)==digest for name,digest in sources.items())
    write('build-source.json',sources)
    before=closure();write('closure-before-build.json',before)
    events=json.loads((CLOSURE/'cargo-library-events.json').read_text())
    selected={}
    for name in ['symbolica','oneloop','serde_json']:
        rows=[e for e in events if e['target']['name']==name and e['profile']['opt_level']=='3' and e['profile']['test'] is False]
        assert len(rows)==1
        rlibs=[p for p in rows[0]['filenames'] if p.endswith('.rlib')];assert len(rlibs)==1
        path=CLOSURE/'deps'/Path(rlibs[0]).name
        assert str(path.relative_to(ROOT)) in before
        selected[name]={'archive':str(path.relative_to(ROOT)),'sha256':sha(path),'cargo_event':rows[0]}
    native=['build/blake3-be485904775d6e47/out','build/gmp-mpfr-sys-575ed8ab5d02dcec/out/lib','build/gmp-mpfr-sys-e9fd89ef30e561a9/out/lib','build/psm-3e52beb8ea08afba/out','build/psm-a698b6f3f5aee778/out']
    common=['taskset','-c','18','rustc','--edition=2024','--crate-name','input_enclosure_compare',str(SCRATCH/'input_enclosure_compare.rs'),'-L',f'dependency={CLOSURE}/deps']
    for path in native:common+=['-L',f'native={CLOSURE/path}']
    for name,row in selected.items():common+=['--extern',f'{name}={ROOT/row["archive"]}']
    env=os.environ|{'CARGO_CRATE_NAME':'input_enclosure_compare','RAYON_NUM_THREADS':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
    commands=[('metadata',common+['--emit=metadata','-o',str(SCRATCH/'input-enclosure.rmeta')]),
        ('link',common+['-C','opt-level=3','-C','lto=thin','-C','embed-bitcode=yes','-C','codegen-units=1','-o',str(BINARY)])]
    builds=[]
    for name,command in commands:
        start=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
        with (HERE/f'build-{name}.log').open('w') as log:
            result=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        record={'stage':name,'command':command,'exit_code':result.returncode,'started_utc':started,
            'diagnostic_seconds':time.monotonic()-start,'log_sha256':sha(HERE/f'build-{name}.log')}
        builds.append(record);write('build-progress.json',builds)
        assert result.returncode==0,(name,result.returncode)
    after=closure();write('closure-after-build.json',after);assert after==before
    assert all(sha(SCRATCH/name)==sha(HERE/name)==digest for name,digest in sources.items())
    write('build.json',{'status':'private_input_enclosure_driver_built','production_changed':False,
        'source_sha256':sources,'builds':builds,'binary_sha256':sha(BINARY),'selected':selected,
        'closure_files_verified':len(before),'closure_before_sha256':sha(HERE/'closure-before-build.json'),
        'closure_after_sha256':sha(HERE/'closure-after-build.json'),'dependency_closure':str(CLOSURE.relative_to(ROOT)),
        'native_search_directories':native,'rustc':subprocess.check_output(['rustc','--version'],text=True).strip(),
        'scope':'One private driver/module; all dependencies retained from the completed6b24 release closure. No production master integration or benchmark.'})
    print(json.dumps({'manifest':str((HERE/'build.json').relative_to(ROOT)),'sha256':sha(HERE/'build.json')}),flush=True)
if __name__=='__main__':main()
