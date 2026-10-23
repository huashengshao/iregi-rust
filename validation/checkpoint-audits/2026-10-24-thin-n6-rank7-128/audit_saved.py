#!/usr/bin/env python3
"""Independent saved-data audit; never imports a project comparator or runs kernels."""
from pathlib import Path
from decimal import Decimal, localcontext
from fractions import Fraction
from collections import Counter
import argparse, datetime, hashlib, json, tarfile

ROOT = Path.cwd().resolve()
H = ROOT / 'target/public-highpoint/thin-n6-rank7-phase'
OUT = ROOT / 'target/guard-performance-review/rank7-audit'
D = Decimal
SEEN = {}
CHECKS = Counter()


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def bind(path, expected=None):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    value = sha(path)
    if expected is not None and value != expected:
        raise ValueError(f'hash mismatch {path}: {value} != {expected}')
    key = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    if key in SEEN and SEEN[key] != value:
        raise ValueError(f'changed repeated artifact {key}')
    SEEN[key] = value
    CHECKS['artifact_bindings'] += 1
    return path


def load(path, expected=None):
    return json.loads(bind(path, expected).read_text(), parse_float=D)


def require(condition, message):
    CHECKS['assertions'] += 1
    if not condition:
        raise ValueError(message)


def rational(text):
    require(isinstance(text, str), 'candidate represented value is not a string')
    value = Fraction(text)
    return value


def decimal_fraction(value):
    return D(value.numerator) / D(value.denominator)


def complex_value(slot):
    require(set(slot) == {'real', 'imaginary', 'real_precision', 'imaginary_precision'}, 'unexpected complex schema')
    require(all(isinstance(slot[x], int) and slot[x] > 0 for x in ('real_precision', 'imaginary_precision')), 'invalid represented precision')
    return rational(slot['real']), rational(slot['imaginary'])


def modulus(re, im):
    return (re * re + im * im).sqrt()


def normalization(sample):
    # Numeric normalization only, from the declared formula. No symbolic
    # operation, comparator import, binary64 conversion or kernel invocation.
    lines = sample['propagators'][:6]
    masses = [Fraction(p['mass_squared'][0]) for p in lines]
    require(all(Fraction(p['mass_squared'][1]) == 0 for p in lines), 'scope requires real masses')
    points = [[Fraction(x) for x in p['shift']] for p in lines]
    squared = [Fraction(1)] + [abs(m) for m in masses]
    for i in range(6):
        for j in range(i):
            delta = [points[i][k] - points[j][k] for k in range(4)]
            invariant = delta[0] * delta[0] - sum((x * x for x in delta[1:]), Fraction(0))
            squared.append(abs(invariant))
    q2 = max(squared)
    require(q2 == 4, 'unexpected fixture Q squared')
    return decimal_fraction(q2).sqrt()


def expected_basis():
    # API index enumeration, independent of any polynomial implementation.
    result = []
    for degree in range(8):
        for time in range(degree, -1, -1):
            for x in range(degree - time, -1, -1):
                for y in range(degree - time - x, -1, -1):
                    result.append([time, x, y, degree - time - x - y])
    return result


