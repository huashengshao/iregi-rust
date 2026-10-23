"""One shared adapter build. Invoke only after ROOT grants this frozen recipe."""
from pathlib import Path
import datetime,hashlib,json,os,signal,subprocess,sys,time

ROOT=Path.cwd();HERE=ROOT/'target/selected-native-optimized'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
save=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n')
audit=read(HERE/'closure-audit.json')
assert audit['status']=='source-and-ABI-audit-passed-no-build'
assert sha(HERE/'closure-audit.json')=='7faf196a9b4befa33cb7d55d3dc3dd4d8917c6ddba0ee1a5a93716b6086c72c8'
attempt=HERE/'shared'/('build-'+sys.argv[1]);attempt.mkdir(parents=True,exist_ok=False)
crate=ROOT/'target/selected-native-reduction/copied/crates/iregi-masters'
bindings={Path(p):h for p,h in audit['verified_archive_and_sysroot_bindings'].items()}
bindings.update({ROOT/p:h for p,h in audit['numerical_source_files'].items()})
bindings.update({ROOT/p:h for p,h in audit['current_master_sources'].items()})
bindings.update({crate/p:h for p,h in audit['selected_private_master_sources'].items()})
for p in [HERE/'closure-audit.json',HERE/'plan.md',HERE/'build_shared.py',ROOT/audit['selected_private_source_qualification']]:bindings[p]=sha(p)
assert sha(ROOT/audit['selected_private_source_qualification'])==audit['selected_private_source_qualification_sha256']
def verify():
    for p,h in bindings.items():assert sha(p)==h,f'changed input: {p}'
verify()
compiler=subprocess.check_output(['rustc','-vV'],text=True).strip();assert compiler==audit['compiler']
deps=ROOT/'target/benchmark/dependency-closures/6b24c03-complete-kinds/deps'
output=attempt/'libiregi_masters_selected.rlib'
command=['taskset','-c','20,21','rustc','--edition=2024','--crate-name','iregi_masters','--crate-type','rlib',str(crate/'src/lib.rs'),
    '-C','opt-level=3','-C','codegen-units=16','-C','embed-bitcode=yes','-C','debuginfo=0','-C','debug-assertions=no','-C','overflow-checks=no',
    '-C','metadata=shared_current_selected_master_opt3','-L',f'dependency={deps}','-L',f'native={ROOT/audit["native_search_path"]}',
    '--extern',f'symbolica={ROOT/audit["runtime_artifacts"]["symbolica"]["path"]}',
    '--extern',f'oneloop={ROOT/audit["runtime_artifacts"]["oneloop"]["path"]}','-o',str(output)]
env=os.environ.copy();env.update(CARGO_CRATE_NAME='iregi_masters',CARGO_MANIFEST_DIR=str(crate))
record={'status':'building','scope':'single current public master adapter shared by approved experiments; no dependency rebuild or native D0 module','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timeout_seconds':180,'command':command,'compiler':compiler,'closure_receipt_sha256':sha(HERE/'closure-audit.json'),'inputs':{str(p):h for p,h in bindings.items()},'environment':{k:env.get(k) for k in ['CARGO_CRATE_NAME','CARGO_MANIFEST_DIR','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER']}}
save(attempt/'build.json',record);started=time.monotonic()
with (attempt/'compiler.log').open('w') as log:
    process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    record['owned_process_group']=process.pid;save(attempt/'build.json',record)
    try:record['returncode']=process.wait(timeout=180)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid,signal.SIGTERM)
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
        record.update(returncode=process.returncode,timeout=True)
record.update(elapsed_seconds=time.monotonic()-started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='compiled' if record['returncode']==0 else 'failed')
save(attempt/'build.json',record) # Terminal state precedes potentially failing guards.
try:
    verify();record['inputs_unchanged']=True
    if record['returncode']==0:
        record.update(status='passed',artifact={'path':str(output.relative_to(ROOT)),'sha256':sha(output),'bytes':output.stat().st_size})
except Exception as error:record.update(status='failed',guard_error=str(error))
save(attempt/'build.json',record)
if record['status']=='passed':
    accepted=HERE/'shared/accepted.json';assert not accepted.exists(),'preserve accepted adapter receipt'
    save(accepted,{'status':'accepted-shared-opt3-adapter','build_record':str((attempt/'build.json').relative_to(ROOT)),'build_sha256':sha(attempt/'build.json'),'artifact':record['artifact'],'source_qualification':audit['selected_private_source_qualification'],'source_qualification_sha256':audit['selected_private_source_qualification_sha256']})
print(json.dumps({'status':record['status'],'seconds':record['elapsed_seconds'],'artifact':record.get('artifact')}))
sys.exit(0 if record['status']=='passed' else 1)
