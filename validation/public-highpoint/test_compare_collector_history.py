from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import unittest
import compare_collector_history as history


HERE = Path(__file__).resolve().parent


class HistoricalComparison(unittest.TestCase):
    def setUp(self):
        self.old = json.loads((HERE / 'collector-capture-output.baseline.json').read_text())
        self.new = [row for row in json.loads((HERE / 'collector-v2-baseline.json').read_text()) if row['fixture'] == 'retained_v1']

    def test_real_capture_differences_are_recorded(self):
        result = history.compare(self.old,self.new)
        self.assertEqual(len(result['changed_leaves']),29)
        self.assertEqual(result['maximum_raw_difference_exact'],'1/340282366920938463463374607431768211456')
        for key, count in result['compared_complex_components'].items():
            expected = sum(len(lane) for row in self.old for lane in row['result'][key] if lane is not None)
            self.assertEqual(count,expected)

    def test_status_change_rejected(self):
        self.new[0]['result']['statuses'] = 'wrong'
        with self.assertRaises(AssertionError): history.compare(self.old,self.new)

    def test_missing_laurent_slot_rejected(self):
        self.new[0]['result']['moments'][0].pop()
        with self.assertRaises(AssertionError): history.compare(self.old,self.new)

    def test_last_second_order_dual_component_checked(self):
        self.new[3]['result']['moments'][0][-1][0]['rational'] = '1'
        with self.assertRaises(AssertionError): history.compare(self.old,self.new)

    def test_pole_component_checked(self):
        self.new[0]['result']['moments'][0][0][0]['rational'] = '1'
        with self.assertRaises(AssertionError): history.compare(self.old,self.new)

    def test_repeat_checked(self):
        self.new[0]['result']['repeat'][0][-1][0]['rational'] = '1'
        with self.assertRaises(AssertionError): history.compare(self.old,self.new)

    def test_contraction_checked(self):
        self.new[0]['result']['contracted'][0][-1][0]['rational'] = '1'
        with self.assertRaises(AssertionError): history.compare(self.old,self.new)

    def test_scale_and_complex_error(self):
        left = [{'rational':'0'},{'rational':'0'}]
        right = [{'rational':'3/1000000000000'},{'rational':'4/1000000000000'}]
        self.assertEqual(history.error(left,right,Decimal('0.01')),Decimal('5e-10'))

    def test_exact_input_required(self):
        self.new[0]['input'][0][0]['rational'] = '1'
        with self.assertRaises(AssertionError): history.compare(self.old,self.new)


if __name__ == '__main__':
    unittest.main()
