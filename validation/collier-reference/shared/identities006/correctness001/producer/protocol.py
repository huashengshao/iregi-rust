"""Saved-data admission and independent identities using prepared Symbolica terms."""
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys


ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
PARENT = ROOT/"validation/collier-reference/shared/attempt004"
sys.path.insert(0, str(PARENT/"producer"))
import support
SPEC = importlib.util.spec_from_file_location("existing_n4_identity_tools", ROOT/"validation/collier-reference/n4/check_identities.py")
identity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(identity)
basis = identity.basis_module.tensor_basis


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def polynomial(data, expression):
    return data["polynomials"][expression]["prepared"]


def prepared_constant(data, expression):
    terms = polynomial(data, expression)["terms"]
    if not terms:
        return "0"
    if len(terms) != 1 or terms[0]["exponents"] != [0]*4:
        raise ValueError("Symbolica constant witness is not scalar")
    return support.scalar_text(terms[0]["coefficient"])


def admit(data):
    if (data.get("status") != "prepared-not-numerically-qualified" or data.get("guards_unchanged") is not True
            or data.get("reference_reduction_performed") is not False):
        raise ValueError("complete Symbolica-only guarded preparation required")
    branches = data["branches"]
    if len(branches) != 3 or [b["id"] for b in branches] != [0, 1, 2]:
        raise ValueError("three unchanged ordered branches required")
    keys = [support.proof_key(b["sample"], 5) for b in branches]
    if len(set(keys)) != 3 or any(b["proof_key"] != key for b, key in zip(branches, keys)):
        raise ValueError("branch input/proof identity differs")
    if data["original32_proof_keys"] != [keys[i % 3] for i in range(32)]:
        raise ValueError("original32 lane map differs")
    for b in branches:
        if support.exact_number(b["parent_domain_proof"]["positive_mass_polynomial_lower_bound"]) <= 0:
            raise ValueError("positive Feynman-polynomial domain required")
        for i in range(1, 5):
            zero = polynomial(data, data["aliases"][f"difference-cancellation-{b['id']}-{i}"])
            if zero["terms"]:
                raise ValueError("denominator cancellation witness is nonzero")
        if polynomial(data, data["aliases"][f"trace-cancellation-{b['id']}"])["terms"]:
            raise ValueError("trace cancellation witness is nonzero")
    cases = data["pinched_cases"]+data["routing_cases"]
    expected = {(f"n5-pinch{i}-rank1", 4, 1) for i in range(5)} | {
        ("n5-cyclic-origin1", 5, 2), ("n5-reversed-nonzero", 5, 2)}
    if len(cases) != 7 or {(c["id"], c["n"], c["rank"]) for c in cases} != expected:
        raise ValueError("exact five pinches and two routing witnesses required")
    generated = []
    for case in cases:
        if len(case["samples"]) != 3:
            raise ValueError("one lane per original branch required")
        if case["n"] == 4:
            pinch = int(case["id"][8])
            order = [i for i in range(5) if i != pinch]
        else:
            order = [1, 2, 3, 4, 0] if case["id"] == "n5-cyclic-origin1" else [0, 4, 3, 2, 1]
            if case["denominator_order"] != order:
                raise ValueError("routing denominator order changed")
        for branch, sample in zip(branches, case["samples"]):
            original = branch["sample"]
            origin = original["shifts"][order[0]]
            expected_shifts = [[prepared_constant(data, f"({original['shifts'][i][nu]})-({origin[nu]})")
                                for nu in range(4)] for i in order]
            if (sample["mu"] != original["mu"] or sample["masses"] != [original["masses"][i] for i in order]
                    or sample["shifts"] != expected_shifts):
                raise ValueError("pinch/routing input differs from its exact Symbolica witness")
        policies = [("iregi", mode) for mode in ("Hybrid", "PassarinoVeltman", "Ibp")]
        if case["n"] == 5:
            policies.append(("generic", 1))
        for engine, mode in policies:
            for group in support.scale_groups(case, case["samples"]):
                text = (support.original_iregi_request(case, group["samples"], mode) if engine == "iregi"
                        else support.collier_request(case, group["samples"], mode))
                generated.append({"case": case["id"], "engine": engine, "mode": mode, "scale": group["scale"],
                    "lane_indices": group["lane_indices"], "wire_request": text,
                    "wire_request_sha256": hashlib.sha256(text.encode()).hexdigest()})
    if len(generated) != 46 or data["reference_request_inventory"] != generated:
        raise ValueError("exact46 prepared requests changed, duplicated or omitted")
    return cases


