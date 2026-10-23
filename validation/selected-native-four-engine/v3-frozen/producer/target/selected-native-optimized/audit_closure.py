"""Source/metadata/hash audit only; never builds or executes numerical kernels."""
from pathlib import Path
import hashlib,json,os,re,subprocess

ROOT=Path.cwd();HERE=ROOT/'target/selected-native-optimized';CLOSURE=ROOT/'target/benchmark/dependency-closures/6b24c03-complete-kinds'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
manifest=read(CLOSURE/'manifest.json');completion=read(CLOSURE/'workspace-completion.json');build=read(CLOSURE/'completed-workspace-build.json');events=read(CLOSURE/'cargo-library-events.json')
assert build['status']=='complete' and build['provenance_qualified'] and build['resources']['returncode']==0
assert completion['status']=='whole_workspace_build_completed_and_source_binaries_verified'
assert sha(CLOSURE/'manifest.json')==completion['dependency_closure_manifest_sha256']
assert sha(CLOSURE/'completed-workspace-build.json')==completion['workspace_manifest_sha256']
compiler=subprocess.check_output(['rustc','-vV'],text=True).strip();assert compiler==build['rustc'].strip()
assert build['environment']['RUSTFLAGS'] is None and build['environment']['CARGO_ENCODED_RUSTFLAGS'] is None
assert {k:build['environment'][k] for k in ['CARGO_PROFILE_RELEASE_OPT_LEVEL','CARGO_PROFILE_RELEASE_LTO','CARGO_PROFILE_RELEASE_CODEGEN_UNITS']}=={'CARGO_PROFILE_RELEASE_OPT_LEVEL':'3','CARGO_PROFILE_RELEASE_LTO':'thin','CARGO_PROFILE_RELEASE_CODEGEN_UNITS':'1'}
source={p:h for p,h in build['source_sha256_before'].items() if p.startswith(('dependencies/symbolica/','dependencies/oneloopmaster/'))}
assert len(source)==298
for p,h in source.items():assert build['source_sha256'][p]==h and sha(ROOT/p)==h,p
for p in ['Cargo.toml','Cargo.lock']:assert sha(ROOT/p)==build['source_sha256'][p]
assert subprocess.check_output(['git','diff',build['source_revision']+'..HEAD','--','dependencies/symbolica','dependencies/oneloopmaster'])==b''
available={Path(f['retained']).name:f for f in manifest['files']}
runtime={'symbolica':'libsymbolica-2ae1abcc9fd9c0db.rlib','numerica':'libnumerica-f2720232b78e95ca.rlib','graphica':'libgraphica-0f8ec0b96b63d035.rlib','oneloop':'liboneloop-6117c7de19c8681b.rlib','serde':'libserde-bde6fd4136f3a6c8.rlib','serde_json':'libserde_json-d5ce7f4fcf58bd84.rlib','thiserror':'libthiserror-7d7ef35ea784c43a.rlib','gmp_mpfr_sys':'libgmp_mpfr_sys-abd713454cac2ce0.rlib'}
env=os.environ.copy();env['RUSTC_BOOTSTRAP']='1'
sysroot=Path(subprocess.check_output(['rustc','--print','sysroot'],text=True).strip())/'lib/rustlib/x86_64-unknown-linux-gnu/lib'
artifacts={};graph={};bindings={}
for name,file in runtime.items():
    path=CLOSURE/'deps'/file;entry=available[file];assert sha(path)==entry['sha256']
    event=next(e for e in events if any(Path(f).name==file for f in e.get('filenames',[])))
    assert event['profile']=={'opt_level':'3','debuginfo':0,'debug_assertions':False,'overflow_checks':False,'test':False}
    command=['rustc','-Zls=root',str(path)];metadata=subprocess.check_output(command,env=env,text=True)
    (HERE/'metadata'/f'{name}.txt').write_text(metadata)
    assert 'triple x86_64-unknown-linux-gnu' in metadata and f'name {file[3:-5]}' in metadata
    dependencies=re.findall(r'^\d+ ([\w-]+) hash ([0-9a-f]+).*$',metadata,re.M)
    resolved=[]
    for dep,crate_hash in dependencies:
        choices=[f'lib{dep}.rlib',f'lib{dep}.so']
        retained=next((available[c] for c in choices if c in available),None)
        if retained:
            dependency=Path(retained['retained']);expected=retained['sha256'];kind='retained'
        else:
            dependency=next((sysroot/c for c in choices if (sysroot/c).exists()),None)
            assert dependency is not None,(name,dep)
            expected=sha(dependency);kind='same-toolchain-sysroot'
        if str(dependency) not in bindings:assert sha(dependency)==expected;bindings[str(dependency)]=expected
        resolved.append({'name':dep,'crate_hash':crate_hash,'path':str(dependency),'sha256':expected,'kind':kind})
    members=subprocess.check_output(['ar','t',str(path)],text=True).splitlines();object_name=next(m for m in members if m.endswith('.o'))
    data=subprocess.check_output(['ar','p',str(path),object_name]);magic=data[:4].hex()
    assert magic in ['4243c0de','7f454c46']
    artifacts[name]={'path':str(path.relative_to(ROOT)),'sha256':entry['sha256'],'bytes':path.stat().st_size,'cargo_event':event,'metadata_path':f'metadata/{name}.txt','metadata_sha256':sha(HERE/'metadata'/f'{name}.txt'),'first_object':object_name,'first_object_magic':magic,'first_object_sha256':hashlib.sha256(data).hexdigest()}
    bindings[str(path)]=entry['sha256'];graph[name]=resolved
