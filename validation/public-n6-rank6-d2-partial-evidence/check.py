#!/usr/bin/env python3
"""Portable stdlib D2 partial/failure replay; never imports a numerical producer."""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import tarfile

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PARENT='validation/checked-g-generalized-core-tests'
PARENT_MANIFEST='ee4bc172dd8b87e3242158afacab425e6b13376f72dd3fbb6678feb701a97417'
LOW='target/affine-power-post-memo-current-d2'
HIGH='target/affine-power-post-memo-current-d2-pair'
ROOT_PREFIX='/shared/external/iregi/iregi-rust/'
LOW_PROTOCOL='e0435bf805c9d7be5689ea547f761316d04c9054276a32bfe725b860d61034da'
HIGH_PROTOCOL='6d4351b385e0e843a81dec78f9772c34727651e15ecba3c2e1902117ded79800'
HIGH_RECEIPT='f4e9f3fd7ac1f7fa6fd675c2d0a10d69ebda8d9d70c21e5be0659463a6e817f0'
HIGH_STDOUT='2a7c9154293f445c09ca96fcf5a2c4b8c123047888ffba62b76440ed27e63040'
FAILURE_AUDIT='a641e9a5ab95129a848c7c13e916e923cae1e6d0de5af622831d9db99673c071'
LOW_RECEIPT='471087ff9f76f1e6aa952bcdad02541940041b12af11345d9ae87184d8400c11'
LOW_AUDIT='6e4a1b01c9d664bb4b31426fcae44ff802c58364f33870cd0045516bcfbd392f'
CLI='0b28ce2428f7719da1acf9eee9584365d2a6bf62f83ee63db950d30b2b0bc58d'
REFERENCE='f237bb6a7a136b0582f654949688b5b13402677f3e566bf930c170f116ecef92'
SAMPLE='af124aadf35699c35799fee5332a563cd8641e499a9f11cdbbd64e3dab3c1f5b'
ADMISSION='ad13acbb025596760232afb309ec993ab0c71f8538a49cf414c83bf4478bccfe'
REFERENCE_AUDIT='6f7fcc3ac1fe9702c2a581c9d764f1c36b452475673da0ea74e9544390933bcc'
REQUEST='0d148e3eee18fd977778baa144617ab8081d236f2f8233f820e7899c738b5429'


def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(raw):return {'sha256':sha(raw),'bytes':len(raw)}
def alias(path):return str(path).removeprefix(ROOT_PREFIX)
def parse(raw):
    def unique(items):
        result={}
        for key,value in items:need(key not in result,'duplicate JSON key');result[key]=value
        return result
    def nonfinite(v):raise ValueError('nonfinite JSON '+v)
    return json.loads(raw,object_pairs_hook=unique,parse_float=str,parse_constant=nonfinite)
def safe(name):
    p=Path(name);need(name and not p.is_absolute()and'..'not in p.parts and str(p)==name,'unsafe byte alias')
def scan(name,raw):
    safe(name)
    need(Path(name).suffix not in ['.o','.mod','.smod','.pyc','.so','.a','.dll','.dylib']and'__pycache__'not in Path(name).parts,'compiled/cache payload')
    need(not raw.startswith((b'\x7fELF',b'!<arch>',b'MZ')),'native payload')
    need(re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}',raw)is None,'license literal payload')
def strings(value):
    if isinstance(value,str):yield value
    elif isinstance(value,dict):
        for v in value.values():yield from strings(v)
    elif isinstance(value,list):
        for v in value:yield from strings(v)
def complex_pair(pair):
    pattern=r'[+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?'
    need(type(pair)is list and len(pair)==2 and all(type(v)is str and re.fullmatch(pattern,v.strip())for v in pair),'complete finite decimal complex pair')
    return tuple(F(v)for v in pair)
def basis():return [[t,x,y,r-t-x-y]for r in range(7)for t in range(r,-1,-1)for x in range(r-t,-1,-1)for y in range(r-t-x,-1,-1)]
def display(square):
    with localcontext()as c:c.prec=80;return str((Decimal(square.numerator)/Decimal(square.denominator)).sqrt())


