"""Freeze a minimal matched optimized build; no compiler or integral is run."""
from pathlib import Path
import datetime, difflib, hashlib, json, shutil, subprocess

ROOT = Path('/shared/external/iregi/iregi-rust')
HERE = ROOT / 'target/guard-performance-review/optimized-performance-proposal'
SYM = ROOT / 'target/guard-performance-review/dependent-relink-qualification'
CHAIN = ROOT / 'target/guard-performance-review/dependent-chain-proposal'
CLOSURE = ROOT / 'target/benchmark/dependency-closures/6b24c03-complete-kinds'
OLD_AUDIT = ROOT / 'target/selected-native-optimized/closure-audit.json'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')

def replace(text, old, new, count=1):
    assert text.count(old) == count, (old, text.count(old), count)
    return text.replace(old, new)

def main():
    assert Path.cwd() == ROOT
    assert not (HERE / 'fresh-build-protocol.json').exists(), 'Do not overwrite a frozen proposal'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    protected = {}

    def bind(path, expected=None):
        value = sha(path)
        assert expected is None or value == expected, str(path)
        protected[str(Path(path).relative_to(ROOT)) if Path(path).is_relative_to(ROOT) else str(path)] = value
        return value

    # Reuse already frozen exact source bytes, rather than copy 390 MB again.
    sinv = read(SYM / 'source-inventory.json')
    cinv = read(CHAIN / 'source-inventory.json')
    capture_changes = {
        'crates/iregi-masters/src/lib.rs',
        'crates/iregi-rust/src/lib.rs',
        'crates/iregi-rust/src/execution.rs',
    }
    for variant in ['baseline', 'candidate']:
        for relative, expected in sinv['source_sha256'][variant].items():
            frozen = SYM / 'source' / variant / 'symbolica' / relative
            bind(frozen, expected)
            current = ROOT / 'dependencies/symbolica' / relative
            if variant == 'baseline' or relative != 'src/evaluate/batch.rs':
                bind(current, expected)
            else:
                bind(current, sinv['source_sha256']['baseline'][relative])
    assert len(sinv['source_sha256']['baseline']) == 91
    assert sha(ROOT / 'dependencies/symbolica/src/poly.rs') == '0f246ceca41a50213458c51d0c103e36f85d023616120d5789482fd35a65d6d2'
    for relative, expected in cinv['live_source_sha256'].items():
        bind(ROOT / relative, expected)
    changed = []
    for relative, expected in cinv['private_source_sha256'].items():
        bind(CHAIN / relative, expected)
        if relative.startswith('source/') and relative[7:] in cinv['live_source_sha256']:
            if expected != cinv['live_source_sha256'][relative[7:]]:
                changed.append(relative[7:])
    assert set(changed) == capture_changes
    for path in [ROOT/'Cargo.lock', ROOT/'Cargo.toml', SYM/'source-inventory.json',
                 CHAIN/'source-inventory.json', CHAIN/'observation-only.patch',
                 ROOT/'validation/uniform-branch-dependent/qualification.json',
                 HERE/'source-differences.json', HERE/'reviews/reference-cohort-source-review.json',
                 HERE/'reviews/frozen-optimized-dependency-recipe-review.json', OLD_AUDIT,
                 CLOSURE/'manifest.json', CLOSURE/'cargo-library-events.json']:
        bind(path)

    # The lower dependency context is historical opt3, exactly shared. It is not
    # the current Cargo feature graph. No old Symbolica/OneLoop/core is reused.
    audit = read(OLD_AUDIT)
    dependency_review = read(HERE/'reviews/frozen-optimized-dependency-recipe-review.json')
    for relative, expected in dependency_review['numerica_graphica_source_sha256'].items():
        bind(ROOT/relative, expected)
    old_lock = ROOT/'target/benchmark/sources/6b24c0372022e22606a1ac85f30c7fa579fb41f0/Cargo.lock'
    bind(old_lock, dependency_review['lock_context']['old_lock_sha256'])
    externs = {name: ROOT/item['path'] for name, item in dependency_review['symbolica_explicit_externs'].items()}
    assert len(externs) == 28
    inherited = dependency_review['lower_abi_closure_sha256_excluding_stale_symbolica_oneloop']
    for raw, expected in inherited.items():
        bind(Path(raw), expected)
    for name, item in dependency_review['symbolica_explicit_externs'].items():
        bind(ROOT/item['path'], item['sha256'])
    for name in ['serde', 'serde_json', 'thiserror']:
        item = audit['runtime_artifacts'][name]
        externs[name] = ROOT/item['path']
        bind(externs[name], item['sha256'])
    for name in ['bincode', 'symjit']:
        assert name in externs
    for item in read(CLOSURE/'manifest.json')['native_files']:
        bind(Path(item['retained']), item['sha256'])
    native = ROOT/audit['native_search_path']

    # Qualification uses the previous exact captured probe. The timing probe
    # removes every capture call; it still emits complete untimed final arrays.
    source = HERE/'fresh-source'
    source.mkdir()
    old = CHAIN/'source/probe/core_probe.rs'
    text = old.read_text()
    a = text.index('fn check_backends(')
    b = text.index('\nfn observe<', a)
    text = text[:a] + text[b:]
    for oldline in [
        '    assert!(core_impl::take_master_captures().is_empty(),"unconsumed capture");\n',
        '    core_impl::set_master_capture(true);\n',
        '    let captures=core_impl::take_master_captures();\n',
        '    core_impl::set_master_capture(false);\n',
        '    let captures=serde_json::to_value(captures).unwrap();\n',
        '    check_backends(&captures);\n',
    ]:
        text = replace(text, oldline, '')
    text = replace(text, '"master_captures":captures', '"master_captures":[]')
    text = replace(text, '    let mut record=observe(&mut p.workspace,&batch,p.degrees.len(),false)?;', '''    let measured=request.engine.is_some();
    p.workspace.set_profiling(false);
    let mut every_call_successful=true;
    let mut total_ns=Vec::<f64>::new();
    let mut elapsed_ns=Vec::<u128>::new();
    if measured {
        if request.engine.as_deref()!=Some(env!("TIRUST_SCHEDULER_VARIANT")) || request.repeats!=1 || request.iterations==0 || request.iterations>i32::MAX as usize {
            return Err("timing requires own variant and one positive signed32 fixed-count block".into());
        }
        for _ in 0..request.warmup {
            let result=p.workspace.reduce_batch(std::hint::black_box(&batch)).map_err(|e|e.to_string())?;
            every_call_successful &= result.statuses.iter().all(|s|*s==LaneStatus::Success);
            std::hint::black_box(result);
        }
        let start=std::time::Instant::now();
        for _ in 0..request.iterations {
            let result=p.workspace.reduce_batch(std::hint::black_box(&batch)).map_err(|e|e.to_string())?;
            every_call_successful &= result.statuses.iter().all(|s|*s==LaneStatus::Success);
            std::hint::black_box(result);
        }
        let duration=start.elapsed().as_nanos();
        elapsed_ns.push(duration);
        total_ns.push(duration as f64/request.iterations as f64);
    } else if request.warmup!=0 || request.repeats!=0 || request.iterations!=0 {
        return Err("untimed request must not carry timing counts".into());
    }
    let mut record=observe(&mut p.workspace,&batch,p.degrees.len(),false)?;
    assert!(every_call_successful,"timed public call failed");''')
    text = replace(text, '    for _ in 0..2 {\n        assert_eq!(observe(&mut p.workspace,&batch,p.degrees.len(),false)?,record,"own complete repeated record changed");\n    }', '''    if !measured {
        for _ in 0..2 {
            assert_eq!(observe(&mut p.workspace,&batch,p.degrees.len(),false)?,record,"own complete repeated record changed");
        }
    }''')
    text = replace(text, '"total_ns":[],"elapsed_ns":[],"iterations":0,"capture_enabled":true,"profiling_enabled":false,\n        "own_repeated_outputs_exact":true,"input_unchanged":true', '''"total_ns":total_ns,"elapsed_ns":elapsed_ns,"iterations":if measured{request.iterations}else{0},"capture_enabled":false,"profiling_enabled":false,
        "own_repeated_outputs_exact":!measured,"input_unchanged":true''')
    text = replace(text, '"scope":"untimed generic-only scheduler whole-reduction qualification"', '"scope":if measured{"whole-public-call fixed-count timing"}else{"untimed capture-free scheduler whole-reduction qualification"}')
    assert 'take_master_captures' not in text and 'set_master_capture' not in text
    (source/'uncaptured_core_probe.rs').write_text(text)
    (source/'uncaptured_core_probe.rs.patch').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),text.splitlines(True),fromfile=str(old.relative_to(ROOT)),tofile='fresh-source/uncaptured_core_probe.rs')))
    wrapper = (CHAIN/'source/probe/probe.rs').read_text()
    wrapper = replace(wrapper, '#[cfg(not(iregi_qualification_capture))]\ncompile_error!("qualification requires the observation-only capture cfg");\n', '#[cfg(iregi_qualification_capture)]\ncompile_error!("timing product must not compile capture hooks");\n')
    wrapper = replace(wrapper, 'include!("core_probe.rs")', 'include!("uncaptured_core_probe.rs")')
    wrapper = replace(wrapper, '    assert!(iregi_rust::QUALIFICATION_CAPTURE_ENABLED);\n', '')
    wrapper = replace(wrapper, 'Ok(r) if r.engine.is_none()&&r.warmup==0&&r.repeats==0&&r.iterations==0 =>', 'Ok(r) if r.engine.is_some() || (r.warmup==0&&r.repeats==0&&r.iterations==0) =>')
    wrapper = replace(wrapper, 'json!({"status":"invalid_request","error":"qualification is untimed; engine and timing counts are forbidden"})', 'json!({"status":"invalid_request","error":"untimed request must not carry timing counts"})')
    wrapper = replace(wrapper, 'iregi_rust::set_master_capture(false);let _=iregi_rust::take_master_captures();\n            ', '')
    # include! resolves this sibling file without modifying the frozen controls.
    shutil.copyfile(CHAIN/'source/probe/master_controls.rs', source/'master_controls.rs')
    (source/'uncaptured_probe.rs').write_text(wrapper)
    shutil.copyfile(CHAIN/'lifecycle.py', HERE/'fresh_lifecycle.py')
    assert sha(HERE/'fresh_lifecycle.py') == 'c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824'

    oldsp = read(SYM/'protocol.json')
    tool_sha = oldsp['tool_sha256']
    rustc = oldsp['steps'][0]['command'][3]
    taskset = oldsp['steps'][0]['command'][0]
    linker = next(v[7:] for v in oldsp['steps'][0]['command'] if v.startswith('linker='))
    for p, expected in tool_sha.items():
        bind(Path(p), expected)
    rootout = HERE/'fresh-build-001'
    assert not rootout.exists()
    profile = ['-C','opt-level=3','-C','debuginfo=0','-C','strip=debuginfo',
               '-C','codegen-units=16','-C','embed-bitcode=yes',
               '-C','debug-assertions=no','-C','overflow-checks=no','-C',f'linker={linker}']
    steps=[]
    def add(variant, product, crate, path, deps, feature_cfg=(), capture=False, probe=False):
        directory=rootout/variant/('captured' if capture and product!='masters' else 'uncaptured' if product in ['core','probe'] else 'shared')
        output=directory/('probe' if probe else f'lib{crate}.rlib')
        command=[taskset,'-c','32,33',rustc,'--edition=2024',*profile,
                 '--crate-name',crate,'-C',f'metadata=tirust_sched_{variant}_{product}_{"capture" if capture else "plain"}_opt3_001']
        command += ['-C','lto=thin'] if probe else ['--crate-type','rlib','-C','lto=off']
        for directory_ in sorted(set(p.parent for p in deps.values()) | {CLOSURE/'deps'}):
            command += ['-L',f'dependency={directory_}']
        command += ['-L',f'native={native}']
        for feature in feature_cfg:command+=['--cfg',f'feature="{feature}"']
        if capture:command+=['--cfg','iregi_qualification_capture']
        command += [str(path)]
        for name, p in deps.items():command+=['--extern',f'{name}={p}']
        command += ['-o',str(output)]
        environment={'CARGO_CRATE_NAME':crate,'CARGO_PKG_VERSION':'3.0.1' if product=='symbolica' else '0.1.0',
                     'CARGO_MANIFEST_DIR':str(path.parent if probe else path.parent.parent),'TIRUST_SCHEDULER_VARIANT':variant}
        if product=='symbolica':environment['SYMBOLICA_VERSION']='symbolica-9cdc2949-iregi-scope-cache'
        cap={'symbolica':600,'oneloop':300,'masters':180,'core':240,'probe':480}[product]
        step={'label':variant+'-'+product+('-captured' if capture and product!='masters' else '-uncaptured' if product in ['core','probe'] else ''),
              'variant':variant,'product':product,'capture_cfg':capture,'command':command,'environment':environment,
              'compiler_cap_seconds':cap,'output':str(output),'explicit_externs':{n:str(p) for n,p in deps.items()},'features':list(feature_cfg)}
        if probe:
            linkmap=directory/'probe.map'
            command += ['-C',f'link-arg=-Wl,-Map={linkmap}']
            step.update(link_map=str(linkmap),expected_link_archives={n:str(deps[n]) for n in ['symbolica','oneloop','iregi_masters','iregi_rust']})
        steps.append(step)
        return output
    symbolica_features=['bincode','float-mpfr','integer-gmp','native_code_generation','serde','tracing_max_level_info']
    for variant in ['baseline','candidate']:
        sp=add(variant,'symbolica','symbolica',SYM/'source'/variant/'symbolica/src/lib.rs',{n:p for n,p in externs.items() if n in dependency_review['symbolica_explicit_externs']},symbolica_features)
        op=add(variant,'oneloop','oneloop',CHAIN/'source/dependencies/oneloopmaster/src/lib.rs',{'symbolica':sp,'bincode':externs['bincode'],'symjit':externs['symjit']},['default','generated-evaluators','prebuilt','rust-codegen'])
        mp=add(variant,'masters','iregi_masters',CHAIN/'source/crates/iregi-masters/src/lib.rs',{'symbolica':sp,'oneloop':op},capture=True)
        for captured in [True,False]:
            cp=add(variant,'core','iregi_rust',CHAIN/'source/crates/iregi-rust/src/lib.rs',{'symbolica':sp,'iregi_masters':mp,'serde':externs['serde'],'thiserror':externs['thiserror']},capture=captured)
            add(variant,'probe','tirust_scheduler_probe',CHAIN/'source/probe/probe.rs' if captured else source/'uncaptured_probe.rs',
                {'iregi_rust':cp,'iregi_masters':mp,'symbolica':sp,'oneloop':op,'serde':externs['serde'],'serde_json':externs['serde_json']},capture=captured,probe=True)
    assert len(steps)==14
    for path in [HERE/'prepare_fresh.py', HERE/'build_fresh.py', HERE/'fresh_lifecycle.py', *source.rglob('*')]:
        if path.is_file():bind(path)
    protocol={
        'schema_version':1,'status':'SOURCE_REVIEW_REQUIRED_NO_COMPILER_OR_RUNTIME_GRANT',
        'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'current_git_revision':head,'cwd':str(ROOT),
        'scope':'Fourteen sequential fresh matched opt3 compiler products; inherited frozen opt3 lower-dependency feature context. No Cargo, source mutation, integral evaluation or timing. Captured probes qualify the complete retained corpus before any timing.',
        'aggregate_budget_seconds':3600,'cleanup_postguard_reserve_seconds':30,'effective_work_deadline_seconds':3570,
        'cpu_affinity':'32,33','attempt_directory':str(rootout),'steps':steps,'protected_sha256':protected,'tool_sha256':tool_sha,
        'profile':{'all_fresh':'opt3 cgu16 embed-bitcode debug/overflow off','final_probes':'ThinLTO','fast_math':False},
        'sources_reused_by_hash_not_copied':True,'source_difference':'Only Symbolica evaluate/batch.rs differs between scheduler variants. Capture core cfg hooks are identical and absent in uncaptured products; shared masters cfg only exposes a read-only accessor.',
        'inherited_lower_dependency_context':'6b24c03-complete-kinds optimized archives; Numerica/Graphica source unchanged. Broader historical serde/bincode/serde_json features retained, not current Cargo feature identity.',
        'old_symbolica_oneloop_masters_core_archives_forbidden':True,
        'success_is_build_only':True,'numerical_qualified':False,'performance_qualified':False,'production_adoption_authorized':False,
        'failure_policy':'Stop first compiler failure, timeout, cancellation, changed input or cleanup error. No automatic retry or budget extension. Terminal child/group receipt precedes guards.',
        'next_gate':'Exact retained 60-request captured corpus with eight families, all master controls and values; independent saved-data review; then complete uncaptured corpus/controls and capture projection equality. Separate bounded runtime protocol required. Only then same-cohort four-engine preregistered timing.'}
    save(HERE/'fresh-build-protocol.json',protocol)
    print(json.dumps({'protocol_sha256':sha(HERE/'fresh-build-protocol.json'),'products':len(steps),'protected_inputs':len(protected),'no_compiler_or_integral_executed':True}))

if __name__ == '__main__':
    main()
