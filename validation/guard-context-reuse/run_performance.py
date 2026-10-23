#!/usr/bin/env python3
"""Run only under an explicitly granted quiet CPU0 timing window."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess, tempfile, time
ROOT=Path(__file__).resolve().parents[2]; E=ROOT/'validation/guard-context-reuse'; OUT=ROOT/'target/guard-context-reuse'
parser=argparse.ArgumentParser();parser.add_argument('--timeout',type=float,default=120);args=parser.parse_args()
os.sched_setaffinity(0,{0})
binary=OUT/'performance';manifest=E/'performance-compile.json';build=json.loads(manifest.read_text())
data=binary.read_bytes();digest=hashlib.sha256(data).hexdigest()
if digest != build['binary_sha256']:raise SystemExit('binary differs from the retained build manifest')
executed=OUT/'executed';executed.mkdir(exist_ok=True)
fd,name=tempfile.mkstemp(prefix='guard-context-',dir=executed)
with os.fdopen(fd,'wb') as stream:stream.write(data)
frozen=Path(name);frozen.chmod(0o500)
if hashlib.sha256(frozen.read_bytes()).hexdigest()!=digest:raise SystemExit('frozen executable copy differs')
record={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'command':[str(frozen)],'binary':str(binary.relative_to(ROOT)),'binary_sha256':digest,
 'executed_copy':str(frozen.relative_to(ROOT)),'build_manifest':str(manifest.relative_to(ROOT)),
 'build_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
 'cpu_affinity':[0],'quiet_window':'run only after the central coordinator explicitly grants the window',
 'scope':'isolated paired f64 direct-rustc guard-context experiment, not the IREGI reference acceptance benchmark'}
start=time.monotonic();code=1
try:
 with (E/'performance.csv').open('w') as out,(E/'performance.log').open('w') as err:
  try:code=subprocess.run([str(frozen)],cwd=ROOT,stdout=out,stderr=err,timeout=args.timeout).returncode
  except subprocess.TimeoutExpired:code=124
finally:
 record.update(exit_code=code,seconds=time.monotonic()-start,provenance_qualified=False)
 (E/'performance-run.json').write_text(json.dumps(record,indent=2)+'\n')
 try:
  final_digest=hashlib.sha256(frozen.read_bytes()).hexdigest()
  record.update(executed_copy_final_sha256=final_digest,provenance_qualified=final_digest==digest,
   raw_csv_sha256=hashlib.sha256((E/'performance.csv').read_bytes()).hexdigest(),
   log_sha256=hashlib.sha256((E/'performance.log').read_bytes()).hexdigest())
 except OSError as error:record['provenance_error']=str(error)
 if not record['provenance_qualified']:record['exit_code']=code=1
 (E/'performance-run.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2));raise SystemExit(code)
