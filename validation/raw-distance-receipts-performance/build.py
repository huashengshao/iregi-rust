from pathlib import Path
import os,json,hashlib,subprocess,time
root=Path.cwd();out=root/'target/raw-distance-receipts';closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds';os.sched_setaffinity(0,{6,7});sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
perf=out/'performance'
build=json.loads((out/'candidate-lib-build.json').read_text());m=json.loads((closure/'manifest.json').read_text());records=m['files']+m['native_files'];source=perf/'probe.rs';binary=perf/'probe'
externs={k:closure/'deps'/Path(next(f for f in e['filenames'] if f.endswith('.rlib'))).name for k,e in build['selected_library_events'].items() if k in ['symbolica','iregi_masters']}
for variant in ['baseline','candidate']:
 path=out/('libreceipt_'+variant+'.rlib');record=json.loads((out/(variant+'-lib-build.json')).read_text());assert record['exit_code']==0 and sha(path)==record['binary_sha256'];assert record['closure_manifest_sha256']==sha(closure/'manifest.json');externs['receipt_'+variant]=path
cmd=['rustc','--crate-name','receipt_performance','--edition=2024','-C','opt-level=3','-C','codegen-units=16','-C','lto=thin','-C','embed-bitcode=yes',str(source),'-L',f'dependency={out}','-L',f'dependency={closure}/deps']
for directory in sorted({str(Path(r['retained']).parent) for r in m['native_files'] if Path(r['retained']).suffix in ['.a','.so']}):cmd+=['-L',f'native={directory}']
for name,path in externs.items():cmd+=['--extern',f'{name}={path}']
cmd+=['-o',str(binary)]
def verify():
 for rec in records:
  p=Path(rec['retained']);assert p.stat().st_size==rec['bytes'] and sha(p)==rec['sha256'],str(p)
verify();meta={'status':'compiling','command':cmd,'source_sha256':sha(source),'extern_sha256':{str(p.relative_to(root)):sha(p) for p in externs.values()},'dependency_closure_manifest_sha256':sha(closure/'manifest.json'),'closure_files_verified_before':len(records),'cpu_affinity':[6,7]};path=perf/'build.json';path.write_text(json.dumps(meta,indent=2)+'\n');t=time.monotonic()
with (perf/'build.log').open('w') as log:r=subprocess.run(cmd,cwd=root,env=dict(os.environ,CARGO_CRATE_NAME='receipt_performance',CARGO_MANIFEST_DIR=str(root/'crates/iregi-rust')),stdout=log,stderr=subprocess.STDOUT)
meta.update(status='compiled_not_run' if r.returncode==0 else 'compile_failed',exit_code=r.returncode,seconds=time.monotonic()-t,source_unchanged=sha(source)==meta['source_sha256'],externs_unchanged=all(sha(root/p)==h for p,h in meta['extern_sha256'].items()));verify();meta['closure_files_verified_after']=len(records)
if not r.returncode and (not meta['source_unchanged'] or not meta['externs_unchanged']):meta.update(status='provenance_failed',exit_code=1)
if not meta['exit_code']:meta['binary_sha256']=sha(binary)
path.write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps({k:meta[k] for k in ['status','exit_code','seconds','source_unchanged','externs_unchanged']}));raise SystemExit(meta['exit_code'])
