"""Finite actual-main N7 rank-seven stages; no operation runs on import."""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import time

ROOT=Path('/shared/external/iregi/iregi-rust')
HERE=Path(__file__).resolve().parent
from runtime_lifecycle import Budget,execute


def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def load(path):return json.loads(Path(path).read_text())
def save(path,record):
    temporary=path.with_suffix('.partial')
    temporary.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n');temporary.replace(path)
def require(ok,reason):
    if not ok:raise ValueError(reason)


def main():
    require(Path.cwd().resolve()==ROOT and len(sys.argv)==2,'runtime.py guard|capture128|single128|capture256|compare')
    operation=sys.argv[1]
    policies=dict(guard=(60,15,30,6),capture128=(1680,120,1500,6),
        single128=(120,15,0,6),capture256=(1980,120,1800,7),compare=(120,15,0,6))
    require(operation in policies,'declared operation')
    total,reserve,cap,cpu=policies[operation]
    budget=Budget(total);budget.work_deadline=budget.deadline-reserve;budget.arm()
    folder=HERE/'runtime'/(operation+'-001')
    receipt=folder/'receipt.json'
    record=dict(status='preflight',operation=operation,total_seconds=total,reserve_seconds=reserve,
        child_cap_seconds=cap,cpu_affinity=[cpu],started_monotonic=budget.started,
        absolute_deadline_monotonic=budget.deadline,work_deadline_monotonic=budget.work_deadline,
        started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),steps=[],cleanup_errors=[],
        outputs={},numerical_qualified=False,public_rank_support_claimed=False,performance_qualified=False,
        license_recorded=False)
    guards={};complete=False
    try:
        os.sched_setaffinity(0,{cpu})
        folder.mkdir(parents=True,exist_ok=False);save(receipt,record)
        protocol_path=HERE/'runtime-protocol.json';protocol=load(protocol_path)
        require(protocol['status']=='root_authorized_frozen_actual_main_N7_rank7','frozen protocol')
        guards.update(protocol['inputs']);guards[str(protocol_path)]=sha(protocol_path)
        prerequisites=dict(guard=[],capture128=['guard'],single128=['capture128'],
            capture256=['single128'],compare=['single128','capture256'])[operation]
        for prior in prerequisites:
            path=HERE/'runtime'/(prior+'-001')/'receipt.json';d=load(path)
            require(d['status']=='passed' and d['inputs_unchanged'] is True and not d['cleanup_errors'],
                'prior stage must pass: '+prior)
            guards[str(path)]=sha(path)
            for name,digest in d['outputs'].items():
                guards[str(path.parent/name)]=digest
        record['inputs']=guards
        for path,digest in guards.items():
            budget.remaining();require(sha(path)==digest,'changed active input '+path)
        env=dict(os.environ)
        for key,value in protocol['environment'].items():require(env.get(key)==value,'changed runtime env '+key)
        require(bool(env.get('SYMBOLICA_LICENSE')),'forward license in memory')
        env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
            RUST_TEST_THREADS='1',RUST_MIN_STACK='67108864',SYMBOLICA_HIDE_BANNER='1',
            IREGI_PV_PREPARATION_PROFILE='1',IREGI_PREPARATION_PROFILE='1',SYMBOLICA_SCOPE_PROFILE='1')
        executable=protocol['executable'];binary_sha=protocol['executable_sha256']
        if operation in ('guard','capture128','capture256'):
            if operation=='guard':
                command=[executable,'--exact','seven_point::tests::unsupported_domain_is_rejected_before_symbolic_preparation',
                    '--nocapture','--test-threads=1']
            else:
                bits=int(operation.removeprefix('capture'))
                env.update(IREGI_N7_PROBE_FIXTURE=protocol['fixture'],IREGI_N7_PROBE_RANK='7',
                    IREGI_N7_PROBE_WORKING_BITS=str(bits),IREGI_N7_PROBE_OUTPUT=str(folder/'result.json'))
                command=[protocol['python'],'-B',str(HERE/'resource_exec.py'),executable,binary_sha,
                         str(folder/'exec-prelude.json')]
            step={};record['steps'].append(step)
            def persist(value):step.update(value);save(receipt,record)
            result=execute(command,folder/'step-0.log',budget,cap,record['cleanup_errors'],persist,env)
            require(result['status']=='exited' and result.get('owned_group_gone') is True,'owned test stage failed')
            text=(folder/'step-0.log').read_text()
            summaries=[x for x in text.splitlines()if x.startswith('test result:')]
            require(len(summaries)==1 and re.fullmatch(r'test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; [0-9]+ filtered out; finished in [^\n]+',summaries[0]),'strict one named successful test summary')
            expected='thin_n7::numeric_probe::capture_complete_moments_from_fixture' if operation!='guard' else 'seven_point::tests::unsupported_domain_is_rejected_before_symbolic_preparation'
            require('test '+expected+' ...' in text and 'running 1 test' in text,'exact named test executed')
            if operation!='guard':
                d=load(folder/'result.json')
                require(d['status']=='all_lanes_success' and d['lane_statuses']==['Success'],'complete native lane required')
                require(len(d['basis'])==330 and len(d['lanes'][0]['moments'])==330 and
                    all(len(x)==4 for x in d['lanes'][0]['moments']),'full1320complexslots')
                prelude=load(folder/'exec-prelude.json')
                require(prelude['address_space_soft_hard_bytes']==[34359738368]*2 and
                    prelude['executable_sha256']==binary_sha,'actual resource-bound executable')
        else:
            source=HERE/('check_single_saved.py' if operation=='single128' else 'compare_main_private_saved.py')
            spec=importlib.util.spec_from_file_location('finite_saved_N7_rules',source)
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            argv=sys.argv
            try:
                low=HERE/'runtime/capture128-001/result.json'
                args=[str(low),str(folder/'comparison.json')]
                if operation=='compare':args=[str(low),str(HERE/'runtime/capture256-001/result.json'),str(folder/'comparison.json')]
                sys.argv=[str(source),*args];code=module.main()
            finally:sys.argv=argv
            require(code==0,'saved complete math gate failed')
            record['saved_math_status']=load(folder/'comparison.json')['status']
        complete=True;record['status']='completed_awaiting_guards';budget.remaining()
    except BaseException as error:record.update(status='failed',error=repr(error))
    finally:
        budget.disarm()
        post=Budget(max(0,budget.deadline-time.monotonic()));post.deadline=budget.deadline;post.work_deadline=budget.deadline-3
        try:
            post.arm();require(bool(guards),'preflight inputs not admitted')
            for path,digest in guards.items():post.remaining();require(sha(path)==digest,'changed terminal active input '+path)
            record['inputs_unchanged']=True
            for path in sorted(folder.iterdir()):
                post.remaining()
                if path.is_file()and path!=receipt and not path.name.endswith('.partial'):record['outputs'][path.name]=sha(path)
            post.remaining()
        except BaseException as error:record.update(inputs_unchanged=False,postguard_error=repr(error))
        finally:post.disarm()
        record.update(elapsed_seconds=budget.elapsed(),cancellation=budget.cancelled,
            finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        record['status']='passed'if complete and record.get('inputs_unchanged')is True and not record['cleanup_errors'] and not budget.cancelled and not post.cancelled and record['elapsed_seconds']<=total else'failed'
        final=Budget(max(0,budget.deadline-time.monotonic()));final.deadline=final.work_deadline=budget.deadline
        try:final.arm();save(receipt,record);final.remaining()
        finally:final.disarm()
    print(json.dumps(dict(operation=operation,status=record['status'],receipt=str(receipt),sha256=sha(receipt))))
    return 0 if record['status']=='passed'else 1


if __name__=='__main__':raise SystemExit(main())
