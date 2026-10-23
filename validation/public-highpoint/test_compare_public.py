"""Regression tests for false qualification through mismatched provenance."""
from pathlib import Path
import copy
import json
import tempfile
import unittest

import compare_public as compare


class ReferenceBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path("validation/public-highpoint")
        cls.fixture = json.loads((here / "fixture-conditioned_masses.json").read_text())
        cls.reference = json.loads((here / "reference-conditioned_masses.json").read_text())
        cls.fixture_hash = compare.digest(here / "fixture-conditioned_masses.json")

    def test_captured_reference_binds_to_fixture_and_raw_transport(self):
        compare.validate_reference(self.reference, self.fixture, self.fixture_hash)

    def test_same_case_ids_do_not_allow_a_different_mass_family(self):
        wrong = json.loads(Path("validation/public-highpoint/reference.json").read_text())
        with self.assertRaisesRegex(ValueError, "another fixture"):
            compare.validate_reference(wrong, self.fixture, self.fixture_hash)

    def test_hash_alone_does_not_hide_changed_reference_request(self):
        wrong = copy.deepcopy(self.reference)
        lines = wrong["cases"][0]["request"].splitlines()
        values = lines[1].split()
        values[4] = "123"
        lines[1] = " ".join(values)
        wrong["cases"][0]["request"] = "\n".join(lines) + "\n"
        with self.assertRaisesRegex(ValueError, "propagators differ"):
            compare.validate_reference(wrong, self.fixture, self.fixture_hash)

    def test_response_must_match_recorded_transport(self):
        wrong = copy.deepcopy(self.reference)
        wrong["cases"][0]["response"]["moments"][0][3][1] = "123"
        with self.assertRaisesRegex(ValueError, "captured transport"):
            compare.validate_reference(wrong, self.fixture, self.fixture_hash)

    def test_wrong_pole_order_is_rejected_even_with_matching_raw_capture(self):
        wrong = copy.deepcopy(self.reference)
        case = wrong["cases"][0]
        case["response"]["poles"] = ["finite", "uv1", "ir1", "ir2"]
        case["stdout"] = "RESULT " + json.dumps(case["response"]) + "\n"
        with self.assertRaisesRegex(ValueError, "Laurent ordering"):
            compare.validate_reference(wrong, self.fixture, self.fixture_hash)


class ExecutionBindingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="public-provenance-", dir="target")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.here = self.root / "validation/public-highpoint"
        self.here.mkdir(parents=True)
        self.binary = self.root / "target/public-highpoint/highpoint_public"
        self.binary.parent.mkdir(parents=True)
        self.binary.write_bytes(b"test-only executable identity")
        source = self.root / "crates/iregi-rust/examples/highpoint_public.rs"
        source.parent.mkdir(parents=True)
        source.write_text("test-only source identity")
        self.fixture = self.here / "fixture-conditioned_masses.json"
        self.fixture.write_text("{}\n")
        self.output = self.here / "low.json"
        self.record = {"fixture": "validation/public-highpoint/fixture-conditioned_masses.json",
                       "settings": {"propagators": 6, "rank": 7, "algorithm": "PassarinoVeltman"},
                       "working_bits": 128, "requested_bits": 53, "rows": 1}
        self.output.write_text(json.dumps(self.record))
        self.log = self.output.with_suffix(".log")
        self.log.write_text("test log")
        self.build_path = self.here / "build.json"
        self.build = {"status": "passed", "changed_inputs": {}, "exit_code": 0,
                      "binary_sha256": compare.digest(self.binary), "source_sha256": compare.digest(source),
                      "library_source_hashes": {"example": "test-source-hash"},
                      "explicit_extern_sha256": {"example": "test-archive-hash"}}
        self.build_path.write_text(json.dumps(self.build))
        self.run_path = self.here / "low-run.json"
        self.run = {"status": "completed", "exit_code": 0, "last_public_stage": "all_lanes_success",
                    "result_sha256": compare.digest(self.output), "fixture_sha256": compare.digest(self.fixture),
                    "build_manifest_sha256": compare.digest(self.build_path), "binary_sha256": compare.digest(self.binary),
                    "probe_source_sha256": compare.digest(source), "log_sha256": compare.digest(self.log),
                    "command": ["taskset", "-c", "0", str(self.binary), self.record["fixture"],
                                "6", "7", "pv", "128", "53", "1", "validation/public-highpoint/low.json"]}

    def check(self):
        self.run_path.write_text(json.dumps(self.run))
        return compare.validate_provenance(self.record, self.output, self.fixture, self.root)

    def test_complete_matching_chain_is_accepted(self):
        self.assertEqual(self.check()["binary_sha256"], compare.digest(self.binary))

    def test_timeout_cannot_qualify_even_if_result_says_success(self):
        self.run.update(status="timeout", exit_code=-9)
        with self.assertRaisesRegex(ValueError, "unsuccessful"):
            self.check()

    def test_changed_result_or_build_is_rejected(self):
        self.output.write_text(self.output.read_text()+"\n")
        with self.assertRaisesRegex(ValueError, "mismatched"):
            self.check()
        self.run["result_sha256"] = compare.digest(self.output)
        self.build_path.write_text(self.build_path.read_text()+"\n")
        with self.assertRaisesRegex(ValueError, "mismatched"):
            self.check()

    def test_wrong_runtime_precision_and_changed_binary_are_rejected(self):
        self.run["command"][8] = "256"
        with self.assertRaisesRegex(ValueError, "command"):
            self.check()
        self.run["command"][8] = "128"
        self.binary.write_bytes(b"different binary")
        with self.assertRaisesRegex(ValueError, "executable"):
            self.check()

    def test_candidate_requires_post_build_and_run_source_verification(self):
        snapshot = self.root / "target/public-highpoint/candidate/source/crates/iregi-rust"
        (snapshot / "src").mkdir(parents=True)
        frozen = snapshot / "src/lib.rs"
        frozen.write_text("frozen test core")
        self.binary = self.root / "target/public-highpoint/candidate/highpoint_public"
        self.binary.write_bytes(b"candidate test-only executable")
        self.build_path = self.here / "candidate-build.json"
        self.build.update(core_exit_code=0, probe_exit_code=0,
                          binary_sha256=compare.digest(self.binary),
                          frozen_core_source=str(snapshot.relative_to(self.root)),
                          library_source_hashes={"crates/iregi-rust/src/lib.rs": compare.digest(frozen)})
        self.build_path.write_text(json.dumps(self.build))
        self.run.update(variant="candidate", binary_sha256=compare.digest(self.binary),
                        build_manifest_sha256=compare.digest(self.build_path),
                        frozen_source_files_unchanged=1)
        self.run["command"][3] = str(self.binary)
        with self.assertRaisesRegex(ValueError, "verify its frozen inputs"):
            self.check()
        self.build["frozen_core_sources_verified_after_build"] = True
        self.build_path.write_text(json.dumps(self.build))
        self.run["build_manifest_sha256"] = compare.digest(self.build_path)
        self.assertEqual(self.check()["variant"], "candidate")
        self.run["frozen_source_files_unchanged"] = 0
        with self.assertRaisesRegex(ValueError, "complete frozen core source"):
            self.check()
        self.run["frozen_source_files_unchanged"] = 1
        frozen.write_text("modified after compilation")
        with self.assertRaisesRegex(ValueError, "Frozen core source changed"):
            self.check()


if __name__ == "__main__":
    unittest.main()
