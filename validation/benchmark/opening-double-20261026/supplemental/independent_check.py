#!/usr/bin/env python3
"""Saved-only audit of four fixed denominator-permuted binary64 candidates.

No producer imports, compilation, subprocesses or integral evaluation. Run from
the repository root after native measurements finish. The default output is in
target, so replay never modifies the sealed measurement directory.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

BASE = "validation/benchmark/opening-double-20261026"
HERE = BASE + "/supplemental"
OLD = "validation/benchmark/opening-rank6-20261026"
OLD_COMPARISON_SHA = "5d72855e1ad01690c534672d39c7a12e4e2bbbf043b4215a1b163375c95cae8e"
POLES = ["UV single", "IR single", "IR double", "finite"]
FIELDS = ("outer_total_ns", "scalar_masters_ns", "tirust_exclusive_ns")
PERMUTATION = [1, 0, 2, 3]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def decode(body):
    def unique(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    def bad_constant(value):
        raise ValueError("nonfinite JSON number: " + value)

    return json.loads(body, object_pairs_hook=unique, parse_float=F,
                      parse_constant=bad_constant)


def basis(rank):
    # Documented enumeration of Cartesian indices; no symbolic manipulation.
    return [[t, x, y, r-t-x-y] for r in range(rank+1)
            for t in range(r, -1, -1) for x in range(r-t, -1, -1)
            for y in range(r-t-x, -1, -1)]


def real(value, binary64):
    need(set(value) == {"exact_rational", "working_bits", "negative_sign", "finite"}
         and value["finite"] is True and isinstance(value["exact_rational"], str),
         "finite exact represented coefficient")
    need(type(value["working_bits"]) is int and value["working_bits"] > 0
         and (not binary64 or value["working_bits"] == 53), "represented precision")
    q = F(value["exact_rational"])
    need(type(value["negative_sign"]) is bool and
         (q == 0 or value["negative_sign"] == (q < 0)), "represented sign")
    if binary64:
        need(q.denominator & (q.denominator-1) == 0, "binary64 denominator")
        n = abs(q.numerator)
        if n:
            odd = n >> ((n & -n).bit_length()-1)
            need(odd.bit_length() <= 53 and abs(q) <= F(2**1024-2**971)
                 and q.denominator <= 2**1074, "finite f64 representability")
    return q


def values(array, request, binary64):
    need(array["basis"] == basis(request["rank"]) and array["components"] == 1
         and array["convention"] == "IregiNative" and array["tensor_weights"] == "Components"
         and array["laurent_order"] == POLES and len(array["lanes"]) == 1,
         "complete native cumulative tensor layout")
    lane = array["lanes"][0]
    need(lane["lane"] == 0 and type(lane["fallback_used"]) is bool
         and type(lane["analytic_used"]) is bool, "lane metadata")
    if lane["status"] != "Success":
        need(lane["values"] is None, "failed guarded lane exposes null coefficients")
        return None
    need(len(lane["values"]) == 4*len(array["basis"]), "complete complex tensor fields")
    result = []
    for pair in lane["values"]:
        need(len(pair) == 2, "complex pair width")
        result.append(tuple(real(value, binary64) for value in pair))
    return result


def accuracy(actual, expected, request):
    a, b = values(actual, request, True), values(expected, request, False)
    if a is None:
        return {"measured": False, "honest_null_refusal": True}
    need(b is not None, "successful admitted comparison reference")
    mu, error2, amplitude2, mixed2 = F(request["samples"][0]["mu"]), F(0), F(0), F(0)
    need(mu > 0, "positive dimensional weighting scale")
    for index, (left, right) in enumerate(zip(a, b)):
        degree = sum(actual["basis"][index//4])
        dimension = degree+4+2*request["dimension_shift"]-2*sum(request["powers"])
        weight2 = mu**(2*dimension)
        difference2 = sum((x-y)**2 for x, y in zip(left, right))
        norm2 = sum(y*y for y in right)
        error2 = max(error2, difference2/weight2)
        amplitude2 = max(amplitude2, norm2/weight2)
        mixed2 = max(mixed2, difference2/max(weight2, norm2))
    relative2 = error2/amplitude2 if amplitude2 else (F(0) if error2 == 0 else None)
    return {"measured": True, "compared_complex_fields": len(a),
            "relative_error_squared_exact": str(relative2) if relative2 is not None else None,
            "relative_error": math.sqrt(float(relative2)) if relative2 is not None else None,
            "maximum_componentwise_mixed_error": math.sqrt(float(mixed2)),
            "relative_error_at_most_1e6": relative2 is not None and relative2 <= F(1, 10**12),
            "relative_error_at_most_1e3": relative2 is not None and relative2 <= F(1, 10**6)}


def close(actual, expected, label):
    need((actual is None and expected is None) or
         (actual is not None and expected is not None and math.isfinite(float(actual))
          and math.isclose(float(actual), expected, rel_tol=1e-12, abs_tol=1e-300)), label)


def timing(result, request):
    blocks, warmups = result["repeated_measurements"], result["warmup_call_ns"]
    need(len(blocks) == request["repeats"] == 11 and len(warmups) == 3
         and all(type(t) is int and t > 0 for t in warmups), "fixed repeats/warmup")
    count = max(1, min(10000, (30000000+warmups[-1]-1)//warmups[-1]))
    need(result["realized_iterations_per_repeat"] == count, "once-calibrated loop count")
    samples = {field: [] for field in FIELDS}
    for index, block in enumerate(blocks):
        calls = block["calls"]
        need(block["repeat"] == index and len(calls) == count
             and block["all_statuses_and_accessible_arrays_reproduced"] is True,
             "complete fixed repeat and output checks")
        for call in calls:
            keys = set(FIELDS) | {"profile_total_ns", "profile_arguments_ns",
                                  "profile_recurrence_and_stability_ns"}
            need(set(call) == keys and all(type(call[k]) is int and call[k] >= 0 for k in keys),
                 "nonnegative integer timing fields")
            need(call["outer_total_ns"] > 0 and call["outer_total_ns"] ==
                 call["scalar_masters_ns"]+call["tirust_exclusive_ns"], "same-call additive split")
            need(call["profile_arguments_ns"]+call["scalar_masters_ns"]+
                 call["profile_recurrence_and_stability_ns"] <= call["profile_total_ns"] <=
                 call["outer_total_ns"], "nonoverlapping nested stages")
        for field in FIELDS:
            samples[field].append(F(sum(c[field] for c in calls), count*1000))
    output = {}
    for field, data in samples.items():
        mean = sum(data)/len(data)
        deviation = math.sqrt(float(sum((v-mean)**2 for v in data)/(len(data)-1)))
        output[field.removesuffix("_ns")+"_us"] = {
            "mean": float(mean), "median": float(sorted(data)[len(data)//2]),
            "minimum": float(min(data)), "maximum": float(max(data)),
            "stdev": deviation, "standard_error": deviation/math.sqrt(len(data))}
    return output, count


def audit(root, summary_name, live_source, live_binary):
    bindings = {}

    def read(name, expected=None):
        need(type(name) is str and not name.startswith("/") and "\\" not in name
             and all(p not in ("", ".", "..") for p in name.split("/")), "safe relative path")
        path = (root/name).resolve()
        need(path.is_relative_to(root), "path within project")
        body = path.read_bytes()
        need(expected is None or digest(body) == expected, "SHA256 binding: "+name)
        bindings[name] = {"sha256": digest(body), "bytes": len(body)}
        return body

    def load(name, expected=None):
        return decode(read(name, expected))

    summary = load(summary_name)
    built = load(BASE+"/build.json", summary["original_build"]["sha256"])
    need(summary["original_build"]["path"] == BASE+"/build.json" and built["status"] == "built_and_frozen"
         and built["sources_unchanged"] is True and built["features"] == ["native-f64-abc"]
         and len(built["source_hashes"]) == 215, "frozen source-guarded build215")
    need(built["step"]["returncode"] == 0 and built["step"]["timed_out"] is False
         and built["step"]["owned_group_gone"] is True, "successful saved build")
    protocol_binding = summary["protocol"]
    need(protocol_binding["path"] == HERE+"/protocol.json", "supplemental protocol path")
    protocol = load(protocol_binding["path"], protocol_binding["sha256"])
    need(protocol["original_build"] == summary["original_build"]
         and protocol["source_hashes"] == summary["source_hashes"] == built["source_hashes"]
         and protocol["supplemental_script_hashes"] == summary["supplemental_script_hashes"]
         and protocol["binary_path"] == built["binary_path"]
         and protocol["binary_sha256"] == built["binary_sha256"]
         and protocol["permutation"] == PERMUTATION and protocol["fixed_additional_candidates"] == 4,
         "exact fixed supplemental protocol/build/source association")
    for name, expected in protocol["supplemental_script_hashes"].items():
        read(name, expected)
    need(set(protocol["supplemental_script_hashes"]) ==
         {HERE+"/"+name for name in ("run.py", "README.md")}, "runner/readme hash inventory")
    read(HERE+"/independent_check.py")
    read(BASE+"/run.py", built["source_hashes"][BASE+"/run.py"])
    if live_source:
        for name, expected in built["source_hashes"].items():
            read(name, expected)
    if live_binary:
        read(built["binary_path"], built["binary_sha256"])
    suite = load(BASE+"/inputs.json", built["source_hashes"][BASE+"/inputs.json"])
    need(protocol["original_inputs"] == {"path": BASE+"/inputs.json",
         "sha256": built["source_hashes"][BASE+"/inputs.json"]}, "original input suite byte pin")
    cases = {case["id"]: case for case in suite["cases"]}
    admission = load(OLD+"/reference-comparison.json", OLD_COMPARISON_SHA)
    need(admission["all_18_rows_mathematically_and_terminal_qualified"] is True
         and admission["compared_complex_fields"] == 8968 and admission["failed_complex_fields"] == 0,
         "previous restricted independent reference admission")
    expected_inventory = {(case, candidate) for case in
                          ("extended-n4-r6-dot2", "extended-n4-r6-dot3")
                          for candidate in ("pv-permuted-native-abc", "pv-permuted-symbolica")}
    need(len(summary["attempts"]) == 4 and
         {(a["case_id"], a["candidate_id"]) for a in summary["attempts"]} == expected_inventory,
         "exact predeclared four-candidate inventory")
    rows = []
    for item in summary["attempts"]:
        ident, candidate = item["case_id"], item["candidate_id"]
        request = load(item["request_source"], item["request_sha256"])
        original = cases[ident]["driver_request"]
        recorded = next(row for row in protocol["rows"]
                        if row["case_id"] == ident and row["candidate_id"] == candidate)
        need(all(item[key] == value for key, value in recorded.items())
             and recorded["request"] == request and recorded["permutation"] == PERMUTATION,
             "summary preserves original prepared supplemental request")
        original_candidate = next(c["request"] for c in cases[ident]["candidates"]
                                  if c["id"] == ("native-abc" if candidate.endswith("native-abc") else "symbolica"))
        need(recorded["original_request"] == original_candidate, "exact saved original candidate")
        need(request["n"] == original["n"] == 4 and request["rank"] == original["rank"] == 6
             and request["dimension_shift"] == original["dimension_shift"] == 0
             and request["powers"] == [original["powers"][i] for i in PERMUTATION],
             "unchanged denominator-permuted tensor definition")
        need(len(request["samples"]) == len(original["samples"]) == 1, "one sample")
        a, b = request["samples"][0], original["samples"][0]
        need(a["shifts"] == [b["shifts"][i] for i in PERMUTATION]
             and a["masses_squared"] == [b["masses_squared"][i] for i in PERMUTATION]
             and a["mu"] == b["mu"], "exact shift/mass/power triple permutation; unchanged loop variable")
        policy = "NativeF64Abc" if candidate.endswith("native-abc") else "Symbolica"
        need(request["numeric_type"] == "f64" and request["working_bits"] == request["requested_bits"] == 53
             and request["algorithm"] == "PassarinoVeltman" and request["master_policy"] == policy
             and request["postconstruction_profiling"] is False and request["warmup"] == 3
             and request["repeats"] == 11 and request["iterations"] == 1
             and request["target_block_ns"] == 30000000 and request["maximum_iterations"] == 10000,
             "fixed f64/request53/PV/warm protocol")
        step = load(item["supervision_source"], item["supervision_sha256"])
        need(step["request_sha256"] == bindings[item["request_source"]]["sha256"]
             and step["binary_sha256"] == built["binary_sha256"]
             and step["source_hashes_unchanged"] is True and step["binary_unchanged_after"] is True
             and step["source_hashes_before"] == step["source_hashes_after"] == built["source_hashes"]
             and step["protocol"] == protocol_binding
             and step["supplemental_scripts_unchanged"] is True
             and step["supplemental_script_hashes_after"] == protocol["supplemental_script_hashes"]
             and step["case_id"] == ident and step["candidate_id"] == candidate
             and step["owned_group_gone"] is True and type(step["returncode"]) is int
             and type(step["timed_out"]) is bool, "terminal source/binary/request guard")
        read(item["supervision_source"].rsplit("/", 1)[0]+"/native.log", step["log_sha256"])
        command = step["command"]
        need(command[:3] == ["taskset", "-c", str(step["cpu"])] and len(command) == 6
             and command[3].endswith("/"+built["binary_path"])
             and command[4].endswith("/"+item["request_source"])
             and command[5].endswith("/"+item["result_source"]), "exact supervised executable/input/output")
        if item["result_sha256"] is None:
            need(not (root/item["result_source"]).exists() and step.get("result_sha256") is None
                 and item["status"] == "timeout_or_native_failure"
                 and item["timing_captured"] is False and item["eligible_optimistic_result"] is False
                 and item["accuracy"]["measured"] is False, "honest terminal attempt without result")
            rows.append({"case_id": ident, "candidate_id": candidate, "status": item["status"],
                         "timing_captured": False, "eligible": False,
                         "accuracy": {"measured": False}, "no_result_payload": True})
            continue
        result = load(item["result_source"], step["result_sha256"])
        need(item["result_sha256"] == step["result_sha256"] and result["request"] == request
             and result["id"] == request["id"] and result["status"] == item["status"] == step["driver_status"],
             "saved result identity/status")
        if result.get("settings") is not None:
            need(result["settings"] == {
            "algorithm": "PassarinoVeltman", "convention": "IregiNative", "dimension_shift": 0,
            "input_policy": "Preserve", "invariants": "FromShifts", "powers": request["powers"],
            "propagators": 4, "rank": 6, "tensor_weights": "Components"}, "actual native settings")
        expected_inputs = [(F(x), F(0)) for shift in a["shifts"] for x in shift]
        expected_inputs += [tuple(F(x) for x in pair) for pair in a["masses_squared"]]
        expected_inputs.append((F(a["mu"]), F(0)))
        represented = result.get("represented_inputs")
        if represented is not None:
            need(len(represented) == len(expected_inputs) and all(
                len(pair) == 2 and tuple(real(v, True) for v in pair) == expected
                for pair, expected in zip(represented, expected_inputs)), "exact represented f64 inputs")
        reference_name = OLD+"/cases/"+ident+"/result.json"
        reference_sha = admission["input_bindings"][reference_name]["sha256"]
        need(item["accuracy"]["reference_sha256"] == reference_sha
             and item["accuracy"]["reference_comparison_sha256"] == OLD_COMPARISON_SHA,
             "reference arrays bound to prior independent admission")
        reference = load(reference_name, reference_sha)["first_output"]
        checked = (accuracy(result["first_output"], reference, request)
                   if result.get("first_output") is not None else
                   {"measured": False, "no_complete_output": True})
        for label in ("final_output", "failure_output"):
            if result.get(label) is not None:
                accuracy(result[label], reference, request)
        need(item["accuracy"]["reference_source"] == reference_name, "unpermuted reference source")
        need(bool(item["accuracy"]["measured"]) == checked["measured"], "independent accessibility")
        if checked["measured"]:
            for key in ("compared_complex_fields", "relative_error_squared_exact",
                        "relative_error_at_most_1e3", "relative_error_at_most_1e6"):
                need(item["accuracy"][key] == checked[key], "independent exact E/A: "+key)
            for key in ("relative_error", "maximum_componentwise_mixed_error"):
                close(item["accuracy"][key], checked[key], "independent accuracy display")
        captured = result.get("timing_qualified") is True and step["returncode"] == 0 and not step["timed_out"]
        need(item["timing_captured"] == captured, "independent timing eligibility")
        if captured:
            need(result["input_preserved"] is True and represented is not None
                 and result["first_output"] == result["final_output"]
                 and result["all_outputs_exactly_reproduced"] is True,
                 "captured timing preserves input and repeated complete output")
            measured, count = timing(result, request)
            for field, statistics in measured.items():
                for key, expected in statistics.items():
                    close(item["timing"][field][key], expected, "independent timing statistic")
            need(item["repeats"] == 11 and item["calls_per_repeat"] == count
                 and item["total_timed_calls"] == 11*count and item["maximum_additive_error_us"] == 0,
                 "raw timing counts/additivity")
        eligible = captured and checked["measured"] and checked["relative_error_at_most_1e3"]
        need(item["successful_finite_full_array"] == bool(result.get("all_successful_finite_full_arrays"))
             and (not captured or bool(result.get("all_successful_finite_full_arrays")) == bool(checked["measured"])),
             "independent complete-finite-success flags")
        need(item["eligible_optimistic_result"] == eligible, "independent optimistic eligibility")
        rows.append({"case_id": ident, "candidate_id": candidate, "status": result["status"],
                     "timing_captured": captured, "eligible": eligible, "accuracy": checked})
    for ident in ("extended-n4-r6-dot2", "extended-n4-r6-dot3"):
        candidates = [item for item in summary["attempts"] if item["case_id"] == ident
                      and item["eligible_optimistic_result"]]
        selected = min(candidates, key=lambda item: float(item["timing"]["outer_total_us"]["mean"]),
                       default={}).get("candidate_id")
        need(summary["selected_additional_candidate_by_case"][ident] == selected,
             "minimum measured mean among eligible fixed supplemental candidates")
    return {"schema_version": 1, "status": "passed_saved_supplemental_review", "passed": True,
            "attempts": rows, "planned_attempts": 4, "input_bindings": bindings,
            "live_selected_source_guards_rehashed": live_source,
            "live_frozen_binary_rehashed": live_binary, "native_or_integral_execution": False,
            "producer_imports": False, "denominator_permutation": PERMUTATION,
            "reference_scope": "Previous finite-precision admitted complete tensors, not exact integral values"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", default=HERE+"/supplemental-summary.json")
    parser.add_argument("--output", default="target/opening-double-20261026/supplemental-independent-review.json")
    parser.add_argument("--verify-live-source", action="store_true")
    parser.add_argument("--verify-live-binary", action="store_true")
    args = parser.parse_args()
    root = Path.cwd().resolve()
    need((root/"Cargo.toml").is_file(), "run from project root")
    try:
        result = audit(root, args.summary, args.verify_live_source, args.verify_live_binary)
    except (ValueError, KeyError, TypeError, OSError, IndexError, OverflowError) as error:
        result = {"schema_version": 1, "passed": False,
                  "status": "failed_saved_supplemental_review", "error": str(error),
                  "native_or_integral_execution": False}
    output = root/args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "output": args.output}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