def load_prepared():
    qualification_path = HERE/"prepared001/qualification.json"
    qualification = json.loads(qualification_path.read_text())
    for path, expected in qualification["files"].items():
        if digest(ROOT/path) != expected:
            raise ValueError("durable preparation artifact/source changed")
    info = qualification["preparation"]
    if digest(ROOT/info["path"]) != info["sha256"]:
        raise ValueError("durable preparation changed")
    raw = gzip.decompress((ROOT/info["path"]).read_bytes())
    if hashlib.sha256(raw).hexdigest() != info["uncompressed_sha256"]:
        raise ValueError("preparation payload changed")
    data = json.loads(raw)
    cases = admit(data)
    for path, expected in data["guards"].items():
        if digest(ROOT/path) != expected:
            raise ValueError("preparation source/input/CLI guard changed")
    parent = json.loads(gzip.decompress((PARENT/"capture.json.gz").read_bytes()))
    parent_cases = {c["rank"]: c for c in parent["input_cases"] if c["n"] == 5}
    if set(parent_cases) != {0, 1, 2} or any([support.proof_key(s, 5) for s in c["samples"]]
            != data["original32_proof_keys"] for c in parent_cases.values()):
        raise ValueError("parent rank context/lane proof keys differ")
    for name, info in parent["binaries"].items():
        if digest(ROOT/info["path"]) != info["sha256"]:
            raise ValueError(f"immutable {name} reference binary changed")
    return data, parent, cases


def accepted_moments(response, lane, rank):
    row = response["lanes"][lane]
    if row["status"] != "success" or row.get("moments") is None:
        raise ValueError("native lane rejected; its raw diagnostics cannot qualify an identity")
    if any(row.get(key, 0) != 0 for key in ("last_err_flag", "last_acc_flag", "worst_err_flag", "worst_acc_flag")):
        raise ValueError("native failure flag prevents identity acceptance")
    if response.get("collier_mode") is not None:
        flags = ("last_err_flag", "last_acc_flag", "worst_err_flag", "worst_acc_flag")
        if any(key not in row or type(row[key]) is not int for key in flags):
            raise ValueError("missing native COLLIER flag")
        poles = response.get("pole_check_errors")
        if (not isinstance(poles, list) or len(poles) != len(response["lanes"])
                or len(poles[lane]) != 3 or any(type(x) not in (int, float) or not math.isfinite(x)
                    or x < 0 or x > 1e-12 for x in poles[lane])):
            raise ValueError("native separated-pole probe prevents identity acceptance")
    moments = row["moments"]
    if len(moments) != math.comb(rank+4, 4) or any(len(m) != 4 or any(
            not isinstance(z, list) or len(z) != 2 or any(type(x) not in (int, float) or not math.isfinite(x) for x in z)
            for z in m) for m in moments):
        raise ValueError("incomplete or nonfinite native tensor/Laurent array")
    return moments


def energy(sample):
    wire = support.wire_sample(sample, len(sample["shifts"]))
    return max(1., wire["mu"], *(abs(x) for p in wire["shifts"] for x in p),
               *(math.sqrt(math.hypot(*m)) for m in wire["masses"]))


