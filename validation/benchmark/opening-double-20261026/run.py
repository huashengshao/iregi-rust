#!/usr/bin/env python3
"""Bounded binary64-only candidate capture; never changes old evidence.

Use build, run, summarize from the repository root. Compilation/native execution
are root-owned and require a numerical quiet window. Saved reference comparison
uses exact rational f64 operands and the previously validated complete tensors.
"""
import argparse
import datetime
from fractions import Fraction as F
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import statistics
import subprocess
import time

ROOT=Path.cwd().resolve()
HERE=Path(__file__).resolve().parent
OLD=ROOT/'validation/benchmark/opening-rank6-20261026'
TARGET=ROOT/'target/opening-double-20261026'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.partial')
    temporary.write_text(json.dumps(value,indent=2)+'\n')
    temporary.replace(path)


def capture(command):
    return subprocess.check_output(command,text=True).strip()


def source_hashes():
    paths=set(json.loads((OLD/'source-files.json').read_text())['paths'])
    paths.update(str((HERE/name).relative_to(ROOT)) for name in ('run.py','make-inputs.py','inputs.json'))
    paths.add('crates/iregi-rust/examples/opening_double.rs')
    return {name:digest(ROOT/name) for name in sorted(paths)}


def supervise(command,log,cap_seconds):
    started=time.monotonic()
    result={'command':command,'cap_seconds':cap_seconds,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with log.open('wb') as stream:
        process=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
        result['owned_process_group']=process.pid
        try:
            result['returncode']=process.wait(timeout=cap_seconds)
            result['timed_out']=False
        except subprocess.TimeoutExpired:
            result['timed_out']=True
            os.killpg(process.pid,signal.SIGTERM)
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGKILL)
                process.wait(timeout=10)
            result['returncode']=process.returncode
        finally:
            try: os.killpg(process.pid,0)
            except ProcessLookupError: result['owned_group_gone']=True
            else:
                os.killpg(process.pid,signal.SIGKILL)
                result['owned_group_gone']=False
    result.update(elapsed_seconds=time.monotonic()-started,log_sha256=digest(log))
    return result


def build(args):
    TARGET.mkdir(parents=True,exist_ok=True)
    before=source_hashes()
    command=['taskset','-c',str(args.cpu),shutil.which('cargo'),'build','--release','--locked','--offline',
             '-p','iregi-rust','--example','opening_double','--features','native-f64-abc','--message-format=json','-j2']
    receipt={'schema_version':1,'source_revision':capture(['git','rev-parse','HEAD']),
             'source_hashes':before,'selected_context_not_complete_build_closure':True,
             'cargo':capture(['cargo','--version']),'rustc':capture(['rustc','-Vv']),
             'environment_overrides':{name:os.environ.get(name) for name in ('CARGO_TARGET_DIR','CARGO_BUILD_BUILD_DIR','CARGO_BUILD_JOBS','RAYON_NUM_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','RUST_MIN_STACK')},
             'cpu':args.cpu,'machine':capture(['uname','-a']),'cpu_information':capture(['lscpu']),
             'native_evaluation':False,'features':['native-f64-abc']}
    receipt['step']=supervise(command,TARGET/'build.log',args.timeout)
    receipt['sources_unchanged']=before==source_hashes()
    if receipt['step']['returncode']==0 and receipt['sources_unchanged']:
        artifacts=[]
        for line in (TARGET/'build.log').read_text().splitlines():
            try: event=json.loads(line)
            except ValueError: continue
            if event.get('reason')=='compiler-artifact' and event.get('executable') and event['target']['name']=='opening_double': artifacts.append(event)
        if len(artifacts)!=1: raise RuntimeError('expected one matching executable')
        frozen=TARGET/'opening_double'
        shutil.copy2(artifacts[0]['executable'],frozen)
        receipt.update(binary_sha256=digest(frozen),binary_path=str(frozen.relative_to(ROOT)),cargo_artifact=artifacts[0],status='built_and_frozen')
    else: receipt['status']='build_failed'
    save(HERE/'build.json',receipt)
    print(json.dumps({'status':receipt['status'],'seconds':receipt['step']['elapsed_seconds']}),flush=True)
    return int(receipt['status']!='built_and_frozen')


