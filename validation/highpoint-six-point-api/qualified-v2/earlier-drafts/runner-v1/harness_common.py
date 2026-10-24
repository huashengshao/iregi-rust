"""Frozen source/build/run validation; no numerical producer is launched here."""
from pathlib import Path
import hashlib, json, math, re
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
CORE = HERE/'core/crates/iregi-rust'
BASELINE = PARENT/'production-baseline/crates/iregi-rust'
BUILD = HERE/'build-001'
PROTOCOL = HERE/'protocol.json'
FIXTURE = ROOT/'validation/public-highpoint/fixture-conditioned_masses.json'
REFERENCE = ROOT/'validation/public-highpoint/reference-conditioned_masses.json'
SHARED = ROOT/'validation/public-highpoint/compare_public.py'
DEPS = ROOT/'target/e6-direct-n2/deps'
NATIVE = ROOT/'target/e6-direct-n2/native'
SUPPLEMENTAL = ROOT/'target/core-fused-cse-census/supplemental-deps'
ENVIRONMENT = {'RAYON_NUM_THREADS':'1','RUST_TEST_THREADS':'1',
               'IREGI_PREPARATION_PROFILE':'1','IREGI_PV_PREPARATION_PROFILE':'1'}
OUTPUTS = ['libcandidate.rlib','tests','six_point','libbaseline.rlib','ordinary','lifecycle']
RUNS = {'exact':'exact-001','ordinary-baseline':'ordinary-baseline-001',
        'ordinary-candidate':'ordinary-candidate-001','128':'public-rank3-128-001',
        '256':'public-rank3-256-001','lifecycle':'lifecycle-001'}
BOUNDS = {'exact':180,'ordinary-baseline':120,'ordinary-candidate':120,
          '128':180,'256':180,'lifecycle':180}
EXTERNS = {'iregi_masters':DEPS/'libiregi_masters-f07797f04e91954e.rlib',
           'symbolica':DEPS/'libsymbolica-06e42762cabb77d9.rlib',
           'serde':DEPS/'libserde-b04ba25115fa19f8.rlib',
           'serde_json':DEPS/'libserde_json-d657c5438f354a41.rlib',
           'thiserror':SUPPLEMENTAL/'libthiserror-0527e2191ec3561c.rlib'}

def require(condition,message):
    if not condition: raise ValueError(message)
def load(path): return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def key(path):
    path=Path(path).resolve()
    try: return str(path.relative_to(ROOT))
    except ValueError: return str(path)
def absolute(name): return Path(name) if Path(name).is_absolute() else ROOT/name
def bind(path,inputs,expected=None):
    name=key(path); digest=sha(absolute(name))
    require(expected is None or digest==expected,f'changed input: {name}')
    require(name not in inputs or inputs[name]==digest,f'conflicting binding: {name}')
    inputs[name]=digest; return digest
def final_verify(inputs):
    for name,digest in inputs.items(): require(sha(absolute(name))==digest,f'changed input: {name}')
def save(path,record): Path(path).write_text(json.dumps(record,indent=2,default=str)+'\n')

def closure_bindings():
    result={}
    for manifest in [ROOT/'target/e6-direct-n2/preparation.json',ROOT/'target/core-fused-cse-census/supplemental-deps.json']:
        bind(manifest,result)
        for entry in load(manifest)['files']: bind(ROOT/entry['frozen'],result,entry['sha256'])
    for folder,suffixes in [(DEPS,{'.rlib','.so'}),(SUPPLEMENTAL,{'.rlib','.so'}),(NATIVE,{'.a','.so'})]:
        actual={key(p) for p in folder.rglob('*') if p.is_file() and p.suffix in suffixes}
        expected={name for name in result if absolute(name).is_relative_to(folder) and absolute(name).suffix in suffixes}
        require(actual==expected,f'extern/native inventory differs: {folder}')
    return result

