"""Replay restored zero-profile source/build/focused-test evidence, without native execution."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = 'validation/e6-dual-postfix-nonfinite-boundaries'
PREFIX = '/shared/external/iregi/iregi-rust/'
EXECUTION = 'crates/iregi-rust/src/execution.rs'
TEST_SOURCE = 'crates/iregi-rust/src/execution/quadrature_context_tests.rs'
NEW_TEST = 'execution::quadrature_context_tests::e6_dual_exact_zero_profiles_require_full_taylor_zeros_and_keep_owned_contexts'


def need(value, message):
    if not value:
        raise ValueError(message)


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


def restore_files(manifest):
    need({str(p.relative_to(HERE)) for p in HERE.rglob('*')
          if p.is_file() and '__pycache__' not in p.parts} == set(manifest['capsule_files']) | {'manifest.json'},
         'closed own capsule inventory')
    for name, row in manifest['capsule_files'].items():
        need(desc((HERE / name).read_bytes()) == row, 'own file identity')
    for name, row in manifest['parent_files'].items():
        need(desc((ROOT / name).read_bytes()) == row, 'immutable parent file identity')
    parent_body = (ROOT / PARENT / 'manifest.json').read_bytes()
    need(sha(parent_body) == manifest['parent_manifest_sha256'], 'actual historical failure/source parent')
    parent = runpy.run_path(str(ROOT / PARENT / 'check.py'), run_name='saved_nonfinite_parent_loader')
    inherited = parent['restore_files'](load(parent_body))
    # Use the already hash-pinned source-parent archive utility; no parent math checker runs.
    resource = runpy.run_path(str(ROOT / 'validation/e6-dual-postfix-resource-boundaries/check.py'),
                             run_name='saved_archive_reader')
    own = resource['unpack']((HERE / 'payload.tar.gz').read_bytes(), manifest['payload_members'], complete=True)
    files = dict(inherited)
    for alias, row in manifest['aliases'].items():
        resource['safe'](alias)
        body = inherited[row['parent_alias']] if 'parent_alias' in row else own[row['member']]
        need(desc(body) == {k: row[k] for k in ['sha256', 'bytes']}, 'saved selected body')
        need(alias not in files or files[alias] == body, 'phase aliases do not overwrite historical canonical sources')
        files[alias] = body
    return files


def replay(manifest, files):
    def read(alias):
        return load(files[alias])

    omitted = manifest['omitted_native_artifacts']
    checked_inputs = checked_outputs = owned_groups = 0
    builds = {}
    for build_alias, context in manifest['compiled_sources'].items():
        receipt = read(build_alias)
        need(len(context) == len(receipt['sources']) == 210, 'actual selected source count')
        for canonical, row in context.items():
            need(row['snapshot_alias'] == build_alias.rsplit('/', 1)[0] + '/source-snapshot/' + canonical,
                 'actual phase-specific compiled snapshot alias')
            need(desc(files[row['snapshot_alias']]) == {k: row[k] for k in ['sha256', 'bytes']}
                 and receipt['sources'][canonical] == row['sha256'], 'actual build selected source body')
        builds[build_alias] = receipt

    def phase(alias, build_alias):
        nonlocal checked_inputs, checked_outputs, owned_groups
        receipt = read(alias)
        base = alias.rsplit('/', 1)[0]
        context = manifest['compiled_sources'][build_alias]
        need(receipt['inputs_unchanged'] is True and receipt['cleanup_errors'] == [],
             'actual terminal input guards and cleanup')
        source_map = receipt.get('sources', receipt.get('source_files'))
        need(source_map == {p: row['sha256'] for p, row in context.items()}, 'actual source context for phase')
        for absolute, digest in receipt['inputs'].items():
            if absolute in omitted:
                need(omitted[absolute] == digest, 'omitted historical native artifact identity')
                continue
            need(absolute.startswith(PREFIX), 'project-local guarded input')
            selected = absolute[len(PREFIX):]
            if selected in context:
                selected = context[selected]['snapshot_alias']
            need(selected in files and sha(files[selected]) == digest, 'actual phase-specific source/input guard')
            checked_inputs += 1
        for name, digest in receipt['outputs'].items():
            selected = base + '/' + name
            if PREFIX + selected in omitted:
                need(omitted[PREFIX + selected] == digest, 'omitted historical native output identity')
            else:
                need(sha(files[selected]) == digest, 'actual saved output identity')
                checked_outputs += 1
        for step in receipt['steps']:
            need(step['owned_group_gone'] is True, 'every actual owned process group cleaned')
            owned_groups += 1
        return receipt

    for alias in builds:
        phase(alias, alias)
        root = alias.rsplit('/build-001/', 1)[0]
        freeze = read(root + '/source-freeze.json')
        need(freeze['sources'] == builds[alias]['sources'] and freeze['full_dependency_closure_claimed'] is False,
             'actual selected source freeze, without full closure claim')
        for absolute, digest in freeze['inputs'].items():
            need(absolute.startswith(PREFIX) and sha(files[absolute[len(PREFIX):]]) == digest,
                 'source-freeze immutable controller/history input')

    old_timeout = builds[manifest['build_roles']['old_timeout']]
    old_cancel = builds[manifest['build_roles']['old_cancel']]
    need(old_timeout['status'] == old_cancel['status'] == 'failed_or_incomplete'
         and old_timeout['products'] == old_cancel['products'] == {}, 'old failed compiles never became products')
    need(old_timeout['steps'][0]['timeout'] is True and old_timeout['steps'][0]['timeout_seconds'] == 780
         and old_timeout['steps'][0]['returncode'] == -15, 'original 780-second compile timeout')
    need(old_cancel['steps'][0]['returncode'] == -15
         and 'cancelled by signal 15' in old_cancel['steps'][0]['cancellation'], 'separate root-authorized cancellation')
    stopped = read('target/e6-dual-release-qualification-2400/root-authorized-stop.json')
    need(stopped['all_pre_stop_guards_unchanged'] is True
         and stopped['native_owned_group'] == old_cancel['steps'][0]['kernel_start_identity'],
         'root-authorized stop binds the actual cancelled group')

    prior_alias = manifest['build_roles']['prior_restored']
    current_alias = manifest['build_roles']['current']
    for alias in [prior_alias, current_alias]:
        built = builds[alias]
        need(built['status'] == 'passed_fresh_core_libtest_build_and_freeze'
             and len(built['steps']) == 1 and built['steps'][0]['status'] == 'exited'
             and built['steps'][0]['returncode'] == 0, 'actual successful restored-source build')
        product = built['products']['tests']
        base = alias.rsplit('/', 1)[0]
        event = read(base + '/' + product['cargo_event'])
        need(event['reason'] == 'compiler-artifact' and event['target']['name'] == 'iregi_rust'
             and event['executable'] == product['cargo_executable']
             and event['profile'] == built['actual_cargo_profile'] == manifest['actual_cargo_profile'],
             'actual opt3/test Cargo artifact profile')
        need(omitted[product['path']] == product['sha256'], 'actual frozen product historical hash')
        events = []
        for line in files[base + '/cargo-core.log'].splitlines():
            try:
                events.append(load(line))
            except (ValueError, UnicodeDecodeError):
                pass
        need([row['success'] for row in events if row.get('reason') == 'build-finished'] == [True],
             'actual saved Cargo success event')

    prior = phase(manifest['prior_focused_receipt_alias'], prior_alias)
    current = phase(manifest['current_focused_receipt_alias'], current_alias)
    tests = manifest['focused_test_names']
    need(len(tests) == len(set(tests)) == 24 and tests[-1] == NEW_TEST,
         'exact current24 test identities')
    need(prior['status'] == 'failed_or_incomplete' and prior['selected_tests'] == tests
         and prior['passed_tests'] == tests[:-1] and prior['unrun_tests'] == [NEW_TEST]
         and prior['steps'][-1]['returncode'] == 101, 'original23 passes and failed overoptimistic regression retained')
    need(current['status'] == 'passed_24_focused_current_source_regressions'
         and current['selected_tests'] == current['passed_tests'] == tests and current['unrun_tests'] == []
         and len(current['steps']) == 25, 'actual listing plus all24 current tests passed')
    for receipt, alias, names in [(prior, manifest['prior_focused_receipt_alias'], tests[:-1]),
                                 (current, manifest['current_focused_receipt_alias'], tests)]:
        base = alias.rsplit('/', 1)[0]
        listing = files[base + '/listing.log'].decode()
        need(receipt['steps'][0]['returncode'] == 0 and receipt['new_full_tensor_integrals'] is False
             and receipt['performance_qualified'] is False, 'listing and focused scope only')
        for index, name in enumerate(names):
            step = receipt['steps'][index + 1]
            log = files[base + '/test-' + str(index) + '.log'].decode()
            need(step['command'][-4:] == ['--exact', name, '--nocapture', '--test-threads=1']
                 and step['status'] == 'exited' and step['returncode'] == 0 and name + ': test' in listing,
                 'actual exact owned test selector')
            need(re.findall(r'^running .*$', log, re.M) == ['running 1 test']
                 and 'test ' + name + ' ... ok' in log
                 and re.findall(r'^test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; '
                                r'502 filtered out; finished in [0-9.]+s$', log, re.M),
                 'one actual successful saved test summary')
    failed_log = files[manifest['prior_focused_receipt_alias'].rsplit('/', 1)[0] + '/test-23.log']
    need(b'left: [Success, Success, Unstable(' in failed_log
         and b'E6 leaf 0: NonConvergent (quadrature order 128' in failed_log
         and b'right: [Success, Success, Success]' in failed_log
         and b'test result: FAILED. 0 passed; 1 failed;' in failed_log,
         'original third-lane refusal and failed all-three-success expectation preserved')

    def source(alias, canonical):
        return files[manifest['compiled_sources'][alias][canonical]['snapshot_alias']]

    old = files[EXECUTION]
    restored = source(current_alias, EXECUTION)
    start = old.index(b'                // This specialization is optional: preparation/evaluation\n')
    end = old.index(b'                if !self.zero_profiles.contains_key(&profile) {', start)
    need(old[start:end].count(b'\n') == 15 and old[:start] + old[end:] == restored
         and restored == source(prior_alias, EXECUTION), 'exact15-line bypass removal; rest of execution source unchanged')
    changed = [name for name, row in manifest['compiled_sources'][prior_alias].items()
               if row['sha256'] != manifest['compiled_sources'][current_alias][name]['sha256']]
    need(changed == [TEST_SOURCE], 'only cfg-test body changes between restored builds')
    corrected = source(current_alias, TEST_SOURCE)
    need(b'for lane in 0..2 {' in corrected
         and b'actual.result().lane(2).is_err()' in corrected
         and b'actual.origin(2, 53, 53).is_err()' in corrected
         and b'actual.errors(2, 53, 53).is_err()' in corrected
         and b'actual.result().validated_primal_envelope(2, 53, 53).is_err()' in corrected
         and b'actual.result().analytic_used, [true, false, false]' in corrected
         and b'reason.contains("E6 leaf 0: NonConvergent")' in corrected
         and b'reason.contains("quadrature order 128")' in corrected,
         'corrected test preserves complete successful neighbors and honest third-lane refusal')
    return {'status': 'passed_saved_restored_zero_profile_core_test_evidence_replay',
            'current_build_receipt_sha256': sha(files[current_alias]),
            'current_frozen_libtest_sha256': builds[current_alias]['products']['tests']['sha256'],
            'current_focused_receipt_sha256': sha(files[manifest['current_focused_receipt_alias']]),
            'current_focused_distinct_tests_passed': 24, 'current_focused_owned_groups': 25,
            'current_focused_seconds': current['elapsed_seconds'],
            'current_regression_native_seconds': current['steps'][-1]['elapsed_seconds'],
            'selected_sources_per_build': 210, 'source_contexts_preserved': 4,
            'checked_nonbinary_inputs': checked_inputs, 'checked_nonbinary_outputs': checked_outputs,
            'all_preserved_owned_groups_cleaned': owned_groups,
            'restored_production_removed_lines': 15,
            'production_execution_identical_between_restored_builds': True,
            'prior_restored_passes': 23, 'prior_restored_failed_regression_preserved': True,
            'third_lane_E6_nonconvergence_remains_expected': True,
            'old_780_compile_timeout_preserved': True, 'old_authorized_compile_cancel_preserved': True,
            'actual_cargo_profile': manifest['actual_cargo_profile'],
            'compiler_profile_numeric_equivalence_claimed': False,
            'historical_canonical_aliases_preserved': True, 'new_source_aliases_are_phase_specific': True,
            'full_rank6_array_qualified': False, 'same_source_precision_convergence_qualified': False,
            'native_execution': False, 'native_artifact_rehash': False,
            'new_integral_evaluation': False, 'performance_qualified': False}


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
