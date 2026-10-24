"""Independent saved-response qualification; never launches or times a kernel."""
from pathlib import Path
import hashlib,json,math,sys
import admission as a
ROOT=Path.cwd();HERE=ROOT/'target/native-f64-opt-in/qualification'
def read(path):return json.loads(Path(path).read_text())
def digest(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def payload(case,samples):return json.dumps({'id':case['id'],'n':case['n'],'rank':case['rank'],'algorithm':'Hybrid','samples':samples})+'\n'
def exact(left,right):return json.dumps(left,sort_keys=True,allow_nan=False)==json.dumps(right,sort_keys=True,allow_nan=False)
def schedule(cases):
    rows=[]
    for case in cases:
        for batch in [1,32]:
            key=[case['id'],batch];samples=case['samples'][:batch];text=payload(case,samples)
            rows.extend([('TIRust','initial',key,text),('TIRust','own-repeat',key,text),('IREGI','reference',key,a.h.fortran_request(case,samples,'Hybrid',0,1))])
    rows.extend([('TIRust','controls',['controls',0],'CONTROLS\n'),('TIRust','controls-repeat',['controls',1],'CONTROLS\n')])
    for case in cases:
        for batch in [1,32]:rows.append(('TIRust','retained',[case['id'],batch],payload(case,case['samples'][:batch])))
    first=cases[0];base=json.loads(payload(first,first['samples'][:1]))
    for field,value in [('engine','baseline'),('warmup',1),('repeats',1),('iterations',1)]:
        rows.append(('TIRust','invalid-request',[field,value],json.dumps({**base,field:value})+'\n'))
    assert len(rows)==38
    return rows

def qualify(record,events,cases,inventory):
    """Reject missing/extra/reordered pairs and reconstruct numerical checks."""
    assert record['status']=='passed-awaiting-independent-raw-validation'
    assert record['runtime_cap_seconds']==120 and record['request_count']==38
    assert record['inputs_unchanged']is True and record['deadline_exceeded']is False
    assert record['cleanup_errors']==[]and'error'not in record and'guard_error'not in record
    assert type(record['elapsed_seconds'])in[int,float]and math.isfinite(record['elapsed_seconds'])and 0<=record['elapsed_seconds']<=120
    terminals=record['process_terminals'];assert len(terminals)==2
    assert [item['label']for item in terminals]==['TIRust','IREGI']
    assert all(type(item['returncode'])is int and item['returncode']==0 and item['owned_group_gone']is True for item in terminals)
    assert len(record['processes'])==2
    for launched,terminal,label in zip(record['processes'],terminals,['TIRust','IREGI']):
        assert launched['label']==terminal['label']==label and launched['status']=='running'
        group=launched['owned_process_group'];assert type(group)is int and group>0
        assert terminal['owned_process_group']==group
        assert terminal['received_responses']==(30 if label=='TIRust'else 8)
    assert record['processes'][0]['owned_process_group']!=record['processes'][1]['owned_process_group']
    assert len(cases)==4 and len(events)==76
    admitted={};checks=[];whole_controls=None
    expected=schedule(cases);case_map={case['id']:case for case in cases}
    assert len(case_map)==4
    for serial,(engine,stage,key,text)in enumerate(expected,1):
        request,response=events[2*(serial-1):2*serial]
        for event,kind in [(request,'request'),(response,'response')]:
            assert event['event']==kind and type(event['serial'])is int and event['serial']==serial
            assert event['engine']==engine and event['stage']==stage and event['key']==key and event['payload']==text
            assert set(event)=={'event','serial','engine','stage','key','payload'}|({'response'}if kind=='response'else set())
        result=response['response']
        if stage in ['initial','own-repeat','retained']:
            case=case_map[key[0]];samples=case['samples'][:key[1]]
            check=a.validate_response(result,case,samples)
            if stage=='initial':admitted[tuple(key)]=result;checks.append({'id':key[0],'batch':key[1],**check})
            else:assert exact(a.canonical(result),a.canonical(admitted[tuple(key)])),'own complete record drift'
        elif stage=='reference':
            case=case_map[key[0]];samples=case['samples'][:key[1]]
            assert result['id']==key[0]and result['stable']is True
            comparisons={policy:a.h.compare(admitted[tuple(key)][policy],result,case,samples)for policy in ['baseline','candidate']}
            assert all(item['status']=='passed'for item in comparisons.values())
            checks[-1]['reference_comparisons']=comparisons
        elif stage=='controls':
            controls=a.validate_controls(result,inventory);whole_controls=result
        elif stage=='controls-repeat':
            a.validate_controls(result,inventory);assert exact(result,whole_controls),'own complete controls drift'
        else:
            assert result=={'status':'invalid_request','error':'qualification is untimed; engine and timing counts are forbidden'}
    expected_keys=[(case['id'],batch)for case in cases for batch in [1,32]]
    assert len(checks)==8 and list(admitted)==expected_keys
    for field in ['rows','retained_rows']:
        assert len(record[field])==8
        assert [(item['id'],item['batch'])for item in record[field]]==expected_keys
        assert all(item['status']=='passed'for item in record[field])
    for actual,derived in zip(record['rows'],checks):
        assert exact(actual['comparison'],{key:derived[key]for key in ['whole_cross_backend','masters']})
        assert exact(actual['reference_comparisons'],derived['reference_comparisons'])
    assert exact(record['controls'],controls)
    assert record['invalid_request_controls']=={'status':'passed','cases':[{'field':field,'value':value,'status':'passed'}for field,value in [('engine','baseline'),('warmup',1),('repeats',1),('iterations',1)]]}
    return {'status':'passed','scope':'saved-data full numerical admission; no new numerical evaluation or timing','requests':38,'responses':38,'whole_cases':checks,'controls':controls,'own_repeats_and_retained_records':'all complete records exact in current process','invalid_timing_request_controls':4}

def main():
    assert len(sys.argv)==2,'qualification-id'
    folder=HERE/('whole-qualification-'+sys.argv[1]);record_path=folder/'results.json';record=read(record_path)
    # Guard the executed source/closure as well as the saved record and raw bytes.
    prep_path=HERE/'observation-preparation.json';prep=read(prep_path)
    build_path=Path(record['build_receipt']);assert digest(build_path)==record['build_receipt_sha256']
    build=read(build_path);assert build['status']=='passed'and build['stage']=='observation'
    expected={**prep['input_sha256'],str(prep_path):digest(prep_path)}
    assert build['input_sha256']==expected,'build/preparation source closure mismatch'
    expected.update({str(build_path):digest(build_path),build['outputs']['selective-probe']['path']:build['outputs']['selective-probe']['sha256'],str(ROOT/prep['reference']['path']):prep['reference']['sha256']})
    assert record['input_sha256']==expected,'runtime input closure differs from compiled source bindings'
    assert record['executed_executables']['TIRust']['sha256']==build['outputs']['selective-probe']['sha256']
    assert record['executed_executables']['IREGI']['sha256']==prep['reference']['sha256']
    for path,value in record['input_sha256'].items():assert digest(path)==value,path
    for label,item in record['executed_executables'].items():assert digest(item['path'])==item['sha256'],label
    assert set(record['executed_executables'])=={'TIRust','IREGI'}
    raw=folder/'responses.jsonl';assert digest(raw)==record['raw_sha256']
    for label,value in record['stderr_sha256'].items():assert digest(folder/(label+'.stderr.log'))==value
    assert set(record['stderr_sha256'])=={'TIRust','IREGI'}
    for item in record['processes']:
        expected_command=[prep['tools']['taskset']['path'],'-c','22',record['executed_executables'][item['label']]['path']]
        assert item['command']==expected_command,'launched command differs from frozen protocol'
    assert set(record['stdout_sha256'])=={'TIRust','IREGI'}
    emitted={}
    for label,value in record['stdout_sha256'].items():
        path=folder/(label+'.stdout.log');assert digest(path)==value
        data=path.read_bytes();assert not data or data.endswith(b'\n'),'unfinished stdout line'
        emitted[label]=[json.loads(line[7:])for line in data.splitlines()if line.startswith(b'RESULT ')]
    assert str(Path(__file__).resolve())in record['input_sha256']
    events=[json.loads(line)for line in raw.read_text().splitlines()]
    for label in ['TIRust','IREGI']:
        captured=[event['response']for event in events if event['event']=='response'and event['engine']==label]
        assert exact(emitted[label],captured),'stdout RESULT count/order differs from captured raw records'
    result=qualify(record,events,read(ROOT/prep['whole_inputs']),read(HERE/'control-inventory.json')['controls'])
    result.update(raw_sha256=digest(raw),producer_receipt_sha256=digest(record_path),validator_sha256=digest(__file__),admission_sha256=digest(HERE/'admission.py'))
    with(folder/'independent-admission.json').open('x')as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'whole_cases':len(result['whole_cases']),'responses':result['responses']}))
if __name__=='__main__':main()
