#!/usr/bin/env python3
"""Package terminal saved bytes, waiting for a separate audit-clear before sealing.

No compiler, evaluator, integral, process launch, legacy dependency census or
compiled artifact hashing occurs here. Compiled digest evidence comes from the
unchanged producer receipts; compiled instances and bytecode are omitted.
"""
from pathlib import Path
import argparse
import gzip
import io
import json
import sys
import tarfile
sys.dont_write_bytecode = True

from portable import (CACHE, NUMERIC, NUMERIC_AUDIT, NUMERIC_AUDIT_SHA,
                      NUMERIC_AUDITOR, NUMERIC_AUDITOR_SHA, PARENT, PREFIX, allowed, descriptor,
                      digest, document, find_root, load_parent,
                      reconstruct_sources, require, safe, validate_independent_numeric_audit)

HERE = Path(__file__).resolve().parent
ROOT = find_root(HERE)
FINAL = ROOT / 'validation/highpoint-dual-sensitivity'
CODE = ['package.py', 'check.py', 'portable.py', 'saved_numeric.py', 'README.md']
DOMAINS = ['Float128Mass0', 'Float256Mass0', 'Float128Scale', 'Float256Scale']
EVIDENCE_FOLDERS = {'base', 'proposed', 'source-v1', 'source-v2', 'source-v3',
                    'build-source', 'build-001', 'tests-001', 'numerical-v1', '__pycache__'}
EXTRAS = [
    'target/resume-20261025-review/dual-sensitivity-prototype-independent-saved-review.json',
    'target/resume-20261025-review/audit_dual_sensitivity_saved.py',
    NUMERIC_AUDIT,
    NUMERIC_AUDITOR,
    'target/routing-rational-full-core/first-001/n6_unit-candidate.json',
    'target/routing-rational-full-core/remaining-001/n6_dot0-candidate.json',
    'target/routing-rational-full-core/remaining-001/n6_dot0-reference.json',
    'target/routing-rational-full-core/continuation-v3/continuation-001/n6_dot0-comparison.json',
    'target/resume-20261025-review/routing-v3-dot0-independent-saved-numeric-audit.json',
    'target/resume-20261025-review/audit_routing_v3_dot0_saved.py',
    'target/resume-20261025-review/routing-full-core-v2-first-independent-saved-audit.json',
]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def recorded_products():
    """Historical digests only; do not read/hash the omitted products."""
    products = {}
    for prefix, receipt in [(PREFIX, 'build-001/build.json'),
                            (NUMERIC, 'build-001/build.json')]:
        for name, expected in document((ROOT / prefix / receipt).read_bytes())['outputs'].items():
            products[prefix + '/build-001/' + name] = expected
    tests = document((ROOT / PREFIX / 'tests-001/tests.json').read_bytes())
    products[PREFIX + '/tests-001/frozen-component-tests'] = tests['executed_binary_sha256']
    for domain in DOMAINS:
        prefix = NUMERIC + '/runtime-' + domain + '-001'
        run = document((ROOT / prefix / 'run.json').read_bytes())
        products[prefix + '/frozen-component-probe'] = run['executed_binary_sha256']
    require(len(products) == 9, 'unexpected compiled product inventory')
    return products


