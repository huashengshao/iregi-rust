"""Bytes-only capsule primitives and committed-parent reconstruction.

The strict unified-diff replay follows the committed exact-master-cache checker.
It additionally accepts difflib's a/new-file -0,0 form when that file is absent.
This is source text reconstruction, never symbolic algebra or compilation.
"""
from pathlib import Path
import hashlib
import io
import json
import re
import tarfile

PARENT = 'validation/exact-master-variant-cache'
PARENT_MANIFEST_SHA = '422169dd762d0d5811ecec8986b348664a42aa38fae714d6c5ad7c813146c12f'
CACHE = 'target/exact-master-variant-cache-proposal'
OLD = 'target/public-highpoint/numeric-types-dual'
OLD_CAPSULE = 'validation/highpoint-six-point-numeric-types'
PREFIX = 'target/highpoint-dual-sensitivity'
NUMERIC = PREFIX + '/numerical-v1'
HISTORICAL_ROOT = '/shared/external/iregi/iregi-rust/'
NUMERIC_AUDIT = 'target/resume-20261025-review/dual-sensitivity-numerical-v1-independent-saved-review.json'
NUMERIC_AUDIT_SHA = 'dfa12c20ef5500f26affa1527683785600d63f798e81a35efe8a3dbaa4a75402'
NUMERIC_AUDITOR = 'target/resume-20261025-review/audit_sensitivity_numerical_v1.py'
NUMERIC_AUDITOR_SHA = '8d2ee401cdf11231e1491ab45d8c46a80c659a4d3d02ecb34ae7bbec4e7ac172'


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def descriptor(body):
    return dict(sha256=digest(body), bytes=len(body))


def document(body):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(body, object_pairs_hook=pairs, parse_constant=invalid)


def safe(name):
    p = Path(name)
    require(isinstance(name, str) and bool(name) and not p.is_absolute()
            and '..' not in p.parts and str(p) == name, 'unsafe path: ' + str(name))


def allowed(name, body):
    safe(name)
    require(not body.startswith((b'\x7fELF', b'!<arch>')), 'compiled payload: ' + name)
    require(not re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}', body),
            'license literal: ' + name)


def archive(body, expected):
    files = {}
    with tarfile.open(fileobj=io.BytesIO(body), mode='r:gz') as stream:
        for item in stream:
            require(item.isfile() and item.name not in files, 'invalid archive member')
            payload = stream.extractfile(item).read()
            allowed(item.name, payload)
            files[item.name] = payload
    require({name: descriptor(body) for name, body in files.items()} == expected,
            'archive member inventory mismatch')
    return files


def apply_source_patch(base, patch):
    result = dict(base)
    lines = patch.decode().splitlines(keepends=True)
    index, changed = 0, []
    while index < len(lines):
        require(lines[index].startswith('--- '), 'unexpected patch record')
        old_name = lines[index][4:].rstrip('\n')
        index += 1
        require(index < len(lines) and lines[index].startswith('+++ '), 'patch destination missing')
        new_name = lines[index][4:].rstrip('\n')
        index += 1
        require(new_name.startswith('b/'), 'unsupported patch destination')
        name = new_name[2:]
        safe(name)
        require(name not in changed, 'duplicate patch destination')
        changed.append(name)
        require(old_name in ['a/' + name, '/dev/null'], 'patch path mismatch')
        absent = name not in result
        require(old_name != '/dev/null' or absent, 'new patch file already exists')
        old = [] if absent else result[name].decode().splitlines(keepends=True)
        new, cursor, hunks = [], 0, 0
        while index < len(lines) and lines[index].startswith('@@ '):
            match = re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*\n', lines[index])
            require(match is not None, 'bad hunk header')
            index += 1
            a, ac, b, bc = [int(x) if x is not None else 1 for x in match.groups()]
            require(not absent or (a, ac) == (0, 0), 'absent file patch consumes old lines')
            start = max(0, a - 1)
            require(cursor <= start <= len(old), 'overlapping/out-of-range patch hunk')
            new.extend(old[cursor:start])
            cursor = start
            require(len(new) == max(0, b - 1), 'new hunk position mismatch')
            old_count = new_count = 0
            while index < len(lines) and not lines[index].startswith(('@@ ', '--- ')):
                line = lines[index]
                index += 1
                require(line[:1] in [' ', '+', '-'], 'unsupported patch line')
                body = line[1:]
                if line[0] in ' -':
                    require(cursor < len(old) and old[cursor] == body, 'patch context mismatch')
                    cursor += 1
                    old_count += 1
                if line[0] in ' +':
                    new.append(body)
                    new_count += 1
            require((old_count, new_count) == (ac, bc), 'patch hunk counts mismatch')
            hunks += 1
        require(hunks > 0, 'patch has no hunks')
        new.extend(old[cursor:])
        result[name] = ''.join(new).encode()
    return result, changed