assert 'numerica-f2720232b78e95ca' in (HERE/'metadata/symbolica.txt').read_text()
assert 'symbolica-2ae1abcc9fd9c0db' in (HERE/'metadata/oneloop.txt').read_text()
native=CLOSURE/'build/gmp-mpfr-sys-e9fd89ef30e561a9/out/lib'
for path in native.glob('*.a'):
    entry=next(f for f in manifest['native_files'] if Path(f['retained'])==path);assert sha(path)==entry['sha256'];bindings[str(path)]=entry['sha256']
current={p:sha(ROOT/p) for p in subprocess.check_output(['git','ls-files','crates/iregi-masters'],text=True).splitlines() if (ROOT/p).is_file()}
semantics=read(ROOT/'validation/selected-native-reduction/source-manifest.json')
for p,h in semantics['production_sources'].items():
    if p.startswith('crates/iregi-masters/'):assert current[p]==h
private=ROOT/'target/selected-native-reduction/copied/crates/iregi-masters'
private_source={str(p.relative_to(private)):sha(p) for p in private.rglob('*') if p.is_file()}
for p,h in private_source.items():assert semantics['private_sources']['copied/crates/iregi-masters/'+p]==h
result={'status':'source-and-ABI-audit-passed-no-build','compiler':compiler,'source_revision_of_closure':build['source_revision'],'current_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    'closure_manifest_sha256':sha(CLOSURE/'manifest.json'),'completed_build_sha256':sha(CLOSURE/'completed-workspace-build.json'),'completion_sha256':sha(CLOSURE/'workspace-completion.json'),'cargo_events_sha256':sha(CLOSURE/'cargo-library-events.json'),
    'numerical_source_files':source,'numerical_sources_match_before_after_and_current':True,'workspace_manifests':{p:sha(ROOT/p) for p in ['Cargo.toml','Cargo.lock']},
    'runtime_artifacts':artifacts,'metadata_dependency_graph':graph,'verified_archive_and_sysroot_bindings':bindings,'native_search_path':str(native.relative_to(ROOT)),
    'current_master_sources':current,'selected_private_master_sources':private_source,'selected_private_source_qualification':'validation/selected-native-reduction/qualification.json','selected_private_source_qualification_sha256':sha(ROOT/'validation/selected-native-reduction/qualification.json'),
    'current_master_change_from_old_closure':subprocess.check_output(['git','diff','--stat',build['source_revision']+'..HEAD','--','crates/iregi-masters'],text=True),
    'excluded':['old6b24 master archive','host opt0 runtime-name variants','debug e6-direct-n2 closure','separate binary-fold Symbolica candidate'],
    'optimization':{'retained_runtime_rust':'opt3; ThinLTO-compatible LLVM bitcode; original release codegen-units1, debug assertions/overflow checks off','new_shared_master_and_cores_proposed':'opt3,codegen-units16,embed-bitcode=yes,debug-assertions=no,overflow-checks=no; no native-batch feature','new_probes_proposed':'opt3,codegen-units16,embed-bitcode=yes,lto=thin,debug-assertions=no,overflow-checks=no','native_GMP_MPFR_MPC':'unchanged frozen archive bytes from the completed release closure; original build-script flags are not newly inferred'},
    'scope':'read-only source/hash/Rust metadata inspection only; no compilation, numerical execution or timing; a new source-matched shared current private master adapter must be compiled after ROOT authorization'}
(HERE/'closure-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'numerical_sources':len(source),'runtime_artifacts':len(artifacts),'transitive_bindings':len(bindings),'receipt_sha256':sha(HERE/'closure-audit.json')},indent=2))
