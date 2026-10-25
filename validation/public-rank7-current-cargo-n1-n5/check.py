#!/usr/bin/env python3
"""Portable source integrity and complete saved-value replay; standard library.

Never invokes a compiler, evaluator, reference, producer comparator or native
binary, and never probes a process. Actual historical native identities and
process absence are supported by the retained independently reviewed receipts.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import tarfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = "target/public-rank7-n1-n5-current-cargo"
OWNER = "target/routing-rational-cayley-adoption/current-cargo-qualification"
HISTORICAL_ROOT = "/shared/external/iregi/iregi-rust/"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def describe(body):
    return {"sha256":sha(body),"bytes":len(body)}


def load(body):
    return json.loads(body)


def safe(name):
    p = Path(name)
    require(name and not p.is_absolute() and ".." not in p.parts and str(p) == name,
            "unsafe capsule name")


def unpack(body, expected):
    files = {}
    with tarfile.open(fileobj=io.BytesIO(body),mode="r:gz") as archive:
        for entry in archive:
            safe(entry.name)
            require(entry.isfile() and entry.name not in files, "archive type or duplicate")
            value = archive.extractfile(entry).read()
            require(not value.startswith((b"\x7fELF", b"!<arch>"))
                    and Path(entry.name).suffix not in (".o",".mod",".smod",".pyc",".rlib",".so"),
                    "compiled/cache payload")
            require(not re.search(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}",value),
                    "literal Symbolica license in payload")
            files[entry.name] = value
    require({n:describe(v) for n,v in files.items()} == expected, "exact archive inventory")
    return files


def restore_files(manifest):
    require({str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
            == set(manifest["capsule_files"])|{"manifest.json"}, "capsule closed membership")
    for name,expected in manifest["capsule_files"].items():
        safe(name)
        require(describe((HERE/name).read_bytes()) == expected, "capsule file "+name)
    parent = manifest["reference_parent"]
    parent_dir = ROOT/parent["path"]
    require(describe((parent_dir/"manifest.json").read_bytes()) == parent["manifest"], "reference parent manifest")
    require(describe((parent_dir/"check.py").read_bytes()) == parent["checker"], "reference parent checker")
    spec = importlib.util.spec_from_file_location("saved_quad_rank7_parent",parent_dir/"check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    files = module.restore_files(load((parent_dir/"manifest.json").read_bytes()))
    for name,expected in manifest["direct_parent_files"].items():
        safe(name)
        value = (ROOT/name).read_bytes()
        require(describe(value) == expected,"direct parent "+name)
        require(name not in files or files[name] == value,"direct parent collision")
        files[name] = value
    payload = unpack((HERE/"evidence.tar.gz").read_bytes(),manifest["evidence_members"])
    for name,record in manifest["preserved_files"].items():
        value = payload[record["member"]]
        require(describe(value) == {key:record[key] for key in ("sha256","bytes")},"preserved alias identity")
        require(name not in files or files[name] == value,"evidence alias collision")
        files[name] = value
    inventory = load((HERE/"source-inventory.json").read_bytes())
    require(sha((HERE/"sources.tar.gz").read_bytes()) == inventory["archive_sha256"],"source archive digest")
    sources = unpack((HERE/"sources.tar.gz").read_bytes(),inventory["members"])
    require(len(sources) == inventory["source_count"] == 64,"exact current source count")
    context = load(files[OWNER+"/source-context.json"])
    require(sha(files[OWNER+"/source-context.json"]) == inventory["source_context_sha256"]
            and {n:sha(v) for n,v in sources.items()} == context["source_files"],"64-source context identity")
    for name,value in sources.items():
        for alias in (name, OWNER+"/source-snapshot/"+name):
            require(alias not in files or files[alias] == value,"current source alias collision")
            files[alias] = value
    protocol = load(files[PRIVATE+"/protocol.json"])
    for absolute,expected in protocol["bindings"].items():
        if absolute.startswith(HISTORICAL_ROOT):
            relative = absolute[len(HISTORICAL_ROOT):]
            if relative in manifest["omitted_native_products"]:
                require(manifest["omitted_native_products"][relative]["sha256"] == expected,
                        "historical omitted native identity")
            else:
                require(relative in files and sha(files[relative]) == expected,"portable project binding "+relative)
        else:
            require(absolute in manifest["omitted_immutable_tool_bindings"]
                    and manifest["omitted_immutable_tool_bindings"][absolute] == expected,
                    "declared immutable external tool identity")
    return files


def compare(a,b,unit2,threshold2):
    squared = sum((x-y)**2 for x,y in zip(a,b))/max(unit2,sum(x*x for x in b))
    require(squared <= threshold2,"saved complex numerical gate")
    return squared


def scale2(sample,n):
    props = sample["propagators"][:n]
    value = max(Fraction(1),*(abs(Fraction(p["mass_squared"][0])) for p in props))
    for i,p in enumerate(props):
        for q in props[:i]:
            delta = [Fraction(a)-Fraction(b) for a,b in zip(p["shift"],q["shift"])]
            value = max(value,abs(delta[0]**2-sum(x*x for x in delta[1:])))
    return value


def replay(files):
    protocol = load(files[PRIVATE+"/protocol.json"])
    fixture = load(files["validation/public-highpoint/fixture-conditioned_masses.json"])
    basis = [[t,x,y,r-t-x-y] for r in range(8) for t in range(r,-1,-1)
             for x in range(r-t,-1,-1) for y in range(r-t-x,-1,-1)]
    samples = fixture["samples"]
    require(len(samples) == 3 and len(basis) == 330,"fixed corpus shape")
    reference_prefix = "target/quad-iregi-source-audit/rank7-n1-n5-corpus"
    reference_protocol = load(files[reference_prefix+"/protocol.json"])
    reference_validation = load(files[reference_prefix+"/capture-001/validation.json"])
    anchors = {}
    def slots(response):
        require(response["stable"] is True and response["poles"] == ["uv1","ir1","ir2","finite"]
                and len(response["moments"]) == 330,"stable complete quad IBP reference")
        require(all(len(m) == 4 and all(len(z) == 2 for z in m) for m in response["moments"]),"reference slots")
        return [[tuple(Fraction(v) for v in z) for z in m] for m in response["moments"]]
    for case in reference_validation["cases"]:
        if not case["eligible_IBP_reference_anchor"]:
            continue
        n,sid = case["propagators"],case["sample"]
        sample = next(s for s in samples if s["id"] == sid)
        request = next(r for r in reference_protocol["runtime"]["cases"] if r["id"] == case["id"])
        require(case["mode"] == 0 and case["applicable_identities_pass"] is True
                and request["exact_propagators"] == sample["propagators"][:n]
                and Fraction(request["exact_scale"]) == Fraction(sample["mu"]),"reference exact inputs/mode")
        anchors[n,sid] = slots(case["response"])
    old = files["target/quad-iregi-source-audit/future-positive-rank-requests/capture-001/request-3.stdout"].decode()
    response = [load(line[7:]) for line in old.splitlines() if line.startswith("RESULT ")]
    require(len(response) == 1 and response[0]["id"] == "quad_n5_first_five_conditioned_rank7","N5 archived base")
    anchors[5,samples[0]["id"]] = slots(response[0])
    require(len(anchors) == 15,"all fifteen IBP anchors")
    values = {}
    totals = {"reference_slots":0,"precision_slots":0,"scaling_slots":0,"IR_slots":0,"UV_convergent_slots":0,
              "exact_input_complex_arguments":0,"stored_precision_fields":0,"owned_groups_historically_absent":0}
    maxima = {"reference":Fraction(0),"precision":Fraction(0),"scaling":Fraction(0)}
    for case in protocol["cases"]:
        prefix = PRIVATE+"/captures/"+case["id"]
        receipt = load(files[prefix+"/receipt.json"])
        data = load(files[prefix+"/result.json"])
        n,bits = case["n"],case["bits"]
        require(receipt["status"] == "terminal_capture" and receipt["case"] == case
                and receipt["inputs_unchanged"] is True and receipt["cancellation"] is None
                and not receipt["cleanup_errors"] and len(receipt["steps"]) == 1
                and receipt["steps"][0]["returncode"] == 0
                and receipt["steps"][0]["owned_group_gone"] is True
                and receipt["elapsed_seconds"] <= case["total_seconds"]
                and receipt["driver_ledger_sha256"] == sha(files[prefix+"/result.json"]),"terminal owned capture")
        totals["owned_groups_historically_absent"] += 1
        for name,digest in receipt["saved_files"].items():
            if name in files:
                require(sha(files[name]) == digest,"retained output identity")
            else:
                require(name.endswith("/highpoint_public-frozen")
                        and digest == protocol["binary_sha256"],"explicitly omitted owned native copy")
        expected_settings = {"propagators":n,"rank":7,"powers":[1]*n,"dimension_shift":0,
                "algorithm":"PassarinoVeltman","convention":"IregiNative","tensor_weights":"Components",
                "invariants":"FromShifts","input_policy":"Preserve"}
        require(data["status"] == "all_lanes_success" and data["settings"] == expected_settings
                and data["working_bits"] == bits and data["requested_bits"] == 53
                and data["rows"] == 3 and data["components"] == 1
                and data["basis"] == basis and data["lane_statuses"] == ["Success"]*3,
                "exact complete public metadata")
        master_count = {1:1,2:3,3:7,4:15,5:30}[n]
        require(data["master_count"] == master_count and data["algorithm_used"] == "PassarinoVeltman"
                and data["fallback_used"] == data["analytic_used"] == [False]*3
                and len(data["diagnostics"]) == 3,"ordinary branch proof")
        require(data["execution"] == {"input_rows":3,"argument_rows":3,"reduction_rows":3,
                "master_rows":3*master_count,"master_family_batches":min(n,4),"pentagon_box_rows":0,
                "fallback_rows":0,"fallback_successes":0,"analytic_rows":0},"observed instruction-major batch counters")
        rows = []
        require(len(data["lanes"]) == 3,"complete sample lanes")
        for row,(lane,sample) in enumerate(zip(data["lanes"],samples)):
            expected = [[str(Fraction(v)),"0"] for prop in sample["propagators"][:n] for v in prop["shift"]]
            expected += [[str(Fraction(v)) for v in prop["mass_squared"]] for prop in sample["propagators"][:n]]
            expected += [[str(Fraction(sample["mu"])),"0"]]
            require(data["input_exact_rational"][row] == expected,"exact represented input")
            totals["exact_input_complex_arguments"] += len(expected)
            require(lane["row"] == row and lane["status"] == "Success" and len(lane["moments"]) == 330,"complete tensor lane")
            tensor = []
            for index,(alpha,moment) in enumerate(zip(basis,lane["moments"])):
                require(len(moment) == 4,"complete Laurent moment")
                unit2 = scale2(sample,n)**(sum(alpha)+4-2*n)
                target = []
                for slot,z in enumerate(moment):
                    require(all(type(z[k]) is int and 0 < z[k] <= bits for k in
                                ("real_precision","imaginary_precision")),"actual component precision metadata")
                    totals["stored_precision_fields"] += 2
                    pair = Fraction(z["real"]),Fraction(z["imaginary"])
                    target.append(pair)
                    maxima["reference"] = max(maxima["reference"],compare(pair,anchors[n,sample["id"]][index][slot],unit2,Fraction(1,10**20)))
                    totals["reference_slots"] += 1
                    if slot in (1,2):
                        require(pair == (0,0),"exact positive-F IR zero identity")
                        totals["IR_slots"] += 1
                    if slot == 0 and 4+sum(alpha)-2*n < 0:
                        require(pair == (0,0),"exact convergent UV zero identity")
                        totals["UV_convergent_slots"] += 1
                tensor.append(target)
            rows.append(tensor)
        values[n,bits] = rows
    require(len(values) == 10,"all ten successful cases")
    for n in range(1,6):
        for row,sample in enumerate(samples):
            for index,alpha in enumerate(basis):
                unit2 = scale2(sample,n)**(sum(alpha)+4-2*n)
                for slot in range(4):
                    maxima["precision"] = max(maxima["precision"],compare(values[n,128][row][index][slot],values[n,256][row][index][slot],unit2,Fraction(1,2**160)))
                    totals["precision_slots"] += 1
        for bits in (128,256):
            for index,alpha in enumerate(basis):
                factor = Fraction(2)**(sum(alpha)+4-2*n)
                unit2 = scale2(samples[1],n)**(sum(alpha)+4-2*n)
                for slot in range(4):
                    target = tuple(v*factor for v in values[n,bits][0][index][slot])
                    maxima["scaling"] = max(maxima["scaling"],compare(values[n,bits][1][index][slot],target,unit2,Fraction(1,2**160)))
                    totals["scaling_slots"] += 1
    require(totals == {"reference_slots":39600,"precision_slots":19800,"scaling_slots":13200,
        "IR_slots":19800,"UV_convergent_slots":996,"exact_input_complex_arguments":480,
        "stored_precision_fields":79200,"owned_groups_historically_absent":10},"complete replay counts")
    with localcontext() as c:
        c.prec = 100
        shown = {name:str((Decimal(q.numerator)/Decimal(q.denominator)).sqrt()) for name,q in maxima.items()}
    return {"status":"passed_complete_saved_numeric_and_source_replay","counts":totals,
            "maximum_normalized_complex_errors":shown,"new_native_execution":False,"new_process_probe":False,
            "full_rank7_domain_or_performance_qualified":False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct",type=Path)
    args = parser.parse_args()
    manifest = load((HERE/"manifest.json").read_bytes())
    files = restore_files(manifest)
    result = replay(files)
    if args.reconstruct is not None:
        require(not args.reconstruct.exists(),"reconstruction path already exists")
        for name,value in files.items():
            safe(name)
            path = args.reconstruct/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(value)
    print(json.dumps({"capsule_manifest_sha256":sha((HERE/"manifest.json").read_bytes()),
            "restored_files":len(files),"replay":result},indent=2))


if __name__ == "__main__":
    main()
