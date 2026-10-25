#!/usr/bin/env python3
"""Saved-only comparison of the fixed planar scalar vertical slice.

All 30 Rust jobs and three parameter-oracle jobs are mandatory. Acceptance uses
exact Fraction arithmetic. Decimal formats error displays only. No producer,
mpmath, Symbolica, executable, compiler or process-management API is imported.
"""
import argparse
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re

HERE=Path('validation/certified-planar-generalized-scalar')
DEFAULT_ROOT=Path('target/certified-planar-generalized-scalar-numeric')
POINTS=((0,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1),(0,1,1,1))
MASSES=(4,9,16,25,36)
POLES=['uv1','ir1','ir2','finite']
DIRECT2=F(1,10**20)
PAIR2=F(1,2**160)
ORACLE2=F(1,10**24)
MODES={'scalar':(5,1,2),'mass-jets':(7,2,5),'finite-difference':(21,1,None)}
REQUESTS=[(1,None)]+[(h,i) for h in [0,1] for i in range(5)]
ORDERS=[(12,50),(16,70),(20,90)]
SAMPLES=[('1/2','1/3','1/4','1/5'),('1/7','2/5','3/8','4/9'),('3/4','1/6','2/7','3/10')]

def require(ok,message):
    if not ok:raise ValueError(message)

def unique(items):
    result={}
    for key,value in items:
        require(key not in result,'duplicate JSON key '+key)
        result[key]=value
    return result

def nonfinite(text):raise ValueError('nonfinite JSON '+text)

def decode(raw):
    return json.loads(raw,parse_float=str,parse_constant=nonfinite,object_pairs_hook=unique)

def rational(value):
    require(type(value) in (int,str),'exact integer or numeric string required')
    token=str(value).strip()
    require(re.fullmatch(r'[+-]?(?:\d+/\d+|(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?)',token) is not None,
            'invalid/nonfinite rational token')
    return F(token)

def pair(value):
    require(isinstance(value,list) and len(value)==2,'complex pair must have two exact components')
    return tuple(map(rational,value))

def complex_slot(value,bits):
    require(isinstance(value,dict) and set(value)=={'real','imaginary','real_precision','imaginary_precision'},
            'complete complex slot and precision metadata required')
    require(all(type(value[key]) is int and 0<value[key]<=bits
                for key in ['real_precision','imaginary_precision']),'component precision outside working context')
    return rational(value['real']),rational(value['imaginary'])

def plus(a,b):return tuple(x+y for x,y in zip(a,b))
def minus(a,b):return tuple(x-y for x,y in zip(a,b))
def times(a,factor):return tuple(value*factor for value in a)
def norm2(value):return sum(x*x for x in value)

def squared_error(actual,reference,dimension,q2):
    return norm2(minus(actual,reference))/max(q2**dimension,norm2(reference))

def show_squared(value):
    if value==0:return '0'
    with localcontext() as context:
        context.prec=100
        return str((Decimal(value.numerator)/Decimal(value.denominator)).sqrt())

def request_name(h,dot):return f'h{h}-'+('unit' if dot is None else f'dot{dot}')
def job_name(mode,h,dot,bits):return f'{mode}-{request_name(h,dot)}-Float{bits}'
def expected_job_keys():
    return [(job_name('scalar',h,dot,bits),'rust','scalar',h,dot,bits) for h,dot in REQUESTS for bits in [128,256]]+[
        (job_name(mode,h,None,bits),'rust',mode,h,None,bits)
        for mode in ['mass-jets','finite-difference'] for h in [0,1] for bits in [128,256]]+[
        (f'oracle-order{order}-digits{digits}','independent_parameter_oracle',None,None,None,None)
        for order,digits in ORDERS]

def base_values():return [F(x) for p in POINTS for x in p]+list(map(F,MASSES))+[F(3)]

def input_rows(mode):
    base=base_values()
    if mode=='scalar':
        scaled=[value*(2 if i<20 or i==25 else 4) for i,value in enumerate(base)]
        bad=base.copy();bad[16]+=F(1,16)
        translated=base.copy();translation=[0,F(1,4),F(-1,8),F(3,8)]
        for i in range(20):translated[i]+=translation[i%4]
        return ([base,scaled,bad,translated,base.copy()],
                ['base','scaled_by_two','nonplanar_invalid','translated','base_repeat'])
    if mode=='mass-jets':
        rows=[]
        for i in range(5):
            row=[item for value in base for item in [value,F(0)]]
            row[2*(20+i)+1]=F(1);rows.append(row)
        bad=rows[0].copy();bad[2*16+1]=F(1)
        return rows+[bad,rows[0].copy()],[f'mass_squared_{i}_jet' for i in range(5)]+['transverse_invalid','mass_0_repeat']
    require(mode=='finite-difference','unknown input mode')
    rows=[base.copy()];labels=['base']
    for i in range(5):
        for exponent in [12,16]:
            for sign in [-1,1]:
                row=base.copy();row[20+i]+=F(sign,2**exponent);rows.append(row)
                labels.append(f'mass_{i}_step_2^-{exponent}_{sign}')
    return rows,labels

def natural_q2(row,components):
    primal=row[::components]
    values=[F(1)]+[abs(value) for value in primal[20:25]]
    for i in range(5):
        for j in range(i+1,5):
            d=[primal[4*i+mu]-primal[4*j+mu] for mu in range(4)]
            values.append(abs(d[0]**2-sum(value**2 for value in d[1:])))
    return max(values)

