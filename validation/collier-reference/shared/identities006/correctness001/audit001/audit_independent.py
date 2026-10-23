"""Replay only saved N5 evidence; never execute a CLI, reference, or build.

This checker deliberately imports neither the producer comparator nor its
contraction/residual helpers. Symbolica's saved coefficient tables supply all
polynomials and translations. The operations below are numerical dot products,
wire parsing, index enumeration, and evidence integrity checks.
"""
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import tarfile
import time


ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "correctness001/audit-independent.json"
ENGINES = ("iregi-Hybrid", "iregi-PassarinoVeltman", "iregi-Ibp", "generic-1")
MODES = ("Hybrid", "PassarinoVeltman", "Ibp")
TOLERANCE = 1e-10
COUNTS = Counter()
REPLAY = {}
BINDINGS = {}


def require(condition, message):
    COUNTS["assertions"] += 1
    if not condition:
        raise ValueError(message)


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def bound_file(path, expected):
    path = Path(path)
    require(path.is_relative_to(ROOT), "evidence path outside project")
    actual = file_hash(path)
    require(actual == expected, f"changed evidence: {path.relative_to(ROOT)}")
    BINDINGS[str(path.relative_to(ROOT))] = actual
    return path.read_bytes()


def document(path, expected=None):
    path = Path(path)
    blob = bound_file(path, expected) if expected else path.read_bytes()
    BINDINGS[str(path.relative_to(ROOT))] = sha(blob)
    return json.loads(blob)


def payload(info):
    packed = bound_file(ROOT / info["path"], info["sha256"])
    raw = gzip.decompress(packed)
    require(sha(raw) == info["uncompressed_sha256"], "uncompressed payload hash differs")
    if "uncompressed_bytes" in info:
        require(len(raw) == info["uncompressed_bytes"], "uncompressed size differs")
    return json.loads(raw)


def archive(info, key="members"):
    packed = bound_file(ROOT / info["path"], info["sha256"])
    raw = gzip.decompress(packed)
    require(sha(raw) == info["uncompressed_sha256"], "archive payload hash differs")
    contents = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as stream:
        for member in stream.getmembers():
            require(member.isfile() and member.name not in contents, "duplicate/nonfile archive member")
            require(not Path(member.name).is_absolute() and ".." not in Path(member.name).parts,
                    "unsafe archive path")
            blob = stream.extractfile(member).read()
            require(not blob.startswith((b"\x7fELF", b"!<arch>\n")), "compiled asset in text evidence")
            require(sha(blob) == info[key].get(member.name), "archive member hash differs")
            contents[member.name] = blob
            COUNTS["archive_members"] += 1
    require(set(contents) == set(info[key]), "archive inventory differs")
    return contents


def files(info):
    for path, expected in info.items():
        bound_file(ROOT / path, expected)


def rational(value):
    require(type(value) in (str, int, float), "invalid numeric scalar")
    return Fraction(value)


def number(value):
    exact = rational(value)
    result = float(exact)
    require(math.isfinite(result) and Fraction.from_float(result) == exact,
            "reference boundary loses scalar input precision")
    return result


def scalar_text(value):
    return str(rational(value))


def proof_key(sample):
    obj = {"mu": scalar_text(sample["mu"]),
           "shifts": [[scalar_text(x) for x in row] for row in sample["shifts"]],
           "masses": [[scalar_text(x) for x in row] for row in sample["masses"]]}
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def energy(sample):
    return max(1., number(sample["mu"]),
               *(abs(number(x)) for row in sample["shifts"] for x in row),
               *(math.sqrt(math.hypot(*(number(x) for x in row))) for row in sample["masses"]))


def indices(rank):
    # Cartesian multiset enumeration only; this is not polynomial manipulation.
    result = []
    for degree in range(rank + 1):
        for t in reversed(range(degree + 1)):
            for x in reversed(range(degree - t + 1)):
                for y in reversed(range(degree - t - x + 1)):
                    result.append((t, x, y, degree - t - x - y))
    require(len(result) == math.comb(rank + 4, 4), "tensor index count differs")
    return result


