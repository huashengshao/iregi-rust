#!/usr/bin/env python3
"""Verify retained sources, logs and raw diagnostic samples without an engine."""
from pathlib import Path
import hashlib,json,statistics


def main():
    root=Path(__file__).resolve().parent
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    records=json.loads((root/'files.json').read_text())['files']
    by_original={r['original']:root/r['stored'] for r in records}
    for record in records:
        p=root/record['stored']
        assert p.stat().st_size==record['bytes'],p
        assert sha(p)==record['sha256'],p
    q=json.loads((root/'qualification.json').read_text())
    assert not q['performance_gate'] and not q['production_changed']
    assert not q['full_core_candidate_tested'] and not q['complex_only_performance_tested']
    assert q['candidate_sha256']==sha(root/'artifacts/candidate.rs')
    for name in ['profile_probe','certificate_tests']:
        build=json.loads((root/f'artifacts/{name}-build.json').read_text())
        assert build['returncode']==0 and build['status']=='compiled'
        assert build['sources_unchanged'] and build['archives_unchanged']
        for source,digest in build['source_sha256'].items():
            p=by_original[source]
            if name=='profile_probe' and source.endswith('/candidate.rs'):
                p=root/'artifacts/candidate-at-profile-build.rs'
            assert sha(p)==digest,(name,source)
    assert '4 passed; 0 failed' in (root/q['paired_tests']['log']).read_text()
    assert '8 passed; 0 failed' in (root/q['inherited_certificate_tests']['log']).read_text()
    baseline=json.loads((root/'artifacts/profile-results.json').read_text())
    candidate=json.loads((root/'artifacts/candidate-profile-results.json').read_text())
    assert baseline['operations']==candidate['operations']==q['profile']['operations']
    for expected,br,cr in zip(q['profile']['rows'],baseline['rows'],candidate['rows'],strict=True):
        n=expected['batch_width'];assert n==br['batch_width']==cr['batch_width']
        for r,is_real in [(br,False),(cr,True)]:
            assert len(r['samples'])==21 and r['status']=='all_certified_zero'
            for sample in r['samples']:
                assert sample['certificate_passes']==1 and sample['evaluated_rows']==n
                assert sample['real_batch_calls']==int(is_real)
                assert sample['complex_batch_calls']==int(not is_real)
        bm=statistics.median(s['total_ns_per_batch'] for s in br['samples'])
        cm=statistics.median(s['total_ns_per_batch'] for s in cr['samples'])
        assert bm==expected['baseline_median_ns'] and cm==expected['candidate_median_ns']
        assert cm/bm==expected['candidate_over_baseline']
    print(f'Verified {len(records)} retained files, 4 paired + 8 inherited passing tests and 3 diagnostic profiles; no performance gate.')


if __name__=='__main__':
    main()
