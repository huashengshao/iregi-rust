"""Mutation tests use existing captures; they do not stand in for the pending v2 run."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from qualify_collector_capture_v2 import check_rows, check_guard_inventory, check_artifact_inventory, REMOVED_ENVIRONMENT


HERE = Path(__file__).resolve().parent


class CaptureChecks(unittest.TestCase):
    def setUp(self):
        self.original = json.loads((HERE / 'collector-capture-output.baseline.json').read_text())
        self.probe = json.loads((HERE / 'collector-v2-probe-baseline.json').read_text())
        retained = deepcopy(self.original)
        for row in retained:
            positive = row['propagators'] < 4 or row['domain'] != 'f64'
            row.update(fixture='retained_v1', validation_role='positive' if positive else 'known_guard_parity',
                       requires_ordinary_lane_success=positive)
        self.rows = retained[:9] + deepcopy(self.probe) + retained[9:]

    def validate(self):
        return check_rows(self.rows, deepcopy(self.rows), self.original, self.probe)

    def test_existing_rows_satisfy_structural_checks(self):
        counts = self.validate()
        self.assertEqual((counts['required_ordinary_successes'], counts['known_ordinary_guard_parity_cases']), (26, 3))

    def test_missing_case_rejected(self):
        self.rows.pop()
        with self.assertRaises(AssertionError):
            self.validate()

    def test_changed_paired_result_rejected(self):
        candidate = deepcopy(self.rows)
        candidate[0]['result']['metadata'] = 'wrong'
        with self.assertRaises(AssertionError):
            check_rows(self.rows, candidate, self.original, self.probe)

    def test_changed_retained_input_rejected(self):
        self.rows[0]['input'] = []
        with self.assertRaises(AssertionError):
            self.validate()

    def test_matching_all_failure_cannot_pass(self):
        for target in [self.rows[0], self.original[0]]:
            target['result'].update(ordinary_lane_success=False, lane_successes=[False]*5,
                                    moments=[None]*5, repeat=[None]*5, contracted=[None]*5)
        with self.assertRaises(AssertionError):
            self.validate()

    def test_guard_cannot_count_as_positive(self):
        self.rows[6]['requires_ordinary_lane_success'] = True
        self.rows[6]['validation_role'] = 'positive'
        with self.assertRaises(AssertionError):
            self.validate()

    def test_invalid_scale_must_remain_guarded(self):
        for target in [self.rows[0], self.original[0]]:
            target['result']['invalid_scale_guard'] = False
        with self.assertRaises(AssertionError):
            self.validate()

    def test_matching_truncated_arrays_rejected(self):
        for target in [self.rows[0], self.original[0]]:
            target['result']['moments'][0].pop()
            target['result']['repeat'][0].pop()
        with self.assertRaises(AssertionError):
            self.validate()

    def test_nonzero_dual_component_required(self):
        for target in [self.rows[3], self.original[3]]:
            for key in ['moments', 'repeat']:
                for i, value in enumerate(target['result'][key][0]):
                    if i % 3:
                        for part in value:
                            part['rational'] = '0'
        with self.assertRaises(AssertionError):
            self.validate()

    def test_first_derivative_cannot_stand_in_for_second(self):
        for target in [self.rows[3], self.original[3]]:
            for key in ['moments', 'repeat']:
                for i, value in enumerate(target['result'][key][0]):
                    if i % 3 == 2:
                        for part in value:
                            part['rational'] = '0'
        with self.assertRaises(AssertionError):
            self.validate()

    def test_conditioned_probe_binding_required(self):
        self.rows[9]['input'] = []
        with self.assertRaises(AssertionError):
            self.validate()


class ProvenanceChecks(unittest.TestCase):
    def setUp(self):
        self.build = {'protected_input_hashes': {'source': 'source-hash'}}
        self.required = {'runner': 'runner-hash', 'binary': 'binary-hash', 'manifest': 'manifest-hash'}
        self.run = {'protected_input_hashes': {'source': 'source-hash', **self.required},
                    'environment_additions': {'RAYON_NUM_THREADS': '1'},
                    'environment_removals': REMOVED_ENVIRONMENT.copy()}

    def test_complete_inventory_accepted(self):
        check_guard_inventory(self.run, self.build, self.required)

    def test_each_missing_guard_rejected(self):
        for key in list(self.run['protected_input_hashes']):
            with self.subTest(key=key):
                changed = deepcopy(self.run)
                del changed['protected_input_hashes'][key]
                with self.assertRaises(AssertionError):
                    check_guard_inventory(changed, self.build, self.required)

    def test_changed_guard_rejected(self):
        self.run['protected_input_hashes']['binary'] = 'wrong'
        with self.assertRaises(AssertionError):
            check_guard_inventory(self.run, self.build, self.required)

    def test_changed_environment_rejected(self):
        self.run['environment_removals'].pop()
        with self.assertRaises(AssertionError):
            check_guard_inventory(self.run, self.build, self.required)

    def test_missing_reference_artifact_rejected(self):
        with self.assertRaises(AssertionError):
            check_artifact_inventory({'build': 'hash'}, ['build', 'original-reference'])


if __name__ == '__main__':
    unittest.main()
