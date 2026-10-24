"""Actual current-Cargo provenance adapter for the UNCHANGED saved-data gates."""
from pathlib import Path
import hashlib,json,math,re
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
BUILD=HERE.parent
FIXTURE=ROOT/'validation/public-highpoint/fixture-conditioned_masses.json'
REFERENCE=ROOT/'validation/public-highpoint/reference-conditioned_masses.json'
SHARED=ROOT/'validation/public-highpoint/compare_public.py'
RUNS={'list':'list-001','exact':'exact-001','128':'public-rank3-128-001','256':'public-rank3-256-001'}
BOUNDS={'list':40,'exact':240,'128':120,'256':120}
ENVIRONMENT={'RAYON_NUM_THREADS':'1','RUST_TEST_THREADS':'1','IREGI_PREPARATION_PROFILE':'1','IREGI_PV_PREPARATION_PROFILE':'1'}
def require(condition,message):
    if not condition:raise ValueError(message)
def load(path):return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def key(path):
    path=Path(path).resolve()
    try:return str(path.relative_to(ROOT))
    except ValueError:return str(path)
def absolute(name):return Path(name) if Path(name).is_absolute() else ROOT/name
def bind(path,inputs,expected=None):
    name=key(path);digest=sha(absolute(name));require(expected is None or digest==expected,'changed input: '+name)
    require(name not in inputs or inputs[name]==digest,'conflicting binding: '+name);inputs[name]=digest;return digest
def final_verify(inputs):
    for name,digest in inputs.items():require(sha(absolute(name))==digest,'changed input: '+name)
def save(path,record):Path(path).write_text(json.dumps(record,indent=2,default=str)+'\n')
def protocol():
    p=load(HERE/'protocol.json');require(p['status']=='frozen_pending_root_runtime_grant','unexpected runtime proposal status')
    require(p['context']=='actual_current_locked_cargo_not_private_extern_build','wrong artifact context')
    require(p['owned_group_helper_sha256']==sha(HERE/'lifecycle.py')=='c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824','owned-group helper differs')
    require(p['comparator_sha256']==sha(HERE/'compare.py')=='5e786bc33b23e96cf71e4c16250e5eed08427f93dc887b35fa85e3facf7cdad3','unchanged comparison gate differs')
    selection=load(HERE/'selection.json');require(selection==p['selection'],'test selection changed')
    require(sum(len(g['names']) for g in selection['exact_groups'])==len({n for g in selection['exact_groups'] for n in g['names']})==34,'selected membership differs')
    require(p['bounds_seconds']==BOUNDS and p['postwork_reserve_seconds']==20,'runtime bounds differ')
    return p

def prerequisites(operation):
    return {'list':[],'exact':[HERE/'list-001/membership.json',HERE/'list-001/run.json'],'128':[HERE/'exact-comparison.json'],'256':[HERE/'comparison-128.json']}[operation]
def run_inputs(operation):
    p=protocol();assert_runtime_grant(operation);inputs=dict(p['inputs']);bind(HERE/'protocol.json',inputs);bind(HERE/'runtime-grant.json',inputs)
    for path in prerequisites(operation):
        r=load(path);bind(path,inputs)
        require(r.get('passed') is True or r.get('status')=='passed','prior current-Cargo stage failed: '+str(path))
        for name,digest in r.get('input_sha256',r.get('inputs',{})).items():bind(absolute(name),inputs,digest)
    final_verify(inputs);return inputs

def run_commands(operation,p):
    start=['taskset','-c','14'];tests=str(HERE/'bin/current-tests');example=str(HERE/'bin/current-six_point');out=HERE/RUNS[operation]
    if operation=='list':return [start+[tests,'--list','--format','terse']]
    if operation=='exact':return [start+[tests,g['filter'],'--test-threads=1','--nocapture'] for g in p['selection']['exact_groups']]
    require(operation in ['128','256'],'unknown operation');return [start+[example,key(FIXTURE),'6','3','pv',operation,'53','1',str(out/'result.json')]]

