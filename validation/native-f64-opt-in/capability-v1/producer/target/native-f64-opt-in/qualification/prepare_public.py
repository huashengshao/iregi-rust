"""Freeze the next public-source codegen recipe; no compiler or test execution."""
from pathlib import Path
import hashlib,importlib.util,json,datetime
ROOT=Path.cwd();HERE=ROOT/'target/native-f64-opt-in/qualification'
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def save(path,value):
    with Path(path).open('x')as stream:stream.write(json.dumps(value,indent=2)+'\n')
prior_path=HERE/'metadata-preparation.json';prior=read(prior_path)
assert sha(prior_path)=='30cb99984ef9362c6af70bb8d54a947541dc1457fc07618babfffa8a9b57c019'
result_path=HERE/'metadata-build-001/build.json';result=read(result_path)
assert sha(result_path)=='bbbab6c542c40fc517ca521b49d9961cebf46df702688000d5b23660dc42d671'
assert all(step['status']=='passed'for step in result['steps'][:8])
assert result['inputs_unchanged']is True and result['cleanup_errors']==[]
inputs={Path(path):value for path,value in prior['input_sha256'].items()}
for relative in ['metadata-preparation.json','metadata-command-plan.json','metadata-build-001/build.json','reviews/metadata-source-review.json','run_public_tests.py','reviews/runtime-lifecycle-source-review.json','prepare_public.py']:
    path=HERE/relative;inputs[path]=sha(path)
for path,value in inputs.items():assert sha(path)==value,str(path)
manifest={**prior,'status':'public-codegen-only-inputs-frozen-no-compiler-invoked','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':{'metadata_only':False,'feature_configurations':['default','selective'],'expected_rustc_invocations':8,'per_invocation_seconds':180,'aggregate_seconds':360,'cleanup_reserve_seconds':8,'compile_cpus':[20,21],'runtime_execution':False,'cargo':False,'dependency_rebuild':False,'production_mutations':False,'later_stages_require_separate_root_grants':True},
 'prior_metadata_receipt':{'path':str(result_path),'sha256':sha(result_path),'default_selective_checks_passed':8,'broad_metadata':'60s timeout; subsequent7broad/bothchecks unrun; compatibility remains incomplete'},
 'input_sha256':{str(path):value for path,value in sorted(inputs.items())}}
save(HERE/'preparation.json',manifest)
spec=importlib.util.spec_from_file_location('public_recipe',HERE/'build.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
commands=module.recipe('public',HERE/'public-build-001',manifest);assert len(commands)==8
save(HERE/'public-command-plan.json',{'preparation_sha256':sha(HERE/'preparation.json'),'status':'commands-only-not-executed','commands':commands})
print(json.dumps({'status':manifest['status'],'inputs':len(inputs),'preparation_sha256':sha(HERE/'preparation.json'),'commands_sha256':sha(HERE/'public-command-plan.json')}))
