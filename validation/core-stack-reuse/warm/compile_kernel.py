from pathlib import Path
import hashlib,json,subprocess,sys,time
root=Path.cwd();base=root/'target/core-stack-reuse';private=base/'deps';shared=root/'target/cargo-build/debug/deps';variant=sys.argv[1]
assert variant in ['baseline','candidate']
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
source=base/variant/'crates/iregi-rust/examples/kernel_benchmark.rs'
extern={'iregi_rust':base/variant/'libiregi_rust.rlib','symbolica':private/'libsymbolica-5cca42ee48491872.rlib','iregi_masters':private/'libiregi_masters-0d5459afd211649c.rlib','serde_json':private/'libserde_json-3b583d0e8aa0facc.rlib','serde':private/'libserde-fc3dcd4b8c210596.rlib'}
command=['taskset','-c','18' if variant=='baseline' else '19','rustc','--edition=2024',str(source),'-C','opt-level=2','-L',f'dependency={private}','-L',f'dependency={shared}','-L',f'native={root}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
for name,path in extern.items():command+=['--extern',f'{name}={path}']
command+=['-o',str(base/variant/'kernel_benchmark')]
record={'command':command,'source_sha256':sha(source),'extern_before':{str(p):sha(p) for p in extern.values()}}
start=time.monotonic()
with (base/variant/'kernel-compile.log').open('w') as log:code=subprocess.call(command,stdout=log,stderr=subprocess.STDOUT)
record.update(exit_code=code,elapsed_seconds=time.monotonic()-start,extern_after={str(p):sha(p) for p in extern.values()})
assert record['extern_before']==record['extern_after']
if code==0:record['binary_sha256']=sha(base/variant/'kernel_benchmark')
(base/variant/'kernel-compile.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['exit_code','elapsed_seconds']}),flush=True)
if code:print((base/variant/'kernel-compile.log').read_text()[-12000:],flush=True)
raise SystemExit(code)
