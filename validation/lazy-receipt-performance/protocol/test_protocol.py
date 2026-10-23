"""Synthetic protocol checks only; never execute a numeric benchmark."""
import unittest

from protocol import INITIAL_ITERATIONS, MATRIX, next_iterations, parse_calibration, parse_measurements


def fixture():
    log = []
    csv = ["workload,rows,block,order,implementation,iterations,ns_per_batch"]
    for name, rows in sorted(MATRIX):
        initial = INITIAL_ITERATIONS[name][0 if rows == 1 else 1]
        count = next_iterations(initial, 100_000_000)
        log.append(f"CALIBRATION,{name},{rows},0,baseline-first,{initial},100000000,150000000")
        log.append(f"CALIBRATION,{name},{rows},1,candidate-first,{count},220000000,300000000")
        for block in range(41):
            order = "baseline-first" if block % 2 == 0 else "candidate-first"
            for side in ("baseline", "candidate"):
                csv.append(f"{name},{rows},{block},{order},{side},{count},123.5")
    return "\n".join(log), "\n".join(csv)


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.log, self.csv = fixture()

    def test_complete_matrix(self):
        parsed = parse_measurements(self.csv, parse_calibration(self.log))
        self.assertEqual(len(parsed), 14)
        self.assertEqual(sum(len(blocks) for blocks in parsed.values()), 574)

    def test_changed_initial_count(self):
        with self.assertRaises(AssertionError):
            parse_calibration(self.log.replace(",0,baseline-first,128,", ",0,baseline-first,129,", 1))

    def test_changed_calibration_rule(self):
        with self.assertRaises(AssertionError):
            parse_calibration(self.log.replace(",1,candidate-first,262,", ",1,candidate-first,263,", 1))

    def test_calibration_below_target(self):
        with self.assertRaises(AssertionError):
            parse_calibration(self.log.replace(",220000000,300000000", ",199999999,300000000", 1))

    def test_missing_calibration_case(self):
        with self.assertRaises(AssertionError):
            parse_calibration("\n".join(self.log.splitlines()[2:]))

    def test_changed_timing_iterations(self):
        calibration = parse_calibration(self.log)
        row = self.csv.splitlines()[1].split(",")
        row[5] = str(int(row[5]) + 1)
        text = "\n".join([self.csv.splitlines()[0], ",".join(row), *self.csv.splitlines()[2:]])
        with self.assertRaises(AssertionError):
            parse_measurements(text, calibration)

    def test_nonpositive_or_nonfinite_time(self):
        for value in ("0", "-1", "nan", "inf", "-inf"):
            with self.subTest(value=value), self.assertRaises(AssertionError):
                parse_measurements(self.csv.replace(",123.5", f",{value}", 1), parse_calibration(self.log))

    def test_missing_or_duplicate_measurement(self):
        for text in ("\n".join(self.csv.splitlines()[:-1]), self.csv + "\n" + self.csv.splitlines()[1]):
            with self.assertRaises(AssertionError):
                parse_measurements(text, parse_calibration(self.log))

    def test_wrong_block_order(self):
        with self.assertRaises(AssertionError):
            parse_measurements(self.csv.replace(",0,baseline-first,", ",0,candidate-first,", 1), parse_calibration(self.log))


if __name__ == "__main__":
    unittest.main()
