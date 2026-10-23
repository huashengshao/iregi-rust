#!/usr/bin/env python3
"""Review retained exact certificates and bind compact coverage to source archives."""
import gzip
import hashlib
import io
import json
from fractions import Fraction
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_run(stem):
    output=HERE/f"{stem}.json"; run=HERE/f"{stem}-run.json"; log=HERE/f"{stem}.log"
    data=json.loads(output.read_text()); record=json.loads(run.read_text())
    assert record["exit_code"]==0 and not record["timed_out"] and record["inputs_unchanged"]
    assert record["sha256_before"]==record["sha256_after"]
    build_path=ROOT/record["build_manifest"]
    assert sha(build_path)==record["build_manifest_sha256"]
    build=json.loads(build_path.read_text())
    assert all(record["sha256_before"][p]==v for p,v in build["sha256"].items())
    assert sha(output)==record["output_sha256"] and sha(log)==record["log_sha256"]
    successful=0
    if "numeric" in data:
        numeric=data["numeric"]
        for lane in numeric["lanes"]:
            if lane["status"]!="Success":
                assert lane["values"] is None
                continue
            assert len(lane["values"])==len(data["shape"])
            for value,bound in zip(lane["values"],lane["bounds"]):
                assert Fraction(value["certified_error_squared_upper"])<=Fraction(value["allowed_squared"])
                assert Fraction(bound["maximum_error_squared"])<=Fraction(bound["allowed_error_squared"])
                successful+=1
        statuses={x["name"]:x["status"] for x in numeric["lanes"]}
        extra={"shape":data["shape"],"lane_statuses":statuses,"batch_execution":numeric["batch_execution"],
          "overlap_requested_bits":24,"overlap_status":numeric["overlap_status"],"overlap_components":len(numeric["overlap_components"])}
    else:
        numeric=data
        for row in data["rows"]:
            if row["status"]!="Success":
                assert row["values"] is None
                assert row["status"]=="UncertifiedComponent(6)"
                assert all(Fraction(x)==0 for x in row["tail_bounds"][:6])
                assert Fraction(row["tail_bounds"][6])>0
                continue
            assert len(row["values"])==len(data["shape"])
            for value in row["values"]:
                error=value.get("exact_error_squared",value.get("oracle_error_squared_upper"))
                assert Fraction(error)<=Fraction(value["allowed_error_squared"])
                if "certificate_error_squared_upper" in value:
                    assert Fraction(value["certificate_error_squared_upper"])<=Fraction(value["allowed_error_squared"])
                successful+=1
        extra={"shape":data["shape"],"lane_statuses":[x["status"]for x in data["rows"]],
          "numeric_batch_calls":data["numeric_batch_calls"]}
        if "static_dynamic_component_container_equivalence" in data:
            extra["static_dynamic_component_container_equivalence"]=data["static_dynamic_component_container_equivalence"]
        if "mass_offsets" in data:extra["mass_offsets"]=data["mass_offsets"]
    return {"label":stem,"status":data["status"],"working_bits":numeric["working_bits"],"requested_bits":numeric["requested_bits"],
      "successful_components_independently_certified":successful,**extra,
      "diagnostic_wall_seconds":record["diagnostic_wall_seconds"],
      "artifacts":{str(p.relative_to(ROOT)):sha(p) for p in [output,run,log]},"build_manifest":record["build_manifest"]}

def archive_sources(manifest):
    build=json.loads(manifest.read_text()); paths=[p for p in build["sha256"] if p.endswith(".rs")]
    payload=io.BytesIO()
    with gzip.GzipFile(fileobj=payload,mode="wb",mtime=0) as compressed:
        with tarfile.open(fileobj=compressed,mode="w") as archive:
            for path in sorted(paths):
                source=ROOT/path
                assert sha(source)==build["sha256"][path]
                name=str(Path(path).relative_to(Path(path).parents[1] if "/support/" in path else Path(path).parent))
                content=source.read_bytes(); info=tarfile.TarInfo(name); info.size=len(content);info.mtime=0;info.mode=0o644
                archive.addfile(info,io.BytesIO(content))
    destination=HERE/"source-archives"/(manifest.stem.removesuffix("-build")+".tar.gz")
    destination.parent.mkdir(exist_ok=True); destination.write_bytes(payload.getvalue())
    return {"build_manifest":str(manifest.relative_to(ROOT)),"build_manifest_sha256":sha(manifest),
      "source_archive":str(destination.relative_to(ROOT)),"source_archive_sha256":sha(destination),
      "source_sha256":{p:build["sha256"][p]for p in paths}}

