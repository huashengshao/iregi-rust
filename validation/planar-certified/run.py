from pathlib import Path
import hashlib, json, os, signal, subprocess, sys, time
root=Path.cwd(); base=root/'target/planar-certified'
name=sys.argv[1]; timeout=float(sys.argv[2]) if len(sys.argv)>2 else 120
assert name.replace('_','').isalnum()
variant=os.environ.get('IREGI_PLANAR_VARIANT','')
prefix=variant+'-' if variant else ''
binary=base/('core-tests-'+variant if variant else 'core-tests')
compile_manifest=base/('compile-'+variant+'.json' if variant else 'compile.json')
command=[str(binary),'--exact','certified_planar::tests::'+name,'--nocapture','--test-threads=1']
report={'command':command,'timeout_seconds':timeout,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'compile_manifest_sha256':hashlib.sha256(compile_manifest.read_bytes()).hexdigest()}
start=time.monotonic()
with (base/(prefix+name+'.log')).open('w') as log:
 process=subprocess.Popen(command,cwd=root,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try: status=process.wait(timeout=timeout)
 except subprocess.TimeoutExpired:
  os.killpg(process.pid,signal.SIGTERM)
  try: process.wait(timeout=5)
  except subprocess.TimeoutExpired: os.killpg(process.pid,signal.SIGKILL); process.wait()
  status=124
report.update(exit_code=status,elapsed_seconds=time.monotonic()-start)
(base/(prefix+name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
print((base/(prefix+name+'.log')).read_text(),flush=True)
sys.exit(status)