def verify_result(result, sample, bits=128):
    expected = {'algorithm': 'PassarinoVeltman', 'convention': 'IregiNative', 'dimension_shift': 0,
                'input_policy': 'Preserve', 'invariants': 'FromShifts', 'powers': [1] * 6,
                'propagators': 6, 'rank': 7, 'tensor_weights': 'Components'}
    require(result['settings'] == expected, 'settings changed')
    require(result['working_bits'] == bits and result['requested_bits'] == 53, 'precision configuration changed')
    require(result['rows'] == 1 and result['components'] == 1, 'sample/Taylor shape changed')
    require(result['status'] == 'all_lanes_success' and result['lane_statuses'] == ['Success'], 'capture has unsuccessful lane')
    require(result['analytic_used'] == [True] and result['fallback_used'] == [True], 'analytic/fallback flags changed')
    require(len(result['lanes']) == 1 and result['lanes'][0]['row'] == 0 and result['lanes'][0]['status'] == 'Success', 'invalid lane ledger')
    require(result['basis'] == expected_basis() and len(result['basis']) == 330, 'basis cardinality/order changed')
    lines = sample['propagators'][:6]
    packed = [[Fraction(x), Fraction(0)] for p in lines for x in p['shift']]
    packed += [[Fraction(x) for x in p['mass_squared']] for p in lines]
    packed += [[Fraction(sample['mu']), Fraction(0)]]
    actual = [[Fraction(x) for x in pair] for pair in result['input_exact_rational'][0]]
    require(len(result['input_exact_rational']) == 1 and len(actual) == 31 and actual == packed, 'exact input packing mismatch')
    moments = result['lanes'][0]['moments']
    require(len(moments) == 330 and all(len(m) == 4 for m in moments), 'incomplete tensor/Laurent array')
    require(result['execution']['child_batch_calls'] == 1 and result['execution']['parent_batch_calls'] == 1, 'batch call count changed')
    require(result['execution']['packed_child_rows'] == 6 and result['execution']['packed_parent_rows'] == 1 and result['execution']['parent_input_rows'] == 1, 'packed row count changed')
    return moments


def verify_metadata():
    protocol = load(H/'protocol.json', '289e73fc1ade605cb5642cb443843f1ae6303d97f44edce07d1fc76d420aac0a')
    build = load(H/'build-001/build.json', 'f8f09d7fa2f745aaf09882f74ded59ff856d12423f380e16fedc56b23a723fa2')
    run = load(H/'n6-rank7-128-001/run.json', 'dfdbd263b9a28a5b5fb29627f67f3fd4bda21d8c4f43c1d2637bb6dc527b2aa7')
    failed_gate = load(H/'comparison-128.json', 'ad2fb606dd473a901f0c13192edf02b66c2cb14155dc2592524a4cc89218eb02')
    require(protocol['status'] == 'approved_source_only', 'protocol not approved')
    require(protocol['rank'] == 7 and protocol['child_rank'] == 6 and protocol['complex_slots'] == 1320 and protocol['moments'] == 330, 'protocol shape changed')
    require(protocol['fixture_rows'] == [0] and protocol['requested_bits'] == 53, 'protocol sample/accuracy changed')
    require(protocol['normalized_original_tolerance'] == '1e-10' and protocol['convergence_tolerance'] == '2^-80', 'tolerance changed')
    require(len(protocol['artifacts']) == 225 and len(build['inputs']) == 226 and len(run['inputs']) == 229, 'closure inventory size changed')
    require(build['status'] == 'passed' and run['status'] == 'passed' and build['inputs_unchanged'] and run['inputs_unchanged'], 'build/run terminal guard failed')
    require(build['bound_seconds'] == protocol['build_bound_seconds'] == 90 and run['bound_seconds'] == protocol['runtime_bound_seconds'] == 300, 'resource bounds changed')
    require(build['elapsed_seconds'] <= 90 and run['elapsed_seconds'] <= 300, 'overall bound exceeded')
    require(all(s['exit_code'] == 0 for s in build['steps'] + run['steps']), 'nonzero process exit')
    require(len(run['steps']) == 1 and run['steps'][0]['seconds'] <= 300, 'unexpected capture count/time')
    expected_command = ['taskset','-c','14',str(H/'build-001/driver'),str(ROOT/'validation/public-highpoint/fixture-conditioned_masses.json'),'6','7','pv','128','53','1',str(H/'n6-rank7-128-001/result.json')]
    require(run['steps'][0]['command'] == expected_command, 'kernel command mismatch')
    for record, key in [(protocol,'artifacts'), (build,'inputs'), (run,'inputs'), (failed_gate,'input_sha256')]:
        for path, digest in record[key].items():
            bind(path,digest)
    for directory, record in [(H/'build-001',build),(H/'n6-rank7-128-001',run)]:
        for name,digest in record['outputs'].items():
            bind(directory/name,digest)
    protocol_paths = {str((ROOT/path).resolve()) for path in protocol['artifacts']}
    require(set(build['inputs']) == protocol_paths | {str(H/'protocol.json')}, 'build closure differs from frozen protocol')
    require(set(run['inputs']) == set(build['inputs']) | {str(H/'build-001/build.json'), str(H/'build-001/driver'), str(H/'build-001/libiregi_rust.rlib')}, 'runtime closure differs from built artifacts')
    require(failed_gate['status'] == 'failed' and not failed_gate['full_array_original_agreement_qualified'] and not failed_gate['precision_convergence_qualified'], 'failed numerical gate was promoted')
    return protocol,build,run,failed_gate


