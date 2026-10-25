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
 r=json.loads((HERE/'review.json').read_text());require(r['status']=='passed_saved_copy_integrity_and_replay_of_INCOMPLETE_corpus' and r['manifest_sha256']==m['parent_manifest_sha256'],'independent PASS receipt')
 require(sha((HERE/'audit.py').read_bytes())==r['audit_script_sha256'],'pre-execution audit source identity')
 for prefix,key in [('default','default_replay'),('minimal','minimal_replay')]:
  for suffix in ['stdout','stderr']:require(sha((HERE/(prefix+'.'+suffix)).read_bytes())==r[key][suffix+'_sha256'],'saved replay log')
  result=json.loads((HERE/(prefix+'.stdout')).read_text());require(result==r[key]['result'] and result['capsule_manifest_sha256']==m['parent_manifest_sha256'],'saved replay result')
 require((HERE/'default.stdout').read_bytes()==(HERE/'minimal.stdout').read_bytes(),'identical portable outputs')
 require(r['checks_passed']==1232 and r['exact_own_evidence_origin_copies']==36 and r['inherited_source_files']==64 and r['minimal_validation_only_file_count']==49 and r['full_requested_IBP_corpus_qualified'] is False and r['historical_cleanup_failure_count']==2,'complete INCOMPLETE-corpus review counts')
 require(r['new_native_compiler_integral_algebra_or_PID_probe'] is False and r['sealed_capsule_source_or_receipt_mutation'] is False,'saved-only review scope')
 print(json.dumps({'status':'passed_saved_review_copy_of_INCOMPLETE_corpus','parent_manifest_sha256':m['parent_manifest_sha256'],'review_sha256':sha((HERE/'review.json').read_bytes()),'full_requested_IBP_corpus_qualified':False,'new_native_or_process_execution':False},indent=2))
if __name__=='__main__':main()
