from pathlib import Path
import hashlib,json,os,subprocess,time
root=Path.cwd();base=root/'target/cli-coefficient-cse-timing';closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds';deps=closure/'deps'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
prepared=json.loads((closure/'manifest.json').read_text())
closure_records=prepared['files']+prepared['native_files']
for item in closure_records: assert sha(Path(item['retained']))==item['sha256']
extern={
'symbolica':'libsymbolica-2ae1abcc9fd9c0db.rlib','iregi_masters':'libiregi_masters-736462b347335a0f.rlib',
'iregi_rust':'libiregi_rust-b16ff118efb36669.rlib','iregi_prepare':'libiregi_prepare-b6f3066dd631bcd7.rlib',
'serde':'libserde-bde6fd4136f3a6c8.rlib','serde_json':'libserde_json-d5ce7f4fcf58bd84.rlib'}
command=['taskset','-c','8,9','rustc','--edition=2024','--crate-name','cli_coefficient_cse_timing',str(base/'source/warm.rs'),'-C','opt-level=2','-C','lto=thin','-C','codegen-units=1','-C','metadata=cli_coefficient_cse_timing_private','-L',f'dependency={deps}','-L',f'native={closure}/build/gmp-mpfr-sys-e9fd89ef30e561a9/out/lib']
for name,file in extern.items(): command+=['--extern',f'{name}={deps/file}']
for native in sorted({str(Path(item['retained']).parent) for item in prepared['native_files']}): command+=['-L',f'native={native}']
command+=['-o',str(base/'probe')]
files=sorted((base/'source').glob('*.rs'));before={str(p.relative_to(base)):sha(p) for p in files}
record={'command':command,'source_before':before,'extern_before':{file:sha(deps/file) for file in extern.values()},'rustc':subprocess.check_output(['rustc','--version','--verbose'],text=True),'runner_sha256':sha(Path(__file__)),'dependency_closure_manifest_sha256':sha(closure/'manifest.json'),'dependency_events_sha256':sha(closure/'cargo-library-events.json'),'profile':'Private probe opt2 thinLTO codegen1 with coherent frozen6b24 completed-library closure; no whole-workspace performance-gate claim.'}
start=time.monotonic()
check_command=command[:-2]+['--emit=metadata','-o',str(base/'probe.rmeta')]
with (base/'check.log').open('w') as log: check_code=subprocess.call(check_command,stdout=log,stderr=subprocess.STDOUT)
record['check_command']=check_command;record['check_exit_code']=check_code
if check_code:
 (base/'compile.json').write_text(json.dumps(record,indent=2)+'\n')
 print((base/'check.log').read_text());raise SystemExit(check_code)
with (base/'compile.log').open('w') as log:code=subprocess.call(command,stdout=log,stderr=subprocess.STDOUT)
record.update(exit_code=code,elapsed_seconds=time.monotonic()-start,source_after={str(p.relative_to(base)):sha(p) for p in files},extern_after={file:sha(deps/file) for file in extern.values()})
assert before==record['source_after'];assert record['extern_before']==record['extern_after']
for item in closure_records: assert sha(Path(item['retained']))==item['sha256']
record['all_closure_hashes_rechecked']=True
if code==0: record['binary_sha256']=sha(base/'probe')
(base/'compile.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k] for k in ['exit_code','elapsed_seconds']}),flush=True)
if code:print((base/'compile.log').read_text()[-12000:]);raise SystemExit(code)
