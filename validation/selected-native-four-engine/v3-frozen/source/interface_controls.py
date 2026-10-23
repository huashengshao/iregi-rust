"""Saved-data initialization admission controls; no child process or numerical kernel."""
from pathlib import Path
import copy,json
import admission_v3 as a
import preparation as p

def main():
    source=a.HERE/'initialization-order-diagnostic/attempt001/raw.jsonl'
    assert a.sha(source)=='c5395738f01bbf91e14b6041d152706dee3ebe3d7c25bcbcb4d11d8a8816b9fc'
    historical=[json.loads(line)for line in source.read_text().splitlines()]
    cases=a.read(a.ROOT/'validation/native-master-replay/inputs.json')
    q=a.read(a.HERE/'qualification-001/results.json')
    raw=[]
    for serial,(case,batch,repeat)in enumerate(p.coordinates(cases)):
        saved=historical[20+serial]
        assert saved['process']=='B'and saved['request']['id']==case['id']and saved['request']['batch']==batch and saved['request']['repeat']==repeat
        raw.append({'serial':serial,'stage':'initialization','kind':'initialization','engine':'bothTIRust','id':case['id'],'batch':batch,'repeat':repeat,'response':saved['response']})
    raw.append({'serial':16,'stage':'before','kind':'controls','engine':'bothTIRust','response':historical[36]['response']})
    receipt={'initialization':{'status':'passed','schedule':p.SCHEDULE,'raw_serials':list(range(16))}}
    assert p.validate_initialization(receipt,raw,q,cases)==list(range(16))
    mutations=[
      ('missing_initialization',lambda r,x:r.pop('initialization')),
      ('failed_initialization',lambda r,x:r['initialization'].update(status='failed')),
      ('wrong_schedule',lambda r,x:r['initialization'].update(schedule='controls-first')),
      ('boolean_serial_list',lambda r,x:r['initialization']['raw_serials'].__setitem__(0,False)),
      ('boolean_raw_serial',lambda r,x:x[0].update(serial=False)),
      ('boolean_repeat',lambda r,x:x[0].update(repeat=False)),
      ('boolean_batch',lambda r,x:x[0].update(batch=True)),
      ('float_raw_serial',lambda r,x:x[0].update(serial=0.)),
      ('float_repeat',lambda r,x:x[0].update(repeat=0.)),
      ('float_batch',lambda r,x:x[0].update(batch=1.)),
      ('wrong_control_serial',lambda r,x:x[16].update(serial=17)),
      ('wrong_control_engine',lambda r,x:x[16].update(engine='candidateTIRust')),
      ('missing_serial',lambda r,x:r['initialization']['raw_serials'].pop()),
      ('duplicate_serial',lambda r,x:r['initialization']['raw_serials'].__setitem__(1,0)),
      ('reordered_serials',lambda r,x:r['initialization']['raw_serials'].reverse()),
      ('missing_response',lambda r,x:x.pop()),
      ('early_control',lambda r,x:x[0].update(kind='controls')),
      ('wrong_raw_serial',lambda r,x:x[0].update(serial=1)),
      ('wrong_stage',lambda r,x:x[0].update(stage='before')),
      ('wrong_engine',lambda r,x:x[0].update(engine='candidateTIRust')),
      ('wrong_case',lambda r,x:x[0].update(id='other')),
      ('wrong_batch',lambda r,x:x[0].update(batch=32)),
      ('wrong_repeat',lambda r,x:x[0].update(repeat=1)),
      ('wrong_initial_control_stage',lambda r,x:x[16].update(stage='after')),
      ('changed_rational',lambda r,x:x[0]['response']['baseline']['lanes'][0]['represented'][3][1].update(rational='1')),
      ('changed_status',lambda r,x:x[0]['response']['baseline']['lanes'][0].update(status='failed')),
      ('changed_fallback',lambda r,x:x[0]['response']['baseline']['lanes'][0].update(fallback_used=True)),
      ('nonempty_timing',lambda r,x:x[0]['response']['baseline'].update(total_ns=[1],elapsed_ns=[1],iterations=1)),
      ('missing_master_capture',lambda r,x:x[0]['response']['baseline']['master_captures'].pop()),
    ]
    checks=[]
    for name,mutate in mutations:
        rr=copy.deepcopy(receipt);xx=copy.deepcopy(raw);mutate(rr,xx)
        try:p.validate_initialization(rr,xx,q,cases)
        except(AssertionError,KeyError,TypeError,ValueError):checks.append({'mutation':name,'rejected':True})
        else:raise AssertionError(name)
    old=a.read(a.V2/'interface-controls.json');parent=a.read(a.HERE/'admission-controls.json')
    assert old['status']=='passed'and parent['status']=='passed'
    record={'status':'passed','scope':'saved-data initialization parser checks; no numerical kernels','positive_initialization_responses':16,'mutations':checks,'historical_collier_controls_sha256':a.sha(a.V2/'interface-controls.json'),'historical_parent_controls_sha256':a.sha(a.HERE/'admission-controls.json'),'source_sha256':{str(f):a.sha(f)for f in [Path(__file__),a.V3/'preparation.py',a.V3/'admission_v3.py',a.V2/'admission_v2.py',a.HERE/'admission.py',source,a.HERE/'qualification-001/results.json']}}
    (a.V3/'interface-controls.json').write_text(json.dumps(record,indent=2)+'\n')
    print('16 saved initialization responses accepted;29 malformed controls rejected')
if __name__=='__main__':main()
