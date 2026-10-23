"""One bounded untimed schedule experiment. Never import to launch a run."""
from pathlib import Path
import datetime, hashlib, importlib.util, json, math, os, signal, struct, sys, time
ROOT=Path.cwd(); HERE=ROOT/'target/selected-native-optimized'; D=HERE/'initialization-order-diagnostic'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
write=lambda p,v:Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')

def differences(a,b,path=''):
    """JSON-pointer paths; do not normalize numeric values or signed zero."""
    if type(a) is not type(b): return [{'path':path,'before':a,'after':b,'kind':'type'}]
    if isinstance(a,dict):
        result=[]
        for k in sorted(a.keys()|b.keys()):
            p=path+'/'+k.replace('~','~0').replace('/','~1')
            if k not in a or k not in b:result.append({'path':p,'before_present':k in a,'after_present':k in b,'before':a.get(k),'after':b.get(k),'kind':'key'})
            else:result.extend(differences(a[k],b[k],p))
        return result
    if isinstance(a,list):
        if len(a)!=len(b):return [{'path':path,'before':a,'after':b,'kind':'length'}]
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in differences(x,y,path+'/'+str(i))]
    same=struct.pack('>d',a)==struct.pack('>d',b) if isinstance(a,float) else a==b
    return [] if same else [{'path':path,'before':a,'after':b,'kind':'value'}]

