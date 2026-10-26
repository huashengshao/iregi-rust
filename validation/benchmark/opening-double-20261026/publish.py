#!/usr/bin/env python3
"""Bind and seal the additive binary64 opening-table publication.

This is an artifact-only helper. It neither builds nor executes numerical code.
Run from the repository root after the campaign and independent reviews finish.
Use --dry-run to inspect either operation without changing publication files.
"""

import argparse
import copy
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile


ROOT = Path.cwd().resolve()
HERE = Path("validation/benchmark/opening-double-20261026")
BASE = "78193d6ea5dd8804b25032a65d47492a128f427e"
RESULTS = Path("docs/data/results.json")
PROOF = Path("docs/data/report-validation.json")
MANIFEST = HERE / "manifest.json"
PREFIX = "opening_double_precision_"
CHECKPOINT = "opening_double_precision_checkpoint_20261026"


def encoded(value):
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def project_path(value):
    path = Path(value)
    absolute = (ROOT / path).resolve()
    if not absolute.is_relative_to(ROOT):
        raise ValueError(f"path outside repository: {value}")
    return absolute.relative_to(ROOT)


def atomic_write(path, payload):
    path = ROOT / path
    with tempfile.NamedTemporaryFile(
        prefix=path.name + ".", suffix=".partial", dir=path.parent, delete=False,
    ) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    temporary.replace(path)


