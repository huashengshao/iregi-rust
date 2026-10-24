"""Reproduce an isolated exact-source owner test without changing the root lock."""
from __future__ import annotations
import hashlib,json,shutil,subprocess,tomllib
from pathlib import Path
root=Path.cwd();source=root/'dependencies/linnest';dest=root/'target/python-render-fix/test-owner'
assert not dest.exists(),'Preserve existing attempts; choose a fresh copy instead of overwriting evidence.'
shutil.copytree(source,dest)
manifest=(dest/'Cargo.toml').read_text()
patches=(root/'Cargo.toml').read_text().split('[patch.crates-io]\n',1)[1].split('\n[profile.release]',1)[0]
patches=patches.replace('path = "dependencies/','path = "'+str(root/'dependencies')+'/')
manifest+='\n# Isolated exact-owner regression harness; production manifest above is unchanged.\n[workspace]\n\n[profile.dev]\nopt-level = 2\n\n[profile.dev.package."*"]\nopt-level = 2\n\n[patch.crates-io]\n'+patches+'\n'
(dest/'Cargo.toml').write_text(manifest)
shutil.copyfile(root/'Cargo.lock',dest/'Cargo.lock')
lock_sha=hashlib.sha256((root/'Cargo.lock').read_bytes()).hexdigest()
command=['cargo','metadata','--offline','--manifest-path',str(dest.relative_to(root)/'Cargo.toml'),'--features','svg','--format-version','1']
metadata=json.loads(subprocess.check_output(command,text=True))
key=lambda rows:{(r['name'],r['version'],r.get('source')) for r in rows}
live=tomllib.loads((root/'Cargo.lock').read_text())['package'];isolated=tomllib.loads((dest/'Cargo.lock').read_text())['package']
assert not key(isolated)-key(live),'No dependency additions/upgrades are permitted.'
assert not any(p['name'] in ('symbolica','numerica','graphica','pyo3') for p in metadata['packages'])
assert hashlib.sha256((root/'Cargo.lock').read_bytes()).hexdigest()==lock_sha
for path in source.rglob('*'):
    if path.is_file() and path.name!='Cargo.toml':assert path.read_bytes()==(dest/path.relative_to(source)).read_bytes()
print(json.dumps({'scope':'isolated exact-source owner test prepared; no test/build run','packages':len(isolated),'new_packages':0,'root_lock_unchanged':True,'source_equal_except_manifest_harness_append':True}))
