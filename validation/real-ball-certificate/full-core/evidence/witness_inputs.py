"""Private frozen-input witnesses; no numerical subprocess or compiler is invoked.

API: build_bundle(), write_bundle(directory), compare_kernel(packet, a, b),
compare_physical(packet, a, b), read_responses(path), reference_catalog().
Requests and retained outputs use SHA256 of canonical UTF-8 JSON plus newline.
Kernel durations are diagnostic only, never a performance qualification.
"""
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVISION = "6b24c0372022e22606a1ac85f30c7fa579fb41f0"
FROZEN = ROOT / "target/benchmark/sources" / REVISION
PINS = {
    "fixtures/models/sm.json": "95716e0deeabe7bce3638fdc69264022f9a25ddad63a97e6441bf4843cd1ec41",
    "examples/graphs/ggh_top_triangle.dot": "3e0f8dd9aea927698e4fd08caa666b7342a065c3b137366e2ecd911fa71b2206",
    "validation/physical/ggh-cli-input.json": "55327750a66af5d8442aacc9e8b8366311dac6c7da9d559d5a28d0e2b324b4b8",
    "validation/benchmark/physical-joint-smoke/canonical-reference/reference-records.json": "4cf98c31922ad5f09039816494b65c34b676c1e696297e400aa4b70342d98fa2",
    "validation/benchmark/physical-joint-smoke/qualification.json": "2e19d67d76bedf6cab7776368b18afff2d2efd7afda553dd23135ef30fa5300a",
    "validation/benchmark/physical-alignment/ggh-preserved-reference.json": "35efc175b9f822f7678a13be3d8a3574a26886beea65cdd961ce370753deacaa",
    "validation/benchmark/physical-alignment/qualification.json": "579f21d805c8b9a3b0ffa863087d24bd8c36c45acd11af77af1db4e471bfe516",
    "validation/physical/madloop/fixtures/ggh-helicity-1.json": "afa15fe2f94933b5d70e57824de65d091414b1a2b224177612f7d8c5837ef71d",
    "validation/physical/ggh-cli-comparison.json": "8c0c6e3791c7bc69371a808c54329ca4f3ede50dfc04b90d979ae7483062d6a1",
    "validation/physical/compare_cli.py": "bd15231de5b8adeb70524e5b92e7f8133afd7139aa59977395acb3474e8bae5b",
}
COUNTERS = ["input_rows", "argument_rows", "master_family_batches", "master_rows",
            "pentagon_box_rows", "reduction_rows", "fallback_rows", "fallback_successes", "analytic_rows"]
PHYSICAL_COUNTERS = ["input_rows", "master_rows", "master_family_batches", "pentagon_box_rows",
                     "fallback_rows", "analytic_rows"]