def validate_protocol():
    protocol=load(PROTOCOL)
    require(protocol.get('status')=='approved_source_only' and '/root' in protocol.get('reviewers',[]),'ROOT has not approved this exact protocol')
    require(protocol['revision']==2 and protocol['build_bound_seconds']==180 and protocol['exact_expected_tests']==34,'protocol bounds/scope differ')
    groups=protocol['exact_groups'];names=[n for g in groups for n in g['names']]
    require(len(names)==len(set(names))==34,'test membership is incomplete or duplicated')
    source=load(HERE/'source.json'); baseline=load(PARENT/'baseline.json')
    current={str(p.relative_to(HERE/'core')):sha(p) for p in (HERE/'core').rglob('*') if p.is_file()}
    require(current==source['candidate_files'],'candidate source inventory changed')
    for name,digest in current.items(): require(protocol['inputs'].get(key(HERE/'core'/name))==digest,'candidate source missing from protocol')
    for name,digest in baseline['source_files'].items():
        require(sha(BASELINE/name)==digest and protocol['inputs'].get(key(BASELINE/name))==digest,'production baseline changed or omitted')
    for name,digest in closure_bindings().items(): require(protocol['inputs'].get(name)==digest,'frozen dependency omitted')
    for path in EXTERNS.values(): require(key(path) in protocol['inputs'],'explicit extern omitted')
    for name in ['harness_common.py','build.py','run.py','compare.py','compare-lifecycle.py','protocol-draft.json','source.json','source-review.json','hardening.json']:
        require(protocol['inputs'].get(key(HERE/name))==sha(HERE/name),'protocol script/review omitted')
    require(protocol['inputs'].get(key(Path(protocol['compiler_path'])))==sha(protocol['compiler_path']),'compiler is not bound')
    final_verify(protocol['inputs'])
    return protocol

def build_commands(protocol):
    common=['taskset','-c','14,15',protocol['compiler_path'],'--edition=2024','-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo',
            '-L',f'dependency={DEPS}','-L',f'dependency={SUPPLEMENTAL}','-L',f'native={NATIVE}']
    def ext(names): return [arg for name in names for arg in ['--extern',f'{name}={EXTERNS[name]}']]
    def library(name,source,metadata):
        return common+['--crate-name','iregi_rust','--crate-type','rlib','-C',f'metadata={metadata}',str(source/'src/lib.rs'),'-o',str(BUILD/name)]+ext(EXTERNS)
    def driver(name,source,extra):
        return common+['--crate-name',name,str(source),'-o',str(BUILD/name)]+ext(['symbolica','iregi_masters','serde_json'])+[arg for alias,path in extra.items() for arg in ['--extern',f'{alias}={path}']]
    return [
        ('candidate',library('libcandidate.rlib',CORE,'six_point_v2_candidate'),CORE),
        ('tests',common+['--crate-name','iregi_rust','--test','-C','metadata=six_point_v2_tests',str(CORE/'src/lib.rs'),'-o',str(BUILD/'tests')]+ext(EXTERNS),CORE),
        ('six_point',driver('six_point',CORE/'examples/six_point.rs',{'iregi_rust':BUILD/'libcandidate.rlib'}),CORE),
        ('baseline',library('libbaseline.rlib',BASELINE,'six_point_v2_baseline'),BASELINE),
        ('ordinary',driver('ordinary',PARENT/'ordinary-equivalence-driver.rs',{'baseline':BUILD/'libbaseline.rlib','candidate':BUILD/'libcandidate.rlib'}),CORE),
        ('lifecycle',driver('lifecycle',PARENT/'public-lifecycle-driver.rs',{'iregi_rust':BUILD/'libcandidate.rlib'}),CORE),
    ]

