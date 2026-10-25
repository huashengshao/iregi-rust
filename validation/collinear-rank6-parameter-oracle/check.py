#!/usr/bin/env python3
"""Portable saved-byte replay of one scoped collinear rank-six reference."""
import argparse
import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = "validation/orthogonal-rank6-current-cli"
PARENT_MANIFEST = "af6a1d77de0c1ef9aeafe49833f2c140a7a75cd9b2fdca0578811cdb407be129"
OLD = "target/collinear-rank6-parameter-oracle"
NEW = "target/collinear-rank6-parameter-oracle-refinement-v3"
ALLOWED = {"argparse", "collections", "decimal", "fractions", "itertools",
           "hashlib", "json", "pathlib", "re"}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {"sha256": sha(body), "bytes": len(body)}


def load(body):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("nonfinite JSON constant: " + value)
    return json.loads(body, object_pairs_hook=pairs, parse_constant=invalid)


def safe(name):
    path = PurePosixPath(name)
    require(type(name) is str and name and not path.is_absolute()
            and ".." not in path.parts and str(path) == name, "safe evidence alias")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def restore_files(manifest=None):
    m = manifest or load((HERE / "manifest.json").read_bytes())
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts}
    require(actual == set(m["capsule_files"]) | {"manifest.json"}, "closed capsule inventory")
    for name, expected in m["capsule_files"].items():
        safe(name)
        require(desc((HERE / name).read_bytes()) == expected, "exact capsule file: " + name)
    for name, expected in m["parent_files"].items():
        safe(name)
        require(desc((ROOT / name).read_bytes()) == expected, "exact inherited capsule file: " + name)
    require(sha((ROOT / PARENT / "manifest.json").read_bytes()) == PARENT_MANIFEST,
            "fixed independently reviewed orthogonal parent")
    parent = module("collinear_saved_orthogonal_parent", ROOT / PARENT / "check.py")
    files = parent.restore_files(load((ROOT / PARENT / "manifest.json").read_bytes()))
    require(len(files) == m["parent_aliases"], "exact restored parent alias count")
    origins = load((HERE / "origins.json").read_bytes())
    members = {}
    with tarfile.open(fileobj=io.BytesIO((HERE / "payload.tar.gz").read_bytes()), mode="r:gz") as archive:
        for item in archive:
            safe(item.name)
            require(item.isfile() and item.name not in members
                    and item.name in m["payload_members"], "unique regular declared payload member")
            require(0 <= item.size <= 16000000, "bounded payload member")
            body = archive.extractfile(item).read()
            require(desc(body) == m["payload_members"][item.name], "exact archived bytes")
            require(not body.startswith(b"\x7fELF") and "__pycache__" not in PurePosixPath(item.name).parts,
                    "compiled payload forbidden")
            members[item.name] = body
    require(set(members) == set(m["payload_members"]), "complete payload member inventory")
    require(set(origins) == set(m["preserved_files"]) | set(m["inherited_aliases"]),
            "exact preserved source origins")
    for alias, row in m["preserved_files"].items():
        safe(alias)
        body = members[row["member"]]
        require(desc(body) == {k: row[k] for k in ("sha256", "bytes")}
                == {k: origins[alias][k] for k in ("sha256", "bytes")}, "own alias descriptor")
        require(alias not in files or files[alias] == body, "own/parent alias collision")
        files[alias] = body
    for alias, row in m["inherited_aliases"].items():
        safe(alias)
        body = files[row["parent_source_alias"]]
        require(desc(body) == {k: row[k] for k in ("sha256", "bytes")}
                == {k: origins[alias][k] for k in ("sha256", "bytes")}, "borrowed alias descriptor")
        require(alias not in files or files[alias] == body, "borrowed alias collision")
        files[alias] = body
    require(len(files) == m["restored_evidence_aliases"], "complete restored alias inventory")
    return files


def run_independent(files, source_alias, receipt_alias, source_pin):
    raw = files[source_alias]
    require(sha(raw) == source_pin, "unchanged independently reviewed audit source")
    tree = ast.parse(raw, filename=source_alias)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            require(all(item.name in ALLOWED for item in node.names), "stdlib audit imports only")
        elif isinstance(node, ast.ImportFrom):
            require(node.level == 0 and node.module in ALLOWED, "stdlib audit imports only")
    namespace = {"__name__": "collinear_saved_independent", "__file__": source_alias}
    exec(compile(tree, source_alias, "exec"), namespace)
    computed = namespace["audit"](lambda alias: files[alias])
    require(computed == namespace["decode"](files[receipt_alias]),
            "entire independent numeric receipt equality")
    return computed


