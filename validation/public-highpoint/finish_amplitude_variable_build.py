"""Complete only interrupted build work and freeze native link inputs.

The first orchestrator was suspended for ROOT's storage-priority window after
core/public compilation. Its original 240-second budget is never extended.
This explicit continuation preserves that failed/interrupted record, reuses
the unchanged core, and links final executables against frozen native inputs.
"""
from pathlib import Path
import hashlib
import json
import os
import signal
import subprocess
import time


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    root=Path.cwd();here=root/'validation/public-highpoint'
    previous_path=here/'amplitude-vars-build.json';previous=json.loads(previous_path.read_text())
    assert previous['status']=='failed'
    assert [(r['label'],r['status']) for r in previous['runs']]==[('core','passed'),('public','passed')]
    assert not previous['changed_inputs'] and previous['sources_unchanged']
    destination=here/'amplitude-vars-build-qualified.json';assert not destination.exists()
    frozen=root/previous['frozen_source_root'];target=frozen.parent
    assert all(sha(frozen/n)==v for n,v in previous['source_hashes'].items())
    protected=dict(previous['protected_input_hashes'])
    protected.update(previous['dependency_hashes'])
    protected.update(previous['toolchain_dependency_hashes'])
    for p in [Path(__file__),previous_path,here/'amplitude-vars-build-coordination.json',target/'libiregi_rust.rlib',target/'highpoint_public']:
        protected[str(p.relative_to(root))]=sha(p)
    assert all(sha(root/n)==v for n,v in protected.items())
    native=target/'frozen-native';native.mkdir()
    native_hashes={};native_origins={}
    native_dirs={Path(part.split('=',1)[1]) for cmd in previous['commands'] for part in cmd if part.startswith('native=')}
    for directory in native_dirs:
        for src in sorted(directory.iterdir()):
            if not src.is_file():continue
            expected=sha(src);dst=native/src.name
            assert not dst.exists()
            subprocess.run(['cp','--reflink=always',str(src),str(dst)],check=True,timeout=30)
            assert sha(src)==sha(dst)==expected
            native_hashes[str(dst.relative_to(root))]=expected
            native_origins[str(dst.relative_to(root))]=str(src.relative_to(root))
    protected.update(native_hashes)
    core_command=[('native='+str(native)) if p.startswith('native=') else p for p in previous['commands'][0]]
    core_command[core_command.index('-o')+1]=str(target/'libiregi_rust_verified.rlib')
    commands=[core_command]
    for old in previous['commands'][1:]:
        new=[('native='+str(native)) if p.startswith('native=') else p for p in old]
        # Remove debug sections at link time to avoid another large debug binary
        # on the nearly full shared filesystem. Core codegen flags are unchanged.
        new.extend(['-C','strip=debuginfo'])
        if old==previous['commands'][1]:new[new.index('-o')+1]=str(target/'highpoint_public_frozen_native')
        commands.append(new)
    env=os.environ.copy();env.update(CARGO_MANIFEST_DIR=str(frozen/'crates/iregi-rust'),CARGO_CRATE_NAME='iregi_rust')
    rows=[];started=time.monotonic();limit=240
    for label,command in zip(['core_verification','public','tests','exact'],commands):
        remaining=limit-(time.monotonic()-started)
        if remaining<=0:break
        log=here/('amplitude-vars-continuation-'+label+'-build.log');assert not log.exists()
        with log.open('wb') as out:
            child=subprocess.Popen(command,cwd=root,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
            try:
                code=child.wait(timeout=remaining);status='passed' if code==0 else 'failed'
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGKILL);code=child.wait();status='timeout'
        rows.append(dict(label=label,status=status,exit_code=code,log_path=str(log.relative_to(root)),log_sha256=sha(log)))
        if code:break
        if label=='core_verification':
            rows[-1]['retained_core_sha256']=sha(target/'libiregi_rust.rlib')
            rows[-1]['rebuilt_core_sha256']=sha(target/'libiregi_rust_verified.rlib')
            rows[-1]['byte_identical']=rows[-1]['retained_core_sha256']==rows[-1]['rebuilt_core_sha256']
            if not rows[-1]['byte_identical']:
                rows[-1]['status']='core_rebuild_bytes_differ'
                break
    changed={n:[v,sha(root/n)] for n,v in protected.items() if sha(root/n)!=v}
    unchanged=all(sha(frozen/n)==v for n,v in previous['source_hashes'].items())
    record=dict(status='passed' if len(rows)==4 and all(r['status']=='passed' for r in rows) and not changed and unchanged else 'failed',
                source_revision=previous['source_revision'],frozen_source_root=previous['frozen_source_root'],source_hashes=previous['source_hashes'],
                protected_input_hashes=protected,dependency_hashes=previous['dependency_hashes'],native_dependency_hashes=native_hashes,
                toolchain_dependency_hashes=previous['toolchain_dependency_hashes'],native_origins=native_origins,
                previous_interrupted_build_sha256=sha(previous_path),reused_core_sha256=sha(target/'libiregi_rust.rlib'),
                commands=commands,runs=rows,changed_inputs=changed,sources_unchanged=unchanged,timeout_seconds=limit,elapsed_seconds=time.monotonic()-started,
                scope='Explicit continuation after storage-priority suspension; original240s record retained. The prior builder did not hash output files; existing core frozen at continuation is therefore independently rebuilt from the guarded source and required byte-identical before reuse. All final executables use private112-object historical Rust closure and frozen native archives, with toolchain files hash guarded. Final links strip debug sections for storage; core codegen, assertions and overflow flags stay unchanged. Initial public executable retained and unused. Development-profile diagnostic, not optimized performance qualification.')
    if record['status']=='passed':
        for label,name in [('binary','highpoint_public_frozen_native'),('test_binary','core_tests'),('exact_binary','amplitude_variable_probe')]:
            record[label+'_path']=str((target/name).relative_to(root));record[label+'_sha256']=sha(target/name)
        record['public_relink_byte_identical']=sha(target/'highpoint_public_frozen_native')==sha(target/'highpoint_public')
    destination.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ['status','runs','changed_inputs','elapsed_seconds']}),flush=True)
    if record['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
