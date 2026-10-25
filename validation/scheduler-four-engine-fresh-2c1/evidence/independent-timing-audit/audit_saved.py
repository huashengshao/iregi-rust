"""Independent saved timing audit; run only after terminal and root quiet release.

No executable-under-test, compiler, numerical evaluator or producer validator is
imported or invoked. The only new numerical work is saved-data comparison and,
after verifying root release, independently recomputing bootstrap statistics.
"""
from collections import Counter
from pathlib import Path
import argparse
import copy
import csv
import datetime
import hashlib
import itertools
import json
import math
import os
import random
import signal
import time

import numeric_primitives as q
import independent_captured_primitives as cap
import independent_uncaptured_primitives as unc
import independent_preflight_primitives as pf

ROOT = pf.ROOT
BASE = pf.BASE
PIN = pf.PIN
LABELS = pf.LABELS
TIRUST = pf.TIRUST
ENGINES = ['baselineTIRust', 'candidateTIRust', 'iregi', 'collier']
RATIOS = [('baselineTIRust', 'iregi'), ('candidateTIRust', 'iregi'), ('baselineTIRust', 'collier'), ('candidateTIRust', 'collier'), ('candidateTIRust', 'baselineTIRust')]
ORDERS = list(itertools.permutations(ENGINES))*2
random.Random(173).shuffle(ORDERS)
MINIMUM_NS = 100_000_000
TARGET_NS = 110_000_000
MAX_COUNT = 2**31-1
AUDIT_CAP_SECONDS = 300
SEMANTIC = ['id', 'n', 'rank', 'batch', 'stable', 'degrees', 'lanes', 'diagnostics', 'execution', 'requested_master_backend', 'input_unchanged']


def require(value, context='saved timing assertion'):
    q.require(value, context)


def expect(a, b, context):
    pf.expect(a, b, context)


def timeout(_number, _frame):
    raise TimeoutError('fixed saved-only 300-second audit allocation exhausted')


def payload(case, batch, label, iterations=None, warmup=0):
    if label in TIRUST:
        result = q.decode(pf.rust_payload(case, batch))
        if iterations is not None:
            result.update(engine='baseline' if label.startswith('baseline') else 'candidate', warmup=warmup, repeats=1, iterations=iterations)
        return json.dumps(result, allow_nan=False)+'\n'
    samples = case['samples'][:batch]
    mu = samples[0]['mu']; require(all(s['mu'] == mu for s in samples))
    measured = iterations is not None
    verb = 'BENCH' if measured or label == 'iregi' else 'CHECK'
    count = iterations if measured else 1
    lines = [f'{verb} {case["id"]} {1 if label == "collier" else 2} {case["n"]} {case["rank"]} {mu:.17g} {batch} {warmup} 1 {count}']
    for sample in samples:
        for shift, mass in zip(sample['shifts'], sample['masses']):
            lines.append(' '.join(f'{x:.17g}' for x in shift)+f' ({mass[0]:.17g},{mass[1]:.17g})')
    return '\n'.join(lines)+'\n'