def run(args):
    suite=json.loads((HERE/'inputs.json').read_text())
    built=json.loads((HERE/'build.json').read_text())
    if source_hashes()!=built['source_hashes'] or digest(ROOT/built['binary_path'])!=built['binary_sha256']:
        raise RuntimeError('source or frozen binary changed since build')
    rows=[]
    for case in suite['cases']:
        if args.only and case['id'] not in args.only: continue
        for candidate in case['candidates']:
            if args.candidate and candidate['id'] not in args.candidate: continue
            folder=HERE/'cases'/case['id']/candidate['id']
            folder.mkdir(parents=True,exist_ok=True)
            result=folder/'result.json'
            if result.exists() or (folder/'supervision.json').exists():
                if args.skip_existing: continue
                raise RuntimeError('refusing to overwrite previous attempt: '+str(folder))
            request=candidate['request']
            save(folder/'request.json',request)
            command=['taskset','-c',str(args.cpu),str(ROOT/built['binary_path']),str(folder/'request.json'),str(result)]
            print(json.dumps({'starting':case['id'],'candidate':candidate['id'],'cpu':args.cpu}),flush=True)
            step=supervise(command,folder/'native.log',args.timeout)
            step.update(id=case['id'],candidate=candidate['id'],cpu=args.cpu,binary_sha256=built['binary_sha256'],
                        binary_unchanged_after=digest(ROOT/built['binary_path'])==built['binary_sha256'],
                        request_sha256=digest(folder/'request.json'),source_hashes_unchanged=source_hashes()==built['source_hashes'],
                        environment_threads={name:os.environ.get(name) for name in ('RAYON_NUM_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS')})
            if result.exists():
                step.update(result_sha256=digest(result),driver_status=json.loads(result.read_text())['status'])
            save(folder/'supervision.json',step)
            rows.append(step)
            print(json.dumps({'finished':case['id'],'candidate':candidate['id'],'returncode':step['returncode'],'status':step.get('driver_status'),'seconds':step['elapsed_seconds']}),flush=True)
    return int(any(row['returncode']!=0 for row in rows))


def stats(values):
    return {'mean':statistics.mean(values),'median':statistics.median(values),'minimum':min(values),'maximum':max(values),
            'stdev':statistics.stdev(values) if len(values)>1 else None,
            'standard_error':statistics.stdev(values)/math.sqrt(len(values)) if len(values)>1 else None}


def represented(pair):
    if len(pair)!=2 or any(value.get('finite') is not True or value.get('exact_rational') is None for value in pair):
        raise ValueError('nonfinite or missing exact coefficient')
    return tuple(F(value['exact_rational']) for value in pair)


