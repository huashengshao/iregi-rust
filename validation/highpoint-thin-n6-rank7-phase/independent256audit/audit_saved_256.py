#!/usr/bin/env python3
"""Independent Fraction/Decimal saved diagnostic review; no producer imports."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, localcontext
from collections import Counter
import datetime,hashlib,json
ROOT=Path.cwd().resolve();H=ROOT/'target/public-highpoint/thin-n6-rank7-phase';O=ROOT/'target/guard-performance-review/rank7-diagnostic-256-audit';D=Decimal
BINDINGS={};COUNTS=Counter()
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def check(value,message):
    COUNTS['assertions']+=1
    if not value:raise ValueError(message)
def bind(p,expected=None):
    p=Path(p);p=p if p.is_absolute() else ROOT/p;p=p.resolve();digest=sha(p)
    if expected is not None:check(digest==expected,'hash mismatch '+str(p))
    key=str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
    if key in BINDINGS:check(BINDINGS[key]==digest,'changed repeated artifact '+key)
    BINDINGS[key]=digest;COUNTS['artifact_bindings']+=1;return p
def load(p,expected=None):return json.loads(bind(p,expected).read_text(),parse_float=D)
def frac(text):
    check(isinstance(text,str),'nonstring candidate exact value');return Fraction(text)
def dec(f):return D(f.numerator)/D(f.denominator)
def norm(re,im):return (re*re+im*im).sqrt()
def number(slot):
    check(set(slot)=={'real','imaginary','real_precision','imaginary_precision'},'complex schema mismatch')
    check(all(isinstance(slot[k],int) and slot[k]>0 for k in ['real_precision','imaginary_precision']),'nonpositive precision')
    return frac(slot['real']),frac(slot['imaginary'])
def agree_report(ours,saved,label):
    # Report formatting agreement only, not a change to either physical gate.
    ours,saved=D(ours),D(saved)
    check(abs(ours-saved)<=max(abs(ours),abs(saved),D('1e-300'))*D('1e-190'),'saved report rounding mismatch '+label)

def main():
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    protocol=load(H/'diagnostic-protocol.json','3328f45c2e5f47eed881faea2dd1a2b9be4c66d5ed7c37debc1d5b8ed85bdaaa')
    run=load(H/'n6-rank7-256-diagnostic-001/run.json','ae8c57f5729a1b4991021a5056698d4db6c26bdbdeda5433a1756cc1c085e59d')
    saved=load(H/'diagnostic-comparison-128-256.json','8cda24afcb1f060b169b25ab42b4b69b4ae6613aec42360d55f6c5f0f7dba22b')
    check(protocol['status']=='approved_source_only' and protocol['acceptance_qualified'] is False,'diagnostic authorization changed')
    check(protocol['runtime_bound_seconds']==run['bound_seconds']==300 and run['elapsed_seconds']<=300,'runtime bound failed')
    check(run['status']=='passed' and run['inputs_unchanged'] and run['acceptance_qualified'] is False,'run terminal status failed')
    check(len(protocol['artifacts'])==275 and len(run['inputs'])==276 and len(saved['input_sha256'])==279,'artifact inventory size changed')
    check(len(run['steps'])==1 and run['steps'][0]['exit_code']==0 and run['steps'][0]['seconds']<=300,'kernel count/exit/bound changed')
    expected=['taskset','-c','14',str(H/'build-001/driver'),str(ROOT/'validation/public-highpoint/fixture-conditioned_masses.json'),'6','7','pv','256','53','1',str(H/'n6-rank7-256-diagnostic-001/result.json')]
    check(run['steps'][0]['command']==expected,'kernel command changed')
    for record,key in [(protocol,'artifacts'),(run,'inputs'),(saved,'input_sha256')]:
        for path,digest in record[key].items():bind(path,digest)
    for name,digest in run['outputs'].items():bind(H/'n6-rank7-256-diagnostic-001'/name,digest)
    check(set(run['inputs'])=={str((ROOT/p).resolve()) for p in protocol['artifacts']}|{str(H/'diagnostic-protocol.json')},'runtime/protocol closure differs')
    for flag in ['acceptance_qualified','full_array_original_agreement_qualified','precision_convergence_qualified','lifecycle_qualified','performance_qualified']:
        check(saved[flag] is False,'diagnostic promoted '+flag)
    check(saved['status']=='completed_diagnostic' and saved['diagnostic_only'] is True and saved['prior_acceptance_status']=='failed','failed original acceptance disappeared')
    failed=load(H/'comparison-128.json','ad2fb606dd473a901f0c13192edf02b66c2cb14155dc2592524a4cc89218eb02')
    check(failed['status']=='failed' and failed['full_array_original_agreement_qualified'] is False,'original128 failure changed')
    a=load(H/'n6-rank7-128-001/result.json','717ec3e0e634add1975bd969291aab0b23c640fb0d6c41cd3307d23f96b00982')
    b=load(H/'n6-rank7-256-diagnostic-001/result.json','593232f7aa8403d9f713a6ac1c8a7db8ce73bccd72cb8ba385ee995a0a1b599f')
    oldaudit=load('target/guard-performance-review/rank7-audit/audit-128.json','9fd8f76748730315304c8eebfe59950f894e2a265f31d9505e8bf4b0d954f78e')
    phase=load('target/guard-performance-review/rank7-audit/phase-zero-diagnostics.json','fb1cdf7a4970bb6cf9f477aa36616704d225291caefe3174113ad369754d1746')
    check(phase['phase_zero_premise_verified'] and phase['positive_F_lower_bound']=='15/16','phase premise binding failed')
    check(oldaudit['source_restoration']['restored_files']==36 and oldaudit['source_restoration']['removed_diagnostic_lines']==29,'source restoration context changed')
    expected_settings={'algorithm':'PassarinoVeltman','convention':'IregiNative','dimension_shift':0,'input_policy':'Preserve','invariants':'FromShifts','powers':[1]*6,'propagators':6,'rank':7,'tensor_weights':'Components'}
    basis=[]
    for rank in range(8):
        for t in range(rank,-1,-1):
            for x in range(rank-t,-1,-1):
                for y in range(rank-t-x,-1,-1):basis.append([t,x,y,rank-t-x-y])
    check(len(basis)==330,'independent basis count wrong')
    fixture=load('validation/public-highpoint/fixture-conditioned_masses.json');sample=fixture['samples'][0];props=sample['propagators'][:6]
    expected_input=[[Fraction(v),Fraction(0)] for p in props for v in p['shift']]+[[Fraction(v) for v in p['mass_squared']] for p in props]+[[Fraction(sample['mu']),Fraction(0)]]
    q2=max([Fraction(1)]+[abs(Fraction(p['mass_squared'][0])) for p in props]+[abs((Fraction(p['shift'][0])-Fraction(q['shift'][0]))**2-sum(((Fraction(p['shift'][k])-Fraction(q['shift'][k]))**2 for k in range(1,4)),Fraction(0))) for p in props for q in props])
    check(q2==4,'Q squared changed')
    for bits,result in [(128,a),(256,b)]:
        check(result['settings']==expected_settings and result['basis']==basis,'settings/order changed')
        check(result['working_bits']==bits and result['requested_bits']==53 and result['components']==1 and result['rows']==1,'precision/shape changed')
        check(result['status']=='all_lanes_success' and result['lane_statuses']==['Success'] and result['fallback_used']==[True] and result['analytic_used']==[True],'lane status changed')
        check(len(result['lanes'])==1 and result['lanes'][0]['status']=='Success' and result['lanes'][0]['row']==0,'lane ledger changed')
        check([[Fraction(v) for v in pair] for pair in result['input_exact_rational'][0]]==expected_input and len(result['input_exact_rational'])==1,'exact inputs changed')
        check(len(result['lanes'][0]['moments'])==330 and all(len(m)==4 for m in result['lanes'][0]['moments']),'incomplete moments')
        check(result['execution']['packed_child_rows']==6 and result['execution']['packed_parent_rows']==1 and result['execution']['child_batch_calls']==1 and result['execution']['parent_batch_calls']==1,'batch trace changed')
    reference=load('validation/public-highpoint/reference-conditioned_masses.json');refs={}
    for mode in [0,1,2]:
        case=next(c for c in reference['cases'] if c['id']==f'n6_base_mode{mode}')
        check(case['rank']==7 and case['propagators']==6 and case['mode']==mode and case['exit_code']==0 and case['status']=='captured','reference metadata changed')
        wire=case['request'].splitlines();head=wire[0].split();check(head==['EVAL',f'n6_base_mode{mode}','tensor',str(mode),'6','7','0','3','0','1e-6'] and len(wire)==8 and wire[-1]=='QUIT','reference wire changed')
        for line,p in zip(wire[1:-1],props):check([Fraction(v) for v in line.split()]==[Fraction(v) for v in p['shift']+p['mass_squared']]+[Fraction(1)],'reference inputs differ')
        raw=[line[7:] for line in case['stdout'].splitlines() if line.startswith('RESULT ')];check(len(raw)==1,'ambiguous reference RESULT')
        parsed=json.loads(raw[0],parse_float=D);check(len(parsed['moments'])==330 and parsed['poles']==['uv1','ir1','ir2','finite'] and parsed['stable'] is (mode!=1),'reference arrays/stability changed')
        refs[mode]=parsed
    slot_records=[];mode_summary={};precision_by_rank={};phase_summary={128:{'maximum':D(0),'failures':0},256:{'maximum':D(0),'failures':0}};poles={128:0,256:0};precision_max=D(0);precision_fail=0
    with localcontext() as ctx:
        ctx.prec=240
        for i,monomial in enumerate(basis):
            rank=sum(monomial);scale=D(2)**(rank-8)
            pr=precision_by_rank.setdefault(rank,{'slots':0,'failures':0,'maximum':D(0)})
            for pole in range(4):
                numbers={bits:number(result['lanes'][0]['moments'][i][pole]) for bits,result in [(128,a),(256,b)]}
                low_re,low_im=numbers[128];hi_re,hi_im=numbers[256]
                high_norm=norm(dec(hi_re),dec(hi_im));precision_error=norm(dec(low_re-hi_re),dec(low_im-hi_im))/max(scale,high_norm)
                precision_max=max(precision_max,precision_error);precision_fail+=int(precision_error>D(2)**-80);pr['slots']+=1;pr['failures']+=int(precision_error>D(2)**-80);pr['maximum']=max(pr['maximum'],precision_error)
                row={'moment':i,'basis':monomial,'rank':rank,'slot':pole,'precision_difference':str(precision_error),'phase_zero':{},'original_errors':{}}
                for bits in [128,256]:
                    re,im=numbers[bits]
                    if pole<3:check(re==0 and im==0,'nonzero candidate pole');poles[bits]+=1
                    residual=abs(dec(re))/scale;phase_summary[bits]['maximum']=max(phase_summary[bits]['maximum'],residual);phase_summary[bits]['failures']+=int(residual>D('1e-10'));row['phase_zero'][bits]=str(residual)
                    row['original_errors'][bits]={}
                    for mode in [0,1,2]:
                        old_re,old_im=map(D,refs[mode]['moments'][i][pole]);check(old_re.is_finite() and old_im.is_finite(),'nonfinite reference')
                        error=norm(dec(re)-old_re,dec(im)-old_im)/max(scale,norm(old_re,old_im))
                        stats=mode_summary.setdefault((bits,mode),{'slots':0,'failures':0,'maximum':D(0),'failures_by_rank':Counter(),'by_rank':{}});stats['slots']+=1;stats['maximum']=max(stats['maximum'],error)
                        rankrow=stats['by_rank'].setdefault(rank,{'slots':0,'failures':0,'maximum':D(0)});rankrow['slots']+=1;rankrow['maximum']=max(rankrow['maximum'],error)
                        if error>D('1e-10'):stats['failures']+=1;stats['failures_by_rank'][rank]+=1;rankrow['failures']+=1
                        row['original_errors'][bits][mode]=str(error)
                slot_records.append(row)
        check(len(slot_records)==1320 and all(v==990 for v in poles.values()),'full comparison/pole count mismatch')
        check(precision_fail==0,'precision diagnostic exceeds unchanged2^-80 threshold')
        agree_report(precision_max,saved['precision_comparison']['maximum_normalized_error'],'precision maximum')
        for rank,row in precision_by_rank.items():
            recorded=saved['precision_comparison']['by_rank'][str(rank)];check(row['slots']==recorded['compared_complex_slots'] and row['failures']==recorded['failures'],'precision rank count differs');agree_report(row['maximum'],recorded['maximum_normalized_error'],'precision rank'+str(rank))
        mode_rows=[]
        for (bits,mode),row in sorted(mode_summary.items()):
            recorded=next(x for x in saved['original_mode_comparisons'] if x['working_bits']==bits and x['original_mode']==mode)
            check(row['slots']==recorded['compared_complex_slots']==1320 and row['failures']==recorded['failures'],'original mode count differs');agree_report(row['maximum'],recorded['maximum_normalized_error'],'mode maximum')
            for rank,rankrow in row['by_rank'].items():
                rr=recorded['by_rank'][str(rank)];check(rankrow['slots']==rr['compared_complex_slots'] and rankrow['failures']==rr['failures'],'original rank count differs');agree_report(rankrow['maximum'],rr['maximum_normalized_error'],'original rank maximum')
            mode_rows.append({'working_bits':bits,'mode':mode,'reference_stable':refs[mode]['stable'],**row})
        for bits,row in phase_summary.items():
            recorded=next(x for x in saved['analytic_real_zero_diagnostics']['records'] if x['working_bits']==bits);check(row['failures']==recorded['failures']==0,'phase residual gate differs');agree_report(row['maximum'],recorded['maximum_normalized_error'],'phase maximum')
        oracle=[]
        for order in [8,12,16,20]:
            for mapping in [0,1]:
                path=ROOT/f'validation/public-highpoint/simplex-n6-order{order}-map{mapping}.json'
                if not path.exists():continue
                quad=load(path);check(quad['fixture_sha256']==sha(ROOT/'validation/public-highpoint/fixture-conditioned_masses.json'),'quadrature fixture differs')
                for estimate in quad['results']:
                    index=estimate['moment_index'];check(estimate['monomial']==basis[index],'quadrature basis differs');scale=D(2)**(sum(basis[index])-8);center=estimate['native_finite_imaginary']
                    for bits,result in [(128,a),(256,b)]:
                        re,im=number(result['lanes'][0]['moments'][index][3]);error=norm(dec(re),dec(im)-center)/max(scale,abs(center))
                        recorded=next(x for x in saved['saved_parameter_oracle']['comparisons'] if x['working_bits']==bits and x['moment']==index and x['order']==order and x['mapping']==mapping);agree_report(error,recorded['normalized_error'],'quadrature error');check((error<=D('1e-10'))==recorded['observed_within_tolerance'],'quadrature observed flag differs')
                        oracle.append({'bits':bits,'moment':index,'order':order,'mapping':mapping,'error':str(error),'within_1e_minus_10':error<=D('1e-10'),'scope':'saved quadrature estimate only, no rigorous bound or acceptance upgrade'})
        check(len(oracle)==28,'saved quadrature comparison count differs')
    (O/'all-slots.json').write_text(json.dumps({'schema_version':1,'records':slot_records},indent=2)+'\n')
    summary={'schema_version':1,'status':'passed_independent_saved_data_diagnostic_audit','reviewer':'/root/guard_performance_review','started_utc':started,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'arithmetic':'Independent exact Fraction and240-digit Decimal, raworiginalRESULTdecimal literals; no producer/comparator import/read/arithmetic reuse or f64 candidate conversion. Saved report roundingcheckedat190significantdigits separately from physical thresholds.','scope':'Same retained private N6rank7base singleton, working128/256/request53, unchangednativeComponents. Original128acceptancefailed and cannot beupgraded by thisdiagnostic. No fullimaginaryaccuracy, lifecycle, generaldomain, productionadoption or performancequalification.','kernel_build_test_or_quadrature_executed_by_reviewer':False,'acceptance_qualified':False,'full_array_original_agreement_qualified':False,'precision_convergence_qualified':False,'precision_diagnostic_observed_passed':precision_fail==0,'imaginary_accuracy_qualified':False,'precision':{'complex_slots':1320,'threshold':'2^-80','failures':precision_fail,'maximum':str(precision_max),'by_rank':precision_by_rank},'exact_zero_poles_by_working_bits':poles,'phase_zero':phase_summary,'original_modes':mode_rows,'saved_oracle_comparisons':oracle,'prior_failed_gate_sha256':'ad2fb606dd473a901f0c13192edf02b66c2cb14155dc2592524a4cc89218eb02','protocol_sha256':'3328f45c2e5f47eed881faea2dd1a2b9be4c66d5ed7c37debc1d5b8ed85bdaaa','runtime':{'kernel_seconds':str(run['steps'][0]['seconds']),'guarded_seconds':str(run['elapsed_seconds']),'bound_seconds':300,'inputs_unchanged':True},'checked_counts':dict(COUNTS),'unique_bound_artifacts':len(BINDINGS),'input_sha256':BINDINGS,'script_sha256':sha(Path(__file__)),'all_slots_sha256':sha(O/'all-slots.json')}
    (O/'audit.json').write_text(json.dumps(summary,indent=2,default=str)+'\n')
    print(json.dumps({'status':summary['status'],'acceptance_qualified':False,'precision_diagnostic_passed':True,'precision_maximum':str(precision_max),'phase_zero':phase_summary,'mode_failures':[{'bits':x['working_bits'],'mode':x['mode'],'stable':x['reference_stable'],'failures':x['failures']} for x in mode_rows],'exact_zero_poles':poles,'unique_bound_artifacts':len(BINDINGS),'audit_sha256':sha(O/'audit.json')},indent=2,default=str))

if __name__=='__main__':main()
