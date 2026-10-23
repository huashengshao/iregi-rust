from pathlib import Path
import hashlib,json,os,subprocess,time
root=Path.cwd();base=root/'target/native-master-replay';prep=json.loads((base/'preparation.json').read_text());deps=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds/deps';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert not (base/'capture-build.json').exists(),'preserve previous build attempt'
for item in prep['archives'].values():assert sha(Path(item['path']))==item['sha256']
native=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds/build/gmp-mpfr-sys-e9fd89ef30e561a9/out/lib'
assert native.exists()
manifest=base/'core/crates/iregi-rust';env=os.environ.copy();env.update(CARGO_CRATE_NAME='iregi_rust',CARGO_MANIFEST_DIR=str(manifest))
sources=[p for p in (base/'core').rglob('*') if p.is_file()]+[base/'source/capture.rs'];before={str(p.relative_to(base)):sha(p) for p in sources}
commands=[];results=[]
for kind in ['core','capture']:
 src=manifest/'src/lib.rs' if kind=='core' else base/'source/capture.rs';out=base/('libiregi_rust_capture.rlib' if kind=='core' else 'capture')
 cmd=['taskset','-c','20,21','rustc','--edition=2024','--crate-name','iregi_rust' if kind=='core' else 'master_request_capture',str(src),'-C','opt-level=3','-C','codegen-units=1','-C',f'metadata=master_request_capture_{kind}','-L',f'dependency={deps}','-L',f'native={native}']
 if kind=='core':cmd+=['--crate-type','rlib']
 else:cmd+=['-C','lto=thin','--extern',f'iregi_rust={base}/libiregi_rust_capture.rlib']
 for name,item in prep['archives'].items():
  if kind=='core' and name in ['serde_json','oneloop']:continue
  cmd+=['--extern',f'{name}={item["path"]}']
 cmd+=['-o',str(out)];commands.append(cmd);start=time.monotonic()
 with (base/f'{kind}-build.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
 result={'kind':kind,'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-start,'command':cmd}
 if r.returncode==0:result['artifact_sha256']=sha(out)
 results.append(result);print(json.dumps({k:v for k,v in result.items() if k!='command'}),flush=True)
 if r.returncode:print((base/f'{kind}-build.log').read_text()[-14000:]);break
record={'scope':'Private current-core observational capture, frozen optimized default dependencies; no full workspace or native/D0 build','source_revision':prep['source_revision'],'sources_before':before,'sources_after':{str(p.relative_to(base)):sha(p) for p in sources},'archives_after':{name:sha(Path(item['path'])) for name,item in prep['archives'].items()},'stages':results,'rustc':subprocess.check_output(['rustc','-vV'],text=True)}
assert record['sources_before']==record['sources_after'];assert all(record['archives_after'][name]==item['sha256'] for name,item in prep['archives'].items())
(base/'capture-build.json').write_text(json.dumps(record,indent=2)+'\n');raise SystemExit(0 if len(results)==2 and all(x['exit_code']==0 for x in results) else 1)
