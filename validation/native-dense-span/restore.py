from pathlib import Path
import hashlib,json,shutil,tarfile
root=Path.cwd();out=root/'validation/native-dense-span';base=root/'target/native-dense-span';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((out/'manifest.json').read_text())
for name,digest in m['files'].items():assert sha(out/name)==digest,(name,'evidence digest mismatch')
assert sha(root/'validation/benchmark/run.py')==m['analysis_helper_sha256']
assert not base.exists(),'refusing to overwrite target/native-dense-span'
base.mkdir(parents=True)
for p in out.rglob('*'):
 if p.is_file() and p.name not in ['manifest.json','generated-sources.tar.gz']:
  dst=base/p.relative_to(out);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
expected=json.loads((out/'generated-source-sha256.json').read_text())
with tarfile.open(out/'generated-sources.tar.gz','r:gz') as archive:
 for member in archive:
  assert member.isfile() and member.name in expected
  data=archive.extractfile(member).read();assert hashlib.sha256(data).hexdigest()==expected[member.name]
  dst=base/member.name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
print('Verified/restored dense experiment evidence and exact sources; runtime archives, binaries and private license values are excluded.')
