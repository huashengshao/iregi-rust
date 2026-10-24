"""Copy already terminal source/test evidence. Never launches a compiler or kernel."""
from pathlib import Path
from io import BytesIO
import datetime, gzip, hashlib, json, shutil, sys, tarfile

ROOT = Path('/shared/external/iregi/iregi-rust')
HERE = ROOT / 'target/guard-performance-review'
DEST = ROOT / 'validation/uniform-branch-scheduler'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def package(reviews):
    assert Path.cwd() == ROOT
    assert reviews, 'Independent saved-evidence review is required'
    v4 = HERE / 'qualification-plan-v4'
    protocol = json.loads((v4 / 'protocol.json').read_text())
    assert sha(v4 / 'protocol.json') == '093c8d1112b927851fe00c83d5eb7077e257c4e6789822a3abb9b3d7833e48f0'
    for raw, expected in {**protocol['protected_sha256'], **protocol['tool_sha256']}.items():
        path = Path(raw) if Path(raw).is_absolute() else ROOT / raw
        assert sha(path) == expected, str(path)
    compile_receipt = json.loads((v4 / 'compile-003/receipt.json').read_text())
    test_receipt = json.loads((v4 / 'tests-003/receipt.json').read_text())
    assert compile_receipt['success'] and test_receipt['success']
    assert compile_receipt['guard_after'] and test_receipt['guard_after']
    assert sha(v4 / 'compile-003/unit-tests') == compile_receipt['binary_sha256'] == test_receipt['binary_sha256']
    assert sha(v4 / 'compile-003/receipt.json') == test_receipt['compile_receipt']['sha256']
    for step in test_receipt['steps']:
        assert step['status'] == 'passed' and step['owned_group_gone'] and step['returncode'] == 0
        assert sha(v4 / 'tests-003' / (step['name'] + '.log')) == step['log_sha256']
    DEST.mkdir(exist_ok=False)
    members = {}
    for version in [2, 3, 4]:
        source = HERE / ('qualification-plan-v' + str(version))
        manifest = json.loads((source / 'manifest.json').read_text())
        for name, entry in manifest['files'].items():
            path = source / name
            assert sha(path) == entry['sha256'] and path.stat().st_size == entry['bytes']
            members[str(path.relative_to(HERE))] = path
        members[str((source / 'manifest.json').relative_to(HERE))] = source / 'manifest.json'
    for name in ['base/batch.rs', 'candidate/batch.rs', 'uniform-branch.patch', 'PROPOSAL.md']:
        members['original-proposal/' + name] = HERE / name
    api = json.loads((v4 / 'source-api-check.json').read_text())
    for name, expected in api['sources'].items():
        path = ROOT / name
        assert sha(path) == expected
        members['numeric-api/' + name] = path
    inventory = {name: {'original_path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size} for name, path in sorted(members.items())}
    with (DEST / 'source-packets.tar.gz').open('xb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
            with tarfile.open(mode='w', fileobj=gz) as archive:
                for name, path in sorted(members.items()):
                    data = path.read_bytes()
                    info = tarfile.TarInfo(name)
                    info.size = len(data); info.mode = 0o644; info.mtime = 0
                    archive.addfile(info, BytesIO(data))
    with tarfile.open(DEST / 'source-packets.tar.gz', 'r:gz') as archive:
        assert sorted(archive.getnames()) == sorted(inventory)
        for member in archive:
            data = archive.extractfile(member).read()
            assert hashlib.sha256(data).hexdigest() == inventory[member.name]['sha256']
            assert len(data) == inventory[member.name]['bytes']
    save(DEST / 'archive-member-inventory.json', inventory)
    origins = {}

    def copy(source, name):
        target = DEST / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        assert source.read_bytes() == target.read_bytes()
        origins[name] = {'original_path': str(source.relative_to(ROOT)), 'sha256': sha(source), 'bytes': source.stat().st_size}

    for version, attempt in [(2, '001'), (3, '002'), (4, '003')]:
        source = HERE / ('qualification-plan-v' + str(version)) / ('compile-' + attempt)
        for name in ['receipt.json', 'compile.log']:
            copy(source / name, 'attempts/compile-' + attempt + '/' + name)
    for path in sorted((v4 / 'tests-003').iterdir()):
        if path.is_file():
            copy(path, 'attempts/tests-003/' + path.name)
    for name in ['uniform_branch_tests.rs', 'uniform_branch_baseline.rs', 'constructor-trait-selection.patch', 'protocol.json', 'manifest.json', 'source-inventory.json', 'narrow-source-review.json']:
        copy(v4 / name, 'source/' + name)
    for name in ['base/batch.rs', 'candidate/batch.rs', 'uniform-branch.patch']:
        copy(HERE / name, 'source/production-' + name.replace('/', '-'))
    copy(HERE / 'dependent-relink-proposal/PROPOSAL.md', 'next-stage-proposal.md')
    for index, source in enumerate(reviews):
        assert source.is_file()
        copy(source, 'reviews/' + str(index) + '-' + source.name)
    copy(Path(__file__).resolve(), 'package.py')
    save(DEST / 'payload-origins.json', origins)
    (DEST / 'README.md').write_text('''# Private uniform-branch scheduler fixture gate

Exactly 15 requested Symbolica tests pass: five existing batch tests, six focused scheduler tests, and four existing nested/shared evaluator tests. The focused tests compare the actual frozen old batch evaluator, the candidate, and the scalar evaluator; they require finite values, exact value/precision/debug observations, ordered active-lane traces, and signed-zero bits. Numeric coverage includes f64, DoubleFloat, mixed 80/192-bit Float, and static/dynamic three-component second-order and nine-component mixed-order Dual shapes.

This is a private, instrumented local scheduler fixture qualification. The production candidate has not been applied to live sources; dependent OneLoop/core/master numerical qualification, optimized timing and adoption remain unqualified. The next-stage document is only a proposal and launches nothing. Build/test elapsed times are lifecycle diagnostics, not performance measurements.

Both earlier compile-only fixture API failures remain visible: compile001 missed the Constructible bound implied by Complex's inherent zero constructor; compile002 then excluded Float. Compile003 selects the existing FloatLike temporary constructor explicitly, preserving Float coverage and all numerical fixtures. No production arithmetic, branch predicate, guard or tolerance changed.

The deterministic source archive contains the complete frozen source packets from all three attempts, plus the original production delta and the relevant existing Numerica constructor APIs. Its inventory records every exact source path/hash/size. Terminal receipts/logs, the repaired test source, protocol and independent reviews are also directly readable here. The 157 MB test executable and preexisting dependency archives are deliberately external; their exact hashes, sizes and retained paths are bound by the receipts/protocol. No license environment is included.

The protocol records the exact historical compiler/test commands and environment. Reproduction requires the pinned non-Python dependency/native closure and supported Symbolica license. Extract source into a fresh private directory, issue a fresh reviewed path/output protocol, and preserve all prior attempts; do not rerun the frozen runners into their existing output directories. No comparison result may be inferred from merely rebuilding the archive.
''')
    names = [name for step in test_receipt['steps'] if 'expected_pass_count' in step for name in step['expected_test_names']]
    assert len(names) == 15 and len(set(names)) == 15
    files = {str(path.relative_to(DEST)): {'sha256': sha(path), 'bytes': path.stat().st_size} for path in sorted(DEST.rglob('*')) if path.is_file()}
    qualification = {
        'schema_version': 1, 'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'PRIVATE_SYMBOLICA_SCHEDULER_FIXTURE_GATE_PASSED',
        'local_fixture_qualified': True, 'production_source_applied': False,
        'dependent_core_master_qualified': False, 'full_reduction_qualified': False,
        'performance_qualified': False, 'production_adoption_qualified': False,
        'production_candidate_sha256': sha(HERE / 'candidate/batch.rs'),
        'final_protocol_sha256': sha(v4 / 'protocol.json'),
        'final_source_manifest_sha256': sha(v4 / 'manifest.json'),
        'compile_receipt_sha256': sha(v4 / 'compile-003/receipt.json'),
        'test_receipt_sha256': sha(v4 / 'tests-003/receipt.json'),
        'test_binary_sha256': compile_receipt['binary_sha256'],
        'test_binary_bytes': compile_receipt['binary_bytes'],
        'test_binary_included': False, 'retained_failed_compile_attempts': ['001', '002'],
        'local_exact_test_count': 15, 'local_exact_test_names': names, 'selected_ignored_tests': 0,
        'numeric_scope': ['f64', 'DoubleFloat', 'mixed Float80/192', 'static/dynamic Dual shapes3/9'],
        'comparison_scope': 'Actual old-batch/candidate/scalar finite/value/precision/debug and active instruction/lane assertions; no exported raw numeric arrays.',
        'protected_input_count': len(protocol['protected_sha256']),
        'tool_guard_count': len(protocol['tool_sha256']),
        'source_archive_members': len(inventory),
        'diagnostic_compile_seconds': compile_receipt['elapsed_seconds_diagnostic'],
        'diagnostic_test_seconds': test_receipt['elapsed_seconds_diagnostic'],
        'files': files,
    }
    for raw, expected in {**protocol['protected_sha256'], **protocol['tool_sha256']}.items():
        path = Path(raw) if Path(raw).is_absolute() else ROOT / raw
        assert sha(path) == expected, 'Post-copy source guard: ' + str(path)
    save(DEST / 'qualification.json', qualification)
    print(json.dumps({'capsule': str(DEST.relative_to(ROOT)), 'qualification_sha256': sha(DEST / 'qualification.json'), 'source_members': len(inventory), 'payload_files': len(files), 'archive_bytes': (DEST / 'source-packets.tar.gz').stat().st_size}))


if __name__ == '__main__':
    package([Path(path).resolve() for path in sys.argv[1:]])
