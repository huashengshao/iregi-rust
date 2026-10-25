#!/usr/bin/env python3
"""Portable source reconstruction and saved-evidence checks; no native work."""
from pathlib import Path
import argparse
import json
import math
import re
import sys
sys.dont_write_bytecode = True

from portable import (HISTORICAL_ROOT, NUMERIC, NUMERIC_AUDIT, NUMERIC_AUDIT_SHA, PARENT, PREFIX, allowed, archive,
                      descriptor, digest, document, find_root, load_parent,
                      reconstruct_sources, require, safe, validate_independent_numeric_audit)
from saved_numeric import check_saved

HERE = Path(__file__).resolve().parent
ROOT = find_root(HERE)
DOMAINS = ['Float128Mass0', 'Float256Mass0', 'Float128Scale', 'Float256Scale']
BOUNDS = {'build': [180, 20, 160], 'Float128Mass0': [300, 35, 260],
          'Float256Mass0': [300, 35, 260], 'Float128Scale': [600, 40, 550],
          'Float256Scale': [600, 40, 550], 'saved-gate': [90, 15, 70]}
CODE = ['package.py', 'check.py', 'portable.py', 'saved_numeric.py', 'README.md']


def normalized(name):
    return name.removeprefix(HISTORICAL_ROOT)


def stage(record, count, bounds, groups):
    bound, reserve = bounds[:2]
    require(record['status'] == 'passed' and record['inputs_unchanged'] is True
            and record['cleanup_errors'] == [], 'saved stage failed guard/status/cleanup')
    require(record['bound_seconds'] == bound and record['postwork_reserve_seconds'] == reserve,
            'saved stage budget differs')
    require(type(record['elapsed_seconds']) in [int, float] and math.isfinite(record['elapsed_seconds'])
            and 0 <= record['elapsed_seconds'] <= bound, 'saved stage exceeded bound')
    require(len(record['steps']) == count, 'saved stage process count differs')
    require(not record.get('cancellation') and not record.get('postguard_cancellation'), 'cancelled stage')
    for step in record['steps']:
        group = step['owned_process_group']
        require(type(group) is int and group > 0 and group not in groups
                and step['owned_group_gone'] is True, 'saved owned process group invalid')
        groups.append(group)
        require(step['status'] == 'exited' and step['returncode'] == 0
                and not any(step.get(k) for k in ['error', 'timeout', 'cancellation']), 'saved child did not pass')
        require(0 < step['timeout_seconds'] <= bound - reserve, 'saved child timeout exceeds work budget')


