from pathlib import Path
import hashlib,json,os,signal,subprocess,time

root=Path.cwd();base=root/'target/e6-direct-n2-typed';closure=root/'target/e6-direct-n2'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
prep=json.loads((closure/'preparation.json').read_text())
assert not (base/'build.json').exists(), 'preserve build attempts'
for item in prep['files']:
    assert sha(root/item['frozen'])==item['sha256'],item['frozen']
sources={str(p.relative_to(root)):sha(p) for p in sorted((base/'source').iterdir()) if p.is_file()}
(base/'source-manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
cmd=['taskset','-c','18,19','rustc','--edition=2024','--crate-name','e6_direct_n2_typed',
     str(base/'source/typed.rs'),'-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo',
     '-L',f'dependency={closure/"deps"}','-L',f'native={closure/"native"}']
for name,item in prep['artifacts'].items():cmd+=['--extern',f'{name}={root/item["frozen"]}']
cmd+=['-o',str(base/'validate')]
env=os.environ.copy();env['CARGO_CRATE_NAME']='e6_direct_n2_typed'
record={'scope':'Typed validation of unchanged E6 N2 candidate; retained native-object dependencies; no production change',
        'command':cmd,'compile_environment_overrides':{'CARGO_CRATE_NAME':env['CARGO_CRATE_NAME']},
        'sources':sources,'preparation_sha256':sha(base/'preparation.json'),
        'runner_sha256':sha(Path(__file__)),'timeout_seconds':180,'started_unix_time':time.time()}
start=time.monotonic()
with (base/'build.log').open('w') as log:
    p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
    record['pid']=p.pid
    (base/'active-build.json').write_text(json.dumps({'pid':p.pid,'command':cmd})+'\n')
    try:record['exit_code']=p.wait(timeout=180)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid,signal.SIGTERM)
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
        record.update(exit_code=p.returncode,timed_out=True)
record.update(elapsed_seconds_diagnostic=time.monotonic()-start,
              sources_unchanged=all(sha(root/path)==digest for path,digest in sources.items()),
              closure_unchanged=all(sha(root/x['frozen'])==x['sha256'] for x in prep['files']),
              build_log_sha256=sha(base/'build.log'))
if record['exit_code']==0:record.update(binary_sha256=sha(base/'validate'),binary_bytes=(base/'validate').stat().st_size)
(base/'build.json').write_text(json.dumps(record,indent=2)+'\n')
(base/'active-build.json').unlink()
print(json.dumps(record,indent=2))
raise SystemExit(0 if record['exit_code']==0 and record['sources_unchanged'] and record['closure_unchanged'] else 1)
