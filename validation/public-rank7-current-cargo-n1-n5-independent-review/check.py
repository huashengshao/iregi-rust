"""Receipt/log integrity only; no native execution or process probes."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(body):return hashlib.sha256(body).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def main():
 m=json.loads((HERE/'manifest.json').read_text())
 require({str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}==set(m['files'])|{'manifest.json'},'closed review inventory')
 for name,r in m['files'].items():
  body=(HERE/name).read_bytes();require({'sha256':sha(body),'bytes':len(body)}==r,'review file '+name)
 parent=ROOT/m['parent_path'];require(sha((parent/'manifest.json').read_bytes())==m['parent_manifest_sha256'],'unchanged parent manifest')
 r=json.loads((HERE/'review.json').read_text());require(r['status']=='passed_saved_copy_source_inventory_and_portable_replay' and r['manifest_sha256']==m['parent_manifest_sha256'],'independent PASS receipt')
 require(sha((HERE/'audit.py').read_bytes())==r['audit_script_sha256'],'pre-execution audit source identity')
 for prefix,key in [('default','default_replay'),('minimal','fresh_minimal_replay')]:
  for suffix in ['stdout','stderr']:require(sha((HERE/(prefix+'.'+suffix)).read_bytes())==r[key][suffix+'_sha256'],'saved replay log')
  result=json.loads((HERE/(prefix+'.stdout')).read_text());require(result==r[key]['result'] and result['capsule_manifest_sha256']==m['parent_manifest_sha256'],'saved replay result')
 require((HERE/'default.stdout').read_bytes()==(HERE/'minimal.stdout').read_bytes(),'identical portable outputs')
 require(r['checks_passed']==1720 and r['evidence_origins_compared']==62 and r['archived_sources_compared_to_exact_snapshot']==64 and r['minimal_validation_only_files']==44,'complete independent review counts')
 require(r['new_compiler_native_integral_or_process_probe'] is False and r['capsule_or_producer_source_modified'] is False,'saved-only review scope')
 print(json.dumps({'status':'passed_saved_review_copy_integrity','parent_manifest_sha256':m['parent_manifest_sha256'],'review_sha256':sha((HERE/'review.json').read_bytes()),'new_native_or_process_execution':False},indent=2))
if __name__=='__main__':main()
