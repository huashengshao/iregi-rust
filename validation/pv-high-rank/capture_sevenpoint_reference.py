"""Capture original-IREGI-only evidence without modifying the Rust timeout.

Run from the project root with `source scripts/env.sh` first. This uses only
original Fortran IREGI and ordinary Python; no Symbolica process is started.
"""

from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
from math import comb
from pathlib import Path
import subprocess


DIRECTORY = Path("validation/pv-high-rank/oracle-runs")
SOURCE = DIRECTORY / "n7-base-rank7.json"
OUTPUT = DIRECTORY / "n7-base-reference-rank7.json"
INPUT = DIRECTORY / "n7-base-reference-precision-input.json"
EXECUTABLE = Path("target/reference/iregi-reference-original")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    source_bytes = SOURCE.read_bytes()
    source = json.loads(source_bytes)
    if source["status"] != "preparation_timeout" or (source["propagators"], source["rank"]) != (7, 7):
        raise ValueError("Expected the preserved seven-point rank-seven preparation timeout")
    points, masses, mu = source["shifts"], source["mass_squared"], source["mu"]
    if len(points) != 7 or len(masses) != 7 or any(len(p) != 4 for p in points):
        raise ValueError("Incomplete input fixture")
    if any(type(v) is not int for row in points for v in row) or any(type(m) is not int for m in masses) or type(mu) is not int:
        raise ValueError("This capture requires the exact integer fixture")
    executable_hash = sha256(EXECUTABLE.read_bytes())
    request = "EVAL target tensor 0 7 7 0 " + str(mu) + " 0 1e-6\n"
    request += "".join(" ".join(map(str, p + [m, 0, 1])) + "\n" for p, m in zip(points, masses))
    request += "QUIT\n"
    completed = subprocess.run([str(EXECUTABLE.resolve())], input=request, capture_output=True,
                               text=True, timeout=30, check=True)
    results = [json.loads(line[7:], parse_float=Decimal)
               for line in completed.stdout.splitlines() if line.startswith("RESULT ")]
    if len(results) != 1 or results[0].get("id") != "target":
        raise ValueError("Original IREGI returned an unexpected result set")
    reference = results[0]
    count = comb(7+4, 4)
    moments = reference.get("moments")
    if type(reference.get("stable")) is not bool or not isinstance(moments, list) or len(moments) != count:
        raise ValueError("Original IREGI returned an incomplete array")
    for moment in moments:
        if len(moment) != 4 or any(len(slot) != 2 for slot in moment):
            raise ValueError("Incorrect Laurent/component shape")
        if any(not Decimal(str(value)).is_finite() for slot in moment for value in slot):
            raise ValueError("Nonfinite reference output")
    if sha256(EXECUTABLE.read_bytes()) != executable_hash:
        raise ValueError("Reference executable changed during capture")
    if SOURCE.read_bytes() != source_bytes:
        raise ValueError("The preserved timeout changed concurrently")
    rank_of_moment = [rank for rank in range(8) for _ in range(comb(rank+3, 3))]
    with localcontext() as context:
        context.prec = 80
        q2 = max(Decimal(1), *(abs(Decimal(m)) for m in masses))
        positive_distances = []
        for i, p in enumerate(points):
            for j, q in enumerate(points):
                d = [Decimal(x-y) for x, y in zip(p, q)]
                distance = d[0]**2-sum(v*v for v in d[1:])
                q2 = max(q2, abs(distance))
                if j > i and distance > 0:
                    positive_distances.append({"pair": [i, j], "distance": str(distance)})
        f_lower_bound = min(Decimal(m) for m in masses) - sum(Decimal(row["distance"]) for row in positive_distances)/4
        if f_lower_bound <= 0:
            raise ValueError("The elementary positive-F bound no longer applies")
        q = q2.sqrt()
        summary = {}
        for slot, label in enumerate(["uv1", "ir1", "ir2"]):
            values = [(index, component, Decimal(str(moment[slot][component])))
                      for index, moment in enumerate(moments) for component in range(2)]
            normalized = [(i, c, abs(value)/q**(rank_of_moment[i]+4-14)) for i, c, value in values]
            largest = max(normalized, key=lambda row: row[2])
            summary[label] = {
                "max_absolute_native": str(max(abs(v) for _, _, v in values)),
                "max_absolute_dimensionally_normalized": str(largest[2]),
                "worst_moment": largest[0], "worst_component": largest[1],
                "nonzero_components": sum(v != 0 for _, _, v in values),
                "components_above_1e_minus_10_normalized": sum(v >= Decimal("1e-10") for _, _, v in normalized),
            }
    record = {
        "status": "reference_only", "reference_stable": reference["stable"],
        "propagators": 7, "rank": 7, "moments": count, "variant": "base",
        "shifts": points, "mass_squared": masses, "mu": mu,
        "dimension_shift": 0, "propagator_powers": "unit",
        "normalization": "Native IREGI; UV, IR single, IR double, finite; raw Cartesian moments",
        "reference_evaluation": "Original untouched IREGI IBP, complete tensor array, on-shell snapping disabled",
        "rust_evaluation": "Not performed; this artifact contains original-IREGI reference data only",
        "discrepancies": [], "reference": reference,
        "source_timeout_record": str(SOURCE), "source_timeout_sha256": sha256(source_bytes),
        "reference_binary": str(EXECUTABLE), "reference_binary_sha256": executable_hash,
        "reference_build_provenance": json.loads(Path("target/reference/provenance.json").read_text()),
        "capture_script": str(Path(__file__).relative_to(Path.cwd())),
        "capture_script_sha256": sha256(Path(__file__).read_bytes()),
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "reference_request": request, "reference_request_sha256": sha256(request.encode()),
        "reference_stdout_sha256": sha256(completed.stdout.encode()),
        "reference_stderr": completed.stderr,
        "kinematic_scale_squared": str(q2),
        "all_poles_analytically_zero": True,
        "pole_argument": "For N=7 and ranks 0..7, rank+4-2N<=-3, so UV poles vanish. All masses are positive, and F=sum(x_i*m_i^2)-sum(i<j,x_i*x_j*dij)>=min(m_i^2)-sum(dij>0,dij)/4>0, excluding IR singularities.",
        "positive_pair_distances": positive_distances, "positive_f_lower_bound": str(f_lower_bound),
        "reference_pole_summary": summary,
        "qualification": "Reference-only evidence. The original stability flag is retained, not an accuracy guarantee; numerical pole residues are explicitly reported. No Rust comparison or performance qualification is implied. The separate Rust preparation timeout remains unchanged.",
    }
    precision_input = {
        "rank": 7, "mu": str(mu), "dimension_shift": 0,
        "propagators": [{"shift": [str(x) for x in p], "mass_squared": [str(m), "0"], "power": 1}
                        for p, m in zip(points, masses)],
        "source_oracle_record": str(OUTPUT),
    }
    OUTPUT.write_text(json.dumps(record, indent=2, default=str) + "\n")
    INPUT.write_text(json.dumps(precision_input, indent=2) + "\n")
    if SOURCE.read_bytes() != source_bytes:
        raise ValueError("The preserved timeout changed concurrently")
    print(json.dumps({"reference": str(OUTPUT), "precision_input": str(INPUT),
                      "reference_stable": reference["stable"], "moments": count,
                      "positive_f_lower_bound": str(f_lower_bound), "pole_summary": summary}, indent=2))


if __name__ == "__main__":
    main()
