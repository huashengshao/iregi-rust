"""One independently granted finite stage; no producer runs on import."""
import datetime
import importlib.util
import os
import sys
import time

import rank_adapter as h
from lifecycle import Budget, execute


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def capture_shape(record, bits):
    return h.capture_shape(record, bits)


def main(operation):
    h.require(operation in h.REQUIRES, 'use freeze_sources.py for initial source sealing')
    row = h.policy(operation)
    budget = Budget(row['bound_seconds'])
    budget.work_deadline = budget.deadline-row['postwork_reserve_seconds']
    budget.arm()
    folder = h.stage_directory(operation)
    folder.parent.mkdir(parents=True, exist_ok=True)
    folder.mkdir(exist_ok=False)
    receipt = folder / 'run.json'
    record = dict(status='preflight', context=h.CONTEXT, operation=operation, tensor_rank=h.rank(), attempt=1,
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
        preflight = dict(bindings)
        for name, digest in cache_admission.items():
            h.merge(preflight, name, digest)
        record['provenance_before'] = h.verify(preflight, budget, 'before')
        record['inputs'] = bindings
        if cache_admission:
            record['initial_seed_admission_files'] = len(cache_admission)
        if operation == 'compare':
            source = h.HERE / 'compare_positive_saved.py'
            spec = importlib.util.spec_from_file_location('frozen_private_positive_rank_saved_math', source)
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
            environment.update(RAYON_NUM_THREADS='1', OMP_NUM_THREADS='1',
                               SYMBOLICA_HIDE_BANNER='1', IREGI_PV_PREPARATION_PROFILE='1')
            if operation.startswith('capture'):
                record['executed_binary_sha256'] = protocol['owned_generic_probe_sha256']
                record['shared_readonly_executable'] = protocol['shared_executable']

            def persist(value):
                step.update(value)
                h.save(receipt, record)

            result = execute(command, folder / 'step-0.log', budget, row['per_child_cap_seconds'],
                             record['cleanup_errors'], persist, environment)
            h.require(result['status'] == 'exited' and result['owned_group_gone'] is True,
                      'owned process failed or descendants remain')
            # The terminal process/group event is durable before any artifact read.
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
        expected = {'capture128': {'step-0.log', 'result.json'},
            'capture256': {'step-0.log', 'result.json'},
            'compare': {'comparison.json'}}[operation]
        h.require(set(record['outputs']) == expected, 'finite output inventory incomplete')
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
    h.require(len(sys.argv) == 3, 'rank(2|7) and exact capture/compare operation required')
    h.select_rank(int(sys.argv[1]))
    sys.exit(main(sys.argv[2]))
