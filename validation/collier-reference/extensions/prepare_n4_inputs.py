"""Prepare the next ordinary massive box cohort; do not run any kernel."""
import hashlib
import json
from pathlib import Path


ROOT = Path.cwd()
OUTPUT = ROOT / "validation/collier-reference/extensions"


def main():
    baseline = ROOT / "validation/benchmark/baseline-6b24c03-licensed/results-inputs.json"
    shifts = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0.25, 1.25, 0], [0, 0.125, 0.25, 1.5]]
    samples = []
    for lane in range(32):
        dilation = 1.0 + lane / 256.0
        samples.append({"shifts": [[x * dilation for x in p] for p in shifts],
                        "masses": [[float((i + 2) ** 2) + lane / 64.0, 0.0] for i in range(4)],
                        "mu": 3.0})
    cases = [{"id": f"n4-r{rank}-massive", "n": 4, "rank": rank,
              "mass_class": "massive", "samples": samples} for rank in range(4)]
    OUTPUT.mkdir(exist_ok=True)
    path = OUTPUT / "n4-inputs.json"
    path.write_text(json.dumps(cases, indent=2, allow_nan=False) + "\n")
    provenance = {"schema_version": 1, "status": "prepared-not-numerically-qualified",
                  "purpose": "Next eight N4rank0/1/2/3 ×batch1/32 ordinary undotted massive rows; no timing yet",
                  "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                  "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "existing_baseline": {"path": str(baseline.relative_to(ROOT)),
                                        "sha256": hashlib.sha256(baseline.read_bytes()).hexdigest()},
                  "shared_sample_construction": "Same lane dilation1+lane/256, squared masses(i+2)^2+lane/64, scale3 as initial N2/N3; add fixed fourth spatial shift(0,1/8,1/4,3/2)",
                  "arithmetic": "All inputs and perturbations are dyadic and exactly represented in binary64",
                  "domain": "Positive real squared masses; zero-origin spatial real shifts; no repeated powers or dimension shift",
                  "correctness_pending": "Complete Cartesian/Laurent arrays, delta-parameter probes, rank2/3 metric signs and normalization before timing",
                  "independent_uv_identity": "All undotted N4 moments through rank3 are superficially UV finite; check every UV component is zero",
                  "timing_pending": "Requires separately reviewed correctness receipt and ROOT-granted quiet cohort; no reuse of initial8 timing results"}
    (OUTPUT / "n4-inputs-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
