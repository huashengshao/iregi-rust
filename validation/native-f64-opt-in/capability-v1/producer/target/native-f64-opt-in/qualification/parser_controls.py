"""Retained-data parser controls only: no Rust/Symbolica kernels or timing."""
from pathlib import Path
from copy import deepcopy
import datetime,hashlib,json,signal,sys,time
import admission as a
ROOT=Path.cwd();HERE=ROOT/'target/native-f64-opt-in/qualification'
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def main():
    folder=HERE/'parser-controls-001';folder.mkdir(exist_ok=False)
    source=ROOT/'target/selected-native-optimized/qualification-001/results.json';inventory_path=HERE/'control-inventory.json';case_path=ROOT/'validation/native-master-replay/inputs.json'
    bindings={str(path):sha(path)for path in [source,inventory_path,case_path,HERE/'admission.py',Path(__file__),ROOT/'validation/benchmark/run.py']}
    retained=read(source);inventory=read(inventory_path)['controls']['controls']['masters'];cases={case['id']:case for case in read(case_path)}
    assert retained['status']=='passed'
    result={'status':'running','scope':'parser-only controls using retained old numerical arrays plus explicitly synthetic new policy/untimed/own-repeat schema metadata. No current candidate numerical admission, no kernel or timing run.','input_sha256':bindings,'positive_whole':[],'positive_selected':[],'malformed_controls':[],'metadata_controls':[]}
    def save():(folder/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    started=time.monotonic();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('30-second parser-only bound')));signal.alarm(30)
    save()
    def annotate(response):
        response=deepcopy(response)
        for side,policy in a.POLICIES.items():
            value=response[side];value.pop('private_selected_native')
            value.update(requested_master_policy=policy,scope='untimed public-policy whole-reduction qualification',total_ns=[],elapsed_ns=[],iterations=0,capture_enabled=True,profiling_enabled=False,own_repeated_outputs_exact=True,input_unchanged=True)
        return response
    adapted=[]
    try:
        for row in retained['rows']:
            case=cases[row['id']];batch=row['outer_batch'];response=annotate(row['response'])
            a.validate_response(response,case,case['samples'][:batch]);adapted.append((response,case,batch))
            result['positive_whole'].append({'id':row['id'],'batch':batch,'status':'passed'})
        assert len(adapted)==8
        for group in inventory['selected_families']:
            for case in group['cases']:
                a.selected_case(case,case,group['family'])
                result['positive_selected'].append({'family':group['family'],'label':case['label'],'status':'passed'})
        assert len(result['positive_selected'])==34
        original,case,batch=adapted[-1]
        changes=[
            ('wrong-policy',['candidate','requested_master_policy'],'Symbolica'),
            ('legacy-private-field',['candidate','private_selected_native'],True),
            ('timing-field',['candidate','iterations'],1),
            ('timing-result',['candidate','elapsed_ns'],[1]),
            ('false-own-repeat',['candidate','own_repeated_outputs_exact'],False),
            ('false-input-preservation',['candidate','input_unchanged'],False),
            ('boolean-batch',['candidate','batch'],True),
            ('wrong-precision',['candidate','lanes',0,'represented',0,0,'precision'],52),
            ('nonbinary-rational',['candidate','lanes',0,'represented',0,0,'rational'],'1/3'),
            ('nonfinite-rational',['candidate','lanes',0,'represented',0,0,'rational'],'NaN'),
            ('represented-native-disagreement',['candidate','lanes',0,'represented',0,0,'rational'],'7'),
            ('unexpected-fallback',['candidate','lanes',0,'fallback_used'],True),
            ('wrong-master-backend',['candidate','master_captures',0,'backend'],'SymbolicaBatch'),
            ('truncated-master-output',['candidate','master_captures',0,'output'],[]),
            ('truncated-tensors',['candidate','lanes',0,'moments'],[]),
            ('truncated-representations',['candidate','lanes',0,'represented'],[]),
            ('wrong-request-order',['candidate','master_captures',0,'requests'],list(reversed(original['candidate']['master_captures'][0]['requests']))),
            ('whole-master-error',['candidate','master_captures',0,'whole_batch_error'],'bad'),
        ]
        def assign(value,path,new):
            target=value
            for key in path[:-1]:target=target[key]
            target[path[-1]]=new
        for label,path,new in changes:
            changed=deepcopy(original);assign(changed,path,new)
            try:a.validate_response(changed,case,case['samples'][:batch])
            except (AssertionError,KeyError,TypeError,ValueError,OverflowError)as error:
                result['malformed_controls'].append({'label':label,'path':path,'replacement':new,'status':'rejected','error_type':type(error).__name__})
            else:raise AssertionError('malformed control accepted: '+label)
        for field,new in [('input_rows',0),('argument_rows',0),('reduction_rows',0),('fallback_successes',1)]:
            changed=deepcopy(original)
            for side in a.POLICIES:changed[side]['execution'][field]=new
            try:a.validate_response(changed,case,case['samples'][:batch])
            except AssertionError:result['malformed_controls'].append({'label':'both-side-counter-'+field,'replacement':new,'status':'rejected'})
            else:raise AssertionError('co-mutated counter accepted: '+field)
        good={'finite':True,'rational':'1','precision':256,'negative_sign':False}
        assert a.number(good,'Float')==1
        for label,path,new in [('boolean-precision',['precision'],True),('zero-precision',['precision'],0),('over-u32',['precision'],2**32),('wrong-sign',['negative_sign'],True),('nonbinary',['rational'],'1/3'),('missing-exact',['rational'],None)]:
            changed=deepcopy(good);assign(changed,path,new)
            try:a.number(changed,'Float')
            except (AssertionError,TypeError,ValueError):result['metadata_controls'].append({'label':label,'replacement':new,'status':'rejected'})
            else:raise AssertionError('malformed metadata accepted: '+label)
        for path,value in bindings.items():assert sha(path)==value,path
        result['inputs_unchanged']=True;result['status']='passed'
    except Exception as error:result.update(status='failed',error=repr(error))
    finally:
        signal.alarm(0);result['elapsed_seconds']=time.monotonic()-started;result['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        if result['elapsed_seconds']>30:result.update(status='failed',deadline_exceeded=True)
        save()
    print(json.dumps({'status':result['status'],'positive_whole':len(result['positive_whole']),'positive_selected':len(result['positive_selected']),'rejected':len(result['malformed_controls'])+len(result['metadata_controls']),'elapsed_seconds':result['elapsed_seconds']}))
    return 0 if result['status']=='passed'else 1
if __name__=='__main__':sys.exit(main())
