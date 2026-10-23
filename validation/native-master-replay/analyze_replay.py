"""Retain all eight requested bundles, with explicit raw-kernel-only scope."""
from pathlib import Path
import hashlib
import json
import math
from collections import Counter
from benchmark_helper import summarize, ratio_summary
from replay_parser import validate_rows

BASE = Path(__file__).parent
sha = lambda path: hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
helper = json.loads((BASE / "statistics-source.json").read_text())
assert sha(BASE / "benchmark_helper.py") == helper["sha256"]
capture = json.loads((BASE / "capture-results.json").read_text())
run = {}
raw = []
admission_error = None
try:
    run = json.loads((BASE / "replay-timing.json").read_text())
    assert sha(BASE / "replay-timing.jsonl") == run["jsonl_sha256"]
    assert sha(BASE / "capture-results.json") == run["capture_sha256"]
    assert sha(BASE / "replay_parser.py") == run["parser_sha256"]
    assert sha(BASE / "run_replay.py") == run["runner_sha256"]
    assert run["initial_outputs_bitwise_unchanged"] is True
    assert run["initial_qualification_sha256"] == sha(BASE / "replay-qualification-initial.json")
    raw = [json.loads(line) for line in (BASE / "replay-timing.jsonl").read_text().splitlines()]
    assert run["status"] == "passed", run.get("validation_errors")
    validate_rows(raw, capture, True)
except Exception as error:
    admission_error = str(error)

DEFINITION = ("Native / Symbolica paired block latency on identical actual master bundles; "
              "99% bootstrap median interval, 10000 resamples, seed173; "
              "CI width must be <=2% of median for a definitive classification")


def ratio(candidate, baseline):
    result = ratio_summary(candidate, baseline, {"status": "passed"})
    assert all(math.isfinite(value) and value > 0 for value in result["samples"])
    result["definition"] = DEFINITION
    return result


rows = []
for original in capture["rows"]:
    entry = {"id": original["id"], "outer_batch": original["outer_batch"],
             "ordered_groups": [{"family": group["family"], "rows": group["rows"]}
                                for group in original["capture"]["master_captures"]],
             "status": "unqualified", "ratio": None}
    matches = [row for row in raw if (row.get("id"), row.get("outer_batch")) ==
               (entry["id"], entry["outer_batch"])]
    if admission_error is not None or len(matches) != 1:
        entry["error"] = admission_error or "missing or duplicate case"
    else:
        measured = matches[0]
        blocks = measured["result"]["timing"]["blocks"]
        baseline = [block["elapsed_ns"][0] / block["iterations"] for block in blocks]
        candidate = [block["elapsed_ns"][1] / block["iterations"] for block in blocks]
        strata = {}
        for first, label in [(0, "symbolica_first"), (1, "native_first")]:
            indices = [index for index, block in enumerate(blocks) if block["order"][0] == first]
            strata[label] = ratio([candidate[index] for index in indices], [baseline[index] for index in indices])
        entry.update(status="measured", symbolica=summarize(baseline), native=summarize(candidate),
                     ratio=ratio(candidate, baseline), order_strata=strata,
                     native_slower_pairs=sum(a > b for a, b in zip(candidate, baseline)),
                     blocks=len(blocks), iterations=measured["result"]["timing"]["iterations"],
                     numerical=measured["result"]["groups"],
                     preparation_ns=measured["result"]["preparation_ns"],
                     native_context_preparation_ns=measured["native_context_preparation_ns"])
    rows.append(entry)

result = {"status": "passed" if admission_error is None else "unqualified",
          "scope": "Raw selected unchanged A0/B0/C0 native kernels versus Symbolica on eight actual core master bundles. Adapter validation/allocation, recurrence and final contractions are excluded. No IREGI/end-to-end performance claim.",
          "definition": DEFINITION, "capture_sha256": sha(BASE / "capture-results.json"),
          "timing_record_sha256": sha(BASE / "replay-timing.json") if (BASE / "replay-timing.json").is_file() else None,
          "raw_sha256": sha(BASE / "replay-timing.jsonl") if (BASE / "replay-timing.jsonl").is_file() else None,
          "parser_sha256": sha(BASE / "replay_parser.py"), "analysis_sha256": sha(Path(__file__)),
          "statistics_source_sha256": helper["sha256"], "rows": rows,
          "gates": dict(Counter(row["ratio"]["gate"] if row["ratio"] else "unqualified" for row in rows)),
          "production_changed": False}
(BASE / "replay-timing-summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
print(json.dumps({"status": result["status"], "gates": result["gates"], "rows": [
    {"id": row["id"], "batch": row["outer_batch"], "ratio": row["ratio"]["median"] if row["ratio"] else None,
     "ci99": row["ratio"]["ci99"] if row["ratio"] else None,
     "gate": row["ratio"]["gate"] if row["ratio"] else "unqualified"} for row in rows]}, indent=2))
raise SystemExit(0 if result["status"] == "passed" else 1)
