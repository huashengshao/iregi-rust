#!/usr/bin/env python3
"""Package current-dependency repeats only after the independent audit passes."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    build = json.loads((HERE / 'thin-lto/build.json').read_text())
    runs = json.loads((HERE / 'thin-lto/runs.json').read_text())
    audit_path = HERE / 'thin-lto/audit.json'
    audit = json.loads(audit_path.read_text())
    assert audit.get('status') == 'passed', audit
    assert len(runs) == 6
    assert all(row['exit_code'] == 0 and not row['timed_out'] and row['inputs_unchanged'] for row in runs)
    previous = ROOT / 'validation/near-vacuum-adapter-v3/qualification.json'
    previous_data = json.loads(previous.read_text())
    old_members = previous_data['source_archive']['members']
    prefix = 'target/near-vacuum-adapter-current-thin-lto/'
    for path, digest in build['source_sha256'].items():
        name = path.removeprefix(prefix)
        prior = 'contour/five_pinch_compare.rs' if name == 'five_pinch_compare.rs' else name
        assert old_members[prior] == digest, name
    typed = []
    for name in ['f64', 'dd', 'float128', 'float256']:
        row = json.loads((HERE / f'thin-lto/{name}.json').read_text())
        prior = json.loads((ROOT / f'validation/near-vacuum-adapter-v3/v3-{name}.json').read_text())
        assert row['status'] == 'isolated_adapter_checks_passed'
        assert row['primary_components_matching_qualified_candidate'] == 24
        typed.append({'numeric': name, 'working_bits': row['working_bits'],
                      'requested_bits': row['requested_bits'], 'accepted_components': 24,
                      'serialized_rows_equal_to_previous_v3': row['rows'] == prior['rows']})
    control_path = HERE / 'build-control-events.jsonl'
    events = [json.loads(line) for line in control_path.read_text().splitlines()]
    intervals = []
    pending = None
    for event in events:
        if event['action'] == 'pause':
            assert pending is None
            pending = event['utc']
        else:
            assert event['action'] == 'resume' and pending is not None
            duration = datetime.datetime.fromisoformat(event['utc']) - datetime.datetime.fromisoformat(pending)
            intervals.append({'paused_utc': pending, 'resumed_utc': event['utc'],
                              'pause_seconds': duration.total_seconds()})
            pending = None
    assert pending is None
    artifacts = {str(path.relative_to(ROOT)): sha(path) for path in sorted(HERE.rglob('*'))
                 if path.is_file() and path.name != 'qualification.json' and '__pycache__' not in path.parts}
    result = {
        'status': 'private_v3_current_release_dependency_checks_passed',
        'production_changed': False,
        'previous_qualification': {'path': str(previous.relative_to(ROOT)), 'sha256': sha(previous)},
        'source_bytes_unchanged_from_previous_v3': True,
        'dependency_closure': build['dependency_closure'],
        'closure_files_verified_before_and_after_build_and_runs': build['closure_files_verified'],
        'complete_workspace_dependency_provenance': True,
        'primary_component_checks': 96, 'typed_cases': typed,
        'dispatch_contract': 'Unsupported valid native shape falls back only under the explicit ordinary policy; required-certificate failures hide values; all-outside rows prepare only N2.',
        'independent_contour': {'working_bits': 256, 'requested_bits': 128,
                                'primal_boxes': 5, 'contracted_results': 1,
                                'scope': 'Exact dyadic fixed-contour inputs; does not enclose production contour mapping or shifted-input rounding.'},
        'retained_failure': 'Initial direct-rustc driver link omitted required thin-LTO flags. No numerical runtime or dependency integrity failure occurred in that attempt.',
        'compiler_pause_intervals': intervals,
        'compiler_diagnostic_time_note': 'Observed build wall times include these coordinated quiet-window pauses; no numerical runtime was paused.',
        'independent_audit': {'path': str(audit_path.relative_to(ROOT)), 'sha256': sha(audit_path)},
        'remaining_limits': [
            'Private source only; production master and core dispatch are unchanged.',
            'Selected exact represented-input certificates only; no general DNS formula certificate.',
            'No public E6 geometry, shifted-input, quadrature or requested256-bit qualification.',
            'Concurrent diagnostic durations are not performance measurements.'
        ],
        'artifacts': artifacts,
    }
    path = HERE / 'qualification.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'qualification': str(path.relative_to(ROOT)), 'sha256': sha(path)}))

if __name__ == '__main__':
    main()
