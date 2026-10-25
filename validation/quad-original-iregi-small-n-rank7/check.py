#!/usr/bin/env python3
"""Portable source restoration and exact saved small-N reference replay.

Public helper API:
  restore(manifest) -> (files: dict[str, bytes], helpers, inherited_summary)
  restore_files(manifest) -> dict[str, bytes]
  replay(files, helpers, manifest) -> saved-evidence summary
No producer import, native binary, compiler, integral, or process probe runs.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
import argparse
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = "validation/quad-original-iregi-positive-rank-anchors"
PRIVATE = "target/quad-iregi-source-audit/rank7-n1-n5-corpus"
SMALL = "target/rank7-n1-n4-reference-proposal"
HISTORICAL = "/shared/external/iregi/iregi-rust/"
LIMIT = F(1, 10**20)


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {"sha256": sha(body), "bytes": len(body)}


def load(body):
    return json.loads(body, parse_float=str)


def display(squared):
    with localcontext() as context:
        context.prec = 100
        return str((Decimal(squared.numerator) / Decimal(squared.denominator)).sqrt())


def scale2(props):
    points = [[F(v) for v in p["shift"]] for p in props]
    result = max(F(1), *(abs(F(p["mass_squared"][0])) for p in props))
    for a in points:
        for b in points:
            delta = [x-y for x, y in zip(a, b)]
            result = max(result, abs(delta[0]**2 - sum(x*x for x in delta[1:])))
    return result


def restore(manifest):
    for name, expected in manifest["capsule_files"].items():
        require(desc((HERE/name).read_bytes()) == expected, "capsule file " + name)
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    require(actual == set(manifest["capsule_files"]) | {"manifest.json"}, "capsule exact file inventory")
    for name, expected in manifest["parent_files"].items():
        require(desc((ROOT/name).read_bytes()) == expected, "parent hash " + name)
    require(sha((ROOT/PARENT/"manifest.json").read_bytes()) == "6fbc3465f3e2ee54a789b0ea556a51616744437e18d53bff29cec177755d9ddb", "fixed positive-rank parent")
    path = ROOT/PARENT/"check.py"
    require(sha(path.read_bytes()) == "573cb307406b20c787fea76372cc9ddaffb682e3c1661d639b2c573e3ebe47f9", "independent stdlib parent source")
    spec = importlib.util.spec_from_file_location("quad_positive_rank_saved_parent", path)
    positive = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(positive)
    pm = load((ROOT/PARENT/"manifest.json").read_bytes())
    files, helpers, inherited = positive.restore(pm)
    previous = positive.replay(files, helpers, pm)
    members = helpers.read_archive((HERE/"payload.tar.gz").read_bytes(), manifest["payload_members"])
    origins = load((HERE/"payload-origins.json").read_bytes())
    require(set(origins) == set(manifest["preserved_files"]) | set(manifest["inherited_aliases"]), "closed origin inventory")
    for name, row in manifest["preserved_files"].items():
        helpers.safe(name)
        value = members[row["member"]]
        require(desc(value) == {k: row[k] for k in ["sha256", "bytes"]} == {k: origins[name][k] for k in ["sha256", "bytes"]}, "own file/alias identity")
        require(name not in files or files[name] == value, "parent collision")
        files[name] = value
    for name, row in manifest["inherited_aliases"].items():
        helpers.safe(name)
        value = files[row["inherited_source"]]
        require(desc(value) == {k: row[k] for k in ["sha256", "bytes"]} == {k: origins[name][k] for k in ["sha256", "bytes"]}, "inherited alias identity")
        files[name] = value
    frozen = load(files[SMALL+"/source-freeze.json"])
    for name, expected in frozen["owned_files"].items():
        require(sha(files[name]) == expected, "24-request original owned source inventory")
    require(frozen["request_count"] == 24 and len(frozen["closed_request_inventory"]) == 24, "closed original24 inventory")
    old = load(files[PRIVATE+"/earlier-draft-001/source-inventory.json"])
    for name, expected in old["files"].items():
        require(sha(files[PRIVATE+"/earlier-draft-001/"+name]) == expected, "unexecuted original draft preserved")
    require(old["native_execution"] is False, "initial draft never executed")
    review = load(files[PRIVATE+"/independent-source-review.json"])
    require(review["synthetic_parser_controls_sha256"] == sha(files["target/resume-20261025-review/rank7-corpus-source-review/parser-negative-controls.json"]), "source-review parser-control receipt")
    return files, helpers, {**inherited, "positive_rank_reference_slots_replayed": previous["complete_reference_complex_slots"],
                            "positive_rank_N7_pole_gates_replayed": previous["exact_N7_pole_records"]}


def restore_files(manifest):
    """Return original-path aliases as bytes, including all new IBP and N5base raw files."""
    return restore(manifest)[0]


def replay(files, helpers, manifest):
    def read(name):
        return load(files[PRIVATE+"/"+name])
    p, run, saved = read("protocol.json"), read("capture-001/run.json"), read("capture-001/validation.json")
    grant, review, audit = read("root-execution-grant.json"), read("independent-source-review.json"), read("independent-saved-review.json")
    require(grant["status"] == "granted" and grant["grantor"] == "/root" and grant["stages"] == ["runtime"]
            and grant["recipe_sha256"] == sha(files[PRIVATE+"/protocol.json"]) and grant["review_sha256"] == sha(files[PRIVATE+"/independent-source-review.json"]), "exact original grant")
    require(review["status"] == "passed_independent_source_runner_comparator_review" and review["findings"] == [], "original source review clear")
    require(audit["status"] == "passed_independent_rank7_reference_corpus_saved_review" and audit["findings"] == []
            and audit["checker_sha256"] == sha(files["target/resume-20261025-review/audit_quad_rank7_corpus_saved.py"]), "original independent saved review identity")
    require(run["status"] == "passed" and run["inputs_unchanged"] is True and run["changed_inputs"] == {} and run["cleanup_errors"] == [] and not run["cancellation"], "terminal guarded transport")
    require(run["bound_seconds"] == 300 and run["cleanup_reserve_seconds"] == 30 and F(run["elapsed_seconds"]) < 300
            and len(run["steps"]) == 26 and run["executed_native_integral_requests"] == 26, "fixed finite 26-process cohort")
    expected = dict(p["bindings"])
    for name in ["protocol.json", "root-execution-grant.json", "independent-source-review.json"]:
        expected[HISTORICAL+PRIVATE+"/"+name] = sha(files[PRIVATE+"/"+name])
    require(expected == run["inputs"] and len(expected) == 304 and len(p["bindings"]) == 301, "exact admission union")
    origins = load((HERE/"payload-origins.json").read_bytes())
    by_origin = {}
    for package in ["validation/quad-original-iregi-rank7-adjudication", PARENT]:
        for name, row in load((ROOT/package/"payload-origins.json").read_bytes()).items():
            by_origin.setdefault(row["origin"], set()).add(sha(files[name]))
    for name, row in origins.items():
        by_origin.setdefault(row["origin"], set()).add(sha(files[name]))
    for name, body in files.items():
        if name.startswith("validation/"):
            by_origin.setdefault(HISTORICAL+name, set()).add(sha(body))
    fresh = historical = 0
    for name, expected_hash in expected.items():
        if name in by_origin:
            require(expected_hash in by_origin[name], "available source/data guard " + name)
            fresh += 1
        else:
            historical += 1
    for name, expected_hash in run["outputs"].items():
        key = PRIVATE+"/capture-001/"+name
        if key in files:
            require(sha(files[key]) == expected_hash, "preserved raw transport bytes")
        else:
            require(manifest["omitted_compiled_products"][key]["captured_sha256"] == expected_hash, "omitted native provenance")
    require(run["runtime_binary_sha256"] == run["outputs"]["iregi-reference-quad"] == p["prior_binary_sha256"], "owned reused binary hash attestation")
    basis = [[a,b,c,r-a-b-c] for r in range(8) for a in range(r,-1,-1) for b in range(r-a,-1,-1) for c in range(r-a-b,-1,-1)]
    require(p["basis"] == basis and len(basis) == 330, "native canonical cumulative basis")
    fixture = load(files[p["conditioned_fixture"].removeprefix(HISTORICAL)])
    samples = {s["id"]: s for s in fixture["samples"]}
    state, arrays, records, groups = {}, {}, [], []

    def gate(identifier, kind, moment, slot, squared):
        records.append({"id": identifier, "kind": kind, "moment": moment, "slot": slot, "error": display(squared), "passed": squared <= LIMIT})
        return squared <= LIMIT

    def parse_raw(name, identifier, missing=False):
        text = files[name].decode()
        lines = text.splitlines()
        require([load(line[10:]) for line in lines if line.startswith("PRECISION ")] == [{"dbl_kind":16,"olo_kind":16,"storage_bits":128,"binary_digits":113,"decimal_digits":33}]
                and lines.count("READY IREGI_REFERENCE_QP_V1") == 1, "actual precision/ready witnesses")
        rows = [load(line[7:]) for line in lines if line.startswith("RESULT ")]
        if not rows and missing:
            require("ERROR:out of range of pave_UV" in text, "original N2PV missing-result error retained")
            return None, None
        require(len(rows) == 1 and rows[0]["id"] == identifier, "one matching raw RESULT")
        return rows[0], helpers.slots(rows[0],330,identifier)

    for ordinal, case in enumerate(p["runtime"]["cases"]):
        n, mode = case["propagators"], case["mode"]
        step = run["steps"][ordinal]
        request = case["input"].removeprefix(HISTORICAL)
        require(case["exact_propagators"] == samples[case["sample"]]["propagators"][:n] and case["exact_scale"] == samples[case["sample"]]["mu"], "exact conditioned sample selection")
        text = files[request].decode().splitlines()
        require(text[0].split() == ["EVAL",case["id"],"tensor",str(mode),str(n),"7","0",case["exact_scale"],"0","1e-6"]
                and len(text) == n+2 and text[-1] == "QUIT" and sha(files[request]) == case["request_sha256"], "exact ordinary request controls")
        for line, prop in zip(text[1:-1],case["exact_propagators"]):
            require(list(map(F,line.split())) == list(map(F,prop["shift"]+prop["mass_squared"]+["1"])), "exact ordered propagator row")
        expected_command = [p["tools"]["taskset"],"-c","26",p["tools"]["python"],HISTORICAL+"target/quad-iregi-source-audit/capture_worker.py",
                            "--binary",HISTORICAL+PRIVATE+"/capture-001/iregi-reference-quad","--input",case["input"],
                            "--stdout",HISTORICAL+PRIVATE+f"/capture-001/request-{ordinal}.stdout","--stderr",HISTORICAL+PRIVATE+f"/capture-001/request-{ordinal}.stderr"]
        require(step["command"] == expected_command and step["label"] == case["id"] and step["status"] == "exited"
                and step["returncode"] == 0 and step["owned_group_gone"] is True and step["timeout_seconds"] == (20 if n<=4 else 45), "saved exact command and owned transport")
        groups.append(step["owned_process_group"])
        worker = read(f"capture-001/step-{ordinal}.log")
        require(worker == {"binary_sha256":run["runtime_binary_sha256"],"input_sha256":sha(files[request]),"returncode":0,
                           "stdout_sha256":run["outputs"][f"request-{ordinal}.stdout"],"stderr_sha256":run["outputs"][f"request-{ordinal}.stderr"]}, "worker binary/input/output chain")
        response, values = parse_raw(PRIVATE+f"/capture-001/request-{ordinal}.stdout",case["id"],n==2 and mode==1)
        item = {"native_stable":None,"status":"invalid_response","identities":True,"eligible":False,"accepted_PV":False}
        state[(n,case["sample"],mode)] = (case,item)
        if values is None:
            require("IEEE_DENORMAL" in files[PRIVATE+f"/capture-001/request-{ordinal}.stderr"].decode(), "native N2PV stderr retained")
            continue
        item.update(native_stable=response["stable"],status="captured")
        require(saved["cases"][ordinal]["response"] == response, "complete raw/saved response equality")
        arrays[case["id"]] = values
        unit = scale2(case["exact_propagators"])
        for moment, powers in enumerate(basis):
            degree = sum(powers)
            for slot in range(4):
                kinds = []
                if slot in [1,2]: kinds.append("IR_zero")
                if slot == 0 and degree+4-2*n<0: kinds.append("UV_convergent_zero")
                if n == 1 and any(v%2 for v in powers): kinds.append("N1_odd_component_zero")
                for kind in kinds:
                    item["identities"] &= gate(case["id"],kind,moment,slot,sum(v*v for v in values[moment][slot])/unit**(degree+4-2*n))
    old = p["N5_base"]
    old_response, old_values = parse_raw(old["raw"].removeprefix(HISTORICAL),old["id"])
    old_controls = True
    for moment,powers in enumerate(basis):
        for slot in range(3):
            kind = "IR_zero" if slot in [1,2] else ("UV_convergent_zero" if sum(powers)+4-10<0 else None)
            if kind:
                old_controls &= gate(old["id"],"archived_N5_"+kind,moment,slot,sum(v*v for v in old_values[moment][slot])/scale2(samples["base"]["propagators"][:5])**(sum(powers)+4-10))
    scaling = []
    for n in range(1,6):
        case,item = state[n,"scaled_by_two",0]
        if n<5:
            base_case,base_item = state[n,"base",0]
            base,base_valid = arrays[base_case["id"]], base_item["native_stable"] and base_item["identities"]
        else:
            base,base_valid = old_values, old_response["stable"] and old_controls
        errors = []
        for moment,powers in enumerate(basis):
            degree = sum(powers)+4-2*n
            for slot in range(4):
                target = tuple(F(2)**degree*v for v in base[moment][slot])
                error = sum((x-y)**2 for x,y in zip(arrays[case["id"]][moment][slot],target))/max(scale2(case["exact_propagators"])**degree,sum(v*v for v in target))
                errors.append(error);gate(case["id"],"IBP_scale_identity",moment,slot,error)
        valid = bool(base_valid and item["native_stable"] and item["identities"] and max(errors)<=LIMIT)
        item["scaling"] = valid
        if n<5: base_item["scaling"] = valid
        scaling.append({"n":n,"compared_slots":1320,"failures":sum(e>LIMIT for e in errors),"maximum_error":display(max(errors))})
    for (n,sample,mode),(case,item) in state.items():
        if mode == 0:
            item["eligible"] = bool(item["native_stable"] and item["identities"] and (sample=="first_mass_squared_plus_one" or item.get("scaling")))
    pairs = []
    for n in range(1,5):
        for sample in ["base","scaled_by_two","first_mass_squared_plus_one"]:
            ibp,anchor = state[n,sample,0]
            pv,item = state[n,sample,1]
            if pv["id"] not in arrays:
                pairs.append({"n":n,"sample":sample,"complete":False,"failures":None});continue
            errors = []
            for moment,powers in enumerate(basis):
                for slot in range(4):
                    a,b = arrays[pv["id"]][moment][slot], arrays[ibp["id"]][moment][slot]
                    error = sum((x-y)**2 for x,y in zip(a,b))/max(scale2(pv["exact_propagators"])**(sum(powers)+4-2*n),sum(v*v for v in b))
                    errors.append(error);gate(pv["id"],"PV_vs_same_input_IBP",moment,slot,error)
            item["accepted_PV"] = bool(item["native_stable"] and item["identities"] and anchor["eligible"] and max(errors)<=LIMIT)
            pairs.append({"n":n,"sample":sample,"complete":True,"failures":sum(e>LIMIT for e in errors),"maximum_error":display(max(errors))})
    require(records == saved["records"] and len(records) == 42018, "all42018 exact saved records")
    require(scaling == audit["scaling"] and pairs == audit["PV_IBP_pairs"], "independent scale/PV audit summaries")
    for case,item in state.values():
        actual = next(row for row in saved["cases"] if row["id"] == case["id"])
        require(actual["status"] == item["status"] and actual["eligible_IBP_reference_anchor"] == item["eligible"]
                and actual["accepted_PV_reference"] == item["accepted_PV"], "complete qualification partition")
    require(len(arrays) == 23 and saved["total_complete_complex_slots"] == 30360 and saved["all_requested_arrays_complete"] is False
            and saved["failed_identity_or_pair_records"] == 486, "complete and missing slots/failures visible")
    require(sum(item["eligible"] for _,item in state.values()) == 14 and sum(item["accepted_PV"] for _,item in state.values()) == 3, "14newIBP and3N1PV only")
    release = read("capture-001/numerical-release.json")
    require([row["group"] for row in release["owned_groups"]] == groups and len(set(groups)) == 26 and all(row["absent"] is True for row in release["owned_groups"])
            and release["all_inputs_rehashed_unchanged"] == 304, "historical26group release; no fresh process probe")
    require(saved["compared_TIRust_slots"] == 0 and saved["zero_projection_performed"] is False
            and saved["finite_coefficients_independently_certified_by_identities"] is False, "limited reference-only scope")
    return {"requested_arrays":26,"requested_complex_slots":34320,"complete_arrays":23,"complete_complex_slots":30360,"missing_N2_PV_arrays":3,"missing_complex_slots":3960,
            "exact_saved_records_replayed":42018,"new_IBP_anchors":14,"archived_N5_base_anchors":1,"accepted_N1_PV_controls":3,"stable_but_rejected_N3_N4_PV_arrays":6,
            "PV_failing_finite_slots":486,"available_source_data_guards_checked":fresh,"omitted_native_external_guards_historical_only":historical,
            "fresh_native_hash_or_process_probe":False,"TIRust_or_currentCargo_qualification":False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct",type=Path)
    args = parser.parse_args()
    manifest = load((HERE/"manifest.json").read_bytes())
    files,parent,inherited = restore(manifest)
    result = replay(files,parent,manifest)
    qualification = load((HERE/"qualification.json").read_bytes())
    require((HERE/"qualification.json").read_bytes() == files[PRIVATE+"/qualification.json"], "exact final qualification copy")
    require(qualification["TIRust_compared_slots"] == 0 and qualification["currentCargo_qualified"] is False and qualification["full_rank7_domain_qualified"] is False
            and qualification["performance_qualified"] is False and qualification["finite_coefficients_independently_certified_by_identities"] is False, "no scope promotion")
    if args.reconstruct is not None:
        require(not args.reconstruct.exists(), "reconstruction destination exists")
        args.reconstruct.mkdir(parents=True)
        for name,value in files.items():
            parent.safe(name);path=args.reconstruct/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value)
    print(json.dumps({"status":"passed_portable_smallN_source_and_saved_reference_replay","manifest_sha256":sha((HERE/"manifest.json").read_bytes()),
                      "restored_files":len(files),"inherited":inherited,"smallN_reference_replay":result,"new_native_compiler_integral_or_PID_work":False},indent=2))


if __name__ == "__main__":
    main()
