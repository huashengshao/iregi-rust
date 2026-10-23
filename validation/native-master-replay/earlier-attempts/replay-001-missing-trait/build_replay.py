from pathlib import Path
import hashlib,json,subprocess,time
root=Path.cwd();base=root/'target/native-master-replay';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();prep=json.loads((base/'preparation.json').read_text())
assert not (base/'replay-build.json').exists(),'preserve prior compile attempt'
deps=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds/deps';native=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds/build/gmp-mpfr-sys-e9fd89ef30e561a9/out/lib'
names=['iregi_masters','oneloop','symbolica','serde_json'];inputs=[base/'source/replay.rs',*(base/'source/native').glob('*.rs')];before={str(p.relative_to(base)):sha(p) for p in inputs}
for name in names:assert sha(Path(prep['archives'][name]['path']))==prep['archives'][name]['sha256']
cmd=['taskset','-c','20,21','rustc','--edition=2024','--crate-name','actual_master_replay',str(base/'source/replay.rs'),'-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-C','metadata=actual_master_replay','-L',f'dependency={deps}','-L',f'native={native}']
for name in names:cmd+=['--extern',f'{name}={prep["archives"][name]["path"]}']
cmd+=['-o',str(base/'replay')];start=time.monotonic()
with (base/'replay-build.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
report={'scope':'Selected original A0/B0/C0 native versus Symbolica raw f64 kernels; no full feature/D0/core recompilation','command':cmd,'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-start,'sources_before':before,'sources_after':{str(p.relative_to(base)):sha(p) for p in inputs},'archives':{name:prep['archives'][name] for name in names},'rustc':subprocess.check_output(['rustc','-vV'],text=True)}
assert report['sources_before']==report['sources_after']
if r.returncode==0:report['binary_sha256']=sha(base/'replay')
(base/'replay-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['command','sources_before','sources_after','archives']}),flush=True)
if r.returncode:print((base/'replay-build.log').read_text()[-12000:])
raise SystemExit(r.returncode)
