#!/usr/bin/env python3
"""Create exact, explicit timing inputs; does not run a numerical executable."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DESTINATION = Path(__file__).with_name("inputs.json")
FIXTURE = Path("validation/highpoint-seven-point-current-cargo/fixture.json")
raw = (ROOT / FIXTURE).read_bytes()
fixture = json.loads(raw)
base = fixture["samples"][0]


def case(identifier, section, n, rank, *, power=1, shift=0, numeric="f64", bits=53,
         algorithm="Hybrid"):
    propagators = base["propagators"][:n]
    powers = [1] * n
    powers[0] = power
    unsupported = []
    if power != 1:
        unsupported.append("positive repeated propagator powers (dotted denominators)")
    if shift:
        unsupported.append("independent dimension shift D=4+2h-2epsilon with h nonzero")
    return {
        "id": identifier,
        "table": section,
        "label": f"N={n}, R={rank}",
        "input_family": "conditioned massive Cartesian prefix E",
        "input_fixture": str(FIXTURE),
        "input_sample": base.get("id", "base"),
        "input_selection": f"first {n} propagators, unchanged shifts/masses/scale",
        "collier_unsupported_reason": "; ".join(unsupported) if unsupported else None,
        "driver_request": {
            "id": identifier,
            "n": n,
            "rank": rank,
            "powers": powers,
            "dimension_shift": shift,
            "algorithm": algorithm,
            "numeric_type": numeric,
            "working_bits": bits,
            "requested_bits": 53,
            "samples": [{
                "shifts": [p["shift"] for p in propagators],
                "masses_squared": [p["mass_squared"] for p in propagators],
                "mu": base["mu"],
            }],
            "warmup": 1 if n >= 5 else 3,
            "repeats": 5 if n >= 5 else 11,
            "iterations": 1,
            "target_block_ns": None if n >= 5 else 100_000_000,
            "maximum_iterations": 10_000,
        },
    }


ordinary = [
    case("ordinary-n1-r0", "ordinary", 1, 0),
    case("ordinary-n1-r6", "ordinary", 1, 6),
    case("ordinary-n2-r1", "ordinary", 2, 1),
    case("ordinary-n2-r6", "ordinary", 2, 6),
    case("ordinary-n3-r2", "ordinary", 3, 2),
    case("ordinary-n3-r3", "ordinary", 3, 3),
    case("ordinary-n3-r6", "ordinary", 3, 6),
    case("ordinary-n4-r4", "ordinary", 4, 4),
    case("ordinary-n4-r6", "ordinary", 4, 6),
    case("ordinary-n5-r5", "ordinary", 5, 5, numeric="float", bits=128),
    case("ordinary-n5-r6", "ordinary", 5, 6, numeric="float", bits=128),
    case("ordinary-n6-r6", "ordinary", 6, 6, numeric="float", bits=128),
]
extended = [
    case("extended-n1-r6-dot2", "extended", 1, 6, power=2, numeric="float", bits=128,
         algorithm="Ibp"),
    case("extended-n2-r2-dot2", "extended", 2, 2, power=2, numeric="float", bits=128,
         algorithm="Ibp"),
    case("extended-n3-r4-dot2", "extended", 3, 4, power=2, numeric="float", bits=128,
         algorithm="Ibp"),
    case("extended-n4-r6-dot2", "extended", 4, 6, power=2, numeric="float", bits=128,
         algorithm="Ibp"),
    case("extended-n4-r6-dot3", "extended", 4, 6, power=3, numeric="float", bits=128,
         algorithm="Ibp"),
    case("extended-n3-r2-h1", "extended", 3, 2, shift=1, numeric="float", bits=128,
         algorithm="Ibp"),
]
suite = {
    "schema_version": 1,
    "suite_id": "opening-rank6-20261026",
    "purpose": "Representative absolute warm profiled timing; no speed-parity gate",
    "output_scope": "Every cumulative Cartesian tensor through rank R and all native UV/IR/finite slots",
    "sample_lanes": 1,
    "input_family": {
        "name": "E",
        "fixture": str(FIXTURE),
        "fixture_sha256": hashlib.sha256(raw).hexdigest(),
        "metric": "+---",
        "shifts_time_first": [p["shift"] for p in base["propagators"][:6]],
        "masses_squared": [p["mass_squared"] for p in base["propagators"][:6]],
        "scale_mu": base["mu"],
        "preserve_inputs": True,
        "embedding": "Exact rational strings, exactly representable in all selected binary domains",
    },
    "timing_contract": {
        "api": "TensorReductionPlan / TensorWorkspace, explicit Symbolica master policy, profiling enabled",
        "exclusive": "Per-call outer wall time minus the aggregate nested scalar-master wall time",
        "inclusive": "Per-call wall time around reduce_batch only; does not include subsequent output checks or I/O",
        "phase_additivity": "Arithmetic means of the same calls; exclusive plus masters equals total",
        "excluded": ["plan preparation", "workspace construction", "first call/lazy specialization", "warmup", "full-array equality and finite checks", "JSON I/O", "process startup"],
        "selection": "The profiler changes eligible thin high-point workspace dispatch to the existing AffinePower path; actual engine is always retained",
        "blocks": "N<=4: three warmup calls, then 11 fixed blocks, loop count chosen once from final warmup, target 100 ms capped at 10000 calls. N>=5: one warmup, then five one-call blocks fixed in advance.",
        "precision": "Per-row working precision and requested accuracy parameter retained; no achieved-bits certificate inferred",
        "failure_policy": "Keep failed, refused, killed and unmeasured rows visible; do not replace them with zero timing",
    },
    "validation_notice": "The driver verifies complete finite successful arrays, exact repeated-output equality and input preservation. Independent reference qualification remains separate and is not inferred from repetition.",
    "cases": ordinary + extended,
}
DESTINATION.write_text(json.dumps(suite, indent=2) + "\n")
print(json.dumps({"output": str(DESTINATION.relative_to(ROOT)), "cases": len(suite["cases"]),
                  "sha256": hashlib.sha256(DESTINATION.read_bytes()).hexdigest()}))
