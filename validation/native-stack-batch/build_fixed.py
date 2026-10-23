from pathlib import Path
import os, sys, subprocess, json, hashlib, time
root=Path.cwd();base=root/'target/native-stack-batch';fam=sys.argv[1];assert fam in ['a0','b0','db0','c0','d0']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (base/f'fixed-{fam}-build.json').exists(),'preserve existing fixed-protocol build before retry'
source=base/f'probe-fixed-{fam}-source.rs';source.write_bytes((base/'probe-fixed.rs').read_bytes())
extern={'oneloop':base/'deps/liboneloop-8562c3cbbf948c0e.rlib','symbolica':base/'deps/libsymbolica-5cca42ee48491872.rlib','iregi_masters':base/'deps/libiregi_masters-0d5459afd211649c.rlib'}
args=['taskset','-c','20,21','rustc','--edition=2024','--crate-name',f'native_stack_fixed_{fam}','--cfg',f'family_{fam}','--cfg','timing_only',str(source),'-C','opt-level=3','-C','codegen-units=16','-C',f'metadata=native_stack_fixed_{fam}','-L',f'dependency={base}/deps','-L',f'dependency={root}/target/cargo-build/debug/deps','-L',f'native={root}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
for name,p in extern.items():args+=['--extern',f'{name}={p}']
args+=['-o',str(base/f'probe-fixed-{fam}')]
sources=[source,*(base/fam).glob('*.rs')];records={str(p.relative_to(root)):sha(p) for p in [*sources,*extern.values()]}
toolchain=subprocess.check_output(['rustc','-vV'],text=True)
start=time.monotonic()
with (base/f'fixed-{fam}-build.log').open('w') as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
changed=[str(p.relative_to(root)) for p in [*sources,*extern.values()] if sha(p)!=records[str(p.relative_to(root))]]
report={'protocol':'fixed-loop-v2','qualification_domains':['f64'],'layout_difference':'f64-only monomorphization; original all-domain binary retained separately','rustc_version_verbose':toolchain,'command':args,'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-start,'inputs':records,'changed':changed}
if not r.returncode:report['binary_sha256']=sha(base/f'probe-fixed-{fam}')
(base/f'fixed-{fam}-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['command','inputs']}),flush=True)
if r.returncode:print((base/f'fixed-{fam}-build.log').read_text())
sys.exit(r.returncode)
