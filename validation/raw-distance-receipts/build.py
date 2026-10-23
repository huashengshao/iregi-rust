#!/usr/bin/env python3
from pathlib import Path
import argparse,os,hashlib,json,subprocess,time
root=Path.cwd(); out=root/'target/raw-distance-receipts';closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds';deps=closure/'deps'
p=argparse.ArgumentParser();p.add_argument('variant',choices=['baseline','candidate']);p.add_argument('kind',choices=['metadata','unit','lib']);a=p.parse_args()
os.sched_setaffinity(0,{6,7})
source=out/a.variant/'crates/iregi-rust/src/lib.rs';crate_name='receipt_'+a.variant;binary=out/((crate_name+'-unit') if a.kind=='unit' else (crate_name+'.rmeta') if a.kind=='metadata' else ('lib'+crate_name+'.rlib'))
events=json.loads((closure/'cargo-library-events.json').read_text())
externs={}
selected={}
for name in ['symbolica','iregi_masters','serde','serde_json','thiserror']:
 matches=[e for e in events if e['target']['name']==name and e['profile']['opt_level']=='3' and not e['profile']['test']]
 assert len(matches)==1,(name,len(matches))
 selected[name]=matches[0]
 paths=[deps/Path(f).name for f in matches[0]['filenames'] if f.endswith('.rlib')]
 assert len(paths)==1
 externs[name]=paths[0]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cmd=['rustc','--crate-name',crate_name,'--edition=2024',str(source),'-L',f'dependency={deps}']
for native in sorted((closure/'build').glob('*/out')):
 cmd+=['-L',f'native={native}']
 if (native/'lib').exists():cmd+=['-L',f'native={native}/lib']
for k,v in externs.items():cmd+=['--extern',f'{k}={v}']
if a.kind=='metadata':cmd+=['--test','--emit=metadata','-C','opt-level=0']
elif a.kind=='unit':cmd+=['--test','-C','opt-level=1','-C','codegen-units=16','-C','lto=thin','-C','embed-bitcode=yes']
else:cmd+=['--crate-type','rlib','-C','opt-level=3','-C','codegen-units=16','-C','embed-bitcode=yes']
cmd+=['-o',str(binary)]
meta={'status':'compiling','command':cmd,'closure':str(closure.relative_to(root)),'closure_manifest_sha256':sha(closure/'manifest.json'),'selected_library_events':selected,'extern_sha256':{str(v.relative_to(root)):sha(v) for v in externs.values()},'source_sha256':{str(p.relative_to(root)):sha(p) for p in sorted(source.parent.rglob('*.rs'))},'cpu_affinity':[6,7],'source_only_experiment':True}
record=out/(a.variant+'-'+a.kind+'-build.json');record.write_text(json.dumps(meta,indent=2)+'\n');t=time.monotonic()
env=dict(os.environ,CARGO_MANIFEST_DIR=str(source.parent.parent),CARGO_PKG_NAME='iregi-rust',CARGO_CRATE_NAME='iregi_rust',CARGO_PKG_VERSION='0.1.0')
with (out/(a.variant+'-'+a.kind+'-build.log')).open('w') as log:r=subprocess.run(cmd,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
meta.update(status='compiled_not_run' if r.returncode==0 else 'compile_failed',exit_code=r.returncode,seconds=time.monotonic()-t,sources_unchanged=all(sha(root/p)==h for p,h in meta['source_sha256'].items()),externs_unchanged=all(sha(root/p)==h for p,h in meta['extern_sha256'].items()))
if not r.returncode:meta['binary_sha256']=sha(binary)
record.write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps({k:meta[k] for k in ['status','exit_code','seconds','sources_unchanged','externs_unchanged']}));raise SystemExit(r.returncode)
