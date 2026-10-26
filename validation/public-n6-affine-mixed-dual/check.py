#!/usr/bin/env python3
"""Replay saved public N6 mixed-Dual PV evidence; Python standard library only."""
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
PARENT = 'validation/affine-power-generalized-current-core'
PARENT_HASH = '0f9207da517720f4919ab8232fb3ea47dd8c50663e93cdd98b7b928b027dfbf3'
PREFIX = '/shared/external/iregi/iregi-rust/'
PRIVATE = 'target/n6-affine-facade-dual-probe-v1'
BUILD = 'target/affine-power-observed-quadrature-proposal/build-001'
AUDITOR = PRIVATE + '/independent_saved_audit_v1.py'
AUDITOR_HASH = 'eda59c1b5486ac611856ff551aef78b1bfc75449c3ad338949f2519f0e564c0c'


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
            'safe project-relative identity')


def restore_files(manifest):
    """Return immutable project-relative bytes, including the pinned parent."""
    own = {str(p.relative_to(HERE)) for p in HERE.rglob('*')
           if p.is_file() and '__pycache__' not in p.parts}
    require(own == set(manifest['capsule_files']) | {'manifest.json'}, 'closed capsule files')
    for name, expected in manifest['capsule_files'].items():
        safe(name)
        require(desc((HERE / name).read_bytes()) == expected, 'exact capsule bytes: ' + name)
    for name, expected in manifest['parent_files'].items():
        safe(name)
        require(desc((ROOT / name).read_bytes()) == expected, 'exact parent bytes: ' + name)
    raw = (ROOT / PARENT / 'manifest.json').read_bytes()
    require(sha(raw) == manifest['parent_manifest_sha256'] == PARENT_HASH, 'fixed affine-power parent')
    spec = importlib.util.spec_from_file_location('public_n6_dual_saved_parent', ROOT / PARENT / 'check.py')
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    files = parent.restore_files(parent.load(raw))
    members = {}
    with tarfile.open(fileobj=io.BytesIO((HERE / 'payload.tar.gz').read_bytes()), mode='r:gz') as archive:
        for item in archive:
            safe(item.name)
            require(item.isfile() and item.name not in members, 'unique regular archive member')
            body = archive.extractfile(item).read()
            require(desc(body) == manifest['payload_members'].get(item.name), 'exact archived bytes')
            require(not body.startswith((b'\x7fELF', b'!<arch>\n')) and b'S-130-' not in body,
                    'no compiled product or literal license')
            members[item.name] = body
    require(set(members) == set(manifest['payload_members']), 'closed archive inventory')
    for alias, row in manifest['aliases'].items():
        safe(alias)
        require(len(set(row) & {'member', 'parent_alias'}) == 1, 'one archived byte selector')
        body = members[row['member']] if 'member' in row else files[row['parent_alias']]
        require(desc(body) == {key: row[key] for key in ('sha256', 'bytes')}, 'exact saved alias')
        require(alias not in files or files[alias] == body, 'no parent alias overwrite')
        files[alias] = body
    for name in own:
        files[manifest['capsule_directory'] + '/' + name] = (HERE / name).read_bytes()
    return files


