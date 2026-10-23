"""Audit every actual legacy response from attempt003; no reference execution."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path.cwd()
CANDIDATE = ROOT / "validation/collier-reference/shared/candidate004"
sys.path.insert(0, str(CANDIDATE))
import run_correctness as candidate


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    raw = ROOT / "validation/collier-reference/shared/attempt003/capture.json.gz"
    old = json.loads(gzip.decompress(raw.read_bytes()))
    checks, response_count, rejected_count, component_count = 0, 0, 0, 0

    def require(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    rows = [r for r in old["rows"] if r["n"] <= 4]
    require(len(rows) == 16, "every fixed preflight row required")
    for row in rows:
        case = next(c for c in old["input_cases"] if c["id"] == row["id"])
        require(row["iregi_frozen_regression"]["status"] == "passed", "retained IREGI regression changed")
        for mode in (1, 2):
            attempts = row["request_attempts"][f"wrapped-{mode}"]
            require(len(attempts) == 1, "fixed legacy row should have one unchanged scale group")
            attempt = attempts[0]
            response = attempt["response"]
            require(isinstance(response, dict), "missing actual raw legacy response")
            require(attempt["child_exit_code"] == 0, "legacy child did not close cleanly")
            require(response["id"] == row["id"] and response["collier_mode"] == mode, "legacy identity/policy changed")
            require("interface" not in response and "direct_tensor_threshold" not in response,
                    "fixture unexpectedly acquired newer metadata")
            candidate.validate_engine_header(response, case, "wrapped", mode)
            response_count += 1
            require(len(response["lanes"]) == row["batch_width"], "legacy lane count changed")
            generic = row["responses"][f"generic-{mode}"]
            candidate.validate_engine_header(generic, case, "generic", mode)
            require(generic["stable"] == response["stable"], "native acceptance changed")
            require(generic["pole_check_errors"] == response["pole_check_errors"], "separated-pole probes changed")
            for a, b in zip(generic["lanes"], response["lanes"]):
                for key in ("status", "last_err_flag", "last_acc_flag", "worst_err_flag", "worst_acc_flag", "moments"):
                    require(a.get(key) == b.get(key), f"legacy/new dedicated response differs: {key}")
                values = b["moments"] if b["status"] == "success" else b.get("diagnostic_moments")
                if b["status"] != "success":
                    rejected_count += 1
                    require(b["moments"] is None, "rejected diagnostic became an accepted array")
                count = (case["rank"]+1)*(case["rank"]+2)*(case["rank"]+3)*(case["rank"]+4)//24
                require(isinstance(values, list) and len(values) == count, "incomplete Cartesian array")
                for moment in values:
                    require(len(moment) == 4 and all(len(z) == 2 for z in moment), "incomplete native Laurent array")
                    component_count += 4
    report = {"kind": "actual-legacy-header-preflight-audit", "status": "passed", "assertions": checks,
              "fixed_rows": len(rows), "actual_legacy_responses": response_count,
              "rejected_lanes_preserved": rejected_count, "native_complex_slots_checked": component_count,
              "reference_kernels_executed": False, "performance_evidence": False,
              "bindings": {str(p.relative_to(ROOT)): digest(p) for p in
                           [raw, Path(__file__).resolve(), CANDIDATE/"run_correctness.py", CANDIDATE/"support.py"]}}
    destination = CANDIDATE / "legacy-header-preflight-audit.json"
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(destination)


if __name__ == "__main__":
    main()
