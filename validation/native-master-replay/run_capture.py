from pathlib import Path
import hashlib,importlib.util,json,os,time
root=Path.cwd();base=root/'target/native-master-replay';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
spec=importlib.util.spec_from_file_location('benchmark_harness',root/'validation/benchmark/run.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
assert not (base/'capture-results.json').exists(),'preserve prior numerical attempt'
build=json.loads((base/'capture-build.json').read_text());assert len(build['stages'])==2 and all(r['exit_code']==0 for r in build['stages'])
binary=base/'capture';assert sha(binary)==build['stages'][-1]['artifact_sha256']
reference=root/'target/benchmark/iregi-benchmark';ref_manifest=json.loads((root/'target/benchmark/reference-build.json').read_text());assert sha(reference)==ref_manifest['binary_sha256']
prep=json.loads((base/'preparation.json').read_text());assert sha(base/'inputs.json')==prep['benchmark_input_sha256']
for path,digest in build['sources_before'].items():assert sha(base/path)==digest,path
os.sched_setaffinity(0,{20,21});start=time.monotonic()
result={'scope':'Untimed actual master request capture from committed21622 current-core source against unchanged optimized6b24 default scalar dependencies; reference execution only validates all tensor/Laurent outputs. No timing qualification.','source_revision':prep['source_revision'],'input_sha256':sha(base/'inputs.json'),'binary_sha256':sha(binary),'reference_binary_sha256':sha(reference),'license_environment_present':any('SYMBOLICA' in k and 'LICENSE' in k for k in os.environ),'rows':[]}
capture=h.Process(binary,'capture',base,120);reference_process=h.Process(reference,'reference',base,120)
cases=json.loads((base/'inputs.json').read_text())
try:
 for case in cases:
  for width in [1,32]:
   samples=case['samples'][:width];row={'id':case['id'],'n':case['n'],'rank':case['rank'],'outer_batch':width,'status':'pending'};result['rows'].append(row)
   try:
    response=capture.request(h.rust_request(case,samples,'Hybrid',0,1));row['capture']=response
    ref=reference_process.request(h.fortran_request(case,samples,'Hybrid',0,1));ref.pop('total_ns',None);row['reference']=ref
    comparison=h.compare(response,ref,case,samples);row['correctness']=comparison
    assert comparison['status']=='passed',comparison
    assert response['master_backend']=='SymbolicaBatch' and response['stable']
    assert response['execution']['fallback_rows']==0 and response['execution']['analytic_rows']==0,'replay corpus must not mix fallback/analytic recursion'
    groups=response['master_captures'];expected={(2,0):{'B0':width},(2,1):{'A0':2*width,'B0':width},(3,0):{'C0':width},(3,1):{'B0':3*width,'C0':width}}[(case['n'],case['rank'])]
    assert {g['family']:g['rows'] for g in groups}==expected and len(groups)==len(expected)
    assert response['execution']['master_family_batches']==len(groups) and response['execution']['master_rows']==sum(g['rows'] for g in groups)
    for group in groups:
     assert group['components']==1 and group['whole_batch_error'] is None and all(e is None for e in group['errors'])
     assert group['valid_lanes']==list(range(width))
     arity={'A0':2,'B0':4,'C0':7}[group['family']]
     assert len(group['input'])==arity*group['rows'] and len(group['requests'])==group['rows'] and len(group['output'])==group['rows'] and len(group['errors'])==group['rows']
     assert all(len(v)==5 for v in group['output'])
     assert group['requests']==sorted(group['requests']),'leaf-major request order changed'
     for collection in [group['input'],[v for row in group['output'] for v in row]]:
      for complex_value in collection:
       assert len(complex_value)==2 and all(v['finite'] and v['rational'] is not None and v['precision']==53 for v in complex_value)
    row['status']='passed'
   except Exception as e:row.update(status='failed',error=str(e))
   (base/'capture-results.json').write_text(json.dumps(result,indent=2)+'\n')
finally:
 capture.close();reference_process.close()
result.update(status='passed' if len(result['rows'])==8 and all(r['status']=='passed' for r in result['rows']) else 'failed',elapsed_seconds=time.monotonic()-start,binary_unchanged=sha(binary)==result['binary_sha256'],reference_unchanged=sha(reference)==result['reference_binary_sha256'],sources_unchanged=all(sha(base/p)==digest for p,digest in build['sources_before'].items()))
(base/'capture-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'elapsed_seconds':result['elapsed_seconds'],'rows':[{'id':r['id'],'batch':r['outer_batch'],'status':r['status'],'groups':[(g['family'],g['rows']) for g in r.get('capture',{}).get('master_captures',[])]} for r in result['rows']]},indent=2))
raise SystemExit(0 if result['status']=='passed' else 1)