def find_root(here):
    for path in [here] + list(here.parents):
        if (path / 'Cargo.toml').is_file() and (path / PARENT / 'manifest.json').is_file():
            return path
    raise ValueError('committed project root not found')


def load_parent(root):
    """Read committed capsule bytes only; return reconstructed files and pins."""
    manifest_body = (root / PARENT / 'manifest.json').read_bytes()
    require(digest(manifest_body) == PARENT_MANIFEST_SHA, 'committed parent manifest changed')
    manifest = document(manifest_body)
    borrowed = {PARENT + '/manifest.json': manifest_body}
    for name, expected in manifest['files'].items():
        safe(name)
        body = (root / PARENT / name).read_bytes()
        require(descriptor(body) == expected, 'parent capsule file changed: ' + name)
        borrowed[PARENT + '/' + name] = body
    for name, expected in manifest['borrowed_inputs'].items():
        safe(name)
        body = (root / name).read_bytes()
        require(descriptor(body) == expected, 'parent borrowed file changed: ' + name)
        require(name not in borrowed or borrowed[name] == body, 'parent borrowed alias differs')
        borrowed[name] = body
    winddown = document(borrowed['validation/winddown/manifest.json'])
    composition = archive(borrowed[manifest['composition_parent']['path']],
                          winddown['archives']['native-f64-sixpoint-composition']['members'])
    payload = archive(borrowed[PARENT + '/payload.tar.gz'], manifest['payload_archive']['members'])
    source = document(payload[CACHE + '/source-proposal.json'])
    require(digest(payload[CACHE + '/source-proposal.json']) ==
            '1c849a1bc59c4e935f4af4bf309987dd52c2fa0ddf0e4b2576d1a0e5e35ced77', 'parent88 source proposal changed')
    base = {name: composition['proposed/' + name] for name in source['base_files']}
    require(len(base) == 85 and {n: descriptor(b) for n, b in base.items()} == source['base_files'],
            'parent85 source reconstruction mismatch')
    candidate = dict(base)
    for name in source['changed_files']:
        candidate[name] = payload[CACHE + '/proposed/' + name]
    require(len(candidate) == 88 and {n: descriptor(b) for n, b in candidate.items()} == source['proposed_files'],
            'parent88 source reconstruction mismatch')
    patched, changed = apply_source_patch(base, payload[CACHE + '/proposal.patch'])
    require(patched == candidate and changed == source['changed_files'], 'parent patch mismatch')
    files = dict(payload)
    for name, alias in manifest['source_aliases'].items():
        safe(name)
        safe(alias['member'])
        require(name not in files, 'parent alias duplicate')
        files[name] = {'composition': composition, 'candidate': candidate,
                       'payload': payload, 'repository': borrowed}[alias['kind']][alias['member']]
    require({n: descriptor(b) for n, b in files.items()} == manifest['reconstructed_private_files'],
            'parent full reconstruction mismatch')
    old_manifest = document(borrowed[OLD_CAPSULE + '/manifest.json'])
    old = archive(borrowed[old_manifest['parent_archive']['path']], old_manifest['parent_archive']['members'])
    old.update(archive(borrowed[OLD_CAPSULE + '/' + old_manifest['delta_archive']['path']],
                       old_manifest['delta_archive']['members']))
    require({n: descriptor(b) for n, b in old.items()} == old_manifest['reconstructed_private_tree'],
            'original partial typed pilot reconstruction mismatch')
    files.update({OLD + '/' + name: body for name, body in old.items()})
    return candidate, files, borrowed