def terms(prepared, expression):
    result = prepared["polynomials"][expression]["prepared"]["terms"]
    seen = set()
    for term in result:
        alpha = term["exponents"]
        require(len(alpha) == 4 and all(type(x) is int and x >= 0 for x in alpha),
                "invalid Symbolica-prepared tensor exponent")
        require(tuple(alpha) not in seen, "duplicate Symbolica-prepared monomial")
        seen.add(tuple(alpha))
        require(type(term["coefficient"]) is str and math.isfinite(float(Fraction(term["coefficient"]))),
                "non-rational/nonfinite Symbolica coefficient")
    return result


def poly(prepared, alias):
    return prepared["aliases"][alias]


def constant(prepared, expression):
    rows = terms(prepared, expression)
    require(not rows or len(rows) == 1 and rows[0]["exponents"] == [0] * 4,
            "prepared scalar witness is not constant")
    return Fraction(rows[0]["coefficient"]) if rows else Fraction(0)


def dot(prepared, expression, moments, rank):
    index = {alpha: i for i, alpha in enumerate(indices(rank))}
    products = [[] for _ in range(4)]
    for term in terms(prepared, expression):
        alpha = tuple(term["exponents"])
        require(alpha in index, "prepared polynomial exceeds native rank")
        c = float(Fraction(term["coefficient"]))
        for pole, pair in enumerate(moments[index[alpha]]):
            products[pole].append(c * complex(*pair))
    # Separately accumulated real/imaginary parts differ from producer's naive
    # complex += loop. These are numerical coefficient/tensor dot products.
    return [complex(math.fsum(z.real for z in row), math.fsum(z.imag for z in row))
            for row in products]


def add(*vectors):
    return [complex(math.fsum(v[p].real for v in vectors), math.fsum(v[p].imag for v in vectors))
            for p in range(4)]


def times(factor, vector):
    return [factor * z for z in vector]


def native(response, rank, lanes, collier):
    require(response["stable"] is True and len(response["lanes"]) == lanes,
            "native response unstable/incomplete")
    if collier:
        require(response["collier_mode"] == 1 and response["interface"] == "TNten_cll"
                and response["direct_tensor_threshold"] == 6
                and response["initialization_rank_capacity"] == max(rank, 1),
                "N5 COLLIER policy/interface/capacity differs")
        require(len(response["pole_check_errors"]) == lanes, "COLLIER pole probe missing lanes")
    for lane, row in enumerate(response["lanes"]):
        require(row["status"] == "success", "rejected native lane cannot qualify")
        if collier:
            for key in ("last_err_flag", "last_acc_flag", "worst_err_flag", "worst_acc_flag"):
                require(type(row[key]) is int and row[key] == 0, "COLLIER native flag rejects lane")
            probes = response["pole_check_errors"][lane]
            require(len(probes) == 3 and all(type(x) in (float, int) and math.isfinite(x)
                    and 0 <= x <= 1e-12 for x in probes), "separated-pole native gate rejects lane")
            COUNTS["native_pole_probe_slots"] += 3
        else:
            require(all(row.get(k, 0) == 0 for k in ("last_err_flag", "last_acc_flag", "worst_err_flag", "worst_acc_flag")),
                    "unexpected native failure flag")
        require(len(row["moments"]) == math.comb(rank + 4, 4), "missing native tensor moment")
        for moment in row["moments"]:
            require(len(moment) == 4, "missing native Laurent slot")
            for pair in moment:
                require(type(pair) is list and len(pair) == 2
                        and all(type(x) in (int, float) and math.isfinite(x) for x in pair),
                        "nonfinite/incomplete native complex coefficient")
                COUNTS["native_complex_pairs_admitted_in_unique_responses"] += 1
        COUNTS["native_lanes_admitted_in_unique_responses"] += 1


def vectors(moments, rank, alpha):
    return [complex(*z) for z in moments[indices(rank).index(tuple(alpha))]]


