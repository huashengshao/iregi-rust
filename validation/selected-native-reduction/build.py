"""Bounded direct builds against frozen completed debug native-object archives."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, signal, subprocess, sys, time

ROOT=Path.cwd(); HERE=ROOT/'target/selected-native-reduction'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
save=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n')
attempt=HERE/('build-'+sys.argv[1]); attempt.mkdir(exist_ok=False)
manifest=read(HERE/'source-manifest.json')
closure_path=ROOT/manifest['closure_path']; supplement_path=ROOT/manifest['supplemental_path']
assert sha(closure_path)==manifest['closure_sha256']
assert sha(supplement_path)==manifest['supplemental_sha256']
closure=read(closure_path); supplement=read(supplement_path)
bindings={ROOT/f['frozen']:f['sha256'] for f in closure['files']+supplement['files']}
bindings.update({HERE/p:h for p,h in manifest['private_sources'].items()})
bindings.update({ROOT/p:h for p,h in manifest['production_sources'].items()})
for p in [HERE/'source-manifest.json',HERE/'private.patch',HERE/'design.md',HERE/'build.py',closure_path,supplement_path,*sorted((HERE/'source').glob('*.rs'))]:bindings[p]=sha(p)
for p in ['thiserror-metadata.txt','thiserror-cargo-fingerprint.json']:
    bindings[ROOT/'target/core-fused-cse-census'/p]=sha(ROOT/'target/core-fused-cse-census'/p)
assert bindings[ROOT/'target/core-fused-cse-census/thiserror-metadata.txt']==supplement['metadata_sha256']
assert bindings[ROOT/'target/core-fused-cse-census/thiserror-cargo-fingerprint.json']==supplement['fingerprint_sha256']
def verify():
    for p,h in bindings.items():assert sha(p)==h, f'changed build input: {p}'
verify()
deps=ROOT/'target/e6-direct-n2/deps'; extra=ROOT/'target/core-fused-cse-census/supplemental-deps'; native=ROOT/'target/e6-direct-n2/native'
externs={n:deps/f for n,f in {
    'symbolica':'libsymbolica-06e42762cabb77d9.rlib',
    'oneloop':'liboneloop-ad2b1eccf125afee.rlib',
    'serde':'libserde-b04ba25115fa19f8.rlib',
    'serde_json':'libserde_json-d657c5438f354a41.rlib',
}.items()}
externs['thiserror']=extra/'libthiserror-0527e2191ec3561c.rlib'
native_checks={}
for name,p in externs.items():
    members=subprocess.check_output(['ar','t',str(p)],text=True).splitlines()
    object_name=next(m for m in members if m.endswith('.o'))
    data=subprocess.check_output(['ar','p',str(p),object_name])
    assert data.startswith(b'\x7fELF'),name
    native_checks[name]={'archive':str(p.relative_to(ROOT)),'archive_sha256':sha(p),'first_object':object_name,'magic':data[:4].hex(),'object_sha256':hashlib.sha256(data).hexdigest()}
common=['taskset','-c','20,21','rustc','--edition=2024','-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo','-L',f'dependency={deps}','-L',f'dependency={extra}','-L',f'dependency={attempt}','-L',f'native={native}']
record={'status':'building','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiler':subprocess.check_output(['rustc','-vV'],text=True),'scope':'private opt0 correctness only; no dependency rebuild, no global native feature, no D0 generated module, no timing qualification','input_sha256':{str(p.relative_to(ROOT)):h for p,h in bindings.items()},'native_object_checks':native_checks,'closure_source':str(closure_path.relative_to(ROOT)),'closure_sha256':sha(closure_path),'supplemental_provenance':str(supplement_path.relative_to(ROOT)),'steps':[]}
save(attempt/'build.json',record)
reuse=None
if len(sys.argv)>2:
    reuse_dir=HERE/('build-'+sys.argv[2]);reuse=read(reuse_dir/'build.json')
    assert [s['label'] for s in reuse['steps'][:3]]==['selected_masters','selected_baseline','selected_candidate']
    assert all(s['returncode']==0 for s in reuse['steps'][:3])
    # All compiled library source and dependency inputs must still be identical.
    # Only the failed probe fixture and this reuse-aware build driver may differ.
    exceptions={'target/selected-native-reduction/build.py','target/selected-native-reduction/source/core_probe.rs'}
    for p,h in reuse['input_sha256'].items():
        if p not in exceptions:assert sha(ROOT/p)==h, f'changed reused-library input: {p}'
    record['reuse']={'prior_build':str((reuse_dir/'build.json').relative_to(ROOT)),'prior_build_sha256':sha(reuse_dir/'build.json'),'allowed_changes':sorted(exceptions),'scope':'only three completed library artifacts; prior combined-probe compile failed before code generation','artifacts':{}}
    for name in ['libiregi_masters_selected.rlib','libselected_baseline.rlib','libselected_candidate.rlib']:
        old=reuse_dir/name;before=sha(old);shutil.copy2(old,attempt/name);assert sha(attempt/name)==sha(old)==before
        record['reuse']['artifacts'][name]={'sha256':before,'bytes':old.stat().st_size}
        bindings[old]=before
    bindings[reuse_dir/'build.json']=sha(reuse_dir/'build.json')
    for step in reuse['steps'][:3]:bindings[reuse_dir/(step['label']+'.log')]=sha(reuse_dir/(step['label']+'.log'))
    record['input_sha256']={str(p.relative_to(ROOT)):h for p,h in bindings.items()}
    save(attempt/'build.json',record)
def build(label,args,envadd,limit):
    env=os.environ.copy();env.update(envadd)
    step={'label':label,'command':args,'environment':envadd,'timeout_seconds':limit};record['steps'].append(step);save(attempt/'build.json',record)
    started=time.monotonic()
    with (attempt/(label+'.log')).open('w') as log:
        process=subprocess.Popen(args,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        step['owned_pid']=process.pid;save(attempt/'build.json',record)
        try:step['returncode']=process.wait(timeout=limit)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=3)
            except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
            step.update(returncode=process.returncode,timeout=True)
    step['seconds']=time.monotonic()-started;save(attempt/'build.json',record)
    print(json.dumps({k:v for k,v in step.items() if k not in ['command','environment']}),flush=True)
    assert step['returncode']==0, f'{label} failed; log preserved'
def extras(args,names):
    for n in names:args+=['--extern',f'{n}={externs[n]}']
    return args
try:
    master_dir=HERE/'copied/crates/iregi-masters'
    masters=attempt/'libiregi_masters_selected.rlib'
    args=extras(common+['--crate-name','iregi_masters','--crate-type','rlib',str(master_dir/'src/lib.rs'),'-C','metadata=selected_native_private_masters','-o',str(masters)],['symbolica','oneloop'])
    if reuse is None:build('selected_masters',args,{'CARGO_CRATE_NAME':'iregi_masters','CARGO_MANIFEST_DIR':str(master_dir)},180)
    externs['iregi_masters']=masters
    core_dir=HERE/'copied/crates/iregi-rust'
    for name,selected in [('selected_baseline',False),('selected_candidate',True)]:
        output=attempt/f'lib{name}.rlib'
        args=common+['--crate-name',name,'--crate-type','rlib',str(core_dir/'src/lib.rs'),'-C',f'metadata={name}_debug_private','-o',str(output)]
        if selected:args+=['--cfg','private_selected_native']
        extras(args,['symbolica','iregi_masters','serde','thiserror'])
        if reuse is None:build(name,args,{'CARGO_CRATE_NAME':'iregi_rust','CARGO_MANIFEST_DIR':str(core_dir)},180)
        externs[name]=output
    args=extras(common+['--crate-name','selected_native_qualification',str(HERE/'source/probe.rs'),'-o',str(attempt/'probe')],['selected_baseline','selected_candidate','iregi_masters','symbolica','oneloop','serde','serde_json'])
    build('probe',args,{'CARGO_CRATE_NAME':'selected_native_qualification'},600)
    verify()
    record.update(status='passed',inputs_unchanged=True,outputs={p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in [masters,externs['selected_baseline'],externs['selected_candidate'],attempt/'probe']})
except Exception as error:record.update(status='failed',error=str(error))
finally:
    record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(attempt/'build.json',record)
print(json.dumps({'status':record['status'],'attempt':str(attempt),'error':record.get('error')}))
sys.exit(0 if record['status']=='passed' else 1)
