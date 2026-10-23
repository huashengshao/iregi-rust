from pathlib import Path
import hashlib,json,shutil,tarfile
root=Path.cwd();source=root/'validation/native-shared-binary';target=root/'target/native-shared-binary'
assert not target.exists(),'refusing to overwrite an existing experiment'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((source/'manifest.json').read_text())
for item in manifest['files']:assert sha(source/item['path'])==item['sha256'],item['path']
records=json.loads((source/'source-archive.json').read_text());archive=source/'generated-sources.tar.gz';assert sha(archive)==records['archive_sha256']
target.mkdir(parents=True)
for p in source.iterdir():
 if p.is_file() and p.name not in ['generated-sources.tar.gz','manifest.json','source-archive.json']:shutil.copy2(p,target/p.name)
with tarfile.open(archive) as tar:
 for member in tar.getmembers():
  path=Path(member.name);assert not path.is_absolute() and '..' not in path.parts and member.isfile(),member.name
 tar.extractall(target,filter='data')
for item in records['members']:assert sha(target/item['path'])==item['sha256'],item['path']
print(f'Restored {len(records["members"])} source files; runtime archives, binaries, and license are intentionally omitted.')
