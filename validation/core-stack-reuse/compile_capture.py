from pathlib import Path
import hashlib,json,os,subprocess,time
root=Path.cwd();base=root/'target/core-stack-reuse';private=base/'deps';shared=root/'target/cargo-build/debug/deps'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
extern={'baseline':base/'baseline/libiregi_rust.rlib','candidate':base/'candidate/libiregi_rust.rlib','symbolica':private/'libsymbolica-5cca42ee48491872.rlib','iregi_masters':private/'libiregi_masters-0d5459afd211649c.rlib','serde_json':private/'libserde_json-3b583d0e8aa0facc.rlib'}
command=['taskset','-c','18,19','rustc','--edition=2024',str(base/'capture.rs'),'-C','opt-level=2','-L',f'dependency={private}','-L',f'dependency={shared}','-L',f'native={root}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
for name,path in extern.items():command+=['--extern',f'{name}={path}']
command+=['-o',str(base/'capture')]
record={'command':command,'source_sha256':sha(base/'capture.rs'),'extern_before':{str(p):sha(p) for p in extern.values()}}
start=time.monotonic()
with (base/'capture-compile.log').open('w') as log:code=subprocess.call(command,stdout=log,stderr=subprocess.STDOUT)
record.update(exit_code=code,elapsed_seconds=time.monotonic()-start,extern_after={str(p):sha(p) for p in extern.values()})
assert record['extern_before']==record['extern_after']
if code==0:record['binary_sha256']=sha(base/'capture')
(base/'capture-compile.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['exit_code','elapsed_seconds']}),flush=True)
if code:print((base/'capture-compile.log').read_text()[-16000:],flush=True)
raise SystemExit(code)
