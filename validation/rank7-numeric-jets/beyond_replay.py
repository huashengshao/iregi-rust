"""Independent portable saved-only 1+2^-54 audit; no producer import or engine."""
from fractions import Fraction as F
from decimal import Decimal, localcontext
from pathlib import PurePosixPath
import hashlib
import io
import json
import tarfile

ROOT=PurePosixPath('/shared/external/iregi/iregi-rust')
BASE='target/rank7-numeric-jets-execution'
HERE=BASE+'/beyond53'
DELTA=F(1,2**54)
BASIS=[[t,x,y,r-t-x-y] for r in range(8) for t in range(r,-1,-1) for x in range(r-t,-1,-1) for y in range(r-t-x,-1,-1)]
def demand(ok,message):
    if not ok:raise ValueError(message)
def sha(body):return hashlib.sha256(body).hexdigest()
def parse(body):
    def pairs(items):
        d={}
        for k,v in items:demand(k not in d,'duplicate key');d[k]=v
        return d
    return json.loads(body,parse_float=str,object_pairs_hook=pairs,parse_constant=lambda v:(_ for _ in ()).throw(ValueError(v)))
def q(part):
    demand(set(part)=={'rational','precision','negative_sign','finite'} and part['finite'] is True and type(part['rational']) is str,'native operand')
    x=F(part['rational']);demand(type(part['precision']) is int and part['precision']>0,'native precision')
    demand(type(part['negative_sign']) is bool and (x==0 or part['negative_sign']==(x<0)),'native sign')
    return x
def z(value):demand(len(value)==2,'complex width');return tuple(q(p) for p in value)
def text(x):
    with localcontext() as c:c.prec=100;return str(Decimal(x.numerator)/Decimal(x.denominator))

