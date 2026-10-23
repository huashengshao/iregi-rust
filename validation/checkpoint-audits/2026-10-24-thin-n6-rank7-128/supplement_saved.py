#!/usr/bin/env python3
"""Saved modes and quadrature only; no imports/launches of numerical producers."""
from pathlib import Path
from decimal import Decimal, localcontext
from fractions import Fraction
from collections import Counter
import hashlib, json, datetime

ROOT=Path.cwd().resolve()
HERE=ROOT/'target/guard-performance-review/rank7-audit'
D=Decimal
bindings={}
def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def bind(path,expected=None):
    p=Path(path)
    if not p.is_absolute():p=ROOT/p
    actual=digest(p)
    if expected is not None:assert actual==expected,(str(p),actual,expected)
    bindings[str(p.relative_to(ROOT))]=actual
    return p
def load(path):return json.loads(bind(path).read_text(),parse_float=D)
def dec(value):
    if isinstance(value,Fraction):return D(value.numerator)/D(value.denominator)
    return D(value)
def mag(re,im):return (re*re+im*im).sqrt()
def native(slot):return dec(Fraction(slot['real'])),dec(Fraction(slot['imaginary']))
def response(case):
    raw=[x[7:] for x in case['stdout'].splitlines() if x.startswith('RESULT ')]
    assert len(raw)==1
    parsed=json.loads(raw[0],parse_float=D)
    assert parsed['poles']==['uv1','ir1','ir2','finite'] and len(parsed['moments'])==330
    return parsed

