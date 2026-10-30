#!/usr/bin/env python3
"""Append the direct-engine campaign to the report data and reseal the proof.

bind: append new top-level members to docs/data/results.json, preserving the
      raw spelling of every existing member (append-only, as the checker
      requires with --preserve-from).
seal: after rebuilding docs/benchmark.pdf and an independent byte-identical
      copy, refresh docs/data/report-validation.json: every listed report
      artifact is rehashed, the new records join the source ledger, and a new
      checkpoint entry keeps the previous proof hash.

usage: publish.py bind
       publish.py seal --independent-pdf PATH --page-count N --base-commit SHA
Run from the repository root.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RESULTS = ROOT / "docs/data/results.json"
PROOF = ROOT / "docs/data/report-validation.json"
REPORT_DATE = "2026-10-30"
RECORDS = {
    "direct_engine_20261030": ("summary.json", True),
    "direct_engine_20261030_build": ("build.json", True),
    "direct_engine_20261030_inputs": ("inputs.json", False),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind() -> None:
    text = RESULTS.read_text()
    existing = json.loads(text)
    additions = {}
    if "direct_engine_report_updated_on" not in existing:
        additions["direct_engine_report_updated_on"] = REPORT_DATE
    for key, (name, snapshot) in RECORDS.items():
        if key in existing:
            raise SystemExit(f"{key} already bound; results.json is append-only")
        path = HERE / name
        record = {"source": str(path.relative_to(ROOT)), "sha256": sha256(path)}
        if snapshot:
            record["snapshot"] = json.loads(path.read_text())
        additions[key] = record
    body = text.rstrip()
    if not body.endswith("}"):
        raise SystemExit("unexpected results.json layout")
    body = body[:-1].rstrip()
    for key, value in additions.items():
        body += ",\n  " + json.dumps(key) + ": " + json.dumps(value, indent=None)
    RESULTS.write_text(body + "\n}\n")
    json.loads(RESULTS.read_text())
    print(f"bound {len(additions)} records")


def seal(independent: Path, pages: int, base_commit: str) -> None:
    proof = json.loads(PROOF.read_text())
    previous_sha = sha256(PROOF)
    pdf = ROOT / "docs/benchmark.pdf"
    if pdf.read_bytes() != independent.read_bytes():
        raise SystemExit("independent rebuild differs from docs/benchmark.pdf")
    results = json.loads(RESULTS.read_text())
    artifacts = proof["report_artifacts"]
    for name in list(artifacts):
        artifacts[name] = sha256(ROOT / name)
    for name in ("scripts/build-benchmark-report.sh",):
        artifacts[name] = sha256(ROOT / name)
    ledger_keys = {record["key"] for record in proof["source_ledger"]}
    new_keys = []
    for key in RECORDS:
        record = results[key]
        if key not in ledger_keys:
            proof["source_ledger"].append({"key": key, "source": record["source"], "sha256": record["sha256"]})
            new_keys.append(key)
    proof["source_ledger_count"] = len(proof["source_ledger"])
    stamp = int(datetime.datetime.combine(datetime.date.fromisoformat(REPORT_DATE), datetime.time(),
                                          datetime.timezone.utc).timestamp())
    proof["recorded_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proof["status"] = "passed_direct_engine_same_session_report_rebuild"
    proof["scope"] = ("Direct numerical engine is the public binary64 default. New same-session interleaved "
                      "TIRust/original-IREGI/COLLIER tables (18 rows, batch 1 and 32) with full-array validation; "
                      "all previous records unchanged.")
    proof["creation_timestamp_utc"] = f"{REPORT_DATE}T00:00:00Z"
    proof["creation_timestamp_unix"] = stamp
    proof["independent_rebuild_command"] = (f"typst compile --root . --creation-timestamp {stamp} docs/benchmark.typ "
                                            f"{independent.relative_to(ROOT) if independent.is_relative_to(ROOT) else independent}")
    proof["byte_identical_rebuild"] = True
    proof["page_count"] = pages
    proof["direct_engine_checkpoint_20261030"] = {
        "base_commit": base_commit,
        "previous_proof_sha256": previous_sha,
        "new_result_records": new_keys + ["direct_engine_report_updated_on"],
        "campaign": str(HERE.relative_to(ROOT)),
        "note": ("Previous proof was stale for HANDOFF.md at the base commit; all listed artifacts are rehashed "
                 "here. Historical result members are preserved byte-for-byte."),
    }
    PROOF.write_text(json.dumps(proof, indent=1) + "\n")
    print(json.dumps({"ledger": proof["source_ledger_count"], "new": new_keys, "pages": pages}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("bind", "seal"))
    parser.add_argument("--independent-pdf", type=Path)
    parser.add_argument("--page-count", type=int)
    parser.add_argument("--base-commit")
    args = parser.parse_args()
    if args.action == "bind":
        bind()
    else:
        seal(args.independent_pdf.resolve(), args.page_count, args.base_commit)


if __name__ == "__main__":
    main()
