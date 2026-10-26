#!/usr/bin/env python3
"""Replay frozen LegacyNoOp source and saved arrays without native execution."""
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
Q = "target/legacy-noop-qualification"
W = "validation/python-interface/facade-wheel-003"
N = "validation/quad-original-iregi-positive-rank-anchors"
SMALL = "validation/quad-original-iregi-small-n-rank7"
PREFIX = "/shared/external/iregi/iregi-rust/"
BUILD = "5dccfdf1207a30c78036f455e80e225d73e2bee19dea0e3241179becec87c545"
QUAL = "63c3ea5cd84e84f0796df6573b706939c2a4debd515d74edf85842718c1896bc"
REFERENCE = "target/quad-iregi-source-audit/future-positive-rank-requests/capture-001/request-3.stdout"
PARENT_PINS = {
 W + "/manifest.json": "cb7a2b09282c89b17802a485d0aca6a42b36b23b110d7fe8aead0b2ea0f74a18",
 N + "/manifest.json": "6fbc3465f3e2ee54a789b0ea556a51616744437e18d53bff29cec177755d9ddb",
 SMALL + "/manifest.json": "9b614c6567c28d23039053de390a7da5c665f4a57a978d54cd3148519fb3cb62",
}

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
    need(actual == set(manifest["capsule_files"]) | {"manifest.json"} and len(actual) == 7, "closed seven-file capsule")
    for name, expected in manifest["capsule_files"].items():
        body = (HERE/name).read_bytes()
        scan(name, body)
        need(desc(body) == expected, "capsule bytes " + name)
    parents = {}
    for name, expected in manifest["parent_files"].items():
        safe(name)
        body = (ROOT/name).read_bytes()
        need(desc(body) == expected, "declared parent bytes " + name)
        parents[name] = body
    need(set(parents) == set(PARENT_PINS) | {W+"/sources.tar.gz", N+"/payload.tar.gz", SMALL+"/payload.tar.gz"}, "six declared parent files")
    for name, expected in PARENT_PINS.items():
        need(sha(parents[name]) == expected, "fixed parent manifest")
    wm, nm, sm = [load(parents[p+"/manifest.json"]) for p in [W, N, SMALL]]
    need(sm["parent_files"][N+"/manifest.json"] == manifest["parent_files"][N+"/manifest.json"], "small-N reference ancestry")
    need(sm["parent_files"][N+"/payload.tar.gz"] == manifest["parent_files"][N+"/payload.tar.gz"], "small-N reference archive ancestry")
    need(desc(parents[W+"/sources.tar.gz"]) == {k: wm["sources"][k] for k in ["sha256", "bytes"]}, "source archive bytes")
    need(desc(parents[N+"/payload.tar.gz"]) == nm["capsule_files"]["payload.tar.gz"], "reference archive bytes")
    need(desc(parents[SMALL+"/payload.tar.gz"]) == sm["capsule_files"]["payload.tar.gz"], "reference admission archive bytes")
    archives = {W+"/sources.tar.gz": unpack(parents[W+"/sources.tar.gz"], wm["sources"]["members"]),
                N+"/payload.tar.gz": unpack(parents[N+"/payload.tar.gz"], nm["payload_members"]),
                SMALL+"/payload.tar.gz": unpack(parents[SMALL+"/payload.tar.gz"], sm["payload_members"])}
    need(len(archives[W+"/sources.tar.gz"]) == 147, "fixed 147-source parent")
    members = unpack((HERE/"payload.tar.gz").read_bytes(), manifest["payload_members"])
    origins = load((HERE/"payload-origins.json").read_bytes())
    need(set(origins) == set(manifest["preserved_files"]) | set(manifest["borrowed_files"]), "origin alias closure")
    files = {}
    for name, row in manifest["preserved_files"].items():
        safe(name)
        body = members[row["member"]]
        need(desc(body) == {k: row[k] for k in ["sha256", "bytes"]} == {k: origins[name][k] for k in ["sha256", "bytes"]}, "own alias bytes")
        files[name] = body
    for name, row in manifest["borrowed_files"].items():
        safe(name)
        body = archives[row["parent_archive"]][row["member"]]
        need(name not in files and desc(body) == {k: row[k] for k in ["sha256", "bytes"]}
             == {k: origins[name][k] for k in ["sha256", "bytes"]}, "borrowed alias bytes")
        files[name] = body
    need(sha(files[Q+"/qualification.json"]) == QUAL and files[Q+"/qualification.json"] == (HERE/"qualification.json").read_bytes(), "fixed qualification")
    return files, parents


