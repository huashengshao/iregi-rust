#!/usr/bin/env python3
"""Stage a narrow, unapplied cleanup of the exact qualified adapter sources."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
QUALIFIED = ROOT / 'target/near-vacuum-adapter-current-thin-lto/source'
STAGE = ROOT / 'target/near-vacuum-production-ready/crates/iregi-masters'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def replace_once(source, old, new, changes):
    assert source.count(old) == 1, old
    changes.append({'old': old, 'new': new})
    return source.replace(old, new)

def transform(name, source):
    changes = []
    if name == 'near_vacuum.rs':
        source = replace_once(source,
            '//! Validation-only finite D0 neighborhood. All polynomial/jet/ball operations\n//! belong to Symbolica; production master dispatch is deliberately untouched.\n',
            '//! Finite D0 series and component enclosures in a bounded near-vacuum domain.\n//! Polynomial operations, parameter integration, Taylor jets and ball evaluation\n//! use Symbolica and Numerica. The ordinary master evaluator is unchanged.\n', changes)
        source = replace_once(source, '        let preparation_started = std::time::Instant::now();\n', '', changes)
        pattern = re.compile(r'^(?P<indent> +)eprintln!\(\n.*?^(?P=indent)\);\n', re.M | re.S)
        statements = list(pattern.finditer(source))
        assert len(statements) == 7
        labels = ['Jacobian complete', 'series complete', 'polynomial complete',
                  'integral{variable} complete', 'exact expression ready',
                  'compiled/dualized polynomial', 'tail complete']
        for statement, label in zip(statements, labels):
            text = statement.group()
            assert f'near-vacuum preparation {label}' in text
            assert 'preparation_started.elapsed()' in text
            changes.append({'old': text, 'new': ''})
        source = pattern.sub('', source)
        for old, new in [
            ('validation program exceeds the 500000-instruction preparation limit', 'near-vacuum program exceeds the 500000-instruction preparation limit'),
            ('invalid or oversized validation Dual shape', 'invalid or oversized near-vacuum Dual shape'),
            ('validation stage supports only orders two and four', 'near-vacuum series supports only orders two and four'),
            ('validation parameter polynomial exceeds term limit', 'near-vacuum parameter polynomial exceeds term limit'),
        ]:
            source = replace_once(source, old, new, changes)
        source = replace_once(source, '    pub requested_bits: u32,\n',
            '    /// Diagnostic bit target; the explicit budgets below define acceptance.\n    pub requested_bits: u32,\n', changes)
    elif name == 'certified.rs':
        source = replace_once(source,
            '//! Isolated proposed accuracy-aware master adapter; not production dispatch.\n',
            '//! Explicit accuracy-aware scalar-master evaluation.\n//!\n//! Certified finite D0 results enclose the function of the exact represented\n//! input components. Routing or shift roundoff before this call requires its\n//! own enclosure. The bounded series supports orders two and four, at most\n//! 32 ancestor-closed Taylor components, and total derivative degree at most four.\n//!\n//! Explicit Rational budgets determine acceptance. Ordinary fallback is opt-in\n//! and carries no certificate. The ordinary `MasterEvaluator` API is unchanged.\n', changes)
    else:
        raise AssertionError(name)
    return source, changes

def diff(old, new, before, after):
    return ''.join(difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                        fromfile=before, tofile=after))

def main():
    HERE.mkdir(parents=True, exist_ok=True)
    assert not (STAGE / 'src').exists(), 'Do not overwrite a frozen staging source tree'
    build_path = ROOT / 'validation/near-vacuum-adapter-current/thin-lto/build.json'
    build = json.loads(build_path.read_text())
    qualification_path = ROOT / 'validation/near-vacuum-adapter-current/qualification.json'
    assert sha(qualification_path) == 'e444a5cdd5c0d6dedf4046da53e7aaa0c4f99c4d6487c9001cbfa6d6b0afd7be'
    for path in QUALIFIED.rglob('*.rs'):
        assert sha(path) == build['source_sha256'][str(path.relative_to(ROOT))]
    shutil.copytree(QUALIFIED, STAGE / 'src')
    records = {}
    cleanup = []
    for name in ['near_vacuum.rs', 'certified.rs']:
        original = (QUALIFIED / name).read_text()
        result, changes = transform(name, original)
        (STAGE / 'src' / name).write_text(result)
        # A second reconstruction proves the staged bytes equal only the
        # explicitly enumerated cleanup; no formatter or token normalization is used.
        replay = original
        for change in changes:
            assert replay.count(change['old']) == 1, change['old']
            replay = replay.replace(change['old'], change['new'])
        assert replay == result
        records[name] = {'qualified_sha256': sha(QUALIFIED / name),
                         'staged_sha256': sha(STAGE / 'src' / name),
                         'whitelisted_changes': changes,
                         'only_whitelisted_changes': True}
        cleanup.append(diff(original, result, f'qualified/{name}', f'production-ready/{name}'))
    # The qualified integration additions are unchanged. Ordinary code is
    # compared directly after removing those six explicit additions.
    lib = (STAGE / 'src/lib.rs').read_text()
    qualified_lib = (QUALIFIED / 'lib.rs').read_text()
    assert lib == qualified_lib
    additions = [
        'pub mod certified;\nmod near_vacuum;\n',
        '    InvalidAccuracy(String),\n',
        '            Self::InvalidAccuracy(reason) => write!(f, "invalid accuracy context: {reason}"),\n',
        '    UncertifiedFinite(Option<usize>),\n',
        '            Self::UncertifiedFinite(component) => write!(f, "finite coefficient has no requested accuracy certificate: {component:?}"),\n',
    ]
    ordinary = lib
    for addition in additions:
        assert ordinary.count(addition) == 1
        ordinary = ordinary.replace(addition, '')
    production_lib = ROOT / 'crates/iregi-masters/src/lib.rs'
    assert ordinary == production_lib.read_text(), 'Live ordinary master implementation changed'
    (HERE / 'cleanup.patch').write_text(''.join(cleanup))
    unchanged = {}
    for path in sorted(QUALIFIED.rglob('*.rs')):
        relative = path.relative_to(QUALIFIED)
        if str(relative) in records:
            continue
        staged = STAGE / 'src' / relative
        assert path.read_bytes() == staged.read_bytes()
        unchanged[str(relative)] = sha(path)
    result = {'status': 'unapplied_production_cleanup_staged', 'production_changed': False,
              'qualified_checkpoint': {'path': str(qualification_path.relative_to(ROOT)), 'sha256': sha(qualification_path)},
              'qualified_build_sha256': sha(build_path),
              'formatting': 'Preserved exactly; rustfmt is unavailable in the pinned command environment.',
              'arithmetic_and_dispatch_changes': 'None; exact whitelisted comment/diagnostic text replacements, seven removed eprintln statements, one removed timer binding, only. No general string/token stripping or formatter is used.',
              'changed_files': records, 'unchanged_qualified_sources': unchanged,
              'live_production_lib_sha256': sha(production_lib),
              'ordinary_master_implementation_byte_identical_after_removing_api_additions': True,
              'cleanup_patch_sha256': sha(HERE / 'cleanup.patch'),
              'prepare_script_sha256': sha(Path(__file__)),
              'remaining_work': 'Focused public integration tests and final unapplied production patch; no new arithmetic runtime is claimed by this cleanup proof.'}
    (HERE / 'cleanup-proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'proof': str((HERE / 'cleanup-proof.json').relative_to(ROOT)),
                      'sha256': sha(HERE / 'cleanup-proof.json'), 'removed_trace_sites': 7}))

if __name__ == '__main__':
    main()
