"""Offline verification of the recorded current-planar interaction evidence."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads((root/p).read_text())
inventory=read('files.json');actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name!='files.json' and '__pycache__' not in p.parts};assert actual==set(inventory)
for path,digest in inventory.items():assert sha(root/path)==digest,path
q=read('qualification.json');assert q['status']=='passed_private_interaction' and q['production_adoption'] is False and q['performance_gate'] is False
b=read('evidence/candidate/artifacts/unit-build.json');r=read('evidence/candidate/artifacts/planar-tests.json');s=read('evidence/sources.json');review=read('evidence/source-review.json')
assert b['status']=='compiled' and type(b['returncode']) is int and b['returncode']==0 and b['verified_before'] and b['verified_after']
assert r['status']=='passed' and len(r['rows'])==10 and r['complete_closure_verified_before'] and r['complete_closure_verified_after'];assert len(r['excluded_tests'])==3
assert r['binary_sha256']==q['binary_sha256']==b['binary_sha256'];assert sha(root/'evidence/candidate/artifacts/unit-build.json')==r['build_manifest_sha256']==q['build_manifest_sha256'];assert sha(root/'evidence/sources.json')==b['source_inventory_sha256']==q['source_inventory_sha256']==review['source_inventory_sha256'];assert sha(root/'evidence/run_tests.py')==r['script_sha256']
for name,digest in s['variants']['candidate'].items():assert sha(root/'evidence/candidate'/name)==digest,name
assert q['candidate_certificate_sha256']=='9a89286f2e7f2c515ac48284c3ddbff101bec83cbab191c93bc263a0a50a5fc2'
for row in r['rows']:
 assert row['status']=='passed' and type(row['returncode']) is int and row['returncode']==0 and row['summary']==[['ok','1','0','0']]
 name=row['name'].split('::')[-1];assert sha(root/'evidence/candidate/artifacts'/(name+'.log'))==row['log_sha256']
assert 'No space left on device' in (root/'evidence/failed-enospc-compile/unit-build.log').read_text()
assert 'Real' in (root/'evidence/failed-first-compile/unit-build.log').read_text()
print(json.dumps({'status':'passed','files_verified':len(inventory),'candidate_source_files':len(s['variants']['candidate']),'interaction_tests_passed':10,'excluded_rank7_tests':3,'performance_claim':False},indent=2))
