"""One reviewed 180-second isolated build, with no dependency rebuild."""
import datetime, os, signal, subprocess, sys, time
import harness_common as h

def main():
    h.BUILD.mkdir(exist_ok=False)
    started=time.monotonic();record={'status':'preflight','bound_seconds':180,'steps':[],
        'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    h.save(h.BUILD/'build.json',record)
    try:
        protocol=h.validate_protocol();inputs=dict(protocol['inputs']);h.bind(h.PROTOCOL,inputs)
        record.update(status='building',inputs=inputs,compiler_path=protocol['compiler_path'])
        for name,command,manifest in h.build_commands(protocol):
            step={'name':name,'command':command,'manifest_dir':str(manifest),'timeout':False};record['steps'].append(step)
            h.save(h.BUILD/'build.json',record)
            remaining=180-(time.monotonic()-started);h.require(remaining>0,'total build bound exhausted')
            env=os.environ.copy();env.update(CARGO_CRATE_NAME='iregi_rust',CARGO_MANIFEST_DIR=str(manifest))
            t=time.monotonic()
            with (h.BUILD/(name+'.log')).open('w') as log:
                process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                try:step['exit_code']=process.wait(timeout=remaining)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGKILL);process.wait();step.update(exit_code=None,timeout=True)
            step.update(seconds=time.monotonic()-t,log_sha256=h.sha(h.BUILD/(name+'.log')))
            h.save(h.BUILD/'build.json',record);h.require(step['exit_code']==0,f'{name} failed or timed out')
        h.final_verify(inputs);record['inputs_unchanged']=True
        h.require(time.monotonic()-started<=180,'total build including guards exceeded180seconds')
        record['outputs']={name:h.sha(h.BUILD/name) for name in h.OUTPUTS};record['status']='passed'
    except Exception as error:
        record.update(status='failed',error=str(error))
        if 'inputs' in record:
            try:h.final_verify(record['inputs']);record['inputs_unchanged']=True
            except Exception as changed:record.update(inputs_unchanged=False,guard_error=str(changed))
        record['retained_outputs']={p.name:h.sha(p) for p in h.BUILD.iterdir() if p.is_file() and p.name!='build.json'}
    record.update(elapsed_seconds=time.monotonic()-started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    if record['status']=='passed' and record['elapsed_seconds']>180:
        record.update(status='failed',error='final receipt and output hashing exceeded total bound')
    h.save(h.BUILD/'build.json',record)
    print({'status':record['status'],'seconds':record['elapsed_seconds'],'steps':len(record['steps'])})
    return 0 if record['status']=='passed' else 1
if __name__=='__main__':sys.exit(main())
