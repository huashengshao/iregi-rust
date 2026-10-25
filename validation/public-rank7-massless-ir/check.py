#!/usr/bin/env python3
"""Portable exact replay of three saved massless rank-seven points.

restore_files(manifest) returns original-path byte aliases; replay(files) rechecks
all 11,884 numeric records and saved terminal/source attribution. No producer
comparator, native executable, compiler, integral evaluator or process probe runs.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = "validation/public-rank7-current-cargo-n1-n5"
PRIVATE = "target/public-rank7-massless-ir"
HISTORICAL = "/shared/external/iregi/iregi-rust/"
PROTOCOL = "d50d7823a3f49944186b20fb6675ba479ad1a6a97f17e69688ee0523f7f44299"
AUDIT = "237bb627fc0dd05a54dab40bafd3a7a25a51389b1c1f2aa65dd41c0ccbfb1858"
METADATA = "target/resume-20261025-review/massless-rank7-independent-terminal-metadata-review.json"


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def desc(value):
    return {"sha256": sha(value), "bytes": len(value)}


def load(value):
    return json.loads(value, parse_float=str)


def restore(manifest):
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts}
    require(actual == set(manifest["capsule_files"]) | {"manifest.json"}, "exact seven-file capsule inventory")
    for name, expected in manifest["capsule_files"].items():
        require(desc((HERE/name).read_bytes()) == expected, "capsule file " + name)
    for name, expected in manifest["parent_files"].items():
        require(desc((ROOT/name).read_bytes()) == expected, "declared parent " + name)
    require(sha((ROOT/PARENT/"manifest.json").read_bytes()) ==
            "735a1004f379f31ec6d39916e4f4d805f845434a02a87cd016a2fbce43d8ef83", "fixed actual-Cargo parent")
    require(sha((ROOT/PARENT/"check.py").read_bytes()) ==
            "c80b6ce042ea33a567e4eb053086cda927ab32932cdba8499be3d822d158d77d", "fixed independent parent checker")
    spec = importlib.util.spec_from_file_location("massless_saved_actual_cargo_parent", ROOT/PARENT/"check.py")
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    files = parent.restore_files(load((ROOT/PARENT/"manifest.json").read_bytes()))
    inherited = parent.replay(files)
    for name in manifest["parent_files"]:
        value = (ROOT/name).read_bytes()
        require(name not in files or files[name] == value, "parent top-file collision")
        files[name] = value
    members = parent.unpack((HERE/"payload.tar.gz").read_bytes(), manifest["payload_members"])
    origins = load((HERE/"payload-origins.json").read_bytes())
    require(set(origins) == set(manifest["preserved_files"]) | set(manifest["inherited_aliases"]), "closed own origins")
    for name, row in manifest["preserved_files"].items():
        parent.safe(name)
        value = members[row["member"]]
        require(desc(value) == {k:row[k] for k in ["sha256","bytes"]} ==
                {k:origins[name][k] for k in ["sha256","bytes"]}, "own alias identity")
        require(name not in files or files[name] == value, "own/parent collision")
        files[name] = value
    for name, row in manifest["inherited_aliases"].items():
        parent.safe(name)
        value = files[row["inherited_source"]]
        require(desc(value) == {k:row[k] for k in ["sha256","bytes"]} ==
                {k:origins[name][k] for k in ["sha256","bytes"]}, "inherited alias identity")
        files[name] = value
    return files, inherited


def restore_files(manifest):
    return restore(manifest)[0]


def independent_math(files):
    """Run hash-pinned independent arithmetic with in-memory path providers.

    Only reviewed imports, definitions, constants and the basis assertion are
    admitted. The original read/load functions and __main__ output writer are
    excluded. Two exact source substitutions preserve historical path identity
    and replace this-script hashing with the preserved original source bytes.
    Acceptance arithmetic, parsing, controls and main() are unchanged.
    """
    raw = files[PRIVATE+"/review/saved-math/audit.py"]
    require(sha(raw) == AUDIT, "independent audit source pin")
    source = raw.decode()
    substitutions = {
        "str((ROOT/f'fixtures/n{n}.json').resolve())": "HISTORICAL + str(ROOT/f'fixtures/n{n}.json')",
        "Path(__file__).read_bytes()": "ORIGINAL_AUDIT_BYTES",
    }
    for old, new in substitutions.items():
        require(source.count(old) == 1, "exact mechanical audit path substitution")
        source = source.replace(old,new)
    tree = ast.parse(source)
    definitions = {"require","unique_object","forbidden_constant","decode","rational","z","norm2","basis",
                   "parse_quad","fixture","parse_rust","receipt","error2","display_squared","record_key",
                   "profile","precision_profile","controls","main"}
    selected = []
    found = set()
    for node in tree.body:
        if isinstance(node,(ast.Import,ast.ImportFrom,ast.Assign)):
            selected.append(node)
        elif isinstance(node,ast.FunctionDef) and node.name in definitions:
            selected.append(node); found.add(node.name)
        elif isinstance(node,ast.Expr) and isinstance(node.value,ast.Call):
            require(isinstance(node.value.func,ast.Name) and node.value.func.id == "require", "only basis assertion at audit top-level")
            selected.append(node)
        else:
            require(isinstance(node,(ast.FunctionDef,ast.If)) or
                    isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant), "unexpected audit top-level statement")
    require(found == definitions, "closed independent audit definitions")
    namespace = {"HISTORICAL":HISTORICAL, "ORIGINAL_AUDIT_BYTES":raw}
    exec(compile(ast.Module(body=selected,type_ignores=[]),"<preserved-independent-massless-audit>","exec"),namespace)

    def read(path, expected=None):
        name = str(path)
        require(Path(name).name != "owned-executable", "no executable reads")
        require(name in files, "saved audit read closure " + name)
        body = files[name]
        require(len(body) < 8_000_000 and (expected is None or sha(body) == expected), "saved audit read identity")
        namespace["READ"][name] = desc(body)
        return body

    namespace["read"] = read
    namespace["load"] = lambda path, expected=None: namespace["decode"](read(path,expected))
    computed = namespace["decode"](json.dumps(namespace["main"]()))
    saved = namespace["decode"](files[PRIVATE+"/review/saved-math/receipt.json"])
    require(computed == saved, "complete independent saved numeric receipt equality")
    return computed


def replay(files):
    read = lambda name: load(files[PRIVATE+"/"+name])
    p, release, q = read("protocol.json"), read("numerical-release.json"), read("qualification-after-independent.json")
    require(sha(files[PRIVATE+"/protocol.json"]) == PROTOCOL, "fixed executed protocol")
    grant, source = read("root-grant.json"), read("review/independent-source-review.json")
    for draft in ["001-unexecuted-before-review","002-unexecuted-before-deadline-cleanup","003-unexecuted-before-started-flag"]:
        prefix = PRIVATE+"/earlier-drafts/"+draft
        inventory = load(files[prefix+"/inventory.json"])
        require(inventory["native_execution"] is False, "earlier draft unexecuted")
        for name,digest in inventory["files"].items():
            alias = prefix+"/"+name
            if alias not in files:
                require(name.startswith("fixtures/"), "only unchanged shared fixtures outside draft directory")
                alias = PRIVATE+"/"+name
            require(sha(files[alias]) == digest, "earlier unexecuted source inventory")
    require(grant["status"] == "granted" and grant["grantor"] == "/root" and grant["protocol_sha256"] == PROTOCOL
            and grant["review_sha256"] == sha(files[PRIVATE+"/review/independent-source-review.json"])
            and grant["cases"] == [c["id"] for c in p["cases"]] and grant["no_retry_or_budget_extension"] is True, "exact root grant")
    require(source["findings"] == [] and source["recipe_sha256"] == PROTOCOL, "source review clear")
    for name, expected in source["subject_sha256"].items():
        require(sha(files[PRIVATE+"/"+name]) == expected, "reviewed controller source")
    for name, row in source["review_controls"].items():
        require(sha(files[PRIVATE+"/review/"+name]) == row["sha256"], "reviewer control source/result")
    manifest = load((HERE/"manifest.json").read_bytes())
    historical = manifest["omitted_native_and_tool_bindings"]
    fresh = 0
    for absolute, expected in release["bindings"].items():
        name = absolute.removeprefix(HISTORICAL)
        if name in files:
            require(sha(files[name]) == expected, "retained narrow release binding " + name); fresh += 1
        else:
            require(historical[absolute] == expected, "explicit omitted native/tool attestation")
    expected_union = {**p["bindings"], **{HISTORICAL+PRIVATE+"/"+n:sha(files[PRIVATE+"/"+n])
                        for n in ["protocol.json","review/independent-source-review.json","root-grant.json"]},
                      **{case["binary"]:case["binary_sha256"] for case in p["cases"]}}
    require(release["bindings"] == expected_union and len(expected_union) == 55, "exact 55-guard release union")
    require(release["status"] == "all_nine_owned_groups_absent_numeric_lease_released" and release["numerical_lease_released"] is True
            and release["new_integral_or_compilation_performed"] is False and release["previous_owned_binary_copies_rehashed"] is False, "saved release scope")
    groups = []
    for ordinal, case in enumerate(p["cases"]):
        prefix = PRIVATE+"/captures/"+case["id"]
        receipt = load(files[prefix+"/receipt.json"])
        step = receipt["steps"][0]
        owned = HISTORICAL+prefix+"/owned-executable"
        case_union = {**p["bindings"], **{HISTORICAL+PRIVATE+"/"+n:sha(files[PRIVATE+"/"+n])
                      for n in ["protocol.json","review/independent-source-review.json","root-grant.json"]},
                      case["binary"]:case["binary_sha256"], owned:case["binary_sha256"]}
        require(receipt["inputs"] == case_union and len(case_union) == 55, "exact per-case guarded union")
        command = [p["tools"]["taskset"],"-c",str(case["cpu"])]
        if case["kind"] == "quad":
            command += [p["tools"]["python"],p["quad_worker"],"--binary",owned,"--input",case["input"],
                        "--stdout",HISTORICAL+prefix+"/stdout.txt","--stderr",HISTORICAL+prefix+"/stderr.txt"]
        else:
            command += [owned,case["input"],str(case["n"]),"7","pv",str(case["bits"]),"53","1",HISTORICAL+prefix+"/result.json"]
            require(receipt["environment_additions"] == {name:"1" for name in
                    ["RAYON_NUM_THREADS","RUST_TEST_THREADS","OMP_NUM_THREADS","OPENBLAS_NUM_THREADS"]}, "single-thread saved environment")
        require(receipt["command"] == step["command"] == command, "exact invocation")
        row = release["cases"][ordinal]
        require(row == {"case":case["id"],"receipt_sha256":sha(files[prefix+"/receipt.json"]),
                        "group":step["owned_process_group"],"actual_absence_checked":True}, "historical terminal group receipt")
        groups.append(step["owned_process_group"])
    require(len(groups) == len(set(groups)) == 9, "nine distinct saved owned groups")
    schedule = read("executor-schedule-attestation.json")
    require(schedule["protocol_sha256"] == PROTOCOL and schedule["release_sha256"] == sha(files[PRIVATE+"/numerical-release.json"])
            and schedule["UTC_start_finish_recorded_in_case_controller"] is False
            and schedule["absolute_overlap_independently_replayable_from_saved_receipts"] is False
            and schedule["maximum_native_case_width_executor_attested"] == 2
            and schedule["mtime_not_used_as_clock_evidence"] is True and schedule["no_timestamp_invented"] is True, "attested chronology limitations")
    require([len(row["cases"]) for row in schedule["phases"]] == [1,1,1,2,2,2], "attested phase widths")
    attested = [item for phase in schedule["phases"] for item in phase["cases"]]
    for case,item in zip(p["cases"],attested):
        receipt = read("captures/"+case["id"]+"/receipt.json")
        require(item["case"] == case["id"] and item["cpu"] == case["cpu"] and item["owned_group"] == receipt["steps"][0]["owned_process_group"]
                and item["receipt_sha256"] == sha(files[PRIVATE+"/captures/"+case["id"]+"/receipt.json"])
                and item["terminal_collected_before_next_phase_executor_attestation"] is True, "attested case/session map")
    metadata = load(files[METADATA])
    require(metadata["findings"] == [] and metadata["checks"] == 542 and metadata["protocol_sha256"] == PROTOCOL
            and metadata["fresh_groups_absent"] == groups and metadata["previous_owned_executable_copies_rehashed"] is False, "preserved independent metadata review")
    require(metadata["reconstructed_actual_Cargo_sources"] == 64 and
            set(metadata["original_frozen_binaries_freshly_hashed_once_each"]) == {c["binary_sha256"] for c in p["cases"]},
            "historical archived source/original artifact attribution")
    for name,digest in metadata["fresh_hashes"].items():
        if name in files:
            require(sha(files[name]) == digest, "preserved metadata source/data hash")
        else:
            absolute = name if name.startswith("/") else HISTORICAL+name
            require(historical[absolute] == digest, "historical metadata binary/tool identity")
    require(metadata["checker_sha256"] == sha(files["target/resume-20261025-review/audit_massless_rank7_metadata_saved.py"]), "preserved metadata checker bytes only")
    numeric = independent_math(files)
    for name in ["provisional_qualification","source_review","grant","comparison","numerical_release","independent_saved_numeric_review",
                 "executor_schedule_attestation"]:
        path = {"provisional_qualification":"qualification.json","source_review":"review/independent-source-review.json",
                "grant":"root-grant.json","comparison":"comparison.json","numerical_release":"numerical-release.json",
                "independent_saved_numeric_review":"review/saved-math/receipt.json","executor_schedule_attestation":"executor-schedule-attestation.json"}[name]
        require(q[name+"_sha256"] == sha(files[PRIVATE+"/"+path]), "final qualification dependency " + name)
    require(q["independent_narrow_source_terminal_metadata_review_sha256"] == sha(files[METADATA])
            and q["independent_saved_numeric_reviewer_script_sha256"] == AUDIT
            and q["protocol_sha256"] == PROTOCOL, "independent final qualification pins")
    require((HERE/"qualification.json").read_bytes() == files[PRIVATE+"/qualification-after-independent.json"], "exact final qualification copy")
    require(q["all_numeric_records"] == 11884 and q["numeric_failures"] == 0
            and q["all_Rust_actual_algorithm"] == "PassarinoVeltman" and q["all_Rust_analytic_used"] is True
            and q["all_Rust_fallback_used"] is False and q["individual_UV_IR_preserved"] is True, "final numerical/route scope")
    require(q["maximum_errors"] == numeric["maximum_reported_errors"] and q["complete_reference_arrays"] == 3
            and q["complete_Rust_arrays"] == 6 and q["native_reference_complex_slots"] == 3960
            and q["candidate_complex_slots"] == q["reference_comparisons"] == 7920
            and q["precision_pairs"] == 3960 and q["existing_scalar_anchor_checks"] == 4, "final qualification counts/maxima")
    for flag in ["current_live_Cargo_or_facade_rebuild_qualified","full_massless_domain_qualified",
                 "Dual_generalized_physical_or_performance_qualified","independent_absolute_UTC_or_overlap_proof",
                 "achieved_working_precision_bits_claimed","zero_projection_performed"]:
        require(q[flag] is False, "unqualified scope remains explicit")
    return {"complete_reference_arrays":3,"reference_complex_slots":3960,"complete_Rust_arrays":6,
            "Rust_complex_slots":7920,"exact_numeric_records_replayed":11884,"numeric_failures":0,
            "actual_PV_analytic_arrays":6,"fallback_arrays":0,"individual_UV_IR_preserved":True,
            "available_narrow_source_data_guards_checked":fresh,"historical_native_tool_guard_identities":55-fresh,
            "saved_owned_groups_historically_absent":9,"executor_attested_phase_widths":[1,1,1,2,2,2],
            "independent_UTC_overlap_proof":False,"fresh_native_hash_or_process_probe":False,
            "full_massless_domain_or_current_live_Cargo_or_performance_qualified":False,
            "maximum_errors":numeric["maximum_reported_errors"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct",type=Path)
    args = parser.parse_args()
    manifest = load((HERE/"manifest.json").read_bytes())
    files,inherited = restore(manifest)
    result = replay(files)
    inventory = {n:desc(v) for n,v in sorted(files.items())}
    receipt = load((HERE/"copy-receipt.json").read_bytes())
    require(receipt["restored_files"] == len(files) and receipt["restored_inventory_sha256"] ==
            sha((json.dumps(inventory,sort_keys=True,indent=2)+"\n").encode())
            and receipt["massless_replay"] == result and receipt["inherited_actual_Cargo_replay"] == inherited,
            "saved copy receipt replay/inventory")
    if args.reconstruct:
        require(not args.reconstruct.exists(), "reconstruction destination must be new")
        destination = args.reconstruct.resolve()
        require(destination != ROOT and ROOT not in destination.parents or HERE/".packaging" in destination.parents,
                "reconstruct outside project or packaging scratch")
        for name,value in files.items():
            path = destination/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(value)
    print(json.dumps({"status":"passed_portable_restricted_massless_rank7_saved_replay",
                      "restored_files":len(files),"inherited_actual_Cargo":inherited,"massless":result},sort_keys=True))


if __name__ == "__main__":
    main()