def compare_identities(data, parent, responses):
    """Use existing N4 numerical contraction of Symbolica-prepared coefficients."""
    parent_rows = {(r["rank"], r["batch_width"]): r for r in parent["rows"] if r["n"] == 5}
    engines = ("iregi-Hybrid", "iregi-PassarinoVeltman", "iregi-Ibp", "generic-1")
    result = {"prefix_rows": [], "branch_identities": [], "routing_rows": [], "finiteness_rows": [], "original_coverage_rows": [
        {key: r[key] for key in ("id", "n", "rank", "batch_width", "status")} for r in parent["rows"]]}
    finite_inputs = [(next(c for c in parent["input_cases"] if c["id"] == row["id"]), engine,
                      row["responses"][engine], row["batch_width"]) for row in parent["rows"] if row["n"] == 5 for engine in engines]
    cases = {c["id"]: c for c in data["pinched_cases"]+data["routing_cases"]}
    finite_inputs += [(cases[case_id], engine, response, 3) for (case_id, engine), response in responses.items()]
    for case, engine, response, width in finite_inputs:
        record = {"case": case["id"], "engine": engine, "batch_width": width, "lanes": []}
        result["finiteness_rows"].append(record)
        for lane, sample in enumerate(case["samples"][:width]):
            checks = []
            try:
                moments = accepted_moments(response, lane, case["rank"])
                for moment, alpha in zip(moments, basis(case["rank"])):
                    checks.append(identity.residual([complex(*z) for z in moment[:3]], [0j]*3,
                        energy(sample)**(4+sum(alpha)-2*case["n"])))
                record["lanes"].append({"lane": lane, "status": "passed" if all(c["status"] == "passed" for c in checks) else "failed", "checks": checks})
            except Exception as error:
                record["lanes"].append({"lane": lane, "status": "unavailable", "reason": str(error)})
    for low, high in ((0, 1), (0, 2), (1, 2)):
        for width in (1, 32):
            for engine in engines:
                record = {"lower_rank": low, "higher_rank": high, "batch_width": width, "engine": engine, "lanes": []}
                result["prefix_rows"].append(record)
                low_response, high_response = parent_rows[(low, width)]["responses"][engine], parent_rows[(high, width)]["responses"][engine]
                high_index = {tuple(alpha): index for index, alpha in enumerate(basis(high))}
                for lane, proof_key in enumerate(data["original32_proof_keys"][:width]):
                    branch = next(b for b in data["branches"] if b["proof_key"] == proof_key)
                    checks = []
                    try:
                        left, right = accepted_moments(low_response, lane, low), accepted_moments(high_response, lane, high)
                        for index, alpha in enumerate(basis(low)):
                            checks.append(identity.residual([complex(*z) for z in left[index]],
                                [complex(*z) for z in right[high_index[tuple(alpha)]]], energy(branch["sample"])**(sum(alpha)-6)))
                        record["lanes"].append({"lane": lane, "proof_key": proof_key, "status": "passed" if all(c["status"] == "passed" for c in checks) else "failed", "checks": checks})
                    except Exception as error:
                        record["lanes"].append({"lane": lane, "proof_key": proof_key, "status": "unavailable", "reason": str(error)})
    for engine in engines:
        for rhs_mode in ("Hybrid", "PassarinoVeltman", "Ibp"):
            for branch in data["branches"]:
                record = {"engine": engine, "pinched_rhs_mode": rhs_mode, "branch": branch["id"], "proof_key": branch["proof_key"], "checks": []}
                result["branch_identities"].append(record)
                try:
                    parent_lane = data["original32_proof_keys"].index(branch["proof_key"])
                    moments = accepted_moments(parent_rows[(2, 32)]["responses"][engine], parent_lane, 2)
                    pinched = {i: accepted_moments(responses[(f"n5-pinch{i}-rank1", "iregi-"+rhs_mode)], branch["id"], 1) for i in range(5)}
                    scalar = lambda values, rank: identity.contract(polynomial(data, "1"), values, rank)
                    e0, d0 = scalar(moments, 2), scalar(pinched[0], 1)
                    for difference in branch["denominator_differences"]:
                        i, f = difference["i"], support.binary64(difference["f"])
                        lhs = identity.contract(polynomial(data, difference["linear_polynomial"]), moments, 2)
                        di = scalar(pinched[i], 1)
                        record["checks"].append({"identity": f"denominator-difference-{i}", **identity.residual(lhs,
                            [di[p]-d0[p]-f*e0[p] for p in range(4)], energy(branch["sample"])**-4)})
                        for nu in range(4):
                            q = f"iregi::q{nu}"
                            alpha = [0]*4
                            alpha[nu] = 1
                            translated = branch["translation_monomials"]["-".join(map(str, alpha))]
                            lhs = identity.contract(polynomial(data, f"({difference['linear_polynomial']})*{q}"), moments, 2)
                            divec = identity.contract(polynomial(data, q), pinched[i], 1)
                            d0vec = identity.contract(polynomial(data, translated), pinched[0], 1)
                            evec = identity.contract(polynomial(data, q), moments, 2)
                            record["checks"].append({"identity": f"denominator-difference-{i}-q{nu}", **identity.residual(lhs,
                                [divec[p]-d0vec[p]-f*evec[p] for p in range(4)], energy(branch["sample"])**-3)})
                    trace = identity.contract(polynomial(data, data["aliases"]["metric-trace-rank2"]), moments, 2)
                    m0 = support.binary64(branch["sample"]["masses"][0][0])
                    record["checks"].append({"identity": "rank2-metric-trace", **identity.residual(trace,
                        [d0[p]+m0*e0[p] for p in range(4)], energy(branch["sample"])**-4)})
                    record["status"] = "passed" if all(c["status"] == "passed" for c in record["checks"]) else "failed"
                except Exception as error:
                    record.update(status="unavailable", reason=str(error))
    for case in data["routing_cases"]:
        for engine in engines:
            record = {"case": case["id"], "engine": engine, "lanes": []}
            result["routing_rows"].append(record)
            for branch in data["branches"]:
                checks = []
                try:
                    routed = accepted_moments(responses[(case["id"], engine)], branch["id"], 2)
                    original_lane = data["original32_proof_keys"].index(branch["proof_key"])
                    target = accepted_moments(parent_rows[(2, 32)]["responses"][engine], original_lane, 2)
                    for index, alpha in enumerate(basis(2)):
                        lhs = (identity.contract(polynomial(data, branch["translation_monomials"]["-".join(map(str, alpha))]), routed, 2)
                               if case["denominator_order"][0] == 1 else [complex(*z) for z in routed[index]])
                        checks.append({"moment": alpha, **identity.residual(lhs, [complex(*z) for z in target[index]],
                            energy(branch["sample"])**(sum(alpha)-6))})
                    record["lanes"].append({"branch": branch["id"], "proof_key": branch["proof_key"],
                        "status": "passed" if all(c["status"] == "passed" for c in checks) else "failed", "checks": checks})
                except Exception as error:
                    record["lanes"].append({"branch": branch["id"], "proof_key": branch["proof_key"], "status": "unavailable", "reason": str(error)})
    statuses = [lane["status"] for row in result["prefix_rows"]+result["routing_rows"]+result["finiteness_rows"] for lane in row["lanes"]]
    statuses += [row["status"] for row in result["branch_identities"]]
    result["status"] = "passed" if all(status == "passed" for status in statuses) else "failed-or-unavailable"
    result["scope"] = "Native-accepted arrays only; no identity overrides a rejected lane; r0/r1/r2 all-slot prefix consistency connects lower ranks to independent rank2 identities"
    return result
