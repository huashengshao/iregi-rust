"""Frozen qualification checks reused by the timing runner; no process side effects."""
from pathlib import Path
from fractions import Fraction
import importlib.util,json,math,struct
ROOT=Path.cwd()
helper=ROOT/'validation/benchmark/run.py'
spec=importlib.util.spec_from_file_location('selected_timing_helper',helper)
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
def finite_complex(value):
    assert type(value) is list and len(value)==2
    for x in value:
        assert type(x) is dict and x['finite'] is True and type(x['precision']) is int and x['precision']==53 and type(x['negative_sign']) is bool
        assert type(x['rational']) is str
    result=[]
    for x in value:
        exact=Fraction(x['rational']); f=float(exact)
        assert math.isfinite(f) and Fraction.from_float(f)==exact,'not an exact represented binary64 value'
        if exact:assert (exact<0)==x['negative_sign']
        else:f=math.copysign(0.,-1. if x['negative_sign'] else 1.)
        result.append(f)
    assert all(math.isfinite(x) for x in result)
    return complex(*result)

def master_compare(base, selected, n, rank, batch):
    groups={(2,0):[('B0',batch)],(2,1):[('B0',batch),('A0',2*batch)],(3,0):[('C0',batch)],(3,1):[('C0',batch),('B0',3*batch)]}[(n,rank)]
    a=base['master_captures'];b=selected['master_captures'];assert len(a)==len(b)==len(groups)
    outputs=0;worst=0.;differences=0
    for x,y,(family,rows) in zip(a,b,groups):
        for field in ['family','components','rows','requests','valid_lanes','input','output_order','errors','whole_batch_error']:assert x[field]==y[field],field
        assert x['family']==family and x['rows']==rows and x['components']==1
        assert x['backend']=='SymbolicaBatch' and y['backend']=='RustBatch'
        assert x['whole_batch_error'] is None and x['errors']==[None]*rows
        assert x['valid_lanes']==list(range(batch))
        assert x['requests']==sorted(x['requests']) and len(x['requests'])==rows
        leaves={('B0',2,0):[0],('B0',2,1):[0],('A0',2,1):[1,2],('C0',3,0):[0],('C0',3,1):[0],('B0',3,1):[1,2,3]}[(family,n,rank)]
        assert x['requests']==[[leaf,lane] for leaf in leaves for lane in range(batch)]
        assert x['output_order']==['finite','total_single','ir_double','uv_single','ir_single','derivative_discriminant']
        arity={'A0':2,'B0':4,'C0':7}[family]
        assert len(x['input'])==arity*rows and len(x['output'])==len(y['output'])==rows
        inputs=[finite_complex(z) for z in x['input']]
        for lane,(xa,ya) in enumerate(zip(x['output'],y['output'])):
            assert len(xa)==len(ya)==6
            squared=max(1.,*(abs(z) for z in inputs[lane*arity:(lane+1)*arity]))
            unit={'A0':squared,'B0':1.,'C0':1./squared}[family]
            assert math.isfinite(squared) and squared>0 and math.isfinite(unit) and unit>0
            for coefficient,(za,zb) in enumerate(zip(xa,ya)):
                va=finite_complex(za);vb=finite_complex(zb)
                denominator=(1. if coefficient==5 else unit)+abs(va)
                assert math.isfinite(denominator) and denominator>0
                error=abs(vb-va)/denominator
                assert math.isfinite(error) and error<=1e-10,(family,lane,coefficient,error)
                worst=max(worst,error);outputs+=1
                differences+=sum(aa!=bb for aa,bb in zip(za,zb))
    return {'status':'passed','master_groups':len(groups),'master_rows':sum(g[1] for g in groups),'complex_outputs':outputs,'max_normalized_error':worst,'represented_component_differences':differences}

def validate_response(response,case,samples):
    base=response['baseline'];selected=response['candidate'];batch=len(samples)
    assert response['id']==case['id']
    assert base['private_selected_native'] is False and selected['private_selected_native'] is True
    for value in [base,selected]:
        assert value['id']==case['id'] and value['n']==case['n'] and value['rank']==case['rank'] and value['batch']==batch and value['stable'] is True
        assert value['degrees']==h.degrees(case['rank']) and len(value['lanes'])==batch
        for lane in value['lanes']:
            assert lane['status']=='success' and lane['fallback_used'] is False and lane['analytic_used'] is False
            assert len(lane['represented'])==4*len(value['degrees'])
            numeric=[z for moment in lane['moments'] for z in moment]
            assert len(numeric)==len(lane['represented'])
            for z,actual in zip(lane['represented'],numeric):
                represented=finite_complex(z)
                assert type(actual) is list and len(actual)==2
                for lhs,rhs in zip([represented.real,represented.imag],actual):
                    assert type(rhs) in [int,float] and math.isfinite(rhs)
                    assert struct.pack('>d',lhs)==struct.pack('>d',rhs),'reported value and represented value differ'
    for field in ['degrees','diagnostics','execution']:assert base[field]==selected[field],field
    assert base['execution']['fallback_rows']==base['execution']['analytic_rows']==0
    cross=h.compare(selected,base,case,samples);assert cross['status']=='passed',cross
    masters=master_compare(base,selected,case['n'],case['rank'],batch)
    assert base['execution']['master_family_batches']==masters['master_groups'] and base['execution']['master_rows']==masters['master_rows']
    return {'whole_cross_backend':cross,'masters':masters}

