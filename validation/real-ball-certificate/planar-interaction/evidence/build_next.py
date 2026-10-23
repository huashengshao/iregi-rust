from pathlib import Path
import argparse,hashlib,json,os,signal,subprocess,time
root=Path.cwd();out=Path(__file__).resolve().parent;closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds';deps=closure/'deps'
p=argparse.ArgumentParser();p.add_argument('variant',choices=['baseline','candidate']);p.add_argument('kind',choices=['unit','core','cli','kernel','physical','typed']);a=p.parse_args();variant=out/a.variant;dest=variant/'artifacts';dest.mkdir(exist_ok=True)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();manifest=closure/'manifest.json';m=json.loads(manifest.read_text());events_path=closure/'cargo-library-events.json';events=json.loads(events_path.read_text());completion_path=closure/'workspace-completion.json';completion=json.loads(completion_path.read_text());assert completion['cargo_returncode']==0 and completion['dependency_closure_manifest_sha256']==sha(manifest);parent=Path(m['workspace_build_manifest']);assert completion['workspace_manifest_sha256']==sha(parent)
sources_path=out/'sources.json';sources=json.loads(sources_path.read_text());inventory=sources['variants'][a.variant]
for name,digest in inventory.items():assert sha(variant/name)==digest,name
selected={};externs={}
def library(name):
 matches=[e for e in events if e['target']['name']==name and e['profile']['opt_level']=='3' and not e['profile']['test']];assert len(matches)==1,(name,len(matches));selected[name]=matches[0];paths=[deps/Path(f).name for f in matches[0]['filenames'] if f.endswith('.rlib')];assert len(paths)==1;return paths[0]
needed={'unit':['symbolica','iregi_masters','serde','serde_json','thiserror'],'core':['symbolica','iregi_masters','serde','serde_json','thiserror'],'cli':['symbolica','iregi_masters','iregi_prepare','serde','serde_json'],'kernel':['symbolica','iregi_masters','serde','serde_json'],'physical':['symbolica','iregi_masters','iregi_prepare','serde','serde_json'],'typed':['symbolica','iregi_masters','serde_json']}[a.kind]
externs={name:library(name) for name in needed}
if a.kind in ['cli','kernel','physical','typed']:externs['iregi_rust']=dest/'libiregi_rust.rlib'
if a.kind=='physical':externs['iregi_cli']=dest/'libiregi_cli.rlib'
producer_records={}
for dependency,kind in [('iregi_rust','core'),('iregi_cli','cli')]:
 if dependency in externs and externs[dependency].parent==dest:
  producer=dest/f'{kind}-build.json';pd=json.loads(producer.read_text());assert pd['status']=='compiled' and pd['returncode']==0 and pd['verified_before'] and pd['verified_after'];assert pd['variant']==a.variant and pd['binary_sha256']==sha(externs[dependency]);producer_records[dependency]={'manifest':str(producer.relative_to(root)),'sha256':sha(producer),'binary_sha256':pd['binary_sha256']}
