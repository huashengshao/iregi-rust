"""Independent stdlib numeric primitives copied from prior independent audit; no producer module imported."""
from pathlib import Path
from fractions import Fraction
import json,math,re,struct
CHECKS=0

def require(predicate, context="check"):
    global CHECKS
    CHECKS += 1
    if not predicate:
        raise AssertionError(context)

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result

def decode(text):
    def invalid_constant(value):
        raise ValueError("nonstandard JSON constant: " + value)
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_constant)

def read(path):
    return decode(Path(path).read_text())

def array(value, count):
    require(type(value) is list and len(value) == count, ("array length", count))
    return value

def natural(value, expected=None):
    require(type(value) is int and value >= 0, ("natural", value))
    if expected is not None:
        require(value == expected, ("natural value", value, expected))
    return value

def real_metadata(value, domain="f64", finite_field=True, allow_nonfinite=False):
    required = {"rational", "precision", "negative_sign"} | ({"finite"} if finite_field else set())
    require(type(value) is dict and set(value) == required, "number metadata schema")
    precision = natural(value["precision"])
    require(0 < precision <= 2**32 - 1 and type(value["negative_sign"]) is bool)
    if domain in ("f64", "DoubleFloat"):
        require(precision == {"f64": 53, "DoubleFloat": 106}[domain])
    else:
        require(domain == "Float")
    if finite_field:
        require(type(value["finite"]) is bool)
        if not value["finite"]:
            require(allow_nonfinite and value["rational"] is None)
            return None
    require(type(value["rational"]) is str and re.fullmatch(r"-?\d+(?:/[1-9]\d*)?", value["rational"]) is not None)
    rational = Fraction(value["rational"])
    require(rational.denominator & (rational.denominator - 1) == 0)
    if rational:
        require((rational < 0) == value["negative_sign"])
        if domain != "DoubleFloat":
            numerator = abs(rational.numerator)
            odd = numerator >> ((numerator & -numerator).bit_length() - 1)
            require(odd.bit_length() <= precision)
    if domain == "f64":
        native = float(rational)
        require(math.isfinite(native) and Fraction.from_float(native) == rational)
    return rational

def represented(z, domain="f64", finite_field=True, allow_nonfinite=False):
    return tuple(real_metadata(v, domain, finite_field, allow_nonfinite) for v in array(z, 2))

def f64_represented(z, finite_field=True):
    parts = represented(z, "f64", finite_field)
    return tuple(float(q) if q else math.copysign(0., -1. if v["negative_sign"] else 1.) for q, v in zip(parts, z))

def f64_complex(z):
    array(z, 2)
    require(all(type(v) in (int, float) and math.isfinite(v) for v in z), "finite native complex")
    return tuple(z)

def expected_execution(batch, groups, rows):
    return {"input_rows": batch, "argument_rows": batch, "master_family_batches": groups,
            "master_rows": rows, "pentagon_box_rows": 0, "reduction_rows": batch,
            "fallback_rows": 0, "fallback_successes": 0, "analytic_rows": 0}
