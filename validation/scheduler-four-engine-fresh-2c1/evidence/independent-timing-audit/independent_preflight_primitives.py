"""Independent saved six-process preflight audit; no child processes or bootstrap.

The numeric schema routines are byte-for-byte copies of earlier independent
saved-data checkers. No producer validator, numerical library or executable is
imported. Every reference tensor coefficient is compared afresh below.
"""
from collections import Counter
from pathlib import Path
import argparse
import copy
import datetime
import hashlib
import json
import math
import os
import time

import numeric_primitives as q
import independent_captured_primitives as cap
import independent_uncaptured_primitives as unc

ROOT = Path('/shared/external/iregi/iregi-rust')
BASE = ROOT/'target/guard-performance-review/optimized-performance-proposal'
HERE = BASE/'fresh-four-engine-proposal'
PIN = '2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2'
PROTOCOL = '5eaeb1bf6a5085226333f65c9836c6cf897488d31efa108f9507c257ee070886'
LABELS = ['baseline-captured', 'candidate-captured', 'baselineTIRust', 'candidateTIRust', 'iregi', 'collier']
TIRUST = LABELS[:4]
EXPECTED_QUALIFICATIONS = {
    'captured': ('0450b25c2a806c81f4410f567b370612f82401d9a322cb2f87d4115f53770232', '750310b9290ae9e9aa6f396dfae5837187dbf9f451bdc1fce950f5d2a288b21e', '39e63fef002b9d05ff6aa689666ce0b175b9d637c1198ccf5eaffe1462b594f2', 'baa1997b374ea6cc3b65ede4ce64c6877f7767d7e0406b7c6b6a9a000999af0d'),
    'uncaptured': ('025642a833720322bb0ca1377118de4cda0c677d18c7c45891785f379bd74a23', 'ac1a9267ad5325a6bcfca5269b0bb0c82314e226ab954dd918e65a69732c4ba7', '6e4974887796893db7feedf9c69c539b7fefce389885010027b85ec609b62f0a', 'd5b346f8efb78821ef8356485e8013a9a278322486e7535e60f0795ed997eb60'),
}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def expect(actual, wanted, context):
    q.require(cap.exact(actual, wanted), context)


def project(body):
    """Independent projection; preserve all other fields and plan_reused."""
    def visit(node):
        if type(node) is dict:
            return {k: visit(v) for k, v in node.items() if k != 'master_captures'}
        if type(node) is list:
            return [visit(v) for v in node]
        return copy.deepcopy(node)
    value = visit(body)
    if type(value) is dict and set(value) == {'id', 'result'}:
        q.require('scope' in value['result'] and 'capture_enabled' in value['result'])
        del value['result']['scope']; del value['result']['capture_enabled']
    return value


def canonical(body):
    value = copy.deepcopy(body)
    del value['result']['plan_reused']
    return value


def rust_payload(case, batch):
    return json.dumps({'id': case['id'], 'n': case['n'], 'rank': case['rank'], 'algorithm': 'Hybrid', 'samples': case['samples'][:batch]}, allow_nan=False)+'\n'


def reference_payload(case, batch, collier):
    samples = case['samples'][:batch]
    mu = samples[0]['mu']
    q.require(all(s['mu'] == mu for s in samples))
    lines = [f'{"CHECK" if collier else "BENCH"} {case["id"]} {1 if collier else 2} {case["n"]} {case["rank"]} {mu:.17g} {batch} 0 1 1']
    for sample in samples:
        for shift, mass in zip(sample['shifts'], sample['masses']):
            lines.append(' '.join(f'{x:.17g}' for x in shift)+f' ({mass[0]:.17g},{mass[1]:.17g})')
    return '\n'.join(lines)+'\n'


def energy(sample):
    return max(1.0, sample['mu'], *(abs(x) for p in sample['shifts'] for x in p), *(math.sqrt(math.hypot(*m)) for m in sample['masses']))


