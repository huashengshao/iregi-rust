#!/usr/bin/env python3
"""Seal saved bytes only AFTER the owner explicitly reports first-dot terminal.

Do not execute while that producer is active. The required receipt-hash argument
is supplied from the owner's terminal notice, never discovered by polling.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import re
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = 'validation/ordinary-complex-box-correlation'
PARENT_SHA = 'aec684253e59a73944b1e5a8e58c6b385bf9a81d5acf17f81643f6eec3aed2e0'
R = 'target/ordinary-gh-parent-requalification'
P = R+'/parent-proposal'
I = R+'/independent-parent-saved-review'
PREFIX = '/shared/external/iregi/iregi-rust/'


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {'sha256':sha(body),'bytes':len(body)}


def require(ok,why):
    if not ok:
        raise ValueError(why)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first-dot-owner-terminal-receipt-sha256',required=True)
    args = parser.parse_args()
    require(re.fullmatch('[0-9a-f]{64}',args.first_dot_owner_terminal_receipt_sha256),'explicit owner terminal receipt identity')
    require(not (HERE/'manifest.json').exists(),'capsule not previously sealed')
    # This is deliberately the first possible capture read. No active-first-dot
    # scan, status polling or array discovery occurs during source staging.
    terminal_alias = P+'/captures/first_dot-Float256-001/receipt.json'
    terminal_bytes = (ROOT/terminal_alias).read_bytes()
    require(sha(terminal_bytes)==args.first_dot_owner_terminal_receipt_sha256,'owner terminal receipt bytes')
    terminal = json.loads(terminal_bytes)
    require(terminal.get('finished_utc') and terminal.get('status') not in ('preflight','running'), 'actual owner terminal receipt')
    parent_raw = (ROOT/PARENT/'manifest.json').read_bytes()
    require(sha(parent_raw)==PARENT_SHA,'sealed scalar parent identity')
    spec = importlib.util.spec_from_file_location('ordinary_gh_scalar_saved_parent',ROOT/PARENT/'check.py')
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    inherited = parent.restore_files(parent.load(parent_raw))
    by_hash = {}
    for alias,body in sorted(inherited.items()):
        by_hash.setdefault(sha(body),alias)
    sources,origins = {},{}

    def add(alias,origin=None):
        origin = origin or alias
        body = (ROOT/origin).read_bytes()
        require(not body.startswith((b'\x7fELF',b'!<arch>\n')),'native product omitted')
        require(not re.search(rb'S-[0-9]{3}-[0-9]{4}[.][0-9]{2}[.][0-9]{2}-[A-Z2-7]{20,}',body),'no license literal')
        require(alias not in sources or sources[alias]==body,'unambiguous alias')
        sources[alias],origins[alias] = body,origin

    # All these trees are immutable prerequisites or terminal saved captures.
    # No executable, .partial file or cache is copied.
    for item in (ROOT/P).rglob('*'):
        if item.is_file() and '__pycache__' not in item.parts and item.suffix in ('.py','.json','.jsonl','.log','.stdout','.md'):
            add(str(item.relative_to(ROOT)))
    qualified,receipt_context,omitted = {},{},dict(json.loads(parent_raw)['omitted_native_artifacts'])
    for case in ('D2','first_dot'):
        directory = P+'/captures/'+case+'-Float256-001'
        receipt = json.loads(sources[directory+'/receipt.json'])
        require(receipt.get('finished_utc') and receipt['case']==case,'two completed owner receipts')
        qualified[case] = receipt['status']=='passed_current256_quad_and_CROSS_SOURCE_840_pairs'
        review_alias = I+'/'+case+'-review.json'
        if (ROOT/review_alias).exists():
            add(review_alias)
        require(not qualified[case] or review_alias in sources,'successful case requires actual independent saved review')
        omitted[PREFIX+directory+'/cli-owned'] = '7005b0966709525945f7e1b330b4a3b23b6b63ccfb1faf3566f893dfe8ac5890'
    add(I+'/check.py')
    add(I+'/README.md')
    for name in ('receipt.json','check.py','package.py','manifest.json'):
        add(R+'/capsule-packaging-attempt-001/'+name)
    for name in ('receipt.json','check.py','package.py','manifest.json','qualify-parent-capsule.py','minimal.stderr'):
        add(R+'/capsule-packaging-attempt-002/'+name)
    add('target/n6-rank6-generalized-quad/requests/n6_rank6_unit_D2.txt')
    old_D2 = 'target/affine-power-post-memo-current-d2-pair'
    for name in ('endpoint-source-map.json','independent_failure_audit.py','independent-saved-failure-audit.json',
                 'captures/Float256-001/receipt.json','captures/Float256-001/stdout.json'):
        add(old_D2+'/'+name)
    # Copy the actual fresh128source snapshot once. The parent already owns
    # relevant scalar bodies; other bodies are added as unique own objects.
    build_alias = R+'/build-001/receipt.json'
    built = json.loads(inherited[build_alias])
    require(len(built['source_files'])==128 and sha(inherited[build_alias])=='faa4ea0e4ea4029a8e61dbdbb02c5324f985793008e4cdc3aec1d8341fa64845',
            'exact actual fresh build context')
    fresh = {}
    for relative,digest in built['source_files'].items():
        alias = R+'/build-001/source-snapshot/'+relative
        add(alias)
        require(sha(sources[alias])==digest,'immutable actual Cargo source copy')
        fresh[relative] = alias
    # Preserve canonical earlier aliases from already-frozen small copies,
    # rather than walking their historical directory/dependency trees.
    for row in json.loads(sources[P+'/copy-provenance.json'])['copies']:
        require(sha(sources[row['copy']])==row['sha256'],'exact frozen small prior/reference copy')
        add(row['source'],row['copy'])
    require(all(inherited[alias]==body for alias,body in sources.items() if alias in inherited),
            'no inherited canonical alias may change bytes')
    all_available = {**inherited,**sources}
    for case in ('D2','first_dot'):
        receipt = json.loads(sources[P+'/captures/'+case+'-Float256-001/receipt.json'])
        receipt_context[case] = {absolute:absolute.removeprefix(PREFIX) for absolute,digest in receipt['inputs'].items()
            if absolute.startswith(PREFIX) and absolute.removeprefix(PREFIX) in all_available
            and sha(all_available[absolute.removeprefix(PREFIX)])==digest}
    objects,aliases = {},{}
    for alias,body in sorted(sources.items()):
        digest = sha(body)
        if digest in by_hash:
            aliases[alias] = {'parent_alias':by_hash[digest],**desc(body)}
        else:
            objects[digest] = body
            aliases[alias] = {'member':'objects/'+digest,**desc(body)}
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed,mode='wb',mtime=0) as stream:
        with tarfile.open(fileobj=stream,mode='w') as archive:
            for digest,body in sorted(objects.items()):
                info = tarfile.TarInfo('objects/'+digest)
                info.size,info.mode = len(body),0o644
                archive.addfile(info,io.BytesIO(body))
    (HERE/'payload.tar.gz').write_bytes(compressed.getvalue())
    parent_files = {PARENT+'/'+name:desc((ROOT/PARENT/name).read_bytes())
                    for name in sorted(set(json.loads(parent_raw)['capsule_files'])|{'manifest.json'})}
    manifest = {'schema_version':1,'capsule_directory':str(HERE.relative_to(ROOT)),
        'status':'sealed_two_terminal_outcomes_saved_only','parent_manifest_sha256':PARENT_SHA,'parent_files':parent_files,
        'capsule_files':{name:desc((HERE/name).read_bytes()) for name in ('README.md','check.py','package.py','payload.tar.gz')},
        'payload_members':{'objects/'+digest:desc(body) for digest,body in sorted(objects.items())},
        'aliases':aliases,'copy_origins':dict(sorted(origins.items())),
        'fresh_source_aliases':fresh,'selected_input_bindings':receipt_context,
        'first_dot_owner_terminal_notice_sha256':args.first_dot_owner_terminal_receipt_sha256,
        'case_qualified':qualified,'omitted_native_artifacts':omitted,
        'prior_full_context_reference':{'path':'validation/checked-g-generalized-core-tests/manifest.json',
            'sha256':'ee4bc172dd8b87e3242158afacab425e6b13376f72dd3fbb6678feb701a97417',
            'referenced_historical_identity_only_not_recursively_restored':True},
        'prior_failed_Float256_reference':{'capsule':'validation/affine-power-generalized-memo-dot-rank6/manifest.json',
            'manifest_sha256':'82e48ff83b92ec0f2193e5125d9b37e95f97adabfeb1db6607e205ff21c15a68',
            'failed_receipt_sha256':'3671d809732aef26c205b9ea71df1861e62249d34a7915f816c124180cd67584',
            'scope':'historical failed E6NonConvergent context remains preserved in prior capsule; no source retry or replacement'},
        'prior_failed_D2_Float256_evidence':{'receipt':old_D2+'/captures/Float256-001/receipt.json',
            'receipt_sha256':'f4e9f3fd7ac1f7fa6fd675c2d0a10d69ebda8d9d70c21e5be0659463a6e817f0',
            'stdout_sha256':'2a7c9154293f445c09ca96fcf5a2c4b8c123047888ffba62b76440ed27e63040',
            'qualified':False,'scope':'five actual historical records, no parent arrays; ancillary profile/resource hashes remain receipt metadata'},
        'same_source_precision_convergence_qualified':False,'full_domain_qualified':False,
        'D6_qualified':False,'performance_qualified':False,'native_backend_qualified':False,
        'raw_producer_bytes_modified':False,'native_or_compiler_execution_by_packager':False}
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest_sha256':sha((HERE/'manifest.json').read_bytes()),'own_payload_bytes':len(compressed.getvalue()),
                      'own_unique_bodies':len(objects),'aliases':len(aliases),'inherited_aliases':sum('parent_alias' in r for r in aliases.values()),
                      'case_qualified':qualified}))


if __name__=='__main__':
    main()
