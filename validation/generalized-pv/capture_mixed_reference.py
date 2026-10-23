"""Capture original generalized tensors with a nonzero mixed Cartesian moment."""
import datetime
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path.cwd()
OUT = ROOT / "target/generalized-pv"
sys.path.insert(0, str(OUT))
import capture_reference as harness

harness.RAW = OUT / "reference-mixed-raw"
harness.RAW.mkdir(parents=True, exist_ok=True)


def main():
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    base_path = OUT / "reference-capture.json"
    base = json.loads(base_path.read_text())
    provenance = base["provenance"]
    assert harness.sha(harness.EXE) == provenance["executable_sha256"]
    assert harness.sha(harness.PROVENANCE) == provenance["build_provenance_sha256"]
    historical = provenance["recorded_build_driver"]
    assert harness.sha(ROOT / historical["path"]) == historical["sha256"]
    assert historical["sha256"] == provenance["captured_build_provenance"]["driver_sha256"]
    assert harness.sha(ROOT / "validation/reference/factorial_pair.patch") == provenance["captured_build_provenance"]["patch_sha256"]
    checked_sources = ["global.f90", "gti_reduce.f90", "si_reduce.f90", "pave_reduce.f90",
                       "ti_reduce.f90", "matrices.f90", "oneloop/avh_olo_foriregi.f90"]
    for source in checked_sources:
        assert harness.sha(ROOT / "target/reference/source" / source) == provenance["captured_build_provenance"]["source_sha256"][source]
    cases = []
    for mode in range(3):
        request = harness.case(f"mixed_n2_p12_h1_r2_mode{mode}", [1, 2], 1, 2, mode)
        request["propagators"][1]["shift"] = [1, 2, 0, 0]
        cases.append(harness.capture(request, "anchored_generalized_mixed_cartesian_tensor"))
    comparisons = [{"left_mode": 0, "right_mode": mode, **harness.compare(cases[0], cases[mode])}
                   for mode in (1, 2)]
    verified_logs = 0
    verified_slots = 0
    mixed_moments = []
    for record in cases:
        for log in record["transport"]["logs"].values():
            assert harness.sha(ROOT / log["path"]) == log["sha256"]
            verified_logs += 1
        if record["status"] == "stable_finite_reference_result":
            result = record["expected"]
            assert result["id"] == record["input"]["id"]
            assert result["poles"] == ["uv1", "ir1", "ir2", "finite"]
            assert len(result["moments"]) == math.comb(6, 4)
            assert all(len(moment) == 4 and all(len(value) == 2 for value in moment)
                       for moment in result["moments"])
            assert all(math.isfinite(part) for moment in result["moments"] for value in moment for part in value)
            verified_slots += 4 * len(result["moments"])
            mixed_moments.append({"mode": record["input"]["mode"],
                                  "basis_index_zero_based": 6,
                                  "exponents": [1, 1, 0, 0],
                                  "slots": result["moments"][6],
                                  "nonzero_finite_slot": any(part != 0 for part in result["moments"][6][3])})
    artifact = {
        "schema_version": 1,
        "capture_started_utc": started,
        "capture_completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "normalization": "native_iregi",
        "basis": "unweighted_cartesian_monomials",
        "dimension_shift_convention": "full even idim; D=4+idim-2epsilon",
        "pole_slots": ["uv1", "ir1", "ir2", "finite"],
        "scope": "Three direct anchored generalized real tensor requests, rank two, with nonzero time-space mixed moments. No tensor coordinate or normalization transformations performed.",
        "tolerance": harness.TOLERANCE,
        "comparison_scale": base["comparison_scale"],
        "fixture_policy": base["fixture_policy"],
        "kinematics": {"shifts": [[0, 0, 0, 0], [1, 2, 0, 0]],
                       "mass_squared": [4, 9], "powers": [1, 2], "half_dimension_shift": 1,
                       "rank": 2, "mu": 3,
                       "rationale": "The nonzero shift is spacelike with square -3, while both time and x components are nonzero. Distinct positive masses keep the Feynman polynomial positive."},
        "provenance": {
            "inherited_capture": harness.relative(base_path),
            "inherited_capture_sha256": harness.sha(base_path),
            "reference_build": provenance,
            "capture_script": harness.relative(Path(__file__)),
            "capture_script_sha256": harness.sha(Path(__file__)),
            "capture_helper": harness.relative(Path(harness.__file__)),
            "capture_helper_sha256": harness.sha(Path(harness.__file__)),
            "command": [sys.executable, harness.relative(Path(__file__))],
            "working_directory": str(ROOT),
            "historical_driver_matches_recorded_build": True,
            "driver_drift_inactive": "All masses are real, distinct and positive; snapping is disabled. Neither later mass-reference deduplication nor tiny-complex-width dispatch affects these inputs.",
            "selected_fortran_source_hashes_verified": checked_sources,
            "factorial_patch_matches_recorded_build": True,
            "symbolica_runtime_used": False,
            "tensor_transformations_performed": False,
        },
        "cases": cases,
        "intermode_comparisons": comparisons,
        "mixed_moment_witnesses": mixed_moments,
        "summary": {
            "generalized_requests": len(cases),
            "stable_finite_generalized_results": sum(c["status"] == "stable_finite_reference_result" for c in cases),
            "generalized_reference_failures": sum(c["status"] != "stable_finite_reference_result" for c in cases),
            "intermode_agreements": sum(c["status"] == "agreement" for c in comparisons),
            "intermode_discrepancies": sum(c["status"] == "reference_discrepancy" for c in comparisons),
            "raw_files_sha256_verified": verified_logs,
            "complex_slots_captured": verified_slots,
            "nonzero_mixed_finite_moments": sum(w["nonzero_finite_slot"] for w in mixed_moments),
        },
    }
    artifact_path = OUT / "reference-mixed-capture.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n")
    print(json.dumps({**artifact["summary"], "artifact_sha256": harness.sha(artifact_path),
                      "maximum_inter_mode_normalized_error": max((c.get("maximum_normalized_error", 0) for c in comparisons), default=0)}, indent=2))


if __name__ == "__main__":
    main()
