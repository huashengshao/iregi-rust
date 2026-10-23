from copy import deepcopy
import json
from pathlib import Path
import unittest
import compare_collector_history_v4 as history
import compare_collector_controls as controls
from test_compare_collector_history import HistoricalComparison


HERE=Path(__file__).resolve().parent


class Version4History(HistoricalComparison):
    """Repeat the nine mutation/coverage checks against the version4 implementation."""
    def setUp(self):
        super().setUp()
        import test_compare_collector_history
        self.previous=test_compare_collector_history.history
        test_compare_collector_history.history=history

    def tearDown(self):
        import test_compare_collector_history
        test_compare_collector_history.history=self.previous


class FullControlReference(unittest.TestCase):
    def setUp(self):
        self.rows=[r for r in json.loads((HERE/'collector-v2-baseline.json').read_text()) if r['fixture']=='orthogonal_unit_n4']
        self.probe=json.loads((HERE/'collector-v2-probe-baseline.json').read_text())
        self.reference=json.loads((HERE/'collector-v2-probe-original.json').read_text())

    def test_complete_control_history(self):
        report=history.compare(self.probe,self.rows,expected_cases=2)
        self.assertEqual(len(report['changed_leaves']),178)
        for field,count in report['compared_complex_components'].items():
            self.assertEqual(count,sum(len(lane) for row in self.probe for lane in row['result'][field] if lane is not None))

    def test_actual_primal_reference(self):
        report=controls.compare(self.rows,self.reference)
        self.assertEqual([x['compared_primal_complex_slots'] for x in report['comparisons']],[60,20])

    def test_reference_request_mismatch_rejected(self):
        self.reference['request']=self.reference['request'].replace('0 3 0 1e-6','0 4 0 1e-6')
        with self.assertRaises(AssertionError):controls.compare(self.rows,self.reference)

    def test_last_requested_primal_checked(self):
        self.rows[1]['result']['moments'][0][-3][0]['rational']='1'
        with self.assertRaises(AssertionError):controls.compare(self.rows,self.reference)

    def test_missing_slot_rejected(self):
        self.rows[0]['result']['moments'][0].pop()
        with self.assertRaises(AssertionError):controls.compare(self.rows,self.reference)


if __name__=='__main__':unittest.main()
