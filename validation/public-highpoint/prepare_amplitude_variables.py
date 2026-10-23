"""Freeze an isolated Symbolica amplitude-variable collector candidate."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    parent_path = here / 'collector-nway-build.json'
    protected = [Path(__file__), parent_path, here / 'amplitude_variable_cases.rs',
                 here / 'amplitude_variable_probe.rs', here / 'collector-nway-full-qualification.json']
    protected_hashes = {str(p.relative_to(root)): sha(p) for p in protected}
    parent = json.loads(parent_path.read_text())
    assert parent['status'] == 'passed'
    original = root / parent['frozen_source_root']
    target = root / 'target/public-highpoint/amplitude-vars'
    assert not target.exists(), 'Preserve frozen candidates'
    assert all(sha(original / name) == value for name, value in parent['source_hashes'].items())
    frozen = target / 'source'
    shutil.copytree(original, frozen)
    assert all(sha(frozen / name) == value for name, value in parent['source_hashes'].items())
    source_path = frozen / 'crates/iregi-rust/src/stability.rs'
    source = source_path.read_text()
    start = source.index('fn collect_amplitude_variables(\n')
    end = source.index('\n/// Weighted roundoff', start)
    old = source[start:end]
    legacy = old.replace('collect_amplitude_variables(', 'collect_amplitude_variables_legacy(')
    candidate = old.replace('collect_amplitude_variables(', 'collect_amplitude_variables_candidate(')
    anchor = '    match expression {\n'
    assert candidate.count(anchor) == 1
    fastpath = '''    // Num coefficients deliberately remain opaque, as in the legacy walker.
    if matches!(expression, AtomView::Num(_)) {
        return;
    }
    if matches!(expression, AtomView::Var(_)) {
        let value = expression.to_owned();
        if amplitudes.contains_key(&value) {
            variables.insert(value);
        }
        return;
    }
    // Whole IF generators were handled above. Only IF-free subtrees use
    // Symbolica's indeterminate collection; function heads are not variables.
    if !expression.contains_symbol(Symbol::IF) {
        for variable in expression.get_all_indeterminates(true) {
            if matches!(variable, AtomView::Var(_)) {
                let value = variable.to_owned();
                if amplitudes.contains_key(&value) {
                    variables.insert(value);
                }
            }
        }
        return;
    }
'''
    candidate = candidate.replace(anchor, fastpath + anchor)
    wrapper = '''fn collect_amplitude_variables(
    expression: AtomView<'_>,
    amplitudes: &HashMap<Atom, Atom>,
    variables: &mut BTreeSet<Atom>,
) {
    static MODE: std::sync::OnceLock<String> = std::sync::OnceLock::new();
    let mode = MODE.get_or_init(|| std::env::var("IREGI_AMPLITUDE_VARIABLE_MODE").unwrap_or_else(|_| "candidate".into()));
    match mode.as_str() {
        "legacy" => collect_amplitude_variables_legacy(expression, amplitudes, variables),
        "candidate" => collect_amplitude_variables_candidate(expression, amplitudes, variables),
        "verify" => {
            let mut expected = variables.clone();
            collect_amplitude_variables_legacy(expression, amplitudes, &mut expected);
            collect_amplitude_variables_candidate(expression, amplitudes, variables);
            assert_eq!(*variables, expected, "complete amplitude-variable set differs");
        }
        _ => panic!("unknown IREGI_AMPLITUDE_VARIABLE_MODE"),
    }
}

'''
    source = source[:start] + wrapper + candidate + '\n' + legacy + source[end:]
    # Keep the legacy amplitude path independent of the candidate collector.
    start = source.index('fn master_amplitude_legacy(\n')
    end = source.index('\nfn collect_amplitude_variables(', start)
    block = source[start:end]
    assert block.count('collect_amplitude_variables(') == 1
    source = source[:start] + block.replace('collect_amplitude_variables(', 'collect_amplitude_variables_legacy(') + source[end:]
    source += '\n' + (here / 'amplitude_variable_cases.rs').read_text()
    source_path.write_text(source)
    lib = frozen / 'crates/iregi-rust/src/lib.rs'
    lib.write_text(lib.read_text() + '\npub use stability::diagnostic_amplitude_variable_cases;\n')
    patch = subprocess.run(['diff', '-ru', str(original), str(frozen)], capture_output=True, text=True)
    assert patch.returncode == 1
    patch_path = here / 'amplitude-vars-prepared.patch'
    patch_path.write_text(patch.stdout)
    assert all(sha(root / name) == value for name, value in protected_hashes.items())
    record = dict(status='source_prepared_only', source_revision=parent['source_revision'],
                  parent_build_manifest_sha256=sha(parent_path), frozen_source_root=str(frozen.relative_to(root)),
                  source_hashes={str(p.relative_to(frozen)): sha(p) for p in frozen.rglob('*') if p.is_file()},
                  protected_input_hashes=protected_hashes,
                  prepared_patch_sha256=sha(patch_path),
                  scope='Private frozen collector+nway snapshot plus IF-free amplitude-variable discovery via existing Symbolica get_all_indeterminates(true); Num semantics and lazy whole IF generators preserved. Independent recursive legacy collector remains in the legacy amplitude path. Uncompiled and unqualified.')
    (here / 'amplitude-vars-source.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k:record[k] for k in ['status','frozen_source_root','scope']}))


if __name__ == '__main__':
    main()
