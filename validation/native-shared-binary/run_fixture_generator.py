from pathlib import Path
import hashlib,json,os,subprocess,sys,time
root=Path.cwd();base=root/'target/native-shared-binary';family='fixture'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();binary=base/'generate-fixture';build=json.loads((base/'fixture-generator-build.json').read_text());assert sha(binary)==build['binary_sha256']
command=['taskset','-c','20,21',str(binary)];start=time.monotonic()
report={'family':family,'command':command,'binary_sha256':build['binary_sha256'],'license_environment_present':any('SYMBOLICA' in k and 'LICENSE' in k for k in os.environ)}
with (base/f'{family}-generation.csv').open('w') as out,(base/f'{family}-generation.log').open('w') as err:
 try:
  r=subprocess.run(command,stdout=out,stderr=err,timeout=120);report.update(status='passed' if r.returncode==0 else 'failed',exit_code=r.returncode)
 except subprocess.TimeoutExpired:report.update(status='timeout',exit_code=None)
report.update(elapsed_seconds=time.monotonic()-start,binary_unchanged=sha(binary)==build['binary_sha256'],generated={str(p.relative_to(root)):sha(p) for p in sorted((base/family).glob('*')) if p.is_file()})
(base/f'{family}-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='generated'}))
raise SystemExit(0 if report['status']=='passed' else 1)
