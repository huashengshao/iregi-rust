"""Exact input transport for the optional ordinary N2..N7 reference slice.

This is reference tooling: it performs no polynomial or matrix algebra.
Symbolica-prepared scalar constants certify the admitted finite-mass domain.
"""
from fractions import Fraction
import importlib.util
import json
import math
from pathlib import Path


ROOT = Path.cwd()
SPEC = importlib.util.spec_from_file_location("unchanged_collier_comparison", ROOT / "validation/collier-reference/run.py")
common = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(common)
kernel = common.kernel


def exact_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError("integer, binary64 value, or exact rational string required")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("finite scalar required")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError, OverflowError) as error:
        raise ValueError("finite exact rational required") from error


def scalar_text(value):
    value = exact_number(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def binary64(value):
    rational = exact_number(value)
    try:
        converted = float(rational)
    except OverflowError as error:
        raise ValueError("reference binary64 input overflow") from error
    if not math.isfinite(converted) or Fraction.from_float(converted) != rational:
        raise ValueError("input is not exactly representable in the binary64 reference")
    return converted


def invariant_pairs(n):
    """Index enumeration from the COLLIER manual, without invariant algebra."""
    if type(n) is not int or not 2 <= n <= 7:
        raise ValueError("N2..N7 required")
    return [(start, (start+distance) % n)
            for distance in range(1, n//2+1)
            for start in range(n//2 if 2*distance == n else n)]


def exact_sample(sample, n):
    if set(sample).difference({"shifts", "masses", "mu", "id"}):
        raise ValueError("unsupported sample fields, including powers/dimension shifts")
    if len(sample["shifts"]) != n or len(sample["masses"]) != n:
        raise ValueError("propagator count mismatch")
    if any(len(p) != 4 for p in sample["shifts"]) or any(len(m) != 2 for m in sample["masses"]):
        raise ValueError("four shift components and complex squared mass pairs required")
    shifts = [[scalar_text(x) for x in p] for p in sample["shifts"]]
    masses = [[scalar_text(x) for x in m] for m in sample["masses"]]
    if any(exact_number(x) != 0 for x in shifts[0]):
        raise ValueError("zero-origin routing required")
    if any(exact_number(m[0]) <= 0 or exact_number(m[1]) != 0 for m in masses):
        raise ValueError("this initial shared slice requires positive real squared masses")
    mu = scalar_text(sample["mu"])
    if exact_number(mu) <= 0:
        raise ValueError("positive scale required")
    result = {"shifts": shifts, "masses": masses, "mu": mu}
    if "id" in sample:
        result["id"] = sample["id"]
    # Reject all precision loss at the optional binary64 boundary.
    for row in shifts + masses:
        for x in row:
            binary64(x)
    scale = binary64(mu)
    if not math.isfinite(scale*scale) or scale*scale == 0:
        raise ValueError("positive representable squared scale required")
    return result


def wire_sample(sample, n):
    exact = exact_sample(sample, n)
    return {"shifts": [[binary64(x) for x in p] for p in exact["shifts"]],
            "masses": [[binary64(x) for x in m] for m in exact["masses"]],
            "mu": binary64(exact["mu"])}


def proof_key(sample, n):
    exact = exact_sample(sample, n)
    exact.pop("id", None)
    return json.dumps(exact, sort_keys=True, separators=(",", ":"))


def original_iregi_request(case, samples, mode):
    """Reuse the frozen original-IREGI N<=7/rank<=7 tensor interface."""
    validate_interface(case)
    return kernel.fortran_request(case, [wire_sample(s, case["n"]) for s in samples], mode, 0, 1)


def collier_request(case, samples, mode, *, check=True):
    validate_interface(case)
    if mode not in (1, 2):
        raise ValueError("publish COLI1 and DD2 as separate reference policies")
    return common.collier_request(case, [wire_sample(s, case["n"]) for s in samples], mode, 0, 1, check=check)


def scale_groups(case, samples):
    """Partition only wire transport; retain exact samples and original order."""
    validate_interface(case)
    groups = {}
    for lane, sample in enumerate(samples):
        exact = exact_sample(sample, case["n"])
        scale = exact["mu"]
        group = groups.setdefault(scale, {"scale": scale, "lane_indices": [], "samples": []})
        group["lane_indices"].append(lane)
        group["samples"].append(sample)
    if not groups:
        raise ValueError("nonempty reference sample list required")
    return list(groups.values())


def assemble_groups(case, samples, groups, responses):
    """Gather validated complete group responses; never fabricate missing lanes."""
    if len(groups) != len(responses) or not responses:
        raise ValueError("one complete response per scale group required")
    lanes, poles, seen = [None] * len(samples), [None] * len(samples), set()
    header_keys = ("interface", "direct_tensor_threshold", "collier_mode", "initialization_rank_capacity")
    first = responses[0]
    has_poles = first.get("pole_check_errors") is not None
    for group, response in zip(groups, responses):
        kernel.validate_response(response, case)
        indices = group["lane_indices"]
        if len(response.get("lanes", [])) != len(indices):
            raise ValueError("scale-group lane count differs from unchanged input")
        if any(response.get(key) != first.get(key) for key in header_keys):
            raise ValueError("scale-group engine policy or initialization changed")
        if (response.get("pole_check_errors") is not None) != has_poles:
            raise ValueError("inconsistent scale-group pole evidence")
        if has_poles and len(response["pole_check_errors"]) != len(indices):
            raise ValueError("scale-group pole count differs from lanes")
        for local, lane in enumerate(indices):
            if type(lane) is not int or not 0 <= lane < len(samples) or lane in seen:
                raise ValueError("duplicate or invalid original lane index")
            if (samples[lane] != group["samples"][local]
                    or scalar_text(samples[lane]["mu"]) != group["scale"]):
                raise ValueError("scale grouping changed input or scale")
            seen.add(lane)
            lanes[lane] = response["lanes"][local]
            if has_poles:
                poles[lane] = response["pole_check_errors"][local]
    if seen != set(range(len(samples))):
        raise ValueError("missing original sample lane")
    result = {key: first[key] for key in header_keys if key in first}
    result.update(id=case["id"], stable=all(r["stable"] for r in responses), lanes=lanes,
                  total_ns=[sum(r["total_ns"][0] for r in responses)],
                  pole_check_errors=poles if has_poles else None,
                  transport="exact-scale groups; original-order gather", performance_evidence=False)
    return result


def initialization_capacity(n, rank):
    return max(rank, n - max(n - 2, 4)) if n >= 5 else rank


def expected_collier_interface(n):
    if type(n) is not int or not 2 <= n <= 7:
        raise ValueError("N2..N7 required")
    return {2: "Bten_cll", 3: "Cten_cll", 4: "Dten_cll"}.get(n, "TNten_cll")


def validate_collier_header(response, case, mode, *, capacity=True):
    if (response.get("interface") != expected_collier_interface(case["n"])
            or response.get("direct_tensor_threshold") != 6 or response.get("collier_mode") != mode):
        raise ValueError("response used a different COLLIER interface or policy")
    if capacity and response.get("initialization_rank_capacity") != initialization_capacity(case["n"], case["rank"]):
        raise ValueError("response used a different initialization capacity")


def validate_interface(case):
    if (type(case["n"]) is not int or not 2 <= case["n"] <= 7
            or type(case["rank"]) is not int or not 0 <= case["rank"] <= 7):
        raise ValueError("shared reference tensor interface supports N2..7/ranks0..7")
    shift = case.get("dimension_shift", 0)
    powers = case.get("powers", [1]*case["n"])
    if (type(shift) is not int or shift != 0 or not isinstance(powers, list)
            or len(powers) != case["n"] or any(type(p) is not int or p != 1 for p in powers)):
        raise ValueError("shared comparison requires ordinary undotted D=4-2epsilon tensors")


def load_document(path):
    data = json.loads(Path(path).read_text())
    if (data.get("status") != "prepared-not-numerically-qualified" or not data.get("cases")
            or data.get("guards_unchanged") is not True):
        raise ValueError("Symbolica-prepared nonempty shared-slice input document required")
    cases = data["cases"]
    if len({c["id"] for c in cases}) != len(cases):
        raise ValueError("duplicate case identifier")
    for case in cases:
        validate_interface(case)
        if type(case["n"]) is not int or not 2 <= case["n"] <= 7 or type(case["rank"]) is not int or not 0 <= case["rank"] <= 3:
            raise ValueError("first shared slice is N2..7 ranks0..3, higher-N ranks0..2 only")
        if case["n"] >= 5 and case["rank"] > 2:
            raise ValueError("higher-point first qualification is restricted to ranks0/1/2")
        if case.get("dimension_shift", 0) != 0 or case.get("powers", [1]*case["n"]) != [1]*case["n"]:
            raise ValueError("ordinary undotted, unshifted dimension required")
        if len(case["samples"]) != 32:
            raise ValueError("this fixed source-defined family requires32 explicitly labelled sample lanes")
        for sample in case["samples"]:
            key = proof_key(sample, case["n"])
            proof = data["sample_domain_proofs"].get(key)
            if (not proof or proof.get("algebra_provider") != "Symbolica via existing iregi-rust prepare CLI"
                    or exact_number(proof["positive_mass_polynomial_lower_bound"]) <= 0
                    or proof.get("invariant_pairs") != [list(pair) for pair in invariant_pairs(case["n"])]
                    or len(proof.get("exact_invariants", [])) != case["n"]*(case["n"]-1)//2):
                raise ValueError("missing positive exact Symbolica-prepared Feynman-polynomial bound")
    fixed = []
    for source in (ROOT / "validation/benchmark/baseline-6b24c03-licensed/results-inputs.json",
                   ROOT / "validation/collier-reference/extensions/n4-inputs.json"):
        fixed.extend((c["id"], c["n"], c["rank"]) for c in json.loads(source.read_text()))
    expected = set(fixed) | {(f"n{n}-r{rank}-conditioned-cycle32", n, rank)
                             for n in (5, 6, 7) for rank in (0, 1, 2)}
    if {(c["id"], c["n"], c["rank"]) for c in cases} != expected or len(cases) != 17:
        raise ValueError("fixed17-family matrix cannot omit or replace a case")
    return data
