from pathlib import Path
import hashlib,json,os,subprocess,time
root=Path.cwd();base=root/'target/core-stack-adoption';snapshot=base/'snapshot';manifest=snapshot/'crates/iregi-rust';src=manifest/'src/lib.rs'
private=root/'target/core-stack-reuse/deps';shared=root/'target/cargo-build/debug/deps'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
prepared=json.loads((root/'target/core-stack-reuse/preparation.json').read_text())
for e in prepared['archives']: assert sha(Path(e['retained']))==e['sha256']
extern={
 'iregi_masters':private/'libiregi_masters-0d5459afd211649c.rlib',
 'symbolica':private/'libsymbolica-5cca42ee48491872.rlib',
 'serde':private/'libserde-fc3dcd4b8c210596.rlib',
 'serde_json':private/'libserde_json-3b583d0e8aa0facc.rlib',
 'thiserror':private/'libthiserror-b877110d28821624.rlib',
}
out=base/'core_tests'
command=['taskset','-c','18','rustc','--crate-name','iregi_rust','--edition=2024','--test',str(src),'-C','opt-level=2','-C','metadata=core_stack_production_adoption','-L',f'dependency={private}','-L',f'dependency={shared}','-L',f'native={root}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
for name,path in extern.items():command+=['--extern',f'{name}={path}']
command+=['-o',str(out)]
env=os.environ.copy();env.update(CARGO_CRATE_NAME='iregi_rust',CARGO_MANIFEST_DIR=str(manifest))
files=sorted(p for p in snapshot.rglob('*') if p.is_file())
record={'command':command,'environment':{k:env[k] for k in ['CARGO_CRATE_NAME','CARGO_MANIFEST_DIR']},'source_before':{str(p.relative_to(snapshot)):sha(p) for p in files},'extern_before':{str(p):sha(p) for p in extern.values()},'rustc':subprocess.check_output(['rustc','--version','--verbose'],text=True),'runner_sha256':sha(Path(__file__))}
start=time.monotonic()
with (base/'compile.log').open('w') as log:code=subprocess.call(command,env=env,stdout=log,stderr=subprocess.STDOUT)
record.update(exit_code=code,elapsed_seconds=time.monotonic()-start,source_after={str(p.relative_to(snapshot)):sha(p) for p in files},extern_after={str(p):sha(p) for p in extern.values()})
assert record['source_before']==record['source_after'];assert record['extern_before']==record['extern_after']
if code==0:record['binary_sha256']=sha(out)
(base/'compile.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['exit_code','elapsed_seconds']}),flush=True)
if code:print((base/'compile.log').read_text()[-20000:],flush=True)
raise SystemExit(code)