BASIS = [[indices.count(axis) for axis in range(4)] for rank in range(3)
         for indices in itertools.combinations_with_replacement(range(4), rank)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def json_sha256(value):
    return hashlib.sha256(json_bytes(value)).hexdigest()


def file_record(path, expected=None):
    path = Path(path).resolve()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    require(expected is None or digest == expected, f"file hash differs: {path}")
    return {"path": str(path), "sha256": digest, "bytes": path.stat().st_size}


def frozen_assets():
    return {name: file_record(FROZEN / name, digest) for name, digest in PINS.items()}


def reference_catalog():
    assets = frozen_assets()
    return {
        "canonical_iregi": assets["validation/benchmark/physical-joint-smoke/canonical-reference/reference-records.json"],
        "canonical_qualification": assets["validation/benchmark/physical-joint-smoke/qualification.json"],
        "madloop_preserved": assets["validation/benchmark/physical-alignment/ggh-preserved-reference.json"],
        "madloop_preserved_qualification": assets["validation/benchmark/physical-alignment/qualification.json"],
        "historical_madloop": assets["validation/physical/madloop/fixtures/ggh-helicity-1.json"],
        "historical_physical_comparison": assets["validation/physical/ggh-cli-comparison.json"],
        "existing_numeric_comparer_source": assets["validation/physical/compare_cli.py"],
        "scope": "Independent references apply to the unchanged real-mass ggH input only; complex-mass variants have no independent fixture here.",
        "canonical_convention": "IREGI native UV1/IR1/IR2/finite; all three modes, rank2,15 moments, preserved input",
        "physical_convention": "Rust OneLoop; canonical tensors need the existing numeric conversion. MadLoop group1 raw [finite,single,double] has fixed equal-color factor -1/2.",
        "excluded": ["R2", "UV counterterms"],
        "performance_gate": False,
    }


def _packet(kind, request, roles, assets):
    return {"kind": kind, "id": request.get("id", request.get("configuration", {}).get("id")),
            "request": request, "request_sha256": json_sha256(request), "lane_roles": roles,
            "source_revision": REVISION, "assets": assets, "performance_gate": False,
            "timing_scope": "diagnostic only; no parity, speedup, or quiet-window qualification"}


def _f64_exact(text):
    # Only the binary64 kernel protocol requires Python floats. Fixture values
    # are dyadic; reject any conversion that would silently round this point.
    value = float(text)
    require(Fraction.from_float(value) == Fraction(text), "kernel fixture component is not exactly binary64")
    return value


def build_bundle():
    assets = frozen_assets()
    sample = json.loads((FROZEN / "validation/physical/ggh-cli-input.json").read_text())
    require(sample["rank"] == 2 and len(sample["propagators"]) == 3, "ggH fixture shape differs")
    base = {"shifts": [[_f64_exact(v) for v in p["shift"]] for p in sample["propagators"]],
            "masses": [[_f64_exact(v) for v in p["mass_squared"]] for p in sample["propagators"]],
            "mu": _f64_exact(sample["mu"])}
    kernels = []
    for family, widths in [("real", [1, 3, 32]), ("complex", [1, 3, 32]), ("mixed-invalid", [3, 32])]:
        for width in widths:
            rows, roles = [], []
            for lane in range(width):
                row = deepcopy(base)
                role = family
                if family == "mixed-invalid":
                    role = ["real", "complex", "invalid_scale", "real", "complex"][lane % 5]
                if role == "complex":
                    row["masses"] = [[mass[0], -0.25] for mass in row["masses"]]
                if role == "invalid_scale":
                    row["mu"] = -125.0
                rows.append(row)
                roles.append(role)
            request = {"id": f"real-ball-ggh-{family}-b{width}", "n": 3, "rank": 2,
                       "algorithm": "Hybrid", "samples": rows, "warmup": 0,
                       "repeats": 1, "iterations": 1, "profile": True}
            kernels.append(_packet("kernel", request, roles, assets))
    physical = []
    for width in [1, 3]:
        configuration = {"id": f"real-ball-physical-ggh-f64-b{width}",
                         "model": (FROZEN / "fixtures/models/sm.json").read_text(),
                         "dot": (FROZEN / "examples/graphs/ggh_top_triangle.dot").read_text(),
                         "component": [0, 0], "input": {"samples": [deepcopy(sample) for _ in range(width)]},
                         "precision": "f64", "bits": 53, "accuracy_bits": 53, "algorithm": "Hybrid"}
        physical.append(_packet("physical", {"op": "prepare", "configuration": configuration}, ["real"] * width, assets))
    return {"schema": 1, "source_revision": REVISION, "source_root": str(FROZEN),
            "generator": file_record(__file__), "core_snapshot": file_record(ROOT / "target/real-ball-core/sources.json"),
            "assets": assets, "kernel": kernels, "physical": physical,
            "independent_references": reference_catalog(), "performance_gate": False}


def write_bundle(directory):
    """Write a fresh directory; never overwrite evidence from an earlier run."""
    directory = Path(directory)
    bundle = build_bundle()
    directory.mkdir(parents=True, exist_ok=False)
    files = []
    for packet in bundle["kernel"] + bundle["physical"]:
        path = directory / (packet["id"] + ".request.json")
        path.write_bytes(json_bytes(packet["request"]))
        files.append(file_record(path, packet["request_sha256"]))
    bundle["request_files"] = files
    path = directory / "inputs.json"
    path.write_bytes(json_bytes(bundle))
    return file_record(path)


def read_responses(path):
    """Retain non-JSON engine chatter; malformed JSON records fail explicitly."""
    records, chatter = [], []
    for line in Path(path).read_text().splitlines():
        payload = line[7:] if line.startswith("RESULT ") else line
        if line.startswith("RESULT ") or payload.lstrip().startswith("{"):
            records.append(json.loads(payload, parse_constant=lambda text: (_ for _ in ()).throw(ValueError(text))))
        elif line.strip():
            chatter.append(line)
    return {"source": file_record(path), "records": records, "chatter": chatter}


def _decimal(value):
    require(type(value) in (int, float, str), "numeric component has invalid type")
    result = Decimal.from_float(value) if type(value) is float else Decimal(value)
    require(result.is_finite(), "nonfinite numeric component")
    return result


def _tensor_compare(left, right, scale, tolerance, report, location):
    require(isinstance(left, list) and len(left) == 2 and isinstance(right, list) and len(right) == 2,
            f"malformed complex pair at {location}")
    with localcontext() as context:
        context.prec = 160
        a, b = list(map(_decimal, left)), list(map(_decimal, right))
        error = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2).sqrt()
        magnitude = (b[0] ** 2 + b[1] ** 2).sqrt()
        normalized = error / (scale + magnitude)
        report["complex_slots_checked"] += 1
        if normalized > Decimal(report["maximum_normalized_difference"]):
            report["maximum_normalized_difference"] = str(normalized)
            report["worst"] = location
        if normalized > tolerance:
            report["differences"].append({"location": location, "baseline": left, "candidate": right,
                                          "normalized_difference": str(normalized)})


