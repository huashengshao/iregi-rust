"""Portable stdlib complete saved N2 rank7 check; never launches native code."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
import hashlib,io,json,tarfile,sys
HERE=Path(__file__).resolve().parent;COUNT=0

def require(ok,why):
    global COUNT
    if not ok:raise ValueError(why)
    COUNT+=1

def sha(value):return hashlib.sha256(value).hexdigest()
def describe(value):return {'sha256':sha(value),'bytes':len(value)}
def read(value):return json.loads(value)
def unpack(name,expected):
    values={}
    with tarfile.open(HERE/name,'r:gz') as tar:
        for member in tar:
            p=Path(member.name);require(member.isfile() and not p.is_absolute() and '..' not in p.parts and member.name not in values,'safe archive member')
            values[member.name]=tar.extractfile(member).read()
    require({n:describe(b) for n,b in values.items()}==expected,'closed exact archive '+name)
    return values

def restore_files(manifest=None):
    if manifest is None:manifest=read((HERE/'manifest.json').read_bytes())
    for name,digest in manifest['capsule_files'].items():require(sha((HERE/name).read_bytes())==digest,'capsule file '+name)
    sources=unpack('sources.tar.gz',manifest['sources']);records=unpack('evidence.tar.gz',manifest['evidence'])
    result={alias:(sources if item['archive']=='sources' else records)[item['member']] for alias,item in manifest['aliases'].items()}
    for name,body in sources.items():result[name]=body
    return result

def replay(files,manifest):
    root=manifest['historical_root'];prefix=root+manifest['private_prefix'];catalog=read(files[prefix+'/catalog.json']);comparison=read(files[prefix+'/comparison.json']);terminal=read(files[prefix+'/execution-001/receipt.json'])
    require(terminal['status']=='passed_restricted_N2_rank7_IBP_postfix' and not terminal['cleanup_errors'] and terminal['inputs_unchanged'] is True and not terminal['unrun_labels'] and terminal['elapsed_seconds']<660,'terminal bounded cohort')
    require(comparison['status']=='passed_restricted_fresh_Cargo_N2_IBP_rank7_postfix' and not comparison['failures'],'saved full comparison passed')
    fixture=read(files[catalog['fixture']]);require(sha(files[catalog['fixture']])==catalog['fixture_sha256'] and len(fixture['samples'])==3,'three original fixture rows')
    oracle=read(files[catalog['oracle_subset']]);require(sha(files[catalog['oracle_subset']])==catalog['oracle_subset_sha256'],'independent saved oracle identity')
    for name in ('reference_validation','reference_protocol','original_independent_saved_review'):
        item=oracle[name];require(sha(files[item['path']])==item['sha256'],'oracle provenance '+name)
    anchors={}
    for a in oracle['anchors']:
        sample=next(s for s in fixture['samples'] if s['id']==a['sample']);require(a['mode']==0 and a['native_stable'] is True and a['applicable_identities_pass'] is True and a['exact_propagators']==sample['propagators'][:2] and F(a['exact_scale'])==F(sample['mu']),'independent exact input/eligibility')
        response=a['response'];require(response['stable'] is True and response['poles']==['uv1','ir1','ir2','finite'] and len(response['moments'])==330,'full quad IBP reference')
        anchors[sample['id']]=[[tuple(map(F,z)) for z in m] for m in response['moments']]
    require(len(anchors)==3,'three reference arrays')
    basis=[[t,x,y,r-t-x-y] for r in range(8) for t in range(r,-1,-1) for x in range(r-t,-1,-1) for y in range(r-t-x,-1,-1)];require(len(basis)==330,'native basis')
    def unit2(sample,alpha):
        props=sample['propagators'][:2];scale=max(F(1),*(abs(F(p['mass_squared'][0])) for p in props));q=[F(a)-F(b) for a,b in zip(props[1]['shift'],props[0]['shift'])];scale=max(scale,abs(q[0]**2-sum(v*v for v in q[1:])));return scale**sum(alpha)
    parsed={};counts={'reference_slots':0,'precision_slots':0,'scaling_slots':0,'IR_zero_slots':0};maximums={key:F(0) for key in counts}
    def compare(a,b,unit,threshold,key):
        ratio=sum((x-y)**2 for x,y in zip(a,b))/max(unit,sum(x*x for x in b));require(ratio<=threshold,'complete saved '+key);counts[key]+=1;maximums[key]=max(maximums[key],ratio)
    for case in catalog['cases']:
        path=prefix+'/captures/'+case['id'];receipt=read(files[path+'/receipt.json']);data=read(files[path+'/result.json']);bits=case['working_bits'];require(receipt['status']=='terminal_capture' and receipt['inputs_unchanged'] is True and not receipt['cleanup_errors'] and receipt['cancellation'] is None and sha(files[path+'/result.json'])==receipt['driver_ledger_sha256'],'successful exact capture')
        require(receipt['protocol_sha256']==sha(files[prefix+'/catalog.json']) and len(receipt['steps'])==1 and receipt['steps'][0]['returncode']==0 and receipt['steps'][0]['owned_group_gone'] is True,'exact owned capture lifecycle')
        for absolute,digest in receipt['inputs'].items():
            if absolute in manifest['omitted_compiled_artifacts']:require(manifest['omitted_compiled_artifacts'][absolute]==digest,'declared exact compiled omission')
            else:require(absolute in files and sha(files[absolute])==digest,'portable captured guard '+absolute)
        require(data['settings']=={'propagators':2,'rank':7,'powers':[1,1],'dimension_shift':0,'algorithm':'Ibp','convention':'IregiNative','tensor_weights':'Components','invariants':'FromShifts','input_policy':'Preserve'},'exact requested native settings')
        require(data['algorithm_used']=='Ibp' and data['status']=='all_lanes_success' and data['working_bits']==bits and data['requested_bits']==53 and data['rows']==3 and data['components']==1 and data['basis']==basis and data['lane_statuses']==['Success']*3 and data['fallback_used']==data['analytic_used']==[False]*3 and data['diagnostics']==[[],[],[]],'complete actual IBP branch/status/basis')
        require(data['master_count']==3 and data['alias_count']==618 and data['execution']=={'input_rows':3,'argument_rows':3,'master_family_batches':2,'master_rows':9,'pentagon_box_rows':0,'reduction_rows':3,'fallback_rows':0,'fallback_successes':0,'analytic_rows':0},'actual retained work counters')
        inputs=[];lanes=[]
        for index,(sample,lane) in enumerate(zip(fixture['samples'],data['lanes'])):
            exact=[[str(F(v)),'0'] for p in sample['propagators'][:2] for v in p['shift']]+[[str(F(v)) for v in p['mass_squared']] for p in sample['propagators'][:2]]+[[str(F(sample['mu'])),'0']];inputs.append(exact)
            require(lane['row']==index and lane['status']=='Success' and len(lane['moments'])==330,'complete tensor lane')
            values=[]
            for alpha,moment,reference in zip(basis,lane['moments'],anchors[sample['id']]):
                require(len(moment)==len(reference)==4,'four Laurent slots');v=[]
                for slot,z in enumerate(moment):
                    require(set(z)=={'real','imaginary','real_precision','imaginary_precision'} and all(type(z[k]) is int and 1<=z[k]<=bits for k in ('real_precision','imaginary_precision')),'stored numeric precision metadata');a=(F(z['real']),F(z['imaginary']));v.append(a);compare(a,reference[slot],unit2(sample,alpha),F(1,10**20),'reference_slots')
                    if slot in (1,2):compare(a,(F(0),F(0)),unit2(sample,alpha),F(1,10**20),'IR_zero_slots')
                values.append(v)
            lanes.append(values)
        require(data['input_exact_rational']==inputs,'every exact input');parsed[bits]=lanes
    for row,sample in enumerate(fixture['samples']):
        for i,alpha in enumerate(basis):
            for slot in range(4):compare(parsed[128][row][i][slot],parsed[256][row][i][slot],unit2(sample,alpha),F(1,2**160),'precision_slots')
    for bits in (128,256):
        for i,alpha in enumerate(basis):
            factor=F(2)**sum(alpha)
            for slot in range(4):compare(parsed[bits][1][i][slot],tuple(v*factor for v in parsed[bits][0][i][slot]),unit2(fixture['samples'][1],alpha),F(1,2**160),'scaling_slots')
    require(counts=={'reference_slots':7920,'precision_slots':3960,'scaling_slots':2640,'IR_zero_slots':3960},'all complete counts')
    with localcontext() as ctx:
        ctx.prec=90;display={k:str((Decimal(v.numerator)/Decimal(v.denominator)).sqrt()) for k,v in maximums.items()}
    return {'status':'passed_portable_complete_N2_rank7_IBP','counts':counts,'maximum_normalized_errors':display,'checks':COUNT,'native_jobs':0,'compiler_jobs':0,'performance_qualified':False,'full_rank7_domain_qualified':False}

def main():
    m=read((HERE/'manifest.json').read_bytes());files=restore_files(m);print(json.dumps(replay(files,m)))
if __name__=='__main__':main()
