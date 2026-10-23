"""Bind the reviewed production sources to completed independent/API checks."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path.cwd()
OUT = ROOT / "validation/near-vacuum-production"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads((ROOT / path).read_text())


def bind(path):
    return {"path": path, "sha256": sha(ROOT / path)}


tests_path = "validation/near-vacuum-production/attempt004/qualification.json"
tests = read(tests_path)
assert tests["status"] == "passed" and tests["changed_sources"] == []
assert [phase["label"] for phase in tests["phases"]] == ["build", "tests"]
for phase in tests["phases"]:
    assert phase["status"] == "passed" and phase["exit_code"] == 0
    assert sha(OUT / "attempt004" / (phase["label"] + ".log")) == phase["log_sha256"]
assert tests["phases"][1]["elapsed_seconds"] < 600
log = (OUT / "attempt004/tests.log").read_text()
for name in ["primal_certificates_preserve_lanes_and_explicit_accuracy_contracts",
             "unsupported_native_shape_can_use_only_explicit_uncertified_fallback",
             "zero_primal_tail_does_not_hide_a_third_mass_derivative"]:
    assert f"test {name} ... ok" in log
assert "3 passed; 0 failed; 0 ignored" in log

continuation_path = "validation/near-vacuum-production/attempt004/build-continuation.json"
continuation = read(continuation_path)
assert continuation["status"] == "continuation-finished"
assert continuation["compilation_process_finished"]
assert not continuation.get("extra_compilation_timed_out", False)
core_path = "validation/near-vacuum-production/core-check/qualification.json"
core = read(core_path)
assert core["status"] == "passed" and core["changed_sources"] == []
assert core["public_test_qualification_sha256"] == sha(ROOT / tests_path)
assert sha(OUT / "core-check/check.log") == core["log_sha256"]

ready = read("validation/near-vacuum-production-ready/manifest.json")
collector = read("validation/public-highpoint/collector-nway-adoption.json")
sources = dict(ready["staged_source_sha256"])
sources["crates/iregi-rust/src/stability.rs"] = collector["review_source_sha256"]
for path, digest in tests["source_sha256"].items():
    assert sha(ROOT / path) == digest, path
for path, digest in sources.items():
    assert sha(ROOT / path) == digest == tests["source_sha256"][path], path

executable = ROOT / tests["executable"]["path"]
assert sha(executable) == tests["executable"]["sha256"]
retained = ROOT / "target/near-vacuum-production/certified-public"
retained.parent.mkdir(parents=True, exist_ok=True)
if not retained.exists():
    shutil.copy2(executable, retained)
assert sha(retained) == tests["executable"]["sha256"]
assert sha(OUT / "run_stripped_public_tests.py") == tests["runner_sha256"]

evidence = [tests_path, continuation_path, core_path,
            "validation/near-vacuum-adapter-current/qualification.json",
            "validation/near-vacuum-production-ready/manifest.json",
            "validation/near-vacuum-production-ready/cleanup-proof.json",
            "validation/public-highpoint/collector-capture-v4-qualification.json",
            "validation/public-highpoint/collector-nway-checks.json",
            "validation/public-highpoint/collector-v4-independent-audit.json",
            "validation/public-highpoint/collector-nway-adoption.json"]
record = {
    "status": "integrated_and_qualified",
    "base_revision": "21622ec9abfdedcf18993768845a29a9bb1c1e1d",
    "source_sha256": sources,
    "evidence": [bind(path) for path in evidence],
    "qualifier_sha256": sha(Path(__file__)),
    "public_api_tests": {"passed": 3, "failed": 0, "ignored": 0,
                         "source_files_verified": len(tests["source_sha256"]),
                         "retained_executable": bind(str(retained.relative_to(ROOT)))},
    "build_limit": "Compilation used an explicit logged continuation after storage failures; the original600s build cap is not claimed met. Numerical tests remained within their unchanged600s cap. Build/runtime durations here are not performance measurements.",
    "changes": [
        "Explicit finite D0 near-vacuum accuracy API with exact rational component budgets, lazy N2/N4 batch programs and finite enclosures.",
        "Exact Symbolica alias-use collection for IF-free subtrees, preserving conditional activation and current tensor results.",
        "New typed public accuracy/failure variants; downstream exhaustive enum matches must account for them."
    ],
    "limits": [
        "Finite certificates cover exact represented master inputs, not upstream routing, input uncertainty or quadrature error.",
        "Series support is limited to the checked analytic neighborhood, orders2/4, at most32 ancestor-closed Taylor components and total degree4.",
        "Ordinary scalar-master and tensor-reduction default formulas remain unchanged; ordinary fallback is explicitly uncertified.",
        "No new IREGI performance parity is claimed; the primary measured baseline remains6b24c03.",
        "High-point coverage and all private automatic-planar/receipt/slim/native/CSE experiments remain separate."
    ]
}
(OUT / "promotion.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({"status": record["status"], "source_files": len(sources),
                  "evidence_records": len(evidence), "public_api_tests_passed": 3,
                  "promotion_sha256": sha(OUT / "promotion.json")}, indent=2))
