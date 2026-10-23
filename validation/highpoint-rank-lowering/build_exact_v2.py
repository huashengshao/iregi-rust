"""Build only corrected tests; preserve the initial paired binaries and failure."""
from pathlib import Path
import hashlib,json,os,signal,subprocess,time
def sha(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
root=Path.cwd();here=root/'validation/highpoint-rank-lowering';build=json.loads((here/'build.json').read_text())
source=json.loads((here/'exact-v2-source.json').read_text());frozen=root/source['source_root']
assert build['status']=='passed'
destination=here/'exact-v2-build.json';assert not destination.exists()
guarded=dict(build['protected_input_hashes'])
guarded.update({str(Path(source['source_root'])/n):h for n,h in source['source_hashes'].items()})
for p in [Path(__file__),here/'build.json',here/'exact-v2-source.json',here/'chart_case.rs']:guarded[str(p.relative_to(root))]=sha(p)
assert all(sha(root/n)==h for n,h in guarded.items())
command=build['commands'][0]['command']
command=[p.replace('/rank-lowering/candidate/', '/rank-lowering/candidate-tests-v2/').replace('metadata=rank_lowering_candidate_tests','metadata=rank_lowering_candidate_tests_v2') for p in command]
binary=root/'target/public-highpoint/rank-lowering/candidate_tests_v2';command[command.index('-o')+1]=str(binary)
env=dict(os.environ,CARGO_MANIFEST_DIR=str(frozen/'crates/iregi-rust'),CARGO_CRATE_NAME='iregi_rust')
log=here/'exact-v2-build.log';assert not log.exists();started=time.monotonic();limit=100
with log.open('wb') as out:
    child=subprocess.Popen(command,cwd=root,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
    try:code=child.wait(timeout=limit);status='passed' if code==0 else 'failed'
    except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait();status='timeout'
changed={n:[h,sha(root/n)] for n,h in guarded.items() if sha(root/n)!=h}
record=dict(status=status,exit_code=code,command=command,timeout_seconds=limit,elapsed_seconds=time.monotonic()-started,
            protected_input_hashes=guarded,changed_inputs=changed,log_path=str(log.relative_to(root)),log_sha256=sha(log),
            binary_path=str(binary.relative_to(root)),binary_sha256=sha(binary) if code==0 else None,
            scope=source['scope'])
destination.write_text(json.dumps(record,indent=2)+'\n');print(status,flush=True);raise SystemExit(code!=0 or bool(changed))
