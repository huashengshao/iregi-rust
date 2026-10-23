"""Bounded paired build using the existing immutable dependency closure."""
from pathlib import Path
import hashlib, json, os, signal, subprocess, time

def sha(p):
    with p.open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()

root=Path.cwd(); here=root/'validation/highpoint-rank-lowering'
source_path=here/'source-final.json'; source=json.loads(source_path.read_text())
parent_path=root/'validation/public-highpoint/amplitude-vars-build-final.json'; parent=json.loads(parent_path.read_text())
recipes=json.loads((root/'validation/public-highpoint/amplitude-vars-build-qualified.json').read_text())
assert parent['status']=='passed'
destination=here/'build.json'; assert not destination.exists()
protected={str(p.relative_to(root)):sha(p) for p in [Path(__file__),source_path,parent_path,here/'exact_cases.rs',here/'coordinate_method.rs']}
for category in ['dependency_hashes','native_dependency_hashes','toolchain_dependency_hashes']: protected.update(parent[category])
for variant in ['baseline','candidate']:
    for name,value in source[variant+'_source_hashes'].items(): protected[str(Path(source[variant+'_root'])/name)]=value
assert all(sha(root/n)==h for n,h in protected.items())
old=root/'target/public-highpoint/amplitude-vars'
target=root/'target/public-highpoint/rank-lowering'
commands=[]
for variant,label,index in [('candidate','tests',2),('candidate','core',0),('candidate','public',1),('baseline','core',0),('baseline','public',1)]:
    command=[]
    for part in recipes['commands'][index]:
        part=part.replace(str(old/'source'), str(root/source[variant+'_root']))
        if part==str(old/'core_tests'): part=str(target/(variant+'_tests'))
        if part==str(old/'highpoint_public_frozen_native'): part=str(target/(variant+'_public'))
        if part==str(old/'libiregi_rust_verified.rlib'): part=str(target/('libiregi_rust_'+variant+'.rlib'))
        if part.startswith('iregi_rust='): part='iregi_rust='+str(target/('libiregi_rust_'+variant+'.rlib'))
        if part=='dependency='+str(old): part='dependency='+str(target)
        if part.startswith('metadata='): part='metadata=rank_lowering_'+variant+'_'+label
        command.append(part)
    commands.append(dict(variant=variant,label=label,command=command))
limit=240; started=time.monotonic(); runs=[]
for row in commands:
    remaining=limit-(time.monotonic()-started)
    if remaining<=0: break
    env=dict(os.environ,CARGO_MANIFEST_DIR=str(root/source[row['variant']+'_root']/'crates/iregi-rust'),CARGO_CRATE_NAME='iregi_rust')
    log=here/(row['variant']+'-'+row['label']+'-build.log'); assert not log.exists()
    print('starting',row['variant'],row['label'],flush=True)
    tick=time.monotonic()
    with log.open('wb') as out:
        child=subprocess.Popen(row['command'],cwd=root,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        try: code=child.wait(timeout=remaining); status='passed' if code==0 else 'failed'
        except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL); code=child.wait(); status='timeout'
    output=Path(row['command'][row['command'].index('-o')+1])
    runs.append(dict(**row,status=status,exit_code=code,elapsed_seconds=time.monotonic()-tick,
                     log_path=str(log.relative_to(root)),log_sha256=sha(log),
                     output_path=str(output.relative_to(root)),output_sha256=sha(output) if code==0 else None))
    print(row['variant'],row['label'],status,flush=True)
    if code: break
changed={n:[h,sha(root/n)] for n,h in protected.items() if sha(root/n)!=h}
record=dict(status='passed' if len(runs)==5 and all(x['status']=='passed' for x in runs) and not changed else 'failed',
            source_revision=source['revision'],source_manifest_sha256=sha(source_path),
            protected_input_hashes=protected,changed_inputs=changed,runs=runs,commands=commands,
            timeout_seconds=limit,elapsed_seconds=time.monotonic()-started,
            scope='Frozen current06706e2 source; private candidate only Cartesian rank-lowering plus tests. Baseline independently compiled. Historical matched112 Rust/3 native archives and recorded toolchain closure reused with no live search paths. Core opt0 debuginfo2 assertions/overflow enabled; publicdriver opt2; development preparation diagnostics only, no performance qualification.')
destination.write_text(json.dumps(record,indent=2)+'\n'); print(record['status'],flush=True)
raise SystemExit(record['status']!='passed')
