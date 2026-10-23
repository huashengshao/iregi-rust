from pathlib import Path
import hashlib,json,os,subprocess,time,sys
root=Path.cwd();base=root/'target/cli-coefficient-stack';binary=base/'probe'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
compiled=json.loads((base/'compile.json').read_text());assert compiled['exit_code']==0
assert sha(binary)==compiled['binary_sha256']
source_before={str(p.relative_to(base)):sha(p) for p in sorted((base/'source').glob('*.rs'))}
assert source_before==compiled['source_after']
assets={str(p.relative_to(base)):sha(p) for p in sorted((base/'assets').rglob('*')) if p.is_file()}
runroot=base/'qualification';runroot.mkdir(exist_ok=False)
record={'schema_version':1,'scope':'Exact paired physical coefficient correctness and root storage; no timing gate','binary_sha256':sha(binary),'compile_manifest_sha256':sha(base/'compile.json'),'runner_sha256':sha(Path(__file__)),'sources':source_before,'assets':assets,'runs':[]}
(runroot/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
for case in ['ggh','gghh','gghhh','gggg-up']:
 out=runroot/case;command=['/run/current-system/sw/bin/time','-f','elapsed_seconds=%e\nmaximum_rss_kib=%M','-o',str(runroot/(case+'.resource.txt')),'timeout','240','taskset','-c','8',str(binary),case,str(out)]
 started=time.monotonic();print('START '+case,flush=True)
 with (runroot/(case+'.log')).open('w') as log: code=subprocess.call(command,stdout=log,stderr=subprocess.STDOUT)
 entry={'case':case,'command':command,'returncode':code,'elapsed_seconds':time.monotonic()-started,'log_sha256':sha(runroot/(case+'.log'))}
 if (out/'outputs.json').exists():
  result=json.loads((out/'outputs.json').read_text());entry.update(status=result['status'],structure=result['structure'],output_sha256=sha(out/'outputs.json'))
 else:entry['status']='timeout' if code==124 else 'failed'
 record['runs'].append(entry);(runroot/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(entry),flush=True)
 if code:break
assert sha(binary)==record['binary_sha256']
assert source_before=={str(p.relative_to(base)):sha(p) for p in sorted((base/'source').glob('*.rs'))}
assert assets=={str(p.relative_to(base)):sha(p) for p in sorted((base/'assets').rglob('*')) if p.is_file()}
record['inputs_unchanged']=True;record['status']='passed' if len(record['runs'])==4 and all(r['returncode']==0 and r['status']=='passed' for r in record['runs']) else 'failed_or_incomplete'
(runroot/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(record['status'],flush=True)
raise SystemExit(0 if record['status']=='passed' else 1)
