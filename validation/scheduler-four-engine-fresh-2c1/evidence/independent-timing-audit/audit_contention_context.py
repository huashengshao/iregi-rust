"""Independently recompute saved shared-host counters; alter no timing evidence."""
from pathlib import Path
import datetime
import hashlib
import json

ROOT = Path('/shared/external/iregi/iregi-rust')
BASE = ROOT/'target/guard-performance-review/optimized-performance-proposal'
HERE = BASE/'contention-context-fresh2c1-001'
TARGET = BASE/'independent-timing-audit/audit-001/environment-addendum.json'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main():
    assert Path.cwd() == ROOT and not TARGET.exists()
    bindings = {}
    def bind(path, wanted=None):
        actual = sha(path)
        assert wanted is None or actual == wanted
        bindings[str(path)] = actual
        return read(path)
    before = bind(HERE/'before.json')
    after = bind(HERE/'after.json')
    produced = bind(HERE/'summary.json')
    review = bind(TARGET.with_name('full-review.json'), 'ca9ce926009cd6d26b08b93d120fa48829d5767de7ed036f2ca8b896f72904d0')
    admission = bind(TARGET.with_name('admission.json'), 'a9bced63ed013f28bc572bdb766c6dbb969572a663fa32c85d54b88034f2cbac')
    receipt = bind(Path(review['receipt_path']), review['receipt_sha256'])
    protocol = bind(Path(receipt['protocol']), review['protocol_sha256'])
    grant = bind(Path(protocol['quiet_grant']['path']), protocol['quiet_grant']['sha256'])
    release = bind(BASE/'fresh-four-engine-proposal/root-quiet-release-fresh2c1-001.json', review['quiet_release_sha256'])
    assert produced['inputs_sha256'] == {name: sha(HERE/name) for name in ['before.json', 'after.json']}
    assert before['clock_ticks_per_second'] == after['clock_ticks_per_second'] == 100
    assert before['smt_siblings'] == after['smt_siblings'] == '34,290'
    assert protocol['cpu'] == grant['cpu'] == release['cpu'] == 34
    assert 290 in grant['smt_siblings']
    parse_time = datetime.datetime.fromisoformat
    start, finish = parse_time(before['recorded_utc']), parse_time(after['recorded_utc'])
    span = (finish-start).total_seconds()
    assert start <= parse_time(receipt['started_utc']) <= parse_time(receipt['finished_utc']) <= finish
    assert finish <= parse_time(release['recorded_utc'])
    assert produced['before_utc'] == before['recorded_utc'] and produced['after_utc'] == after['recorded_utc']
    def counters(snapshot):
        result = {}
        for line in snapshot['cpu_stat']:
            name, *fields = line.split()
            cpu = int(name.removeprefix('cpu'))
            assert cpu not in result and len(fields) == 10
            result[cpu] = list(map(int, fields))
        assert set(result) == {34, 290}
        return result
    old, new = counters(before), counters(after)
    rows = []
    for cpu in [34, 290]:
        delta = [b-a for a, b in zip(old[cpu][:8], new[cpu][:8])]
        assert all(x >= 0 for x in delta)
        total = sum(delta)
        assert total > 0 and abs(total/100-span) < 1
        idle = delta[3]+delta[4]
        rows.append({'cpu': cpu, 'counter_delta_first8_fields': delta, 'total_ticks': total,
                     'non_idle_fraction': (total-idle)/total})
    assert rows == produced['cpu_rows']
    assert review['status'] == admission['status'] == 'passed' and review['ratio_count'] == 40
    assert review['gate_counts'] == {'regression': 12, 'inconclusive-noise': 16, 'improvement': 2, 'inconclusive-short-block': 10}
    result = {
        'schema_version': 1, 'status': 'passed-counter-and-scope-audit',
        'reviewer': '/root/scheduler_perf_resume/fresh_recipe_audit',
        'pinned_source_revision': review['pinned_source_revision'],
        'scope': 'Separate final acceptance context for the sealed experimental scheduler cohort. Saved raw timing, CI values and preregistered statistical gates remain unchanged.',
        'observation_before_utc': before['recorded_utc'], 'observation_after_utc': after['recorded_utc'],
        'observation_span_seconds': span, 'cpu_rows_independently_recomputed': rows,
        'observation_scope_limit': 'The interval includes setup, source review and polling gaps as well as kernel measurements. Aggregate counters and last-CPU process samples cannot attribute interference to individual paired blocks or quantify its effect on any ratio.',
        'root_project_quiet_lease': 'The root held other project compiler and numerical jobs; this did not reserve the physical core against unrelated host activity.',
        'material_environment_caveat': 'Reserved physical core sibling CPU290 had substantial unrelated/background activity, approximately69.6% non-idle over the observation interval. This does not support an uncontended or isolated-host performance claim.',
        'acceptance_eligibility': False,
        'acceptance_ineligibility_reason': 'Reserved physical core sibling had substantial unrelated activity.',
        'statistical_gate_counts_unchanged': review['gate_counts'],
        'raw_timings_or_bootstrap_or_gates_mutated': False,
        'uncontended_parity_claim_eligible': False, 'global_performance_claim_eligible': False,
        'default_or_production_adoption_authorized': False,
        'new_measurement_or_repeat_run_performed': False,
        'bindings_sha256': bindings, 'checker_sha256': sha(Path(__file__)),
        'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    for path, wanted in bindings.items():
        assert sha(path) == wanted
    TARGET.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'path': str(TARGET), 'sha256': sha(TARGET), 'acceptance_eligibility': False}))


if __name__ == '__main__':
    main()
