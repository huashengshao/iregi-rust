"""Freeze a diagnostic-only Atom::add_many candidate; never edit production.

Existing polynomial extraction and contributions are unchanged. The retained
legacy function and a whole-expression verification mode provide exact checks.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def once(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new)


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    parent_path = here / 'phase-build.json'
    protected = [Path(__file__), parent_path, here/'nway_exact_cases.rs', here/'nway_exact_probe.rs', root/'crates/iregi-rust/examples/highpoint_public.rs']
    protected_before = {str(path.relative_to(root)):sha(path) for path in protected}
    parent = json.loads(parent_path.read_text())
    original = root / parent['frozen_core_source']
    target = root / 'target/public-highpoint/nway3'
    assert not target.exists(), 'Preserve existing immutable builds'
    for name, expected in parent['library_source_hashes'].items():
        assert sha(original / Path(name).relative_to('crates/iregi-rust')) == expected
    snapshot = target / 'source/crates/iregi-rust'
    snapshot.parent.mkdir(parents=True)
    shutil.copytree(original, snapshot)
    path = snapshot / 'src/stability.rs'
    source = path.read_text()
    begin = source.index('fn master_amplitude(\n')
    end = source.index('\nfn collect_amplitude_variables(', begin)
    legacy = source[begin:end].replace('master_amplitude(', 'master_amplitude_legacy(')
    candidate = source[begin:end].replace('fn master_amplitude(', 'fn master_amplitude_nway(', 1)
    candidate = once(candidate, '    let mut result = Atom::new();', '    let mut contributions = Vec::with_capacity(polynomial.nterms());')
    candidate = once(candidate, '            result = result + coefficient * &variable_amplitudes[index];', '            contributions.push(coefficient * &variable_amplitudes[index]);')
    candidate = once(candidate, '            result += coefficient;', '            contributions.push(coefficient);')
    candidate = once(candidate, '    Ok(result)', '    Ok(Atom::add_many(contributions))')
    candidate = once(candidate, '    let mut variables = BTreeSet::new();', '''    let diagnostic_start = std::time::Instant::now();
    let diagnostic_call = PRIMAL_CALL.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    let mut variables = BTreeSet::new();''')
    candidate = once(candidate, '    let field = AtomField {', '''    let diagnostic_variables_elapsed = diagnostic_start.elapsed();
    let diagnostic_verbose = diagnostic_call % 500 == 0 || variables.len() >= 100;
    if diagnostic_verbose {
        eprintln!("HIGHPOINT_PRIMAL polynomial START call={} variables={} collect_seconds={}", diagnostic_call, variables.len(), diagnostic_variables_elapsed.as_secs_f64());
    }
    let diagnostic_polynomial_start = std::time::Instant::now();
    let field = AtomField {''')
    candidate = once(candidate, '    let mut contributions = Vec::with_capacity(polynomial.nterms());', '''    let diagnostic_polynomial_elapsed = diagnostic_polynomial_start.elapsed();
    if diagnostic_verbose {
        eprintln!("HIGHPOINT_PRIMAL polynomial END call={} terms={} seconds={}", diagnostic_call, polynomial.nterms(), diagnostic_polynomial_elapsed.as_secs_f64());
    }
    let diagnostic_terms_start = std::time::Instant::now();
    let mut contributions = Vec::with_capacity(polynomial.nterms());''')
    candidate = once(candidate, '    Ok(Atom::add_many(contributions))', '''    let diagnostic_terms_elapsed = diagnostic_terms_start.elapsed();
    let diagnostic_sum_start = std::time::Instant::now();
    let result = Atom::add_many(contributions);
    let diagnostic_sum_elapsed = diagnostic_sum_start.elapsed();
    if diagnostic_verbose || diagnostic_start.elapsed().as_secs_f64() > 0.025 {
        eprintln!("HIGHPOINT_PRIMAL END call={} variables={} terms={} collect={} polynomial={} contributions={} sum={} total={}", diagnostic_call, variables.len(), polynomial.nterms(), diagnostic_variables_elapsed.as_secs_f64(), diagnostic_polynomial_elapsed.as_secs_f64(), diagnostic_terms_elapsed.as_secs_f64(), diagnostic_sum_elapsed.as_secs_f64(), diagnostic_start.elapsed().as_secs_f64());
    }
    Ok(result)''')
    wrapper = '''static PRIMAL_CALL: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
static PRIMAL_VERIFIED: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);

fn master_amplitude(expression: &Atom, amplitudes: &HashMap<Atom, Atom>) -> Result<Atom, ReductionError> {
    static MODE: std::sync::OnceLock<String> = std::sync::OnceLock::new();
    let mode = MODE.get_or_init(|| std::env::var("IREGI_PRIMAL_SUM_MODE").unwrap_or_else(|_| "nway".into()));
    match mode.as_str() {
        "legacy" => master_amplitude_legacy(expression, amplitudes),
        "nway" => master_amplitude_nway(expression, amplitudes),
        "verify" => {
            let candidate = master_amplitude_nway(expression, amplitudes);
            let legacy = master_amplitude_legacy(expression, amplitudes);
            match (&candidate, &legacy) {
                (Ok(a), Ok(b)) => assert_eq!(a, b, "exact full master-amplitude mismatch"),
                (Err(a), Err(b)) => assert_eq!(a.to_string(), b.to_string()),
                _ => panic!("master-amplitude success/error mismatch"),
            }
            let count = PRIMAL_VERIFIED.fetch_add(1, std::sync::atomic::Ordering::Relaxed) + 1;
            if count % 500 == 0 { eprintln!("HIGHPOINT_PRIMAL VERIFIED count={count}"); }
            candidate
        }
        _ => panic!("unknown IREGI_PRIMAL_SUM_MODE"),
    }
}

'''
    source = source[:begin] + wrapper + candidate + '\n\n' + legacy + source[end:]
    old = '''        for (alias, body) in &plan.aliases {
            if !reachable.contains_key(alias) || !depends_on_amplitudes(body, &amplitudes) {'''
    new = '''        let diagnostic_primal_start = std::time::Instant::now();
        for (diagnostic_alias, (alias, body)) in plan.aliases.iter().enumerate() {
            if diagnostic_alias % 500 == 0 {
                eprintln!("HIGHPOINT_PRIMAL ALIAS index={} built={} elapsed={}", diagnostic_alias, self.primal_aliases.len(), diagnostic_primal_start.elapsed().as_secs_f64());
            }
            if !reachable.contains_key(alias) || !depends_on_amplitudes(body, &amplitudes) {'''
    source = once(source, old, new)
    source += '\n' + (here / 'nway_exact_cases.rs').read_text()
    path.write_text(source)
    lib = snapshot / 'src/lib.rs'
    lib.write_text(lib.read_text() + '\npub use stability::diagnostic_amplitude_exact_cases;\n')
    sources = {str(p.relative_to(snapshot)): sha(p) for p in (snapshot / 'src').rglob('*.rs')}
    diff = subprocess.run(['diff', '-ru', str(original/'src'), str(snapshot/'src')], capture_output=True, text=True)
    assert diff.returncode == 1
    (here/'nway-instrumentation.patch').write_text(diff.stdout)
    commands = [[part.replace(str(original), str(snapshot)).replace(str(root/'target/public-highpoint/phase'), str(target)).replace('metadata=public_highpoint_phase', 'metadata=public_highpoint_nway') for part in command] for command in parent['commands']]
    exact_command = [part.replace(str(root/'crates/iregi-rust/examples/highpoint_public.rs'), str(here/'nway_exact_probe.rs')).replace('highpoint_public', 'nway_exact_probe') for part in commands[1]]
    commands.append(exact_command)
    guards = [Path(part.split('=',1)[1]) for part in commands[0] if part.startswith(('iregi_masters=', 'symbolica=', 'serde=', 'thiserror='))]
    guards.extend(p for p in (root/'target/cargo-build/debug/deps').iterdir() if p.suffix in ['.rlib','.so'])
    before = {str(p.relative_to(root)):sha(p) for p in guards}
    env = os.environ.copy()
    env.update(CARGO_MANIFEST_DIR=str(snapshot), CARGO_CRATE_NAME='iregi_rust')
    start = time.monotonic()
    codes = []
    for label, command in zip(['core','probe','exact'], commands):
        with (here/f'nway-{label}-build.log').open('w') as log:
            code = subprocess.call(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
        codes.append(code)
        if code: break
    after = {str(p.relative_to(root)):sha(p) for p in guards}
    protected_after = {str(path.relative_to(root)):sha(path) for path in protected}
    for key,value in protected_before.items():
        before[key]=value
        after[key]=protected_after[key]
    changed = {key:[value,after.get(key)] for key,value in before.items() if after.get(key)!=value}
    unchanged = all(sha(snapshot/name)==value for name,value in sources.items())
    record = dict(status='passed' if codes==[0,0,0] and not changed and unchanged else 'failed', commands=commands, exit_codes=codes, changed_inputs=changed, frozen_core_source=str(snapshot.relative_to(root)), library_source_hashes={'crates/iregi-rust/'+key:value for key,value in sources.items()}, frozen_core_sources_verified_after_build=unchanged, parent_build_manifest_sha256=sha(parent_path), instrumentation_patch_sha256=sha(here/'nway-instrumentation.patch'), build_script_sha256=sha(Path(__file__)), source_sha256=parent['source_sha256'], exact_cases_sha256=sha(here/'nway_exact_cases.rs'), exact_probe_source_sha256=sha(here/'nway_exact_probe.rs'), elapsed_seconds=time.monotonic()-start, scope='Isolated Symbolica n-way sum candidate and exact legacy comparator, plus phase instrumentation; not production or numerical acceptance.')
    record.update(protected_input_hashes=protected_before, dependency_hashes={key:value for key,value in before.items() if key not in protected_before}, binary_path=str((target/'highpoint_public').relative_to(root)), exact_binary_path=str((target/'nway_exact_probe').relative_to(root)))
    if codes==[0,0,0]:
        record.update(binary_sha256=sha(target/'highpoint_public'), exact_binary_sha256=sha(target/'nway_exact_probe'))
    (here/'nway-build.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({key:record[key] for key in ['status','exit_codes','elapsed_seconds','changed_inputs']}),flush=True)
    if record['status']!='passed':raise SystemExit(1)

if __name__=='__main__':main()
