"""Offline integrity and semantic qualification checks; no numerical engine."""
from pathlib import Path
import hashlib,json,math
root=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=json.loads((root/'files.json').read_text())
actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name!='files.json' and '__pycache__' not in p.parts}
assert actual==set(files),(actual-set(files),set(files)-actual)
for path,digest in files.items():assert sha(root/path)==digest,path
read=lambda p:json.loads((root/p).read_text())
q=read('qualification.json');assert q['status']=='completed_private_qualification' and q['production_adoption'] is False
unit=read('evidence/candidate/artifacts/unit-run.json');assert unit['status']=='passed' and unit['complete_closure_verified_before'] and unit['complete_closure_verified_after']
assert sum(g['test_result']['passed'] for g in unit['groups'].values())==88
assert sum(g['test_result']['ignored'] for g in unit['groups'].values())==2
for name,count in [('kernel',8),('typed',15),('physical',2)]:
 d=read(f'evidence/{name}-paired/qualification.json');assert d['status']=='passed' and d['verified_before'] and d['verified_after'] and len(d['rows'])==count
 for row in d['rows']:
  assert row['status']=='passed' and row['comparison']['passed']
  for run in row['runs'].values():assert type(run['returncode']) is int and run['returncode']==0
s=read('evidence/sources.json');a=s['variants']['baseline'];b=s['variants']['candidate'];assert a.keys()==b.keys();assert [p for p in a if a[p]!=b[p]]==['crates/iregi-rust/src/invariant_certificate.rs']
for variant in ['baseline','candidate']:assert sha(root/'source'/f'{variant}_invariant_certificate.rs')==s['variants'][variant]['crates/iregi-rust/src/invariant_certificate.rs']
t=read('evidence/kernel-quiet-001/qualification.json');assert t['status']=='completed' and t['verified_before'] and t['verified_after'] and t['performance_provenance_qualified'];assert all(type(c) is int and c==0 for c in t['producer_exit_codes'].values());assert t['cpu_affinity']==[254]
assert [r['ratio']['gate'] for r in t['rows']]==['inconclusive-noise','inconclusive-noise','parity','improvement']
for row in t['rows']:
 assert len(row['blocks'])==21 and len(row['warmup'])==5
 for block in row['calibration']+row['warmup']+row['blocks']:
  assert block['full_outputs_exact'] is True
  for response in block['responses'].values():assert sha(root/'evidence/kernel-quiet-001'/response['path'])==response['sha256']
 width=(row['ratio']['ci99'][1]-row['ratio']['ci99'][0])/row['ratio']['median'];assert math.isclose(width,row['ratio']['relative_ci_width'],rel_tol=1e-14)
 assert (width>0.02)==(row['ratio']['gate']=='inconclusive-noise')
assert q['performance']['quiet_window_sha256']==sha(root/'quiet-window.json')
reg=read('evidence/kernel-long-registration.json');assert reg['status']=='registered_not_run';assert reg['source_sha256']==sha(root/'evidence/run_kernel_timing_long.py')
print(json.dumps({'status':'passed','files_verified':len(files),'core_passed':88,'ignored':2,'kernel_packets':8,'typed_cases':15,'physical_packets':2,'timing_gates':[r['ratio']['gate'] for r in t['rows']]},indent=2))
