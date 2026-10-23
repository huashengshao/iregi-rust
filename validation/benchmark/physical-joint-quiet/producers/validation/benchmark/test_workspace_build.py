"""Build provenance regressions; the tiny Cargo probe has no external dependencies."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
import build_workspace as builder


class WorkspaceBuildTests(unittest.TestCase):
    def setUp(self):
        temporary_root = Path.cwd() / "target/workspace-builder-tests"
        temporary_root.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=temporary_root)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def artifact(self, name, kind, *, features=(), executable=None, opt="3"):
        return {"reason": "compiler-artifact", "target": {"name": name, "kind": [kind]},
                "executable": executable, "profile": {"opt_level": opt},
                "features": list(features), "filenames": []}

    def events(self, *, native=False):
        return [self.artifact(name, "example", executable=str(self.root / name))
                for name in sorted(builder.EXAMPLES)] + [
            self.artifact("iregi_masters", "lib", features=["native-batch"] if native else []),
            {"reason": "build-finished", "success": True}]

    def parse(self, events, native=False):
        path = self.root / "cargo.jsonl"
        path.write_text("".join(json.dumps(event) + "\n" for event in events))
        return builder.inspect_artifacts(path, native)

    def test_missing_binary_wrong_backend_and_unoptimized_artifacts_are_rejected(self):
        examples, _ = self.parse(self.events())
        self.assertEqual(set(examples), builder.EXAMPLES)
        with self.assertRaisesRegex(ValueError, "both requested"):
            self.parse(self.events()[1:])
        with self.assertRaisesRegex(ValueError, "features"):
            self.parse(self.events(native=True))
        events = self.events()
        events[0]["profile"]["opt_level"] = "2"
        with self.assertRaisesRegex(ValueError, "optimized"):
            self.parse(events)

    def test_verbose_build_script_output_does_not_hide_or_replace_cargo_evidence(self):
        path = self.root / "cargo.jsonl"
        records = [json.dumps(event) for event in self.events()]
        records.insert(1, "[radium 0.7.0] cargo:rustc-cfg=radium_atomic_8")
        path.write_text("\n".join(records) + "\n")
        examples, _ = builder.inspect_artifacts(path, False)
        self.assertEqual(set(examples), builder.EXAMPLES)
        path.write_text("[package 1.0.0] build-finished success=true\n")
        with self.assertRaisesRegex(ValueError, "both requested"):
            builder.inspect_artifacts(path, False)
        path.write_text("arbitrary text\n")
        with self.assertRaisesRegex(ValueError, "unrecognized text"):
            builder.inspect_artifacts(path, False)
        path.write_text("{malformed Cargo JSON}\n")
        with self.assertRaises(json.JSONDecodeError):
            builder.inspect_artifacts(path, False)

    def test_source_mutation_or_failed_build_cannot_publish_over_prior_success(self):
        standard = self.root / "target/benchmark/rust-build.json"
        standard.parent.mkdir(parents=True)
        standard.write_text("prior successful build\n")
        with self.assertRaisesRegex(ValueError, "changed"):
            builder.require_unchanged({"source_sha256_before": {"lib.rs": "before"},
                                       "source_sha256": {"lib.rs": "after"}})
        with self.assertRaisesRegex(ValueError, "incomplete"):
            builder.publish(self.root, self.root, {"status": "failed", "provenance_qualified": False})
        self.assertEqual(standard.read_text(), "prior successful build\n")

    def test_compatible_manifest_carries_verified_cargo_exit_status(self):
        data = {key: None for key in [
            "status", "started_at", "finished_at", "command", "requested_revision",
            "source_revision", "source_root", "master_backend", "backend_qualification",
            "environment", "profile", "rustc", "cargo", "source_sha256", "assets_sha256",
            "provenance_qualified", "manifest_path"]}
        data["binaries"] = {"physical_benchmark": {"path": "binary", "sha256": "digest"}}
        for completion in [{}, {"returncode": 7}, {"returncode": False}]:
            data["resources"] = completion
            with self.assertRaisesRegex(ValueError, "successful Cargo completion"):
                builder.compatibility_manifest(data, "physical_benchmark")
        data["resources"] = {"returncode": 0}
        self.assertEqual(builder.compatibility_manifest(data, "physical_benchmark")["returncode"], 0)

    def test_reference_binary_and_driver_are_both_matched(self):
        output = self.root / "target/benchmark"
        output.mkdir(parents=True)
        binary = output / "iregi-benchmark"
        binary.write_bytes(b"reference")
        driver = self.root / "validation/benchmark/driver.f90"
        driver.parent.mkdir(parents=True)
        driver.write_text("driver")
        builder.save(output / "reference-build.json", {
            "binary_sha256": builder.digest(binary), "driver_sha256": builder.digest(driver)})
        builder.reference_manifest(self.root, self.root)
        driver.write_text("changed driver")
        with self.assertRaisesRegex(ValueError, "driver"):
            builder.reference_manifest(self.root, self.root)
        binary.write_bytes(b"replacement")
        with self.assertRaisesRegex(ValueError, "binary"):
            builder.reference_manifest(self.root, self.root)

    def test_retained_builder_is_independent_and_tamper_checked(self):
        output = self.root / "attempt"
        frozen = builder.freeze_builder(output)
        evidence = builder.verify_builder(output)
        self.assertEqual(len(evidence["files"]), 3)
        self.assertEqual(builder.digest(frozen), builder.digest(Path(builder.__file__)))
        self.assertNotEqual(evidence["files"][0]["original_path"], str(frozen))
        frozen.write_text("changed")
        with self.assertRaisesRegex(ValueError, "builder source changed"):
            builder.verify_builder(output)

    def test_snapshot_rejects_extra_untracked_build_inputs(self):
        (self.root / "Cargo.toml").write_text("tracked")
        with patch.object(subprocess, "check_output", return_value=b"Cargo.toml\0"):
            builder.verify_snapshot_tree(self.root, "revision")
            (self.root / "build.rs").write_text("untracked")
            with self.assertRaisesRegex(ValueError, "inventory"):
                builder.verify_snapshot_tree(self.root, "revision")

    def test_profile_flags_cannot_override_required_settings(self):
        for key, value in [("RUSTFLAGS", "-Clto=fat"),
                           ("CARGO_ENCODED_RUSTFLAGS", "-C\x1fopt-level=0")]:
            with self.subTest(key=key), patch.dict(os.environ, {key: value}):
                with self.assertRaisesRegex(ValueError, "release profile"):
                    builder.build_environment(self.root)

    def test_failed_process_keeps_own_exit_code_and_resource_record(self):
        result = builder.run_build([sys.executable, "-c", "print('build failed');raise SystemExit(7)"],
                                   os.environ.copy(), self.root)
        self.assertEqual(result["returncode"], 7)
        self.assertGreaterEqual(result["max_rss_kib"], 0)
        self.assertIn("build failed", (self.root / "cargo.jsonl").read_text())

    @unittest.skipUnless(shutil.which("cargo"), "Cargo unavailable for dependency-free selection probe")
    def test_named_examples_keep_workspace_feature_union_without_building_other_examples(self):
        (self.root / "Cargo.toml").write_text(
            '[workspace]\nmembers=["a","b","c","shared"]\nresolver="3"\n')
        for name in ["a", "b", "c", "shared"]:
            crate = self.root / name
            (crate / "src").mkdir(parents=True)
            manifest = f'[package]\nname="{name}"\nversion="0.0.0"\nedition="2024"\n'
            if name == "shared":
                manifest += '[features]\na=[]\nb=[]\nc=[]\n'
            else:
                manifest += f'[dependencies]\nshared={{path="../shared",features=["{name}"]}}\n'
            (crate / "Cargo.toml").write_text(manifest)
            (crate / "src/lib.rs").write_text("")
            if name in {"a", "b"}:
                (crate / "examples").mkdir()
                example = "kernel_benchmark" if name == "a" else "physical_benchmark"
                (crate / f"examples/{example}.rs").write_text("fn main() {}\n")
                (crate / "examples/not_requested.rs").write_text('compile_error!("unselected");\n')
        command = builder.build_command(self.root, 2, str(min(os.sched_getaffinity(0))), False)
        # This new toy workspace needs its own generated lockfile, not the project lock.
        command.remove("--locked")
        env = os.environ.copy()
        env.update(CARGO_TARGET_DIR=str(self.root / "target"),
                   CARGO_BUILD_BUILD_DIR=str(self.root / "build"))
        completed = subprocess.run(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, timeout=60)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        artifacts = [json.loads(line) for line in completed.stdout.splitlines()
                     if json.loads(line).get("reason") == "compiler-artifact"]
        names = {event["target"]["name"] for event in artifacts if "example" in event["target"]["kind"]}
        self.assertEqual(names, builder.EXAMPLES)
        shared = [event for event in artifacts if event["target"]["name"] == "shared"]
        self.assertEqual(len(shared), 1)
        self.assertEqual(set(shared[0]["features"]), {"a", "b", "c"})


if __name__ == "__main__":
    unittest.main()
