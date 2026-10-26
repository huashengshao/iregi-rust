#!/usr/bin/env python3
"""Portable saved replay of five ordinary samples and two mass-FD step sizes."""
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
FD = 'target/n6-affine-facade-dual-probe-v1/fd-source'
AUDITOR = FD + '/admit_saved.py'
AUDITOR_HASH = '6742e1fac23f64e8850bc9ae4b10398ff26b78c0996f51bb446ee7509ba54d59'
INDEX_HASH = 'd2c51cf4188d670080b638765d7fdd461cbae7964b90f03e21c5862198fc8f44'
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

    index = read(FD + '/fd-evidence-index.json')
    require(sha(files[FD + '/fd-evidence-index.json']) == INDEX_HASH, 'fixed actual FD index')
    for alias, expected in index['files'].items():
        require(desc(files[alias]) == expected, 'every original FD file descriptor')
    for alias, expected in index['audit_read_bindings'].items():
        require(sha(files[alias]) == expected, 'every original pure-audit read binding')
    sources = manifest['inherited_actual_observer_source_files']
    require(len(sources) == 119 and manifest['actual_source_files'] == {}
            and read(manifest['actual_build_receipt'])['source_files'] == sources,
            'reuse actual observer context; no invented new source build')
    source_prefix = str(PurePosixPath(manifest['actual_build_receipt']).parent) + '/source-snapshot/'
    for name, expected in sources.items():
        require(sha(files[source_prefix + name]) == expected, 'inherited actual observer source body')
    for alias, expected in manifest['receipt_pins'].items():
        require(sha(files[alias]) == expected, 'exact actual receipt')
    for alias, mapping in manifest['receipt_input_aliases'].items():
        r = read(alias)
        require(r['inputs_unchanged'] is True and r['cleanup_errors'] == []
                and r.get('cancellation') is None and r.get('post_cancellation') is None,
                'saved unchanged inputs and cleanup, including the retained weight failure')
        require(set(mapping) == set(r['inputs']), 'complete actual guarded input mapping')
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
                        'explicit omitted native output')
            else:
                require(sha(files[resolved]) == expected, 'actual saved output bytes')
        require(all(s['owned_group_gone'] is True and not s.get('timeout') for s in r['steps']),
                'saved owned group termination')
    require(sha(files[AUDITOR]) == AUDITOR_HASH, 'fixed independently authored admission callback')
    audit = types.ModuleType('frozen_public_mass_FD_saved_arithmetic')
    exec(compile(files[AUDITOR], '<frozen saved finite-difference arithmetic>', 'exec'), audit.__dict__)
    directory = FD + '/fd-capture-001'
    actual = audit.audit(lambda alias: files[alias], read(directory + '/saved-audit-context.json'))
    expected = read(directory + '/independent-saved-audit.json')
    require(actual == {k: v for k, v in expected.items() if not k.startswith('owner_wrapper_')},
            'entire independent FD numerical/observer/convergence report reproduced')
    require(actual['passed'] is True and actual['failures'] == []
            and actual['final_tolerance'] == '1e-10' and actual['floor_changes_final_tolerance'] is False,
            'original fine-step accuracy gates unchanged')
    require(len(actual['comparisons']) == 6720 and len(actual['convergence']) == 1680
            and actual['final_order_target_comparisons'] == 3360
            and actual['raw_ordinary_complex_slots'] == 4200
            and actual['resolved_transitions'] == 420
            and actual['unresolved_floor_transitions'] == 1260
            and actual['resolved_scalar_finite_firstmass_witness'] == 1,
            'all prescribed comparisons and explicit convergence classifications')
    observed = actual['actual_public_observation']
    require(observed['observed_parent_rows'] == 5 and observed['observed_child_rows'] == 20
            and observed['full_native_contexts'] == 25
            and observed['known_no_quadrature_child_rows'] == 20,
            'actual complete ordinary parent and child context coverage')
    require(len(actual['retained_weight_preparation_failures']) == 1
            and actual['public_Dual_qualified'] is False and actual['rigorous_error_qualified'] is False
            and actual['performance_qualified'] is False, 'retained preparation failure and scoped numerical qualification')
    gate = read(directory + '/gate.json')
    require(gate['passed'] is True and gate['failures'] == []
            and gate['report']['sha256'] == sha(files[directory + '/independent-saved-audit.json'])
            and gate['context']['sha256'] == sha(files[directory + '/saved-audit-context.json'])
            and gate['checker'] == dict(path=PREFIX + AUDITOR, sha256=AUDITOR_HASH),
            'exact original terminal gate context/checker/report association')
    require(manifest['full_allfeature_Dual_qualified'] is False and manifest['performance_qualified'] is False,
            'no broader feature or speed promotion')
    return dict(status='passed_portable_five_sample_two_step_first_second_mass_FD_saved_replay',
                restored_aliases=len(files), inherited_actual_observer_source_files=119,
                ordinary_parent_rows=5, actual_N5_child_rows=20, full_native_contexts=25,
                explicit_KnownNoQuadrature_child_rows=20, raw_ordinary_complex_slots=4200,
                recorded_comparisons=6720, fine_step_accuracy_gates=3360,
                resolved_convergence_classifications=420, explicit_floor_classifications=1260,
                nonpolynomial_scalar_firstmass_witness=1,
                final_tolerance='1e-10', floor_changes_final_tolerance=False,
                fine_step_normalized_error_displays={k: v for k, v in index['decimal_sqrt_of_saved_max_error_squared_display_only'].items() if 'h18' in k},
                original_Symbolica_weight_preparation_failure_preserved=True,
                full_allfeature_Dual_qualified=False, current_ELF_or_process_probe=False,
                native_or_integral_execution=False, performance_qualified=False)


if __name__ == '__main__':
    manifest = load((HERE / 'manifest.json').read_bytes())
    result = replay(restore_files(manifest), manifest)
    result['manifest_sha256'] = sha((HERE / 'manifest.json').read_bytes())
    print(json.dumps(result, indent=2))
