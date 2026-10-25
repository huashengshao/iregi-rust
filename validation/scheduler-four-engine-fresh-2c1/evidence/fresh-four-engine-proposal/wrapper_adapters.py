"""Source-only protocol adapters; no process, compiler, integral or timing calls.

These adapt fresh single-scheduler probe transport only. Full numerical/master,
control, raw-event, lifecycle and statistical admission belongs to the reviewed
runner/analyzer described in README.md. Importing this file launches nothing.
"""
import json
import math

ENGINES = ('baselineTIRust', 'candidateTIRust', 'iregi', 'collier')
SELECTOR = {'baselineTIRust': 'baseline', 'candidateTIRust': 'candidate'}
RATIOS = (
    ('baselineTIRust', 'iregi'), ('candidateTIRust', 'iregi'),
    ('baselineTIRust', 'collier'), ('candidateTIRust', 'collier'),
    ('candidateTIRust', 'baselineTIRust'),
)
RESULT_KEYS = {
    'stable', 'lanes', 'diagnostics', 'master_captures', 'execution',
    'id', 'n', 'rank', 'batch', 'plan_reused', 'degrees',
    'requested_master_backend', 'scope', 'total_ns', 'elapsed_ns', 'iterations',
    'capture_enabled', 'profiling_enabled', 'own_repeated_outputs_exact',
    'input_unchanged',
}
SEMANTIC_KEYS = (
    'id', 'n', 'rank', 'batch', 'stable', 'degrees', 'lanes', 'diagnostics',
    'execution', 'requested_master_backend', 'input_unchanged',
)

def exact(left, right):
    return json.dumps(left, sort_keys=True, allow_nan=False, separators=(',', ':')) == json.dumps(
        right, sort_keys=True, allow_nan=False, separators=(',', ':'))

def untimed_payload(case, batch):
    """Do not use historical h.rust_request: it inserts forbidden repeats=1."""
    assert type(batch) is int and batch in (1, 32)
    assert case['n'] in (2, 3) and case['rank'] in (0, 1)
    assert len(case['samples']) >= batch
    return json.dumps({'id': case['id'], 'n': case['n'], 'rank': case['rank'],
                       'algorithm': 'Hybrid', 'samples': case['samples'][:batch]},
                      allow_nan=False) + '\n'

def timed_payload(case, batch, engine, iterations, warmup):
    assert engine in SELECTOR
    assert type(iterations) is int and 0 < iterations <= 2**31 - 1
    assert type(warmup) is int and warmup in (0, 10)
    payload = json.loads(untimed_payload(case, batch))
    payload.update(engine=SELECTOR[engine], warmup=warmup, repeats=1, iterations=iterations)
    return json.dumps(payload, allow_nan=False) + '\n'

def unwrap(response, case, batch, *, capture, timed=False, iterations=0):
    """Strict wrapper/mode validation; caller still validates every numeric slot."""
    assert type(response) is dict and set(response) == {'id', 'result'}
    assert response['id'] == case['id']
    result = response['result']
    assert type(result) is dict and set(result) == RESULT_KEYS
    assert result['id'] == case['id']
    for key, expected in [('n', case['n']), ('rank', case['rank']), ('batch', batch)]:
        assert type(result[key]) is int and result[key] == expected
    assert type(result['plan_reused']) is bool
    assert result['stable'] is True and result['input_unchanged'] is True
    assert result['requested_master_backend'] == 'SymbolicaBatch'
    assert result['capture_enabled'] is capture and result['profiling_enabled'] is False
    if timed:
        assert capture is False and result['scope'] == 'whole-public-call fixed-count timing'
        assert result['own_repeated_outputs_exact'] is False
        assert type(iterations) is int and 0 < iterations <= 2**31 - 1
        assert type(result['iterations']) is int and result['iterations'] == iterations
        assert type(result['elapsed_ns']) is list and len(result['elapsed_ns']) == 1
        assert type(result['elapsed_ns'][0]) is int and result['elapsed_ns'][0] > 0
        assert type(result['total_ns']) is list and len(result['total_ns']) == 1
        total = result['total_ns'][0]
        assert type(total) in (int, float) and math.isfinite(total) and total > 0
        assert total == result['elapsed_ns'][0] / iterations
    else:
        scope = ('untimed generic-only scheduler whole-reduction qualification' if capture
                 else 'untimed capture-free scheduler whole-reduction qualification')
        assert result['scope'] == scope and result['own_repeated_outputs_exact'] is True
        assert type(result['iterations']) is int and result['iterations'] == 0
        assert result['total_ns'] == result['elapsed_ns'] == []
    if not capture:
        assert result['master_captures'] == []
    return result

def semantic_projection(result):
    """Only explicit mode/capture/timing/reuse fields differ across product roles.

    Captured masters must be separately validated in full; this projection never
    turns missing masters into evidence. Full lane records retain represented
    rational values, precision, zero signs, status/fallback and numeric arrays.
    """
    assert set(result) == RESULT_KEYS
    return {key: result[key] for key in SEMANTIC_KEYS}
