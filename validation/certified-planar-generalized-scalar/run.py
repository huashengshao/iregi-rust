"""One explicitly granted bounded build/capture from the frozen finite catalogue."""
import argparse,hashlib,importlib.util,json,os,signal,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path.cwd().resolve();HERE=Path(__file__).resolve().parent
WORK=ROOT/'target/certified-planar-generalized-scalar-numeric'
def require(ok,message):
    if not ok:raise ValueError(message)
def read(path):return json.loads(Path(path).read_text())
def sha(path,deadline=None):
    value=hashlib.sha256()
    with Path(path).open('rb')as stream:
        while block:=stream.read(1024*1024):
            require(deadline is None or time.monotonic()<deadline,'guard deadline exhausted');value.update(block)
    return value.hexdigest()
def save(path,value):
    temporary=path.with_suffix('.partial');temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');temporary.replace(path)
def main():
    started=time.monotonic();parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job');parser.add_argument('--grant',type=Path,required=True);parser.add_argument('--review',type=Path,required=True);args=parser.parse_args()
    catalog_path=HERE/'catalog.json';p=read(catalog_path)
    job=next(job for job in [p['build']]+p['jobs'] if job['id']==args.job)
    helper=HERE/'lifecycle.py';require(sha(helper)==p['bindings'][str(helper)],'lifecycle changed before import')
    spec=importlib.util.spec_from_file_location('planar_scalar_numeric_lifecycle',helper);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    budget=h.Budget(job['total_seconds']);budget.started=started;budget.deadline=started+job['total_seconds'];budget.work_deadline=budget.deadline-job['reserve_seconds'];budget.arm()
    directory=WORK/job['id'];created=complete=False
    record={'job':job,'catalog_sha256':sha(catalog_path),'status':'preflight','steps':[],'cleanup_errors':[],'outputs':{},'inputs_unchanged':False,
        'total_seconds':job['total_seconds'],'reserve_seconds':job['reserve_seconds'],'native_cap_seconds':job['native_cap_seconds'],
        'authorization_sha256':sha(args.grant),'independent_source_review_sha256':sha(args.review),'automatic_retry':False,'native_case_executed':False,
        'performance_qualified':False,'public_generalized_numeric_domain_qualified':False}
    guards=dict(p['bindings']);guards[str(catalog_path)]=record['catalog_sha256'];guards[str(args.grant.resolve())]=record['authorization_sha256'];guards[str(args.review.resolve())]=record['independent_source_review_sha256']
    def verify(deadline):
        for name,expected in guards.items():require(sha(name,deadline)==expected,'input drift '+name)
    try:
        require(not directory.exists(),'existing attempt preserved; no automatic retry');directory.mkdir(parents=True);created=True;save(directory/'receipt.json',record)
        grant,review=read(args.grant),read(args.review)
        require(grant['status']=='granted' and grant['grantor']=='/root' and job['id'] in grant['jobs'] and grant['catalog_sha256']==record['catalog_sha256']
            and grant['review_sha256']==record['independent_source_review_sha256'],'exact root grant missing')
        require(review['status']=='passed_independent_source_runner_comparator_review' and review['findings']==[] and review['catalog_sha256']==record['catalog_sha256'],'exact independent source review not clear')
        verify(budget.work_deadline)
        if job['kind']=='build':
            inventory={}
            for source_name,expected in p['live_build_source_bindings'].items():
                source=Path(source_name);require(sha(source,budget.work_deadline)==expected,'live build source changed')
                relative=source.relative_to(ROOT);dest=directory/'source-snapshot'/relative;dest.parent.mkdir(parents=True,exist_ok=True)
                data=source.read_bytes();dest.write_bytes(data);require(sha(dest,budget.work_deadline)==expected,'snapshot copy changed')
                guards[str(source)]=expected;guards[str(dest)]=expected;inventory[str(relative)]=expected
            save(directory/'source-inventory.json',inventory);command=job['command']
        else:
            built=read(WORK/'build-001/receipt.json');require(built['status']=='passed','build not admitted')
            guards[str(WORK/'build-001/receipt.json')]=sha(WORK/'build-001/receipt.json')
            for relative,expected in built['outputs'].items():
                if relative.startswith('source-snapshot/')or relative=='source-inventory.json':
                    guards[str(WORK/'build-001'/relative)]=expected
            if job['kind']=='rust':
                source=WORK/'build-001/frozen-example';expected=built['artifact_sha256']
                require(sha(source,budget.work_deadline)==expected,'qualified frozen artifact changed')
                owned=directory/'owned-executable';os.link(source,owned)
                require(source.stat().st_ino==owned.stat().st_ino and source.stat().st_dev==owned.stat().st_dev,'owned hardlink changed inode')
                guards[str(source)]=expected;guards[str(owned)]=expected
                record.update(owned_executable_sha256=expected,owned_executable_bytes=owned.stat().st_size,native_hardlink_shared_inode=True,
                    native_alias_scope='readonly hardlink to one frozen artifact; not an independent byte copy')
                command=[p['tools']['taskset'],'-c',str(job['cpu'])]+[str(owned) if arg=='{owned_executable}' else arg for arg in job['command']]
            else:
                oracle=HERE/'oracle.py';owned=directory/'owned-oracle.py';owned.write_bytes(oracle.read_bytes());guards[str(owned)]=p['bindings'][str(oracle)]
                preparation=Path(p['oracle_preparation_capture']);require(preparation.is_file(),'Symbolica preparation capture unavailable')
                guards[str(preparation)]=sha(preparation,budget.work_deadline)
                command=[p['tools']['taskset'],'-c',str(job['cpu'])]+[p['tools']['python'] if arg=='{python}' else str(owned) if arg==str(oracle) else arg for arg in job['command']]
        record['inputs']=guards;record['command']=command;record['status']='running';save(directory/'receipt.json',record)
        environment=os.environ.copy();environment.update(RAYON_NUM_THREADS='1',RUST_TEST_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
        record['license_present']=bool(environment.get('SYMBOLICA_LICENSE'))
        require(job['kind']!='rust' or record['license_present'],'Symbolica license absent')
        record['environment_additions']={k:environment[k] for k in ['RAYON_NUM_THREADS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS']}
        step={};record['steps'].append(step)
        def persist(value):
            step.update(value)
            if 'owned_process_group'in value:record['native_case_executed']=True
            save(directory/'receipt.json',record)
        result=h.execute(command,directory/'step.log',budget,job['native_cap_seconds'],record['cleanup_errors'],persist,environment)
        if job['kind']=='build':
            require(result['status']=='exited','Cargo build failed');events=[]
            for line in (directory/'step.log').read_text().splitlines():
                try:event=json.loads(line)
                except json.JSONDecodeError:continue
                if event.get('reason')=='compiler-artifact' and event.get('target',{}).get('name')=='certified_planar_scalar' and event.get('executable'):events.append(event)
            require(len(events)==1,'one actual Cargo example artifact required')
            event=events[0];source=Path(event['executable']);expected=sha(source,budget.work_deadline)
            h.freeze_binary(source,expected,directory/'frozen-example',budget);guards[str(directory/'frozen-example')]=expected
            record.update(artifact_sha256=expected,cargo_artifact=event,artifact_bytes=(directory/'frozen-example').stat().st_size)
            complete=True
        else:
            output=directory/'result.json'
            if output.exists():record['driver_status']=read(output).get('status')
            complete=result.get('returncode')in[0,2] and result.get('owned_group_gone')is True and not result.get('timeout')
        record['status']='passed'if job['kind']=='build'and complete else 'terminal_capture'if complete else 'failed_or_incomplete'
    except BaseException as error:record.update(status='failed_or_incomplete',error=repr(error))
    finally:
        def terminal_cancel(number,frame):
            budget.cancelled='terminal bookkeeping cancelled by signal '+str(number);raise TimeoutError(budget.cancelled)
        for number in [signal.SIGTERM,signal.SIGINT,signal.SIGALRM]:signal.signal(number,terminal_cancel)
        signal.setitimer(signal.ITIMER_REAL,max(.001,budget.deadline-time.monotonic()))
        if created:
            try:
                verify(budget.deadline);record['inputs_unchanged']=True
                record['outputs']={str(path.relative_to(directory)):sha(path,budget.deadline)for path in directory.rglob('*')if path.is_file()and path.name not in ['receipt.json','receipt.partial','owned-executable','frozen-example']}
            except BaseException as error:record.update(status='failed_or_incomplete',inputs_unchanged=False,terminal_guard_error=repr(error))
        signal.setitimer(signal.ITIMER_REAL,0);record.update(elapsed_seconds=budget.elapsed(),cancellation=budget.cancelled)
        if not complete or not record['inputs_unchanged']or record['cleanup_errors']or budget.cancelled or budget.elapsed()>job['total_seconds']:record['status']='failed_or_incomplete'
        if created:save(directory/'receipt.json',record)
        budget.disarm()
    print(json.dumps({'job':job['id'],'status':record['status'],'elapsed_seconds':record['elapsed_seconds'],'receipt_sha256':sha(directory/'receipt.json')if created else None}),flush=True)
    return 0 if record['status']in['passed','terminal_capture']else 2
if __name__=='__main__':raise SystemExit(main())
