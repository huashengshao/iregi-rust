"""Bounded private rustc phases. This file does nothing when imported."""
from pathlib import Path
import datetime,hashlib,json,os,signal,subprocess,sys,time
ROOT=Path.cwd();HERE=ROOT/'target/native-f64-opt-in/qualification'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
FEATURES={'default':[], 'selective':['native-f64-abc'], 'broad':['native-batch'], 'both':['native-batch','native-f64-abc']}

def recipe(stage,attempt,manifest):
    """Return every command, bound input/output and cap before starting a child."""
    assert stage in ('metadata','public','observation')
    tools=manifest['tools'];deps=ROOT/manifest['dependency_directory'];extra=ROOT/manifest['supplemental_directory'];native=ROOT/manifest['native_directory']
    external={name:ROOT/path for name,path in manifest['externs'].items()}
    common=[tools['taskset']['path'],'-c','20,21',tools['rustc']['path'],'--edition=2024','-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo','-C','debug-assertions=yes','-C','overflow-checks=yes','-C',f'linker={tools["cc"]["path"]}','-L',f'dependency={deps}','-L',f'dependency={extra}','-L',f'native={native}']
    steps=[]
    configurations=list(FEATURES)if stage=='metadata'else(['default','selective']if stage=='public'else['selective'])
    for configuration in configurations:
        folder=attempt/configuration
        snapshot=HERE/('source/observation-overlay'if stage=='observation'else'public-source/crates')
        # Observation overlay uses the same crate-directory names without an extra crates level.
        master=snapshot/'iregi-masters';core=snapshot/'iregi-rust'
        feature=FEATURES[configuration]
        mastercfg=['--cfg','feature="default"']
        for flag in feature:mastercfg+=['--cfg',f'feature="{flag}"']
        corecfg=['--cfg','feature="default"']
        if 'native-f64-abc'in feature:corecfg+=['--cfg','feature="native-f64-abc"']
        if stage=='observation':mastercfg+=['--cfg','iregi_qualification_capture'];corecfg+=['--cfg','iregi_qualification_capture']
        suffix='rmeta'if stage=='metadata'else'rlib'
        outputs={'iregi_masters':folder/f'libiregi_masters.{suffix}','iregi_rust':folder/f'libiregi_rust.{suffix}'}
        def add(label,crate,source,output,extern_names,cfg,*,test=False):
            args=common+['-L',f'dependency={folder}','--crate-name',crate,'-C',f'metadata=native_optin_{stage}_{configuration}_{label}']
            args+=['--test']if test else['--crate-type','rlib']
            if stage=='metadata':args+=['--emit','metadata']
            args+=cfg+[str(source),'-o',str(output)]
            for name in extern_names:args+=['--extern',f'{name}={outputs.get(name,external.get(name))}']
            steps.append({'label':configuration+'-'+label,'configuration':configuration,'command':args,'output':str(output),'timeout_seconds':90 if stage=='metadata'else 180,'environment':{'CARGO_CRATE_NAME':'iregi_masters'if label.startswith('masters')else'iregi_rust','CARGO_MANIFEST_DIR':str(master if label.startswith('masters')else core)}})
        add('masters','iregi_masters',master/'src/lib.rs',outputs['iregi_masters'],['symbolica','oneloop'],mastercfg)
        add('core','iregi_rust',core/'src/lib.rs',outputs['iregi_rust'],['symbolica','iregi_masters','serde','thiserror'],corecfg)
        if stage!='observation':
            add('masters-tests','iregi_masters_tests',master/'src/lib.rs',folder/('masters-tests.rmeta'if stage=='metadata'else'masters-tests'),['symbolica','oneloop'],mastercfg,test=True)
            add('core-tests','iregi_rust_tests',core/'src/lib.rs',folder/('core-tests.rmeta'if stage=='metadata'else'core-tests'),['symbolica','iregi_masters','serde','thiserror','serde_json','oneloop'],corecfg,test=True)
        else:
            args=common+['-L',f'dependency={folder}','--crate-name','native_optin_qualification',str(HERE/'source/probe.rs'),'-o',str(folder/'probe')]
            for name in ['iregi_rust','iregi_masters','symbolica','oneloop','serde','serde_json']:
                args+=['--extern',f'{name}={outputs.get(name,external.get(name))}']
            steps.append({'label':'selective-probe','configuration':configuration,'command':args,'output':str(folder/'probe'),'timeout_seconds':180,'environment':{'CARGO_CRATE_NAME':'native_optin_qualification'}})
    return steps