def _moments(a, b, tolerance, report, lane):
    require(isinstance(a, list) and isinstance(b, list) and len(a) == len(b) == 15, "incomplete rank2 tensors")
    for moment, (left, right) in enumerate(zip(a, b, strict=True)):
        require(isinstance(left, list) and isinstance(right, list) and len(left) == len(right) == 4,
                "incomplete Laurent slots")
        scale = Decimal(173) ** (sum(BASIS[moment]) - 2)
        for pole in range(4):
            _tensor_compare(left[pole], right[pole], scale, tolerance, report, [lane, moment, pole])


def _counters(a, b, expected, keys):
    require(isinstance(a, dict) and isinstance(b, dict), "missing execution counters")
    require(all(type(value.get(key)) is int and value[key] >= 0 for value in [a, b] for key in keys),
            "missing/invalid execution counter")
    require(a == b and a["input_rows"] == expected, "execution counters differ or batch width is wrong")


def _comparison_record(value, omit_numeric_outputs=False):
    """Remove only known timers; unknown metadata differences remain failures."""
    if isinstance(value, dict):
        return {key: _comparison_record(item, omit_numeric_outputs) for key, item in value.items()
                if key not in {"preparation_ns", "total_ns", "profile_ns", "first_observed_ns"}
                and not (omit_numeric_outputs and key in {"moments", "integral"})}
    if isinstance(value, list):
        return [_comparison_record(item, omit_numeric_outputs) for item in value]
    return value


