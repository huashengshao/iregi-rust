from pathlib import Path
import argparse,hashlib,json,os,subprocess,time
root=Path.cwd();base=root/'target/native-shared-binary';p=argparse.ArgumentParser();p.add_argument('family',choices=['b0','c0']);p.add_argument('--cpus',default='254');p.add_argument('--quiet-window',required=True,help='Parent-granted quiet-window manifest path');args=p.parse_args()
assert ',' not in args.cpus and '-' not in args.cpus,'one CPU required'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();binary=base/'probe';build=json.loads((base/'probe-build.json').read_text());qualification=json.loads((base/'qualification.json').read_text())
assert qualification['status']=='numerically-qualified-timing-unrun'
assert build['exit_code']==0 and not build['changed'] and sha(binary)==build['binary_sha256']
for path,h in build['inputs'].items():assert sha(root/path)==h,path
window=Path(args.quiet_window);assert window.exists();stem=f'{args.family}-timing-fixed';assert not (base/f'{stem}.json').exists(),'preserve prior measurements'
command=['taskset','-c',args.cpus,str(binary),f'--benchmark-{args.family}'];start=time.monotonic()
report={'protocol':'shared-binary-fixed-loop-v2','family':args.family,'command':command,'started_unix_time':time.time(),'binary_sha256':build['binary_sha256'],'qualification_sha256':sha(base/'qualification.json'),'quiet_window_manifest':str(window),'quiet_window_sha256_at_start':sha(window),'license_environment_present':any('SYMBOLICA' in k and 'LICENSE' in k for k in os.environ)}
with (base/f'{stem}.csv').open('w') as out,(base/f'{stem}.log').open('w') as err:
 try:
  r=subprocess.run(command,stdout=out,stderr=err,timeout=120);report.update(status='passed' if r.returncode==0 else 'failed',exit_code=r.returncode)
 except subprocess.TimeoutExpired:report.update(status='timeout',exit_code=None)
report.update(finished_unix_time=time.time(),elapsed_seconds=time.monotonic()-start,binary_unchanged=sha(binary)==build['binary_sha256'],csv_sha256=sha(base/f'{stem}.csv'),log_sha256=sha(base/f'{stem}.log'))
(base/f'{stem}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
raise SystemExit(0 if report['status']=='passed' else 1)
