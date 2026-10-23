from pathlib import Path
import hashlib,json,subprocess,time,os
root=Path.cwd();base=root/'target/native-dense-span';deps=root/'target/native-stack-batch/deps'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
extern={'oneloop':deps/'liboneloop-8562c3cbbf948c0e.rlib','symbolica':deps/'libsymbolica-5cca42ee48491872.rlib'}
inputs=[base/'generate.rs',*[p for variant in ['baseline','candidate'] for p in (base/variant).rglob('*.rs')],*extern.values()];before={str(p.relative_to(root)):sha(p) for p in inputs}
args=['taskset','-c','20,21','rustc','--edition=2024','--crate-name','native_dense_generator',str(base/'generate.rs'),'-C','opt-level=1','-C','codegen-units=16','-C','metadata=native_dense_generator','-L',f'dependency={deps}','-L',f'dependency={root}/target/cargo-build/debug/deps','-L',f'native={root}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
for name,path in extern.items():args+=['--extern',f'{name}={path}']
args+=['-o',str(base/'generate')];env=os.environ.copy();env['CARGO_CRATE_NAME']='iregi_masters';start=time.monotonic()
with (base/'generator-build.log').open('w') as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,env=env)
report={'environment':{'CARGO_CRATE_NAME':'iregi_masters'},'command':args,'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-start,'inputs':before,'changed':[str(p.relative_to(root)) for p in inputs if sha(p)!=before[str(p.relative_to(root))]]}
if r.returncode==0:report['binary_sha256']=sha(base/'generate')
(base/'generator-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['command','inputs']}),flush=True)
if r.returncode:print((base/'generator-build.log').read_text())
raise SystemExit(r.returncode)
