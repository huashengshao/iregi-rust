"""Tiny deterministic mock tests only. Never execute the real bootstrap."""
import ast
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import timing_statistics as stats

HERE = Path(__file__).resolve().parent
checks = []

class SourceOnlyTests(unittest.TestCase):
    def test_quantiles(self):
        self.assertEqual(stats.quantile([3., 1., 2.], 0), 1.)
        self.assertEqual(stats.quantile([3., 1., 2.], 1), 3.)
        self.assertEqual(stats.quantile([0., 100.], .005), .5)
        self.assertEqual(stats.quantile([0., 100.], .995), 99.5)
        self.assertEqual(stats.quantile([7.], .005), 7.)

    def test_historical_gates(self):
        for median, low, high, admitted, expected in [
            (.5, .5, .5, True, 'improvement'),
            (1., 1., 1., True, 'parity'),
            (2., 2., 2., True, 'regression'),
            (1., .8, 1.2, True, 'inconclusive-noise'),
            (.5, .5, .5, False, 'correctness-failed'),
            (1., 1., 1.02, True, 'inconclusive-noise'),
        ]:
            self.assertEqual(stats._historical_gate(median, low, high, admitted)[0], expected)

    def test_pairing_and_outer_gates_without_bootstrap(self):
        with patch.object(stats, '_bootstrap_medians', return_value=[.5, .5, .5]) as fake:
            result = stats.summarize([2., 4.], [4., 8.])
            self.assertEqual(result['samples'], [.5, .5])
            self.assertEqual(result['gate'], 'improvement')
            self.assertEqual(result['slower_pairs'], 0)
            fake.assert_called_once_with([.5, .5])
            short = stats.summarize([2., 4.], [4., 8.], short=True)
            self.assertEqual(short['gate'], 'inconclusive-short-block')
            self.assertEqual(short['historical_gate'], 'correctness-failed')
            rejected = stats.summarize([2., 4.], [4., 8.], admitted=False)
            self.assertEqual(rejected['gate'], 'correctness-or-cohort-failed')
            self.assertEqual(rejected['historical_gate'], 'correctness-failed')

    def test_empty_and_invalid_without_bootstrap(self):
        with patch.object(stats, '_bootstrap_medians', side_effect=AssertionError('must not bootstrap')):
            self.assertIsNone(stats.summarize([], []))
            for left, right in [([1], []), ([True], [1]), ([0], [1]), ([float('inf')], [1]), ([1], [-1])]:
                with self.assertRaises(ValueError): stats.summarize(left, right)
            result = stats.summarize_stratified([1.], [2.], [True])
            self.assertEqual(result['gate'], 'inconclusive-incomplete-family')

    def test_balanced_strata_with_mock_only(self):
        with patch.object(stats, '_bootstrap_medians', return_value=[2.]) as fake:
            result = stats.summarize_stratified([2.] * 48, [1.] * 48, [True, False] * 24)
            self.assertEqual(fake.call_count, 3)
            self.assertEqual([len(c.args[0]) for c in fake.call_args_list], [48, 24, 24])
            self.assertEqual(result['slower_pairs'], 48)
            self.assertEqual(result['gate'], 'regression')
            self.assertEqual(set(result['order_strata']), {'numerator_first', 'denominator_first'})
            for value in result['order_strata'].values():
                self.assertEqual(value['samples'], [2.] * 24)
                self.assertEqual(value['gate'], 'regression')
        with patch.object(stats, '_bootstrap_medians', side_effect=AssertionError('must not bootstrap')):
            with self.assertRaises(ValueError):
                stats.summarize_stratified([2.] * 48, [1.] * 48, [True] * 48)

    def test_rng_protocol_with_fake_rng_two_tiny_draws_only(self):
        class FakeRandom:
            def __init__(self, seed):
                self.seed = seed; self.calls = []
            def choices(self, population, k):
                self.calls.append((list(population), k)); return [population[0]] * k
        fake = FakeRandom(173)
        with patch.object(stats.random, 'Random', return_value=fake) as ctor:
            values = stats._bootstrap_medians([1., 2.], seed=173, resamples=2)
            self.assertEqual(values, [1., 1.])
            ctor.assert_called_once_with(173)
            self.assertEqual(fake.calls, [([1., 2.], 2), ([1., 2.], 2)])

if __name__ == '__main__':
    ast.parse((HERE / 'timing_statistics.py').read_text())
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceOnlyTests))
    output = {'status': 'passed-source-only-mocks' if result.wasSuccessful() else 'failed',
              'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
              'real_bootstrap_executed': False, 'saved_timing_values_read': False,
              'numerical_or_compiler_or_probe_process_launched': False,
              'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE / 'timing_statistics.py', Path(__file__)]}}
    (HERE / 'source-only-test-results.json').write_text(json.dumps(output, indent=2) + '\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
