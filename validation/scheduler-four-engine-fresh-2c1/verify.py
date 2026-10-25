"""Portable saved-payload verification; no compiler, integral or benchmark runs."""
from pathlib import Path
import collections
import hashlib
import itertools
import json
import math
import random
import statistics
import sys
import tarfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main():
    manifest = read(HERE / 'manifest.json')
    actual = {str(path.relative_to(HERE)) for path in HERE.rglob('*')
              if path.is_file() and '__pycache__' not in path.parts and path.name != 'manifest.json'}
    assert actual == set(manifest['files'])
    for relative, record in manifest['files'].items():
        path = HERE / relative
        assert not path.is_symlink() and path.stat().st_size == record['bytes']
        assert sha(path) == record['sha256'], relative
        assert path.suffix not in {'.rlib', '.rmeta', '.so', '.a', '.o', '.exe'}
    qualification = read(HERE / 'qualification.json')
    performance = read(HERE / 'performance.json')
    assert qualification['pinned_source_revision'] == '2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2'
    for key in ['matched_optimized_build_passed', 'captured_qualified', 'uncaptured_qualified',
                'preflight_qualified', 'numerical_qualified', 'saved_timing_arithmetic_qualified']:
        assert qualification[key] is True
    for key in ['performance_qualified', 'acceptance_eligibility', 'uncontended_parity_qualified',
                'production_adoption_authorized']:
        assert qualification[key] is False
    assert performance['raw_arithmetic_admitted'] is True
    assert performance['acceptance_eligibility'] is performance['production_adoption_authorized'] is False
    assert qualification['matched_optimized_build_products'] == 14
    original_build = read(HERE / qualification['build_original_failure_preserved']['path'])
    merged_build = read(HERE / qualification['build_merged']['path'])
    assert original_build['status'] == 'failed' and 'symbolica archive contamination' in json.dumps(original_build)
    assert merged_build['status'] == 'passed' and merged_build['success'] is True
    assert len(merged_build['steps']) == 14 and all(step['status'] == 'passed' for step in merged_build['steps'])
    expected_gates = {'regression': 12, 'inconclusive-noise': 16, 'improvement': 2,
                      'inconclusive-short-block': 10}
    assert performance['raw_gate_counts'] == qualification['raw_gate_counts'] == expected_gates

    def links(value):
        if isinstance(value, dict):
            if set(value) == {'path', 'sha256'}:
                assert not Path(value['path']).is_absolute() and '..' not in Path(value['path']).parts
                assert sha(HERE / value['path']) == value['sha256']
            else:
                for child in value.values():
                    links(child)
        elif isinstance(value, list):
            for child in value:
                links(child)
    links(qualification)
    links(performance)
    links(read(HERE / 'source-parentage.json'))
    base = 'evidence/fresh-four-engine-proposal/'
    timing = read(HERE / (base + 'timing-fresh2c1-001/receipt.json'))
    summary = read(HERE / (base + 'timing-fresh2c1-001/summary.json'))
    context = read(HERE / 'evidence/context-adjudication-fresh2c1-001.json')
    assert context['acceptance_eligibility'] is False and context['production_adoption_authorized'] is False
    assert timing['status'] == 'completed-with-inconclusive-rows' and timing['global_lifecycle_clean'] is True
    assert summary['global_admission_errors'] == []
    assert len(timing['process_terminals']) == 6
    assert all(item['returncode'] == 0 and item['owned_group_gone'] is True
               for item in timing['process_terminals'])

    raw_counts = {}
    timing_request_index = {}
    archive_member_counts = {}
    for name in ['numerical-records.tar.gz', 'link-maps.tar.gz',
                 'source-snapshot.tar.gz', 'provenance-metadata.tar.gz']:
        inventory = read(HERE / (name + '.members.json'))
        assert inventory['sha256'] == sha(HERE / name)
        expected = {item['path']: item for item in inventory['members']}
        observed = set()
        with tarfile.open(HERE / name, 'r:gz') as tar:
            for member in tar:
                assert member.isfile() and not member.issym() and not member.islnk()
                assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
                assert Path(member.name).suffix not in {'.rlib', '.rmeta', '.so', '.a', '.o', '.exe'}
                assert member.name in expected and member.name not in observed
                record = expected[member.name]
                assert member.size == record['bytes']
                stream = tar.extractfile(member)
                digest = hashlib.sha256()
                if member.name.endswith('.jsonl'):
                    count = requests = 0
                    last = None
                    stages = collections.Counter()
                    for line in stream:
                        digest.update(line)
                        entry = json.loads(line)
                        count += 1
                        if count % 2:
                            requests += 1
                            assert entry['event'] == 'request' and entry['serial'] == requests
                            last = entry
                            stages[entry['stage']] += 1
                            if '/timing-fresh2c1-001/' in member.name:
                                timing_request_index[requests] = entry
                        else:
                            assert entry['event'] == 'response' and entry['serial'] == requests
                            assert {key: value for key, value in entry.items() if key not in ['event', 'response']} == {
                                key: value for key, value in last.items() if key != 'event'}
                    assert count == requests * 2
                    raw_counts[member.name] = {'events': count, 'requests': requests, 'sha256': digest.hexdigest(),
                                               'stages': dict(stages)}
                else:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(chunk)
                assert digest.hexdigest() == record['sha256'], member.name
                observed.add(member.name)
        assert observed == set(expected)
        archive_member_counts[name] = len(observed)
    assert archive_member_counts['link-maps.tar.gz'] == 4
    assert archive_member_counts['source-snapshot.tar.gz'] == 293
    expected_raw = {
        'evidence/fresh-captured-runtime/qualification-001/responses.jsonl': (60, 120),
        'evidence/fresh-uncaptured-proposal/qualification-001/responses.jsonl': (60, 120),
        base + 'preflight-fresh2c1-001/raw.jsonl': (168, 336),
        base + 'timing-fresh2c1-001/raw.jsonl': (1768, 3536),
    }
    assert set(raw_counts) == set(expected_raw)
    for name, counts in expected_raw.items():
        assert (raw_counts[name]['requests'], raw_counts[name]['events']) == counts
    for stage, raw_name in zip(['captured', 'uncaptured', 'preflight', 'timing'], expected_raw):
        stage_receipt = read(HERE / qualification['frozen_receipts'][stage]['path'])
        assert raw_counts[raw_name]['sha256'] == stage_receipt['raw_sha256']
    timing_raw = raw_counts[base + 'timing-fresh2c1-001/raw.jsonl']
    assert timing_raw['sha256'] == timing['raw_sha256']
    assert timing_raw['stages']['acceptance'] == 1536 and timing_raw['stages']['calibration'] == 64
    numerical = read(HERE / 'numerical-records.tar.gz.members.json')
    indexed = {item['path']: item for item in numerical['members']}
    for stream in ['stdout', 'stderr']:
        assert set(timing[stream + '_sha256']) == {item['label'] for item in timing['process_terminals']}
        for label, wanted in timing[stream + '_sha256'].items():
            assert indexed[base + 'timing-fresh2c1-001/' + label + '.' + stream + '.log']['sha256'] == wanted

    ratios = read(HERE / 'ratio-table.json')
    assert len(ratios) == 40 and dict(collections.Counter(row['gate'] for row in ratios)) == expected_gates
    for row in ratios:
        assert row['numerator'] in ['baselineTIRust', 'candidateTIRust'] and row['quartets'] == 48
        assert row['median'] > 0 and all(math.isfinite(value) and value > 0 for value in row['ci99'])
    quartet_rows = read(HERE / 'quartets.json')
    assert len(quartet_rows) == len(performance['rows']) == len(timing['rows']) == 8
    engines = ['baselineTIRust', 'candidateTIRust', 'iregi', 'collier']
    orders = list(itertools.permutations(engines)) * 2
    random.Random(173).shuffle(orders)
    accepted_serials = set()
    for row, report, original, saved_summary in zip(quartet_rows, performance['rows'], timing['rows'], summary['rows']):
        assert row['id'] == report['id'] == original['id'] == saved_summary['id']
        assert row['batch'] == report['batch'] == original['outer_batch'] == saved_summary['batch']
        assert row['blocks'] == original['blocks'] and row['calibration'] == original['calibration']
        assert len(row['blocks']) == 48
        short = 0
        for index, block in enumerate(row['blocks']):
            assert block['index'] == index and block['order'] == list(orders[index])
            assert [value['engine'] for value in block['engines']] == list(orders[index])
            for value in block['engines']:
                serial = value['raw_serial']
                assert serial not in accepted_serials
                accepted_serials.add(serial)
                request = timing_request_index[serial]
                assert request['stage'] == 'acceptance' and request['engine'] == value['engine']
                assert request['id'] == row['id'] and request['batch'] == row['batch']
                assert request['block'] == index and request['iterations'] == value['iterations'] == row['iterations']
                short += value['elapsed_ns'] < 100_000_000
        assert short == report['short_blocks'] == saved_summary['short_blocks']
        assert report['acceptance_eligibility'] is False
        for engine, values in saved_summary['engine_samples_ns'].items():
            assert len(values) == 48
            median = statistics.median(values)
            assert report['median_ns_per_complete_batch_call'][engine] == median
            assert report['ns_per_sample_from_median_batch_call'][engine] == median / row['batch']
        selected = [value for value in ratios if value['id'] == row['id'] and value['batch'] == row['batch']]
        assert report['raw_ratios'] == selected and len(selected) == 5
    assert len(accepted_serials) == 1536
    assert sum(len(row['blocks']) for row in quartet_rows) == 384
    assert qualification['short_families'] == [
        {'id': 'n2-r1-massive', 'batch': 32, 'short_blocks': 1},
        {'id': 'n3-r0-massive', 'batch': 32, 'short_blocks': 50},
    ]
    print(json.dumps({'status': 'passed-portable-saved-evidence-verification',
                      'files': len(actual), 'archive_members': archive_member_counts,
                      'timing_requests': 1768, 'timing_events': 3536, 'quartets': 384,
                      'ratios': 40, 'acceptance_eligibility': False,
                      'scope': 'Payload/raw accounting and derived-table integrity; original independent numerical/statistical audits are retained. No compiler/integral/timing execution.'}))


if __name__ == '__main__':
    main()
