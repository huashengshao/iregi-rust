"""Adjudicate complete Cartesian arrays against increasing-precision Float data.

Usage: python3 compare_precision_oracle.py ORACLE.json PRECISION.json OUTPUT.json
Only raw D=4 moments with unit propagator powers and coordinate-derived
invariants are supported. No reduction or Symbolica runtime is executed.
"""

from decimal import Decimal, InvalidOperation, localcontext
import glob
import hashlib
import json
from math import comb
from pathlib import Path
import sys
import tempfile

try:
    import mpmath as mp
except ImportError:
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    candidates = glob.glob(f"/nix/store/*-python{version}-mpmath-*/lib/python{version}/site-packages")
    if not candidates:
        raise SystemExit("Install mpmath in the optional validation environment")
    sys.path.insert(0, candidates[0])
    import mpmath as mp


NORMALIZATION = "OneLoop; UV, IR single, IR double, finite; each slot real,imag strings"
TOLERANCE = Decimal("1e-10")
# This checks consistency of stored binary64 evidence, not numerical agreement.
EVIDENCE_ROUNDING = Decimal("1e-14")


class ArtifactError(ValueError):
    """An artifact cannot establish the claimed comparison."""


def require(condition, message):
    if not condition:
        raise ArtifactError(message)


def object_value(value, label):
    require(type(value) is dict, f"{label} must be an object")
    return value


def array(value, length, label):
    require(type(value) is list and len(value) == length,
            f"{label} must contain exactly {length} entries")
    return value


def integer(value, label, minimum=0):
    require(type(value) is int and value >= minimum, f"{label} must be an integer >= {minimum}")
    return value


def number(value, label, string_only=False):
    allowed = (str,) if string_only else (str, int, float, Decimal)
    require(type(value) in allowed, f"{label} must be a {'decimal string' if string_only else 'number'}")
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ArtifactError(f"{label} is not a decimal number") from error
    require(result.is_finite(), f"{label} must be finite")
    return result


def slots(value, label, string_only=False):
    return [[number(v, f"{label}[{i}][{j}]", string_only)
             for j, v in enumerate(array(pair, 2, f"{label}[{i}]"))]
            for i, pair in enumerate(array(value, 4, label))]


def tensor_basis(rank):
    # Index enumeration only, matching src/basis.rs; no polynomial algebra.
    return [[t, x, y, degree-t-x-y]
            for degree in range(rank+1)
            for t in range(degree, -1, -1)
            for x in range(degree-t, -1, -1)
            for y in range(degree-t-x, -1, -1)]


def check_monomial(value, expected, label):
    array(value, 4, label)
    require(all(type(v) is int and v >= 0 for v in value) and value == expected,
            f"{label} does not match the canonical tensor index")


def ordinary_domain(data, label):
    require(integer(data.get("dimension_shift", 0), f"{label}.dimension_shift") == 0,
            f"{label}: only dimension_shift=0 is supported")
    require("scalar_products" not in data, f"{label}: supplied scalar products are unsupported")
    require(data.get("tensor_weights", "raw") in ("raw", "Raw"),
            f"{label}: only raw tensor weights are supported")


