"""Retain the private automatic/receipt qualification and unsuccessful history."""
from pathlib import Path
import hashlib,json,shutil,tarfile,datetime
root=Path.cwd();destination=root/'validation/automatic-planar';assert not destination.exists()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
initial=root/'target/planar-automatic';combined=root/'target/planar-automatic-receipts';final=root/'target/planar-counter-followup'
for base,source in [(initial,'source-snapshot'),(combined,'source-snapshot'),(final,'test-source')]:
 build=json.loads((base/'build.json').read_text());assert build['exit_code']==0
 assert sha(base/'core-tests')==build['binary_sha256']
 for path,digest in build['source_hashes'].items():assert sha(base/source/path)==digest
manifest=json.loads((final/'source.json').read_text())
for kind in ['production','test']:
 for path,digest in manifest[kind+'_source_hashes'].items():assert sha(final/(kind+'-source')/path)==digest
passed_groups=[]
for name in ['eligibility','binary64','hybrid','mixed','auxiliary','ordinary','pv-fast','standalone','success']:
 folder='runs-storage-retry' if name=='success' else 'runs'
 p=combined/folder/(name+'.json');report=json.loads(p.read_text());assert report['status']=='passed' and report['exit_code']==0 and report['source_hashes_unchanged'] and report['binary_unchanged']
 passed_groups.append({'name':name,'report':f'combined/{folder}/{name}.json','passed':report['expected_passed_tests'],'ignored':report['ignored_tests'],'selected_tests':report['selected_tests'],'elapsed_seconds':report['elapsed_seconds']})
last=json.loads((final/'runs/all.json').read_text());assert last['status']=='passed' and last['expected_passed_tests']==18 and last['exit_code']==0 and last['source_hashes_unchanged'] and last['binary_unchanged']
destination.mkdir(parents=True)
def copy(source,relative):
 target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
def tree(source,relative):
 for p in sorted(source.rglob('*')):
  if p.is_file():copy(p,Path(relative)/p.relative_to(source))
def archive(source,relative):
 target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
 def normalized(info):info.mtime=0;info.uid=info.gid=0;info.uname=info.gname='';return info
 with tarfile.open(target,'w:gz') as output:
  for p in sorted(source.rglob('*')):
   if p.is_file():output.add(p,arcname=p.relative_to(source),recursive=False,filter=normalized)
for base,label in [(initial,'initial'),(combined,'combined'),(final,'final')]:
 for name in ['build.py','build.json','build.log','run.py']:
  copy(base/name,Path(label)/name)
 if (base/'runs').exists():tree(base/'runs',Path(label)/'runs')
 if (base/'runs-storage-retry').exists():tree(base/'runs-storage-retry',Path(label)/'runs-storage-retry')
 if (base/'source-snapshot').exists():archive(base/'source-snapshot',f'{label}/source.tar.gz')
for name in ['qualification.json','base.json','patches.json','accounting.patch','automatic.patch','compiler-pause.json','user-pause.json','PAUSED.md']:
 copy(initial/name,Path('initial')/name)
for name in ['merge.json','patches.json','combined.patch','receipt-integration.patch','receipt-merge.log','initial-execution-rejects.patch','retry-storage.py']:
 copy(combined/name,Path('combined')/name)
for base,name,label in [(initial,'failed-build-initializer','initial'),(combined,'failed-build-test-import','combined')]:
 folder=base/name
 for p in folder.iterdir():
  if p.is_file():copy(p,Path(label)/name/p.name)
 archive(folder/'source-snapshot',f'{label}/{name}/source.tar.gz')
for name in ['source.json','source-review.json','adoption.patch','adoption.json','adoption-notes.md','concurrency.json']:
 copy(final/name,Path('final')/name)
