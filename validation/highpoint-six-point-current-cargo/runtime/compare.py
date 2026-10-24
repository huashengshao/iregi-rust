"""Saved-data qualification for exact tests, ordinary parity and public rank3."""
from decimal import Decimal,localcontext
from fractions import Fraction
import importlib.util,math,sys
import harness_common as h

def shared(inputs):
    h.bind(h.SHARED,inputs,'bd7139b6f846b69706a89c6c72e426605aebd5fa4ffbb75dcf1bcfb83c04da9d')
    spec=importlib.util.spec_from_file_location('six_point_shared',h.SHARED);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def merge(inputs,other):
    for name,digest in other.items():h.bind(h.absolute(name),inputs,digest)

def exact(inputs):
    run=h.validate_run('exact');merge(inputs,run['input_sha256'])
    total=0
    for i,group in enumerate(run['protocol']['exact_groups']):
        h.validate_test_log((h.HERE/'exact-001'/f'step-{i}.log').read_text(),group['names']);total+=len(group['names'])
    h.require(total==34,'incomplete exact suite')
    return {'passed':True,'tests_passed':total,'numerical_qualification':False}

def ordinary(inputs):
    runs=[h.validate_run('ordinary-'+variant) for variant in ['baseline','candidate']]
    for run in runs:merge(inputs,run['input_sha256'])
    a,b=[run['record'] for run in runs];h.require(a==b,'ordinary baseline/candidate complete records differ')
    settings=[(1,2,1),(2,2,1),(3,1,1),(2,1,3)]
    expected=[(domain,n,rank,c) for domain in ['f64','DoubleFloat','Float128'] for n,rank,c in settings]
    h.require(len(a)==12 and [(x['domain'],x['propagators'],x['rank'],x['components']) for x in a]==expected,'ordinary case inventory differs')
    successes=failures=slots=0
    for case in a:
        result=case['result'];components=case['components'];width=math.comb(case['rank']+4,4)*4*components
        h.require(len(result['moments'])==len(result['contracted'])==5,'ordinary row count differs')
        h.require(result['moments']==result['repeat'],'repeated ordinary arrays differ')
        h.require(result['moments'][4] is None and 'InvalidInput' in result['statuses'],'invalid zero-scale control missing')
        h.require(any(row is not None for row in result['moments'][:3]),'intended ordinary successes unavailable')
        for row,contracted in zip(result['moments'],result['contracted']):
            if row is None:h.require(contracted is None,'failed moment lane contracts successfully');failures+=1;continue
            h.require(len(row)==width and len(contracted)==4*components,'ordinary complete slot width differs')
            for value in row+contracted:
                h.require(isinstance(value,list) and len(value)==2,'complex ordinary component malformed')
                for part in value:
                    h.require(set(part)=={'rational','bits','negative_sign'} and isinstance(part['rational'],str),'ordinary represented metadata missing')
                    Fraction(part['rational'])
            successes+=1;slots+=width
    return {'passed':True,'paired_cases':12,'successful_lanes':successes,'matching_failed_controls':failures,'native_complex_taylor_slots':slots,'comparison':'complete exact value/precision/sign/status/metadata/flags/diagnostics/counter/input equality','performance_qualified':False}

def represented(record,working,fixture,api):
    settings=dict(propagators=6,rank=3,powers=[1]*6,dimension_shift=0,algorithm='PassarinoVeltman',convention='IregiNative',tensor_weights='Components',invariants='FromShifts',input_policy='Preserve')
    h.require(record['settings']==settings and record['working_bits']==working and record['requested_bits']==53,'public settings/precision differ')
    h.require(record['status']=='all_lanes_success' and record['rows']==record['components']==1 and record['lane_statuses']==['Success'],'public array not wholly successful')
    h.require(record['basis']==api.canonical_basis(3) and len(record['lanes'])==1 and record['lanes'][0]['row']==0 and record['lanes'][0]['status']=='Success','public basis/order differs')
    sample=fixture['samples'][0];ps=sample['propagators'][:6]
    values=[[str(Fraction(v)),'0'] for p in ps for v in p['shift']]+[[str(Fraction(v)) for v in p['mass_squared']] for p in ps]+[[str(Fraction(sample['mu'])),'0']]
    h.require(record['input_exact_rational']==[values],'represented inputs differ from original fixture')
    moments=record['lanes'][0]['moments'];h.require(len(moments)==35,'public moment array incomplete')
    for slots in moments:
        h.require(len(slots)==4,'public Laurent slots incomplete')
        for pole,slot in enumerate(slots):
            h.require(set(slot)=={'real','imaginary','real_precision','imaginary_precision'},'public represented metadata differs')
            for part in ['real','imaginary']:
                h.require(isinstance(slot[part],str),'nonrational public output');value=Fraction(slot[part])
                precision=slot[part+'_precision'];h.require(type(precision)is int and precision>=0 and (value==0 or precision>0),'invalid public operand precision')
                if pole<3:h.require(value==0,'public massive convergent pole is not exactly zero')
    work=record['execution']
    h.require((work['parent_input_rows'],work['child_batch_calls'],work['packed_child_rows'],work['parent_batch_calls'],work['packed_parent_rows'])==(1,1,6,1,1),'six-point batch propagation differs')
    h.require(all(isinstance(work[k],str) for k in ['child_execution','parent_execution','child_certificate_execution','parent_certificate_execution']),'work counters absent')
    return moments

