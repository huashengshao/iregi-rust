"""Run exact alias-use maps and retained lazy-activation tests on the private build."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import os
import resource
import signal
import subprocess
import time


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    root=Path.cwd();here=root/'validation/public-highpoint';build_path=here/'use-dedup-build.json';build=json.loads(build_path.read_text())
    assert build['status']=='passed' and build['exit_codes']==[0,0,0] and not build['changed_inputs']
    binary=root/build['exact_binary_path'];assert sha(binary)==build['exact_binary_sha256']
    frozen=root/build['frozen_core_source'];guards={frozen/Path(name).relative_to('crates/iregi-rust'):value for name,value in build['library_source_hashes'].items()}
    guards.update({root/name:value for name,value in build['protected_input_hashes'].items()})
    guards.update({binary:sha(binary),build_path:sha(build_path),Path(__file__):sha(Path(__file__))})
    assert all(sha(p)==value for p,value in guards.items())
    result=here/'use-dedup-exact-results.json';log=here/'use-dedup-exact.log';record_path=here/'use-dedup-exact-run.json'
    assert not any(p.exists() for p in [result,log,record_path])
    command=['taskset','-c','14',str(binary)]
    env=os.environ.copy();env['IREGI_ALIAS_USE_VERIFY']='1';env['RAYON_NUM_THREADS']='1';env.pop('IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE',None)
    record=dict(status='started',command=command,timeout_seconds=30,started_utc=datetime.now(timezone.utc).isoformat(),build_manifest_sha256=sha(build_path),binary_sha256=sha(binary),runner_sha256=sha(Path(__file__)),environment_additions={'IREGI_ALIAS_USE_VERIFY':'1','RAYON_NUM_THREADS':'1'},environment_removals=['IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE'],license_scope='Private user-supplied license; key excluded.',scope='17 exact normalized alias-use map cases plus three retained numeric-lazy/master-activation semantic tests; no full high-point numerical acceptance or performance gate.')
    record_path.write_text(json.dumps(record,indent=2)+'\n');start=time.monotonic()
    with result.open('wb') as out,log.open('wb') as err:
        child=subprocess.Popen(command,cwd=root,env=env,stdout=out,stderr=err,start_new_session=True)
        try:code=child.wait(timeout=30);record['status']='completed'
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait();record['status']='timeout'
    record.update(exit_code=code,elapsed_seconds=time.monotonic()-start,result_sha256=sha(result),log_sha256=sha(log),finished_utc=datetime.now(timezone.utc).isoformat(),peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    assert all(sha(p)==value for p,value in guards.items());record['guarded_files_unchanged']=len(guards)
    if code==0:
        rows=json.loads(result.read_text());assert len(rows)==20 and len({name for name,_ in rows})==20
        record.update(status='passed',checked_cases=20,result_text_sha256={name:hashlib.sha256(text.encode()).hexdigest() for name,text in rows})
    record_path.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2),flush=True)
    if record['status']!='passed':raise SystemExit(1)

if __name__=='__main__':main()
