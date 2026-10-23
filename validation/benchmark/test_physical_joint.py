"""Protocol/statistical tests only: no Rust, Fortran or Symbolica runtime."""
import copy
import importlib.util
import json
from pathlib import Path
import random
import statistics
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path.cwd()
spec = importlib.util.spec_from_file_location("physical_joint_checks", ROOT / "validation/benchmark/physical_joint.py")
joint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(joint)


class StatisticsTests(unittest.TestCase):
    def test_ratio_of_medians_uses_all_unequal_independent_samples(self):
        a, b = [1, 2, 8], [1, 1, 4, 4, 4]
        got = joint.independent_ratio(a, b, seed=123, resamples=321)
        rng = random.Random(123)
        draws = [statistics.median(rng.choices(a, k=3)) / statistics.median(rng.choices(b, k=5)) for _ in range(321)]
        self.assertEqual(got["ratio"], 0.5)
        self.assertEqual(got["sample_counts"], [3, 5])
        self.assertEqual(got["ci99"], [joint.kernel.quantile(draws, p) for p in [0.005, 0.995]])
        self.assertNotEqual(got["ratio"], statistics.median(x/y for x,y in zip(a,b)))

    def test_independent_bootstrap_does_not_cancel_shared_order_noise(self):
        a = [1] * 10 + [10] * 11
        got = joint.independent_ratio(a, a, resamples=1000)
        self.assertGreater(got["relative_ci_width"], 0.02)
        self.assertEqual(got["statistical_gate"], "inconclusive-noise")

    def test_operational_gates_and_invalid_timings(self):
        for a, expected in [(1,"improvement"), (2,"parity"), (3,"regression")]:
            self.assertEqual(joint.independent_ratio([a]*21, [2]*23, resamples=30)["statistical_gate"], expected)
        for bad in [[], [True], [0], [-1], [float("nan")], [float("inf")], ["1"]]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                joint.independent_ratio(bad, [1])
        for a, b in [(1e308,1e-308),(1e-308,1e308)]:
            with self.assertRaises(ValueError):
                joint.independent_ratio([a],[b],resamples=3)


