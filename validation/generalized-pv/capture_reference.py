"""Focused original-IREGI captures; no Rust/Symbolica execution or algebra."""
import datetime
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path.cwd()
OUT = ROOT / "target/generalized-pv"
RAW = OUT / "reference-raw"
RAW.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "validation/reference"))
from capture import encode

EXE = ROOT / "target/reference/iregi-reference"
PROVENANCE = ROOT / "target/reference/provenance.json"
SPECIFICATIONS = [
    ("n1_p1_h1", [1], 1, 0),
    ("n2_p12_h1", [1, 2], 1, 0),
    ("n2_p13_h2", [1, 3], 2, 0),
    ("n2_p12_h2", [1, 2], 2, 0),
    ("n3_p123_h4", [1, 2, 3], 4, 0),
    ("n4_unit_h1", [1, 1, 1, 1], 1, 0),
    ("n2_p21_h1", [2, 1], 1, 0),
    ("n2_unit_hm1_r0", [1, 1], -1, 0),
    ("n2_unit_hm1_r2", [1, 1], -1, 2),
]
SHIFTS = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 2, 0], [0, 0, 0, 3]]
MASSES = [4, 9, 16, 25]
TRANSLATION = [1, -2, 1, 0]
TOLERANCE = 1e-10


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(path.relative_to(ROOT))


def case(name, powers, h, rank, mode, translated=False, api="general"):
    points = [[p + a for p, a in zip(q, TRANSLATION)] if translated else q
              for q in SHIFTS[:len(powers)]]
    return {"id": name, "api": api, "mode": mode, "rank": rank,
            "dimension_shift": 2 * h, "mu": 3, "snap": False,
            "threshold": 1e-6,
            "propagators": [{"shift": point, "mass_squared": [MASSES[i], 0],
                              "power": power}
                            for i, (point, power) in enumerate(zip(points, powers))]}


def capture(request, role):
    stem = RAW / request["id"]
    paths = {kind: stem.with_suffix(suffix) for kind, suffix in
             [("stdin", ".input"), ("stdout", ".stdout.log"), ("stderr", ".stderr.log")]}
    transport = encode(request) + "QUIT\n"
    paths["stdin"].write_text(transport)
    started = time.monotonic()
    try:
        process = subprocess.run([str(EXE)], input=transport, capture_output=True,
                                 text=True, cwd=ROOT, timeout=30)
        stdout, stderr, returncode = process.stdout, process.stderr, process.returncode
        timeout = False
    except subprocess.TimeoutExpired as error:
        stdout, stderr, returncode = error.stdout or "", error.stderr or "", None
        if isinstance(stdout, bytes): stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes): stderr = stderr.decode(errors="replace")
        timeout = True
    elapsed = time.monotonic() - started
    paths["stdout"].write_text(stdout)
    paths["stderr"].write_text(stderr)
    results = []
    parse_errors = []
    for line in stdout.splitlines():
        if line.startswith("RESULT "):
            try:
                results.append(json.loads(line[7:]))
            except (ValueError, TypeError) as error:
                parse_errors.append(str(error))
    result = results[0] if len(results) == 1 and results[0].get("id") == request["id"] else None
    finite = bool(result and result.get("moments") is not None and
                  all(math.isfinite(part) for moment in result["moments"]
                      for value in moment for part in value))
    completed = returncode == 0 and not timeout and not parse_errors and len(results) == 1 and result is not None
    status = ("stable_finite_reference_result" if completed and finite and result.get("stable")
              else "reference_failure")
    record = {"input": request, "role": role, "status": status,
              "reference_repaired": True, "expected": result,
              "transport": {"returncode": returncode, "timeout": timeout,
                            "elapsed_seconds": elapsed, "result_count": len(results),
                            "parse_errors": parse_errors,
                            "logs": {kind: {"path": relative(path), "sha256": sha(path)}
                                     for kind, path in paths.items()}}}
    print(request["id"], status, flush=True)
    return record


def ranks(maximum):
    # Enumerate the documented packed index counts; no algebraic transformation.
    return [rank for rank in range(maximum + 1)
            for _ in range(math.comb(rank + 3, 3))]


def compare(left, right, first_only=False):
    if left["status"] != "stable_finite_reference_result" or right["status"] != "stable_finite_reference_result":
        return {"status": "unavailable_reference_failure", "failures": []}
    request = left["input"]
    q = max(request["mu"], *(abs(x) for p in request["propagators"] for x in p["shift"]),
            *(math.sqrt(abs(complex(*p["mass_squared"]))) for p in request["propagators"]))
    base_dimension = 4 + request["dimension_shift"] - 2 * sum(p["power"] for p in request["propagators"])
    failures = []
    maximum = 0.
    count = 0
    moment_ranks = ranks(request["rank"])
    left_values = left["expected"]["moments"][:1] if first_only else left["expected"]["moments"]
    right_values = right["expected"]["moments"][:1] if first_only else right["expected"]["moments"]
    if len(left_values) != len(right_values):
        return {"status": "shape_mismatch", "left_moments": len(left_values), "right_moments": len(right_values)}
    for moment, (a, b) in enumerate(zip(left_values, right_values)):
        natural = q ** (base_dimension + moment_ranks[moment])
        for slot, (x, y) in enumerate(zip(a, b)):
            x, y = complex(*x), complex(*y)
            error = abs(x - y)
            scale = natural + abs(x)
            scaled = error / scale
            maximum = max(maximum, scaled)
            count += 1
            if scaled > TOLERANCE:
                failures.append({"moment": moment, "slot": slot, "absolute_error": error,
                                 "normalized_error": scaled, "left": [x.real, x.imag],
                                 "right": [y.real, y.imag]})
    return {"status": "agreement" if not failures else "reference_discrepancy",
            "complex_slots_compared": count, "maximum_normalized_error": maximum,
            "failures": failures}


