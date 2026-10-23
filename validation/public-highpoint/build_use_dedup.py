"""Freeze isolated alias-use deduplication and exact whole-pass verification."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time
from use_dedup_patch import prepare_source


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def once(s,a,b):
    assert s.count(a)==1,a[:100]
    return s.replace(a,b)


def main():
    root=Path.cwd();here=root/'validation/public-highpoint'
    parent_path=here/'phase-build.json';parent=json.loads(parent_path.read_text())
    protected=[Path(__file__),parent_path,root/'crates/iregi-rust/examples/highpoint_public.rs',here/'use_dedup_patch.py',here/'use_dedup_cases.rs',here/'use_dedup_exact_probe.rs']
    protected_before={str(p.relative_to(root)):sha(p) for p in protected}
    original=root/parent['frozen_core_source'];target=root/'target/public-highpoint/use-dedup2'
    assert not target.exists(),'Preserve existing frozen builds'
    for name,expected in parent['library_source_hashes'].items():
        assert sha(original/Path(name).relative_to('crates/iregi-rust'))==expected
    snapshot=target/'source/crates/iregi-rust';snapshot.parent.mkdir(parents=True)
    shutil.copytree(original,snapshot)
    p=snapshot/'src/stability.rs';s=p.read_text()
    s=prepare_source(s,s,(here/'use_dedup_cases.rs').read_text())
    p.write_text(s)
    lib=snapshot/'src/lib.rs';lib.write_text(lib.read_text()+'\npub use stability::diagnostic_alias_use_cases;\n')
    sources={str(p.relative_to(snapshot)):sha(p) for p in (snapshot/'src').rglob('*.rs')}
    diff=subprocess.run(['diff','-ru',str(original/'src'),str(snapshot/'src')],capture_output=True,text=True)
    assert diff.returncode==1
    (here/'use-dedup-instrumentation.patch').write_text(diff.stdout)
    commands=[[part.replace(str(original),str(snapshot)).replace(str(root/'target/public-highpoint/phase'),str(target)).replace('metadata=public_highpoint_phase','metadata=public_highpoint_use_dedup') for part in command] for command in parent['commands']]
    exact_command=[part.replace(str(root/'crates/iregi-rust/examples/highpoint_public.rs'),str(here/'use_dedup_exact_probe.rs')).replace('highpoint_public','use_dedup_exact_probe') for part in commands[1]]
    commands.append(exact_command)
    guards=[Path(part.split('=',1)[1]) for part in commands[0] if part.startswith(('iregi_masters=','symbolica=','serde=','thiserror='))]
    for part in commands[0]:
        if part.startswith('dependency='):
            directory=Path(part.split('=',1)[1])
            guards.extend(p for p in directory.iterdir() if p.suffix in ['.rlib','.so'])
    guards=list(dict.fromkeys(guards))
    before={str(p.relative_to(root)):sha(p) for p in guards}
    env=os.environ.copy();env.update(CARGO_MANIFEST_DIR=str(snapshot),CARGO_CRATE_NAME='iregi_rust')
    start=time.monotonic();codes=[]
    for label,command in zip(['core','probe','exact'],commands):
        with (here/f'use-dedup-{label}-build.log').open('w') as log:
            code=subprocess.call(command,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
        codes.append(code)
        if code:break
    after={str(p.relative_to(root)):sha(p) for p in guards}
    changed={key:[value,after.get(key)] for key,value in before.items() if after.get(key)!=value}
    for path,expected in protected_before.items():
        if sha(root/path)!=expected:changed[path]=[expected,sha(root/path)]
    unchanged=all(sha(snapshot/path)==expected for path,expected in sources.items())
    record=dict(status='passed' if codes==[0,0,0] and not changed and unchanged else 'failed',commands=commands,exit_codes=codes,changed_inputs=changed,frozen_core_source=str(snapshot.relative_to(root)),library_source_hashes={'crates/iregi-rust/'+path:value for path,value in sources.items()},frozen_core_sources_verified_after_build=unchanged,parent_build_manifest_sha256=sha(parent_path),instrumentation_patch_sha256=sha(here/'use-dedup-instrumentation.patch'),build_script_sha256=sha(Path(__file__)),source_sha256=parent['source_sha256'],elapsed_seconds=time.monotonic()-start,scope='Isolated Symbolica alias-use deduplication containing exact normalized-predicate and whole-reverse-pass verification hooks. Compilation alone is not a runtime proof or numerical high-point acceptance.',protected_input_hashes=protected_before,dependency_hashes=before,binary_path=str((target/'highpoint_public').relative_to(root)))
    if codes==[0,0,0]:
        record.update(binary_sha256=sha(target/'highpoint_public'),exact_binary_sha256=sha(target/'use_dedup_exact_probe'),exact_binary_path=str((target/'use_dedup_exact_probe').relative_to(root)))
    (here/'use-dedup-build.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ['status','exit_codes','elapsed_seconds','changed_inputs']}),flush=True)
    if record['status']!='passed':raise SystemExit(1)

if __name__=='__main__':main()
