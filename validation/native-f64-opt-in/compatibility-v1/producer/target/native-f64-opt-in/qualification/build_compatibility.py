"""One bounded metadata-only broad/both continuation, separate from old attempts."""
from pathlib import Path
import datetime,json,os,sys
import build as prior
from lifecycle import Budget,execute
ROOT=Path.cwd();HERE=ROOT/'target/native-f64-opt-in/qualification'
sha=prior.sha;read=prior.read;save=prior.save

def recipe(attempt,manifest):
    steps=[x for x in prior.recipe('metadata',attempt,manifest) if x['configuration'] in ('broad','both')]
    assert [x['label'] for x in steps]==[c+'-'+s for c in ('broad','both') for s in ('masters','core','masters-tests','core-tests')]
    for step in steps:
        assert step['command'].count('--emit')==1
        assert step['command'][step['command'].index('--emit')+1]=='metadata'
        assert Path(step['output']).suffix=='.rmeta'
        step['timeout_seconds']=180 if step['label'].endswith(('masters','masters-tests')) else 60
    return steps

def main():
    assert len(sys.argv)==2 and sys.argv[1]=='001','one authorized attempt: 001'
    attempt=HERE/'compatibility-build-001';attempt.mkdir(exist_ok=False)
    manifest_path=HERE/'compatibility-preparation.json';manifest=read(manifest_path)
    bindings={Path(p):v for p,v in manifest['input_sha256'].items()};bindings[manifest_path]=sha(manifest_path)
    assert bindings[Path(__file__).resolve()]==sha(Path(__file__))
    steps=recipe(attempt,manifest)
    assert steps==read(HERE/'compatibility-command-plan.json')['steps']
    budget=Budget(600)
    record={'status':'preparing','stage':'broad-both-metadata-compatibility','scope':'Same private qualified public Rust source and frozen dependency closure; metadata only, no codegen/runtime/performance or production adoption. Original metadata attempt is unchanged.','runtime_cap_seconds':600,'cleanup_reserve_seconds':8,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_sha256':{str(p):v for p,v in bindings.items()},'steps':steps,'outputs':{},'cleanup_errors':[]}
    for step in steps:step['status']='unrun'
    save(attempt/'build.json',record)
    def verify():
        for p,v in bindings.items():budget.remaining();assert sha(p)==v,f'changed input: {p}'
    budget.arm()
    try:
        verify()
        for step in steps:
            budget.remaining();Path(step['output']).parent.mkdir(exist_ok=True)
            env=os.environ.copy();env.update(step['environment'])
            def persist(result):step.update(result);save(attempt/'build.json',record)
            result=execute(step['command'],attempt/(step['label']+'.log'),budget,step['timeout_seconds'],record['cleanup_errors'],persist,env)
            step['status']='compiled' if result['status']=='exited' else 'failed'
            save(attempt/'build.json',record)
            assert step['status']=='compiled',step['label']+' failed; stop, no retry'
            verify();output=Path(step['output']);step['output_sha256']=sha(output);step['status']='passed'
            record['outputs'][step['label']]={'path':str(output),'sha256':step['output_sha256'],'bytes':output.stat().st_size}
            save(attempt/'build.json',record)
        record['status']='completed-awaiting-guards'
    except Exception as error:record.update(status='failed',error=repr(error))
    # Preserve a terminal state before final hashes/guards can fail.
    record['elapsed_seconds']=budget.elapsed();record['deadline_exceeded']=record['elapsed_seconds']>600
    save(attempt/'build.json',record)
    try:
        verify();record['inputs_unchanged']=True
        record['compiler_logs_sha256']={str(p):sha(p) for p in sorted(attempt.glob('*.log'))}
    except Exception as error:record.update(inputs_unchanged=False,guard_error=repr(error))
    record['elapsed_seconds']=budget.elapsed();record['deadline_exceeded']|=record['elapsed_seconds']>600
    record['status']='passed' if all(x['status']=='passed' for x in steps) and record['inputs_unchanged'] and not record['cleanup_errors'] and not record['deadline_exceeded'] and 'error' not in record else 'failed'
    record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(attempt/'build.json',record)
    budget.disarm()
    print(json.dumps({'status':record['status'],'elapsed_seconds':record['elapsed_seconds'],'steps':[{k:s.get(k) for k in ['label','status','returncode','elapsed_seconds']} for s in steps]}))
    return 0 if record['status']=='passed' else 1
if __name__=='__main__':sys.exit(main())
