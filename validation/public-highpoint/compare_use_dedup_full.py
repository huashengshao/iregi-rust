"""Bound full-candidate arrays to their captures and inspect original IREGI.

A single array establishes reference/pole agreement only. Optional --high uses
the existing two-precision convergence comparison on the same frozen build.
No executable is started by this script.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import argparse
import hashlib
import json

import compare_public as public


EXPECTED_REVISION = "6b24c0372022e22606a1ac85f30c7fa579fb41f0"
MODULE_COUNTS = {"stability::": 38, "execution::": 35}
REFERENCE_TOLERANCE = Decimal("1e-10")
NORMALIZATION = (
    "Q^2=max(1,abs(real mass_squared_i),abs((q_i-q_j)^2)); "
    "D=rank+4-2N; reference error=abs(value-reference)/max(Q^D,abs(reference)); "
    "zero-pole residue=abs(value)/Q^D; abs is the complex Euclidean norm"
)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def check_hashes(entries, root, label):
    require(isinstance(entries, dict) and bool(entries), f"Missing {label} hashes")
    for name, expected in entries.items():
        require(digest(root / name) == expected, f"Changed {label}: {name}")


def validate_provenance(record, result_path, fixture_path, root=None):
    root = Path.cwd() if root is None else Path(root).resolve()
    result_path, fixture_path = Path(result_path).resolve(), Path(fixture_path).resolve()
    here = root / "validation/public-highpoint"
    build_path = here / "use-dedup-full-build.json"
    run_path = result_path.with_name(result_path.stem + "-run.json")
    build, run = read(build_path), read(run_path)
    build_hash = digest(build_path)
    require(run.get("variant") == "use-dedup-full"
            and run.get("status") == "completed" and run.get("exit_code") == 0
            and run.get("last_public_stage") == "all_lanes_success"
            and run.get("numerical_reduction_entered") is True
            and run.get("result_sha256") == digest(result_path)
            and run.get("fixture_sha256") == digest(fixture_path)
            and run.get("build_manifest_sha256") == build_hash,
            "Incomplete, unsuccessful, or mismatched full-run provenance")
    require(build.get("status") == "passed" and build.get("exit_codes") == [0, 0, 0]
            and build.get("changed_inputs") == {} and build.get("sources_unchanged") is True
            and build.get("source_revision") == EXPECTED_REVISION,
            "Full build did not preserve the reviewed revision and frozen inputs")
    frozen = root / build["frozen_source_root"]
    check_hashes(build["frozen_source_hashes"], frozen, "frozen source")
    check_hashes(build["original_source_hashes"], frozen.parent / "original", "original source")
    check_hashes(build["protected_input_hashes"], root, "build input")
    check_hashes(build["dependency_hashes"], root, "build dependency")
    require(run.get("frozen_source_files_unchanged") == len(build["frozen_source_hashes"]),
            "Run did not verify every frozen source")
    require(build["instrumentation_patch_sha256"]
            == digest(here / "use-dedup-full-instrumentation.patch"),
            "Full instrumentation patch differs from the compiled build")
    binary = root / build["binary_path"]
    driver_name = "crates/iregi-rust/examples/highpoint_public.rs"
    require(run["binary_sha256"] == build["binary_sha256"] == digest(binary)
            and run["probe_source_sha256"] == build["frozen_source_hashes"][driver_name]
            and run["probe_source_sha256"] == digest(frozen / driver_name)
            and run["runner_source_sha256"] == digest(here / "run_use_dedup_full.py")
            and run["log_sha256"] == digest(result_path.with_suffix(".log")),
            "Executable, frozen driver, runner, or log differs from the capture")
    require(run.get("environment_additions") == {
                "IREGI_PV_PREPARATION_PROFILE": "1", "RAYON_NUM_THREADS": "1",
                "IREGI_PREPARATION_PROFILE": "1"}
            and run.get("environment_removals") == [
                "IREGI_ALIAS_USE_VERIFY", "IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE",
                "IREGI_MASTER_AMPLITUDE_MODE"],
            "Full-run environment does not match the reviewed capture")
    limit = run.get("timeout_seconds")
    require(type(limit) in [int, float] and 0 < limit <= 600,
            "Missing or unsupported public runtime bound")
    command = run["command"]
    require(len(command) == 12 and command[:2] == ["taskset", "-c"]
            and isinstance(command[2], str) and command[2].isdigit(), "Malformed CPU command")
    settings = record["settings"]
    algorithms = {"Ibp": "ibp", "PassarinoVeltman": "pv", "Hybrid": "hybrid"}
    expected = ["taskset", "-c", command[2], str(binary), str(fixture_path.relative_to(root)),
                str(settings["propagators"]), str(settings["rank"]), algorithms[settings["algorithm"]],
                str(record["working_bits"]), str(record["requested_bits"]), str(record["rows"]),
                str(result_path.relative_to(root))]
    require(command == expected and record["fixture"] == str(fixture_path.relative_to(root)),
            "Public command does not match output settings, precision, or input")

    semantic_path = here / "use-dedup-full-tests-run.json"
    qualification_path = here / "use-dedup-full-tests-qualification.json"
    semantic, qualification = read(semantic_path), read(qualification_path)
    require(run["semantic_qualification_sha256"] == digest(qualification_path)
            and semantic.get("status") == "passed" and semantic.get("changed_inputs") == {}
            and semantic.get("build_manifest_sha256") == build_hash
            and qualification.get("status") == "passed"
            and qualification.get("build_manifest_sha256") == build_hash
            and qualification.get("exact_complete_module_counts") == MODULE_COUNTS
            and qualification.get("total_passed") == 73,
            "Missing complete semantic qualification for the same frozen build")
    artifacts = qualification["artifacts"]
    for path in [build_path, semantic_path, here / "use-dedup-full-tests-list.txt",
                 here / "qualify_use_dedup_full_tests.py",
                 here / "use-dedup-full-tests-stability.log", here / "use-dedup-full-tests-execution.log"]:
        require(artifacts.get(str(path.relative_to(root))) == digest(path),
                "Semantic qualification is missing a bound artifact")
    check_hashes(artifacts, root, "semantic qualification artifact")
    check_hashes(semantic["protected_input_hashes"], root, "semantic run input")
    require(digest(root / build["test_binary_path"]) == build["test_binary_sha256"],
            "Semantic test executable changed")

    baseline_path = here / "build.json"
    baseline = read(baseline_path)
    matching = {}
    for name in ["iregi_masters", "symbolica", "oneloop"]:
        entries = [entry for entry in baseline["library_artifacts"]
                   if Path(entry["preserved_path"]).name.startswith("lib" + name + "-")]
        require(len(entries) == 1, "Missing unique baseline dependency")
        entry = entries[0]
        require(entry["sha256"] == build["dependency_hashes"].get(entry["preserved_path"])
                == digest(root / entry["preserved_path"]), "Baseline dependency mismatch")
        matching[name] = entry["sha256"]
    return {"run_manifest_sha256": digest(run_path), "build_manifest_sha256": build_hash,
            "binary_sha256": run["binary_sha256"], "source_revision": build["source_revision"],
            "semantic_qualification_sha256": digest(qualification_path),
            "baseline_manifest_sha256": digest(baseline_path),
            "matching_baseline_dependencies": matching, "variant": "use-dedup-full"}


def validate_reference_capture(reference, reference_path, fixture_path, fixture, root):
    public.validate_reference(reference, fixture, digest(fixture_path))
    executable = root / "target/reference/iregi-reference-original"
    require(reference.get("fixture") == str(fixture_path.relative_to(root))
            and reference.get("executable_sha256") == digest(executable),
            "Original reference executable or fixture provenance differs")
    return {"reference_sha256": digest(reference_path),
            "fixture_sha256": digest(fixture_path),
            "executable_sha256": digest(executable),
            "transport_binding": "Every captured request and raw RESULT response validated against fixture"}


def reference_cases(record, reference, fixture, fixture_sha256):
    public.validate(record, fixture)
    public.validate_reference(reference, fixture, fixture_sha256)
    require(type(record["rows"]) is int and 1 <= record["rows"] <= len(fixture["samples"]),
            "Fixture does not contain every requested row")
    require(type(record["working_bits"]) is int and record["working_bits"] in [128, 256, 384]
            and type(record["requested_bits"]) is int and record["requested_bits"] > 0,
            "Unsupported public precision metadata")
    n = record["settings"]["propagators"]
    selected = []
    for sample in fixture["samples"][:record["rows"]]:
        label = f"n{n}_{sample['id']}_mode0"
        matches = [case for case in reference["cases"] if case["id"] == label]
        require(len(matches) == 1 and matches[0]["status"] == "captured"
                and matches[0]["response"]["stable"] is True,
                "Missing unique stable complete original IBP reference")
        # Exact arithmetic establishes the zero-pole premise for this fixture.
        propagators = sample["propagators"][:n]
        masses = [Fraction(p["mass_squared"][0]) for p in propagators]
        require(len(propagators) == n and all(m > 0 for m in masses)
                and all(Fraction(p["mass_squared"][1]) == 0 for p in propagators),
                "Zero-pole check requires positive real masses")
        points = [[Fraction(v) for v in p["shift"]] for p in propagators]
        positive_sum = Fraction(0)
        for i in range(n):
            for j in range(i):
                d = [a-b for a, b in zip(points[i], points[j])]
                positive_sum += max(Fraction(0), d[0]**2-sum(v*v for v in d[1:]))
        require(min(masses)-positive_sum/4 > 0 and 7+4-2*n < 0,
                "Independent zero-pole premise is not established")
        selected.append(matches[0])
    return selected


def inspect_single(record, reference, fixture, fixture_sha256):
    cases = reference_cases(record, reference, fixture, fixture_sha256)
    n = record["settings"]["propagators"]
    result = {"status": "complete", "comparison_mode": "single_array_reference_inspection",
              "precision_convergence_checked": False, "n": n, "rank": 7, "rows": record["rows"],
              "working_bits": record["working_bits"], "requested_bits": record["requested_bits"],
              "reference_tolerance": str(REFERENCE_TOLERANCE), "normalization": NORMALIZATION,
              "reference_failures": [], "pole_failures": [], "reference_pole_failures": [],
              "compared_complex_slots": 0, "maximum_reference_error": Decimal(0),
              "maximum_pole_residue": Decimal(0), "maximum_reference_pole_residue": Decimal(0)}
    for row, (sample, case) in enumerate(zip(fixture["samples"], cases)):
        q = public.scale(sample, n)
        for index, monomial in enumerate(record["basis"]):
            normalization = q**(sum(monomial)+4-2*n)
            for slot in range(4):
                value = tuple(public.decimal_rational(record["lanes"][row]["moments"][index][slot][key])
                              / normalization for key in ["real", "imaginary"])
                old = tuple(Decimal(str(v))/normalization for v in case["response"]["moments"][index][slot])
                error = public.norm(tuple(a-b for a, b in zip(value, old))) / max(Decimal(1), public.norm(old))
                location = {"row": row, "moment": index, "monomial": monomial, "slot": slot}
                result["maximum_reference_error"] = max(result["maximum_reference_error"], error)
                if error > REFERENCE_TOLERANCE:
                    result["reference_failures"].append({**location, "normalized_error": str(error)})
                if slot < 3:
                    for vector, maximum, failures in [
                            (value, "maximum_pole_residue", "pole_failures"),
                            (old, "maximum_reference_pole_residue", "reference_pole_failures")]:
                        residue = public.norm(vector)
                        result[maximum] = max(result[maximum], residue)
                        if residue > REFERENCE_TOLERANCE:
                            result[failures].append({**location, "normalized_absolute_residue": str(residue)})
                result["compared_complex_slots"] += 1
    require(result["compared_complex_slots"] == record["rows"] * 330 * 4,
            "Every complex Laurent slot must be compared")
    result["passed"] = not any(result[key] for key in ["reference_failures", "pole_failures", "reference_pole_failures"])
    result["qualification"] = (
        "One complete ordinary public array inspected against stable original IBP and independent zero-pole constraints. "
        "No working-precision convergence, achieved-precision, generic high-point, or performance qualification."
    )
    return result


def compare_arrays(low, high, reference, fixture, fixture_sha256):
    if high is None:
        return inspect_single(low, reference, fixture, fixture_sha256)
    reference_cases(low, reference, fixture, fixture_sha256)
    extra = inspect_single(high, reference, fixture, fixture_sha256)
    result = public.compare(low, high, reference, fixture, fixture_sha256)
    result.update(comparison_mode="two_precision_reference_comparison", precision_convergence_checked=True,
                  normalization=NORMALIZATION, working_bits=[low["working_bits"], high["working_bits"]],
                  requested_bits=low["requested_bits"], reference_pole_failures=extra["reference_pole_failures"],
                  maximum_reference_pole_residue=extra["maximum_reference_pole_residue"])
    result["passed"] = result["passed"] and not result["reference_pole_failures"]
    result["qualification"] = (
        "Two complete ordinary public arrays from the same frozen build checked at increasing working precision, "
        "against stable original IBP and independent zero-pole constraints. One structured family; "
        "no generic high-point or controlled performance qualification."
    )
    return result


def require_same_build(provenance):
    if "high" in provenance:
        keys = ["binary_sha256", "build_manifest_sha256", "source_revision", "semantic_qualification_sha256",
                "baseline_manifest_sha256", "matching_baseline_dependencies"]
        require(all(provenance["low"][key] == provenance["high"][key] for key in keys),
                "Precision runs were not produced by the same frozen build")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("low", help="Single successful public array, or the lower-precision array")
    parser.add_argument("output")
    parser.add_argument("--high", help="Optional independently captured higher-precision array")
    args = parser.parse_args()
    root = Path.cwd()
    here = root / "validation/public-highpoint"
    files = {"low": Path(args.low).resolve(), "fixture": here / "fixture-conditioned_masses.json",
             "reference": here / "reference-conditioned_masses.json"}
    if args.high:
        files["high"] = Path(args.high).resolve()
    require(not Path(args.output).exists(), "Preserve existing comparison evidence; use a fresh output path")
    records = {name: read(path) for name, path in files.items()}
    with localcontext() as context:
        context.prec = 160
        for name in [key for key in ["low", "high"] if key in files]:
            public.validate(records[name], records["fixture"])
        provenance = {name: validate_provenance(records[name], files[name], files["fixture"], root)
                      for name in [key for key in ["low", "high"] if key in files]}
        require_same_build(provenance)
        reference_provenance = validate_reference_capture(records["reference"], files["reference"],
                                                         files["fixture"], records["fixture"], root)
        result = compare_arrays(records["low"], records.get("high"), records["reference"],
                                records["fixture"], digest(files["fixture"]))
    result.update(execution_provenance=provenance, reference_provenance=reference_provenance,
                  input_sha256={name: digest(path) for name, path in files.items()},
                  script_sha256=digest(__file__), comparison_helpers_sha256=digest(public.__file__))
    with Path(args.output).open("x") as stream:
        stream.write(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps({key: value for key, value in result.items() if not key.endswith("failures")}, indent=2, default=str))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
