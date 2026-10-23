"""Safety checks for the validation-artifact comparator; no reduction runtime."""

import contextlib
import copy
from decimal import Decimal, localcontext
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("precision_comparator", Path(__file__).with_name("compare_precision_oracle.py"))
comparator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(comparator)


def fixture():
    # Constant and four vector components, in IREGI ordering.
    monomials = [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    oracle = {
        "rank": 1, "propagators": 1, "moments": 5, "mu": 3,
        "mass_squared": [4], "shifts": [[0, 0, 0, 0]], "status": "passed",
        "reference": {"stable": True, "moments": [[[0, 0] for _ in range(4)] for _ in range(5)]},
        "discrepancies": [],
    }
    precision = {
        "input": "same-path-can-contain-stale-input.json",
        "input_snapshot": {"rank": 1, "mu": "3", "propagators": [
            {"shift": ["0"]*4, "mass_squared": ["4", "0"], "power": 1}]},
        "normalization": comparator.NORMALIZATION, "dimension_shift": 0,
        "propagator_powers": "unit", "input_decimal_embedding_bits": 1024,
        "results": [{"bits": bits, "moments": [
            {"index": i, "monomial": list(m), "oneloop_native_slots": [["0", "0"] for _ in range(4)]}
            for i, m in enumerate(monomials)]} for bits in [128, 256]],
    }
    return oracle, precision


def retained_row():
    return {"moment": 4, "monomial": [0, 0, 0, 1], "slot": 3, "component": 1,
            "actual_normalized": "1", "expected_normalized": "0", "mixed_error": "1"}


class ComparatorTests(unittest.TestCase):
    def test_complete_zero_array_cannot_qualify_missing_rust_data(self):
        result = comparator.compare(*fixture())
        self.assertTrue(result["qualified_oracle"])
        self.assertEqual(result["coefficients_compared_per_array"], 40)
        self.assertFalse(result["rust_complete_array"])
        self.assertIsNone(result["rust_agreement_passed"])

    def test_reference_only_never_qualifies_a_rust_comparison(self):
        oracle, precision = fixture()
        oracle.update(status="reference_only", reference_stable=True)
        result = comparator.compare(oracle, precision)
        self.assertTrue(result["qualified_oracle"])
        self.assertTrue(result["reference_only"])
        self.assertFalse(result["rust_complete_array"])
        self.assertIsNone(result["rust_agreement_passed"])
        self.assertEqual(result["rust_coefficients_compared"], 0)
        contaminated = copy.deepcopy(oracle)
        contaminated["discrepancies"] = [retained_row()]
        with self.assertRaises(comparator.ArtifactError):
            comparator.compare(contaminated, precision)
        contaminated = copy.deepcopy(oracle)
        contaminated["rust_original_master_moments_normalized"] = [[["0", "0"] for _ in range(4)] for _ in range(5)]
        with self.assertRaises(comparator.ArtifactError):
            comparator.compare(contaminated, precision)
        oracle["reference_stable"] = False
        with self.assertRaises(comparator.ArtifactError):
            comparator.compare(oracle, precision)

    def test_native_phase_and_rank_dependent_units(self):
        oracle, precision = fixture()
        for level in precision["results"]:
            level["moments"][1]["oneloop_native_slots"][3] = ["0", "1"]
        result = comparator.compare(oracle, precision)
        discrepancy = next(row for row in result["reference_discrepancies"]
                           if (row["moment"], row["slot"], row["component"]) == (1, 3, 0))
        with localcontext() as context:
            context.prec = 60
            pi = Decimal("3.14159265358979323846264338327950288419716939937510582097494459")
            # i*pi^2 times i, divided by Q^(rank+4-2N)=2^3.
            self.assertLess(abs(Decimal(discrepancy["truth_normalized"]) + pi*pi/8), Decimal("1e-55"))

    def test_scaleless_uv_ir_cancellation_survives_normalization(self):
        oracle, precision = fixture()
        for level in precision["results"]:
            level["moments"][0]["oneloop_native_slots"][0] = ["1", "0"]
            level["moments"][0]["oneloop_native_slots"][1] = ["-1", "0"]
        result = comparator.compare(oracle, precision)
        rows = [r for r in result["reference_discrepancies"] if r["moment"] == 0]
        self.assertEqual({(r["slot"], r["component"]) for r in rows}, {(0, 1), (1, 1)})
        self.assertEqual(Decimal(rows[0]["truth_normalized"]),
                         Decimal(rows[1]["truth_normalized"]).copy_negate())

    def test_partial_duplicate_negative_and_misordered_moments_rejected(self):
        mutations = [
            lambda p: p["results"][1].update(moments=[]),
            lambda p: p["results"][0]["moments"].pop(),
            lambda p: p["results"][1]["moments"][4].update(index=3),
            lambda p: p["results"][1]["moments"][4].update(index=-1),
            lambda p: p["results"][1]["moments"][4].update(index=True),
            lambda p: p["results"][0]["moments"][4].update(monomial=[1, 0, 0, 0]),
            lambda p: p["results"][1]["moments"][4].update(monomial=[0, 0, 0, True]),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                oracle, precision = fixture()
                mutate(precision)
                with self.assertRaises(comparator.ArtifactError):
                    comparator.compare(oracle, precision)

    def test_precision_and_laurent_schema_rejected(self):
        mutations = [
            lambda p: p["results"][0].update(bits=256),
            lambda p: p["results"][0].update(bits="128"),
            lambda p: p["results"][0]["moments"][0]["oneloop_native_slots"].append(["0", "0"]),
            lambda p: p["results"][0]["moments"][0]["oneloop_native_slots"][0].append("0"),
            lambda p: p["results"][0]["moments"][0]["oneloop_native_slots"].__setitem__(0, [0.0, "0"]),
            lambda p: p["results"][0]["moments"][0]["oneloop_native_slots"].__setitem__(0, ["NaN", "0"]),
            lambda p: p["results"][0]["moments"][0]["oneloop_native_slots"].__setitem__(0, ["Infinity", "0"]),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                oracle, precision = fixture()
                mutate(precision)
                with self.assertRaises(comparator.ArtifactError):
                    comparator.compare(oracle, precision)

    def test_snapshot_prevents_stale_or_incompatible_input(self):
        mutations = [
            lambda p: p.pop("input_snapshot"),
            lambda p: p["input_snapshot"].update(mu="4"),
            lambda p: p["input_snapshot"]["propagators"][0]["shift"].__setitem__(0, "1"),
            lambda p: p["input_snapshot"]["propagators"][0]["mass_squared"].__setitem__(1, "1"),
            lambda p: p["input_snapshot"]["propagators"][0].update(power=2),
            lambda p: p["input_snapshot"].update(scalar_products=None),
            lambda p: p["input_snapshot"].update(dimension_shift=1),
            lambda p: p["input_snapshot"].update(tensor_weights="Multinomial"),
            lambda p: p.update(normalization="IREGI"),
            lambda p: p.update(dimension_shift=1),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                oracle, precision = fixture()
                mutate(precision)
                with self.assertRaises(comparator.ArtifactError):
                    comparator.compare(oracle, precision)

    def test_incomplete_or_unstable_reference_rejected(self):
        mutations = [
            lambda o: o.update(status="started"),
            lambda o: o.update(status="preparation_failed"),
            lambda o: o.update(moments=4),
            lambda o: o["reference"].update(stable=False),
            lambda o: o["reference"].update(stable=1),
            lambda o: o["reference"]["moments"].pop(),
            lambda o: o["reference"]["moments"][0].__setitem__(0, ["NaN", 0]),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                oracle, precision = fixture()
                mutate(oracle)
                with self.assertRaises(comparator.ArtifactError):
                    comparator.compare(oracle, precision)

    def test_retained_discrepancies_cannot_disappear_or_mismatch_reference(self):
        oracle, precision = fixture()
        oracle["status"] = "failed"
        oracle["discrepancies"] = [retained_row()]
        report = comparator.compare(oracle, precision)
        self.assertEqual(len(report["retained_binary64_disagreements"]), 1)
        self.assertFalse(report["rust_agreement_passed"])
        for change in [{"moment": 5}, {"slot": -1}, {"component": 2},
                       {"monomial": [1, 0, 0, 0]}, {"expected_normalized": "1"}]:
            with self.subTest(change=change):
                altered = copy.deepcopy(oracle)
                altered["discrepancies"][0].update(change)
                with self.assertRaises(comparator.ArtifactError):
                    comparator.compare(altered, precision)
        oracle["discrepancies"].append(retained_row())
        with self.assertRaises(comparator.ArtifactError):
            comparator.compare(oracle, precision)

    def test_complete_rust_array_is_checked_beyond_retained_disagreements(self):
        oracle, precision = fixture()
        oracle["rust_original_master_moments_normalized"] = [[["0", "0"] for _ in range(4)] for _ in range(5)]
        oracle["rust_original_master_moments_normalized"][4][3][1] = "1"
        report = comparator.compare(oracle, precision)
        self.assertTrue(report["rust_complete_array"])
        self.assertFalse(report["rust_agreement_passed"])
        self.assertEqual(report["rust_coefficients_compared"], 40)
        self.assertEqual(len(report["rust_discrepancies"]), 1)
        oracle["rust_original_master_moments_normalized"].pop()
        with self.assertRaises(comparator.ArtifactError):
            comparator.compare(oracle, precision)

    def test_nonconvergence_cannot_qualify_reference_or_rust(self):
        oracle, precision = fixture()
        precision["results"][0]["moments"][0]["oneloop_native_slots"][3][0] = "1"
        oracle["rust_original_master_moments_normalized"] = [[["0", "0"] for _ in range(4)] for _ in range(5)]
        report = comparator.compare(oracle, precision)
        self.assertFalse(report["qualified_oracle"])
        self.assertFalse(report["reference_agreement_passed"])
        self.assertFalse(report["rust_agreement_passed"])

    def test_duplicate_keys_and_nonfinite_json_are_rejected(self):
        for data in ['{"results":[],"results":[]}', '{"value": NaN}', '{"value": Infinity}']:
            with self.subTest(data=data), self.assertRaises(comparator.ArtifactError):
                comparator.read_json(data)

    def test_invalid_input_replaces_a_stale_success_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            oracle_path, precision_path, output = [root / name for name in ("oracle.json", "precision.json", "report.json")]
            oracle, precision = fixture()
            oracle_path.write_text(json.dumps(oracle))
            precision_path.write_text(json.dumps(precision))
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(comparator.main([str(oracle_path), str(precision_path), str(output)]), 0)
                self.assertTrue(json.loads(output.read_text())["qualified_oracle"])
                precision_path.write_text('{"results":')
                self.assertEqual(comparator.main([str(oracle_path), str(precision_path), str(output)]), 2)
            invalid = json.loads(output.read_text())
            self.assertEqual(invalid["status"], "invalid")
            self.assertFalse(invalid["qualified_oracle"])
            self.assertFalse(invalid["precision_convergence_passed"])


if __name__ == "__main__":
    unittest.main()
