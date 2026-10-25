"""Pure validation/projection of separately qualified captured saved responses.

No process, compiler, integral or timing is launched. The bounded caller reads
hash-bound saved data and checks its independently admitted receipt first.
"""
import copy
import json
import admission as uncaptured
import captured_admission as captured


def project(value):
    """Drop only master_captures recursively and two root-result mode fields.

    Every other field, including plan_reused, survives. Direct six-output scalar
    master controls have no master_captures key and remain completely intact.
    """
    def visit(node):
        if type(node) is dict:
            return {key: visit(item) for key, item in node.items() if key != 'master_captures'}
        if type(node) is list:
            return [visit(item) for item in node]
        return copy.deepcopy(node)
    result = visit(value)
    if type(result) is dict and set(result) == {'id', 'result'}:
        assert type(result['result']) is dict
        for key in ['scope', 'capture_enabled']:
            assert key in result['result'], 'Missing explicit root result mode field'
            result['result'].pop(key)
    return result


def schedule(cases):
    assert len(cases) == 4
    coordinates = [(case, rows) for case in cases for rows in [1, 32]]
    assert len({(case['id'], rows) for case, rows in coordinates}) == 8
    result = []
    for case, rows in coordinates:
        for stage in ['initial', 'own-repeat']:
            for engine in ['baseline', 'candidate']:
                result.append((stage, [case['id'], rows], engine))
    for stage, step in [('controls', 0), ('controls-repeat', 1)]:
        for engine in ['baseline', 'candidate']:
            result.append((stage, ['controls', step], engine))
    for case, rows in coordinates:
        for engine in ['baseline', 'candidate']:
            result.append(('retained', [case['id'], rows], engine))
    for field, value in [('engine', 'baseline'), ('warmup', 1), ('repeats', 1), ('iterations', 1)]:
        for engine in ['baseline', 'candidate']:
            result.append(('invalid-request', [field, value], engine))
    assert len(result) == 60
    return result


class SavedCapture:
    def __init__(self, receipt, raw, cases, shape, remaining=lambda: None):
        assert receipt['status'] == 'passed-awaiting-independent-saved-data-review'
        assert receipt['guard_before'] is True and receipt['guard_after'] is True
        assert receipt['cleanup_errors'] == [] and receipt['deadline_exceeded'] is False
        assert 'error' not in receipt and 'guard_error' not in receipt and 'cancellation' not in receipt
        assert receipt['request_count'] == 60
        terminals = receipt['process_terminals']
        assert len(terminals) == 2 and {value['label'] for value in terminals} == {'baseline', 'candidate'}
        assert all(value['returncode'] == 0 and value['owned_group_gone'] is True
                   and value['received_responses'] == 30 for value in terminals)
        self.cases = {case['id']: case for case in cases}
        self.shape = shape
        expected = schedule(cases)
        assert len(raw) == 120
        self.records = {}
        for serial, (stage, key, engine) in enumerate(expected, 1):
            remaining()
            request, response = raw[2 * serial - 2:2 * serial]
            assert set(request) == {'serial', 'stage', 'key', 'engine', 'payload', 'event'}
            assert set(response) == set(request) | {'response'}
            assert request['event'] == 'request' and response['event'] == 'response'
            assert type(request['serial']) is int and request['serial'] == serial
            assert type(response['serial']) is int and response['serial'] == serial
            for field in ['serial', 'stage', 'key', 'engine', 'payload']:
                assert captured.exact(request[field], response[field])
            assert request['stage'] == stage and captured.exact(request['key'], key)
            assert request['engine'] == engine
            body = response['response']
            if stage in ['controls', 'controls-repeat']:
                assert request['payload'] == 'CONTROLS\n'
                captured.controls(body, shape)
            elif stage == 'invalid-request':
                assert body == {'status': 'invalid_request', 'error': 'qualification is untimed; engine and timing counts are forbidden'}
            else:
                case, rows = self.cases[key[0]], key[1]
                payload = {'id': case['id'], 'n': case['n'], 'rank': case['rank'],
                           'algorithm': 'Hybrid', 'samples': case['samples'][:rows]}
                assert json.loads(request['payload']) == payload
                captured.response(body, case, rows)
            self.records[serial] = response
        coordinates = [(case['id'], rows) for case in cases for rows in [1, 32]]
        for name in ['rows', 'retained_rows']:
            assert [(row['id'], row['batch']) for row in receipt[name]] == coordinates
            assert all(row['status'] == 'passed' for row in receipt[name])
        assert receipt['controls']['status'] == receipt['invalid_request_controls']['status'] == 'passed'
        # Existing saved-data admission is required independently; additionally
        # recheck the core equality/reuse/control invariants needed by this anchor.
        initial, controls = {}, {}
        for serial, record in self.records.items():
            remaining()
            stage, key, engine, body = record['stage'], record['key'], record['engine'], record['response']
            if stage == 'initial':
                initial[(key[0], key[1], engine)] = body
            elif stage in ['own-repeat', 'retained']:
                assert captured.exact(captured.canonical(body), captured.canonical(initial[(key[0], key[1], engine)]))
            if stage in ['controls', 'controls-repeat']:
                if stage == 'controls':
                    controls[engine] = body
                else:
                    assert captured.exact(body, controls[engine])
        for case, rows in [(case, rows) for case in cases for rows in [1, 32]]:
            assert captured.exact(initial[(case['id'], rows, 'baseline')], initial[(case['id'], rows, 'candidate')])
        assert captured.exact(controls['baseline'], controls['candidate'])
        self.compared = set()

    def compare(self, serial, stage, key, engine, payload, actual):
        assert type(serial) is int and serial in self.records and serial not in self.compared
        anchor = self.records[serial]
        assert stage != 'invalid-request'
        assert stage == anchor['stage'] and captured.exact(key, anchor['key']) and engine == anchor['engine']
        assert payload == anchor['payload'], 'Normal request differs from same-phase captured request'
        if stage in ['controls', 'controls-repeat']:
            uncaptured.controls(actual, self.shape)
        else:
            uncaptured.response(actual, self.cases[key[0]], key[1])
        assert captured.exact(project(actual), project(anchor['response'])), 'Complete same-phase captured projection differs'
        self.compared.add(serial)
        return {'status': 'passed', 'captured_raw_serial': serial,
                'only_projection_fields': ['master_captures recursively', 'root.result.scope', 'root.result.capture_enabled'],
                'plan_reused_checked_exactly': True}
