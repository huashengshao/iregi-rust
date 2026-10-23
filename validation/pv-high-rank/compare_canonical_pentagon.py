"""Compare retained physical-pentagon results using decimal arithmetic.

This does not execute a reduction. Reproduce the two source artifacts first;
the comparison qualifies only the q0*qz^3 moment, not a complete physical graph.
"""

from decimal import Decimal, localcontext
from hashlib import sha256
import json
from pathlib import Path


def main():
    directory = Path("validation/pv-high-rank")
    probe_path = directory / "canonical-pentagon-precision.json"
    reference_path = directory / "canonical-pentagon-threshold-probe.json"
    probe = json.loads(probe_path.read_text())
    reference = json.loads(reference_path.read_text())
    rows = sorted(probe["results"], key=lambda row: row["bits"])
    assert [row["bits"] for row in rows] == [128, 256]
    assert all(row["moments"][0]["monomial"] == [1, 0, 0, 3] for row in rows)
    with localcontext() as context:
        context.prec = 90
        low, high = [
            [[Decimal(value) for value in slot]
             for slot in row["moments"][0]["oneloop_native_slots"]]
            for row in rows
        ]
        q_squared = Decimal(750)**2
        tolerance = Decimal("1e-10")

        def error(actual, expected):
            # This rank-four five-point tensor has mass dimension minus two.
            difference = sum((a-b)**2 for a, b in zip(actual, expected)).sqrt()
            magnitude = sum(b*b for b in expected).sqrt()
            return difference*q_squared/(1+magnitude*q_squared)

        convergence = [error(a, b) for a, b in zip(low, high)]
        comparisons = []
        for row in reference["results"]:
            if row["input"] != "canonical" or row["threshold"] != "1e-6":
                continue
            values = [[Decimal(str(v)) for v in slot] for slot in row["target"]]
            errors = [error(a, b) for a, b in zip(values, high)]
            comparisons.append({
                "mode": row["mode"], "reference_stable": row["stable"],
                "oneloop_slots": row["target"],
                "normalized_mixed_errors": [str(e) for e in errors],
                "passes_fixed_gate": all(e < tolerance for e in errors),
            })
        assert len(comparisons) == 3
        report = {
            "scope": "Only canonical ggHHH pentagon raw tensor moment54=q0*qz^3",
            "sources": {str(p): sha256(p.read_bytes()).hexdigest()
                        for p in [probe_path, reference_path, Path(__file__)]},
            "comparison_normalization": "OneLoop UV, IR single, IR double, finite",
            "dimensional_normalization": "Multiply each complex moment by Q^2, Q=750",
            "fixed_mixed_tolerance": str(tolerance),
            "precision_convergence_normalized_errors": [str(e) for e in convergence],
            "precision_convergence_passed": all(e < tolerance for e in convergence),
            "binary256_oneloop_slots": [[str(v) for v in slot] for slot in high],
            "independent_pole_constraint": "Rank4 N5 superficial UV degree -2 and positive internal masses imply all UV/IR poles vanish.",
            "reference_comparisons": comparisons,
            "conclusion": "Highprecision PV agrees with original PV/hybrid for this component. Original IBP fails, including a UV pole independently excluded by power counting.",
            "limitations": "No complete physical tensor, graph contraction, MadLoop comparison, runtime performance, or interval-certified finite integral is qualified by this artifact.",
        }
    output = directory / "canonical-pentagon-adjudication.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["precision_convergence_passed"]:
        raise SystemExit("Precision convergence failed")
    if [row["passes_fixed_gate"] for row in comparisons] != [False, True, True]:
        raise SystemExit("Reference comparison changed; investigate retained artifacts")


if __name__ == "__main__":
    main()