def reconstruct_sources(base, files, borrowed):
    """Reconstruct all frozen89/92 source versions without private directories."""
    snapshots = {'base': dict(base)}
    for version in [1, 2, 3]:
        source = document(files[PREFIX + f'/source-v{version}.json'])
        patch_name = PREFIX + f'/component-sensitivity-v{version}.patch'
        require(digest(files[patch_name]) == source['patch']['sha256'], 'component patch hash mismatch')
        snapshot, changed = apply_source_patch(base, files[patch_name])
        require(len(snapshot) == 89 and {n: descriptor(b) for n, b in snapshot.items()} == source['files'],
                'prototype89 source reconstruction mismatch')
        require(changed == source['changed_files'], 'prototype changed-file inventory mismatch')
        snapshots[f'source-v{version}'] = snapshot
    numeric_base = {'core/' + name: body for name, body in snapshots['source-v3'].items()}
    numeric_base['main.rs'] = files[NUMERIC + '/base-helpers/main.rs']
    for version in [1, 2]:
        source = document(files[NUMERIC + f'/source-v{version}.json'])
        patch_name = NUMERIC + f'/capture-overlay-v{version}.patch'
        require(digest(files[patch_name]) == source['patch']['sha256'], 'capture patch hash mismatch')
        snapshot, changed = apply_source_patch(numeric_base, files[patch_name])
        require(len(snapshot) == 92 and {n: descriptor(b) for n, b in snapshot.items()} == source['files'],
                'numeric92 source reconstruction mismatch')
        require(changed == source['changed_or_added_files'], 'capture changed-file inventory mismatch')
        snapshots[f'numerical-v{version}'] = snapshot
    build = dict(snapshots['source-v3'])
    protocol = document(files[PREFIX + '/qualification-protocol.json'])
    for name, expected in protocol['compile_fixtures'].items():
        require(digest(borrowed[name]) == expected, 'compile fixture changed')
        build[name] = borrowed[name]
    require(len(build) == 92, 'synthetic build source inventory mismatch')
    snapshots['build-source'] = build
    return snapshots


def validate_independent_numeric_audit(body, get_bytes):
    """Pin the actual raw-data audit to this cohort, never a source-only review."""
    require(digest(body) == NUMERIC_AUDIT_SHA, 'independent numerical audit pin differs')
    audit = document(body)
    require(audit['status'] == 'passed-independent-saved-full-component-sensitivity-numerical-v1-audit'
            and audit['reviewer'] == '/root/resume_auditor' and audit['checks'] == 171834
            and audit['compiled_source_files'] == 92 and audit['complex_parent_slots'] == 528
            and audit['packed_child_rows'] == 156 and audit['precision_pairs'] == 264
            and audit['validated_complete_contexts'] == 182 and audit['mutation_checks'] == 944,
            'independent numerical audit scope differs')
    for field in ['public_dual_qualified', 'rigorous_derivative_uncertainty_qualified',
                  'performance_qualified', 'compiler_or_integral_execution', 'producer_or_comparator_import']:
        require(audit[field] is False, 'independent audit scope promoted: ' + field)
    require(audit['audit_source_sha256'] == NUMERIC_AUDITOR_SHA
            and digest(get_bytes(NUMERIC_AUDITOR)) == NUMERIC_AUDITOR_SHA,
            'independent numerical auditor source differs')
    critical = [NUMERIC + '/' + name for name in ['protocol.json', 'root-execution-grant.json',
                'source-v2.json', 'saved-gate-001/comparison.json']]
    critical += [NUMERIC + '/runtime-' + domain + '-001/result.json'
                 for domain in ['Float128Mass0', 'Float256Mass0', 'Float128Scale', 'Float256Scale']]
    for name in critical:
        require(audit['all_source_and_saved_subjects_sha256'][name] == digest(get_bytes(name)),
                'independent audit does not bind this raw cohort: ' + name)
    require(audit['protocol_sha256'] == digest(get_bytes(NUMERIC + '/protocol.json'))
            and audit['source_v2_sha256'] == digest(get_bytes(NUMERIC + '/source-v2.json')),
            'independent audit protocol/source differs')
    return audit
