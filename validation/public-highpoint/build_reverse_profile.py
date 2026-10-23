"""Freeze unchanged reverse-predicate logic with substage/counter instrumentation."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def once(s,a,b):
    assert s.count(a)==1,a[:100]
    return s.replace(a,b)


def main():
    root=Path.cwd();here=root/'validation/public-highpoint'
    parent_path=here/'phase-build.json';parent=json.loads(parent_path.read_text())
    protected=[Path(__file__),parent_path,root/'crates/iregi-rust/examples/highpoint_public.rs']
    protected_before={str(p.relative_to(root)):sha(p) for p in protected}
    original=root/parent['frozen_core_source'];target=root/'target/public-highpoint/reverse-profile'
    assert not target.exists(),'Preserve existing frozen builds'
    for name,expected in parent['library_source_hashes'].items():
        assert sha(original/Path(name).relative_to('crates/iregi-rust'))==expected
    snapshot=target/'source/crates/iregi-rust';snapshot.parent.mkdir(parents=True)
    shutil.copytree(original,snapshot)
    p=snapshot/'src/stability.rs';s=p.read_text()
    s=once(s,'''        eprintln!("HIGHPOINT_PHASE reverse alias uses START");
        let phase_started = std::time::Instant::now();''','''        REVERSE_COUNTS.with(|counts| *counts.borrow_mut() = ReverseCounts::default());
        let mut reverse_union_seconds = 0.0f64;
        let mut reverse_intern_seconds = 0.0f64;
        let mut reverse_collect_seconds = 0.0f64;
        let mut reverse_total_paths = 0usize;
        let mut reverse_max_paths = 0usize;
        let mut reverse_unconditional_sets = 0usize;
        let mut reverse_max_union_bytes = 0usize;
        eprintln!("HIGHPOINT_PHASE reverse alias uses START");
        let phase_started = std::time::Instant::now();''')
    s=once(s,'''                let active = monitor.intern_predicate(union_paths(paths), &mut predicate_indices);
                collect_alias_uses(body.as_view(), &active, &definitions, &mut uses);
                reachable.insert(alias.clone(), active);''','''                reverse_total_paths += paths.len();
                reverse_max_paths = reverse_max_paths.max(paths.len());
                reverse_unconditional_sets += usize::from(paths.contains(&always));
                let detail_started = std::time::Instant::now();
                let union = union_paths(paths);
                let union_seconds = detail_started.elapsed().as_secs_f64();
                reverse_union_seconds += union_seconds;
                let union_bytes = union.as_view().get_byte_size();
                reverse_max_union_bytes = reverse_max_union_bytes.max(union_bytes);
                let detail_started = std::time::Instant::now();
                let active = monitor.intern_predicate(union, &mut predicate_indices);
                let intern_seconds = detail_started.elapsed().as_secs_f64();
                reverse_intern_seconds += intern_seconds;
                let detail_started = std::time::Instant::now();
                collect_alias_uses(body.as_view(), &active, &definitions, &mut uses);
                let collect_seconds = detail_started.elapsed().as_secs_f64();
                reverse_collect_seconds += collect_seconds;
                if union_seconds + intern_seconds + collect_seconds >= 0.25 {
                    eprintln!("HIGHPOINT_REVERSE SLOW index={} union={} intern={} collect={} union_bytes={} body_bytes={}", phase_index, union_seconds, intern_seconds, collect_seconds, union_bytes, body.as_view().get_byte_size());
                }
                reachable.insert(alias.clone(), active);''')
    s=once(s,'''        eprintln!("HIGHPOINT_PHASE reverse alias uses END elapsed={:?} reachable={}", phase_started.elapsed(), reachable.len());''','''        eprintln!("HIGHPOINT_PHASE reverse alias uses END elapsed={:?} reachable={}", phase_started.elapsed(), reachable.len());
        eprintln!("HIGHPOINT_REVERSE TOTAL union_seconds={} intern_seconds={} collect_seconds={} paths={} max_paths={} unconditional_sets={} max_union_bytes={} predicate_aliases={}", reverse_union_seconds, reverse_intern_seconds, reverse_collect_seconds, reverse_total_paths, reverse_max_paths, reverse_unconditional_sets, reverse_max_union_bytes, monitor.predicate_aliases.len());
        REVERSE_COUNTS.with(|counts| eprintln!("HIGHPOINT_REVERSE COUNTERS {:?}", counts.borrow()));
        if std::env::var_os("IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE").is_some() {
            return Err(ReductionError::Preparation("diagnostic stop after unchanged reverse pass".into()));
        }''')
    a=s.index('fn collect_alias_uses(\n');b=s.index('\nfn collect_denominators(',a)
    body=s[a:b]
    signature=body[:body.index('    if let Some((condition, yes, no))')]
    profiled=body.replace('collect_alias_uses(', 'collect_alias_uses_profiled(')
    profiled=once(profiled,'''    uses: &mut HashMap<Atom, BTreeSet<Atom>>,
) {''','''    uses: &mut HashMap<Atom, BTreeSet<Atom>>,
    counts: &mut ReverseCounts,
) {
    counts.visited_nodes += 1;''')
    profiled=profiled.replace('definitions, uses)', 'definitions, uses, counts)')
    profiled=profiled.replace('            uses,\n', '            uses, counts,\n')
    profiled=once(profiled,'''    if let Some((condition, yes, no)) = if_parts(value) {''','''    if let Some((condition, yes, no)) = if_parts(value) {
        counts.visited_ifs += 1;''')
    profiled=once(profiled,'''        AtomView::Var(_) => {
            let alias = value.to_owned();''','''        AtomView::Var(_) => {
            counts.visited_variables += 1;
            let alias = value.to_owned();''')
    profiled=once(profiled,'''                uses.entry(alias).or_default().insert(active.clone());''','''                counts.alias_occurrences += 1;
                counts.literal_one_occurrences += u64::from(active == &Atom::num(1));
                let entry = uses.entry(alias).or_default();
                counts.already_unconditional += u64::from(entry.contains(&Atom::num(1)));
                if !entry.insert(active.clone()) { counts.duplicate_insertions += 1; }
                counts.max_entry_paths = counts.max_entry_paths.max(entry.len());''')
    wrapper='''#[derive(Debug, Default)]
struct ReverseCounts {
    visited_nodes: u64,
    visited_ifs: u64,
    visited_variables: u64,
    alias_occurrences: u64,
    literal_one_occurrences: u64,
    already_unconditional: u64,
    duplicate_insertions: u64,
    max_entry_paths: usize,
}
thread_local! {
    static REVERSE_COUNTS: std::cell::RefCell<ReverseCounts> = std::cell::RefCell::new(ReverseCounts::default());
}

'''+signature+'''    REVERSE_COUNTS.with(|counts| collect_alias_uses_profiled(value, active, definitions, uses, &mut counts.borrow_mut()));
}

'''
    s=s[:a]+wrapper+profiled+s[b:];p.write_text(s)
    sources={str(p.relative_to(snapshot)):sha(p) for p in (snapshot/'src').rglob('*.rs')}
    diff=subprocess.run(['diff','-ru',str(original/'src'),str(snapshot/'src')],capture_output=True,text=True)
    assert diff.returncode==1
    (here/'reverse-profile-instrumentation.patch').write_text(diff.stdout)
    commands=[[part.replace(str(original),str(snapshot)).replace(str(root/'target/public-highpoint/phase'),str(target)).replace('metadata=public_highpoint_phase','metadata=public_highpoint_reverse_profile') for part in command] for command in parent['commands']]
    guards=[Path(part.split('=',1)[1]) for part in commands[0] if part.startswith(('iregi_masters=','symbolica=','serde=','thiserror='))]
    guards.extend(p for p in (root/'target/cargo-build/debug/deps').iterdir() if p.suffix in ['.rlib','.so'])
    before={str(p.relative_to(root)):sha(p) for p in guards}
    env=os.environ.copy();env.update(CARGO_MANIFEST_DIR=str(snapshot),CARGO_CRATE_NAME='iregi_rust')
    start=time.monotonic();codes=[]
    for label,command in zip(['core','probe'],commands):
        with (here/f'reverse-profile-{label}-build.log').open('w') as log:
            code=subprocess.call(command,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
        codes.append(code)
        if code:break
    after={str(p.relative_to(root)):sha(p) for p in guards}
    changed={key:[value,after.get(key)] for key,value in before.items() if after.get(key)!=value}
    for path,expected in protected_before.items():
        if sha(root/path)!=expected:changed[path]=[expected,sha(root/path)]
    unchanged=all(sha(snapshot/path)==expected for path,expected in sources.items())
    record=dict(status='passed' if codes==[0,0] and not changed and unchanged else 'failed',commands=commands,exit_codes=codes,changed_inputs=changed,frozen_core_source=str(snapshot.relative_to(root)),library_source_hashes={'crates/iregi-rust/'+path:value for path,value in sources.items()},frozen_core_sources_verified_after_build=unchanged,parent_build_manifest_sha256=sha(parent_path),instrumentation_patch_sha256=sha(here/'reverse-profile-instrumentation.patch'),build_script_sha256=sha(Path(__file__)),source_sha256=parent['source_sha256'],elapsed_seconds=time.monotonic()-start,scope='Unchanged reverse predicate algorithm with substage/counter instrumentation and explicit diagnostic stop before local checks; not numerical coverage.',protected_input_hashes=protected_before,dependency_hashes=before,binary_path=str((target/'highpoint_public').relative_to(root)))
    if codes==[0,0]:record['binary_sha256']=sha(target/'highpoint_public')
    (here/'reverse-profile-build.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ['status','exit_codes','elapsed_seconds','changed_inputs']}),flush=True)
    if record['status']!='passed':raise SystemExit(1)

if __name__=='__main__':main()
