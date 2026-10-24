"""Seal one completed metadata continuation; preserves partial/failure outcomes."""
from pathlib import Path
import datetime,hashlib,json,shutil
ROOT=Path.cwd();BASE=ROOT/'target/native-f64-opt-in';Q=BASE/'qualification'
OUT=ROOT/'validation/native-f64-opt-in/compatibility-v1'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
receipt=Q/'compatibility-build-001/build.json';data=read(receipt)
assert data['status'] in ('passed','failed') and 'finished_utc' in data
review=Q/'reviews/compatibility-build-001-independent-audit.json';audit=read(review)
assert audit['status']=='saved-evidence-audit-passed'
assert not OUT.exists();OUT.mkdir(parents=True)
paths=[Q/n for n in ['build_compatibility.py','prepare_compatibility.py','compatibility-protocol.md','compatibility-preparation.json','compatibility-command-plan.json','compatibility-execution-grant-001.json','reviews/compatibility-source-review.json','build.py','lifecycle.py']]
paths += [receipt,review,Path(__file__).resolve()]
paths += sorted((Q/'compatibility-build-001').glob('*.log'))
mapping={}
for p in paths:
    t=OUT/'producer'/p.relative_to(ROOT);t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,t)
    mapping[str(p)]={'path':str(t.relative_to(OUT)),'sha256':sha(p)}
save(OUT/'archive-map.json',{'files':mapping,'source_archive':'../capability-v1/compiled-sources.tar.gz','scope':'Exact source/closure bindings and rmeta output digests remain in the copied preparation/build receipts. Dependency/tool/rmeta binaries are not redistributed.'})
passed=[s['label'] for s in data['steps'] if s['status']=='passed']
failed=[s['label'] for s in data['steps'] if s['status']=='failed']
unrun=[s['label'] for s in data['steps'] if s['status']=='unrun']
qual={'status':'metadata-compatibility-complete' if data['status']=='passed' else 'metadata-compatibility-incomplete','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Private broad/both feature metadata only; no native D0 codegen/runtime or performance qualification. Default/selective capability snapshot remains unchanged.','producer_status':data['status'],'passed':passed,'failed':failed,'unrun':unrun,'runtime_cap_seconds':600,'elapsed_seconds':data['elapsed_seconds'],'cleanup_errors':data['cleanup_errors'],'deadline_exceeded':data['deadline_exceeded'],'inputs_unchanged':data['inputs_unchanged'],'build_receipt_sha256':sha(receipt),'independent_audit_sha256':sha(review),'capability_manifest_sha256':sha(ROOT/'validation/native-f64-opt-in/capability-v1/manifest.json'),'original_metadata_receipt_sha256':sha(Q/'metadata-build-001/build.json'),'archive_map_sha256':sha(OUT/'archive-map.json'),'production_source_changed':False,'default_changed':False,'performance_qualified':False}
save(OUT/'qualification.json',qual)
(OUT/'README.md').write_text('''# Broad/both metadata compatibility continuation

This separate evidence package preserves one metadata-only attempt on the same private public source as `../capability-v1`. Its commands are the original broad/both commands relocated to a new output directory. The authorized limits were 180 seconds per master/master-test call, 60 seconds per core/core-test call, and 600 seconds in aggregate including cleanup. All later rows stop at the first failure. Consult `qualification.json` for the actual outcome, including every incomplete row.

The earlier 60-second timeout and seven unrun checks remain immutable in capability-v1. No code generation, numerical execution, kernel timing, production mutation or default-policy change is part of this continuation. A saved-evidence audit passing means the records are consistent; it does not convert a failed compiler step into a compatibility pass. This package links the complete qualified Rust source archive and dependency closure rather than duplicating them. Compiled metadata outputs are retained by digest and original path in the build receipt.
''')
inventory={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p!=OUT/'manifest.json'}
save(OUT/'manifest.json',{'files':inventory,'self_exclusion':'only this top-level manifest.json','qualification_sha256':sha(OUT/'qualification.json')})
print(json.dumps({'path':str(OUT.relative_to(ROOT)),'status':qual['status'],'passed':passed,'failed':failed,'unrun':unrun,'qualification_sha256':sha(OUT/'qualification.json'),'manifest_sha256':sha(OUT/'manifest.json')}))