def canonical(response):
    # Reuse metadata differs once a workspace has been prepared; numerical data cannot.
    result=json.loads(json.dumps(response))
    for backend in ['baseline','candidate']:result[backend].pop('plan_reused',None)
    return result


def validate_timed(response,expected,engine,iterations,case,samples):
    assert engine in ['baseline','candidate']
    assert response['stable'] is True
    for field in ['id','n','rank','batch','degrees','lanes','diagnostics','execution','private_selected_native']:
        # JSON spelling preserves floating signed zero as well as exact representation metadata.
        assert json.dumps(response[field],sort_keys=True)==json.dumps(expected[field],sort_keys=True),field
    assert response['capture_enabled'] is False and response['profiling_enabled'] is False
    assert response['master_captures']==[] and response['iterations']==iterations
    elapsed=response['elapsed_ns'];total=response['total_ns']
    assert type(elapsed) is list and len(elapsed)==1 and type(elapsed[0]) is int and elapsed[0]>0
    assert type(total) is list and len(total)==1 and type(total[0]) in [int,float] and math.isfinite(total[0]) and total[0]>0
    assert total[0]==elapsed[0]/iterations
    assert h.compare(response,expected,case,samples)['status']=='passed'
    return elapsed[0]

def validate_reference(response,expected,iterations,case,samples):
    assert response['stable'] is True and response['id']==case['id']
    for field in ['id','lanes','clock_ticks_per_second']:
        assert json.dumps(response[field],sort_keys=True)==json.dumps(expected[field],sort_keys=True),field
    total=response['total_ns']
    assert type(total) is list and len(total)==1 and type(total[0]) in [int,float] and math.isfinite(total[0]) and total[0]>0
    assert h.compare(response,expected,case,samples)['status']=='passed'
    return total[0]*iterations

def validate_controls(response,inventory):
    assert response['id']=='controls' and response['status']=='passed'
    c=response['controls'];expected=inventory['controls']
    assert c['baseline']==c['candidate'] and len(c['baseline'])==len(expected['baseline'])==1
    for actual,prior in zip(c['baseline'],expected['baseline']):
        for field in ['label','components','input']:assert actual[field]==prior[field]
        r=actual['result'];e=prior['result']
        for field in ['statuses','diagnostics','fallback_used','analytic_used','execution']:assert r[field]==e[field]
        assert len(r['values'])==len(e['values'])==40
        for z in r['values']:finite_complex(z)
        assert len(r['master_captures'])==len(e['master_captures'])
        for group,old in zip(r['master_captures'],e['master_captures']):
            for field in ['family','components','rows','requests','valid_lanes','input','output_order','errors','whole_batch_error','backend']:assert group[field]==old[field]
            assert group['backend']=='SymbolicaBatch' and len(group['output'])==len(old['output'])
            for lane,prior_lane in zip(group['output'],old['output']):
                assert len(lane)==len(prior_lane)
                for z in lane:finite_complex(z)
    m=c['masters'];em=expected['masters'];assert m['status']=='passed'
    assert len(m['selected_families'])==len(em['selected_families'])==3
    assert len(m['unchanged_paths'])==len(em['unchanged_paths'])==6
    def direct_complex(z):
        assert type(z) is list and len(z)==2
        return finite_complex([{**v,'finite':True} for v in z])
    def snapshot(actual,prior):
        for key in ['rows','components']:assert actual[key]==prior[key]
        assert len(actual['lanes'])==len(prior['lanes'])==actual['rows']
        for lane,old in zip(actual['lanes'],prior['lanes']):
            assert lane['error']==old['error']
            if lane['error'] is not None:assert lane['six_outputs'] is None
            else:
                assert len(lane['six_outputs'])==len(old['six_outputs'])==6*actual['components']
                for z in lane['six_outputs']:direct_complex(z)
    for group,old in zip(m['selected_families'],em['selected_families']):
        for field in ['family','status','layout_and_overflow_errors_checked','ordinary_dual_adapter_rejected','warm_clone_checked']:assert group[field]==old[field]
        assert group['status']=='passed' and len(group['cases'])==len(old['cases'])
        for case,prior in zip(group['cases'],old['cases']):
            for field in ['label','family','baseline_backend','candidate_backend','input_metadata','input_unchanged','own_repeated_outputs_exact','status']:assert case[field]==prior[field]
            assert case['status']=='passed' and case['input_unchanged'] is True and case['own_repeated_outputs_exact'] is True
            assert math.isfinite(case['maximum_normalized_error']) and 0<=case['maximum_normalized_error']<=1e-10
            snapshot(case['baseline'],prior['baseline']);snapshot(case['candidate'],prior['candidate'])
    for group,old in zip(m['unchanged_paths'],em['unchanged_paths']):
        for field in ['label','family','components','shape','backend','status']:assert group[field]==old[field]
        assert group['status']=='passed' and group['backend']=='SymbolicaBatch'
        assert len(group['cases'])==len(old['cases'])
        for case,prior in zip(group['cases'],old['cases']):
            for field in ['label','input_metadata','input_unchanged','own_repeated_outputs_exact','candidate_exactly_matches_baseline','status']:assert case[field]==prior[field]
            assert case['status']=='passed' and case['candidate_exactly_matches_baseline'] is True
            snapshot(case['represented_outputs'],prior['represented_outputs'])
    return {'status':'passed','selected_cases':34,'unchanged_cases':21,'whole_dual_cases':1}
