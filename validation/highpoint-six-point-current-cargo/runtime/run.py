"""Current emitted Cargo binaries only; staged execution requires an exact root grant."""
import datetime,os,re,sys,time
import harness_common as h
from lifecycle import Budget,execute

def membership(text,p):
    names=re.findall(r'^([A-Za-z0-9_:]+): test$',text,re.M)
    h.require(names and len(names)==len(set(names)),'test list malformed/duplicated')
    groups=p['selection']['exact_groups'];selected=[]
    for group in groups:
        actual=[name for name in names if group['filter'] in name]
        h.require(set(actual)==set(group['names']) and len(actual)==len(group['names']),'actual current test-filter membership differs: '+group['filter'])
        selected.extend(actual)
    h.require(len(selected)==len(set(selected))==34,'actual selected test total differs')
    return {'passed':True,'total_discovered_tests':len(names),'selected_tests':sorted(selected),'selected_count':34,'source':'actual current Cargo unit binary --list; no private-binary listing reused'}

def main(operation):
    h.require(operation in h.RUNS,'unknown operation');h.assert_runtime_grant(operation)
    out=h.HERE/h.RUNS[operation];out.mkdir(exist_ok=False);bound=h.BOUNDS[operation];budget=Budget(bound);budget.work_deadline=budget.deadline-20
    record={'status':'preflight','operation':operation,'bound_seconds':bound,'postwork_reserve_seconds':20,'steps':[],'cleanup_errors':[],'environment_additions':h.ENVIRONMENT,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    h.save(out/'run.json',record);work_passed=False
    try:
        budget.arm();p=h.protocol();inputs=h.run_inputs(operation);record.update(status='running',inputs=inputs);env=os.environ.copy();env.update(h.ENVIRONMENT)
        for index,command in enumerate(h.run_commands(operation,p)):
            budget.remaining();step={'command':command};record['steps'].append(step)
            def persist(result):step.update(result);h.save(out/'run.json',record)
            result=execute(command,out/f'step-{index}.log',budget,bound,record['cleanup_errors'],persist,env)
            h.require(result['status']=='exited' and result.get('owned_group_gone') is True,'runtime failed or retained an owned group')
        work_passed=True;record['status']='completed_awaiting_guards'
    except Exception as error:record.update(status='failed',error=repr(error))
    finally:
        budget.disarm();record['elapsed_seconds']=budget.elapsed()
        if budget.cancelled:record['cancellation']=budget.cancelled
        h.save(out/'run.json',record)
    # Every execute() persisted its complete terminal before these reads/hashes.
    post=Budget(max(0,budget.deadline-time.monotonic()))
    try:
        post.arm();post.remaining();h.require('inputs' in record,'input bindings not established')
        if work_passed and operation=='list':h.save(out/'membership.json',membership((out/'step-0.log').read_text(),p))
        if work_passed and operation=='exact':
            for i,group in enumerate(p['selection']['exact_groups']):h.validate_test_log((out/f'step-{i}.log').read_text(),group['names'])
        h.final_verify(record['inputs']);record['inputs_unchanged']=True;record['outputs']={}
        for path in sorted(out.iterdir()):
            if path.is_file() and path.name!='run.json':post.remaining();record['outputs'][path.name]=h.sha(path)
    except Exception as error:record.update(postguard_error=repr(error),inputs_unchanged=False)
    finally:post.disarm()
    record.update(elapsed_seconds=budget.elapsed(),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    if post.cancelled:record['postguard_cancellation']=post.cancelled
    record['status']='passed' if(work_passed and record.get('inputs_unchanged') is True and not record['cleanup_errors'] and not budget.cancelled and not post.cancelled and record['elapsed_seconds']<=bound and all(s.get('status')=='exited' and s.get('owned_group_gone') is True for s in record['steps']))else'failed'
    h.save(out/'run.json',record);print({'operation':operation,'status':record['status'],'seconds':record['elapsed_seconds']});return 0 if record['status']=='passed' else 1
if __name__=='__main__':sys.exit(main(sys.argv[1]))
