"""Independent saved-text audit; stdlib only, never imports a producer.

``audit(read_bytes)`` accepts project-relative aliases for portable capsule
replay. It does not read executables, licenses or numerical package trees.
All comparisons below concern represented numeric data, not symbolic algebra.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import product
import hashlib
import json
from pathlib import Path
import re

BASE = "target/low-n-complex-rank7-oracle/quadrature-proposal"
CAPTURE = BASE + "/capture-001"
PINS = {
    BASE + "/manifest.json": "7bcc2ed4b8a867eab1ea7d835e58546d20108af7a600a50c0898175e8d249625",
    CAPTURE + "/receipt.json": "aa4e89f43ae5f16c4b30e702a600fd8df4732167b24b09d7de8850f16661d15d",
    CAPTURE + "/comparison.json": "ae5d90e0eab7ac38a660ac5af956fb2d2799a23caf17b26363a644cfa008a566",
    BASE + "/numerical-release.json": "a0468d4052f96f9c897ee3cd5e981d5d8b19adaa598dac8e887a41273f1096d0",
}
DECIMAL = re.compile(r"\s*[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[Ee][+-]?[0-9]+)?\s*")
LIMIT = Fraction(1, 10**20)
SLOTS = ["uv1", "ir1", "ir2", "finite"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def decode(body):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("nonfinite JSON constant " + value)
    return json.loads(body, object_pairs_hook=pairs, parse_constant=invalid, parse_float=Decimal)


def decimal(value):
    require(type(value) is str and DECIMAL.fullmatch(value), "quoted finite decimal required")
    return Fraction(value)


def tensor(raw):
    require(type(raw) is list and len(raw) == 330, "complete330 moments required")
    result = []
    for row in raw:
        require(type(row) is list and len(row) == 4, "four Laurent slots required")
        for value in row:
            require(type(value) is list and len(value) == 2, "complex pair required")
            result.append(tuple(decimal(part) for part in value))
    require(len(result) == 1320, "complete1320 complex values required")
    return result


def magnitude_squared(value):
    return value[0] * value[0] + value[1] * value[1]


def discrepancy(left, right, unit_squared):
    delta = (left[0] - right[0], left[1] - right[1])
    scale = max(unit_squared, magnitude_squared(right))
    require(scale > 0, "positive dimensional scale required")
    return magnitude_squared(delta) / scale


def displayed_error(squared):
    with localcontext() as context:
        context.prec = 80
        return str((Decimal(squared.numerator) / Decimal(squared.denominator)).sqrt())


def key(record):
    return tuple(record.get(name) for name in ("kind", "grid", "moment", "slot", "other"))


def check_error_record(saved, expected_squared):
    require(saved["squared_error"] == str(expected_squared), "represented squared error differs")
    require(saved["error"] == displayed_error(expected_squared), "80-digit displayed error differs")
    require(saved["limit_squared"] == str(LIMIT), "threshold differs")
    require(saved["passed"] is (expected_squared <= LIMIT), "comparison verdict differs")


def controls():
    count = 0
    def rejects(function, *args):
        nonlocal count
        try:
            function(*args)
        except (ValueError, TypeError, KeyError):
            count += 1
            return
        raise ValueError("independent negative control was accepted")
    for value in (None, 0, True, "NaN", "inf", "1/3", "", "1_0"):
        rejects(decimal, value)
    rejects(decode, '{"a":1,"a":2}')
    rejects(decode, '{"a":NaN}')
    rejects(tensor, [])
    rejects(tensor, [[["0", "0"]] * 3 for _ in range(330)])
    square = Fraction(1, 10**20)
    valid = dict(squared_error=str(square), error=displayed_error(square),
                 limit_squared=str(LIMIT), passed=True)
    check_error_record(valid, square)
    rejects(check_error_record, dict(valid, passed=False), square)
    rejects(check_error_record, dict(valid, squared_error="0"), square)
    rejects(check_error_record, dict(valid, error="0"), square)
    require(discrepancy((Fraction(0), Fraction(1)), (Fraction(0), Fraction(0)), Fraction(1)) == 1,
            "imaginary difference was dropped")
    require(square <= LIMIT and square + Fraction(1, 10**40) > LIMIT, "exact threshold boundary differs")
    return count


def audit(read_bytes):
    seen, cache = {}, {}
    historical = {}
    def read(alias, expected=None):
        require(not alias.startswith("/") and ".." not in Path(alias).parts,
                "only project-relative saved aliases may be read")
        if alias not in cache:
            body = read_bytes(alias)
            require(type(body) is bytes, "read_bytes must return bytes")
            cache[alias] = body
            seen[alias] = dict(sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
        if expected is not None:
            require(seen[alias]["sha256"] == expected, "saved binding drift: " + alias)
        return cache[alias]
    def load(alias, expected=None):
        return decode(read(alias, expected))
    for alias, expected in PINS.items():
        read(alias, expected)
    manifest = load(BASE + "/manifest.json")
    for alias, expected in manifest["bindings"].items():
        if alias.startswith("/"):
            historical[alias] = expected
        else:
            read(alias, expected)
    require(len(manifest["bindings"]) == 39 and len(historical) == 1, "narrow source membership differs")
    catalogue = load(BASE + "/catalog.json")
    receipt = load(CAPTURE + "/receipt.json")
    saved = load(CAPTURE + "/comparison.json")
    require(receipt["comparison_sha256"] == PINS[CAPTURE + "/comparison.json"], "comparison receipt pin differs")
    require(receipt["manifest_sha256"] == PINS[BASE + "/manifest.json"], "source manifest identity differs")
    load(BASE + "/root-authorization.json", receipt["root_grant_sha256"])
    exponents = sorted((a for a in product(range(8), repeat=4) if sum(a) <= 7),
                       key=lambda a: (sum(a), -a[0], -a[1], -a[2]))
    require(len(exponents) == 330 and exponents[273] == (1, 3, 2, 1), "independent basis differs")
    require(catalogue["orders"] == [12, 20, 32] and catalogue["topology_order"] == [4, 2, 3]
            and catalogue["maps"] == ["identity", "reverse"], "finite catalogue changed")
    expected_grids = [(n, order, mapping) for n in (4, 2, 3) for order in (12, 20, 32)
                      for mapping in ("identity", "reverse")]
    require([(g["topology"], g["order"], g["map"]) for g in catalogue["grids"]] == expected_grids,
            "catalogue membership/order differs")
    require(sum(g["points"] for g in catalogue["grids"]) == 88256, "catalogue rows differ")
    identities = {case["id"]: case for case in load(catalogue["independent_reference_review"])["cases"]}
    references, rejected = {}, None
    for n in (2, 3, 4):
        spec = catalogue["references"][str(n)]
        require(spec["eligible"] is (n != 4), "N4 reference became eligible")
        require(identities[spec["id"] + "-quad-IBP-001"]["eligible_for_subsequent_full_array_comparison"]
                is (n != 4), "independent reference admission differs")
        lines = read(spec["stdout"]).decode().splitlines()
        require(lines.count("READY IREGI_REFERENCE_QP_V1") == 1, "quad READY differs")
        witnesses = [decode(line[len("PRECISION "):]) for line in lines if line.startswith("PRECISION ")]
        require(witnesses == [dict(dbl_kind=16, olo_kind=16, storage_bits=128,
                                  binary_digits=113, decimal_digits=33)], "quad precision witness differs")
        result = [decode(line[len("RESULT "):]) for line in lines if line.startswith("RESULT ")]
        require(len(result) == 1 and result[0]["id"] == spec["response_id"]
                and result[0]["stable"] is True and result[0].get("error") is None
                and result[0]["poles"] == SLOTS, "quad response differs")
        values = tensor(result[0]["moments"])
        if n == 4:
            rejected = values
            require(saved["rejected_N4_reference"] == dict(stdout=spec["stdout"],
                sha256=seen[spec["stdout"]]["sha256"], eligible=False,
                scalar_finite=[str(part) for part in values[3]]), "rejected original N4 diagnostic differs")
        else:
            references[n] = values
    require(rejected is not None and rejected[3] == (0, 0), "expected rejected N4 zero not retained")
    records = {}
    for record in saved["records"]:
        identity = key(record)
        require(identity not in records, "duplicate saved comparison record")
        records[identity] = record
    consumed, categories, maxima = set(), Counter(), {}
    def verify(kind, grid, moment, slot, squared, other=None):
        identity = (kind, grid, moment, slot, other)
        require(identity in records and identity not in consumed, "missing/duplicate required comparison")
        check_error_record(records[identity], squared)
        require(squared <= LIMIT, "independent recomputation found a failed comparison")
        consumed.add(identity)
        categories[kind] += 1
        if kind not in maxima or squared > maxima[kind][0]:
            maxima[kind] = (squared, identity)
    arrays, ir_checks, row_total = {}, 0, 0
    grid_summaries, n4_scalars = [], []
    for grid in catalogue["grids"]:
        n, order, mapping = grid["topology"], grid["order"], grid["map"]
        capture_grid = next(item for item in receipt["grids"] if item["id"] == grid["id"])
        alias = CAPTURE + "/grids/" + grid["id"] + "/result.json"
        data = load(alias, capture_grid["result_sha256"])
        require(data["status"] == "one_fixed_complex_order_returned_not_accuracy_qualified"
                and data["topology"] == n and data["order"] == order and data["tensor_rank"] == 7
                and data["moments"] == 330 and data["native_slot_order"] == SLOTS
                and data["basis"] == [list(a) for a in exponents]
                and data["map_permutation"] == grid["permutation"]
                and data["points"] == data["worker_rows"] == order**(n-1) == grid["points"],
                "saved full-grid identity/count differs")
        units = [Fraction(3)**(sum(a)+4-2*n) for a in exponents]
        require([Fraction(value) for value in data["normalization_units_exact"]] == units
                and data["normalization_scale_Q_exact"] == "3", "exact dimensional normalization differs")
        values = tensor(data["native_laurent"])
        normalized = tensor(data["normalized_native_laurent"])
        require(data["minimum_observed_real_F"] >= 1
                and data["maximum_observed_imaginary_F"] <= Fraction(-1, 8)
                and data["minimum_observed_imaginary_F"] >= Fraction(-n, 8), "point domain evidence differs")
        nonzero = [0]*4
        for moment, (alpha, unit) in enumerate(zip(exponents, units)):
            for slot in range(4):
                offset = 4*moment + slot
                if magnitude_squared(values[offset]):
                    nonzero[slot] += 1
                if slot in (1, 2):
                    require(values[offset] == normalized[offset] == (0, 0), "separate IR slot is nonzero")
                    ir_checks += 1
                if n in references:
                    verify("eligible_original_quad", grid["id"], moment, slot,
                           discrepancy(values[offset], references[n][offset], unit*unit))
        if n == 4:
            identity = ("N4_scalar_nonvanishing_lower_bound", grid["id"], 0, 3, None)
            expected = dict(kind=identity[0], grid=grid["id"], moment=0, slot=3,
                native_imaginary=str(values[3][1]), strict_lower_bound="18/21025",
                passed=values[3][1] > Fraction(18, 21025))
            require(identity in records and records[identity] == expected and expected["passed"],
                    "independent N4 scalar nonvanishing check differs")
            consumed.add(identity)
            categories[identity[0]] += 1
            n4_scalars.append(dict(grid=grid["id"], native_finite=data["native_laurent"][0][3]))
        arrays[(n, order, mapping)] = values
        row_total += data["worker_rows"]
        grid_summaries.append(dict(id=grid["id"], sha256=seen[alias]["sha256"],
                                   complex_slots=len(values), represented_nonzero_by_slot=nonzero))
    for n in (2, 3, 4):
        comparisons = [((n, lo, mapping), (n, hi, mapping)) for mapping in ("identity", "reverse")
                       for lo, hi in ((12, 20), (20, 32))]
        comparisons += [((n, order, "identity"), (n, order, "reverse")) for order in (12, 20, 32)]
        for left, right in comparisons:
            for offset, (a, b) in enumerate(zip(arrays[left], arrays[right])):
                moment, slot = divmod(offset, 4)
                unit = Fraction(3)**(sum(exponents[moment])+4-2*n)
                verify("fixed_rule_convergence_indicator", str(left), moment, slot,
                       discrepancy(a, b, unit*unit), str(right))
    require(categories == {"eligible_original_quad":15840, "fixed_rule_convergence_indicator":27720,
                           "N4_scalar_nonvanishing_lower_bound":6}, "complete comparison counts differ")
    require(len(consumed) == len(records) == 43566 and ir_checks == 11880 and row_total == 88256,
            "complete saved record/IR/point coverage differs")
    require(saved["summary"] == dict(complete_grids=18, records=43566, failures=0)
            and saved["failures"] == [] and saved["reference_complex_slots"] == 15840
            and saved["convergence_complex_slots"] == 27720 and saved["separate_IR_zero_checks"] == 11880,
            "saved summary differs from independent reconstruction")
    require(saved["N4_original_reference_admission"] == "REJECTED_analytic_scalar_sector"
            and saved["N4_full_array_independent_accuracy_anchor_available"] is False
            and saved["rigorous_error_bounds"] is False and saved["performance_evidence"] is False,
            "saved scientific scope was widened")
    return dict(status="passed_independent_saved_complex_oracle_numeric_audit", findings=[],
        input_bindings=seen, historical_tool_binding_not_rehashed=historical,
        complete_grids=18, complete_native_complex_slots=23760, point_rows=88256,
        comparison_records=43566, comparison_categories=dict(categories), separate_IR_zero_checks=ir_checks,
        failures=0, maxima={kind:dict(squared_error=str(value[0]), error=displayed_error(value[0]),
            record_identity=list(value[1])) for kind, value in maxima.items()},
        grids=grid_summaries, N4_scalar_finite_values=n4_scalars,
        negative_controls_passed=controls(), producer_imported=False, numerical_libraries_imported=False,
        new_integrals_or_native_jobs=False, binary_or_package_tree_rehash=False,
        N4_original_reference_eligible=False, N4_saved_full_array_quadrature_empirically_checked=True,
        rigorous_error_bound=False, performance_evidence=False,
        limitations=["Exact represented-data comparisons, not a new integral calculation.",
          "Fixed-order/map differences are convergence indicators, not rigorous error bounds.",
          "Binary64 nodes/worker with longdouble accumulation do not certify arbitrary precision.",
          "N2/N3 original quad source-constant caveats persist; N4 original zero remains rejected.",
          "Metadata/process release is separately reviewed; no current PID or executable was read."])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = Path.cwd()
    result = audit(lambda alias: (root/alias).read_bytes())
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps(dict(status=result["status"], records=result["comparison_records"],
                         IR_checks=result["separate_IR_zero_checks"], failures=result["failures"])))
