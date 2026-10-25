"""Check additive bindings for historical manifests omitted by original package.
No compiler, integral, producer or timing execution. --origins is optional.
"""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
CAPSULE=HERE/'scheduler-four-engine-fresh-2c1'
INVENTORY=HERE/'scheduler-four-engine-fresh-2c1-supplement.json'
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
 assert set(sys.argv[1:])<= {'--origins'}
 data=json.loads(INVENTORY.read_text()); manifest=json.loads((CAPSULE/'manifest.json').read_text())
 assert sha(CAPSULE/'manifest.json')==data['original_manifest_sha256']
 assert sha(Path(__file__))==data['checker_sha256']
 actual={str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p!=CAPSULE/'manifest.json'}
 original=set(manifest['files']); supplemental={r['path'] for r in data['files']}
 assert len(original)==235 and len(supplemental)==2 and not original&supplemental
 assert actual==original|supplemental and len(actual)==237
 for rec in data['files']:
  p=CAPSULE/rec['path']; assert not p.is_symlink() and p.stat().st_size==rec['bytes'] and sha(p)==rec['sha256']
  if '--origins' in sys.argv:
   p=Path(rec['origin']); assert not p.is_symlink() and p.stat().st_size==rec['bytes'] and sha(p)==rec['sha256']
 print(json.dumps({'status':'passed-additive-saved-manifest-bindings','original_sealed_payloads':235,'additive_nested_manifests':2,'actual_non_root_files':237,'origins_checked':'--origins' in sys.argv,'acceptance_eligibility':False}))
if __name__=='__main__':main()