def verify_source_restoration():
    copy = load(H/'copy-manifest.json')
    instrument = load(H/'instrumentation-manifest.json')
    archive = ROOT/'validation/highpoint-thin-n6-generic/sources.tar.gz'
    ledger = load('validation/highpoint-thin-n6-generic/archive-manifest.json')
    bind(archive,ledger['archive_sha256'])
    require(instrument['file_count'] == 36 and instrument['instrumentation_line_count'] == 29, 'instrumentation inventory changed')
    require(set(copy['source_files']) == {x['path'] for x in instrument['files']}, 'source file sets differ')
    changed=[]; removed=0; members=0
    with tarfile.open(archive) as stream:
        for member in stream.getmembers():
            require(member.isfile(), 'unexpected archive member type')
            data=stream.extractfile(member).read()
            require(hashlib.sha256(data).hexdigest() == ledger['members'][member.name], 'archive member hash mismatch')
            members+=1
        for path,digest in copy['source_files'].items():
            source=stream.extractfile('fixed/'+path).read()
            require(hashlib.sha256(source).hexdigest()==digest, 'qualified source hash mismatch')
            current=bind(H/'core'/path).read_bytes()
            entries=current.splitlines(keepends=True)
            restored=b''.join(line for line in entries if not line.rstrip().endswith(b'// IREGI_PHASE_ONLY'))
            removed+=sum(line.rstrip().endswith(b'// IREGI_PHASE_ONLY') for line in entries)
            require(restored==source, 'instrumentation does not exactly restore qualified source '+path)
            row=next(x for x in instrument['files'] if x['path']==path)
            require(hashlib.sha256(current).hexdigest()==row['instrumented_sha256'] and digest==row['source_sha256'], 'instrumentation file ledger differs')
            if current!=source:changed.append(path)
    require(members==len(ledger['members'])==95 and removed==29, 'archive/instrumentation count mismatch')
    require(changed==instrument['changed_files'], 'changed source inventory differs')
    generic = load('validation/highpoint-thin-n6-generic/qualification.json')
    exact = load('validation/highpoint-thin-n6-generic/fixed/exact-001/run.json',generic['exact_run_sha256'])
    require(generic['exact_tests']==25 and exact['status']=='passed', 'prior exact tests not qualified')
    return {'restored_files':36,'removed_diagnostic_lines':removed,'changed_files':changed,'verified_archive_members':members,'reused_exact_tests':25,'rerun_on_logging_binary':False}