def validate_owned_steps(record,bound,reserve):
    require(record.get('cleanup_errors')==[] and record.get('postwork_reserve_seconds')==reserve,'cleanup/reserve failure')
    require(not any(record.get(k) for k in ['cancellation','postguard_cancellation','postguard_error','error']),'failed terminal receipt')
    groups=[]
    for step in record['steps']:
        pgid=step.get('owned_process_group');groups.append(pgid)
        require(type(pgid) is int and pgid>0 and step.get('owned_group_gone') is True,'owned group remains')
        require(step.get('status')=='exited' and step.get('returncode')==0 and not any(step.get(k) for k in ['timeout','error','cancellation']),'runtime child failed')
        require(type(step.get('timeout_seconds')) in [int,float] and 0<step['timeout_seconds']<=bound-reserve,'child consumed postwork reserve')
        require(type(step.get('elapsed_seconds')) in [int,float] and math.isfinite(step['elapsed_seconds']) and 0<=step['elapsed_seconds']<=bound,'invalid child time')
        require(type(step.get('group_existed_at_cleanup')) is bool,'cleanup check absent')
    require(len(groups)==len(set(groups)),'owned process group reused')
def validate_run(operation):
    require(operation in RUNS,'unknown run');p=protocol();expected=run_inputs(operation);out=HERE/RUNS[operation];r=load(out/'run.json');inputs=dict(expected);bind(out/'run.json',inputs)
    require(r['inputs']==expected and r['operation']==operation and r['bound_seconds']==BOUNDS[operation],'run provenance differs')
    require(r['status']=='passed' and r['inputs_unchanged'] is True and r['environment_additions']==ENVIRONMENT,'runtime failed/changed environment')
    require([s['command'] for s in r['steps']]==run_commands(operation,p),'runtime commands differ')
    validate_owned_steps(r,BOUNDS[operation],20)
    require(math.isfinite(r['elapsed_seconds']) and 0<=r['elapsed_seconds']<=BOUNDS[operation],'run exceeded bound')
    names={f'step-{i}.log' for i in range(len(r['steps']))}
    if operation in ['128','256']:names.add('result.json')
    if operation=='list':names.add('membership.json')
    require(set(r['outputs'])==names,'runtime output inventory differs')
    for name,digest in r['outputs'].items():bind(out/name,inputs,digest)
    return {'record':load(out/'result.json') if operation in ['128','256'] else None,'run':r,'input_sha256':inputs,'protocol':{'exact_groups':p['selection']['exact_groups']}}

# This validator is copied byte-for-byte from the qualified V2 source below.
def validate_test_log(text,names):
    require(re.findall(r'^running (\d+) tests?$',text,re.M)==[str(len(names))],'test start count differs')
    completed=[];pending=None
    for line in text.splitlines():
        m=re.match(r'^test ([A-Za-z0-9_:]+) \.\.\.\s*(.*)$',line)
        if m:
            require(pending is None,'unfinished previous test');pending,tail=m.groups()
            if tail=='ok':completed.append(pending);pending=None
            elif tail in ['FAILED','ignored']:raise ValueError('failed/ignored exact test')
        elif line.strip()=='ok':
            require(pending is not None,'unbound test completion');completed.append(pending);pending=None
    require(pending is None and len(completed)==len(names) and set(completed)==set(names),'test membership differs')
    require(re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; \d+ filtered out;',text,re.M)==[(str(len(names)),'0','0','0')],'test summary differs')


def assert_runtime_grant(operation):
    g=load(HERE/'runtime-grant.json')
    require(g['status']=='root_approved_runtime' and g['protocol_sha256']==sha(HERE/'protocol.json'),'runtime protocol has no matching root grant')
    require(operation in g['operations'] and g['bounds_seconds'][operation]==BOUNDS[operation],'operation is not granted')
    require(g['numerical_lease_released'] is True,'prior numerical lease not released')
    return g