def git_bytes(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def checker_module():
    spec = importlib.util.spec_from_file_location(
        "opening_double_report_checker", ROOT / "scripts/check-benchmark-report.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preserve_history(text):
    """Verify exact original JSON value spelling, not merely value equality."""
    raw_members = checker_module().raw_members
    old = raw_members(git_bytes(RESULTS).decode())
    current = raw_members(text)
    changed = [key for key, value in old.items() if current.get(key) != value]
    if changed:
        raise ValueError(f"historical result records changed: {changed}")
    if len(old) != 469:
        raise ValueError(f"unexpected pinned baseline record count: {len(old)}")
    return old, current


def inventory():
    files = {}
    for path in sorted((ROOT / HERE).rglob("*")):
        if not path.is_file():
            continue
        relative = project_path(path)
        if (relative == MANIFEST or "__pycache__" in relative.parts
                or path.name.endswith(".partial")):
            continue
        files[str(relative)] = {"sha256": digest(path), "bytes": path.stat().st_size}
    return files


def manifest_value():
    files = inventory()
    return {
        "schema_version": 2,
        "base_revision": BASE,
        "status": "binary64_timing_first_campaign_archival_inventory",
        "scope": (
            "New binary64 opening-table campaign; all candidate attempts retained. "
            "Timings and measured whole-array relative errors are separate. "
            "Earlier mixed-precision captures and strict classifications remain historical. "
            "This inventory alone is not numerical qualification or a speed gate."
        ),
        "inventory_exclusions": [str(MANIFEST), "__pycache__ subtrees", "*.partial"],
        "files": files,
        "file_count": len(files),
        "total_bytes": sum(value["bytes"] for value in files.values()),
    }


def binding(path, pending=None):
    path = project_path(path)
    if path in (PROOF, RESULTS):
        raise ValueError(f"a result record cannot bind its containing publication files: {path}")
    payload = pending if pending is not None else (ROOT / path).read_bytes()
    record = {"source": str(path), "sha256": sha256_bytes(payload)}
    if path.suffix == ".json":
        record["snapshot"] = json.loads(payload)
    return record


def binding_paths(args):
    paths = {
        PREFIX + "examples": project_path(args.summary),
        PREFIX + "build": project_path(args.build),
        PREFIX + "qualification": project_path(args.qualification),
        PREFIX + "independent_review": project_path(args.independent_review),
        PREFIX + "manifest": MANIFEST,
    }
    for suffix, name in (
        ("examples", "summary.json"), ("build", "build.json"),
        ("supervision", "supervision.json"), ("qualification", "qualification.json"),
        ("independent_review", "independent-review.json"), ("manifest", "manifest.json"),
    ):
        path = HERE / "collier" / name
        if (ROOT / path).is_file():
            paths[PREFIX + "collier_" + suffix] = path
    for item in args.binding:
        key, separator, value = item.partition("=")
        if not separator or not key.startswith(PREFIX):
            raise ValueError("additional bindings must be opening_double_precision_KEY=PATH")
        if key in paths:
            raise ValueError(f"duplicate requested binding: {key}")
        paths[key] = project_path(value)
    return paths


def validate_binary64_summary(path):
    summary = json.loads((ROOT / path).read_text())
    rows = summary.get("rows", [])
    previous = json.loads(git_bytes(Path("validation/benchmark/opening-rank6-20261026/inputs.json")))
    expected = {case["id"]: case["driver_request"] for case in previous["cases"]}
    identifiers = [row.get("id") for row in rows]
    if len(identifiers) != len(set(identifiers)) or set(identifiers) != set(expected):
        raise ValueError("opening summary must retain each of the exact 18 historical input IDs once")
    high = {"ordinary-n5-r5", "ordinary-n5-r6", "ordinary-n6-r6"}
    for row in rows:
        if any(row.get(name) != expected[row["id"]][name]
               for name in ("n", "rank", "powers", "dimension_shift")):
            raise ValueError(f"opening mathematical input metadata changed: {row.get('id')}")
        if row.get("numeric_type") != "f64" or row.get("working_bits") != 53:
            raise ValueError(f"opening row is not working binary64: {row.get('id')}")
        requested = 39 if row.get("id") in high else 53
        if row.get("requested_bits") != requested:
            raise ValueError(f"opening requested accuracy differs: {row.get('id')}")
    return summary


def bind(args):
    text = (ROOT / RESULTS).read_text()
    old, current = preserve_history(text)
    paths = binding_paths(args)
    validate_binary64_summary(paths[PREFIX + "examples"])
    pending_manifest = encoded(manifest_value())
    new = {key: binding(path, pending_manifest if path == MANIFEST else None)
           for key, path in paths.items()}
    duplicates = set(new) & set(current)
    if duplicates:
        raise ValueError(f"refusing to overwrite existing archival records: {sorted(duplicates)}")
    # Only append to the existing object. Every previous member's byte spelling survives.
    updated = (text.rstrip()[:-1].rstrip() + ",\n"
               + json.dumps(new, indent=2, allow_nan=False)[1:-1].strip("\n")
               + "\n}\n")
    preserve_history(updated)
    if not args.dry_run:
        atomic_write(MANIFEST, pending_manifest)
        atomic_write(RESULTS, updated.encode())
    print(json.dumps({"operation": "bind", "dry_run": args.dry_run,
                      "historical_raw_records_preserved": len(old),
                      "new_records": len(new), "keys": list(new),
                      "manifest_files": len(json.loads(pending_manifest)["files"])}))


def seal(args):
    text = (ROOT / RESULTS).read_text()
    old_members, current_members = preserve_history(text)
    results = json.loads(text)
    summary_record = results.get(PREFIX + "examples")
    if not summary_record:
        raise ValueError("bind the completed campaign before sealing its proof")
    summary = validate_binary64_summary(project_path(summary_record["source"]))
    manifest = json.loads((ROOT / MANIFEST).read_text())
    if manifest["files"] != inventory():
        raise ValueError("campaign inventory changed after binding; do not seal stale evidence")
    for key, record in results.items():
        if not isinstance(record, dict) or not isinstance(record.get("source"), str):
            continue
        if not isinstance(record.get("sha256"), str):
            continue
        path = project_path(record["source"])
        if digest(ROOT / path) != record["sha256"]:
            raise ValueError(f"bound source changed before sealing: {key}")
        if key.startswith(PREFIX) and path.suffix == ".json":
            if json.loads((ROOT / path).read_text()) != record.get("snapshot"):
                raise ValueError(f"new snapshot differs from bound source: {key}")
    root_review_path = project_path(args.root_review)
    root_review = json.loads((ROOT / root_review_path).read_text())
    if not str(root_review.get("status", "")).startswith("passed"):
        raise ValueError("the root review must explicitly record a passed artifact review")
    for name, expected in root_review.get("report_artifacts", {}).items():
        path = project_path(name)
        if path == PROOF:
            raise ValueError("the root review cannot bind the final report proof's hash")
        if digest(ROOT / path) != expected:
            raise ValueError(f"root review artifact changed before sealing: {path}")
    independent = project_path(args.independent_pdf)
    if independent == Path("docs/benchmark.pdf"):
        raise ValueError("the independent rebuild must be a distinct PDF path")
    if (ROOT / independent).read_bytes() != (ROOT / "docs/benchmark.pdf").read_bytes():
        raise ValueError("independently rebuilt PDF is not byte-identical")
    previous_bytes = git_bytes(PROOF)
    previous = json.loads(previous_bytes)
    proof = copy.deepcopy(previous)
    proof["previous_78193d6_publication"] = previous
    proof["recorded_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proof["status"] = "passed_opening_binary64_timing_first_report_rebuild_and_review"
    proof["scope"] = (
        "The first two opening tables use new binary64 timings for all 18 TIRust inputs "
        "and the ordinary COLLIER comparison. Fastest finite measured configurations "
        "within three relative digits are selected; numerical warnings and incomplete "
        "attempts remain visible. Three high-point rows request approximately 1e-6. "
        "Historical data and the complete previous publication proof are preserved. "
        "No controlled-host comparative performance gate is claimed."
    )
    ledger = [dict(key=key, source=value["source"], sha256=value["sha256"])
              for key, value in results.items() if isinstance(value, dict)
              and isinstance(value.get("source"), str)
              and isinstance(value.get("sha256"), str)]
    proof["source_ledger"] = ledger
    proof["source_ledger_count"] = len(ledger)
    artifact_names = set(previous["report_artifacts"])
    artifact_names.update(record["source"] for key, record in results.items()
                          if key.startswith(PREFIX) and isinstance(record, dict)
                          and isinstance(record.get("source"), str))
    artifact_names.add(str(root_review_path))
    artifact_names.update(str(project_path(path)) for path in args.artifact)
    if str(PROOF) in artifact_names:
        raise ValueError("a report proof cannot bind its own hash")
    proof["report_artifacts"] = {name: digest(ROOT / project_path(name))
                                 for name in sorted(artifact_names)}
    proof["page_count"] = args.page_count
    proof["byte_identical_rebuild"] = True
    proof["independent_rebuild_command"] = (
        "typst compile --root . --creation-timestamp 1792972800 docs/benchmark.typ "
        + str(independent)
    )
    proof["render_check"] = args.render_check
    proof[CHECKPOINT] = {
        "base_commit": BASE,
        "historical_raw_records_preserved": len(old_members),
        "new_archival_records": len(current_members) - len(old_members),
        "all_prior_proof_history_preserved": True,
        "prior_proof_sha256": sha256_bytes(previous_bytes),
        "new_opening_working_numeric_type": "f64",
        "new_opening_working_significand_bits": 53,
        "tirust_rows": len(summary["rows"]),
        "tirust_measured_rows": summary.get("measured_rows"),
        "tirust_three_digit_rows": summary.get("three_digit_rows"),
        "old_strict_gate_or_native_warning_alone_suppresses_timing": False,
        "new_controlled_comparative_speed_gate": False,
        "root_review": {"source": str(root_review_path), "sha256": digest(ROOT / root_review_path)},
    }
    proof.setdefault("known_limits", []).append(
        "The current first two opening tables supersede the historical mixed-precision "
        "opening display with an optimistic binary64-only candidate sweep. Measured "
        "whole-array relative discrepancy is separate from requested accuracy. Flags "
        "alone do not disqualify timing; missing or nonfinite arrays cannot qualify "
        "a usable reduction. Fastest means and descriptive repeat uncertainty do not "
        "constitute a controlled-host speed-parity gate. Prior strict classifications "
        "and mixed-precision captures remain unchanged historical evidence."
    )
    proof["known_limits"].extend(args.known_limit)
    if not args.dry_run:
        atomic_write(PROOF, encoded(proof))
        check = checker_module().check(ROOT, BASE)
    else:
        check = None
    print(json.dumps({"operation": "seal", "dry_run": args.dry_run,
                      "source_bindings": len(ledger), "page_count": args.page_count,
                      "prior_proof_history_preserved": True, "report_check": check}))


def main():
    if Path(__file__).resolve().parent != ROOT / HERE:
        raise SystemExit("run this helper from /shared/external/iregi/iregi-rust")
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    bind_parser = commands.add_parser("bind", help="create inventory and append new result bindings")
    bind_parser.add_argument("--summary", default=str(HERE / "summary.json"))
    bind_parser.add_argument("--build", default=str(HERE / "build.json"))
    bind_parser.add_argument("--qualification", default=str(HERE / "qualification.json"))
    bind_parser.add_argument("--independent-review", default=str(HERE / "independent-review.json"))
    bind_parser.add_argument("--binding", action="append", default=[], metavar="KEY=PATH")
    seal_parser = commands.add_parser("seal", help="seal reviewed report after independent PDF rebuild")
    seal_parser.add_argument("--page-count", type=int, required=True)
    seal_parser.add_argument("--independent-pdf", required=True)
    seal_parser.add_argument("--root-review", required=True)
    seal_parser.add_argument("--render-check", required=True)
    seal_parser.add_argument("--artifact", action="append", default=[])
    seal_parser.add_argument("--known-limit", action="append", default=[])
    for command in (bind_parser, seal_parser):
        command.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.operation == "seal" and args.page_count <= 0:
        parser.error("--page-count must be positive")
    {"bind": bind, "seal": seal}[args.operation](args)


if __name__ == "__main__":
    main()