def main():
    started=time.monotonic();deadline=started+120
    assert len(sys.argv)==3,'usage: run.py attempt001 CPU'
    attempt,cpu=sys.argv[1],int(sys.argv[2]); assert attempt=='attempt001'
    out=D/attempt;out.mkdir(exist_ok=False)
    manifest=read(D/'preparation.json')
    bindings={Path(k):v for k,v in manifest['guard_sha256'].items()}
    bindings[D/'preparation.json']=sha(D/'preparation.json')
    record={'status':'pending','scope':'untimed schedule diagnostic only; no timing admission','cpu':cpu,'cap_seconds':120,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guard_sha256':{str(k):v for k,v in bindings.items()},'processes':[],'requests':[],'exact_comparisons':[],'observed_exact_differences':0,'numeric_admission_failures':0,'current_production_source_equality_claimed':False}
    proc=None
    raw=(out/'raw.jsonl').open('x');write(out/'receipt.json',record)
    def verify():
        for p,v in bindings.items():
            assert time.monotonic()<deadline,'diagnostic cap exhausted during guards'
            assert sha(p)==v,f'changed bound artifact: {p}'
    def alarm(_signum,_frame):raise TimeoutError('fixed120-second diagnostic cap reached')
    signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,max(.001,deadline-time.monotonic()))
    try:
        verify()
        spec=importlib.util.spec_from_file_location('frozen_selected_admission',HERE/'admission.py')
        a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);h=a.h
        qualified=read(HERE/'qualification-001/results.json');assert qualified['status']=='passed'
        inventory=read(HERE/'control-inventory.json')['controls']
        cases=read(ROOT/'validation/native-master-replay/inputs.json');assert len(cases)==4
        prior={(r['id'],r['outer_batch']):r for r in qualified['rows']};assert len(prior)==8
        plan=[]
        for name,schedule in [('A',['C','C','K','C','C']),('B',['K','C','C','K','C'])]:
            requests=[]
            for stage,kind in enumerate(schedule):
                if kind=='C':requests.append({'kind':'controls','stage':stage,'key':'controls','payload':'CONTROLS\n'})
                else:
                    for case in cases:
                        for batch in [1,32]:
                            for repeat in [0,1]:
                                payload=h.rust_request(case,case['samples'][:batch],'Hybrid',0,1)
                                decoded=json.loads(payload);assert 'engine' not in decoded and decoded['warmup']==0
                                requests.append({'kind':'case','stage':stage,'key':case['id']+'/'+str(batch),'id':case['id'],'batch':batch,'repeat':repeat,'payload':payload})
            plan.append((name,requests))
        assert sum(len(r) for _,r in plan)==55
        for name,requests in plan:
            record['requests'].extend({'process':name,**r,'status':'pending'} for r in requests)
        os.sched_setaffinity(0,{cpu});previous={};serial=0
        for name,requests in plan:
            process_record={'name':name,'status':'running','exit_code':None};record['processes'].append(process_record)
            proc=h.Process(HERE/'build-001/probe',name,out,max(.001,deadline-time.monotonic()))
            own={}
            for request in requests:
                planned=record['requests'][serial];assert planned['process']==name
                remaining=deadline-time.monotonic();assert remaining>0,'diagnostic cap exhausted'
                proc.timeout=remaining
                response=proc.request(request['payload'])
                raw.write(json.dumps({'serial':serial,'process':name,'request':request,'response':response},allow_nan=False)+'\n');raw.flush()
                planned['status']='received';planned['serial']=serial
                try:
                    if request['kind']=='controls':
                        admission=a.validate_controls(response,inventory)
                        canonical=response;old=qualified['controls']
                    else:
                        case=next(c for c in cases if c['id']==request['id']);samples=case['samples'][:request['batch']]
                        admission=a.validate_response(response,case,samples)
                        for engine in ['baseline','candidate']:
                            assert response[engine]['total_ns']==response[engine]['elapsed_ns']==[] and response[engine]['iterations']==0
                            comparison=h.compare(response[engine],prior[(case['id'],len(samples))]['reference'],case,samples)
                            assert comparison['status']=='passed',comparison
                            admission[engine+'_saved_iregi']=comparison
                        canonical=a.canonical(response);old=a.canonical(prior[(case['id'],len(samples))]['response'])
                    planned['admission']={'status':'passed','detail':admission}
                except Exception as error:
                    planned['admission']={'status':'failed','error':repr(error)};record['numeric_admission_failures']+=1
                    canonical=response;old=qualified['controls'] if request['kind']=='controls' else prior[(request['id'],request['batch'])]['response']
                comparisons=[('saved_qualification',None,old)]
                if request['key'] in own:comparisons.append(('within_process_first',own[request['key']][0],own[request['key']][1]))
                if request['key'] in previous:comparisons.append(('across_process_first',previous[request['key']][0],previous[request['key']][1]))
                for scope,other,value in comparisons:
                    delta=differences(value,canonical)
                    record['exact_comparisons'].append({'serial':serial,'other_serial':other,'scope':scope,'key':request['key'],'exactly_equal':not delta,'differences':delta})
                    record['observed_exact_differences']+=len(delta)
                own.setdefault(request['key'],(serial,canonical));serial+=1
                write(out/'receipt.json',record)
            for key,value in own.items():previous.setdefault(key,value)
            proc.close();process_record.update(status='completed',exit_code=proc.process.returncode);proc=None
            assert process_record['exit_code']==0,'nonzero diagnostic child exit'
        assert serial==55
        record['status']='completed_with_observations'
    except Exception as error:
        record.update(status='failed_or_incomplete',error=repr(error))
    finally:
        if proc is not None:
            if proc.process.poll() is None:proc.process.kill();proc.process.wait()
            proc.close();record['processes'][-1].update(status='terminated_or_failed',exit_code=proc.process.returncode)
        raw.close()
        try:verify();record['guards_unchanged']=True
        except Exception as error:record.update(status='failed_or_incomplete',guards_unchanged=False,guard_error=repr(error))
        signal.setitimer(signal.ITIMER_REAL,0)
        record.update(elapsed_seconds=time.monotonic()-started,raw_sha256=sha(out/'raw.jsonl'),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        write(out/'receipt.json',record)
    print(json.dumps({k:record[k] for k in ['status','elapsed_seconds','observed_exact_differences','numeric_admission_failures','raw_sha256']}))
    return 0 if record['status']=='completed_with_observations' and record['numeric_admission_failures']==0 else 1
if __name__=='__main__':sys.exit(main())
