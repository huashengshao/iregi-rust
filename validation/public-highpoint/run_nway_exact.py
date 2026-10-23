"""Run the private whole-expression witness only after ROOT grants a lease."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import resource
import signal
import subprocess
import time


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    root=Path.cwd(); here=root/'validation/public-highpoint'
    build_path=here/'nway-build.json'; build=json.loads(build_path.read_text())
    assert build['status']=='passed'
    binary=root/build['exact_binary_path']
    assert sha(binary)==build['exact_binary_sha256']
    frozen=root/build['frozen_core_source']
    files={frozen/Path(name).relative_to('crates/iregi-rust'):value for name,value in build['library_source_hashes'].items()}
    files.update({binary:sha(binary), build_path:sha(build_path), Path(__file__):sha(Path(__file__))})
    assert all(sha(path)==expected for path,expected in files.items())
    result=here/'nway-exact-results.json'; log=here/'nway-exact.log'; record_path=here/'nway-exact-run.json'
    assert not any(p.exists() for p in [result,log,record_path])
    command=['taskset','-c','14',str(binary)]
    env=os.environ.copy(); env['IREGI_PRIMAL_SUM_MODE']='nway'; env['RAYON_NUM_THREADS']='1'
    record=dict(status='started',command=command,timeout_seconds=30,started_utc=datetime.now(timezone.utc).isoformat(),build_manifest_sha256=sha(build_path),binary_sha256=sha(binary),runner_sha256=sha(Path(__file__)),scope='Exact complete Atom equality only; synthetic diagnostic, no numerical high-point coverage or controlled performance claim.')
    record['license_scope']='Private user-supplied Symbolica license; license contents excluded from evidence.'
    record['environment_additions']={'IREGI_PRIMAL_SUM_MODE':'nway','RAYON_NUM_THREADS':'1'}
    record_path.write_text(json.dumps(record,indent=2)+'\n')
    start=time.monotonic()
    with result.open('wb') as out,log.open('wb') as err:
        child=subprocess.Popen(command,cwd=root,env=env,stdout=out,stderr=err,start_new_session=True)
        try:
            code=child.wait(timeout=30);record['status']='completed'
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGKILL);code=child.wait();record['status']='timeout'
    record.update(exit_code=code,elapsed_seconds=time.monotonic()-start,result_sha256=sha(result),log_sha256=sha(log),finished_utc=datetime.now(timezone.utc).isoformat())
    assert all(sha(path)==expected for path,expected in files.items())
    record['peak_child_rss_kib']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    record['guarded_files_unchanged']=len(files)
    if code==0:
        values=json.loads(result.read_text())
        assert len(values)==20 and len({row[0] for row in values})==20
        record['exact_equal_cases']=len(values)
        record['canonical_expression_sha256']={name:hashlib.sha256(expression.encode()).hexdigest() for name,expression in values}
        record['status']='passed'
    record_path.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2),flush=True)
    if record['status']!='passed':raise SystemExit(1)

if __name__=='__main__':main()