def basis(rank):
    return [[t, x, y, r-t-x-y] for r in range(rank+1) for t in range(r, -1, -1)
            for x in range(r-t, -1, -1) for y in range(r-t-x, -1, -1)]


def display(squared):
    with localcontext() as context:
        context.prec = 100
        return str((Decimal(squared.numerator)/Decimal(squared.denominator)).sqrt())


def numerical_gates(files):
    raw = files[REFERENCE].decode()
    precision = [load(line[10:]) for line in raw.splitlines() if line.startswith("PRECISION ")]
    need(precision == [{"dbl_kind": 16, "olo_kind": 16, "storage_bits": 128, "binary_digits": 113, "decimal_digits": 33}], "reference precision canary")
    refs = [load(line[7:]) for line in raw.splitlines() if line.startswith("RESULT ")]
    need(len(refs) == 1, "one raw reference result")
    ref = refs[0]
    need(ref["id"] == "quad_n5_first_five_conditioned_rank7" and ref["stable"] is True and len(ref["moments"]) == 330, "original rank-seven reference")
    fixture = load(files[Q+"/fixture.json"])
    reference_prefix = "target/quad-iregi-source-audit/future-positive-rank-requests/"
    protocol = load(files[reference_prefix+"protocol.json"])
    case = protocol["runtime"]["cases"][3]
    need(case["id"] == ref["id"] and case["algorithm"] == "original_IREGI_IBP" and case["mode"] == 0
         and case["rank"] == 7 and case["propagators"] == 5 and case["moments"] == 330, "original reference request semantics")
    need(case["exact_propagators"] == fixture["propagators"] and F(case["exact_scale"]) == F(fixture["mu"]) == 3,
         "exact ordered masses, shifts, powers, and scale correspondence")
    request = files[case["request"]]
    need(sha(request) == case["request_sha256"] == "ec54244820bb854510c96049cf5f9933e254a31849beb1b8361f3d99d6967648", "reference request bytes")
    lines = request.decode().splitlines()
    need(lines[0].split() == ["EVAL", ref["id"], "tensor", "0", "5", "7", "0", "3", "0", "1e-6"]
         and lines[-1] == "QUIT", "unsnapped original IBP unit/h0 request")
    for line, prop in zip(lines[1:-1], fixture["propagators"]):
        need(list(map(F, line.split())) == list(map(F, prop["shift"]+prop["mass_squared"]+[str(prop["power"])])), "lossless reference propagator request")
    need(fixture["snap"] is True and fixture["threshold"] == "1/1000000" and fixture["rank"] == 6
         and fixture["dimension_shift"] == 0, "Legacy no-op versus unsnapped reference distinction")
    admission = load(files["target/quad-iregi-source-audit/rank7-n1-n5-corpus/capture-001/validation.json"])
    need(admission["archived_N5_base_controls"] == {"native_stable": True, "counts": {"IR_zero": 660, "UV_convergent_zero": 126},
         "failures": {"IR_zero": 0, "UV_convergent_zero": 0}, "passed": True}, "archived independent N5 base admission")
    outputs, maxima = [], {}
    for tag, bits in [("128-002", 128), ("256-001", 256)]:
        out, saved = [load(files[Q+"/"+tag+"/"+n+".json"]) for n in ["result", "comparison"]]
        settings = out["settings"]
        need(settings == {"algorithm": "PassarinoVeltman", "convention": "IregiNative", "dimension_shift": 0,
                          "input_policy": {"LegacyOnShell": {"threshold": "1/1000000"}}, "invariants": "FromShifts",
                          "powers": [1]*5, "propagators": 5, "rank": 6, "tensor_weights": "Components"}, "fixed requested mathematical interface")
        need(out["input_policy"] == settings["input_policy"] and out["algorithm_requested"] == out["algorithm_used"] == "PassarinoVeltman", "retained Legacy/PV request")
        need(out["precision_bits"] == bits and out["precision_control"]["accuracy_bits"] == 53
             and out["rescue_execution"] == {"enabled": False}, "working versus requested precision")
        need(out["poles"] == ref["poles"] == ["uv1", "ir1", "ir2", "finite"] and out["basis"] == basis(6), "complete native ordering")
        need(len(out["samples"]) == 1 and out["samples"][0]["status"] == "success"
             and out["samples"][0]["id"] == fixture["id"], "successful retained physical sample")
        engine = out["engine_execution"]
        need(engine["engine"] == "LegacyNoOp" and engine["input_rows"] == engine["accepted_rows"] == 1
             and engine["rejected_rows"] == 0 and engine["query_count"] == 51, "actual admitted 51-query path")
        need(engine["certificate_execution"]["evaluated_rows"] > 0 and engine["certificate_execution"]["passes"] > 0
             and engine["child_preparation_attempts"] == 1 and engine["child_preparation_error"] is None
             and engine["child"]["engine"] == "Generic" and engine["child"]["execution"]["reduction_rows"] > 0, "fresh certificate and actual lazy child execution")
        moments = out["samples"][0]["moments"]
        need(len(moments) == 210 and len(saved["records"]) == 840 and saved["failures"] == [], "complete 840 saved comparisons")
        maximum = F(0)
        for moment, (alpha, values, wanted) in enumerate(zip(basis(6), moments, ref["moments"][:210])):
            need(len(values) == len(wanted) == 4, "four independent slots, including UV")
            for slot, (actual, expected) in enumerate(zip(values, wanted)):
                need(len(actual) == len(expected) == 2 and all(isinstance(v, str) for v in actual+expected), "lossless complex strings")
                a, e = list(map(F, actual)), list(map(F, expected))
                error = sum((x-y)**2 for x, y in zip(a, e))/max(F(9)**(sum(alpha)+4-10), sum(x*x for x in e))
                need(saved["records"][4*moment+slot] == {"moment": moment, "monomial": alpha, "slot": slot,
                     "normalized_squared_error": str(error), "passed": error <= F(1, 10**20)}, "exact original-quad gate")
                need(error <= F(1, 10**20), "1e-10 mixed normalized tolerance")
                maximum = max(maximum, error)
        maxima[tag] = display(maximum)
        need(saved["maximum_normalized_error"] == maxima[tag] and saved["status"] == "passed_complete_Legacy_N5_R6_quad_array"
             and saved["complete_complex_slots"] == 840 and saved["working_component_bits"] == bits
             and saved["requested_bits"] == 53 and saved["native_UV_not_projected_at_rank6"] is True
             and saved["native_IR_slots_retained"] is True and saved["reference_rank7_prefix_first210"] is True, "saved comparison summary")
        for absolute, expected in saved["source_inputs"].items():
            need(sha(files[absolute.removeprefix(PREFIX)]) == expected, "comparison exact input binding")
        outputs.append(moments)
    pair = load(files[Q+"/working-precision-pair.json"])
    need(pair["slots"] == 840 and pair["working_bits"] == [128, 256] and pair["requested_bits"] == 53, "pair domain")
    maximum = F(0)
    for moment, (alpha, left, right) in enumerate(zip(basis(6), *outputs)):
        for slot, (a, b) in enumerate(zip(left, right)):
            a, b = list(map(F, a)), list(map(F, b))
            error = sum((x-y)**2 for x, y in zip(a, b))/max(F(9)**(sum(alpha)+4-10), sum(x*x for x in a), sum(x*x for x in b))
            need(pair["records"][4*moment+slot] == {"moment": moment, "monomial": alpha, "slot": slot,
                 "normalized_squared_error": str(error), "passed": error <= F(1, 2**160)}, "exact saved strict pair gate")
            need(error <= F(1, 2**160), "all 840 strict 80-bit pair decisions")
            maximum = max(maximum, error)
    need(pair["maximum_normalized_error"] == display(maximum) and pair["status"] == "passed_840_working_pair_80bit_agreement", "pair maximum")
    for absolute, expected in pair["inputs"].items():
        need(sha(files[absolute.removeprefix(PREFIX)]) == expected, "pair input identity")
    return {"quad_complex_slots_replayed": 1680, "strict_pair_slots_replayed": 840,
            "quad_maxima": maxima, "pair_maximum": display(maximum)}


