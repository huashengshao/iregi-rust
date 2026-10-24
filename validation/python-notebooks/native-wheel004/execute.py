"""Execute the single approved gallery protocol, preserving every terminal result."""
import hashlib,json,os,pathlib,signal,subprocess,time
ROOT=pathlib.Path.cwd();BASE=ROOT/'target/notebook-wheel004-protocol';OUT=BASE/'execution';OUT.mkdir(exist_ok=True)
P=json.loads((BASE/'protocol.json').read_text());M=json.loads((BASE/'source-manifest.json').read_text())

def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def guard():
 checks={p:sha(ROOT/p)==h for p,h in M['files'].items()}
 checks[P['wheel_path']]=sha(P['wheel_path'])==P['wheel_sha256']
 checks.update({x['path']:sha(ROOT/x['path'])==x['sha256'] for x in P['owner_preflight_receipts']})
 assert all(checks.values()),checks
 return checks

def run(name,cmd,cap):
 before=guard();start=time.monotonic();proc=subprocess.Popen(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 status='completed'
 try:stdout,stderr=proc.communicate(timeout=cap)
 except subprocess.TimeoutExpired:
  status='timeout';os.killpg(proc.pid,signal.SIGTERM)
  try:stdout,stderr=proc.communicate(timeout=3)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);stdout,stderr=proc.communicate()
 seconds=time.monotonic()-start
 (OUT/f'{name}.stdout.log').write_bytes(stdout);(OUT/f'{name}.stderr.log').write_bytes(stderr)
 result={'argv':cmd,'cap_seconds':cap,'seconds':seconds,'status':status,'exit_code':proc.returncode,'before':before,'after':guard(),'pass':proc.returncode==0 and status=='completed' and seconds<=cap}
 (OUT/f'{name}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'name':name,'seconds':seconds,'exit_code':proc.returncode,'pass':result['pass']}),flush=True)
 if not result['pass']:raise SystemExit(f'Stop after preserved failure: {name}')
 return result

if __name__=='__main__':
 import sys
 phase=P['phases'][int(sys.argv[1])];began=time.monotonic();total=phase.get('total_cap_seconds',phase.get('cap_seconds'))
 for i,cmd in enumerate(phase['commands']):
  remaining=total-(time.monotonic()-began)
  cap=min(phase.get('per_command_cap_seconds',remaining),remaining)
  assert cap>0
  run(f'{phase["name"]}-{i+1:02}',cmd,cap)