def preparation_check(preparation):
    require(preparation['schema_version']==1 and preparation['algebra_provider']=='Symbolica','Symbolica preparation provenance')
    require(preparation['cube_variable_order']==['u','v','w','z'] and
            preparation['simplex_variable_order']==['x0','x1','x2','x3','x4'],'preparation parameter order')
    require(all(isinstance(preparation[key],str) and preparation[key].strip()
                for key in ['F_expression','jacobian_expression']),'preparation expression strings')
    witnesses=preparation['evaluations'];require(isinstance(witnesses,list) and len(witnesses)==3,'three exact preparation witnesses')
    expected={tuple(map(F,cube)) for cube in SAMPLES};seen=set()
    for witness in witnesses:
        cube=tuple(map(rational,witness['cube']));require(cube in expected and cube not in seen,'preparation sample identities')
        seen.add(cube);u,v,w,z=cube;a,b,c=1-u,1-v,1-w
        xs=(u,a*v,a*b*w,a*b*c*z,a*b*c*(1-z))
        require(tuple(map(rational,witness['simplex']))==xs,'preparation map sample')
        f=sum(x*m for x,m in zip(xs,MASSES))
        for i in range(5):
            for j in range(i+1,5):
                d=[POINTS[i][mu]-POINTS[j][mu] for mu in range(4)]
                f-=xs[i]*xs[j]*(d[0]**2-sum(value**2 for value in d[1:]))
        require(rational(witness['F'])==f and rational(witness['jacobian'])==a**3*b**2*c,
                'preparation F/Jacobian numeric witness')

def parse_rust(document,job):
    mode,h,dot,bits=job['mode'],job['h'],job['dot'],job['working_bits']
    rows,components,invalid=MODES[mode];expected_inputs,labels=input_rows(mode)
    require(document['schema_version']==1 and document['status']=='completed_with_expected_lane_controls','complete Rust capture status')
    require(document['interface']=='CertifiedPlanarReductionPlan and CertifiedPlanarWorkspace','certified public interface')
    require(document['dimension_shift']==h and document['dot']==dot and document['mode']==mode,'Rust request identity')
    require(document['dot'] is None if dot is None else type(document['dot']) is int,'strict dot index type')
    require(document['fixture']==job['command'][1],'exact fixture attribution')
    require(document['working_bits']==bits and document['requested_bits']==job['requested_bits'],'Rust precision request')
    require(all(type(document[key]) is int for key in ['schema_version','dimension_shift','working_bits','requested_bits','components']),
            'strict integer Rust metadata')
    require(document['components']==components and document['dual_shape']==([[0],[1]] if components==2 else None),
            'derivative axis must be distinct from sample rows')
    if components==2:require(all(type(value) is int for row in document['dual_shape'] for value in row),'strict derivative indices')
    require(document['basis']==[[0,0,0,0]] and document['native_slots']==POLES,'rank-zero basis/native Laurent order')
    require(all(type(value) is int for value in document['basis'][0]),'strict rank-zero basis indices')
    require(document['expected_invalid_lane']==invalid and document['row_labels']==labels,'exact lane labels/control placement')
    powers=[2 if i==dot else 1 for i in range(5)]
    algorithm='PassarinoVeltman' if h==0 and dot is None else 'Ibp'
    require(document['settings']=={'propagators':5,'rank':0,'powers':powers,'dimension_shift':h,
        'algorithm':algorithm,'invariants':'FromShifts','input_policy':'Preserve',
        'convention':'IregiNative','tensor_weights':'Components'},'exact native settings')
    require(all(type(document['settings'][key]) is int for key in ['propagators','rank','dimension_shift'])
            and all(type(value) is int for value in document['settings']['powers']), 'strict integer settings')
    require(document['normalization']=='IregiNative i*pi^(2+h), separate Laurent slots; no pole projection','normalization declaration')
    require(document['timings_are_performance_evidence'] is False and document['full_generalized_domain_qualified'] is False
            and document['genuine_E6_evaluated'] is False,'Rust scope/backend flags')
    require(document['input_jet_provider']=='Symbolica derivative and exact substitution; reduction/master jets use the core Symbolica Dualizer',
            'input derivative preparation provenance')
    exact_rows=document['input_exact_rational'];require(isinstance(exact_rows,list) and len(exact_rows)==rows,'complete exact input table')
    for actual,expected in zip(exact_rows,expected_inputs):
        require(isinstance(actual,list) and len(actual)==26*components,'input component layout')
        require([pair(value) for value in actual]==[(value,F(0)) for value in expected],'exact preserved input values')
    before=document['input_before_numeric'];after=document['input_after_numeric']
    require(document['input_values_and_precision_preserved'] is True and before==after,
            'input values and precision must survive reduction unchanged')
    require(document['signed_zero_preservation_checked'] is False,'no unsupported signed-zero preservation claim')
    require(isinstance(before,list) and len(before)==rows*26*components,'complete before/after numeric input ledger')
    require([complex_slot(value,bits) for value in before]==[(value,F(0)) for row in expected_inputs for value in row],
            'numeric input ledger matches exact input layout')
    for key in ['lane_statuses','lanes','fallback_used','analytic_used','diagnostics','actual_chart_omitted_rows_from_diagnostics']:
        require(isinstance(document[key],list) and len(document[key])==rows,'complete per-lane metadata '+key)
    parsed=[];precision_counts={}
    prefix='exact full-Taylor planar identity with regular constant-one chart omitting coordinate row '
    for row,lane in enumerate(document['lanes']):
        require(set(lane)=={'row','status','slots'} and lane['row']==row,'ordered lane identity')
        require(type(lane['row']) is int and isinstance(lane['status'],str),'strict row/status types')
        require(lane['status']==document['lane_statuses'][row],'consistent lane status')
        require(document['fallback_used'][row] is False,'unexpected fallback')
        diagnostics=document['diagnostics'][row]
        require(isinstance(diagnostics,list) and all(isinstance(value,str) for value in diagnostics),'diagnostic shape')
        if row==invalid:
            require(lane['status'].startswith('InvalidInput(') and 'planar coordinate determinant' in lane['status'],
                    'intended nonplanar/transverse rejection')
            require(lane['slots'] is None and document['actual_chart_omitted_rows_from_diagnostics'][row] is None,
                    'invalid lane must have null values/chart')
            require(document['analytic_used'][row] is False and not any(value.startswith(prefix) for value in diagnostics),
                    'invalid lane never dispatched')
            parsed.append(None);continue
        require(lane['status']=='Success' and document['analytic_used'][row] is True,'valid lane success/analytic route')
        require(type(document['actual_chart_omitted_rows_from_diagnostics'][row]) is int and
                document['actual_chart_omitted_rows_from_diagnostics'][row]==0,'regular primal chart omits only time row')
        require([value for value in diagnostics if value.startswith(prefix)]==[prefix+'0'],'exact chart diagnostic attribution')
        slots=lane['slots'];require(isinstance(slots,list) and len(slots)==4,'four Laurent slots remain separate')
        values=[]
        for slot in slots:
            require(isinstance(slot,list) and len(slot)==components,'complete derivative components per slot')
            values.append([complex_slot(value,bits) for value in slot])
            for value in slot:
                for key in ['real_precision','imaginary_precision']:
                    precision=str(value[key]);precision_counts[precision]=precision_counts.get(precision,0)+1
        parsed.append(values)
    execution=document['execution'];certificate=document['certificate_execution'];good=rows-(invalid is not None)
    require(all(type(value) is int and value>=0 for value in execution.values()),'integer execution counters')
    require(set(execution)=={'input_rows','argument_rows','master_family_batches','master_rows','pentagon_box_rows',
                            'reduction_rows','fallback_rows','fallback_successes','analytic_rows'},'execution counter inventory')
    require(execution['input_rows']==rows and execution['reduction_rows']==good and execution['analytic_rows']==good,
            'batched chart execution row attribution')
    require(execution['pentagon_box_rows']==execution['fallback_rows']==execution['fallback_successes']==0,
            'no E6/fallback work hidden')
    require(set(certificate)=={'input_rows','evaluated_rows','passes','reduction_batches'} and
            all(type(value) is int and value>=0 for value in certificate.values()),'certificate counter inventory')
    require(certificate['input_rows']==rows and certificate['reduction_batches']==1 and certificate['passes']>=2
            and certificate['evaluated_rows']>=rows+good,'full-batch planar and chart certificates')
    preparation_check(document['oracle_preparation'])
    return {'document':document,'array':parsed,'q2':[natural_q2(row,components) for row in expected_inputs],
            'dimension':4+2*h-2*sum(powers),'precision_histogram':precision_counts}