def replay(files, manifest=None):
    m = manifest or load((HERE / "manifest.json").read_bytes())
    old = run_independent(files, OLD + "/independent/audit_saved.py", OLD + "/independent/receipt.json",
                          "2178e1e62153b4e31d2dec0b9675ac26517fe649e5db37c756656db44a2d57c0")
    require(old["comparison_records"] == 13470 and old["empirical_catalogue_passed"] is False
            and len(old["empirical_failures"]) == 6
            and old["failure_partition"] == {"order12_vs20": 5, "order12_identity_vs_reverse": 1},
            "coarse catalogue remains failed after exact replay")
    require((HERE / "independent_numeric_audit.py").read_bytes()
            == files[NEW + "/independent/audit_saved.py"], "exact portable independent checker copy")
    new = run_independent(files, NEW + "/independent/audit_saved.py", NEW + "/independent/receipt.json",
                          "a223f47dfe6fba641b4c85cc8173fdbfd60f1f62fdfecc754d3612c5536d706a")
    require(new["comparison_records"] == 15150 and new["comparison_categories"] == {
        "fixed_rule_convergence_indicator": 7560, "separate_IR_exact_zero": 2520,
        "UV_convergent_zero": 30, "original_quad_diagnostic_only": 5040}
        and new["negative_controls_passed"] == 12 and new["empirical_catalogue_passed"] is True
        and new["empirical_failures"] == [] and new["old_failed_catalogue_preserved"] is True,
        "complete fixed refinement coverage")
    peer = load(files[NEW + "/independent/source-peer-review.json"])
    require(sha(files[NEW + "/independent/source-peer-review.json"])
            == "deca7e903e973178828ce8392d7681d8addb9c5f08b725a77f101c2b98158949"
            and peer["blocking_findings"] == [], "independent source peer review")
    admission = load(files[NEW + "/anchor-admission.json"])
    index = load(files[NEW + "/anchor-index.json"])
    require((HERE / "qualification.json").read_bytes() == files[NEW + "/anchor-admission.json"]
            and sha(files[NEW + "/anchor-admission.json"]) == m["qualification_sha256"],
            "exact scoped admission copy")
    require(admission["independent_numeric_checker_sha256"] == sha(files[NEW + "/independent/audit_saved.py"])
            and admission["independent_numeric_receipt_sha256"] == sha(files[NEW + "/independent/receipt.json"])
            and admission["index_sha256"] == sha(files[NEW + "/anchor-index.json"]), "exact admission chain")
    anchor, = index["records"]
    require(anchor["order"] == 48 and anchor["map"] == "identity"
            and anchor["accepted_prefix_moments"] == 210 and anchor["accepted_native_complex_slots"] == 840
            and sha(files[anchor["result"]]) == anchor["result_sha256"], "scoped selected anchor")
    for key in ("rank7_accuracy_qualified", "broad_finite_accuracy_qualified", "rigorous_error_bound",
                "arbitrary_precision_integral_accuracy", "Float_or_Dual_integral_accuracy",
                "physical_qualification", "TIRust_agreement_qualified", "performance_evidence",
                "fresh_native_PID_package_attestations"):
        require(admission[key] is False, "scope must not widen: " + key)
    require(admission["old_failed_coarse_catalogue_remains_failed"] is True
            and admission["unexecuted_v2_source_rejection_preserved"] is True, "failed history preserved")
    return {"status": "passed_complete_saved_collinear_reference_replay",
            "coarse_records_replayed": 13470, "coarse_failures_retained": 6,
            "refinement_records_replayed": 15150, "all_order_pair_map_checks": 7560,
            "separate_IR_checks": 2520, "UV_convergent_checks": 30,
            "original_quad_diagnostic_checks": 5040, "independent_negative_controls_per_audit": 12,
            "refinement_grids": 6, "unique_saved_grids": 8, "accepted_moments": 210,
            "retained_moments": 330, "new_rows": 4608, "new_batches": 18,
            "scoped_order48_identity_empirical_anchor_admitted": True,
            "TIRust_agreement_or_Dual_or_performance_qualified": False,
            "native_PID_compiler_package_or_producer_work_executed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct", type=Path)
    args = parser.parse_args()
    manifest = load((HERE / "manifest.json").read_bytes())
    files = restore_files(manifest)
    result = replay(files, manifest)
    if args.reconstruct is not None:
        require(not args.reconstruct.exists(), "fresh reconstruction destination required")
        for name, body in files.items():
            safe(name)
            destination = args.reconstruct / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(body)
        result["reconstructed_aliases"] = len(files)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
