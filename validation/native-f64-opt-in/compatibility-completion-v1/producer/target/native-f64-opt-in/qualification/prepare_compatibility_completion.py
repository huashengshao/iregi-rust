"""Freeze only the two unfinished metadata calls; no compiler invocation."""
from pathlib import Path
import datetime,json
import build_compatibility_completion as b
ROOT=Path.cwd();Q=ROOT/'target/native-f64-opt-in/qualification'
old=Q/'compatibility-preparation.json';manifest=b.read(old);bindings=dict(manifest['input_sha256'])
retained=Q/'compatibility-build-001/both/libiregi_masters.rmeta'
assert b.sha(retained)=='b34c2f4d8cc40fec1f96a8935bcb3526b7738a9fe67f9f4561aaf036c332cc00'
for p in [old,Q/'build_compatibility_completion.py',Path(__file__).resolve(),Q/'compatibility-completion-proposal.md',Q/'compatibility-build-001/build.json',Q/'reviews/compatibility-build-001-independent-audit.json',retained,ROOT/'validation/native-f64-opt-in/compatibility-v1/manifest.json',ROOT/'validation/native-f64-opt-in/compatibility-v1/qualification.json']:
    bindings[str(p)]=b.sha(p)
for p,d in bindings.items():assert b.sha(p)==d,p
manifest.update(status='two-unfinished-metadata-calls-frozen-no-compiler-invoked',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope={'metadata_only':True,'feature_configurations':['both'],'expected_rustc_invocations':2,'master_tests_cap_seconds':210,'core_tests_cap_seconds':60,'aggregate_seconds':300,'cleanup_reserve_seconds':8,'compile_cpus':[20,21],'retained_successful_master_metadata':str(retained),'retained_master_sha256':b.sha(retained),'completed_calls_repeated':0,'runtime_execution':False,'cargo':False,'dependency_rebuild':False,'production_mutations':False,'stop_on_first_failure':True,'retry_authorized':False},input_sha256=bindings)
plan=Q/'compatibility-completion-command-plan.json';prep=Q/'compatibility-completion-preparation.json'
assert not plan.exists() and not prep.exists()
b.save(plan,{'scope':manifest['scope'],'steps':b.recipe(Q/'compatibility-completion-build-001',manifest)})
manifest['input_sha256'][str(plan)]=b.sha(plan);b.save(prep,manifest)
print(json.dumps({'preparation_sha256':b.sha(prep),'command_plan_sha256':b.sha(plan),'bound_inputs':len(manifest['input_sha256']),'runner_sha256':b.sha(Q/'build_compatibility_completion.py')}))