def parse_oracle(document,job):
    order,digits=job['order'],job['digits']
    require(document['schema_version']==1 and document['status']=='complete_finite_parameter_capture_not_yet_qualified',
            'complete independent parameter capture')
    require(document['run_id']==f'q{order}-d{digits}' and document['order_per_axis']==order
            and document['working_decimal_digits']==digits and document['serialized_decimal_digits']==digits-8,
            'oracle order/precision catalogue')
    require(document['nodes_evaluated']==order**4 and document['simultaneous_integrals']==12,'complete four-dimensional node/integral count')
    require(document['independent_of_reduction'] is True and document['numerator_or_tensor_reduction_used'] is False,
            'defining-integral oracle independence')
    for key in ['quadrature_convergence_checked','rigorous_error_bound','public_generalized_numeric_domain_qualified',
                'performance_qualified','automatic_retry_or_refinement']:
        require(document[key] is False,'oracle preserves qualification limit '+key)
    require(document['normalization']=='J_h=pi^(-h) I_D with common i*pi^2 stripped; native finite=i*pi^(2+h)*J_h',
            'oracle native normalization')
    fixture=document['fixture']
    require([[rational(value) for value in p] for p in fixture['shifts']]==[list(map(F,p)) for p in POINTS]
            and list(map(rational,fixture['mass_squared']))==list(map(F,MASSES)),'oracle exact original kinematics')
    require(rational(fixture['mu'])==3 and rational(fixture['scale'])==1 and rational(fixture['F_lower_bound'])==4
            and list(map(rational,fixture['mass_offsets_before_scaling']))==[F(0)]*5,'base positive-F oracle domain')
    expected_names=['J_h0_unit','J_h1_unit']+[f'J_h0_dot{i}' for i in range(5)]+[f'J_h1_dot{i}' for i in range(5)]
    require(document['integral_names']==expected_names,'twelve defining-integral order')
    integrals=list(map(rational,document['finite_integrals']))
    require(len(integrals)==12 and integrals[0]<0 and integrals[1]<0 and all(value>0 for value in integrals[2:]),
            'twelve finite nonzero defining integrals with expected signs')
    require(rational(document['h0_unit_derivative_control'])==integrals[0],'ordinary scalar control value')
    requests=document['requests'];require(isinstance(requests,list) and len(requests)==11,'eleven requested oracle objects')
    result={}
    for request,(h,dot) in zip(requests,REQUESTS):
        require(request['id']==request_name(h,dot) and request['h']==h
                and request['powers']==[2 if i==dot else 1 for i in range(5)],'oracle requested powers/dimension')
        index=1 if dot is None else 2+dot+5*h
        require(rational(request['J'])==integrals[index],'oracle J index')
        result[h,dot]=oracle_slots(request)
    control=document['h0_unit_control']
    require(control['id']=='h0-unit-control' and control['h']==0 and control['powers']==[1]*5
            and rational(control['J'])==integrals[0],'twelfth ordinary scalar control')
    result[0,None]=oracle_slots(control)
    prep=document['symbolica_preparation']
    require(prep['exact_numeric_samples_checked']==3 and prep['expression_strings_interpreted'] is False,
            'oracle exact numeric Symbolica witnesses')
    require(isinstance(prep['path'],str) and isinstance(prep['sha256'],str)
            and re.fullmatch('[0-9a-f]{64}',prep['sha256']),'oracle preparation payload identity')
    require(document['common_mass_identity']['independent_derivative_qualification'] is False,
            'correlated common-mass diagnostic must not claim independent validation')
    reuse=document['quadrature_reuse']
    require(reuse['source_sha256']=='ef11c91cbdaf453733e8f710237245d647c79dbe5f619c514295d2654444a1ca'
            and reuse['function_source_sha256']=='fd8e964d56aa8519d8ff7fb42083f184ace108a2d8da79016be0799cfb2d5480'
            and reuse['function']=='unit_rule' and reuse['full_producer_module_imported'] is False,
            'pinned existing quadrature helper without producer import')
    return {'document':document,'values':result}

