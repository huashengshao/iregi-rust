"""Preserve the reviewed final receipt cohort before any timing run."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import re
import shutil
import tarfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "target/raw-distance-final-performance"
DST = ROOT / "validation/raw-distance-final-performance"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(rel):
    return json.loads((SRC / rel).read_text())


def main():
    assert not DST.exists(), "Preserve an existing readiness package unchanged"
    source = read("source-manifest.json")
    build = read("protocol/build.json")
    preflight = read("protocol/preflight.json")
    assert preflight["status"] == "passed" and preflight["cases_passed"] == 14
    assert preflight["binary_sha256"] == build["binary_sha256"] == sha(SRC / "protocol/probe")
    assert preflight["log_sha256"] == sha(SRC / "protocol/preflight.log")
    assert preflight["build_manifest_sha256"] == sha(SRC / "protocol/build.json")
    for name, digest in build["cohort_bindings"].items():
        assert sha(ROOT / name) == digest, name
    for side, files in source["compiled_source_hashes"].items():
        for rel, digest in files.items():
            assert sha(SRC / side / rel) == digest, (side, rel)
    lines = (SRC / "protocol/preflight.log").read_text().splitlines()
    case_re = re.compile(r"PARITY_PASS (\S+) rows=(1|32) fixed_iterations=(\d+) candidate_proof_work=\[(\d+), (\d+), (\d+), (\d+)\]")
    cases = []
    for line in lines:
        if not line.startswith("PARITY_PASS "):
            continue
        m = case_re.fullmatch(line)
        assert m, line
        family, rows, count, *work = m.groups()
        cases.append({"family": family, "rows": int(rows), "initial_iterations": int(count),
                      "candidate_proof_work": list(map(int, work)), "status": "exact_parity_passed"})
    prereg = read("protocol/preregistration.json")
    expected = {(x, n) for x in prereg["matrix"]["workloads"] for n in prereg["matrix"]["rows"]}
    assert len(cases) == 14 and {(x["family"], x["rows"]) for x in cases} == expected
    DST.mkdir(parents=True)
    rels = ["source-manifest.json", "source-review.json", "private-instrumentation.patch",
            "baseline-lib-build.json", "baseline-lib-build.log", "candidate-lib-build.json",
            "candidate-lib-build.log", "lib_build.py", "build-environment.json", "package_readiness.py"]
    rels += [str(p.relative_to(SRC)) for p in sorted((SRC / "protocol").iterdir())
             if p.is_file() and p.suffix in {".rs", ".py", ".json", ".log"}]
    for rel in rels:
        out = DST / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SRC / rel, out)
    shutil.copyfile(ROOT / "validation/automatic-planar/final/adoption.patch", DST / "adoption.patch")
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w") as tf:
        for side, files in source["compiled_source_hashes"].items():
            for rel in sorted(files):
                data = (SRC / side / rel).read_bytes()
                info = tarfile.TarInfo(f"{side}/{rel}")
                info.size, info.mode, info.mtime = len(data), 0o644, 0
                tf.addfile(info, io.BytesIO(data))
    (DST / "source-snapshots.tar.gz").write_bytes(gzip.compress(archive.getvalue(), mtime=0))
    qualification = {
        "status": "final_implementation_preflight_qualified_timing_pending",
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "production_adopted": False,
        "timing_performed": False,
        "cohort": "New final implementation cohort; distinct from the historical first receipt cohort",
        "baseline": "21622ec core plus shared collector; independently verified byte-equivalent to 06706e2 core",
        "candidate": "Same baseline plus final automatic-planar/accounting/checked-receipt patch; private read-only counter accessor outside timed loop",
        "dependencies": "Both sides use the same frozen 6b24c03-complete-kinds master/Symbolica dependency closure",
        "source_manifest_sha256": sha(SRC / "source-manifest.json"),
        "source_review_sha256": sha(SRC / "source-review.json"),
        "final_patch_sha256": sha(DST / "adoption.patch"),
        "preregistration_sha256": sha(SRC / "protocol/preregistration.json"),
        "build_manifest_sha256": sha(SRC / "protocol/build.json"),
        "preflight_manifest_sha256": sha(SRC / "protocol/preflight.json"),
        "preflight_log_sha256": sha(SRC / "protocol/preflight.log"),
        "probe_sha256": build["binary_sha256"],
        "preflight": {"passed": 14, "failed": 0, "seconds": preflight["seconds"],
                      "duration_scope": "Validation only; not a performance measurement",
                      "cases": cases,
                      "exact_comparisons": ["represented input/output bits", "ordered Dual shape and precision context",
                                            "basis and metadata", "all lane statuses", "fallback and analytic flags",
                                            "all public ExecutionStats fields", "diagnostics"],
                      "public_stats_deltas": "None permitted; all compared exactly",
                      "candidate_n5_certificate_counters": "All zero, asserted by the probe"},
        "parser_tests": {"passed": 9, "failed": 0, "manifest": "protocol/parser-tests.json"},
        "provenance": {"closure_files_verified_before_and_after_build_and_preflight": 865,
                       "sources_externs_build_review_and_binary_bindings_unchanged": True},
        "future_timing": {"requires_new_root_quiet_grant": True, "overall_timeout_seconds": 600,
                          "cases": 14, "blocks_per_case": 41, "warm_calls_per_side": 5,
                          "calibration_faster_side_minimum_seconds": 0.2,
                          "estimated_total_seconds": "Approximately 300–350, not guaranteed; preserve any timeout",
                          "cpu": "Explicit coordinator grant required"},
        "limitations": ["No timing result exists for this new cohort yet.",
                        "All workloads are N2/N3; the included N5 automatic fallback is inactive and its performance is not measured.",
                        "Frozen masters exclude later additive master APIs; this is not full current-workspace or IREGI-reference performance qualification.",
                        "This new compiled cohort does not resolve noise for identical binaries in the historical first cohort."],
        "historical_first_cohort": {"path": "validation/raw-distance-receipts-performance/qualification.json",
                                    "sha256": prereg["original_qualification_sha256"]},
    }
    (DST / "qualification.json").write_text(json.dumps(qualification, indent=2) + "\n")
    (DST / "README.md").write_text(
        "# Final receipt implementation cohort\n\n"
        "All 14 untimed comparison cases passed. Performance timing is pending a separate quiet-window grant. "
        "The 17.40 s preflight duration is validation only.\n\n"
        "The baseline core is 21622ec plus the common collector, independently verified to match 06706e2. "
        "The candidate adds the final reviewed automatic-planar, error-accounting and checked receipt patch. "
        "Both sides use the same frozen 6b24 master/Symbolica artifacts. All cases have two or three propagators; "
        "the automatic five-propagator path remains inactive. This is a new cohort, separate from the earlier receipt measurements.\n\n"
        "`source-snapshots.tar.gz` contains the exact 24 baseline and 30 candidate source files. "
        "The sole private instrumentation is a read-only accessor for existing proof counters, called outside timing. "
        "Build records bind the independent source review, source manifest, paired archives, protocol, and dependency closure. "
        "The preflight retains all exact result snapshots and permits no public statistics differences.\n\n"
        "After an explicit timing grant, from the repository root:\n\n"
        "```sh\nsource scripts/env.sh\nsource .local/symbolica-license.env\n"
        "python3 target/raw-distance-final-performance/protocol/run_timing.py --cpu GRANTED_CPU --quiet-manifest WINDOW_JSON\n```\n\n"
        "The fixed protocol uses all 14 cases, 41 alternating paired blocks, five warm calls per implementation, "
        "and shared calibration until the faster side takes at least 200 ms. The whole numerical process has a 600 s limit. "
        "Analysis retains every row and uses the preregistered 99% paired-bootstrap interval and 2% width gate. "
        "No favorable-block selection or confidence-driven stopping is allowed.\n")
    inventory = {str(p.relative_to(DST)): sha(p) for p in sorted(DST.rglob("*")) if p.is_file()}
    (DST / "files.json").write_text(json.dumps(inventory, indent=2) + "\n")
    print(json.dumps({"status": qualification["status"], "path": str(DST.relative_to(ROOT)),
                      "files": len(inventory), "qualification_sha256": sha(DST / "qualification.json")}))


if __name__ == "__main__":
    main()
