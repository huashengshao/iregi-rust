"""Preserve private capability evidence; no compiler or numerical execution."""
from pathlib import Path
import datetime,gzip,hashlib,io,json,shutil,tarfile

ROOT=Path.cwd(); BASE=ROOT/'target/native-f64-opt-in'; Q=BASE/'qualification'
OUT=ROOT/'validation/native-f64-opt-in/capability-v1'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
assert not OUT.exists(), 'sealed output already exists'
audit=read(Q/'whole-qualification-001/independent-evidence-review.json')
assert audit['status']=='independent-evidence-review-passed'
OUT.mkdir(parents=True)
mapping={}
source_paths=sorted(set(p for folder in [Q/'public-source',Q/'source'] for p in folder.rglob('*') if p.is_file()))
with (OUT/'compiled-sources.tar.gz').open('wb') as f:
    with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0,compresslevel=6) as gz:
        with tarfile.open(fileobj=gz,mode='w') as tar:
            for p in source_paths:
                member=str(p.relative_to(ROOT));data=p.read_bytes();info=tarfile.TarInfo(member)
                info.size=len(data);info.mode=0o644;info.mtime=0;tar.addfile(info,io.BytesIO(data))
                mapping[str(p)]={'archive':'compiled-sources.tar.gz','member':member,'sha256':sha(p),'bytes':len(data)}
suffixes={'.json','.jsonl','.py','.md','.log','.txt','.patch','.csv'}
paths=set(p for p in Q.rglob('*') if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts and str(p) not in mapping)
for name in ['base-manifest.json','source-review-ready.json','proposed.patch']:
    paths.add(BASE/name)
paths.add(Path(__file__).resolve())
bindings={}
for name in ['metadata-preparation.json','preparation.json','observation-preparation.json','whole-qualification-001/results.json']:
    bindings.update(read(Q/name)['input_sha256'])
for name in bindings:
    p=Path(name)
    if p.is_relative_to(ROOT) and p.suffix in suffixes|{'.rs'} and p.stat().st_size<16_000_000 and str(p) not in mapping:
        paths.add(p)
for p in sorted(paths):
    if str(p) in mapping:continue
    target=OUT/'producer'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
    if p.stat().st_size>512_000:
        target=target.with_name(target.name+'.gz')
        with p.open('rb') as src,target.open('wb') as dst:
            with gzip.GzipFile(filename='',fileobj=dst,mode='wb',mtime=0,compresslevel=6) as gz:shutil.copyfileobj(src,gz)
        mapping[str(p)]={'path':str(target.relative_to(OUT)),'encoding':'gzip','sha256':sha(p),'bytes':p.stat().st_size}
    else:
        shutil.copyfile(p,target)
        mapping[str(p)]={'path':str(target.relative_to(OUT)),'encoding':'identity','sha256':sha(p),'bytes':p.stat().st_size}
for p,digest in bindings.items():
    assert sha(p)==digest, f'changed bound artifact: {p}'
