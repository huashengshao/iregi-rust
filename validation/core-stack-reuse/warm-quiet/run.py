from pathlib import Path
import hashlib,json,os,signal,statistics,struct,sys,time
sys.dont_write_bytecode=True
from benchmark_helper import Process,suite,rust_request,validate_response,summarize
root=Path.cwd();base=root/'target/core-stack-reuse';out=base/'warm-quiet';start=time.monotonic();procs=[]
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def timeout(signum,frame):raise TimeoutError('whole diagnostic exceeded120seconds')
signal.signal(signal.SIGALRM,timeout);signal.alarm(120)
os.sched_setaffinity(0,{18})
paths={v:base/v/'kernel_benchmark' for v in ['baseline','candidate']}
for v,p in paths.items():assert sha(p)==json.loads((base/v/'kernel-compile.json').read_text())['binary_sha256']
records=[];parity_checks=0
report={'status':'running','kind':'paired ordinary-core stack allocation warm diagnostic','cpu':18,'source_revision':'80949dbc4711947971a702643f75d639ef217e82','compiler_scope':'Matched opt2 proof core libraries; retained development dependency profiles; not the opt3 workspace benchmark binaries.','performance_gate':'Quiet opt2 diagnostic only. All other project computations held by coordinator; proof instrumentation affects preparation, which is excluded. No opt3 workspace or reference-engine parity claim.','binary_sha256_before':{v:sha(p) for v,p in paths.items()},'helper_sha256':sha(out/'benchmark_helper.py'),'runner_sha256':sha(Path(__file__))}
def ratio_summary(values):
    result=summarize(values)
    return {'unit':'dimensionless candidate/baseline time ratio','samples':result['samples_ns'],'median':result['median_ns'],'ci99':result['ci99_ns'],'minimum':result['minimum_ns'],'maximum':result['maximum_ns'],'relative_mad':result['relative_mad']}
def parity_value(x):
 if isinstance(x,float):return ('f64',struct.pack('>d',x).hex())
 if isinstance(x,list):return [parity_value(i) for i in x]
 if isinstance(x,dict):return {k:parity_value(v) for k,v in x.items()}
 return x
def same(a,b):
 global parity_checks
 for key in ['lanes','degrees','execution','master_backend','stable']:
  assert parity_value(a[key])==parity_value(b[key]),(key,a[key],b[key])
 assert a['stable'] and b['stable'];parity_checks+=1
try:
 for v,p in paths.items():procs.append(Process(p,v,out,110))
 with (out/'raw.jsonl').open('w') as raw:
  for case in suite([1],['massive'],[1,32]):
   for batch in [1,32]:
    samples=case['samples'][:batch];pilots=[]
    for proc in procs:
     response=proc.request(rust_request(case,samples,'Hybrid',3,1))
     validate_response(response,case,profile=False);pilots.append(response)
    same(*pilots)
    iterations=[max(1,min(200000,round(30000000/p['total_ns'][0]))) for p in pilots]
    series=[[],[]]
    for block in range(21):
     results=[None,None]
     for offset in range(2):
      index=(block+offset)%2
      result=procs[index].request(rust_request(case,samples,'Hybrid',0,iterations[index]))
      validate_response(result,case,profile=False);results[index]=result;series[index].append(result['total_ns'][0])
      raw.write(json.dumps({'id':case['id'],'batch':batch,'block':block,'variant':['baseline','candidate'][index],'iterations':iterations[index],'request_samples':samples,'response':result})+'\n');raw.flush()
     same(*results)
    final=[p.request(rust_request(case,samples,'Hybrid',0,1)) for p in procs];same(*final)
    ratios=[c/b for b,c in zip(*series)];row={'id':case['id'],'batch':batch,'blocks':21,'baseline_ns':series[0],'candidate_ns':series[1],'baseline_median_ns':statistics.median(series[0]),'candidate_median_ns':statistics.median(series[1]),'candidate_over_baseline':ratio_summary(ratios),'all_outputs_exact':True}
    records.append(row);print(json.dumps(row),flush=True)
 report.update(status='passed',rows=records,parity_checks=parity_checks)
except BaseException as error:
 report.update(status='failed',error=f'{type(error).__name__}: {error}',rows=records,parity_checks=parity_checks);raise
finally:
 signal.alarm(0)
 for p in procs:p.close()
 report.update(elapsed_seconds=time.monotonic()-start,binary_sha256_after={v:sha(p) for v,p in paths.items()},helper_sha256_after=sha(out/'benchmark_helper.py'),runner_sha256_after=sha(Path(__file__)))
 assert report['binary_sha256_before']==report['binary_sha256_after']
 assert report['helper_sha256']==report['helper_sha256_after']
 assert report['runner_sha256']==report['runner_sha256_after']
 (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