def oracle_slots(request):
    require(request['native_Laurent_order']==POLES,'oracle native slot order')
    slots=request['native_slots'];require(isinstance(slots,list) and len(slots)==4,'oracle four-slot shape')
    values=list(map(pair,slots));require(values[:3]==[(F(0),F(0))]*3,'positive-F oracle poles')
    require(values[3][0]==0 and values[3][1]*rational(request['J'])>0,'oracle native phase/sign')
    return values

class Comparison:
    def __init__(self):self.records=[];self.failures=[];self.read_files={};self.cases=[]
    def read(self,path):
        path=Path(path);require(path.suffix in ['.json','.log','.txt','.py'],'only small saved metadata/source/log files may be read')
        require(not path.is_symlink() and path.stat().st_size<8_000_000,'native/large/symlink payload read forbidden')
        raw=path.read_bytes();self.read_files[str(path)]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
        return raw
    def load(self,path):return decode(self.read(path))
    def gate(self,kind,actual,reference,dimension,q2=F(36),threshold=DIRECT2,**labels):
        record={'kind':kind,**labels,'dimension':dimension,'Q_squared':str(q2),'threshold_squared':str(threshold)}
        if actual is None or reference is None:
            record.update(status='blocked',passed=False,error_squared=None,error=None)
        else:
            value=squared_error(actual,reference,dimension,q2)
            record.update(status='passed' if value<=threshold else 'failed',passed=value<=threshold,
                          actual=list(map(str,actual)),reference=list(map(str,reference)),
                          error_squared=str(value),error=show_squared(value))
        self.records.append(record)
        if not record['passed']:self.failures.append({'record':len(self.records)-1,'kind':kind,**labels,'status':record['status']})
        return None if record['error_squared'] is None else F(record['error_squared'])
    def condition(self,kind,value,**labels):
        record={'kind':kind,**labels,'passed':value is True,'status':'blocked' if value is None else ('passed' if value else 'failed')}
        self.records.append(record)
        if value is not True:self.failures.append({'record':len(self.records)-1,'kind':kind,**labels,'status':record['status']})

def get(data,row,slot,component=0):
    if data is None:return None
    return data['array'][row][slot][component]

def oget(data,h,dot,slot):return None if data is None else data['values'][h,dot][slot]

def receipt_check(comparison,receipt,job,catalog_sha,directory,artifact,tools):
    require(receipt['status']=='terminal_capture' and receipt['job']==job,'terminal receipt full job identity')
    require(receipt['catalog_sha256']==catalog_sha,'exact frozen catalogue binding')
    require(receipt['inputs_unchanged'] is True and receipt['cancellation'] is None and receipt['cleanup_errors']==[],
            'saved input/cleanup/cancellation gate')
    require(receipt.get('automatic_retry',False) is False,'no automatic retry')
    require(receipt['native_case_executed'] is True and receipt['performance_qualified'] is False
            and receipt['public_generalized_numeric_domain_qualified'] is False,'capture execution/scope flags')
    require(all(receipt[key]==job[key] for key in ['total_seconds','reserve_seconds','native_cap_seconds']),
            'capture declared budget context')
    require(all(receipt['environment_additions'][key]=='1'
                for key in ['RAYON_NUM_THREADS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS']),
            'single-thread saved environment')
    for name in ['authorization_sha256','independent_source_review_sha256']:
        require(isinstance(receipt[name],str) and re.fullmatch('[0-9a-f]{64}',receipt[name]),'saved grant/review attestation '+name)
        require(receipt[name] in receipt['inputs'].values(),'grant/review hash must be in the saved guarded input map')
    require(isinstance(receipt['steps'],list) and len(receipt['steps'])==1,'one bounded child per capture')
    step=receipt['steps'][0]
    require(step['command']==receipt['command'] and step['status']=='exited' and step['returncode']==0
            and step['owned_group_gone'] is True,'successful owned-child terminal witness')
    require(not any(key in step for key in ['error','timeout','cancellation']),'no failed child fields')
    require(0<F(str(step['timeout_seconds']))<=job['native_cap_seconds'] and
            0<=F(str(receipt['elapsed_seconds']))<=job['total_seconds'],'finite saved CPU/wall budgets')
    require(0<=F(str(step['elapsed_seconds']))<=F(str(receipt['elapsed_seconds'])) and
            type(step['owned_process_group']) is int and step['owned_process_group']>0,'saved child time/ownership')
    command=receipt['command'];require(isinstance(command,list) and len(command)>4 and
        Path(command[0]).name=='taskset' and command[1:3]==['-c',str(job['cpu'])],'exact capture CPU')
    if tools:require(command[0]==tools['taskset'],'exact frozen taskset tool identity')
    arguments=command[3:];template=job['command']
    if job['kind']=='rust':
        require(artifact is not None and receipt['owned_executable_sha256']==artifact,'captured common Cargo binary digest')
        require(receipt['native_hardlink_shared_inode'] is True,'honest shared-inode native alias attribution')
        require(receipt['license_present'] is True and type(receipt['owned_executable_bytes']) is int
                and receipt['owned_executable_bytes']>0,'captured native/license metadata')
        require(arguments[0]==str(directory.resolve()/'owned-executable'),'exact owned native alias')
        require(arguments[1:]==template[1:],'exact Rust fixture/request/output arguments')
    else:
        require(Path(arguments[0]).name.startswith('python'),'fixed Python oracle command')
        if tools:require(arguments[0]==tools['python'],'exact frozen Python tool identity')
        require(len(arguments)==len(template),'complete oracle arguments')
        # The guarded script is copied into this case directory; all remaining
        # arguments, including the preparation source, must be byte-identical.
        require(arguments[1]==str(directory.resolve()/'owned-oracle.py'),'exact owned oracle script attribution')
        require(arguments[2:]==template[2:],'exact oracle catalogue/preparation/output arguments')
    outputs=receipt['outputs'];require(isinstance(outputs,dict) and 'result.json' in outputs
        and sum(name.endswith('.log') for name in outputs)==1,'saved result and one child log output binding')
    for name,digest in outputs.items():
        require(Path(name).name==name and name not in ['owned-executable','frozen-tests','frozen-example'],
                'output inventory must contain only small saved files')
        raw=comparison.read(directory/name)
        require(hashlib.sha256(raw).hexdigest()==digest,'saved output payload hash '+name)

