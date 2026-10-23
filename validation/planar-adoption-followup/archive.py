"""Archive exact independent-comparison and shared-path regression evidence."""
from pathlib import Path
import gzip, hashlib, json, shutil
from fractions import Fraction

root=Path.cwd(); base=root/'target/planar-mixed-reference'
parent=root/'validation/planar-adoption'; out=root/'validation/planar-adoption-followup'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
load=lambda p:json.loads(p.read_text())
assert not out.exists();out.mkdir()
run=load(base/'run.json');build=load(base/'build.json');result=load(base/'comparison.json')
assert run['status']=='passed' and run['exit_code']==0 and run['inputs_unchanged']
assert result['status']=='passed' and result['compared_complex_slots']==10560
assert run['output_artifact_sha256']==sha(base/'comparison.json')
assert run['primary_artifact_sha256']==sha(parent/'mixed-rank7.json')
assert build['exit_code']==0 and build['binary_sha256']==run['binary_sha256']
assert run['build_manifest_sha256']==sha(base/'build.json')
for x in result['comparisons']:
 assert x['complex_slots']==5280 and 0<=Fraction(x['maximum_normalized_error'])<=Fraction(1,10**10)
def copy(src,dst):
 dst=out/dst;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for name in ['source/compare.rs','build.py','build.json','build.log','run.py','run.json','run.log','review.json']:
 copy(base/name,'comparator/'+name)
for p in sorted((base/'failed-build-missing-real').rglob('*')):
 if p.is_file():copy(p,'comparator/'+str(p.relative_to(base)))
copy(Path(__file__),'archive.py')
compressed=out/'comparator/comparison.json.gz'
with compressed.open('wb') as raw:
 with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as zipped:
  zipped.write((base/'comparison.json').read_bytes())
assert hashlib.sha256(gzip.decompress(compressed.read_bytes())).hexdigest()==sha(base/'comparison.json')
regressions=[]
for name,count,ignored in [('execution',35,[]),('pv',14,['pv::tests::original_iregi_cartesian_moments'])]:
 report=root/f'target/planar-adoption/runs/{name}-regressions.json';r=load(report)
 assert r['status']=='passed' and r['exit_code']==0 and r['source_hashes_unchanged'] and r['binary_unchanged']
 assert r['expected_passed_tests']==count and r['ignored_tests']==ignored
 assert r['binary_sha256']==load(parent/'qualification.json')['binary_sha256']
 for suffix in ['json','log']:copy(report.with_suffix('.'+suffix),'regressions/'+name+'.'+suffix)
 regressions.append({'group':name,'passed':count,'ignored':ignored,'report':'regressions/'+name+'.json','elapsed_seconds':r['elapsed_seconds']})
copy(root/'target/planar-adoption/run_regressions.py','regressions/run.py')
qualification={
 'schema_version':1,'kind':'private-certified-planar-mixed-rank7-independent-comparison',
 'status':'passed','production_promoted':False,'automatic_workspace_fallback':False,
 'primary_evidence':{'path':'validation/planar-adoption/qualification.json','sha256':sha(parent/'qualification.json'),
  'original_run_status':'timeout','original_artifact_status':'primary_complete',
  'artifact_path':'validation/planar-adoption/mixed-rank7.json','artifact_sha256':sha(parent/'mixed-rank7.json')},
 'ordinary_rank7_parent':{'path':'validation/planar-integrated/qualification.json','sha256':sha(root/'validation/planar-integrated/qualification.json'),
  'scope':'Separate earlier private binary: ordinary Float128/256 primary versus boxes and exact-artifact convergence; not rerun by this comparator.'},
 'mixed_comparison':{'primary_working_precision':128,'reference_working_precision':256,'requested_precision':53,
  'moments':330,'laurent_slots':4,'shape':[[0,0],[0,1],[1,0],[1,1]],'components':4,
  'primary_rows':3,'accepted_duplicate_lanes':[0,2],'transverse_mixed_rejected_lane':1,
  'complex_slots_per_accepted_lane':5280,'compared_complex_slots':10560,
  'independent_box_rows':5,'independent_box_statuses':result['box_statuses'],
  'comparisons':result['comparisons'],'dimensional_tolerance':'1/10000000000',
  'normalization':'|primary-reference| / max(|reference|, physical_scale^(monomial_rank-6))',
  'convention':'MadLoop','tensor_weights':'Multinomial',
  'independent_algorithm':'Ordinary production6b24 four-point PV; all five pinches in one batch; coefficient jets (2,-1,-1,-1,1)/(6+2st) constructed at256 bits and contracted by Symbolica Dualizer.',
  'primary_validation':'Exact represented input rationals, all successful output slots, full returned basis/convention/weights/ordered shape, duplicate equality, explicit transverse status and rounded128 coefficient jets checked before reference preparation.',
  'report':'comparator/run.json','artifact':'comparator/comparison.json.gz','uncompressed_artifact_sha256':sha(base/'comparison.json'),
  'artifact_bytes':(base/'comparison.json').stat().st_size,'elapsed_seconds':run['elapsed_seconds'],'timeout_seconds':run['timeout_seconds'],
  'build_manifest_sha256':sha(base/'build.json'),'binary_sha256':build['binary_sha256']},
 'shared_path_regressions':regressions,
 'limitations':['Standalone private API candidate only; no automatic fallback or production promotion.',
  'Original combined600s test remains a timeout; independent agreement is established by this separately built bounded comparator.',
  'Two accepted primary lanes are duplicates of one tangent fixture; this is not broader mixed-kinematics coverage.',
  'Exact-rational output encoding does not retain signed-zero signs; claims are numerical agreement, not bitwise identity.',
  'No performance parity or speedup inferred from bounded correctness runs.',
  'One ordinary PV external-reference test remains ignored in this focused run.']}
(out/'qualification.json').write_text(json.dumps(qualification,indent=2)+'\n')
(out/'README.md').write_text("""# Certified planar follow-up evidence

This increment binds the independently evaluated five-box result to the complete
saved mixed-Dual rank-seven primary artifact. The original combined test remains
a timeout in the parent bundle. Read qualification.json for exact scope and counts.

The primary used Float128; this reference uses Float256, both requesting53 bits.
All330 tensor moments, four Laurent slots and four ordered Taylor components are
compared in each of the two accepted duplicate lanes. The transverse mixed lane
remains rejected. This is a private standalone API candidate, without automatic
ordinary-Workspace fallback or a performance claim.

Source/build provenance is in comparator/. The completed6b24 dependency closure
is retained and bound by the parent bundle. The compressed JSON contains every
box output and independent contracted value as exact represented rational values
with per-component precision. Its uncompressed SHA is in qualification.json.

Reproduce from the repository root with the matching retained closure and primary:

```sh
source scripts/env.sh
source .local/symbolica-license.env
python3 target/planar-mixed-reference/build.py
taskset --cpu-list16,17 python3 target/planar-mixed-reference/run.py
```

The scripts require fresh build/output paths and refuse to overwrite prior runs.
An ordinary execution/PV regression increment is retained in regressions/:
35 execution tests and14 PV tests passed; the external-reference PV test was
ignored. Those tests ran against the clean standalone candidate binary, not the
ordinary production archive used by the independent box comparator.
""".replace('--cpu-list16','--cpu-list 16'))
files={str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(out.rglob('*')) if p.is_file()}
(out/'files.json').write_text(json.dumps(files,indent=2)+'\n')
for p,v in files.items():assert sha(out/p)==v['sha256']
print(json.dumps({'qualification_sha256':sha(out/'qualification.json'),'files_sha256':sha(out/'files.json'),'files':len(files)}))
