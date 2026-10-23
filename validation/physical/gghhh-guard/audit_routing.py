#!/usr/bin/env python3
"""Read retained inputs; evaluate existing numeric expressions with Fraction.

No symbolic manipulation, engine execution, or project source modification.
"""
import copy
import datetime
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

ROOT = Path.cwd()
OUT = ROOT / "target/physical-gghhh-guard"
REVISION = "80949dbc4711947971a702643f75d639ef217e82"
FROZEN = ROOT / "target/benchmark/sources" / REVISION
RUN = ROOT / "target/benchmark/physical-joint/80949db-quiet-physical-002/gghhh"
PROMOTED = OUT / "float256-from-binary64"


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(value):
    return dict(numerator=str(value.numerator), denominator=str(value.denominator),
                fraction=str(value), decimal_70_significant_digits=format(value, ".70g"))


def binary64(text):
    return Fraction(*float(text).as_integer_ratio())


def at(value, path):
    for key in path:
        value = value[key]
    return value


def assign(value, path, number):
    for key in path[:-1]:
        value = value[key]
    value[path[-1]] = number


def square(vector):
    # Evaluate the existing (+---) numeric expression without changing it.
    return vector[0] ** 2 - vector[1] ** 2 - vector[2] ** 2 - vector[3] ** 2


paths = {
    "audit_script": Path(__file__).resolve(),
    "failed_rust_run": RUN / "rust.json",
    "frozen_requests": RUN / "rust-inputs.json",
    "canonical_reference_records": RUN / "gghhh-f64-hybrid-batch1/reference-records.json",
    "physical_fixture_input": ROOT / "validation/physical/gghhh-cli-input.json",
    "captured_madloop_fixture": ROOT / "validation/physical/madloop/fixtures/gghhh-helicity-1.json",
    "promoted_request": PROMOTED / "request.json",
    "conversion_ledger": PROMOTED / "input-conversions.json",
    "promoted_request_512": OUT / "float512-from-binary64/request.json",
    "conversion_ledger_512": OUT / "float512-from-binary64/input-conversions.json",
    "frozen_benchmark_source": FROZEN / "crates/iregi-cli/examples/physical_benchmark.rs",
    "frozen_cli_input_source": FROZEN / "crates/iregi-cli/src/input.rs",
    "frozen_plan_source": FROZEN / "crates/iregi-rust/src/plan.rs",
    "frozen_execution_source": FROZEN / "crates/iregi-rust/src/execution.rs",
    "frozen_argument_guard_source": FROZEN / "crates/iregi-rust/src/stability/arguments.rs",
    "frozen_fixture_generation_source": FROZEN / "crates/iregi-prepare/tests/madloop_numerator.rs",
    "frozen_model": FROZEN / "fixtures/models/sm.json",
    "frozen_dot": FROZEN / "examples/graphs/gghhh_top_pentagon.dot",
}
before = {name: digest(path) for name, path in paths.items()}
requests = read(paths["frozen_requests"])
configuration = requests[0]["configuration"]
sample = configuration["input"]["samples"][0]
assert configuration["precision"] == "f64" and configuration["accuracy_bits"] == 53
assert sample == read(paths["physical_fixture_input"])
assert all(row["case"] == "gghhh" and
           all(lane == sample for lane in row["configuration"]["input"]["samples"])
           for row in requests)
promoted = read(paths["promoted_request"])
assert promoted["op"] == "prepare"
prepared = promoted["configuration"]
assert prepared["precision"] == "float" and prepared["bits"] == 256 and prepared["accuracy_bits"] == 53
assert prepared["algorithm"] == configuration["algorithm"] == "Hybrid"
assert prepared["component"] == configuration["component"] == [0, 0]
assert len(prepared["input"]["samples"]) == 1
promoted_sample = prepared["input"]["samples"][0]
for field in ("model", "dot"):
    assert prepared[field] == configuration[field] == paths[f"frozen_{field}"].read_text()

numeric_paths = [("mu",)]
numeric_paths += [("parameters", name, component) for name, value in sample["parameters"].items()
                 for component in range(len(value))]
numeric_paths += [("propagators", index, field, component)
                 for index, propagator in enumerate(sample["propagators"])
                 for field in ("shift", "mass_squared") for component in range(len(propagator[field]))]
conversions = read(paths["conversion_ledger"])
by_path = {tuple(row["path"]): row for row in conversions}
assert len(by_path) == len(conversions) == len(numeric_paths)
assert set(by_path) == set(numeric_paths)
expected_sample = copy.deepcopy(sample)
conversion_checks = []
zero_count = negative_zero_count = 0
for path in numeric_paths:
    original, actual = at(sample, path), at(promoted_sample, path)
    row = by_path[path]
    assert row["original"] == original and row["exact_binary64"] == actual
    value = float(original)
    assert math.isfinite(value)
    expected_fraction = Fraction(*value.as_integer_ratio())
    assert Fraction(actual) == expected_fraction
    negative_zero = value == 0 and math.copysign(1.0, value) < 0
    if value == 0:
        zero_count += 1
        negative_zero_count += int(negative_zero)
        assert actual.strip().startswith("-") == negative_zero
    assign(expected_sample, path, actual)
    conversion_checks.append(dict(path=list(path), original=original, promoted=actual,
                                  binary64_hex=value.hex(), binary64_bits=struct.pack(">d", value).hex(),
                                  exact_fraction=str(expected_fraction), negative_zero=negative_zero, passed=True))
