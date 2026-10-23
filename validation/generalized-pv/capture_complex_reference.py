"""Retain complex generalized transport limits and direct scalar counterparts."""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path.cwd()
OUT = ROOT / "target/generalized-pv"
sys.path.insert(0, str(OUT))
import capture_reference as harness

harness.RAW = OUT / "reference-complex-raw"
harness.RAW.mkdir(parents=True, exist_ok=True)


def main():
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    base = json.loads((OUT / "reference-capture.json").read_text())
    assert harness.sha(harness.EXE) == base["provenance"]["executable_sha256"]
    specifications = [
        ("complex_n2_p12_h1_r2", [1, 2], 1, 2),
        ("complex_n3_p121_h2_r1", [1, 2, 1], 2, 1),
    ]
    cases, scalars, dispatch_checks = [], [], []
    for family, powers, h, rank in specifications:
        requests = []
        for mode in range(3):
            request = harness.case(f"{family}_mode{mode}", powers, h, rank, mode)
            for i, propagator in enumerate(request["propagators"]):
                propagator["mass_squared"][1] = -(i + 1) / 4
            requests.append(request)
            record = harness.capture(request, "requested_complex_generalized_tensor")
            stderr_path = ROOT / record["transport"]["logs"]["stderr"]["path"]
            record["boundary"] = {
                "supported": False,
                "reason": "The unmodified generalized tensor adapter and original general_ti_reduce accept real squared masses only.",
                "explicit_rejection_observed": "general tensor API supports real masses only" in stderr_path.read_text(),
            }
            cases.append(record)
        scalar_request = copy.deepcopy(requests[0])
        scalar_request["id"] = family + "_scalar_counterpart"
        scalar_request["api"] = "scalar"
        scalar_request["rank"] = 0
        scalar = harness.capture(scalar_request, "direct_complex_generalized_scalar")
        scalar["scope"] = "Rank-zero counterpart only, through comp_scalar_integral_reduce; original scalar API ignores mode. No tensor moments assembled or inferred."
        scalars.append(scalar)
        masses = [complex(*p["mass_squared"]) for p in scalar_request["propagators"]]
        old_dispatch = any(m.imag != 0 for m in masses)
        current_ratios = [abs(m.imag) / max(abs(m), 1e-2) for m in masses]
        current_dispatch = any(ratio > 1e-15 for ratio in current_ratios)
        assert old_dispatch and current_dispatch
        dispatch_checks.append({"family": family,
                                "recorded_old_driver_selects_complex": old_dispatch,
                                "current_driver_selects_complex": current_dispatch,
                                "current_relative_widths": current_ratios,
                                "reference_masses_distinct_positive_real_parts": len({m.real for m in masses}) == len(masses) and all(m.real > 0 for m in masses),
                                "snap": False})
    artifact = {
        "schema_version": 1,
        "capture_started_utc": started,
        "capture_completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "normalization": "native_iregi",
        "basis": "unweighted_cartesian_monomials",
        "dimension_shift_convention": "full even idim; D=4+idim-2epsilon",
        "pole_slots": ["uv1", "ir1", "ir2", "finite"],
        "scope": "Six requested complex generalized tensor requests are retained as unsupported transport failures. Two direct complex generalized scalar counterparts provide independent rank-zero values only.",
        "source_limitation": "No complex generalized tensor wrapper exists in the supplied IREGI source. The public ordinary complex tensor interface accepts unit powers and zero shift; the lower-level complex scalar recursion accepts generalized powers and dimensions.",
        "provenance": {
            "inherited_capture": "target/generalized-pv/reference-capture.json",
            "inherited_capture_sha256": harness.sha(OUT / "reference-capture.json"),
            "reference_build": base["provenance"],
            "capture_script": harness.relative(Path(__file__)),
            "capture_script_sha256": harness.sha(Path(__file__)),
            "capture_helper": harness.relative(Path(harness.__file__)),
            "capture_helper_sha256": harness.sha(Path(harness.__file__)),
            "command": [sys.executable, harness.relative(Path(__file__))],
            "working_directory": str(ROOT),
            "complex_dispatch_drift_checks": dispatch_checks,
            "symbolica_runtime_used": False,
            "tensor_transformations_performed": False,
        },
        "cases": cases,
        "scalar_cases": scalars,
        "summary": {
            "requested_complex_tensor_requests": len(cases),
            "explicit_unsupported_complex_tensor_rejections": sum(c["boundary"]["explicit_rejection_observed"] for c in cases),
            "successful_complex_tensor_results": sum(c["status"] == "stable_finite_reference_result" for c in cases),
            "stable_finite_complex_scalar_counterparts": sum(c["status"] == "stable_finite_reference_result" for c in scalars),
        },
    }
    (OUT / "reference-complex-capture.json").write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n")
    print(json.dumps(artifact["summary"], indent=2))


if __name__ == "__main__":
    main()