def check_synthetic(files):
    load = lambda name: document(files[PREFIX + '/' + name])
    protocol, build, tests, q = [load(n) for n in ['qualification-protocol.json',
        'build-001/build.json', 'tests-001/tests.json', 'qualification-v3.json']]
    groups = []
    stage(build, 2, [180, 20], groups)
    stage(tests, 20, [180, 20], groups)
    require(build['commands'] == protocol['build_commands'] and tests['commands'] == protocol['test_commands'],
            'synthetic frozen commands differ')
    for step, command in zip(build['steps'], protocol['build_commands']):
        require([step['name'], step['command']] == command, 'synthetic executed build command differs')
        require(digest(files[PREFIX + '/build-001/' + step['name'] + '.log']) == step['log_sha256'],
                'synthetic build log hash differs')
    selected = protocol['selected_tests']
    require(len(selected) == len(set(selected)) == 19, '19 unique selected tests required')
    listing = files[PREFIX + '/tests-001/list.log'].decode()
    listed = [line.removesuffix(': test') for line in listing.splitlines() if line.endswith(': test')]
    require(len(listed) == 258 and all(listed.count(name) == 1 for name in selected),
            'synthetic listing coverage differs')
    for index, step in enumerate(tests['steps']):
        require([step['name'], step['command']] == protocol['test_commands'][index]
                and step['selected_test_gate_passed'] is True, 'synthetic selected command/gate differs')
        logfile = 'list.log' if index == 0 else f'test-{index:02}.log'
        body = files[PREFIX + '/tests-001/' + logfile]
        require(digest(body) == step['log_sha256'], 'synthetic exact log hash differs')
        if index:
            name, text = selected[index - 1], body.decode()
            require(step['command'][-4:] == ['--exact', name, '--nocapture', '--test-threads=1'],
                    'synthetic exact test argv differs')
            require(text.count('running 1 test\n') == 1 and text.count('test ' + name + ' ... ok') == 1,
                    'synthetic intended test not exactly once passed')
            require(re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured;', text)
                    == [('ok', '1', '0', '0', '0')], 'synthetic exact summary differs')
    expected = build['outputs']['component-tests']
    require(tests['executed_binary_sha256'] == tests['outputs']['frozen-component-tests'] == expected,
            'synthetic omitted executable digest chain differs')
    require(q['status'] == 'private_core_build_and_19_synthetic_regressions_passed'
            and q['source_files'] == 89 and q['source_new_tests'] == 11
            and q['tests']['actual_passed'] == q['tests']['selected'] == 19
            and q['tests']['failed'] == q['tests']['ignored'] == 0
            and q['tests']['exact_names'] == selected and q['compile']['products'] == build['outputs']
            and q['tests']['executed_binary_sha256'] == expected, 'synthetic qualification scope/chain differs')
    require(q['lifecycle']['owned_groups'] == groups and q['lifecycle']['all_owned_groups_terminal'] is True,
            'synthetic saved lifecycle summary differs')
    for name, expected in q['bound_documents'].items():
        require(digest(files[PREFIX + '/' + name]) == expected, 'synthetic qualified artifact differs')
    audit = load('independent-execution-audit-v3.json')
    require(audit['status'] == 'passed' and audit['findings'] == [], 'independent prototype execution audit failed')
    root_audit = document(files['target/resume-20261025-review/dual-sensitivity-prototype-independent-saved-review.json'])
    require(root_audit['status'] == 'passed-independent-dual-sensitivity-prototype-saved-review'
            and root_audit['findings'] == [] and root_audit['checks'] == 858,
            'independent prototype saved review failed')
    release = load('execution-release.json')
    require(release['status'] == 'released' and release['authority'] == '/root'
            and release['protocol_sha256'] == digest(files[PREFIX + '/qualification-protocol.json'])
            and release['phases'] == ['build', 'tests'] and release['scheduler_quiet_window_terminal'] is True,
            'prototype release differs')
    for key in ['quiet_root_release', 'quiet_terminal_receipt']:
        item = release[key]
        require(digest(files[item['path']]) == item['sha256'], 'quiet release/receipt differs')
    return groups