def validate_fixture(oracle, precision):
    object_value(oracle, "oracle")
    object_value(precision, "precision")
    ordinary_domain(oracle, "oracle")
    rank = integer(oracle.get("rank"), "oracle.rank")
    n = integer(oracle.get("propagators"), "oracle.propagators", 1)
    count = comb(rank+4, 4)
    require(integer(oracle.get("moments"), "oracle.moments", 1) == count,
            "oracle moment count is inconsistent with its rank")
    require(oracle.get("status") in ("passed", "failed", "reference_only"),
            "oracle run is incomplete or has no numerical result")
    if oracle["status"] == "reference_only":
        require("rust_original_master_moments_normalized" not in oracle
                and oracle.get("discrepancies") == [],
                "reference_only artifacts must not contain Rust arrays or retained discrepancies")
        require(oracle.get("reference_stable") is True,
                "reference_only artifacts must explicitly declare reference_stable=true")
    shifts = [[number(v, f"oracle.shifts[{i}][{j}]")
               for j, v in enumerate(array(p, 4, f"oracle.shifts[{i}]"))]
              for i, p in enumerate(array(oracle.get("shifts"), n, "oracle.shifts"))]
    masses = [number(v, f"oracle.mass_squared[{i}]")
              for i, v in enumerate(array(oracle.get("mass_squared"), n, "oracle.mass_squared"))]
    mu = number(oracle.get("mu"), "oracle.mu")
    require(mu > 0, "oracle.mu must be positive")
    if "powers" in oracle:
        require(all(type(v) is int and v == 1 for v in array(oracle["powers"], n, "oracle.powers")),
                "oracle: only unit powers are supported")
    require(oracle.get("propagator_powers", "unit") == "unit", "oracle: only unit powers are supported")
    require(precision.get("normalization") == NORMALIZATION, "precision normalization is missing or incompatible")
    require(type(precision.get("dimension_shift")) is int and precision["dimension_shift"] == 0,
            "precision must declare dimension_shift=0")
    require(precision.get("propagator_powers") == "unit", "precision must declare unit propagator powers")
    embedding_bits = integer(precision.get("input_decimal_embedding_bits"), "precision.input_decimal_embedding_bits", 1)
    snapshot = object_value(precision.get("input_snapshot"), "precision.input_snapshot")
    ordinary_domain(snapshot, "precision.input_snapshot")
    require(integer(snapshot.get("rank"), "snapshot.rank") == rank, "snapshot rank does not match oracle")
    require(number(snapshot.get("mu"), "snapshot.mu") == mu, "snapshot scale does not match oracle")
    for i, p in enumerate(array(snapshot.get("propagators"), n, "snapshot.propagators")):
        object_value(p, f"snapshot.propagators[{i}]")
        require(integer(p.get("power", 1), f"snapshot.propagators[{i}].power", 1) == 1,
                "snapshot contains a nonunit propagator power")
        actual_shift = [number(v, f"snapshot.shift[{i}][{j}]")
                        for j, v in enumerate(array(p.get("shift"), 4, f"snapshot.shift[{i}]"))]
        mass = array(p.get("mass_squared"), 2, f"snapshot.mass_squared[{i}]")
        require(actual_shift == shifts[i], f"snapshot shift {i} does not match oracle")
        require(number(mass[0], f"snapshot.mass_squared[{i}].real") == masses[i]
                and number(mass[1], f"snapshot.mass_squared[{i}].imaginary") == 0,
                f"snapshot mass {i} does not match the real-mass oracle")
    return rank, n, count, shifts, masses, embedding_bits


def native_slots(values, pi, a, b):
    """The D=4 raw OneLoop -> IREGI map in src/convention.rs."""
    transformed = [values[0], [values[1][c]-a*values[2][c] for c in range(2)], values[2],
                   [values[3][c]-a*(values[0][c]+values[1][c])
                    +(a*a/2-b)*values[2][c] for c in range(2)]]
    return [[-v[1]*pi*pi, v[0]*pi*pi] for v in transformed]


def validate_precision_rows(precision, basis):
    results = precision.get("results")
    require(type(results) is list and len(results) >= 2, "at least two precision levels are required")
    seen_bits, validated = set(), []
    for result in results:
        object_value(result, "precision result")
        bits = integer(result.get("bits"), "precision bits", 1)
        require(bits not in seen_bits, "precision levels must be distinct")
        seen_bits.add(bits)
        moments = array(result.get("moments"), len(basis), f"precision {bits} moments")
        indexed = {}
        for row in moments:
            object_value(row, "precision moment")
            index = integer(row.get("index"), "precision moment index")
            require(index < len(basis) and index not in indexed, "precision moment indices must be unique and in range")
            check_monomial(row.get("monomial"), basis[index], f"precision moment {index} monomial")
            indexed[index] = slots(row.get("oneloop_native_slots"), f"precision moment {index} slots", True)
        require(set(indexed) == set(range(len(basis))), "precision moment array is incomplete")
        validated.append((bits, indexed))
    return sorted(validated)


def mixed_error(actual, expected):
    return abs(actual-expected)/(1+abs(expected))


