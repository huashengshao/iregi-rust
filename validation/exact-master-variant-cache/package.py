#!/usr/bin/env python3
"""Freeze already terminal saved evidence. No compiler or numerical execution."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import re
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = 'target/exact-master-variant-cache-proposal'
FAILED = 'target/public-highpoint/numeric-types-dual-shared-cache'
TYPED = FAILED + '-link-closure'
OLD = 'target/public-highpoint/numeric-types-dual'
COMPOSITION = 'validation/winddown/native-f64-sixpoint-composition.tar.gz'
OLD_CAPSULE = 'validation/highpoint-six-point-numeric-types'
AUDITS = ['target/resume-20261025-review/typed-cache-link-independent-saved-audit.py',
          'target/resume-20261025-review/typed-cache-link-independent-saved-audit.json',
          'target/resume-20261025-review/typed-cache-link-independent-metadata-supplement.json']
EXPECTED = {
 CACHE+'/source-proposal.json':'1c849a1bc59c4e935f4af4bf309987dd52c2fa0ddf0e4b2576d1a0e5e35ced77',
 CACHE+'/proposal.patch':'74f84db6d50e4b1987fd865458cce6f3d806151f64140d7acc005ef00b1f07f2',
 CACHE+'/qualification.json':'3514c228f18326dc5d86ac4ae233623b120520d36daf8b07929586b276944d50',
 TYPED+'/qualification.json':'97c4780204bbf81f12a21cc00e8a02c6575a65a14962428df88849a9133859db',
 AUDITS[0]:'16e50b804710dfd50de070fdaef7cee13721504673c543bf5b31212a9a4a0f90',
 AUDITS[1]:'332772366147121e12766144f3b8ae29e18b14d174112f09637768451d4f4919',
 AUDITS[2]:'3febc1494e665706b5bd25da86168298a675aadd90bdf457a5702f379d9afaff',
}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def descriptor(data):
    return {'sha256':sha(data), 'bytes':len(data)}


def load(path):
    return json.loads(Path(path).read_text())


def allowed(name, body):
    require(not body.startswith((b'\x7fELF', b'!<arch>')), 'compiled payload: '+name)
    require(not re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}', body), 'license literal in '+name)


def archive(body):
    result = {}
    with tarfile.open(fileobj=io.BytesIO(body), mode='r:gz') as stream:
        for item in stream:
            p = Path(item.name)
            require(item.isfile() and item.name not in result and not p.is_absolute()
                    and '..' not in p.parts and str(p) == item.name, 'unsafe archive')
            result[item.name] = stream.extractfile(item).read()
    return result


def main():
    require(Path.cwd().resolve() == ROOT, 'run from project root')
    require(not (HERE/'manifest.json').exists(), 'sealed capsule is immutable')
    for name, expected in EXPECTED.items():
        require(sha((ROOT/name).read_bytes()) == expected, 'anchor changed: '+name)
    parent_bytes = (ROOT/COMPOSITION).read_bytes()
    require(sha(parent_bytes) == '25bdb8eaef1ca55875e8ab73b0b59b6c8a6e85c90c2fe166317fef01881a7329', 'composition parent changed')
    parent = archive(parent_bytes)
    source = load(ROOT/CACHE/'source-proposal.json')
    borrowed = [COMPOSITION, 'validation/winddown/manifest.json',
                'validation/winddown/n6-numeric-types-dual.tar.gz',
                OLD_CAPSULE+'/manifest.json', OLD_CAPSULE+'/payload.tar.gz',
                'validation/public-highpoint/fixture-conditioned_masses.json',
                'validation/public-highpoint/reference-conditioned_masses.json',
                'validation/highpoint-six-point-api/qualified-v2/public-rank3-256-001/result.json',
                'validation/reference/fixtures.json',
                'validation/pv-high-rank/lightlike-feynman-parameters.json',
                'validation/reference/snapping/reductions.json']
    for name in ['independent-numeric-audit.json','independent-provenance-audit.json','qualification.json']:
        borrowed.append(OLD_CAPSULE+'/'+name)
    # Check parent membership before omitting duplicated source snapshots.
    base = {name:parent['proposed/'+name] for name in source['base_files']}
    require({n:descriptor(b) for n,b in base.items()} == source['base_files'], 'base85 parent mismatch')
    reconstructed, payload, omitted, source_aliases = {}, {}, {}, {}
    excluded_trees = ('base/', 'proposed/', 'build-source/', 'mechanical-reconstruction/', 'core/')
    for prefix in [CACHE, FAILED, TYPED]:
        for path in sorted((ROOT/prefix).rglob('*')):
            require(not path.is_symlink(), 'symlink in evidence tree')
            if not path.is_file():
                continue
            name = str(path.relative_to(ROOT)); local = str(path.relative_to(ROOT/prefix))
            if '__pycache__' in path.parts or path.suffix in ['.pyc','.pyo']:
                omitted[name] = {'reason':'generated Python bytecode', 'bytes':path.stat().st_size}
                continue
            with path.open('rb') as stream:
                start = stream.read(8)
            if start.startswith((b'\x7fELF',b'!<arch>')):
                # Read only a small number of known outputs; never copy them.
                with path.open('rb') as stream:
                    digest = hashlib.file_digest(stream,'sha256').hexdigest()
                omitted[name] = {'reason':'compiled product; digest is historical evidence only',
                                 'sha256':digest,'bytes':path.stat().st_size}
                continue
            body = path.read_bytes(); allowed(name,body); reconstructed[name] = body
            if local.startswith(excluded_trees):
                continue
            payload[name] = body
    for name in source['changed_files']:
        key = CACHE+'/proposed/'+name
        payload[key] = reconstructed[key]
    typed_lib = FAILED+'/core/crates/iregi-rust/src/lib.rs'
    payload[typed_lib] = reconstructed[typed_lib]
    for name in AUDITS:
        body = (ROOT/name).read_bytes(); allowed(name,body)
        payload[name] = body; reconstructed[name] = body
    candidate = dict(base)
    for name in source['changed_files']:
        candidate[name] = reconstructed[CACHE+'/proposed/'+name]
    require({n:descriptor(b) for n,b in candidate.items()} == source['proposed_files'], 'candidate88 mismatch')
    # Every excluded duplicate must have an explicit exact reconstruction rule.
    for name, body in reconstructed.items():
        if name in payload:
            continue
        if name.startswith(CACHE+'/base/'):
            member = 'proposed/'+name[len(CACHE+'/base/'):]
            require(body == parent[member], 'base alias mismatch')
            source_aliases[name] = {'kind':'composition','member':member}
        elif any(name.startswith(CACHE+'/'+folder+'/') for folder in ['proposed','mechanical-reconstruction','build-source']):
            folder, member = name[len(CACHE)+1:].split('/',1)
            if member in candidate:
                require(body == candidate[member], 'candidate alias mismatch')
                source_aliases[name] = {'kind':'candidate','member':member}
            else:
                require(folder == 'build-source' and member in borrowed and body == (ROOT/member).read_bytes(), 'compile fixture mismatch')
                source_aliases[name] = {'kind':'repository','member':member}
        elif name.startswith(FAILED+'/core/'):
            member = name[len(FAILED+'/core/'):]
            if member in ['crates/iregi-rust/src/highpoint_numeric_probe.rs','crates/iregi-rust/src/jet_inputs.rs']:
                helper = 'source/capture.rs' if member.endswith('highpoint_numeric_probe.rs') else 'source/jet_inputs.rs'
                require(body == reconstructed[FAILED+'/'+helper], 'typed helper mismatch')
                source_aliases[name] = {'kind':'payload','member':FAILED+'/'+helper}
            else:
                require(body == candidate[member], 'typed core alias mismatch')
                source_aliases[name] = {'kind':'candidate','member':member}
        else:
            raise ValueError('unmapped omission '+name)
    require(sum(name.endswith('.pyc') for name in omitted) == 8, 'bytecode omission inventory changed')
    require(sum('sha256' in v for v in omitted.values()) == 9, 'compiled omission inventory changed')
    # Small overlays contain only 386KB Rust implementation changes plus runners.
    new_code_bytes = sum(len(body) for name,body in payload.items() if name.endswith(('.rs','.py')))
    require(new_code_bytes < 1_000_000, 'new code exceeds compact scope')
    tar = io.BytesIO()
    with tarfile.open(fileobj=tar,mode='w',format=tarfile.PAX_FORMAT) as stream:
        for name,body in sorted(payload.items()):
            item = tarfile.TarInfo(name); item.size=len(body);item.mode=0o644;item.mtime=0
            stream.addfile(item,io.BytesIO(body))
    (HERE/'payload.tar.gz').write_bytes(gzip.compress(tar.getvalue(),compresslevel=9,mtime=0))
    for name, origin in [('qualification.json',TYPED+'/qualification.json'),
                         ('cache-test-qualification.json',CACHE+'/qualification.json'),
                         ('independent-saved-audit.json',AUDITS[1]),
                         ('independent-metadata-supplement.json',AUDITS[2])]:
        (HERE/name).write_bytes(reconstructed[origin])
    files = {str(p.relative_to(HERE)):descriptor(p.read_bytes()) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.pyo']}
    for name in files:allowed(name,(HERE/name).read_bytes())
    manifest = dict(schema_version=1,
        status='sealed_private_exact_master_cache_18_test_gate_and_failed_partial_typed_pilot',
        files=files, borrowed_inputs={n:descriptor((ROOT/n).read_bytes()) for n in borrowed},
        payload_archive={'path':'payload.tar.gz','members':{n:descriptor(b) for n,b in sorted(payload.items())}},
        composition_parent={'path':COMPOSITION,'sha256':sha(parent_bytes),'prefix':'proposed/'},
        source_aliases=source_aliases,
        reconstructed_private_files={n:descriptor(b) for n,b in sorted(reconstructed.items())},
        omitted_private_files=omitted,
        counts=dict(base_files=85,candidate_files=88,typed_capture_files=90,build_source_files=91,
                    changed_or_new_implementation_files=8,unchanged_master_files=30,selected_tests=18,
                    available_output_slots=88,represented_input_slots=1736,old_exact_controls=64,
                    available_partial_pairs=24,required_full_pairs=240,new_code_bytes=new_code_bytes),
        historical_native_guard_policy='Keep original guarded native/dependency digests in raw protocols and audit receipts. Portable checking validates only reproduced or committed bytes; omitted binaries, /nix/store and unbundled native dependencies are not rehashed or requalified.',
        historical_process_group_policy='Saved terminal/absence attestations are checked. Historical process identifiers are never probed during portable checking.',
        original_typed_capsule=OLD_CAPSULE+'/manifest.json',
        source_reconstruction='Composition parent85 + eight-file overlay gives candidate88; three committed compile fixtures give build91; capture+jet helpers and one lib.rs declaration give typed90.',
        no_compiler_integral_reference_profile_or_benchmark_executed_by_packaging=True,
        compiled_outputs_or_license_literals_in_payload=False,
        fresh_native_build_or_numerical_requalification=False,
        full_cargo_suite_qualified=False,public_dual_qualified=False,
        derivative_uncertainty_transport_qualified=False,performance_qualified=False,
        commands=['python3 validation/exact-master-variant-cache/check.py',
                  'python3 validation/exact-master-variant-cache/check.py --reconstruct target/exact-master-cache-restored'])
    with (HERE/'manifest.json').open('x') as stream:json.dump(manifest,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps(dict(status='sealed',manifest_sha256=sha((HERE/'manifest.json').read_bytes()),
        payload_members=len(payload),reconstructed_files=len(reconstructed),omitted_files=len(omitted),
        archive_bytes=(HERE/'payload.tar.gz').stat().st_size,new_code_bytes=new_code_bytes)))


if __name__ == '__main__':main()
