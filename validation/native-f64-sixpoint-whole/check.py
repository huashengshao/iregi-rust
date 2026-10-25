#!/usr/bin/env python3
"""Verify compact capsule/parent reconstruction; no producer imports or kernels."""
from pathlib import Path
import argparse,hashlib,json,tarfile

def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def blobsha(data):return hashlib.sha256(data).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--origins',action='store_true');args=parser.parse_args()
    capsule=Path(__file__).resolve().parent;root=capsule.parents[1]
    manifest=json.loads((capsule/'manifest.json').read_text());parent=json.loads((capsule/'parent.json').read_text())
    expected_top=set(manifest['metadata_files'])|{'manifest.json',manifest['archive']['path']}
    assert {path.name for path in capsule.iterdir()if path.is_file()}==expected_top,'top-level capsule membership differs'
    for relative,item in manifest['metadata_files'].items():
        path=capsule/relative;assert path.stat().st_size==item['bytes']and sha(path)==item['sha256'],relative
    arc=manifest['archive'];assert sha(capsule/arc['path'])==arc['sha256']
    assert (capsule/arc['path']).stat().st_size==arc['bytes']
    payload={}
    with tarfile.open(capsule/arc['path'],'r:gz')as archive:
        members=archive.getmembers();assert len(members)==len(arc['members'])
        assert {item.name for item in members}==set(arc['members'])
        for member in members:
            assert member.isfile()and not Path(member.name).is_absolute()and '..'not in Path(member.name).parts
            data=archive.extractfile(member).read();item=arc['members'][member.name]
            assert member.size==item['bytes']==len(data)and blobsha(data)==item['sha256'],member.name
            assert not data.startswith((b'\x7fELF',b'!<arch>\n')),member.name
            if args.origins:assert sha(root/item['origin'])==item['sha256'],item['origin']
            payload[member.name]=data
    assert sha(root/parent['path'])==parent['sha256']
    inherited={}
    with tarfile.open(root/parent['path'],'r:gz')as archive:
        for relative,item in parent['inherited_source_files'].items():
            data=archive.extractfile(item['parent_member']).read()
            assert len(data)==item['bytes']and blobsha(data)==item['sha256'],relative
            inherited[relative]=data
    prep=json.loads(payload['preparation.json']);reconstructed=0
    for variant,mapping in prep['overlay_source_mapping'].items():
        for relative,expected in mapping.items():
            key=f'source/{variant}/{relative}';data=payload[key]if key in payload else inherited[key]
            assert blobsha(data)==expected,key
            reconstructed+=1
    q=json.loads((capsule/'qualification.json').read_text());build=json.loads(payload['observation-build-001/build.json'])
    record=json.loads(payload['whole-qualification-001/results.json']);gate=json.loads(payload['whole-qualification-001/independent-admission.json'])
    assert q['status']=='private-actual-base-combined-candidate-whole38-qualified'
    assert build['status']=='passed'and record['status']=='passed-awaiting-independent-raw-validation'and gate['status']=='passed'
    assert len(build['steps'])==4 and len(build['input_sha256'])==776 and len(record['input_sha256'])==782
    assert all(item['status']=='passed'and item['returncode']==0 and item['owned_group_gone']for item in build['steps'])
    assert build['elapsed_seconds']<180 and record['elapsed_seconds']<120
    assert build['inputs_unchanged']and record['inputs_unchanged']and not build['cleanup_errors']and not record['cleanup_errors']
    assert not build['deadline_exceeded']and not record['deadline_exceeded']
    assert record['request_count']==gate['requests']==gate['responses']==38 and len(gate['whole_cases'])==8
    raw=payload['whole-qualification-001/responses.jsonl'];assert blobsha(raw)==record['raw_sha256']==gate['raw_sha256']
    events=[json.loads(line)for line in raw.splitlines()];assert len(events)==76
    for label,expected in [('TIRust',30),('IREGI',8)]:
        emitted=[json.loads(line[7:])for line in payload[f'whole-qualification-001/{label}.stdout.log'].splitlines()if line.startswith(b'RESULT ')]
        recorded=[item['response']for item in events if item['event']=='response'and item['engine']==label]
        assert len(emitted)==len(recorded)==expected and emitted==recorded
    assert len(record['process_terminals'])==2 and all(item['returncode']==0 and item['owned_group_gone']for item in record['process_terminals'])
    assert gate['controls']['actual_base_unchanged_master_cases']==21 and gate['controls']['actual_base_extended_master_cases']==12
    assert all(q['not_qualified_by_this_capsule'].values())and not q['production_mutations']and not q['benchmark_execution']
    assert manifest['content_audit']['ELF_or_ar_payloads']==manifest['content_audit']['provided_license_occurrences']==0
    assert len(parent['inherited_source_files'])==165 and reconstructed==167
    print(json.dumps({'status':'passed','archive_payloads':len(payload),'inherited_source_files':len(inherited),'reconstructed_captured_source_files':reconstructed,'raw_events':len(events),'origins_checked':args.origins,'compiler_or_integral_or_benchmark_executed':False}))
if __name__=='__main__':main()
