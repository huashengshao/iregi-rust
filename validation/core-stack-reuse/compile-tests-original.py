from pathlib import Path
import hashlib,json,os,subprocess,sys,time
root=Path.cwd();base=root/'target/core-stack-reuse';variant=sys.argv[1]
assert variant in ['baseline','candidate']
folder=base/variant;manifest=folder/'crates/iregi-rust';src=manifest/'src/lib.rs'
private=base/'deps';shared=root/'target/cargo-build/debug/deps'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
prepared=json.loads((base/'preparation.json').read_text())
for e in prepared['archives']: assert sha(Path(e['retained']))==e['sha256']
extern={
 'iregi_masters':private/'libiregi_masters-0d5459afd211649c.rlib',
 'symbolica':private/'libsymbolica-5cca42ee48491872.rlib',
 'serde':private/'libserde-fc3dcd4b8c210596.rlib',
 'serde_json':private/'libserde_json-3b583d0e8aa0facc.rlib',
 'thiserror':private/'libthiserror-b877110d28821624.rlib',
}
out=folder/'core_tests'
command=['taskset','-c','18' if variant=='baseline' else '19','rustc','--crate-name','iregi_rust','--edition=2024','--test',str(src),'-C','opt-level=2','-C',f'metadata=core_stack_reuse_{variant}','-L',f'dependency={private}','-L',f'dependency={shared}','-L',f'native={root}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
for name,path in extern.items():command+=['--extern',f'{name}={path}']
command+=['-o',str(out)]
env=os.environ.copy();env.update(CARGO_CRATE_NAME='iregi_rust',CARGO_MANIFEST_DIR=str(manifest))
files=sorted(p for p in folder.rglob('*') if p.is_file() and (p.suffix in ['.rs','.json'] or p.name=='Cargo.toml') and p.name!='compile.json')
before={str(p.relative_to(folder)):sha(p) for p in files}
record={'variant':variant,'command':command,'source_before':before,'extern_before':{str(p):sha(p) for p in extern.values()},'rustc':subprocess.check_output(['rustc','--version','--verbose'],text=True),'compiler_scope':'Instrumented proof builds opt2; compile-only, not performance benchmarks.','runner_sha256':sha(Path(__file__))}
start=time.monotonic()
with (folder/'compile.log').open('w') as log:code=subprocess.call(command,env=env,stdout=log,stderr=subprocess.STDOUT)
record.update(exit_code=code,elapsed_seconds=time.monotonic()-start,source_after={str(p.relative_to(folder)):sha(p) for p in files},extern_after={str(p):sha(p) for p in extern.values()})
assert record['source_before']==record['source_after'];assert record['extern_before']==record['extern_after']
if code==0:record['binary_sha256']=sha(out)
(folder/'compile.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['variant','exit_code','elapsed_seconds']}),flush=True)
if code:print((folder/'compile.log').read_text()[-12000:],flush=True)
sys.exit(code)
