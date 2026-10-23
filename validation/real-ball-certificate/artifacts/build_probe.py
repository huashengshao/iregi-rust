from pathlib import Path
import argparse,hashlib,json,os,subprocess,time
root=Path.cwd();out=root/'target/real-ball-certificate';p=argparse.ArgumentParser();p.add_argument('variant',choices=['profile','candidate','tests']);a=p.parse_args();stem={'profile':'profile_probe','candidate':'candidate_probe','tests':'certificate_tests'}[a.variant]
source=out/(stem+'.rs');binary=out/stem
D=root/'target/benchmark/workspace-builds/80949db-default-resume/deps';deps=root/'target/optimized/cargo-build/release/deps'
externs={'iregi_rust':D/'libiregi_rust-b16ff118efb36669.rlib','iregi_masters':D/'libiregi_masters-736462b347335a0f.rlib','symbolica':D/'libsymbolica-2ae1abcc9fd9c0db.rlib','serde_json':deps/'libserde_json-d5ce7f4fcf58bd84.rlib'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
argv=['rustc','--crate-name',stem,'--edition=2024','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-C','embed-bitcode=yes',str(source),'-L',f'dependency={D}','-L',f'dependency={deps}','-L',f'native={root}/target/optimized/cargo-build/release/build/gmp-mpfr-sys-e9fd89ef30e561a9/out/lib']
if a.variant=='tests':argv+=['--test']
for k,v in externs.items():argv+=['--extern',f'{k}={v}']
argv+=['-o',str(binary)]
files=[source,out/'profiled.rs',out/'candidate.rs',Path(__file__)]
meta=dict(status='compiling',command=argv,cpu_affinity=sorted(os.sched_getaffinity(0)),source_sha256={str(p.relative_to(root)):sha(p) for p in files},extern_sha256={str(v.relative_to(root)):sha(v) for v in externs.values()},parent_build='target/benchmark/workspace-builds/80949db-default-resume/workspace-build-recovered.json',lto_note='Retained release archives contain LLVM bitcode; matching thinLTO required by linker.')
manifest=out/(stem+'-build.json');save=lambda:manifest.write_text(json.dumps(meta,indent=2)+'\n');save();t=time.monotonic()
with (out/(stem+'-build.log')).open('w') as log:r=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,CARGO_CRATE_NAME=stem))
meta.update(returncode=r.returncode,wall_seconds=time.monotonic()-t,status='compiled' if r.returncode==0 else 'failed',sources_unchanged=all(sha(root/p)==s for p,s in meta['source_sha256'].items()),archives_unchanged=all(sha(root/p)==s for p,s in meta['extern_sha256'].items()))
if r.returncode==0:meta['binary_sha256']=sha(binary)
save();print(json.dumps({k:meta[k] for k in ['status','returncode','wall_seconds','sources_unchanged','archives_unchanged']}));raise SystemExit(r.returncode)
