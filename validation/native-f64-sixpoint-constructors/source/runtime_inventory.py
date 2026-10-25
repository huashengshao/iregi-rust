"""Exact 27-test source inventory; importing it executes no test binary."""
GROUPS = {"ordinary": {"count": 20, "aggregate_seconds": 180, "per_test_seconds": 60},
          "constructors": {"count": 7, "aggregate_seconds": 300, "per_test_seconds": 120}}
SIDECARS = [
    "workspace_policy_default_preserves_values_without_sidecar_allocation",
    "workspace_policy_isolates_retry_while_sharing_exact_arithmetic_cache",
    "workspace_policy_survives_dual_specialization_eager_and_lazy_children",
    "workspace_policy_certificate_totals_reset_before_empty_and_invalid_calls",
    "workspace_policy_counts_nested_analytic_work_without_changing_ordinary_counts",
]

def cases():
    result = []
    for configuration in ("default", "selective"):
        def add(group, module, filename, names):
            result.extend({"group": group, "configuration": configuration, "name": module + "::" + name,
                           "source": "crates/iregi-rust/src/" + filename} for name in names)
        names = ["explicit_symbolica_overrides_the_legacy_feature_and_preserves_default_cache"]
        names += (["unavailable_selective_policy_fails_before_exact_preparation"] if configuration == "default" else
                  ["selective_workspaces_keep_cache_policy_and_recursive_lane_semantics",
                   "selective_policy_keeps_high_precision_and_component_one_duals_on_symbolica"])
        add("ordinary", "execution::master_policy_tests", "master_policy_tests.rs", names)
        add("ordinary", "execution::tests", "execution/policy_tests.rs", SIDECARS)
        names = ["composition_sidecars_share_exact_cache_but_master_policies_do_not",
                 "composition_ordered_dual_shapes_and_master_policy_separate_exact_entries"]
        if configuration == "selective":
            names.append("composition_selected_policy_survives_eager_dual_and_lazy_children")
        add("ordinary", "execution::policy_composition_tests", "execution/policy_composition_tests.rs", names)
        names = ["composition_masked_planar_chart_preserves_explicit_symbolica"]
        if configuration == "selective":
            names.append("composition_masked_planar_chart_preserves_selected_policy_for_both_shapes")
        add("constructors", "certified_planar::policy_composition_tests", "certified_planar/policy_composition_tests.rs", names)
        add("constructors", "execution::planar_fallback::policy_composition_tests", "execution/planar_fallback.rs",
            ["composition_planar_retry_forwards_policies_to_lazy_masked_charts"])
        add("constructors", "thin_n6::policy_composition_tests", "thin_n6/policy_composition_tests.rs",
            ["composition_six_point_constructors_pin_symbolica_with_no_backend_option"])
    assert len(result) == 27 and len({(case["configuration"], case["name"]) for case in result}) == 27
    for group, limits in GROUPS.items():
        assert sum(case["group"] == group for case in result) == limits["count"]
    return result

def tracked(name):
    return name.startswith(("execution::master_policy_tests::", "execution::policy_composition_tests::",
                            "execution::tests::workspace_policy_", "certified_planar::policy_composition_tests::",
                            "execution::planar_fallback::policy_composition_tests::", "thin_n6::policy_composition_tests::"))

def plan(stage, attempt, manifest):
    assert stage in GROUPS
    taskset = manifest["tools"]["taskset"]["path"]
    binaries = {configuration: attempt / (configuration + "-core-tests-frozen") for configuration in ("default", "selective")}
    listings = [{"configuration": configuration,
                 "command": [taskset, "-c", "22", str(binary), "--list", "--format", "terse"],
                 "timeout_seconds": 15} for configuration, binary in binaries.items()]
    selected = []
    for case in cases():
        if case["group"] != stage:
            continue
        configuration = case["configuration"]
        selected.append({**case, "binary": manifest["test_binaries"][configuration]["path"],
                         "command": [taskset, "-c", "22", str(binaries[configuration]), "--exact", case["name"], "--test-threads=1", "--nocapture"],
                         "timeout_seconds": GROUPS[stage]["per_test_seconds"]})
    return {"stage": stage, "limits": GROUPS[stage], "listings": listings, "cases": selected}
