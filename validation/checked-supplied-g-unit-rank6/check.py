#!/usr/bin/env python3
"""Portable checked-G saved source/data replay; no producer or native imports."""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Q = "target/checked-g-packed-qualification"
S = "target/checked-g-packed-source"
W = "validation/python-interface/facade-wheel-003"
N = "validation/quad-original-iregi-generalized-n6-rank6"
PREFIX = "/shared/external/iregi/iregi-rust/"
BUILD = "96e91d3f2a502e23c180150b7860375e524bdb4174191784a270fca9d40fe3c9"
QUAL = "90eccf70eecbe9751b0cf5eebc198556ff2cb9032799de01d890b3823de05273"
DECIMAL = re.compile(r"\s*[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\s*")
RATIONAL = re.compile(r"\s*[+-]?\d+/[1-9]\d*\s*")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {"sha256": sha(body), "bytes": len(body)}


def safe(name):
    p = Path(name)
    need(name and not p.is_absolute() and ".." not in p.parts and str(p) == name, "unsafe alias")


def scan(name, body):
    safe(name)
    need(Path(name).suffix not in {".o", ".mod", ".smod", ".pyc", ".so", ".a", ".dll", ".dylib"}
         and "__pycache__" not in Path(name).parts, "compiled/cache payload")
    need(not body.startswith((b"\x7fELF", b"!<arch>", b"MZ")), "native payload")
    need(not re.search(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}", body), "license literal")


def load(body):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError("nonfinite JSON constant: " + value)

    return json.loads(body, object_pairs_hook=pairs, parse_constant=nonfinite, parse_float=str)


def unpack(body, expected):
    result = {}
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as tar:
        for item in tar:
            need(item.isfile() and item.name not in result, "unique regular member")
            value = tar.extractfile(item).read()
            scan(item.name, value)
            need(desc(value) == expected.get(item.name), "exact member descriptor")
            result[item.name] = value
    need(set(result) == set(expected), "closed archive inventory")
    return result


def restore(manifest):
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    need(actual == set(manifest["capsule_files"]) | {"manifest.json"}, "seven-file capsule closure")
    need(len(actual) == 7, "seven files")
    for name, expected in manifest["capsule_files"].items():
        scan(name, (HERE/name).read_bytes())
        need(desc((HERE/name).read_bytes()) == expected, "capsule byte identity")
    parents = {}
    for name, expected in manifest["parent_files"].items():
        safe(name)
        body = (ROOT/name).read_bytes()
        need(desc(body) == expected, "declared immutable parent file")
        parents[name] = body
    need(len(parents) == 6 and sha(parents[W+"/manifest.json"]) == "cb7a2b09282c89b17802a485d0aca6a42b36b23b110d7fe8aead0b2ea0f74a18"
         and sha(parents[N+"/manifest.json"]) == "90e4ede40dbf46e537064dea0e85309b0079bfd12d245f7dc9ba658aa16d2f0e", "pinned source and quad parents")
    wm, nm = load(parents[W+"/manifest.json"]), load(parents[N+"/manifest.json"])
    archives = {}
    for name, expected in [(W+"/sources.tar.gz", wm["sources"]), (W+"/evidence.tar.gz", wm["evidence"])]:
        need(desc(parents[name]) == {k: expected[k] for k in ["sha256", "bytes"]}, "parent archive descriptor")
        archives[name] = unpack(parents[name], expected["members"])
    need(desc(parents[N+"/payload.tar.gz"]) == nm["capsule_files"]["payload.tar.gz"], "quad archive descriptor")
    archives[N+"/payload.tar.gz"] = unpack(parents[N+"/payload.tar.gz"], nm["payload_members"])
    context = archives[W+"/evidence.tar.gz"]["context.json"]
    need(sha(context) == manifest["source_parent_context_sha256"] == wm["source_context_sha256"]
         == "e873a0bec5cdb087caa812c6f2b1c668323f3670daed8438d3f538686da0c29c", "actual parent source context")
    need(len(archives[W+"/sources.tar.gz"]) == wm["source_files"] == 147, "147 parent selected sources")
    for absolute, expected in load(context)["inputs"].items():
        name = absolute.removeprefix(PREFIX)
        need(name in archives[W+"/sources.tar.gz"] and sha(archives[W+"/sources.tar.gz"][name]) == expected,
             "exact body for every selected parent context source")
    members = unpack((HERE/"payload.tar.gz").read_bytes(), manifest["payload_members"])
    origins = load((HERE/"payload-origins.json").read_bytes())
    need(set(origins) == set(manifest["preserved_files"]) | set(manifest["borrowed_files"]), "exact origin closure")
    files = {}
    for name, row in manifest["preserved_files"].items():
        safe(name)
        body = members[row["member"]]
        need(desc(body) == {k: row[k] for k in ["sha256", "bytes"]}
             == {k: origins[name][k] for k in ["sha256", "bytes"]}, "own saved alias bytes")
        files[name] = body
    for name, row in manifest["borrowed_files"].items():
        safe(name)
        body = archives[row["parent_archive"]][row["member"]]
        need(name not in files and desc(body) == {k: row[k] for k in ["sha256", "bytes"]}
             == {k: origins[name][k] for k in ["sha256", "bytes"]}, "exact borrowed bytes")
        files[name] = body
    need(sha(files[Q+"/qualification.json"]) == QUAL
         and files[Q+"/qualification.json"] == (HERE/"qualification.json").read_bytes(), "exact final qualification")
    return files, parents


def basis(rank):
    return [[t, x, y, r-t-x-y] for r in range(rank+1) for t in range(r, -1, -1)
            for x in range(r-t, -1, -1) for y in range(r-t-x, -1, -1)]


def norm(value):
    return sum(v*v for v in value)


def complex_value(value, native=False):
    if native:
        need(isinstance(value, list) and len(value) == 2, "native complex pair")
        parts = value
    else:
        need(isinstance(value, dict) and set(value) == {"real", "imaginary", "real_precision", "imaginary_precision"}, "Rust complex object with precision metadata")
        parts = [value["real"], value["imaginary"]]
    need(all(isinstance(v, str) and (DECIMAL.fullmatch(v) or (not native and RATIONAL.fullmatch(v))) for v in parts),
         "quoted finite exact components")
    return tuple(F(v) for v in parts)


def display(squared):
    with localcontext() as context:
        context.prec = 100
        return str((Decimal(squared.numerator)/Decimal(squared.denominator)).sqrt())


def replay(files, manifest):
    def read(name):
        return load(files[Q+"/"+name])

    qualification, binding, built = read("qualification.json"), read("binding-v2.json"), read("build-001/receipt.json")
    need(sha(files[Q+"/build-001/receipt.json"]) == BUILD == qualification["build_receipt_sha256"]
         == binding["build_receipt_sha256"], "actual compiled build chain")
    need(built["status"] == "passed" and built["inputs_unchanged"] is True and built["cleanup_errors"] == []
         and built["total_seconds"] == 600 and built["cleanup_reserve_seconds"] == 45
         and F(built["elapsed_seconds"]) <= 600 and len(built["steps"]) == 2, "bounded actual Cargo build attestation")
    need(len(built["source_files"]) == len(manifest["compiled_sources"]) == 145, "all145 compiled source records")
    for name, expected in built["source_files"].items():
        body = files[Q+"/build-001/source-snapshot/"+name]
        need(body == files[name] and sha(body) == expected
             and desc(body) == {k: manifest["compiled_sources"][name][k] for k in ["sha256", "bytes"]},
             "exact compiled source snapshot + source reconstruction")
        need(built["inputs"][PREFIX+name] == expected
             and built["inputs"][PREFIX+Q+"/build-001/source-snapshot/"+name] == expected, "actual compiled double source guards")
    need(sum(row["origin"] == "source_parent" for row in manifest["compiled_sources"].values()) == 110
         and manifest["own_source_delta"] == 35, "110 inherited and35 own compiled sources")
    need(binding["g_sources"] == qualification["owned_source_hashes"] and len(binding["g_sources"]) == 8,
         "eight corrected compiled suppliedG overlays")
    for name, expected in binding["g_sources"].items():
        need(built["source_files"][name] == expected, "corrected G source is actually compiled")
    for key, name in [("g_source_proposal_sha256", S+"/source-proposal.json"),
                      ("g_patch_sha256", S+"/checked-g-packed.patch"),
                      ("g_composition_sha256", S+"/composition.json")]:
        need(binding[key] == sha(files[name]), "exact corrected source packet application context")
    for name, expected in built["outputs"].items():
        alias = Q+"/build-001/"+name
        if alias in files:
            need(sha(files[alias]) == expected, "preserved build event/log")
        else:
            need(manifest["omitted_compiled_products"].get(alias) == expected, "omitted owned compiled product")
    for kind, product in built["products"].items():
        event = read("build-001/"+product["cargo_event"])
        need(event["reason"] == "compiler-artifact" and event["executable"] == product["cargo_executable"], "actual Cargo executable event")
        need((kind == "tests" and event["target"]["name"] == "iregi_rust" and event["profile"]["test"] is True)
             or (kind == "checked_tensor_public" and event["target"]["name"] == kind
                 and event["target"]["kind"] == ["example"] and event["profile"]["test"] is False), "selected actual target")
    for absolute, expected in built["inputs"].items():
        name = absolute.removeprefix(PREFIX)
        if name in files:
            need(sha(files[name]) == expected, "available compiled input guard")
        else:
            need(manifest["omitted_compiled_products"].get(name) == expected, "historical omitted native build input")

    selected = read("selection-v2.json")
    groups, tests = [], 0
    for stage in ["cheap-002", "array-001", "128-001", "256-001"]:
        receipt = read(stage+"/receipt.json")
        need(receipt["status"] == "passed" and receipt["cleanup_errors"] == []
             and receipt["guard_inputs_unchanged"] is True and receipt["owned_artifact_unchanged"] is True
             and receipt["automatic_retry"] is False and receipt["performance_qualified"] is False
             and receipt["build_receipt_sha256"] == BUILD and receipt["runtime_cpu"] == 16
             and receipt["address_space_limit_bytes"] == 34359738368
             and F(receipt["elapsed_seconds"]) <= receipt["total_seconds"], "saved bounded successful stage")
        need(qualification["receipts"][stage]["receipt_sha256"] == sha(files[Q+"/"+stage+"/receipt.json"]), "qualification exact stage receipt")
        kind = "tests" if stage in ["cheap-002", "array-001"] else "checked_tensor_public"
        need(receipt["artifact_sha256"] == built["products"][kind]["sha256"], "runtime actual owned artifact")
        for name, expected in receipt["guards"].items():
            need(name in files and sha(files[name]) == expected, "every runtime source/data guard available")
        for name, expected in receipt["outputs"].items():
            need(sha(files[Q+"/"+stage+"/"+name]) == expected, "raw stage output byte identity")
        names = selected["normal_cases"] if stage == "cheap-002" else [selected["genuine_case"]] if stage == "array-001" else None
        need(len(receipt["steps"]) == (len(names) if names else 1), "closed stage child count")
        if names:
            need(receipt["test_cases"] == names and len(names) == (20 if stage == "cheap-002" else 1), "exact selected named test list")
        for index, step in enumerate(receipt["steps"]):
            need(step["status"] == "exited" and step["returncode"] == 0 and step["owned_group_gone"] is True,
                 "historical successful owned process group")
            groups.append(step["owned_process_group"])
            need(step["command"] == receipt["commands"][index] and step["timeout_seconds"] <= receipt["child_cap_seconds"], "exact saved runtime command")
            if names:
                text = files[Q+"/"+stage+f"/step-{index}.log"].decode()
                summaries = [line for line in text.splitlines() if line.startswith("test result:")]
                need(len(summaries) == 1 and re.fullmatch(r"test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; \d+ filtered out; finished in [^\n]+", summaries[0])
                     and "running 1 test" in text and "test "+names[index]+" ..." in text,
                     "actual named onePASS raw log, no skip")
                need(names[index] in step["command"] and "--exact" in step["command"], "actual exact named command")
                tests += 1
    need(len(groups) == len(set(groups)) == 23
         and qualification["all_owned_groups_freshly_absent"] == [{"owned_process_group": g, "actually_absent_now": True} for g in groups],
         "23historical runtime group release attestations")
    # The R1 log proves the named compiled assertions ran, not fresh numeric execution.
    tensor_source = files["crates/iregi-rust/src/certified_tensor.rs"].decode()
    for needle in ["packed[0].child_batch_calls,1", "packed[0].packed_child_rows,12",
                   "packed[0].parent_batch_calls,1", "packed[0].packed_parent_rows,2",
                   "result.lane(1).is_err()", "contracted.lane(1).is_err()", "recovered.lane(0).unwrap()"]:
        need(needle in tensor_source, "compiled actual R1 assertion retained: " + needle)

    case_alias = "target/n6-rank6-generalized-current-cli/inputs/n6_rank6_unit_control.json"
    case = load(files[case_alias])
    ref_alias = "target/n6-rank6-generalized-quad/capture-001/request-0.stdout"
    need(sha(files[ref_alias]) == "006fd1d90dfc76d0b34f2cd4a1be36b1272c6700da18c25e18808fc269d207ab", "exact independent quad unit anchor")
    lines = files[ref_alias].decode().splitlines()
    need([load(line[10:]) for line in lines if line.startswith("PRECISION ")]
         == [{"dbl_kind": 16, "olo_kind": 16, "storage_bits": 128, "binary_digits": 113, "decimal_digits": 33}], "actual quad canary")
    references = [load(line[7:]) for line in lines if line.startswith("RESULT ")]
    need(len(references) == 1, "one native result")
    reference = references[0]
    need(reference["id"] == case["id"] == "n6_rank6_unit_control" and reference["stable"] is True
         and reference["poles"] == ["uv1", "ir1", "ir2", "finite"] and len(reference["moments"]) == 210,
         "complete stable native ordering")
    admission_alias = "target/n6-rank6-generalized-quad/anchor-admission.json"
    need(sha(files[admission_alias]) == "ad13acbb025596760232afb309ec993ab0c71f8538a49cf414c83bf4478bccfe", "pinned independent reference admission")
    need(case["dimension_shift"] == 0 and [p["power"] for p in case["propagators"]] == [1]*6
         and F(case["mu"]) == 3, "exact ordinary unit/h0 case")
    scale = max(F(case["mu"])**2, F(1), *(abs(F(p["mass_squared"][0])) for p in case["propagators"]))
    for a in case["propagators"]:
        for b in case["propagators"]:
            delta = [F(x)-F(y) for x, y in zip(a["shift"], b["shift"])]
            scale = max(scale, abs(delta[0]**2-sum(v*v for v in delta[1:])))
    need(scale == 9, "same dimensionful normalization Q2=9")
    outputs, maxima = [], {}
    for bits in [128, 256]:
        output, saved = read(f"{bits}-001/result.json"), read(f"{bits}-001/comparison.json")
        outputs.append(output)
        need(output["status"] == "all_lanes_success" and output["input_preserved"] is True
             and output["rows"] == output["components"] == 1 and output["requested_bits"] == 53
             and output["working_bits"] == bits and output["basis"] == basis(6)
             and output["case_id"] == case["id"] and output["lane_statuses"] == ["Success"]
             and len(output["lanes"]) == 1 and output["lanes"][0]["status"] == "Success",
             "actual successful singleton native component layout")
        need(output["settings"] == {"algorithm": "PassarinoVeltman", "convention": "IregiNative", "dimension_shift": 0,
                                    "input_policy": "Preserve", "invariants": "SuppliedScalarProducts", "powers": [1]*6,
                                    "propagators": 6, "rank": 6, "tensor_weights": "Components"}, "strict PV/unit/h0 native settings")
        cert = output["certificates"]
        need(cert["cartesian"]["evaluated_rows"] >= 1 and cert["gram"]["evaluated_rows"] >= 1
             and cert["gram"]["reduction_batches"] == 1, "both actual certificates and batch dispatch")
        actual = output["lanes"][0]["moments"]
        need(len(actual) == 210, "all210 actual native moments")
        records, maximum, witness = [], F(0), None
        for moment, alpha in enumerate(basis(6)):
            need(len(actual[moment]) == len(reference["moments"][moment]) == 4, "four coefficients before contraction")
            unit = scale**(sum(alpha)+4-12)
            for slot in range(4):
                need(all(type(actual[moment][slot][key]) is int and 1 <= actual[moment][slot][key] <= bits
                         for key in ["real_precision", "imaginary_precision"]),
                     "actual per-component transport precision metadata retained")
                a = complex_value(actual[moment][slot])
                e = complex_value(reference["moments"][moment][slot], native=True)
                error = norm(tuple(x-y for x, y in zip(a, e)))/max(unit, norm(e))
                records.append({"moment": moment, "monomial": alpha, "slot": slot,
                                "normalized_squared_error": str(error), "passed": error <= F(1, 10**20)})
                if error > maximum:
                    maximum, witness = error, [moment, slot]
        need(saved["records"] == records and len(records) == 840 and all(r["passed"] for r in records)
             and saved["failures"] == [] and saved["maximum_normalized_error"] == display(maximum)
             and saved["maximum_witness"] == witness and saved["status"] == "passed_complete_checkedG_quad_array",
             "all840 independent exact quad records +maximum")
        for absolute, expected in saved["source_inputs"].items():
            need(sha(files[absolute.removeprefix(PREFIX)]) == expected, "comparison raw input pin")
        summary = qualification["reference_comparisons"][str(bits)]
        need(summary["comparison_sha256"] == sha(files[Q+f"/{bits}-001/comparison.json"])
             and summary["result_sha256"] == sha(files[Q+f"/{bits}-001/result.json"])
             and summary["maximum_quad_normalized_difference"] == display(maximum), "qualification quad chain")
        maxima[str(bits)] = display(maximum)
    low, high = outputs
    need(low["input_exact_rational"] == high["input_exact_rational"] and low["settings"] == high["settings"], "identical exact inputs/settings across working precisions")
    pair, strict = read("working-precision-pair-comparison.json"), read("working-precision-pair-80bit-gate.json")
    records, maximum, witness, strict_failures = [], F(0), None, []
    for moment, alpha in enumerate(basis(6)):
        unit = F(9)**(sum(alpha)+4-12)
        for slot in range(4):
            a, b = [complex_value(out["lanes"][0]["moments"][moment][slot]) for out in outputs]
            error = norm(tuple(x-y for x, y in zip(a, b)))/max(unit, norm(a), norm(b))
            row = {"moment": moment, "monomial": alpha, "slot": slot,
                   "normalized_squared_difference": str(error), "passed": error <= F(1, 10**20)}
            records.append(row)
            if error > F(1, 2**160):
                strict_failures.append(row)
            if error > maximum:
                maximum, witness = error, [moment, slot]
    need(pair["records"] == records and len(records) == 840 and all(r["passed"] for r in records)
         and pair["maximum_normalized_difference"] == display(maximum) and pair["maximum_witness"] == witness
         and pair["status"] == "passed_complete_saved_working_precision_agreement", "all840 exact saved pair records")
    need(strict["status"] == "passed_saved_normalized_pair_agreement_2pow_minus80"
         and strict["squared_difference_limit"] == str(F(1, 2**160)) and strict["failures"] == strict_failures == []
         and strict["complete_complex_slots"] == 840 and strict["maximum_normalized_difference"] == display(maximum)
         and strict["pair_comparison_sha256"] == sha(files[Q+"/working-precision-pair-comparison.json"]), "all840 strict2^-80 agreement decisions")
    need(qualification["pair_comparison_sha256"] == sha(files[Q+"/working-precision-pair-comparison.json"])
         and qualification["pair_80bit_gate_sha256"] == sha(files[Q+"/working-precision-pair-80bit-gate.json"])
         and qualification["binding_sha256"] == sha(files[Q+"/binding-v2.json"]), "final proof chain")
    # Failure/source history is checked as saved evidence, with no PID operations.
    old = "target/certified-tensor-qualification/"
    failed, partial, release, watch = [load(files[old+n]) for n in
                                     ["rank6-unit-001/receipt.json", "rank6-unit-001/result.json",
                                      "rank6-unit-terminal-release.json", "rank6-unit-memory-watch.json"]]
    need(sha(files[old+"rank6-unit-001/receipt.json"]) == "c46c5d3a5531bf011eb245f188ce432e104b1b34a39860b24ce45ae5f352ad4f"
         and failed["status"] == "failed" and failed["cleanup_errors"] != []
         and failed["steps"][0]["timeout"] is True and failed["steps"][0]["owned_group_gone"] is False
         and partial["status"] == "reducing" and "lanes" not in partial, "old inline timeout cannot supply arrays")
    need(release["failed_receipt_sha256"] == sha(files[old+"rank6-unit-001/receipt.json"])
         and release["original_cleanup_errors_preserved"] == failed["cleanup_errors"]
         and release["owned_group_absent_now"] is True and release["complete_array_obtained"] is False
         and release["watcher_sha256"] == sha(files[old+"rank6-unit-memory-watch.json"])
         and release["last_sample_only_not_peak"] == watch["samples"][-1]
         and watch["samples"][-1]["rss_kib"] == 152769352, "additive later release and sampled-not-peak RSS")
    cheap, cheap_release = read("cheap-001/receipt.json"), read("cheap-001-terminal-release.json")
    need(sha(files[Q+"/cheap-001/receipt.json"]) == "cfd337a7f2814161b8e2381756ce8e71b94615b620d8eb2cd5a4121822f04bae"
         and cheap["status"] == "failed" and len(cheap["steps"]) == 6 and cheap["steps"][-1]["timeout"] is True
         and cheap["steps"][-1]["timeout_seconds"] == 60 and cheap_release["original_failure_not_rewritten"] is True
         and cheap_release["failed_receipt_sha256"] == sha(files[Q+"/cheap-001/receipt.json"])
         and cheap_release["all_owned_groups_absent"] is True, "constructor failure and later release retained")
    application = read("variant-reuse-fix/application.json")
    need(sha(files[Q+"/variant-reuse-fix/application.json"]) == binding["variant_reuse_application_sha256"]
         and sha(files[Q+"/variant-reuse-fix/variant-reuse.patch"]) == application["patch_sha256"]
         and sha(files[Q+"/variant-reuse-fix/plan.base.rs"]) == application["before_sha256"]
         and sha(files[Q+"/variant-reuse-fix/plan.candidate.rs"]) == application["after_sha256"]
         == built["source_files"]["crates/iregi-rust/src/plan.rs"], "actual applied variant fix context")
    draft = S+"/earlier-drafts/normalization-v1/"
    retraction = load(files[draft+"independent-peer-review-retraction.json"])
    need(sha(files[draft+"checked-g-packed.patch"]) == retraction["patch_sha256"]
         == "39aed6001a5bc821a9885d8ea21a96579bc36eebd4177d4e8b5934f10f95cf1f"
         and sha(files[draft+"source-proposal.json"]) == retraction["proposal_sha256"]
         and sha(files[draft+"independent-peer-review.json"]) == retraction["supersedes_review_sha256"]
         and retraction["status"] == "prior_no_blocker_review_retracted_confirmed_source_blocker", "unexecuted bad-normalization packet and retracted review")
    need(manifest["generalized_suppliedG_or_numerical_Dual_qualified"] is False
         and manifest["achieved_precision_qualified"] is False and manifest["performance_qualified"] is False
         and qualification["native_jobs_active"] is False, "no scope promotion")
    return {"compiled_source_hashes_checked": 145, "parent_sources_reused": 110, "own_source_delta": 35,
            "normal_tests": 20, "actual_R1_mixed_validity_test": 1, "named_PASS_logs": tests,
            "quad_complex_slots_replayed": 1680, "pair_complex_slots_replayed": 840, "strict_pair_decisions": 840,
            "quad_maxima": maxima, "pair_maximum": display(maximum), "strict_pair_failure_count": 0,
            "preserved_inline_and_constructor_failures": 2, "fresh_native_hash_or_process_probe": False,
            "achieved_precision_or_performance_qualified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct", type=Path)
    args = parser.parse_args()
    manifest = load((HERE/"manifest.json").read_bytes())
    files, parents = restore(manifest)
    result = replay(files, manifest)
    if args.reconstruct:
        need(not args.reconstruct.exists(), "reconstruction target already exists")
        args.reconstruct.mkdir(parents=True)
        for name, body in files.items():
            safe(name)
            path = args.reconstruct/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
    print(json.dumps({"status": "passed_portable_source_bound_checked_G_unit_rank6_saved_replay",
                      "manifest_sha256": sha((HERE/"manifest.json").read_bytes()), "restored_aliases": len(files),
                      "parent_files": len(parents), "checked_G_replay": result,
                      "producer_native_integral_compiler_PID_or_Git_work": False}, indent=2))


if __name__ == "__main__":
    main()
