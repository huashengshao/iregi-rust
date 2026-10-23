"""Stop/resume only the verified dedicated process group of a selected fixed-protocol build."""
import argparse,json,os,signal,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('action',choices=['stop','continue']);p.add_argument('family',choices=['a0','b0','db0','c0','d0']);args=p.parse_args();base=Path('target/native-stack-batch')
processes={}
for line in subprocess.check_output(['ps','-eo','pid=,ppid=,pgid=,args='],text=True).splitlines():
 a=line.split(None,3)
 if len(a)==4:processes[int(a[0])]={'ppid':int(a[1]),'pgid':int(a[2]),'command':a[3]}
drivers=[pid for pid,r in processes.items() if r['command']==f'python target/native-stack-batch/build_fixed.py {args.family}']
if not drivers:
 print(json.dumps({'action':args.action,'status':'build_driver_absent_no_signal'}));raise SystemExit(0)
assert len(drivers)==1;driver=drivers[0];group=processes[driver]['pgid'];assert group==driver and group>1 and group!=os.getpgrp()
members=[pid for pid,r in processes.items() if r['pgid']==group]
for pid in members:
 current=pid;seen=set()
 while current!=driver:
  assert current not in seen and current in processes,(pid,'not an owned descendant');seen.add(current);current=processes[current]['ppid']
record={'action':args.action,'unix_time':time.time(),'driver_pid':driver,'process_group':group,'verified_member_pids':members,'scope':f'only dedicated fixed-protocol {args.family} compile driver and descendants'}
os.killpg(group,signal.SIGSTOP if args.action=='stop' else signal.SIGCONT)
with (base/'fixed-build-pauses.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
print(json.dumps(record))