def audit(read_bytes):
    report=dict(schema_version=1,status='failed_independent_beyond53_saved_audit',passed=False,findings=[],input_sha256={},producer_imports=False,native_or_evaluator_execution=False,typed_f64_or_DoubleFloat_Dual_tested=False,public_highpoint_Dual_qualified=False,performance_qualified=False,rigorous_error_qualified=False)
    pins=report['input_sha256']
    def raw(path,expected=None):
        p=PurePosixPath(path);p=p.relative_to(ROOT) if p.is_absolute() else p;demand('..' not in p.parts,'virtual path escape');name=str(p)
        body=read_bytes(name);demand(type(body) is bytes,'immutable bytes');digest=sha(body)
        demand(expected is None or digest==expected,'saved hash mismatch '+name);demand(name not in pins or pins[name]==digest,'changed repeat read '+name);pins[name]=digest
        return body
    def read(path,expected=None):return parse(raw(path,expected))
    try:
        full=read(BASE+'/comparison-fixed.json','08866730793916569eef2776d07ba9c0440880245614fd6313439074aa93a488')
        demand(full['passed'] is True and full['failures']==[],'initial eleven prerequisite')
        independent=read(BASE+'/independent-initial11-saved-numeric-audit.json','d183d6df7305a7529aee47c29b142c9877c40608ba3226ab411fb83633dc9658')
        demand(independent['passed'] is True and independent['findings']==[] if 'findings' in independent else independent['passed'] is True and independent['failures']==[],'independent initial prerequisite')
        gate=read(HERE+'/capture-v2-beyond-float256-001/gate-stage-v2.json')
        demand(gate['passed'] is True and gate['failures']==[] and gate['unattempted_cases']==[] and gate['attempted_cases']==['f64-rejection','beyond-dd','beyond-float128','beyond-float256'],'complete four terminal cases')
        fixture=read(HERE+'/fixture.json','635e4edd895693c60876f6e564706307d2b340f0bcaa922f5687e032ac75c0ea')
        props=fixture['samples'][0]['propagators'][:2]
        base=[F(v) for p in props for v in p['shift']]+[F(p['mass_squared'][0]) for p in props]+[F(fixture['samples'][0]['mu'])]
        demand(base==[F(0)]*5+[F(1),F(0),F(0),1+DELTA,F(2),F(3)],'unrounded first squared mass1+2^-54')
        capsule='validation/quad-original-iregi-generalized-rank7';cm=read(capsule+'/manifest.json','ccda92bdd0be40484b2d8762d479658ada0beb98eb610df7c96b44f7f521a0b0')
        payload=raw(capsule+'/payload.tar.gz',cm['capsule_files']['payload.tar.gz']['sha256']);stream='target/quad-generalized-rank7-anchors/capture-001/request-2.stdout'
        with tarfile.open(fileobj=io.BytesIO(payload),mode='r:gz') as archive:
            body=archive.extractfile(stream).read()
        demand(sha(body)==cm['payload_members'][stream]['sha256']=='30a5b60827f57751516fd2b4a21cffc2676b4401ab8739640e6b4d81b0b44cdb','exact originalquad dot0 stream')
        values=[parse(line[7:]) for line in body.decode().splitlines() if line.startswith('RESULT ')]
        demand(len(values)==1 and values[0]['stable'] is True and len(values[0]['moments'])==330 and values[0]['poles']==['uv1','ir1','ir2','finite'],'full original dot0 array')
        dot=[tuple(F(v) for v in item) for moment in values[0]['moments'] for item in moment];demand(len(dot)==1320,'full quad Laurent slots')
        decoded={};max_slope=F(0);slope_count=0;receipts=[]
        for case in ['f64-rejection','beyond-dd','beyond-float128','beyond-float256']:
            folder=HERE+'/capture-v2-'+case+'-001';receipt=read(folder+'/receipt.json');record=read(folder+'/result.json',receipt['outputs']['result.json'])
            demand(receipt['status']=='passed_capture_only_pending_saved_gate' and receipt['stage']==case and receipt['inputs_unchanged'] is True and receipt['cleanup_errors']==[] and receipt['cancellation'] is None and len(receipt['steps'])==1,'terminal capture receipt')
            step=receipt['steps'][0];demand(step['owned_group_gone'] is True and not step.get('timeout'),'historical owned process absence')
            demand(F(str(receipt['elapsed_seconds']))<=receipt['total_seconds'] and receipt['no_build'] is True and receipt['no_binary_copy'] is True,'finite no-build capture')
            demand([F(v) for v in record['base_exact_rational']]==base and record['profile']=='plain' and record['ordered_shape'] is None,'exact beyond53 plain carrier')
            expectedrows=[[v*F(scale)**(2 if 8<=i<10 else 1) for i,v in enumerate(base)] for scale in [1,2]]
            demand([[F(v) for v in row] for row in record['input_exact_rational']]==expectedrows,'exact saved base/scaled inputs')
            if case=='f64-rejection':
                demand(step['returncode']==2 and step['status']=='failed' and receipt['expected_conversion_rejection'] is True,'expected nonzero f64 conversion rejection')
                demand(record['status']=='capture_error' and record['error']=='input rounding would change this exact cohort' and record['calls']==[] and not any(k in record for k in ['basis','algorithm_used','preparation_notes','all_expected_outcomes']),'rejection before structural preparation')
                receipts.append(dict(case=case,returncode=2,conversion_rejection_before_preparation=True,owned_group_gone=True));continue
            bits=106 if case=='beyond-dd' else 128 if case=='beyond-float128' else 256
            demand(step['returncode']==0 and step['status']=='exited' and record['status']=='capture_complete_not_yet_qualified' and record['all_expected_outcomes'] is True and record['working_bits']==bits and record['requested_bits']==53 and record['basis']==BASIS,'complete ordinary carrier')
            call=record['calls'][0];demand(len(record['calls'])==1 and call['name']=='ordinary_odd3' and call['input_before']==call['input_after'] and call['input_preserved'] is True and call['expected_outcomes'] is True and call['status']=='captured','one exact ordinary input-preserving call')
            actualinput=[z(v) for v in call['input_before']];invalid=list(expectedrows[0]);invalid[-1]=F(0)
            demand(actualinput==[(v,F(0)) for row in [expectedrows[0],invalid,expectedrows[1]] for v in row],'actual native input no53bit rounding')
            if bits==106:demand(all(part['precision']==106 for value in call['input_before'] for part in value),'fixed DD carrier input precision')
            s=call['execution'];demand(s['input_rows']==3 and s['argument_rows']==s['reduction_rows']==2 and s['master_rows']>=2 and s['master_rows']%2==0 and s['master_family_batches']>0 and not any(s[k] for k in ['pentagon_box_rows','fallback_rows','fallback_successes','analytic_rows']),'actual master/reduction batching')
            demand(len(call['lanes'])==len(call['diagnostics'])==3,'full lane inventory');output=[]
            for i,lane in enumerate(call['lanes']):
                demand(lane['lane']==i and lane['expected_outcome'] is True and lane['fallback_used'] is False and lane['analytic_used'] is False,'lane identity/routes')
                if i==1:demand(lane['status'].startswith('InvalidInput(') and lane['values'] is None and call['diagnostics'][i]==[],'invalid null isolation')
                else:
                    demand(lane['status']=='Success' and len(lane['values'])==1320,'complete successful tensor')
                    if bits==106:demand(all(part['precision']==106 for value in lane['values'] for part in value),'fixed DD output precision')
                    output.append([z(v) for v in lane['values']])
            decoded[case]=output
            baseline_name='plain-dd' if bits==106 else 'first-float'+str(bits)
            baseline_path=BASE+'/captures/'+baseline_name+'-001/result.json';baseline=read(baseline_path,full['input_sha256'][str(ROOT/baseline_path)])
            previous=[baseline['calls'][0]['lanes'][0]['values'],baseline['calls'][0]['lanes'][2]['values']] if bits==106 else [baseline['calls'][0]['lanes'][0]['values'][::2],baseline['calls'][1]['lanes'][0]['values'][::2]]
            for row,scale in enumerate([1,2]):
                old=[z(v) for v in previous[row]]
                for index,(new,oldvalue) in enumerate(zip(output[row],old)):
                    degree=sum(BASIS[index//4]);actual=tuple((a-b)/(DELTA*scale**2) for a,b in zip(new,oldvalue));expected=tuple(v*F(scale)**(degree-2) for v in dot[index])
                    error=sum(abs(a-b) for a,b in zip(actual,expected))/((F(3)*scale)**(degree-2)+sum(abs(v) for v in expected));max_slope=max(max_slope,error);slope_count+=1
                    demand(error<=F(1,10**10),'beyond53 slope originalquad discrepancy')
            receipts.append(dict(case=case,returncode=0,owned_group_gone=True,complex_slots=2640,stored_bits=bits))
        pair_count=0;max_pair=F(0)
        for row,scale in enumerate([1,2]):
            for index,(a,b) in enumerate(zip(decoded['beyond-float128'][row],decoded['beyond-float256'][row])):
                degree=sum(BASIS[index//4]);error=sum(abs(x-y) for x,y in zip(a,b))/((F(3)*scale)**degree+sum(abs(x) for x in b));max_pair=max(max_pair,error);pair_count+=1;demand(error<=F(1,2**80),'raw128256 precision disagreement')
        demand(slope_count==7920 and pair_count==2640,'complete exact extension coverage')
        demand(gate['comparison_counts']==dict(beyond53_raw_128_256=2640,beyond53_slope_original_quad=7920),'producer count')
        demand(text(max_slope)==gate['max_errors']['beyond53_slope_original_quad'] and text(max_pair)==gate['max_errors']['beyond53_raw_128_256'],'independent maxima differ')
        report.update(passed=True,status='passed_independent_beyond53_saved_audit',slope_comparisons=slope_count,raw_pair_comparisons=pair_count,max_slope_error=text(max_slope),max_raw_pair_error=text(max_pair),exact_delta=str(DELTA),integral_domains=3,expected_f64_preplan_rejections=1,terminal_metadata=receipts,scope='Separate ordinary-input perturbation of one N2rank7massivefixture; no typed f64/DD Dual claim.',limits=['Finite secant slopes use delta2^-54 and independent originalquad firstmass derivative, retaining all330moments and4Laurents.','Native/source identities and owned PGabsence checked from exact saved receipts; no executable/dependencyhash or liveprocesscheck.','No public highpointDual, rigorouserror or performance qualification.'])
    except Exception as exc:report['findings'].append(dict(kind='audit_structure',message=f'{type(exc).__name__}: {exc}'))
    for path,expected in pins.items():demand(sha(read_bytes(path))==expected,'changed virtual postguard '+path)
    return report