def validate_build():
    protocol=validate_protocol(); inputs=dict(protocol['inputs']);bind(PROTOCOL,inputs)
    record=load(BUILD/'build.json');bind(BUILD/'build.json',inputs)
    require(record['status']=='passed' and record['bound_seconds']==180 and record['inputs_unchanged'] is True,'build failed or changed inputs')
    expected_inputs=dict(protocol['inputs']);expected_inputs[key(PROTOCOL)]=sha(PROTOCOL)
    require(record['inputs']==expected_inputs,'build input inventory differs')
    expected=[(n,c,str(d)) for n,c,d in build_commands(protocol)]
    require([(s['name'],s['command'],s['manifest_dir']) for s in record['steps']]==expected,'build command or source differs')
    require(all(s.get('exit_code')==0 and not s.get('timeout',False) for s in record['steps']),'build has incomplete steps')
    require(type(record['elapsed_seconds']) in [int,float] and 0<=record['elapsed_seconds']<=180,'build exceeded total bound')
    require(set(record['outputs'])==set(OUTPUTS),'build outputs differ')
    for name,digest in record['outputs'].items():bind(BUILD/name,inputs,digest)
    for step in record['steps']:bind(BUILD/(step['name']+'.log'),inputs,step['log_sha256'])
    return {'record':record,'input_sha256':inputs,'protocol':protocol}

def run_commands(operation,protocol):
    out=HERE/RUNS[operation];start=['taskset','-c','14']
    if operation=='exact':return [start+[str(BUILD/'tests'),group['filter'],'--test-threads=1','--nocapture'] for group in protocol['exact_groups']]
    if operation.startswith('ordinary-'):
        return [start+[str(BUILD/'ordinary'),str(out/'result.json'),operation.removeprefix('ordinary-')]]
    if operation in ['128','256']:
        return [start+[str(BUILD/'six_point'),key(FIXTURE),'6','3','pv',operation,'53','1',str(out/'result.json')]]
    require(operation=='lifecycle','unknown operation')
    return [start+[str(BUILD/'lifecycle'),key(FIXTURE),str(out/'result.json')]]

def prerequisites(operation):
    if operation=='exact':return []
    if operation.startswith('ordinary-'):return [HERE/'exact-comparison.json']
    if operation=='128':return [HERE/'ordinary-comparison.json']
    if operation=='256':return [HERE/'comparison-128.json']
    return [HERE/'comparison-128-256.json']

def run_inputs(operation,build):
    inputs=dict(build['input_sha256'])
    for path in prerequisites(operation):
        record=load(path);bind(path,inputs)
        require(record.get('passed') is True,'prerequisite gate failed: '+str(path))
        for name,digest in record['input_sha256'].items():bind(absolute(name),inputs,digest)
    return inputs

def validate_run(operation):
    require(operation in RUNS,'unknown operation');build=validate_build();expected=run_inputs(operation,build)
    out=HERE/RUNS[operation];record=load(out/'run.json');inputs=dict(expected);bind(out/'run.json',inputs)
    require(record['operation']==operation and record['inputs']==expected,'runtime input inventory differs')
    require(record['status']=='passed' and record['bound_seconds']==BOUNDS[operation] and record['inputs_unchanged'] is True,'runtime failed, timed out or changed inputs')
    require(record['environment_additions']==ENVIRONMENT,'runtime environment differs')
    require([s['command'] for s in record['steps']]==run_commands(operation,build['protocol']),'runtime command differs')
    require(all(s.get('exit_code')==0 and not s.get('timeout',False) for s in record['steps']),'runtime child failure')
    require(type(record['elapsed_seconds']) in [int,float] and math.isfinite(record['elapsed_seconds']) and 0<=record['elapsed_seconds']<=BOUNDS[operation],'runtime bound exceeded')
    names={f'step-{i}.log' for i in range(len(record['steps']))}
    if operation!='exact':names.add('result.json')
    require(set(record['outputs'])==names,'runtime output inventory differs')
    for name,digest in record['outputs'].items():bind(out/name,inputs,digest)
    return {'record':None if operation=='exact' else load(out/'result.json'),'run':record,'input_sha256':inputs,'protocol':build['protocol']}

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