archive(final/'production-source','final/production-source.tar.gz');archive(final/'test-source','final/test-source.tar.gz')
copy(root/'target/raw-distance-receipts/adoption/combined-source-review.json','reviews/combined-receipt-source.json')
copy(root/'target/raw-distance-receipts/adoption/counter-followup/counter-accounting.patch','reviews/counter-accounting.patch')
copy(root/'validation/raw-distance-receipts-performance/adoption/adoption.patch','reviews/original-receipt-adoption.patch')
closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds'
for name in ['manifest.json','workspace-completion.json','cargo-library-events.json']:copy(closure/name,Path('dependency-closure')/name)
copy(Path(__file__),'package.py')
qualification={'schema_version':1,'kind':'private-automatic-planar-retry-and-receipt-accounting','status':'passed-for-listed-scopes','production_promoted':False,'base':'21622ec','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'combined_candidate':{'build':'combined/build.json','binary_sha256':json.loads((combined/'build.json').read_text())['binary_sha256'],'groups':passed_groups,'scope':'Automatic PV/Hybrid N5 ordinary ranks1/2 and rank2 four/six-component ordered Dual dispatch; full returned arrays/metadata and per-stage counters. Guard failures/invalid rows retained.','counter_version':'Initial unchecked internal receipt increments; final mechanical delta separately qualified below.'},'final_counter_followup':{'build':'final/build.json','binary_sha256':json.loads((final/'build.json').read_text())['binary_sha256'],'report':'final/runs/all.json','passed':18,'selected_tests':last['selected_tests'],'elapsed_seconds':last['elapsed_seconds'],'scope':'Corrected12receipt +6accounting; final checked-counter code and global-error work harvesting. Test-only module trimming source map independently audited.','source_manifest':'final/source.json','source_review':'final/source-review.json'},'final_adoption_patch':{'path':'final/adoption.patch','sha256':sha(final/'adoption.patch'),'production_source':'final/production-source.tar.gz'},'failed_history':[{'path':'initial/runs/hybrid.json','reason':'Incorrect test assumption: full-rank nonplanar tetra fixture has exactly singular triangle sub-Gram; next candidate preserves failure and adds qualified rank1 positive control.'},{'path':'initial/runs/pv-supervisor-failure.json','reason':'ENOSPC erased final report; no PASS/timeout inferred from incomplete log.'},{'path':'combined/runs/receipts.json','reason':'11PASS/1FAIL: new synthetic fixture cloned an already-prepared immutable execution cache before mutating moments; fresh-parent fixture then passed final followup.'},{'path':'combined/runs/success-supervisor-failure.json','reason':'ENOSPC prevented final record, numerical failure location unknown. Same binary fresh-destination retry passed.'},{'path':'initial/failed-build-initializer/build.json','reason':'Incorrect private workspace initializer placement, preserved and corrected.'},{'path':'combined/failed-build-test-import/build.json','reason':'New concrete Float fixture lacked SingleFloat trait import, preserved and corrected.'}],'limitations':['No automatic rank7 numerical claim; standalone rank7 complete-array/box agreement remains separate prior evidence.','Automatic numeric probes cover f64 and Float128, not a new DoubleFloat or arbitrary-width performance qualification.','Final checked-counter delta was tested with18focused tests, not a repeated full combined69-test suite.','Elapsed correctness timings include documented CPU contention; no parity, speedup, or final-code performance conclusion.','One external coefficient-oracle test ignored; longrank7prototype explicitly excluded from pv-fast.','Failed or unsupported lanes retain original failure, never successful initialized zeros.']}
(destination/'qualification.json').write_text(json.dumps(qualification,indent=2)+'\n')
files=[{'path':str(p.relative_to(destination)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(destination.rglob('*')) if p.is_file()]
(destination/'files.json').write_text(json.dumps(files,indent=2)+'\n')
for item in files:assert sha(destination/item['path'])==item['sha256']
print(json.dumps({'path':str(destination/'qualification.json'),'qualification_sha256':sha(destination/'qualification.json'),'files_sha256':sha(destination/'files.json'),'files':len(files),'bytes':sum(x['bytes'] for x in files)},indent=2))
