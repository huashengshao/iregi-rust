"""Fail-closed exact witnesses and focused semantics for the private candidate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import signal
import subprocess
import time


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    build_path = here / 'amplitude-vars-build-final.json'
    build = json.loads(build_path.read_text())
    assert build['status'] == 'passed'
    destination = here / 'amplitude-vars-checks.json'
    assert not destination.exists()
    frozen = root / build['frozen_source_root']
    protected = {str((frozen / n).relative_to(root)):v for n,v in build['source_hashes'].items()}
    protected.update(build['protected_input_hashes'])
    protected.update(build['dependency_hashes'])
    protected.update(build.get('native_dependency_hashes',{}))
    for name in ['test_binary','exact_binary']:
        assert sha(root / build[name+'_path']) == build[name+'_sha256']
        protected[build[name+'_path']] = build[name+'_sha256']
    for p in [Path(__file__),build_path,here/'nway-exact-results.json']:
        protected[str(p.relative_to(root))] = sha(p)
    assert all(sha(root/n)==v for n,v in protected.items())
    env = os.environ.copy()
    env.update(IREGI_PRIMAL_SUM_MODE='verify',IREGI_AMPLITUDE_VARIABLE_MODE='verify',RAYON_NUM_THREADS='1',RUST_TEST_THREADS='1')
    for name in ['IREGI_ALIAS_USE_VERIFY','IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE','IREGI_MASTER_AMPLITUDE_MODE']:
        env.pop(name,None)
    listed = subprocess.check_output([str(root/build['test_binary_path']),'--list'],text=True,env=env,timeout=30)
    names = re.findall(r'^(\S+): test$',listed,re.M)
    assert len(names)==174
    listing = here/'amplitude-vars-tests-list.txt';assert not listing.exists();listing.write_text(listed)
    rows=[]
    for label,key,args,limit,expected in [
        ('exact','exact_binary_path',[],30,82),
        ('stability','test_binary_path',['stability::','--test-threads=1','--nocapture'],120,38),
        ('execution','test_binary_path',['execution::','--test-threads=1','--nocapture'],120,35),
    ]:
        log=here/('amplitude-vars-'+label+'.log');out=here/'amplitude-vars-exact-results.json' if label=='exact' else log
        assert not log.exists() and (out==log or not out.exists())
        command=['taskset','-c','14',str(root/build[key]),*args]
        started=time.monotonic()
        with log.open('wb') as stream:
            output=out.open('wb') if out!=log else stream
            try:
                child=subprocess.Popen(command,env=env,cwd=root,stdout=output,stderr=stream,start_new_session=True)
                try:
                    code=child.wait(timeout=limit);status='passed' if code==0 else 'failed'
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid,signal.SIGKILL);code=child.wait();status='timeout'
            finally:
                if output!=stream:output.close()
        row=dict(label=label,command=command,timeout_seconds=limit,elapsed_seconds=time.monotonic()-started,status=status,exit_code=code,
                 log_path=str(log.relative_to(root)),log_sha256=sha(log))
        if code==0:
            if label=='exact':
                result=json.loads(out.read_text())
                retained=result['retained_amplitude_cases'];extra=result['variable_and_extra_amplitude_cases']
                assert retained==json.loads((here/'nway-exact-results.json').read_text())
                assert len(retained)==len(dict(retained))==20
                assert len(extra)==len(dict(extra))==62
                assert sum(k.startswith('set_') for k,_ in extra)==48
                assert sum(k.startswith('amplitude_') for k,_ in extra)==14
                row.update(result_path=str(out.relative_to(root)),result_sha256=sha(out),checked_cases=82,
                           exact_set_cases=48,extra_full_amplitude_cases=14,retained_full_amplitude_cases=20)
            else:
                text=log.read_text()
                summary=re.findall(r'^test result: ok\. (\d+) passed; 0 failed; 0 ignored; 0 measured; (\d+) filtered out; finished in [0-9.]+s$',text,re.M)
                actual=re.findall(r'^test (\S+) \.\.\.',text,re.M)
                wanted={n for n in names if n.startswith(label+'::')}
                assert len(summary)==1 and tuple(map(int,summary[0]))==(expected,174-expected)
                assert len(actual)==expected and set(actual)==wanted
                row['checked_cases']=expected
        rows.append(row)
        if code:break
    changed={n:[v,sha(root/n)] for n,v in protected.items() if sha(root/n)!=v}
    record=dict(status='passed' if len(rows)==3 and all(r['status']=='passed' for r in rows) and not changed else 'failed',
                build_manifest_sha256=sha(build_path),protected_input_hashes=protected,changed_inputs=changed,runs=rows,
                environment={'IREGI_PRIMAL_SUM_MODE':'verify','IREGI_AMPLITUDE_VARIABLE_MODE':'verify','RAYON_NUM_THREADS':'1','RUST_TEST_THREADS':'1'},
                test_listing_sha256=sha(listing),finished_utc=datetime.now(timezone.utc).isoformat(),
                scope='48 complete expected variable sets,34 complete canonical amplitude/error witnesses,38 stability and35 execution tests. Independent recursive legacy collector; both verify modes required by exact probe. No N6 arrays or performance qualification.')
    destination.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ['status','runs','changed_inputs']}),flush=True)
    if record['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