def reference(value, case, batch, collier):
    expected = ['id', 'stable', 'clock_ticks_per_second', 'total_ns', 'lanes']
    if collier:
        expected += ['collier_mode', 'pole_check_errors']
    cap.keys(value, expected)
    q.require(value['id'] == case['id'] and value['stable'] is True)
    q.natural(value['clock_ticks_per_second'])
    q.require(value['clock_ticks_per_second'] > 0)
    interval = q.array(value['total_ns'], 1)[0]
    q.require(type(interval) in (int, float) and math.isfinite(interval) and interval > 0)
    degrees = [0] if case['rank'] == 0 else [0, 1, 1, 1, 1]
    count = 0
    for lane in q.array(value['lanes'], batch):
        cap.keys(lane, ['status', 'moments'])
        q.require(lane['status'] == 'success')
        for moment in q.array(lane['moments'], len(degrees)):
            for pole in q.array(moment, 4):
                q.f64_complex(pole)
                count += 1
    if collier:
        q.require(type(value['collier_mode']) is int and value['collier_mode'] == 1)
        for lane in q.array(value['pole_check_errors'], batch):
            for item in q.array(lane, 3):
                q.require(type(item) in (int, float) and math.isfinite(item) and 0 <= item <= 1e-12, 'COLLIER independent delta-parameter separated-pole probe')
    return count


def compare(actual, expected, case, batch):
    """All native UV/IR/finite coefficients, dimensionally normalized 1e-10."""
    maximum = 0.0
    count = 0
    degrees = [0] if case['rank'] == 0 else [0, 1, 1, 1, 1]
    for left, right, sample in zip(q.array(actual['lanes'], batch), q.array(expected['lanes'], batch), case['samples'][:batch]):
        for a, b, degree in zip(q.array(left['moments'], len(degrees)), q.array(right['moments'], len(degrees)), degrees):
            unit = energy(sample)**(4+degree-2*case['n'])
            for av, bv in zip(q.array(a, 4), q.array(b, 4)):
                ar, ai = q.f64_complex(av); br, bi = q.f64_complex(bv)
                error = math.hypot(ar-br, ai-bi)/(unit+math.hypot(br, bi))
                q.require(math.isfinite(error) and error <= 1e-10, 'independent complete reference coefficient agreement')
                maximum = max(maximum, error); count += 1
    return maximum, count


