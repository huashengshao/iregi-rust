"""Verify capture shapes and retained provenance without executing a backend."""
import hashlib
import json
import math
from pathlib import Path

root = Path.cwd()
artifact_path = root / "target/generalized-pv/reference-capture.json"
data = json.loads(artifact_path.read_text())
records = data["cases"] + data["translated_scalar_checks"] + [data["translated_general_transport"]]
checked_logs = 0
slots = 0
shapes = 0


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for record in records:
    for log in record["transport"]["logs"].values():
        assert digest(root / log["path"]) == log["sha256"]
        checked_logs += 1
    if record["status"] == "stable_finite_reference_result":
        output, request = record["expected"], record["input"]
        assert output["id"] == request["id"]
        assert output["poles"] == ["uv1", "ir1", "ir2", "finite"]
        assert len(output["moments"]) == math.comb(request["rank"] + 4, 4)
        assert all(len(moment) == 4 and all(len(value) == 2 for value in moment)
                   for moment in output["moments"])
        assert all(math.isfinite(part) for moment in output["moments"]
                   for value in moment for part in value)
        slots += 4 * len(output["moments"])
        shapes += 1

provenance = data["provenance"]
historical = provenance["recorded_build_driver"]
assert digest(root / historical["path"]) == historical["sha256"]
assert historical["sha256"] == provenance["captured_build_provenance"]["driver_sha256"]
assert digest(root / provenance["driver_drift"]["diff_path"]) == provenance["driver_drift"]["diff_sha256"]
assert digest(root / provenance["executable"]) == provenance["executable_sha256"]
assert digest(root / provenance["script"]) == provenance["script_sha256"]
assert digest(root / "validation/reference/factorial_pair.patch") == provenance["captured_build_provenance"]["patch_sha256"]
source_hashes = provenance["captured_build_provenance"]["source_sha256"]
checked_sources = ["global.f90", "gti_reduce.f90", "si_reduce.f90", "pave_reduce.f90",
                   "ti_reduce.f90", "matrices.f90", "oneloop/avh_olo_foriregi.f90"]
for source in checked_sources:
    assert digest(root / "target/reference/source" / source) == source_hashes[source]
assert data["summary"]["generalized_requests"] == 27
assert data["summary"]["intermode_agreements"] == 18
assert data["summary"]["translated_scalar_agreements"] == 9
assert data["translated_general_transport"]["transport"]["returncode"] != 0
assert data["translated_general_transport"]["transport"]["result_count"] == 0

summary = {
    "artifact_sha256": digest(artifact_path),
    "checked_record_shapes": shapes,
    "complex_slots_captured": slots,
    "raw_files_sha256_verified": checked_logs,
    "historical_driver_matches_recorded_build": True,
    "current_driver_matches_recorded_build": provenance["driver_drift"]["current_matches_recorded_build"],
    "driver_drift_resolution": provenance["driver_drift"]["scope"],
    "selected_fortran_source_hashes_verified": checked_sources,
    "factorial_patch_matches_recorded_build": True,
    "executable_and_capture_script_sha256_verified": True,
    "intermode_complex_slots_compared": sum(c["complex_slots_compared"] for c in data["intermode_comparisons"]),
    "maximum_inter_mode_normalized_error": max(c["maximum_normalized_error"] for c in data["intermode_comparisons"]),
    "translated_scalar_slots_compared": sum(c["comparison_to_anchored_general_mode0_scalar"]["complex_slots_compared"]
                                           for c in data["translated_scalar_checks"]),
    "symbolica_runtime_used": False,
    "tensor_translation_performed": False,
}
(root / "target/generalized-pv/reference-capture-verification.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
