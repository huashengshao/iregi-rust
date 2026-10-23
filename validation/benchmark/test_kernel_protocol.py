"""Exercise kernel main's protocol/provenance gates without numerical engines."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
import run as kernel


class KernelMainProtocolTests(unittest.TestCase):
    def fixture(self, transform=None, *, replace_binary=False, fail_final_hash=False):
        (kernel.ROOT / "target").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="kernel-main-test-", dir=kernel.ROOT / "target") as temporary:
            directory = Path(temporary)
            rust, reference = directory / "rust", directory / "reference"
            rust.write_bytes(b"original-rust")
            reference.write_bytes(b"original-reference")
            snapshot = directory / "snapshot"
            snapshot.mkdir()
            source_hashes = {"Cargo.toml": "frozen-source"}
            live_hashes = {"validation/benchmark/run.py": "live-harness"}
            rust_manifest = directory / "chosen-rust-build.json"
            reference_manifest = directory / "chosen-reference-build.json"
            rust_manifest.write_text(json.dumps({
                "binary_sha256": kernel.digest(rust), "source_root": str(snapshot),
                "source_sha256": source_hashes, "master_backend": "test-backend",
            }))
            reference_manifest.write_text(json.dumps({"binary_sha256": kernel.digest(reference)}))
            sample = {"shifts": [[0., 0., 0., 0.], [0., 1., 0., 0.]],
                      "masses": [[2., 0.], [3., 0.]], "mu": 1.}
            case = {"id": "fixture", "n": 2, "rank": 0,
                    "mass_class": "massive", "samples": [sample]}
            inputs = directory / "inputs.json"
            inputs.write_text(json.dumps([case]))
            output = directory / "result.json"
            state = {"closed": False, "spawned_hashes": {}, "requests": []}

            def hashes(path=None):
                if fail_final_hash and state["closed"]:
                    raise FileNotFoundError("source removed before final provenance collection")
                return source_hashes if path is not None and Path(path) == snapshot else live_hashes

            class FakeProcess:
                def __init__(self, binary, label, *_args):
                    self.label = label
                    if replace_binary and label == "rust":
                        # An independently rebuilt original path must either
                        # fail provenance or leave a frozen executed copy intact.
                        rust.write_bytes(b"replacement-rust")
                    state["spawned_hashes"][label] = kernel.digest(binary)

                def request(self, payload):
                    if self.label == "rust":
                        request = json.loads(payload)
                    else:
                        fields = payload.splitlines()[0].split()
                        request = {"id": fields[1], "profile": False}
                    state["requests"].append((self.label, request.copy()))
                    response = {
                        "id": request["id"], "stable": True,
                        "total_ns": [100.],
                        "lanes": [{"status": "success", "moments": [[[0., 0.] for _ in range(4)]]}],
                    }
                    if self.label == "rust":
                        response.update(
                            precision="binary64", degrees=[0], preparation_ns=1.,
                            plan_reused=False, master_backend="test-backend", execution={},
                            profiled=request.get("profile", False),
                            profile_ns={name: [10.] for name in ["arguments", "masters", "reduction", "total"]}
                            if request.get("profile") else None,
                        )
                    else:
                        response["clock_ticks_per_second"] = 1_000_000_000
                    if transform:
                        transform(response, request, self.label)
                    return response

                def close(self):
                    state["closed"] = True

            argv = [
                "run.py", "--rust", str(rust), "--reference", str(reference),
                "--rust-build-manifest", str(rust_manifest),
                "--reference-build-manifest", str(reference_manifest),
                "--input", str(inputs), "--output", str(output),
                "--batches", "1", "--repeats", "3", "--warmup", "0",
                "--block-ms", "0.001", "--timeout", "1", "--cpu", "10",
            ]
            exception = None
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.object(sys, "argv", argv))
                stack.enter_context(patch.object(kernel, "Process", FakeProcess))
                stack.enter_context(patch.object(kernel, "source_hashes", side_effect=hashes))
                stack.enter_context(patch.object(kernel, "environment", return_value={"source_sha256": live_hashes}))
                stack.enter_context(patch.object(kernel.os, "sched_getaffinity", return_value={10, 11}))
                stack.enter_context(patch.object(kernel.os, "sched_setaffinity"))
                stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                try:
                    kernel.main()
                except Exception as error:
                    exception = error
            self.assertTrue(output.is_file(), "requested workloads must have a persisted ledger")
            data = json.loads(output.read_text())
            self.assertNotEqual(data["status"], "running", repr(exception))
            self.assertIn("counts", data, repr(exception))
            self.assertEqual(sum(data["counts"].values()), 1)
            self.assertEqual(len(data["rows"]), 1)
            return data, state, exception

    def assert_rejected(self, data):
        row = data["rows"][0]
        self.assertIn(row["status"], {"failed", "correctness-failed"}, row)
        if row.get("ratio") is not None:
            self.assertEqual(row["ratio"]["gate"], "correctness-failed")

    def test_valid_control_uses_selected_manifests(self):
        data, state, error = self.fixture()
        self.assertIsNone(error)
        self.assertEqual(data["status"], "complete")
        self.assertEqual(data["rows"][0]["status"], "measured")
        self.assertTrue(data["provenance_qualified"])
        self.assertTrue(data["build_manifest_paths"]["rust"].endswith("chosen-rust-build.json"))
        self.assertTrue(data["build_manifest_paths"]["reference"].endswith("chosen-reference-build.json"))
        self.assertEqual(state["spawned_hashes"]["rust"], data["binaries"]["rust"]["sha256"])

    def test_replaced_binary_cannot_qualify_unrecorded_executed_bytes(self):
        data, state, _ = self.fixture(replace_binary=True)
        if data.get("provenance_qualified"):
            # Copying the verified bytes before the competing rebuild is valid;
            # merely hashing the original path before Popen is insufficient.
            self.assertEqual(state["spawned_hashes"]["rust"], data["binaries"]["rust"]["sha256"])
        else:
            self.assertFalse(data["provenance_qualified"])

    def test_final_hash_failure_still_saves_finalized_unqualified_ledger(self):
        data, _, _ = self.fixture(fail_final_hash=True)
        self.assertFalse(data["provenance_qualified"])
        self.assertEqual(data["rows"][0]["status"], "measured")
        self.assertEqual(data["counts"], {"measured": 1})

    def test_total_timings_require_one_positive_finite_numeric_value(self):
        for label in ["rust", "reference"]:
            for value in [[-1.], [0.], [float("nan")], [float("inf")], [], [1., 2.], [None], [True]]:
                with self.subTest(engine=label, value=value):
                    def mutate(response, _request, engine):
                        if engine == label:
                            response["total_ns"] = copy.deepcopy(value)
                    data, _, _ = self.fixture(mutate)
                    self.assert_rejected(data)

    def test_response_id_must_match_requested_configuration(self):
        for label in ["rust", "reference"]:
            with self.subTest(engine=label):
                def mutate(response, _request, engine):
                    if engine == label:
                        response["id"] = "unrelated-case"
                data, _, _ = self.fixture(mutate)
                self.assert_rejected(data)

    def test_stability_flag_must_be_a_boolean(self):
        for label in ["rust", "reference"]:
            for value in ["false", 1, {"reason": "failed"}, [], None]:
                with self.subTest(engine=label, value=value):
                    def mutate(response, _request, engine):
                        if engine == label:
                            response["stable"] = copy.deepcopy(value)
                    data, _, _ = self.fixture(mutate)
                    self.assert_rejected(data)

    def test_profile_failure_and_last_complex_shape_are_checked(self):
        for failure in ["unstable", "last-complex-shape", "wrong-profile-flag"]:
            with self.subTest(failure=failure):
                def mutate(response, request, engine):
                    if engine != "rust" or not request.get("profile"):
                        return
                    if failure == "unstable":
                        response["stable"] = False
                        response["lanes"][0]["status"] = "unstable"
                    elif failure == "last-complex-shape":
                        response["lanes"][-1]["moments"][-1][-1] = [0., 0., 17.]
                    else:
                        response["profiled"] = False
                data, state, _ = self.fixture(mutate)
                self.assertTrue(any(request.get("profile") for _, request in state["requests"]))
                self.assert_rejected(data)

    def test_profile_components_require_one_nonnegative_finite_value(self):
        for value in [[-1.], [float("nan")], [float("inf")], [], [1., 2.], [None], [True]]:
            with self.subTest(value=value):
                def mutate(response, request, engine):
                    if engine == "rust" and request.get("profile"):
                        response["profile_ns"]["masters"] = copy.deepcopy(value)
                data, _, _ = self.fixture(mutate)
                self.assert_rejected(data)

    def test_zero_profile_component_is_valid(self):
        def mutate(response, request, engine):
            if engine == "rust" and request.get("profile"):
                response["profile_ns"]["arguments"] = [0.]
        data, _, error = self.fixture(mutate)
        self.assertIsNone(error)
        self.assertEqual(data["rows"][0]["status"], "measured")


if __name__ == "__main__":
    unittest.main()