def accuracy(case,result):
    reference_path=OLD/'cases'/case['id']/'result.json'
    prior=json.loads(reference_path.read_text())
    expected=prior['first_output']
    actual=result.get('first_output')
    info={'reference_source':str(reference_path.relative_to(ROOT)),'reference_sha256':digest(reference_path),
          'reference_qualification':'Previously admitted complete TIRust tensor (all18 independently agreed with original IREGI at1e-10); reference is finite-precision, not an exact integral oracle',
          'reference_comparison_sha256':digest(OLD/'reference-comparison.json'),'measured':False,
          'formula':'E/A with E=max_j |computed-reference|/mu^(degree+4+2h-2sum powers), A=max_j |reference|/same weight'}
    if not actual or len(actual.get('lanes',[]))!=1 or actual['lanes'][0].get('values') is None: return info
    if actual['basis']!=expected['basis'] or actual['laurent_order']!=expected['laurent_order'] or actual['components']!=1:
        raise ValueError('coefficient order or component mismatch')
    lhs=actual['lanes'][0]['values'];rhs=expected['lanes'][0]['values']
    if len(lhs)!=len(rhs) or len(lhs)!=4*len(actual['basis']): raise ValueError('incomplete tensor array')
    req=case['driver_request']
    mu=F(req['samples'][0]['mu'])
    difference=F(0);amplitude=F(0);mixed=F(0)
    try:
        for index,(a,b) in enumerate(zip(lhs,rhs)):
            av,bv=represented(a),represented(b)
            degree=sum(actual['basis'][index//4])
            exponent=degree+4+2*req['dimension_shift']-2*sum(req['powers'])
            weight_squared=mu**(2*exponent)
            difference_squared=sum((x-y)**2 for x,y in zip(av,bv))
            norm_squared=sum(y*y for y in bv)
            difference=max(difference,difference_squared/weight_squared)
            amplitude=max(amplitude,norm_squared/weight_squared)
            mixed=max(mixed,difference_squared/max(weight_squared,norm_squared))
    except ValueError as error:
        info['error']=str(error)
        return info
    relative_squared=difference/amplitude if amplitude else (F(0) if difference==0 else None)
    info.update(measured=True,compared_complex_fields=len(lhs),maximum_componentwise_mixed_error=math.sqrt(float(mixed)),
                relative_error=math.sqrt(float(relative_squared)) if relative_squared is not None else None,
                relative_error_squared_exact=str(relative_squared) if relative_squared is not None else None,
                relative_error_at_most_1e6=relative_squared is not None and relative_squared<=F(1,10**12),
                relative_error_at_most_1e3=relative_squared is not None and relative_squared<=F(1,10**6))
    return info


def summarize(args):
    suite=json.loads((HERE/'inputs.json').read_text())
    built=json.loads((HERE/'build.json').read_text())
    rows=[]
    for case in suite['cases']:
        req=case['driver_request']
        row={name:value for name,value in case.items() if name not in ('driver_request','candidates')}
        row.update({name:req[name] for name in ('n','rank','powers','dimension_shift','numeric_type','working_bits','requested_bits')})
        row.update(batch_size=1,moments=math.comb(row['rank']+4,4),laurent_slots=4,source_revision=built['source_revision'])
        attempts=[]
        for candidate in case['candidates']:
            folder=HERE/'cases'/case['id']/candidate['id']
            item={'id':candidate['id'],'request':candidate['request'],'status':'unmeasured',
                  'result_source':str((folder/'result.json').relative_to(ROOT))}
            if (folder/'supervision.json').exists():
                supervision=json.loads((folder/'supervision.json').read_text())
                result=json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else {}
                item.update(status=result.get('status','timeout_or_native_failure'),engine=result.get('workspace_engine'),
                            plan_engine=result.get('plan_engine'),plan_ns=result.get('plan_ns'),workspace_ns=result.get('workspace_ns'),
                            first_call_ns=result.get('first_call_ns'),successful_finite_full_array=bool(result.get('all_successful_finite_full_arrays')),
                            supervision_source=str((folder/'supervision.json').relative_to(ROOT)),
                            timing_captured=bool(result.get('timing_qualified')) and supervision['returncode']==0 and supervision['source_hashes_unchanged'] and supervision['owned_group_gone'] and supervision['binary_unchanged_after'])
                item['accuracy']=accuracy(case,result)
                if item['timing_captured']:
                    blocks=result['repeated_measurements']
                    fields=('tirust_exclusive_ns','scalar_masters_ns','outer_total_ns')
                    values={field:[statistics.mean(call[field] for call in block['calls'])/1000 for block in blocks] for field in fields}
                    item['timing']={field.removesuffix('_ns')+'_us':stats(data) for field,data in values.items()}
                    item.update(repeats=len(blocks),calls_per_repeat=len(blocks[0]['calls']),total_timed_calls=sum(len(block['calls']) for block in blocks),
                                maximum_additive_error_us=max(abs(call['outer_total_ns']-call['tirust_exclusive_ns']-call['scalar_masters_ns']) for block in blocks for call in block['calls'])/1000)
                    if item['maximum_additive_error_us']!=0: raise ValueError('nonadditive master split')
                item['eligible_optimistic_result']=bool(item.get('timing_captured') and item.get('successful_finite_full_array') and item['accuracy'].get('relative_error_at_most_1e3'))
            attempts.append(item)
        eligible=[item for item in attempts if item.get('eligible_optimistic_result')]
        timed=[item for item in attempts if item.get('timing_captured')]
        finite=[item for item in timed if item.get('successful_finite_full_array') and item.get('accuracy',{}).get('measured')]
        chosen=min(eligible or finite or timed,key=lambda item:item['timing']['outer_total_us']['mean']) if timed else None
        row.update(attempts=attempts,status='unmeasured' if chosen is None else chosen['status'],selected_candidate=None if chosen is None else chosen['id'],
                   timing_qualified=bool(chosen and chosen.get('eligible_optimistic_result')),
                   selection_warning=None if eligible else 'No measured candidate produced a complete finite tensor within three relative digits; diagnostic timing is explicitly not a usable result')
        if chosen:
            for key in ('timing','accuracy','engine','plan_engine','plan_ns','workspace_ns','first_call_ns','repeats','calls_per_repeat','total_timed_calls','result_source','supervision_source','successful_finite_full_array','timing_captured'):
                if key in chosen: row[key]=chosen[key]
            row['algorithm']=chosen['request']['algorithm']
            row['master_policy']=chosen['request']['master_policy']
            row['postconstruction_profiling']=chosen['request']['postconstruction_profiling']
        rows.append(row)
    summary={'schema_version':2,'suite_id':suite['suite_id'],'measurement_date':'2026-10-26','timing_contract':suite['timing_contract'],
             'input_family':suite['input_family'],'candidate_policy':suite['candidate_policy'],'rows':rows,
             'selection_notice':'Optimistic timing-first binary64 measurements. Fastest mean among fixed candidates with finite complete outputs and measured relative error <=1e-3. Measured accuracy shown separately; requested1e-6 applies onlythree high-point ordinaryrows. Failures and all candidates retained.',
             'statistics':'Arithmetic mean of equal-sized block means; standard error descriptive across repeats, not a controlled-host confidence guarantee. Same-call additive master split.',
             'measured_rows':sum(bool(row.get('timing_captured')) for row in rows),
             'three_digit_rows':sum(bool(row['timing_qualified']) for row in rows)}
    save(HERE/'summary.json',summary)
    print(json.dumps({key:summary[key] for key in ('measured_rows','three_digit_rows')}))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('build','run','summarize'))
    parser.add_argument('--cpu',type=int,default=18)
    parser.add_argument('--timeout',type=int,default=1800)
    parser.add_argument('--only',nargs='*')
    parser.add_argument('--candidate',nargs='*')
    parser.add_argument('--skip-existing',action='store_true')
    args=parser.parse_args()
    raise SystemExit(globals()[args.mode](args))