def compare(catalog_path,capture_root):
    report=Comparison();catalog=report.load(catalog_path);catalog_sha=report.read_files[str(catalog_path)]['sha256']
    expected=expected_job_keys();require(len(expected)==33,'fixed mandatory job count')
    jobs=catalog['jobs'];require(isinstance(jobs,list) and len(jobs)==33,'all 33 catalogue entries mandatory')
    bindings=catalog.get('bindings',{})
    if bindings:
        require(bindings.get(str(Path(__file__).resolve()))==hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'this saved comparator must match the frozen source binding')
    require([job['id'] for job in jobs]==[row[0] for row in expected],'fixed complete job set/order')
    for job,(identity,kind,mode,h,dot,bits) in zip(jobs,expected):
        require(job['kind']==kind,'catalogue job kind')
        if kind=='rust':
            require((job['mode'],job['h'],job['dot'],job['working_bits'])==(mode,h,dot,bits),'catalogue finite Rust domain')
            require(job['expected_rows']==MODES[mode][0] and job['expected_components']==MODES[mode][1]
                    and job['expected_invalid_lane']==MODES[mode][2],'catalogue sample/derivative layout')
            require(job['requested_bits']==80 and job['cpu']==(20 if bits==128 else 21),'frozen precision/CPU request')
            require(all(type(job[key]) is int for key in ['h','working_bits','requested_bits','cpu','expected_rows','expected_components']),
                    'strict integer catalogue Rust metadata')
            require(job['dot'] is None if dot is None else type(job['dot']) is int,'strict catalogue dot index')
        else:
            order,digits=ORDERS[[row[0] for row in expected[-3:]].index(identity)]
            require(job['order']==order and job['digits']==digits and job['cpu']==22,'fixed oracle grid/digits/CPU')
    artifact=None;artifact_bytes=None;build_review=None
    try:
        built=report.load(capture_root/'build-001/receipt.json')
        require(built['status']=='passed' and re.fullmatch('[0-9a-f]{64}',built['artifact_sha256']), 'successful frozen Cargo build receipt')
        require(built['catalog_sha256']==catalog_sha and built['job']==catalog['build'] and built['inputs_unchanged'] is True,
                'common build catalogue/guard context')
        artifact=built['artifact_sha256'];artifact_bytes=built['artifact_bytes'];build_review=built['independent_source_review_sha256']
    except Exception as error:
        report.failures.append({'kind':'build_attestation','error':type(error).__name__+': '+str(error)})
    rust={};oracles={};attestations=set()
    for job in jobs:
        directory=capture_root/job['id'];record={'id':job['id'],'kind':job['kind'],'complete':False}
        try:
            receipt=report.load(directory/'receipt.json');document=report.load(directory/'result.json')
            payload_sha=report.read_files[str(directory/'result.json')]['sha256']
            record['raw_payload_status']=document.get('status')
            receipt_check(report,receipt,job,catalog_sha,directory,artifact,catalog.get('tools',{}))
            require(payload_sha==receipt['outputs']['result.json'],'parsed payload bound to saved result hash')
            require(receipt['driver_status']==document['status'],'receipt/payload terminal status agreement')
            attestations.add((receipt['authorization_sha256'],receipt['independent_source_review_sha256']))
            if job['kind']=='rust':
                require(receipt['owned_executable_bytes']==artifact_bytes,'same captured native byte count as admitted build')
                data=parse_rust(document,job);rust[job['mode'],job['h'],job['dot'],job['working_bits']]=data
                record.update(complete=True,valid_rows=MODES[job['mode']][0]-(MODES[job['mode']][2] is not None),
                              components=MODES[job['mode']][1],saved_component_precision_histogram=data['precision_histogram'],
                              actual_charts=document['actual_chart_omitted_rows_from_diagnostics'],
                              execution=document['execution'],certificate_execution=document['certificate_execution'],
                              captured_native_sha256=receipt['owned_executable_sha256'],
                              captured_native_bytes=receipt['owned_executable_bytes'],native_hardlink_shared_inode=True,
                              input_values_and_precision_preserved=True,signed_zero_preservation_checked=False)
            else:
                data=parse_oracle(document,job)
                if bindings:
                    require(document['oracle_source_sha256']==bindings[str((HERE/'oracle.py').resolve())],
                            'captured oracle script matches admitted source')
                oracles[job['order']]=data;record.update(complete=True,nodes=document['nodes_evaluated'])
        except Exception as error:
            record['error']=type(error).__name__+': '+str(error)
            report.failures.append({'kind':'capture','id':job['id'],'error':record['error']})
        report.cases.append(record)
    reviews={review for grant,review in attestations}
    if len(reviews)!=1 or (build_review is not None and reviews!={build_review}):
        report.failures.append({'kind':'inconsistent_or_missing_source_review_attestations','count':len(reviews)})
    preparation_path=capture_root/'scalar-h1-unit-Float256/result.json'
    preparation_sha=report.read_files.get(str(preparation_path),{}).get('sha256')
    for order,data in oracles.items():
        prep=data['document']['symbolica_preparation']
        if prep['sha256']!=preparation_sha or Path(prep['path'])!=preparation_path.resolve():
            report.failures.append({'kind':'oracle_preparation_payload_binding','order':order})
    finest=oracles.get(20)
    all_requests=[(0,None)]+REQUESTS
    for coarse,fine in [(12,16),(16,20)]:
        for h,dot in all_requests:
            d=4+2*h-2*(5+(dot is not None))
            for slot in range(4):
                report.gate('oracle_refinement',oget(oracles.get(coarse),h,dot,slot),oget(oracles.get(fine),h,dot,slot),
                            d,threshold=ORACLE2,coarse=coarse,fine=fine,h=h,dot=dot,slot=slot)
    for h,dot in REQUESTS:
        d=4+2*h-2*(5+(dot is not None))
        for bits in [128,256]:
            data=rust.get(('scalar',h,dot,bits))
            for slot in range(4):
                base=get(data,0,slot)
                report.gate('scalar_base_oracle',base,oget(finest,h,dot,slot),d,h=h,dot=dot,bits=bits,slot=slot)
                report.gate('scalar_scale_identity',get(data,1,slot),None if base is None else times(base,F(2)**d),
                            d,q2=F(144),h=h,dot=dot,bits=bits,slot=slot)
                report.gate('scalar_translation_identity',get(data,3,slot),base,d,h=h,dot=dot,bits=bits,slot=slot)
                report.gate('scalar_repeat_exact',get(data,4,slot),base,d,threshold=F(0),h=h,dot=dot,bits=bits,slot=slot)
    for mode in MODES:
        families=REQUESTS if mode=='scalar' else [(0,None),(1,None)]
        for h,dot in families:
            rows,components,invalid=MODES[mode];left=rust.get((mode,h,dot,128));right=rust.get((mode,h,dot,256))
            d=4+2*h-2*(5+(dot is not None))
            for row in range(rows):
                if row==invalid:continue
                for slot in range(4):
                    for component in range(components):
                        q2=natural_q2(input_rows(mode)[0][row],components)
                        report.gate('precision_pair',get(left,row,slot,component),get(right,row,slot,component),d-2*component,
                                    q2=q2,threshold=PAIR2,mode=mode,h=h,dot=dot,row=row,slot=slot,component=component)
            for bits in [128,256]:
                data=rust.get((mode,h,dot,bits))
                for row in range(rows):
                    if row==invalid:continue
                    for slot in range(3):
                        for component in range(components):
                            q2=natural_q2(input_rows(mode)[0][row],components)
                            report.gate('positive_F_pole_exact',get(data,row,slot,component),(F(0),F(0)),d-2*component,
                                        q2=q2,threshold=F(0),mode=mode,h=h,dot=dot,bits=bits,row=row,slot=slot,component=component)
    fd_diagnostics=[]
    for h in [0,1]:
        d=4+2*h-10
        for bits in [128,256]:
            jets=rust.get(('mass-jets',h,None,bits));fd=rust.get(('finite-difference',h,None,bits))
            for row in [0,1,2,3,4,6]:
                i=0 if row==6 else row;dot=rust.get(('scalar',h,i,bits))
                for slot in range(4):
                    report.gate('massjet_primal_oracle',get(jets,row,slot,0),oget(finest,h,None,slot),d,h=h,bits=bits,row=row,slot=slot)
                    derivative=get(jets,row,slot,1)
                    report.gate('massjet_derivative_dot',derivative,get(dot,0,slot),d-2,h=h,bits=bits,row=row,mass=i,slot=slot)
                    report.gate('massjet_derivative_oracle',derivative,oget(finest,h,i,slot),d-2,h=h,bits=bits,row=row,mass=i,slot=slot)
            for slot in range(4):
                for component in [0,1]:
                    report.gate('massjet_repeat_exact',get(jets,6,slot,component),get(jets,0,slot,component),d-2*component,
                                threshold=F(0),h=h,bits=bits,slot=slot,component=component)
                report.gate('FD_base_oracle',get(fd,0,slot),oget(finest,h,None,slot),d,h=h,bits=bits,slot=slot)
            for i in range(5):
                dot=rust.get(('scalar',h,i,bits))
                for slot in range(4):
                    derivatives=[]
                    for offset,exponent in [(0,12),(2,16)]:
                        low=get(fd,1+4*i+offset,slot);high=get(fd,2+4*i+offset,slot)
                        derivatives.append(None if low is None or high is None else times(minus(high,low),F(2**exponent,2)))
                    coarse,fine=derivatives
                    richardson=None if coarse is None or fine is None else times(minus(times(fine,256),coarse),F(1,255))
                    rust_ref=get(dot,0,slot);oracle_ref=oget(finest,h,i,slot)
                    report.gate('FD_Richardson_dot',richardson,rust_ref,d-2,h=h,bits=bits,mass=i,slot=slot)
                    report.gate('FD_Richardson_oracle',richardson,oracle_ref,d-2,h=h,bits=bits,mass=i,slot=slot)
                    diagnostic={'h':h,'bits':bits,'mass':i,'slot':slot,'dimension':d-2}
                    for name,reference in [('Rust_dot',rust_ref),('oracle',oracle_ref)]:
                        if coarse is None or fine is None or reference is None:
                            diagnostic[name]={'coarse_error_squared':None,'fine_error_squared':None,'fine_improves':None}
                        else:
                            ce=squared_error(coarse,reference,d-2,F(36));fe=squared_error(fine,reference,d-2,F(36))
                            diagnostic[name]={'coarse_error_squared':str(ce),'fine_error_squared':str(fe),
                                'coarse_error':show_squared(ce),'fine_error':show_squared(fe),'fine_improves':fe<=ce}
                    diagnostic['coarse_derivative']=None if coarse is None else list(map(str,coarse))
                    diagnostic['fine_derivative']=None if fine is None else list(map(str,fine))
                    diagnostic['Richardson_derivative']=None if richardson is None else list(map(str,richardson))
                    fd_diagnostics.append(diagnostic)
                    if slot==3:
                        values=diagnostic['Rust_dot'];ce,fe=values['coarse_error_squared'],values['fine_error_squared']
                        passed=None if ce is None else F(fe)<=F(ce) or (F(fe)<=PAIR2 and F(ce)<=PAIR2)
                        report.condition('FD_finite_refinement',passed,h=h,bits=bits,mass=i,
                            coarse_error_squared=ce,fine_error_squared=fe,precision_floor_squared=str(PAIR2),
                            oracle_monotonicity_is_diagnostic_only=True)
    require(len(report.records)==2064 and len(fd_diagnostics)==80,'complete fixed comparison gate inventory')
    counts={'mandatory_jobs':33,'complete_jobs':sum(case['complete'] for case in report.cases),
            'complete_Rust_jobs':len(rust),'complete_oracle_jobs':len(oracles),
            'mandatory_numeric_records':len(report.records),'numeric_passed':sum(record['passed'] for record in report.records),
            'numeric_failed_or_blocked':sum(not record['passed'] for record in report.records),
            'FD_coarse_fine_slot_diagnostics':len(fd_diagnostics)}
    passed=not report.failures and counts['complete_jobs']==33
    return {'schema_version':1,'status':'passed_restricted_planar_scalar_numeric_gates' if passed else 'failed_or_inconclusive_planar_scalar_numeric_gates',
        'catalog_sha256':catalog_sha,'comparator_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'capture_root':str(capture_root),'counts':counts,'cases':report.cases,'records':report.records,
        'failures':report.failures,'finite_difference_diagnostics':fd_diagnostics,'read_saved_files':report.read_files,
        'thresholds_squared_exact':{'direct':str(DIRECT2),'precision_pair':str(PAIR2),'oracle_refinement':str(ORACLE2)},
        'scope':'All eleven generalized scalar requests at one positive-F planar point, scale/translation/invalid/repeat controls, two first-order unit mass-jet contexts and their finite differences; frozen saved build only.',
        'arithmetic':'Fraction acceptance; Decimal square-root display only; no pole merging/projection',
        'artifact_sha256_attestation':artifact,'native_bytes_rehashed':False,'authorization_review_attestations':list(map(list,sorted(attestations))),
        'multiple_exact_phase_grants_allowed':True,
        'root_grant_provenance_independently_audited_by_this_comparator':False,
        'scoped_numeric_gates_passed':passed,'independent_numeric_review_completed':False,
        'public_generalized_numeric_domain_qualified':False,'rigorous_quadrature_error_bound':False,
        'performance_qualified':False,'new_native_integral_or_symbolic_execution':False,
        'automatic_retry_refinement_or_failed_case_exclusion':False}

