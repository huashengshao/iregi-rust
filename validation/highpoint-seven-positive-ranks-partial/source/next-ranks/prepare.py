"""One bounded, source/hash-only compact seal; no compiler or integral process."""
import gzip
import hashlib
import io
import os
from pathlib import Path
import sys
import tarfile
import time

import rank_adapter as h
from lifecycle import Budget

QUAD = 'target/quad-iregi-source-audit/future-positive-rank-requests/'
WARM_PROTOCOL_SHA = '256ba15b891df1ac70e676a74d1817429db978150a5926b6e24c059da22143a0'
CORRECTION_SHA = '6e3f18985f39ff945793e92825ceb524bec564bb07515d90fb22f14395a393a5'
PROBE_SOURCE_SHA = '9cc1860aaac2649db4eae850c7ecca4ea25e7013da4db168aa824dd0f2dbc9a1'


def pin(path, expected, budget):
    h.require(h.sha(path, budget) == expected, 'changed admitted source/attestation: ' + str(path))


def main():
    h.require(Path.cwd().resolve() == h.ROOT and len(sys.argv) == 1, 'prepare takes no arguments; project cwd required')
    budget = Budget(180)
    budget.work_deadline = budget.deadline - 30
    budget.arm()
    folder = h.DELTA / 'prepare-001'
    folder.mkdir(exist_ok=False)
    receipt = folder / 'run.json'
    record = dict(status='preparing_compact_source_seal', bound_seconds=180,
        postwork_reserve_seconds=30, per_child_cap_seconds=0, cpu_affinity=[20,21],
        started_monotonic=budget.started, absolute_deadline_monotonic=budget.deadline,
        work_deadline_monotonic=budget.work_deadline, compiler_or_integral_execution=False,
        license_recorded=False, source_directory_walks=0, transitive_dependency_hashes=0,
        numerical_qualified=False, performance_qualified=False, outputs={})
    h.save(receipt, record)
    completed = False
    try:
        h.require({20,21}.issubset(os.sched_getaffinity(0)), 'source seal CPU reservation unavailable')
        h.require(not any((h.DELTA/name).exists() for name in
            ['protocol.json','source-manifest.json','source-snapshot.tar.gz']), 'one-shot compact source seal already exists')
        warm_path = h.WARM/'protocol.json'
        pin(warm_path, WARM_PROTOCOL_SHA, budget)
        warm = h.load(warm_path)
        base_path = h.HERE/'protocol.json'
        pin(base_path, warm['base_protocol_sha256'], budget)
        base = h.load(base_path)
        correction_path = h.WARM/'correction.json'
        pin(correction_path, CORRECTION_SHA, budget)
        correction = h.load(correction_path)
        build_path = h.WARM/'runs/build-002/run.json'
        pin(build_path, h.BUILD_SHA, budget)
        build = h.load(build_path)
        h.require(build['status']=='passed' and build['operation']=='build' and build['attempt']==2
            and build['inputs_unchanged'] is True and not build['cleanup_errors']
            and build['outputs']['positive-rank-probe']==h.PROBE_SHA, 'actual Cargo build002 was not admitted')
        gate_path = h.WARM/'runs/compare-001/run.json'
        math_path = h.WARM/'runs/compare-001/comparison.json'
        pin(gate_path,h.RANK1_GATE_SHA,budget)
        pin(math_path,h.RANK1_MATH_SHA,budget)
        h.rank1_gate(h.load(gate_path),h.load(math_path))
        source_names = base['source_directory_inventory'][str(h.SOURCE)]['files']
        h.require(len(source_names)==len(set(source_names))==128, 'exact private128 source membership required')
        source_inputs = {}
        archive_path = h.DELTA/'source-snapshot.tar.gz'
        with archive_path.open('xb') as raw:
            with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as compressed:
                with tarfile.open(fileobj=compressed,mode='w|',format=tarfile.PAX_FORMAT) as archive:
                    for name in sorted(source_names):
                        budget.remaining()
                        relative = Path(name)
                        h.require(not relative.is_absolute() and '..' not in relative.parts
                            and str(relative)==name, 'invalid explicit snapshot member')
                        source = h.SOURCE/relative
                        h.require(source.resolve()==source and source.is_file(), 'source symlink/type differs')
                        expected = base['inputs'][h.key(source)]
                        if h.key(source)==correction['old_probe_source_path']:
                            h.require(expected==correction['old_probe_sha256']
                                and correction['new_probe_sha256']==PROBE_SOURCE_SHA, 'wrong corrected probe source identity')
                            expected = PROBE_SOURCE_SHA
                        h.require(build['inputs'][h.key(source)]==expected, 'source not bound by admitted build')
                        data = source.read_bytes()
                        h.require(hashlib.sha256(data).hexdigest()==expected, 'source snapshot byte drift: '+name)
                        entry = tarfile.TarInfo(name)
                        entry.size,entry.mode,entry.mtime,entry.uid,entry.gid = len(data),0o444,0,0,0
                        entry.uname=entry.gname=''
                        archive.addfile(entry,io.BytesIO(data))
                        source_inputs[name]=expected
        archive_path.chmod(0o444)
        manifest_path = h.DELTA/'source-manifest.json'
        h.save(manifest_path,dict(status='exact_corrected_private128_source_snapshot',files=source_inputs,
            archive_sha256=h.sha(archive_path,budget),actual_Cargo_build_receipt_sha256=h.BUILD_SHA,
            explicit_membership_from=base['source_directory_inventory'][str(h.SOURCE)]['files'],
            transitive_dependency_sources_copied=False,live_source_tree_guard_required=False))
        manifest_path.chmod(0o444)
        active = {}
        def add(path, expected=None):
            digest=h.sha(path,budget)
            h.require(expected is None or digest==expected,'compact admitted input changed: '+str(path))
            h.merge(active,h.key(path),digest)
        for name in ['rank_adapter.py','run.py','prepare.py','recipe.json','README.md',
                     'source-manifest.json','source-snapshot.tar.gz']:
            add(h.DELTA/name)
        for name in ['common.py','lifecycle.py','compare_positive_saved.py']:
            path=h.HERE/name
            add(path,build['inputs'][h.key(path)])
        helper=h.ROOT/'validation/highpoint-thin-n6-rank7-phase/reference/compare_public.py'
        add(helper,build['inputs'][h.key(helper)])
        add(h.BUNDLE/'fixture.json','6c78096e83a399acd111137115505eae10da620b9dd68b6ead56eb2fa06489d2')
        executable=h.WARM/'runs/build-002/positive-rank-probe'
        add(executable,h.PROBE_SHA)
        for suffix in ['independent-saved-review.json','quad_n7_seventh_time_quarter_rank2.txt',
                       'quad_n7_seventh_time_quarter_rank7.txt','capture-001/request-1.stdout',
                       'capture-001/request-2.stdout']:
            name=QUAD+suffix
            add(h.ROOT/name,build['inputs'][name])
        h.require(active[QUAD+'independent-saved-review.json']==h.QUAD_AUDIT_SHA,'quad review pin differs')
        audit=h.load(QUAD+'independent-saved-review.json')
        h.require(audit['status']=='passed_independent_quad_future_reference_raw_and_N7_zero_pole_review'
            and all(len([c for c in audit['cases'] if c['n']==7 and c['rank']==rank
                and c['complete_complex_slots']==slots])==1 for rank,slots in [(2,60),(7,1320)]),
            'independent full matching-rank quad arrays missing')
        historical={}
        for path,expected in [(warm_path,WARM_PROTOCOL_SHA),(base_path,warm['base_protocol_sha256']),
            (correction_path,CORRECTION_SHA),(build_path,h.BUILD_SHA),
            (h.WARM/'partial-build-lineage.json','8181a677fba40e9e988f66e8199f51b80731560073f287bf6cadfeb037f3d0d9'),
            (h.BUNDLE/'build-001/run.json','7de2a5ace98eca653c89143d80bde8467ff10285c4caba560641fddf2b08d108'),
            (gate_path,h.RANK1_GATE_SHA),(math_path,h.RANK1_MATH_SHA)]:
            pin(path,expected,budget)
            h.merge(historical,h.key(path),expected)
        tools={name:base['tools'][name] for name in ['python','taskset']}
        for path in tools.values():
            add(Path(path),build['inputs'][h.key(Path(path))])
        p=dict(h.load(h.DELTA/'recipe.json')['future_protocol_fields'],
            tools=tools,shared_executable=h.key(executable),inputs=active,
            historical_attestations=historical,
            source_snapshot=dict(path=h.key(archive_path),files=128,sha256=active[h.key(archive_path)],
                manifest=h.key(manifest_path)),
            frozen_environment={name:base['frozen_environment'].get(name) for name in h.ENVIRONMENT_KEYS},
            no_recursive_historical_guards=True,license_recorded=False,native_link_closure_qualified=False,
            source_scope='exact compiled private source snapshot; historical external build closure is attested',
            numerical_qualified=False,performance_qualified=False)
        h.check_context(p,budget=budget)
        protocol_path=h.DELTA/'protocol.json'
        h.save(protocol_path,p)
        protocol_path.chmod(0o444)
        record['compact_inputs']=active
        record['historical_attestations']=historical
        record['snapshot_files']=128
        completed=True
    except Exception as error:
        record.update(status='failed',error=repr(error))
    finally:
        budget.disarm()
    post=Budget(max(0,budget.deadline-time.monotonic()))
    post.deadline,post.work_deadline=budget.deadline,budget.deadline-5
    try:
        post.arm()
        h.require(completed,'compact seal did not complete')
        p=h.load(h.DELTA/'protocol.json')
        h.check_context(p,budget=post)
        guard=dict(p['inputs'])
        for name,digest in p['historical_attestations'].items():h.merge(guard,name,digest)
        record['provenance_after']=h.verify(guard,post,'source_seal_after')
        for name in ['protocol.json','source-manifest.json','source-snapshot.tar.gz']:
            record['outputs'][name]=h.sha(h.DELTA/name,post)
        record['inputs_unchanged']=True
    except Exception as error:
        record.update(status='failed',postguard_error=repr(error),inputs_unchanged=False)
    finally:
        post.disarm()
    record.update(elapsed_seconds=budget.elapsed(),cancellation=budget.cancelled,postguard_cancellation=post.cancelled)
    record['status']='compact_source_seal_passed_awaiting_independent_review_and_root_grants' if (
        completed and record.get('inputs_unchanged') is True and not budget.cancelled and not post.cancelled
        and record['elapsed_seconds']<=180) else 'failed'
    tail=Budget(max(0,budget.deadline-time.monotonic()))
    tail.deadline=tail.work_deadline=budget.deadline
    try:
        tail.arm()
        h.save(receipt,record)
        tail.remaining()
    except Exception as error:
        record.update(status='failed',finalization_error=repr(error),elapsed_seconds=budget.elapsed())
        h.save(receipt,record)
    finally:
        tail.disarm()
    print({'status':record['status'],'receipt':h.key(receipt)})
    return 0 if record['status'].startswith('compact_source_seal_passed') else 1


if __name__=='__main__':
    sys.exit(main())
