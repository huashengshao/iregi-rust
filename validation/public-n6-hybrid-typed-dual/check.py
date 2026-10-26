#!/usr/bin/env python3
"""Saved-only public default-Hybrid and typed mixed-Dual evidence replay."""
from pathlib import Path, PurePosixPath
import hashlib
import importlib.util
import io
import json
import sys
import tarfile
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = 'validation/public-n6-affine-mixed-dual'
PARENT_HASH = 'f025d7d43908d2afdd9b121e17b0b7b15e3b7fe19c4df653bd4e34b28f518711'
MIXED = 'target/n6-affine-facade-dual-probe-v1'
TYPED = 'target/n6-public-typed-example-proposal'
TYPED_FINAL = TYPED + '/post-harness-fix'
HYBRID_AUDITOR = MIXED + '/independent_saved_audit_v1.py'
HYBRID_AUDITOR_HASH = 'eda59c1b5486ac611856ff551aef78b1bfc75449c3ad338949f2519f0e564c0c'
TYPED_AUDITOR = TYPED + '/independent_saved_audit_v1.py'
TYPED_AUDITOR_HASH = '35e64deb046966df5f8e88fe095ae5e84d1853662c0578d99b826e4e8989373d'
PREFIX = '/shared/external/iregi/iregi-rust/'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return dict(sha256=sha(body), bytes=len(body))


def load(body):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(body, object_pairs_hook=unique)


def safe(name):
    p = PurePosixPath(name)
    require(name and not p.is_absolute() and '..' not in p.parts and str(p) == name,
            'safe relative identity')


def restore_files(manifest):
    """Return hash-checked project-relative byte aliases for later capsules."""
    own = {str(p.relative_to(HERE)) for p in HERE.rglob('*')
           if p.is_file() and '__pycache__' not in p.parts}
    require(own == set(manifest['capsule_files']) | {'manifest.json'}, 'closed capsule files')
    for name, expected in manifest['capsule_files'].items():
        safe(name)
        require(desc((HERE / name).read_bytes()) == expected, 'exact capsule file')
    for name, expected in manifest['parent_files'].items():
        safe(name)
        require(desc((ROOT / name).read_bytes()) == expected, 'exact declared parent file')
    body = (ROOT / PARENT / 'manifest.json').read_bytes()
    require(sha(body) == manifest['parent_manifest_sha256'] == PARENT_HASH, 'fixed public PV parent')
    spec = importlib.util.spec_from_file_location('public_n6_hybrid_typed_parent', ROOT / PARENT / 'check.py')
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    files = parent.restore_files(parent.load(body))
    members = {}
    with tarfile.open(fileobj=io.BytesIO((HERE / 'payload.tar.gz').read_bytes()), mode='r:gz') as archive:
        for entry in archive:
            safe(entry.name)
            require(entry.isfile() and entry.name not in members, 'unique regular archive entries')
            body = archive.extractfile(entry).read()
            require(desc(body) == manifest['payload_members'].get(entry.name), 'exact archived bytes')
            require(not body.startswith((b'\x7fELF', b'!<arch>\n')) and b'S-130-' not in body,
                    'no native artifact or literal license')
            members[entry.name] = body
    require(set(members) == set(manifest['payload_members']), 'closed archive inventory')
    for alias, row in manifest['aliases'].items():
        safe(alias)
        require(len(set(row) & {'member', 'parent_alias'}) == 1, 'one saved byte selector')
        body = members[row['member']] if 'member' in row else files[row['parent_alias']]
        require(desc(body) == {key: row[key] for key in ('sha256', 'bytes')}, 'exact alias bytes')
        require(alias not in files or files[alias] == body, 'no inherited alias overwrite')
        files[alias] = body
    for name in own:
        files[manifest['capsule_directory'] + '/' + name] = (HERE / name).read_bytes()
    return files