def check_numerical_lifecycle(files, omitted):
    load = lambda name: document(files[NUMERIC + '/' + name])
    protocol, grant = load('protocol.json'), load('root-execution-grant.json')
    operations = ['build'] + DOMAINS + ['saved-gate']
    require(protocol['ordered_stages'] == operations and protocol['domain_order'] == DOMAINS
            and protocol['bounds'] == BOUNDS and protocol['cpu_affinity'] == {'build': [24, 25], 'runtime': [14]},
            'numeric fixed schedule/bounds/CPU differs')
    require(grant['status'] == 'granted' and grant['grantor'] == '/root' and grant['phases'] == operations
            and grant['protocol_sha256'] == digest(files[NUMERIC + '/protocol.json'])
            and grant['independent_reviews_cleared'] is True and grant['typed_cache_pilot_lease_terminal'] is True
            and grant['bounds'] == BOUNDS and grant['no_automatic_retry_or_extension'] is True,
            'numeric immutable conditional grant differs')
    review = load('runner-comparator-review.json')
    require(review['status'] == 'passed' and review['findings'] == []
            and review['draft_sha256'] == digest(files[NUMERIC + '/protocol-draft.json']), 'numeric runner review differs')
    for name, expected in review['subject_sha256'].items():
        require(digest(files[NUMERIC + '/' + name]) == expected, 'reviewed numeric runner source differs')
    failed_review = load('runner-comparator-review-v1.json')
    require(failed_review['status'] == 'failed' and len(failed_review['findings']) == 1
            and failed_review['findings'][0]['id'] == 'R1'
            and failed_review['draft_sha256'] == digest(files[NUMERIC + '/protocol-draft-v1.json']),
            'historical runner finding was not preserved')
    require(digest(files[NUMERIC + '/run-v1.py']) == failed_review['subject_sha256']['run.py'],
            'historical rejected runner changed')
    groups, compiled = [], {}
    initial = dict(protocol['inputs'])
    initial[NUMERIC + '/protocol.json'] = digest(files[NUMERIC + '/protocol.json'])
    initial[NUMERIC + '/root-execution-grant.json'] = digest(files[NUMERIC + '/root-execution-grant.json'])
    build = load('build-001/build.json')
    require(build['inputs'] == initial, 'numeric build guard map differs')
    stage(build, 2, BOUNDS['build'], groups)
    require(build['commands'] == protocol['commands']['build'], 'numeric build commands differ')
    expected_runtime = dict(initial)
    expected_runtime[NUMERIC + '/build-001/build.json'] = digest(files[NUMERIC + '/build-001/build.json'])
    for name, expected in build['outputs'].items():
        key = NUMERIC + '/build-001/' + name
        compiled[key] = expected
        expected_runtime[key] = expected
    for step, command in zip(build['steps'], protocol['commands']['build']):
        require([step['name'], step['command']] == command, 'numeric actual build argv differs')
        name = NUMERIC + '/build-001/' + step['name'] + '.log'
        require(digest(files[name]) == step['log_sha256'], 'numeric build log differs')
        expected_runtime[name] = step['log_sha256']
    prior = {}
    for operation in DOMAINS + ['saved-gate']:
        folder = NUMERIC + ('/saved-gate-001' if operation == 'saved-gate' else '/runtime-' + operation + '-001')
        run = document(files[folder + '/run.json'])
        expected = dict(expected_runtime)
        for name, previous in prior.items():
            previous_folder = NUMERIC + '/runtime-' + name + '-001'
            expected[previous_folder + '/run.json'] = digest(files[previous_folder + '/run.json'])
            if operation == 'saved-gate':
                for output, expected_hash in previous['outputs'].items():
                    expected[previous_folder + '/' + output] = expected_hash
        require(run['operation'] == operation and run['inputs'] == expected, 'numeric ordered guard map differs')
        stage(run, 1, BOUNDS[operation], groups)
        require(run['child_limit_seconds'] == BOUNDS[operation][2]
                and run['commands'] == protocol['commands'][operation]
                and [run['steps'][0]['name'], run['steps'][0]['command']] == protocol['commands'][operation][0],
                'numeric actual operation/budget/command differs')
        require(run['steps'][0]['timeout_seconds'] <= BOUNDS[operation][2], 'numeric child cap exceeded')
        log = folder + '/' + run['steps'][0]['name'] + '.log'
        require(digest(files[log]) == run['steps'][0]['log_sha256'], 'numeric operation log differs')
        if operation == 'saved-gate':
            require(set(run['outputs']) == {'comparison.json'} and run['captured_status'] == 'passed_saved_numerical_gates_only',
                    'saved numerical gate did not pass')
            require(digest(files[folder + '/comparison.json']) == run['outputs']['comparison.json'], 'saved gate output differs')
        else:
            require(set(run['outputs']) == {'frozen-component-probe', 'result.json'}
                    and run['executed_binary_sha256'] == run['outputs']['frozen-component-probe']
                    == build['outputs']['full-component-probe']
                    and run['captured_status'] == 'capture_complete_not_yet_qualified', 'numeric capture binary/output chain differs')
            compiled[folder + '/frozen-component-probe'] = run['executed_binary_sha256']
            require(digest(files[folder + '/result.json']) == run['outputs']['result.json'], 'numeric capture bytes differ')
            prior[operation] = run
    q = load('qualification-summary.json')
    require(q['parent_complex_laurent_taylor_slots'] == 528 and q['child_rows'] == 156
            and q['paired_complex_components'] == 264, 'numeric coverage summary differs')
    require(len(q['stages']) == 6 and [item['operation'] for item in q['stages']] == operations,
            'numeric lifecycle summary inventory differs')
    for item in q['stages']:
        require(item['status'] == 'passed' and item['all_groups_terminal_absent'] is True
                and item['inputs_unchanged'] is True and digest(files[item['receipt']]) == item['sha256'],
                'numeric stage summary differs')
    require(all(omitted[name]['sha256'] == expected for name, expected in compiled.items()),
            'numeric omitted executable digest chain differs')
    return groups


