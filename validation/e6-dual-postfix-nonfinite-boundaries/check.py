"""Replay the two original SAMPLE nonfinite failure packets, using saved bytes only."""
from pathlib import Path
import argparse
import hashlib
import json
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = 'validation/e6-dual-postfix-resource-boundaries'
PREFIX = '/shared/external/iregi/iregi-rust/'
SHAPE = [[0, 0], [1, 0], [2, 0]]


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
        need(desc((ROOT / name).read_bytes()) == row, 'immutable inherited file identity')
    parent_body = (ROOT / PARENT / 'manifest.json').read_bytes()
    need(sha(parent_body) == manifest['parent_manifest_sha256'], 'actual historical source/resource parent')
    parent = runpy.run_path(str(ROOT / PARENT / 'check.py'), run_name='saved_resource_parent_loader')
    inherited = parent['restore_files'](load(parent_body))
    own = parent['unpack']((HERE / 'payload.tar.gz').read_bytes(), manifest['payload_members'], complete=True)
    files = dict(inherited)
    for alias, row in manifest['aliases'].items():
        parent['safe'](alias)
        body = inherited[row['parent_alias']] if 'parent_alias' in row else own[row['member']]
        need(desc(body) == {k: row[k] for k in ['sha256', 'bytes']}, 'actual selected saved bytes')
        need(alias not in files or files[alias] == body, 'no conflicting inherited source alias')
        files[alias] = body
    return files


