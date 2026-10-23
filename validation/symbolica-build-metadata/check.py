#!/usr/bin/env python3
"""Compile only build.rs and check version/watch behavior in disposable repos."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import unittest


PARSER = argparse.ArgumentParser(description=__doc__)
PARSER.add_argument("--baseline", type=Path, required=True)
PARSER.add_argument("--candidate", type=Path, required=True)
PARSER.add_argument("--output", type=Path, required=True)
ARGS = PARSER.parse_args()
ROOT = Path.cwd()
OUT = ARGS.output.resolve()
if not OUT.is_relative_to(ROOT) or OUT.exists():
    raise SystemExit("Use a new output directory inside the current project")
OUT.mkdir(parents=True)
EVIDENCE = {"scope": "Standalone Rust build scripts; no Symbolica library or runtime", "cases": []}
ENV = os.environ.copy()
for key in tuple(ENV):
    if key.startswith("GIT_"):
        del ENV[key]
ENV.update(CARGO_PKG_VERSION="3.0.1", GIT_CONFIG_GLOBAL="/dev/null",
           GIT_CONFIG_NOSYSTEM="1", GIT_CEILING_DIRECTORIES=str(OUT))
BINARIES = {}
for name, source in [("baseline", ARGS.baseline), ("candidate", ARGS.candidate)]:
    source = source.resolve()
    binary = OUT / (name + "-build-script")
    command = ["rustc", "--edition=2024", "--crate-name", name + "_build", str(source), "-o", str(binary)]
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    BINARIES[name] = binary
    EVIDENCE[name] = {"source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                      "command": command, "stdout": result.stdout, "stderr": result.stderr,
                      "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest()}
EVIDENCE["rustc"] = subprocess.check_output(["rustc", "--version", "--verbose"], text=True)


def git(directory, *arguments):
    return subprocess.check_output(["git", "-C", str(directory), "-c", "core.hooksPath=/dev/null",
                                    "-c", "commit.gpgsign=false", "-c", "user.name=huashengshao",
                                    "-c", "user.email=erdissshaw@gmail.com", *arguments], env=ENV,
                                   text=True, stderr=subprocess.STDOUT).strip()


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.directory = OUT / self._testMethodName
        self.directory.mkdir()
        self.vendor = self.directory / "dependencies/symbolica"
        self.vendor.mkdir(parents=True)
        self.evidence = {"name": self._testMethodName, "runs": []}
        EVIDENCE["cases"].append(self.evidence)

    def initialize_git(self):
        git(self.directory, "init", "--quiet")
        return self.commit("initial")

    def commit(self, contents):
        (self.directory / "payload.txt").write_text(contents)
        git(self.directory, "add", "payload.txt")
        git(self.directory, "commit", "--quiet", "-m", contents)
        return git(self.directory, "rev-parse", "HEAD")

    def invoke(self, name="candidate", environment=None):
        result = subprocess.run([str(BINARIES[name])], cwd=self.vendor,
                                env=ENV if environment is None else environment,
                                text=True, capture_output=True, check=True)
        lines = result.stdout.splitlines()
        version = [line.split("=", 2)[2] for line in lines if line.startswith("cargo:rustc-env=SYMBOLICA_VERSION=")]
        watches = [line.split("=", 1)[1] for line in lines if line.startswith("cargo:rerun-if-changed=")]
        self.assertEqual(len(version), 1)
        self.assertEqual(len(watches), len(set(watches)))
        self.assertIn("IREGI_UPSTREAM_VERSION", watches)
        self.assertIn("build.rs", watches)
        run = {"variant": name, "version": version[0], "watches": watches,
               "stdout": result.stdout, "stderr": result.stderr}
        self.evidence["runs"].append(run)
        return run

    def assert_fallback(self, result):
        self.assertEqual(result["version"], "symbolica-" + git(self.vendor, "describe", "--tags", "--always"))
        expected = {"IREGI_UPSTREAM_VERSION", "build.rs"}
        for entry in ("HEAD", "refs", "packed-refs"):
            path = Path(git(self.vendor, "rev-parse", "--path-format=absolute", "--git-path", entry))
            if path.exists():
                expected.add(str(path))
        self.assertEqual(set(result["watches"]), expected)

    def test_explicit_version_ignores_embedding_commits(self):
        before_commit = self.initialize_git()
        (self.vendor / "IREGI_UPSTREAM_VERSION").write_text("  9cdc2949-iregi-scope-cache\n")
        baseline = self.invoke("baseline")
        before = self.invoke()
        self.assertGreater(len(baseline["watches"]), 2)
        self.assertEqual(before["version"], baseline["version"])
        self.assertEqual(before["version"], "symbolica-9cdc2949-iregi-scope-cache")
        self.assertEqual(set(before["watches"]), {"IREGI_UPSTREAM_VERSION", "build.rs"})
        after_commit = self.commit("unrelated embedding project edit")
        self.assertNotEqual(before_commit, after_commit)
        after = self.invoke()
        self.assertEqual(before["stdout"], after["stdout"])
        self.evidence.update(before_commit=before_commit, after_commit=after_commit)

    def test_version_file_change_is_observed(self):
        self.initialize_git()
        version_file = self.vendor / "IREGI_UPSTREAM_VERSION"
        version_file.write_text("first\n")
        first = self.invoke()
        version_file.write_text("second\n")
        second = self.invoke()
        self.assertEqual(first["version"], "symbolica-first")
        self.assertEqual(second["version"], "symbolica-second")
        self.assertEqual(first["watches"], second["watches"])
        version_file.unlink()
        self.assert_fallback(self.invoke())

    def test_missing_version_uses_changing_git_fallback(self):
        self.initialize_git()
        before = self.invoke()
        self.assert_fallback(before)
        baseline = self.invoke("baseline")
        self.assertEqual(before["version"], baseline["version"])
        self.assertEqual(set(before["watches"]), set(baseline["watches"]))
        self.commit("fallback version changes")
        after = self.invoke()
        self.assert_fallback(after)
        self.assertNotEqual(before["version"], after["version"])
        git(self.directory, "pack-refs", "--all")
        packed = self.invoke()
        self.assert_fallback(packed)
        self.assertTrue(any(path.endswith("/packed-refs") for path in packed["watches"]))

    def test_empty_and_invalid_version_use_git_fallback(self):
        self.initialize_git()
        for contents in (b"", b" \t\n", b"\xff"):
            (self.vendor / "IREGI_UPSTREAM_VERSION").write_bytes(contents)
            self.assert_fallback(self.invoke())

    def test_non_repository_uses_package_version(self):
        result = self.invoke()
        self.assertEqual(result["version"], "symbolica-3.0.1")
        self.assertEqual(set(result["watches"]), {"IREGI_UPSTREAM_VERSION", "build.rs"})

    def test_explicit_version_and_package_fallback_without_git(self):
        self.initialize_git()
        empty_path = OUT / "no-programs"
        empty_path.mkdir(exist_ok=True)
        environment = dict(ENV, PATH=str(empty_path))
        version_file = self.vendor / "IREGI_UPSTREAM_VERSION"
        version_file.write_text("9cdc2949-iregi-scope-cache\n")
        explicit = self.invoke(environment=environment)
        self.assertEqual(explicit["version"], "symbolica-9cdc2949-iregi-scope-cache")
        self.assertEqual(set(explicit["watches"]), {"IREGI_UPSTREAM_VERSION", "build.rs"})
        version_file.unlink()
        fallback = self.invoke(environment=environment)
        self.assertEqual(fallback["version"], "symbolica-3.0.1")
        self.assertEqual(set(fallback["watches"]), {"IREGI_UPSTREAM_VERSION", "build.rs"})


suite = unittest.defaultTestLoader.loadTestsFromTestCase(MetadataTests)
result = unittest.TextTestRunner(verbosity=2).run(suite)
EVIDENCE.update(status="passed" if result.wasSuccessful() else "failed", tests_run=result.testsRun,
                failures=[(str(test), message) for test, message in result.failures],
                errors=[(str(test), message) for test, message in result.errors])
(OUT / "results.json").write_text(json.dumps(EVIDENCE, indent=2) + "\n")
raise SystemExit(0 if result.wasSuccessful() else 1)