class LedgerTests(unittest.TestCase):
    def test_saved_complete_result_cannot_override_failed_producer_exit(self):
        joint.require_phase_success(dict(status="complete",returncode=0),"Rust")
        for phase in [dict(status="failed",returncode=7),dict(status="failed",returncode=-9),
                      dict(status="interrupted",returncode=0),dict(status="complete",returncode=False),
                      dict(status="complete")]:
            with self.subTest(phase=phase), self.assertRaises(ValueError):
                joint.require_phase_success(phase,"Rust")

    def test_all_unrun_interrupted_and_failed_families_stay_visible(self):
        data = {"rows":[{"status":"pending", "gate":"not_run"}, {"status":"running"},
                        {"status":"failed", "gate":"unqualified"}, {"status":"measured", "gate":"improvement"}]}
        joint.finish_rows(data, False)
        self.assertEqual([r["status"] for r in data["rows"]], ["not_run", "interrupted", "failed", "measured"])
        self.assertEqual(data["status"], "interrupted")
        self.assertFalse(data["performance_parity_established"])

    def test_statistical_noise_or_regression_prevents_all_family_parity(self):
        for gate in ["inconclusive-noise", "regression", "diagnostic-protocol", "provenance-changed"]:
            data = {"rows":[dict(status="measured",gate="parity"),dict(status="measured",gate=gate)]}
            joint.finish_rows(data, True)
            self.assertFalse(data["performance_parity_established"])
        data = {"rows":[dict(status="measured",gate="parity")]}
        joint.finish_rows(data, False)
        self.assertFalse(data["performance_parity_established"])

    def test_file_identity_is_rechecked_and_evidence_is_copied(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            original = root / "original"
            original.write_text("first")
            saved = joint.retain_file(original, root / "private/copy")
            original.write_text("later")
            joint.verify_file(saved)
            Path(saved["path"]).write_text("changed")
            with self.assertRaises(ValueError):
                joint.verify_file(saved)

    def test_interruption_and_final_hash_error_still_persist_terminal_ledger(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            placeholder = root / "input"
            placeholder.write_text("{}")
            output = root / "attempt/results.json"
            cpu = min(joint.os.sched_getaffinity(0))
            argv = ["--execute", "--cases", "ggh", "--batches", "1", "--cpu", str(cpu),
                    "--build-cpus", str(cpu), "--rust", str(placeholder), "--oracle", str(placeholder),
                    "--build-manifest", str(placeholder), "--output", str(output)]
            with patch.object(joint.kernel,"source_hashes",side_effect=[{},OSError("source disappeared")]), \
                 patch.object(joint.rust,"physical_asset_hashes",return_value={}), \
                 patch.object(joint.alignment,"contract",return_value={}), \
                 patch.object(joint,"validate_build_completion",return_value={}), \
                 patch.object(joint,"phase",side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
                joint.main(argv)
            saved = json.loads(output.read_text())
            self.assertEqual(saved["status"],"interrupted")
            self.assertEqual(saved["rows"][0]["status"],"interrupted")
            self.assertFalse(saved["performance_parity_established"])
            self.assertFalse(saved["producer_inputs_unchanged"])
            self.assertIn("source disappeared",saved["final_provenance_error"])

    def test_a_new_ledger_name_cannot_overwrite_an_existing_artifact_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            evidence = root / "previous-response.jsonl"
            evidence.write_text("retained")
            cpu = min(joint.os.sched_getaffinity(0))
            with self.assertRaisesRegex(ValueError,"fresh output directory"):
                joint.main(["--cases","ggh","--cpu",str(cpu),"--build-cpus",str(cpu),
                            "--output",str(root/"different-results.json")])
            self.assertEqual(evidence.read_text(),"retained")


class WorkspaceManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.parent_path = self.root / "workspace.json"
        self.binary = self.root / "physical_benchmark"
        self.binary.write_text("test binary identity only")
        self.archive = self.root / "masters.rlib"
        self.archive.write_text("test archive identity only")
        self.builder = self.root / "builder.py"
        self.builder.write_text("# retained builder identity\n")
        original = "/original/physical_benchmark"
        self.events = [dict(reason="compiler-artifact",target=dict(kind=["example"],name=name,
                                  src_path=str(self.root / "crates/iregi-cli/examples/physical_benchmark.rs") if name == "physical_benchmark" else "/kernel.rs"),
                            profile=dict(opt_level="3"),executable=original if name == "physical_benchmark" else "/kernel")
                       for name in ["physical_benchmark","kernel_benchmark"]]
        self.events.append(dict(reason="compiler-artifact",target=dict(kind=["lib"],name="iregi_masters"),
                                profile=dict(opt_level="3"),features=["default"],filenames=["/original/masters.rlib"]))
        self.events.append(dict(reason="build-finished",success=True))
        shared = dict(status="complete",started_at="start",finished_at="finish",command=["cargo","build"],
                      requested_revision="revision",source_revision="revision",source_root=str(self.root),
                      master_backend="SymbolicaBatch",backend_qualification="features",environment={},
                      profile="release",rustc="rustc",cargo="cargo",source_sha256={"code":"hash"},
                      assets_sha256={"input":"hash"},provenance_qualified=True)
        self.parent = dict(shared,kind="workspace-benchmark-build",manifest_path=str(self.parent_path),
                           resources=dict(returncode=0),source_sha256_before=shared["source_sha256"],
                           assets_sha256_before=shared["assets_sha256"],
                           binaries={"physical_benchmark":dict(path=str(self.binary),original_path=original,sha256=joint.kernel.digest(self.binary))},
                           archives=[dict(path=str(self.archive),original_path="/original/masters.rlib",sha256=joint.kernel.digest(self.archive))],
                           builder=dict(files=[dict(retained_path=str(self.builder),sha256=joint.kernel.digest(self.builder))]))
        self.child = dict(shared,kind="physical-rust-build",binary_path=str(self.binary),binary_sha256=joint.kernel.digest(self.binary),
                          workspace_build_manifest=str(self.parent_path))
        self.save()

    def save(self):
        path = self.root / "cargo.jsonl"
        path.write_text("".join(json.dumps(event)+"\n" for event in self.events))
        examples = {event["target"]["name"]:event for event in self.events[:2]}
        self.parent["cargo_artifacts"] = dict(examples=examples,libraries=[self.events[2]])
        self.parent_path.write_text(json.dumps(self.parent))

    def test_missing_child_exit_is_verified_without_changing_any_manifest(self):
        before = self.parent_path.read_bytes()
        child = copy.deepcopy(self.child)
        proof = joint.validate_build_completion(self.child)
        self.assertEqual(proof["kind"],"verified-workspace-parent")
        self.assertEqual(proof["returncode"],0)
        self.assertEqual(proof["parent_manifest"]["sha256"],joint.kernel.digest(self.parent_path))
        self.assertEqual(set(proof["child_fields_supplied_by_parent"]),{"returncode","source_sha256_before","assets_sha256_before"})
        self.assertEqual(self.child,child)
        self.assertEqual(self.parent_path.read_bytes(),before)

    def test_parent_nonzero_or_missing_exit_cannot_be_inferred_from_artifacts(self):
        for resources in [{},dict(returncode=1),dict(returncode=False)]:
            self.parent["resources"] = resources
            self.save()
            with self.assertRaises(ValueError):
                joint.validate_build_completion(self.child)

    def test_child_source_backend_and_binary_must_match_parent(self):
        for field,value in [("source_revision","different"),("source_sha256",{"code":"different"}),
                            ("master_backend","RustBatch"),("binary_sha256","different"),("returncode",7)]:
            child = dict(self.child,**{field:value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                joint.validate_build_completion(child)

    def test_actual_cargo_finish_and_feature_records_are_required(self):
        events = copy.deepcopy(self.events)
        for mutate in [lambda: self.events[-1].update(success=False),
                       lambda: self.events[2].update(features=["default","native-batch"]),
                       lambda: self.events[0].update(executable="/different")]:
            self.events = copy.deepcopy(events)
            mutate()
            self.save()
            with self.assertRaises(ValueError):
                joint.validate_build_completion(self.child)

    def test_retained_binary_archive_and_builder_tampering_is_rejected(self):
        for path in [self.binary,self.archive,self.builder]:
            original = path.read_bytes()
            path.write_text("modified")
            with self.subTest(path=path), self.assertRaises(ValueError):
                joint.validate_build_completion(self.child)
            path.write_bytes(original)


class OutputTests(unittest.TestCase):
    def test_exact_sample_and_execution_width_before_any_comparison(self):
        config = joint.rust.request_configuration("ggh", "f64", 53, 53, "hybrid", 3)
        for output in [{"samples":[{}], "execution":{"input_rows":3}},
                       {"samples":[{}, {}, {}], "execution":{"input_rows":1}}]:
            with self.assertRaises(ValueError):
                joint.check_output("ggh", 3, output, config, [], {})

    def test_all_tensor_components_reject_nonfinite_and_boolean_pairs(self):
        config = joint.rust.request_configuration("ggh", "f64", 53, 53, "hybrid", 1)
        for pair in [[True,0], ["nan",0], [1,2,3]]:
            output = {"samples":[{"moments":[[pair,[0,0],[0,0],[0,0]]]}], "execution":{"input_rows":1}}
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                joint.check_output("ggh", 1, output, config, [], {})

    def test_both_canonical_tensor_and_preserved_graph_checks_are_required(self):
        output = {"samples":[{"moments":[]}], "execution":{"input_rows":1}}
        for tensor_pass, graph_pass in [(False,True),(True,False)]:
            with patch.object(joint.rust,"check",return_value={"passed":tensor_pass}), \
                 patch.object(joint.alignment,"compare_rust_output",return_value={"passed":graph_pass}), \
                 self.assertRaises(ValueError):
                joint.check_output("ggh",1,output,{},[],{})


class ResponseJoinTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.options = dict(cpu=0,batches=[1],repeats=3,warmup=3,block_ms=30)
        self.configuration = joint.rust.request_configuration("ggh", "f64",53,53,"hybrid",1)
        self.identity = self.configuration["id"]
        self.output = {"execution":{"input_rows":1},"samples":[{"moments":[]}]}
        self.row = dict(id=self.identity,case="ggh",batch_width=1,status="measured",precision="f64",bits=53,
                        accuracy_bits=53,master_backend="SymbolicaBatch",initial_output=self.output,
                        stages={stage:dict(iterations_per_block=2,samples_ns=[10,11,12]) for stage in joint.STAGES},
                        profiled_components={name:joint.rust.summarized([value]*3)
                                             for name,value in zip(["arguments","masters","reduction","total"],[1,2,3,6])},
                        stage_orders=[joint.STAGES]*3)
        self.responses = [dict(request={"op":"prepare","id":self.identity},
                               response={"id":self.identity,"status":"prepared","output":self.output,"master_backend":"SymbolicaBatch"})]
        for stage in joint.STAGES:
            self.add(stage, 3, 1, 100)
        for value in [10,11,12]:
            for stage in joint.STAGES:
                self.add(stage, 0, 2, value)
        for _ in range(3):
            self.add("reduction",0,2,99,True)
        canonical = self.directory / "canonical.json"
        canonical.write_text("[]")
        self.files = {"canonical":joint.record_file(canonical)}

    def add(self, stage, warmup, iterations, value, profile=False):
        request = dict(op="measure",id=self.identity,stage=stage,warmup=warmup,iterations=iterations,repeats=1)
        if profile:
            request["profile"] = True
        response = dict(id=self.identity,status="measured",stage=stage,warmup=warmup,iterations=iterations,repeats=1,
                        profiled=profile,total_ns=[value],profile_order=["arguments","masters","reduction","total"],
                        profile_ns=[[1,2,3,6]] if profile else [], output=self.output)
        self.responses.append(dict(request=request,response=response))

    def validate(self):
        path = self.directory / "responses.jsonl"
        path.write_text("".join(json.dumps(row)+"\n" for row in self.responses))
        self.files["responses"] = joint.record_file(path)
        with patch.object(joint,"check_output",return_value={"passed":True}) as checked:
            result = joint.validate_rust_row("ggh",1,self.row,self.files,{},self.options,"SymbolicaBatch")
            self.assertEqual(checked.call_count, len(self.responses)+1)
            return result

    def test_pilots_and_profile_values_are_not_joined_to_timings(self):
        self.assertEqual(self.validate()["checked_responses"], 20)

    def test_missing_duplicate_or_modified_blocks_fail(self):
        original = copy.deepcopy(self.responses)
        for mutate in [lambda: self.responses.pop(),
                       lambda: self.responses.append(copy.deepcopy(self.responses[-1])),
                       lambda: self.responses[5]["response"].update(total_ns=[999]),
                       lambda: self.responses[5]["request"].update(iterations=3),
                       lambda: self.responses[5]["response"].update(profiled=True)]:
            self.responses = copy.deepcopy(original)
            mutate()
            with self.assertRaises(ValueError):
                self.validate()

    def test_backend_failed_row_and_missing_stage_are_rejected(self):
        original = copy.deepcopy(self.row)
        for mutate in [lambda: self.row.update(status="failed"),
                       lambda: self.row.update(master_backend="RustBatch"),
                       lambda: self.row["stages"].pop("numerator")]:
            self.row = copy.deepcopy(original)
            mutate()
            with self.assertRaises((ValueError,KeyError)):
                self.validate()


if __name__ == "__main__":
    unittest.main()
