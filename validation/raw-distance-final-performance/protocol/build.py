from pathlib import Path
import os,json,hashlib,subprocess,time
root=Path.cwd();out=root/'target/raw-distance-final-performance';closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds';os.sched_setaffinity(0,{6,7});sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
perf=out/'protocol'
review=json.loads((out/'source-review.json').read_text());assert review['status']=='source_review_passed';assert review['source_manifest_sha256']==sha(out/'source-manifest.json')
for name,digest in review['protocol_sources_sha256'].items():assert sha(out/name)==digest,name
build=json.loads((out/'candidate-lib-build.json').read_text());m=json.loads((closure/'manifest.json').read_text());records=m['files']+m['native_files'];source=perf/'probe.rs';binary=perf/'probe'
externs={k:closure/'deps'/Path(next(f for f in e['filenames'] if f.endswith('.rlib'))).name for k,e in build['selected_library_events'].items() if k in ['symbolica','iregi_masters']}
for variant in ['baseline','candidate']:
 path=out/('libreceipt_final_'+variant+'.rlib');record=json.loads((out/(variant+'-lib-build.json')).read_text());assert record['exit_code']==0 and record['provenance_qualified'] and record['sources_unchanged'] and record['externs_unchanged'] and sha(path)==record['binary_sha256'];assert record['source_manifest_sha256']==review['source_manifest_sha256'];assert record['closure_manifest_sha256']==sha(closure/'manifest.json');externs['receipt_final_'+variant]=path
cmd=['rustc','--crate-name','receipt_final_performance','--edition=2024','-C','opt-level=3','-C','codegen-units=16','-C','lto=thin','-C','embed-bitcode=yes',str(source),'-L',f'dependency={out}','-L',f'dependency={closure}/deps']
for directory in sorted({str(Path(r['retained']).parent) for r in m['native_files'] if Path(r['retained']).suffix in ['.a','.so']}):cmd+=['-L',f'native={directory}']
for name,path in externs.items():cmd+=['--extern',f'{name}={path}']
cmd+=['-o',str(binary)]
bindings={str(path.relative_to(root)):sha(path) for path in [out/'source-review.json',out/'source-manifest.json',out/'baseline-lib-build.json',out/'candidate-lib-build.json',Path(__file__).resolve()]}
def verify():
 for name,digest in bindings.items():assert sha(root/name)==digest,name
 for rec in records:
  p=Path(rec['retained']);assert p.stat().st_size==rec['bytes'] and sha(p)==rec['sha256'],str(p)
verify();meta={'status':'compiling','cohort_bindings':bindings,'command':cmd,'source_sha256':sha(source),'extern_sha256':{str(p.relative_to(root)):sha(p) for p in externs.values()},'dependency_closure_manifest_sha256':sha(closure/'manifest.json'),'closure_files_verified_before':len(records),'cpu_affinity':[6,7]};path=perf/'build.json';assert not path.exists(),'preserve every build attempt';path.write_text(json.dumps(meta,indent=2)+'\n');t=time.monotonic()
with (perf/'build.log').open('w') as log:r=subprocess.run(cmd,cwd=root,env=dict(os.environ,CARGO_CRATE_NAME='receipt_final_performance',CARGO_MANIFEST_DIR=str(root/'crates/iregi-rust')),stdout=log,stderr=subprocess.STDOUT)
meta.update(status='compiled_not_run' if r.returncode==0 else 'compile_failed',exit_code=r.returncode,seconds=time.monotonic()-t,source_unchanged=sha(source)==meta['source_sha256'],externs_unchanged=all(sha(root/p)==h for p,h in meta['extern_sha256'].items()));path.write_text(json.dumps(meta,indent=2)+'\n')
try:
 verify();meta['closure_files_verified_after']=len(records);meta['cohort_bindings_unchanged']=True
except (OSError,AssertionError) as error:
 meta.update(status='provenance_failed',exit_code=1,provenance_error=str(error),cohort_bindings_unchanged=False)
if not r.returncode and (not meta['source_unchanged'] or not meta['externs_unchanged']):meta.update(status='provenance_failed',exit_code=1)
if not meta['exit_code']:meta['binary_sha256']=sha(binary)
path.write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps({k:meta[k] for k in ['status','exit_code','seconds','source_unchanged','externs_unchanged']}));raise SystemExit(meta['exit_code'])
