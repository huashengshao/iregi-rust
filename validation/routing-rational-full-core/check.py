"""Portable source/result verification and saved-data-only numeric checks."""
from pathlib import Path
from decimal import localcontext
import hashlib
import json
import tarfile

HERE=Path(__file__).resolve().parent
def require(value,message):
    if not value:raise ValueError(message)
q=json.loads((HERE/"qualification.json").read_text())
archive=HERE/q["archive"]["path"]
require(hashlib.sha256(archive.read_bytes()).hexdigest()==q["archive"]["sha256"],"archive digest differs")
with tarfile.open(archive,"r:gz") as tf:
    entries=tf.getmembers()
    require(all(e.isfile() and not e.name.startswith("/") and ".." not in Path(e.name).parts for e in entries),"unexpected archive member type/path")
    require(len(entries)==len({e.name for e in entries}),"duplicate archive member")
    payload={e.name:tf.extractfile(e).read() for e in entries}
require(set(payload)==set(q["payload_sha256"]),"closed payload inventory differs")
for name,data in payload.items():require(hashlib.sha256(data).hexdigest()==q["payload_sha256"][name],"payload changed "+name)
require(q["status"]=="partial-private-full-core-qualification" and q["performance_qualified"] is False and q["dual_qualified"] is False and q["current_cargo_qualified"] is False,"qualification scope differs")
review=q["independent_final_review"]
require(hashlib.sha256(payload[review["path"]]).hexdigest()==review["sha256"] and json.loads(payload[review["path"]])["status"]==review["expected_status"],"independent partial audit differs")
# Execute only the already hashed standalone saved-data module. Its __main__
# block is disabled; it imports Python's standard library and no Rust/Fortran.
source="target/routing-rational-full-core/continuation-v3/compare.py"
namespace={"__name__":"saved_data_capsule_comparator"}
exec(compile(payload[source],source,"exec"),namespace)
def read(name):return json.loads(payload[name])
for name,case in q["passed_cases"].items():
    fixture=read(case["fixture"])
    settings=next(c for c in fixture["cases"] if c["id"]==name)
    with localcontext() as context:
        context.prec=170
        result=namespace["compare"](fixture,settings,read(case["capture"]),read(case["reference"]))
    require(result==case["result"]==read(case["comparison"]),"saved numeric reconstruction differs "+name)
require(set(q["failed_cases"])=={"n7_dot0"} and q["unrun_cases"]==["n7_hminus1"] and set(q["baseline_cases"].values())=={"unrun"},"failure/unrun inventory differs")
print(json.dumps(dict(status="passed",payloads=len(payload),completed_cases=list(q["passed_cases"]),failed_cases=list(q["failed_cases"]),unrun_cases=q["unrun_cases"],performance_qualified=False)))