def replay(files, manifest):
    def read(alias):
        return load(files[alias])

    def guards(alias):
        r = read(alias)
        require(r['inputs_unchanged'] is True and r['cleanup_errors'] == []
                and r.get('cancellation') is None and r.get('post_cancellation') is None,
                'saved unchanged inputs and clean termination: ' + alias)
        base = str(PurePosixPath(alias).parent)
        for path, expected in r['inputs'].items():
            if path in manifest['omitted_native_inputs']:
                require(expected == manifest['omitted_native_inputs'][path], 'explicit omitted native input')
                continue
            name = manifest['receipt_input_aliases'][alias][path]
            require(name is not None, 'unavailable input must be an explicit omitted executable')
            require(name in files and sha(files[name]) == expected, 'available actual saved input: ' + name)
        for name, expected in r.get('outputs', {}).items():
            absolute = PREFIX + base + '/' + name
            if absolute in manifest['omitted_native_inputs']:
                require(expected == manifest['omitted_native_inputs'][absolute], 'explicit omitted native output')
            else:
                require(sha(files[base + '/' + name]) == expected, 'exact saved output')
        require(all(s['status'] == 'exited' and s['returncode'] == 0
                    and s['owned_group_gone'] is True for s in r['steps']), 'saved actual successful children')
        return r

    for alias, expected in manifest['receipt_pins'].items():
        require(sha(files[alias]) == expected, 'exact pinned actual/historical receipt')
    for alias, selected in manifest['actual_source_files'].items():
        r = guards(alias)
        require(r['source_files'] == selected, 'complete actual selected source inventory')
        prefix = manifest['actual_source_snapshots'][alias]
        for name, expected in selected.items():
            require(sha(files[prefix + '/' + name]) == expected, 'exact source context body')
    built = read(BUILD + '/receipt.json')
    source_files = manifest['actual_source_files'][BUILD + '/receipt.json']
    require(built['status'] == 'passed' and built['source_files'] == source_files
            and len(source_files) == 119, 'actual complete119 selected compiled sources')
    for name, expected in source_files.items():
        require(sha(files[BUILD + '/source-snapshot/' + name]) == expected, 'actual compiled source body')
    events = [load(line) for line in files[BUILD + '/cargo-0.log'].decode().splitlines()
              if line.startswith('{')]
    require([v['success'] for v in events if v.get('reason') == 'build-finished'] == [True],
            'actual successful Cargo terminal event')
    product = built['products']['library-tests']
    event = read(BUILD + '/' + product['cargo_event'])
    require(event in events and event['reason'] == 'compiler-artifact'
            and event['executable'] == product['cargo_executable']
            and manifest['omitted_native_inputs'][product['path']] == product['sha256'],
            'actual Cargo product association; executable omitted')
    for bits in (128, 256):
        base = PRIVATE + '/pv/capture-mixed' + str(bits) + '-001'
        guards(base + '/receipt.json')
        gate = read(base + '/gate.json')
        require(gate['passed'] is True and gate['failures'] == [], 'actual saved independent gate')
        for field, name in [('report', 'independent-saved-audit.json'),
                            ('context', 'saved-audit-context.json')]:
            require(gate[field]['path'] == PREFIX + base + '/' + name
                    and gate[field]['sha256'] == sha(files[base + '/' + name]), 'gate byte association')
        require(gate['checker'] == dict(path=PREFIX + AUDITOR, sha256=AUDITOR_HASH), 'fixed independent auditor')
    source = files[AUDITOR]
    require(sha(source) == AUDITOR_HASH, 'unaltered independent math checker')
    auditor = types.ModuleType('frozen_public_n6_independent_math')
    exec(compile(source, '<frozen independent saved arithmetic>', 'exec'), auditor.__dict__)
    base = PRIVATE + '/pv/capture-mixed256-001'
    context = load(files[base + '/saved-audit-context.json'])
    actual = auditor.audit(lambda alias: files[alias], context, 'mixed256')
    expected = load(files[base + '/independent-saved-audit.json'])
    require(actual == {k: v for k, v in expected.items() if not k.startswith('owner_wrapper_')},
            'full independent parent/child/context/reference replay exactly reproduces saved report')
    require(actual['passed'] is True and actual['findings'] == [] and actual['pair_pending'] is False,
            'complete mixed precision pair passes')
    require(actual['original_quad_comparisons'] == 30240
            and actual['precision_pair_comparisons'] == 75600
            and actual['child_precision_pair_comparisons'] == 60480
            and actual['full_component_contexts'] == 15
            and actual['known_no_quadrature_child_rows'] == 12
            and actual['requested_algorithm'] == 'PassarinoVeltman'
            and actual['requested_algorithm_origin'] == 'explicit_pv', 'fixed scoped complete PV coverage')
    for directory in ('n6-rank6-full-dual', 'n6-rank6-full-dual-intern-v1'):
        prefix = 'target/' + directory + '/capture-mixed128-001'
        r = read(prefix + '/receipt.json')
        require(r['status'] == 'failed' and r['inputs_unchanged'] is True
                and r['cleanup_errors'] == [] and len(r['steps']) == 1
                and r['steps'][0]['returncode'] == -6
                and r['steps'][0]['owned_group_gone'] is True, 'prior ThinSix allocation failure remains failed')
        for name, expected_hash in r['outputs'].items():
            require(sha(files[prefix + '/' + name]) == expected_hash, 'exact prior failed output')
        c = read(prefix + '/capture.json')
        require(c['status'] == 'evaluating_batch' and c['calls'] == []
                and b'memory allocation of ' in files[prefix + '/native.log'], 'prior failure has no completed tensor array')
    require(manifest['Hybrid_qualified'] is False and manifest['full_allfeature_Dual_qualified'] is False
            and manifest['performance_qualified'] is False, 'no unexecuted domain or speed promotion')
    return dict(status='passed_portable_public_N6_PV_mixed_Dual_saved_replay',
                source_files=len(source_files), restored_aliases=len(files),
                original_quad_complex_comparisons=actual['original_quad_comparisons'],
                precision_pair_complex_comparisons=actual['precision_pair_comparisons'],
                child_precision_pair_complex_comparisons=actual['child_precision_pair_comparisons'],
                full_component_contexts_per_precision=15,
                known_no_quadrature_child_rows_per_precision=12,
                preserved_prior_allocation_failures=2,
                maximum_original_error=actual['max_original_error'],
                maximum_precision_pair_error=actual['max_pair_error'],
                Hybrid_qualified=False, full_allfeature_Dual_qualified=False,
                current_ELF_or_process_probe=False, native_or_integral_execution=False,
                performance_qualified=False)


if __name__ == '__main__':
    manifest = load((HERE / 'manifest.json').read_bytes())
    result = replay(restore_files(manifest), manifest)
    result['manifest_sha256'] = sha((HERE / 'manifest.json').read_bytes())
    print(json.dumps(result, indent=2))
