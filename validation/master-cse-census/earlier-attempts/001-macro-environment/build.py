from pathlib import Path
import hashlib,json,os,signal,subprocess,time
root=Path.cwd();base=root/'target/master-cse-census';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
prep=json.loads((base/'preparation.json').read_text());assert not (base/'build.json').exists(),'preserve previous build attempts'
for item in prep['artifacts'].values():assert sha(Path(item['archive']))==item['sha256']
for path,digest in prep['source_sha256'].items():assert sha(root/path)==digest,path
source=base/'source/census.rs';source_sha=sha(source);deps=root/'target/cargo-build/debug/deps'
cmd=['taskset','-c','20,21','rustc','--edition=2024','--crate-name','master_cse_census',str(source),'-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo','-L',f'dependency={deps}']
for path in prep['native_link_event']['linked_paths']:cmd+=['-L',path]
for name,item in prep['artifacts'].items():cmd+=['--extern',f'{name}={item["archive"]}']
cmd+=['-o',str(base/'census')]
record={'scope':'Concrete Complex<Rational> exact-only census, actual completed Cargo debug native-object dependencies; no ThinLTO/dependency rebuild/floating kernels','command':cmd,'source_sha256':source_sha,'preparation_sha256':sha(base/'preparation.json'),'runner_sha256':sha(Path(__file__)),'timeout_seconds':180,'started_unix_time':time.time()}
start=time.monotonic()
with (base/'build.log').open('w') as log:
 process=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:record['exit_code']=process.wait(timeout=180)
 except subprocess.TimeoutExpired:
  os.killpg(process.pid,signal.SIGTERM)
  try:process.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
  record.update(exit_code=process.returncode,timed_out=True)
record.update(elapsed_seconds=time.monotonic()-start,source_unchanged=sha(source)==source_sha,archives_unchanged=all(sha(Path(item['archive']))==item['sha256'] for item in prep['artifacts'].values()),build_log_sha256=sha(base/'build.log'))
if record['exit_code']==0:record.update(binary_sha256=sha(base/'census'),binary_bytes=(base/'census').stat().st_size)
(base/'build.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
raise SystemExit(0 if record['exit_code']==0 and record['source_unchanged'] and record['archives_unchanged'] else 1)
