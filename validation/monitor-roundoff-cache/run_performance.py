#!/usr/bin/env python3
"""Run the two distinct paired diagnostics only in a ROOT-granted quiet window."""
from pathlib import Path
import os,json,hashlib,subprocess,time,datetime,argparse,tempfile
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--timeout',type=float,default=120);args=p.parse_args()
os.sched_setaffinity(0,{0})
runs=[('earlier_guard_overhead',ROOT/'target/mixed-precision-guard-probe/probe',ROOT/'validation/mixed-precision','guard-probe','analyze_guard_probe.py'),('local_monitor_cache',ROOT/'target/monitor-roundoff-cache/performance',ROOT/'validation/monitor-roundoff-cache','performance','analyze.py')]
results=[]
for name,binary,directory,stem,analysis in runs:
 print('START',name,flush=True);start=time.monotonic();binary_bytes=binary.read_bytes();digest=hashlib.sha256(binary_bytes).hexdigest()
 build_path=directory/('guard-probe-build.json' if name=='earlier_guard_overhead' else 'performance-compile.json')
 build=json.loads(build_path.read_text())
 expected=build['sha256'][str(binary.relative_to(ROOT))] if name=='earlier_guard_overhead' else build['binary_sha256']
 if digest!=expected:raise RuntimeError(f'binary differs from retained build manifest: {name}')
 frozen_directory=ROOT/'target/monitor-roundoff-cache/executed';frozen_directory.mkdir(exist_ok=True)
 fd,frozen_name=tempfile.mkstemp(prefix=name+'-',dir=frozen_directory)
 with os.fdopen(fd,'wb') as stream:stream.write(binary_bytes)
 frozen=Path(frozen_name);frozen.chmod(0o500)
 assert hashlib.sha256(frozen.read_bytes()).hexdigest()==digest
 del binary_bytes
 with (directory/(stem+'.csv')).open('w') as out,(directory/(stem+'.log')).open('w') as err:
  try:r=subprocess.run([str(frozen)],cwd=ROOT,stdout=out,stderr=err,timeout=args.timeout);code=r.returncode
  except subprocess.TimeoutExpired:code=124
 record={'name':name,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary':str(binary.relative_to(ROOT)),'binary_sha256':digest,'executed_copy':str(frozen.relative_to(ROOT)),'executed_copy_final_sha256':hashlib.sha256(frozen.read_bytes()).hexdigest(),'build_manifest':str(build_path.relative_to(ROOT)),'build_manifest_sha256':hashlib.sha256(build_path.read_bytes()).hexdigest(),'exit_code':code,'seconds':time.monotonic()-start,'cpu_affinity':[0],'quiet_window':'requires central lease; CPU affinity alone is not evidence of a quiet host','raw_csv_sha256':hashlib.sha256((directory/(stem+'.csv')).read_bytes()).hexdigest(),'log_sha256':hashlib.sha256((directory/(stem+'.log')).read_bytes()).hexdigest(),'scope':'paired isolated direct-rustc experiment, not IREGI performance acceptance'}
 record['provenance_qualified']=record['executed_copy_final_sha256']==digest
 if not record['provenance_qualified']:record['exit_code']=code=1
 (directory/(stem+'-run.json')).write_text(json.dumps(record,indent=2)+'\n');results.append(record)
 print('END',name,code,round(record['seconds'],3),flush=True)
 if code:break
 # Bootstrap analysis is read-only numerical Python, performed after timing.
for record, (name,binary,directory,stem,analysis) in zip(results, runs):
 if record['exit_code']:
  continue
 with (directory/(stem+'-analysis.log')).open('w') as log:
  result=subprocess.run(['python3',str(directory/analysis)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 record['analysis_exit_code']=result.returncode
(ROOT/'validation/monitor-roundoff-cache/paired-performance-runs.json').write_text(json.dumps({'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'scope':'Separate earlier accuracy-guard and later monitor-cache diagnostics; do not pool or multiply their speedups'},indent=2)+'\n')
raise SystemExit(0 if len(results)==len(runs) and all(r['exit_code']==0 and r.get('analysis_exit_code')==0 for r in results) else 1)