def restore(manifest,root):
    """Inherit only the existing seven-file parent; restore no external target tree."""
    pm_path=root/PARENT/'manifest.json';need(sha(pm_path.read_bytes())==PARENT_MANIFEST,'frozen central source parent')
    pm=parse(pm_path.read_bytes())
    expected_parent={PARENT+'/'+name:witness for name,witness in pm['capsule_files'].items()}
    expected_parent[PARENT+'/manifest.json']=desc(pm_path.read_bytes())
    need(manifest['parent_files']==expected_parent,'exact seven-file parent inventory')
    for name,witness in manifest['parent_files'].items():
        safe(name);need(desc((root/name).read_bytes())==witness,'parent capsule file '+name)
    spec=importlib.util.spec_from_file_location('d2_partial_parent_saved_checker',root/PARENT/'check.py')
    parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
    inherited=parent.restore_files(pm)
    parent.replay(inherited,pm)
    actual={p.name for p in HERE.iterdir()}
    need(actual==set(manifest['capsule_files'])|{'manifest.json'}and all(p.is_file()and not p.is_symlink()for p in HERE.iterdir()),'closed regular child capsule inventory')
    for name,witness in manifest['capsule_files'].items():
        raw=(HERE/name).read_bytes();scan(name,raw);need(desc(raw)==witness,'child file '+name)
    members={}
    with tarfile.open(fileobj=io.BytesIO((HERE/'payload.tar.gz').read_bytes()),mode='r:gz')as archive:
        for entry in archive:
            need(entry.isfile()and entry.name not in members,'unique regular payload member')
            raw=archive.extractfile(entry).read();scan(entry.name,raw)
            need(desc(raw)==manifest['payload_members'].get(entry.name),'payload member identity')
            members[entry.name]=raw
    need(set(members)==set(manifest['payload_members']),'closed payload member set')
    files=dict(inherited)
    for name,row in manifest['preserved_files'].items():
        safe(name);raw=members[row['member']]
        need(desc(raw)=={k:row[k]for k in['sha256','bytes']},'own byte alias '+name)
        need(name not in files or files[name]==raw,'same-name inherited source collision')
        files[name]=raw
    for name,row in manifest['borrowed_files'].items():
        need(name in inherited and desc(inherited[name])==row,'exact borrowed parent byte alias')
    return files,pm


