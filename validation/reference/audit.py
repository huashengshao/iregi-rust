"""Reproduce known disagreements within the untouched original reference."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from capture import OUT, evaluate, sample

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    inputs = [sample(f"bubble_rank4_mode{mode}", 2, rank=4, mode=mode) for mode in range(3)]
    outputs, _ = evaluate(OUT / "iregi-reference-original", inputs)
    index = 55  # q1^4 in the packed basis through rank four.
    if not all(output["stable"] for output in outputs):
        raise AssertionError("The known issue requires all methods to claim stability")
    finite = [complex(*output["moments"][index][3]) for output in outputs]
    if abs(finite[0]-finite[1]) < 0.1 or finite[1] != finite[2]:
        raise AssertionError("Pinned-source PV/IBP discrepancy was not reproduced")
    document = {
        "schema_version": 1,
        "source_commit": "6c1b4684b46ad26c4f0ebc57eb9963649f350142",
        "issues": [{
            "id": "original-pv-bubble-rank4-quadratic-roots",
            "status": "reference disagreement reproduced; no additional source repair applied",
            "description": "Original real-mass PV and hybrid disagree with original IBP for the finite q1^4 bubble moment, while every method reports stable.",
            "input": inputs[0],
            "affected_moment": {"index": index, "exponents": [0,4,0,0]},
            "observations": [{"mode": mode, "stable": output["stable"],
                              "poles": output["moments"][index]}
                             for mode, output in enumerate(outputs)],
            "suspected_cause": "pave_reduce.f90 lines 468-475 and 2432-2439 divide only the square-root term, rather than the complete quadratic numerator, by 2*P02.",
            "oracle_policy": "Do not silently accept PV/hybrid as truth in this domain; compare independent IBP and analytic or high-precision evidence. Keep this separate from the validated factorial initialization repair."
        }]
    }
    if args.write:
        Path("validation/reference/known-issues.json").write_text(json.dumps(document, indent=2)+"\n")
    print(json.dumps(document, indent=2))

if __name__ == "__main__":
    main()
