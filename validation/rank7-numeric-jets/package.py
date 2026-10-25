"""Package saved N2 bytes and source deltas; never build or evaluate an integral."""
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode=True
from portable import (BEYOND_AUDIT,BEYOND_CASES,BEYOND_REPLAY,CASES,CODE,INITIAL_AUDIT,INITIAL_REPLAY,MUTATION_AUDIT,
                      PREFIX,ROOT_ID,SOURCE_PARENT,archive_bytes,describe,digest,document,load_parents,normalized,plain_saved_file,require,unpack)

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SUFFIXES={".py",".json",".md",".patch",".log",".rs",".txt"}


def save(path,value):
    Path(path).write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def draft(destination):
    require(Path.cwd().resolve()==ROOT,"run from project root")
    destination=Path(destination).resolve()
    require(destination.parent==ROOT/"target","draft must be a fresh direct child of project target, outside the corpus scan")
    require(destination!=ROOT/"validation/rank7-numeric-jets","draft must not occupy the final capsule path")
    destination.mkdir(exist_ok=False)
    parent_pins,parent_sources,borrowed=load_parents(ROOT)
    index={}
    parent_manifest=document(borrowed[SOURCE_PARENT+"/manifest.json"])
    for key in sorted(parent_manifest["sources"]):
        body=parent_sources[key]
        index.setdefault(digest(body),(key,body))
    blobs,aliases,source_sets,omitted,owned_guards={},{},{},{},{}
    def add(name,body):
        name=normalized(name)
        descriptor=describe(body)
        sha=descriptor["sha256"]
        if name in borrowed and borrowed[name]==body:
            entry=dict(descriptor,origin="committed_parent",key=name)
        elif sha in index:
            entry=dict(descriptor,origin="source_parent",key=index[sha][0])
        else:
            blobs["blobs/"+sha]=body
            entry=dict(descriptor,origin="payload")
        require(name not in aliases or aliases[name]==entry,"conflicting alias "+name)
        aliases[name]=entry
        return entry
    def file(name,expected=None):
        name=normalized(name)
        body=plain_saved_file(ROOT/name)
        require(expected is None or digest(body)==expected,"changed saved input "+name)
        return add(name,body)
    builds={}
    for context in ["build-001","build-002"]:
        name=PREFIX+"/"+context+"/receipt.json"
        record=document((ROOT/name).read_bytes());builds[context]=record
        require(len(record["source_files"])==71,"exact71-source snapshot required")
        source_sets[context]={}
        for source,sha in record["source_files"].items():
            alias=PREFIX+"/"+context+"/source-snapshot/"+source
            source_sets[context][source]=file(alias,sha)
        file(name)
    product=builds["build-002"]["product"]
    omitted[normalized(product["path"])]=product["sha256"]
    # Include only the selected cohort's source/evidence directories. Compiled
    # products and Python caches are never opened; snapshots are mapped above.
    for base in [PREFIX,"target/rank7-numeric-jets-proposal"]:
        for path in sorted((ROOT/base).rglob("*")):
            if not path.is_file() or path.suffix not in SUFFIXES or "__pycache__" in path.parts:
                continue
            name=str(path.relative_to(ROOT))
            if "/source-snapshot/" in name:
                continue
            file(name)
    def guards(record_name,mapping,context):
        entries={}
        for nominal,sha in mapping.items():
            require(type(sha) is str and len(sha)==64,"invalid saved guard digest")
            if nominal.startswith("archive:"):
                name=normalized(nominal[8:])
                require(name in borrowed and digest(borrowed[name])==sha,"unavailable exact quad alias")
                entries[nominal]=dict(kind="committed_quad_member",alias=name,sha256=sha)
                continue
            name=normalized(nominal)
            if name in omitted:
                require(omitted[name]==sha,"compiled omission digest differs from build receipt")
                entries[nominal]=dict(kind="omitted_compiled",alias=name,sha256=sha)
            elif name in source_sets[context]:
                require(source_sets[context][name]["sha256"]==sha,"contextual source guard differs")
                entries[nominal]=dict(kind="source_snapshot",context=context,source=name,sha256=sha)
            elif name in borrowed:
                require(digest(borrowed[name])==sha,"committed parent guard differs")
                entries[nominal]=dict(kind="committed_parent",alias=name,sha256=sha)
            else:
                file(name,sha)
                entries[nominal]=dict(kind="alias",alias=name,sha256=sha)
        owned_guards[record_name]=dict(context=context,entries=entries)
    # Contextual guard maps are derived only from the cohort's OWN receipts and
    # directly audited records. Other historical receipts are retained bytes;
    # recursively traversing their dependency closures is explicitly excluded.
    records=[]
    for context in ["build-001","build-002"]:
        records.append((PREFIX+"/"+context+"/receipt.json",context,["inputs","saved_files"]))
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
    for name,context,fields in records:
        record=document((ROOT/name).read_bytes())
        for field in fields:
            mapping=record[field]
            if field=="outputs":
                mapping={str(Path(name).parent/key):value for key,value in mapping.items()}
            guards(name+"#"+field,mapping,context)
    require(digest((ROOT/PREFIX/"independent-initial11-saved-numeric-audit.json").read_bytes())==INITIAL_AUDIT,
            "initial immutable independent audit changed")
    require(digest((ROOT/PREFIX/"beyond53/independent-saved-audit-v1.json").read_bytes())==BEYOND_AUDIT,
            "beyond immutable independent audit changed")
    require(digest((ROOT/PREFIX/"independent-initial11-mutation-companion.json").read_bytes())==MUTATION_AUDIT,
            "frozen independent mutation companion changed")
    payload=archive_bytes(blobs)
    (destination/"payload.tar.gz").write_bytes(payload)
    for name in CODE:
        body=plain_saved_file(HERE/name)
        if name=="initial_replay.py":require(digest(body)==INITIAL_REPLAY,"initial independent replay changed")
        if name=="beyond_replay.py":require(digest(body)==BEYOND_REPLAY,"beyond independent replay changed")
        (destination/name).write_bytes(body)
    manifest=dict(schema_version=1,status="draft_saved_N2_numeric_jets_capsule_not_sealed",
        historical_root=ROOT_ID,private_prefix=PREFIX,case_order=CASES,beyond_case_order=BEYOND_CASES,
        parent_files=parent_pins,aliases=aliases,source_sets=source_sets,guard_maps=owned_guards,
        payload_members={name:describe(body) for name,body in blobs.items()},
        omitted_compiled_artifacts=omitted,
        unhashed_build_product_paths=[product["cargo_executable"]],
        direct_historical_receipts_not_recursively_expanded=["target/main-private-seven-instrumented/build-002/receipt.json",
            "target/highpoint-dual-focused-tests-v1/tests-001/receipt.json","target/highpoint-dual-focused-tests-v1/release.json",
            "target/certified-planar-generalized-scalar-numeric/build-001/receipt.json"],
        immutable_audits=dict(initial=INITIAL_AUDIT,beyond53=BEYOND_AUDIT,mutation=MUTATION_AUDIT),
        capsule_files={name:describe((destination/name).read_bytes()) for name in CODE+["payload.tar.gz"]},
        all_numerical_evidence_preserved=True,source_reconstruction_is_complete_for_declared_71_files_only=True,
        external_hermetic_build_closure_claimed=False,new_native_or_compiler_execution=False,
        public_highpoint_Dual_qualified=False,typed_f64_or_DoubleFloat_Dual_tested=False,
        rigorous_error_qualified=False,performance_qualified=False)
    save(destination/"manifest.json",manifest)
    print(json.dumps(dict(status=manifest["status"],output=str(destination),manifest_sha256=digest((destination/"manifest.json").read_bytes()),
                         payload_bytes=len(payload),blob_count=len(blobs),alias_count=len(aliases))))


