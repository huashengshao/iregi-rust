"""Restore only hash-verified immutable source snapshots; no compilation/runtime."""
from pathlib import Path
import hashlib,json,subprocess
root=Path.cwd();bundle=Path(__file__).resolve().parent;dest=root/'target/real-ball-core'
data=json.loads((bundle/'evidence/sources.json').read_text())
for variant,files in data['variants'].items():
 for name,digest in files.items():
  if name=='crates/iregi-rust/src/invariant_certificate.rs':body=(bundle/'source'/f'{variant}_invariant_certificate.rs').read_bytes()
  else:body=subprocess.check_output(['git','show',data['source_revision']+':'+name])
  assert hashlib.sha256(body).hexdigest()==digest,name
  path=dest/variant/name
  if path.exists():assert path.read_bytes()==body,('refusing to overwrite differing source',str(path))
  else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
print('restored/verified immutable source snapshots')
