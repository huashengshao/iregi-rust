"""Compare complete current-Cargo tensors with saved original quad IBP.

All gates use exact represented rationals. Decimal is presentation only.
No reducer, reference process, symbolic algebra or numerical integral runs here.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
HERE = ROOT / "target/rank7-six-current"
QUAD = ROOT / "target/quad-iregi-source-audit"


def read(path):
    return json.loads(Path(path).read_text(), parse_float=str)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(a, b, unit, tolerance):
    squared = sum((x-y)**2 for x, y in zip(a, b)) / max(unit**2, sum(x*x for x in b))
    with localcontext() as context:
        context.prec = 100
        display = str((Decimal(squared.numerator)/Decimal(squared.denominator)).sqrt())
    return squared <= tolerance**2, display


def main():
    recipe = read(QUAD / "recipe-v6.json")
    ordinal, case = next((i, c) for i, c in enumerate(recipe["runtime"]["cases"])
                         if c["id"] == "n6_base_mode0")
    reference_path = Path(recipe["runtime"]["directory"]) / f"request-{ordinal}.stdout"
    responses = [json.loads(line[len("RESULT "):], parse_float=str)
                 for line in reference_path.read_text().splitlines() if line.startswith("RESULT ")]
    require(len(responses) == 1, "one complete original response required")
    response = responses[0]
    require(response["id"] == case["id"] and response["stable"] is True, "stable IBP required")
    require(response["poles"] == ["uv1", "ir1", "ir2", "finite"], "native pole ordering")
    expected = [[tuple(F(x) for x in s) for s in m] for m in response["moments"]]
    basis = [[t,x,y,r-t-x-y] for r in range(8) for t in range(r,-1,-1)
             for x in range(r-t,-1,-1) for y in range(r-t-x,-1,-1)]
    require(len(expected) == len(basis) == 330 and all(len(m) == 4 for m in expected), "full reference shape")
    old_root = ROOT / "validation/highpoint-thin-n6-rank7-phase/phase"
    old_paths = {128: old_root/"n6-rank7-128-001/result.json",
                 256: old_root/"n6-rank7-256-diagnostic-001/result.json"}
    summary = []
    arrays = {}
    failures = []
    for bits in [128, 256]:
        directory = HERE / f"rank7-{bits}"
        receipt, data = read(directory/"receipt.json"), read(directory/"result.json")
        require(receipt["status"] == "passed" and receipt["source_changes"] == [], "capture process/source guard")
        require(data["status"] == "all_lanes_success" and data["basis"] == basis, "complete successful tensor basis")
        require(data["working_bits"] == bits and data["requested_bits"] == 53, "precision context")
        require(data["rows"] == data["components"] == 1, "ordinary singleton shape")
        old = read(old_paths[bits])
        require(data["settings"] == old["settings"] and data["input_exact_rational"] == old["input_exact_rational"], "exact fixture/settings identity")
        require(len(data["lanes"]) == 1 and data["lanes"][0]["status"] == "Success", "complete lane")
        raw = data["lanes"][0]["moments"]
        require(len(raw) == 330 and all(len(m) == 4 for m in raw), "all 1320 complex slots")
        arrays[bits] = [[(F(s["real"]), F(s["imaginary"])) for s in m] for m in raw]
        stats = data["execution"]
        require(stats["child_batch_calls"] == stats["parent_batch_calls"] == 1
                and stats["packed_child_rows"] == 6 and stats["packed_parent_rows"] == 1, "packed recurrence batch accounting")
        maximum = Decimal(0)
        for i, monomial in enumerate(basis):
            unit = F(2)**(sum(monomial)-8)
            for slot in range(4):
                passed, display = check(arrays[bits][i][slot], expected[i][slot], unit, F(1,10**10))
                maximum = max(maximum, Decimal(display))
                if not passed:
                    failures.append({"working_bits":bits,"moment":i,"basis":monomial,"slot":slot,"error":display})
        summary.append({"working_bits":bits,"moments":330,"complex_slots":1320,"maximum_normalized_reference_error":str(maximum),"capture_sha256":sha(directory/"result.json")})
    maximum = Decimal(0)
    for i, monomial in enumerate(basis):
        for slot in range(4):
            passed, display = check(arrays[128][i][slot], arrays[256][i][slot], F(2)**(sum(monomial)-8), F(1,2**80))
            maximum = max(maximum, Decimal(display))
            if not passed:
                failures.append({"precision_pair":True,"moment":i,"slot":slot,"error":display})
    result = {"status":"passed" if not failures else "failed", "scope":"Actual locked/offline current-Cargo public SixPoint rank7, ordinary Float128/256, retained real-mass fixture only", "captures":summary,"reference_sha256":sha(reference_path),"comparator_sha256":sha(__file__),"reference_tolerance":"1e-10","precision_tolerance":"2^-80","precision_complex_pairs":1320,"maximum_normalized_precision_difference":str(maximum),"packed_child_batch_checked":True,"failures":failures,"complete_goal_qualified":False,"performance_qualified":False,"lifecycle_and_contractions_qualified":False}
    destination = HERE/"comparison.json"
    require(not destination.exists(), "preserve prior comparisons")
    destination.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
