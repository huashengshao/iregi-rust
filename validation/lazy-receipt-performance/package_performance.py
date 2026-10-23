"""Preserve the single completed eager/lazy cohort; never run or repeat timings."""
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile

ROOT = Path.cwd()
SRC = ROOT / "target/raw-distance-lazy-capture-optimized"
DST = ROOT / "validation/lazy-receipt-performance"
QUIET = ROOT / "validation/benchmark-quiet/20261023e"
SHARED = ROOT / "target/selected-native-optimized"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    assert not DST.exists(), "Preserve existing qualification; do not overwrite"
    run = read(SRC / "protocol/performance-run.json")
    analysis = read(SRC / "protocol/performance-analysis.json")
    review = read(SRC / "review/statistics-review.json")
    assert review["status"] == "passed", review["status"]
    assert run["status"] == "passed" and run["provenance_qualified"]
    assert run["cases_passed"] == 14 and run["measurement_rows"] == 1148
    assert run["exit_code"] == 0 and not run["timed_out"]
    assert run["protocol_validated"] and run["seconds"] <= 600
    for name, field in [("performance.csv", "raw_csv_sha256"), ("performance.log", "log_sha256"),
                        ("analyze.py", "analysis_source_sha256"), ("protocol.py", "protocol_source_sha256"),
                        ("preregistration.json", "preregistration_sha256")]:
        assert sha(SRC / "protocol" / name) == run[field], name
    for name in ["performance-run.json", "performance.csv", "performance.log", "analyze.py", "run_timing.py"]:
        assert sha(SRC / "protocol" / name) == sha(QUIET / "lazy-capture" / name), name
    assert sha(QUIET / "window.json") == run["quiet_manifest_initial_sha256"] == run["quiet_manifest_final_sha256"]
    counts = dict(Counter(r["classification"] for r in analysis["results"]))
    for key in ["improvement", "parity", "regression", "inconclusive-noise"]:
        counts.setdefault(key, 0)
    assert counts == {"improvement": 5, "parity": 6, "regression": 3, "inconclusive-noise": 0}
    assert len(analysis["results"]) == 14 and all(r["ci_width_qualified"] for r in analysis["results"])
    DST.mkdir(parents=True)
    copied = {}

    def copy(source, relative):
        path = DST / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, path)
        digest = sha(source)
        assert sha(path) == digest
        copied[relative] = {"source": str(source.relative_to(ROOT)), "sha256": digest}

    for name in ["source-manifest.json", "build.py", "freeze.py", "probe.rs", "preflight.py", "preflight.json", "preflight.log",
                 "readiness.json", "readiness-qualified.json", "timing-ready.json", "package_performance.py", "verify.py"]:
        copy(SRC / name, name)
    for name in ["source-review.json", "runtime-review.json", "protocol-review.json", "statistics-review.json"]:
        copy(SRC / "review" / name, "review/" + name)
    for name in ["build.json", "eager.log", "lazy.log", "probe.log"]:
        copy(SRC / "build-001" / name, "build/" + name)
    for name in ["analyze.py", "protocol.py", "test_protocol.py", "preregistration.json", "manifest.json", "parser-admission.json",
                 "run_timing.py", "freeze_readiness.py", "performance-run.json", "performance.csv", "performance.log",
                 "performance-analysis.json", "analysis.stdout.json"]:
        copy(SRC / "protocol" / name, "protocol/" + name)
    for name in ["window.json", "completion.json", "cpu-survey.json", "cpu-survey-v2.json"]:
        copy(QUIET / name, "quiet-window/" + name)
    for name in ["closure-audit.json", "plan.md", "plan-binding.json", "build_shared.py", "shared/accepted.json", "shared/build-001/build.json", "shared/build-001/compiler.log"]:
        copy(SHARED / name, "shared-adapter/" + name)
    closure = ROOT / "target/benchmark/dependency-closures/6b24c03-complete-kinds"
    for name in ["manifest.json", "completed-workspace-build.json", "workspace-completion.json"]:
        copy(closure / name, "numerical-closure/" + name)
    for source, name in [(ROOT / "validation/raw-distance-lazy-capture/candidate.patch", "lazy.patch"),
                         (ROOT / "validation/automatic-planar/final/adoption.patch", "eager-final.patch"),
                         (ROOT / "validation/raw-distance-lazy-capture/qualification.json", "debug-correctness.json"),
                         (ROOT / "validation/raw-distance-final-performance/performance-qualification.json", "eager-final-performance.json"),
                         (ROOT / "validation/selected-native-reduction/qualification.json", "shared-master-source-qualification.json")]:
        copy(source, "prior-evidence/" + name)

    # Exact source snapshots only. Large binary archives remain hash-bound, not copied into Git.
    sources = {}
    manifest = read(SRC / "source-manifest.json")
    for name, digest in manifest["source_files"].items():
        sources[name] = {"path": SRC / name, "sha256": digest}
    master_root = ROOT / "target/selected-native-reduction/copied/crates/iregi-masters"
    for name, digest in read(SHARED / "shared/build-001/build.json")["inputs"].items():
        path = Path(name)
        if path.is_relative_to(master_root):
            sources["shared-masters/" + str(path.relative_to(master_root))] = {"path": path, "sha256": digest}
    with (DST / "source-snapshots.tar.gz").open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, filename="", mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for name, entry in sorted(sources.items()):
                    data = entry["path"].read_bytes()
                    assert hashlib.sha256(data).hexdigest() == entry["sha256"], name
                    info = tarfile.TarInfo(name)
                    info.size, info.mode, info.mtime = len(data), 0o644, 0
                    archive.addfile(info, io.BytesIO(data))
    save(DST / "source-archive-manifest.json", {name: {"source": str(v["path"].relative_to(ROOT)), "sha256": v["sha256"]} for name, v in sorted(sources.items())})
    save(DST / "copy-map.json", copied)
    readiness = read(SRC / "readiness-qualified.json")
    window = read(QUIET / "window.json")
    qualification = {
        "status": "completed_private_lazy_vs_eager_cohort_with_three_qualified_regressions",
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "production_adopted": False,
        "recommendation": "Do not adopt this lazy-capture patch under the all-family no-regression criterion: three retained cases have qualified regressions. No repeat is authorized or recommended from these observations alone.",
        "ratio_definition": "TIRust(lazy) / TIRust(eager), below one is faster",
        "baseline": "Final reviewed eager automatic-planar/accounting/checked-receipt implementation, e23ce191 patch over the common 06706e2-equivalent core and collector",
        "candidate": "Same baseline plus the qualified lazy receipt capture patch; no numerical operation, threshold, conditioning or result changes",
        "scope": analysis["scope"],
        "correctness": {"optimized_preflight_pairs_passed": 14, "unique_complex_output_slots": 10560,
                        "snapshot_calls_per_side_per_case": 7, "parser_admission_tests_passed": 9,
                        "exact_inputs_outputs_context_metadata_status_flags_statistics_and_proof_counters": True,
                        "warm_and_post_timing_snapshot_checks_passed": True,
                        "n5_automatic_fallback_inactive": True, "default_master_backend": "SymbolicaBatch",
                        "prior_debug_tests_passed": 26, "prior_debug_pairs_passed": 14,
                        "debug_tests_rerun_in_optimized_binary": False},
        "build": {"flags": readiness["flags"], "steps": readiness["build"]["steps"],
                  "outputs": readiness["build"]["outputs"], "source_files_in_archive": len(sources)},
        "performance": {"exit_code": 0, "timed_out": False, "seconds_including_preparation_and_calibration": run["seconds"],
                        "bound_seconds": 600, "cases": 14, "paired_blocks_per_case": 41, "observations": 1148,
                        "calibration_min_faster_side_seconds": 0.2, "warm_calls_per_side": 5,
                        "baseline_first_blocks": 21, "candidate_first_blocks": 20,
                        "measurement_scope": "Entire reduce_batch call including result construction/drop; preparation, calibration and snapshots excluded from block latency",
                        "timed_status_scope": "Top-level Result unwrap each iteration; full lane status and output parity before/after, not inside every timed iteration",
                        "no_case_omitted": True, "no_ci_adaptive_stopping_or_retry": True,
                        "counts": counts, "all_intervals_pass_width_gate": True,
                        "method": analysis["method"], "classification_gate": analysis["classification_gate"], "results": analysis["results"]},
        "provenance": {"qualified": run["provenance_qualified"], "run_sha256": sha(SRC / "protocol/performance-run.json"),
                       "analysis_sha256": sha(SRC / "protocol/performance-analysis.json"), "raw_csv_sha256": run["raw_csv_sha256"],
                       "log_sha256": run["log_sha256"], "probe_sha256": run["binary_sha256"],
                       "source_manifest_sha256": sha(SRC / "source-manifest.json"),
                       "shared_master_artifact": read(SHARED / "shared/accepted.json")["artifact"],
                       "independent_statistics_review": {"path": "review/statistics-review.json", "sha256": sha(SRC / "review/statistics-review.json")},
                       "committed_pause_copies_byte_identical": True, "quiet_window_sha256": sha(QUIET / "window.json"),
                       "quiet_completion_sha256": sha(QUIET / "completion.json")},
        "host_context": {"cpu": 254, "pre_window_cpu_busy_fraction": window["survey"]["cpu_busy_fraction"],
                         "project_policy": window["project_policy"], "external_host_policy": window["external_host_policy"]},
        "limitations": [
            "This is an internal eager/lazy comparison, not an original IREGI or COLLIER performance comparison; overall user performance acceptance remains open.",
            "All cases are N2/N3 with binary64 base values, including flattened mixed Dual. No higher-point automatic fallback, DoubleFloat or arbitrary-precision performance is measured.",
            "The previous eager-final-versus-core-baseline cohort and its two regressions remain unchanged. Ratios from different cohorts must not be multiplied or relabeled as direct comparisons.",
            "The shared adapter includes separately qualified opt-in native capability, but neither receipt variant selects it. The separate Symbolica arity-two candidate is excluded.",
            "External host activity was uncontrolled. Classifications are conditional on this single fixed run; percentile bootstrap intervals are not simultaneous familywise guarantees.",
            "Parity means the interval includes one; it is not a proof of equivalence or satisfaction of the user's overall performance requirement.",
            "Build and numerical preparation seconds are validation measurements, not performance comparisons.",
            "Historical readiness, source and quiet-completion records retain their original pending/unmeasured labels; this append-only qualification records the later analysis.",
            "Full runtime binaries and dependency archives remain external hash-bound artifacts; source snapshots, commands, features, compiler/linker identities and raw-analysis inputs are retained here."
        ],
    }
    save(DST / "qualification.json", qualification)
    lines = ["# Lazy receipt capture performance", "", "The fixed optimized cohort contains **five qualified improvements, six parity results, and three qualified regressions**. All 14 intervals meet the preregistered 2% width gate. The lazy patch is not recommended for adoption under the all-family no-regression criterion; production is unchanged.", "",
             "Every displayed ratio is **TIRust(lazy) / TIRust(eager)**; below one is faster. The paired variants use the same accepted current master adapter and unchanged opt3 numerical dependencies. This is not an IREGI/COLLIER comparison.", "",
             "| Workload | Batch | Lazy / eager | 99% interval | Relative width | Classification |",
             "|---|---:|---:|---:|---:|---|"]
    for row in analysis["results"]:
        lo, hi = row["latency_ratio_ci99"]
        lines.append(f"| {row['workload']} | {row['rows']} | {row['candidate_over_baseline_latency_ratio']:.6f} | [{lo:.6f}, {hi:.6f}] | {row['relative_ci_width']*100:.3f}% | {row['classification']} |")
    lines += ["", "The single 256.685 s process completed all 1,148 observations (14 cases × 41 paired blocks), below the fixed 600 s bound. Five warm calls precede shared-count calibration to at least 200 ms on the faster side. Order alternates, with 21 eager-first and 20 lazy-first blocks. All cases, calibration trials and outcomes are retained; there were no timing retries or confidence-driven omissions.", "",
              "The reported statistic is a median paired log ratio with 20,000 paired bootstrap resamples, seed 14050301 and a 99% percentile interval. Parity means the interval includes one, not proof of equivalence. This is a per-case conditional classification, not a familywise guarantee. The coordinator serialized project computation on CPU 254; the pre-window survey observed 0.664% CPU busy, and unrelated host activity was uncontrolled.", "",
              "Optimized preflight compared all 14 exact snapshots (10,560 complex slots), ordered precision/Taylor context, metadata, status, flags, public statistics and proof counters. Both variants also checked exact cold/warm/final snapshots in the timing process. Each timed iteration checks the top-level Result; full lane-status parity is checked outside the timed blocks. The prior 26 debug tests remain separately qualified and were not rerun in the optimized binary.", "",
              "All workloads have two or three propagators, including flattened mixed Dual cases. Automatic N5 fallback is inactive. Both sides use SymbolicaBatch by default; no native-selection or arity-two dependency candidate is included. The earlier eager-final-versus-core cohort, including its two regressions, remains separate and unchanged; cross-cohort ratios must not be multiplied.", "",
              "To verify the retained package (no numerical runtime):", "", "```sh", "python3 validation/lazy-receipt-performance/verify.py", "```", "",
              "To reproduce the frozen analysis from retained raw inputs (no timing):", "", "```sh", "python3 validation/lazy-receipt-performance/protocol/analyze.py", "```", "",
              "`source-snapshots.tar.gz` contains all 61 eager/lazy core files plus 26 shared-adapter source files. `source-manifest.json`, `build/build.json`, and `shared-adapter/` retain exact commands, flags and dependency identities. Rebuilding requires the matching external hash-bound numerical archives; the original scripts intentionally retain their historical workspace paths. New builds or timings require a separate authorized experiment and must not overwrite this evidence.", "",
              "`readiness*.json`, `timing-ready.json`, and `quiet-window/completion.json` are historical immutable snapshots. Their pending/unmeasured labels describe their creation time; `qualification.json` is the final append-only analysis record. No license key or secret is included.", ""]
    (DST / "README.md").write_text("\n".join(lines))
    inventory = {str(p.relative_to(DST)): sha(p) for p in sorted(DST.rglob("*")) if p.is_file() and p.name != "files.json"}
    save(DST / "files.json", inventory)
    print(json.dumps({"status": qualification["status"], "files": len(inventory), "source_files": len(sources),
                      "qualification_sha256": sha(DST / "qualification.json"), "files_sha256": sha(DST / "files.json"), "counts": counts}))


if __name__ == "__main__":
    main()
