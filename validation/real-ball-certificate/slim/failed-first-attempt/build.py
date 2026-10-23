from pathlib import Path
import hashlib,json,os,subprocess,time
root=Path.cwd();out=Path(__file__).resolve().parent;closure=root/'target/benchmark/dependency-closures/6b24c03';manifest=closure/'manifest.json';events_path=closure/'cargo-library-events.json'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
m=json.loads(manifest.read_text());events=json.loads(events_path.read_text());assert m['source_revision']=='6b24c0372022e22606a1ac85f30c7fa579fb41f0';assert len(events)==m['library_event_count']==423
records=m['files']+m['native_files'];retained={r['original']:Path(r['retained']) for r in records}
files=[out/'slim.rs',out/'original.rs',out/'slim_tests.rs',Path(__file__).resolve()]
assert (out/'original.rs').read_bytes()==(Path(m['source_root'])/'crates/iregi-rust/src/invariant_certificate.rs').read_bytes()
selected={};externs={}
for name in ['iregi_rust','iregi_masters','symbolica']:
 matches=[e for e in events if e['target']['name']==name and e['profile']['opt_level']=='3' and not e['profile']['test']]
 assert len(matches)==1,(name,len(matches));selected[name]=matches[0]
 paths=[retained[f] for f in matches[0]['filenames'] if f.endswith('.rlib')];assert len(paths)==1;externs[name]=paths[0]
argv=['rustc','--crate-name','certificate_slim_tests','--edition=2024','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-C','embed-bitcode=yes','--test',str(out/'slim_tests.rs'),'-L',f'dependency={closure}/deps']
native_dirs=sorted({str(Path(r['retained']).parent) for r in m['native_files'] if Path(r['retained']).suffix in ['.a','.so']})
for directory in native_dirs:argv+=['-L',f'native={directory}']
for name,path in externs.items():argv+=['--extern',f'{name}={path}']
binary=out/'certificate_slim_tests';argv+=['-o',str(binary)]
state={'schema':1,'status':'verifying_closure','source_revision':m['source_revision'],'dependency_closure_manifest':str(manifest.relative_to(root)),'dependency_closure_manifest_sha256':sha(manifest),'cargo_library_events_sha256':sha(events_path),'parent_workspace_status':m['status'],'whole_workspace_success_claimed':False,'command':argv,'cpu_affinity':sorted(os.sched_getaffinity(0)),'source_sha256':{str(p.relative_to(root)):sha(p) for p in files},'selected_library_events':selected,'explicit_archive_sha256':{str(p.relative_to(root)):sha(p) for p in externs.values()},'closure_files':len(records),'native_search_dirs':native_dirs}
path=out/'build.json';save=lambda:path.write_text(json.dumps(state,indent=2)+'\n');save()
def verify_closure():
 for record in records:
  p=Path(record['retained']);assert p.stat().st_size==record['bytes'] and sha(p)==record['sha256'],str(p)
 assert sha(manifest)==state['dependency_closure_manifest_sha256']
 assert sha(events_path)==state['cargo_library_events_sha256']
verify_closure();state['closure_verified_before']=True;state['status']='compiling';save();print('Full retained closure verified; compiling slim tests.',flush=True);start=time.monotonic()
with (out/'build.log').open('w') as log:
 r=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,CARGO_CRATE_NAME='certificate_slim_tests'))
state['returncode']=r.returncode;state['wall_seconds']=time.monotonic()-start;state['status']='verifying_after';save();verify_closure();state['closure_verified_after']=True;state['sources_unchanged']=all(sha(root/p)==h for p,h in state['source_sha256'].items());assert state['sources_unchanged']
state['status']='compiled' if r.returncode==0 else 'failed'
if r.returncode==0:state['binary_sha256']=sha(binary)
save();print(json.dumps({k:state[k] for k in ['status','returncode','wall_seconds','closure_verified_before','closure_verified_after','sources_unchanged']}),flush=True);raise SystemExit(r.returncode)