def seal(source,destination,clear_path):
    source,destination=Path(source).resolve(),Path(destination).resolve()
    require(Path.cwd().resolve()==ROOT,"run from project root")
    clear_body=plain_saved_file(clear_path);clear=document(clear_body)
    draft_manifest_body=(source/"manifest.json").read_bytes()
    manifest=document(draft_manifest_body)
    require(clear["status"]=="released_compact_N2_saved_capsule_seal"
            and clear["draft_manifest_sha256"]==digest((source/"manifest.json").read_bytes())
            and clear["initial_audit_sha256"]==INITIAL_AUDIT and clear["beyond_audit_sha256"]==BEYOND_AUDIT
            and clear["mutation_companion_sha256"]==MUTATION_AUDIT,
            "missing exact reviewed final anchor release")
    require(clear["code_sha256"]=={name:digest((HERE/name).read_bytes()) for name in CODE}
            and clear["code_sha256"]=={name:manifest["capsule_files"][name]["sha256"] for name in CODE},
            "sealed source code differs from reviewed draft/release")
    require(manifest["status"]=="draft_saved_N2_numeric_jets_capsule_not_sealed","source is not a reviewed draft")
    for name,descriptor in manifest["capsule_files"].items():
        require(describe((source/name).read_bytes())==descriptor,"draft capsule changed")
    blobs=unpack((source/"payload.tar.gz").read_bytes(),manifest["payload_members"])
    additions=dict(clear["additional_evidence"])
    additions[normalized(str(Path(clear_path).resolve().relative_to(ROOT)))]=digest(clear_body)
    for name,sha in additions.items():
        name=normalized(name);body=plain_saved_file(ROOT/name)
        require(digest(body)==sha,"seal review/evidence changed")
        if name in manifest["aliases"]:
            require(manifest["aliases"][name]["sha256"]==sha and manifest["aliases"][name]["bytes"]==len(body),
                    "conflicting seal evidence alias")
            continue
        entry=dict(describe(body),origin="payload")
        manifest["aliases"][name]=entry;blobs["blobs/"+sha]=body
    draft_alias=normalized(str(source.relative_to(ROOT)/"manifest.json"))
    require(draft_alias not in manifest["aliases"],"draft manifest alias already exists")
    manifest["aliases"][draft_alias]=dict(describe(draft_manifest_body),origin="payload")
    blobs["blobs/"+digest(draft_manifest_body)]=draft_manifest_body
    destination.mkdir(exist_ok=False)
    for name in CODE:(destination/name).write_bytes((source/name).read_bytes())
    body=archive_bytes(blobs);(destination/"payload.tar.gz").write_bytes(body)
    manifest["payload_members"]={name:describe(body) for name,body in blobs.items()}
    manifest["capsule_files"]["payload.tar.gz"]=describe(body)
    manifest.update(status="sealed_saved_N2_numeric_jets_with_beyond53",final_release_alias=normalized(str(Path(clear_path).resolve().relative_to(ROOT))),
                    approved_draft_manifest_alias=draft_alias)
    save(destination/"manifest.json",manifest)
    print(json.dumps(dict(status=manifest["status"],output=str(destination),manifest_sha256=digest((destination/"manifest.json").read_bytes()))))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--draft")
    group.add_argument("--seal")
    parser.add_argument("--output")
    parser.add_argument("--clear")
    args=parser.parse_args()
    if args.draft:
        require(args.output is None and args.clear is None,"draft takes only its explicit destination")
        draft(args.draft)
    else:
        require(args.output is not None and args.clear is not None,"seal needs exact output and final clear")
        seal(args.seal,args.output,args.clear)


if __name__=="__main__":main()