def main():
    assert len(sys.argv)==3,'stage attempt-id'
    stage,identity=sys.argv[1:];assert stage in ('metadata','public','observation')
    attempt=HERE/(stage+'-build-'+identity);attempt.mkdir(exist_ok=False)
    manifest_path=HERE/'preparation.json';manifest=read(manifest_path)
    bindings={Path(p):v for p,v in manifest['input_sha256'].items()}
    bindings[manifest_path]=sha(manifest_path)
    assert bindings[Path(__file__).resolve()]==sha(Path(__file__))
    cap={'metadata':600,'public':900,'observation':540}[stage]
    started=time.monotonic();deadline=started+cap
    record={'status':'preparing','stage':stage,'scope':'private opt0 correctness build, frozen non-Python native-object closure; no performance qualification','runtime_cap_seconds':cap,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_sha256':{str(p):v for p,v in bindings.items()},'steps':recipe(stage,attempt,manifest),'outputs':{},'cleanup_errors':[]}
    for step in record['steps']:step['status']='unrun'
    save(attempt/'build.json',record)
    def verify():
        for p,v in bindings.items():assert sha(p)==v,f'changed input: {p}'
    try:
        verify()
        for step in record['steps']:
            remaining=deadline-time.monotonic()
            assert remaining>0,'aggregate build bound exhausted'
            Path(step['output']).parent.mkdir(exist_ok=True)
            env=os.environ.copy();env.update(step['environment'])
            step['status']='running';save(attempt/'build.json',record)
            before=time.monotonic();owner=None
            try:
                with(attempt/(step['label']+'.log')).open('x')as log:
                    owner=subprocess.Popen(step['command'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                    step['owned_process_group']=owner.pid;save(attempt/'build.json',record)
                    try:owner.wait(timeout=min(step['timeout_seconds'],remaining))
                    except subprocess.TimeoutExpired:
                        step['timeout']=True;os.killpg(owner.pid,signal.SIGTERM)
                        try:owner.wait(timeout=3)
                        except subprocess.TimeoutExpired:os.killpg(owner.pid,signal.SIGKILL);owner.wait(timeout=5)
                    step['returncode']=owner.returncode
            finally:
                if owner is not None and owner.poll()is None:
                    try:os.killpg(owner.pid,signal.SIGKILL);owner.wait(timeout=5)
                    except Exception as error:record['cleanup_errors'].append(repr(error))
                step['elapsed_seconds']=time.monotonic()-before
                step['status']='compiled'if step.get('returncode')==0 and not step.get('timeout')else'failed'
                save(attempt/'build.json',record) # terminal precedes risky guards/hashes
            assert step['status']=='compiled',step['label']+' failed; no retry authorized'
            verify();output=Path(step['output'])
            step['output_sha256']=sha(output);step['status']='passed'
            record['outputs'][step['label']]={'path':str(output),'sha256':step['output_sha256'],'bytes':output.stat().st_size}
            save(attempt/'build.json',record)
        record['status']='completed-awaiting-guards'
    except Exception as error:record.update(status='failed',error=repr(error))
    record['elapsed_seconds']=time.monotonic()-started
    record['deadline_exceeded']=record['elapsed_seconds']>cap
    save(attempt/'build.json',record)
    try:verify();record['inputs_unchanged']=True
    except Exception as error:record.update(inputs_unchanged=False,guard_error=repr(error))
    record['elapsed_seconds']=time.monotonic()-started;record['deadline_exceeded']|=record['elapsed_seconds']>cap
    record['status']='passed'if all(x['status']=='passed'for x in record['steps'])and record['inputs_unchanged']and not record['cleanup_errors']and not record['deadline_exceeded']and'error'not in record else'failed'
    record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(attempt/'build.json',record)
    print(json.dumps({'status':record['status'],'stage':stage,'elapsed_seconds':record['elapsed_seconds'],'steps':[{k:s.get(k)for k in ['label','status','returncode','elapsed_seconds']}for s in record['steps']]}))
    return 0 if record['status']=='passed'else 1
if __name__=='__main__':sys.exit(main())