def analyze(result, sample, reference):
    moments=verify_result(result,sample)
    case=next(c for c in reference['cases'] if c['id']=='n6_base_mode0')
    require(case['status']=='captured' and case['exit_code']==0 and case['mode']==0 and case['rank']==7 and case['propagators']==6, 'reference case mismatch')
    raw=[line[7:] for line in case['stdout'].splitlines() if line.startswith('RESULT ')]
    require(len(raw)==1,'ambiguous original RESULT')
    original=json.loads(raw[0],parse_float=D)
    require(original['stable'] is True and original['poles']==['uv1','ir1','ir2','finite'] and len(original['moments'])==330, 'original not stable/full/native')
    require(reference['reference']=='untouched original IREGI' and reference['status']=='complete', 'reference provenance mismatch')
    bind('target/reference/iregi-reference-original',reference['executable_sha256'])
    wire=case['request'].splitlines()
    require(wire[0].split()==['EVAL','n6_base_mode0','tensor','0','6','7','0','3','0','1e-6'] and wire[-1]=='QUIT' and len(wire)==8, 'reference request configuration changed')
    for line,propagator in zip(wire[1:-1],sample['propagators'][:6]):
        require([Fraction(x) for x in line.split()]==[Fraction(x) for x in propagator['shift']+propagator['mass_squared']]+[Fraction(1)], 'reference exact input differs')
    q=normalization(sample)
    threshold=D('1e-10')
    records=[]; zero_poles=0; rank_stats={}
    for index,(basis,candidate,old) in enumerate(zip(result['basis'],moments,original['moments'])):
        degree=sum(basis); scale=q**(degree-8)
        rank_stats.setdefault(degree,{'moments':0,'slots':0,'failed_slots':0,'maximum_error':D(0),'maximum_real_error':D(0),'maximum_imaginary_error':D(0)})['moments']+=1
        require(len(old)==4,'reference Laurent count mismatch')
        for pole,(slot,old_pair) in enumerate(zip(candidate,old)):
            re,im=complex_value(slot)
            if pole<3:
                require(re==0 and im==0,'candidate pole is not exactly zero')
                zero_poles+=1
            value_re,value_im=decimal_fraction(re),decimal_fraction(im)
            old_re,old_im=(D(x) for x in old_pair)
            require(old_re.is_finite() and old_im.is_finite(),'reference nonfinite')
            require(old_re==D(case['response']['moments'][index][pole][0]) and old_im==D(case['response']['moments'][index][pole][1]),'raw and structured reference disagree')
            denominator=max(scale,modulus(old_re,old_im))
            delta_re,delta_im=value_re-old_re,value_im-old_im
            error=modulus(delta_re,delta_im)/denominator
            real_error,imag_error=abs(delta_re)/denominator,abs(delta_im)/denominator
            record={'moment':index,'basis':basis,'rank':degree,'slot':pole,'laurent':['uv1','ir1','ir2','finite'][pole],'error':str(error),'real_error':str(real_error),'imaginary_error':str(imag_error),'failed':error>threshold,'candidate_real':slot['real'],'candidate_imaginary':slot['imaginary'],'reference_real':str(old_re),'reference_imaginary':str(old_im),'real_precision':slot['real_precision'],'imaginary_precision':slot['imaginary_precision']}
            records.append(record)
            stats=rank_stats[degree];stats['slots']+=1;stats['failed_slots']+=int(error>threshold)
            stats['maximum_error']=max(stats['maximum_error'],error);stats['maximum_real_error']=max(stats['maximum_real_error'],real_error);stats['maximum_imaginary_error']=max(stats['maximum_imaginary_error'],imag_error)
    require(len(records)==1320 and zero_poles==990,'full array count mismatch')
    failures=[x for x in records if x['failed']]
    prefix=load('validation/highpoint-thin-n6-generic/fixed/n6-rank3-128-001/result.json')
    require(prefix['working_bits']==128 and prefix['requested_bits']==53 and prefix['basis']==result['basis'][:35] and prefix['input_exact_rational']==result['input_exact_rational'],'qualified rank3 prefix context mismatch')
    prefix_max=D(0); represented_changes=precision_changes=0; prefix_failed=0
    for index,old in enumerate(prefix['lanes'][0]['moments']):
        scale=q**(sum(result['basis'][index])-8)
        for pole,old_slot in enumerate(old):
            now=moments[index][pole]
            current_re,current_im=complex_value(now);old_re,old_im=complex_value(old_slot)
            represented_changes+=int(current_re!=old_re or current_im!=old_im)
            precision_changes+=int((now['real_precision'],now['imaginary_precision'])!=(old_slot['real_precision'],old_slot['imaginary_precision']))
            denom=max(scale,modulus(decimal_fraction(old_re),decimal_fraction(old_im)))
            difference=modulus(decimal_fraction(current_re-old_re),decimal_fraction(current_im-old_im))/denom
            prefix_max=max(prefix_max,difference);prefix_failed+=int(difference>D(2)**-80)
    return {'q':str(q),'q_definition':'sqrt(max(1, |Re m_i^2|, |(p_i-p_j)^2_Minkowski|)); excludes mu','error_definition':'Euclidean |candidate-reference| / max(Q^(rank-8), Euclidean |reference|)','threshold':str(threshold),'moments':330,'complex_slots':len(records),'exact_zero_candidate_pole_slots':zero_poles,'failed_slots':len(failures),'failure_counts_by_laurent':dict(Counter(x['laurent'] for x in failures)),'maximum_error':str(max(D(x['error']) for x in records)),'first_failure':failures[0] if failures else None,'worst_failures':sorted(failures,key=lambda x:D(x['error']),reverse=True)[:20],'by_rank':rank_stats,'rank3_prefix_consistency':{'complex_slots':140,'threshold':'2^-80','maximum_difference':str(prefix_max),'threshold_failures':prefix_failed,'exact_represented_value_changes':represented_changes,'precision_metadata_changes':precision_changes,'scope':'same128-bit working precision, rank3 versus rank7 parent request; regression consistency only, not128/256 convergence'}},records


