"""Compile the private planar candidate against the complete6b24 closure."""
from pathlib import Path
import hashlib,json,os,subprocess,time

root=Path.cwd();base=root/'target/planar-counter-followup';source=base/'test-source'
closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds';deps=closure/'deps'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
manifest=json.loads((closure/'manifest.json').read_text())
completion=json.loads((closure/'workspace-completion.json').read_text())
assert completion['cargo_returncode']==0
assert completion['status']=='whole_workspace_build_completed_and_source_binaries_verified'
assert completion['dependency_closure_manifest_sha256']==sha(closure/'manifest.json')
records=manifest['files']+manifest['native_files']
for item in records:assert sha(Path(item['retained']))==item['sha256']
extern={
 'symbolica':'libsymbolica-2ae1abcc9fd9c0db.rlib',
 'iregi_masters':'libiregi_masters-736462b347335a0f.rlib',
 'oneloop':'liboneloop-6117c7de19c8681b.rlib',
 'serde':'libserde-bde6fd4136f3a6c8.rlib',
 'serde_json':'libserde_json-d5ce7f4fcf58bd84.rlib',
 'thiserror':'libthiserror-7d7ef35ea784c43a.rlib',
}
command=['taskset','--cpu-list','16,17','rustc','--test','--crate-name','iregi_rust',
 '--edition=2024','-C','opt-level=2','-C','lto=thin','-C','codegen-units=1',
 '-C','metadata=planar_counter_followup_01',str(source/'crates/iregi-rust/src/lib.rs'),
 '-L','dependency='+str(deps)]
for name,file in extern.items():command+=['--extern',name+'='+str(deps/file)]
for native in sorted({str(Path(item['retained']).parent) for item in manifest['native_files']}):
 command+=['-L','native='+native]
command+=['-o',str(base/'core-tests')]
env=os.environ.copy();env.update(CARGO_MANIFEST_DIR=str(source/'crates/iregi-rust'),CARGO_CRATE_NAME='iregi_rust')
hashes=lambda:{str(p.relative_to(source)):sha(p) for p in sorted(source.rglob('*')) if p.is_file()}
record={'command':command,'environment':{k:env[k] for k in ('CARGO_MANIFEST_DIR','CARGO_CRATE_NAME')},
 'cpu_affinity':[16,17],'source_hashes':hashes(),
 'dependencies':{name:{'path':str(deps/file),'sha256':sha(deps/file)} for name,file in extern.items()},
 'dependency_closure':str(closure),'closure_manifest_sha256':sha(closure/'manifest.json'),
 'workspace_completion_sha256':sha(closure/'workspace-completion.json'),
 'cargo_events_sha256':sha(closure/'cargo-library-events.json'),'closure_files':len(records),
 'profile':'Narrow18-test corrected receipt/accounting and checked-counter followup candidate, opt2 thinLTO codegen1 with coherent completed6b24 optimized dependency closure; correctness qualification only.',
 'runner_sha256':sha(Path(__file__)),'rustc':subprocess.check_output(['rustc','--version','--verbose'],text=True)}
assert not (base/'build.json').exists() and not (base/'build.log').exists()
start=time.monotonic()
with (base/'build.log').open('w') as log:
 result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=env)
record.update(exit_code=result.returncode,elapsed_seconds=time.monotonic()-start,source_hashes_after=hashes())
assert record['source_hashes']==record['source_hashes_after']
for item in records:assert sha(Path(item['retained']))==item['sha256']
record['all_closure_hashes_rechecked']=True
if result.returncode==0:record['binary_sha256']=sha(base/'core-tests')
(base/'build.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({key:record[key] for key in ('exit_code','elapsed_seconds','binary_sha256') if key in record}),flush=True)
if result.returncode:print((base/'build.log').read_text()[-12000:])
raise SystemExit(result.returncode)
