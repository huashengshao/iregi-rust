"""Record stability of untouched original rank-seven modes, preserving failures."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd() / "validation/reference"))
import capture

points = [[0,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[1,0,0,0],[2,3,5,7],[11,13,17,19]]
report = []
for n in range(4, 8):
    cases = []
    for mode in [0, 1]:
        case = capture.sample(f"n{n}_mode{mode}", 1, rank=7, mode=mode)
        case["propagators"] = [{"shift": points[i], "mass_squared": [(i+2)**2, 0], "power": 1}
                               for i in range(n)]
        cases.append(case)
    rows, _ = capture.evaluate(capture.OUT / "iregi-reference-original", cases)
    entry = {"propagator_count": n, "rank": 7, "shifts": points[:n],
             "mass_squared": [(i+2)**2 for i in range(n)], "mu": 3,
             "original_ibp_stable": rows[0]["stable"], "original_pv_stable": rows[1]["stable"]}
    if all(row["stable"] for row in rows):
        first, second = map(capture.values, rows)
        differences = [(abs(a[3] - b[3]) / (1 + abs(a[3])), i)
                       for i, (a, b) in enumerate(zip(first, second))]
        error, moment = max(differences)
        entry["largest_finite_relative_difference"] = error
        entry["moment_index"] = moment
        entry["ibp_coefficients"] = rows[0]["moments"][moment]
        entry["pv_coefficients"] = rows[1]["moments"][moment]
    report.append(entry)
encoded = json.dumps({"reference": "untouched original IREGI", "cases": report}, indent=2) + "\n"
Path("validation/pv-high-rank/reference-coverage.json").write_text(encoded)
print(encoded)
