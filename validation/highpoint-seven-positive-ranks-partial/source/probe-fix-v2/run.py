"""One independently granted finite stage; no producer runs on import."""
import datetime
import importlib.util
import os
from pathlib import Path
import sys
import time

import continuation as h
from lifecycle import Budget, execute, freeze_binary


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def cache_membership(protocol, budget):
    manifest = h.load(h.HERE / 'cache-manifest.json')
    root = Path(manifest['source_root'])
    for selected, expected in manifest['directory_inventory'].items():
        directory = root / selected
        files = h.source_inventory(directory, budget, [])
        actual_files = sorted(str((directory / name).relative_to(root)) for name in files)
        actual_directories = []
        for current, _, _ in os.walk(directory):
            budget.remaining()
            actual_directories.append(str(Path(current).relative_to(root)))
        h.require(actual_files == expected['files']
                  and sorted(actual_directories) == expected['directories'], 'original cache membership changed')


def capture_shape(record, bits):
    h.require(record['private_validation_overlay'] is True and record['public_positive_rank_support'] is False
        and record['working_bits'] == bits and record['requested_bits'] == 53
        and record['rows'] == record['components'] == 1
        and record['fixture'] == str(h.BUNDLE / 'fixture.json')
        and record['basis'] == [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        and record['parameter_count'] == 36, 'private rank1 capture shape/context differs')
    settings = record['settings']
    h.require(settings == dict(propagators=7, rank=1, powers=[1]*7, dimension_shift=0,
        algorithm='PassarinoVeltman', convention='IregiNative', tensor_weights='Components',
        invariants='FromShifts', input_policy='Preserve'), 'capture mathematical input settings differ')
    h.require(len(record['lanes']) == 1 and len(record['lane_statuses']) == 1
              and len(record['fallback_used']) == len(record['analytic_used']) == 1,
              'capture lane/flag dimensions incomplete')
    lane = record['lanes'][0]
    if record['status'] == 'all_lanes_success':
        h.require(record['lane_statuses'] == ['Success'] and lane['status'] == 'Success'
            and len(lane['moments']) == 5 and all(len(moment) == 4 for moment in lane['moments'])
            and all(isinstance(slot[name], str) and slot[name] for moment in lane['moments']
                    for slot in moment for name in ['real', 'imaginary']), 'successful full array incomplete')
    else:
        h.require(record['status'] == 'lanes_rejected' and lane['moments'] is None,
                  'incomplete/failed coefficients cannot be accepted as zero')
    # No coefficient comparison or convergence gate is performed by producers.


def main(operation):
    h.require(operation in h.REQUIRES, 'use freeze_sources.py for initial source sealing')
    row = h.policy(operation)
    budget = Budget(row['bound_seconds'])
    budget.work_deadline = budget.deadline-row['postwork_reserve_seconds']
    budget.arm()
    folder = h.stage_directory(operation)
    folder.mkdir(exist_ok=False)
    receipt = folder / 'run.json'
    record = dict(status='preflight', context=h.CONTEXT, operation=operation, attempt=2 if operation == 'build' else 1,
        **row, started_utc=utc(), started_monotonic=budget.started,
        absolute_deadline_monotonic=budget.deadline, work_deadline_monotonic=budget.work_deadline,
        steps=[], cleanup_errors=[], outputs={}, artifact_inputs={},
        numerical_qualified=False, performance_qualified=False, license_recorded=False)
    h.save(receipt, record)
    work_passed, protocol = False, None
    closures, new_closures = [], []
    try:
        protocol = h.read_protocol()
        h.require(set(row['cpu_affinity']).issubset(os.sched_getaffinity(0)), 'reserved CPUs unavailable')
        bindings, closures, cache_admission = h.stage_context(operation, protocol)
        h.check_context(protocol, closures, budget)
        if operation == 'cache-seed':
            cache_membership(protocol, budget)
        preflight = dict(bindings)
        for name, digest in cache_admission.items():
            h.merge(preflight, name, digest)
        record['provenance_before'] = h.verify(preflight, budget, 'before')
        record['inputs'] = bindings
        if cache_admission:
            record['initial_seed_admission_files'] = len(cache_admission)
        if operation == 'compare':
            source = h.HERE / 'compare_positive_saved.py'
            spec = importlib.util.spec_from_file_location('frozen_private_rank1_saved_math', source)
            module = importlib.util.module_from_spec(spec)
            argv = sys.argv
            try:
                sys.argv = [str(source), str(h.stage_directory('capture128') / 'result.json'),
                            str(h.stage_directory('capture256') / 'result.json'), str(folder / 'comparison.json')]
                spec.loader.exec_module(module)
                code = module.main()
            finally:
                sys.argv = argv
            comparison = h.load(folder / 'comparison.json')
            record['saved_math_status'] = comparison['status']
            h.require(code == 0 and comparison['status'] == 'passed_saved_math',
                      'saved full-array numerical gate failed; output retained')
            record['numerical_cohort_admitted_awaiting_guards'] = True
        else:
            command = h.command(operation, protocol, budget)
            step = dict(name=operation, command=command)
            record['steps'].append(step)
            record['status'] = 'running'
            h.save(receipt, record)
            environment = dict(os.environ)  # License is forwarded here, never serialized.
            if operation in ['metadata', 'build']:
                environment.update(h.cargo_environment(protocol))
            else:
                environment.update(RAYON_NUM_THREADS='1', OMP_NUM_THREADS='1',
                                   SYMBOLICA_HIDE_BANNER='1', IREGI_PV_PREPARATION_PROFILE='1')
            if operation.startswith('capture'):
                built = h.stage_directory('build')
                build_receipt = h.load(built / 'run.json')
                expected = build_receipt['outputs']['positive-rank-probe']
                freeze_binary(built / 'positive-rank-probe', expected, folder / 'frozen-executable', budget)
                record['executed_binary_sha256'] = expected

            def persist(value):
                step.update(value)
                h.save(receipt, record)

            result = execute(command, folder / 'step-0.log', budget, row['per_child_cap_seconds'],
                             record['cleanup_errors'], persist, environment)
            h.require(result['status'] == 'exited' and result['owned_group_gone'] is True,
                      'owned process failed or descendants remain')
            # The terminal process/group event is durable before any artifact read.
            if operation == 'cache-seed':
                manifest = h.load(h.HERE / 'cache-manifest.json')
                copied = h.load(folder / 'seed-result.json')
                h.require(copied['status'] == 'cache_seed_complete_awaiting_supervisor_guards'
                    and copied['completed_files'] == len(manifest['members']) == 1118
                    and copied['hardlinks_created'] == 0 and copied['metadata_rewritten'] is False
                    and set(copied['members']) == set(manifest['members']), 'isolated cache copy incomplete')
                record['seeded_cache_inputs'] = {}
                for name, entry in manifest['members'].items():
                    copied_entry = copied['members'][name]
                    h.require(copied_entry['sha256'] == entry['sha256'] and copied_entry['distinct_inode'] is True
                        and (copied_entry['source_device'], copied_entry['source_inode'])
                            != (copied_entry['destination_device'], copied_entry['destination_inode']),
                        'copied cache member not independently admitted')
                    h.merge(record['seeded_cache_inputs'], h.key(h.BUNDLE / 'cargo-build' / name), entry['sha256'])
            elif operation == 'metadata':
                document = h.metadata_document(folder / 'step-0.log')
                closure = h.resolved_source_closure(document, protocol, budget)
                h.save(folder / 'metadata-source-freeze.json', closure)
                for name, digest in closure['inputs'].items():
                    h.merge(record['artifact_inputs'], name, digest)
                new_closures.append(closure)
                record['private_package_ids'] = {p['name']: p['id'] for p in document['packages']
                    if p['manifest_path'] in [str(h.SOURCE / 'crates/iregi-rust/Cargo.toml'),
                                              str(h.SOURCE / 'crates/iregi-masters/Cargo.toml')]}
            elif operation == 'build':
                document = h.metadata_document(h.stage_directory('metadata') / 'step-0.log')
                parsed, products = h.parse_build(folder / 'step-0.log', protocol, document)
                closure = h.emitted_artifact_closure(parsed, protocol, budget)
                new_closures.append(closure)
                record['artifact_inputs'] = closure['inputs']
                owned = {}
                for name, event in products.items():
                    source = event['executable'] if name == 'driver' else next(x for x in event['filenames'] if x.endswith('.rlib'))
                    expected = closure['inputs'][h.key(Path(source))]
                    destination = folder / {'core': 'private-core.rlib', 'masters': 'private-masters.rlib',
                                            'driver': 'positive-rank-probe'}[name]
                    freeze_binary(source, expected, destination, budget)
                    owned[name] = dict(event=event, emitted_sha256=expected, owned_path=h.key(destination))
                h.save(folder / 'cargo-artifacts.json', dict(status='private_actual_Cargo_products_admitted',
                    parsed=parsed, products=owned, artifact_closure=closure,
                    old_product_substitution=False, native_link_closure_qualified=False))
            else:
                result_record = h.load(folder / 'result.json')
                capture_shape(result_record, int(operation.removeprefix('capture')))
                record['capture_status'] = result_record['status']
                record['complete_successful_arrays'] = result_record['status'] == 'all_lanes_success'
                h.require(record['complete_successful_arrays'], 'native lane rejected; diagnostics retained')
        budget.remaining()
        work_passed = True
        record['status'] = 'completed_awaiting_guards'
    except Exception as error:
        record.update(status='failed', error=repr(error))
    finally:
        budget.disarm()
        if budget.cancelled:
            record['cancellation'] = budget.cancelled
        record['elapsed_seconds'] = budget.elapsed()
        h.save(receipt, record)
    post = Budget(max(0, budget.deadline-time.monotonic()))
    post.deadline, post.work_deadline = budget.deadline, budget.deadline-5
    try:
        post.arm()
        h.require(protocol is not None and 'inputs' in record, 'preflight source admission incomplete')
        h.check_context(protocol, [*closures, *new_closures], post)
        if operation == 'cache-seed':
            cache_membership(protocol, post)
        guard = dict(record['inputs'])
        for group in ['artifact_inputs', 'seeded_cache_inputs']:
            for name, digest in record.get(group, {}).items():
                h.merge(guard, name, digest)
        record['provenance_after'] = h.verify(guard, post, 'after')
        record['inputs_unchanged'] = True
        for path in sorted(folder.iterdir()):
            post.remaining()
            if path.is_file() and path != receipt and not path.name.endswith('.tmp'):
                record['outputs'][path.name] = h.sha(path, post)
        expected = {'cache-seed': {'step-0.log', 'seed-result.json'},
            'metadata': {'step-0.log', 'metadata-source-freeze.json'},
            'build': {'step-0.log', 'cargo-artifacts.json', 'private-core.rlib', 'private-masters.rlib',
                      'positive-rank-probe'},
            'capture128': {'step-0.log', 'frozen-executable', 'result.json'},
            'capture256': {'step-0.log', 'frozen-executable', 'result.json'},
            'compare': {'comparison.json'}}[operation]
        h.require(set(record['outputs']) == expected, 'finite output inventory incomplete')
        if operation.startswith('capture'):
            h.require(record['outputs']['frozen-executable'] == record['executed_binary_sha256'],
                      'owned executed binary changed')
        post.remaining()
    except Exception as error:
        record.update(postguard_error=repr(error), inputs_unchanged=False)
    finally:
        post.disarm()
    if post.cancelled:
        record['postguard_cancellation'] = post.cancelled
    record.update(elapsed_seconds=budget.elapsed(), finished_utc=utc())
    record['status'] = 'passed' if (work_passed and record.get('inputs_unchanged') is True
        and not record['cleanup_errors'] and not budget.cancelled and not post.cancelled
        and not record.get('postguard_error') and record['elapsed_seconds'] <= row['bound_seconds']) else 'failed'
    tail = Budget(max(0, budget.deadline-time.monotonic()))
    tail.deadline = tail.work_deadline = budget.deadline
    try:
        tail.arm()
        h.save(receipt, record)
        tail.remaining()
    except Exception as error:
        record.update(status='failed', finalization_error=repr(error), elapsed_seconds=budget.elapsed())
        h.save(receipt, record)  # Durable failure is never promoted if this exceeded the bound.
    finally:
        tail.disarm()
    print({'operation': operation, 'status': record['status'], 'receipt': h.key(receipt)})
    return 0 if record['status'] == 'passed' else 1


if __name__ == '__main__':
    h.require(len(sys.argv) == 2, 'one exact finite operation argument required')
    sys.exit(main(sys.argv[1]))
