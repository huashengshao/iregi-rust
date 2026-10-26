"""Replay saved optional-zero-profile source/build/focused-test evidence only."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import io
import json
import re
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = '/shared/external/iregi/iregi-rust/'
RAW = 'target/e6-dual-optional-zero-profile-qualification'
BUILD = RAW + '/build-001'
NEW_TEST = 'execution::quadrature_context_tests::e6_dual_zero_profiles_are_optional_and_generic_contexts_stay_coupled'


def need(value, why):
    if not value:
        raise ValueError(why)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {'sha256': sha(body), 'bytes': len(body)}


def load(body):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(body, object_pairs_hook=pairs)


def safe(name):
    path = PurePosixPath(name)
    need(name and str(path) == name and not path.is_absolute() and '..' not in path.parts,
         'safe relative alias')


def unpack(body, selected, complete=False):
    result = {}
    seen = set()
    with tarfile.open(fileobj=io.BytesIO(body), mode='r:gz') as archive:
        for item in archive:
            safe(item.name)
            need(item.isfile() and item.name not in seen, 'unique regular archive member')
            seen.add(item.name)
            if item.name in selected:
                data = archive.extractfile(item).read()
                need(desc(data) == selected[item.name], 'selected archive member identity')
                need(not data.startswith((b'\x7fELF', b'!<arch>')) and b'S-130-' not in data,
                     'source/text payload only')
                result[item.name] = data
    need(set(result) == set(selected), 'every selected member present')
    if complete:
        need(seen == set(selected), 'closed own archive inventory')
    return result


def restore_files(manifest):
    own = set(manifest['capsule_files']) | {'manifest.json'}
    need({str(p.relative_to(HERE)) for p in HERE.rglob('*')
          if p.is_file() and '__pycache__' not in p.parts} == own, 'closed own inventory')
    for name, row in manifest['capsule_files'].items():
        safe(name)
        need(desc((HERE / name).read_bytes()) == row, 'own file identity')
    for name, row in manifest['parent_files'].items():
        safe(name)
        need(desc((ROOT / name).read_bytes()) == row, 'shallow parent file identity')
    archives = {}
    for name, row in manifest['direct_archives'].items():
        need(manifest['parent_files'][name] == {k: row[k] for k in ['sha256', 'bytes']},
             'direct archive identity is pinned')
        archives[name] = unpack((ROOT / name).read_bytes(), row['members'])
    delta = unpack((HERE / 'payload.tar.gz').read_bytes(), manifest['payload_members'], complete=True)
    result = {}
    for alias, row in manifest['aliases'].items():
        safe(alias)
        if 'archive' in row:
            need('member' in row and row['archive'] in archives, 'one borrowed body locator')
            body = archives[row['archive']][row['member']]
        else:
            body = delta[row['member']]
        need(desc(body) == {k: row[k] for k in ['sha256', 'bytes']}, 'saved alias identity')
        result[alias] = body
    return result


def replay(manifest, files):
    def read(alias):
        return load(files[alias])

    source_map = manifest['compiled_sources']
    need(len(source_map) == 210, 'actual selected source count')
    for canonical, row in source_map.items():
        need(row['snapshot_alias'] == BUILD + '/source-snapshot/' + canonical,
             'actual immutable source snapshot alias')
        need(desc(files[canonical]) == desc(files[row['snapshot_alias']])
             == {k: row[k] for k in ['sha256', 'bytes']}, 'compiled selected source bytes')

    checked_inputs = checked_outputs = 0
    omitted = manifest['omitted_native_artifacts']

    def phase(name):
        nonlocal checked_inputs, checked_outputs
        base = RAW + '/' + name
        receipt = read(base + '/receipt.json')
        need(receipt['inputs_unchanged'] is True and receipt['cleanup_errors'] == [],
             'terminal input guards and cleanup ' + name)
        need(receipt.get('sources', receipt.get('source_files')) ==
             {p: row['sha256'] for p, row in source_map.items()}, 'same actual source map ' + name)
        for absolute, digest in receipt['inputs'].items():
            if absolute in omitted:
                need(omitted[absolute] == digest, 'historical native product hash')
                continue
            need(absolute.startswith(PREFIX), 'project guarded input')
            alias = absolute[len(PREFIX):]
            if alias in source_map:
                alias = source_map[alias]['snapshot_alias']
            need(alias in files and sha(files[alias]) == digest, 'guarded input ' + alias)
            checked_inputs += 1
        for name, digest in receipt['outputs'].items():
            alias = base + '/' + name
            if PREFIX + alias in omitted:
                need(omitted[PREFIX + alias] == digest, 'historical native output hash')
                continue
            need(alias in files and sha(files[alias]) == digest, 'saved output ' + alias)
            checked_outputs += 1
        for step in receipt['steps']:
            need(step['owned_group_gone'] is True, 'owned process group cleaned')
        return receipt

    built = phase('build-001')
    need(built['status'] == 'passed_fresh_core_libtest_build_and_freeze'
         and len(built['steps']) == 1, 'one passed actual fresh libtest build')
    need(built['steps'][0]['returncode'] == 0 and built['steps'][0]['status'] == 'exited',
         'actual Cargo build terminal')
    need(built['source_context_is_complete_dependency_closure'] is False,
         'selected source scope remains explicit')
    product = built['products']['tests']
    need(omitted[product['path']] == product['sha256'] == manifest['frozen_libtest_sha256'],
         'actual frozen libtest identity')
    event = read(BUILD + '/' + product['cargo_event'])
    need(event['reason'] == 'compiler-artifact' and event['executable'] == product['cargo_executable']
         and event['target']['name'] == 'iregi_rust' and event['profile']['test'] is True,
         'actual product Cargo event')
    events = []
    for line in files[BUILD + '/cargo-core.log'].splitlines():
        try:
            events.append(load(line))
        except (ValueError, UnicodeDecodeError):
            pass
    need([event['success'] for event in events if event.get('reason') == 'build-finished'] == [True],
         'saved successful Cargo completion')
    freeze = read(RAW + '/source-freeze.json')
    need(freeze['sources'] == built['sources'] and freeze['source_count'] == 210
         and freeze['full_dependency_closure_claimed'] is False, 'actual source freeze')
    for path, digest in freeze['inputs'].items():
        need(path.startswith(PREFIX) and sha(files[path[len(PREFIX):]]) == digest,
             'source freeze selected input guard')

    initial = phase('focused-001')
    final = phase('focused-new-regression-001')
    selected = manifest['focused_test_names']
    need(initial['status'] == 'failed_or_incomplete' and initial['selected_tests'] == selected
         and len(selected) == len(set(selected)) == 24, 'preserved initial selected24 scope')
    need(initial['passed_tests'] == selected[:-1] and initial['unrun_tests'] == [NEW_TEST]
         and selected[-1] == NEW_TEST, '23 prior passes and original incomplete test')
    need(len(initial['steps']) == 25 and len(final['steps']) == 2, 'actual listing and child counts')
    timeout = initial['steps'][-1]
    need(timeout['timeout_seconds'] == 60 and timeout['timeout'] is True
         and timeout['returncode'] == -15 and timeout['status'] == 'failed', 'original 60-second timeout retained')
    need(final['status'] == 'passed_one_new_regression_and_combined24_current_source'
         and final['selected_tests'] == final['passed_tests'] == [NEW_TEST]
         and final['unrun_tests'] == [] and final['combined_distinct_passes'] == selected,
         'later one-test pass gives 24 distinct current-source tests')
    prior = final['prior_23_pass_receipt']
    need(prior['path'] == PREFIX + RAW + '/focused-001/receipt.json'
         and prior['sha256'] == sha(files[RAW + '/focused-001/receipt.json']), 'actual prior receipt linkage')
    for receipt, dirname, names in [(initial, 'focused-001', selected[:-1]),
                                   (final, 'focused-new-regression-001', [NEW_TEST])]:
        need(receipt['new_full_tensor_integrals'] is False and receipt['performance_qualified'] is False,
             'focused scope does not qualify full rank or timing')
        listing = files[RAW + '/' + dirname + '/listing.log'].decode()
        for index, name in enumerate(names):
            step = receipt['steps'][index + 1]
            log = files[RAW + '/' + dirname + '/test-' + str(index) + '.log'].decode()
            need(step['status'] == 'exited' and step['returncode'] == 0
                 and step['command'][-4:] == ['--exact', name, '--nocapture', '--test-threads=1'],
                 'actual exact test command ' + name)
            need(name + ': test' in listing and re.findall(r'^running .*$', log, re.M) == ['running 1 test']
                 and 'test ' + name + ' ... ok' in log, 'one actual named test in saved log')
            need(re.findall(r'^test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; '
                            r'502 filtered out; finished in [0-9.]+s$', log, re.M),
                 'one strict successful saved test summary')
    failed_log = files[RAW + '/focused-001/test-23.log']
    need(NEW_TEST.encode() in failed_log and b'test result:' not in failed_log,
         'initial timeout has no fabricated test completion')

    execution = files['crates/iregi-rust/src/execution.rs']
    need(b'if self.components > 1 && self.quadrature.is_some() {' in execution
         and b'exact-zero profile specialization skipped for full-component quadrature; ordinary reduction retained' in execution,
         'actual narrow optional profile condition and lane diagnostic')
    need(b'ordinary.extend(compact_lanes);' in execution, 'retained ordinary recipe')
    regression = files['crates/iregi-rust/src/execution/quadrature_context_tests.rs']
    need(NEW_TEST.rsplit('::', 1)[-1].encode() in regression, 'actual compiled new regression source')
    need('execution::tests::failed_optional_zero_profile_rejoins_ordinary_batch_in_original_order' in selected,
         'existing optional retry regression is retained')
    need(sha(files[manifest['source_proof_alias']]) == manifest['source_proof_sha256'], 'source proof identity')

    failures = []
    for item in manifest['preserved_prior_failures']:
        receipt = read(item['receipt_alias'])
        need(sha(files[item['receipt_alias']]) == item['sha256'], 'historical failure receipt identity')
        need(receipt['status'] == 'failed_capture_retained' and receipt['inputs_unchanged'] is True
             and receipt['cleanup_errors'] == [] and receipt['steps'][-1]['returncode'] == -6
             and receipt['steps'][-1]['owned_group_gone'] is True, 'actual preserved terminal allocation failure')
        for alias, row in item['saved_files'].items():
            need(desc(files[alias]) == row, 'historical failure selected log identity')
        base = item['receipt_alias'].rsplit('/', 1)[0]
        for name in ['native.log', 'capture.json']:
            need(sha(files[base + '/' + name]) == receipt['outputs'][name], 'historical failure output guard')
        need(read(base + '/capture.json')['calls'] == [], 'old failed capture produced no tensor arrays')
        failures.append({'label': item['label'], 'receipt_sha256': item['sha256'],
                         'saved_status': receipt.get('status'), 'scope': 'historical terminal receipt and selected logs only'})
    correction = read(manifest['diagnosis_correction_alias'])
    for alias, digest in correction['preserved_prior_hashes'].items():
        need(sha(files[alias]) == digest, 'additive correction retains prior diagnosis bytes')
    sequence = read(manifest['stage_sequence_alias'])
    need(sequence['no_native_evaluation'] is True and len(sequence['logs']) == 3,
         'saved-only Hybrid64/PV128/PV256 sequence scope')
    for item in sequence['logs']:
        body = files[item['path']]
        need(sha(body) == item['sha256'], 'stage-sequence log binding')
        lines = body.decode().splitlines()
        for event in item['events']:
            need(lines[event['line'] - 1] == event['text'], 'exact saved stage line')
        end = next(e['line'] for e in item['events'] if e['text'].startswith('PV prepare end affine-power N5'))
        second = next(e['line'] for e in item['events'] if 'reachability 0/12318 aliases' in e['text'])
        need(end < second, 'generic child completes before second optional-profile pass')
    return {'status': 'passed_saved_optional_zero_profile_core_tests_replay',
            'actual_build_receipt_sha256': sha(files[BUILD + '/receipt.json']),
            'frozen_libtest_sha256': product['sha256'], 'selected_source_bodies': 210,
            'direct_borrowed_source_bodies': 205, 'own_new_snapshot_source_bodies': 5,
            'checked_nonbinary_inputs': checked_inputs, 'checked_nonbinary_outputs': checked_outputs,
            'focused_distinct_tests_passed': 24, 'focused_test_names': selected,
            'initial_passes': 23, 'initial_new_test_timeout_retained': True,
            'initial_new_test_timeout_seconds': timeout['elapsed_seconds'],
            'additive_new_test_native_seconds': final['steps'][-1]['elapsed_seconds'],
            'additive_new_test_total_seconds': final['elapsed_seconds'],
            'preserved_prior_failures': failures, 'full_rank6_dual_qualified': False,
            'complete_dependency_closure_claimed': False, 'new_integral_evaluation': False,
            'native_execution': False, 'native_artifact_rehash': False,
            'performance_qualified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output')
    args = parser.parse_args()
    manifest = load((HERE / 'manifest.json').read_bytes())
    result = replay(manifest, restore_files(manifest))
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
