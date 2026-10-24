"""Current live Cargo build only, with whole-group bounds and a postprocess reserve."""
from __future__ import annotations
import hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
root=Path.cwd();base=root/'target/public-six-point-cargo';index=int(sys.argv[1]);assert index in (0,1)
grant=json.loads((base/'grant.json').read_text());prep=json.loads((base/'preparation.json').read_text());freeze=json.loads((base/'source-freeze.json').read_text())
sha=lambda path:hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
assert sha(base/'source-freeze.json')==grant['source_freeze_sha256'];assert sha(base/'preparation.json')==grant['preparation_sha256']
for path,row in freeze['files'].items():assert sha(root/path)==row['sha256'],path
for name,row in prep['tools'].items():assert sha(Path(row['path']))==row['sha256'],name
for key,value in prep['selected_environment_only'].items():assert os.environ.get(key)==value,key
if index==1:
    previous=json.loads((base/'lib-no-run.json').read_text());assert previous['pass'] and previous['terminal_before_hash']
label=['lib-no-run','example-build'][index];command=grant['commands'][index];cap=grant['overall_cap_seconds'][index];execution_cap=grant['execution_cap_seconds'][index];rss_cap=grant['sampled_whole_pg_rss_caps_bytes'][index]
started=time.time();tick=time.monotonic()
start={'scope':'actual current locked Cargo; compile only; no tests/listing/example execution','command':command,'started_unix':started,'overall_cap_seconds':cap,'execution_cap_seconds':execution_cap,'postprocess_reserve_seconds':grant['postprocess_reserve_seconds'],'sampled_whole_pg_rss_cap_bytes':rss_cap,'source_freeze_sha256':grant['source_freeze_sha256'],'grant_sha256':sha(base/'grant.json'),'preparation_sha256':grant['preparation_sha256'],'profile_overrides':False,'runtime_execution_authorized':False}
(base/f'{label}-start.json').write_text(json.dumps(start,indent=2)+'\n')
def group(pgid):
    out=subprocess.run(['ps','-g',str(pgid),'-o','pid=,ppid=,stat=,rss=,pcpu=,comm='],capture_output=True,text=True).stdout
    result=[]
    for line in out.splitlines():
        pid,ppid,stat,rss,cpu,comm=line.split(maxsplit=5);result.append({'pid':int(pid),'ppid':int(ppid),'state':stat,'rss_bytes':int(rss)*1024,'cpu_percent':float(cpu),'command':comm})
    return result

def kill(pgid):
    try:os.killpg(pgid,signal.SIGKILL)
    except ProcessLookupError:pass

def snapshot(pgid,elapsed):
    rows=[]
    for row in group(pgid):
        if row['command']!='rustc':continue
        try:
            argv=[part.decode(errors='replace') for part in Path(f"/proc/{row['pid']}/cmdline").read_bytes().split(b'\0') if part]
            rows.append({'pid':row['pid'],'argv':argv,'affinity':sorted(os.sched_getaffinity(row['pid']))})
        except (FileNotFoundError,ProcessLookupError):pass
    return {'seconds':elapsed,'actual_rustc_commands':rows}
status='completed';peak=0
with (base/f'{label}-stdout.jsonl').open('w') as out,(base/f'{label}-stderr.log').open('w') as err,(base/f'{label}-resources.jsonl').open('w') as samples:
    p=subprocess.Popen(command,stdout=out,stderr=err,start_new_session=True)
    (base/f'{label}-pgid.json').write_text(json.dumps({'pid':p.pid,'pgid':p.pid})+'\n')
    next_sample=0;checkpoints=iter((30,120,300,600));next_checkpoint=next(checkpoints,None)
    while p.poll() is None:
        elapsed=time.monotonic()-tick
        if elapsed>=execution_cap:status='timeout';kill(p.pid);break
        if elapsed>=next_sample:
            rows=group(p.pid);rss=sum(row['rss_bytes'] for row in rows);peak=max(peak,rss)
            samples.write(json.dumps({'seconds':elapsed,'whole_pg_rss_bytes':rss,'processes':rows})+'\n');samples.flush()
            if rss>rss_cap:status='rss_limit';kill(p.pid);break
            if next_checkpoint is not None and elapsed>=next_checkpoint:
                (base/f'{label}-checkpoint-{next_checkpoint:04d}.json').write_text(json.dumps(snapshot(p.pid,elapsed),indent=2)+'\n');next_checkpoint=next(checkpoints,None)
            next_sample=elapsed+5
        time.sleep(.25)
    code=p.wait()
execution_seconds=time.monotonic()-tick
remaining=group(p.pid)
if remaining:
    kill(p.pid)
    cleanup_deadline=min(tick+cap-10,time.monotonic()+8)
    while remaining and time.monotonic()<cleanup_deadline:time.sleep(.1);remaining=group(p.pid)
terminal_before_hash=not remaining
terminal={'status':status,'exit_code':code,'execution_seconds':execution_seconds,'remaining_owned_processes':remaining,'terminal_before_hash':terminal_before_hash}
(base/f'{label}-terminal.json').write_text(json.dumps(terminal,indent=2)+'\n')
changed=[];tool_changes=[];artifacts=[];targets={}
if terminal_before_hash:
    changed=[path for path,row in freeze['files'].items() if not (root/path).exists() or sha(root/path)!=row['sha256']]
    tool_changes=[name for name,row in prep['tools'].items() if sha(Path(row['path']))!=row['sha256']]
    for line in (base/f'{label}-stdout.jsonl').read_text().splitlines():
        try:o=json.loads(line)
        except json.JSONDecodeError:continue
        if o.get('reason')!='compiler-artifact':continue
        artifacts.append(o)
        name=o['target']['name']
        if name in ('symbolica','numerica','graphica','oneloop','iregi_masters','iregi_rust','six_point'):
            files={}
            for path in o['filenames']:
                q=Path(path)
                if q.is_file():files[path]={'bytes':q.stat().st_size,'sha256':sha(q)}
            targets.setdefault(name,[]).append({'package_id':o['package_id'],'features':o['features'],'profile':o['profile'],'fresh':o['fresh'],'kind':o['target']['kind'],'executable':o['executable'],'files':files})
(base/f'{label}-artifacts.json').write_text(json.dumps({'artifacts':artifacts,'selected_current_artifact_identities':targets},indent=2)+'\n')
seconds=time.monotonic()-tick
result={**start,**terminal,'seconds_including_cleanup_hashes_receipts':seconds,'peak_sampled_whole_pg_rss_bytes':peak,'source_files':len(freeze['files']),'changed_source_inputs':changed,'changed_tools':tool_changes,'guard_check_performed':terminal_before_hash,'within_overall_cap':seconds<=cap,'compiler_artifact_count':len(artifacts),'selected_current_artifact_identities':targets,'pass':status=='completed' and code==0 and terminal_before_hash and not changed and not tool_changes and seconds<=cap}
(base/f'{label}.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='selected_current_artifact_identities'}));sys.exit(0 if result['pass'] else 1)