def self_test():
    controls=[]
    def rejects(name,function):
        try:function()
        except (ValueError,TypeError,KeyError,ZeroDivisionError):controls.append({'name':name,'passed':True})
        else:raise ValueError('synthetic invalid input accepted: '+name)
    rejects('duplicate JSON keys',lambda:decode('{"a":1,"a":2}'))
    rejects('JSON NaN',lambda:decode('{"a":NaN}'))
    rejects('numeric Infinity',lambda:rational('Infinity'))
    rejects('bool is not an exact integer',lambda:rational(True))
    rejects('null complex pair',lambda:pair(None))
    rejects('short complex pair',lambda:pair(['0']))
    valid={'real':'1/3','imaginary':'-2/7','real_precision':127,'imaginary_precision':128}
    require(complex_slot(valid,128)==(F(1,3),F(-2,7)),'exact parser positive control')
    controls.append({'name':'lower propagated component precision accepted','passed':True})
    for name,changes in [('missing component',{'imaginary':None}),('nonfinite component',{'real':'NaN'}),
                         ('precision zero',{'real_precision':0}),('precision exceeds working bits',{'real_precision':129})]:
        value={**valid,**changes};rejects(name,lambda value=value:complex_slot(value,128))
    for mode,shape in MODES.items():
        rows,labels=input_rows(mode)
        require(len(rows)==len(labels)==shape[0] and all(len(row)==26*shape[1] for row in rows),'synthetic axis shape')
    controls.append({'name':'sample rows and derivative components kept distinct','passed':True})
    require(DIRECT2==F('1e-10')**2 and PAIR2==F(1,2**80)**2 and ORACLE2==F('1e-12')**2,'amplitude squares exact')
    controls.append({'name':'exact amplitude squared thresholds','passed':True})
    require(squared_error((F(0),F(-1)),(F(0),F(1)),-6,F(36))>DIRECT2,'sign flip control')
    controls.append({'name':'mass derivative sign reversal fails','passed':True})
    require(plus((F(1),F(0)),(F(-1),F(0)))==(0,0) and norm2((F(1),F(0)))>0,'separate pole control')
    controls.append({'name':'nonzero cancelling poles remain individually visible','passed':True})
    # A complete synthetic metadata envelope tests parser rejection paths. Its
    # finite values are intentionally zero mock data, never an integral oracle.
    job={'mode':'scalar','h':1,'dot':None,'working_bits':128,'requested_bits':80,
         'command':['{owned_executable}','synthetic-fixture.json']}
    rows,labels=input_rows('scalar')
    numeric=lambda value:{'real':str(value),'imaginary':'0','real_precision':128,'imaginary_precision':128}
    before=[numeric(value) for row in rows for value in row]
    status='InvalidInput("planar coordinate determinant synthetic rejection")'
    prefix='exact full-Taylor planar identity with regular constant-one chart omitting coordinate row 0'
    witnesses=[]
    for tokens in SAMPLES:
        u,v,w,z=map(F,tokens);a,b,c=1-u,1-v,1-w
        xs=(u,a*v,a*b*w,a*b*c*z,a*b*c*(1-z));f=sum(x*m for x,m in zip(xs,MASSES))
        for i in range(5):
            for j in range(i+1,5):
                f+=xs[i]*xs[j]*sum((POINTS[i][mu]-POINTS[j][mu])**2 for mu in [1,2,3])
        witnesses.append({'cube':list(tokens),'simplex':list(map(str,xs)),'F':str(f),'jacobian':str(a**3*b**2*c)})
    document={'schema_version':1,'status':'completed_with_expected_lane_controls',
        'interface':'CertifiedPlanarReductionPlan and CertifiedPlanarWorkspace','fixture':'synthetic-fixture.json',
        'dimension_shift':1,'dot':None,'mode':'scalar','working_bits':128,'requested_bits':80,
        'components':1,'dual_shape':None,'basis':[[0,0,0,0]],'native_slots':POLES,
        'expected_invalid_lane':2,'row_labels':labels,'settings':{'propagators':5,'rank':0,'powers':[1]*5,
          'dimension_shift':1,'algorithm':'Ibp','invariants':'FromShifts','input_policy':'Preserve',
          'convention':'IregiNative','tensor_weights':'Components'},
        'normalization':'IregiNative i*pi^(2+h), separate Laurent slots; no pole projection',
        'timings_are_performance_evidence':False,'full_generalized_domain_qualified':False,'genuine_E6_evaluated':False,
        'input_jet_provider':'Symbolica derivative and exact substitution; reduction/master jets use the core Symbolica Dualizer',
        'input_exact_rational':[[[str(value),'0'] for value in row] for row in rows],
        'input_before_numeric':before,'input_after_numeric':deepcopy(before),
        'input_values_and_precision_preserved':True,'signed_zero_preservation_checked':False,
        'lane_statuses':['Success','Success',status,'Success','Success'],'fallback_used':[False]*5,
        'analytic_used':[True,True,False,True,True],'diagnostics':[[prefix],[prefix],[],[prefix],[prefix]],
        'actual_chart_omitted_rows_from_diagnostics':[0,0,None,0,0],
        'lanes':[{'row':row,'status':status if row==2 else 'Success',
                  'slots':None if row==2 else [[numeric(F(0))] for _ in range(4)]} for row in range(5)],
        'execution':{'input_rows':5,'argument_rows':8,'master_family_batches':1,'master_rows':4,
          'pentagon_box_rows':0,'reduction_rows':4,'fallback_rows':0,'fallback_successes':0,'analytic_rows':4},
        'certificate_execution':{'input_rows':5,'evaluated_rows':9,'passes':2,'reduction_batches':1},
        'oracle_preparation':{'schema_version':1,'algebra_provider':'Symbolica',
          'cube_variable_order':['u','v','w','z'],'simplex_variable_order':['x0','x1','x2','x3','x4'],
          'F_expression':'synthetic provenance string, never interpreted',
          'jacobian_expression':'synthetic provenance string, never interpreted','evaluations':witnesses}}
    parse_rust(document,job)
    controls.append({'name':'complete synthetic Rust envelope accepted structurally only','passed':True})
    for name,mutate in [
        ('invalid lane carries values',lambda x:x['lanes'][2].update(slots=[[numeric(F(0))] for _ in range(4)])),
        ('sample and derivative axes conflated',lambda x:x.update(dual_shape=[[0],[1]])),
        ('input precision changed after reduction',lambda x:x['input_after_numeric'][0].update(real_precision=127)),
        ('valid lane missing derivative component',lambda x:x['lanes'][0]['slots'].__setitem__(0,[])),
        ('wrong actual chart',lambda x:x['actual_chart_omitted_rows_from_diagnostics'].__setitem__(0,1)),
        ('truncated sample array',lambda x:x['lanes'].pop()),
        ('nonpreserved exact input',lambda x:x['input_exact_rational'][0][0].__setitem__(0,'1'))]:
        changed=deepcopy(document);mutate(changed)
        rejects(name,lambda changed=changed:parse_rust(changed,job))
    pole=Comparison();pole.gate('synthetic_nonzero_pole',(F(1),F(0)),(F(0),F(0)),-4,threshold=F(0))
    require(pole.records[0]['actual']==['1','0'] and pole.records[0]['passed'] is False,
            'raw nonzero pole must fail without projection')
    controls.append({'name':'nonzero pole retained and exact-zero gate fails','passed':True})
    return {'status':'passed_synthetic_parser_arithmetic_controls_only','controls':controls,
            'actual_capture_read':False,'integrals_or_native_executed':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',type=Path,default=HERE/'catalog.json')
    parser.add_argument('--capture-root',type=Path,default=DEFAULT_ROOT)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--self-test',action='store_true',help='synthetic parser/arithmetic checks only, no saved captures')
    args=parser.parse_args()
    if args.self_test:print(json.dumps(self_test(),indent=2,sort_keys=True));return 0
    require(args.output is not None and not args.output.exists(),'a new --output path is required; preserve prior comparisons')
    try:result=compare(args.catalog,args.capture_root)
    except Exception as error:
        result={'schema_version':1,'status':'failed_or_inconclusive_planar_scalar_numeric_gates',
                'failures':[{'kind':'catalog_or_global_metadata','error':type(error).__name__+': '+str(error)}],
                'scoped_numeric_gates_passed':False,'public_generalized_numeric_domain_qualified':False,
                'automatic_retry_refinement_or_failed_case_exclusion':False,'new_native_integral_or_symbolic_execution':False}
    with args.output.open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
    print(json.dumps({'status':result['status'],'output':str(args.output),
                      'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))
    return 0 if result['status']=='passed_restricted_planar_scalar_numeric_gates' else 2

if __name__=='__main__':raise SystemExit(main())
