"""Immutable compiled inputs and evolving validation producers stay distinct."""
import copy
import unittest

import physical_run as benchmark


class BuildInputTests(unittest.TestCase):
    def setUp(self):
        self.sources = {"crates/iregi-cli/examples/physical_benchmark.rs":"rust",
                        "validation/benchmark/physical_run.py":"old-runner"}
        self.assets = {"fixtures/models/sm.json":"model", "examples/graphs/ggh.dot":"graph",
                       "validation/physical/ggh-cli-input.json":"point",
                       "validation/physical/madloop/fixtures/ggh.json":"fixture",
                       "validation/physical/canonical-reference-audit.json":"audit",
                       "validation/physical/madloop/benchmark.py":"old-reference-producer"}
        self.build = dict(status="complete",provenance_qualified=True,binary_sha256="binary",
                          source_sha256=self.sources,assets_sha256=self.assets)

    def checks(self, sources=None, built=None, live=None):
        return benchmark.build_provenance_checks(self.build,"binary",sources or self.sources,
                                                 built or self.assets,live or self.assets)

    def test_producer_only_update_is_allowed_and_independently_recorded(self):
        live = dict(self.assets, **{"validation/physical/madloop/benchmark.py":"new-reference-producer"})
        current = dict(self.sources, **{"validation/benchmark/physical_run.py":"new-runner"})
        self.assertTrue(all(self.checks(live=live).values()))
        recorded = benchmark.validation_producer_hashes(current,live)
        self.assertEqual(recorded, {"validation/physical/madloop/benchmark.py":"new-reference-producer",
                                    "validation/benchmark/physical_run.py":"new-runner"})
        self.assertEqual(self.build["assets_sha256"],self.assets)
        self.assertNotEqual(recorded,benchmark.validation_producer_hashes(self.sources,self.assets))

    def test_compiled_code_or_any_frozen_asset_change_is_rejected(self):
        changed = dict(self.sources, **{"crates/iregi-cli/examples/physical_benchmark.rs":"modified"})
        self.assertFalse(self.checks(sources=changed)["sources_match_manifest"])
        for name in self.assets:
            changed = dict(self.assets, **{name:"modified"})
            self.assertFalse(self.checks(built=changed)["assets_match_manifest"])

    def test_model_graph_input_fixture_and_audit_changes_are_rejected(self):
        for name in benchmark.numeric_asset_hashes(self.assets):
            with self.subTest(name=name):
                changed = dict(self.assets, **{name:"modified"})
                self.assertFalse(self.checks(live=changed)["numeric_assets_match_build"])

    def test_new_or_removed_numerical_assets_are_rejected(self):
        changed = dict(self.assets, **{"validation/physical/new.json":"new"})
        self.assertFalse(self.checks(live=changed)["numeric_assets_match_build"])
        del changed["validation/physical/new.json"]
        del changed["fixtures/models/sm.json"]
        self.assertFalse(self.checks(live=changed)["numeric_assets_match_build"])

    def test_live_producer_change_during_run_still_fails(self):
        data = dict(build_provenance_checks=self.checks(), source_changed_during_run=False,
                    workspace_source_changed_during_run=False,assets_changed_during_run=False,
                    binaries_changed_during_run=False,validation_producers_changed_during_run=False,
                    build_assets_changed_during_run=False)
        self.assertTrue(benchmark.provenance_qualified(data))
        for name in ["validation_producers_changed_during_run","build_assets_changed_during_run"]:
            modified = copy.deepcopy(data)
            modified[name] = True
            self.assertFalse(benchmark.provenance_qualified(modified))


if __name__ == "__main__":
    unittest.main()