def main():
    stems=[]
    for shape in ["primal","mixed"]:
        for kind,bits in [("f64",40),("dd",80),("float128",100),("float256",128)]:
            stems.append(f"n4-current3-{shape}-{kind}-{bits}")
    stems += [f"n2-current3-{shape}-float256-128"for shape in ["primal","mixed"]]
    stems += [f"n{order}-heterogeneous3-float256-128"for order in [2,4]]
    stems += [f"n4-unequal3-{kind}-{bits}"for kind,bits in [("dd",80),("float128",100),("float256",128)]]
    stems += ["n4-current4-mixed-float256-128","n4-heterogeneous4-float256-128","n4-unequal4-float256-128"]
    cases=[verify_run(stem)for stem in stems]
    archives=[archive_sources(HERE/f"{variant}-build.json")for variant in ["stage1","profile","rational","oracle","current3","heterogeneous3","unequal3","current4","heterogeneous4","unequal4"]]
    for variant in ["current4","heterogeneous4","unequal4"]:
        build=json.loads((HERE/f"{variant}-build.json").read_text())
        for path,digest in build["sha256"].items():
            if path.endswith(".rs"):
                suffix=path.split(f"stage-{variant}-source/",1)[1]
                assert sha(ROOT/"crates/iregi-rust/examples"/suffix)==digest
    historical=[]
    for run in sorted(HERE.glob("*-run.json")):
        if run.stem.removesuffix("-run") in stems:continue
        data=json.loads(run.read_text())
        historical.append({"artifact":str(run.relative_to(ROOT)),"sha256":sha(run),"timed_out":data["timed_out"],"exit_code":data["exit_code"],"output":data["output"]})
    result={"status":"validation_only_near_vacuum_candidate_qualified_for_selected_families","production_changed":False,
      "scope":"N2/N4 finite D0 candidate; explicit per-component mixed absolute/relative accuracy; successful lanes checked against independent exact rational series or exact differentiated-integrand oracle. No generalD0/E6 production or performance parity claim.",
      "source_scope":"Current4/heterogeneous4/unequal4 snapshots match live Rust sources. They differ from respective3 snapshots only in formatting one existing map_coeff chain; fresh Float256 checks cover allthree final binaries. Retained baseline nofeatures oneloop Expression DNS and pre-default-stack Symbolica archives remain explicit.",
      "numeric_api":"NativeFloat scalar components plus explicit Symbolica Dualizer shapes; sample lanes remain distinct. Static/dynamic carrier equivalence covers component containers and shape extraction, not a new standalone Dual-carrier public master API.",
      "qualified_cases":cases,"source_archives":archives,"historical_attempts_retained":historical,
      "input_integrity":"Unequal masses M+[-1,0,1,2]eta ateta2^-64 remain exactlyrepresented/distinct inDD,Float128,Float256; independentoracle expandsaroundM, candidatearoundM-eta.",
      "rejection_integrity":"Invalidphysicaldomain/radius lanes, unattainableaccuracy, insufficientmixedtails, andN2 exactvacuum thirdderivative expose noresultvalues. Retained history includes preparationtimeouts andinitialresourcecapfailure.",
      "review":"Independent source/math review of candidate, common/unequal series oracle and exactvacuum derivative oracle; machine review rechecks everyreported successful error bound, retainedrejections, build/source hash mappings and output/logdigests.",
      "remaining":["independent parameter quadrature and highprecision finite-difference expansion beyond selected identities","production D0 integration with explicit requestedaccuracy and finitecomponent certificates","E6 certificate propagation and original-fixture public rerun","fullrequested256bit convergence/higher boundedorders","performance gates and memory/allocation optimization"],
      "timing_scope":"All times diagnostic only. Some correctness processes ran concurrently onCPU4/5; no timing comparisons or parity conclusions are drawn."}
    destination=HERE/"qualification.json"
    destination.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"qualification_sha256":sha(destination),"runs":len(cases),"certified_components":sum(x['successful_components_independently_certified']for x in cases)}))

if __name__=="__main__":main()
