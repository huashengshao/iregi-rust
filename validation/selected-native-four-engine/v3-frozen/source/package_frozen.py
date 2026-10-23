"""Archive the completed frozen cohort without changing any producer artifact."""
from pathlib import Path
import gzip,hashlib,json,shutil
ROOT=Path.cwd();BASE=ROOT/'target/selected-native-optimized';V3=BASE/'four-engine-v3'
OUT=ROOT/'validation/selected-native-four-engine/v3-frozen'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not OUT.exists(), 'immutable package already exists'
assert sha(V3/'timing-quiet254/summary.json')=='e4b807914566d52e61798848344a59455f21f839d70f2faa2fca592f3a2513c3'
OUT.mkdir(parents=True)
mapping=[]
def copy(source,destination,compress=False):
    source=ROOT/source if not Path(source).is_absolute()else Path(source)
    dest=OUT/destination;dest.parent.mkdir(parents=True,exist_ok=True)
    data=source.read_bytes();dest.write_bytes(gzip.compress(data,compresslevel=9,mtime=0)if compress else data)
    mapping.append({'original_path':str(source.relative_to(ROOT)),'original_sha256':hashlib.sha256(data).hexdigest(),'package_path':str(dest.relative_to(OUT)),'package_sha256':sha(dest),'compression':'gzip-mtime0'if compress else None})
for dirname in ['timing-quiet254','preflight-001']:
    for source in (V3/dirname).iterdir():
        if not source.is_file():continue
        compress=source.name=='raw.jsonl'
        copy(source,Path(dirname)/(source.name+('.gz'if compress else '')),compress)
for source in V3.iterdir():
    if source.is_file()and source.name!='package_frozen.py'and source.name!='per-family-analysis-proposal.md':copy(source,Path('source')/source.name)
for name in ['admission.py','run.py','control-inventory.json','timing-ready.json','closure-audit.json','plan-binding.json','build.py','build_shared.py','audit_closure.py']:
    if(BASE/name).exists():copy(BASE/name,Path('producer/target/selected-native-optimized')/name)
for folder,names in {'build-001':['build.json','source-qualification-admission.json','baseline.log','candidate.log','probe.log'], 'shared':['accepted.json'], 'shared/build-001':['build.json','compiler.log'], 'source':['probe.rs','core_probe.rs','master_controls.rs'], 'four-engine-v2':['admission_v2.py','timing-ready.json','source-review.json','interface-controls.json'], 'initialization-order-diagnostic':['preparation.json']}.items():
    for name in names:
        p=BASE/folder/name
        if p.exists():copy(p,Path('producer/target/selected-native-optimized')/folder/name)
for source in [BASE/'qualification-001/results.json',BASE/'four-engine-v2/qualification-001/results.json']:
    copy(source,Path('producer')/source.relative_to(ROOT).with_suffix('.json.gz'),True)
for name in ['validation/benchmark/run.py','validation/native-master-replay/inputs.json','target/benchmark/reference-build.json','validation/collier-reference/ready-initial8-v3/build.json','validation/collier-reference/ready-initial8-v3/correctness.json','validation/collier-reference/ready-initial8-v3/producer/validation/collier-reference/run.py','validation/collier-reference/driver.f90','validation/selected-native-initialization-order/manifest.json','target/performance-next-audit/native-v3-final-review.json']:
    copy(name,Path('producer')/name)
for source in(ROOT/'validation/benchmark-quiet/20261024a').iterdir():
    if source.is_file():copy(source,Path('quiet-window')/source.name)
copy(Path(__file__),Path('source/package_frozen.py'))
(OUT/'archive-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
print(json.dumps({'package':str(OUT.relative_to(ROOT)),'archived_files':len(mapping),'originals_unchanged':all(sha(ROOT/x['original_path'])==x['original_sha256']for x in mapping)}))
