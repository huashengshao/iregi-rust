"""Freeze a source-only uncaptured protocol after build/captured admission pass.

No compiler or executable-under-test is launched. Preparing the protocol does not
grant numerical execution; the exact generated protocol still requires review.
"""
from pathlib import Path
import argparse
import ast
import datetime
import hashlib
import json
import sys
sys.dont_write_bytecode = True
ROOT = Path('/shared/external/iregi/iregi-rust')
BASE = ROOT/'target/guard-performance-review/optimized-performance-proposal'
HERE = BASE/'fresh-uncaptured-proposal'
CAPTURED = BASE/'fresh-captured-runtime'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--captured-independent-admission', type=Path, required=True)
    parser.add_argument('--captured-independent-admission-sha256', required=True)
    args = parser.parse_args()
    assert Path.cwd() == ROOT
    destination = HERE/'protocol.json'
    assert not destination.exists(), 'Preserve first generated protocol; use a reviewed new proposal for changes'
    template = read(HERE/'protocol-template.json')
    build_protocol_path = BASE/'v3/protocol.json'
    build_protocol = read(build_protocol_path)
    build_receipt_path = Path(build_protocol['attempt_directory'])/'complete-build-admission.json'
    build = read(build_receipt_path)
    assert build['status'] == 'passed' and build['success'] is True
    assert build['protocol_sha256'] == sha(build_protocol_path)
    assert len(build['steps']) == 14 and all(value['status'] == 'passed' for value in build['steps'])
    assert build['guard_before'] is True and build['guard_after'] is True and not build['cleanup_errors']
    assert build['original_failed_receipt_sha256'] == build_protocol['original_failed_receipt_sha256']
    continuation = Path(build['continuation_receipt'])
    assert sha(continuation) == build['continuation_receipt_sha256'] and read(continuation)['success'] is True
    captured_protocol_path = CAPTURED/'protocol.json'
    captured_protocol = read(captured_protocol_path)
    captured_receipt_path = CAPTURED/'qualification-001/results.json'
    captured_receipt = read(captured_receipt_path)
    captured_raw = CAPTURED/'qualification-001/responses.jsonl'
    assert captured_receipt['status'] == 'passed-awaiting-independent-saved-data-review'
    assert captured_receipt['protocol_sha256'] == sha(captured_protocol_path)
    assert captured_receipt['build_receipt_sha256'] == sha(build_receipt_path)
    assert captured_receipt['guard_before'] is True and captured_receipt['guard_after'] is True
    assert captured_receipt['cleanup_errors'] == [] and captured_receipt['deadline_exceeded'] is False
    assert captured_receipt['request_count'] == 60 and sha(captured_raw) == captured_receipt['raw_sha256']
    captured_events = [json.loads(line) for line in captured_raw.read_text().splitlines()]
    assert len(captured_events) == 120
    assert [value['event'] for value in captured_events] == ['request', 'response'] * 60
    assert [value['serial'] for value in captured_events] == [serial for serial in range(1,61) for _ in range(2)]
    assert all(key not in captured_receipt for key in ['error', 'guard_error', 'cancellation'])
    independent_path = args.captured_independent_admission.resolve()
    assert sha(independent_path) == args.captured_independent_admission_sha256
    independent = read(independent_path)
    assert independent['status'] == 'passed'
    assert independent['receipt_sha256'] == sha(captured_receipt_path)
    assert independent['raw_sha256'] == sha(captured_raw)
    assert type(independent['request_count']) is int and independent['request_count'] == 60
    assert type(independent['raw_event_count']) is int and independent['raw_event_count'] == 120
    assert independent['all_complete_records_and_controls_checked'] is True
    assert independent['pinned_source_revision'] == build_protocol['pinned_source_revision'] == captured_protocol['pinned_source_revision'] == '2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2'
    full_review_path = Path(independent['full_review_path']).resolve()
    assert full_review_path != independent_path
    assert sha(full_review_path) == independent['full_review_sha256']
    protected = {}
    def add(path, expected=None):
        path = Path(path).resolve()
        observed = sha(path)
        if expected is not None:
            assert observed == expected, str(path)
        key = str(path)
        assert key not in protected or protected[key] == observed
        protected[key] = observed
    for raw, expected in captured_protocol['protected_sha256'].items():
        add(Path(raw) if Path(raw).is_absolute() else ROOT/raw, expected)
    for raw, expected in captured_receipt['input_sha256'].items():
        add(raw, expected)
    for record in captured_receipt['executed_executables'].values():
        add(record['path'], record['sha256'])
    probes = {}
    for variant in ['baseline', 'candidate']:
        captured_item = build['outputs'][variant+'-probe-captured']
        assert captured_protocol['probes'][variant]['path'] == captured_item['path']
        assert captured_protocol['probes'][variant]['sha256'] == captured_item['sha256']
        item = build['outputs'][variant+'-probe-uncaptured']
        assert set(item['archive_binding']) == {'symbolica', 'oneloop', 'iregi_masters', 'iregi_rust'}
        probes[variant] = {key:item[key] for key in ['path', 'sha256', 'bytes', 'archive_binding', 'link_map']}
    for item in build['outputs'].values():
        for record in [item]+[item[key] for key in ['link_map', 'metadata_log'] if key in item]:
            path = Path(record['path'])
            assert path.stat().st_size == record['bytes']
            add(path, record['sha256'])
    for path in [build_protocol_path, build_receipt_path, continuation, captured_protocol_path,
                 captured_receipt_path, captured_raw, independent_path, full_review_path]:
        add(path)
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in ['.py', '.json', '.patch', '.md']:
            if path.suffix == '.py':
                ast.parse(path.read_text(), filename=str(path))
            add(path)
    inputs = ROOT/'validation/native-master-replay/inputs.json'
    assert sha(inputs) == '65d0d2fd554807478569ac88b6d689c9132ce541e98cfb2a3a55b8ef98e5c7ef'
    assert captured_protocol['inputs_sha256'] == sha(inputs)
    add(inputs)
    shapes = HERE/'control-shapes.json'
    assert sha(shapes) == captured_protocol['control_shapes_sha256']
    add(shapes)
    # The untouched inherited transport intentionally pins CPU32 for this
    # untimed qualification. Quiet-window timing will need a separate adapter.
    assert template['cpu_affinity'] == captured_protocol['cpu_affinity'] == '32'
    assert sha(HERE/'lifecycle.py') == 'c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824'
    tools = dict(captured_protocol['tool_sha256'])
    tools[str(Path(sys.executable).resolve())] = sha(Path(sys.executable).resolve())
    for raw, expected in tools.items():
        assert sha(Path(raw)) == expected
    runtime = dict(template)
    runtime.update(
        status='SOURCE_REVIEW_REQUIRED_NO_NUMERICAL_GRANT',
        recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        pinned_source_revision=build_protocol['pinned_source_revision'],
        taskset=build_protocol['steps'][0]['command'][0],
        probes=probes,
        build_receipt=str(build_receipt_path), build_receipt_sha256=sha(build_receipt_path),
        inputs=str(inputs), inputs_sha256=sha(inputs),
        control_shapes=str(shapes), control_shapes_sha256=sha(shapes),
        captured_anchor={
            'protocol':str(captured_protocol_path), 'protocol_sha256':sha(captured_protocol_path),
            'receipt':str(captured_receipt_path), 'receipt_sha256':sha(captured_receipt_path),
            'raw':str(captured_raw), 'raw_sha256':sha(captured_raw),
            'independent_admission':str(independent_path), 'independent_admission_sha256':sha(independent_path),
        },
        protected_sha256=protected, tool_sha256=tools,
        future_command=['python3',str(HERE/'run.py'),'<independently-reviewed-protocol-sha256>'],
    )
    with destination.open('x') as stream:
        stream.write(json.dumps(runtime,indent=2)+'\n')
    print(json.dumps({'status':runtime['status'],'protocol_sha256':sha(destination),
                      'protected_inputs':len(protected),'request_count':60,
                      'normal_responses_projected':52,'no_executable_or_integral_launched':True}))

if __name__=='__main__':
    main()
