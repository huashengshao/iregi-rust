#!/usr/bin/env python3
"""Package finite saved affine-power evidence; never runs native programs."""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = 'target/affine-power-reduction-proposal'
PARENT = 'validation/quad-original-iregi-generalized-n6-rank6'
PARENT_HASH = '90e4ede40dbf46e537064dea0e85309b0079bfd12d245f7dc9ba658aa16d2f0e'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return dict(sha256=sha(body), bytes=len(body))


def read(path):
    return json.loads(path.read_bytes())


def archive(bodies):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w') as tar:
        for name, body in sorted(bodies.items()):
            require(not body.startswith(b'\x7fELF') and b'S-130-' not in body, 'no native ELF or license literal')
            item = tarfile.TarInfo(name)
            item.size, item.mode, item.mtime = len(body), 0o644, 0
            tar.addfile(item, io.BytesIO(body))
    return gzip.compress(raw.getvalue(), mtime=0)


def prepare_sources():
    receipt = read(ROOT / PRIVATE / 'build-002/receipt.json')
    require(sha((ROOT / PRIVATE / 'build-002/receipt.json').read_bytes()) == '16957f0e22f69d218ab02676ca5ac129f9448a2faeda1b511b85f32649c7518e', 'fixed actual build')
    require(receipt['status'] == 'passed' and len(receipt['source_files']) == 145, 'actual145 sources')
    bodies = {}
    for name, digest in receipt['source_files'].items():
        body = (ROOT / PRIVATE / 'build-002/source-snapshot' / name).read_bytes()
        require(sha(body) == digest, 'immutable source copy ' + name)
        bodies[name] = body
    encoded = archive(bodies)
    dest = HERE / 'sources.tar.gz'
    if dest.exists():
        require(dest.read_bytes() == encoded, 'preserve prior prepared source archive')
    else:
        dest.write_bytes(encoded)
    return bodies


