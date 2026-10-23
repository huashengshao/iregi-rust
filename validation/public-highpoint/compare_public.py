"""Fail-closed full-array convergence and original-IREGI comparison.

Run only after two complete public probes. This is numeric evidence accounting,
not polynomial manipulation. All values retain their represented precision.
"""
from pathlib import Path
from decimal import Decimal, localcontext
from fractions import Fraction
import argparse
import hashlib
import json


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def decimal_rational(text):
    if not isinstance(text, str):
        raise ValueError("Expected an exact rational string")
    value = Fraction(text)
    return Decimal(value.numerator)/Decimal(value.denominator)


def canonical_basis(rank):
    return [[t, x, y, r-t-x-y] for r in range(rank+1) for t in range(r, -1, -1)
            for x in range(r-t, -1, -1) for y in range(r-t-x, -1, -1)]


def validate_reference(reference, fixture, fixture_sha256):
    if (reference.get("status") != "complete"
            or reference.get("reference") != "untouched original IREGI"
            or reference.get("fixture_sha256") != fixture_sha256):
        raise ValueError("Original reference is incomplete or belongs to another fixture")
    samples = {sample["id"]: sample for sample in fixture["samples"]}
    for case in reference["cases"]:
        if case["sample"] not in samples:
            raise ValueError("Unknown original-reference sample")
        sample, n, mode = samples[case["sample"]], case["propagators"], case["mode"]
        if n not in [6, 7] or mode not in [0, 1, 2] or case["rank"] != 7:
            raise ValueError("Unsupported original-reference request")
        label = f"n{n}_{sample['id']}_mode{mode}"
        lines = case["request"].splitlines()
        if len(lines) != n+2 or lines[-1] != "QUIT" or case["id"] != label:
            raise ValueError("Malformed original-reference request")
        header = lines[0].split()
        if (len(header) != 10 or header[:7] != ["EVAL", label, "tensor", str(mode), str(n), "7", "0"]
                or Fraction(header[7]) != Fraction(sample["mu"])
                or header[8] != "0" or Fraction(header[9]) != Fraction("1e-6")):
            raise ValueError("Original-reference request header differs from the fixture")
        for line, propagator in zip(lines[1:-1], sample["propagators"][:n]):
            expected = propagator["shift"] + propagator["mass_squared"] + [str(propagator["power"])]
            if list(map(Fraction, line.split())) != list(map(Fraction, expected)):
                raise ValueError("Original-reference propagators differ from the fixture")
        if case["status"] == "captured":
            raw = [json.loads(line[7:], parse_float=str) for line in case["stdout"].splitlines()
                   if line.startswith("RESULT ")]
            if case["exit_code"] != 0 or raw != [case["response"]] or raw[0]["id"] != label:
                raise ValueError("Original-reference response does not match its captured transport")
            response = case["response"]
            moments = response.get("moments")
            if (type(response.get("stable")) is not bool
                    or response.get("poles") != ["uv1", "ir1", "ir2", "finite"]
                    or not isinstance(moments, list) or len(moments) != 330
                    or any(not isinstance(m, list) or len(m) != 4 for m in moments)
                    or any(not isinstance(s, list) or len(s) != 2 for m in moments for s in m)
                    or any(not Decimal(str(v)).is_finite() for m in moments for s in m for v in s)):
                raise ValueError("Original-reference Laurent ordering or full array shape is invalid")