assert promoted_sample == expected_sample
request_checks = []
for bits, request_key, ledger_key in [(256, "promoted_request", "conversion_ledger"),
                                     (512, "promoted_request_512", "conversion_ledger_512")]:
    request = read(paths[request_key])
    config = request["configuration"]
    assert request["op"] == "prepare" and config["precision"] == "float"
    assert config["bits"] == bits and config["accuracy_bits"] == 53
    assert config["algorithm"] == configuration["algorithm"] == "Hybrid"
    assert config["component"] == configuration["component"] == [0, 0]
    assert len(config["input"]["samples"]) == 1
    assert config["input"]["samples"][0] == expected_sample
    assert read(paths[ledger_key]) == conversions
    for field in ("model", "dot"):
        assert config[field] == configuration[field] == paths[f"frozen_{field}"].read_text()
    for path in numeric_paths:
        original = float(at(sample, path))
        actual = at(config["input"]["samples"][0], path)
        assert Fraction(actual) == Fraction(*original.as_integer_ratio())
        if original == 0:
            assert actual.strip().startswith("-") == (math.copysign(1.0, original) < 0)
    request_checks.append(dict(working_bits=bits, accuracy_bits=53, request_provenance_key=request_key,
                               conversion_ledger_provenance_key=ledger_key, id=config["id"],
                               numeric_components_checked=len(numeric_paths), zero_components_checked=zero_count,
                               negative_zero_components_preserved=negative_zero_count,
                               sample_matches_exact_binary64_conversions=True,
                               model_and_dot_identical_to_captured_and_frozen_inputs=True, passed=True))

fixture = read(paths["captured_madloop_fixture"])
external_decimal = [[Fraction(value) for value in vector] for vector in fixture["metadata"]["evaluated_external_momenta"]]
external_binary = [[binary64(value) for value in vector] for vector in fixture["metadata"]["evaluated_external_momenta"]]
selected = next(row for row in fixture["records"] if row["group"] == fixture["selected_feynkit_group"])
reference_shifts = [[binary64(value) for value in vector] for vector in selected["shifts"]]
coordinates = sample["propagators"][1]["shift"]
assert sample["propagators"][0]["edge_id"] == 0 and sample["propagators"][1]["edge_id"] == 1
assert all(Fraction(value) == 0 for value in sample["propagators"][0]["shift"])
decimal_vector = list(map(Fraction, coordinates))
binary_vector = list(map(binary64, coordinates))
decimal_distance, binary_distance = square(decimal_vector), square(binary_vector)
envelope = sum(value ** 2 for value in binary_vector)
unit, target = Fraction(1, 2 ** 52), Fraction(1, 2 ** 34)
ulp = binary64(str(math.ulp(float(coordinates[0]))))
assert ulp == Fraction(1, 2 ** 44)
assert abs(binary_vector[0] + binary_vector[3]) == ulp
assert square(external_binary[1]) == 0

def conservation(vectors):
    return [vectors[0][axis] + vectors[1][axis] - vectors[2][axis]
            - vectors[3][axis] - vectors[4][axis] for axis in range(4)]

canonical = read(paths["canonical_reference_records"])
for row in canonical:
    assert row["input"]["propagators"] == sample["propagators"]
    assert row["input"]["mu"] == sample["mu"] and row["input"]["snap"] is False

