"""Verify only saved routing algebra evidence; never run Rust/Symbolica."""
from pathlib import Path
import hashlib
import json
import re
import sys
import tarfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    here = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else Path(__file__).resolve().parent
    q = json.loads((here / 'qualification.json').read_text())
    archive = here / q['archive']['path']
    data = archive.read_bytes()
    assert digest(data) == q['archive']['sha256'] and len(data) == q['archive']['bytes']
    files = {}
    with tarfile.open(archive, 'r:gz') as stream:
        for member in stream:
            assert member.isfile() and not Path(member.name).is_absolute()
            assert '..' not in Path(member.name).parts and member.name not in files
            payload = stream.extractfile(member).read()
            assert not payload.startswith((b'\x7fELF', b'!<arch>\n'))
            assert b'S-' + b'130-' not in payload
            expected = q['archive']['member_bindings'][member.name]
            assert digest(payload) == expected['sha256'] and len(payload) == expected['bytes']
            files[member.name] = payload
    assert set(files) == set(q['archive']['member_bindings'])
    assert len(files) == q['archive']['members']

    def load(name):
        return json.loads(files[name])

    original = load('protocol-env-v3/protocol.json')
    continuation = load('protocol-continuation-v5-cpu8/protocol.json')
    failed_build = load('runs/build-001/result.json')
    build = load('runs-env-v3/build-001/result.json')
    partial = load('runs-env-v3/exact-001/result.json')
    final = load('runs-continuation-v5-cpu8/exact-001/result.json')
    assert digest(files['protocol-continuation-v5-cpu8/protocol.json']) == q['protocol_sha256']
    assert failed_build['status'] == 'failed' and build['status'] == 'passed'
    assert partial['status'] == 'failed' and partial['errors'] == ["RuntimeError('cancelled by signal 15')"]
    assert original['selected_tests'] == q['selected_cases'] == continuation['complete_gate']
    assert len(original['selected_tests']) == len(set(original['selected_tests'])) == 16
    assert partial['completed_cases'] == original['selected_tests'][:9]
    assert continuation['selected_tests'] == original['selected_tests'][9:]
    assert len(original['expected_listing']) == q['discovered_cases'] == 39
    assert len(continuation['inputs']) == q['bound_inputs'] == 176
    assert len(continuation['closed_search_directories']) == 2
    assert continuation['bounds'] == original['bounds']
    assert continuation['cpu_affinity']['exact'] == [8]
    assert original['cpu_affinity']['exact'] == [6]
    assert build['binary_sha256'] == partial['binary_sha256'] == final['binary_sha256'] == q['test_binary_sha256']
    assert final['status'] == 'passed' and final['completed_cases'] == continuation['selected_tests']
    assert partial['completed_cases'] + final['completed_cases'] == q['completed_cases']
    assert len(q['completed_cases']) == 16 and not q['remaining_unadmitted_cases']
    for folder, result, selected in [
        ('runs-env-v3/exact-001', partial, partial['completed_cases']),
        ('runs-continuation-v5-cpu8/exact-001', final, final['completed_cases']),
    ]:
        assert result['all_owned_groups_gone']
        for index, name in enumerate(selected):
            event = result['commands'][index + 1]
            assert event['label'] == f'test-{index:02}'
            assert event['status'] == 'exited' and event['returncode'] == 0 and event['owned_group_gone']
            assert name in event['command'] and '--exact' in event['command']
            text = files[f'{folder}/{index+1:02}-test-{index:02}.log'].decode()
            assert re.search(r'^test ' + re.escape(name) + r' \.\.\. ok$', text, re.M)
            assert re.search(r'^test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured;', text, re.M)
    assert digest(files[q['source_and_exact_independent_review']]) == q['independent_exact_audit_sha256']
    assert q['status'] == 'private_algebra_qualification_passed'
    assert q['complete_original_sixteen_case_gate_passed']
    assert not any(q[name] for name in [
        'production_applied', 'full_core_integration_qualified', 'current_cargo_qualified',
        'scalar_numerical_reference_qualified', 'generalized_highpoint_qualified',
        'dual_accuracy_qualified', 'performance_qualified'])
    print(json.dumps(dict(status='passed', exact_cases=16, archive_members=len(files),
                          preserved_failed_build=True, preserved_scheduling_abort=True,
                          no_rust_symbolica_or_integral_executed=True)))


if __name__ == '__main__':
    main()
