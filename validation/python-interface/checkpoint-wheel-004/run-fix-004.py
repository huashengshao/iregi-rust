"""Bounded renderer qualification commands; never records credential environments."""
from __future__ import annotations
import hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
base=Path('target/python-interface-build')
mode=sys.argv[1]
assert mode in ('cbor','cbor-owner','cbor-owner-2','wheel')
name={'cbor':'cbor-004','cbor-owner':'cbor-owner-004','cbor-owner-2':'cbor-owner-004-2','wheel':'wheel-004'}[mode]
if mode in ('cbor','cbor-owner','cbor-owner-2'):
    command=['cargo','test','--locked','--offline','-p','linnest','--lib','numeric_cbor_regression','--jobs','8','--','--nocapture']
    if mode in ('cbor-owner','cbor-owner-2'):
        command=['cargo','test','--manifest-path','target/python-render-fix/test-owner/Cargo.toml','--locked','--offline','--features','svg','--lib','numeric_cbor_regression','--jobs','8','--','--nocapture']
    cap=180
    rss_cap=16*1024**3
else:
    command=list(json.loads((base/'wheel-003-start.json').read_text())['command'])
    command[command.index('--out')+1]='target/python-interface-build/wheels-004'
    cap=1200
    rss_cap=64*1024**3
baseline=json.loads((base/'wheel-003-start.json').read_text())['input_files']
for path,sha in baseline.items():
    if path not in ('Cargo.toml','Cargo.lock'):
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
files=set(baseline)
if mode in ('cbor-owner','cbor-owner-2'):
    files.update(str(p) for p in Path('target/python-render-fix/test-owner').rglob('*') if p.is_file())
for folder in ('dependencies/linnest','dependencies/linnest-patches'):
    files.update(str(p) for p in Path(folder).rglob('*') if p.is_file())
files.update(str(p) for p in Path('tests/python').glob('test_tirust_*.py'))
before={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sorted(files)}
start=time.time();tick=time.monotonic()
receipt={'scope':'actual upstream native SVG typed-CBOR owner repair; ordinary numerical code unchanged','command':command,'cap_seconds':cap,'jobs':8,'sampled_whole_pg_rss_cap_bytes':rss_cap,'input_files':before,'started_unix':start,'lock_sha256':before['Cargo.lock'],'baseline_wheel_preserved':True}
(base/f'{name}-start.json').write_text(json.dumps(receipt,indent=2)+'\n')
def group(pgid):
    out=subprocess.run(['ps','-g',str(pgid),'-o','pid=,ppid=,rss=,pcpu=,comm='],capture_output=True,text=True).stdout
    rows=[]
    for line in out.splitlines():
        pid,parent,rss,cpu,comm=line.split(maxsplit=4)
        rows.append({'pid':int(pid),'ppid':int(parent),'rss_bytes':int(rss)*1024,'cpu_percent':float(cpu),'command':comm})
    return rows
status='completed';peak=0
with (base/f'{name}.log').open('w') as log,(base/f'{name}-resources.jsonl').open('w') as resources:
    process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (base/f'{name}-pgid.json').write_text(json.dumps({'pid':process.pid,'pgid':process.pid})+'\n')
    next_sample=0
    while process.poll() is None:
        elapsed=time.monotonic()-tick
        if elapsed>=cap:
            status='timeout';os.killpg(process.pid,signal.SIGKILL);break
        if elapsed>=next_sample:
            rows=group(process.pid);rss=sum(r['rss_bytes'] for r in rows);peak=max(peak,rss)
            resources.write(json.dumps({'seconds':elapsed,'whole_pg_rss_bytes':rss,'processes':rows})+'\n');resources.flush()
            if rss>rss_cap:
                status='rss_limit';os.killpg(process.pid,signal.SIGKILL);break
            next_sample=elapsed+5
        time.sleep(.25)
    code=process.wait()
changed=[p for p,sha in before.items() if not Path(p).exists() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=sha]
receipt.update({'seconds':time.monotonic()-tick,'status':status,'exit_code':code,'peak_sampled_whole_pg_rss_bytes':peak,'changed_inputs':changed,'source_unchanged':not changed,'remaining_owned_processes':group(process.pid),'guarded_input_files':len(before)})
(base/f'{name}.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='input_files'}))
sys.exit(0 if code==0 and status=='completed' and not changed and not receipt['remaining_owned_processes'] else 1)
