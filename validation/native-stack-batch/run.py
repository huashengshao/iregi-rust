from pathlib import Path
import argparse, hashlib, json, subprocess, time, os
root=Path.cwd();base=root/'target/native-stack-batch';p=argparse.ArgumentParser();p.add_argument('family',choices=['a0','b0','db0','c0','d0']);p.add_argument('--export',action='store_true');p.add_argument('--benchmark',action='store_true');p.add_argument('--timeout',type=float,default=120);p.add_argument('--cpus',default='0');args=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fam=args.family;mode='export' if args.export else 'timing' if args.benchmark else 'parity'
stem=f'{fam}-{mode}';attempt=1
while (base/f'{stem}.json').exists():
 attempt+=1;stem=f'{fam}-{mode}-{attempt}'
if args.export:
 binary=root/'target/stack-reuse-production/factory_probe'
 assert sha(binary)=='f28f98884db414aa3fa436640899840ca60885aa4de8a14094fdd1c87d8bba6c'
 command=['taskset','-c',args.cpus,str(binary),str(base/f'export-{fam}'),{'db0':'dB0'}.get(fam,fam.upper()),'--emit']
else:
 binary=base/f'probe-{fam}';build=json.loads((base/f'{fam}-build.json').read_text());assert sha(binary)==build['binary_sha256'];command=['taskset','-c',args.cpus,str(binary)]+(['--benchmark'] if args.benchmark else [])
report={'family':fam,'mode':mode,'command':command,'binary_sha256':sha(binary),'timeout_seconds':args.timeout,'status':'running','license_environment_present':any('SYMBOLICA' in k and 'LICENSE' in k for k in os.environ)};(base/f'{stem}.json').write_text(json.dumps(report,indent=2)+'\n')
start=time.monotonic()
with (base/f'{stem}.csv').open('w') as out,(base/f'{stem}.log').open('w') as err:
 try:r=subprocess.run(command,stdout=out,stderr=err,timeout=args.timeout);report.update(status='passed' if r.returncode==0 else 'failed',exit_code=r.returncode)
 except subprocess.TimeoutExpired:report.update(status='timeout',exit_code=None)
report.update(elapsed_seconds=time.monotonic()-start,binary_unchanged=sha(binary)==report['binary_sha256'],artifacts={str(q.relative_to(root)):sha(q) for q in [base/f'{stem}.csv',base/f'{stem}.log']})
(base/f'{stem}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
raise SystemExit(0 if report['status']=='passed' else 1)