def main():
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    protocol,build,run,failed_gate=verify_metadata()
    source=verify_source_restoration()
    fixture=load('validation/public-highpoint/fixture-conditioned_masses.json')
    reference=load('validation/public-highpoint/reference-conditioned_masses.json')
    require(reference['fixture_sha256']==sha(ROOT/'validation/public-highpoint/fixture-conditioned_masses.json'),'reference fixture binding differs')
    result=load(H/'n6-rank7-128-001/result.json','717ec3e0e634add1975bd969291aab0b23c640fb0d6c41cd3307d23f96b00982')
    with localcontext() as context:
        context.prec=220
        numerical,records=analyze(result,fixture['samples'][0],reference)
    require(numerical['failed_slots']>0,'expected failed gate unexpectedly fully agrees')
    (OUT/'all-slots.json').write_text(json.dumps({'schema_version':1,'arithmetic':'Independent stdlib Fraction/Decimal at220decimal digits; exact Rational candidate strings and original raw RESULT decimal literals; no comparator import/execution/arithmetic reuse','records':records},indent=2)+'\n')
    summary={'schema_version':1,'status':'passed_independent_saved_data_audit_of_failed_numerical_gate','reviewer':'/root/guard_performance_review','started_utc':started,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'One private retained N6 rank7 base singleton Float128/request53 native Components; full saved-array failure characterization. No production qualification, performance or128/256 convergence claim. No implementation is identified as the cause of disagreement.','numerical_agreement_qualified':False,'precision_convergence_qualified':False,'kernel_build_or_test_executed_by_reviewer':False,'arithmetic':'Independent Fraction and220-digit Decimal; no f64 candidate conversion or comparator code import/reuse','source_restoration':source,'runtime':{'build_bound_seconds':90,'build_elapsed_seconds':str(build['elapsed_seconds']),'capture_bound_seconds':300,'kernel_seconds':str(run['steps'][0]['seconds']),'capture_elapsed_seconds':str(run['elapsed_seconds']),'terminal_exit_code':run['steps'][0]['exit_code'],'guards_unchanged':True},'numerical':numerical,'original_failed_comparator_status':failed_gate['status'],'checks':dict(CHECKS),'unique_bound_artifacts':len(SEEN),'input_sha256':SEEN,'script_sha256':sha(Path(__file__)),'all_slots_sha256':sha(OUT/'all-slots.json')}
    (OUT/'audit-128.json').write_text(json.dumps(summary,indent=2,default=str)+'\n')
    print(json.dumps({'audit_status':summary['status'],'numerical_agreement_qualified':False,'failed_slots':numerical['failed_slots'],'failure_counts_by_laurent':numerical['failure_counts_by_laurent'],'by_rank':numerical['by_rank'],'maximum_error':numerical['maximum_error'],'rank3_prefix_consistency':numerical['rank3_prefix_consistency'],'unique_bound_artifacts':len(SEEN),'audit_sha256':sha(OUT/'audit-128.json')},indent=2,default=str))


if __name__=='__main__':
    main()
