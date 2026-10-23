from pathlib import Path
import os,sys,subprocess,json,hashlib,time
root=Path.cwd();base=root/'target/native-shared-binary';deps=root/'target/native-stack-batch/deps'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (base/'probe-build.json').exists(),'preserve prior attempt'
extern={'oneloop':deps/'liboneloop-8562c3cbbf948c0e.rlib','symbolica':deps/'libsymbolica-5cca42ee48491872.rlib','iregi_masters':deps/'libiregi_masters-0d5459afd211649c.rlib'}
args=['taskset','-c','20,21','rustc','--edition=2024','--crate-name','native_shared_binary_probe',str(base/'probe.rs'),'-C','opt-level=3','-C','codegen-units=16','-C','metadata=native_shared_binary_probe','-L',f'dependency={deps}','-L',f'dependency={root}/target/cargo-build/debug/deps','-L',f'native={root}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
for name,path in extern.items():args+=['--extern',f'{name}={path}']
args+=['-o',str(base/'probe')]
inputs=[base/'probe.rs',base/'shared_binary_kernel.rs',base/'kernel_controls.rs',*[p for fam in ['b0','c0','fixture'] for p in (base/fam).glob('*.rs')],*extern.values()]
before={str(p.relative_to(root)):sha(p) for p in inputs};start=time.monotonic();toolchain=subprocess.check_output(['rustc','-vV'],text=True)
with (base/'probe-build.log').open('w') as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
report={'scope':'Combined B0/C0 f64, DoubleFloat, Float256 qualification and optional f64 paired benchmark; no D0','command':args,'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-start,'inputs':before,'changed':[str(p.relative_to(root)) for p in inputs if sha(p)!=before[str(p.relative_to(root))]],'rustc_version_verbose':toolchain}
if r.returncode==0:report['binary_sha256']=sha(base/'probe')
(base/'probe-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['command','inputs']}),flush=True)
if r.returncode:print((base/'probe-build.log').read_text())
raise SystemExit(r.returncode)
