"""Capture full tensor arrays with the original optional on-shell policy.

Run from the project root after the isolated reference build. This deliberately
contains no Rust evaluation; each array is independently produced by IREGI.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path.cwd()
HERE = ROOT / "validation/reference/snapping"
spec = importlib.util.spec_from_file_location("iregi_reference_capture", HERE.parent / "capture.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


def cases():
    result = []
    for mode in [0, 1, 2]:
        for name, shifts in [
            ("bubble_near_mass", [[0, 0, 0, 0], [2.0000001, 0, 0, 0]]),
            ("triangle_cross_dot", [[0, 0, 0, 0], [1, 0, 0, 0], [4.000001, 1, 0, 0]]),
            ("box_cross_dot", [[0, 0, 0, 0], [1, 0, 0, 0], [4.000001, 1, 0, 0], [0, .3, 1, .2]]),
        ]:
            base = capture.sample(f"{name}_mode{mode}", len(shifts), rank=2, mode=mode)
            base["snap"] = True
            for propagator, shift in zip(base["propagators"], shifts):
                propagator["shift"] = shift
            result.append(base)
            translated = copy.deepcopy(base)
            translated["id"] += "_translated_complex"
            offset = [.25, .125, -.25, .125]
            for propagator in translated["propagators"]:
                propagator["shift"] = [x + y for x, y in zip(propagator["shift"], offset)]
                propagator["mass_squared"][1] = -.01 * propagator["mass_squared"][0]
            result.append(translated)
            if len(shifts) > 2:
                # Keep the original exact bubble pseudothreshold above as a
                # visible exceptional case. This distinct ordinary variant
                # keeps p1.p2=4.000001 but avoids that Cayley singularity.
                regular = copy.deepcopy(base)
                regular["id"] = regular["id"].replace("_mode", "_regular_mode")
                regular["propagators"][1]["shift"] = [1.25, 0, 0, 0]
                regular["propagators"][2]["shift"] = [3.2000008, 1, 0, 0]
                result.append(regular)
                regular_complex = copy.deepcopy(regular)
                regular_complex["id"] += "_translated_complex"
                for propagator in regular_complex["propagators"]:
                    propagator["shift"] = [x + y for x, y in zip(propagator["shift"], offset)]
                    propagator["mass_squared"][1] = -.01 * propagator["mass_squared"][0]
                result.append(regular_complex)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, default=ROOT / "target/snapping-reference/oracle-build/iregi-reference")
    parser.add_argument("--write-fixtures", action="store_true")
    args = parser.parse_args()
    inputs = cases()
    results, process = capture.evaluate(args.executable, inputs)
    if not all(result["stable"] for result in results):
        unstable = [result["id"] for result in results if not result["stable"]]
        raise AssertionError(f"Reference legacy cases are unstable: {unstable}\n{process.stdout}")
    unsupported_inputs = []
    for api, rank, power, mode in [("tensor", 0, 1, 0), ("tensor", 2, 1, 0), ("tensor", 2, 1, 1), ("general", 0, 2, 0)]:
        for snap in [False, True]:
            sample = capture.sample(f"negative_zero_threshold_{api}_{rank}_{power}_{mode}_{snap}", 1, rank=rank, mode=mode, api=api, powers=[power])
            sample["snap"] = snap
            sample["threshold"] = 0
            sample["propagators"][0]["mass_squared"] = [-4, 0]
            unsupported_inputs.append(sample)
    unsupported_results, _ = capture.evaluate(args.executable, unsupported_inputs)
    if not all(result["stable"] for result in unsupported_results):
        raise AssertionError("Negative-reference zero-threshold evidence is unstable")
    data = {
        "schema_version": 1,
        "executable_sha256": hashlib.sha256(args.executable.read_bytes()).hexdigest(),
        "driver_sha256": hashlib.sha256((HERE.parent / "driver.f90").read_bytes()).hexdigest(),
        "cases": [{"input": sample, "reference": result} for sample, result in zip(inputs, results)],
        "nonphysical_zero_threshold_evidence": [{"input": sample, "reference": result} for sample, result in zip(unsupported_inputs, unsupported_results)],
    }
    path = HERE / "reductions.json"
    if args.write_fixtures:
        path.write_text(json.dumps(data, indent=2) + "\n")
    else:
        saved = json.loads(path.read_text())
        for field in ["cases", "nonphysical_zero_threshold_evidence"]:
            if data[field] != saved[field]:
                raise AssertionError(f"Full legacy reduction fixtures changed: {field}")
    print(f"PASS: {len(results)} stable original-IREGI legacy tensor arrays")


if __name__ == "__main__":
    main()
