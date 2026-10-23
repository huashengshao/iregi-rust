"""Record the untouched original IREGI for the modest-scale rank-seven corpus.

This starts only Fortran; it does not require a Symbolica runtime lease.
Outputs are observations, not authoritative answers merely because stable=true.
"""
import hashlib
import json
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import subprocess
import time

ROOT = Path.cwd()
HERE = ROOT / "validation/public-highpoint"
EXE = ROOT / "target/reference/iregi-reference-original"


FAMILIES = {
    "wide_masses": [9, 11, 13, 17, 19, 23, 29],
    "conditioned_masses": [1, 2, 3, 4, 2, 3, 4],
    "halfstep_masses": ["1", "3/2", "2", "5/2", "3", "7/2", "4"],
    "offset_masses": [4, 5, 6, 7, 8, 9, 10],
}


def fixture(family="wide_masses"):
    shifts = [["0", "0", "0", "0"], ["0", "1", "0", "0"],
              ["0", "0", "1", "0"], ["0", "0", "0", "1"],
              ["1/2", "0", "0", "0"], ["0", "1", "1", "0"],
              ["0", "0", "1", "1"]]
    masses = [Fraction(m) for m in FAMILIES[family]]
    samples = []
    for label, scale, mass_offset in [("base", 1, 0), ("scaled_by_two", 2, 0),
                                      ("first_mass_squared_plus_one", 1, 1)]:
        samples.append({
            "id": label, "mu": str(3 * scale),
            "propagators": [{"shift": [str(Fraction(v) * scale) for v in q],
                             "mass_squared": [str((m + (mass_offset if i == 0 else 0)) * scale**2), "0"],
                             "power": 1}
                            for i, (q, m) in enumerate(zip(shifts, masses))],
        })
    return {"schema_version": 1, "name": "regular_coordinate_" + family, "samples": samples,
            "intent": "Regular four-dimensional coordinate rank, positive massive Feynman polynomial, modest scales, distinct denominators; includes exact uniform scaling and a mass perturbation. This is one structured family, not general high-point qualification."}


def decimal(value):
    value = Fraction(value)
    return Decimal(value.numerator) / Decimal(value.denominator)


def request(sample, n, mode):
    label = f"n{n}_{sample['id']}_mode{mode}"
    rows = [f"EVAL {label} tensor {mode} {n} 7 0 {decimal(sample['mu'])} 0 1e-6"]
    for p in sample["propagators"][:n]:
        rows.append(" ".join(str(decimal(v)) for v in p["shift"] + p["mass_squared"]) + " 1")
    return label, "\n".join(rows) + "\nQUIT\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=FAMILIES, default="conditioned_masses")
    parser.add_argument("--base-ibp-only", action="store_true")
    args = parser.parse_args()
    HERE.mkdir(exist_ok=True)
    data = fixture(args.family)
    fixture_path = HERE / f"fixture-{args.family}.json"
    fixture_path.write_text(json.dumps(data, indent=2) + "\n")
    exe_hash = hashlib.sha256(EXE.read_bytes()).hexdigest()
    result = {"schema_version": 1, "status": "started", "reference": "untouched original IREGI",
              "executable_sha256": exe_hash, "fixture": str(fixture_path.relative_to(ROOT)),
              "fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
              "cases": []}
    destination = HERE / f"reference-{args.family}.json"
    with localcontext() as context:
        context.prec = 80
        for n in [6, 7]:
            for sample in data["samples"][:1 if args.base_ibp_only else 3]:
                for mode in [0] if args.base_ibp_only else [0, 1, 2]:
                    label, text = request(sample, n, mode)
                    entry = {"id": label, "propagators": n, "rank": 7, "sample": sample["id"],
                             "mode": mode, "request": text, "status": "running"}
                    result["cases"].append(entry)
                    destination.write_text(json.dumps(result, indent=2) + "\n")
                    started = time.monotonic()
                    try:
                        child = subprocess.run([str(EXE)], input=text, text=True,
                                               capture_output=True, timeout=30, check=False)
                    except subprocess.TimeoutExpired as error:
                        entry.update(status="timeout", elapsed_seconds=time.monotonic()-started,
                                     stdout=(error.stdout or b"").decode() if isinstance(error.stdout, bytes) else error.stdout,
                                     stderr=(error.stderr or b"").decode() if isinstance(error.stderr, bytes) else error.stderr)
                        continue
                    entry.update(exit_code=child.returncode, elapsed_seconds=time.monotonic()-started,
                                 stdout=child.stdout, stderr=child.stderr)
                    responses = [json.loads(line[7:], parse_float=str) for line in child.stdout.splitlines()
                                 if line.startswith("RESULT ")]
                    if child.returncode or len(responses) != 1 or responses[0].get("id") != label:
                        entry["status"] = "transport_failed"
                        continue
                    response = responses[0]
                    moments = response.get("moments")
                    if (type(response.get("stable")) is not bool or not isinstance(moments, list)
                            or len(moments) != 330 or any(len(m) != 4 for m in moments)
                            or any(len(s) != 2 for m in moments for s in m)
                            or any(not Decimal(str(v)).is_finite() for m in moments for s in m for v in s)):
                        entry["status"] = "malformed_response"
                        continue
                    entry.update(status="captured", response=response)
                    points = [[decimal(v) for v in p["shift"]] for p in sample["propagators"][:n]]
                    masses = [decimal(p["mass_squared"][0]) for p in sample["propagators"][:n]]
                    q2, positive_sum = max(masses), Decimal(0)
                    for i in range(n):
                        for j in range(i):
                            delta = [a-b for a, b in zip(points[i], points[j])]
                            distance = delta[0]**2-sum(v*v for v in delta[1:])
                            q2 = max(q2, abs(distance))
                            positive_sum += max(distance, Decimal(0))
                    f_lower = min(masses)-positive_sum/4
                    assert f_lower > 0
                    ranks = [r for r in range(8) for t in range(r+1) for x in range(r-t+1) for y in range(r-t-x+1)]
                    failures = []
                    worst = Decimal(0)
                    for index, (rank, moment) in enumerate(zip(ranks, moments)):
                        normalization = q2.sqrt() ** (rank+4-2*n)
                        for slot in range(3):
                            error = max(abs(Decimal(str(v))) for v in moment[slot]) / normalization
                            worst = max(worst, error)
                            if error > Decimal("1e-10"):
                                failures.append({"index": index, "slot": slot, "normalized_absolute_residue": str(error)})
                    entry["independent_pole_check"] = {
                        "all_poles_zero": True,
                        "reason": "rank+4-2N<0 at every requested rank; positive masses and the stated positive F lower bound exclude infrared singularities",
                        "positive_F_lower_bound": str(f_lower), "Q_squared": str(q2),
                        "maximum_normalized_absolute_pole_residue": str(worst),
                        "violations_at_1e_minus_10": failures,
                    }
                    print(label, "stable", response["stable"], "pole_failures", len(failures), flush=True)
    assert hashlib.sha256(EXE.read_bytes()).hexdigest() == exe_hash
    result["status"] = "complete"
    result["qualification"] = "Reference-only capture. Stability flags and every pole violation are retained. No Rust numerical or performance qualification follows from this capture."
    destination.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