def validate_provenance(record, result_path, fixture_path, root=None):
    root = Path.cwd() if root is None else Path(root).resolve()
    result_path, fixture_path = Path(result_path).resolve(), Path(fixture_path).resolve()
    run_path = result_path.with_name(result_path.stem + "-run.json")
    run = json.loads(run_path.read_text())
    variant = run.get("variant", "baseline")
    if variant not in ["baseline", "candidate"]:
        raise ValueError("Unknown public execution build variant")
    build_path = result_path.parent / ("build.json" if variant == "baseline" else "candidate-build.json")
    build = json.loads(build_path.read_text())
    if (run.get("status") != "completed" or run.get("exit_code") != 0
            or run.get("last_public_stage") != "all_lanes_success"
            or run.get("result_sha256") != digest(result_path)
            or run.get("fixture_sha256") != digest(fixture_path)
            or run.get("build_manifest_sha256") != digest(build_path)
            or build.get("status") != "passed" or build.get("changed_inputs") != {}):
        raise ValueError("Incomplete, unsuccessful, or mismatched public execution provenance")
    if variant == "candidate":
        if (build.get("core_exit_code") != 0 or build.get("probe_exit_code") != 0
                or build.get("frozen_core_sources_verified_after_build") is not True):
            raise ValueError("Candidate build did not verify its frozen inputs")
        snapshot = root / build["frozen_core_source"]
        for name, expected in build["library_source_hashes"].items():
            if digest(snapshot / Path(name).relative_to("crates/iregi-rust")) != expected:
                raise ValueError("Frozen core source changed after compilation")
        if run.get("frozen_source_files_unchanged") != len(build["library_source_hashes"]):
            raise ValueError("Run did not verify its complete frozen core source")
    elif build.get("exit_code") != 0:
        raise ValueError("Baseline build failed")
    binary = root / ("target/public-highpoint/highpoint_public" if variant == "baseline"
                     else "target/public-highpoint/candidate/highpoint_public")
    source = root / "crates/iregi-rust/examples/highpoint_public.rs"
    if (run.get("binary_sha256") != build.get("binary_sha256")
            or run.get("binary_sha256") != digest(binary)
            or run.get("probe_source_sha256") != build.get("source_sha256")
            or run.get("probe_source_sha256") != digest(source)
            or run.get("log_sha256") != digest(result_path.with_suffix(".log"))):
        raise ValueError("Public executable, source, or captured log differs from its provenance")
    algorithms = {"Ibp": "ibp", "PassarinoVeltman": "pv", "Hybrid": "hybrid"}
    settings = record["settings"]
    expected_command = ["taskset", "-c", "0", str(binary), str(fixture_path.relative_to(root)),
                        str(settings["propagators"]), str(settings["rank"]), algorithms[settings["algorithm"]],
                        str(record["working_bits"]), str(record["requested_bits"]), str(record["rows"]),
                        str(result_path.relative_to(root))]
    if run.get("command") != expected_command or record["fixture"] != str(fixture_path.relative_to(root)):
        raise ValueError("Public command does not match its captured output settings")
    return {"run_manifest_sha256": digest(run_path), "build_manifest_sha256": digest(build_path),
            "binary_sha256": run["binary_sha256"], "variant": variant,
            "library_source_hashes": build["library_source_hashes"],
            "explicit_extern_sha256": build["explicit_extern_sha256"]}


def validate(record, fixture):
    settings = record["settings"]
    n, rank, rows = settings["propagators"], settings["rank"], record["rows"]
    if (record["status"] != "all_lanes_success" or n not in [6, 7] or rank != 7
            or settings["powers"] != [1]*n or settings["dimension_shift"] != 0
            or settings["convention"] != "IregiNative" or settings["tensor_weights"] != "Components"
            or settings["invariants"] != "FromShifts" or settings["input_policy"] != "Preserve"
            or record["components"] != 1 or not 1 <= rows <= 3
            or record["basis"] != canonical_basis(rank)
            or record["lane_statuses"] != ["Success"]*rows or len(record["lanes"]) != rows):
        raise ValueError("Incomplete or unsupported public report")
    expected_inputs = []
    for sample in fixture["samples"][:rows]:
        propagators = sample["propagators"][:n]
        row = [[str(Fraction(v)), "0"] for p in propagators for v in p["shift"]]
        row += [[str(Fraction(v)) for v in p["mass_squared"]] for p in propagators]
        row += [[str(Fraction(sample["mu"])), "0"]]
        expected_inputs.append(row)
    if record["input_exact_rational"] != expected_inputs:
        raise ValueError("Public inputs differ from the original fixture")
    for row, lane in enumerate(record["lanes"]):
        if lane["row"] != row or lane["status"] != "Success" or len(lane["moments"]) != 330:
            raise ValueError("Incomplete or reordered public lane")
        for slots in lane["moments"]:
            if len(slots) != 4:
                raise ValueError("Incomplete Laurent slots")
            for slot in slots:
                for key in ["real", "imaginary"]:
                    if not decimal_rational(slot[key]).is_finite():
                        raise ValueError("Nonfinite public result")


def norm(value):
    return sum(x*x for x in value).sqrt()


def scale(sample, n):
    p = [[decimal_rational(v) for v in item["shift"]] for item in sample["propagators"][:n]]
    q2 = max(Decimal(1), *(abs(decimal_rational(item["mass_squared"][0])) for item in sample["propagators"][:n]))
    for i in range(n):
        for j in range(i):
            d = [x-y for x, y in zip(p[i], p[j])]
            q2 = max(q2, abs(d[0]**2-sum(v*v for v in d[1:])))
    return q2.sqrt()