source={'unit':'crates/iregi-rust/src/lib.rs','core':'crates/iregi-rust/src/lib.rs','cli':'crates/iregi-cli/src/lib.rs','kernel':'crates/iregi-rust/examples/kernel_benchmark.rs','physical':'crates/iregi-cli/examples/physical_benchmark.rs','typed':str(out/'typed_witness.rs')}[a.kind]
crate={'unit':'iregi_rust','core':'iregi_rust','cli':'iregi_cli','kernel':'kernel_benchmark','physical':'physical_benchmark','typed':'typed_witness'}[a.kind]
binary=dest/{'unit':'core_tests','core':'libiregi_rust.rlib','cli':'libiregi_cli.rlib','kernel':'kernel_benchmark','physical':'physical_benchmark','typed':'typed_witness'}[a.kind]
cmd=['rustc','--crate-name',crate,'--edition=2024',str(variant/source),'-L',f'dependency={dest}','-L',f'dependency={deps}']
for directory in sorted({str(Path(r['retained']).parent) for r in m['native_files'] if Path(r['retained']).suffix in ['.a','.so']}):cmd+=['-L',f'native={directory}']
for name,path in externs.items():cmd+=['--extern',f'{name}={path}']
if a.kind=='unit':cmd+=['--test','-C','opt-level=1','-C','codegen-units=16','-C','lto=thin','-C','embed-bitcode=yes']
elif a.kind in ['core','cli']:cmd+=['--crate-type','rlib','-C','opt-level=3','-C','codegen-units=1','-C','embed-bitcode=yes']
else:cmd+=['-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-C','embed-bitcode=yes']
cmd+=['-o',str(binary)]
state={'schema':1,'status':'verifying_before','variant':a.variant,'kind':a.kind,'command':cmd,'cpu_affinity':sorted(os.sched_getaffinity(0)),'source_revision':sources['source_revision'],'source_inventory_sha256':sha(sources_path),'build_script_sha256':sha(Path(__file__)),'closure_manifest_sha256':sha(manifest),'cargo_library_events_sha256':sha(events_path),'workspace_completion_sha256':sha(completion_path),'producer_builds':producer_records,'selected_library_events':selected,'extern_sha256':{str(p.relative_to(root)):sha(p) for p in externs.values()},'source_sha256':inventory,'supplemental_source_sha256':{source:sha(Path(source))} if a.kind=='typed' else {},'whole_workspace_completion':completion,'rustc_verbose':subprocess.check_output(['rustc','-vV'],text=True),'rustc_sysroot':subprocess.check_output(['rustc','--print','sysroot'],text=True).strip(),'scope':'Current core/planar private snapshot plus slim only and paired certificate validation modules. Immutable6b24 dependency arithmetic; no new public-master qualification.'}
record=dest/f'{a.kind}-build.json';save=lambda:record.write_text(json.dumps(state,indent=2)+'\n');save()
def verify():
 for r in m['files']+m['native_files']:
  p=Path(r['retained']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],str(p)
 for name,digest in inventory.items():assert sha(variant/name)==digest,name
 for name,digest in state['supplemental_source_sha256'].items():assert sha(Path(name))==digest,name
 for name,digest in state['extern_sha256'].items():assert sha(root/name)==digest,name
 assert sha(Path(__file__))==state['build_script_sha256'];assert sha(events_path)==state['cargo_library_events_sha256']
 for binding in producer_records.values():assert sha(root/binding['manifest'])==binding['sha256']
 assert sha(sources_path)==state['source_inventory_sha256'];assert sha(manifest)==state['closure_manifest_sha256'];assert sha(completion_path)==state['workspace_completion_sha256'];assert sha(parent)==completion['workspace_manifest_sha256']
verify();state['verified_before']=True;state['status']='compiling';save();print(f'{a.variant} {a.kind}: verified snapshot/closure; compiling',flush=True);start=time.monotonic();env=dict(os.environ,CARGO_MANIFEST_DIR=str(variant/'crates'/('iregi-cli' if a.kind in ['cli','physical'] else 'iregi-rust')),CARGO_PKG_NAME='iregi-rust',CARGO_CRATE_NAME=crate,CARGO_PKG_VERSION='0.1.0')
pause_marker=out/'PAUSE_COMPILERS'
state['pause_marker']=str(pause_marker.relative_to(root));state['pause_events']=[]
with (dest/f'{a.kind}-build.log').open('w') as log:
 while pause_marker.exists():time.sleep(0.2)
 r=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 state['owned_compiler_process_group']=r.pid;save();paused=False
 try:
  while r.poll() is None:
   requested=pause_marker.exists()
   if requested != paused:
    try:os.killpg(r.pid,signal.SIGSTOP if requested else signal.SIGCONT)
    except ProcessLookupError:break
    paused=requested;state['pause_events'].append({'action':'pause' if paused else 'resume','elapsed_seconds':time.monotonic()-start});save()
   time.sleep(0.2)
 finally:
  if paused:
   try:os.killpg(r.pid,signal.SIGCONT)
   except ProcessLookupError:pass
 r.wait()
state['returncode']=r.returncode;state['wall_seconds']=time.monotonic()-start;state['status']='verifying_after';save();verify();state['verified_after']=True;state['status']='compiled' if r.returncode==0 else 'failed'
if r.returncode==0:state['binary_sha256']=sha(binary)
save();print(json.dumps({k:state[k] for k in ['variant','kind','status','returncode','wall_seconds','verified_before','verified_after']}),flush=True);raise SystemExit(r.returncode)
