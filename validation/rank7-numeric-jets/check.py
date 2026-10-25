"""Portable replay of saved N2 tensors/jets/FD and beyond-53 evidence only."""
from pathlib import Path
from fractions import Fraction as F
import argparse
import json
import sys

sys.dont_write_bytecode=True
from portable import (BEYOND_AUDIT,BEYOND_CASES,BEYOND_REPLAY,CASES,CODE,INITIAL_AUDIT,INITIAL_REPLAY,MUTATION_AUDIT,
                      PREFIX,SOURCE_PARENT,describe,digest,document,import_checked,load_parents,
                      materialize,normalized,require,unpack)

HERE=Path(__file__).resolve().parent


def read_map(files,name):
    return document(files[normalized(name)])


def saved_leases(files,builds):
    """Check the seventeen saved stage identities/bounds, never live processes."""
    catalog=read_map(files,PREFIX+"/catalog_fixed.json")
    groups=set()
    environment=dict(RAYON_NUM_THREADS="1",RUST_TEST_THREADS="1",RUST_MIN_STACK="67108864")
    def stage(record,total,reserve,cap,command,returncode,status,cap_key="child_cap_seconds"):
        require(record["total_seconds"]==total and record["cleanup_reserve_seconds"]==reserve
                and record[cap_key]==cap and 0<cap<=total-reserve
                and 0<=F(str(record["elapsed_seconds"]))<=total
                and record["environment_overrides"]==environment and len(record["steps"])==1,
                "saved stage budget/environment differs")
        step=record["steps"][0]
        require(step["command"]==command and step["returncode"]==returncode and step["status"]==status
                and step["owned_group_gone"] is True and not step.get("timeout") and "error" not in step
                and 0<F(str(step["timeout_seconds"]))<=cap
                and 0<=F(str(step["elapsed_seconds"]))<=F(str(record["elapsed_seconds"])),
                "saved bounded command/outcome differs")
        group=step["owned_process_group"]
        require(type(group) is int and group>0 and group not in groups,"saved owned PG identifier reused/missing")
        groups.add(group)
        if "planned_command" in record:require(record["planned_command"]==command,"saved planned command differs")
    require(catalog["runtime_cpu_affinity"]=="20" or catalog["runtime_cpu_affinity"]==20,"frozen runtime CPU differs")
    require(catalog["build"]["total_seconds"]==900 and catalog["build"]["cleanup_reserve_seconds"]==60
            and catalog["build"]["jobs"]==4 and catalog["build"]["cpu_affinity"]=="18,24","frozen build bounds differ")
    build_command=["taskset","-c","18,24","cargo","build","--locked","--offline","-p","iregi-rust",
                   "--example","rank7_numeric_jets","--message-format=json","-j","4"]
    for context,code,status in [("build-001",101,"failed"),("build-002",0,"exited")]:
        stage(builds[context],900,60,780,build_command,code,status)
    product=builds["build-002"]["product"]["path"]
    require([c["id"] for c in catalog["cases"]]==CASES,"frozen initial case order differs")
    for case in catalog["cases"]:
        name=case["id"];record=read_map(files,PREFIX+"/captures/"+name+"-001/receipt.json")
        fd=name=="fd-float384"
        total,cap=(420,360) if fd else (300,240)
        require(case["total_seconds"]==total and case["cleanup_reserve_seconds"]==30
                and case["child_cap_seconds"]==cap,"frozen catalog case cap differs")
        command=["taskset","-c","20",product,catalog["fixture"],"2","7",case["domain"],str(case["requested_bits"]),
                 case["profile"],"pv",str(case["first_power"]),
                 "/shared/external/iregi/iregi-rust/"+PREFIX+"/captures/"+name+"-001/result.json"]
        stage(record,total,30,cap,command,0,"exited")
    protocol=read_map(files,PREFIX+"/beyond53/runtime-protocol-v2.json")
    require(protocol["order"]==BEYOND_CASES and protocol["cpu"]==20 and protocol["product"]["path"]==product,
            "beyond retained product/CPU/order differs")
    for name in BEYOND_CASES:
        case=protocol["cases"][name]
        record=read_map(files,PREFIX+"/beyond53/capture-v2-"+name+"-001/receipt.json")
        reject=name=="f64-rejection"
        total,reserve,cap,code=(90,20,30,2) if reject else (300,30,240,0)
        require(case["total_seconds"]==total and case["cleanup_reserve_seconds"]==reserve
                and case["child_seconds"]==cap and case["returncode"]==code
                and record["no_build"] is True and record["no_binary_copy"] is True,"beyond fixed cap/no-build differs")
        command=["taskset","-c","20",product,PREFIX+"/beyond53/fixture.json","2","7",case["domain"],"53","plain","pv","1",
                 "/shared/external/iregi/iregi-rust/"+PREFIX+"/beyond53/capture-v2-"+name+"-001/result.json"]
        stage(record,total,reserve,cap,command,code,"failed" if reject else "exited","child_seconds")
    require(len(groups)==17,"complete saved build/native stage metadata required")
    return len(groups)