def compare(low, high, reference, fixture, fixture_sha256):
    validate_reference(reference, fixture, fixture_sha256)
    validate(low, fixture)
    validate(high, fixture)
    if (low["settings"] != high["settings"] or low["rows"] != high["rows"]
            or low["input_exact_rational"] != high["input_exact_rational"]
            or low["working_bits"] >= high["working_bits"]
            or low["requested_bits"] != high["requested_bits"]):
        raise ValueError("Precision runs must differ only in increasing working precision")
    n = low["settings"]["propagators"]
    result = {"status": "complete", "n": n, "rank": 7, "rows": low["rows"],
              "convergence_tolerance": str(Decimal(2)**-80), "reference_tolerance": "1e-10",
              "convergence_failures": [], "reference_failures": [], "pole_failures": [],
              "compared_complex_slots": 0, "maximum_convergence_error": Decimal(0),
              "maximum_reference_error": Decimal(0), "maximum_pole_residue": Decimal(0)}
    for row, sample in enumerate(fixture["samples"][:low["rows"]]):
        label = f"n{n}_{sample['id']}_mode0"
        matches = [x for x in reference["cases"] if x["id"] == label]
        if len(matches) != 1 or matches[0]["status"] != "captured":
            raise ValueError("Missing unique original reference")
        ref = matches[0]["response"]
        if ref["stable"] is not True or len(ref["moments"]) != 330:
            raise ValueError("Original reference did not return a stable complete array")
        q = scale(sample, n)
        for index, monomial in enumerate(low["basis"]):
            normalization = q**(sum(monomial)+4-2*n)
            for slot in range(4):
                lhs, rhs = [tuple(decimal_rational(record["lanes"][row]["moments"][index][slot][key])/normalization
                                  for key in ["real", "imaginary"]) for record in [low, high]]
                old = tuple(Decimal(str(v))/normalization for v in ref["moments"][index][slot])
                if len(old) != 2 or any(not v.is_finite() for v in old):
                    raise ValueError("Malformed original reference coefficient")
                convergence = norm(tuple(a-b for a, b in zip(lhs, rhs)))/max(Decimal(1), norm(rhs))
                original = norm(tuple(a-b for a, b in zip(rhs, old)))/max(Decimal(1), norm(old))
                location = {"row": row, "moment": index, "monomial": monomial, "slot": slot}
                result["maximum_convergence_error"] = max(result["maximum_convergence_error"], convergence)
                result["maximum_reference_error"] = max(result["maximum_reference_error"], original)
                if convergence > Decimal(2)**-80:
                    result["convergence_failures"].append({**location, "normalized_error": str(convergence)})
                if original > Decimal("1e-10"):
                    result["reference_failures"].append({**location, "normalized_error": str(original)})
                if slot < 3:
                    residue = max(norm(lhs), norm(rhs))
                    result["maximum_pole_residue"] = max(result["maximum_pole_residue"], residue)
                    if residue > Decimal("1e-10"):
                        result["pole_failures"].append({**location, "normalized_absolute_residue": str(residue)})
                result["compared_complex_slots"] += 1
    result["passed"] = not any(result[key] for key in ["convergence_failures", "reference_failures", "pole_failures"])
    result["qualification"] = "Full ordinary public arrays at two working precisions compared with original IBP and independent zero-pole constraints. One structured coordinate family; no generic high-point or performance claim. Separate finite simplex witnesses add independent checks."
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("low")
    parser.add_argument("high")
    parser.add_argument("output")
    args = parser.parse_args()
    here = Path("validation/public-highpoint")
    files = {"low": Path(args.low), "high": Path(args.high),
             "reference": here / "reference-conditioned_masses.json", "fixture": here / "fixture-conditioned_masses.json"}
    records = {key: json.loads(path.read_text()) for key, path in files.items()}
    provenance = {key: validate_provenance(records[key], files[key], files["fixture"]) for key in ["low", "high"]}
    if any(provenance["low"][key] != provenance["high"][key]
           for key in ["binary_sha256", "build_manifest_sha256", "library_source_hashes", "explicit_extern_sha256"]):
        raise ValueError("Precision runs were not produced by the same frozen build")
    with localcontext() as context:
        context.prec = 160
        result = compare(**records, fixture_sha256=digest(files["fixture"]))
    result["execution_provenance"] = provenance
    result["input_sha256"] = {key: digest(path) for key, path in files.items()}
    result["script_sha256"] = digest(__file__)
    Path(args.output).write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps({k: v for k, v in result.items() if not k.endswith("failures")}, indent=2, default=str))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
