from pathlib import Path
import hashlib,json,shutil,tarfile
root=Path.cwd();evidence=root/'validation/native-stack-batch';target=root/'target/native-stack-batch'
manifest=json.loads((evidence/'manifest.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in manifest['files'].items():assert sha(evidence/name)==digest,(name,'evidence digest mismatch')
assert sha(root/'validation/benchmark/run.py')==manifest['analysis_helper_sha256'],'analysis helper changed; retain historical dependency before replay'
assert not target.exists(),'refusing to overwrite existing target/native-stack-batch'
target.mkdir(parents=True)
for p in evidence.rglob('*'):
 if p.is_file() and p.name not in ['generated-modules.tar.gz','manifest.json']:
  dst=target/p.relative_to(evidence);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
expected=json.loads((evidence/'generated-module-sha256.json').read_text())
with tarfile.open(evidence/'generated-modules.tar.gz','r:gz') as archive:
 for member in archive:
  assert member.isfile() and member.name in expected
  data=archive.extractfile(member).read();assert hashlib.sha256(data).hexdigest()==expected[member.name]
  dst=target/member.name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
print('Verified and restored evidence and generated sources; binaries and private license values are not included.')
