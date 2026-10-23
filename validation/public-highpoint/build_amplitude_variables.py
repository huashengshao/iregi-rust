"""One bounded build using a separately copied and hash-verified closure."""
from pathlib import Path
import hashlib
import json
import os
import re
import signal
import subprocess
import time


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    prepared_path = here / 'amplitude-vars-source.json'
    parent_path = here / 'collector-nway-build.json'
    prepared, parent = [json.loads(p.read_text()) for p in [prepared_path, parent_path]]
    assert prepared['status'] == 'source_prepared_only' and parent['status'] == 'passed'
    assert prepared['parent_build_manifest_sha256'] == sha(parent_path)
    frozen = root / prepared['frozen_source_root']
    target = frozen.parent
    destination = here / 'amplitude-vars-build.json'
    assert not destination.exists()
    protected = dict(prepared['protected_input_hashes'])
    protected.update({str(Path(__file__).relative_to(root)):sha(Path(__file__)), str(prepared_path.relative_to(root)):sha(prepared_path)})
    assert all(sha(root / n) == v for n,v in protected.items())
    assert all(sha(frozen / n) == v for n,v in prepared['source_hashes'].items())
    deps = target / 'frozen-deps'
    deps.mkdir()
    dependency_hashes = {}
    historical = {Path(n).name:(root/n,v) for n,v in parent['dependency_hashes'].items()}
    seeds = {Path(part.split('=',1)[1]).name for command in parent['commands'] for part in command
             if '=' in part and part.split('=',1)[0] in ['iregi_masters','symbolica','serde','thiserror','serde_json','oneloop']}
    selected = set(seeds)
    metadata = {}
    toolchain = {}
    meta_env = dict(os.environ, RUSTC_BOOTSTRAP='1')
    sysroot = Path(subprocess.check_output(['rustc','--print','target-libdir'],text=True).strip())
    # rustc's crate metadata lists transitive dependencies, including proc macros.
    for name in sorted(seeds):
        src, expected = historical[name]
        assert sha(src) == expected
        command = ['taskset','-c','15','rustc','-Zls=root',str(src)]
        output = subprocess.check_output(command,env=meta_env,text=True,timeout=30)
        metadata[name] = dict(command=command,output=output)
        for dependency in re.findall(r'^\d+ (\S+) hash ',output,re.M):
            candidates = ['lib'+dependency+suffix for suffix in ['.rlib','.so']]
            found = [c for c in candidates if c in historical]
            if found:
                selected.update(found)
            else:
                standard = [sysroot/c for c in candidates if (sysroot/c).exists()]
                assert standard, 'Unresolved dependency: '+dependency
                for p in standard:
                    toolchain[str(p)] = sha(p)
    # Copy only the metadata-derived closure; never search a live cargo directory.
    # Reflink is mandatory because the shared filesystem is near capacity.
    for name in sorted(selected):
        src, expected = historical[name]
        assert sha(src) == expected, 'Historical dependency changed: ' + name
        dst = deps / src.name
        if dst.exists():
            assert sha(dst) == expected
        else:
            subprocess.run(['cp', '--reflink=always', str(src), str(dst)], check=True, timeout=60)
            assert sha(dst) == expected
        dependency_hashes[str(dst.relative_to(root))] = expected
    old_target = (root / parent['frozen_source_root']).parent
    commands = []
    for source_command in parent['commands']:
        command = []
        for part in source_command:
            part = part.replace(str(old_target), str(target)).replace('metadata=public_highpoint_collector_nway','metadata=public_highpoint_amplitude_vars')
            if part.startswith('dependency=') and Path(part.split('=',1)[1]) != target:
                part = 'dependency=' + str(deps)
            elif '=' in part and part.split('=',1)[0] in ['iregi_masters','symbolica','serde','thiserror','serde_json','oneloop']:
                part = part.split('=',1)[0] + '=' + str(deps / Path(part.split('=',1)[1]).name)
            part = part.replace(str(here / 'nway_exact_probe.rs'), str(here / 'amplitude_variable_probe.rs'))
            part = part.replace('nway_exact_probe', 'amplitude_variable_probe')
            command.append(part)
        commands.append(command)
    env = os.environ.copy()
    env.update(CARGO_MANIFEST_DIR=str(frozen / 'crates/iregi-rust'), CARGO_CRATE_NAME='iregi_rust')
    runs = []
    started = time.monotonic()
    limit = 240
    for label, command in zip(['core','public','tests','exact'], commands):
        log = here / ('amplitude-vars-' + label + '-build.log')
        assert not log.exists()
        remaining = limit - (time.monotonic() - started)
        if remaining <= 0:
            break
        with log.open('wb') as output:
            child = subprocess.Popen(command, cwd=root, env=env, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = child.wait(timeout=remaining)
                status = 'passed' if code == 0 else 'failed'
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                code = child.wait()
                status = 'timeout'
        runs.append(dict(label=label,status=status,exit_code=code,log_path=str(log.relative_to(root)),log_sha256=sha(log)))
        if code:
            break
    changed = {n:[v,sha(root/n)] for n,v in {**protected,**dependency_hashes}.items() if sha(root/n)!=v}
    unchanged = all(sha(frozen/n)==v for n,v in prepared['source_hashes'].items())
    record = dict(status='passed' if len(runs)==4 and all(r['status']=='passed' for r in runs) and not changed and unchanged else 'failed',
                  source_revision=prepared['source_revision'], frozen_source_root=prepared['frozen_source_root'], source_hashes=prepared['source_hashes'],
                  prepared_manifest_sha256=sha(prepared_path),protected_input_hashes=protected,dependency_hashes=dependency_hashes,
                  dependency_metadata=metadata,toolchain_dependency_hashes=toolchain,
                  commands=commands,runs=runs,changed_inputs=changed,sources_unchanged=unchanged,timeout_seconds=limit,elapsed_seconds=time.monotonic()-started,
                  scope='Private amplitude-variable collector bundle; copied complete hash-verified historical Rust dependency closure, existing native GMP search path. No runtime qualification.')
    if record['status']=='passed':
        for label,filename in [('binary','highpoint_public'),('test_binary','core_tests'),('exact_binary','amplitude_variable_probe')]:
            record[label+'_path']=str((target/filename).relative_to(root));record[label+'_sha256']=sha(target/filename)
    destination.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ['status','runs','changed_inputs','elapsed_seconds']}),flush=True)
    if record['status']!='passed':
        raise SystemExit(1)


if __name__=='__main__':
    main()