def numeric(operation,inputs):
    api=shared(inputs)
    h.bind(h.FIXTURE,inputs,'ec27f2c5774a18d3d84d2d733e634dae93e9bd4c74523d6f77e8784d13421ada')
    h.bind(h.REFERENCE,inputs,'9bc3f10ad27615f23ddb3c2f62169575378d32e6c35c9d2a9dd51223f9b39ec4')
    fixture,reference=h.load(h.FIXTURE),h.load(h.REFERENCE);api.validate_reference(reference,fixture,h.sha(h.FIXTURE))
    original=[x for x in reference['cases'] if x['id']=='n6_base_mode0']
    h.require(len(original)==1 and original[0]['status']=='captured' and original[0]['response']['stable'] is True,'untouched stable original IBP unavailable')
    old=original[0]['response']['moments'];bits=[128] if operation=='128' else [128,256]
    arrays={};failure=[];comparisons=[];historical_differences=[];max_original=Decimal(0);max_convergence=Decimal(0)
    history_root=h.ROOT/'validation/highpoint-thin-n6-generic';h.bind(history_root/'qualification.json',inputs,'79ccaaa6439fd6cc2307f0dc186b6c6fbf7ba4a1585177a6ceab360d53b74d34')
    history_qualification=h.load(history_root/'qualification.json')
    h.require(history_qualification['status']=='private_retained_n6_rank3_qualified','historical private rank3 scope differs')
    sample=fixture['samples'][0];q=api.scale(sample,6)
    for working in bits:
        run=h.validate_run(str(working));merge(inputs,run['input_sha256']);record=run['record'];arrays[working]=represented(record,working,fixture,api)
        h.require(record['fixture']==h.key(h.FIXTURE),'public fixture path differs from runtime')
        historic_name=f'fixed/n6-rank3-{working}-001/result.json';historic_path=history_root/historic_name;h.bind(historic_path,inputs,history_qualification['files'][historic_name])
        historic=h.load(historic_path)
        h.require(historic['settings']==record['settings'] and historic['input_exact_rational']==record['input_exact_rational'] and historic['basis']==record['basis'],'historical private inputs/basis/settings differ')
        for moment,monomial in enumerate(record['basis']):
            natural=q**(sum(monomial)-8)
            for pole in range(4):
                value=tuple(api.decimal_rational(arrays[working][moment][pole][part]) for part in ['real','imaginary'])
                reference_value=tuple(Decimal(str(v)) for v in old[moment][pole])
                error=api.norm(tuple(a-b for a,b in zip(value,reference_value)))/max(natural,api.norm(reference_value))
                max_original=max(max_original,error)
                entry={'working_bits':working,'moment':moment,'monomial':monomial,'laurent_slot':pole,'normalized_original_error':str(error)};comparisons.append(entry)
                if error>Decimal('1e-10'):failure.append(entry)
                previous=historic['lanes'][0]['moments'][moment][pole]
                hvalue=tuple(api.decimal_rational(previous[part]) for part in ['real','imaginary'])
                historical_error=api.norm(tuple(a-b for a,b in zip(value,hvalue)))/max(natural,api.norm(hvalue))
                if arrays[working][moment][pole]!=previous:historical_differences.append({'working_bits':working,'moment':moment,'slot':pole,'actual':arrays[working][moment][pole],'historical':previous,'normalized_error':str(historical_error)})
                if historical_error>Decimal('1e-10'):failure.append({'historical_numeric_failure':True,**entry,'historical_error':str(historical_error)})
    convergence=[]
    if operation=='256':
        for moment,monomial in enumerate(api.canonical_basis(3)):
            natural=q**(sum(monomial)-8)
            for pole in range(4):
                low,high=[tuple(api.decimal_rational(arrays[bit][moment][pole][part]) for part in ['real','imaginary']) for bit in [128,256]]
                error=api.norm(tuple(a-b for a,b in zip(low,high)))/max(natural,api.norm(high));max_convergence=max(max_convergence,error)
                entry={'moment':moment,'laurent_slot':pole,'normalized_convergence_error':str(error)};convergence.append(entry)
                if error>Decimal(2)**-80:failure.append(entry)
    h.require(len(comparisons)==140*len(bits) and len(convergence)==(140 if operation=='256' else 0),'incomplete slot comparison')
    return {'passed':not failure,'scope':'Restricted explicit N6 public rank3, same retained base fixture only; no production adoption or broad-domain/performance claim.','working_bits':bits,'native_slots_per_precision':140,'exact_zero_poles_per_precision':105,'original_tolerance':'1e-10','convergence_tolerance':'2^-80','maximum_original_error':str(max_original),'maximum_convergence_error':str(max_convergence) if operation=='256' else None,'all_original_comparisons':comparisons,'all_convergence_comparisons':convergence,'historical_exact_differences':historical_differences,'failures':failure,'precision_convergence_qualified':operation=='256' and not failure,'performance_qualified':False}

def main(operation):
    names={'exact':'exact-comparison.json','ordinary':'ordinary-comparison.json','128':'comparison-128.json','256':'comparison-128-256.json'}
    h.require(operation in names,'unknown comparison');output=h.HERE/names[operation];h.require(not output.exists(),'comparison already exists')
    inputs={};h.bind(__file__,inputs);h.bind(h.HERE/'harness_common.py',inputs)
    try:
        with localcontext() as context:
            context.prec=220
            result=exact(inputs) if operation=='exact' else ordinary(inputs) if operation=='ordinary' else numeric(operation,inputs)
        h.final_verify(inputs);result.update(status='passed' if result['passed'] else 'failed',input_sha256=inputs,inputs_unchanged=True)
    except Exception as error:result={'status':'failed','passed':False,'error':str(error),'input_sha256':inputs}
    h.save(output,result);print({key:result[key] for key in ['status','passed']});return 0 if result['passed'] else 1
if __name__=='__main__':sys.exit(main(sys.argv[1]))
