#!/usr/bin/env python3
"""Serial correctness qualification; run only during an authorized runtime lease."""
from pathlib import Path
import os,json,hashlib,subprocess,time,datetime,argparse,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'target/guard-context-reuse';E=ROOT/'validation/guard-context-reuse'
p=argparse.ArgumentParser();p.add_argument('--timeout',type=float,default=120);p.add_argument('--group',choices=['all','units','protocol','remaining','execution','rescue'],default='all');p.add_argument('--cpus',type=int,nargs='+',default=[10,11]);args=p.parse_args()
os.sched_setaffinity(0,set(args.cpus))
groups=[]
if args.group in ['all','units']:
 groups += [(v+'-stability',[str(OUT/(v+'-unit')),'stability::tests','--test-threads=1','--nocapture']) for v in ['baseline','candidate']]
if args.group in ['all','remaining']:
 groups += [(v+'-'+module,[str(OUT/(v+'-unit')),f'stability::{module}::tests','--test-threads=1','--nocapture']) for v in ['baseline','candidate'] for module in ['arguments','quadrature']]
if args.group in ['all','protocol']:groups += [('protocol',[str(OUT/'protocol')])]
if args.group in ['all','execution']:groups += [(v+'-execution',[str(OUT/(v+'-unit')),'execution::tests','--test-threads=1','--nocapture']) for v in ['baseline','candidate']]
if args.group in ['all','rescue']:groups += [(v+'-rescue',[str(OUT/(v+'-unit')),'rescue::tests','--test-threads=1','--nocapture']) for v in ['baseline','candidate']]
results=[]
for name,cmd in groups:
 print('START',name,flush=True);start=time.monotonic();binary_hash=hashlib.sha256(Path(cmd[0]).read_bytes()).hexdigest()
 with (E/f'{name}.log').open('w') as log:
  try:r=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=args.timeout);code=r.returncode
  except subprocess.TimeoutExpired:code=124
 logtext=(E/f'{name}.log').read_text();counts=re.search(r'test result: \w+\. (\d+) passed; (\d+) failed; (\d+) ignored;',logtext)
 result={'name':name,'command':cmd,'exit_code':code,'seconds':time.monotonic()-start,'binary_sha256':binary_hash,'final_binary_sha256':hashlib.sha256(Path(cmd[0]).read_bytes()).hexdigest(),'log_sha256':hashlib.sha256((E/f'{name}.log').read_bytes()).hexdigest(),'tests_passed':int(counts[1]) if counts else None,'tests_failed':int(counts[2]) if counts else None,'tests_ignored':int(counts[3]) if counts else None};results.append(result)
 (E/f'{name}.json').write_text(json.dumps(result,indent=2)+'\n');print('END',name,code,round(result['seconds'],3),flush=True)
 report={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed' if all(r['exit_code']==0 for r in results) and len(results)==len(groups) else 'failed_or_incomplete','scope':'serial numerical correctness; no performance or actual concurrent execution','cpu_affinity':sorted(os.sched_getaffinity(0)),'group':args.group,'results':results}
 (E/f'qualification-{args.group}.json').write_text(json.dumps(report,indent=2)+'\n')
 if code:break
raise SystemExit(0 if len(results)==len(groups) and all(r['exit_code']==0 for r in results) else 1)