def main():
    result=load('target/public-highpoint/thin-n6-rank7-phase/n6-rank7-128-001/result.json')
    audit=load(HERE/'audit-128.json')
    assert audit['status']=='passed_independent_saved_data_audit_of_failed_numerical_gate'
    reference=load('validation/public-highpoint/reference-conditioned_masses.json')
    fixture=load('validation/public-highpoint/fixture-conditioned_masses.json')
    assert reference['fixture_sha256']==digest(ROOT/'validation/public-highpoint/fixture-conditioned_masses.json')
    modes=[]
    with localcontext() as ctx:
        ctx.prec=220
        for mode in [0,1,2]:
            case=next(c for c in reference['cases'] if c['id']==f'n6_base_mode{mode}')
            assert case['exit_code']==0 and case['rank']==7 and case['mode']==mode
            parsed=response(case)
            assert parsed['stable'] is (mode!=1)
            rank_rows={};failures=[]
            for i,(basis,candidate,old) in enumerate(zip(result['basis'],result['lanes'][0]['moments'],parsed['moments'])):
                rank=sum(basis);scale=D(2)**(rank-8)
                stats=rank_rows.setdefault(rank,{'complex_slots':0,'failed_slots':0,'maximum_error':D(0)})
                for pole,(value,pair) in enumerate(zip(candidate,old)):
                    re,im=native(value);ore,oim=map(D,pair)
                    assert ore.is_finite() and oim.is_finite()
                    denominator=max(scale,mag(ore,oim))
                    error=mag(re-ore,im-oim)/denominator
                    stats['complex_slots']+=1;stats['maximum_error']=max(stats['maximum_error'],error)
                    if error>D('1e-10'):
                        stats['failed_slots']+=1
                        failures.append({'moment':i,'basis':basis,'rank':rank,'slot':pole,'error':str(error)})
            modes.append({'mode':mode,'method':{0:'IBP',1:'PV',2:'Hybrid'}[mode],'reference_stable':parsed['stable'],'qualification':'diagnostic only; unstable reference excluded from acceptance' if not parsed['stable'] else 'saved stable reference diagnostics; original all-slot failed gate remains unchanged','complex_slots':1320,'failed_slots_at_1e_minus_10':len(failures),'failures_by_rank':dict(Counter(x['rank'] for x in failures)),'failures_by_laurent_slot':dict(Counter(x['slot'] for x in failures)),'by_rank':rank_rows,'worst':max(failures,key=lambda x:D(x['error'])) if failures else None})
        estimates={};quadrature_context=[]
        for order in [8,12,16,20]:
            for mapping in [0,1]:
                path=ROOT/f'validation/public-highpoint/simplex-n6-order{order}-map{mapping}.json'
                value=load(path)
                assert value['status']=='fixed_rule_evaluated' and value['n']==6 and value['order']==order and value['mapping']==mapping
                assert value['fixture_sha256']==digest(ROOT/'validation/public-highpoint/fixture-conditioned_masses.json')
                bind('validation/public-highpoint/simplex_oracle.py',value['script_sha256'])
                bind(value['existing_rank7_integrand_source'],value['existing_rank7_integrand_sha256'])
                assert value['points_evaluated']==order**5 and value['minimum_observed_F']>=D(15)/16
                assert len(value['results'])==2
                for row in value['results']:
                    index=row['moment_index'];assert row['monomial']==result['basis'][index]
                    estimates[(order,mapping,index)]=row['native_finite_imaginary']
                quadrature_context.append({'order':order,'mapping':mapping,'points':value['points_evaluated'],'minimum_observed_F':str(value['minimum_observed_F']),'rule_volume':str(value['simplex_volume_from_rule'])})
        summary=load('validation/public-highpoint/simplex-summary.json')
        assert summary['fixture_sha256']==digest(ROOT/'validation/public-highpoint/fixture-conditioned_masses.json') and summary['reference_sha256']==digest(ROOT/'validation/public-highpoint/reference-conditioned_masses.json')
        # Verify retained summary inputs without executing its producer.
        for path,expected in summary['input_hashes'].items():bind(path,expected)
        witnesses=[]
        for index in [0,321]:
            basis=result['basis'][index];rank=sum(basis);scale=D(2)**(rank-8)
            center=estimates[(20,1,index)]
            latest=[estimates[(order,mapping,index)] for order in [16,20] for mapping in [0,1]]
            spread=max(latest)-min(latest)
            max_center_deviation=max(abs(x-center) for x in latest)
            denominator=max(scale,abs(center))
            re,im=native(result['lanes'][0]['moments'][index][3])
            comparisons=[]
            for mode in [0,1,2]:
                parsed=response(next(c for c in reference['cases'] if c['id']==f'n6_base_mode{mode}'))
                ore,oim=map(D,parsed['moments'][index][3])
                comparisons.append({'mode':mode,'reference_stable':parsed['stable'],'complex_difference_to_estimate_normalized':str(mag(ore,oim-center)/denominator),'real_component':str(ore),'imaginary_component':str(oim),'unstable_is_qualified':False})
            witnesses.append({'moment':index,'basis':basis,'rank':rank,'estimate_center_order20_map1':str(center),'latest_four_spread_native':str(spread),'latest_four_max_center_deviation_native':str(max_center_deviation),'latest_four_max_center_deviation_normalized':str(max_center_deviation/denominator),'candidate_complex_difference_to_estimate_normalized':str(mag(re,im-center)/denominator),'candidate_real':str(re),'candidate_imaginary':str(im),'saved_order_mapping_estimates':[{'order':order,'mapping':mapping,'value':str(estimates[(order,mapping,index)])} for order in [8,12,16,20] for mapping in [0,1]],'original_mode_comparisons':comparisons})
    record={'schema_version':1,'status':'completed_saved_data_diagnostics_only','reviewer':'/root/guard_performance_review','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kernel_build_test_or_quadrature_execution':False,'numerical_agreement_qualified':False,'precision_convergence_qualified':False,'qualification':'All modes and all existing quadrature orders/maps remain visible. Unstable original PV is never accepted. Only scalar and moment321 have quadrature estimates, with empirical order/map differences rather than rigorous interval bounds. These two witnesses cannot replace the failed1320-slot gate or identify the cause of disagreement.','arithmetic':'220-digit Decimal and exact candidate Fraction values; no producer/comparator imports, SciPy execution or f64 candidate conversion','mode_comparisons':modes,'quadrature_context':quadrature_context,'quadrature_witnesses':witnesses,'input_sha256':bindings,'script_sha256':digest(Path(__file__))}
    (HERE/'supplemental-diagnostics.json').write_text(json.dumps(record,indent=2,default=str)+'\n')
    print(json.dumps({'status':record['status'],'modes':[{'mode':m['mode'],'stable':m['reference_stable'],'failed_slots':m['failed_slots_at_1e_minus_10'],'max':max(str(row['maximum_error']) for row in m['by_rank'].values())} for m in modes],'witnesses':[{'moment':w['moment'],'candidate_error':w['candidate_complex_difference_to_estimate_normalized'],'estimated_center_deviation':w['latest_four_max_center_deviation_normalized']} for w in witnesses],'sha256':digest(HERE/'supplemental-diagnostics.json')},indent=2))

if __name__=='__main__':main()
