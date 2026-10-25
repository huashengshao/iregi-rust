#!/usr/bin/env python3
"""Portable saved-data replay only; no producer or numerical package imports."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = "validation/quad-original-iregi-generalized-rank7"
PRIVATE = "target/low-n-complex-rank7-oracle"
BASE = PRIVATE+"/quadrature-proposal"
CAPTURE = BASE+"/capture-001"
HISTORICAL = "/shared/external/iregi/iregi-rust/"
AUDIT_SHA = "94e726bced4201332edf714ff60d1c7c82661dd360150cc681b825fdef06f0a0"
MATH_SHA = "b2a68e18d02b199145a87d8d6cc901c2be72b40cb551c9c1326ab6b2cfc7d8be"
METADATA_SHA = "44d9baa70e2c684356917c40ae956f6db593719929b7392914c7560ab5f62318"


def require(ok,message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return dict(sha256=sha(body),bytes=len(body))


def load(body):
    def pairs(items):
        result = {}
        for key,value in items:
            require(key not in result,"duplicate JSON key")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("nonfinite JSON constant: "+value)
    return json.loads(body,object_pairs_hook=pairs,parse_constant=invalid,parse_float=str)


def module(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def restore(manifest):
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts}
    require(actual==set(manifest["capsule_files"])|{"manifest.json"},"exact capsule inventory")
    for name,expected in manifest["capsule_files"].items():
        require(desc((HERE/name).read_bytes())==expected,"capsule byte identity: "+name)
    for name,expected in manifest["parent_files"].items():
        require(desc((ROOT/name).read_bytes())==expected,"parent byte identity: "+name)
    require(sha((ROOT/PARENT/"manifest.json").read_bytes())==
        "ccda92bdd0be40484b2d8762d479658ada0beb98eb610df7c96b44f7f521a0b0","fixed generalized quad parent")
    require(sha((ROOT/PARENT/"check.py").read_bytes())==
        "8bd9efc8ee6f95f9a0387c3510f105b9bceda416aade16c2e3bee2ef445cee7e","fixed independent parent checker")
    parent = module("complex_oracle_generalized_quad_parent",ROOT/PARENT/"check.py")
    pm = load((ROOT/PARENT/"manifest.json").read_bytes())
    files,helpers,inherited = parent.restore(pm)
    parent_summary = parent.replay(files,helpers,pm)
    for name in manifest["parent_files"]:
        body = (ROOT/name).read_bytes()
        require(name not in files or files[name]==body,"parent top-file collision")
        files[name] = body
    for name,expected in manifest["required_parent_sources"].items():
        require(name in files and desc(files[name])==expected,"inherited original-quad source context")
    members = helpers.read_archive((HERE/"payload.tar.gz").read_bytes(),manifest["payload_members"])
    origins = load((HERE/"payload-origins.json").read_bytes())
    require(set(origins)==set(manifest["preserved_files"])|set(manifest["inherited_aliases"]),"exact alias origin inventory")
    for name,row in manifest["preserved_files"].items():
        helpers.safe(name)
        body = members[row["member"]]
        expected = {k:row[k] for k in ("sha256","bytes")}
        require(desc(body)==expected=={k:origins[name][k] for k in expected},"preserved alias bytes")
        require(name not in files or files[name]==body,"new/parent alias collision")
        files[name] = body
    for name,row in manifest["inherited_aliases"].items():
        helpers.safe(name)
        body = files[row["inherited_source"]]
        expected = {k:row[k] for k in ("sha256","bytes")}
        require(desc(body)==expected=={k:origins[name][k] for k in expected},"borrowed alias bytes")
        require(name not in files or files[name]==body,"borrowed alias collision")
        files[name] = body
    return files,dict(parent_reference_replay=parent_summary,inherited=inherited)


def restore_files(manifest):
    return restore(manifest)[0]


def replay(files,manifest=None):
    manifest = manifest or load((HERE/"manifest.json").read_bytes())
    read = lambda name: load(files[PRIVATE+"/"+name])
    # Import the independent saved-only checker unchanged. Its __main__ writer
    # is inactive; audit() can read only the supplied original-path aliases.
    raw = (HERE/"independent_numeric_audit.py").read_bytes()
    require(sha(raw)==AUDIT_SHA and raw==files[PRIVATE+"/review/audit_saved_complex.py"],"unchanged independent checker bytes")
    audit = module("complex_oracle_independent_saved_numeric",HERE/"independent_numeric_audit.py")
    computed = audit.audit(lambda alias: files[alias])
    saved_raw = files[PRIVATE+"/review/independent-saved-complex-numeric.json"]
    require(sha(saved_raw)==MATH_SHA,"independent numeric receipt pin")
    require(computed==audit.decode(saved_raw),"entire independently recomputed numeric receipt equality")
    require(computed["comparison_records"]==43566 and computed["separate_IR_zero_checks"]==11880
            and computed["complete_native_complex_slots"]==23760 and computed["negative_controls_passed"]==15
            and computed["failures"]==0,"complete independent numeric coverage")

    metadata_raw = files[PRIVATE+"/review/independent-saved-complex-metadata.json"]
    require(sha(metadata_raw)==METADATA_SHA,"independent metadata receipt pin")
    metadata = load(metadata_raw)
    require(metadata["status"]=="passed_independent_saved_complex_metadata_source_bindings_and_terminal_attestation_review"
            and metadata["findings"]==[] and metadata["checks_passed"]==453,
            "saved metadata/source review clear")
    # Archive the metadata auditor as provenance only. Never import it: its
    # original execution context includes historical process/source checks.
    require(sha(files[PRIVATE+"/review/audit_saved_complex_metadata.py"])==metadata["audit_source_sha256"],
            "archived metadata checker identity")
    for name,expected in metadata["freshly_verified"]["raw_saved_files_hashed"].items():
        require(name in files and desc(files[name])==expected,"saved metadata byte descriptor")

    gate = read("engineering-v3/review/saved-gate-attestation.json")
    require(sha(files[PRIVATE+"/engineering-v3/review/saved-gate-attestation.json"])==
        "31cb525c1545b1f121e2b33dd08e4374daece57ac54edc6e9fd3931455ee5a5c"
        and gate["findings"]==[] and gate["prerequisite_component_gates_passed"] is True,
        "independent composite control attestation")
    for name,digest in gate["evidence_sha256"].items():
        require(sha(files[PRIVATE+"/engineering-v3/"+name])==digest,"exact composite gate saved evidence")
    require(gate["Rust_tests"]["passed"]==15 and gate["separate_corrected_Python_controls"]["passed"]==17
            and gate["preserved_combined_phase"]["saved_status"]=="failed", "15+17 controls preserve initial failure")
    initial,combined,corrected = read("build-001/receipt.json"),read("engineering-v3/tests-001/receipt.json"),read("engineering-v3/python-controls-001/receipt.json")
    require(initial["status"]=="failed" and b"E0599" in files[PRIVATE+"/build-001/step-1.log"],"initial accessor compile failure remains failed")
    require(combined["status"]=="failed" and b"No module named 'numpy'" in files[PRIVATE+"/engineering-v3/tests-001/step-2.log"]
            and corrected["status"]=="passed" and corrected["Rust_rebuilt"] is False,"failed bare environment and separate correction")
    engineering = read("engineering-v3/packet.json")
    require(sha(files[PRIVATE+"/engineering-v3/packet.json"])=="45fc274db39bb1ab2877794f287491ffd25e4a35bc5d2239d7fcff0b027ddd26","actual engineering source packet")
    for name,expected in engineering["rust_source_files"].items():
        body = files[PRIVATE+"/engineering-v3/"+name]
        require(desc(body)==expected,"actual five Rust source leaves")
        alias = "crates/iregi-rust/examples/parameter_oracle/"+Path(name).name
        require(files[alias]==body,"actual staged source alias")

    for directory in ("build-001","engineering-v3/build-001","engineering-v3/tests-001","engineering-v3/python-controls-001"):
        receipt = read(directory+"/receipt.json")
        for name,digest in receipt.get("outputs",{}).items():
            alias = PRIVATE+"/"+directory+"/"+name
            if alias in files:
                require(sha(files[alias])==digest,"saved build/control output digest")
            else:
                require(manifest["omitted_native_products"][alias]["captured_sha256"]==digest,"explicit omitted compiled output attestation")

    catalogue,receipt,release = read("quadrature-proposal/catalog.json"),read("quadrature-proposal/capture-001/receipt.json"),read("quadrature-proposal/numerical-release.json")
    require(receipt["status"]=="complete_catalogue_pending_independent_saved_audit"
            and receipt["bound_seconds"]==1200 and receipt["cleanup_reserve_seconds"]==45
            and receipt["inputs_unchanged"] is True and receipt["cleanup_errors"]==[]
            and receipt["cancellation"] is None and receipt["empirical_gates_passed"] is True
            and receipt["total_worker_rows"]==88256 and len(receipt["workers"])==3,
            "saved finite catalogue terminal state")
    require(release["outer_exit_code"]==0 and release["CPU26_released"] is True
            and release["receipt_sha256"]==sha(files[CAPTURE+"/receipt.json"])
            and release["comparison_sha256"]==sha(files[CAPTURE+"/comparison.json"]),"historical outer release chain")
    for worker in receipt["workers"]:
        n = worker["topology"]
        artifact = load(files[CAPTURE+f"/n{n}-symbolica-coefficients.json"])
        require(sha(files[CAPTURE+f"/n{n}-symbolica-coefficients.json"])==worker["artifact_sha256"]
                and artifact["basis"]==load(files[CAPTURE+f"/grids/n{n}-order32-identity/result.json"])["basis"],
                "coefficient artifact hash")
        # No symbolic expressions are evaluated. Shape/zero strings preserve
        # the already independently tested exact Symbolica preparation.
        require(artifact["topology"]==n and artifact["moments"]==330 and artifact["outputs"]==1320
                and len(artifact["expressions"])==1320 and artifact["native_normalization_included"] is True
                and all(artifact["expressions"][4*m+s]=="0" for m in range(330) for s in (1,2)),
                "complete source expressions and separate IR zeros")
        require(worker["status"]=="complete" and worker["owned_group_gone"] is True
                and any(g["topology"]==n and g["owned_process_group"]==worker["owned_process_group"]
                        and g["actually_absent"] is True for g in release["groups"]),"historical worker group release")
        for grid in (g for g in catalogue["grids"] if g["topology"]==n):
            progress = load(files[CAPTURE+"/grids/"+grid["id"]+"/progress.json"])
            require(progress["points_completed"]==grid["points"],"final preserved progress count")

    source_review = read("review/quadrature-proposal-source-review.json")
    require(source_review["status"]=="passed_source_only_numerical_closure_runner_review"
            and source_review["manifest_sha256"]==sha(files[BASE+"/manifest.json"])
            and source_review["blocking_findings"]==[],"finite source review")
    index,admission = read("quadrature-proposal/anchor-index.json"),read("quadrature-proposal/anchor-admission.json")
    require(sha(files[BASE+"/anchor-index.json"])=="bdeee49b1ca2979ef4275c72d646d49922fb21e210e0e96c3736a587a05fb999"
            and sha(files[BASE+"/anchor-admission.json"])=="0352163a61102427b2dfc77ecb93b32865f1bd4de55805884d13b3266bc21add",
            "fixed anchor index and additive final admission")
    require(admission["independent_numeric_review_sha256"]==MATH_SHA
            and admission["independent_numeric_checker_sha256"]==AUDIT_SHA
            and admission["independent_metadata_review_sha256"]==METADATA_SHA
            and admission["index_sha256"]==sha(files[BASE+"/anchor-index.json"])
            and admission["TIRust_agreement_not_qualified_by_this_admission"] is True,
            "final scoped anchor admission chain")
    for anchor in index["records"]:
        alias = anchor["result"].removeprefix(HISTORICAL)
        require(sha(files[alias])==anchor["result_sha256"] and anchor["order"]==32
                and anchor["map"]=="identity" and anchor["accepted_rank6_prefix_moments"]==210,
                "selected order32 anchors and exact rank6 prefix")
    require((HERE/"qualification.json").read_bytes()==files[BASE+"/anchor-admission.json"],"exact additive qualification copy")
    return dict(status="passed_complete_independent_complex_saved_receipt_replay",
        complete_grids=18,point_rows=88256,complete_complex_slots=23760,exact_comparison_records=43566,
        separate_IR_zero_checks=11880,independent_negative_controls=15,
        source_Rust_tests=15,source_Python_controls=17,preserved_failed_build=True,
        preserved_failed_bare_Python_phase=True,N4_original_reference_eligible=False,
        N4_scoped_empirical_reference_admitted=True,TIRust_agreement_qualified=False,
        rigorous_error_bound=False,arbitrary_precision_integral_accuracy=False,
        metadata_or_PID_or_native_or_package_hashes_freshly_reenacted=False,performance_evidence=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct",type=Path)
    args = parser.parse_args()
    manifest = load((HERE/"manifest.json").read_bytes())
    files,inherited = restore(manifest)
    result = replay(files,manifest)
    if args.reconstruct is not None:
        require(not args.reconstruct.exists(),"fresh reconstruction destination required")
        for name,body in files.items():
            require(not name.startswith("/") and ".." not in Path(name).parts,"safe restored alias")
            destination = args.reconstruct/name
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(body)
    print(json.dumps(dict(status="passed_portable_complex_parameter_tensor_oracle",
        manifest_sha256=sha((HERE/"manifest.json").read_bytes()),restored_files=len(files),
        inherited=inherited,complex_oracle_replay=result,new_native_compiler_integral_or_PID_work=False),indent=2))


if __name__=="__main__":
    main()