def main():
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    provenance = json.loads(PROVENANCE.read_text())
    historical_driver = subprocess.check_output(
        ["git", "show", "92eafe8:validation/reference/driver.f90"], cwd=ROOT)
    assert hashlib.sha256(historical_driver).hexdigest() == provenance["driver_sha256"]
    historical_driver_path = RAW / "recorded-build-driver.f90"
    historical_driver_path.write_bytes(historical_driver)
    driver_diff_path = RAW / "recorded-build-driver-to-current.diff"
    driver_diff_path.write_bytes(subprocess.check_output(
        ["git", "diff", "92eafe8", "--", "validation/reference/driver.f90"], cwd=ROOT))
    historical_commit = subprocess.check_output(
        ["git", "rev-parse", "92eafe8"], text=True, cwd=ROOT).strip()
    cases, comparisons, translated_scalars = [], [], []
    for name, powers, h, rank in SPECIFICATIONS:
        modes = [capture(case(f"{name}_mode{mode}", powers, h, rank, mode), "anchored_generalized")
                 for mode in range(3)]
        cases.extend(modes)
        for mode in (1, 2):
            comparison = compare(modes[0], modes[mode])
            comparisons.append({"family": name, "left_mode": 0, "right_mode": mode, **comparison})
        scalar = capture(case(f"{name}_translated_scalar", powers, h, 0, 0,
                              translated=True, api="scalar"), "translated_scalar_api")
        translated_scalars.append({**scalar, "scope": "Direct rank-zero scalar API; mode is ignored by the original scalar entry point.",
                                   "comparison_to_anchored_general_mode0_scalar": compare(modes[0], scalar, first_only=True)})
    unsupported = capture(case("translated_general_transport_probe", [1, 1], -1, 2, 1,
                               translated=True), "expected_unsupported_transport")
    artifact = {"schema_version": 1, "capture_started_utc": started,
                "capture_completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "normalization": "native_iregi", "basis": "unweighted_cartesian_monomials",
                "dimension_shift_convention": "full even idim; D=4+idim-2epsilon",
                "pole_slots": ["uv1", "ir1", "ir2", "finite"],
                "tolerance": TOLERANCE,
                "comparison_scale": "Q^(4+idim+rank-2*sum(powers)) + abs(mode0_value); Q=max(mu, abs(shifts), sqrt(abs(mass_squared)))",
                "fixture_policy": "Reference stability and intermode agreement are recorded, not assumed to prove correctness. Preserve every failed or disagreeing mode; no reference repair beyond existing factorial initialization patch.",
                "translation_policy": "No hand-derived tensor translation. The original generalized transport requires zero first shift; direct translated scalar-API results are separately scoped and the rejected generalized transport probe is retained.",
                "kinematics": {"anchored_shifts": SHIFTS, "positive_mass_squared": MASSES,
                               "common_translation": TRANSLATION,
                               "rationale": "Integer spacelike differences, orthogonal nonzero external vectors, distinct positive masses; Feynman polynomial strictly positive."},
                "provenance": {"executable": relative(EXE), "executable_sha256": sha(EXE),
                               "captured_build_provenance": provenance,
                               "build_provenance_path": relative(PROVENANCE), "build_provenance_sha256": sha(PROVENANCE),
                               "script": relative(Path(__file__)), "script_sha256": sha(Path(__file__)),
                               "encoding_harness": "validation/reference/capture.py", "encoding_harness_sha256": sha(ROOT / "validation/reference/capture.py"),
                               "driver_source_sha256_current": sha(ROOT / "validation/reference/driver.f90"),
                               "recorded_build_driver": {"path": relative(historical_driver_path),
                                                         "sha256": sha(historical_driver_path),
                                                         "source_commit": historical_commit,
                                                         "matches_recorded_build_hash": True},
                               "driver_drift": {"current_matches_recorded_build": sha(ROOT / "validation/reference/driver.f90") == provenance["driver_sha256"],
                                                "diff_path": relative(driver_diff_path), "diff_sha256": sha(driver_diff_path),
                                                "scope": "Later driver changes add mass-reference deduplication and tiny-complex-width dispatch; fixtures use distinct positive real masses with snapping disabled, so these changes are inactive here. No claim is made that the executable uses the current driver."},
                               "patched_funlib_sha256": sha(ROOT / "target/reference/patched/funlib.f90"),
                               "python_executable": sys.executable, "python_version": sys.version,
                               "working_directory": str(ROOT),
                               "command": [sys.executable, relative(Path(__file__))],
                               "isolated_process_per_request": True, "timeout_seconds_per_request": 30},
                "cases": cases, "intermode_comparisons": comparisons,
                "translated_scalar_checks": translated_scalars,
                "translated_general_transport": unsupported}
    artifact["summary"] = {
        "generalized_requests": len(cases),
        "stable_finite_generalized_results": sum(c["status"] == "stable_finite_reference_result" for c in cases),
        "generalized_reference_failures": sum(c["status"] != "stable_finite_reference_result" for c in cases),
        "intermode_discrepancies": sum(c["status"] == "reference_discrepancy" for c in comparisons),
        "intermode_agreements": sum(c["status"] == "agreement" for c in comparisons),
        "translated_scalar_agreements": sum(c["comparison_to_anchored_general_mode0_scalar"]["status"] == "agreement" for c in translated_scalars),
        "translated_general_transport_rejected": unsupported["status"] == "reference_failure"}
    (OUT / "reference-capture.json").write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n")
    print(json.dumps(artifact["summary"], indent=2))


if __name__ == "__main__":
    main()