def replay(files,manifest,parent_manifest):
    """Pure saved Fraction replay over restored bytes; no process or filesystem work."""
    def raw(name,expected=None):
        name=alias(name);need(name in files,'missing saved alias '+name);value=files[name]
        need(expected is None or sha(value)==expected,'exact saved pin '+name);return value
    def load(name,expected=None):return parse(raw(name,expected))
    need(manifest['schema_version']==1 and manifest['status']=='source_bound_saved_D2_Float128_pass_Float256_failure'
         and manifest['parent_manifest_sha256']==PARENT_MANIFEST and manifest['compiled_source_count']==158
         and manifest['compiled_source_parent_context']=='build-003'and manifest['cli_sha256']==CLI
         and manifest['D6_hold']is True and manifest['performance_qualified']is False and manifest['public_Dual_qualified']is False
         and manifest['finite_reference_independently_certified']is False and manifest['new_native_hash_or_process_probe']is False
         and manifest['source_and_process_provenance_historical']is True and manifest['Float256_qualified']is False
         and manifest['precision_pair_qualified']is False,'explicit closed qualification scope')
    need(manifest['source_epoch']=='CLI003-pre-Gh-repair-source158'and manifest['current_main_equality_claimed']is False,'historical source epoch explicit')
    context=parent_manifest['source_contexts']['build-003'];need(len(context['source_files'])==158,'same158 compiled source epoch')
    built=load('target/checked-g-generalized-qualification/build-003/receipt.json','71eeca714e839be16c331ca9cf3985d9d17365be13dad04aecb6c73c6cf590cb')
    need(built['source_files']==context['source_files']and built['products']['cli']['sha256']==CLI,'CLI003 artifact/source coupling')
    for name,expected in context['source_files'].items():raw(context['source_alias_prefix']+name,expected)
    low_audit=load(LOW+'/independent-saved-audit.json',LOW_AUDIT)
    need(low_audit['status']=='passed_independent_saved_D2_Float128_audit'and low_audit['findings']==[],'independent low audit')
    review=load(manifest['independent_failure_review']['path'],manifest['independent_failure_review']['sha256'])
    need(manifest['independent_failure_review']['sha256']==FAILURE_AUDIT
         and review['status']=='passed_independent_saved_failure_audit'and review['findings']==[], 'independent failure review passed')
    need(review['numerical_outcome']=='failed_NonConvergent_no_coefficients'
         and review['high_reference_comparison']==dict(status='unrun',requested_slots=840,completed_slots=0,maximum_error=None)
         and review['strict_precision_pair_comparison']==dict(status='unrun',requested_slots=840,completed_slots=0,maximum_error=None,tolerance='2^-80')
         and review['current_absence']==dict(worker_group=True,native_pid=True)
         and review['Float256_qualified']is False and review['strict_precision_pair_qualified']is False,'independent failure audit keeps all unrun gates and absence evidence explicit')
    review_strings=set(strings(review))
    need(HIGH_PROTOCOL in review_strings and HIGH_RECEIPT in review_strings and manifest['high_receipt_sha256']==HIGH_RECEIPT,'independent review bound to actual protocol/receipt')
    admission=load('target/n6-rank6-generalized-quad/anchor-admission.json',ADMISSION)
    reference_audit=raw('target/n6-rank6-generalized-quad/independent-saved-review.json',REFERENCE_AUDIT)
    anchor=admission['records'][5]
    need(admission['status']=='admitted_scoped_original_quad_N6_rank6_generalized_references'
         and admission['independent_saved_review_sha256']==sha(reference_audit)
         and(anchor['index'],anchor['id'],anchor['h'],anchor['idim'],anchor['powers'])==(5,'n6_rank6_unit_D2',-1,-2,[1]*6)
         and anchor['raw_sha256']==REFERENCE and anchor['request_sha256']==REQUEST,'scoped original D2 anchor admission')
    need(raw(anchor['raw'],REFERENCE)==raw(LOW+'/reference.stdout',REFERENCE)
         and raw(anchor['request'],REQUEST)==raw(LOW+'/reference-request.txt',REQUEST),'exact original raw/request aliases retained')
    sample=load(LOW+'/input.json',SAMPLE)
    expected_shifts=[['0','0','0','0'],['0','1','0','0'],['0','0','1','0'],['0','0','0','1'],['1/2','0','0','0'],['0','1','1','0']]
    need(sample['rank']==6 and sample['dimension_shift']==-2 and sample['mu']=='3'and sample['mode']==0 and sample['snap']is False
         and[p['shift']for p in sample['propagators']]==expected_shifts
         and[p['mass_squared']for p in sample['propagators']]==[[m,'0']for m in['1','2','3','4','2','3']]
         and[p['power']for p in sample['propagators']]==[1]*6,'exact31 preserved EC27 D2 primals')
    reference_raw=raw(LOW+'/reference.stdout',REFERENCE);lines=reference_raw.decode().splitlines()
    need(lines.count('READY IREGI_REFERENCE_QP_V1')==1,'original reference ready')
    need([parse(v[10:])for v in lines if v.startswith('PRECISION ')]==[dict(dbl_kind=16,olo_kind=16,storage_bits=128,binary_digits=113,decimal_digits=33)],'originalquad precision witness')
    refs=[parse(v[7:])for v in lines if v.startswith('RESULT ')]
    need(len(refs)==1 and refs[0]['id']==sample['id']and refs[0]['stable']is True and refs[0].get('error')is None and refs[0]['poles']==['uv1','ir1','ir2','finite']and len(refs[0]['moments'])==210,'complete original reference identity')
    refs=refs[0]['moments'];b=basis();outputs=[];records=[];contexts=[]
    settings=dict(algorithm='Ibp',convention='IregiNative',dimension_shift=-1,input_policy='Preserve',invariants='FromShifts',powers=[1]*6,propagators=6,rank=6,tensor_weights='Components')
    for prefix,bits,protocol_pin,receipt_pin in[(LOW,128,LOW_PROTOCOL,LOW_RECEIPT)]:
        folder=prefix+'/captures/Float'+str(bits)+'-001';p=load(prefix+'/protocol.json',protocol_pin);r=load(folder+'/receipt.json',receipt_pin)
        need(p['run_order']==[bits]and p['cli_sha256']==CLI and p['requested_accuracy_bits']==53 and p['bounds']==dict(total_seconds=2580,native_child_cap_seconds=2400,cleanup_reserve_seconds=120,pre_post_work_allowance_seconds=60,cpu=20,address_space_limit_bytes=None),'fixed protocol artifact/bounds')
        need(r['status']=='passed_complete_840_native_coefficients'and r['working_bits']==bits and r['case']==sample['id']and r['inputs_unchanged']is True and r['cleanup_errors']==[]and r['cancellation']is None and r['post_cancellation']is None and r['automatic_retry']is False and r['next_native_partner_automatic']is False and F(r['elapsed_seconds'])<2580,'actual terminal native result/postguards')
        need(r['source_context']=='immutable actualCLI003 source snapshot; no current-main equality or live-source lease','native receipt historical source context')
        need(all(r[k]==p['bounds'][k]for k in p['bounds']),'actual finite execution envelope')
        need(len(r['steps'])==1,'one actual native worker')
        step=r['steps'][0];need(step['status']=='exited'and step['returncode']==0 and step['owned_group_gone']is True and F(step['elapsed_seconds'])<=step['timeout_seconds']==2400,'historical owned native completion')
        command=step['command'];need(command[:3]==['taskset','-c','20']and command[4:]==[ROOT_PREFIX+prefix+'/capture_worker.py',ROOT_PREFIX+folder+'/cli-owned',p['sample'],ROOT_PREFIX+folder,str(bits)],'actual sample/binary/controller command')
        guards=dict(p['inputs']);guards[ROOT_PREFIX+prefix+'/protocol.json']=protocol_pin;guards[ROOT_PREFIX+folder+'/cli-owned']=CLI
        controllers=['run.py','capture_worker.py','compare_saved.py','lifecycle.py','protocol.json']
        if bits==256:controllers.insert(3,'compare_pair.py')
        for name in controllers:
            witness=raw(folder+'/controller-snapshot/'+name);need(witness==raw(prefix+'/'+name),'frozen actual controller body')
            guards[ROOT_PREFIX+folder+'/controller-snapshot/'+name]=sha(witness)
        need(r['inputs']==guards,'exact all saved pre/post guard identities')
        for name,expected in r['outputs'].items():raw(folder+'/'+name,expected)
        data=load(folder+'/stdout.json',r['stdout_sha256']);comparison=load(folder+'/comparison.json',r['comparison_sha256'])
        need(r['outputs']['stdout.json']==r['stdout_sha256']and r['outputs']['comparison.json']==r['comparison_sha256'],'raw/comparison output coupling')
        need(data['schema_version']==1 and data['settings']==settings and data['basis']==b and data['precision_bits']==bits and data['algorithm_requested']==data['algorithm_used']=='Ibp'and data['poles']==['uv1','ir1','ir2','finite']and data['input_policy']=='Preserve'and len(data['samples'])==1,'same complete native tensor semantics')
        need(data['precision_control']['accuracy_bits']==53 and data['precision_control']['output_bits']==bits and data['precision_control']['rescue']is None and data['rescue_execution']=={'enabled':False},'no unobserved precision rescue')
        lane=data['samples'][0];need(lane['status']=='success'and lane['id']==sample['id']and len(lane['moments'])==210 and lane['precision_rescue']=={'status':'not_requested'}and lane['fallback_used']is False and lane['analytic_used']is True,'actual success/analytic flags retained')
        maxima={'quad_reference_slots':F(0),'positive_F_IR_zero_slots':F(0),'convergent_UV_zero_slots':F(0)};counts={k:0 for k in maxima};witnesses={k:None for k in maxima};parsed=[]
        for index,alpha in enumerate(b):
            actual=lane['moments'][index];goal=refs[index]
            need(type(actual)is list and len(actual)==4 and type(goal)is list and len(goal)==4,'all4 actual/reference slots')
            natural_squared=F(9)**(sum(alpha)-10);row=[]
            for slot in range(4):
                a=complex_pair(actual[slot]);g=complex_pair(goal[slot]);row.append(a)
                checks=[('quad_reference_slots',g)]
                if slot==0:checks.append(('convergent_UV_zero_slots',(F(0),F(0))))
                if slot in[1,2]:checks.append(('positive_F_IR_zero_slots',(F(0),F(0))))
                for kind,target in checks:
                    error=sum((a[j]-target[j])**2 for j in range(2))/max(natural_squared,sum(v*v for v in target))
                    counts[kind]+=1
                    if error>maxima[kind]:maxima[kind]=error;witnesses[kind]=[index,slot]
                    need(error<=F(1,10**20),'unchanged1e-10 full-complex quad/pole gate')
            parsed.append(row)
        need(counts==dict(quad_reference_slots=840,positive_F_IR_zero_slots=420,convergent_UV_zero_slots=210)
             and maxima['positive_F_IR_zero_slots']==maxima['convergent_UV_zero_slots']==0,'full gate counts and exact native pole zeros')
        need(comparison['status']=='passed_complete_N6_rank6_quad_comparison'and not comparison['failures']and comparison['counts']==counts and comparison['maximum_normalized_error_squared']=={k:str(v)for k,v in maxima.items()}and comparison['maximum_witnesses']==witnesses,'independent arithmetic matches actual comparator')
        for key in ['execution','engine_execution','diagnostics','preparation_notes','precision_control','rescue_execution']:
            need(comparison[key]==data[key],'saved execution/context retained '+key)
        detail=data['engine_execution'];child=detail['child_execution'];parent=detail['parent_execution']
        need(set(child)==set(parent)and all(type(v)is int and v>=0 for v in list(child.values())+list(parent.values())),'complete nonnegative native work counters')
        need(detail['engine']=='AffinePower'and(detail['profiles'],detail['dag_nodes'],detail['dag_edges'],detail['packed_child_rows'],detail['child_batch_calls'],detail['parent_batch_calls'],detail['parent_rows'],detail['quadrature_work_rows'])==(1,5,4,4,1,1,1,840),'actual four-terminal affine DAG')
        need(data['execution']=={k:1 if k=='input_rows'else child[k]+parent[k]for k in child}and detail['certificate_execution']==dict(evaluated_rows=7,input_rows=1,passes=7,reduction_batches=0),'actual summed batch/certificate counters')
        need(detail['child_methods']==[dict(actual='Ibp',notes=[],powers=[1]*5,propagators=5,requested='Ibp',rows=4)],'actual requested/used child algorithm')
        obs=[parse(line)for line in raw(folder+'/resource-observations.jsonl').splitlines()]
        need(bool(obs)and all(v['pid']==obs[0]['pid']and v['starttime_ticks']==obs[0]['starttime_ticks']and v['sampled_peak_only']is True and'unavailable'not in v and int(v['process_status']['Pid'])==v['pid']and int(v['process_status']['PPid'])==step['owned_process_group']for v in obs),'actual source-identity-coupled resource observations')
        need(all(F(a['monotonic'])<F(z['monotonic'])for a,z in zip(obs,obs[1:])),'resource chronology')
        if bits==128:need(len(obs)==70,'all70 originalFloat128 resource observations preserved')
        records.append(dict(working_bits=bits,counts=counts,maxima_squared={k:str(v)for k,v in maxima.items()},maximum_reference_error=display(maxima['quad_reference_slots']),resource_observations=len(obs),guarded_identities=len(guards),engine_execution=detail,native_elapsed_seconds=step['elapsed_seconds'],aggregate_elapsed_seconds=r['elapsed_seconds']))
        contexts.append(dict(working_bits=bits,engine_execution=detail,execution=data['execution'],diagnostics=data['diagnostics'],preparation_notes=data['preparation_notes']))
        outputs.append(parsed)
    folder=HIGH+'/captures/Float256-001'
    p=load(HIGH+'/protocol.json',HIGH_PROTOCOL);r=load(folder+'/receipt.json',HIGH_RECEIPT)
    need(p['run_order']==[256]and p['cli_sha256']==CLI and p['requested_accuracy_bits']==53
         and p['bounds']==dict(total_seconds=2580,native_child_cap_seconds=2400,cleanup_reserve_seconds=120,pre_post_work_allowance_seconds=60,cpu=20,address_space_limit_bytes=None),'fixed failed256 native envelope')
    need(r['status']=='failed_or_incomplete'and r['working_bits']==256 and r['case']==sample['id']
         and r['requested_accuracy_bits']==53 and r['inputs_unchanged']is True and r['cleanup_errors']==[]
         and r['cancellation']is None and r['post_cancellation']is None and r['automatic_retry']is False
         and r['next_native_partner_automatic']is False and F(r['elapsed_seconds'])<2580,'actual failed256 complete terminal/postguards')
    need(r['source_context']=='immutable actualCLI003 source snapshot; no current-main equality or live-source lease'
         and all(r[k]==p['bounds'][k]for k in p['bounds']),'failed256 historical source and finite bound')
    need(len(r['steps'])==1,'one actual failed256 native worker');step=r['steps'][0]
    need(step['status']=='failed'and step['returncode']==1 and step['owned_group_gone']is True
         and F(step['elapsed_seconds'])<step['timeout_seconds']==2400,'actual guard failure, not timeout or missing process')
    need(step['owned_process_group']==4118140 and step['kernel_start_identity']==dict(pid=4118140,starttime_ticks=102166507,process_group=4118140,session=4118140),'failed256 saved owned group identity')
    command=step['command']
    need(command[:3]==['taskset','-c','20']and command[4:]==[ROOT_PREFIX+HIGH+'/capture_worker.py',ROOT_PREFIX+folder+'/cli-owned',p['sample'],ROOT_PREFIX+folder,'256'],'exact failed256 native command')
    guards=dict(p['inputs']);guards[ROOT_PREFIX+HIGH+'/protocol.json']=HIGH_PROTOCOL;guards[ROOT_PREFIX+folder+'/cli-owned']=CLI
    for name in ['run.py','capture_worker.py','compare_saved.py','compare_pair.py','lifecycle.py','protocol.json']:
        witness=raw(folder+'/controller-snapshot/'+name);need(witness==raw(HIGH+'/'+name),'actual failed256 controller snapshot')
        guards[ROOT_PREFIX+folder+'/controller-snapshot/'+name]=sha(witness)
    need(r['inputs']==guards,'all failed256 input guard maps retained')
    need(set(r['outputs'])=={'stdout.json','profile.log','worker.log','resource-observations.jsonl'}
         and 'comparison_sha256'not in r and 'precision_pair_sha256'not in r,'no unrun comparison receipt invented')
    for name,expected in r['outputs'].items():raw(folder+'/'+name,expected)
    need(r['stdout_sha256']==HIGH_STDOUT and r['outputs']['stdout.json']==HIGH_STDOUT,'exact failed256 raw record')
    need(folder+'/comparison.json'not in files and folder+'/pair-comparison.json'not in files,'high reference and precision comparisons were unrun')
    data=load(folder+'/stdout.json',HIGH_STDOUT)
    need(data['schema_version']==1 and data['basis']==b and data['settings']==settings and data['precision_bits']==256
         and data['algorithm_requested']==data['algorithm_used']=='Ibp'and data['input_policy']=='Preserve'
         and data['poles']==['uv1','ir1','ir2','finite']and len(data['samples'])==1,'complete requested failed256 layout')
    need(data['precision_control']['accuracy_bits']==53 and data['precision_control']['output_bits']==256
         and data['precision_control']['rescue']is None and data['rescue_execution']=={'enabled':False},'failed256 no unobserved rescue')
    lane=data['samples'][0]
    reason='Unstable("terminal 1: Unstable(\\"E6 leaf 30: NonConvergent (quadrature order 128, box rows 1240, error estimate 2.499e-4)\\")")'
    need(set(lane)=={'analytic_used','fallback_used','id','precision_rescue','reason','status'}
         and lane['status']=='failed'and lane['id']==sample['id']and lane['reason']==reason
         and lane['analytic_used']is False and lane['fallback_used']is False
         and lane['precision_rescue']=={'status':'not_requested'},'failed256 exact Unstable reason and no moments')
    detail=data['engine_execution'];child=detail['child_execution'];parent=detail['parent_execution']
    need(detail['engine']=='AffinePower'and(detail['profiles'],detail['dag_nodes'],detail['dag_edges'],detail['packed_child_rows'],detail['child_batch_calls'],detail['parent_batch_calls'],detail['parent_rows'],detail['quadrature_work_rows'])==(1,5,4,4,1,0,0,0),'failed256 actual four-terminal DAG with parent unrun')
    need(child==dict(analytic_rows=0,argument_rows=4,fallback_rows=0,fallback_successes=0,input_rows=4,master_family_batches=5,master_rows=124,pentagon_box_rows=3040,reduction_rows=3)
         and parent=={k:0 for k in child}and data['execution']=={k:1 if k=='input_rows'else child[k]for k in child},'failed256 actual three successful child rows and all3040 box rows')
    need(detail['certificate_execution']==dict(evaluated_rows=7,input_rows=1,passes=7,reduction_batches=0)
         and detail['child_methods']==[dict(actual='Ibp',notes=[],powers=[1]*5,propagators=5,requested='Ibp',rows=4)],'failed256 certificate and child methods retained')
    diagnostics=data['diagnostics'];need(len(diagnostics)==1 and len(diagnostics[0])==7,'all seven failed256 diagnostics retained')
    rows=diagnostics[0]
    need(rows[0]=='constant-one affine power DAG chart 0, inactive [3, 4]; unchanged q, rank 6, h=-1'
         and all('terminal '+str(i)+' powers [1, 1, 1, 1, 1]: E6 leaf 30: quadrature order 64, box rows 600, error estimate 'in rows[j]for i,j in[(0,1),(2,4),(3,5)])
         and rows[2]=='terminal 1 powers [1, 1, 1, 1, 1]: E6 leaf 30: quadrature order 128, box rows 1240, error estimate 2.499e-4'
         and 'NonConvergent (quadrature order 128, box rows 1240, error estimate 2.499e-4)'in rows[3]
         and rows[6]=='terminal 1: Unstable("E6 leaf 30: NonConvergent (quadrature order 128, box rows 1240, error estimate 2.499e-4)")','exact failed terminal/order/error; other three observed converged terminals')
    obs=[parse(line)for line in raw(folder+'/resource-observations.jsonl').splitlines()]
    need(len(obs)==78 and all(v['pid']==4118145 and v['starttime_ticks']==102166511 and v['sampled_peak_only']is True
         and 'unavailable'not in v and v['process_status']['Pid']=='4118145'and v['process_status']['PPid']=='4118140'for v in obs)
         and all(F(a['monotonic'])<F(z['monotonic'])for a,z in zip(obs,obs[1:])),'all78 actual failed256 resource observations')
    high_protocol=p
    for name,pin in [('receipt.json',LOW_RECEIPT),('comparison.json','c1bef5c6e7575031337156b68df746212095dcf140114f355011ccdd1d00bdb4'),('stdout.json','fa93e137283f0a7dd1c416777ff0d2e855a30cefc43532cf9a733aa96a144723')]:
        need(high_protocol['inputs'][ROOT_PREFIX+LOW+'/captures/Float128-001/'+name]==pin,'retained fixed prior128 pins not overwritten')
    need(load(HIGH+'/prior-pin-hardening.json')['native_executed']is False,'prelaunch rejected controller retained without inventing execution')
    return {'status':'passed_portable_D2_partial_evidence_replay','qualification_state':'partial; Float128 passed, Float256 failed quadrature stability',
        'source_epoch':manifest['source_epoch'],'Float128_reference_slots_passed':840,'Float256_reference_slots_run':0,'precision_pairs_run':0,
        'Float256_reference_slots_unrun':840,'precision_pairs_unrun':840,'Float128_capture':records[0],
        'Float256_failure':{'status':lane['status'],'reason':lane['reason'],'diagnostics':diagnostics,'engine_execution':detail,
            'execution':data['execution'],'resource_observations':78,'guarded_identities':len(guards),'native_elapsed_seconds':step['elapsed_seconds'],
            'aggregate_elapsed_seconds':r['elapsed_seconds'],'moments_present':False,'receipt_status':r['status'],'returncode':1,
            'precision_control':data['precision_control'],'rescue_execution':data['rescue_execution'],'preparation_notes':data['preparation_notes']},
        'D6_hold':True,'Float256_qualified':False,'precision_pair_qualified':False,'public_Dual_qualified':False,'performance_qualified':False,
        'achieved_bits_qualified':False,'finite_reference_independently_certified':False,'current_main_equality_claimed':False,
        'process_provenance':'Historical owned terminal and independent saved absence evidence; portable replay performs no current PID probe.',
        'limitations':['Fixed real EC27 N6 rank6 unit powers/h=-1 only; Float128 empirical originalquad agreement, not defining-integral certification.',
        'Float256 stability guard failed without coefficients. Its840 reference comparisons and840 strict precision pairs remain unrun, not zero or successful.',
        'Reuses immutable CLI003/pre-Gh-repair source158 epoch; subsequent production changes are not silently qualified.',
        'No native artifacts, sourcearchive duplication, producer imports, compiler, integral or numerical dependency imports.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=HERE.parents[1]);parser.add_argument('--reconstruct',type=Path);args=parser.parse_args()
    manifest=parse((HERE/'manifest.json').read_bytes());files,parent=restore(manifest,args.root.resolve());result=replay(files,manifest,parent)
    if args.reconstruct:
        need(not args.reconstruct.exists(),'fresh reconstruction path');args.reconstruct.mkdir(parents=True)
        for name,raw in files.items():
            output=args.reconstruct/name;output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(raw)
        result['reconstructed_aliases']=len(files)
    result['manifest_sha256']=sha((HERE/'manifest.json').read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