def residual(category, lhs, rhs, unit, stored):
    require(unit > 0 and math.isfinite(unit), "invalid dimensional normalization")
    require(len(lhs) == len(rhs) == len(stored["slots"]), "residual Laurent width differs")
    require(stored["status"] == "passed" and stored["tolerance"] == TOLERANCE
            and stored["absolute_unit"] == unit, "stored status/unit/tolerance differs")
    statistics = REPLAY.setdefault(category, {"residual_records": 0, "complex_slot_comparisons": 0,
        "maximum_normalized_error": 0., "maximum_saved_value_difference": 0.})
    errors = []
    for pole, (left, right, recorded) in enumerate(zip(lhs, rhs, stored["slots"])):
        error = abs(left - right) / (unit + abs(right))
        require(math.isfinite(error) and error <= TOLERANCE, "independent native identity fails tolerance")
        require(recorded["pole"] == pole, "stored Laurent ordering differs")
        # This envelope concerns replay roundoff only. It never relaxes the
        # independent integral-identity tolerance above. All sums contain <=4
        # nonzero terms in this fixed data; 64 ulps of the compared operands is
        # conservative for the different summation and subtraction order.
        for value, key in ((left, "lhs"), (right, "rhs"), (left-right, "residual")):
            saved = complex(*recorded[key])
            envelope = 64 * sys.float_info.epsilon * max(unit, abs(left), abs(right), abs(value), abs(saved))
            difference = abs(value-saved)
            require(difference <= envelope, "stored operand/residual differs beyond replay roundoff")
            statistics["maximum_saved_value_difference"] = max(statistics["maximum_saved_value_difference"], difference)
        saved_error = abs(complex(*recorded["residual"])) / (unit + abs(complex(*recorded["rhs"])))
        require(saved_error == recorded["normalized_error"], "stored normalized error is inconsistent")
        errors.append(error)
        statistics["maximum_normalized_error"] = max(statistics["maximum_normalized_error"], error)
        statistics["complex_slot_comparisons"] += 1
    require(stored["maximum_normalized_error"] == max(r["normalized_error"] for r in stored["slots"]),
            "stored maximum residual differs")
    statistics["residual_records"] += 1


def wire(prepared, attempt, case):
    head, *rows = attempt["wire_request"].splitlines()
    fields = head.split()
    require(len(fields) == 10 and fields[1] == case["id"], "wire header shape/case differs")
    generic = attempt["engine"] == "generic"
    expected_mode = 1 if generic else {"Hybrid": 2, "PassarinoVeltman": 1, "Ibp": 0}[attempt["mode"]]
    require(fields[0] == ("CHECK" if generic else "BENCH"), "wire engine differs")
    # Both frozen BENCH and CHECK put method at field2 and width at field6.
    width_at, mode_at = 6, 2
    require(int(fields[mode_at]) == expected_mode and int(fields[width_at]) == len(attempt["lane_indices"])
            and int(fields[3]) == case["n"] and int(fields[4]) == case["rank"]
            and Fraction(fields[5]) == Fraction(attempt["scale"])
            and fields[7:] == ["0", "1", "1"], "wire tensor/batch/scale/control metadata differs")
    require(len(rows) == case["n"] * len(attempt["lane_indices"]), "wire propagator rows missing")
    for local, original in enumerate(attempt["lane_indices"]):
        sample = case["samples"][original]
        require(scalar_text(sample["mu"]) == attempt["scale"], "scale group changed original sample")
        for i in range(case["n"]):
            values = rows[local * case["n"] + i].split()
            require(len(values) == 5 and values[4].startswith("(") and values[4].endswith(")"),
                    "wire propagator row malformed")
            scalar_values = values[:4] + values[4][1:-1].split(",")
            expected = sample["shifts"][i] + sample["masses"][i]
            require([Fraction(x) for x in scalar_values] == [rational(x) for x in expected],
                    "wire changed shift/mass or numeric precision")


