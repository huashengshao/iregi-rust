from pathlib import Path
import hashlib,json
base=Path(__file__).resolve().parent
records=json.loads((base/'files.json').read_text())
expected={item['path'] for item in records}
actual={str(p.relative_to(base)) for p in base.rglob('*') if p.is_file() and p.name!='files.json'}
assert actual==expected,(actual-expected,expected-actual)
for item in records:
 p=base/item['path']
 assert p.stat().st_size==item['bytes']
 with p.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==item['sha256'],item['path']
print(f"Verified {len(records)} retained files.")