def timed_response(label, body, before, case, batch, iterations):
    require(type(iterations) is int and 0 < iterations <= MAX_COUNT)
    if label in TIRUST:
        cap.keys(body, ['id', 'result']); require(body['id'] == case['id'])
        result = body['result']
        cap.keys(result, before[label]['result'])
        require(result['scope'] == 'whole-public-call fixed-count timing' and result['capture_enabled'] is False)
        require(result['profiling_enabled'] is False and result['own_repeated_outputs_exact'] is False)
        require(type(result['iterations']) is int and result['iterations'] == iterations)
        elapsed = q.array(result['elapsed_ns'], 1)[0]
        require(type(elapsed) is int and elapsed > 0, 'actual integer Rust Instant nanoseconds')
        ns = q.array(result['total_ns'], 1)[0]
        require(type(ns) in (int, float) and math.isfinite(ns) and ns > 0 and ns == elapsed/iterations)
        # Validate all underlying lane/represented/native/counter values using
        # the unchanged independent untimed schema, then compare every semantic
        # field exactly against this family's own immediately preceding record.
        untimed = copy.deepcopy(body)
        untimed['result'].update(scope='untimed capture-free scheduler whole-reduction qualification', own_repeated_outputs_exact=True, iterations=0, elapsed_ns=[], total_ns=[])
        unc.normal(untimed, case, batch)
        expect({k: result[k] for k in SEMANTIC}, {k: before[label]['result'][k] for k in SEMANTIC}, 'complete timed public-call tensor arrays equal own before record')
        require(result['plan_reused'] is True, 'same family workspace must remain prepared during timing')
    else:
        actual = copy.deepcopy(body)
        if label == 'collier':
            require(body['pole_check_errors'] is None, 'COLLIER pole probes excluded from timed block')
            actual['pole_check_errors'] = before[label]['pole_check_errors']
        pf.reference(actual, case, batch, label == 'collier')
        fields = ['id', 'stable', 'clock_ticks_per_second', 'lanes']+(['collier_mode'] if label == 'collier' else [])
        expect({k: body[k] for k in fields}, {k: before[label][k] for k in fields}, 'complete timed reference arrays equal own before record')
        ns = body['total_ns'][0]
        elapsed = ns*iterations
        require(type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed > 0)
    return elapsed, ns


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--protocol-sha256', required=True)
    parser.add_argument('--receipt-sha256', required=True)
    parser.add_argument('--quiet-release', type=Path, required=True)
    parser.add_argument('--quiet-release-sha256', required=True)
    parser.add_argument('--output-directory', type=Path, required=True)
    args = parser.parse_args()
    require(Path.cwd() == ROOT)
    started = time.monotonic(); previous_alarm = signal.signal(signal.SIGALRM, timeout); signal.alarm(AUDIT_CAP_SECONDS-5)
    out = args.output_directory.resolve(); out.mkdir(exist_ok=False)
    bindings = {}; row_table = []; raw_ratios = []
    report = {'schema_version': 1, 'status': 'checking', 'reviewer': '/root/scheduler_perf_resume/fresh_recipe_audit', 'mode': 'timing', 'pinned_source_revision': PIN,
              'scope': 'Independent saved-only full timing data/schema/provenance/numerical/calibration/bootstrap audit after root quiet release; no producer validator or bootstrap imported.',
              'saved_audit_cap_seconds': AUDIT_CAP_SECONDS, 'subprocesses_launched': 0, 'integrals_evaluated': 0, 'production_adoption_authorized': False}
    def bind(path, wanted=None):
        path = Path(path).resolve(); actual = pf.digest(path)
        require(wanted is None or actual == wanted, 'changed bound input '+str(path))
        require(path not in bindings or bindings[path] == actual)
        bindings[path] = actual
        return actual
    try:
        # This small root-owned release gate is checked before reading raw saved
        # workloads, validating numerical arrays, or invoking any real bootstrap.
        bind(args.protocol, args.protocol_sha256); p = q.read(args.protocol)
        require(p['mode'] == 'timing' and p['pinned_source_revision'] == PIN)
        folder = Path(p['attempt_directory']); receipt_path = folder/'receipt.json'
        bind(receipt_path, args.receipt_sha256); r = q.read(receipt_path)
        bind(args.quiet_release, args.quiet_release_sha256); release = q.read(args.quiet_release)
        require(release['status'] == 'released' and release['receipt_sha256'] == args.receipt_sha256 and release['quiet_grant_sha256'] == p['quiet_grant']['sha256'] and release['cpu'] == p['cpu'], 'actual root quiet lease released for this exact terminal receipt')
        require(len(r['process_terminals']) == 6 and all(t['returncode'] == 0 and t['owned_group_gone'] is True for t in r['process_terminals']), 'all six numerical executables terminal before saved audit')
        bind(p['quiet_grant']['path'], p['quiet_grant']['sha256']); grant = q.read(p['quiet_grant']['path'])
        require(grant['status'] == 'granted' and grant['mode'] == 'timing' and grant['pinned_source_revision'] == PIN)
        require(grant['run_id'] == p['run_id'] and grant['attempt_directory'] == str(folder) and grant['cpu'] == p['cpu'] and grant['one_shot'] is True)
        require(grant['allowed_process_labels'] == LABELS and grant['cpu_exclusive'] is True and grant['no_other_project_compilers_or_numerics'] is True)
        require(grant['source_manifest_sha256'] == p['source_manifest_sha256'] and grant['aggregate_budget_seconds'] == p['aggregate_budget_seconds'] == 900 and grant['cleanup_postguard_reserve_seconds'] == p['cleanup_postguard_reserve_seconds'] == 30)
        require(type(grant['root_authority']) is str and grant['root_authority'].strip() and grant['grant_id'] == p['quiet_grant']['grant_id'])
        expect(r['quiet_grant'], p['quiet_grant'], 'actual terminal quiet grant context')
        report.update(receipt_path=str(receipt_path), receipt_sha256=args.receipt_sha256, protocol_sha256=args.protocol_sha256, quiet_release_sha256=args.quiet_release_sha256, quiet_release_checked_before_raw_and_statistics=True)
        for name in ['audit_saved.py', 'independent_preflight_primitives.py', 'independent_captured_primitives.py', 'independent_uncaptured_primitives.py', 'numeric_primitives.py', 'numeric-primitives-origin.json', 'source-origin.json', 'timing_statistics.py']:
            bind(Path(__file__).with_name(name))
        require(r['mode'] == 'timing' and r['pinned_source_revision'] == PIN and r['protocol_sha256'] == args.protocol_sha256 and r['run_id'] == p['run_id'] and r['cpu'] == p['cpu'])
        require(r['global_lifecycle_clean'] is True and r['guard_before'] is True and r['guard_after'] is True and r['cleanup_errors'] == [] and r['deadline_exceeded'] is False)
        require(not any(k in r for k in ['error', 'guard_error', 'cancellation']))
        require(0 <= r['numerical_elapsed_seconds'] <= r['cleanup_finished_elapsed_seconds'] <= r['elapsed_seconds'] <= 900)
        require(r['aggregate_budget_seconds'] == 900 and r['cleanup_postguard_reserve_seconds'] == 30)
        expect(p['request_policy']['orders'], [list(o) for o in ORDERS], 'all 24 engine permutations exactly twice, frozen seed173')
        expect(r['orders'], [list(o) for o in ORDERS], 'terminal order context')
        expect(r['ratio_inventory'], [{'numerator': a, 'denominator': b} for a, b in RATIOS], 'all five TIRust numerator ratios')
        for path, wanted in {**p['protected_sha256'], **p['tool_sha256'], **r['input_sha256']}.items():
            bind(path, wanted)
        require(set(r['executed_executables']) == set(LABELS))
        for label, item in r['executed_executables'].items():
            bind(item['path'], item['sha256']); require(item['sha256'] == p['processes'][label]['sha256'])
        preflight = p['preflight_admission']; bind(preflight['path'], preflight['sha256']); pa = q.read(preflight['path'])
        require(pa['status'] == 'passed' and pa['mode'] == 'preflight' and pa['all_families_and_controls_checked'] is True and pa['six_owned_processes_clean'] is True and pa['pinned_source_revision'] == PIN)
        bind(pa['receipt_path'], pa['receipt_sha256']); pr = q.read(pa['receipt_path'])
        bind(pa['full_review_path'], pa['full_review_sha256']); require(pr['cpu'] == p['cpu'])
        cases = q.read(p['inputs']); shape = q.read(p['control_shapes']); coords = [(case, batch) for case in cases for batch in [1, 32]]
        require([(case['n'], case['rank']) for case in cases] == [(2, 0), (2, 1), (3, 0), (3, 1)])
        expect([(row['id'], row['outer_batch']) for row in r['rows']], [(c['id'], batch) for c, batch in coords], 'all eight families remain visible')
        row_table = [{'id': c['id'], 'n': c['n'], 'rank': c['rank'], 'batch': batch, 'status': row['status'], 'ratios': []} for (c, batch), row in zip(coords, r['rows'])]
        anchors = {}; anchor_controls = {}
        for role, (rh, rawh, ah, reviewh) in pf.EXPECTED_QUALIFICATIONS.items():
            item = p['qualifications'][role]
            bind(item['receipt'], rh); bind(item['raw'], rawh); bind(item['independent_admission'], ah)
            admitted = q.read(item['independent_admission']); bind(admitted['full_review_path'], reviewh)
            require(admitted['status'] == 'passed' and admitted['full_review_sha256'] == reviewh)
            for event in [q.decode(line) for line in Path(item['raw']).read_text().splitlines()][1::2]:
                label = event['engine']+('-captured' if role == 'captured' else 'TIRust')
                if event['stage'] in ['initial', 'own-repeat']:
                    anchors[label, event['key'][0], event['key'][1], event['stage']] = event['response']
                elif event['stage'] == 'controls':
                    anchor_controls[label] = event['response']
        raw_path = folder/'raw.jsonl'; bind(raw_path, r['raw_sha256']); events = [q.decode(line) for line in raw_path.read_text().splitlines()]
        require(len(events) == 2*r['raw_request_count'])
        serial = 0; emitted = {label: [] for label in LABELS}; last_key = {label: None for label in TIRUST}; measured = 0
        def answer(label, wire, meta):
            nonlocal serial
            serial += 1
            require(serial <= r['raw_request_count'], 'missing required raw response')
            request, response = events[2*serial-2:2*serial]
            wanted = {'serial': serial, 'engine': label, 'payload': wire, **meta}
            expect(request, {**wanted, 'event': 'request'}, 'exact saved request serial/phase/payload')
            cap.keys(response, [*wanted, 'event', 'response']); require(response['event'] == 'response')
            expect({k: response[k] for k in wanted}, wanted, 'exact paired response metadata')
            emitted[label].append(response['response'])
            return response['response']
        def normal(label, body, case, batch, phase=None):
            (cap if label.endswith('-captured') else unc).normal(body, case, batch)
            key = (case['n'], case['rank'], 'Hybrid')
            require(body['result']['plan_reused'] is (last_key[label] == key), 'exact prepared plan reuse from complete process request history')
            last_key[label] = key
            target = anchors[label, case['id'], batch, phase or 'initial']
            expect(body if phase else pf.canonical(body), target if phase else pf.canonical(target), 'complete current full numerical record against admitted independent anchor')
        def cross(values):
            expect(values['baseline-captured'], values['candidate-captured'], 'complete cross-scheduler captured output')
            expect(values['baselineTIRust'], values['candidateTIRust'], 'complete cross-scheduler uncaptured output')
            for variant in ['baseline', 'candidate']:
                expect(pf.project(values[variant+'-captured']), pf.project(values[variant+'TIRust']), 'exact current-phase projection, retaining plan_reused')
        initialization = []
        for case, batch in coords:
            values = {}
            for label in TIRUST:
                for repeat in [0, 1]:
                    body = answer(label, payload(case, batch, label), {'stage': 'initialization', 'kind': 'initialization', 'id': case['id'], 'batch': batch, 'repeat': repeat})
                    normal(label, body, case, batch, 'initial' if repeat == 0 else 'own-repeat')
                    values[label, repeat] = body; initialization.append(serial)
            for repeat in [0, 1]: cross({label: values[label, repeat] for label in TIRUST})
        require(r['initialization']['status'] == 'passed'); expect(r['initialization']['raw_serials'], initialization, 'all64 initialization replies precede controls')
        def controls(stage, field):
            values = {}; indices = []
            for label in TIRUST:
                body = answer(label, 'CONTROLS\n', {'stage': stage, 'kind': 'controls'})
                (cap if label.endswith('-captured') else unc).controls(body, shape)
                expect(body, anchor_controls[label], 'all complete direct six-output controls and cache contexts')
                values[label] = body; indices.append(serial)
            cross(values); require(r[field]['status'] == 'passed'); expect(r[field]['raw_serials'], indices, 'exact control response serials')
        controls('controls-before', 'controls_before')
        reference_max = 0.0; reference_coefficients = 0; uv_max = 0.0
        def family(stage, row, case, batch):
            nonlocal reference_max, reference_coefficients, uv_max
            values = {}; indices = []
            for label in LABELS:
                body = answer(label, payload(case, batch, label), {'stage': stage, 'kind': 'qualification', 'id': case['id'], 'batch': batch})
                if label in TIRUST: normal(label, body, case, batch)
                else: pf.reference(body, case, batch, label == 'collier')
                values[label] = body; indices.append(serial)
            cross(values); expect(row[stage+'_raw_serials'], indices, 'exact full six-role family qualification response serials')
            for label in TIRUST:
                for oracle in ['iregi', 'collier']:
                    maximum, count = pf.compare(values[label]['result'], values[oracle], case, batch)
                    reference_max = max(reference_max, maximum); reference_coefficients += count
            maximum, count = pf.compare(values['collier'], values['iregi'], case, batch)
            reference_max = max(reference_max, maximum); reference_coefficients += count
            for label in LABELS:
                maximum, _ = pf.uv_identity(values[label]['result'] if label in TIRUST else values[label], case, batch)
                uv_max = max(uv_max, maximum)
            return values
        def measure(label, case, batch, n, warmup, stage, block, saved, before):
            nonlocal measured
            require(type(n) is int and 0 < n <= MAX_COUNT)
            body = answer(label, payload(case, batch, label, n, warmup), {'stage': stage, 'kind': 'timing', 'id': case['id'], 'batch': batch, 'iterations': n, 'warmup': warmup, 'block': block})
            elapsed, ns = timed_response(label, body, before, case, batch, n)
            require(saved['engine'] == label and type(saved['iterations']) is int and saved['iterations'] == n and saved['raw_serial'] == serial)
            expect(saved['elapsed_ns'], elapsed, 'saved interval reconstructed from full actual response')
            expect(saved['ns_per_call'], ns, 'saved ns/call exact response value')
            measured += 1
            return elapsed, ns
        cohort_complete = True
        for row_index, ((case, batch), row) in enumerate(zip(coords, r['rows'])):
            table = row_table[row_index]
            if row['status'] == 'unrun':
                cohort_complete = False; table['qualification'] = 'unrun'; continue
            before = family('before', row, case, batch)
            n = 1; require(1 <= len(row['calibration']) <= 8)
            last_intervals = None
            for index, group in enumerate(row['calibration']):
                expect([v['engine'] for v in group], ENGINES, 'calibration fixed four-engine order')
                intervals = [measure(label, case, batch, n, 10 if index == 0 else 0, 'calibration', index, saved, before)[0] for label, saved in zip(ENGINES, group)]
                minimum = min(intervals); last_intervals = intervals
                if index+1 < len(row['calibration']):
                    require(minimum < MINIMUM_NS, 'no extra calibration after target admission')
                    n = max(n+1, math.ceil(n*TARGET_NS/minimum)); require(n <= MAX_COUNT, 'shared signed32 calibration overflow')
            require(row['iterations'] == n and type(row['iterations']) is int)
            calibrated = min(last_intervals) >= MINIMUM_NS
            if not calibrated:
                require(len(row['calibration']) == 8 and row['status'] == 'calibration-inconclusive' and row['blocks'] == [])
                cohort_complete = False
            if calibrated and row['status'] == 'budget-inconclusive':
                require(row['blocks'] == [] and row['estimated_acceptance_seconds'] == 48*sum(last_intervals)/1e9 and row['estimated_acceptance_seconds']+2 > row['remaining_work_seconds'])
                cohort_complete = False
            blocks = row['blocks']; timings = {label: [] for label in ENGINES}; short = 0
            require(len(blocks) <= 48)
            for index, block in enumerate(blocks):
                require(calibrated and block['index'] == index)
                expect(block['order'], list(ORDERS[index]), 'exact balanced permutation order')
                expect([value['engine'] for value in block['engines']], list(ORDERS[index]), 'all four engine samples, no exclusion')
                for label, saved in zip(ORDERS[index], block['engines']):
                    elapsed, ns = measure(label, case, batch, n, 0, 'acceptance', index, saved, before)
                    timings[label].append(ns); short += elapsed < MINIMUM_NS
            if len(blocks) == 48:
                require(row['short_blocks'] == short and row['status'] == ('short-block-inconclusive' if short else 'completed'))
                require(row['estimated_acceptance_seconds'] == 48*sum(last_intervals)/1e9)
                require(row['estimated_acceptance_seconds']+2 <= row['remaining_work_seconds'], 'acceptance launch honored frozen conservative budget estimate')
            else:
                cohort_complete = False
            after = family('after', row, case, batch)
            require(row['before_after_qualification'] == 'passed' and 'error' not in row)
            for label in LABELS:
                if label in TIRUST:
                    expect(pf.canonical(before[label]), pf.canonical(after[label]), 'complete own before/after arrays and observational masters')
                else:
                    fields = ['id', 'stable', 'clock_ticks_per_second', 'lanes']+(['collier_mode', 'pole_check_errors'] if label == 'collier' else [])
                    expect({k: before[label][k] for k in fields}, {k: after[label][k] for k in fields}, 'complete own reference before/after arrays and poles')
            table.update(iterations=n, calibration_rounds=len(row['calibration']), quartets=len(blocks), short_blocks=short, qualification='passed', timings_ns=timings)
        controls('controls-after', 'controls_after')
        require(serial == r['raw_request_count'], 'no omitted/extra/duplicate raw events or timing observations')
        expect([p['label'] for p in r['processes']], LABELS, 'all six launch roles')
        expect([p['label'] for p in r['process_terminals']], LABELS, 'all six terminal roles')
        for process, terminal in zip(r['processes'], r['process_terminals']):
            label = process['label']
            expect(process['command'], [p['taskset'], '-c', str(p['cpu']), r['executed_executables'][label]['path']], 'same pinned CPU in every actual child launch')
            require(process['owned_process_group'] == terminal['owned_process_group'] and terminal['received_responses'] == len(emitted[label]))
            try: os.killpg(terminal['owned_process_group'], 0)
            except ProcessLookupError: pass
            else: require(False, 'owned process group remains during postrelease saved audit')
            for stream in ['stdout', 'stderr']:
                path = folder/(label+'.'+stream+'.log'); require(path.is_file() and not path.is_symlink()); bind(path, r[stream+'_sha256'][label])
            stdout = (folder/(label+'.stdout.log')).read_text()
            expect([q.decode(line[7:]) for line in stdout.splitlines() if line.startswith('RESULT ')], emitted[label], 'every persisted RESULT response equals exact raw sequence')
            require((folder/(label+'.stderr.log')).read_bytes() == b'', 'unexpected timing stderr')
        summary_path = folder/'summary.json'; bind(summary_path); produced = q.read(summary_path)
        require(produced['global_admission_errors'] == [] and len(produced['rows']) == 8)
        require(produced['receipt_sha256'] == args.receipt_sha256 and produced['raw_sha256'] == r['raw_sha256'])
        require(produced['quiet_release']['sha256'] == args.quiet_release_sha256)
        if cohort_complete:
            require(r['status'] == ('completed-with-inconclusive-rows' if any(t['short_blocks'] for t in row_table) else 'completed'), 'terminal aggregate status explained by complete raw-derived family statuses')
        # All source, log and numerical admission precedes the independent real
        # bootstrap. This import itself contains no experiment or startup work.
        import timing_statistics as statistics
        for table, saved_row in zip(row_table, produced['rows']):
            require(table['id'] == saved_row['id'] and table['batch'] == saved_row['batch'])
            require(table['status'] == saved_row['status'] and saved_row['admission_errors'] == [])
            require(table.get('quartets', 0) == saved_row['quartets'] and table.get('short_blocks', 0) == saved_row['short_blocks'])
            if table.get('quartets') != 48:
                table['ratios'] = [{'numerator': a, 'denominator': b, 'gate': 'inconclusive-incomplete-family', 'statistics': None} for a, b in RATIOS]
                continue
            short = table['short_blocks'] > 0
            for index, (numerator, denominator) in enumerate(RATIOS):
                left, right = table['timings_ns'][numerator], table['timings_ns'][denominator]
                admitted = cohort_complete
                calculated = statistics.summarize(left, right, admitted=admitted, short=short)
                saved = saved_row['ratios'][index]
                require(saved['numerator'] == numerator and saved['denominator'] == denominator)
                # Compare every numerical bootstrap result and all raw ratios,
                # never trusting the producer's summarized gate alone.
                for key in ['samples', 'median', 'ci99', 'relative_ci_width']:
                    expect(saved['statistics'][key], calculated[key], 'independent overall10000-sample seed173 bootstrap '+key)
                expect(saved['statistics']['gate'], calculated.get('historical_gate', calculated['gate']), 'retained nested historical statistic gate')
                expect(saved['gate'], calculated['gate'], 'independent family ratio admission gate')
                for first in [True, False]:
                    indices = [i for i, order in enumerate(ORDERS) if (order.index(numerator) < order.index(denominator)) is first]
                    require(len(indices) == 24)
                    sub = statistics.summarize([left[i] for i in indices], [right[i] for i in indices], admitted=admitted, short=short)
                    observed = saved['order_strata']['numerator_first' if first else 'denominator_first']
                    for key in ['samples', 'median', 'ci99', 'relative_ci_width']:
                        expect(observed[key], sub[key], 'independent balanced24-sample order stratum '+key)
                    expect(observed['gate'], sub.get('historical_gate', sub['gate']), 'retained order-stratum statistical gate')
                require(saved['slower_pairs'] == sum(a > b for a, b in zip(left, right)))
                item = {'numerator': numerator, 'denominator': denominator, 'definition': numerator+' / '+denominator, 'median': calculated['median'], 'ci99': calculated['ci99'], 'relative_ci_width': calculated['relative_ci_width'], 'gate': calculated['gate'], 'short_blocks': table['short_blocks'], 'slower_pairs': saved['slower_pairs']}
                table['ratios'].append(item)
                raw_ratios.append({'id': table['id'], 'n': table['n'], 'rank': table['rank'], 'batch': table['batch'], 'iterations': table['iterations'], 'quartets': table['quartets'], **item})
        for path, wanted in bindings.items(): require(pf.digest(path) == wanted, 'postaudit bound file changed '+str(path))
        require(time.monotonic()-started <= AUDIT_CAP_SECONDS)
        report.update(status='passed' if cohort_complete else 'inconclusive-incomplete-cohort', raw_sha256=r['raw_sha256'], raw_event_count=len(events), request_count=serial,
            all_complete_raw_records_and_controls_checked=True, all_timed_own_arrays_checked=True, six_owned_processes_clean=True,
            all_calibration_and_balanced_quartets_checked=True, all_ratio_and_bootstrap_values_independently_recomputed=True,
            cohort_complete=cohort_complete, ratio_count=len(raw_ratios), reference_compared_coefficients=reference_coefficients,
            reference_maximum_dimensionally_normalized_error=reference_max, UV_maximum_normalized_error=uv_max,
            measured_response_count=measured, real_bootstrap_executed_after_quiet_release=True, preflight_numerical_scope_retained=True,
            static_Dual_qualified=False, higher_Dual_qualified=False, mixed_Dual_qualified=False,
            source_artifact_data_bindings=len(bindings), gate_counts=dict(Counter(item['gate'] for item in raw_ratios)))
    except Exception as error:
        report.update(status='failed', error=repr(error))
        for row in row_table:
            if not row['ratios']:
                row['ratios'] = [{'numerator': a, 'denominator': b, 'gate': 'global-audit-failed', 'statistics': None} for a, b in RATIOS]
    finally:
        signal.alarm(0); signal.signal(signal.SIGALRM, previous_alarm)
    report.update(checks=q.CHECKS, bindings_sha256={str(path): h for path, h in bindings.items()}, rows=row_table,
        audit_elapsed_seconds_diagnostic=time.monotonic()-started, finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    target = out/'full-review.json'; target.write_text(json.dumps(report, indent=2)+'\n')
    (out/'ratio-table.json').write_text(json.dumps(raw_ratios, indent=2)+'\n')
    if raw_ratios:
        columns = ['id', 'n', 'rank', 'batch', 'iterations', 'quartets', 'numerator', 'denominator', 'median', 'ci99_low', 'ci99_high', 'relative_ci_width', 'gate', 'short_blocks', 'slower_pairs']
        with (out/'ratio-table.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=columns); writer.writeheader()
            for row in raw_ratios:
                item = {key: row[key] for key in columns if key not in ['ci99_low', 'ci99_high']}
                item.update(ci99_low=row['ci99'][0], ci99_high=row['ci99'][1]); writer.writerow(item)
    if report['status'] == 'passed':
        compact = {key: report[key] for key in ['status', 'mode', 'pinned_source_revision', 'receipt_path', 'receipt_sha256', 'raw_sha256', 'protocol_sha256', 'quiet_release_sha256', 'cohort_complete', 'ratio_count', 'all_complete_raw_records_and_controls_checked', 'all_timed_own_arrays_checked', 'all_calibration_and_balanced_quartets_checked', 'all_ratio_and_bootstrap_values_independently_recomputed', 'six_owned_processes_clean', 'gate_counts']}
        compact.update(full_review_path=str(target), full_review_sha256=pf.digest(target), ratio_table_path=str(out/'ratio-table.json'), ratio_table_sha256=pf.digest(out/'ratio-table.json'))
        (out/'admission.json').write_text(json.dumps(compact, indent=2)+'\n')
    print(json.dumps({'status': report['status'], 'full_review_path': str(target), 'full_review_sha256': pf.digest(target), 'checks': q.CHECKS, 'error': report.get('error'), 'ratio_count': len(raw_ratios)}))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