def replay(files, manifest):
    def read(name):
        return load(files[Q+"/"+name])
    qualification, built, context = read("qualification.json"), read("build-002/receipt.json"), read("source-context.json")
    need(sha(files[Q+"/build-002/receipt.json"]) == BUILD and built["status"] == "passed"
         and built["cleanup_errors"] == [] and built["inputs_unchanged"] is True, "actual successful Cargo receipt")
    need(len(built["source_files"]) == len(manifest["compiled_sources"]) == qualification["build_source_count"] == 151, "151 compiled source files")
    need(context["source_files"] == built["source_files"] and context["build_receipt_sha256"] == BUILD, "actual snapshot context")
    need(context["actual_Cargo_event_sha256"] == sha(files[Q+"/build-002/cargo-cli-artifact.json"]), "source context actual CLI Cargo event")
    product = read("product.json")
    need(product["owned_path"] == built["products"]["cli"]["path"] and product["sha256"] == built["products"]["cli"]["sha256"]
         and product["source_context_sha256"] == sha(files[Q+"/source-context.json"])
         and product["actual_build_receipt"] == PREFIX+Q+"/build-002/receipt.json", "owned CLI metadata binds exact compiled source context")
    for name, expected in built["source_files"].items():
        body = files[Q+"/build-002/source-snapshot/"+name]
        need(sha(body) == expected and body == files[name]
             and desc(body) == {k: manifest["compiled_sources"][name][k] for k in ["sha256", "bytes"]}, "compiled snapshot reconstruction")
        need(built["inputs"][PREFIX+name] == built["inputs"][PREFIX+Q+"/build-002/source-snapshot/"+name] == expected, "historical dual source guards")
    all_events = []
    for index, step in enumerate(built["steps"]):
        need(step["returncode"] == 0 and step["owned_group_gone"] is True
             and F(step["elapsed_seconds"]) <= F(step["timeout_seconds"]), "bounded successful Cargo stage")
        log = files[Q+"/build-002/cargo-"+str(index)+".log"].decode()
        events = [load(line) for line in log.splitlines() if line.startswith("{")]
        all_events.extend(events)
        need(any(event.get("reason") == "build-finished" and event.get("success") is True for event in events), "actual Cargo completion event")
    for key, product in built["products"].items():
        event = load(files[Q+"/build-002/"+product["cargo_event"]])
        need(event["reason"] == "compiler-artifact" and event["executable"] == product["cargo_executable"], "actual selected executable artifact event")
        need(event in all_events, "selected event present in actual Cargo stream")
        need(manifest["omitted_compiled_products"][product["path"].removeprefix(PREFIX)] == product["sha256"], "omitted executable historical identity")
    for name, expected in built["outputs"].items():
        if name.startswith("frozen-"):
            need(manifest["omitted_compiled_products"][Q+"/build-002/"+name] == expected, "unread native output historical identity")
        else:
            need(sha(files[Q+"/build-002/"+name]) == expected, "build raw output identity")
    tests = read("tests-001/receipt.json")
    need(tests["status"] == "passed" and tests["unrun_tests"] == [] and len(tests["selected_tests"]) == 26
         and tests["cleanup_errors"] == [] and tests["inputs_unchanged"] is True and len(tests["steps"]) == 27, "26 focused normal tests completed")
    for index, step in enumerate(tests["steps"]):
        log = files[Q+"/tests-001/step-"+str(index)+".log"].decode()
        need(step["returncode"] == 0 and step["owned_group_gone"] is True, "saved normal-test completion")
        if index:
            name = tests["selected_tests"][index-1]
            need(re.search(r"test " + re.escape(name) + r" \.\.\..*?\bok\b", log, re.S)
                 and "1 passed; 0 failed" in log, "named PASS log")
    for name, expected in tests["outputs"].items():
        need(sha(files[Q+"/tests-001/"+name]) == expected, "focused-test raw output identity")
    for tag, bits in [("128-002", 128), ("256-001", 256)]:
        receipt = read(tag+"/receipt.json")
        need(receipt["status"] == "passed" and receipt["working_component_bits"] == bits and receipt["requested_bits"] == 53
             and receipt["guard_inputs_unchanged"] is True and receipt["owned_artifact_unchanged"] is True
             and receipt["artifact_sha256"] == built["products"]["cli"]["sha256"]
             and receipt["source_context_sha256"] == sha(files[Q+"/source-context.json"]), "source-bound successful public CLI")
        need(receipt["cleanup_errors"] == [] and len(receipt["steps"]) == 1 and receipt["steps"][0]["returncode"] == 0
             and receipt["steps"][0]["owned_group_gone"] is True and receipt["runtime_cpu"] == 16
             and receipt["address_space_limit_bytes"] == 32*1024**3, "bounded historical capture")
        for name, expected in receipt["guards"].items():
            need(sha(files[name]) == expected, "capture guard bytes")
        for name, expected in receipt["outputs"].items():
            need(sha(files[Q+"/"+tag+"/"+name]) == expected, "capture output bytes")
        need(files[Q+"/"+tag+"/step-0.log"] == files[Q+"/"+tag+"/result.json"], "untouched raw public output")
    # Preserve failed attempts as failures; do not manufacture missing arrays.
    old = load(files["target/legacy-n5-rank6-noop/128-001/receipt.json"])
    need(sha(files["target/legacy-n5-rank6-noop/128-001/receipt.json"]) == "a07f634df1686477d25984bd43ad47773577d9e2ee6cb25aab02310d4330c272"
         and old["status"] == "failed" and old["steps"][0]["returncode"] == -6, "old inline memory abort retained")
    need(b"memory allocation of 17439777696 bytes failed" in files["target/legacy-n5-rank6-noop/128-001/step-0.log"], "raw OOM log")
    release = load(files["target/legacy-n5-rank6-noop/release.json"])
    need(release["float128_status"] == "memory_abort_no_arrays" and release["float256_status"] == "not_run_conditional_prerequisite_failed", "old absent arrays and unrun companion")
    first = read("build-001/receipt.json")
    need(first["status"] == "failed" and F(first["elapsed_seconds"]) < 10 and b"Clone" in files[Q+"/build-001/cargo-0.log"], "initial compile failure")
    need(first["source_files"]["crates/iregi-rust/src/dispatch/legacy_noop.rs"] != built["source_files"]["crates/iregi-rust/src/dispatch/legacy_noop.rs"], "pre-Arc source retained distinctly")
    for name, expected in first["source_files"].items():
        need(sha(files[Q+"/build-001/source-snapshot/"+name]) == expected, "all failed-build source bodies")
    preflight = read("128-001/receipt.json")
    need(preflight["status"] == "failed" and preflight["steps"] == [] and preflight["outputs"] == {}
         and preflight["error"] == "RuntimeError('singlethread runtime')", "no native job during failed preflight")
    for absolute, expected in qualification["inputs"].items():
        need(sha(files[absolute.removeprefix(PREFIX)]) == expected, "final qualification exact input chain")
    need(qualification["focused_named_tests_passed"] == 26 and qualification["all_owned_groups_absent"] is True
         and qualification["working_pair_80bit_agreement"] is True, "historical final status")
    return {"compiled_source_hashes_checked": 151, "failed_build_source_hashes_checked": len(first["source_files"]),
            "normal_named_PASS_logs": 26, "failed_attempts_retained": 3, **numerical_gates(files),
            "fresh_native_hash_or_process_guard": False, "performance_or_achieved_precision_qualified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct", type=Path)
    args = parser.parse_args()
    manifest = load((HERE/"manifest.json").read_bytes())
    files, parents = restore(manifest)
    result = replay(files, manifest)
    if args.reconstruct:
        need(not args.reconstruct.exists(), "reconstruction target must be new")
        args.reconstruct.mkdir(parents=True)
        for name, body in files.items():
            path = args.reconstruct/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
    print(json.dumps({"status": "passed_portable_source_bound_LegacyNoOp_rank6_saved_replay",
                      "manifest_sha256": sha((HERE/"manifest.json").read_bytes()), "restored_aliases": len(files),
                      "parent_files": len(parents), "replay": result,
                      "producer_native_integral_compiler_PID_or_Git_work": False}, indent=2))


if __name__ == "__main__":
    main()


