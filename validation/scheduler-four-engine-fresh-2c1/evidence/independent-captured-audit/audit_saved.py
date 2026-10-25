"""Independent saved 60-request captured scheduler audit; no subprocesses.

Only standard-library numeric primitives from a previous independent audit are
reused. No producer admission, numerical evaluator or compiled program imported.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import copy
import datetime
import hashlib
import json
import math
import struct
import time
import numeric_primitives as q

ROOT = Path('/shared/external/iregi/iregi-rust')
BASE = ROOT/'target/guard-performance-review/optimized-performance-proposal'
HERE = BASE/'fresh-captured-runtime'
PIN = '2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2'
PROTOCOL = 'bddd62ae70fbb81200e263ba96ae0185177b090608f7abb0b440e1744bf75b4b'
ARITY = {'A0': 2, 'B0': 4, 'C0': 7, 'dB0': 4, 'D0': 11}
ORDER = ['finite', 'total_single', 'ir_double', 'uv_single', 'ir_single', 'derivative_discriminant']


def exact(left, right):
    """Type-sensitive equality, preserving binary64 signed zeros."""
    if type(left) is not type(right):
        return False
    if type(left) is float:
        return math.isfinite(left) and math.isfinite(right) and struct.pack('>d', left) == struct.pack('>d', right)
    if type(left) is dict:
        return set(left) == set(right) and all(exact(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(exact(a, b) for a, b in zip(left, right))
    return left == right


def expect(value, wanted, context):
    q.require(exact(value, wanted), context)


def keys(value, expected):
    q.require(type(value) is dict and set(value) == set(expected), ('schema', expected))


def groups(n, rank):
    return {(2, 0): [('B0', [0])], (2, 1): [('B0', [0]), ('A0', [1, 2])],
            (3, 0): [('C0', [0])], (3, 1): [('C0', [0]), ('B0', [1, 2, 3])]}[(n, rank)]


def execution(value, n, rank, rows):
    expected = groups(n, rank)
    expect(value, q.expected_execution(rows, len(expected), rows*sum(len(leaves) for _, leaves in expected)), 'execution counters')
    for item in value.values():
        q.natural(item)


def capture(values, n, rank, rows, components=1, domain='f64'):
    count = 0
    for item, (family, leaves) in zip(q.array(values, len(groups(n, rank))), groups(n, rank)):
        keys(item, ['family', 'backend', 'components', 'rows', 'requests', 'valid_lanes', 'input', 'output_order', 'output', 'errors', 'whole_batch_error'])
        q.require(item['family'] == family and item['backend'] == 'SymbolicaBatch')
        q.natural(item['rows'], rows*len(leaves)); q.natural(item['components'], components)
        expect(item['requests'], [[leaf, lane] for leaf in leaves for lane in range(rows)], 'master request routing')
        expect(item['valid_lanes'], list(range(rows)), 'master valid lanes')
        expect(item['output_order'], ORDER, 'six master coefficient order')
        expect(item['errors'], [None]*(rows*len(leaves)), 'master lane errors')
        q.require(item['whole_batch_error'] is None)
        for z in q.array(item['input'], ARITY[family]*rows*len(leaves)*components):
            q.represented(z, domain)
        for lane in q.array(item['output'], rows*len(leaves)):
            for z in q.array(lane, 6*components):
                q.represented(z, domain)
        count += rows*len(leaves)*6*components
    return count


def lane(value, moments, components, native, domain):
    keys(value, ['status', 'represented', 'fallback_used', 'analytic_used']+(['moments'] if native else []))
    q.require(value['status'] == 'success' and value['fallback_used'] is False and value['analytic_used'] is False)
    values = q.array(value['represented'], 4*moments*components)
    for z in values:
        q.represented(z, domain)
    if native:
        q.require(domain == 'f64' and components == 1)
        native_values = [z for m in q.array(value['moments'], moments) for z in q.array(m, 4)]
        for z, observed in zip(values, native_values):
            decoded = q.f64_represented(z)
            q.require(all(struct.pack('>d', a) == struct.pack('>d', b) for a, b in zip(decoded, q.f64_complex(observed))), 'native/represented exact bits')
    return len(values)


def observation(value, components, native):
    keys(value, ['stable', 'lanes', 'diagnostics', 'master_captures', 'execution'])
    q.require(value['stable'] is True)
    lane(q.array(value['lanes'], 1)[0], 5, components, native, 'f64')
    expect(value['diagnostics'], [[]], 'cache diagnostics')
    execution(value['execution'], 2, 1, 1)
    capture(value['master_captures'], 2, 1, 1, components)


def normal(value, case, rows):
    keys(value, ['id', 'result']); q.require(value['id'] == case['id'])
    result = value['result']
    keys(result, ['stable', 'lanes', 'diagnostics', 'master_captures', 'execution', 'id', 'n', 'rank', 'batch', 'plan_reused', 'degrees', 'requested_master_backend', 'scope', 'total_ns', 'elapsed_ns', 'iterations', 'capture_enabled', 'profiling_enabled', 'own_repeated_outputs_exact', 'input_unchanged'])
    q.require(result['id'] == case['id'] and result['stable'] is True)
    for key, wanted in [('n', case['n']), ('rank', case['rank']), ('batch', rows), ('iterations', 0)]:
        q.natural(result[key], wanted)
    q.require(type(result['plan_reused']) is bool)
    expect(result['degrees'], [0] if case['rank'] == 0 else [0, 1, 1, 1, 1], 'tensor ordering/degrees')
    q.require(result['scope'] == 'untimed generic-only scheduler whole-reduction qualification' and result['requested_master_backend'] == 'SymbolicaBatch')
    q.require(result['capture_enabled'] is True and result['profiling_enabled'] is False and result['own_repeated_outputs_exact'] is True and result['input_unchanged'] is True)
    expect(result['total_ns'], [], 'no timing values'); expect(result['elapsed_ns'], [], 'no elapsed measurements')
    tensor = sum(lane(x, len(result['degrees']), 1, True, 'f64') for x in q.array(result['lanes'], rows))
    expect(result['diagnostics'], [[] for _ in range(rows)], 'successful diagnostics')
    execution(result['execution'], case['n'], case['rank'], rows)
    masters = capture(result['master_captures'], case['n'], case['rank'], rows)
    return {'tensor_complex_values': tensor, 'master_complex_values': masters}


def snapshot(value, spec, domain, family, input_values):
    keys(value, ['rows', 'components', 'lanes'])
    rows, components = spec['rows'], spec['components']
    q.natural(value['rows'], rows); q.natural(value['components'], components)
    successes = failures = 0
    for index, (item, error) in enumerate(zip(q.array(value['lanes'], rows), q.array(spec['errors'], rows))):
        keys(item, ['error', 'six_outputs']); expect(item['error'], error, 'direct master expected error')
        if error is not None:
            q.require(item['six_outputs'] is None, 'failed outputs must be null')
            failures += 1
            continue
        outputs = [q.represented(z, domain, False) for z in q.array(item['six_outputs'], 6*components)]
        # Independent bare scalar UV identities, component by component.
        for component in range(components):
            uv = outputs[3*components+component]
            if family == 'A0':
                mass = q.represented(input_values[(index*ARITY[family])*components+component], domain, True, True)
                q.require(uv == mass, 'A0 UV equals mass squared including Taylor components')
            elif family == 'B0':
                q.require(uv == (Fraction(int(component == 0)), Fraction(0)), 'B0 UV constant Taylor identity')
            else:
                q.require(uv == (Fraction(0), Fraction(0)), 'UV-finite scalar family')
        successes += 1
    return {'rows': rows, 'successful_lanes': successes, 'expected_failed_lanes': failures, 'complex_values': successes*6*components}


def core_control(value, spec):
    keys(value, ['label', 'components', 'input', 'result', 'own_repeated_outputs_exact', 'input_unchanged'])
    for key in ['label', 'components', 'input']:
        expect(value[key], spec[key], 'core control '+key)
    domain = 'DoubleFloat' if value['label'].startswith('DoubleFloat') else 'Float' if value['label'].startswith('Float') else 'f64'
    for z in value['input']:
        q.represented(z, domain)
    q.require(value['own_repeated_outputs_exact'] is True and value['input_unchanged'] is True)
    result = value['result']; keys(result, ['values', 'statuses', 'diagnostics', 'fallback_used', 'analytic_used', 'execution', 'master_captures'])
    q.require(result['statuses'] == '[Success]')
    expect(result['diagnostics'], [[]], 'control diagnostics'); expect(result['fallback_used'], [False], 'control fallback'); expect(result['analytic_used'], [False], 'control analytic')
    for z in q.array(result['values'], spec['complex_output_count']):
        q.represented(z, domain)
    execution(result['execution'], 2, 1, 1)
    capture(result['master_captures'], 2, 1, 1, value['components'], domain)


def controls(value, shape):
    keys(value, ['id', 'status', 'core', 'extended_core', 'masters', 'cache_interleaving', 'backend'])
    q.require(value['id'] == 'controls' and value['status'] == 'passed' and value['backend'] == 'SymbolicaBatch')
    for field in ['core', 'extended_core']:
        for actual, spec in zip(q.array(value[field], len(shape[field])), shape[field]):
            core_control(actual, spec)
    masters = value['masters']
    keys(masters, ['status', 'scope', 'comparison', 'unchanged_comparison', 'failed_lane_output_policy', 'selected_families', 'unchanged_paths', 'extended_unchanged_paths', 'extended_inventory'])
    q.require(masters['status'] == 'passed' and masters['failed_lane_output_policy'] == 'null, never successful zero-valued evidence')
    q.require(masters['scope'] == 'untimed generic-only master adapter controls; no performance claim')
    q.require(masters['comparison'] == 'exact represented rational, precision and sign of all six successful outputs; external cross-archive comparison required')
    q.require(masters['unchanged_comparison'] == 'exact represented rational, component precision and sign; explicit expected errors')
    totals = {'cases': 0, 'rows': 0, 'successful_lanes': 0, 'expected_failed_lanes': 0, 'complex_values': 0}
    for group_name in ['selected_families', 'unchanged_paths', 'extended_unchanged_paths']:
        for actual, spec in zip(q.array(masters[group_name], len(shape[group_name])), shape[group_name]):
            selected = group_name == 'selected_families'
            if selected:
                keys(actual, ['family', 'status', 'layout_and_overflow_errors_checked', 'ordinary_dual_adapter_rejected', 'warm_clone_checked', 'cases'])
                q.require(all(actual[k] is True for k in ['layout_and_overflow_errors_checked', 'ordinary_dual_adapter_rejected', 'warm_clone_checked']))
                domain = 'f64'
            else:
                keys(actual, ['label', 'family', 'status', 'backend', 'shape', 'components', 'cases'])
                for key in ['label', 'shape', 'components']:
                    expect(actual[key], spec[key], 'unchanged direct plan '+key)
                q.require(actual['backend'] == 'SymbolicaBatch')
                domain = 'DoubleFloat' if actual['label'].startswith('DoubleFloat') else 'Float' if actual['label'].startswith('Float') else 'f64'
            q.require(actual['family'] == spec['family'] and actual['status'] == 'passed')
            for item, cs in zip(q.array(actual['cases'], len(spec['cases'])), spec['cases']):
                expected_keys = ['label', 'family', 'status', 'baseline_backend', 'candidate_backend', 'independent_generic_instances_exact', 'own_repeated_outputs_exact', 'input_metadata', 'input_unchanged', 'baseline', 'candidate'] if selected else ['label', 'status', 'represented_outputs', 'baseline', 'candidate', 'candidate_exactly_matches_baseline', 'own_repeated_outputs_exact', 'input_metadata', 'input_unchanged']
                keys(item, expected_keys)
                q.require(item['label'] == cs['label'] and item['status'] == 'passed' and item['own_repeated_outputs_exact'] is True and item['input_unchanged'] is True)
                if selected:
                    q.require(item['family'] == actual['family'] and item['baseline_backend'] == item['candidate_backend'] == 'SymbolicaBatch' and item['independent_generic_instances_exact'] is True)
                else:
                    q.require(item['candidate_exactly_matches_baseline'] is True)
                expect(item['input_metadata'], cs['input_metadata'], 'exact direct scalar input context')
                for z in q.array(item['input_metadata'], cs['rows']*ARITY[actual['family']]*cs['components']):
                    q.represented(z, domain, True, True)
                stat = snapshot(item['baseline'], cs, domain, actual['family'], item['input_metadata'])
                snapshot(item['candidate'], cs, domain, actual['family'], item['input_metadata'])
                expect(item['baseline'], item['candidate'], 'independent same-process generic master instances')
                if not selected:
                    snapshot(item['represented_outputs'], cs, domain, actual['family'], item['input_metadata'])
                    expect(item['represented_outputs'], item['baseline'], 'direct represented snapshot')
                for key, count in stat.items():
                    totals[key] += count
                totals['cases'] += 1
    expect(masters['extended_inventory'], shape['extended_inventory'], 'numeric-type inventory')
    q.require(totals == {'cases': 67, 'rows': 133, 'successful_lanes': 106, 'expected_failed_lanes': 27, 'complex_values': 774}, 'complete direct-master inventory')
    cache = value['cache_interleaving']; keys(cache, ['status', 'same_immutable_plan', 'expected_current_process_records', 'steps'])
    q.require(cache['status'] == 'passed' and cache['same_immutable_plan'] is True)
    expected = q.array(cache['expected_current_process_records'], 4)
    for item, dual in zip(expected, shape['cache_shapes']):
        observation(item, 2 if dual else 1, not dual)
    for item, index in zip(q.array(cache['steps'], len(shape['cache_indices'])), shape['cache_indices']):
        keys(item, ['workspace_case', 'backend', 'dual', 'result'])
        q.natural(item['workspace_case'], index)
        q.require(item['backend'] == 'SymbolicaBatch' and item['dual'] is shape['cache_shapes'][index])
        expect(item['result'], expected[index], 'complete cache context interleaving')
    return totals


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--receipt-sha256', required=True)
    ap.add_argument('--output-directory', type=Path, required=True)
    args = ap.parse_args()
    q.require(Path.cwd() == ROOT)
    output = args.output_directory.resolve(); output.mkdir(exist_ok=False)
    started = time.monotonic(); bound = {}
    def bind(path, expected=None):
        path = Path(path); path = path if path.is_absolute() else ROOT/path
        with path.open('rb') as stream:
            h = hashlib.file_digest(stream, 'sha256').hexdigest()
        q.require(expected is None or h == expected, 'changed source/artifact/data '+str(path))
        q.require(path not in bound or bound[path] == h, 'conflicting digest')
        bound[path] = h; return h
    report = {'schema_version': 1, 'reviewer': '/root/scheduler_perf_resume/fresh_recipe_audit', 'status': 'checking', 'scope': 'Independent saved120-event exact numeric/schema/provenance audit; no producer admission imported and no subprocess/evaluator/compiler/metadata/clock measurement launched.', 'pinned_source_revision': PIN, 'numerical_accuracy_oracle': False, 'performance_qualified': False, 'production_adoption_authorized': False}
    try:
        bind(Path(__file__)); bind(Path(q.__file__)); bind(Path(__file__).with_name('numeric-primitives-origin.json'))
        ppath = HERE/'protocol.json'; bind(ppath, PROTOCOL); p = q.read(ppath)
        folder = HERE/'qualification-001'; receipt_path = folder/'results.json'; bind(receipt_path, args.receipt_sha256); result = q.read(receipt_path)
        q.require(result['status'] == 'passed-awaiting-independent-saved-data-review' and result['protocol_sha256'] == PROTOCOL)
        q.require(result['guard_before'] is True and result['guard_after'] is True and result['cleanup_errors'] == [] and result['deadline_exceeded'] is False)
        q.require(not any(k in result for k in ['error', 'guard_error', 'cancellation']))
        q.require(result['request_count'] == 60 and 0 < result['elapsed_seconds_diagnostic'] <= 300)
        q.require((p['cpu_affinity'], result['aggregate_budget_seconds'], result['cleanup_postguard_reserve_seconds']) == ('34', 300, 20))
        q.require(p['pinned_source_revision'] == PIN and result['performance_measurement'] is False)
        for raw, h in {**p['protected_sha256'], **p['tool_sha256'], **result['input_sha256']}.items():
            bind(raw, h)
        for item in result['executed_executables'].values():
            bind(item['path'], item['sha256'])
        cases = q.read(p['inputs']); shape = q.read(p['control_shapes'])
        q.require([(x['n'], x['rank'], len(x['samples'])) for x in cases] == [(2, 0, 32), (2, 1, 32), (3, 0, 32), (3, 1, 32)])
        def payload(case, rows):
            return json.dumps({'id': case['id'], 'n': case['n'], 'rank': case['rank'], 'algorithm': 'Hybrid', 'samples': case['samples'][:rows]}, allow_nan=False)+'\n'
        coords = [(case, rows) for case in cases for rows in [1, 32]]; schedule = []
        for case, rows in coords:
            for stage in ['initial', 'own-repeat']:
                for engine in ['baseline', 'candidate']:
                    schedule.append((stage, [case['id'], rows], engine, payload(case, rows)))
        for stage, index in [('controls', 0), ('controls-repeat', 1)]:
            for engine in ['baseline', 'candidate']:
                schedule.append((stage, ['controls', index], engine, 'CONTROLS\n'))
        for case, rows in coords:
            for engine in ['baseline', 'candidate']:
                schedule.append(('retained', [case['id'], rows], engine, payload(case, rows)))
        invalid = [('engine', 'baseline'), ('warmup', 1), ('repeats', 1), ('iterations', 1)]
        for field, value in invalid:
            for engine in ['baseline', 'candidate']:
                schedule.append(('invalid-request', [field, value], engine, json.dumps({**q.decode(payload(cases[0], 1)), field: value})+'\n'))
        q.require(len(schedule) == 60)
        raw_path = folder/'responses.jsonl'; bind(raw_path, result['raw_sha256'])
        events = [q.decode(line) for line in raw_path.read_text().splitlines()]; q.require(len(events) == 120)
        by_case = {c['id']: c for c in cases}; records = {}; emitted = {'baseline': [], 'candidate': []}; initial = {}; control_records = {}; totals = []; control_counts = None
        for serial, (stage, key, engine, wire) in enumerate(schedule, 1):
            request, response = events[2*serial-2:2*serial]
            wanted = {'serial': serial, 'stage': stage, 'key': key, 'engine': engine, 'payload': wire}
            expect(request, {**wanted, 'event': 'request'}, 'exact raw request phase/order/payload')
            keys(response, [*wanted, 'event', 'response'])
            expect({k: response[k] for k in wanted}, wanted, 'exact paired response metadata'); q.require(response['event'] == 'response')
            body = response['response']; emitted[engine].append(body); records[(stage, tuple(key), engine)] = body
            if stage in ['initial', 'own-repeat', 'retained']:
                stats = normal(body, by_case[key[0]], key[1])
                if stage == 'initial':
                    initial[(tuple(key), engine)] = body
                    if engine == 'baseline': totals.append(stats)
                else:
                    canonical = copy.deepcopy(body); canonical['result'].pop('plan_reused')
                    anchor = copy.deepcopy(initial[(tuple(key), engine)]); anchor['result'].pop('plan_reused')
                    expect(canonical, anchor, 'all own/retained fields except plan_reused')
            elif stage in ['controls', 'controls-repeat']:
                counts = controls(body, shape)
                if stage == 'controls':
                    control_records[engine] = body; control_counts = counts
                else:
                    expect(body, control_records[engine], 'complete own controls repeat')
            else:
                expect(body, {'status': 'invalid_request', 'error': 'qualification is untimed; engine and timing counts are forbidden'}, 'timing request rejected')
        for serial in range(1, 60, 2):
            expect(events[2*serial-1]['response'], events[2*(serial+1)-1]['response'], 'complete paired cross-scheduler response')
        family_totals = {k: sum(x[k] for x in totals) for k in ['tensor_complex_values', 'master_complex_values']}
        expect(family_totals, {'tensor_complex_values': 1584, 'master_complex_values': 1782}, 'all eight complete tensor/master families')
        for field in ['rows', 'retained_rows']:
            q.require([(x['id'], x['batch']) for x in result[field]] == [(c['id'], n) for c, n in coords] and all(x['status'] == 'passed' for x in result[field]))
        q.require(result['controls']['status'] == result['invalid_request_controls']['status'] == 'passed')
        expect(result['invalid_request_controls']['cases'], [{'field': f, 'value': v, 'status': 'passed'} for f, v in invalid], 'invalid request receipt inventory')
        q.require(len(result['processes']) == len(result['process_terminals']) == 2)
        for engine in ['baseline', 'candidate']:
            process = next(x for x in result['processes'] if x['label'] == engine); terminal = next(x for x in result['process_terminals'] if x['label'] == engine)
            q.require(process['command'] == [p['taskset'], '-c', '34', result['executed_executables'][engine]['path']])
            q.require(terminal['returncode'] == 0 and terminal['owned_group_gone'] is True and terminal['received_responses'] == 30 and terminal['owned_process_group'] == process['owned_process_group'])
            stdout = folder/(engine+'.stdout.log'); stderr = folder/(engine+'.stderr.log')
            bind(stdout, result['stdout_sha256'][engine]); bind(stderr, result['stderr_sha256'][engine])
            actual = [q.decode(line[7:]) for line in stdout.read_text().splitlines() if line.startswith('RESULT ')]
            expect(actual, emitted[engine], 'all stdout RESULT lines equal saved events')
            q.require(stderr.read_bytes() == b'', 'unexpected stderr')
        for path, h in bound.items():
            q.require(digest_file(path) == h, 'postaudit file changed')
        report.update(status='passed', receipt_sha256=args.receipt_sha256, raw_sha256=result['raw_sha256'], protocol_sha256=PROTOCOL,
            request_count=60, raw_event_count=120, all_complete_records_and_controls_checked=True,
            own_and_retained_exact_except_plan_reused=True, complete_cross_scheduler_pairs=30,
            stdout_result_sequences_checked=True, process_groups_terminal_and_gone=True,
            family_coverage_per_engine_initial_record=family_totals, direct_control_coverage_per_engine=control_counts,
            independent_scalar_uv_identities_checked=True, all_numeric_types_and_Taylor_components_checked=True,
            all_successful_outputs_finite=True, failed_master_outputs_null=True,
            bound_input_artifact_data_files=len(bound), producer_module_imported=False, subprocesses_launched=0,
            elapsed_seconds_diagnostic_only=result['elapsed_seconds_diagnostic'], no_performance_conclusion_from_lifecycle_duration=True)
    except Exception as error:
        report.update(status='failed', error=repr(error))
    report['checks'] = q.CHECKS
    report['bindings_sha256'] = {str(p): h for p, h in bound.items()}
    report['audit_elapsed_seconds_diagnostic'] = time.monotonic()-started
    report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    target = output/'full-review.json'; target.write_text(json.dumps(report, indent=2)+'\n')
    if report['status'] == 'passed':
        contract = {k: report[k] for k in ['status', 'receipt_sha256', 'raw_sha256', 'request_count', 'raw_event_count', 'all_complete_records_and_controls_checked', 'pinned_source_revision']}
        contract.update(full_review_path=str(target), full_review_sha256=digest_file(target))
        (output/'admission.json').write_text(json.dumps(contract, indent=2)+'\n')
    print(json.dumps({'status': report['status'], 'full_review': str(target), 'sha256': digest_file(target), 'checks': q.CHECKS, 'error': report.get('error')}))
    return 0 if report['status'] == 'passed' else 1


def digest_file(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


if __name__ == '__main__':
    raise SystemExit(main())
