#!/usr/bin/env python3
"""Independently audit saved COLLIER observations, including rejected cases.

Run from the repository root. Reads JSON/text only; never builds or evaluates an
integral. Original target/ capture paths are mapped to the committed archive.
Optional --inspect-local-build rehashes cached binaries/modules if present;
those uncommitted build artifacts are not needed for a portable archive audit.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse
import datetime
import hashlib
import json
import math
import subprocess

ROOT = Path.cwd().resolve()
HERE = Path("validation/benchmark/opening-collier-20261026")
ARCHIVE = HERE / "capture001"
ORIGINAL = Path("target/collier-opening-column-20261026/capture001")
TIRUST = Path("validation/benchmark/opening-rank6-20261026")
LABELS = ("preflight", "pilot", "timed", "postflight")
EXPECTED_REJECTED = {"ordinary-n5-r5", "ordinary-n5-r6", "ordinary-n6-r6"}


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inspect-local-build", action="store_true")
    parser.add_argument("--output", type=Path,
                        default=Path("target/collier-opening-column-20261026/independent-replay.json"),
                        help="write a fresh replay under target/ by default; sealed review needs an explicit path")
    arguments = parser.parse_args()
    errors, files, reviewed = [], {}, []
    check_count = 0
    maximum_statistic_relative_difference = 0.0

    def check(condition, message):
        nonlocal check_count
        check_count += 1
        if not condition:
            errors.append(message)

    def read(path):
        files[str(path)] = digest(path)
        return json.loads((ROOT / path).read_text())

    def bind(path):
        files[str(path)] = digest(path)
        return (ROOT / path).read_text()

    def close(actual, expected, message):
        nonlocal maximum_statistic_relative_difference
        valid = (isinstance(actual, (int, float)) and math.isfinite(actual)
                 and math.isclose(actual, expected, rel_tol=2e-14, abs_tol=2e-14))
        check(valid, message)
        if expected:
            maximum_statistic_relative_difference = max(
                maximum_statistic_relative_difference, abs(actual-expected)/abs(expected))

    def mapped(path):
        path = Path(path)
        return ARCHIVE / path.relative_to(ORIGINAL) if path.is_relative_to(ORIGINAL) else path

    def statistics(values):
        exact = [F(str(v)) for v in values]
        n = len(exact)
        average = sum(exact, F(0)) / n
        ordered = sorted(exact)
        median = ordered[n//2] if n % 2 else (ordered[n//2-1]+ordered[n//2])/2
        deviation = math.sqrt(float(sum((v-average)**2 for v in exact)/(n-1)))
        error = deviation/math.sqrt(n)
        return dict(mean=float(average), median=float(median), stddev=deviation,
                    standard_error=error, confidence_95_half_width_student_t=2.228138852*error,
                    minimum=float(ordered[0]), maximum=float(ordered[-1]))

    def inspect_array(moments, basis, reference, n, context):
        check(isinstance(moments, list) and len(moments) == len(basis), context+" full tensor count")
        failed, missing, finite = [], [], 0
        maximum = F(0)
        for moment, (powers, fields) in enumerate(zip(basis, moments)):
            check(isinstance(fields, list) and len(fields) == 4, context+" four Laurent slots")
            for slot, value in enumerate(fields):
                item = dict(moment_index=moment, basis=powers, slot=slot)
                if value is None:
                    missing.append(item)
                    continue
                check(isinstance(value, list) and len(value) == 2
                      and all(type(v) in (int, float) and math.isfinite(v) for v in value),
                      context+" complete finite complex value")
                if not isinstance(value, list) or len(value) != 2:
                    continue
                finite += 1
                actual = [F(str(v)) for v in value]
                expected = [F(v["exact_rational"]) for v in reference[4*moment+slot]]
                # mu=3 dominates this fixed input family's dimensional scale.
                # Squared mixed absolute/relative norm, degree=|alpha|.
                squared = sum((a-b)**2 for a, b in zip(actual, expected)) / max(
                    F(9)**(sum(powers)+4-2*n), sum(b*b for b in expected))
                maximum = max(maximum, squared)
                if squared > F(1, 10**20):
                    failed.append(dict(item, normalized_error=math.sqrt(float(squared))))
        return dict(distinct_complex_fields=4*len(basis), finite_complex_fields=finite,
                    nonfinite_complex_fields=len(missing), mismatched_finite_complex_fields=len(failed),
                    maximum_normalized_error_over_finite_fields=math.sqrt(float(maximum)),
                    maximum_squared_normalized_error_exact=str(maximum),
                    nonfinite_fields=missing, finite_mismatches=failed)

    def wire_check(path, case, label, iterations):
        lines = bind(path).splitlines()
        request = case["driver_request"]
        n, rank = request["n"], request["rank"]
        header = lines[0].split()
        warmup = 3 if label in ("pilot", "timed") else 0
        repeats = 11 if label == "timed" else 1
        calls = iterations if label == "timed" else 1
        check(header == ["CHECK" if label in ("preflight", "postflight") else "BENCH",
                         case["id"], "1", str(n), str(rank), "3", "1", str(warmup),
                         str(repeats), str(calls)], case["id"]+" "+label+" exact header")
        check(len(lines) == n+1, case["id"]+" "+label+" exact input row count")
        sample = request["samples"][0]
        for line, shift, mass in zip(lines[1:], sample["shifts"], sample["masses_squared"]):
            fields = line.split()
            actual_shift = [F(v) for v in fields[:4]]
            actual_mass = [F(v) for v in fields[4].strip("()").split(",")]
            check(actual_shift == [F(v) for v in shift] and actual_mass == [F(v) for v in mass],
                  case["id"]+" "+label+" unchanged represented shifts/masses")

    raw = read(ARCHIVE / "results.json")
    build = read(HERE / "build.json")
    outer = read(HERE / "supervision.json")
    suite = read(TIRUST / "inputs.json")
    upstream = read(Path(build["upstream_build_receipt"]["source"]))
    check(digest(Path(build["upstream_build_receipt"]["source"])) == build["upstream_build_receipt"]["sha256"],
          "unchanged upstream build receipt")
    check(raw["status"] == "retained_failures", "campaign explicitly retains rejected cases")
    check(raw["mode"] == 1 and raw["numeric_type"] == "binary64" and raw["ratio_campaign"] is False,
          "fixed COLI mode1/binary64 absolute campaign")
    check(raw["cpu"] == 18 and raw["sample_lanes"] == 1 and raw["repeats"] == 11,
          "singleton CPU18 eleven-block contract")
    check(raw["sources_unchanged_after"] and raw["binary_unchanged_after"], "campaign source/binary guards")
    check(build["status"] == "built" and build["guards_unchanged"] and not build["library_rebuilt"]
          and not build["fast_math"] and not build["production_implementation_changed"],
          "unchanged optimized upstream library/client-only build")
    check(build["step"]["returncode"] == 0 and not build["step"]["timed_out"]
          and build["step"]["owned_group_gone"], "successful bounded client link")
    check(digest(HERE/"link.log") == build["step"]["log_sha256"], "link log digest")
    bind(HERE/"link.log")
    check(outer["returncode"] == 1 and not outer["timed_out"] and outer["owned_group_gone"],
          "outer code1 intentionally represents retained mathematical/status failures, with cleanup")
    check(all(outer[k] for k in ["library_unchanged_after", "modules_unchanged_after",
                                "source_hashes_unchanged_after", "binary_unchanged_after"]),
          "outer library/modules/source/binary guards")
    check(digest(HERE/"capture001.log") == outer["log_sha256"], "outer log digest")
    bind(HERE/"capture001.log")
    check(raw["binary"] == build["binary"], "capture frozen binary binding")
    check(len(build["module_hashes"]) == 28, "28 frozen interface modules")
    check(build["library"]["sha256"] == upstream["library"]["sha256"], "upstream library identity")
    for source, expected in {**build["source_hashes"], **raw["input_sources"]}.items():
        check(digest(Path(source)) == expected, "frozen source digest "+source)
        bind(Path(source))
    check(raw["input_sources"][str(TIRUST/"inputs.json")] == digest(TIRUST/"inputs.json"),
          "exact original input suite reused")
    ordinary = [c for c in suite["cases"] if c["table"] == "ordinary"]
    by_id = {r["id"]: r for r in raw["rows"]}
    check(len(ordinary) == len(raw["rows"]) == 12 and set(by_id) == {c["id"] for c in ordinary},
          "all twelve selected ordinary rows retained")
    archive_files = {p.relative_to(ROOT/ARCHIVE) for p in (ROOT/ARCHIVE).rglob("*") if p.is_file()}
    check(len(archive_files) == 169, "169 exact archived capture files")
    original_present = (ROOT/ORIGINAL).is_dir()
    if original_present:
        original_files = {p.relative_to(ROOT/ORIGINAL) for p in (ROOT/ORIGINAL).rglob("*") if p.is_file()}
        check(original_files == archive_files, "original and archive file sets")
        for relative in archive_files:
            check(digest(ARCHIVE/relative) == digest(ORIGINAL/relative), "byte-identical archive "+str(relative))
    for relative in archive_files:
        bind(ARCHIVE/relative)
    total_timed_calls = total_array_comparisons = 0
    for case in ordinary:
        identifier = case["id"]
        request = case["driver_request"]
        n, rank = request["n"], request["rank"]
        row = by_id[identifier]
        expected_qualified = identifier not in EXPECTED_REJECTED
        expected_acc = -2 if n == 6 else -1 if n == 5 else 0
        check(row["input"] == case, identifier+" unchanged selected input")
        check(row["timing_qualified"] == expected_qualified and row["status"] == (
            "measured" if expected_qualified else "measured_but_unqualified"), identifier+" correct qualification")
        check(row["native_returncode"] == 0 and row["binary_unchanged_after"]
              and row["reference_array_unchanged_after"], identifier+" clean child and immutable context")
        reference_path = Path(row["tirust_array_source"]["path"])
        check(digest(reference_path) == row["tirust_array_source"]["sha256"], identifier+" frozen TIRust array digest")
        reference_record = read(reference_path)
        check(reference_record["status"] == "measured" and reference_record["timing_qualified"],
              identifier+" earlier TIRust successful row")
        reference = reference_record["first_output"]["lanes"][0]["values"]
        basis = reference_record["basis"]
        check(len(basis) == math.comb(rank+4, 4), identifier+" cumulative moment count")
        stdout = bind(ARCHIVE/identifier/"collier.stdout.log")
        bind(ARCHIVE/identifier/"collier.stderr.log")
        stdout_responses = [json.loads(line[7:]) for line in stdout.splitlines() if line.startswith("RESULT ")]
        check(len(stdout_responses) == 4, identifier+" all four raw wire responses retained")
        all_responses = {}
        inspections = []
        deterministic_array = None
        for capture_index, label in enumerate(LABELS):
            folder = ARCHIVE/identifier
            response = read(folder/(label+".response.json"))
            assessment = read(folder/(label+".assessment.json"))
            cap = row["captures"][label]
            check(response == stdout_responses[capture_index], identifier+" "+label+" exact stdout JSON")
            check(mapped(cap["response"]) == folder/(label+".response.json")
                  and digest(mapped(cap["response"])) == cap["response_sha256"],
                  identifier+" "+label+" portable response/hash binding")
            check(cap["assessment"] == assessment and assessment["passed"] == expected_qualified,
                  identifier+" "+label+" retained assessment/outcome")
            wire_check(folder/(label+".request.txt"), case, label, row["iterations_per_block"])
            repeats = 11 if label == "timed" else 1
            check(response["id"] == identifier and response["collier_mode"] == 1
                  and response["initialization_topology_capacity"] == max(n, 2)
                  and response["initialization_rank_capacity"] == max(rank, 1, n-max(n-2,4))
                  and response["interface"] == {1:"Aten_cll",2:"Bten_cll",3:"Cten_cll",4:"Dten_cll"}.get(n,"TNten_cll")
                  and response["direct_tensor_threshold"] == 6, identifier+" "+label+" official API/capacities")
            check(type(response["clock_ticks_per_second"]) is int and response["clock_ticks_per_second"] > 0,
                  identifier+" "+label+" monotonic clock")
            check(len(response["total_ns"]) == repeats and all(type(v) in (int,float)
                  and math.isfinite(v) and v > 0 for v in response["total_ns"]),
                  identifier+" "+label+" finite positive raw block times")
            check(response["stable"] == expected_qualified, identifier+" "+label+" cumulative stability")
            check(len(response["lanes"]) == 1 and len(response["blocks"]) == repeats,
                  identifier+" "+label+" complete lane/block count")
            lane = response["lanes"][0]
            check(lane["status"] == ("success" if expected_qualified else "unstable")
                  and lane["last_err_flag"] == lane["worst_err_flag"] == 0
                  and lane["last_acc_flag"] == lane["worst_acc_flag"] == expected_acc,
                  identifier+" "+label+" exact independent status classification")
            arrays = [lane["moments"] if lane["moments"] is not None else lane["diagnostic_moments"]]
            for block in response["blocks"]:
                b = block["lanes"][0]
                check(b["cumulative_stable"] == expected_qualified and b["last_err_flag"] == 0
                      and b["last_acc_flag"] == expected_acc, identifier+" "+label+" block status")
                check(len(b["cumulative_maximum_rank_error_estimates"]) == rank+1
                      and all(math.isfinite(v) and v >= 0 for v in b["cumulative_maximum_rank_error_estimates"]),
                      identifier+" "+label+" complete finite block error estimates")
                arrays.append(b["moments"])
            check(len(lane["maximum_rank_error_estimates"]) == rank+1
                  and all(math.isfinite(v) and v >= 0 for v in lane["maximum_rank_error_estimates"]),
                  identifier+" "+label+" complete finite final error estimates")
            for array_index, array in enumerate(arrays):
                if deterministic_array is None:
                    deterministic_array = array
                check(array == deterministic_array, identifier+" "+label+" deterministic saved snapshot")
                inspection = inspect_array(array, basis, reference, n,
                    identifier+" "+label+" "+str(array_index))
                inspections.append(inspection)
                total_array_comparisons += 1
            if label in ("preflight", "postflight"):
                pole = response["pole_check_errors"]
                check(len(pole) == 1 and len(pole[0]) == 3, identifier+" "+label+" all three pole probes")
                if n == 6:
                    check(all(v > 1e-12 for v in pole[0]), identifier+" "+label+" failed N6 pole probes retained")
                else:
                    check(all(math.isfinite(v) and 0 <= v <= 1e-12 for v in pole[0]),
                          identifier+" "+label+" UV/IR probes pass")
            else:
                check(response["pole_check_errors"] is None, identifier+" "+label+" pole probes excluded from timer")
            all_responses[label] = response
        inspection = inspections[0]
        check(all(v == inspection for v in inspections), identifier+" same full-array diagnostic accounting for every snapshot")
        expected_counts = {"ordinary-n5-r5":(504,0,11),"ordinary-n5-r6":(840,0,62),"ordinary-n6-r6":(645,195,1)}
        expected_finite, expected_null, expected_mismatch = expected_counts.get(identifier,(4*len(basis),0,0))
        check((inspection["finite_complex_fields"],inspection["nonfinite_complex_fields"],
               inspection["mismatched_finite_complex_fields"]) == (expected_finite,expected_null,expected_mismatch),
              identifier+" independently counted finite/nonfinite/mismatched fields")
        iterations = max(1,min(1000000,math.ceil(100000000/all_responses["pilot"]["total_ns"][0])))
        check(row["iterations_per_block"] == iterations, identifier+" one-pilot fixed calibration")
        raw_times = all_responses["timed"]["total_ns"]
        check(row["timing_ns"]["raw_block_means"] == raw_times, identifier+" original eleven block means retained")
        recomputed_ns = statistics(raw_times)
        recomputed_us = {k:v/1000 for k,v in recomputed_ns.items()}
        for field,value in recomputed_ns.items():
            close(row["timing_ns"][field],value,identifier+" recomputed ns "+field)
            close(row["timing_us"][field],value/1000,identifier+" recomputed us "+field)
        total_timed_calls += 11*iterations
        reviewed.append(dict(id=identifier, expected_qualified=expected_qualified,
            measured_status=row["status"], native_accuracy_flag=expected_acc,
            moment_count=len(basis), timed_blocks=11, calls_per_block=iterations,
            total_timed_calls=11*iterations, saved_array_snapshots=len(inspections),
            recomputed_timing_us=recomputed_us, **inspection))
    check(total_array_comparisons == 216, "216 complete saved snapshots examined")
    check(sum(r["distinct_complex_fields"] for r in reviewed) == 6048, "6048 distinct requested complex fields accounted")
    check(sum(r["distinct_complex_fields"] for r in reviewed if r["expected_qualified"]) == 3864,
          "3864 distinct complex fields in nine qualified rows")
    check(sum(r["nonfinite_complex_fields"] for r in reviewed) == 195,
          "195 nonfinite fields remain explicit")
    check(sum(r["mismatched_finite_complex_fields"] for r in reviewed) == 74,
          "74 finite mismatches remain explicit, including one N6 failure before nulls")
    check(total_timed_calls == 2047397, "2047397 root calls including rejected observations")
    local_artifacts = {"requested":arguments.inspect_local_build,"portable_audit_requires_them":False,"hashes":{}}
    if arguments.inspect_local_build:
        artifact_hashes = {build["binary"]["path"]:build["binary"]["sha256"],
                           build["library"]["path"]:build["library"]["sha256"], **build["module_hashes"]}
        for path, expected in artifact_hashes.items():
            check((ROOT/path).is_file() and digest(Path(path)) == expected, "local frozen build artifact "+path)
            local_artifacts["hashes"][path] = expected
    core_paths = ["crates/iregi-rust/src","crates/iregi-masters/src","dependencies/symbolica",
                  "dependencies/oneloopmaster","Cargo.toml","Cargo.lock"]
    core_changes = subprocess.check_output(["git","diff","--name-only",build["source_revision"],"--",*core_paths],text=True).splitlines()
    check(not core_changes, "core/master/dependency/Cargo unchanged since source epoch")
    files[str(HERE/"independent_check.py")] = digest(HERE/"independent_check.py")
    proof = dict(schema_version=1, audit_status="passed" if not errors else "failed",
        numerical_campaign_status="retained_failures", checks=check_count, errors=errors,
        reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        review_scope="Independent saved-data/source audit; no build or native execution. Audit passed means retained outcomes are correctly classified, not that all COLLIER rows passed.",
        original_to_archive_prefix={str(ORIGINAL):str(ARCHIVE)}, archive_files=len(archive_files),
        archive_matches_original_target=original_present,
        source_review=["Official unmodified library, fixed COLI mode1 and required capacities max(N,2), max(R,1,N-max(N-2,4)); requested integrals unchanged.",
                       "Every root resets local-only memoization/flags via InitEvent; timer includes routing, tensor API, masters, normalization/gathering and finite/status scans. TIRust scans occur outside its timer, explicitly different.",
                       "UV=i*pi^2*Tuv, finite=i*pi^2*(T-(EulerGamma+log(pi))*Tuv), IR zeros restricted to this positive finite-mass family and separately probed outside timing.",
                       "N5/N6 COLLIER binary64 results do not form matched precision ratios against earlier Float128 TIRust observations; only absolute timings."],
        accepted_rows=[r["id"] for r in reviewed if r["expected_qualified"]],
        rejected_rows=[r["id"] for r in reviewed if not r["expected_qualified"]],
        distinct_complex_fields=6048, qualified_distinct_complex_fields=3864,
        finite_complex_fields=sum(r["finite_complex_fields"] for r in reviewed),
        nonfinite_complex_fields=195, mismatched_finite_complex_fields=74,
        saved_array_snapshots=total_array_comparisons, total_timed_calls=total_timed_calls,
        maximum_relative_statistic_difference=maximum_statistic_relative_difference,
        comparison="Squared mixed dimensional absolute/relative complex norm: |COLLIER-TIRust|^2 / max(9^(degree+4-2N),|TIRust|^2) <=1e-20, fixed mu=3. Exact rational TIRust values and decimal representations of saved binary64 outputs. Nulls classified separately rather than counted as zero mismatches.",
        failure_notice="N5R5/N5R6 accuracy flag -1 and 11/62 finite mismatches; N6R6 flag -2, failed pole probes, 195 nonfinite finite-slot fields at ranks3..6 and one additional finite mismatch. These are failures for these inputs and this fixed policy, not a claim that COLLIER mathematically lacks N6R6 support. Raw rejected durations are diagnostics, not qualified timing rows.",
        statistics="Manual Fraction means, sorted median/min/max and unbiased sample variance/SEM over all11 fixed raw block means; ns-to-us divide1000. No discarded observations or formal speed ratio.",
        local_build_artifacts=local_artifacts, files=files, rows=reviewed)
    destination=arguments.output if arguments.output.is_absolute() else ROOT/arguments.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(proof,indent=2,allow_nan=False)+"\n")
    print(json.dumps(dict(audit_status=proof["audit_status"],checks=check_count,errors=errors,
        qualified_rows=len(proof["accepted_rows"]),rejected_rows=len(proof["rejected_rows"]),
        distinct_complex_fields=6048,finite_mismatches=74,nonfinite_fields=195,
        total_timed_calls=total_timed_calls,review_output=str(destination.relative_to(ROOT)),
        review_sha256=hashlib.sha256(destination.read_bytes()).hexdigest()),indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
