"""Freeze a distinct eight-call metadata recipe without invoking rustc."""
from pathlib import Path
import datetime,json
import build_compatibility as b
ROOT=Path.cwd();Q=ROOT/'target/native-f64-opt-in/qualification'
old=Q/'preparation.json';manifest=b.read(old)
bindings=dict(manifest['input_sha256'])
for p in [old,Q/'build_compatibility.py',Path(__file__).resolve(),Q/'compatibility-protocol.md',Q/'metadata-build-001/build.json',Q/'public-build-001/build.json',Q/'whole-qualification-001/independent-evidence-review.json',ROOT/'validation/native-f64-opt-in/capability-v1/manifest.json',ROOT/'validation/native-f64-opt-in/capability-v1/qualification.json']:
    bindings[str(p)]=b.sha(p)
for p,d in bindings.items():assert b.sha(p)==d,p
manifest.update(status='compatibility-metadata-frozen-no-compiler-invoked',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope={'metadata_only':True,'feature_configurations':['broad','both'],'expected_rustc_invocations':8,'masters_and_master_tests_cap_seconds':180,'core_and_core_tests_cap_seconds':60,'aggregate_seconds':600,'cleanup_reserve_seconds':8,'compile_cpus':[20,21],'runtime_execution':False,'cargo':False,'dependency_rebuild':False,'production_mutations':False,'stop_on_first_failure':True,'retry_authorized':False},input_sha256=bindings)
plan=Q/'compatibility-command-plan.json';prep=Q/'compatibility-preparation.json'
assert not plan.exists() and not prep.exists()
b.save(plan,{'scope':manifest['scope'],'steps':b.recipe(Q/'compatibility-build-001',manifest)})
manifest['input_sha256'][str(plan)]=b.sha(plan)
b.save(prep,manifest)
print(json.dumps({'preparation_sha256':b.sha(prep),'command_plan_sha256':b.sha(plan),'bound_inputs':len(manifest['input_sha256']),'runner_sha256':b.sha(Q/'build_compatibility.py')}))