def main():
    if OUTPUT.exists():
        raise ValueError("preserve existing independent audit")
    started = time.monotonic()
    pq = document(HERE / "prepared001/qualification.json")
    cq = document(HERE / "correctness001/qualification.json")
    require(cq["preparation_qualification"]["sha256"] == BINDINGS[str((HERE / "prepared001/qualification.json").relative_to(ROOT))],
            "correctness package binds another preparation")
    files(pq["files"])
    files(cq["files"])
    prepared = payload(pq["preparation"])
    data = payload(cq["capture"])
    prepared_artifacts = archive(pq["archive"])
    stderr = archive(cq["stderr"])
    require(len(stderr) == 46 and all(not b for b in stderr.values()), "unexpected missing/nonempty child stderr")
    require(data["status"] == "capture-complete" and data["qualification"] == "identities-passed"
            and data["guards_unchanged"] is True and data["build_performed"] is False
            and data["extra_reduction_requests"] is False and data["performance_evidence"] is False,
            "capture not complete correctness-only evidence")
    require(prepared["guards_unchanged"] is True and prepared["reference_reduction_performed"] is False,
            "preparation performed reduction or changed guards")
    files(data["guards"])
    files(prepared["guards"])
    for info in data["binaries"].values():
        bound_file(ROOT / info["path"], info["sha256"])
    parentq = document(ROOT / "validation/collier-reference/shared/attempt004/qualification.json")
    bound_file(ROOT / "validation/collier-reference/shared/attempt005/qualification.json",
               "3dd671c6e9401c0828facdb46ca673981731a90d06542c1659a981d42cb99dd6")
    parent = payload(parentq["artifacts"]["capture"])
    require(parent["guards_unchanged"] is True, "original parent guards changed")
    require(len(parent["rows"]) == 34 and len(parent["input_cases"]) == 17,
            "original failure visibility lost")
    require(data["original34_rows"] == [{k: row[k] for k in ("id", "n", "rank", "batch_width", "status")}
                                      for row in parent["rows"]], "original row statuses changed")

    require(len(prepared["polynomials"]) == 100 and len(prepared["aliases"]) == 497
            and len(prepared["branches"]) == 3, "prepared polynomial/alias/branch inventory differs")
    for expression, entry in prepared["polynomials"].items():
        require(entry["exit_code"] == 0, "Symbolica preparation unsuccessful")
        command = entry["command"]
        name = Path(command[2]).stem
        require(command[1] == "prepare" and command[3:] == ["--model", str(ROOT / "fixtures/models/phi3.json")],
                "unexpected preparation command")
        require(sha(prepared_artifacts[name + ".dot"]) == entry["dot_sha256"], "prepared DOT binding differs")
        require('num="' + expression + '"' in prepared_artifacts[name + ".dot"].decode(), "DOT expression differs")
        require(json.loads(prepared_artifacts[name + ".prepared.json"]) == entry["prepared"],
                "saved coefficient table differs from CLI output")
        require(prepared_artifacts[name + ".stderr.log"] == b"", "nonempty preparation stderr")
        terms(prepared, expression)
    require(len(prepared_artifacts) == 300, "prepared raw artifact inventory differs")
    require(all(expression in prepared["polynomials"] for expression in prepared["aliases"].values()),
            "alias missing prepared coefficient table")
    branches = prepared["branches"]
    keys = [proof_key(b["sample"]) for b in branches]
    require(len(set(keys)) == 3 and [b["proof_key"] for b in branches] == keys
            and [b["id"] for b in branches] == [0, 1, 2], "exact branch identity differs")
    require(prepared["original32_proof_keys"] == [keys[i % 3] for i in range(32)], "original lane map differs")
    for b in branches:
        require(rational(b["parent_domain_proof"]["positive_mass_polynomial_lower_bound"]) > 0
                and b["parent_domain_proof"]["powers"] == [1] * 5
                and b["parent_domain_proof"]["dimension_shift"] == 0, "positive-F/unit-power/D4 scope differs")
        require(len(b["sample"]["masses"]) == 5
                and all(rational(m[0]) > 0 and rational(m[1]) == 0 for m in b["sample"]["masses"]),
                "positive real massive scope differs")
        for i in range(1, 5):
            require(terms(prepared, poly(prepared, f"difference-cancellation-{b['id']}-{i}")) == [],
                    "Symbolica denominator cancellation witness failed")
            require(constant(prepared, poly(prepared, f"f-{b['id']}-{i}")) == rational(b["denominator_differences"][i-1]["f"]),
                    "f invariant differs from prepared Symbolica scalar")
        require(terms(prepared, poly(prepared, f"trace-cancellation-{b['id']}")) == [],
                "Symbolica trace cancellation witness failed")
    cases = {c["id"]: c for c in prepared["pinched_cases"] + prepared["routing_cases"]}
    expected_case_ids = {f"n5-pinch{i}-rank1" for i in range(5)} | {"n5-cyclic-origin1", "n5-reversed-nonzero"}
    require(set(cases) == expected_case_ids and data["prepared_cases"] == list(cases.values()), "prepared cases changed")
    for case in cases.values():
        is_pinch = case["id"].startswith("n5-pinch")
        order = [i for i in range(5) if i != int(case["id"][8])] if is_pinch else case["denominator_order"]
        require(case["n"] == (4 if is_pinch else 5) and case["rank"] == (1 if is_pinch else 2), "case rank/topology differs")
        require(order == ([i for i in range(5) if i != int(case["id"][8])] if is_pinch
                else [1, 2, 3, 4, 0] if case["id"] == "n5-cyclic-origin1" else [0, 4, 3, 2, 1]),
                "pinch/routing denominator order differs")
        require(len(case["samples"]) == 3, "prepared branch missing")
        for branch, sample in zip(branches, case["samples"]):
            original = branch["sample"]
            origin = original["shifts"][order[0]]
            require(sample["mu"] == original["mu"] and sample["masses"] == [original["masses"][i] for i in order],
                    "pinch/routing changed masses or scale")
            for local, i in enumerate(order):
                for nu in range(4):
                    expression = f"({original['shifts'][i][nu]})-({origin[nu]})"
                    require(rational(sample["shifts"][local][nu]) == constant(prepared, expression),
                            "translated shift differs from Symbolica witness")

    require(len(data["attempts"]) == data["planned_requests"] == 46, "not exact46 capture")
    inventory = prepared["reference_request_inventory"]
    require(len(inventory) == 46, "not exact46 prepared inventory")
    assembled = {(x["case"], x["policy"]): x["response"] for x in data["assembled_responses"]}
    require(len(assembled) == len(data["assembled_responses"]) == 23, "duplicate/missing assembled response")
    expected_policies = {(c, "iregi-"+m) for c in cases for m in MODES} | {
        (c, "generic-1") for c in ("n5-cyclic-origin1", "n5-reversed-nonzero")}
    require(set(assembled) == expected_policies, "case/engine qualification matrix differs")
    grouped = {}
    for ordinal, (attempt, item) in enumerate(zip(data["attempts"], inventory)):
        require({k: attempt[k] for k in item} == item and attempt["status"] == "validated-response"
                and attempt["child_exit_code"] == 0, "request differs, not validated, or child failed")
        require(sha(attempt["wire_request"].encode()) == attempt["wire_request_sha256"], "wire request hash differs")
        wire(prepared, attempt, cases[attempt["case"]])
        policy = attempt["engine"] + "-" + str(attempt["mode"])
        key = (attempt["case"], policy)
        require(key in assembled, "unassembled native response")
        response = attempt["response"]
        require(response["id"] == attempt["case"], "native response case differs")
        native(response, cases[attempt["case"]]["rank"], len(attempt["lane_indices"]), attempt["engine"] == "generic")
        used = grouped.setdefault(key, set())
        for local, lane in enumerate(attempt["lane_indices"]):
            require(type(lane) is int and 0 <= lane < 3 and lane not in used, "lane gather duplicated or invalid")
            used.add(lane)
            require(assembled[key]["lanes"][lane] == response["lanes"][local], "gather changed native lane")
            if attempt["engine"] == "generic":
                require(assembled[key]["pole_check_errors"][lane] == response["pole_check_errors"][local],
                        "gather changed native pole probe")
    for key, used in grouped.items():
        require(used == {0, 1, 2} and assembled[key]["stable"] is True, "gather omitted original branch")
        attempts = [a for a in data["attempts"] if (a["case"], a["engine"]+"-"+str(a["mode"])) == key]
        require(len(attempts) == 2 and {a["scale"] for a in attempts} == {"3", "6"},
                "scale group omitted or duplicated")
    require(set(grouped) == set(assembled), "unexpected assembled response")

    parent_rows = {(r["rank"], r["batch_width"]): r for r in parent["rows"] if r["n"] == 5}
    require(set(parent_rows) == {(r, w) for r in (0, 1, 2) for w in (1, 32)}, "parent N5 rank/batch rows differ")
    parent_cases = {c["rank"]: c for c in parent["input_cases"] if c["n"] == 5}
    for case in parent_cases.values():
        require([proof_key(s) for s in case["samples"]] == prepared["original32_proof_keys"], "parent input lane branch differs")
    for (rank, width), row in parent_rows.items():
        for engine in ENGINES:
            native(row["responses"][engine], rank, width, engine == "generic-1")

    saved = data["identities"]
    require(saved["status"] == "passed", "stored identity overall failure")
    prefixes = {(x["lower_rank"], x["higher_rank"], x["batch_width"], x["engine"]): x for x in saved["prefix_rows"]}
    require(len(prefixes) == len(saved["prefix_rows"]) == 24, "prefix inventory differs")
    for lo, hi in ((0, 1), (0, 2), (1, 2)):
        for width in (1, 32):
            for engine in ENGINES:
                record = prefixes[(lo, hi, width, engine)]
                require(len(record["lanes"]) == width, "prefix lane missing")
                for lane in range(width):
                    row = record["lanes"][lane]
                    branch = branches[lane % 3]
                    require(row["lane"] == lane and row["proof_key"] == keys[lane % 3]
                            and row["status"] == "passed" and len(row["checks"]) == len(indices(lo)), "prefix branch/native status differs")
                    left = parent_rows[(lo, width)]["responses"][engine]["lanes"][lane]["moments"]
                    right = parent_rows[(hi, width)]["responses"][engine]["lanes"][lane]["moments"]
                    for alpha, check in zip(indices(lo), row["checks"]):
                        residual("prefix", vectors(left, lo, alpha), vectors(right, hi, alpha), energy(branch["sample"])**(sum(alpha)-6), check)

    equations = {(x["engine"], x["pinched_rhs_mode"], x["branch"]): x for x in saved["branch_identities"]}
    require(len(equations) == len(saved["branch_identities"]) == 36, "branch-equation inventory differs")
    for engine in ENGINES:
        for mode in MODES:
            for branch in branches:
                bid = branch["id"]
                record = equations[(engine, mode, bid)]
                require(record["status"] == "passed" and record["proof_key"] == keys[bid]
                        and len(record["checks"]) == 21, "branch-equation checks/status differ")
                checks = {x["identity"]: x for x in record["checks"]}
                require(len(checks) == 21, "duplicate branch equation")
                moments = parent_rows[(2, 32)]["responses"][engine]["lanes"][bid]["moments"]
                pinches = {i: assembled[(f"n5-pinch{i}-rank1", "iregi-"+mode)]["lanes"][bid]["moments"] for i in range(5)}
                e0 = vectors(moments, 2, (0, 0, 0, 0))
                d0 = vectors(pinches[0], 1, (0, 0, 0, 0))
                for i in range(1, 5):
                    f = float(constant(prepared, poly(prepared, f"f-{bid}-{i}")))
                    di = vectors(pinches[i], 1, (0, 0, 0, 0))
                    residual("branch", dot(prepared, poly(prepared, f"difference-{bid}-{i}"), moments, 2),
                             add(di, times(-1, d0), times(-f, e0)), energy(branch["sample"])**-4,
                             checks[f"denominator-difference-{i}"])
                    for nu in range(4):
                        alpha = tuple(int(k == nu) for k in range(4))
                        translation = branch["translation_monomials"]["-".join(map(str, alpha))]
                        d0vec = dot(prepared, translation, pinches[0], 1)
                        residual("branch", dot(prepared, poly(prepared, f"difference-{bid}-{i}-q{nu}"), moments, 2),
                                 add(vectors(pinches[i], 1, alpha), times(-1, d0vec), times(-f, vectors(moments, 2, alpha))),
                                 energy(branch["sample"])**-3, checks[f"denominator-difference-{i}-q{nu}"])
                residual("branch", dot(prepared, poly(prepared, "metric-trace-rank2"), moments, 2),
                         add(d0, times(number(branch["sample"]["masses"][0][0]), e0)), energy(branch["sample"])**-4,
                         checks["rank2-metric-trace"])

    routes = {(x["case"], x["engine"]): x for x in saved["routing_rows"]}
    require(len(routes) == len(saved["routing_rows"]) == 8, "routing row inventory differs")
    for case in prepared["routing_cases"]:
        for engine in ENGINES:
            record = routes[(case["id"], engine)]
            require(len(record["lanes"]) == 3, "routing branch missing")
            for bid, branch in enumerate(branches):
                row = record["lanes"][bid]
                require(row["status"] == "passed" and row["branch"] == bid and row["proof_key"] == keys[bid]
                        and len(row["checks"]) == 15, "routing branch/status/check count differs")
                routed = assembled[(case["id"], engine)]["lanes"][bid]["moments"]
                original = parent_rows[(2, 32)]["responses"][engine]["lanes"][bid]["moments"]
                for alpha, check in zip(indices(2), row["checks"]):
                    require(check["moment"] == list(alpha), "routing tensor order differs")
                    left = (dot(prepared, branch["translation_monomials"]["-".join(map(str, alpha))], routed, 2)
                            if case["id"] == "n5-cyclic-origin1" else vectors(routed, 2, alpha))
                    residual("routing", left, vectors(original, 2, alpha), energy(branch["sample"])**(sum(alpha)-6), check)

    finite = {(x["case"], x["engine"], x["batch_width"]): x for x in saved["finiteness_rows"]}
    require(len(finite) == len(saved["finiteness_rows"]) == 47, "finiteness inventory differs")
    finite_inputs = []
    for (rank, width), row in parent_rows.items():
        for engine in ENGINES:
            finite_inputs.append((parent_cases[rank], engine, width, row["responses"][engine]))
    for (case, engine), response in assembled.items():
        finite_inputs.append((cases[case], engine, 3, response))
    for case, engine, width, response in finite_inputs:
        record = finite[(case["id"], engine, width)]
        require(len(record["lanes"]) == width, "finiteness lanes missing")
        for lane in range(width):
            row = record["lanes"][lane]
            require(row["lane"] == lane and row["status"] == "passed"
                    and len(row["checks"]) == len(indices(case["rank"])), "finiteness native status/count differs")
            moments = response["lanes"][lane]["moments"]
            for alpha, check in zip(indices(case["rank"]), row["checks"]):
                residual("finiteness", vectors(moments, case["rank"], alpha)[:3], [0j] * 3,
                         energy(case["samples"][lane])**(4+sum(alpha)-2*case["n"]), check)
    require({k: (v["residual_records"], v["complex_slot_comparisons"]) for k, v in REPLAY.items()} == {
        "prefix": (924, 3696), "branch": (756, 3024), "routing": (360, 1440), "finiteness": (3357, 10071)},
        "independent residual-record/complex-slot counts differ")
    require(COUNTS["native_lanes_admitted_in_unique_responses"] == 465
            and COUNTS["native_complex_pairs_admitted_in_unique_responses"] == 13428,
            "unique native lane/complex-pair count differs")
    result = {"kind": "n5-independent-saved-data-identity-audit", "status": "passed", "audit_source_sha256": file_hash(__file__),
        "elapsed_seconds": time.monotonic()-started, "counts": dict(COUNTS), "recomputed_checks": REPLAY,
        "total_residual_records": sum(x["residual_records"] for x in REPLAY.values()),
        "total_complex_slot_comparisons": sum(x["complex_slot_comparisons"] for x in REPLAY.values()),
        "bound_files_sha256": BINDINGS, "new_reference_or_cli_requests": 0, "builds": 0, "performance_evidence": False,
        "independence": "No producer comparator/contraction/residual import; coefficient/tensor dot products use math.fsum; all polynomials/translations originate in archived Symbolica CLI output",
        "native_admission": "All native lanes and four Laurent slots admitted before replay; rejected flags or incomplete arrays cannot be overridden by identity agreement",
        "scope": "Three retained positive-F massive undotted N5 branches, ranks0/1/2, D=4-2epsilon; 32 lanes cycle these three branches. No physical-process, MadLoop, higher-rank, singular-domain, dotted/dimension-shift or timing qualification",
        "earlier_evidence_policy": "Original attempt004/attempt005 and preparation/correctness qualifications unchanged; this audit supplements capture-preserved-audit-pending labels"}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(OUTPUT.relative_to(ROOT)), "sha256": file_hash(OUTPUT),
                      "counts": dict(COUNTS), "checks": REPLAY}, indent=2))


if __name__ == "__main__":
    main()
