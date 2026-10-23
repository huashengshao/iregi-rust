from pathlib import Path
import hashlib,json,subprocess,time,sys,statistics,platform
sys.dont_write_bytecode=True
from benchmark_helper import summarize
root=Path.cwd();base=root/'target/cli-coefficient-timing';binary=base/'probe'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
compiled=json.loads((base/'compile.json').read_text());assert compiled['exit_code']==0
prepared=json.loads((base/'preparation.json').read_text())
assert sha(Path(prepared['source_qualification_manifest']))==prepared['source_qualification_sha256']
for name,expected in prepared['qualified_source_hashes'].items():assert sha(base/'source'/name)==expected
assert sha(binary)==compiled['binary_sha256']
source={str(p.relative_to(base)):sha(p) for p in sorted((base/'source').glob('*.rs'))};assert source==compiled['source_after']
assets={str(p.relative_to(base)):sha(p) for p in sorted((base/'assets').rglob('*')) if p.is_file()}
output=base/(sys.argv[1] if len(sys.argv)>1 else 'quiet');output.mkdir(exist_ok=False)
cpu=int(sys.argv[2]) if len(sys.argv)>2 else 254
record={'status':'started','scope':'quiet paired f64 coefficient evaluation diagnostic; opt2 caller and frozen6b24opt3 dependencies, no IREGI/end-to-end gate','cpu':cpu,'allocation_detail':'Each fixed block times N public output allocations and N-1 predecessor drops; final output survives for exact comparison and is dropped outside the timer. Both variants follow the same policy.','platform':platform.platform(),'binary_sha256':sha(binary),'compile_manifest_sha256':sha(base/'compile.json'),'runner_sha256':sha(Path(__file__)),'analysis_helper_sha256':sha(base/'benchmark_helper.py'),'source_hashes':source,'assets':assets,'rows':[]}
(output/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
command=['timeout','180','taskset','-c',str(cpu),str(binary),str(output/'raw')];start=time.monotonic()
with (output/'run.log').open('w') as log:code=subprocess.call(command,stdout=log,stderr=subprocess.STDOUT)
record.update(command=command,returncode=code,elapsed_seconds=time.monotonic()-start,log_sha256=sha(output/'run.log'))
for case in ['ggh','gghh','gghhh','gggg-up']:
 path=output/'raw'/(case+'.json');raw=json.loads(path.read_text()) if path.exists() else {}
 for rows in [1,32]:
  matches=[r for r in raw.get('rows',[]) if r.get('rows')==rows];r=matches[0] if len(matches)==1 else {};blocks=r.get('blocks',[])
  summary={'case':case,'rows':rows,'status':r.get('status','not-run'),'block_count':len(blocks)}
  if len(blocks)==21 and r.get('status')=='passed':
   assert [b['block'] for b in blocks]==list(range(21));assert all(b['all_output_bits_precision_signed_zero_equal'] for b in blocks)
   assert all(b['iterations']==r['iterations_per_variant_per_block'] and b['iterations']>0 for b in blocks)
   assert all(b['first_variant']==r['first_variant_by_block'][b['block']] for b in blocks)
   baseline=[b['elapsed_ns'][0]/b['iterations'] for b in blocks];candidate=[b['elapsed_ns'][1]/b['iterations'] for b in blocks]
   ratios=[b['elapsed_ns'][1]/b['elapsed_ns'][0] for b in blocks];estimate=summarize(ratios);median=estimate['median_ns'];low,high=estimate['ci99_ns'];width=(high-low)/median
   classification='inconclusive-noise' if width>0.02 else 'improvement' if high<1 else 'regression' if low>1 else 'parity'
   summary.update(baseline_ns_per_batch=baseline,candidate_ns_per_batch=candidate,baseline_median_ns=statistics.median(baseline),candidate_median_ns=statistics.median(candidate),candidate_over_baseline={'samples':ratios,'median':median,'ci99':[low,high],'relative_ci_width':width,'classification':classification,'interpretation':'paired diagnostic only;99%bootstrap median interval;2%maxrelativeCIwidth'},exact_before_after_all_blocks=True)
  record['rows'].append(summary)
record['status']='passed' if code==0 and len(record['rows'])==8 and all(r['status']=='passed' and r['block_count']==21 for r in record['rows']) else 'failed-or-incomplete'
assert sha(binary)==record['binary_sha256'];assert source=={str(p.relative_to(base)):sha(p) for p in sorted((base/'source').glob('*.rs'))};assert assets=={str(p.relative_to(base)):sha(p) for p in sorted((base/'assets').rglob('*')) if p.is_file()}
record['source_binary_and_assets_unchanged']=True
(output/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2),flush=True)
raise SystemExit(0 if record['status']=='passed' else 1)
