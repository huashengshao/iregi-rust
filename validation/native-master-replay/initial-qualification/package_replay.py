"""Extend the immutable capture bundle with a separately qualified raw replay."""
from pathlib import Path
import hashlib
import json
import shutil
from replay_parser import validate_rows

ROOT = Path.cwd()
BASE = ROOT / "target/native-master-replay"
DEST = ROOT / "validation/native-master-replay"
sha = lambda path: hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
capture = json.loads((BASE / "capture-results.json").read_text())
capture_qualification = json.loads((BASE / "capture-qualification.json").read_text())
assert capture_qualification["captures_sha256"] == sha(BASE / "capture-results.json")
assert sha(DEST / "capture-results.json") == sha(BASE / "capture-results.json")
assert sha(DEST / "capture-qualification.json") == sha(BASE / "capture-qualification.json")
build = json.loads((BASE / "replay-build.json").read_text())
assert build["exit_code"] == 0 and build["sources_before"] == build["sources_after"]
assert sha(BASE / "replay") == build["binary_sha256"]
for name, expected in build["sources_before"].items():
    assert sha(BASE / name) == expected
phases = ["initial"]
timed = (BASE / "replay-timing-summary.json").exists()
if timed:
    phases += ["before", "after"]
rows_by_phase = {}
for phase in phases:
    stem = f"replay-qualification-{phase}"
    result = json.loads((BASE / f"{stem}.json").read_text())
    assert result["status"] == "passed" and result["binary_sha256"] == build["binary_sha256"]
    assert result["jsonl_sha256"] == sha(BASE / f"{stem}.jsonl")
    assert result["runner_sha256"] == sha(BASE / "run_replay.py")
    assert result["parser_sha256"] == sha(BASE / "replay_parser.py")
    rows = [json.loads(line) for line in (BASE / f"{stem}.jsonl").read_text().splitlines()]
    validate_rows(rows, capture, False)
    rows_by_phase[phase] = rows
initial = rows_by_phase["initial"]
for rows in rows_by_phase.values():
    for actual, expected in zip(rows, initial):
        assert actual["result"]["represented_outputs"] == expected["result"]["represented_outputs"]
summary = {
    "status": "numerical-replay-qualified-timing-pending",
    "scope": "Unchanged selected A0/B0/C0 native versus Symbolica on actual ordinary binary64 core master bundles; no D0/Dual/higher-precision/complete-reduction timing claim.",
    "production_changed": False, "capture_qualification_sha256": sha(BASE / "capture-qualification.json"),
    "build_sha256": sha(BASE / "replay-build.json"), "binary_sha256": build["binary_sha256"],
    "qualification_records": {phase: sha(BASE / f"replay-qualification-{phase}.json") for phase in phases},
    "total_cases": len(initial), "total_master_rows": sum(group["rows"] for row in initial for group in row["result"]["groups"]),
    "total_complex_outputs": sum(group["complex_outputs"] for row in initial for group in row["result"]["groups"]),
    "maximum_normalized_error": max(group["max_normalized_error"] for row in initial for group in row["result"]["groups"]),
    "represented_component_differences": sum(group["represented_component_differences"] for row in initial for group in row["result"]["groups"]),
    "signed_zero_differences": sum(group["signed_zero_differences"] for row in initial for group in row["result"]["groups"]),
    "public_symbolica_outputs": "All first five coefficients match captured public outputs exactly, including zero signs; all six finite; ordinary derivative coefficient zero; own backend outputs repeat bitwise.",
    "parser_controls": "31 independent malformed controls rejected; complete synthetic qualification and timing schemas accepted. Synthetic timings are not measurements.",
    "failed_build_attempt": "earlier-attempts/replay-001-missing-trait/failure.json",
}
if timed:
    timing = json.loads((BASE / "replay-timing-summary.json").read_text())
    assert timing["status"] == "passed"
    assert timing["raw_sha256"] == sha(BASE / "replay-timing.jsonl")
    raw = [json.loads(line) for line in (BASE / "replay-timing.jsonl").read_text().splitlines()]
    validate_rows(raw, capture, True)
    for actual, expected in zip(raw, initial):
        assert actual["result"]["represented_outputs"] == expected["result"]["represented_outputs"]
    summary.update(status="numerical-replay-and-raw-timing-qualified", timing_summary_sha256=sha(BASE / "replay-timing-summary.json"), gates=timing["gates"],
                   decision="Diagnostic raw-kernel evidence only. No production adoption or whole-core parity inferred.")
(BASE / "replay-qualification.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
names = ["README.md", "build_replay.py", "run_replay.py", "replay_parser.py", "test_replay_parser.py", "parser-tests.log",
         "analyze_replay.py", "test_replay_analyzer.py", "analyzer-admission-tests.log", "benchmark_helper.py", "statistics-source.json", "package_replay.py", "replay-build.json",
         "replay-build.log", "replay-qualification.json"]
names += [f"replay-qualification-{phase}.{extension}" for phase in phases for extension in ["json", "jsonl", "log"]]
if timed:
    names += ["replay-timing.json", "replay-timing.jsonl", "replay-timing.log", "replay-timing-summary.json", "analysis.log"]
for name in names:
    if (BASE / name).exists():
        shutil.copy2(BASE / name, DEST / name)
shutil.copytree(BASE / "source", DEST / "source", dirs_exist_ok=True)
attempt = "earlier-attempts/replay-001-missing-trait"
shutil.copytree(BASE / attempt, DEST / attempt, dirs_exist_ok=True)
files = [{"path": str(path.relative_to(DEST)), "sha256": sha(path), "bytes": path.stat().st_size}
         for path in sorted(DEST.rglob("*")) if path.is_file() and path.name != "manifest.json"]
(DEST / "manifest.json").write_text(json.dumps({"scope": summary["scope"], "files": files}, indent=2) + "\n")
print(json.dumps({"files": len(files), "qualification": summary,
                  "qualification_sha256": sha(DEST / "replay-qualification.json"),
                  "manifest_sha256": sha(DEST / "manifest.json")}, indent=2))
