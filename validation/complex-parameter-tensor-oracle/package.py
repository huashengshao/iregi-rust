#!/usr/bin/env python3
"""Package saved bytes only. No producer/native/scientific imports or jobs."""
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = "target/low-n-complex-rank7-oracle"
PARENT = "validation/quad-original-iregi-generalized-rank7"
HISTORICAL = "/shared/external/iregi/iregi-rust/"
ALLOWED = {".rs",".py",".json",".md",".log",".txt"}


def require(ok,message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return dict(sha256=sha(body),bytes=len(body))


def load(body):
    return json.loads(body)


def scan(name,body):
    require(not name.startswith("/") and ".." not in Path(name).parts,"safe saved alias")
    require(not body.startswith(b"\x7fELF"),"native executable forbidden")
    require(re.search(rb"S-[0-9]{3}-[0-9]{4}\.[0-9]{2}\.[0-9]{2}-[A-Z0-9]{20}",body) is None,
            "license literal forbidden: "+name)


def main():
    require(Path.cwd().resolve()==ROOT,"run from project root")
    require(not (HERE/"manifest.json").exists(),"preserve sealed capsule")
    pm = load((ROOT/PARENT/"manifest.json").read_bytes())
    require(sha((ROOT/PARENT/"manifest.json").read_bytes())==
        "ccda92bdd0be40484b2d8762d479658ada0beb98eb610df7c96b44f7f521a0b0","fixed parent manifest")
    require(sha((ROOT/PARENT/"check.py").read_bytes())==
        "8bd9efc8ee6f95f9a0387c3510f105b9bceda416aade16c2e3bee2ef445cee7e","fixed parent checker")
    spec = importlib.util.spec_from_file_location("complex_capsule_packaging_independent_parent",ROOT/PARENT/"check.py")
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    inherited,helpers,_ = parent.restore(pm)
    parent_files = dict(pm["parent_files"])
    for name in list(pm["capsule_files"])+["manifest.json"]:
        alias = PARENT+"/"+name
        body = (ROOT/alias).read_bytes()
        parent_files[alias] = desc(body)
        inherited[alias] = body
    for name,expected in parent_files.items():
        require(desc((ROOT/name).read_bytes())==expected,"parent closure drift")
    required_parent_sources = {name:desc(body) for name,body in inherited.items()
        if name.startswith("target/quad-iregi-source-audit/source-v2/")}
    require(required_parent_sources,"original-quad source context required")
    bodies,omitted,caches = {},{},[]
    binary_sha = {
        PRIVATE+"/engineering-v3/build-001/parameter-oracle-worker":"2fbcb850c079305ff68687f5f7bf91702766bc3a206cddae804ca92136c9c4a3",
        PRIVATE+"/engineering-v3/build-001/parameter-oracle-tests":"4498a817e95df1681687fd91a524246a9dfaa30fbf2f950982a0e7af48bbe713",
        PRIVATE+"/quadrature-proposal/capture-001/worker-frozen":"2fbcb850c079305ff68687f5f7bf91702766bc3a206cddae804ca92136c9c4a3"}
    for path in sorted((ROOT/PRIVATE).rglob("*")):
        if not path.is_file():
            continue
        name = str(path.relative_to(ROOT))
        if "__pycache__" in path.parts or path.suffix==".pyc":
            caches.append(name); continue
        if name in binary_sha:
            omitted[name] = dict(captured_sha256=binary_sha[name],reason="historical native artifact; not copied or rehashed")
            continue
        require(path.suffix in ALLOWED and path.stat().st_size<20000000,"unexpected private payload leaf: "+name)
        bodies[name] = path.read_bytes()
    numeric = load(bodies[PRIVATE+"/review/independent-saved-complex-numeric.json"])
    metadata = load(bodies[PRIVATE+"/review/independent-saved-complex-metadata.json"])
    needed = set(numeric["input_bindings"])|set(metadata["freshly_verified"]["raw_saved_files_hashed"])
    for name in needed:
        if name not in bodies:
            bodies[name] = (ROOT/name).read_bytes()
    # Keep raw reference streams, fixtures, requests and producers as source
    # context, without extending this capsule to the other four point families.
    external = ROOT/"target/orthogonal-rank7-kinematics"
    for n in (2,3,4):
        for path in (external/"captures"/f"n{n}_complex_width-quad-IBP-001").iterdir():
            if path.is_file():
                require(path.suffix in ALLOWED,"reference binary forbidden")
                bodies[str(path.relative_to(ROOT))] = path.read_bytes()
        request = external/"fixtures"/f"n{n}_complex_width-quad-IBP.txt"
        bodies[str(request.relative_to(ROOT))] = request.read_bytes()
    for name in ("protocol.json","run.py","capture_worker.py","prepare.py","lifecycle.py",
                 "source-review.json","comparison-amendment.json","comparison-amendment-review.json"):
        path = external/name
        bodies[str(path.relative_to(ROOT))] = path.read_bytes()
    for name,row in load(bodies[PRIVATE+"/engineering-v3/packet.json"])["rust_source_files"].items():
        body = bodies[PRIVATE+"/engineering-v3/"+name]
        require(desc(body)==row,"exact actual Rust source")
        bodies["crates/iregi-rust/examples/parameter_oracle/"+Path(name).name] = body
    for name,expected in numeric["input_bindings"].items():
        require(desc(bodies[name])==expected,"independent numeric read descriptor")
    for name,expected in metadata["freshly_verified"]["raw_saved_files_hashed"].items():
        require(desc(bodies[name])==expected,"independent metadata read descriptor")
    require((HERE/"independent_numeric_audit.py").read_bytes()==bodies[PRIVATE+"/review/audit_saved_complex.py"],
            "independent checker copied unchanged")
    registry = {}
    for name,body in sorted(inherited.items()):
        registry.setdefault((sha(body),len(body)),name)
    members,preserved,aliases,origins = {},{},{},{}
    own_registry = {}
    for name,body in sorted(bodies.items()):
        scan(name,body)
        row = desc(body)
        signature = (row["sha256"],row["bytes"])
        if name in inherited:
            require(body==inherited[name],"parent alias collision")
        if signature in registry:
            aliases[name] = dict(inherited_source=registry[signature],**row)
        else:
            member = own_registry.setdefault(signature,name)
            if member not in members:
                members[member] = body
            preserved[name] = dict(member=member,**row)
        origins[name] = dict(origin=HISTORICAL+name,**row)
    packed = io.BytesIO()
    with gzip.GzipFile(fileobj=packed,mode="wb",filename="",mtime=0) as compressed:
        with tarfile.open(fileobj=compressed,mode="w",format=tarfile.USTAR_FORMAT) as archive:
            for name,body in sorted(members.items()):
                item = tarfile.TarInfo(name)
                item.size,item.mode,item.mtime,item.uid,item.gid = len(body),0o644,0,0,0
                item.uname = item.gname = ""
                archive.addfile(item,io.BytesIO(body))
    (HERE/"payload.tar.gz").write_bytes(packed.getvalue())
    (HERE/"payload-origins.json").write_text(json.dumps(origins,indent=2)+"\n")
    own_files = ["README.md","check.py","package.py","independent_numeric_audit.py","qualification.json",
                 "payload.tar.gz","payload-origins.json"]
    manifest = dict(schema_version=1,status="saved_independently_audited_complex_parameter_tensor_reference",
        capsule_files={name:desc((HERE/name).read_bytes()) for name in own_files},
        payload_members={name:desc(body) for name,body in members.items()},preserved_files=preserved,
        inherited_aliases=aliases,parent_files=parent_files,required_parent_sources=required_parent_sources,
        omitted_native_products=omitted,omitted_python_caches=caches,
        independent_numeric_checker_sha256="94e726bced4201332edf714ff60d1c7c82661dd360150cc681b825fdef06f0a0",
        complete_grids=18,complete_native_complex_slots=23760,point_rows=88256,comparison_records=43566,
        separate_IR_zero_checks=11880,independent_negative_controls=15,
        numerical_package_tree_contents_included=False,broad_Rust_dependency_closure_included=False,
        compiled_products_included=False,license_literal_included=False,
        native_PID_tool_and_package_attestations_freshly_reenacted=False,
        N4_original_reference_eligible=False,rigorous_error_bound=False,
        arbitrary_precision_integral_accuracy=False,TIRust_agreement_qualified=False,performance_evidence=False)
    (HERE/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(dict(status="packaged_saved_bytes_pending_portable_replay",manifest_sha256=sha((HERE/"manifest.json").read_bytes()),
        preserved_aliases=len(preserved),borrowed_aliases=len(aliases),unique_payload_members=len(members),
        parent_files=len(parent_files),payload_bytes=len(packed.getvalue()),new_native_integral_or_PID_jobs=False)))


if __name__=="__main__":
    main()
