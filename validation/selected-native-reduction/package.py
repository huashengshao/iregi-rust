"""Durable complete private semantics evidence; exclude binaries/native archives."""
from pathlib import Path
import gzip, hashlib, json, shutil

ROOT=Path.cwd();HERE=ROOT/'target/selected-native-reduction';DEST=ROOT/'validation/selected-native-reduction'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
save=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n')
raw=HERE/'qualification-001/results.json';result=read(raw)
assert sha(raw)=='c760b59b9e7259d34f82d12f38b14bb298769d86cc220a501ccd19bc5413533b'
assert result['status']=='passed' and result['inputs_unchanged']
audit=HERE/'independent-audit.json';assert audit.exists() and read(audit)['status']=='passed'
assert not DEST.exists(),'preserve previously frozen package'
DEST.mkdir(parents=True)
for rel in ['README.md','design.md','private.patch','source-manifest.json','prepare.py','build.py','run.py','package.py','admission_controls.py','admission-controls.json','independent-audit.json']:
    shutil.copy2(HERE/rel,DEST/rel)
for rel in ['source','copied','earlier-attempts/build001-no-rational-fromstr']:
    shutil.copytree(HERE/rel,DEST/rel)
for attempt in ['build-001','build-002']:
    (DEST/attempt).mkdir()
    for p in (HERE/attempt).glob('*'):
        if p.suffix in ['.log','.json']:shutil.copy2(p,DEST/attempt/p.name)
    shutil.copy2(HERE/(attempt+'-driver.log'),DEST/(attempt+'-driver.log'))
(DEST/'qualification').mkdir()
compressed=DEST/'qualification/results.json.gz'
with raw.open('rb') as src,compressed.open('wb') as dst:
    with gzip.GzipFile(filename='',mode='wb',fileobj=dst,mtime=0) as zipped:shutil.copyfileobj(src,zipped)
assert hashlib.sha256(gzip.decompress(compressed.read_bytes())).hexdigest()==sha(raw)
for p in (HERE/'qualification-001').glob('*.log'):shutil.copy2(p,DEST/'qualification'/p.name)
shutil.copy2(HERE/'qualification-001-driver.log',DEST/'qualification/driver.log')
(DEST/'provenance').mkdir()
for source,name in [
    ('target/e6-direct-n2/preparation.json','debug-closure.json'),
    ('target/core-fused-cse-census/supplemental-deps.json','supplemental-deps.json'),
    ('target/core-fused-cse-census/thiserror-metadata.txt','thiserror-metadata.txt'),
    ('target/core-fused-cse-census/thiserror-cargo-fingerprint.json','thiserror-cargo-fingerprint.json'),
    ('target/master-cse-census/preparation.json','scalar-source-provenance.json'),
    ('target/benchmark/reference-build.json','reference-build.json'),
    ('validation/native-master-replay/inputs.json','inputs.json'),
    ('validation/benchmark/run.py','benchmark-helper.py'),
]:shutil.copy2(ROOT/source,DEST/'provenance'/name)

rows=[]
for row in result['rows']:
    rows.append({'id':row['id'],'batch':row['outer_batch'],'status':row['status'],
        'complex_whole_coefficients_per_backend':sum(len(l['represented']) for l in row['response']['baseline']['lanes']),
        'whole_comparison':row['comparison']['whole_cross_backend'],'master_comparison':row['comparison']['masters'],
        'reference_comparisons':row['reference_comparisons'],'represented_repeated_whole_responses_equal':True})
qualification={'status':'private-opt0-semantics-qualified-performance-unrun','production_adoption':False,
    'scope':'complete public-adapter and whole-reduction correctness for selected ordinary f64 A0/B0/C0, unchanged Symbolica fallback paths; no performance claim',
    'raw_results':{'path':'qualification/results.json.gz','sha256':sha(compressed),'uncompressed_sha256':sha(raw),'uncompressed_bytes':raw.stat().st_size},
    'build_record_sha256':sha(DEST/'build-002/build.json'),'initial_failed_build_sha256':sha(DEST/'build-001/build.json'),
    'initial_failed_probe_log_sha256':sha(DEST/'build-001/probe.log'),
    'initial_failed_fixture_sha256':sha(DEST/'earlier-attempts/build001-no-rational-fromstr/core_probe.rs'),
    'fixture_repair_receipt_sha256':sha(DEST/'earlier-attempts/build001-no-rational-fromstr/receipt.json'),
    'provenance_resolution':'The original raw qualification and independent audit are unchanged; this durable qualification additionally binds the failed probe log and exact fixture-repair receipt explicitly.',
    'source_manifest_sha256':sha(DEST/'source-manifest.json'),'independent_audit_sha256':sha(audit),'parser_controls_sha256':sha(DEST/'admission-controls.json'),
    'runtime_seconds':result['elapsed_seconds'],'runtime_bound_seconds':120,'rows':rows,
    'coverage':{'whole_families':8,'final_complex_coefficients_per_backend':1584,'actual_master_rows':297,'raw_master_complex_coefficients_per_backend':1782,
        'selected_adapter_cases':34,'selected_adapter_successful_lanes':57,'selected_adapter_failed_lanes':21,'selected_adapter_complex_outputs':342,
        'unchanged_master_paths':10,'unchanged_master_cases':33,'unchanged_master_successful_lanes':49,'unchanged_master_failed_lanes':6,'unchanged_master_complex_outputs':432,
        'unchanged_whole_core_paths':3,'unchanged_whole_core_complex_outputs':80,'malformed_parser_controls':24},
    'limitations':['opt0 private master/core and existing debug dependency profiles; no timing inference',
        'direct master/unchanged repeated checks are frozen executable assertions with first/common outputs saved; second snapshots are not retained',
        'bounded N2/N3 rank0/1 whole-family corpus; no new D0 native or high-point coverage claim',
        'all existing production decisions remain unchanged']}
save(DEST/'qualification.json',qualification)
decision={'decision':'retain private semantics qualification; performance and production adoption pending separate authorization',
    'qualification_sha256':sha(DEST/'qualification.json'),'scope':'ordinary binary64 A0/B0/C0 selection through unchanged public adapter',
    'next_candidate':'A bounded optimized whole-call experiment may now be considered; reuse unchanged kernels and preserve the same fallback policy, corpus and guards',
    'timing_authorized':False,'production_changed':False}
save(DEST/'decision.json',decision)
files={str(p.relative_to(DEST)):sha(p) for p in DEST.rglob('*') if p.is_file()}
save(DEST/'manifest.json',{'scope':'complete private selected-native whole-reduction semantics evidence','files':files})
print(json.dumps({'files':len(files),'qualification_sha256':sha(DEST/'qualification.json'),'manifest_sha256':sha(DEST/'manifest.json'),'raw_compressed_bytes':compressed.stat().st_size},indent=2))
