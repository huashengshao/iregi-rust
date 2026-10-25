#!/usr/bin/env python3
"""Portable saved-evidence/source reconstruction; no numerical library imports."""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import io
import json
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "target/public-highpoint/numeric-types-dual/"
DOMAINS = {"f64": 1, "DoubleFloat": 1, "Float128Dual": 6, "Float256Dual": 6}
SCHEDULE = [("singleton_affine", [0]), ("mixed", [0, 3, 1, 2, 0]),
            ("reordered", [2, 1, 0, 3, 0]), ("empty", []), ("singleton_again", [0])]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def safe(name):
    p = Path(name)
    require(name and not p.is_absolute() and ".." not in p.parts and str(p) == name,
            "unsafe archive path: " + name)


def archive(path, expected):
    actual, bodies = {}, {}
    with tarfile.open(fileobj=io.BytesIO(path.read_bytes()), mode="r:gz") as stream:
        for member in stream:
            safe(member.name)
            require(member.isfile() and member.name not in actual, "non-file/duplicate archive member")
            body = stream.extractfile(member).read()
            require(not body.startswith((b"\x7fELF", b"!<arch>")), "compiled archive member")
            actual[member.name] = {"sha256": digest(body), "bytes": len(body)}
            bodies[member.name] = body
    require(actual == expected, "archive member inventory differs")
    return bodies


def operand(value):
    require(set(value) == {"rational", "precision", "negative_sign", "finite"}, "native operand metadata")
    require(value["finite"] is True and type(value["precision"]) is int
            and type(value["negative_sign"]) is bool, "nonfinite/incomplete native operand")
    x = Fraction(value["rational"])
    require(value["precision"] >= 0 and (x == 0 or value["precision"] > 0)
            and (x == 0 or value["negative_sign"] == (x < 0)), "native precision/sign differs")
    return x


def complex_value(value):
    require(len(value) == 2, "incomplete complex operand")
    return tuple(operand(v) for v in value)


def within(actual, expected):
    return sum((a - b)**2 for a, b in zip(actual, expected)) <= Fraction(1, 10**20) * max(
        Fraction(1, 256**2), sum(x*x for x in expected))


