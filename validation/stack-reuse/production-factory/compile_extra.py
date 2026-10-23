from pathlib import Path
import hashlib,json,os,subprocess,sys,time
root=Path.cwd(); base=root/'target/stack-reuse-production'; variant,stage=sys.argv[1:]
assert variant in ['baseline','candidate']
assert stage in ['masters','master_tests','core_tests','core_lib','e6','master_integration','e6_capture']
folder=base/variant; folder.mkdir(exist_ok=True)
snapshot=base/'snapshot'; (snapshot/'target').mkdir(exist_ok=True)
master_root=(snapshot if variant=='baseline' else base/'candidate')/'crates/iregi-masters'
core_root=snapshot/'crates/iregi-rust'
deps=root/'target/cargo-build/debug/deps'
extern={'oneloop':deps/'liboneloop-8562c3cbbf948c0e.rlib','symbolica':deps/'libsymbolica-5cca42ee48491872.rlib'}
if stage in ['masters','master_tests','master_integration']:
    crate='iregi_masters'; manifest=master_root; source=master_root/'src/lib.rs'
    target=folder/('libiregi_masters.rlib' if stage=='masters' else ('master_integration' if stage=='master_integration' else 'master_tests'))
    if stage=='master_integration':
        source=master_root/'tests/masters.rs'
        extern['iregi_masters']=folder/'libiregi_masters.rlib'
else:
    crate='shifted_pentagon' if stage in ['e6','e6_capture'] else 'iregi_rust'
    manifest=core_root
    source=core_root/('tests/shifted_pentagon.rs' if stage in ['e6','e6_capture'] else 'src/lib.rs')
    target=folder/({'core_lib':'libiregi_rust.rlib','core_tests':'core_tests','e6':'shifted_pentagon','e6_capture':'e6_capture'}[stage])
    extern.update(iregi_masters=folder/'libiregi_masters.rlib',serde=deps/'libserde-fc3dcd4b8c210596.rlib',serde_json=deps/'libserde_json-3b583d0e8aa0facc.rlib',thiserror=deps/'libthiserror-b877110d28821624.rlib')
    if stage in ['e6','e6_capture']:extern['iregi_rust']=folder/'libiregi_rust.rlib'
    if stage=='e6_capture':source=base/'e6_capture.rs'
args=['rustc','--crate-name',crate,'--edition=2024',str(source),'-C','opt-level=2','-C',f'metadata=stack_reuse_{variant}_{stage}','-L',f'dependency={deps}','-L',f'dependency={folder}','-L',f'native={root}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
args+=['--crate-type','rlib'] if stage in ['masters','core_lib'] else ['--test']
for name,path in extern.items():args+=['--extern',f'{name}={path}']
args+=['-o',str(target)]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
env=os.environ.copy();env['CARGO_CRATE_NAME']=crate;env['CARGO_MANIFEST_DIR']=str(manifest)
report={'stage':stage,'variant':variant,'command':args,'environment':{k:env[k] for k in ['CARGO_CRATE_NAME','CARGO_MANIFEST_DIR']},'extern_hashes_before':{str(p.relative_to(root)):sha(p) for p in extern.values()}}
start=time.monotonic()
with (folder/f'{stage}-compile.log').open('w') as log:
    status=subprocess.call(args,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
report.update(exit_code=status,elapsed_seconds=time.monotonic()-start,extern_hashes_after={str(p.relative_to(root)):sha(p) for p in extern.values()})
if status==0:report['output_sha256']=sha(target)
(folder/f'{stage}-compile.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['stage','variant','exit_code','elapsed_seconds']}),flush=True)
if status:print((folder/f'{stage}-compile.log').read_text(),flush=True)
sys.exit(status)
