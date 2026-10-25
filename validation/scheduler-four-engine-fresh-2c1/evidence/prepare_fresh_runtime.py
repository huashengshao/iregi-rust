"""Prepare the retained captured qualification corpus after successful builds.

This launches no executable. Captured qualification must precede timing and a
separate captured/uncaptured equality gate. The old runtime source is reused with
only its private HERE path changed; its stricter complete-record admission stays.
"""
from pathlib import Path
import datetime, hashlib, json, shutil, sys

ROOT = Path('/shared/external/iregi/iregi-rust')
HERE = ROOT/'target/guard-performance-review/optimized-performance-proposal'
RUNTIME = HERE/'fresh-captured-runtime'
OLD = ROOT/'target/guard-performance-review/dependent-runtime-proposal'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')

def main():
    assert Path.cwd()==ROOT
    RUNTIME.mkdir(exist_ok=False)
    build_protocol=HERE/'v3/protocol.json'
    protocol=read(build_protocol)
    receipt=Path(protocol['attempt_directory'])/'complete-build-admission.json'
    build=read(receipt)
    assert build['status']=='passed' and build['success'] is True
    assert build['protocol_sha256']==sha(build_protocol)
    assert build['guard_before'] and build['guard_after'] and not build['cleanup_errors']
    assert len(build['steps'])==14 and all(step['status']=='passed' for step in build['steps'])
    assert build['original_failed_receipt_sha256']==protocol['original_failed_receipt_sha256']
    continuation=Path(build['continuation_receipt'])
    assert sha(continuation)==build['continuation_receipt_sha256']
    assert read(continuation)['success'] is True
    independent_path=HERE/'independent-build-audit/audit-001/admission.json'
    independent=read(independent_path)
    assert independent['status']=='passed'
    assert independent['build_receipt_sha256']==sha(receipt)
    assert independent['continuation_receipt_sha256']==sha(continuation)
    assert independent['protocol_sha256']==sha(build_protocol)
    assert independent['pinned_source_revision']==protocol['pinned_source_revision']
    assert independent['compiler_products_checked']==14 and independent['archive_metadata_checked']==10 and independent['probes_checked']==4
    assert independent['all_declared_inputs_artifacts_metadata_maps_checked'] is True
    independent_review=Path(independent['full_review_path'])
    assert sha(independent_review)==independent['full_review_sha256']
    protected=dict(protocol['protected_sha256'])
    tools=dict(protocol['tool_sha256'])
    tools[str(Path(sys.executable))]=sha(Path(sys.executable))
    for raw,expected in {**protected,**tools}.items():
        assert sha(Path(raw) if Path(raw).is_absolute() else ROOT/raw)==expected, raw
    for path in [build_protocol,receipt,continuation,independent_path,independent_review,HERE/'prepare_fresh_runtime.py',
                 HERE/'reviews/v3-origin-context-independent-review.json',
                 HERE/'reviews/fresh-captured-runtime-template-source-review-cpu34.json']:
        protected[str(path.relative_to(ROOT))]=sha(path)
    for item in build['outputs'].values():
        for entry in [item]+[item[key]for key in ['link_map','metadata_log']if key in item]:
            path=Path(entry['path'])
            assert sha(path)==entry['sha256'] and path.stat().st_size==entry['bytes']
            protected[str(path.relative_to(ROOT))]=entry['sha256']
    probes={}
    for variant in ['baseline','candidate']:
        item=build['outputs'][variant+'-probe-captured']
        probes[variant]={key:item[key] for key in ['path','sha256','bytes','archive_binding','link_map']}
        assert set(item['archive_binding'])=={'symbolica','oneloop','iregi_masters','iregi_rust'}
    origins={}
    for name in ['run.py','admission.py','interactive.py','lifecycle.py','control-shapes.json']:
        original=OLD/name
        text=original.read_text()
        if name=='run.py':
            old="HERE=ROOT/'target/guard-performance-review/dependent-runtime-proposal'"
            assert text.count(old)==1
            text=text.replace(old,"HERE=ROOT/'target/guard-performance-review/optimized-performance-proposal/fresh-captured-runtime'")
        if name=='interactive.py':
            old="command=[taskset,'-c','32',str(binary)]"
            assert text.count(old)==1
            text=text.replace(old,"command=[taskset,'-c','34',str(binary)]")
        destination=RUNTIME/name
        destination.write_text(text)
        origins[name]={'path':str(original.relative_to(ROOT)),'sha256':sha(original),
                       'adaptation':'HERE path only' if name=='run.py' else 'CPU32 to CPU34 only' if name=='interactive.py' else 'byte-identical'}
        protected[str(original.relative_to(ROOT))]=sha(original)
        protected[str(destination.relative_to(ROOT))]=sha(destination)
    assert sha(RUNTIME/'lifecycle.py')=='c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824'
    inputs=ROOT/'validation/native-master-replay/inputs.json'
    protected[str(inputs.relative_to(ROOT))]=sha(inputs)
    cases=read(inputs)
    assert len(cases)==4 and {(c['n'],c['rank'])for c in cases}=={(2,0),(2,1),(3,0),(3,1)}
    assert all(len(c['samples'])>=32 for c in cases)
    for path in RUNTIME.glob('*.py'):
        compile(path.read_text(),str(path),'exec')
    runtime={
        'schema_version':1,'status':'SOURCE_REVIEW_REQUIRED_NO_NUMERICAL_GRANT',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cwd':str(ROOT),
        'scope':'Pinned2c1f334 opt3 captured scheduler qualification only, inherited optimized lower dependency context; same retained60requests/eightfamilies/allmasterandDualcontrols. No timing, no uncapturedqualification, no productionapplication.',
        'pinned_source_revision':protocol['pinned_source_revision'],
        'aggregate_budget_seconds':300,'cleanup_postguard_reserve_seconds':20,'effective_work_deadline_seconds':280,
        'cpu_affinity':'34','taskset':protocol['steps'][0]['command'][0],
        'request_count':60,'responses_per_process':30,'probes':probes,
        'build_receipt':str(receipt),'build_receipt_sha256':sha(receipt),
        'independent_build_admission':str(independent_path),'independent_build_admission_sha256':sha(independent_path),
        'inputs':str(inputs),'inputs_sha256':sha(inputs),
        'control_shapes':str(RUNTIME/'control-shapes.json'),'control_shapes_sha256':sha(RUNTIME/'control-shapes.json'),
        'protected_sha256':protected,'tool_sha256':tools,
        'complete_comparison':'Exact complete current cross-scheduler represented values/precision/sign, tensor/Laurent/Taylor/master/status/fallback/diagnostics/counters; own repeats and retained workspaces. Historical opt0 outputs not relabelled as opt3.',
        'environment':'Source scripts/env.sh and private .local/symbolica-license.env silently. Record presence only.',
        'future_command':['python3',str(RUNTIME/'run.py'),'<reviewed-protocol-sha256>'],
        'failure_policy':'Stop first failure, timeout, cancellation, output/hash/change or cleanup issue. Preserve first terminal evidence; no retry/extension.',
        'numerical_executed':False,'numerical_qualified':False,'performance_qualified':False,'production_adoption_authorized':False,
        'next_gate':'Independent saved-data review of complete60requests. Separate uninstrumented qualification/projection gate before same-cohort timing.'}
    save(RUNTIME/'source-origins.json',origins)
    protected[str((RUNTIME/'source-origins.json').relative_to(ROOT))]=sha(RUNTIME/'source-origins.json')
    save(RUNTIME/'protocol.json',runtime)
    print(json.dumps({'protocol_sha256':sha(RUNTIME/'protocol.json'),'protected_inputs':len(protected),'requests':60,'no_executable_or_integral_run':True}))

if __name__=='__main__':
    main()
