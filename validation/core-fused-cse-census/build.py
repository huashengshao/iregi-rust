#!/usr/bin/env python3
"""One private core and driver; existing native-object dependencies only."""
import datetime, hashlib, json, os, pathlib, subprocess, sys, time

ROOT = pathlib.Path.cwd()
HERE = ROOT / 'target/core-fused-cse-census'
CORE = HERE / 'core/crates/iregi-rust'
def sha(p): return hashlib.file_digest(open(p, 'rb'), 'sha256').hexdigest()
def read(p): return json.loads(pathlib.Path(p).read_text())
def save(p, x): pathlib.Path(p).write_text(json.dumps(x, indent=2)+'\n')

attempt = HERE / ('build-' + sys.argv[1])
attempt.mkdir(exist_ok=False)
manifest = read(HERE/'source-manifest.json')
closure_path = ROOT/manifest['closure_preparation']
assert sha(closure_path)==manifest['closure_preparation_sha256']
closure = read(closure_path)
supp = read(HERE/'supplemental-deps.json')
files = {ROOT/f['frozen']:f['sha256'] for f in closure['files']+supp['files']}
files.update({CORE/p:h for p,h in manifest['compiled_source_hashes'].items()})
for p in ['census.rs','source-manifest.json','supplemental-deps.json','thiserror-metadata.txt','thiserror-cargo-fingerprint.json','build.py']:
    files[HERE/p]=sha(HERE/p)
files[closure_path]=sha(closure_path)
assert sha(HERE/'thiserror-metadata.txt')==supp['metadata_sha256']
assert sha(HERE/'thiserror-cargo-fingerprint.json')==supp['fingerprint_sha256']
fingerprint=read(HERE/'thiserror-cargo-fingerprint.json')
assert json.loads(fingerprint['features'])==['default','std']
assert 'thiserror_impl-415c566ab8174dc4' in (HERE/'thiserror-metadata.txt').read_text()
event=next(e for e in supp['completed_metadata_and_proc_macro_events'] if e['target']['name']=='thiserror')
assert event['package_id'].endswith('thiserror@2.0.21') and event['features']==['default','std']
crate=pathlib.Path(event['manifest_path']).parent
for p,h in supp['cached_crate_source_hashes'].items(): files[crate/p]=h
def verify():
    for p,h in files.items(): assert sha(p)==h, f'changed input {p}'
verify()
deps=ROOT/'target/e6-direct-n2/deps'
extra=HERE/'supplemental-deps'
native=ROOT/'target/e6-direct-n2/native'
names={'iregi_masters':'libiregi_masters-f07797f04e91954e.rlib','symbolica':'libsymbolica-06e42762cabb77d9.rlib','serde':'libserde-b04ba25115fa19f8.rlib','serde_json':'libserde_json-d657c5438f354a41.rlib'}
externs={n:deps/f for n,f in names.items()}
externs['thiserror']=extra/'libthiserror-0527e2191ec3561c.rlib'
objects=subprocess.check_output(['ar','t',str(externs['thiserror'])],text=True).splitlines()
native_object=next(x for x in objects if x.endswith('.o'))
native_bytes=subprocess.check_output(['ar','p',str(externs['thiserror']),native_object])
assert native_bytes.startswith(b'\x7fELF'), 'thiserror archive is not native ELF'
common=['taskset','-c','8,9','rustc','--edition=2024','-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo','-L',f'dependency={deps}','-L',f'dependency={extra}','-L',f'native={native}']
record={'status':'building','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiler':subprocess.check_output(['rustc','-vV'],text=True),'supplemental_native_object':{'name':native_object,'magic_hex':native_bytes[:4].hex(),'sha256':hashlib.sha256(native_bytes).hexdigest()},'scope':'Exact Rational census only, no floating runtime or performance measurement; native-object closure reused without numerical dependency rebuild. Supplemental thiserror has metadata/proc-macro completed events and native ELF verification, no completed rlib event.','inputs':{str(p.relative_to(ROOT)):h for p,h in files.items()},'steps':[]}
save(attempt/'build.json',record)
def build(label,args,envadd):
    env=os.environ.copy();env.update(envadd)
    step={'label':label,'command':args,'environment':envadd,'timeout_seconds':180}
    record['steps'].append(step);save(attempt/'build.json',record)
    start=time.monotonic()
    with open(attempt/(label+'.log'),'w') as log:
        try: step['returncode']=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180).returncode
        except subprocess.TimeoutExpired: step['returncode']=None;step['timeout']=True
    step['seconds']=time.monotonic()-start
    save(attempt/'build.json',record)
    assert step['returncode']==0, f'{label} failed; retained log'
try:
    corelib=attempt/'libcore_cse.rlib'
    args=common+['--crate-name','core_cse','--crate-type','rlib',str(CORE/'src/lib.rs'),'-o',str(corelib)]
    for n,p in externs.items(): args+=['--extern',f'{n}={p}']
    build('core',args,{'CARGO_CRATE_NAME':'core_cse','CARGO_MANIFEST_DIR':str(CORE)})
    args=common+['--crate-name','core_fused_cse_census',str(HERE/'census.rs'),'-o',str(attempt/'census'),'--extern',f'core_cse={corelib}']
    for n in ['symbolica','serde_json']: args+=['--extern',f'{n}={externs[n]}']
    build('driver',args,{'CARGO_CRATE_NAME':'core_fused_cse_census'})
    verify()
    record.update(status='passed',inputs_unchanged=True,outputs={p.name:sha(p) for p in [corelib,attempt/'census']})
except Exception as error:
    record.update(status='failed',error=str(error))
finally:
    record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(attempt/'build.json',record)
print(json.dumps({'status':record['status'],'attempt':str(attempt),'steps':record['steps']}))
sys.exit(0 if record['status']=='passed' else 1)
