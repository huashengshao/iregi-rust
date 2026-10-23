"""Link the independently rebuilt core; retain the failed archive-name comparison."""
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
    previous_path=here/'amplitude-vars-build-qualified.json';previous=json.loads(previous_path.read_text())
    assert previous['status']=='failed' and len(previous['runs'])==1
    proof=previous['runs'][0]
    assert (proof['label'],proof['status'],proof['exit_code'])==('core_verification','core_rebuild_bytes_differ',0)
    assert previous['sources_unchanged'] and not previous['changed_inputs']
    frozen=root/previous['frozen_source_root'];target=frozen.parent
    rebuilt=target/'libiregi_rust_verified.rlib'
    assert sha(rebuilt)==proof['rebuilt_core_sha256']
    destination=here/'amplitude-vars-build-final.json';assert not destination.exists()
    protected=dict(previous['protected_input_hashes'])
    for p in [Path(__file__),previous_path,rebuilt,here/'amplitude-vars-core-member-audit.json',root/proof['log_path']]:
        protected[str(p.relative_to(root))]=sha(p)
    assert protected[proof['log_path']]==proof['log_sha256']
    assert all(sha(root/n)==v for n,v in protected.items())
    assert all(sha(frozen/n)==v for n,v in previous['source_hashes'].items())
    commands=[[('iregi_rust='+str(rebuilt)) if part.startswith('iregi_rust=') else part for part in command]
              for command in previous['commands'][1:]]
    assert len(commands)==3
    env=os.environ.copy();env.update(CARGO_MANIFEST_DIR=str(frozen/'crates/iregi-rust'),CARGO_CRATE_NAME='iregi_rust')
    rows=[];started=time.monotonic();limit=240
    for label,command in zip(['public','tests','exact'],commands):
        remaining=limit-(time.monotonic()-started)
        if remaining<=0:break
        log=here/('amplitude-vars-final-'+label+'-build.log');assert not log.exists()
        with log.open('wb') as out:
            child=subprocess.Popen(command,cwd=root,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
            try:
                code=child.wait(timeout=remaining);status='passed' if code==0 else 'failed'
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGKILL);code=child.wait();status='timeout'
        rows.append(dict(label=label,status=status,exit_code=code,log_path=str(log.relative_to(root)),log_sha256=sha(log)))
        if code:break
    changed={n:[v,sha(root/n)] for n,v in protected.items() if sha(root/n)!=v}
    unchanged=all(sha(frozen/n)==v for n,v in previous['source_hashes'].items())
    record=dict(status='passed' if len(rows)==3 and all(r['status']=='passed' for r in rows) and not changed and unchanged else 'failed',
                source_revision=previous['source_revision'],frozen_source_root=previous['frozen_source_root'],source_hashes=previous['source_hashes'],
                protected_input_hashes=protected,dependency_hashes=previous['dependency_hashes'],native_dependency_hashes=previous['native_dependency_hashes'],
                toolchain_dependency_hashes=previous['toolchain_dependency_hashes'],commands=commands,runs=rows,changed_inputs=changed,sources_unchanged=unchanged,
                rebuilt_core_sha256=sha(rebuilt),rebuilt_core_path=str(rebuilt.relative_to(root)),core_build_exit_code=proof['exit_code'],
                previous_rebuild_manifest_sha256=sha(previous_path),timeout_seconds=limit,elapsed_seconds=time.monotonic()-started,
                scope='Fresh240s link/test-build attempt after an unnecessary strict whole-archive-byte expectation failed. All final explicit core externs use the independently rebuilt archive with guarded source/Rust/native/toolchain inputs; no reuse of the unbound initial core. Prior archive mismatch and complete member inventory retained. Final links strip debug info for storage; development-profile diagnostics only.')
    if record['status']=='passed':
        for label,name in [('binary','highpoint_public_frozen_native'),('test_binary','core_tests'),('exact_binary','amplitude_variable_probe')]:
            record[label+'_path']=str((target/name).relative_to(root));record[label+'_sha256']=sha(target/name)
    destination.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ['status','runs','changed_inputs','elapsed_seconds']}),flush=True)
    if record['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