def uv_identity(value, case, batch):
    maximum = 0.0
    count = 0
    for lane, sample in zip(q.array(value['lanes'], batch), case['samples'][:batch]):
        wanted = [(0.0, math.pi**2)] if case['n'] == 2 else [(0.0, 0.0)]
        if case['rank'] == 1:
            wanted += [(0.0, -math.pi**2*x/2) if case['n'] == 2 else (0.0, 0.0) for x in sample['shifts'][1]]
        for index, (moment, target) in enumerate(zip(q.array(lane['moments'], len(wanted)), wanted)):
            re, im = q.f64_complex(q.array(moment, 4)[0])
            error = math.hypot(re-target[0], im-target[1])/(energy(sample)**(4+int(index > 0)-2*case['n'])+math.hypot(*target))
            q.require(math.isfinite(error) and error <= 1e-10, 'independent B/B-vector/C/C-vector bare UV identity')
            maximum = max(maximum, error); count += 1
    return maximum, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt-sha256', required=True)
    parser.add_argument('--output-directory', type=Path, required=True)
    args = parser.parse_args()
    q.require(Path.cwd() == ROOT)
    out = args.output_directory.resolve(); out.mkdir(exist_ok=False)
    started = time.monotonic(); bindings = {}
    report = {'schema_version': 1, 'status': 'checking', 'mode': 'preflight', 'reviewer': '/root/scheduler_perf_resume/fresh_recipe_audit', 'pinned_source_revision': PIN,
              'scope': 'Independent saved six-process numerical/schema/reference/provenance preflight audit. No producer validator imported, no child process, compiler, metadata decoder, integral or bootstrap launched.',
              'performance_qualified': False, 'production_adoption_authorized': False}
    def bind(path, wanted=None):
        path = Path(path)
        q.require(path.is_absolute(), 'absolute binding path')
        actual = digest(path)
        q.require(wanted is None or actual == wanted, 'changed binding '+str(path))
        q.require(path not in bindings or bindings[path] == actual)
        bindings[path] = actual
        return actual
    try:
        for name in ['audit_saved.py', 'independent_captured_primitives.py', 'independent_uncaptured_primitives.py', 'numeric_primitives.py', 'numeric-primitives-origin.json', 'source-origin.json']:
            bind(Path(__file__).with_name(name))
        protocol_path = HERE/'preflight-fresh2c1-001-protocol.json'
        bind(protocol_path, PROTOCOL); p = q.read(protocol_path)
        q.require(p['mode'] == 'preflight' and p['pinned_source_revision'] == PIN and p['quiet_grant'] is None and p['preflight_admission'] is None)
        q.require((p['cpu'], p['aggregate_budget_seconds'], p['cleanup_postguard_reserve_seconds'], p['effective_work_deadline_seconds']) == (34, 180, 20, 160))
        folder = Path(p['attempt_directory'])
        receipt_path = folder/'receipt.json'; bind(receipt_path, args.receipt_sha256); r = q.read(receipt_path)
        report.update(receipt_path=str(receipt_path), receipt_sha256=args.receipt_sha256, protocol_sha256=PROTOCOL)
        q.require(r['status'] == 'completed-preflight' and r['mode'] == 'preflight' and r['protocol_sha256'] == PROTOCOL)
        q.require(r['global_lifecycle_clean'] is True and r['guard_before'] is True and r['guard_after'] is True)
        q.require(r['cleanup_errors'] == [] and r['deadline_exceeded'] is False and not any(k in r for k in ['error', 'guard_error', 'cancellation']))
        q.require(r['pinned_source_revision'] == PIN and r['cpu'] == p['cpu'] and r['run_id'] == p['run_id'])
        q.require(r['protocol'] == str(protocol_path) and r['aggregate_budget_seconds'] == 180 and r['cleanup_postguard_reserve_seconds'] == 20)
        q.require(0 <= r['numerical_elapsed_seconds'] <= r['cleanup_finished_elapsed_seconds'] <= r['elapsed_seconds'] <= 180)
        expect(r['quiet_grant'], None, 'no timing resource grant in preflight')
        q.require(r['raw_request_count'] == 168, 'complete six-process request inventory')
        for path, wanted in {**p['protected_sha256'], **p['tool_sha256'], **r['input_sha256']}.items():
            bind(path, wanted)
        expect(r['orders'], p['request_policy']['orders'], 'retained order context only')
        expect(r['ratio_inventory'], p['statistics']['ratios'], 'TIRust numerator inventory only')
        q.require(set(r['executed_executables']) == set(LABELS))
        for label in LABELS:
            item = r['executed_executables'][label]
            bind(item['path'], item['sha256'])
            q.require(item['sha256'] == p['processes'][label]['sha256'])
        cases = q.read(p['inputs']); shape = q.read(p['control_shapes'])
        coords = [(case, batch) for case in cases for batch in [1, 32]]
        q.require([(case['n'], case['rank']) for case in cases] == [(2, 0), (2, 1), (3, 0), (3, 1)])
        # All earlier complete qualification evidence is bound, never replaced by
        # producer boolean flags. Current records are validated again below.
        anchors = {}; anchor_controls = {}
        for role, (rh, rawh, ah, reviewh) in EXPECTED_QUALIFICATIONS.items():
            item = p['qualifications'][role]
            bind(item['protocol'], item['protocol_sha256']); bind(item['receipt'], rh)
            bind(item['raw'], rawh); bind(item['independent_admission'], ah)
            admission = q.read(item['independent_admission'])
            q.require(admission['status'] == 'passed' and admission['pinned_source_revision'] == PIN and admission['receipt_sha256'] == rh and admission['raw_sha256'] == rawh)
            q.require(admission['request_count'] == 60 and admission['raw_event_count'] == 120 and admission['all_complete_records_and_controls_checked'] is True)
            bind(admission['full_review_path'], reviewh)
            q.require(admission['full_review_sha256'] == reviewh)
            saved = [q.decode(line) for line in Path(item['raw']).read_text().splitlines()]
            q.require(len(saved) == 120)
            for event in saved[1::2]:
                stage, key, variant = event['stage'], event['key'], event['engine']
                label = variant+('-captured' if role == 'captured' else 'TIRust')
                if stage in ['initial', 'own-repeat', 'retained']:
                    anchors[label, key[0], key[1], stage] = event['response']
                elif stage == 'controls':
                    anchor_controls[label] = event['response']
        schedule = []
        for case, batch in coords:
            for label in TIRUST:
                for repeat in [0, 1]:
                    schedule.append((label, rust_payload(case, batch), {'stage': 'initialization', 'kind': 'initialization', 'id': case['id'], 'batch': batch, 'repeat': repeat}))
        schedule += [(label, 'CONTROLS\n', {'stage': 'controls-before', 'kind': 'controls'}) for label in TIRUST]
        for case, batch in coords:
            for stage in ['before', 'after']:
                for label in LABELS:
                    wire = rust_payload(case, batch) if label in TIRUST else reference_payload(case, batch, label == 'collier')
                    schedule.append((label, wire, {'stage': stage, 'kind': 'qualification', 'id': case['id'], 'batch': batch}))
        schedule += [(label, 'CONTROLS\n', {'stage': 'controls-after', 'kind': 'controls'}) for label in TIRUST]
        q.require(len(schedule) == 168)
        raw_path = folder/'raw.jsonl'; bind(raw_path, r['raw_sha256'])
        events = [q.decode(line) for line in raw_path.read_text().splitlines()]
        q.require(len(events) == 336)
        records = {}; emitted = {label: [] for label in LABELS}; last_key = {label: None for label in TIRUST}
        by_id = {case['id']: case for case in cases}; tensors = Counter(); captures = Counter(); reference_values = Counter(); controls_checked = 0
        for serial, (label, wire, meta) in enumerate(schedule, 1):
            request, answer = events[2*serial-2:2*serial]
            wanted = {'serial': serial, 'engine': label, 'payload': wire, **meta}
            expect(request, {**wanted, 'event': 'request'}, 'exact raw request/order/phase/payload')
            cap.keys(answer, [*wanted, 'event', 'response'])
            expect({k: answer[k] for k in wanted}, wanted, 'exact paired raw response metadata')
            q.require(answer['event'] == 'response')
            body = answer['response']; emitted[label].append(body)
            if meta['kind'] == 'controls':
                (cap if label.endswith('-captured') else unc).controls(body, shape)
                expect(body, anchor_controls[label], 'complete direct six-output controls equal independently admitted anchor')
                controls_checked += 1
                records[meta['stage'], label] = body
                continue
            case, batch = by_id[meta['id']], meta['batch']
            if label in TIRUST:
                stats = (cap if label.endswith('-captured') else unc).normal(body, case, batch)
                tensors[label] += stats['tensor_complex_values']; captures[label] += stats['master_complex_values']
                key = (case['n'], case['rank'], 'Hybrid')
                q.require(body['result']['plan_reused'] is (last_key[label] == key), 'exact current prepared-workspace reuse from full saved request history')
                last_key[label] = key
                phase = 'initial' if meta.get('repeat') == 0 else 'own-repeat' if meta['stage'] == 'initialization' else 'initial'
                anchor = anchors[label, case['id'], batch, phase]
                if meta['stage'] == 'initialization':
                    expect(body, anchor, 'complete initialization phase including plan_reused')
                else:
                    expect(canonical(body), canonical(anchor), 'complete family tensor/master output equals independent qualified anchor')
            else:
                reference_values[label] += reference(body, case, batch, label == 'collier')
            records[(meta['stage'], case['id'], batch, label, meta.get('repeat'))] = body
        def cross(values):
            expect(values['baseline-captured'], values['candidate-captured'], 'complete captured cross-scheduler result')
            expect(values['baselineTIRust'], values['candidateTIRust'], 'complete uncaptured cross-scheduler result')
            for variant in ['baseline', 'candidate']:
                expect(project(values[variant+'-captured']), project(values[variant+'TIRust']), 'complete same-phase captured projection preserving plan_reused')
        for case, batch in coords:
            for repeat in [0, 1]:
                cross({label: records['initialization', case['id'], batch, label, repeat] for label in TIRUST})
        for stage in ['controls-before', 'controls-after']:
            cross({label: records[stage, label] for label in TIRUST})
        for label in TIRUST:
            expect(records['controls-before', label], records['controls-after', label], 'complete own before/after controls')
        comparison_max = uv_max = 0.0
        compared_coefficients = uv_coefficients = 0
        for case, batch in coords:
            for stage in ['before', 'after']:
                values = {label: records[stage, case['id'], batch, label, None] for label in LABELS}
                cross({label: values[label] for label in TIRUST})
                for label in TIRUST:
                    for oracle in ['iregi', 'collier']:
                        maximum, count = compare(values[label]['result'], values[oracle], case, batch)
                        comparison_max = max(comparison_max, maximum); compared_coefficients += count
                maximum, count = compare(values['collier'], values['iregi'], case, batch)
                comparison_max = max(comparison_max, maximum); compared_coefficients += count
                for label in LABELS:
                    maximum, count = uv_identity(values[label]['result'] if label in TIRUST else values[label], case, batch)
                    uv_max = max(uv_max, maximum); uv_coefficients += count
            for label in LABELS:
                before = records['before', case['id'], batch, label, None]
                after = records['after', case['id'], batch, label, None]
                if label in TIRUST:
                    expect(canonical(before), canonical(after), 'complete own before/after TIRust record except independently validated reuse')
                else:
                    fields = ['id', 'stable', 'clock_ticks_per_second', 'lanes']+(['collier_mode', 'pole_check_errors'] if label == 'collier' else [])
                    expect({k: before[k] for k in fields}, {k: after[k] for k in fields}, 'complete own reference before/after numerical and pole records')
        q.require(controls_checked == 8)
        q.require(r['initialization']['status'] == 'passed' and r['initialization']['raw_serials'] == list(range(1, 65)))
        for key, indices in [('controls_before', list(range(65, 69))), ('controls_after', list(range(165, 169)))]:
            q.require(r[key]['status'] == 'passed' and r[key]['raw_serials'] == indices)
        q.require([(row['id'], row['outer_batch']) for row in r['rows']] == [(case['id'], batch) for case, batch in coords])
        for index, row in enumerate(r['rows']):
            q.require(row['status'] == 'admitted-without-timings' and row['before_after_qualification'] == 'passed' and 'error' not in row)
            expect(row['calibration'], [], 'preflight has no calibration'); expect(row['blocks'], [], 'preflight has no timing quartets')
            expect(row['before_raw_serials'], list(range(69+12*index, 75+12*index)), 'before six-role response serials')
            expect(row['after_raw_serials'], list(range(75+12*index, 81+12*index)), 'after six-role response serials')
        counts = Counter(label for label, _, _ in schedule)
        q.require(len(r['processes']) == len(r['process_terminals']) == 6)
        expect([item['label'] for item in r['processes']], LABELS, 'all six process launch roles')
        expect([item['label'] for item in r['process_terminals']], LABELS, 'all six terminal roles')
        for process, terminal in zip(r['processes'], r['process_terminals']):
            label = process['label']
            expect(process['command'], [p['taskset'], '-c', '34', r['executed_executables'][label]['path']], 'actual bounded CPU34 executable')
            q.require(process['owned_process_group'] == terminal['owned_process_group'] and terminal['returncode'] == 0 and terminal['owned_group_gone'] is True and terminal['received_responses'] == counts[label])
            try:
                os.killpg(terminal['owned_process_group'], 0)
            except ProcessLookupError:
                pass
            else:
                q.require(False, 'owned process group unexpectedly remains')
            for stream in ['stdout', 'stderr']:
                log = folder/(label+'.'+stream+'.log')
                q.require(log.is_file() and not log.is_symlink())
                bind(log, r[stream+'_sha256'][label])
            stdout = (folder/(label+'.stdout.log')).read_text()
            expect([q.decode(line[7:]) for line in stdout.splitlines() if line.startswith('RESULT ')], emitted[label], 'all persisted stdout RESULT records equal raw responses')
            q.require((folder/(label+'.stderr.log')).read_bytes() == b'', 'unexpected preflight stderr')
        summary_path = folder/'summary.json'; bind(summary_path); summary = q.read(summary_path)
        q.require(summary['status'] == 'passed-preflight-admission' and summary['mode'] == 'preflight' and summary['global_admission_errors'] == [] and len(summary['rows']) == 8)
        q.require(summary['receipt_sha256'] == args.receipt_sha256 and summary['raw_sha256'] == r['raw_sha256'])
        for row in summary['rows']:
            q.require(row['quartets'] == 0 and row['short_blocks'] == 0 and row['admission_errors'] == [])
            q.require(len(row['ratios']) == 5 and all(item['gate'] == 'not-measured-preflight' and item['statistics'] is None for item in row['ratios']))
        for path, wanted in bindings.items():
            q.require(digest(path) == wanted, 'postaudit changed file '+str(path))
        report.update(status='passed', raw_sha256=r['raw_sha256'], request_count=168, raw_event_count=336,
            all_families_and_controls_checked=True, six_owned_processes_clean=True, initialization_case_replies=64,
            controls_replies=8, family_before_after_replies=96, complete_tensor_values_by_TIRust_role=dict(tensors),
            complete_observational_master_values_by_TIRust_role=dict(captures), complete_reference_tensor_values=dict(reference_values),
            reference_compared_complex_coefficients=compared_coefficients, reference_maximum_dimensionally_normalized_error=comparison_max,
            independent_UV_coefficients=uv_coefficients, independent_UV_maximum_normalized_error=uv_max,
            collier_separated_pole_probes_checked=True, current_history_plan_reused_checked_exactly=True,
            all_current_phase_capture_projections_checked=True, all_six_direct_master_outputs_checked=True,
            dynamic_Dual_runtime_scope={'component_type': 'f64', 'shapes': [[[0], [1]], [[0]]]},
            static_Dual_qualified=False, higher_Dual_qualified=False, mixed_Dual_qualified=False,
            source_artifact_data_bindings=len(bindings), producer_validator_imported=False, subprocesses_launched=0,
            real_bootstrap_executed=False, no_performance_conclusion_from_lifecycle_duration=True)
    except Exception as error:
        report.update(status='failed', error=repr(error))
    report['checks'] = q.CHECKS
    report['bindings_sha256'] = {str(path): h for path, h in bindings.items()}
    report['audit_elapsed_seconds_diagnostic'] = time.monotonic()-started
    report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    target = out/'full-review.json'; target.write_text(json.dumps(report, indent=2)+'\n')
    if report['status'] == 'passed':
        contract = {key: report[key] for key in ['status', 'mode', 'receipt_path', 'receipt_sha256', 'raw_sha256', 'all_families_and_controls_checked', 'six_owned_processes_clean', 'pinned_source_revision']}
        contract.update(full_review_path=str(target), full_review_sha256=digest(target))
        (out/'admission.json').write_text(json.dumps(contract, indent=2)+'\n')
    print(json.dumps({'status': report['status'], 'full_review_path': str(target), 'full_review_sha256': digest(target), 'checks': q.CHECKS, 'error': report.get('error')}))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