def source_alias(name, snapshots):
    local = name[len(PREFIX) + 1:]
    folders = [('base/', 'base'), ('proposed/', 'source-v3'),
               ('source-v1/', 'source-v1'), ('source-v2/', 'source-v2'),
               ('source-v3/', 'source-v3'), ('build-source/', 'build-source'),
               ('numerical-v1/source-v1/', 'numerical-v1'),
               ('numerical-v1/source-v2/', 'numerical-v2')]
    for prefix, snapshot in folders:
        if local.startswith(prefix):
            member = local[len(prefix):]
            require(member in snapshots[snapshot], 'unmapped source snapshot: ' + name)
            return dict(snapshot=snapshot, member=member)
    if local.startswith('numerical-v1/core/'):
        member = local[len('numerical-v1/'):]
        require(member in snapshots['numerical-v2'], 'unmapped working capture source')
        return dict(snapshot='numerical-v2', member=member)
    if local == 'numerical-v1/main.rs':
        return dict(snapshot='numerical-v2', member='main.rs')
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--draft', type=Path, help='new target-only draft output directory')
    mode.add_argument('--seal', action='store_true', help='seal final committed capsule after audit-clear')
    parser.add_argument('--audit-clear', type=Path, help='root/parent audit-clear JSON, required for --seal')
    args = parser.parse_args()
    require(Path.cwd().resolve() == ROOT, 'run from project root')
    destination = FINAL if args.seal else args.draft.resolve()
    require(not destination.exists(), 'capsules are immutable; output already exists')
    if not args.seal:
        require(destination.is_relative_to(ROOT / 'target'), 'draft output must remain under target')
    clear, extras = None, list(EXTRAS)
    if args.seal:
        require(args.audit_clear is not None, 'independent audit and explicit audit-clear required')
        clear_path = args.audit_clear.resolve()
        require(clear_path.is_relative_to(ROOT), 'audit-clear must be retained inside project')
        clear = document(clear_path.read_bytes())
        require(clear['status'] == 'cleared' and clear['grantor'] in ['/root', '/root/dual_sensitivity_research'],
                'root/parent audit-clear missing')
        require(clear['package_code_sha256'] == {name: digest((HERE / name).read_bytes()) for name in CODE},
                'audit-clear does not bind these exact five reviewed package files')
        require(clear['source_manifest_sha256'] ==
                'dfd61c594979b41057d3ef745eab60cf96ffb5b86fbd1c8aa97828da673ca045',
                'audit-clear source differs')
        audit = clear['independent_numeric_audit']
        safe(audit['path'])
        body = (ROOT / audit['path']).read_bytes()
        require(audit == dict(path=NUMERIC_AUDIT, sha256=NUMERIC_AUDIT_SHA), 'cleared numerical audit differs')
        validate_independent_numeric_audit(body, lambda name: (ROOT / name).read_bytes())
        extras.append(str(clear_path.relative_to(ROOT)))
        for name, expected in clear['additional_evidence'].items():
            safe(name)
            require(digest((ROOT / name).read_bytes()) == expected, 'cleared evidence changed: ' + name)
            extras.append(name)
        extras.append(audit['path'])
    base, inherited, borrowed = load_parent(ROOT)
    require(digest((ROOT / NUMERIC_AUDIT).read_bytes()) == NUMERIC_AUDIT_SHA
            and digest((ROOT / NUMERIC_AUDITOR).read_bytes()) == NUMERIC_AUDITOR_SHA,
            'actual independent numerical audit/auditor changed')
    # Small source/manifests suffice to reconstruct every duplicate source tree.
    raw = {}
    for path in (ROOT / PREFIX).iterdir():
        if path.is_file():
            raw[str(path.relative_to(ROOT))] = path.read_bytes()
    for path in (ROOT / NUMERIC).iterdir():
        if path.is_file():
            raw[str(path.relative_to(ROOT))] = path.read_bytes()
    for path in (ROOT / NUMERIC / 'base-helpers').iterdir():
        if path.is_file():
            raw[str(path.relative_to(ROOT))] = path.read_bytes()
    snapshots = reconstruct_sources(base, raw, borrowed)
    payload, reconstructed, aliases, omitted = {}, {}, {}, {}
    products = recorded_products()
    for path in sorted((ROOT / PREFIX).rglob('*')):
        if path.is_relative_to(HERE):
            continue
        relative = path.relative_to(ROOT / PREFIX)
        if len(relative.parts) > 1 and relative.parts[0] not in EVIDENCE_FOLDERS:
            # Other ongoing experiments, including rectangular-v1, have their
            # own source/audit lifecycle and are outside this frozen cohort.
            continue
        require(not path.is_symlink(), 'symlink in evidence tree')
        if not path.is_file():
            continue
        name = str(path.relative_to(ROOT))
        if '__pycache__' in path.parts or path.suffix in ['.pyc', '.pyo']:
            omitted[name] = dict(reason='generated Python bytecode', bytes=path.stat().st_size)
            continue
        if name in products:
            omitted[name] = dict(reason='compiled product; historical receipt digest only; not rehashed',
                                 sha256=products[name], bytes=path.stat().st_size)
            continue
        body = path.read_bytes()
        allowed(name, body)
        alias = source_alias(name, snapshots)
        if alias:
            require(body == snapshots[alias['snapshot']][alias['member']], 'working source alias mismatch: ' + name)
            aliases[name] = alias
        else:
            payload[name] = body
        reconstructed[name] = body
    require(set(products) == {name for name, item in omitted.items() if 'sha256' in item},
            'compiled omission inventory incomplete')
    release = document(raw[PREFIX + '/execution-release.json'])
    extras.extend([release['quiet_root_release']['path'], release['quiet_terminal_receipt']['path']])
    for name in sorted(set(extras)):
        safe(name)
        body = (ROOT / name).read_bytes()
        allowed(name, body)
        require(name not in payload or payload[name] == body, 'extra evidence alias differs')
        payload[name] = reconstructed[name] = body
    # Recheck source reconstruction from precisely the payload that will travel.
    require(reconstruct_sources(base, payload, borrowed) == snapshots, 'payload source closure incomplete')
    new_code = sum(len(body) for name, body in payload.items() if name.endswith(('.rs', '.py')))
    require(new_code < 1_000_000 and not any('/generated/' in name for name in payload),
            'compact capsule duplicated generated programs')
    destination.mkdir(parents=True)
    for name in CODE:
        body = (HERE / name).read_bytes()
        allowed(name, body)
        (destination / name).write_bytes(body)
    tar = io.BytesIO()
    with tarfile.open(fileobj=tar, mode='w', format=tarfile.PAX_FORMAT) as stream:
        for name, body in sorted(payload.items()):
            item = tarfile.TarInfo(name)
            item.size, item.mode, item.mtime = len(body), 0o644, 0
            stream.addfile(item, io.BytesIO(body))
    (destination / 'payload.tar.gz').write_bytes(gzip.compress(tar.getvalue(), compresslevel=9, mtime=0))
    for name, origin in [('qualification.json', NUMERIC + '/qualification-summary.json'),
                          ('synthetic-qualification.json', PREFIX + '/qualification-v3.json')]:
        (destination / name).write_bytes(payload[origin])
    if clear:
        (destination / 'audit-clear.json').write_bytes(args.audit_clear.resolve().read_bytes())
        audit = clear['independent_numeric_audit']
        (destination / 'independent-numeric-audit.json').write_bytes(payload[audit['path']])
    files = {str(path.relative_to(destination)): descriptor(path.read_bytes())
             for path in sorted(destination.rglob('*')) if path.is_file()}
    manifest = dict(schema_version=1,
        status='sealed_private_full_component_n6_saved_correctness' if clear else 'draft_pending_independent_numerical_audit_and_seal_release',
        files=files,
        borrowed_inputs={name: descriptor(body) for name, body in sorted(borrowed.items())},
        parent_capsule=dict(path=PARENT, manifest_sha256=digest(borrowed[PARENT + '/manifest.json']),
                            base_source_proposal_sha256='1c849a1bc59c4e935f4af4bf309987dd52c2fa0ddf0e4b2576d1a0e5e35ced77'),
        payload_archive=dict(path='payload.tar.gz', members={n: descriptor(b) for n, b in sorted(payload.items())}),
        source_aliases=aliases,
        reconstructed_private_files={n: descriptor(b) for n, b in sorted(reconstructed.items())},
        inherited_private_file_count=len(inherited), omitted_private_files=omitted,
        evidence_scope_folders=sorted(EVIDENCE_FOLDERS),
        unrelated_excluded_subtrees=[dict(path=PREFIX + '/' + path.name,
            reason='separate work outside the actual19-test and four-capture cohort; no inherited qualification')
            for path in sorted((ROOT / PREFIX).iterdir())
            if path.is_dir() and path.name not in EVIDENCE_FOLDERS and path != HERE],
        source_reconstruction='Committed parent88 + exact component-v1/v2/v3 patches ->89; prototypev3 core + retained base driver + exact capture-v1/v2 patches ->92; three committed fixtures ->92-file synthetic build overlay.',
        source_snapshots={name: {n: descriptor(b) for n, b in sorted(snapshot.items())}
                          for name, snapshot in snapshots.items()},
        counts=dict(base_files=88, prototype_files=89, numerical_capture_files=92, synthetic_build_files=92,
                    changed_prototype_files=5, selected_tests=19, parent_complex_slots=528,
                    actual_child_rows=156, paired_complex_slots=264, new_code_bytes=new_code),
        independent_numeric_audit=clear['independent_numeric_audit'] if clear else None,
        historical_native_guard_policy='Verify only reconstructed or committed bytes. Retain unbundled source/dependency/tool/binary digests as historical evidence, without reading or freshly rehashing the omitted native closure.',
        historical_process_group_policy='Check saved terminal/absence attestations and digest chains; never probe historical process identifiers.',
        public_dual_qualified=False, general_independent_higher_mixed_derivatives_qualified=False,
        finite_differences_qualified=False, rigorous_error_certificate=False,
        current_cargo_qualified=False, performance_qualified=False, production_adoption=False)
    write_json(destination / 'manifest.json', manifest)
    print(json.dumps(dict(destination=str(destination), status=manifest['status'], payload_members=len(payload),
                          source_aliases=len(aliases), omitted_instances=len(omitted),
                          payload_sha256=digest((destination / 'payload.tar.gz').read_bytes())), sort_keys=True))


if __name__ == '__main__':
    main()
