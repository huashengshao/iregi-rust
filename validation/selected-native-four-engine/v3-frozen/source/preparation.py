"""Explicit untimed preparation matching the original optimized qualification."""
from pathlib import Path
import admission_v3 as a
SCHEDULE='original-eight-CASE-each-immediate-repeat-before-CONTROLS'

def historical_bindings():
    d=a.HERE/'initialization-order-diagnostic'
    assert a.sha(d/'preparation.json')=='7548ed8a44f01f0fca2cf57fe82fb60d7a7694578a66a4b282225f369c10e07c'
    prior=a.read(d/'preparation.json')
    bindings={Path(p):v for p,v in prior['guard_sha256'].items()}
    for p in [d/'preparation.json',d/'attempt001/receipt.json',d/'attempt001/raw.jsonl']:
        bindings[p]=a.sha(p)
    assert bindings[d/'attempt001/raw.jsonl']=='c5395738f01bbf91e14b6041d152706dee3ebe3d7c25bcbcb4d11d8a8816b9fc'
    assert bindings[d/'attempt001/receipt.json']=='ce28d3bb4c606d6b759bfb57c9e0632db11f73b5d82240883d63a57da397cd2f'
    durable=a.ROOT/'validation/selected-native-initialization-order'
    assert a.sha(durable/'manifest.json')=='7a49e5ca89bb8ce38e8960f74b6ca3fdefc635246ca3ac8ae3911dd921a68ac0'
    bindings[durable/'manifest.json']=a.sha(durable/'manifest.json')
    for name,digest in a.read(durable/'manifest.json')['files'].items():bindings[durable/name]=digest
    return bindings

def coordinates(cases):
    assert len(cases)==4
    result=[(c,b,r)for c in cases for b in [1,32]for r in [0,1]]
    assert len(result)==16
    return result

def validate_pair(response,case,batch,q,index):
    samples=case['samples'][:batch]
    a.base.validate_response(response,case,samples)
    assert a.base.canonical(response)==a.base.canonical(q['rows'][index]['response']),'initialization own exact snapshot differs'
    for backend in ['baseline','candidate']:
        value=response[backend]
        assert value['capture_enabled'] is True and value['profiling_enabled'] is False
        assert value['total_ns']==value['elapsed_ns']==[] and value['iterations']==0,'initialization must be untimed'
        assert a.h.compare(value,q['rows'][index]['reference'],case,samples)['status']=='passed'

def prepare(request,q,cases):
    record={'status':'running','schedule':SCHEDULE,'raw_serials':[]}
    for serial,(case,batch,repeat)in enumerate(coordinates(cases)):
        response=request(a.h.rust_request(case,case['samples'][:batch],'Hybrid',0,1),
                         {'stage':'initialization','kind':'initialization','engine':'bothTIRust','id':case['id'],'batch':batch,'repeat':repeat})
        validate_pair(response,case,batch,q,serial//2)
        record['raw_serials'].append(serial)
    record['status']='passed'
    return record

def validate_initialization(receipt,raw,q,cases):
    record=receipt['initialization']
    assert record['status']=='passed' and record['schedule']==SCHEDULE
    assert type(record['raw_serials'])is list and all(type(i)is int for i in record['raw_serials'])
    assert record['raw_serials']==list(range(16)) and len(raw)>=17
    for serial,(case,batch,repeat)in enumerate(coordinates(cases)):
        rr=raw[serial]
        assert all(type(rr[k])is int for k in ['serial','batch','repeat'])
        assert rr['serial']==serial and rr['stage']==rr['kind']=='initialization'
        assert rr['engine']=='bothTIRust' and rr['id']==case['id']and rr['batch']==batch and rr['repeat']==repeat
        validate_pair(rr['response'],case,batch,q,serial//2)
    assert type(raw[16]['serial'])is int and raw[16]['serial']==16 and raw[16]['engine']=='bothTIRust'
    assert raw[16]['kind']=='controls'and raw[16]['stage']=='before','CONTROLS must follow all sixteen CASE requests'
    return list(range(16))
