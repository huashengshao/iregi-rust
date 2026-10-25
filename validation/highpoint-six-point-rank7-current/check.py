#!/usr/bin/env python3
"""Replay saved complete-array gates without building or evaluating integrals."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE/name).read_text(), parse_float=str)


def within(a, b, unit, tolerance):
    return sum((x-y)**2 for x,y in zip(a,b)) <= tolerance**2 * max(unit**2, sum(x*x for x in b))


def main():
    manifest = read("manifest.json")
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == digest, name
    source_hashes = read("source-freeze.json")
    with tarfile.open(HERE/"sources.tar.gz", "r:gz") as archive:
        assert sorted(archive.getnames()) == sorted(source_hashes)
        for member in archive:
            assert hashlib.sha256(archive.extractfile(member).read()).hexdigest() == source_hashes[member.name]
    reference = read("quad-ibp.json")
    raw = [json.loads(s[7:], parse_float=str) for s in (HERE/"quad-ibp.stdout").read_text().splitlines() if s.startswith("RESULT ")]
    assert raw == [reference] and reference["stable"] is True
    assert reference["poles"] == ["uv1", "ir1", "ir2", "finite"]
    basis = [[t,x,y,r-t-x-y] for r in range(8) for t in range(r,-1,-1)
             for x in range(r-t,-1,-1) for y in range(r-t-x,-1,-1)]
    expected = [[tuple(F(v) for v in s) for s in m] for m in reference["moments"]]
    assert len(expected) == len(basis) == 330 and all(len(m)==4 for m in expected)
    arrays = []
    inputs = None
    for bits in [128,256]:
        data = read(f"rank7-{bits}/result.json")
        receipt = read(f"rank7-{bits}/receipt.json")
        assert receipt["status"] == "passed" and receipt["source_changes"] == []
        assert data["status"] == "all_lanes_success" and data["basis"] == basis
        assert data["working_bits"] == bits and data["requested_bits"] == 53
        assert data["rows"] == data["components"] == 1
        if inputs is None: inputs = data["input_exact_rational"]
        assert data["input_exact_rational"] == inputs
        lane = data["lanes"][0]
        assert lane["status"] == "Success" and len(lane["moments"]) == 330
        values = [[(F(s["real"]), F(s["imaginary"])) for s in m] for m in lane["moments"]]
        assert all(len(m)==4 for m in values)
        for i,m in enumerate(values):
            for slot,a in enumerate(m):
                assert within(a, expected[i][slot], F(2)**(sum(basis[i])-8), F(1,10**10)), (bits,i,slot)
        arrays.append(values)
    for i in range(330):
        for slot in range(4):
            assert within(arrays[0][i][slot], arrays[1][i][slot], F(2)**(sum(basis[i])-8), F(1,2**80)), (i,slot)
    print(json.dumps({"status":"passed","payload_files":len(manifest["files"]),"source_files":len(source_hashes),"complex_reference_comparisons":2640,"precision_pairs":1320,"new_integrals_or_compilers_executed":False,"full_goal_complete":False}))


if __name__ == "__main__":
    main()