def _compare(packet, baseline, candidate, tolerance, physical):
    report = {"passed": False, "performance_gate": False, "request_sha256": packet.get("request_sha256"),
              "baseline": deepcopy(baseline), "candidate": deepcopy(candidate), "errors": [], "differences": [],
              "complex_slots_checked": 0, "maximum_normalized_difference": "0", "tolerance": str(tolerance)}
    try:
        require(json_sha256(packet["request"]) == packet["request_sha256"], "request hash differs")
        require(packet["source_revision"] == REVISION and packet["kind"] == ("physical" if physical else "kernel"),
                "packet scope differs")
        tol = _decimal(tolerance)
        require(tol >= 0, "negative tolerance")
        request = packet["request"]
        roles = packet["lane_roles"]
        width = len(roles)
        for response in [baseline, candidate]:
            require(isinstance(response, dict) and response.get("id") == packet["id"], "response identity differs")
            require(response.get("master_backend") == "SymbolicaBatch", "unexpected scalar backend")
        if physical:
            require(request["op"] == "prepare", "physical comparer requires a prepare packet")
            configuration = request["configuration"]
            require(len(configuration["input"]["samples"]) == width, "request batch width differs")
            require(baseline.get("status") == candidate.get("status") == "prepared", "physical adapter failed")
            a, b = baseline["output"], candidate["output"]
            expected_settings = {"propagators": 3, "rank": 2, "powers": [1, 1, 1], "dimension_shift": 0,
                                 "algorithm": "Hybrid", "convention": "OneLoop", "tensor_weights": "Components",
                                 "invariants": "FromShifts", "input_policy": "Preserve"}
            for value in [a, b]:
                require(value["settings"] == expected_settings and value["basis"] == BASIS, "physical settings/basis differ")
                require(value["poles"] == ["uv1", "ir1", "ir2", "finite"], "Laurent order differs")
                require(value["precision_bits"] == 53 and value["precision_control"]["accuracy_bits"] == 53,
                        "physical precision differs")
                require(value["graph"]["name"] == "ggh_top_triangle", "graph identity differs")
            for field in ["algorithm_requested", "algorithm_used", "preparation_notes", "precision_control", "kinematics_contract"]:
                require(a[field] == b[field], f"physical metadata differs: {field}")
            rows_a, rows_b = a["samples"], b["samples"]
            _counters(a["execution"], b["execution"], width, PHYSICAL_COUNTERS)
        else:
            require(request["n"] == 3 and request["rank"] == 2 and request["algorithm"] == "Hybrid"
                    and len(request["samples"]) == width, "kernel request shape differs")
            for response in [baseline, candidate]:
                require(response.get("precision") == "binary64" and response.get("degrees") == [sum(x) for x in BASIS],
                        "kernel precision/basis degrees differ")
                require(response.get("stable") is ("invalid_scale" not in roles), "kernel success flag differs from lane contract")
            rows_a, rows_b = baseline["lanes"], candidate["lanes"]
            _counters(baseline["execution"], candidate["execution"], width, COUNTERS)
        require(isinstance(rows_a, list) and isinstance(rows_b, list) and len(rows_a) == len(rows_b) == width,
                "incomplete response batch")
        for lane, (a, b, role) in enumerate(zip(rows_a, rows_b, roles, strict=True)):
            require(a.get("status") == b.get("status"), f"lane {lane} status differs")
            if role == "invalid_scale":
                require(str(a.get("status")).startswith("InvalidInput(") and a.get("moments") is None
                        and b.get("moments") is None, f"lane {lane} did not reject invalid scale")
                continue
            require(role in {"real", "complex"} and a.get("status") == "success", f"valid lane {lane} failed")
            for flag in ["analytic_used", "fallback_used"]:
                require(type(a.get(flag)) is bool and a[flag] == b.get(flag), f"lane {lane} {flag} differs")
            _moments(a["moments"], b["moments"], tol, report, lane)
            if physical:
                expected_id = configuration["input"]["samples"][lane]["id"]
                require(a["id"] == b["id"] == expected_id, "physical sample identity differs")
                require(len(a["integral"]) == len(b["integral"]) == 4, "incomplete contracted Laurent array")
                for pole in range(4):
                    _tensor_compare(a["integral"][pole], b["integral"][pole], Decimal(173), tol, report,
                                    [lane, "contraction", pole])
        # Under the default exact policy, this also retains numeric spelling
        # and signed-zero differences. An explicit nonzero tolerance relaxes
        # numerical tensor/contraction values only, never metadata or failures.
        require(json_bytes(_comparison_record(baseline, tol != 0))
                == json_bytes(_comparison_record(candidate, tol != 0)),
                "non-timing response fields differ")
        report["passed"] = not report["differences"]
    except (ValueError, KeyError, TypeError, IndexError, ArithmeticError) as error:
        report["errors"].append(f"{type(error).__name__}: {error}")
    return report


def compare_kernel(packet, baseline, candidate, tolerance="0"):
    return _compare(packet, baseline, candidate, tolerance, False)


def compare_physical(packet, baseline, candidate, tolerance="0"):
    return _compare(packet, baseline, candidate, tolerance, True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write inputs to a fresh directory; no engine execution")
    arguments = parser.parse_args()
    print(json.dumps(write_bundle(arguments.write) if arguments.write else build_bundle(), indent=2, allow_nan=False))