def replay(files, manifest):
    def read(alias):
        return load(files[alias])

    for alias, expected in manifest['receipt_pins'].items():
        require(sha(files[alias]) == expected, 'exact saved receipt')
    for alias, mapping in manifest['receipt_input_aliases'].items():
        r = read(alias)
        require(r['inputs_unchanged'] is True and r['cleanup_errors'] == []
                and r.get('cancellation') is None and r.get('post_cancellation') is None,
                'saved unchanged inputs and cleanup, including retained failures')
        require(set(mapping) == set(r['inputs']), 'complete actual input mapping')
        for absolute, expected in r['inputs'].items():
            if absolute in manifest['omitted_native_inputs']:
                require(mapping[absolute] is None and manifest['omitted_native_inputs'][absolute] == expected,
                        'explicit metadata-only native input')
            else:
                require(mapping[absolute] in files and sha(files[mapping[absolute]]) == expected,
                        'exact frozen guarded input')
        require(set(manifest['receipt_output_aliases'][alias]) == set(r['outputs']), 'complete output mapping')
        base = str(PurePosixPath(alias).parent)
        for name, expected in r['outputs'].items():
            resolved = manifest['receipt_output_aliases'][alias][name]
            if resolved is None:
                require(manifest['omitted_native_inputs'][PREFIX + base + '/' + name] == expected,
                        'explicit metadata-only native output')
            else:
                require(sha(files[resolved]) == expected, 'actual saved output bytes')
        require(all(s['owned_group_gone'] is True and not s.get('timeout') for s in r['steps']),
                'saved owned process groups terminated')
    for alias, sources in manifest['actual_source_files'].items():
        r = read(alias)
        require(r['status'] == 'passed' and r['source_files'] == sources
                and all(s['returncode'] == 0 for s in r['steps']), 'actual passed source build')
        prefix = manifest['actual_source_snapshots'][alias]
        for name, expected in sources.items():
            require(sha(files[prefix + '/' + name]) == expected, 'actual selected compiled source bytes')
        events = [load(line) for line in files[str(PurePosixPath(alias).parent) + '/cargo-0.log'].decode().splitlines()
                  if line.startswith('{')]
        require([v['success'] for v in events if v.get('reason') == 'build-finished'] == [True],
                'actual successful Cargo terminal event')
        for product in r['products'].values():
            if isinstance(product, dict) and 'cargo_event' in product:
                event = read(str(PurePosixPath(alias).parent) + '/' + product['cargo_event'])
                require(event in events and event['reason'] == 'compiler-artifact'
                        and event['executable'] == product['cargo_executable']
                        and manifest['omitted_native_inputs'][product['path']] == product['sha256'],
                        'actual omitted Cargo artifact association')
    for phase in ('build-001', 'build-002'):
        require(len(manifest['actual_source_files'][TYPED + '/' + phase + '/receipt.json']) == 120,
                'actual typed120-source build context')
    index = read(TYPED + '/typed-evidence-index.json')
    require(sha(files[TYPED + '/typed-evidence-index.json']) ==
            'aaac27b91e515679c6b41553d4fc3adf3575f741f243ba957e42e632c39b1318', 'fixed typed evidence index')
    for alias, expected in index['pins'].items():
        require(sha(files[alias]) == expected, 'every original typed evidence index pin')

    def audit_module(alias, expected):
        require(sha(files[alias]) == expected, 'fixed independent arithmetic module')
        module = types.ModuleType('frozen_saved_' + str(len(alias)))
        exec(compile(files[alias], '<frozen saved arithmetic>', 'exec'), module.__dict__)
        return module

    def reproduced(auditor, directory, case):
        context = read(directory + '/saved-audit-context.json')
        actual = auditor.audit(lambda alias: files[alias], context, case)
        expected = read(directory + '/independent-saved-audit.json')
        require(actual == {k: v for k, v in expected.items() if not k.startswith('owner_wrapper_')},
                'entire independent numerical/guard report reproduced: ' + case)
        if directory + '/gate.json' in files:
            gate = read(directory + '/gate.json')
            require(gate['passed'] is True and gate['failures'] == [], 'original successful saved gate')
            require(gate['report']['sha256'] == sha(files[directory + '/independent-saved-audit.json'])
                    and gate['context']['sha256'] == sha(files[directory + '/saved-audit-context.json']),
                    'gate binds the exact original context/report')
        return actual

    mixed_audit = audit_module(HYBRID_AUDITOR, HYBRID_AUDITOR_HASH)
    hybrid = reproduced(mixed_audit, MIXED + '/hybrid/capture-mixed256-001', 'mixed256')
    require(hybrid['passed'] is True and hybrid['findings'] == [] and hybrid['pair_pending'] is False
            and hybrid['requested_algorithm'] == 'Hybrid'
            and hybrid['requested_algorithm_origin'] == 'public_default'
            and hybrid['actual_capture_algorithm_origins'] == {'mixed128': 'public_default', 'mixed256': 'public_default'}
            and hybrid['original_quad_comparisons'] == 30240
            and hybrid['precision_pair_comparisons'] == 75600
            and hybrid['child_precision_pair_comparisons'] == 60480
            and hybrid['full_component_contexts'] == 15
            and hybrid['known_no_quadrature_child_rows'] == 12, 'complete unchanged-default Hybrid cohort')
    typed_audit = audit_module(TYPED_AUDITOR, TYPED_AUDITOR_HASH)
    dd = reproduced(typed_audit, TYPED_FINAL + '/capture-dd-001', 'dd')
    f64 = reproduced(typed_audit, TYPED_FINAL + '/capture-f64-001', 'f64')
    require(dd['passed'] is True and dd['numerically_qualified'] is True
            and dd['saved_metadata_audit_passed'] is True and dd['findings'] == dd['guard_failures'] == []
            and dd['successful_parent_rows'] == 3 and dd['static_dynamic_base_exact'] is True
            and {k: v['count'] for k, v in dd['comparisons'].items()} ==
                {'original_quad': 15120, 'Float128_control': 15120, 'base_scale': 5040},
            'all35280 DoubleFloat numerical gates')
    require(f64['passed'] is False and f64['numerically_qualified'] is False
            and f64['saved_metadata_audit_passed'] is True and f64['findings'] == []
            and f64['numerical_disagreement'] is False and f64['successful_parent_rows'] == 0
            and len(f64['guard_failures']) == 3
            and all('pv_node_12' in v['status'] and 'Taylor component 2' in v['status'] for v in f64['guard_failures'])
            and all(v['count'] == 0 for v in f64['comparisons'].values()),
            'real f64 guard outcomes remain numerically unqualified with zero invented comparisons')
    require(manifest['full_allfeature_Dual_qualified'] is False and manifest['performance_qualified'] is False,
            'no full-domain or performance promotion')
    return dict(status='passed_portable_default_Hybrid_and_typed_saved_evidence',
                restored_aliases=len(files),
                Hybrid_original_quad_complex_comparisons=hybrid['original_quad_comparisons'],
                Hybrid_precision_pair_complex_comparisons=hybrid['precision_pair_comparisons'],
                Hybrid_child_precision_pair_complex_comparisons=hybrid['child_precision_pair_comparisons'],
                Hybrid_full_component_contexts_per_precision=15,
                Hybrid_known_no_quadrature_child_rows_per_precision=12,
                Hybrid_maximum_original_error=hybrid['max_original_error'],
                Hybrid_maximum_precision_pair_error=hybrid['max_pair_error'],
                DoubleFloat_comparisons=dd['comparisons'], typed_selected_source_files=120,
                f64_saved_metadata_audit_passed=True, f64_numerically_qualified=False,
                f64_real_guard_failures=3, f64_numerical_comparisons=0,
                initial_input_preparation_refusal_preserved=True,
                full_allfeature_Dual_qualified=False, current_ELF_or_process_probe=False,
                native_or_integral_execution=False, performance_qualified=False)


if __name__ == '__main__':
    manifest = load((HERE / 'manifest.json').read_bytes())
    result = replay(restore_files(manifest), manifest)
    result['manifest_sha256'] = sha((HERE / 'manifest.json').read_bytes())
    print(json.dumps(result, indent=2))