def check_guards(manifest,files,value,parent_sources):
    source_sets=manifest["source_sets"]
    require(set(source_sets)=={"build-001","build-002"},"both failed and successful source snapshots required")
    builds={context:read_map(files,PREFIX+"/"+context+"/receipt.json") for context in source_sets}
    failed,passed=builds["build-001"],builds["build-002"]
    require(failed["status"]=="failed" and passed["status"]=="passed"
            and failed["inputs_unchanged"] is True and passed["inputs_unchanged"] is True
            and failed["cleanup_errors"]==passed["cleanup_errors"]==[],"failed/passed build history changed")
    require(len(failed["steps"])==len(passed["steps"])==1
            and failed["steps"][0]["returncode"]==101 and passed["steps"][0]["returncode"]==0
            and all(build["steps"][0]["owned_group_gone"] is True for build in builds.values()),
            "actual old/new build outcomes not preserved")
    require(files[PREFIX+"/build-001/step.log"].count(b"error[E0308]")==2,"two original borrow errors not preserved")
    lease_count=saved_leases(files,builds)
    product=passed["product"]
    require(product["sha256"]=="480a47a84d28d53597c751f4f5aafa7fa4a0c39ad66a707f6a15c759251828d8",
            "same successful frozen example product required")
    omitted={normalized(product["path"]):product["sha256"]}
    require(manifest["omitted_compiled_artifacts"]==omitted
            and manifest["unhashed_build_product_paths"]==[product["cargo_executable"]],"exact compiled omission inventory differs")
    source_manifest=document(files[SOURCE_PARENT+"/manifest.json"])
    inherited={entry["sha256"] for entry in source_manifest["sources"].values()}
    changed={}
    for context,entries in source_sets.items():
        require(set(entries)==set(builds[context]["source_files"]) and len(entries)==71,"complete71-file source snapshot required")
        same=0
        for name,entry in entries.items():
            body=value(entry)
            require(digest(body)==builds[context]["source_files"][name],"reconstructed source differs from actual build")
            if entry["sha256"] in inherited:
                same+=1;require(entry["origin"]=="source_parent","unchanged source unnecessarily duplicated")
            else:
                require(entry["origin"]=="payload","changed source must be explicit local delta")
                changed[entry["sha256"]]=body
        require(same==60,"exact60 inherited/11changed source split required")
    require(len(changed)==12 and sum(map(len,changed.values()))==480930,"exact deduplicated source delta changed")
    fix=read_map(files,PREFIX+"/compile-fix.json")
    source="crates/iregi-rust/examples/rank7_numeric_jets/main.rs"
    before=value(source_sets["build-001"][source]);after=value(source_sets["build-002"][source])
    require(digest(before)==fix["main_before_sha256"] and digest(after)==fix["main_after_sha256"]
            and before.count(fix["before"].encode())==1
            and before.replace(fix["before"].encode(),fix["after"].encode(),1)==after,
            "ownership-only two-RHS source correction changed")
    records=[]
    for context in source_sets:records.append((PREFIX+"/"+context+"/receipt.json",context,["inputs","saved_files"]))
    for case in CASES:
        folder=PREFIX+"/captures/"+case+"-001/"
        records += [(folder+"receipt.json","build-002",["inputs","saved_files"]),
                    (folder+"prerequisite.json","build-002",["source_inputs","anchor_inputs"])]
    for case in BEYOND_CASES:
        records.append((PREFIX+"/beyond53/capture-v2-"+case+"-001/receipt.json","build-002",["inputs","outputs"]))
    records += [(PREFIX+"/comparison-fixed.json","build-002",["input_sha256"]),
                (PREFIX+"/mutation-probes-fixed.json","build-002",["source_inputs"]),
                (PREFIX+"/independent-initial11-saved-numeric-audit.json","build-002",["input_sha256"]),
                (PREFIX+"/independent-initial11-mutation-companion.json","build-002",["input_sha256"]),
                (PREFIX+"/beyond53/independent-saved-audit-v1.json","build-002",["input_sha256"])]
    expected_names=set();guard_count=0
    for name,context,fields in records:
        record=read_map(files,name)
        for field in fields:
            key=name+"#"+field;expected_names.add(key)
            binding=manifest["guard_maps"][key]
            mapping=record[field]
            if field=="outputs":mapping={str(Path(name).parent/k):v for k,v in mapping.items()}
            require(binding["context"]==context and set(binding["entries"])==set(mapping),"closed guard mapping differs")
            for nominal,sha in mapping.items():
                entry=binding["entries"][nominal]
                require(entry["sha256"]==sha,"saved guard digest differs")
                if nominal.startswith("archive:"):
                    alias=normalized(nominal[8:]);expected=dict(kind="committed_quad_member",alias=alias,sha256=sha)
                    body=files[alias]
                else:
                    alias=normalized(nominal)
                    if alias in omitted:
                        require(sha==omitted[alias],"historical executable attestation differs")
                        require(entry==dict(kind="omitted_compiled",alias=alias,sha256=sha),"compiled omission map differs")
                        guard_count+=1;continue
                    if alias in source_sets[context]:
                        expected=dict(kind="source_snapshot",context=context,source=alias,sha256=sha)
                        body=value(source_sets[context][alias])
                    else:
                        require(entry["kind"] in {"committed_parent","alias"},"guard source category differs")
                        expected=dict(kind=entry["kind"],alias=alias,sha256=sha);body=files[alias]
                require(entry==expected and digest(body)==sha,"portable saved guard mismatch: "+nominal)
                guard_count+=1
    require(set(manifest["guard_maps"])==expected_names,"extra/dropped owned guard maps")
    return dict(source_snapshots=2,source_files_per_snapshot=71,inherited_sources_per_snapshot=60,
                unique_source_delta_bodies=12,source_delta_uncompressed_bytes=480930,
                exact_guard_occurrences=guard_count,saved_stage_leases_checked=lease_count,compiled_artifact_bytes_read=0)


