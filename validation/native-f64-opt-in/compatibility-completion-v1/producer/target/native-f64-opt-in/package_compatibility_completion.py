"""Archive the separate two-check continuation without changing earlier receipts."""
from pathlib import Path
import datetime,hashlib,json,shutil
ROOT=Path.cwd();Q=ROOT/'target/native-f64-opt-in/qualification'
OUT=ROOT/'validation/native-f64-opt-in/compatibility-completion-v1'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
receipt=Q/'compatibility-completion-build-001/build.json';data=read(receipt)
review=Q/'reviews/compatibility-completion-build-001-independent-audit.json';audit=read(review)
assert data['status'] in ('passed','failed') and 'finished_utc' in data
assert audit['status']=='saved-evidence-audit-passed'
assert not OUT.exists();OUT.mkdir(parents=True)
paths=[Q/n for n in ['build_compatibility_completion.py','prepare_compatibility_completion.py','compatibility-completion-proposal.md','compatibility-completion-preparation.json','compatibility-completion-command-plan.json','compatibility-completion-execution-grant-001.json','reviews/compatibility-completion-source-review.json','build.py','lifecycle.py']]
paths += [receipt,review,Path(__file__).resolve()]+sorted((Q/'compatibility-completion-build-001').glob('*.log'))
mapping={}
for p in paths:
    t=OUT/'producer'/p.relative_to(ROOT);t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,t)
    mapping[str(p)]={'path':str(t.relative_to(OUT)),'sha256':sha(p)}
save(OUT/'archive-map.json',{'files':mapping,'source_archive':'../capability-v1/compiled-sources.tar.gz','scope':'Same public source and numerical/tool closure as the linked capability package. Prior successful master.rmeta is reused by digest; binaries are not redistributed.'})
prior1=read(Q/'metadata-build-001/build.json');prior2=read(Q/'compatibility-build-001/build.json')
matrix={}
for r in (prior1,prior2,data):
    for s in r['steps']:
        if s['status']=='passed':matrix[s['label']]={'status':'passed','output_sha256':s['output_sha256']}
expected=[c+'-'+s for c in ('default','selective','broad','both') for s in ('masters','core','masters-tests','core-tests')]
assert set(matrix).issubset(expected)
complete=data['status']=='passed' and set(matrix)==set(expected)
qual={'status':'metadata-four-feature-matrix-complete' if complete else 'metadata-four-feature-matrix-incomplete','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Private metadata compilation only; focused numerical capability remains that of the unchanged default/selective package. Broad/both test binaries were not built or executed.','continuation_producer_status':data['status'],'metadata_matrix':{label:matrix.get(label,{'status':'not-completed'}) for label in expected},'completed_metadata_checks':len(matrix),'expected_metadata_checks':16,'continuation_elapsed_seconds':data['elapsed_seconds'],'runtime_cap_seconds':300,'inputs_unchanged':data['inputs_unchanged'],'cleanup_errors':data['cleanup_errors'],'deadline_exceeded':data['deadline_exceeded'],'build_receipt_sha256':sha(receipt),'independent_audit_sha256':sha(review),'capability_manifest_sha256':sha(ROOT/'validation/native-f64-opt-in/capability-v1/manifest.json'),'incomplete_compatibility_manifest_sha256':sha(ROOT/'validation/native-f64-opt-in/compatibility-v1/manifest.json'),'prior_failed_receipts_preserved':True,'prior_false_producer_guard_preserved':True,'source_archive_reused':True,'production_source_changed':False,'default_changed':False,'performance_qualified':False,'archive_map_sha256':sha(OUT/'archive-map.json')}
save(OUT/'qualification.json',qual)
(OUT/'README.md').write_text('''# Two-check metadata compatibility continuation

This package records only the two combined-feature test metadata checks left unfinished by the preceding bounded attempt. The master test call has a 210-second limit, core tests 60 seconds, and the complete stage 300 seconds including cleanup. The core test call reuses the previously successful combined-feature master metadata; none of the six successful earlier calls is repeated.

The cumulative matrix in qualification.json accounts for the default/selective eight successful checks, six successful broad/combined-library checks and these two final checks. Inspect its explicit status; a saved-evidence audit passing by itself never converts a failed compiler call into a pass. The original 60-second timeout, later aggregate-budget cancellation, unrun rows and false producer final guard remain immutable in capability-v1 and compatibility-v1. The independent later rehash is supplementary evidence, not a rewrite of those terminal records.

This is metadata compatibility on the private qualified source snapshot. It adds no broad D0 runtime coverage, numerical benchmark, production integration or default-policy change. The actual public API and numerical qualification remain those documented in capability-v1. All exact sources are in that package's archive; this package binds the unchanged closure and retained master metadata by digest and preserves the continuation source, commands, logs and independent review.
''')
inventory={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p!=OUT/'manifest.json'}
save(OUT/'manifest.json',{'files':inventory,'self_exclusion':'only this top-level manifest.json','qualification_sha256':sha(OUT/'qualification.json')})
print(json.dumps({'path':str(OUT.relative_to(ROOT)),'status':qual['status'],'completed_metadata_checks':len(matrix),'qualification_sha256':sha(OUT/'qualification.json'),'manifest_sha256':sha(OUT/'manifest.json')}))
