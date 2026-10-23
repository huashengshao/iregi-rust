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


def compare(low, high, reference, fixture):
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
    with localcontext() as context:
        context.prec = 160
        result = compare(**{key: json.loads(path.read_text()) for key, path in files.items()})
    result["input_sha256"] = {key: digest(path) for key, path in files.items()}
    result["script_sha256"] = digest(__file__)
    Path(args.output).write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps({k: v for k, v in result.items() if not k.endswith("failures")}, indent=2, default=str))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