def check_exact_omissions(files, omitted):
    """Check all nine historical digest chains without reading any product."""
    expected = {}
    for prefix in [PREFIX, NUMERIC]:
        build = document(files[prefix + '/build-001/build.json'])
        for name, value in build['outputs'].items():
            expected[prefix + '/build-001/' + name] = value
    tests = document(files[PREFIX + '/tests-001/tests.json'])
    expected[PREFIX + '/tests-001/frozen-component-tests'] = tests['executed_binary_sha256']
    for domain in DOMAINS:
        folder = NUMERIC + '/runtime-' + domain + '-001'
        run = document(files[folder + '/run.json'])
        expected[folder + '/frozen-component-probe'] = run['executed_binary_sha256']
    require(len(expected) == 9 and {name: item['sha256'] for name, item in omitted.items() if 'sha256' in item}
            == expected, 'exact nine compiled omission paths/digests differ')
    for name, item in omitted.items():
        safe(name)
        require(type(item['bytes']) is int and item['bytes'] >= 0, 'omission byte size invalid')
        if name in expected:
            require(item['reason'] == 'compiled product; historical receipt digest only; not rehashed',
                    'compiled omission provenance promoted')
        else:
            require(name.endswith(('.pyc', '.pyo')) and '__pycache__' in Path(name).parts
                    and item['reason'] == 'generated Python bytecode' and 'sha256' not in item,
                    'unexpected omitted artifact')
    return len(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-draft', action='store_true', help='check a target-only draft without claiming independent audit clearance')
    parser.add_argument('--reconstruct', type=Path, help='write exact noncompiled source/evidence to a new directory')
    args = parser.parse_args()
    manifest = document((HERE / 'manifest.json').read_bytes())
    sealed = manifest['status'] == 'sealed_private_full_component_n6_saved_correctness'
    require(sealed or (args.allow_draft and HERE.is_relative_to(ROOT / 'target')
            and manifest['status'] == 'draft_pending_independent_numerical_audit_and_seal_release'),
            'independent numerical audit/seal release required')
    actual = {str(path.relative_to(HERE)) for path in HERE.rglob('*')
              if path.is_file() and '__pycache__' not in path.parts}
    require(actual == set(manifest['files']) | {'manifest.json'}, 'exact capsule file inventory differs')
    for name, expected in manifest['files'].items():
        safe(name)
        path = HERE / name
        require(not path.is_symlink(), 'capsule symlink')
        body = path.read_bytes()
        allowed(name, body)
        require(descriptor(body) == expected, 'capsule file changed: ' + name)
    base, inherited, borrowed = load_parent(ROOT)
    require({n: descriptor(b) for n, b in borrowed.items()} == manifest['borrowed_inputs'],
            'committed parent/transitive pins differ')
    payload = archive((HERE / 'payload.tar.gz').read_bytes(), manifest['payload_archive']['members'])
    snapshots = reconstruct_sources(base, payload, borrowed)
    require({name: {n: descriptor(b) for n, b in snapshot.items()} for name, snapshot in snapshots.items()}
            == manifest['source_snapshots'], 'complete reconstructed source inventory differs')
    private = dict(payload)
    for name, alias in manifest['source_aliases'].items():
        safe(name)
        safe(alias['member'])
        require(name not in private, 'source alias duplicates payload')
        private[name] = snapshots[alias['snapshot']][alias['member']]
    require({n: descriptor(b) for n, b in private.items()} == manifest['reconstructed_private_files'],
            'complete private evidence/source reconstruction differs')
    files = dict(inherited)
    for name, body in private.items():
        require(name not in files or files[name] == body, 'inherited evidence path collision')
        files[name] = body
    available = historical = 0
    records = [PREFIX + '/' + name for name in ['qualification-protocol.json', 'build-001/build.json', 'tests-001/tests.json']]
    records += [NUMERIC + '/' + name for name in ['protocol.json', 'build-001/build.json', 'saved-gate-001/run.json']]
    records += [NUMERIC + '/runtime-' + domain + '-001/run.json' for domain in DOMAINS]
    for name in records:
        for key, expected in document(files[name])['inputs'].items():
            key = normalized(key)
            body = files.get(key, borrowed.get(key))
            if body is None:
                historical += 1
            else:
                require(digest(body) == expected, 'reconstructed historical guard bytes differ: ' + key)
                available += 1
    groups = check_synthetic(files)
    numeric_groups = check_numerical_lifecycle(files, manifest['omitted_private_files'])
    compiled_omissions = check_exact_omissions(files, manifest['omitted_private_files'])
    require(not set(groups) & set(numeric_groups), 'owned process group identifier reused within cohort')
    numeric = check_saved(files, borrowed)
    if sealed:
        clear = document((HERE / 'audit-clear.json').read_bytes())
        audit = manifest['independent_numeric_audit']
        require(clear['status'] == 'cleared' and clear['grantor'] in ['/root', '/root/dual_sensitivity_research']
                and clear['independent_numeric_audit'] == audit, 'sealed audit-clear differs')
        require(clear['package_code_sha256'] == {name: digest((HERE / name).read_bytes()) for name in CODE},
                'sealed package files differ from immutable audit-clear')
        body = files[audit['path']]
        require(audit == dict(path=NUMERIC_AUDIT, sha256=NUMERIC_AUDIT_SHA)
                and body == (HERE / 'independent-numeric-audit.json').read_bytes(),
                'sealed independent numerical audit differs')
        evidence = validate_independent_numeric_audit(body, lambda name: files[name])
        for name, expected in evidence['all_source_and_saved_subjects_sha256'].items():
            body = files.get(normalized(name), borrowed.get(normalized(name)))
            if body is not None:
                require(digest(body) == expected, 'independently audited available bytes differ: ' + name)
    for field in ['public_dual_qualified', 'general_independent_higher_mixed_derivatives_qualified',
                  'finite_differences_qualified', 'rigorous_error_certificate', 'current_cargo_qualified',
                  'performance_qualified', 'production_adoption']:
        require(manifest[field] is False, 'capsule scope was promoted: ' + field)
    if args.reconstruct:
        destination = args.reconstruct.resolve()
        require(destination != ROOT and not destination.exists(), 'reconstruction destination must be new')
        destination.mkdir(parents=True)
        for name, body in files.items():
            safe(name)
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
    print(json.dumps(dict(status='passed', independently_audit_cleared_and_sealed=sealed,
        source_snapshots={name: len(snapshot) for name, snapshot in snapshots.items()},
        reconstructed_private_files=len(private), inherited_private_files=len(inherited),
        available_guard_occurrences_checked=available,
        historical_unbundled_guard_occurrences_not_rehashed=historical,
        selected_synthetic_tests_checked=19, saved_owned_group_attestations_checked=len(groups) + len(numeric_groups),
        numeric=numeric, exact_compiled_omissions_checked=compiled_omissions,
        compiled_products_rehashed=False, live_process_identifiers_probed=False,
        no_compiler_evaluator_integral_reference_or_benchmark_executed=True,
        production_adoption=False, public_dual_qualified=False, performance_qualified=False), sort_keys=True))


if __name__ == '__main__':
    main()
