#!/usr/bin/env python3
"""Deterministic bytes-only packaging of the five explicitly admitted roots.

No native executable reads/hashes, numerical evaluations, producer imports,
process probes, live source reads or Git operations. Only _work is written.
"""
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile

WORK=Path('validation/certified-planar-generalized-scalar-qualification/_work')
ROOTS=[Path('target/certified-planar-generalized-scalar-numeric'),
       Path('target/certified-planar-generalized-scalar-oracle-refinement'),
       Path('validation/certified-planar-generalized-scalar'),
       Path('target/certified-planar-generalized-scalar-numeric-source-review'),
       Path('target/planar-scalar-independent-saved-review')]
NATIVE_NAMES={'owned-executable','frozen-example'}
FROZEN_ARTIFACT='18c7a844d2857131098fd8d482c737b5ca3291d7d4a5c6d4516967abd42824f4'
FINAL_QUALIFICATION='f73ad79d5e144e29b09ce4dffa413c9867fe7ac796373d9c3cb27935cf578d27'
LITERAL=re.compile(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z0-9]{25,}')

def check(value,message):
    if not value:raise ValueError(message)

def digest(raw):return hashlib.sha256(raw).hexdigest()

def load(path):return json.loads(path.read_bytes())

def main():
    output=WORK/'payload.tar.gz';origins_path=WORK/'origins.json'
    check(not output.exists() and not origins_path.exists(),'preserve existing packaging result')
    files=[];omitted=[];byroot={};captured_receipts={}
    for root in ROOTS:
        check(root.is_dir(),'missing admitted evidence root '+str(root))
        byroot[str(root)]={'retained_files':0,'retained_bytes':0,'omitted_native_aliases':0,'omitted_pycache':0}
        for path in sorted(root.rglob('*')):
            check(not path.is_symlink(),'no symlink may enter the evidence capsule '+str(path))
            if not path.is_file():continue
            if path.name in NATIVE_NAMES:
                # Read the small saved receipt, never the native alias bytes.
                receipt_path=path.parent/'receipt.json'
                receipt=load(receipt_path)
                if path.name=='frozen-example':
                    sha=receipt['artifact_sha256'];size=receipt['artifact_bytes']
                else:
                    sha=receipt['owned_executable_sha256'];size=receipt['owned_executable_bytes']
                    check(receipt['native_hardlink_shared_inode'] is True,'shared inode attestation missing')
                check(sha==FROZEN_ARTIFACT and size==558710824,'unexpected captured native attestation')
                check(path.stat().st_size==size,'native alias saved byte count drift (stat only)')
                omitted.append({'path':str(path),'reason':'compiled native alias omitted',
                    'sha256':sha,'bytes':size,'digest_basis':'saved immutable capture/build receipt; native bytes not opened or rehashed',
                    'receipt_path':str(receipt_path),'receipt_sha256':digest(receipt_path.read_bytes()),
                    'shared_inode_attested':path.name=='owned-executable'})
                byroot[str(root)]['omitted_native_aliases']+=1
                continue
            if '__pycache__' in path.parts or path.suffix=='.pyc':
                omitted.append({'path':str(path),'reason':'Python compiled cache omitted','bytes':path.stat().st_size,
                                'sha256':None,'digest_basis':'not hashed; non-evidence cache'})
                byroot[str(root)]['omitted_pycache']+=1;continue
            relative=PurePosixPath(path.as_posix())
            check(not relative.is_absolute() and '..' not in relative.parts,'unsafe archive alias')
            check(path.stat().st_size<40_000_000,'unexpected large file; closure expansion forbidden')
            raw=path.read_bytes()
            check(not raw.startswith(b'\x7fELF'),'unrecognized ELF artifact in admitted roots '+str(path))
            check(LITERAL.search(raw) is None,'literal Symbolica license found; do not archive '+str(path))
            entry={'alias':relative.as_posix(),'source_path':str(path.resolve()),'sha256':digest(raw),'bytes':len(raw)}
            files.append((entry,raw))
            byroot[str(root)]['retained_files']+=1;byroot[str(root)]['retained_bytes']+=len(raw)
    files.sort(key=lambda item:item[0]['alias'])
    check(len({entry['alias'] for entry,raw in files})==len(files),'duplicate archive alias')
    lookup={entry['alias']:(entry,raw) for entry,raw in files}
    final_path='target/certified-planar-generalized-scalar-oracle-refinement/qualification-after-independent.json'
    check(lookup[final_path][0]['sha256']==FINAL_QUALIFICATION,'final independent qualification must be present and pinned')
    snapshot_root='target/certified-planar-generalized-scalar-numeric/build-001/source-snapshot/'
    inventory_path='target/certified-planar-generalized-scalar-numeric/build-001/source-inventory.json'
    inventory=json.loads(lookup[inventory_path][1])
    check(len(inventory)==75,'exact captured source inventory count')
    restore=[]
    for path,sha in sorted(inventory.items()):
        entry,raw=lookup[snapshot_root+path]
        check(entry['sha256']==sha,'captured source inventory mismatch '+path)
        restore.append({'project_relative_source_path':path,'snapshot_alias':entry['alias'],
                        'sha256':sha,'bytes':len(raw),
                        'source_kind':'immutable captured build snapshot; no later live source attribution'})
    check(sum(entry['alias'].startswith(snapshot_root) for entry,raw in files)==75,'snapshot has unbound extra file')
    check(len(files)==254 and len(omitted)==31,'expected exact packaging input counts; inspect any later additions before freeze')
    # Pin all small raw output maps while keeping omitted native attestations
    # outside the portable replay. This is byte provenance, not numerical replay.
    output_bindings=[]
    for entry,raw in files:
        if not entry['alias'].endswith('/receipt.json'):continue
        document=json.loads(raw)
        if 'outputs' not in document:continue
        captured_receipts[entry['alias']]=entry['sha256']
        for alias,sha in document['outputs'].items():
            candidate=str(PurePosixPath(entry['alias']).parent/alias)
            if candidate in lookup:
                check(lookup[candidate][0]['sha256']==sha,'saved output hash drift '+candidate)
                output_bindings.append({'receipt_alias':entry['alias'],'output_alias':candidate,'sha256':sha})
            else:
                check(alias in NATIVE_NAMES,'missing retained small receipt output '+candidate)
    with output.open('xb') as file:
        with gzip.GzipFile(filename='',fileobj=file,mode='wb',mtime=0,compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed,mode='w',format=tarfile.PAX_FORMAT) as archive:
                for entry,raw in files:
                    info=tarfile.TarInfo(entry['alias']);info.size=len(raw);info.mode=0o644
                    info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
                    archive.addfile(info,io.BytesIO(raw))
    payload_sha=digest(output.read_bytes())
    # Independently reopen the completed archive and verify exact member bytes,
    # no links/special entries, and reproducible ownership/timestamp metadata.
    with tarfile.open(output,'r:gz') as archive:
        members=archive.getmembers();check([member.name for member in members]==[entry['alias'] for entry,raw in files],
                                         'archive exact sorted member inventory')
        for member in members:
            entry,raw=lookup[member.name]
            check(member.isfile() and member.uid==member.gid==member.mtime==0 and member.mode==0o644,
                  'archive deterministic regular-file metadata')
            extracted=archive.extractfile(member).read()
            check(digest(extracted)==entry['sha256'] and len(extracted)==entry['bytes'],'archive member roundtrip')
    origins={'schema_version':1,'status':'deterministic_saved_evidence_payload_prepared',
        'scope':'Exact five authorized evidence roots, original project-relative aliases, all failed/coarse/refined evidence retained; no external guard-closure expansion.',
        'payload':{'path':str(output),'sha256':payload_sha,'bytes':output.stat().st_size,
                   'member_count':len(files),'uncompressed_member_bytes':sum(entry['bytes'] for entry,raw in files),
                   'format':'gzip mtime0 filename-empty compression9; sorted POSIX pax tar regular files mode0644 uid/gid0 empty names mtime0'},
        'roots':byroot,'members':[entry for entry,raw in files],
        'captured_source_restore_map':restore,'captured_source_inventory_sha256':lookup[inventory_path][0]['sha256'],
        'receipt_small_output_bindings':output_bindings,'captured_receipt_pins':captured_receipts,
        'omitted':omitted,
        'historical_external_attestations':[
          'External compiler/Nix tools, upstream dependency/master paths and compiled source-cache closure are not imported into this capsule.',
          'The mpmath environment source inventory is retained as saved evidence; the installed external Python package bytes are not expanded.',
          'Original native hardlink aliases and the frozen example are omitted. Their digests come only from saved build/capture receipts.',
          'No later mutable main source is attributed to the captured artifact; all75 captured source copies restore separately from their original project-relative identities.'
        ],
        'literal_symbolica_license_included':False,'omitted_python_cache_count':sum('__pycache__' in item['path'] or item['path'].endswith('.pyc') for item in omitted),
        'initial_import_failures_preserved':3,'coarse_refinement_failures_and_both_independent_audits_preserved':True,
        'final_independent_qualification_sha256':FINAL_QUALIFICATION,
        'package_script_sha256':digest(Path(__file__).read_bytes()),
        'activity':{'native_bytes_opened_or_rehashed':False,'live_source_reads':False,'compiler_or_native_jobs':False,
                    'integral_or_symbolic_evaluation':False,'PID_operations':False,'Git_operations':False,'production_edits':False}}
    with origins_path.open('x') as stream:json.dump(origins,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'status':origins['status'],'payload':origins['payload'],
                      'origins_sha256':digest(origins_path.read_bytes()),'omitted_native_aliases':31,
                      'source_restore_files':len(restore),'small_output_bindings':len(output_bindings)},sort_keys=True))

if __name__=='__main__':main()
