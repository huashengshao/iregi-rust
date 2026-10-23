#!/usr/bin/env python3
"""Saved represented real-part residuals against an independently proved zero."""
from pathlib import Path
from decimal import Decimal, localcontext
from fractions import Fraction
from collections import Counter
import hashlib,json,datetime
ROOT=Path.cwd().resolve();HERE=ROOT/'target/guard-performance-review/rank7-audit';D=Decimal
inputs={}
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(p):
    p=Path(p);p=p if p.is_absolute() else ROOT/p
    inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
    return json.loads(p.read_text(),parse_float=D)
def bind(p):
    p=Path(p);p=p if p.is_absolute() else ROOT/p
    inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
def dec(frac):return D(frac.numerator)/D(frac.denominator)
def mag(re,im):return (re*re+im*im).sqrt()

def main():
    fixture=load('validation/public-highpoint/fixture-conditioned_masses.json');sample=fixture['samples'][0]
    propagators=sample['propagators'][:6]
    masses=[Fraction(p['mass_squared'][0]) for p in propagators]
    times=[Fraction(p['shift'][0]) for p in propagators]
    assert min(masses)==1 and min(times)==0 and max(times)==Fraction(1,2)
    assert all(Fraction(p['mass_squared'][1])==0 and p['power']==1 for p in propagators)
    assert Fraction(sample['mu'])>0
    bound=min(masses)-(max(times)-min(times))**2/4
    assert bound==Fraction(15,16)
    result=load('target/public-highpoint/thin-n6-rank7-phase/n6-rank7-128-001/result.json')
    assert result['settings']['convention']=='IregiNative' and result['settings']['tensor_weights']=='Components' and result['settings']['dimension_shift']==0 and result['settings']['powers']==[1]*6
    reference=load('validation/public-highpoint/reference-conditioned_masses.json')
    primary=load(HERE/'audit-128.json');all_slots=load(HERE/'all-slots.json')
    assert primary['numerical_agreement_qualified'] is False
    failed={(r['moment'],r['slot']) for r in all_slots['records'] if r['failed']}
    proof_sources=['docs/conventions.typ','validation/reference/driver.f90','validation/public-highpoint/simplex_oracle.py','validation/pv-high-rank/sixpoint_simplex_oracle.py','target/public-highpoint/thin-n6-rank7-phase/core/crates/iregi-rust/src/convention.rs','target/public-highpoint/thin-n6-rank7-phase/core/crates/iregi-rust/src/types.rs','../references/madgraph/vendor/IREGI/src/mis_warp.f90','../references/madgraph/vendor/IREGI/src/IREGI4ML5_interface.f90']
    for p in proof_sources:bind(p)
    bind(HERE/'phase-zero-proof.md')
    records=[];summaries=[]
    with localcontext() as ctx:
        ctx.prec=220
        for backend in ['TIRust128','IREGI_IBP','IREGI_PV','IREGI_Hybrid']:
            if backend=='TIRust128':
                stable=True;source='candidate';moments=result['lanes'][0]['moments']
            else:
                mode={'IREGI_IBP':0,'IREGI_PV':1,'IREGI_Hybrid':2}[backend]
                case=next(c for c in reference['cases'] if c['id']==f'n6_base_mode{mode}')
                raw=[l[7:] for l in case['stdout'].splitlines() if l.startswith('RESULT ')]
                assert len(raw)==1
                old=json.loads(raw[0],parse_float=D);stable=old['stable'];source='reference';moments=old['moments']
            rankrows={};fail_count=0;maximum=D(0);worst=None;zero=0;matched_fail_count=0
            for i,(basis,moment) in enumerate(zip(result['basis'],moments)):
                rank=sum(basis);scale=D(2)**(rank-8)
                stats=rankrows.setdefault(rank,{'complex_slots':0,'real_zero_identity_failures':0,'maximum_dimensionally_normalized_real_residual':D(0),'maximum_raw_real_magnitude':D(0)})
                for pole,value in enumerate(moment):
                    re=dec(Fraction(value['real'])) if source=='candidate' else D(value[0])
                    assert re.is_finite()
                    residual=abs(re)/scale
                    stats['complex_slots']+=1;stats['real_zero_identity_failures']+=int(residual>D('1e-10'))
                    stats['maximum_dimensionally_normalized_real_residual']=max(stats['maximum_dimensionally_normalized_real_residual'],residual)
                    stats['maximum_raw_real_magnitude']=max(stats['maximum_raw_real_magnitude'],abs(re))
                    zero+=int(re==0);fail_count+=int(residual>D('1e-10'))
                    original=all_slots['records'][4*i+pole]
                    assert original['moment']==i and original['slot']==pole
                    common=max(scale,mag(D(original['reference_real']),D(original['reference_imaginary'])))
                    common_residual=abs(re)/common
                    if backend=='IREGI_IBP' and (i,pole) in failed and common_residual>D('1e-10'):matched_fail_count+=1
                    row={'backend':backend,'moment':i,'basis':basis,'rank':rank,'slot':pole,'represented_real':str(re),'dimensionally_normalized_real_residual':str(residual),'original_gate_normalized_real_residual':str(common_residual),'zero_identity_failure_at_1e_minus_10':residual>D('1e-10')}
                    records.append(row)
                    if residual>maximum:maximum=residual;worst=row
            summaries.append({'backend':backend,'reported_stable':stable,'complex_slots':1320,'exact_zero_real_parts':zero,'real_zero_identity_failures_at_1e_minus_10':fail_count,'maximum_dimensionally_normalized_real_residual':str(maximum),'worst':worst,'by_rank':rankrows,'original_full_array_failed_slots_explained_by_reference_real_residual_alone':matched_fail_count if backend=='IREGI_IBP' else None,'qualification':'unstable original PV remains unqualified' if not stable else 'additional real-zero identity only; imaginary accuracy and original failed full-array gate unchanged'})
    (HERE/'phase-zero-all-slots.json').write_text(json.dumps({'schema_version':1,'records':records},indent=2)+'\n')
    summary={'schema_version':1,'status':'completed_independent_analytic_phase_zero_and_saved_data_diagnostics','reviewer':'/root/guard_performance_review','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase_zero_premise_verified':True,'positive_F_lower_bound':str(bound),'Q':'2','zero_identity_error_definition':'abs(Re output)/Q^(rank-8)','original_gate_real_error_definition':'abs(Re output)/max(Q^(rank-8),abs(original_IBP_complex_output))','threshold':'1e-10','kernel_build_test_or_algebra_execution':False,'numerical_agreement_qualified':False,'precision_convergence_qualified':False,'imaginary_accuracy_qualified':False,'causal_cache_bug_inferred':False,'limitations':'Analytic real-zero identity in the retained real positive-F ordinary domain only. No general complex-mass/threshold/physical-cut claim. Additional real-part accuracy information does not replace the failed complete-array gate or certify imaginary components. Original PV remains explicitly unstable.','backend_summaries':summaries,'input_sha256':inputs,'script_sha256':sha(Path(__file__)),'all_slot_residuals_sha256':sha(HERE/'phase-zero-all-slots.json'),'primary_sources':[{'title':'Alwall et al. Appendix C.1 EqC.1','url':'https://arxiv.org/html/1405.0301v2#A3.SS1'},{'title':'Bern,Dixon,Kosower Eqs3–6','url':'https://cds.cern.ch/record/247616/files/9212308.pdf'}]}
    (HERE/'phase-zero-diagnostics.json').write_text(json.dumps(summary,indent=2,default=str)+'\n')
    print(json.dumps({'status':summary['status'],'phase_zero_premise_verified':True,'positive_F_lower_bound':str(bound),'summaries':[{'backend':r['backend'],'stable':r['reported_stable'],'failed_zero_identities':r['real_zero_identity_failures_at_1e_minus_10'],'maximum':r['maximum_dimensionally_normalized_real_residual'],'failed_IBP_slots_above_reference_real_threshold_alone':r['original_full_array_failed_slots_explained_by_reference_real_residual_alone']} for r in summaries],'sha256':sha(HERE/'phase-zero-diagnostics.json')},indent=2))

if __name__=='__main__':main()
