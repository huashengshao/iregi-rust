"""Append final timing evidence without changing the quiet-window readiness record."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "target/raw-distance-final-performance"
DST = ROOT / "validation/raw-distance-final-performance"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def copy_new(source, relative):
    destination = DST / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        assert sha(source) == sha(destination), relative
    else:
        shutil.copyfile(source, destination)


def main():
    assert not (DST / "performance-qualification.json").exists(), "Preserve the completed cohort"
    original_inventory = load(DST / "files.json")
    for rel, digest in original_inventory.items():
        assert sha(DST / rel) == digest, rel
    readiness = load(DST / "qualification.json")
    assert sha(DST / "qualification.json") == "fc1b60be95236bcefb912a4823126807e3bfb377881d1b6b8a5bfbc7be4027a7"
    run = load(SRC / "protocol/performance-run.json")
    analysis = load(SRC / "protocol/performance-analysis.json")
    review = load(SRC / "statistics-review.json")
    assert review["status"] == "independent_statistics_reconstruction_passed"
    for rel, digest in review["sources"].items():
        assert sha(ROOT / rel) == digest, rel
    assert run["status"] == "passed" and run["provenance_qualified"]
    assert run["cases_passed"] == 14 and run["exit_code"] == 0 and not run["timed_out"]
    assert run["binary_sha256"] == readiness["probe_sha256"]
    for name, key in [("performance.csv", "raw_csv_sha256"), ("performance.log", "log_sha256"),
                      ("analyze.py", "analysis_source_sha256"), ("protocol.py", "protocol_source_sha256"),
                      ("preregistration.json", "preregistration_sha256")]:
        assert sha(SRC / "protocol" / name) == run[key], name
    assert len(analysis["results"]) == 14
    assert len((SRC / "protocol/performance.csv").read_text().splitlines()) == 14 * 41 * 2 + 1
    for name in ["performance-run.json", "performance.csv", "performance.log", "performance-analysis.json", "analysis.log"]:
        copy_new(SRC / "protocol" / name, f"protocol/{name}")
    for name in ["preflight-review.json", "statistics-review.json", "package_performance.py"]:
        copy_new(SRC / name, name)
    quiet = ROOT / "validation/benchmark-quiet/20261023d"
    for name in ["window.json", "completion.json", "cpu-survey.json"]:
        copy_new(quiet / name, f"quiet-window/{name}")
    window = load(quiet / "window.json")
    assert sha(quiet / "window.json") == run["quiet_manifest_initial_sha256"]
    assert sha(quiet / "cpu-survey.json") == window["survey"]["sha256"]
    counts = dict(Counter(r["classification"] for r in analysis["results"]))
    for classification in ["improvement", "parity", "regression", "inconclusive-noise"]:
        counts.setdefault(classification, 0)
    assert counts == review["counts"]
    qualification = {
        "status": "completed_final_implementation_cohort_with_qualified_control_regressions",
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "production_adopted": False,
        "recommendation": "Do not adopt on an all-family no-regression criterion; retain the two qualified ordinary-control regressions.",
        "cohort": readiness["cohort"],
        "baseline": readiness["baseline"],
        "candidate": readiness["candidate"],
        "dependencies": readiness["dependencies"],
        "readiness": {"path": "qualification.json", "sha256": sha(DST / "qualification.json")},
        "correctness": {"preflight_pairs_passed": 14, "parser_tests_passed": 9,
                        "exact_input_output_context_public_metadata_and_stats_parity": True,
                        "inactive_n5_certificate_counters": True,
                        "preflight_review_bindings_rehashed": 80,
                        "preflight_review_sha256": sha(SRC / "preflight-review.json")},
        "performance": {"process_seconds_including_preparation_calibration": run["seconds"],
                        "timeout_seconds": 600, "exit_code": 0, "timed_out": False,
                        "registered_cases": 14, "observed_cases": 14, "paired_blocks_per_case": 41,
                        "observations": 14 * 41 * 2, "warm_calls_per_side_per_case": 5,
                        "calibration_faster_side_minimum_seconds": 0.2,
                        "no_case_dropped": True, "no_confidence_driven_stopping_or_repeat": True,
                        "classification_counts": counts,
                        "all_intervals_pass_width_gate": all(r["ci_width_qualified"] for r in analysis["results"]),
                        "method": analysis["method"], "classification_gate": analysis["classification_gate"],
                        "results": analysis["results"]},
        "provenance": {"probe_sha256": run["binary_sha256"],
                       "source_manifest_sha256": readiness["source_manifest_sha256"],
                       "source_review_sha256": readiness["source_review_sha256"],
                       "final_patch_sha256": readiness["final_patch_sha256"],
                       "run_sha256": sha(SRC / "protocol/performance-run.json"),
                       "analysis_sha256": sha(SRC / "protocol/performance-analysis.json"),
                       "raw_csv_sha256": run["raw_csv_sha256"], "log_sha256": run["log_sha256"],
                       "closure_files_verified_before_and_after": 865,
                       "provenance_qualified": run["provenance_qualified"],
                       "quiet_window_sha256": sha(quiet / "window.json"),
                       "quiet_completion_sha256": sha(quiet / "completion.json")},
        "independent_statistical_review": {"path": "statistics-review.json", "sha256": sha(SRC / "statistics-review.json"),
                                           "status": review["status"]},
        "host_context": {"cpu": 254, "project_heavy_work_serialized": True,
                         "external_host_policy": window["external_host_policy"],
                         "pre_window_cpu_busy_percent": 27.7,
                         "limitation": "External host activity was uncontrolled; interval classification is conditional on this fixed observed cohort."},
        "limitations": ["This is a new final-patch cohort and does not resolve noise for the historical binaries.",
                        "All measured cases have two or three propagators; automatic N5 fallback remains inactive.",
                        "Both sides use frozen6b24 master/Symbolica dependencies; later additive master APIs and the full current workspace are outside scope.",
                        "This internal paired comparison is not a benchmark against original IREGI and does not establish overall user performance acceptance.",
                        "Strong gains in proof-reuse cases do not erase ordinary-control regressions, and gains must not be multiplied by other optimization cohorts."],
        "historical_first_cohort": readiness["historical_first_cohort"],
    }
    (DST / "performance-qualification.json").write_text(json.dumps(qualification, indent=2) + "\n")
    rows = ["# Final receipt implementation performance", "", 
            "The fixed final-patch cohort completed all 14 cases: **11 qualified improvements, one parity result, and two qualified regressions**. "
            "Every 99% interval meets the preregistered 2% width gate. The result does not meet an all-family no-regression criterion; no production adoption is recorded.", "",
            "The 325.77 s run includes preparation and calibration; reported batch latencies exclude those stages. "
            "All 1,148 observations are retained (14 cases × 41 alternating pairs). No case was dropped or repeated based on confidence intervals.", "",
            "| Workload | Batch | Candidate / baseline | 99% interval | Relative interval width | Classification |",
            "|---|---:|---:|---:|---:|---|"]
    for r in analysis["results"]:
        lo, hi = r["latency_ratio_ci99"]
        rows.append(f"| {r['workload']} | {r['rows']} | {r['candidate_over_baseline_latency_ratio']:.6f} | [{lo:.6f}, {hi:.6f}] | {100*r['relative_ci_width']:.3f}% | {r['classification']} |")
    rows += ["", "Baseline: the 06706e2-equivalent core. Candidate: the same core plus the final reviewed automatic-planar, accounting, and checked-receipt patch. "
             "Both use the same frozen 6b24 master/Symbolica archives. Every case is N2/N3, so N5 fallback is inactive. "
             "All pre/post comparisons retain exact input/output bits, contexts, public metadata/statistics, flags, and diagnostics.", "",
             "The coordinator serialized project work on CPU254. External host activity was uncontrolled; the pre-window survey recorded 27.7% busy on that CPU. "
             "The raw observations, calibration records, immutable window manifest, source/binary bindings, and independent review are retained.", "",
             "`qualification.json` remains the original readiness record referenced by the immutable quiet-window manifest. "
             "`performance-qualification.json` records the completed new cohort. The historical first-cohort receipt measurements remain separate. "
             "No IREGI-reference performance parity or multiplication of separate optimization gains follows from this comparison.", ""]
    (DST / "PERFORMANCE.md").write_text("\n".join(rows))
    inventory = {str(p.relative_to(DST)): sha(p) for p in sorted(DST.rglob("*")) if p.is_file() and p.name != "performance-files.json"}
    (DST / "performance-files.json").write_text(json.dumps(inventory, indent=2) + "\n")
    print(json.dumps({"status": qualification["status"], "files": len(inventory),
                      "qualification_sha256": sha(DST / "performance-qualification.json"), "counts": counts}))


if __name__ == "__main__":
    main()
