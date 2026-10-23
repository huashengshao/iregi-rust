from pathlib import Path
import argparse,hashlib,json,os,subprocess,time
root=Path.cwd();base=root/'target/native-shared-binary';binary=base/'probe'
p=argparse.ArgumentParser();p.add_argument('--phase',choices=['initial','before','after'],default='initial');p.add_argument('--cpus',default='20,21');args=p.parse_args();stem='parity' if args.phase=='initial' else 'parity-'+args.phase
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=json.loads((base/'probe-build.json').read_text())
assert build['exit_code']==0 and not build['changed'] and sha(binary)==build['binary_sha256']
assert not (base/f'{stem}.json').exists(),'preserve previous qualification attempt'
for p,h in build['inputs'].items():assert sha(root/p)==h,p
command=['taskset','-c',args.cpus,str(binary)];start=time.monotonic()
report={'command':command,'phase':args.phase,'started_unix_time':time.time(),'binary_sha256':build['binary_sha256'],'license_environment_present':any('SYMBOLICA' in k and 'LICENSE' in k for k in os.environ)}
with (base/f'{stem}.csv').open('w') as out,(base/f'{stem}.log').open('w') as err:
 try:
  r=subprocess.run(command,stdout=out,stderr=err,timeout=240);report.update(status='passed' if r.returncode==0 else 'failed',exit_code=r.returncode)
 except subprocess.TimeoutExpired:report.update(status='timeout',exit_code=None)
report.update(finished_unix_time=time.time(),elapsed_seconds=time.monotonic()-start,binary_unchanged=sha(binary)==build['binary_sha256'],inputs_unchanged=all(sha(root/p)==h for p,h in build['inputs'].items()),csv_sha256=sha(base/f'{stem}.csv'),log_sha256=sha(base/f'{stem}.log'))
(base/f'{stem}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
raise SystemExit(0 if report['status']=='passed' else 1)