result = {
    "schema_version": 1, "status": "passed", "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "scope": "Exact read-only numeric routing and binary64-input promotion audit; no engine execution, symbolic manipulation or final-amplitude qualification",
    "python": sys.version, "frozen_source_revision": REVISION,
    "provenance": {name: {"path": str(path.relative_to(ROOT)), "sha256": before[name]} for name, path in paths.items()},
    "source_locations": {
        "distance_pair_order": {"source": "frozen_execution_source", "line": 650, "description": "Lexicographic i<j raw-distance list: constraint 0 is propagators (0,1)"},
        "distance_expression": {"source": "frozen_plan_source", "line": 988, "description": "Existing squared_difference uses metric (+---)"},
        "preserved_input_pack": {"source": "frozen_benchmark_source", "line": 155, "description": "Packs supplied shifts; no benchmark reconstruction or snapping"},
        "decimal_parse": {"source": "frozen_cli_input_source", "line": 139, "description": "Symbolica parses at prototype precision then converts exact rational to destination type"},
        "fixture_generation": {"source": "frozen_fixture_generation_source", "line": 197, "description": "FeynKit external-coefficient expression evaluated with Complex<f64> bindings, then formatted with {:.17e} at line 199"},
        "relative_argument_guard": {"source": "frozen_argument_guard_source", "line": 92, "description": "Target 2^(19-accuracy_bits); positive-envelope roundoff multiplied by at least 8 operations for a scalar component"},
    },
    "selected_distance": {
        "index": 0, "propagator_positions": [0, 1], "edge_ids": [0, 1], "metric": "+---",
        "expression": "(shift[0]-shift[1])^2; shift[0]=0", "shift1_original_strings": coordinates,
        "working_precision_bits": 53, "effective_input_precision_bits": 53, "requested_accuracy_bits": 53,
        "decimal_string_exact": exact(decimal_distance), "binary64_input_exact": exact(binary_distance),
        "binary64_coordinates": [{"original": value, "hex": float(value).hex(), "exact": exact(binary64(value))} for value in coordinates],
        "energy_plus_z_decimal": exact(decimal_vector[0] + decimal_vector[3]),
        "energy_plus_z_binary64": exact(binary_vector[0] + binary_vector[3]),
        "energy_ulp": exact(ulp), "absolute_energy_vs_abs_z_ulp_difference": 1,
        "positive_envelope_at_shift0_zero": exact(envelope),
        "envelope_over_absolute_distance": exact(envelope / abs(binary_distance)),
        "guard_relative_target": exact(target), "guard_roundoff_unit": exact(unit),
        "minimum_guard_estimate_uses_count": 8,
        "minimum_guard_estimate_over_target": exact(unit * 8 * envelope / (target * abs(binary_distance))),
        "actual_compiled_operation_count": None,
        "minimum_estimate_note": "A source-derived lower bound suffices to explain rejection. No compiled evaluator/intermediate or exact operation count was observed.",
        "absolute_distance_over_top_mass_squared": exact(abs(binary_distance) / Fraction(sample["propagators"][1]["mass_squared"][0])),
        "absolute_distance_over_mu_squared": exact(abs(binary_distance) / Fraction(sample["mu"]) ** 2),
    },
    "routing": {
        "captured_external_p2_strings": fixture["metadata"]["evaluated_external_momenta"][1],
        "captured_p2_binary64_squared": exact(square(external_binary[1])),
        "canonical_shift1_minus_captured_p2_binary64": [exact(a-b) for a,b in zip(binary_vector, external_binary[1])],
        "external_conservation_decimal": [exact(value) for value in conservation(external_decimal)],
        "external_conservation_binary64": [exact(value) for value in conservation(external_binary)],
        "existing_routing_numeric_sum_p3_p4_p5_minus_p1_binary64": [exact(external_binary[2][axis] + external_binary[3][axis] + external_binary[4][axis] - external_binary[0][axis]) for axis in range(4)],
        "selected_madloop_group": fixture["selected_feynkit_group"],
        "declared_routing_relation": fixture["feynkit_routing_relation"],
        "madloop_first_incoming_distance_binary64": exact(square([a-b for a,b in zip(reference_shifts[0], reference_shifts[1])])),
        "madloop_second_incoming_distance_binary64": exact(square([a-b for a,b in zip(reference_shifts[1], reference_shifts[2])])),
        "canonical_reference_input_identity_passed": True,
        "canonical_reference_recorded_stability": [{"mode": row["mode"], "returncode": row.get("returncode"), "stable": row["results"][0]["stable"]} for row in canonical],
    },
    "promoted_request_audit": {
        "passed": True, "numeric_components_checked": len(numeric_paths), "zero_components_checked": zero_count,
        "negative_zero_components_preserved": negative_zero_count,
        "conversion_paths_complete_unique": True, "non_numeric_sample_fields_unchanged": True,
        "model_and_dot_identical_to_captured_and_frozen_inputs": True,
        "algorithm_and_color_components_unchanged": True, "working_bits_checked": [256, 512], "accuracy_bits": 53,
        "requests": request_checks,
        "selected_distance_exact_after_promotion": exact(binary_distance),
        "qualification": "Every promoted numeric component equals float(original).as_integer_ratio(); signed zeros are separately checked. This validates the request, not its numerical result.",
        "components": conversion_checks,
    },
    "interpretation": [
        "The nonzero canonical invariant is poorly conditioned relatively; the current guard is expected to reject it at input/working precision 53.",
        "The captured incoming gluon is null, but the stored canonical routing contains a one-ULP longitudinal discrepancy produced during earlier binary64 fixture preparation.",
        "The guard is conservative for final observables: its rejection does not establish failure of the massive graph integral or the 1e-10 dimensionally normalized comparison.",
        "Preserved canonical IREGI inputs are identical and its recorded stable flags do not certify relative accuracy of this tiny invariant.",
        "The promoted request preserves the exact binary64 canonical inputs, including their nonzero invariant; it does not substitute the original decimal-string values or snap the invariant to zero.",
    ],
}
after = {name: digest(path) for name, path in paths.items()}
assert before == after, "audited source/input changed during audit"
result["audited_files_unchanged"] = True
output = OUT / "routing-audit.json"
output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
print(json.dumps({"path": str(output), "sha256": digest(output), "numeric_components_checked": len(numeric_paths),
                  "negative_zero_components_preserved": negative_zero_count, "status": result["status"]}, indent=2))
