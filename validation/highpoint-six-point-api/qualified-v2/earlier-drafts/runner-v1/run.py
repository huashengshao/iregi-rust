"""Execute exactly one reviewed operation; never retries or extends a bound."""
import datetime, os, signal, subprocess, sys, time
import harness_common as h

def main(operation):
    h.require(operation in h.RUNS,'unknown operation');out=h.HERE/h.RUNS[operation];out.mkdir(exist_ok=False)
    started=time.monotonic();bound=h.BOUNDS[operation]
    record={'status':'preflight','operation':operation,'bound_seconds':bound,'steps':[],
            'environment_additions':h.ENVIRONMENT,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    h.save(out/'run.json',record)
    try:
        build=h.validate_build();inputs=h.run_inputs(operation,build)
        record.update(status='running',inputs=inputs)
        env=os.environ.copy();env.update(h.ENVIRONMENT)
        for index,command in enumerate(h.run_commands(operation,build['protocol'])):
            step={'command':command,'timeout':False};record['steps'].append(step);h.save(out/'run.json',record)
            remaining=bound-(time.monotonic()-started);h.require(remaining>0,'total runtime bound exhausted')
            t=time.monotonic()
            with (out/f'step-{index}.log').open('w') as log:
                process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                try:step['exit_code']=process.wait(timeout=remaining)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGKILL);process.wait();step.update(exit_code=None,timeout=True)
            step['seconds']=time.monotonic()-t;h.save(out/'run.json',record)
            h.require(step['exit_code']==0,'runtime failed or timed out')
        h.final_verify(inputs);record['inputs_unchanged']=True
        h.require(time.monotonic()-started<=bound,'runtime including guards exceeded declared bound')
        record['status']='passed'
    except Exception as error:
        record.update(status='failed',error=str(error))
        if 'inputs' in record:
            try:h.final_verify(record['inputs']);record['inputs_unchanged']=True
            except Exception as changed:record.update(inputs_unchanged=False,guard_error=str(changed))
    record['outputs']={p.name:h.sha(p) for p in out.iterdir() if p.is_file() and p.name!='run.json'}
    record.update(elapsed_seconds=time.monotonic()-started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    if record['status']=='passed' and record['elapsed_seconds']>bound:
        record.update(status='failed',error='final receipt and output hashing exceeded total bound')
    h.save(out/'run.json',record);print({'operation':operation,'status':record['status'],'seconds':record['elapsed_seconds']})
    return 0 if record['status']=='passed' else 1
if __name__=='__main__':sys.exit(main(sys.argv[1]))