def replay(manifest, files):
    def read(alias):
        return load(files[alias])

    omitted = manifest['omitted_native_artifacts']
    total_guards = 0
    outcomes = []
    for item in manifest['attempts']:
        root, base = item['root_alias'], item['capture_alias']
        receipt = read(base + '/receipt.json')
        protocol = read(root + '/protocol.json')
        capture = read(base + '/capture.json')
        diagnosis = read(root + '/saved-nonfinite-diagnosis.json')
        audit = read(root + '/failed-mechanism-audit.json')
        need(sha(files[base + '/receipt.json']) == item['receipt_sha256']
             and sha(files[root + '/saved-nonfinite-diagnosis.json']) == item['diagnosis_sha256'],
             'actual terminal receipt and additive diagnosis pins')
        need(receipt['status'] == 'failed_capture_retained' and receipt['inputs_unchanged'] is True
             and receipt['cleanup_errors'] == [] and len(receipt['inputs']) == 264
             and len(receipt['steps']) == 1, 'actual complete failure guard and ownership evidence')
        need(receipt['address_space_limit_bytes'] == 96 * 1024**3
             and receipt['working_bits'] == item['working_bits'] and receipt['requested_bits'] == 53,
             'actual 96 GiB precision request')
        step = receipt['steps'][0]
        need(step['status'] == 'failed' and step['returncode'] == 101 and not step.get('timeout', False)
             and step['owned_group_gone'] is True and step['timeout_seconds'] == 7200,
             'actual nonfinite test failure, not deadline or allocation boundary')
        for absolute, digest in receipt['inputs'].items():
            if absolute in omitted:
                need(omitted[absolute] == digest, 'omitted historical native identity')
            else:
                need(absolute.startswith(PREFIX) and sha(files[absolute[len(PREFIX):]]) == digest,
                     'all actual nonbinary input guards')
                total_guards += 1
        for name, digest in receipt['outputs'].items():
            absolute = PREFIX + base + '/' + name
            if absolute in omitted:
                need(omitted[absolute] == digest, 'omitted historical native output identity')
            else:
                need(sha(files[base + '/' + name]) == digest, 'all actual saved output guards')
        for absolute, digest in protocol['bindings'].items():
            if absolute in omitted:
                need(omitted[absolute] == digest, 'original protocol native binding')
            else:
                need(absolute.startswith(PREFIX) and sha(files[absolute[len(PREFIX):]]) == digest,
                     'original protocol byte binding')
        for absolute, digest in diagnosis['inputs'].items():
            need(absolute.startswith(PREFIX) and sha(files[absolute[len(PREFIX):]]) == digest,
                 'diagnosis binds historical compiled sources, not live source')
        need(protocol['source_context']['count'] == 210
             and protocol['source_context']['build_receipt_sha256'] == manifest['actual_build_receipt_sha256']
             and protocol['binary']['sha256'] == manifest['frozen_libtest_sha256'],
             'actual historical compiled source and frozen libtest')
        need(capture['status'] == 'failed_or_incomplete' and len(capture['calls']) == 1
             and capture['ordered_shape'] == SHAPE and capture['working_bits'] == item['working_bits']
             and capture['public_Dual_qualified'] is False and capture['numerically_qualified'] is False
             and capture['performance_qualified'] is False, 'failed first call and unchanged Taylor scope')
        call = capture['calls'][0]
        need(call['name'] == 'odd_repeated_with_invalid' and call['status'] == 'captured'
             and call['expected_outcomes'] is False and call['input_preserved'] is True
             and call['input_before'] == call['input_after'], 'actual failed expectation with preserved inputs')
        parent = call['result']
        statuses = [lane['status'] for lane in parent['lanes']]
        need(parent['rows'] == 3 and parent['components'] == 3 and len(parent['basis']) == 210
             and statuses[0] == statuses[2] and statuses[0].startswith('Unstable(')
             and 'reduction has nonfinite coefficients' in statuses[0]
             and statuses[1].startswith('InvalidInput(') and 'mu must be positive and real' in statuses[1],
             'two genuine nonfinite parents and isolated invalid-mu neighbor')
        need(len(call['actual_packed_children']) == 1, 'one actual packed N5 group')
        child = call['actual_packed_children'][0]
        need(child['input_rows'] == child['result']['rows'] == 4 and child['input_components'] == 3
             and child['origins'] == [[0, 0], [2, 0], [0, 1], [2, 1]]
             and all(lane['status'] == 'Unstable("reduction has nonfinite coefficients at this kinematic point")'
                     for lane in child['result']['lanes']), 'four actual nonfinite terminal rows')
        for lane in parent['lanes'] + child['result']['lanes']:
            context = lane['component_context']
            need(lane['values'] is None and context['status'] == 'unavailable_for_failed_lane'
                 and context['raw_envelope'] is None and context['raw_error'] is None,
                 'failed arrays and component contexts are absent, never successful zeroes')
        parent_context = call['actual_parent_quadrature_context']
        for container, rows in [(child, 4), (parent_context, 3)]:
            for field in ['quadrature_errors', 'quadrature_origins']:
                need(len(container[field]) == rows and all(row['status'] == 'unavailable' for row in container[field]),
                     'no validated quadrature context for failed lanes')
        stats = call['execution']['affine_power_execution']
        method = stats['child_methods'][0]
        need(call['execution']['engine_kind'] == 'AffinePower' and stats['packed_child_rows'] == 4
             and stats['child_batch_calls'] == 1 and stats['parent_rows'] == 0
             and method['requested'] == 'PassarinoVeltman' and method['actual'] == 'Ibp'
             and method['rows'] == 4 and any('0 canonical PV requests, 610 IBP requests' in note for note in method['notes']),
             'expected requested-PV to generalized-IBP scalar-term selection')
        execution = stats['child_execution']
        need(execution['master_rows'] == 124 and execution['master_family_batches'] == 5
             and execution['reduction_rows'] == 4 and execution['pentagon_box_rows'] == 2400
             and execution['fallback_rows'] == execution['fallback_successes'] == execution['analytic_rows'] == 0,
             'actual master/recurrence counters without eager fallback or analytic promotion')
        for row in [0, 2]:
            notes = call['diagnostics'][row]
            for terminal in [0, 1]:
                need(any(note.startswith('terminal ' + str(terminal) + ' powers ')
                         and 'E6 leaf 0: quadrature order 64, box rows 600, error estimate ' in note for note in notes),
                     'both accepted E6 endpoint diagnostics retained')
        need(diagnosis['math_or_guard_failure'] is True and diagnosis['resource_failure'] is False
             and diagnosis['first_nonfinite_node_or_output_component_known'] is False
             and diagnosis['independent_numeric_agreement_qualified'] is False
             and diagnosis['full_objective_met'] is False, 'source-localized failure retains unresolved first bad node')
        first = diagnosis['actual_first_call']
        need(first['actual_execution'] == stats and first['parent_statuses'] == statuses
             and first['parent_arrays'] == [False] * 3 and first['child_arrays'] == [False] * 4
             and first['child_statuses'] == [lane['status'] for lane in child['result']['lanes']]
             and first['child_origins'] == child['origins'] and first['diagnostics'] == call['diagnostics'],
             'additive diagnosis matches complete actual recorded first-call state')
        source = diagnosis['source_context']
        need(source['compiled_source_count'] == 210 and source['artifact_sha256'] == manifest['frozen_libtest_sha256']
             and source['working_bits'] == item['working_bits'] and source['requested_bits'] == 53
             and source['raw_taylor_shape'] == SHAPE, 'diagnosis historical numeric source context')
        outcome = diagnosis['actual_native_outcome']
        need(outcome['elapsed_seconds'] == receipt['elapsed_seconds']
             and outcome['step_elapsed_seconds'] == step['elapsed_seconds']
             and outcome['returncode'] == 101 and outcome['owned_group_gone'] is True,
             'diagnosis actual native termination')
        namespace = {'__name__': 'frozen_failed_mechanism'}
        checker = root + '/check_saved_mechanism.py'
        exec(compile(files[checker], checker, 'exec'), namespace)
        findings = []
        try:
            namespace['audit'](capture)
        except (AssertionError, KeyError, TypeError, ValueError) as error:
            findings.append(str(error))
        expected = {'status': 'failed_saved_mechanism_gate', 'capture_sha256': sha(files[base + '/capture.json']),
                    'independent_numeric_agreement_qualified': False, 'performance_qualified': False,
                    'full_objective_met': False, 'default_Hybrid_qualified': False,
                    'algorithm_scope': 'explicit PV only; retained Hybrid preparation failures remain failures',
                    'findings': findings}
        need(audit == expected and findings == ['complete fixed capture'], 'original unchanged failed mechanism audit replay')
        outcomes.append({'working_bits': item['working_bits'], 'receipt_sha256': item['receipt_sha256'],
                         'diagnosis_sha256': item['diagnosis_sha256'], 'native_seconds': step['elapsed_seconds'],
                         'total_seconds': receipt['elapsed_seconds'], 'nonfinite_child_rows': 4,
                         'unstable_parent_rows': 2, 'isolated_invalid_parent_rows': 1,
                         'successful_tensor_arrays': 0, 'later_fixed_calls': 'unrun'})

    execution = files['crates/iregi-rust/src/execution.rs']
    masters = files['crates/iregi-masters/src/lib.rs']
    plan = files['crates/iregi-rust/src/plan.rs']
    need(b'if !output.iter().all(finite) {' in execution
         and b'if result.statuses[lane] == LaneStatus::Success {' in execution
         and b'LaneError::NonFiniteOutput' in masters and b'output[..5 * self.components]' in masters
         and b'let used = if usage.pv == 0 {' in plan, 'compiled historical failure and route-selection source witnesses')
    return {'status': 'passed_saved_postfix_nonfinite_failure_evidence_replay',
            'attempts': outcomes, 'checked_nonbinary_capture_input_guards': total_guards,
            'original_failed_mechanism_audits_reproduced': 2,
            'inherited_compiled_source_bodies': 210, 'source_bodies_duplicated_in_own_payload': 0,
            'dd_reference_bodies_duplicated_in_own_payload': 0,
            'actual_requested_child_method': 'PassarinoVeltman', 'actual_selected_child_method': 'Ibp',
            'ibp_scalar_requests_per_capture': 610, 'E6_endpoint_accepted_order': 64,
            'finite_master_acceptance_scope': 'historical finite-master guards and successful reduction-row selection; raw master arrays not exported',
            'first_nonfinite_node_or_output_component_known': False,
            'successful_tensor_arrays': 0, 'compared_2520_tensor_coefficients': False,
            'same_source_precision_convergence_qualified': False, 'full_rank6_dual_qualified': False,
            'default_Hybrid_qualified': False, 'full_objective_met': False,
            'new_live_source_archived': False, 'native_execution': False,
            'native_artifact_rehash': False, 'new_integral_evaluation': False, 'performance_qualified': False}


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
