"""Boundary tests use fixtures and synthetic records, never numerical runtimes."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path.cwd()
spec = importlib.util.spec_from_file_location("physical_alignment_checks", ROOT / "validation/benchmark/physical_alignment.py")
alignment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alignment)
benchmark = alignment.madloop


def reference(case):
    fixture, _ = alignment.fixture_and_input(case)
    expected = alignment.contract(case)
    group = fixture["selected_feynkit_group"]
    state = {"onshell_iregi": False, "check": False, "threshold": 1e-6}
    return dict(status="measured", precision="binary64", mode="Hybrid", helicity_index=1,
                workload_contract="madloop-selected-generated-graph-v1",
                graph=expected["madloop_graph"],
                observed_input_policy=dict(name="preserve", timer=state, ordinary_graphs={str(group): state},
                                           checked_before_every_timed_step=True),
                observed_call_modes={"ctmode": 1, "iregimode": 2, "algorithm": "Hybrid"},
                correctness=dict(status="passed", max_error=0.0, committed_fixture_input_identity_passed=True),
                reference_record=copy.deepcopy(next(row for row in fixture["records"] if row["group"] == group)),
                metadata=copy.deepcopy(fixture["metadata"]),
                provenance={"fixture_sha256":expected["asset_sha256"][f"validation/physical/madloop/fixtures/{case}-helicity-1.json"]})


class PolicyTests(unittest.TestCase):
    def test_actual_preserved_and_legacy_states_are_distinguished(self):
        for policy, enabled in [("preserve", "F"), ("legacy", "T")]:
            text = f"IREGI_GRAPH_POLICY 2 {enabled} F 1e-6\nIREGI_BENCH_POLICY {enabled} F 1e-6\n"
            observed = benchmark.observed_input_policy(text, policy, 2)
            self.assertEqual(observed["name"], policy)
            self.assertEqual(observed["timer"]["onshell_iregi"], enabled == "T")

    def test_missing_duplicate_malformed_or_effectively_snapped_states_fail(self):
        valid = "IREGI_GRAPH_POLICY 2 F F 1e-6\nIREGI_BENCH_POLICY F F 1e-6\n"
        bad = ["", valid + "IREGI_BENCH_POLICY F F 1e-6\n",
               valid + "IREGI_GRAPH_POLICY 2 F F 1e-6\n",
               valid.replace("2 F F", "2 T F"), valid.replace("F F", "F T"),
               valid.replace("1e-6", "nan"), valid.replace("1e-6", "1e-3"),
               valid.replace("2 F F", "2 maybe F"), valid.replace(" 2 ", " 3 ")]
        for text in bad:
            with self.subTest(text=text), self.assertRaises(RuntimeError):
                benchmark.observed_input_policy(text, "preserve", 2)

    def test_policy_is_applied_after_initializers_and_checked_before_reduction(self):
        original = ("      CALL INITIREGI(IREGIRECY,LOOPLIB,1D-6)\n"
                    "          CALL IMLOOP(CTMODE,IREGIMODE,NLOOPLINE,LOOPMAXCOEFS,RANK\n"
                    "      WRITE(*,*) 'IREGI_AUDIT_END'\n")
        instrumented = benchmark.instrument_input_policy(original, "ML5_0_")
        self.assertIn("CALL INITIREGI(IREGIRECY,LOOPLIB,1D-6)\n      CALL ML5_0_AUDIT_SET_POLICY()", instrumented)
        self.assertLess(instrumented.index("AUDIT_CHECK_POLICY()"), instrumented.index("CALL IMLOOP"))
        with self.assertRaises(RuntimeError):
            benchmark.instrument_input_policy(original + original, "ML5_0_")
        args = argparse.Namespace(batch_widths=[1, 3], n_groups=2, repeats=3,
                                  warmup=0, target_ms=0.1, input_policy="preserve")
        timer = benchmark.timer_source("ML5_0_", 2, args)
        self.assertIn("CALL INITIREGI(.TRUE.,2,1D-6)\n      CALL ML5_0_AUDIT_SET_POLICY()", timer)
        self.assertLess(timer.index("AUDIT_REPORT_POLICY(0)"), timer.index("CALL SYSTEM_CLOCK"))
        step = timer[timer.index("SUBROUTINE ML5_0_AUDIT_STEP"):]
        self.assertLess(step.index("CALL ML5_0_AUDIT_CHECK_POLICY()"), step.index("IF(STAGE.EQ.1)"))
        self.assertIn("ONSHELL_IREGI=.FALSE.", timer)
        self.assertTrue(all(len(line) <= 132 for line in timer.splitlines()))

    def test_exact_input_comparison_retains_signed_zero_and_rejects_nonfinite(self):
        benchmark.exact_numeric_identity(["1e0", "-0.0"], ["1.0", "-0"], "input")
        for actual, expected in [("0", "-0"), ("nan", "nan"), (True, "1"), (["1"], ["1", "2"])]:
            with self.subTest(actual=actual), self.assertRaises(RuntimeError):
                benchmark.exact_numeric_identity(actual, expected, "input")


class ContractTests(unittest.TestCase):
    def test_all_four_qualified_assets_declare_equivalent_not_tensor_workloads(self):
        ranks = {"ggh": (2, 3), "gghh": (4, 4), "gghhh": (4, 5), "gggg-up": (4, 4)}
        for case, expected in ranks.items():
            with self.subTest(case=case):
                contract = alignment.contract(case)
                self.assertEqual((contract["rust_rank"], contract["madloop_rank"]), expected)
                self.assertIs(contract["matched_tensor_workload"], False)
                self.assertIs(contract["timing_parity_established"], False)
                alignment.validate_reference(case, reference(case))

    def test_legacy_partial_failed_and_different_graph_reference_records_fail(self):
        mutations = [lambda r: r.update(status="failed"),
                     lambda r: r["observed_input_policy"].update(name="legacy"),
                     lambda r: r["observed_input_policy"].update(checked_before_every_timed_step=False),
                     lambda r: r["reference_record"]["raw_result"].pop(),
                     lambda r: r["reference_record"]["tensors"].pop(),
                     lambda r: r["reference_record"]["tensors"][0].update(laurent_slot=2),
                     lambda r: r["reference_record"]["raw_result"][0].append("0"),
                     lambda r: r["metadata"]["parameters"].__setitem__(0, "174"),
                     lambda r: r["correctness"].update(max_error=float("nan")),
                     lambda r: r["provenance"].update(fixture_sha256="wrong")]
        for mutate in mutations:
            value = reference("ggh")
            mutate(value)
            with self.subTest(mutation=mutate), self.assertRaises((ValueError, RuntimeError)):
                alignment.validate_reference("ggh", value)

    def test_preserved_fixture_only_exports_the_validated_selected_graph(self):
        fixture = alignment.preserved_fixture("gghh", reference("gghh"))
        self.assertEqual(fixture["input_policy"], "Preserve")
        self.assertEqual(len(fixture["records"]), 1)
        self.assertEqual(fixture["records"][0]["group"], 2)

    def test_final_three_slot_adapter_keeps_factors_and_precision_scope(self):
        case = "ggh"
        ref = reference(case)
        _, sample = alignment.fixture_and_input(case)
        physical = alignment.physical
        final = [physical.CASES[case][2] * physical.number(value) for value in ref["reference_record"]["raw_result"]]
        result = dict(precision_bits=53, algorithm_requested="Hybrid", precision_control={"accuracy_bits":53},
                      settings=dict(input_policy="Preserve", convention="OneLoop", rank=2, dimension_shift=0,
                                    powers=[1]*3, propagators=3, tensor_weights="Components"),
                      graph={"name":"ggh_top_triangle"}, poles=["uv1", "ir1", "ir2", "finite"],
                      samples=[dict(status="success", id=sample["id"], integral=[physical.pair(final[1]), [0,0], physical.pair(final[2]), physical.pair(final[0])])])
        checked = alignment.compare_rust_output(case, ref, result)
        self.assertTrue(checked["passed"])
        self.assertFalse(checked["timing_parity_established"])
        result["precision_bits"] = 128
        with self.assertRaises(ValueError):
            alignment.compare_rust_output(case, ref, result)


if __name__ == "__main__":
    unittest.main()
