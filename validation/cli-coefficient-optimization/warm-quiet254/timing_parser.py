"""Fail-closed parser for the frozen coefficient CSE fixed-block protocol."""
import math, struct
from fractions import Fraction
CASES={'ggh':15,'gghh':69,'gghhh':69,'gggg-up':70}
MASK=(1<<64)-1

def ordered_first(seed):
    values=[i%2 for i in range(21)]
    for i in range(20,0,-1):
        seed^=(seed<<13)&MASK;seed^=seed>>7;seed^=(seed<<17)&MASK;seed&=MASK
        j=seed%(i+1);values[i],values[j]=values[j],values[i]
    return values

def positive_integer(value):
    return isinstance(value,int) and not isinstance(value,bool) and value>0

def validate(case,mode,raw):
    if case not in CASES or mode not in ['cse0','pair1']:raise ValueError('unexpected case/mode')
    if raw.get('case')!=case or raw.get('candidate_mode')!=mode or raw.get('status')!='passed':raise ValueError('case not complete')
    count=CASES[case]
    if raw.get('coefficient_count')!=count:raise ValueError('coefficient count changed')
    for name in ['baseline_exact_proof','candidate_exact_proof']:
        proof=raw.get(name,{})
        if proof.get('outputs_proved')!=count or proof.get('proof')!='Symbolica exact expanded differences are literal zero; no statistical zero test':raise ValueError('missing exact identity proof')
    rows=raw.get('rows',[])
    if len(rows)!=2 or [r.get('rows') for r in rows]!=[1,32]:raise ValueError('batch matrix incomplete')
    output=[]
    for row in rows:
        n=row['rows'];blocks=row.get('blocks',[])
        if row.get('status')!='passed' or len(blocks)!=21:raise ValueError('incomplete blocks')
        iterations=row.get('iterations_per_variant_per_block')
        if not positive_integer(iterations) or iterations>(1<<26):raise ValueError('invalid fixed iteration count')
        pilots=row.get('pilots',[])
        if len(pilots)!=2:raise ValueError('missing pilot pair')
        for pilot in pilots:
            if not isinstance(pilot,list) or len(pilot)!=2 or not all(positive_integer(v) for v in pilot):raise ValueError('invalid pilot')
            pilot_count,elapsed=pilot
            if pilot_count<8 or pilot_count>(1<<26) or pilot_count&(pilot_count-1) or (elapsed<2_000_000 and pilot_count!=(1<<26)):raise ValueError('pilot stop/count invalid')
        numerator=2*30_000_000*pilots[0][0]*pilots[1][0]
        denominator=pilots[0][1]*pilots[1][0]+pilots[1][1]*pilots[0][0]
        calibrated=max(1,min(1<<26,(numerator+denominator-1)//denominator))
        if iterations!=calibrated:raise ValueError('fixed count does not match pilots')
        ordering=row.get('first_variant_by_block',[])
        seed=0x8ae4_d723_f209_16c5^(list(CASES).index(case)*97)^n
        if row.get('seed')!=seed or ordering!=ordered_first(seed) or ordering.count(0)!=11 or ordering.count(1)!=10:raise ValueError('changed seed/order')
        names=row.get('parameter_names',[]);packed=row.get('packed_input_bits',[])
        if not names or len(packed)!=n*len(names) or any(len(z)!=2 or any(type(x)!=int or not 0<=x<=MASK for x in z) for z in packed):raise ValueError('invalid input layout')
        scales=row.get('dimension_scales',[])
        if len(scales)!=n*count or any(not isinstance(x,(int,float)) or not math.isfinite(x) or x<=0 for x in scales):raise ValueError('invalid dimensional scales')
        reference=row.get('reference_checks',[])
        if len(reference)!=2:raise ValueError('missing independent reference checks')
        for check in reference:
            if check.get('complex_outputs')!=n*count or check.get('dimension_metric_passed')is not True:raise ValueError('reference check incomplete')
            dimension_max=Fraction(check['dimension_normalized_max']);raw_max=Fraction(check['raw_max']);tolerance=Fraction(1,10**10)
            if dimension_max<0 or dimension_max>tolerance or raw_max<0:raise ValueError('invalid reference maxima')
            failed=check.get('raw_1e10_failed_components_retained')
            if type(failed)!=int or not 0<=failed<=2*n*count or (failed>0)!=(raw_max>tolerance):raise ValueError('raw failures hidden/inconsistent')
        expected=row.get('expected_outputs_by_variant',[]);final=row.get('final_outputs_by_variant',[])
        if len(expected)!=2 or final!=expected:raise ValueError('variant values/precision/sign changed')
        for result in expected+final:
            if result.get('rows')!=n or result.get('components')!=1 or len(result.get('values',[]))!=n*count:raise ValueError('result shape changed')
            for value in result['values']:
                for component in ['real','imaginary']:
                    number=value.get(component);bits=value.get(component+'_bits');precision=value.get(component+'_precision')
                    if type(number) not in [int,float] or not math.isfinite(number):raise ValueError('invalid output number')
                    if type(bits)!=int or not 0<=bits<=MASK:raise ValueError('missing/invalid output bits')
                    decoded=struct.unpack('>d',struct.pack('>Q',bits))[0]
                    if not math.isfinite(decoded) or struct.unpack('>Q',struct.pack('>d',number))[0]!=bits:raise ValueError('output number and bits disagree')
                    if type(precision)!=int or precision!=53:raise ValueError('binary64 output precision changed')
        timings=[[],[]]
        for i,block in enumerate(blocks):
            if block.get('block')!=i or block.get('first_variant')!=ordering[i] or block.get('iterations')!=iterations:raise ValueError('block coordinate/count changed')
            if block.get('each_variant_matches_own_exact_value_precision_signed_zero')is not True or block.get('cross_variant_dimension_metric_passed')is not True:raise ValueError('missing repeated checks')
            pair=block.get('elapsed_ns',[])
            if len(pair)!=2 or not all(positive_integer(x) for x in pair):raise ValueError('invalid elapsed pair')
            for v in range(2):timings[v].append(pair[v]/iterations)
        output.append({'case':case,'candidate_mode':mode,'batch':n,'iterations':iterations,'baseline_ns':timings[0],'candidate_ns':timings[1],'paired_elapsed_ratios':[b['elapsed_ns'][1]/b['elapsed_ns'][0]for b in blocks],'first_variant_by_block':ordering,'setup':raw['setup']|row['setup'],'reference_checks':reference,'all_own_outputs_exact_before_after':True})
    return output
