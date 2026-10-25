#!/usr/bin/env python3
"""Verify the compact saved Cargo qualification; never build or evaluate an integral."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,tarfile,tempfile

def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def blobsha(data):return hashlib.sha256(data).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--origins',action='store_true');args=parser.parse_args()
    capsule=Path(__file__).resolve().parent;root=capsule.parents[1]
    manifest=json.loads((capsule/'manifest.json').read_text());q=json.loads((capsule/'qualification.json').read_text());parent=json.loads((capsule/'parent.json').read_text())
    assert {p.name for p in capsule.iterdir()if p.is_file()}==set(manifest['metadata_files'])|{'manifest.json','evidence.tar.gz'}
    for rel,item in manifest['metadata_files'].items():assert sha(capsule/rel)==item['sha256']and(capsule/rel).stat().st_size==item['bytes']
    archive=manifest['archive'];assert sha(capsule/'evidence.tar.gz')==archive['sha256']and(capsule/'evidence.tar.gz').stat().st_size==archive['bytes']
    payload={}
    with tarfile.open(capsule/'evidence.tar.gz','r:gz')as stream:
        members=stream.getmembers();assert len(members)==len(archive['members'])and {m.name for m in members}==set(archive['members'])
        for member in members:
            assert member.isfile()and not Path(member.name).is_absolute()and '..'not in Path(member.name).parts
            data=stream.extractfile(member).read();item=archive['members'][member.name]
            assert member.size==len(data)==item['bytes']and blobsha(data)==item['sha256']
            assert not data.startswith((b'\x7fELF',b'!<arch>\n'))
            if args.origins:assert sha(root/item['origin'])==item['sha256'],item['origin']
            payload[member.name]=data
    assert sha(root/parent['path'])==parent['sha256']
    source=json.loads(payload['source-freeze.json']);reconstructed=0
    with tarfile.open(root/parent['path'],'r:gz')as stream:
        for rel,item in parent['production_source_files'].items():
            data=stream.extractfile(item['parent_member']).read();assert len(data)==item['bytes']and blobsha(data)==item['sha256']
            matching=[v for p,v in source['files'].items()if p.endswith('/'+rel)];assert matching==[item['sha256']]
            reconstructed+=1
    assert reconstructed==85
    assert q['status']=='current-Cargo-native-policy-qualified-with-legacy-metadata-timeout'
    assert q['native_only_qualification_passed']is True and q['full_metadata_matrix_passed']is False
    metadata=json.loads(payload['runs/metadata-001/results.json']);assert metadata['status']=='failed'and metadata['inputs_unchanged']and not metadata['cleanup_errors']
    assert [r['configuration']for r in metadata['steps']]==['default','selective','broad','both']
    assert all(r['status']=='passed'and r['returncode']==0 and r['owned_group_gone']for r in metadata['steps'][:2])
    assert metadata['steps'][2]['timeout']and metadata['steps'][2]['owned_group_gone']and metadata['steps'][3]['status']=='unrun'
    assert metadata['elapsed_seconds']<600 and not metadata['deadline_exceeded']
    plan=json.loads(payload['commands-and-selection.json']);selected=0
    for configuration in ['default','selective']:
        for kind,cap in [('build',600),('tests',plan['runtime_aggregate_seconds'][configuration]),('probe',120)]:
            record=json.loads(payload[f'runs/{kind}-{configuration}-001/results.json'])
            assert record['status']=='passed'and record['inputs_unchanged']and not record['cleanup_errors']and not record['deadline_exceeded']and record['elapsed_seconds']<cap
            assert all(r['status']=='passed'and r['returncode']==0 and r['owned_group_gone']for r in record['steps'])
            if kind=='tests':
                cases=[r for r in plan['runtime_cases']if r['configuration']==configuration]
                assert [r['case']for r in record['steps'][2:]]==cases
                assert record['selected_case_count']==len(cases);selected+=len(cases)
    assert selected==26
    assert blobsha(payload['comparison-helper.py'])==q['comparison_helper_sha256']
    previous=Path.cwd()
    try:
        with tempfile.TemporaryDirectory()as directory:
            os.chdir(directory);helper=Path(directory)/'validation/benchmark/run.py';helper.parent.mkdir(parents=True);helper.write_bytes(payload['comparison-helper.py'])
            path=Path(directory)/'admit_probe.py';path.write_bytes(payload['admit_probe.py'])
            spec=importlib.util.spec_from_file_location('saved_current_cargo_admission',path);admission=importlib.util.module_from_spec(spec);spec.loader.exec_module(admission)
            source=json.loads(payload['probe-input.json']);reference=json.loads(payload['probe-reference.json'])
            for configuration in ['default','selective']:
                stdout=payload[f'runs/probe-{configuration}-001/step-0.stdout.log']
                outputs=[json.loads(line[7:])for line in stdout.splitlines()if line.startswith(b'RESULT ')];assert len(outputs)==1
                result=admission.qualify(configuration,outputs[0],source,reference)
                assert result==json.loads(payload[f'runs/probe-{configuration}-001/admission.json'])
    finally:os.chdir(previous)
    assert all(q['not_qualified_by_this_capsule'].values())and not q['benchmark_execution']and not q['automatic_retries']
    assert manifest['content_audit']['ELF_or_ar_payloads']==manifest['content_audit']['provided_license_occurrences']==0
    print(json.dumps({'status':'passed','archive_payloads':len(payload),'inherited_production_source_files':reconstructed,'actual_Cargo_selected_tests':selected,'five_lane_probes':2,'full_legacy_metadata_matrix':'failed-broad-timeout-both-unrun','origins_checked':args.origins,'compiler_integral_or_benchmark_executed':False}))
if __name__=='__main__':main()
