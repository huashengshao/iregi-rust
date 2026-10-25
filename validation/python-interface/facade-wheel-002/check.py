"""Portable saved-only replay; no native host, compiler, subprocess or PID calls."""
from pathlib import Path, PurePosixPath
import gzip
import hashlib
import io
import json
import tarfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
PREFIX = 'target/python-facade-corrected/'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def restore_files(manifest):
    files = {}
    for field in ('source_archive', 'evidence_archive'):
        item = manifest[field]
        data = (HERE / item['path']).read_bytes()
        assert len(data) == item['bytes'] and digest(data) == item['sha256']
        with tarfile.open(fileobj=io.BytesIO(gzip.decompress(data)), mode='r:') as archive:
            members = archive.getmembers()
            assert len(members) == len(item['members'])
            assert {member.name for member in members} == set(item['members'])
            for member in members:
                assert member.isfile() and not PurePosixPath(member.name).is_absolute()
                assert '..' not in PurePosixPath(member.name).parts
                value = archive.extractfile(member).read()
                expected = item['members'][member.name]
                assert len(value) == expected['bytes'] and digest(value) == expected['sha256']
                if member.name in files:
                    assert files[member.name] == value
                files[member.name] = value
    return files


def main():
    manifest = json.loads((HERE / 'manifest.json').read_text())
    assert digest(Path(__file__).read_bytes()) == manifest['checker_sha256']
    files = restore_files(manifest)
    read = lambda name: json.loads(files[PREFIX + name])
    success = ['build-001', 'install-001', 'import-001', 'collect-001',
               'upstream_numeric-003', 'historical-001', 'generic-001', 'n6-001', 'n7-001', 'typing-001']
    groups = []
    for name in success:
        receipt = read(name + '/receipt.json')
        assert receipt['status'] == 'passed' and not receipt['cleanup_errors']
        assert receipt['cancellation'] is None
        assert receipt['elapsed_seconds'] <= receipt['total_seconds']
        assert receipt['live_main_source_lease'] == (name == 'build-001')
        expected_cpu = '18,20,22,24' if name == 'build-001' else '28' if name in {'install-001','import-001','collect-001'} else '30'
        assert receipt['cpu'] == expected_cpu
        for step in receipt['steps']:
            assert step['status'] == 'exited' and step['returncode'] == 0
            assert step['owned_group_gone'] is True and not step.get('timeout', False)
            groups.append(step['owned_process_group'])
    counts = {'upstream_numeric-003':25, 'historical-001':29, 'generic-001':4, 'n6-001':1, 'n7-001':1}
    for name, count in counts.items():
        cases = list(ET.fromstring(files[PREFIX + name + '/tests.xml']).iter('testcase'))
        assert len(cases) == count and all(not list(case) for case in cases)
        assert len(read(name + '/receipt.json')['test_names']) == count
    for name in ['upstream_numeric-001','upstream_numeric-002']:
        receipt = read(name + '/receipt.json')
        assert receipt['status'] == 'failed' and not receipt['cleanup_errors']
        assert receipt['cancellation'] is None
        assert receipt['elapsed_seconds'] <= receipt['total_seconds']
        cases = list(ET.fromstring(files[PREFIX + name + '/tests.xml']).iter('testcase'))
        assert len(cases) == 25 and sum(bool(list(case)) for case in cases) == 1
        assert next(case.attrib['name'] for case in cases if list(case)) == 'test_trait_surface_is_exposed'
        for step in receipt['steps']:
            assert step['returncode'] == 1 and step['owned_group_gone'] is True
            groups.append(step['owned_process_group'])
    assert len(groups) == len(set(groups)) == 13
    assert len(read('collect-001/receipt.json')['test_names']) == 6
    identity = read('import-001/identity.json')
    coercion = identity['upstream_complex_integer_coercion']
    assert coercion['real_bits'] == 2 and coercion['imaginary_bits'] == 128
    assert coercion['integer_scaled_imaginary_bits'] == coercion['float_scaled_imaginary_bits'] == 128
    assert coercion['integer_scaled_imaginary_ratio'] == coercion['float_scaled_imaginary_ratio']
    assert coercion['lost_imaginary_digits'] is False
    typing = read('typing-001/receipt.json')['typing_summary']
    assert typing['errorCount'] == typing['warningCount'] == 0
    assert read('build-001/wheel.json') == manifest['wheel']
    source = manifest['source_archive']['members']
    assert len(source) == 116
    assert source['crates/iregi-python/src/numerical.rs']['sha256'] == 'f61088b6af21ddb3cb0634d1f9776722683def57956ff5a40a018e4855b1f6e5'
    assert source['dependencies/symbolica/lib/numerica/src/domains/float/python.rs']['sha256'] == '169403a10f12e455321de2f3327a14347acfc1809677230c7fd008c4d5e08381'
    assert digest(files[PREFIX+'observer-v3/python_floats.py']) == '7770e460de4055876b48ed2894917f663c0dd3eb1d7c7f18c0c144572ae5a657'
    print(json.dumps({'status':'passed_saved_only','restored_files':len(files),'source_files':116,
        'passed_installed_tests':sum(counts.values()),'typing_errors':0,'typing_warnings':0,
        'corrected_integer_coercion_loss':False,'retained_failed_observer_stages':2,
        'source_scope':'Exact owned build source; post-build observer delta separately retained; no complete native/compiler closure.',
        'native_or_process_execution':False}))


if __name__ == '__main__':
    main()
