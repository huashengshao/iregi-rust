"""Prepare, but do not compile or run, the next isolated current-core candidate.

Retains the complete collector-only timeout snapshot, reuses the exact-qualified
n-way amplitude block, and adds dependency-discovery counters. No production
files are changed. Compilation and runtime need separate bounded commands.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def once(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new)


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    parent_path = here / 'use-dedup-full-build.json'
    nway_path = here / 'nway-build.json'
    parent, nway = [json.loads(p.read_text()) for p in [parent_path, nway_path]]
    assert parent['status'] == nway['status'] == 'passed'
    target = root / 'target/public-highpoint/collector-nway'
    assert not target.exists(), 'Keep frozen candidates immutable'
    original = root / parent['frozen_source_root']
    for name, expected in parent['frozen_source_hashes'].items():
        assert sha(original / name) == expected
    donor = root / nway['frozen_core_source'] / 'src/stability.rs'
    assert sha(donor) == nway['library_source_hashes']['crates/iregi-rust/src/stability.rs']
    frozen = target / 'source'
    shutil.copytree(original, frozen)
    snapshot = frozen / 'crates/iregi-rust'
    path = snapshot / 'src/stability.rs'
    source, old_nway = path.read_text(), donor.read_text()
    start = source.index('fn master_amplitude(\n')
    end = source.index('\nfn collect_amplitude_variables(', start)
    current_legacy = source[start:end].replace('master_amplitude(', 'master_amplitude_legacy(')
    donor_start = old_nway.index('static PRIMAL_CALL:')
    donor_end = old_nway.index('\nfn collect_amplitude_variables(', donor_start)
    block = old_nway[donor_start:donor_end]
    legacy_start = block.index('fn master_amplitude_legacy(\n')
    assert block[legacy_start:].strip() == current_legacy.strip(), 'Qualified legacy must match current core exactly'
    source = source[:start] + block + source[end:]
    old_dependency = '''    expression
        .get_all_symbols(false)
        .into_iter()
        .any(|symbol| amplitudes.contains_key(&Atom::var(symbol)))'''
    new_dependency = '''    let started = std::time::Instant::now();
    let result = expression
        .get_all_symbols(false)
        .into_iter()
        .any(|symbol| amplitudes.contains_key(&Atom::var(symbol)));
    PRIMAL_DEPENDENCY_CALLS.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    PRIMAL_DEPENDENCY_NS.fetch_add(started.elapsed().as_nanos().min(u64::MAX as u128) as u64, std::sync::atomic::Ordering::Relaxed);
    result'''
    source = once(source, old_dependency, new_dependency)
    source = once(source, 'static PRIMAL_CALL:', '''static PRIMAL_DEPENDENCY_CALLS: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
static PRIMAL_DEPENDENCY_NS: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
static PRIMAL_CALL:''')
    source = once(source, '        eprintln!("HIGHPOINT_PHASE primal amplitudes START");', '''        eprintln!("HIGHPOINT_PHASE primal amplitudes START");
        let dependency_calls_before = PRIMAL_DEPENDENCY_CALLS.load(std::sync::atomic::Ordering::Relaxed);
        let dependency_ns_before = PRIMAL_DEPENDENCY_NS.load(std::sync::atomic::Ordering::Relaxed);''')
    source = once(source, '        eprintln!("HIGHPOINT_PHASE primal amplitudes END elapsed={:?}", phase_started.elapsed());', '''        eprintln!("HIGHPOINT_PHASE primal amplitudes END elapsed={:?}", phase_started.elapsed());
        eprintln!("HIGHPOINT_PRIMAL dependency_discovery calls={} nanoseconds={}",
            PRIMAL_DEPENDENCY_CALLS.load(std::sync::atomic::Ordering::Relaxed).saturating_sub(dependency_calls_before),
            PRIMAL_DEPENDENCY_NS.load(std::sync::atomic::Ordering::Relaxed).saturating_sub(dependency_ns_before));''')
    source = once(source, 'amplitudes.len());\n            }\n            if !reachable.contains_key(alias)', '''amplitudes.len());
                eprintln!("HIGHPOINT_PRIMAL dependency_progress calls={} nanoseconds={}",
                    PRIMAL_DEPENDENCY_CALLS.load(std::sync::atomic::Ordering::Relaxed),
                    PRIMAL_DEPENDENCY_NS.load(std::sync::atomic::Ordering::Relaxed));
            }
            if !reachable.contains_key(alias)''')
    source += '\n' + (here / 'nway_exact_cases.rs').read_text()
    path.write_text(source)
    lib = snapshot / 'src/lib.rs'
    lib.write_text(lib.read_text() + '\npub use stability::diagnostic_amplitude_exact_cases;\n')
    diff = subprocess.run(['diff', '-ru', str(original), str(frozen)], capture_output=True, text=True)
    assert diff.returncode == 1
    patch_path = here / 'collector-nway-prepared.patch'
    patch_path.write_text(diff.stdout)
    sources = {str(p.relative_to(frozen)): sha(p) for p in frozen.rglob('*') if p.is_file()}
    protected = [Path(__file__), parent_path, nway_path, here / 'nway-qualification.json',
                 here / 'nway_exact_cases.rs', here / 'nway_exact_probe.rs',
                 here / 'use-dedup-full-capture-qualification.json']
    record = dict(status='source_prepared_only', source_revision=parent['source_revision'],
                  frozen_source_root=str(frozen.relative_to(root)),
                  parent_build_manifest_sha256=sha(parent_path), nway_build_manifest_sha256=sha(nway_path),
                  source_hashes=sources, protected_input_hashes={str(p.relative_to(root)): sha(p) for p in protected},
                  prepared_patch_sha256=sha(patch_path), donor_stability_sha256=sha(donor),
                  scope='Uncompiled current6b24 collector candidate plus byte-identical previously exact-qualified n-way amplitude block and finer counters. Existing exact proof transfers only the unchanged amplitude algorithm; new build/runtime and combined semantics remain unqualified.')
    (here / 'collector-nway-source.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: record[key] for key in ['status', 'source_revision', 'frozen_source_root', 'scope']}))


if __name__ == '__main__':
    main()