def check_saved(pilot, numeric_audit):
    # These are fixed numeric fixture equalities from the independent source
    # math review. All actual polynomial/jet generation belongs to Symbolica.
    a = Fraction(1_152_921_504_606_846_977, 1_152_921_504_606_846_976)
    b = Fraction(3, 2)
    linear = [[1, a, b, 0, 0, 0], [1, a, b, 0, a*b, 0], [1, 0, 0, 0, 0, 0]]
    square = [[1, 2*a, 2*b, a*a, 2*a*b, b*b],
              [1, 2*a, 2*b, a*a, 4*a*b, b*b], [1, 0, 0, 0, 0, 0]]
    response = [[1, -8*a, -8*b, 36*a*a, 72*a*b, 36*b*b],
                [1, -8*a, -8*b, 36*a*a, 64*a*b, 36*b*b], [1, 0, 0, 0, 0, 0]]
    fixture = read(ROOT / "validation/public-highpoint/fixture-conditioned_masses.json")["samples"][0]
    ps = fixture["propagators"][:6]
    base = [Fraction(x) for p in ps for x in p["shift"]]
    base += [Fraction(p["mass_squared"][0]) for p in ps] + [Fraction(fixture["mu"])]
    original = read(ROOT / "validation/public-highpoint/reference-conditioned_masses.json")
    original = [x for x in original["cases"] if x["id"] == "n6_base_mode0"]
    require(len(original) == 1 and original[0]["response"]["stable"] is True, "original scalar anchor")
    original = [tuple(Fraction(v) for v in z) for z in original[0]["response"]["moments"][0]]
    baseline = read(ROOT / "validation/highpoint-six-point-api/qualified-v2/public-rank3-256-001/result.json")
    scalar = [tuple(Fraction(z[k]) for k in ["real", "imaginary"])
              for z in baseline["lanes"][0]["moments"][0]]
    outputs = inputs = 0
    counts = {}
    for domain, components in DOMAINS.items():
        data = json.loads(pilot[f"run-{domain}-001/result.json"])
        gate = json.loads(pilot[f"comparison-{domain}.json"])
        require(gate["provenance_valid"] is True and gate["provenance_errors"] == [], "saved provenance admission")
        require(len(gate["input_sha256"]) == 231, "saved binding inventory")
        require([[Fraction(x) for x in row] for row in data["exact_homogeneity_multipliers"]] == response,
                "independently reviewed response multipliers differ")
        rows = data["represented_input_rows"]
        require(len(rows) == 4 and all(len(row) == 31*components for row in rows), "input jet inventory")
        for profile, row in enumerate(rows):
            for parameter in range(31):
                coefficients = (square if 24 <= parameter < 30 else linear)[0 if profile == 3 else profile]
                for c in range(components):
                    target = 0 if profile == 3 and parameter == 30 else base[parameter]*coefficients[c]
                    require(complex_value(row[parameter*components+c]) == (target, 0), "exact beyond53 input jet")
                    inputs += 1
        successes = invalids = empty = available = rejected_positive = 0
        for call_index, call in enumerate(data["calls"]):
            require(call_index < 5 and (call["name"], call["profile_indices"]) == SCHEDULE[call_index], "call schedule")
            require(call["input_preserved_exactly"] is True and call["status"] == "captured", "call/input preservation")
            require(call["components"] == components and call["basis"] == [[0, 0, 0, 0]], "returned scalar shape")
            indices = call["profile_indices"]
            require(len(call["lanes"]) == len(indices), "lane inventory")
            if not indices:
                empty += 1
                require(call["diagnostics"] == [], "empty reset diagnostics")
            for row, (profile, lane) in enumerate(zip(indices, call["lanes"])):
                require(lane["row"] == row and lane["profile"] == profile, "lane identity")
                values = lane["values"]
                if profile == 3:
                    require(values is None and lane["status"].startswith("InvalidInput("), "invalid-mu failure policy")
                    invalids += 1
                    continue
                if values is None:
                    require(domain == "f64" and lane["status"].startswith("Unstable(")
                            and "estimated cancellation" in lane["status"], "unreported positive rejection")
                    rejected_positive += 1
                    continue
                require(lane["status"] == "Success" and len(values) == 4*components, "successful array incomplete")
                successes += 1
                for index, value in enumerate(values):
                    pole, c = divmod(index, components)
                    value = complex_value(value)
                    target = tuple((response[profile][c] if components == 6 else 1)*x for x in scalar[pole])
                    require(within(value, target), "available scaling identity exceeded tolerance")
                    if c == 0:
                        require(within(value, original[pole]), "available original scalar exceeded tolerance")
                    require(pole == 3 or value == (0, 0), "nonzero pole")
                    require(profile != 2 or c == 0 or value == (0, 0), "constant-profile Taylor response")
                    outputs += 1
                    available += 1
        expected = {"f64": (5, 0, 2, 1, 0, 10), "DoubleFloat": (5, 10, 2, 1, 40, 0),
                    "Float128Dual": (1, 1, 0, 0, 24, 0), "Float256Dual": (0, 0, 0, 0, 0, 0)}[domain]
        require((len(data["calls"]), successes, invalids, empty, available, rejected_positive) == expected,
                "failed/partial case coverage changed")
        independent = numeric_audit["domains"][domain]
        require(independent["complex_slots"] == available and independent["successful_lanes"] == successes,
                "independent audit coverage differs")
        require(gate["passed"] is (domain == "DoubleFloat"), "failed domain promoted")
        counts[domain] = {"successful_lanes": successes, "complex_slots": available, "full_gate_passed": gate["passed"]}
    pair = json.loads(pilot["comparison-paired.json"])
    require(pair["passed"] is False and pair["precision_convergence_qualified"] is False
            and pair["comparisons"] == [], "unsupported pair promoted")
    require((outputs, inputs) == (64, 1736), "complete saved numeric coverage")
    return {"available_output_slots_checked": outputs, "input_slots_checked": inputs, "domains": counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct", type=Path, help="write exact noncompiled private source/evidence tree to a new directory")
    args = parser.parse_args()
    manifest = read(HERE / "manifest.json")
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file()}
    require(actual == set(manifest["files"]) | {"manifest.json"}, "capsule file inventory")
    for name, item in manifest["files"].items():
        data = (HERE/name).read_bytes()
        require({"sha256": digest(data), "bytes": len(data)} == item, "changed capsule payload: " + name)
    for name, item in manifest["borrowed_inputs"].items():
        data = (ROOT/name).read_bytes()
        require({"sha256": digest(data), "bytes": len(data)} == item, "changed borrowed input: " + name)
    parent = manifest["parent_archive"]
    inherited = archive(ROOT/parent["path"], parent["members"])
    delta = archive(HERE/manifest["delta_archive"]["path"], manifest["delta_archive"]["members"])
    pilot = dict(inherited)
    pilot.update(delta)
    require({name: {"sha256": digest(body), "bytes": len(body)} for name, body in pilot.items()}
            == manifest["reconstructed_private_tree"], "private tree reconstruction differs")
    source = json.loads(pilot["source.json"])
    actual_core = {name[5:]: digest(body) for name, body in pilot.items() if name.startswith("core/")}
    require(actual_core == source["candidate_files"] and len(actual_core) == 61, "exact 61-file core reconstruction")
    declaration = source["full_byte_restoration"]["removed_only"].encode()
    for name, expected in source["full_byte_restoration"]["restored_original_files"].items():
        body = pilot["core/"+name]
        if name == "crates/iregi-rust/src/lib.rs":
            require(body.endswith(declaration), "capture-only module declaration")
            body = body[:-len(declaration)]
        require(digest(body) == expected, "qualified original source not restored")
    require(pilot["source/capture.rs"] == pilot["core/crates/iregi-rust/src/highpoint_numeric_probe.rs"]
            and pilot["source/jet_inputs.rs"] == pilot["core/crates/iregi-rust/src/jet_inputs.rs"], "helper reconstruction")
    protocol = json.loads(pilot["protocol.json"])
    require(len(protocol["inputs"]) == 219, "protocol inventory")
    for name, body in pilot.items():
        if PREFIX+name in protocol["inputs"]:
            require(digest(body) == protocol["inputs"][PREFIX+name], "guarded reconstructed source differs")
    source_review = json.loads(pilot["runner-comparator-source-review.json"])
    for name, expected in source_review["subject_sha256"].items():
        require(digest(pilot[name]) == expected, "reviewed harness source differs")
    qualification = read(HERE/"qualification.json")
    require(pilot["qualification.json"] == (HERE/"qualification.json").read_bytes(), "qualification snapshot")
    require(qualification["status"] == "private_typed_scalar_n6_pilot_completed_with_failures"
            and qualification["public_dual_qualified"] is False
            and qualification["derivative_uncertainty_transport_qualified"] is False
            and qualification["performance_qualified"] is False, "qualification scope changed")
    checked = check_saved(pilot, read(HERE/"independent-numeric-audit.json"))
    if args.reconstruct:
        destination = args.reconstruct.resolve()
        destination.mkdir(parents=True, exist_ok=False)
        for name, body in pilot.items():
            path = destination/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
    print(json.dumps({"status": "passed", "reconstructed_private_files": len(pilot),
        "restored_original_files": 59, "core_files": 61, **checked,
        "no_compiler_integral_reference_or_benchmark_executed": True,
        "native_binary_requalification_performed": False,
        "reconstruction_destination": str(args.reconstruct) if args.reconstruct else None}))


if __name__ == "__main__":
    main()
