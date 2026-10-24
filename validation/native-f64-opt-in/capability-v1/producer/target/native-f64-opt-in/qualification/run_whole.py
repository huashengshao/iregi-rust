"""One bounded untimed whole-array/reference qualification; no benchmark mode."""
from pathlib import Path
import datetime,hashlib,json,os,sys
import admission as a
from lifecycle import Budget,digest,freeze_binary
from interactive import Session,close_all
ROOT=Path.cwd();HERE=ROOT/'target/native-f64-opt-in/qualification'
def read(path):return json.loads(Path(path).read_text())
def save(path,obj):Path(path).write_text(json.dumps(obj,indent=2)+'\n')
def rust_request(case,samples):
    return json.dumps({'id':case['id'],'n':case['n'],'rank':case['rank'],'algorithm':'Hybrid','samples':samples})+'\n'
def coordinates(cases):return[(case,batch)for case in cases for batch in [1,32]]

def main():
    assert len(sys.argv)==3,'observation-build-id qualification-id'
    build_path=HERE/('observation-build-'+sys.argv[1])/'build.json';build=read(build_path)
    assert build['status']=='passed'and build['stage']=='observation'
    folder=HERE/('whole-qualification-'+sys.argv[2]);folder.mkdir(exist_ok=False)
    prep=read(HERE/'observation-preparation.json');bindings={Path(path):value for path,value in build['input_sha256'].items()}
    assert bindings[Path(__file__).resolve()]==digest(__file__),'runner differs from frozen build input'
    bindings[build_path]=digest(build_path)
    probe=build['outputs']['selective-probe'];bindings[Path(probe['path'])]=probe['sha256']
    reference=prep['reference'];bindings[ROOT/reference['path']]=reference['sha256']
    cases=read(ROOT/prep['whole_inputs']);assert len(cases)==4
    coords=coordinates(cases);assert len(coords)==8 and len({(c['id'],b)for c,b in coords})==8
    inventory=read(HERE/'control-inventory.json')['controls']
    record={'status':'preparing','scope':'private public-policy correctness only; no performance qualification','runtime_cap_seconds':120,
      'build_receipt':str(build_path),'build_receipt_sha256':digest(build_path),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_sha256':{str(path):value for path,value in bindings.items()},
      'rows':[{'id':case['id'],'batch':batch,'status':'unrun'}for case,batch in coords],
      'controls':{'status':'unrun'},'retained_rows':[{'id':case['id'],'batch':batch,'status':'unrun'}for case,batch in coords],
      'invalid_request_controls':{'status':'unrun'},'processes':[],'executed_executables':{},'cleanup_errors':[],
      'license_environment_present':any('SYMBOLICA'in name and'LICENSE'in name for name in os.environ)}
    save(folder/'results.json',record);budget=Budget(120);sessions=[];raw=None;serial=0
    def verify():
        for path,value in bindings.items():budget.remaining();assert digest(path)==value,'changed input: '+str(path)
    def ask(session,payload,stage,key):
        nonlocal serial
        serial+=1;item={'serial':serial,'stage':stage,'key':key,'engine':session.label,'payload':payload}
        raw.write(json.dumps({**item,'event':'request'})+'\n');raw.flush()
        response=session.request(payload,budget)
        raw.write(json.dumps({**item,'event':'response','response':response})+'\n');raw.flush()
        return response
    budget.arm()
    try:
        verify();raw=(folder/'responses.jsonl').open('x')
        for label,source,expected in [('TIRust',Path(probe['path']),probe['sha256']),('IREGI',ROOT/reference['path'],reference['sha256'])]:
            frozen=freeze_binary(source,expected,folder/(label+'-frozen'),budget);bindings[frozen]=expected
            record['executed_executables'][label]={'path':str(frozen),'sha256':expected};save(folder/'results.json',record)
            session=Session(label);sessions.append(session)
            session.start(frozen,prep['tools']['taskset']['path'],folder,budget,lambda event:(record['processes'].append(event),save(folder/'results.json',record)))
        current,oracle=sessions;initial={}
        for index,(case,batch)in enumerate(coords):
            row=record['rows'][index];row['status']='running';save(folder/'results.json',record)
            key=[case['id'],batch];samples=case['samples'][:batch];payload=rust_request(case,samples)
            response=ask(current,payload,'initial',key);row['comparison']=a.validate_response(response,case,samples)
            repeated=ask(current,payload,'own-repeat',key);a.validate_response(repeated,case,samples)
            assert a.canonical(response)==a.canonical(repeated),'own complete response differs'
            ref=ask(oracle,a.h.fortran_request(case,samples,'Hybrid',0,1),'reference',key)
            assert ref['id']==case['id']and ref['stable']is True
            comparisons={policy:a.h.compare(response[policy],ref,case,samples)for policy in ['baseline','candidate']}
            assert all(value['status']=='passed'for value in comparisons.values()),comparisons
            row.update(status='passed',reference_comparisons=comparisons);initial[tuple(key)]=response;save(folder/'results.json',record)
        control=ask(current,'CONTROLS\n','controls',['controls',0]);record['controls']=a.validate_controls(control,inventory);save(folder/'results.json',record)
        repeated=ask(current,'CONTROLS\n','controls-repeat',['controls',1]);a.validate_controls(repeated,inventory)
        assert control==repeated,'complete controls changed on own repeat'
        for index,(case,batch)in enumerate(coords):
            key=[case['id'],batch];samples=case['samples'][:batch]
            response=ask(current,rust_request(case,samples),'retained',key);a.validate_response(response,case,samples)
            assert a.canonical(response)==a.canonical(initial[tuple(key)]),'retained complete response changed'
            record['retained_rows'][index]['status']='passed';save(folder/'results.json',record)
        bad=[];first,sample=coords[0];base=json.loads(rust_request(first,first['samples'][:sample]))
        for field,value in [('engine','baseline'),('warmup',1),('repeats',1),('iterations',1)]:
            response=ask(current,json.dumps({**base,field:value})+'\n','invalid-request',[field,value])
            assert response=={'status':'invalid_request','error':'qualification is untimed; engine and timing counts are forbidden'}
            bad.append({'field':field,'value':value,'status':'passed'})
        record['invalid_request_controls']={'status':'passed','cases':bad};record['status']='completed-awaiting-cleanup'
    except Exception as error:record.update(status='failed',error=repr(error))
    finally:
        record['process_terminals']=close_all(sessions,budget,record['cleanup_errors'])
        if raw is not None:
            try:raw.close()
            except Exception as error:record['cleanup_errors'].append('raw close: '+repr(error))
        record['request_count']=serial;record['elapsed_seconds']=budget.elapsed();record['deadline_exceeded']=record['elapsed_seconds']>120
        save(folder/'results.json',record)
    try:
        verify();record['inputs_unchanged']=True
        record['raw_sha256']=digest(folder/'responses.jsonl')
        record['stderr_sha256']={session.label:digest(folder/(session.label+'.stderr.log'))for session in sessions}
        record['stdout_sha256']={session.label:digest(folder/(session.label+'.stdout.log'))for session in sessions}
    except Exception as error:record.update(inputs_unchanged=False,guard_error=repr(error))
    record['elapsed_seconds']=budget.elapsed();record['deadline_exceeded']|=record['elapsed_seconds']>120
    passed=all(row['status']=='passed'for row in record['rows']+record['retained_rows'])and record['controls']['status']=='passed'and record['invalid_request_controls']['status']=='passed'
    passed=passed and len(record['process_terminals'])==2 and all(p['returncode']==0 and p['owned_group_gone']for p in record['process_terminals'])
    passed=passed and record.get('inputs_unchanged')is True and not record['cleanup_errors']and not record['deadline_exceeded']and'error'not in record and not budget.cancelled and serial==38
    record['status']='passed-awaiting-independent-raw-validation'if passed else'failed'
    record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(folder/'results.json',record);budget.disarm()
    print(json.dumps({'status':record['status'],'elapsed_seconds':record['elapsed_seconds'],'request_count':serial}))
    return 0 if passed else 1
if __name__=='__main__':sys.exit(main())
