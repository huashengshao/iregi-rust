"""Freeze private metadata inputs and commands only; never invokes a compiler."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,json,shutil
ROOT=Path.cwd();HERE=ROOT/'target/native-f64-opt-in/qualification'
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def save(path,obj):
    with Path(path).open('x')as stream:stream.write(json.dumps(obj,indent=2)+'\n')
closure=ROOT/'target/e6-direct-n2/preparation.json';supplement=ROOT/'target/core-fused-cse-census/supplemental-deps.json'
assert sha(closure)=='8a3fe8b1000030cb3ccdcc65ea3c63b6598ce5857aafb5111637b04095a61c2e'
assert sha(supplement)=='1a08840ef5b9fc30a0fd44e84415bf08bf7281c82e8f2cef2378ba54f9fab75d'
inputs={ROOT/row['frozen']:row['sha256']for source in [closure,supplement]for row in read(source)['files']}
for path in [closure,supplement,ROOT/'target/core-fused-cse-census/thiserror-metadata.txt',ROOT/'target/core-fused-cse-census/thiserror-cargo-fingerprint.json']:
    inputs[path]=sha(path)
base=ROOT/'target/native-f64-opt-in';base_manifest=read(base/'base-manifest.json');review=read(base/'source-review-ready.json')
assert sha(base/'base-manifest.json')==review['base_manifest_sha256']
expected={**base_manifest['source_sha256'],**{row['path']:row['proposed_sha256']for row in review['changes']}}
for relative,digest in expected.items():
    path=HERE/'public-source'/relative;assert sha(path)==digest,relative
for tree in [HERE/'public-source']:
    for path in tree.rglob('*'):
        if path.is_file():inputs[path]=sha(path)
for relative in ['build.py','lifecycle.py','prepare_metadata.py','protocol.md']:
    path=HERE/relative;inputs[path]=sha(path)
    if path.suffix=='.py':ast.parse(path.read_text(),filename=str(path))
for relative in ['base-manifest.json','source-review-ready.json','proposed.patch']:
    path=base/relative;inputs[path]=sha(path)
tools={}
for name in ['rustc','cc','ar','taskset']:
    path=Path(shutil.which(name)).resolve();tools[name]={'path':str(path),'sha256':sha(path)};inputs[path]=sha(path)
for path,digest in inputs.items():assert sha(path)==digest,str(path)
manifest={
 'status':'source-only-metadata-inputs-frozen-no-compiler-invoked',
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'base_project_head':base_manifest['project_head'],'source_review_sha256':sha(base/'source-review-ready.json'),
 'dependency_directory':'target/e6-direct-n2/deps','supplemental_directory':'target/core-fused-cse-census/supplemental-deps','native_directory':'target/e6-direct-n2/native',
 'dependency_scope':'Previously completed non-Python native-ELF debug closure; numerical dependencies unchanged. Their original optimization profiles are retained in the bound preparation. Old project master archive is not an extern and is replaced by each fresh private configuration.',
 'externs':{
  'symbolica':'target/e6-direct-n2/deps/libsymbolica-06e42762cabb77d9.rlib',
  'oneloop':'target/e6-direct-n2/deps/liboneloop-ad2b1eccf125afee.rlib',
  'serde':'target/e6-direct-n2/deps/libserde-b04ba25115fa19f8.rlib',
  'serde_json':'target/e6-direct-n2/deps/libserde_json-d657c5438f354a41.rlib',
  'thiserror':'target/core-fused-cse-census/supplemental-deps/libthiserror-0527e2191ec3561c.rlib'},
 'tools':tools,'input_sha256':{str(path):digest for path,digest in sorted(inputs.items())},
 'scope':{'metadata_only':True,'feature_configurations':['default','selective','broad','both'],'expected_rustc_invocations':16,'per_invocation_seconds':60,'aggregate_seconds':180,'cleanup_reserve_seconds':8,'compile_cpus':[20,21],'runtime_execution':False,'cargo':False,'dependency_rebuild':False,'production_mutations':False,'later_stages_require_separate_root_grants':True},
 'compiled_source_mapping':expected,
 'fixtures':{str(path.relative_to(HERE/'public-source')):sha(path)for path in (HERE/'public-source/validation').rglob('*')if path.is_file()},
}
for name,path in manifest['externs'].items():assert ROOT/path in inputs,name
save(HERE/'metadata-preparation.json',manifest)
spec=importlib.util.spec_from_file_location('metadata_recipe',HERE/'build.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
commands=module.recipe('metadata',HERE/'metadata-build-001',manifest);assert len(commands)==16
save(HERE/'metadata-command-plan.json',{'preparation_sha256':sha(HERE/'metadata-preparation.json'),'status':'commands-only-not-executed','commands':commands})
print(json.dumps({'status':manifest['status'],'input_count':len(inputs),'preparation_sha256':sha(HERE/'metadata-preparation.json'),'commands_sha256':sha(HERE/'metadata-command-plan.json')}))