def replay(manifest,files):
    require(digest(files[PREFIX+"/independent-initial11-saved-numeric-audit.json"])==INITIAL_AUDIT
            and digest(files[PREFIX+"/beyond53/independent-saved-audit-v1.json"])==BEYOND_AUDIT
            and digest(files[PREFIX+"/independent-initial11-mutation-companion.json"])==MUTATION_AUDIT,
            "immutable independent audits/companion changed")
    initial_module=import_checked(HERE/"initial_replay.py",INITIAL_REPLAY,"_n2_initial_independent_replay")
    beyond_module=import_checked(HERE/"beyond_replay.py",BEYOND_REPLAY,"_n2_beyond_independent_replay")
    reads=set()
    def raw(name):
        name=normalized(name);require(name in files,"unknown closed byte callback alias: "+name)
        reads.add(name);return files[name]
    initial=initial_module.audit(raw)
    old=read_map(files,PREFIX+"/independent-initial11-saved-numeric-audit.json")
    clean=lambda d,drop:{k:v for k,v in d.items() if k not in drop}
    require(len(initial["limitations"])==len(old["limitations"])==4
            and initial["limitations"][:3]==old["limitations"][:3]
            and old["limitations"][3]=="Fourteen mutation results are intentionally excluded while their stage is active."
            and initial["limitations"][3]=="Mutation-probe outcomes belong to the separate immutable companion and are not recomputed by this numeric replay.",
            "only the declared transport limitation may differ")
    reconstructed=clean(initial,{"created_utc","elapsed_seconds","portable_replay","filesystem_or_process_access"})
    original=clean(old,{"created_utc","elapsed_seconds"})
    reconstructed["limitations"]=old["limitations"]
    require(reconstructed==original,"independent initial replay differs from immutable audit")
    require(initial["passed"] is True and initial["failures"]==[] and initial["capture_count"]==11
            and initial["fd_reconstructed_components"]==23760
            and initial["comparison_counts"]==dict(quad=79200,pair=36960,mass=23760,dd=2640,scale=29040),
            "complete initial11 independent numerical replay failed")
    beyond=beyond_module.audit(raw)
    old_beyond=read_map(files,PREFIX+"/beyond53/independent-saved-audit-v1.json")
    require(beyond==clean(old_beyond,{"checker_sha256","elapsed_saved_reconstruction_seconds"}),
            "independent beyond53 replay differs from immutable audit")
    require(beyond["passed"] is True and beyond["findings"]==[] and beyond["slope_comparisons"]==7920
            and beyond["raw_pair_comparisons"]==2640 and beyond["expected_f64_preplan_rejections"]==1,
            "complete independent beyond53 replay failed")
    mutation=read_map(files,PREFIX+"/mutation-probes-fixed.json")
    companion=read_map(files,PREFIX+"/independent-initial11-mutation-companion.json")
    require(mutation["status"]=="passed_saved_value_mutation_probes"
            and companion["status"]=="passed_independent_terminal_saved_mutation_companion"
            and companion["initial_numeric_audit_sha256"]==INITIAL_AUDIT
            and companion["initial_numeric_audit_unchanged"] is True
            and companion["named_probe_count"]==14 and companion["all14_rejected_with_nonempty_failures"] is True
            and companion["findings"]==[],"saved mutation evidence/independent companion not passed")
    require(len(companion["checks"])==14 and all(c["rejected"] is True and c["failure_count"]>0 for c in companion["checks"]),
            "all fourteen failed mutation outcomes required")
    require(len(mutation["checks"])==14,"all recorded producer mutation outcomes required")
    for raw,witness in zip(mutation["checks"],companion["checks"]):
        require(raw["name"]==witness["name"] and raw["rejected"] is witness["rejected"] is True
                and len(raw["failures"])==witness["failure_count"]>0
                and sorted({item["category"] for item in raw["failures"]})==witness["categories"],
                "mutation raw rejection details differ from independent companion")
    return dict(initial_comparison_counts=initial["comparison_counts"],initial_native_operands_checked=initial["native_operands_checked"],
                fd_reconstructed_components=initial["fd_reconstructed_components"],
                beyond53_slope_comparisons=beyond["slope_comparisons"],beyond53_raw_pair_comparisons=beyond["raw_pair_comparisons"],
                expected_f64_preplan_rejections=1,saved_mutation_probes=14,
                independent_audit_reports_reproduced=2,closed_callback_aliases_read=len(reads))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parents-root",type=Path,default=HERE.parents[1])
    parser.add_argument("--allow-draft",action="store_true")
    parser.add_argument("--reconstruct",type=Path)
    args=parser.parse_args()
    manifest_body=(HERE/"manifest.json").read_bytes();manifest=document(manifest_body)
    require(manifest["status"]=="sealed_saved_N2_numeric_jets_with_beyond53" or
            args.allow_draft and manifest["status"]=="draft_saved_N2_numeric_jets_capsule_not_sealed","capsule is not sealed")
    require(set(manifest["capsule_files"])==set(CODE+["payload.tar.gz"]),"closed local capsule inventory differs")
    for name,descriptor in manifest["capsule_files"].items():
        require((HERE/name).is_file() and not (HERE/name).is_symlink()
                and describe((HERE/name).read_bytes())==descriptor,"capsule file changed: "+name)
    require(manifest["case_order"]==CASES and manifest["beyond_case_order"]==BEYOND_CASES,"required cases dropped")
    require(manifest["immutable_audits"]==dict(initial=INITIAL_AUDIT,beyond53=BEYOND_AUDIT,mutation=MUTATION_AUDIT),
            "three frozen independent anchors changed")
    require(all(manifest[name] is False for name in ["external_hermetic_build_closure_claimed","new_native_or_compiler_execution",
            "public_highpoint_Dual_qualified","typed_f64_or_DoubleFloat_Dual_tested","rigorous_error_qualified","performance_qualified"]),
            "saved one-family capsule promoted beyond its scope")
    _,sources,borrowed=load_parents(args.parents_root,manifest["parent_files"])
    blobs=unpack((HERE/"payload.tar.gz").read_bytes(),manifest["payload_members"])
    require(all(name=="blobs/"+digest(body) for name,body in blobs.items()),"content-addressed blob member differs")
    files,value=materialize(manifest,blobs,sources,borrowed)
    referenced={"blobs/"+entry["sha256"] for entry in manifest["aliases"].values() if entry["origin"]=="payload"}
    require(referenced==set(blobs),"unreferenced/dropped payload body")
    guards=check_guards(manifest,files,value,sources)
    numeric=replay(manifest,files)
    if manifest["status"].startswith("sealed_"):
        clear=read_map(files,manifest["final_release_alias"])
        require(clear["status"]=="released_compact_N2_saved_capsule_seal"
                and clear["code_sha256"]=={name:manifest["capsule_files"][name]["sha256"] for name in CODE}
                and clear["initial_audit_sha256"]==INITIAL_AUDIT and clear["beyond_audit_sha256"]==BEYOND_AUDIT
                and clear["mutation_companion_sha256"]==MUTATION_AUDIT,
                "sealed release source/anchor binding differs")
        for name,sha in clear["additional_evidence"].items():require(digest(files[normalized(name)])==sha,"sealed source-review evidence changed")
        draft_body=files[manifest["approved_draft_manifest_alias"]]
        require(digest(draft_body)==clear["draft_manifest_sha256"],"approved draft manifest not preserved")
        draft=document(draft_body)
        require(draft["status"]=="draft_saved_N2_numeric_jets_capsule_not_sealed","approved snapshot is not a draft")
        changed={"status","aliases","payload_members","capsule_files","final_release_alias","approved_draft_manifest_alias"}
        require({k:v for k,v in draft.items() if k not in changed}=={k:v for k,v in manifest.items() if k not in changed},
                "sealed cohort/source/parent context differs from approved draft")
        for name,entry in draft["aliases"].items():require(manifest["aliases"].get(name)==entry,"approved draft alias changed")
        for name,entry in draft["payload_members"].items():require(manifest["payload_members"].get(name)==entry,"approved draft payload changed")
        extras={normalized(n) for n in clear["additional_evidence"]}|{manifest["final_release_alias"],manifest["approved_draft_manifest_alias"]}
        require(set(manifest["aliases"])==set(draft["aliases"])|extras,"unexpected sealed evidence aliases")
        require(all(manifest["capsule_files"][n]==draft["capsule_files"][n] for n in CODE),"sealed code changed from approved draft")
    if args.reconstruct:
        args.reconstruct.mkdir(exist_ok=False)
        for context,source_set in manifest["source_sets"].items():
            for name,entry in source_set.items():
                path=args.reconstruct/context/normalized(name);path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(value(entry))
    # Verify the immutable local and parent files again after numeric replay.
    require((HERE/"manifest.json").read_bytes()==manifest_body,"manifest changed during replay")
    for name,descriptor in manifest["capsule_files"].items():require(describe((HERE/name).read_bytes())==descriptor,"capsule changed during replay")
    for name,descriptor in manifest["parent_files"].items():require(describe((args.parents_root/name).read_bytes())==descriptor,"parent changed during replay")
    print(json.dumps(dict(status="passed_portable_saved_N2_numeric_jets_and_beyond53",**guards,**numeric,
        compiler_or_integral_execution=False,current_process_state_probed=False,
        typed_f64_or_DoubleFloat_Dual_tested=False,public_highpoint_Dual_qualified=False,
        rigorous_error_qualified=False,performance_qualified=False),sort_keys=True))


if __name__=="__main__":main()