external={p:d for p,d in bindings.items() if p not in mapping}
save(OUT/'archive-map.json',{'scope':'Exact original bytes mapped to copies or tar members; external binary/dependency/tool inputs remain hash-bound and are not redistributed.','files':mapping,'external_hash_only':external})
qual={
 'status':'private-default-and-selective-capability-qualified',
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'name':'TIRust optional native f64 A0/B0/C0 backend',
 'base_project_head':read(BASE/'base-manifest.json').get('base_project_head',read(Q/'observation-preparation.json')['base_project_head']),
 'patch_sha256':sha(BASE/'proposed.patch'),
 'production_source_changed':False,'default_policy_changed':False,'performance_qualified':False,
 'features':{'default':'metadata/codegen/17-test inventory subset qualified','native-f64-abc':'metadata/codegen/focused tests/whole arrays qualified','native-batch':'incomplete: original master metadata timeout at 60 seconds','both':'unrun after original timeout'},
 'public_tests':{'named_tests_passed':17,'receipt_sha256':sha(Q/'public-tests-001/results.json'),'independent_audit_sha256':sha(Q/'reviews/public-tests-001-independent-audit.json')},
 'whole':{'receipt_sha256':sha(Q/'whole-qualification-001/results.json'),'raw_sha256':sha(Q/'whole-qualification-001/responses.jsonl'),'independent_review_sha256':sha(Q/'whole-qualification-001/independent-evidence-review.json'),**audit['numerical_summary'],**audit['protocol_summary']},
 'limitations':audit['limitations']+['The project crates were compiled at opt0 against the previously bound numerical dependency profiles. These runs support correctness, not performance.','The observation overlay adds read-only capture/accessors under an explicit cfg; focused public API tests exercise the uninstrumented candidate source.','Compiled binaries, toolchain and dependency archives are retained by digest and original path, not distributed inside this evidence bundle.','Original metadata failure, seven unrun compatibility checks, parser-only controls and source-preparation failure are preserved.'],
 'archive_map_sha256':sha(OUT/'archive-map.json')}
save(OUT/'qualification.json',qual)
(OUT/'README.md').write_text('''# Optional native f64 backend capability qualification

This private TIRust candidate adds an explicit `NativeF64Abc` execution policy and `native-f64-abc` feature. The default remains unchanged. The selected path uses the existing oneloopmaster-generated A0/B0/C0 Rust modules only for ordinary f64; D0, dB0, DoubleFloat, Float and Dual use Symbolica under the explicit policy.

Seventeen focused public API tests passed. A separate read-only observation overlay passed all 38 requests, including all eight retained bubble/triangle tensor families and all six master outputs, exact own repeats, IREGI agreement at the original 1e-10 normalized tolerance, precision/Dual fallback, invalid-lane controls and cache interleaving. Independent numerical and provenance audits are included.

The original broad `native-batch` metadata attempt reached its 60-second limit; the remaining seven compatibility checks were not run. That failure remains visible. A later separately authorized compatibility-only attempt, if performed, must have its own receipt and does not rewrite this snapshot. No production integration, default change or performance claim follows from this package.

`compiled-sources.tar.gz` preserves the exact public and observation Rust snapshots. `archive-map.json` maps every preserved original path and decompressed digest. The external hash-only list explicitly identifies omitted binaries, toolchain and dependency archives. Logs, original inputs, source and admission scripts, raw JSONL/stdout, producer and independent receipts, command plans and authorization records are preserved under `producer/`; large files use deterministic gzip. No license material is included.

Reproduction requires restoring mapped bytes at their original project-relative paths and obtaining the pinned toolchain/dependency closure. The original commands and bounded lifecycle are recorded in the build and runtime receipts. Merely rerunning a producer is not independent admission: the saved-data validators and independent reviews are separate evidence.
''')
# Verify archive mappings from packaged bytes, without relying on source files.
with tarfile.open(OUT/'compiled-sources.tar.gz','r:gz') as tar:
    for original,item in mapping.items():
        if 'archive' in item:data=tar.extractfile(item['member']).read()
        else:
            data=(OUT/item['path']).read_bytes()
            if item['encoding']=='gzip':data=gzip.decompress(data)
        assert hashlib.sha256(data).hexdigest()==item['sha256'],original
inventory={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p!=OUT/'manifest.json'}
save(OUT/'manifest.json',{'status':'frozen','files':inventory,'self_exclusion':'only this top-level manifest.json','qualification_sha256':sha(OUT/'qualification.json')})
print(json.dumps({'path':str(OUT.relative_to(ROOT)),'files':len(inventory),'mapped_original_files':len(mapping),'external_hash_only':len(external),'qualification_sha256':sha(OUT/'qualification.json'),'manifest_sha256':sha(OUT/'manifest.json'),'total_bytes':sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())}))