def compare(oracle, precision):
    rank, n, count, shifts, masses, embedding_bits = validate_fixture(oracle, precision)
    # Check lengths before constructing the rank enumeration, including absurd
    # or corrupted rank fields which would otherwise allocate a huge basis.
    results = precision.get("results")
    require(type(results) is list and len(results) >= 2, "at least two precision levels are required")
    for row in results:
        object_value(row, "precision result")
        array(row.get("moments"), count, "precision moments")
    basis = tensor_basis(rank)
    ordered = validate_precision_rows(precision, basis)
    (low_bits, lower), (high_bits, truth) = ordered[-2:]
    reference = object_value(oracle.get("reference"), "oracle.reference")
    require(reference.get("stable") is True, "reference must explicitly report stable=true")
    reference_values = [slots(row, f"reference moment {i}")
                        for i, row in enumerate(array(reference.get("moments"), count, "reference moments"))]
    rust_complete = "rust_original_master_moments_normalized" in oracle
    rust_values = None
    if rust_complete:
        rust_values = [slots(row, f"Rust moment {i}", True)
                       for i, row in enumerate(array(oracle["rust_original_master_moments_normalized"], count, "Rust moments"))]
    discrepancies = oracle.get("discrepancies")
    require(type(discrepancies) is list, "oracle.discrepancies must be an array")
    seen, retained_input = set(), []
    for row in discrepancies:
        object_value(row, "retained discrepancy")
        index = integer(row.get("moment"), "retained moment")
        slot = integer(row.get("slot"), "retained slot")
        component = integer(row.get("component"), "retained component")
        require(index < count and slot < 4 and component < 2, "retained discrepancy index is out of range")
        key = (index, slot, component)
        require(key not in seen, "duplicate retained discrepancy")
        seen.add(key)
        check_monomial(row.get("monomial"), basis[index], "retained monomial")
        actual = number(row.get("actual_normalized"), "retained actual", True)
        expected = number(row.get("expected_normalized"), "retained expected", True)
        number(row.get("mixed_error"), "retained mixed error", True)
        retained_input.append((key, actual, expected))
    working_digits = max(100, high_bits//3+64)
    with mp.workdps(working_digits), localcontext() as context:
        context.prec = working_digits
        pi = Decimal(str(mp.pi))
        a = Decimal(str(mp.euler + mp.log(mp.pi)))
        b = pi*pi/12
        q2 = max(Decimal(1), *(abs(m) for m in masses))
        for p in shifts:
            for q in shifts:
                d = [x-y for x, y in zip(p, q)]
                q2 = max(q2, abs(d[0]**2-sum(v*v for v in d[1:])))
        q = q2.sqrt()
        units = [q**(sum(monomial)+4-2*n) for monomial in basis]
        high_values = {i: native_slots(values, pi, a, b) for i, values in truth.items()}
        convergence, reference_failures, rust_failures = [], [], []
        maximum_convergence = maximum_reference = maximum_rust = Decimal(0)
        for index in range(count):
            lower_values = native_slots(lower[index], pi, a, b)
            for slot in range(4):
                for component in range(2):
                    value = high_values[index][slot][component]/units[index]
                    previous = lower_values[slot][component]/units[index]
                    original = reference_values[index][slot][component]/units[index]
                    error, reference_error = mixed_error(previous, value), mixed_error(original, value)
                    maximum_convergence = max(maximum_convergence, error)
                    maximum_reference = max(maximum_reference, reference_error)
                    common = {"moment": index, "monomial": basis[index], "slot": slot,
                              "component": component, "truth_normalized": str(value)}
                    if error >= TOLERANCE:
                        convergence.append(common | {"mixed_error": str(error)})
                    if reference_error >= TOLERANCE:
                        reference_failures.append(common | {"reference_normalized": str(original), "mixed_error": str(reference_error)})
                    if rust_complete:
                        rust_value = rust_values[index][slot][component]
                        error = mixed_error(rust_value, value)
                        maximum_rust = max(maximum_rust, error)
                        if error >= TOLERANCE:
                            rust_failures.append(common | {"rust_normalized": str(rust_value), "mixed_error": str(error)})
        retained = []
        for (index, slot, component), actual, expected in retained_input:
            original = reference_values[index][slot][component]/units[index]
            require(mixed_error(expected, original) <= EVIDENCE_ROUNDING,
                    f"retained reference value disagrees with full reference at {(index, slot, component)}")
            if rust_complete:
                require(mixed_error(actual, rust_values[index][slot][component]) <= EVIDENCE_ROUNDING,
                        f"retained Rust value disagrees with full Rust array at {(index, slot, component)}")
            value = high_values[index][slot][component]/units[index]
            rust_error = mixed_error(actual, value)
            row = {"moment": index, "monomial": basis[index], "slot": slot, "component": component,
                   "actual_normalized": str(actual), "expected_normalized": str(expected),
                   "mixed_error": str(mixed_error(actual, expected)), "truth_normalized": str(value),
                   "rust_error_against_truth": str(rust_error),
                   "reference_error_against_truth": str(mixed_error(expected, value))}
            retained.append(row)
            if not rust_complete:
                maximum_rust = max(maximum_rust, rust_error)
                if rust_error >= TOLERANCE:
                    rust_failures.append({"moment": index, "monomial": basis[index], "slot": slot,
                                          "component": component, "truth_normalized": str(value),
                                          "rust_normalized": str(actual), "mixed_error": str(rust_error)})
        converged = not convergence
        return {
            "status": "qualified" if converged else "precision_not_converged",
            "oracle_source_status": oracle["status"],
            "reference_only": oracle["status"] == "reference_only",
            "qualified_oracle": converged, "fixture_verified": True,
            "precision_bits": [low_bits, high_bits], "all_precision_bits": [bits for bits, _ in ordered],
            "input_decimal_embedding_bits": embedding_bits, "comparison_decimal_digits": working_digits,
            "moments": count, "complete_array": True, "coefficients_compared_per_array": count*8,
            "normalization": "native IREGI D=4 raw unit-power moments; componentwise mixed error after dimensional normalization",
            "kinematic_scale_squared": str(q2), "tolerance": str(TOLERANCE),
            "max_precision_convergence_error": str(maximum_convergence),
            "precision_convergence_failures": convergence, "precision_convergence_passed": converged,
            "reference_reported_stable": reference["stable"],
            "reference_agreement_passed": converged and reference["stable"] and not reference_failures,
            "max_reference_error": str(maximum_reference), "reference_discrepancies": reference_failures,
            "rust_complete_array": rust_complete,
            "rust_coefficients_compared": count*8 if rust_complete else len(retained),
            "rust_agreement_passed": (converged and not rust_failures) if rust_complete else (False if rust_failures else None),
            "max_rust_error": str(maximum_rust) if rust_complete or retained else None,
            "rust_discrepancies": rust_failures, "retained_binary64_disagreements": retained,
            "qualification": "The full input fixture and every canonical tensor component are checked. Precision convergence is an internal consistency check, not an independent parameter integral or a performance benchmark. Rust agreement is qualified only when its complete binary64 array is supplied; otherwise only retained discrepancies are adjudicated. The original 1e-10 gate is unchanged.",
        }


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(data):
    def reject_constant(value):
        raise ArtifactError(f"nonfinite JSON constant: {value}")
    return json.loads(data, parse_float=Decimal, parse_constant=reject_constant,
                      object_pairs_hook=reject_duplicate_keys)


def write_report(path, report):
    # Atomic replacement prevents a reader from observing a partially written
    # success report. The initial nonpassing report invalidates old successes.
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False) as file:
        temporary = Path(file.name)
        try:
            json.dump(report, file, indent=2, allow_nan=False)
            file.write("\n")
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    temporary.replace(path)


