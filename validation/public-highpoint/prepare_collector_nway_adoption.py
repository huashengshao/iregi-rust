"""Write review-only production patches; never modify production source."""
from pathlib import Path
import difflib
import hashlib
import json
import subprocess


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section(text, start, end):
    return text[text.index(start):text.index(end, text.index(start))]


def patch(before, after):
    return ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
        fromfile='a/crates/iregi-rust/src/stability.rs', tofile='b/crates/iregi-rust/src/stability.rs'))


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    capture_path = here / 'collector-capture-v4-qualification.json'
    capture = json.loads(capture_path.read_text())
    assert capture['status'] == 'qualified' and capture['paired_cases'] == 29
    assert capture['required_ordinary_successes'] == 26 and capture['known_ordinary_guard_parity_cases'] == 3
    checks_path = here / 'collector-nway-checks.json'
    checks = json.loads(checks_path.read_text())
    assert checks['status'] == 'passed' and [row['checked_cases'] for row in checks['runs']] == [20, 38, 35]
    original_path = root / 'target/public-highpoint/use-dedup-full/original/crates/iregi-rust/src/stability.rs'
    collector_path = root / 'target/public-highpoint/use-dedup-full/source/crates/iregi-rust/src/stability.rs'
    production_path = root / 'crates/iregi-rust/src/stability.rs'
    original = original_path.read_text()
    production = production_path.read_text()
    baseline = section(original, 'fn collect_alias_uses(', 'fn collect_denominators(')
    optimized = section(collector_path.read_text(), 'fn record_alias_use(', 'fn collect_denominators(')
    qualified_collector = original.replace(baseline, optimized, 1)
    assert patch(original, qualified_collector) == (here / 'use-dedup-production.patch').read_text(), 'Collector algorithm must be the exact qualified delta'
    assert section(production, 'fn collect_alias_uses(', 'fn collect_denominators(') == baseline
    collector_only = production.replace(baseline, optimized, 1)
    collector_patch = patch(production, collector_only)
    function = section(original, 'fn master_amplitude(', 'fn collect_amplitude_variables(')
    replacements = {
        'let mut result = Atom::new();': 'let mut contributions = Vec::with_capacity(polynomial.nterms());',
        'result = result + coefficient * &variable_amplitudes[index];': 'contributions.push(coefficient * &variable_amplitudes[index]);',
        'result += coefficient;': 'contributions.push(coefficient);',
        'Ok(result)': 'Ok(Atom::add_many(contributions))',
    }
    changed = function
    for before, after in replacements.items():
        assert changed.count(before) == 1
        changed = changed.replace(before, after)
    production_amplitude = section(production, 'fn master_amplitude(', 'fn collect_amplitude_variables(')
    assert production_amplitude in [function, changed], 'Production amplitude differs from both qualified algorithms'
    nway_already_present = production_amplitude == changed
    combined = collector_only if nway_already_present else collector_only.replace(function, changed, 1)
    assert all(marker not in combined for marker in ['HIGHPOINT_PHASE', 'HIGHPOINT_PRIMAL', 'IREGI_PRIMAL_SUM_MODE'])
    target = root / 'target/public-highpoint/adoption-review'
    assert not target.exists()
    target.mkdir()
    (target / 'stability.rs').write_text(combined)
    files = {'collector-adoption.patch': collector_patch,
             'nway-adoption.patch': patch(original, original.replace(function, changed, 1)),
             'collector-nway-adoption.patch': patch(production, combined)}
    for name, text in files.items():
        assert not (here / name).exists()
        (here / name).write_text(text)
    record = dict(status='prepared_not_applied', source_revision='6b24c0372022e22606a1ac85f30c7fa579fb41f0',
                  target_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                  nway_already_present_in_production=nway_already_present,
                  production_source_sha256=sha(production_path), review_source_path=str((target / 'stability.rs').relative_to(root)),
                  review_source_sha256=sha(target / 'stability.rs'),
                  scope='Exact reviewed collector delta, rebased by exact collector/amplitude body checks onto current production source. Separate original-relative four-line n-way patch supplied for review; it is omitted from the combined current-relative patch when already present in production. No profiling, counters, environment modes, reference implementation, or stability threshold changes. Paired snapshots qualify collector;20 exact expression/error witnesses plus73 semantic tests qualify the combined private algorithm. Full N6 coverage is separate.',
                  artifacts={str(p.relative_to(root)): sha(p) for p in [capture_path, checks_path,
                    original_path, collector_path, here / 'use-dedup-production.patch', Path(__file__),
                    *[here / name for name in files]]})
    (here / 'collector-nway-adoption.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
