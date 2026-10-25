"""Seal existing saved evidence only; never compile or run numerical code."""
from pathlib import Path
import collections
import datetime
import gzip
import hashlib
import json
import shutil
import statistics
import tarfile

ROOT = Path('/shared/external/iregi/iregi-rust')
BASE = ROOT / 'target/guard-performance-review/optimized-performance-proposal'
HERE = Path(__file__).resolve().parent
PIN = '2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False) + '\n')


def main():
    assert Path.cwd() == ROOT and HERE == ROOT / 'validation/scheduler-four-engine-fresh-2c1'
    assert not (HERE / 'manifest.json').exists(), 'Never overwrite a sealed capsule'
    origins = []

    def copy(source, relative=None):
        source = Path(source)
        relative = relative or 'evidence/' + str(source.relative_to(BASE))
        destination = HERE / relative
        assert source.is_file() and not source.is_symlink() and not destination.exists()
        before = sha(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        assert sha(destination) == sha(source) == before
        origins.append({'path': relative, 'origin': str(source), 'sha256': before,
                        'bytes': destination.stat().st_size, 'copy': 'byte-identical'})

    def archive(name, members):
        records = []
        destination = HERE / name
        assert not destination.exists()
        with destination.open('xb') as raw:
            with gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0, compresslevel=6) as zipped:
                with tarfile.open(fileobj=zipped, mode='w|') as tar:
                    for member, source, expected in sorted(members):
                        source = Path(source)
                        assert source.is_file() and not source.is_symlink()
                        before = sha(source)
                        if expected is not None:
                            assert before == expected, str(source)
                        info = tarfile.TarInfo(member)
                        info.size = source.stat().st_size
                        info.mode = 0o644
                        info.mtime = info.uid = info.gid = 0
                        info.uname = info.gname = ''
                        with source.open('rb') as stream:
                            tar.addfile(info, stream)
                        assert sha(source) == before
                        records.append({'path': member, 'origin': str(source), 'sha256': before,
                                        'bytes': info.size, 'copy': 'byte-identical archive member'})
        write(HERE / (name + '.members.json'), {'archive': name, 'sha256': sha(destination),
              'members': records, 'uncompressed_bytes': sum(item['bytes'] for item in records)})
        return records

    direct = ['prepare_fresh.py', 'build_fresh.py', 'fresh_lifecycle.py',
              'fresh-build-protocol.json', 'prepare_fresh_runtime.py', 'FRESH-BUILD.md',
              'FRESH-COHORT-HANDOFF.md', 'context-adjudication-fresh2c1-001.json',
              'latency-table-fresh2c1-001.json', 'future-idle-pairs-observation.json']
    for name in direct:
        copy(BASE / name)
    source_directories = ['fresh-source', 'v3', 'fresh-captured-runtime',
                          'fresh-uncaptured-proposal', 'fresh-four-engine-proposal', 'reviews']
    allowed = {'.py', '.json', '.md', '.patch', '.rs', '.csv'}
    for directory in source_directories:
        for path in sorted((BASE / directory).iterdir()):
            if path.is_file() and not path.is_symlink() and path.suffix in allowed:
                copy(path)
    for directory in ['fresh-uncaptured-proposal/draft-cpu32',
                      'fresh-four-engine-proposal/draft-pre-lease-log-hardening']:
        for path in sorted((BASE / directory).rglob('*')):
            if path.is_file() and not path.is_symlink() and path.suffix in allowed:
                copy(path)
    for directory in sorted(BASE.glob('independent-*')):
        if directory.is_dir():
            for path in sorted(directory.rglob('*')):
                if path.is_file() and '__pycache__' not in path.parts and path.suffix in allowed:
                    copy(path)
    for directory in ['fresh-build-001', 'v3/build-001']:
        for path in sorted((BASE / directory).rglob('*')):
            if path.is_file() and path.suffix in {'.json', '.log'}:
                copy(path)
    for directory in ['contention-context-fresh2c1-001']:
        for path in sorted((BASE / directory).glob('*.json')):
            copy(path)

    stages = {
        'captured': BASE / 'fresh-captured-runtime/qualification-001',
        'uncaptured': BASE / 'fresh-uncaptured-proposal/qualification-001',
        'preflight': BASE / 'fresh-four-engine-proposal/preflight-fresh2c1-001',
        'timing': BASE / 'fresh-four-engine-proposal/timing-fresh2c1-001',
    }
    numerical_members = []
    receipts = {}
    for name, directory in stages.items():
        receipt = directory / ('results.json' if name in ['captured', 'uncaptured'] else 'receipt.json')
        receipts[name] = receipt
        copy(receipt)
        for path in sorted(directory.iterdir()):
            if path.name == 'summary.json':
                copy(path)
            elif path.is_file() and (path.suffix == '.jsonl' or path.name.endswith('.stdout.log')
                                     or path.name.endswith('.stderr.log')):
                numerical_members.append(('evidence/' + str(path.relative_to(BASE)), path, None))
    raw_members = archive('numerical-records.tar.gz', numerical_members)

    build = read(BASE / 'v3/build-001/complete-build-admission.json')
    maps = {(value['link_map']['path'], value['link_map']['sha256'])
            for value in build['outputs'].values() if 'link_map' in value}
    assert len(maps) == 4
    archive('link-maps.tar.gz', [('evidence/' + str(Path(path).relative_to(BASE)), Path(path), wanted)
                               for path, wanted in maps])
    v3 = read(BASE / 'v3/protocol.json')
    snapshots = []
    for raw, wanted in v3['protected_sha256'].items():
        path = Path(raw) if Path(raw).is_absolute() else ROOT / raw
        if path.suffix in {'.rs', '.toml', '.lock'} and path.is_relative_to(ROOT / 'target'):
            snapshots.append(('source-snapshot/' + str(path.relative_to(ROOT)), path, wanted))
    assert len(snapshots) == 293
    archive('source-snapshot.tar.gz', snapshots)
    research = BASE / 'provenance-v3-research'
    metadata = [('evidence/' + str(path.relative_to(BASE)), path, None)
                for path in research.rglob('*') if path.is_file() and not path.is_symlink()
                and '__pycache__' not in path.parts and path.suffix in {'.json', '.log', '.md', '.py', '.txt'}]
    archive('provenance-metadata.tar.gz', metadata)

    copy(BASE / 'independent-timing-audit/audit-001/ratio-table.json', 'ratio-table.json')
    copy(BASE / 'independent-timing-audit/audit-001/ratio-table.csv', 'ratio-table.csv')
    copy(BASE / 'latency-table-fresh2c1-001.json', 'latency-table.json')
    original = read(BASE / 'fresh-build-001/build.json')
    merged = BASE / 'v3/build-001/complete-build-admission.json'
    timing = read(receipts['timing'])
    summary_path = stages['timing'] / 'summary.json'
    summary = read(summary_path)
    assert summary['global_admission_errors'] == [] and timing['global_lifecycle_clean'] is True
    assert timing['status'] == 'completed-with-inconclusive-rows'
    ratios = read(HERE / 'ratio-table.json')
    assert len(ratios) == 40
    table = read(HERE / 'latency-table.json')

    def ref(path):
        relative = 'evidence/' + str(Path(path).relative_to(BASE))
        assert (HERE / relative).is_file()
        return {'path': relative, 'sha256': sha(HERE / relative)}

    gates = dict(collections.Counter(row['gate'] for row in ratios))
    rows = []
    quartet_rows = []
    inputs = read(ROOT / 'validation/native-master-replay/inputs.json')
    for receipt_row, times in zip(timing['rows'], table['rows']):
        case = next(case for case in inputs if case['id'] == receipt_row['id'])
        selected = [row for row in ratios if row['id'] == times['id'] and row['batch'] == times['batch']]
        assert len(selected) == 5
        rows.append({'id': times['id'], 'n': case['n'], 'rank': case['rank'], 'batch': times['batch'],
                     'quartets': 48, 'iterations': receipt_row['iterations'],
                     'median_ns_per_complete_batch_call': times['engine_median_ns_per_complete_batch_call'],
                     'ns_per_sample_from_median_batch_call': times['engine_ns_per_sample_from_median_batch_call'],
                     'raw_row_status': receipt_row['status'], 'short_blocks': times['short_blocks'],
                     'raw_ratios': selected, 'acceptance_eligibility': False})
        quartet_rows.append({'id': times['id'], 'batch': times['batch'], 'iterations': receipt_row['iterations'],
                             'calibration': receipt_row['calibration'], 'blocks': receipt_row['blocks']})
    write(HERE / 'quartets.json', quartet_rows)
    write(HERE / 'performance.json', {
        'schema_version': 1, 'scope': read(BASE / 'context-adjudication-fresh2c1-001.json')['scope'],
        'pinned_source_revision': PIN, 'raw_arithmetic_admitted': True,
        'acceptance_eligibility': False, 'uncontended_parity_qualified': False,
        'global_performance_qualified': False, 'production_adoption_authorized': False,
        'reason': 'Substantial unrelated activity on reserved physical core SMT sibling290; raw gates unchanged.',
        'raw_gate_counts': gates, 'quartets': 384, 'ratios': 40,
        'units': 'Nanoseconds per complete batch reduction call; batch32 throughput per sample is call median/32.',
        'rows': rows,
        'original_summary': ref(summary_path),
        'context_adjudication': ref(BASE / 'context-adjudication-fresh2c1-001.json'),
        'independent_environment': ref(BASE / 'independent-timing-audit/audit-001/environment-addendum.json'),
    })
    qualification = {
        'schema_version': 1, 'pinned_source_revision': PIN,
        'matched_optimized_build_products': 14, 'matched_optimized_build_passed': True,
        'captured_qualified': True, 'uncaptured_qualified': True, 'preflight_qualified': True,
        'numerical_qualified': True, 'saved_timing_arithmetic_qualified': True,
        'performance_qualified': False, 'acceptance_eligibility': False,
        'uncontended_parity_qualified': False, 'production_adoption_authorized': False,
        'captured_requests': 60, 'captured_events': 120, 'uncaptured_requests': 60,
        'uncaptured_events': 120, 'normal_exact_captured_projections': 52,
        'preflight_requests': 168, 'preflight_events': 336,
        'timing_requests': 1768, 'timing_events': 3536, 'timed_replies': 1600,
        'quartets': 384, 'ratio_outputs': 40, 'raw_gate_counts': gates,
        'short_families': [{'id': row['id'], 'batch': row['batch'], 'short_blocks': row['short_blocks']}
                           for row in rows if row['short_blocks']],
        'numeric_scope': 'Eight massive Euclidean N2/N3 rank0/1 batch1/32 families. Controls cover Float/DD and dynamic f64 Dual first-order/primal only; static/higher/mixed Dual and precision/Dual performance are not newly qualified.',
        'cohort_scope': 'Pinned2c1f334 private generic-Symbolica scheduler experiment, inherited frozen optimized lower feature context; not latest production/default/native-master performance.',
        'build_original_failure_preserved': ref(BASE / 'fresh-build-001/build.json'),
        'build_merged': ref(merged),
        'independent_build': ref(BASE / 'independent-build-audit/audit-001/admission.json'),
        'independent_captured': ref(BASE / 'independent-captured-audit/audit-001/admission.json'),
        'independent_uncaptured': ref(BASE / 'independent-uncaptured-audit/audit-001/admission.json'),
        'independent_preflight': ref(BASE / 'independent-preflight-audit/audit-001/admission.json'),
        'independent_timing': ref(BASE / 'independent-timing-audit/audit-001/admission.json'),
        'context_adjudication': ref(BASE / 'context-adjudication-fresh2c1-001.json'),
        'frozen_receipts': {key: ref(path) for key, path in receipts.items()},
    }
    write(HERE / 'qualification.json', qualification)
    write(HERE / 'source-parentage.json', {
        'pinned_source_revision': PIN, 'cohort': qualification['cohort_scope'],
        'compilation_source_snapshot_files': 293,
        'source_archive': 'source-snapshot.tar.gz',
        'source_archive_members': 'source-snapshot.tar.gz.members.json',
        'live_origins_are_not_active_compilation_inputs': True,
        'pinned_origin_context': ref(BASE / 'v3/pinned-origin-context.json'),
        'parent_capsules': ['validation/uniform-branch-scheduler', 'validation/uniform-branch-dependent'],
        'lower_context': 'target/benchmark/dependency-closures/6b24c03-complete-kinds',
        'lower_context_limit': 'Numerica49/Graphica7 source files equal pinned sources; inherited broader historical serde/bincode/serde_json features remain. This is not claimed as exact latest Cargo feature configuration.',
        'profile': 'opt-level3,cgu16,embed-bitcode; debug/overflow checks off; final probes ThinLTO',
        'thinlto_map_limit': 'Original receipt remains failed for invalid literal upstream rlib-path criterion; five successful compiler products reused, nine compiled in independently reviewed v3. Actual metadata/argv/closed-search guards establish linkage. Maps show transformed native link only.',
        'original_failure': ref(BASE / 'fresh-build-001/build.json'),
        'continuation': ref(BASE / 'v3/build-001/build.json'),
        'merged_admission': ref(merged),
        'symbolica_patch_applied_to_production': False,
        'default_policy_changed_by_this_capsule': False,
    })
    omitted = {}
    def external(path, wanted, reason):
        path = Path(path) if Path(path).is_absolute() else ROOT / path
        key = str(path)
        if key in omitted:
            assert omitted[key]['sha256'] == wanted
        else:
            omitted[key] = {'path': key, 'sha256': wanted, 'bytes': path.stat().st_size if path.exists() else None,
                            'status': 'not copied; recorded source/artifact binding, verified in saved independent audits',
                            'reason': reason}
    for raw, wanted in v3['protected_sha256'].items():
        if Path(raw).suffix in {'.rlib', '.rmeta', '.so', '.a', '.o'}:
            external(raw, wanted, 'Compiled lower dependency/system artifact omitted')
    for value in build['outputs'].values():
        external(value['path'], value['sha256'], 'Fresh matched compiled product omitted')
    for raw, wanted in v3['tool_sha256'].items():
        external(raw, wanted, 'Tool executable omitted')
    for receipt_path in receipts.values():
        for value in read(receipt_path)['executed_executables'].values():
            external(value['path'], value['sha256'], 'Frozen runtime executable copy omitted')
    write(HERE / 'external-artifacts.json', {
        'scope': 'No compiled executable, object, rlib/rmeta or dependency binary archive is copied. Original immutable receipts retain absolute paths and hashes; this capsule honestly does not claim a self-contained offline compiler build.',
        'artifacts': sorted(omitted.values(), key=lambda value: value['path']),
    })
    write(HERE / 'payload-origins.json', {'scope': 'All original receipts/scripts remain byte-identical. Absolute private paths inside original records are historical; new qualification/performance links use capsule-relative paths. Archive member inventories give complete saved content hashes.',
                                       'copies': sorted(origins, key=lambda value: value['path'])})
    manifest = {}
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.name != 'manifest.json':
            assert not path.is_symlink()
            manifest[str(path.relative_to(HERE))] = {'sha256': sha(path), 'bytes': path.stat().st_size}
    write(HERE / 'manifest.json', {'schema_version': 1,
        'status': 'sealed-saved-evidence-pending-independent-capsule-review',
        'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': qualification['cohort_scope'], 'acceptance_eligibility': False,
        'files': manifest, 'manifest_exclusion': 'manifest.json self hash only; independent review lives beside capsule',
        'compiled_binaries_included': False, 'new_integral_or_timing_run_performed_by_packaging': False,
    })
    print(json.dumps({'status': 'sealed', 'files': len(manifest), 'manifest_sha256': sha(HERE / 'manifest.json'),
                      'bytes': sum(value['bytes'] for value in manifest.values()),
                      'acceptance_eligibility': False, 'new_numerical_execution': False}))


if __name__ == '__main__':
    main()
