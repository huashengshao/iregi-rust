#!/usr/bin/env python3
"""Replay saved facade proof using only Python stdlib; starts no native jobs."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = 'target/shared-tensor-facade/'
ARTIFACT = 'fdaf41f9abcf04856aad2248274ae40afc315454118e83ff6cff84b9ee5256d6'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def describe(data):
    return {'sha256': sha(data), 'bytes': len(data)}


def load(data):
    return json.loads(data)


def safe(name):
    p = Path(name)
    require(name and not p.is_absolute() and '..' not in p.parts and str(p) == name, 'unsafe name')


def unpack(data):
    result = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        for member in archive:
            safe(member.name)
            require(member.isfile() and member.name not in result, 'archive type or duplicate')
            body = archive.extractfile(member).read()
            require(not body.startswith((b'\x7fELF', b'!<arch>'))
                    and Path(member.name).suffix not in ('.o', '.so', '.rlib', '.pyc', '.mod', '.smod')
                    and '__pycache__' not in Path(member.name).parts, 'native or cache payload')
            require(not re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}', body), 'license literal')
            result[member.name] = body
    return result


def restore_files(manifest):
    require({p.name for p in HERE.iterdir() if p.is_file()} == set(manifest['capsule_files']) | {'manifest.json'}, 'closed capsule')
    for name, record in manifest['capsule_files'].items():
        safe(name)
        require(describe((HERE/name).read_bytes()) == record, 'capsule '+name)
    parents = {}
    for name, record in manifest['parents'].items():
        safe(name)
        value = (ROOT/name).read_bytes()
        require(describe(value) == record, 'parent '+name)
        parents[name] = value
    source_inventory = load(parents[manifest['base_source_inventory']])
    sources = unpack(parents[manifest['base_source_archive']])
    require({n: describe(v) for n, v in sources.items()} == source_inventory['members']
            and len(sources) == source_inventory['source_count'] == 64, 'base 64-source identity')
    reset_manifest = load(parents[manifest['reset_manifest']])
    require(sha(parents[manifest['reset_archive']]) == reset_manifest['capsule_files']['evidence.tar.gz'], 'reset payload identity')
    reset = unpack(parents[manifest['reset_archive']])
    require({n: describe(v) for n, v in reset.items()} == reset_manifest['payload_members'], 'reset exact members')
    name = 'crates/iregi-rust/src/execution.rs'
    sources[name] = reset[name]
    payload = unpack((HERE/'evidence.tar.gz').read_bytes())
    require({n: describe(v) for n, v in payload.items()} == manifest['evidence_members'], 'exact evidence members')
    for name in manifest['source_overlays']:
        sources[name] = payload[name]
    inventory = load(payload[PRIVATE+'build-002/source-inventory.json'])
    require(len(sources) == len(inventory) == 65 and {n: sha(v) for n, v in sources.items()} == inventory, 'actual 65-source context')
    before = dict(sources)
    name = 'crates/iregi-rust/src/dispatch.rs'
    old = before[name].replace(b'float::{Float, SingleFloat}', b'float::{Float, FloatLike}', 1)
    require(old != before[name], 'one test import repair')
    before[name] = old
    require({n: sha(v) for n, v in before.items()} == load(payload[PRIVATE+'source-inventory.json']), 'initial failed-build context')
    return payload, sources, before


def replay(manifest, payload, sources, before):
    q = load((HERE/'qualification.json').read_bytes())
    require(q['status'] == 'passed_actual_Cargo_facade_build_and_delegation_tests'
            and q['actual_source_snapshot_files'] == 65 and q['actual_Cargo_test_artifact_sha256'] == ARTIFACT, 'qualification scope')
    require(not any(q[k] for k in ('current_main_after_separate_generalized_source_edits_qualified', 'native_build_input_closure_complete',
            'new_independent_integral_oracle', 'feature_union_qualified', 'higher_point_Dual_promotion', 'full_domain_qualified', 'performance_qualified')), 'no qualification promotion')
    require({n: sha(sources[n]) for n in q['implementation_sha256']} == q['implementation_sha256'], 'four implementation identities')
    review = load(payload['target/resume-20261025-review/tensor-facade-independent-source-review.json'])
    addendum = load(payload['target/resume-20261025-review/tensor-facade-test-import-source-addendum.json'])
    require(not review['findings'] and not addendum['findings'] and review['native_jobs_started'] == addendum['native_jobs_started'] == 0, 'source reviews')
    require({n: sha(before[n]) for n in review['source_sha256']} == review['source_sha256']
            and {n: sha(sources[n]) for n in review['context_sha256']} == review['context_sha256'], 'source review identity')
    require(addendum['parent_review_sha256'] == sha(payload['target/resume-20261025-review/tensor-facade-independent-source-review.json'])
            and addendum['dispatch_sha256'] == sha(sources['crates/iregi-rust/src/dispatch.rs']), 'import addendum identity')
    require(review['design_sha256'] == sha(payload['target/resume-20261025-review/shared-tensor-facade-source-design.json']), 'design identity')
    receipts = {}
    saved_bindings = 0
    for stage in ('build-001', 'build-002', 'normal-001', 'specialized-001'):
        prefix = PRIVATE+stage+'/'
        d = load(payload[prefix+'receipt.json'])
        receipts[stage] = d
        require(sha(payload[prefix+'receipt.json']) == q['receipt_sha256'][stage], 'qualified receipt identity')
        require(len(d['steps']) == 1 and not d['cleanup_errors'] and d['elapsed_seconds'] <= d['total_seconds']
                and not d['native_closure_complete_claim'] and d['no_automatic_retry'], 'finite stage')
        step = d['steps'][0]
        require(step['owned_group_gone'] and not step['group_existed_at_cleanup']
                and step['elapsed_seconds'] <= step['timeout_seconds'] == d['child_cap_seconds']
                and d['child_cap_seconds'] + d['cleanup_reserve_seconds'] <= d['total_seconds'], 'finite owned child')
        require(d['command'] == step['command'] and d['command'][1:3] == ['-c', '18,19' if d['stage'] == 'build' else '18'], 'CPU and command')
        env = d['runtime_environment']
        require(env['RAYON_NUM_THREADS'] == env['RUST_TEST_THREADS'] == '1' and env['license_configured'] is True, 'thread/license boolean')
        for name, digest in d['outputs'].items():
            if name == 'frozen-tests':
                require(manifest['omitted_native_products'][prefix+name] == digest == ARTIFACT, 'omitted immutable artifact attestation')
            else:
                require(sha(payload[prefix+name]) == digest, 'saved output '+prefix+name)
                saved_bindings += 1
        require(sha(payload[PRIVATE+('qualify-build-001.py' if stage == 'build-001' else 'qualify.py')]) == d['controller_sha256']
                and sha(payload[PRIVATE+'lifecycle.py']) == d['lifecycle_sha256'], 'historical controller identity')
        expected = 'failed' if stage == 'build-001' else 'passed'
        require(d['status'] == expected and step['returncode'] == (101 if expected == 'failed' else 0), 'retained stage outcome')
        if d['stage'] == 'build':
            require(d['command'][4:] == ['test', '--locked', '--offline', '-p', 'iregi-rust', '--lib', '--no-run', '--message-format=json', '-j2'], 'actual Cargo command')
        else:
            require(d['executed_binary_sha256'] == ARTIFACT and d['executed_binary_unchanged'], 'same owned artifact')
            require(d['command'][3] == manifest['historical_root']+'/'+prefix+'frozen-tests', 'owned executable path')
    build = receipts['build-002']
    event = build['cargo_test_artifact']
    require(build['source_inputs_unchanged'] and build['test_artifact_sha256'] == ARTIFACT
            and event['features'] == ['default'] and event['profile']['test'] and event['target']['name'] == 'iregi_rust', 'actual default-feature test artifact')
    events = []
    for line in payload[PRIVATE+'build-002/step-0.log'].decode().splitlines():
        try:
            obj = load(line)
        except json.JSONDecodeError:
            continue
        if obj.get('reason') == 'compiler-artifact' and obj.get('target', {}).get('name') == 'iregi_rust' and obj.get('profile', {}).get('test') and obj.get('executable'):
            events.append(obj)
    require(events == [event], 'Cargo event retained in raw log')
    failed = payload[PRIVATE+'build-001/step-0.log'].decode()
    require('E0599' in failed and 'SingleFloat' in failed and 'from_rational' in failed, 'compile failure retained')
    normal = payload[PRIVATE+'normal-001/step-0.log'].decode()
    require(set(re.findall(r'^test dispatch::tests::(\S+) \.\.\. ok$', normal, re.M)) == set(review['selected_normal_tests'])
            and 'test result: ok. 6 passed; 0 failed; 1 ignored;' in normal, 'six normal tests')
    name = review['ignored_specialized_test']
    require('test '+name+' ... ignored,' in normal, 'ordinary exclusion explicit')
    special = payload[PRIVATE+'specialized-001/step-0.log'].decode()
    require(re.search(r'^test '+re.escape(name)+r' \.\.\. ok$', special, re.M)
            and 'test result: ok. 1 passed; 0 failed; 0 ignored;' in special, 'separate meaningful delegation test')
    require(receipts['normal-001']['command'][4:] == ['dispatch::tests::', '--test-threads=1', '--nocapture']
            and receipts['specialized-001']['command'][4:] == [name, '--exact', '--ignored', '--test-threads=1', '--nocapture'], 'selected test invocations')
    return {'status': 'passed_saved_facade_proof', 'source_files': len(sources), 'normal_tests': 6, 'specialized_tests': 1,
            'failed_compile_attempts_preserved': 1, 'verified_saved_output_bindings': saved_bindings,
            'omitted_native_products': len(manifest['omitted_native_products']), 'native_jobs_started': 0,
            'source_context_scope': '65 relevant source files, not complete native/dependency closure',
            'later_joint_main_or_frontend_qualified': False, 'new_integral_oracle': False, 'performance_claim': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reconstruct', type=Path, help='write only reconstructed 65-file source context into a new directory')
    args = parser.parse_args()
    manifest = load((HERE/'manifest.json').read_bytes())
    payload, sources, before = restore_files(manifest)
    result = replay(manifest, payload, sources, before)
    if args.reconstruct:
        args.reconstruct.mkdir(parents=True, exist_ok=False)
        for name, body in sources.items():
            path = args.reconstruct/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        result['reconstructed_source_files'] = len(sources)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
