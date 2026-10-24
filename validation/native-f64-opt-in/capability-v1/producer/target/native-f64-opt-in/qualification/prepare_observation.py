"""Freeze reviewed observation-only source/closure and commands; no compilation."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,json,shutil
ROOT=Path.cwd();HERE=ROOT/'target/native-f64-opt-in/qualification'
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def save(path,value):
    with Path(path).open('x')as stream:stream.write(json.dumps(value,indent=2)+'\n')
prior_path=HERE/'preparation.json';prior=read(prior_path)
assert sha(prior_path)=='157477b5ea67e01d7d89df18c8263710c6b9953b9b00c0f91067022375f2279f'
inputs={Path(path):value for path,value in prior['input_sha256'].items()}
source=HERE/'source';overlay=source/'observation-overlay/crates';public=HERE/'public-source/crates'
changes=[]
for original in public.rglob('*'):
    if original.is_file():
        relative=original.relative_to(public);copied=overlay/relative
        assert copied.is_file(),str(relative)
        if sha(original)!=sha(copied):changes.append(str(relative))
added=[str(path.relative_to(overlay))for path in overlay.rglob('*')if path.is_file()and not(public/path.relative_to(overlay)).exists()]
assert sorted(changes)==['iregi-masters/src/lib.rs','iregi-rust/src/execution.rs','iregi-rust/src/lib.rs']
assert added==['iregi-rust/src/master_capture.rs']
assert sha(overlay/added[0])==sha(ROOT/'validation/selected-native-reduction/source/master_capture.rs')=='616cf5840097d28d691b35b874fdcbe8b01600461b3a0637345a6715db1bb95b'
for path in source.rglob('*'):
    if path.is_file():inputs[path]=sha(path)
for line in (source/'SOURCE-SHA256SUMS').read_text().splitlines():
    expected,relative=line.split(maxsplit=1);path=ROOT/relative;assert path.is_relative_to(source);assert sha(path)==expected,relative
inventory=HERE/'control-inventory.json'
assert not inventory.exists();shutil.copyfile(ROOT/'target/selected-native-optimized/control-inventory.json',inventory)
local=['build_observation.py','run_whole.py','interactive.py','validate_whole.py','admission.py','prepare_observation.py','control-inventory.json',
       'preparation.json','public-command-plan.json','public-build-001/build.json','public-tests-001/results.json','public-tests-001/independent-admission.json',
       'reviews/public-codegen-source-review.json','reviews/public-tests-validator-source-review.json','reviews/public-tests-001-independent-audit.json']
for name in local:
    path=HERE/name;inputs[path]=sha(path)
    if path.suffix=='.py':ast.parse(path.read_text(),filename=str(path))
external=['validation/native-master-replay/inputs.json','validation/benchmark/run.py','target/benchmark/reference-build.json','target/benchmark/iregi-benchmark',
          'validation/selected-native-reduction/source/master_capture.rs','target/selected-native-optimized/control-inventory.json']
for name in external:path=ROOT/name;inputs[path]=sha(path)
assert sha(ROOT/external[0])=='65d0d2fd554807478569ac88b6d689c9132ce541e98cfb2a3a55b8ef98e5c7ef'
assert sha(ROOT/external[1])=='22488d58c1cbed9520728f62efa67f98250cffdef8b88ec8b85cc72b9b99e6b7'
assert sha(ROOT/external[2])=='488782471657193e0e09f69c283cb82d8534577bb4fccd23f3087192c0f2f782'
assert sha(ROOT/external[3])=='4c2241f6dd557db4e9348f0fd397484a72d71f83b953a6efc8010c61d1bdd389'
for path,value in inputs.items():assert sha(path)==value,str(path)
manifest={**prior,'status':'observation-codegen-inputs-frozen-no-compiler-invoked','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':{'metadata_only':False,'feature_configurations':['selective'],'expected_rustc_invocations':3,'per_invocation_seconds':180,'aggregate_seconds':180,'cleanup_reserve_seconds':8,'compile_cpus':[20,21],'runtime_execution':False,'cargo':False,'dependency_rebuild':False,'production_mutations':False,'later_stages_require_separate_root_grants':True},
 'observation_overlay':{'changed_files':changes,'added_files':added,'capture_module_sha256':sha(overlay/added[0]),'generated_arithmetic_changes':False,'production_patch_changes':False,'purpose':'cfg-gated observation only; public source unit qualification separately passed'},
 'whole_inputs':'validation/native-master-replay/inputs.json','reference':{'path':'target/benchmark/iregi-benchmark','sha256':sha(ROOT/'target/benchmark/iregi-benchmark'),'build_manifest':'target/benchmark/reference-build.json','build_manifest_sha256':sha(ROOT/'target/benchmark/reference-build.json')},
 'runtime_protocol':{'status':'prepared-but-not-authorized','requests':38,'whole_families':8,'controls_responses':2,'invalid_timing_request_controls':4,'total_cap_seconds':120,'cpu':22,'same_process_own_repeats':True,'historical_numeric_bitgate':False,'kernel_timing':False},
 'input_sha256':{str(path):value for path,value in sorted(inputs.items())}}
save(HERE/'observation-preparation.json',manifest)
spec=importlib.util.spec_from_file_location('observation_recipe',HERE/'build_observation.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
commands=module.recipe('observation',HERE/'observation-build-001',manifest);assert len(commands)==3
save(HERE/'observation-command-plan.json',{'preparation_sha256':sha(HERE/'observation-preparation.json'),'status':'commands-only-not-executed','commands':commands})
print(json.dumps({'status':manifest['status'],'inputs':len(inputs),'preparation_sha256':sha(HERE/'observation-preparation.json'),'commands_sha256':sha(HERE/'observation-command-plan.json')}))
