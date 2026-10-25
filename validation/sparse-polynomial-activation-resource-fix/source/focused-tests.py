"""Root-authorized finite exact test stage. No work occurs on import."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from lifecycle import Budget,execute

ROOT=Path('/shared/external/iregi/iregi-rust')
HERE=Path(__file__).resolve().parent
TOTAL=240
RESERVE=30
PER_CHILD=30
CPU=6

def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def load(path):return json.loads(Path(path).read_text())
def require(ok,reason):
    if not ok:raise ValueError(reason)
def save(path,value):
    temporary=path.with_suffix('.partial');temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');temporary.replace(path)

def main():
    budget=Budget(TOTAL);budget.work_deadline=budget.deadline-RESERVE;budget.arm()
    folder=HERE/'tests-001';receipt=folder/'receipt.json'
    record=dict(status='preflight',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        total_seconds=TOTAL,reserve_seconds=RESERVE,child_cap_seconds=PER_CHILD,cpu_affinity=[CPU],
        started_monotonic=budget.started,absolute_deadline_monotonic=budget.deadline,
        work_deadline_monotonic=budget.work_deadline,steps=[],cleanup_errors=[],outputs={},
        selected_tests=[],unrun_tests=[],numeric_driver_executed=False,public_Dual_qualified=False,
        performance_qualified=False,license_recorded=False)
    guards={};complete=False
    try:
        require(Path.cwd().resolve()==ROOT and len(sys.argv)==1,'project root; no runtime selection')
        os.sched_setaffinity(0,{CPU});folder.mkdir(exist_ok=False);save(receipt,record)
        protocol_path=HERE/'protocol.json';protocol=load(protocol_path)
        require(protocol['status']=='root_authorized_frozen_owned_joint_libtest','frozen owned build context')
        guards=dict(protocol['inputs']);guards[str(protocol_path)]=sha(protocol_path);record['inputs']=guards
        for path,digest in guards.items():budget.remaining();require(sha(path)==digest,'changed active input '+path)
        build=load(protocol['build_receipt']);require(build['status']=='passed' and build['inputs_unchanged']is True and not build['cleanup_errors'],'actual joint build did not pass')
        require(protocol['executable_sha256']==guards[protocol['executable']],'owned executable must be input bound')
        selection=load(protocol['test_selection']);names=selection['focused_tests']+selection['regression_controls']
        require(len(names)==19 and len(set(names))==19,'exact19 distinct tests')
        require(selection['ignored_numeric_driver']not in names,'ignored numeric driver excluded')
        record['selected_tests']=names;record['unrun_tests']=names.copy();save(receipt,record)
        env=dict(os.environ);require(bool(env.get('SYMBOLICA_LICENSE')),'forward license only in memory')
        env.update(RAYON_NUM_THREADS='1',RUST_TEST_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',SYMBOLICA_HIDE_BANNER='1')
        executable=protocol['executable']
        commands=[('listing',[executable,'--list','--format=terse'])]+[(name,[executable,'--exact',name,'--nocapture','--test-threads=1'])for name in names]
        for index,(name,command)in enumerate(commands):
            budget.remaining();step=dict(name=name);record['steps'].append(step)
            def persist(value):step.update(value);save(receipt,record)
            result=execute(command,folder/('step-'+str(index)+'.log'),budget,PER_CHILD,record['cleanup_errors'],persist,env)
            require(result['status']=='exited' and result.get('owned_group_gone')is True,'owned test stage failed: '+name)
            text=(folder/('step-'+str(index)+'.log')).read_text()
            if name=='listing':
                listed=[line.removesuffix(': test')for line in text.splitlines()if line.endswith(': test')]
                require(all(listed.count(test)==1 for test in names),'every selected exact test must be listed once')
                require(listed.count(selection['ignored_numeric_driver'])==1,'private numerical driver exists but remains ignored')
                step['selected_names_found']=19;step['numeric_driver_listed_but_unrun']=True
            else:
                summaries=[line for line in text.splitlines()if line.startswith('test result:')]
                require(len(summaries)==1 and re.fullmatch(r'test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; [0-9]+ filtered out; finished in [^\n]+',summaries[0]),'strict one-success summary: '+name)
                require('running 1 test'in text and 'test '+name+' ...'in text,'exact selected test name: '+name)
                record['unrun_tests'].remove(name);step['strict_exact_gate']='passed'
            save(receipt,record)
        require(not record['unrun_tests'],'all19 exact tests must pass')
        complete=True;record['status']='completed_awaiting_guards';budget.remaining()
    except BaseException as error:record.update(status='failed',error=repr(error))
    finally:
        budget.disarm();post=Budget(max(0,budget.deadline-time.monotonic()));post.deadline=budget.deadline;post.work_deadline=budget.deadline-3
        try:
            post.arm();require(bool(guards),'active inputs unavailable')
            for path,digest in guards.items():post.remaining();require(sha(path)==digest,'changed terminal input '+path)
            record['inputs_unchanged']=True
            for path in sorted(folder.iterdir()):
                post.remaining()
                if path.is_file()and path!=receipt and path.suffix!='.partial':record['outputs'][path.name]=sha(path)
            post.remaining()
        except BaseException as error:record.update(inputs_unchanged=False,postguard_error=repr(error))
        finally:post.disarm()
        record.update(elapsed_seconds=budget.elapsed(),cancellation=budget.cancelled,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        record['status']='passed'if complete and record.get('inputs_unchanged')is True and not record['cleanup_errors']and not budget.cancelled and not post.cancelled and record['elapsed_seconds']<=TOTAL else'failed'
        final=Budget(max(0,budget.deadline-time.monotonic()));final.deadline=final.work_deadline=budget.deadline
        try:final.arm();save(receipt,record);final.remaining()
        finally:final.disarm()
    print(json.dumps(dict(status=record['status'],receipt=str(receipt),sha256=sha(receipt))))
    return 0 if record['status']=='passed'else 1

if __name__=='__main__':raise SystemExit(main())
