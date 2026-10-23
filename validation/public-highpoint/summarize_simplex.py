"""Conservative estimated convergence and independent original-reference check."""
from pathlib import Path
import hashlib
import json
import math
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    here = Path("validation/public-highpoint")
    fixture = here / "fixture-conditioned_masses.json"
    source = here / "simplex_oracle.py"
    reference_path = here / "reference-conditioned_masses.json"
    reference = json.loads(reference_path.read_text())
    rows, hashes = [], {}
    for n, moment in [(6, 0), (6, 321), (7, 0)]:
        runs = {}
        for order in [16, 20]:
            for mapping in [0, 1]:
                path = here / f"simplex-n{n}-order{order}-map{mapping}.json"
                data = json.loads(path.read_text())
                if (data["status"] != "fixed_rule_evaluated" or data["fixture_sha256"] != digest(fixture)
                        or data["script_sha256"] != digest(source) or data["n"] != n
                        or data["order"] != order or data["mapping"] != mapping):
                    raise ValueError("Stale or incomplete independent quadrature")
                matches = [x for x in data["results"] if x["moment_index"] == moment]
                if len(matches) != 1:
                    raise ValueError("Missing unique independent moment")
                runs[(order, mapping)] = matches[0]
                hashes[str(path)] = digest(path)
        selected = runs[(20, 1)]
        value = selected["native_finite_imaginary"]
        if not math.isfinite(value):
            raise ValueError("Nonfinite independent value")
        changes = [abs(runs[(20, mapping)]["native_finite_imaginary"]
                       - runs[(16, mapping)]["native_finite_imaginary"]) for mapping in [0, 1]]
        changes.append(abs(runs[(20, 0)]["native_finite_imaginary"]-value))
        uncertainty = max(*changes, 64*sys.float_info.epsilon*abs(value))
        rank = sum(selected["monomial"])
        normalization = 2**(rank+4-2*n)  # Exact conditioned-family Q=sqrt(4)=2.
        normalized_uncertainty = uncertainty/normalization
        ref = next(x for x in reference["cases"] if x["id"] == f"n{n}_base_mode0")
        if ref["status"] != "captured" or ref["response"]["stable"] is not True:
            raise ValueError("Original reference incomplete or unstable")
        reference_value = ref["response"]["moments"][moment][3]
        real, imaginary = map(float, reference_value)
        error = math.hypot(real, imaginary-value)/normalization
        denominator = max(1, math.hypot(real, imaginary)/normalization)
        error /= denominator
        uncertainty /= normalization*denominator
        rows.append({
            "n": n, "moment_index": moment, "monomial": selected["monomial"],
            "native_finite_imaginary": value,
            "estimated_absolute_uncertainty_native": normalized_uncertainty*normalization,
            "estimated_absolute_uncertainty_dimensionally_normalized": normalized_uncertainty,
            "original_native_finite": reference_value,
            "original_mixed_error_dimensionally_normalized": error,
            "original_mixed_error_plus_estimated_uncertainty": error+uncertainty,
            "independent_estimated_uncertainty_below_1e_minus_11": normalized_uncertainty < 1e-11,
            "original_agreement_at_unchanged_1e_minus_10": error+uncertainty < 1e-10,
            "last_order_and_mapping_native_differences": changes,
        })
    result = {
        "status": "estimated_converged" if all(x["independent_estimated_uncertainty_below_1e_minus_11"] for x in rows) else "inconclusive",
        "rows": rows, "input_hashes": hashes,
        "fixture_sha256": digest(fixture), "reference_sha256": digest(reference_path),
        "summary_script_sha256": digest(Path(__file__)),
        "qualification": "Three independently integrated finite components only, with successive-order and mapping error estimates, not interval-certified bounds. No public Rust execution or complete-array finite qualification follows from these witnesses. Original spurious real parts are included in the complex mixed-error check. Earlier quadrature orders and failed reference families remain recorded.",
    }
    (here / "simplex-summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