def seal():
    require(not (HERE / 'manifest.json').exists(), 'never rewrite a sealed capsule')
    # The owner explicitly notifies terminal success before invoking --seal.
    unit256 = read(ROOT / PRIVATE / 'numeric/captures/unit-256-001/receipt.json')
    pair = read(ROOT / PRIVATE / 'numeric/pair-unit.json')
    require(unit256['status'] == 'passed_complete_capture_and_840_quad_slots' and unit256['working_bits'] == 256, 'positive terminal UNIT256 required')
    require(pair['status'] == 'passed_complete_840_precision_pairs' and pair['pair_gates'] == 840 and not pair['failures'], 'positive saved complete UNIT precision pair required')
    sources = prepare_sources()
    parent_path = ROOT / PARENT
    parent_manifest = read(parent_path / 'manifest.json')
    require(sha((parent_path / 'manifest.json').read_bytes()) == PARENT_HASH, 'fixed admitted quad parent')
    spec = importlib.util.spec_from_file_location('affine_capsule_quad_parent_packaging', parent_path / 'check.py')
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    inherited = parent.restore_files(parent_manifest)
    objects, aliases, origins = {}, {}, {}
    known = {sha(body): dict(inherited_source=name) for name, body in inherited.items()}
    for name, body in sources.items():
        known[sha(body)] = dict(source_member=name)

    def add(path):
        alias = str(path.relative_to(ROOT))
        body = path.read_bytes()
        require(not body.startswith(b'\x7fELF') and b'S-130-' not in body, 'omit ELF/license from saved evidence')
        digest = sha(body)
        if digest not in known:
            member = 'objects/' + digest
            objects[member] = body
            known[digest] = dict(member=member)
        row = {**known[digest], **desc(body)}
        require(alias not in aliases or aliases[alias] == row, 'one immutable origin per alias')
        aliases[alias], origins[alias] = row, dict(origin=alias, **desc(body))

    for build_id in ['build-001', 'build-002']:
        directory = ROOT / PRIVATE / build_id
        for path in sorted(directory.rglob('*')):
            if path.is_file() and not path.name.startswith('frozen-'):
                add(path)
    for directory in ['tests-001', 'tests-002', 'guard-001']:
        for path in sorted((ROOT / PRIVATE / directory).rglob('*')):
            if path.is_file():
                add(path)
    selected = [
        'build.py', 'build-v2.py', 'tests.py', 'tests_v2.py', 'guard.py',
        'focused-test-inventory.json', 'build-test-api-correction.json', 'test-inventory-correction.json',
        'independent-build-audit.py', 'independent-build-review.json',
        'independent-focused-tests-audit.py', 'independent-focused-tests-review.json',
        'wrapper-source-review.json', 'wrapper-source-review.md', 'wrapper-source-review-addendum.json',
        'dag-independent-review.json', 'packing-independent-review.json', 'executor-test-review.md',
        'application-plan.json', 'algebra-reuse-checks.md',
        'numeric/cases.json', 'numeric/run.py', 'numeric/run_d6.py', 'numeric/capture_worker.py',
        'numeric/compare_saved.py', 'numeric/compare_pair.py', 'numeric/compare_pair-initial-draft.py',
        'numeric/pair-helper-correction.json', 'numeric/d6-prerequisite-amendment.json',
        'numeric/independent-unit128-audit.py', 'numeric/independent-unit128-review.json',
        'numeric/pair-unit.json',
    ]
    for name in selected:
        add(ROOT / PRIVATE / name)
    # Include any additional explicitly named independent UNIT256/pair review,
    # never arbitrary active capture directories or current live source trees.
    for path in sorted((ROOT / PRIVATE / 'numeric').glob('independent-unit256*')):
        if path.is_file():
            add(path)
    for path in sorted((ROOT / PRIVATE / 'numeric').glob('independent-unit-pair*')):
        if path.is_file():
            add(path)
    for path in sorted((ROOT / PRIVATE / 'numeric/inputs').glob('*.json')):
        add(path)
    for name in ['unit-128-001', 'unit-256-001', 'dot-128-001', 'd6-128-001']:
        for path in sorted((ROOT / PRIVATE / 'numeric/captures' / name).rglob('*')):
            if path.is_file() and path.name != 'cli-owned':
                add(path)
    lifecycle = ROOT / 'target/ibp-workspace-preparation-research/profile-n2-rank7-128/lifecycle-profile.py'
    add(lifecycle)
    omitted = {}
    for build_id in ['build-001', 'build-002']:
        receipt = read(ROOT / PRIVATE / build_id / 'receipt.json')
        for kind, product in receipt.get('products', {}).items():
            if 'path' in product:
                omitted[product['path']] = product['sha256']
    for name in ['unit-128-001', 'unit-256-001', 'dot-128-001', 'd6-128-001']:
        omitted[str(ROOT / PRIVATE / 'numeric/captures' / name / 'cli-owned')] = 'f69615f94311c2631dd5b6143df8812cdaa68f056bb865a9e50f566ea54e78bb'
    parent_files = dict(parent_manifest['parent_files'])
    for path in sorted(parent_path.iterdir()):
        if path.is_file():
            parent_files[str(path.relative_to(ROOT))] = desc(path.read_bytes())
    (HERE / 'payload.tar.gz').write_bytes(archive(objects))
    (HERE / 'payload-origins.json').write_text(json.dumps(origins, indent=2) + '\n')
    manifest = {
        'schema_version': 1,
        'status': 'scoped_saved_actual_affine_power_core_with_incomplete_generalized_cases',
        'capsule_directory': str(HERE.relative_to(ROOT)),
        'parent_manifest_sha256': PARENT_HASH,
        'parent_files': parent_files,
        'source_members': {name: desc(body) for name, body in sources.items()},
        'payload_members': {name: desc(body) for name, body in objects.items()},
        'aliases': aliases,
        'omitted_native_inputs': omitted,
        'build002_receipt_sha256': '16957f0e22f69d218ab02676ca5ac129f9448a2faeda1b511b85f32649c7518e',
        'unit128_receipt_sha256': '7aa3964b4e0693258486460b942c4fab6c5aad9f5d4c702791fc764450185dab',
        'unit256_receipt_sha256': sha((ROOT / PRIVATE / 'numeric/captures/unit-256-001/receipt.json').read_bytes()),
        'unit_pair_sha256': sha((ROOT / PRIVATE / 'numeric/pair-unit.json').read_bytes()),
        'requested_capture_status': {'unit128': 'passed_all840', 'unit256': 'passed_all840', 'dot128': 'timeout_no_array', 'd6_128': 'timeout_no_array', 'dot256': 'unrun', 'd6_256': 'unrun'},
        'full_requested_generalized_corpus_qualified': False,
        'Dual_physical_or_performance_qualified': False,
    }
    manifest['capsule_files'] = {p.name: desc(p.read_bytes()) for p in sorted(HERE.iterdir()) if p.is_file() and p.name != 'manifest.json'}
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'manifest_sha256': sha((HERE / 'manifest.json').read_bytes()), 'source_files': len(sources), 'aliases': len(aliases), 'source_archive_bytes': (HERE / 'sources.tar.gz').stat().st_size, 'payload_archive_bytes': (HERE / 'payload.tar.gz').stat().st_size, 'omitted_native_inputs': len(omitted)}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--seal', action='store_true')
    args = p.parse_args()
    require(Path.cwd().resolve() == ROOT, 'project cwd')
    if args.seal:
        seal()
    else:
        bodies = prepare_sources()
        print(json.dumps({'status': 'unsealed_source_archive_prepared', 'source_files': len(bodies), 'sources_sha256': sha((HERE / 'sources.tar.gz').read_bytes())}))
