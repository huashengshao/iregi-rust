"""Bounded whitelist copier for PARTIAL N7 pilot evidence; launches no processes."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
FINITE = HERE.parent
ROOT = Path('/shared/external/iregi/iregi-rust')
NEXT = FINITE/'next-ranks-proposal'
WARM = FINITE/'probe-fix-v2'
sys.path.insert(0,str(FINITE))
from lifecycle import Budget

BUILD_SHA='688a0a0d269a38996075044721321f2aeafe0ab15e549c406c45af19ba1916c6'
PROBE_SHA='213ea01fd30a8acf2a794474db09ad9fc367fb9561667c23f73c76c4953a7e19'
FIXTURE_SHA='6c78096e83a399acd111137115505eae10da620b9dd68b6ead56eb2fa06489d2'
QUAD_SHA='f0b8f0774d901957fac3369165212b0efac3bf6921cea3c940269f191af373fd'
MAX_FILES,MAX_BYTES=100,200_000_000


def require(value,message):
    if not value:raise ValueError(message)


def load(path):
    def unique(pairs):
        result={}
        for name,value in pairs:
            require(name not in result,'duplicate JSON key')
            result[name]=value
        return result
    return json.loads(Path(path).read_text(),object_pairs_hook=unique)


def save(path,value):
    temporary=Path(path).with_name(Path(path).name+'.tmp')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    temporary.replace(path)


def key(path):return str(Path(path).relative_to(ROOT))


def digest(path,budget):
    value=hashlib.sha256()
    with Path(path).open('rb') as stream:
        while True:
            budget.remaining()
            block=stream.read(1024*1024)
            if not block:return value.hexdigest()
            value.update(block)


def metadata(path,expected,budget):
    require(digest(path,budget)==expected,'closed metadata digest differs: '+key(path))
    return load(path)


def main():
    require(Path.cwd().resolve()==ROOT and len(sys.argv)==2,'assemble selection.json from project root')
    selection_path=Path(sys.argv[1]).resolve()
    require(selection_path.is_relative_to(HERE) and selection_path.suffix=='.json','local source selection JSON required')
    selection=load(selection_path)
    require(selection['status']=='ready_for_private_partial_N7_capsule_after_terminal_failures_and_reviews'
        and set(selection['independent_reviews'])=={'1','2'}
        and set(selection['pair_gate_sha256'])=={'1','2'},'only completed rank1/rank2 gates and terminal rank7 failure review required')
    destination=ROOT/selection['destination']
    require(destination.is_relative_to(ROOT/'validation') and '..' not in destination.parts
        and destination.resolve()==destination and not destination.exists(),'fresh validation capsule path required')
    budget=Budget(180)
    budget.work_deadline=budget.deadline-30
    budget.arm()
    destination.mkdir(parents=True,exist_ok=False)
    receipt=destination/'assembly.json'
    record=dict(status='assembling',bound_seconds=180,postwork_reserve_seconds=30,
        per_child_cap_seconds=0,cpu_affinity=[20,21],started_monotonic=budget.started,
        absolute_deadline_monotonic=budget.deadline,files={},copied_bytes=0,
        compiler_or_integral_execution=False,binaries_copied=0,caches_copied=0,
        recursive_closure_walks=0,credentials_copied=False,performance_qualified=False)
    save(receipt,record)
    try:
        require({20,21}.issubset(os.sched_getaffinity(0)),'assembly CPUs unavailable')
        items={}
        def add(source,target,expected):
            source=Path(source)
            relative=Path(target)
            require(source.is_relative_to(ROOT) and source.resolve()==source and source.is_file()
                and not relative.is_absolute() and '..' not in relative.parts,'invalid explicit capsule member')
            require(target not in items and len(expected)==64,'duplicate destination or invalid digest')
            require(source.suffix not in ['.rlib','.rmeta','.so','.a','.o','.mod']
                and source.name not in ['positive-rank-probe','frozen-executable','iregi-reference-quad'],
                'native artifacts are excluded')
            items[target]=dict(source=key(source),sha256=expected)
        build=metadata(WARM/'runs/build-002/run.json',BUILD_SHA,budget)
        require(build['status']=='passed' and build['inputs_unchanged'] is True
            and build['outputs']['positive-rank-probe']==PROBE_SHA,'warm actual-Cargo ancestry not admitted')
        protocol=load(NEXT/'protocol.json')
        source_review=load(NEXT/'source-review.json')
        require(source_review['status']=='source_review_passed' and source_review['findings']==[],
            'compact source review absent')
        add(NEXT/'protocol.json','source/compact-protocol.json',source_review['protocol_sha256'])
        add(NEXT/'prepare-001/run.json','source/preparation-receipt.json',source_review['preparation_receipt_sha256'])
        for name in ['rank_adapter.py','run.py','prepare.py','recipe.json','README.md',
                     'source-manifest.json','source-snapshot.tar.gz']:
            add(NEXT/name,'source/next-ranks/'+name,protocol['inputs'][key(NEXT/name)])
        for name in ['common.py','lifecycle.py','compare_positive_saved.py']:
            add(FINITE/name,'source/finite/'+name,protocol['inputs'][key(FINITE/name)])
        numeric=ROOT/'validation/highpoint-thin-n6-rank7-phase/reference/compare_public.py'
        add(numeric,'source/retained_numeric_helper.py',protocol['inputs'][key(numeric)])
        add(FINITE.parent/'fixture.json','fixture.json',FIXTURE_SHA)
        warm_review=load(WARM/'source-review.json')
        for name in ['continuation.py','run.py','prepare.py','README.md','failed-probe-source.rs','probe-only.patch']:
            add(WARM/name,'source/probe-fix-v2/'+name,warm_review['source_sha256'][key(WARM/name)])
        for path,expected in protocol['historical_attestations'].items():
            if '/runs/compare-001/' in path:continue
            source=ROOT/path
            add(source,'history/'+('initial-'+source.name if source==FINITE/'protocol.json'
                else 'failed-build.json' if source==FINITE.parent/'build-001/run.json'
                else 'warm-build.json' if source==WARM/'runs/build-002/run.json'
                else 'warm-'+source.name if source==WARM/'protocol.json' else source.name),expected)
        add(WARM/'runs/build-002/cargo-artifacts.json','history/actual-Cargo-products.json',
            build['outputs']['cargo-artifacts.json'])
        failed=load(FINITE.parent/'build-001/run.json')
        add(FINITE.parent/'build-001/step-0.log','history/failed-build-E0616.log',failed['outputs']['step-0.log'])
        history_reviews=['positive-n7-build-failure-independent-saved-review.json',
            'positive-n7-probe-fix-lineage-independent-review.json','positive-n7-warm-build-independent-saved-review.json']
        for name in history_reviews:
            path=ROOT/'target/resume-20261025-review'/name
            expected=selection['historical_review_sha256'][name]
            review=metadata(path,expected,budget)
            require(review['findings']==[] and review['status'].startswith('passed_independent'),
                'historical independent review did not pass')
            add(path,'reviews/'+name,expected)
        quad=ROOT/'target/quad-iregi-source-audit/future-positive-rank-requests'
        audit=metadata(quad/'independent-saved-review.json',QUAD_SHA,budget)
        require(audit['findings']==[],'quad review has findings')
        add(quad/'independent-saved-review.json','reference/independent-saved-review.json',QUAD_SHA)
        for suffix,expected in [('protocol.json',audit['protocol_sha256']),
            ('capture-001/run.json',audit['run_sha256']),('capture-001/validation.json',audit['validation_sha256']),
            ('capture-001/pole-zero-exact.json',audit['pole_gate_sha256'])]:
            add(quad/suffix,'reference/'+suffix,expected)
        audited_source_pins={}
        for rank,index in [(1,0),(2,1)]:
            for suffix in [f'quad_n7_seventh_time_quarter_rank{rank}.txt',f'capture-001/request-{index}.stdout']:
                add(quad/suffix,'reference/'+suffix,build['inputs'][key(quad/suffix)])
            folder=WARM/'runs' if rank==1 else NEXT/f'runs/rank{rank}'
            gate_path=folder/'compare-001/run.json'
            gate=metadata(gate_path,selection['pair_gate_sha256'][str(rank)],budget)
            require(gate['status']=='passed' and gate['inputs_unchanged'] is True
                and gate['saved_math_status']=='passed_saved_math' and not gate['cleanup_errors'],
                'rank paired gate did not pass')
            math_path=folder/'compare-001/comparison.json'
            mathematical=metadata(math_path,gate['outputs']['comparison.json'],budget)
            require(mathematical['status']=='passed_saved_math' and mathematical['rank']==rank
                and mathematical['complex_slots_per_capture']=={1:20,2:60,7:1320}[rank],
                'wrong complete rank gate')
            review_spec=selection['independent_reviews'][str(rank)]
            review_path=ROOT/review_spec['path']
            require(review_path.is_relative_to(ROOT/'target/resume-20261025-review')
                and review_path.suffix=='.json','explicit saved independent review JSON required')
            review=metadata(review_path,review_spec['sha256'],budget)
            review_binary=review.get('binary_sha256',review['bindings'].get(
                key(WARM/'runs/build-002/positive-rank-probe')))
            require(review['findings']==[] and review['rank']==rank
                and review['status'].startswith('passed_independent_N7_rank')
                and review_binary==PROBE_SHA
                and review['bindings'][key(gate_path)]==selection['pair_gate_sha256'][str(rank)]
                and review['bindings'][key(math_path)]==gate['outputs']['comparison.json'],
                'matching independent full-array review missing')
            if rank==1:
                audited_source_pins[key(WARM/'source-review.json')]=review['bindings'][key(WARM/'source-review.json')]
            else:
                require(review['bindings'][key(NEXT/'protocol.json')]==source_review['protocol_sha256'],
                    'copied compact protocol is not the independently audited context')
                source_review_pin=review['bindings'][key(NEXT/'source-review.json')]
                require(key(NEXT/'source-review.json') not in audited_source_pins
                    or audited_source_pins[key(NEXT/'source-review.json')]==source_review_pin,
                    'rank audits disagree on active source review')
                audited_source_pins[key(NEXT/'source-review.json')]=source_review_pin
                for entry in items.values():
                    if entry['source'] in protocol['inputs']:
                        require(review['bindings'][entry['source']]==entry['sha256'],
                            'copied active file differs from independently audited leaf')
                for name,expected in protocol['historical_attestations'].items():
                    require(review['bindings'][name]==expected,'historical attestation differs from audited context')
            add(review_path,f'reviews/rank{rank}-independent-review.json',review_spec['sha256'])
            add(gate_path,f'numeric/rank{rank}/paired-receipt.json',selection['pair_gate_sha256'][str(rank)])
            add(math_path,f'numeric/rank{rank}/paired-comparison.json',gate['outputs']['comparison.json'])
            for bits in [128,256]:
                captured=folder/f'capture{bits}-001'
                run_path=captured/'run.json'
                run=metadata(run_path,review['bindings'][key(run_path)],budget)
                require(run['status']=='passed' and run['inputs_unchanged'] is True
                    and run['executed_binary_sha256']==PROBE_SHA and not run['cleanup_errors'],
                    'closed actual capture not admitted')
                add(run_path,f'numeric/rank{rank}/float{bits}/receipt.json',review['bindings'][key(run_path)])
                for name in ['result.json','step-0.log']:
                    require(review['bindings'][key(captured/name)]==run['outputs'][name],
                        'independent raw-result binding differs')
                    add(captured/name,f'numeric/rank{rank}/float{bits}/'+name,run['outputs'][name])
        failure_spec=selection['rank7_failure_review']
        failure_path=ROOT/failure_spec['path']
        require(failure_path.is_relative_to(ROOT/'target/resume-20261025-review')
            and failure_path.suffix=='.json','explicit rank7 failure review required')
        failure=metadata(failure_path,failure_spec['sha256'],budget)
        require(failure['status']=='passed_independent_saved_failure_and_additive_terminal_release_review'
            and failure['findings']==[] and failure['mathematical_qualification'] is False
            and failure['complete_output_arrays']==0 and failure['public_positive_rank_qualified'] is False,
            'rank7 failure/release review must not claim successful arrays')
        expected_outcomes={128:'fixed_child_timeout',256:'deliberate_signal15_resource_abort'}
        require({entry['working_bits']:entry['outcome'] for entry in failure['attempts']}==expected_outcomes
            and all(entry['complete_complex_output_slots']==0 and entry['original_owned_group_gone'] is False
                for entry in failure['attempts']),'rank7 outcome history differs')
        add(failure_path,'reviews/rank7-terminal-failure-independent-review.json',failure_spec['sha256'])
        for suffix in ['quad_n7_seventh_time_quarter_rank7.txt','capture-001/request-2.stdout']:
            add(quad/suffix,'reference/'+suffix,build['inputs'][key(quad/suffix)])
        errors=['owned process leader did not exit after SIGKILL','owned descendant process group remains after cleanup']
        for bits in [128,256]:
            captured=NEXT/f'runs/rank7/capture{bits}-001'
            run_path=captured/'run.json'
            run=metadata(run_path,failure['bindings'][key(run_path)],budget)
            require(run['status']=='failed' and run['cleanup_errors']==errors
                and run['steps'][0]['owned_group_gone'] is False and run['executed_binary_sha256']==PROBE_SHA,
                'original rank7 failure and cleanup fields must remain unchanged')
            if bits==128:require(run['steps'][0].get('timeout') is True,'rank7 Float128 child timeout not retained')
            else:require('signal 15' in run['cancellation'],'rank7 Float256 deliberate cancellation not retained')
            add(run_path,f'diagnostics/rank7/float{bits}/receipt.json',failure['bindings'][key(run_path)])
            for name in ['result.json','step-0.log']:
                require(failure['bindings'][key(captured/name)]==run['outputs'][name],
                    'rank7 checkpoint/log independent digest differs')
                add(captured/name,f'diagnostics/rank7/float{bits}/'+name,run['outputs'][name])
            checkpoint=metadata(captured/'result.json',run['outputs']['result.json'],budget)
            require(checkpoint['status']=='preparing_workspace' and 'lanes' not in checkpoint,
                'rank7 checkpoint is not an empty preparation diagnostic')
        for name in ['rank7-256-resource-abort-001.json','rank7-pair-terminal-absence-001.json',
                     'rank7-workspace-resource-001.json']:
            path=NEXT/'observations'/name
            add(path,'diagnostics/rank7/observations/'+name,failure['bindings'][key(path)])
        absence=load(NEXT/'observations/rank7-pair-terminal-absence-001.json')
        require(absence['original_receipts_rewritten'] is False
            and absence['status']=='owned_groups_absent_after_preserved_historical_cleanup_failures',
            'later release observation must remain separate from failed cleanup')
        add(NEXT/'observations/rank7-128-cleanup-followup-001.json',
            'diagnostics/rank7/observations/rank7-128-cleanup-followup-001.json',
            '636131f264313aade20f7a8517944207828db9645a6422ba80ad64acce073f8a')
        recipe=load(HERE/'recipe.json')
        for source,target in [(NEXT/'source-review.json','reviews/compact-source-review.json'),
            (WARM/'source-review.json','reviews/probe-fix-source-review.json'),
            (selection_path,'assembly-selection.json'),(HERE/'assemble_partial.py','assembly-source/assemble_partial.py'),
            (HERE/'recipe.json','assembly-source/recipe.json'),(HERE/'README.md','README.md')]:
            add(source,target,audited_source_pins.get(key(source)) or digest(source,budget))
        require(len(items)+3<=MAX_FILES and sum((ROOT/v['source']).stat().st_size for v in items.values())<=MAX_BYTES,
            'compact fixed inventory exceeded')
        for target,entry in sorted(items.items()):
            budget.remaining()
            source=ROOT/entry['source'];output=destination/target
            output.parent.mkdir(parents=True,exist_ok=True)
            value=hashlib.sha256()
            with source.open('rb') as src,output.open('xb') as dst:
                require(src.read(4)!=b'\x7fELF','ELF artifact rejected');src.seek(0)
                while block:=src.read(1024*1024):
                    budget.remaining();value.update(block);dst.write(block)
                    record['copied_bytes']+=len(block)
            require(value.hexdigest()==entry['sha256'],'copy differs from admitted source: '+entry['source'])
            record['files'][target]=entry
        save(destination/'qualification.json',recipe['scope'])
        record['status']='copied_awaiting_destination_hashes'
    except Exception as error:record.update(status='failed',error=repr(error))
    finally:budget.disarm()
    post=Budget(max(0,budget.deadline-time.monotonic()))
    post.deadline,post.work_deadline=budget.deadline,budget.deadline-5
    try:
        post.arm();require(record['status']=='copied_awaiting_destination_hashes','copy incomplete')
        for target,entry in record['files'].items():
            require(digest(destination/target,post)==entry['sha256'],'destination digest differs')
        record['qualification_sha256']=digest(destination/'qualification.json',post)
        save(destination/'MANIFEST.json',dict(schema_version=1,status='partial_evidence_only',files=record['files'],qualification_sha256=record['qualification_sha256']))
        record['manifest_sha256']=digest(destination/'MANIFEST.json',post)
        record['status']='partial_capsule_copy_passed_awaiting_root_review'
    except Exception as error:record.update(status='failed',postguard_error=repr(error))
    finally:post.disarm()
    record.update(elapsed_seconds=budget.elapsed(),cancellation=budget.cancelled,postguard_cancellation=post.cancelled)
    if budget.cancelled or post.cancelled or record['elapsed_seconds']>180:record['status']='failed'
    tail=Budget(max(0,budget.deadline-time.monotonic()));tail.deadline=tail.work_deadline=budget.deadline
    try:
        tail.arm();save(receipt,record);tail.remaining()
    except Exception as error:
        record.update(status='failed',finalization_error=repr(error),elapsed_seconds=budget.elapsed());save(receipt,record)
    finally:tail.disarm()
    print({'status':record['status'],'destination':key(destination),'files':len(record['files'])})
    return 0 if record['status']=='partial_capsule_copy_passed_awaiting_root_review' else 1


if __name__=='__main__':sys.exit(main())
