"""One reviewed isolated build with owned-group cleanup and a 25s reserve."""
import datetime,os,sys,time
import harness_common as h
from lifecycle import Budget,execute

def main():
    h.BUILD.mkdir(exist_ok=False)
    budget=Budget(180);budget.work_deadline=budget.deadline-25
    record={'status':'preflight','bound_seconds':180,'postwork_reserve_seconds':25,'steps':[],
        'cleanup_errors':[],'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    h.save(h.BUILD/'build.json',record);work_passed=False
    try:
        budget.arm();protocol=h.validate_protocol();inputs=dict(protocol['inputs']);h.bind(h.PROTOCOL,inputs)
        record.update(status='building',inputs=inputs,compiler_path=protocol['compiler_path'])
        for name,command,manifest in h.build_commands(protocol):
            budget.remaining()
            step={'name':name,'command':command,'manifest_dir':str(manifest)};record['steps'].append(step)
            env=os.environ.copy();env.update(CARGO_CRATE_NAME='iregi_rust',CARGO_MANIFEST_DIR=str(manifest))
            def persist(result):
                step.update(result);h.save(h.BUILD/'build.json',record)
            result=execute(command,h.BUILD/(name+'.log'),budget,180,record['cleanup_errors'],persist,env)
            h.require(result['status']=='exited' and result.get('owned_group_gone') is True,f'{name} failed or retained an owned process')
        work_passed=True;record['status']='completed_awaiting_guards'
    except Exception as error:record.update(status='failed',error=repr(error))
    finally:
        budget.disarm()
        record['elapsed_seconds']=budget.elapsed()
        if budget.cancelled:record['cancellation']=budget.cancelled
        h.save(h.BUILD/'build.json',record)
    # All owned children have terminal records before any log/output hash.
    post=Budget(max(0,budget.deadline-time.monotonic()))
    try:
        post.arm();post.remaining()
        h.require('inputs' in record,'preflight did not establish input bindings')
        h.final_verify(record['inputs']);record['inputs_unchanged']=True
        for step in record['steps']:
            post.remaining();path=h.BUILD/(step['name']+'.log')
            if path.exists():step['log_sha256']=h.sha(path)
        record['outputs']={}
        for name in h.OUTPUTS:
            post.remaining();path=h.BUILD/name
            if path.exists():record['outputs'][name]=h.sha(path)
    except Exception as error:record.update(postguard_error=repr(error),inputs_unchanged=False)
    finally:post.disarm()
    record.update(elapsed_seconds=budget.elapsed(),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    if post.cancelled:record['postguard_cancellation']=post.cancelled
    record['status']='passed' if (work_passed and record.get('inputs_unchanged') is True
        and set(record.get('outputs',{}))==set(h.OUTPUTS) and not record['cleanup_errors']
        and not budget.cancelled and not post.cancelled and record['elapsed_seconds']<=180
        and all(s.get('status')=='exited' and s.get('owned_group_gone') is True for s in record['steps'])) else 'failed'
    h.save(h.BUILD/'build.json',record)
    print({'status':record['status'],'seconds':record['elapsed_seconds'],'steps':len(record['steps'])})
    return 0 if record['status']=='passed' else 1
if __name__=='__main__':sys.exit(main())
