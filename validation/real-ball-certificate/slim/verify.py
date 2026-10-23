#!/usr/bin/env python3
"""Verify slim-candidate evidence without a numerical engine or target binaries."""
from pathlib import Path
import hashlib,json,re


def main():
    root=Path(__file__).resolve().parent
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    read=lambda p:json.loads((root/p).read_text())
    files=read('files.json')['files']
    for record in files:
        p=root/record['stored']
        assert p.stat().st_size==record['bytes'] and sha(p)==record['sha256'],p
    q=read('qualification.json');build=read('qualified/build.json');run=read('qualified/run.json')
    assert not q['production_changed'] and not q['performance_gate']
    assert not q['new_performance_measurements'] and not q['full_core_candidate_tested']
    assert q['candidate_sha256']==sha(root/'qualified/slim.rs')
    assert build['status']=='compiled' and type(build['returncode']) is int and build['returncode']==0
    assert build['closure_verified_before'] and build['closure_verified_after'] and build['sources_unchanged']
    assert run['status']=='passed' and run['verified_before'] and run['verified_after']
    assert run['build_manifest_sha256']==sha(root/'qualified/build.json')
    assert run['binary_sha256']==build['binary_sha256']==q['binary_sha256']
    assert run['source_sha256']==build['source_sha256']==q['source_sha256']
    for filename,digest in build['source_sha256'].items():
        assert sha(root/'qualified'/Path(filename).name)==digest,filename
    closure=read('dependency-closure/manifest.json');events=read('dependency-closure/cargo-library-events.json')
    completion=read('dependency-closure/workspace-completion.json');workspace=read('dependency-closure/workspace-build.json')
    assert sha(root/'dependency-closure/manifest.json')==build['dependency_closure_manifest_sha256']==completion['dependency_closure_manifest_sha256']
    assert sha(root/'dependency-closure/cargo-library-events.json')==build['cargo_library_events_sha256']
    assert len(events)==closure['library_event_count']==425
    assert len(closure['files'])+len(closure['native_files'])==build['closure_files']==865
    assert completion==build['workspace_completion']
    assert sha(root/'dependency-closure/workspace-completion.json')==build['workspace_completion_sha256']
    assert sha(root/'dependency-closure/workspace-build.json')==completion['workspace_manifest_sha256']
    assert type(completion['cargo_returncode']) is int and completion['cargo_returncode']==0
    assert completion['resources']['returncode']==workspace['resources']['returncode']==0
    by_path={record['retained']:record for record in closure['files']}
    for filename,digest in build['explicit_archive_sha256'].items():
        matches=[r for path,r in by_path.items() if path.endswith('/'+filename)]
        assert len(matches)==1 and matches[0]['sha256']==digest,filename
    for name,event in build['selected_library_events'].items():
        assert event in events and event['target']['name']==name
        assert event['profile']['opt_level']=='3' and not event['profile']['test']
    tests=(root/'qualified/tests.log').read_text()
    assert '23 passed; 0 failed; 0 ignored' in tests
    assert len(re.findall(r'^test candidate::tests::.* \.\.\. ok$',tests,re.M))==8
    assert len(re.findall(r'^test baseline::tests::.* \.\.\. ok$',tests,re.M))==8
    assert run['log_sha256']==sha(root/'qualified/tests.log')
    assert run['test_result']=={'status':'ok','passed':23,'failed':0,'ignored':0}
    failed=read('failed-first-attempt/build.json')
    assert failed['status']=='failed' and failed['returncode']!=0
    assert 'E0463' in (root/'failed-first-attempt/build.log').read_text()
    print(f'Verified {len(files)} retained files: 7 paired + 8 candidate + 8 baseline tests pass; no production/performance claim.')


if __name__=='__main__':
    main()