def main(arguments=None):
    arguments = sys.argv[1:] if arguments is None else arguments
    if len(arguments) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    oracle_path, precision_path, output_path = map(Path, arguments)
    source_paths = [oracle_path, precision_path, Path(__file__)]
    if output_path.resolve() in {p.resolve() for p in source_paths}:
        print("Output must not overwrite an input or the comparator source", file=sys.stderr)
        return 2
    invalid = {"status": "incomplete", "qualified_oracle": False,
               "precision_convergence_passed": False, "complete_array": False,
               "rust_complete_array": False, "sources": {}}
    write_report(output_path, invalid)
    try:
        source_bytes = {str(path): path.read_bytes() for path in source_paths}
        sources = {path: hashlib.sha256(data).hexdigest() for path, data in source_bytes.items()}
        invalid["sources"] = sources
        report = compare(read_json(source_bytes[str(oracle_path)]), read_json(source_bytes[str(precision_path)]))
        report["sources"] = sources
        write_report(output_path, report)
    except (ArtifactError, ValueError, TypeError, KeyError, IndexError, ArithmeticError, OSError) as error:
        invalid.update(status="invalid", error=str(error))
        write_report(output_path, invalid)
        print(f"Invalid comparison artifacts: {error}", file=sys.stderr)
        return 2
    print(f"moments={report['moments']} convergence={report['precision_convergence_passed']} "
          f"max_reference_error={report['max_reference_error']} "
          f"reference_failures={len(report['reference_discrepancies'])} "
          f"rust_complete={report['rust_complete_array']}")
    return 0 if report["qualified_oracle"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
