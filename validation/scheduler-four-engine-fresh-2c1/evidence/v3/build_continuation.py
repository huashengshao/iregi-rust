"""Bounded compiler continuation with actual crate-identity provenance.

Importing this file executes nothing. No probe/test/integral is ever run here.
"""
from pathlib import Path
import copy, hashlib, json, os, re, sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent.parent))
from fresh_lifecycle import Budget,execute
from provenance import lower_from_proof,parse,admit

ROOT=Path('/shared/external/iregi/iregi-rust')
BASE=ROOT/'target/guard-performance-review/optimized-performance-proposal'
HERE=BASE/'v3'

def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')

def main():
    assert Path.cwd()==ROOT and len(sys.argv)==2
    reviewed=sys.argv[1];protocol_path=HERE/'protocol.json'
    assert sha(protocol_path)==reviewed
    protocol=read(protocol_path)
    attempt=Path(protocol['attempt_directory']);attempt.mkdir(exist_ok=False)
    budget=Budget(protocol['aggregate_budget_seconds'])
    budget.work_deadline=budget.deadline-protocol['cleanup_postguard_reserve_seconds']
    receipt=attempt/'build.json'
    record={'status':'preparing','success':False,'protocol_sha256':reviewed,'runner_sha256':sha(Path(__file__)),
        'scope':protocol['scope'],'aggregate_budget_seconds':protocol['aggregate_budget_seconds'],
        'cleanup_postguard_reserve_seconds':protocol['cleanup_postguard_reserve_seconds'],
        'steps':[dict(s,status='unrun')for s in protocol['steps']],'outputs':{},'metadata_reads':[],
        'reused_products':copy.deepcopy(protocol['reused_products']),'cleanup_errors':[],
        'original_failed_receipt':protocol['original_failed_receipt'],
        'original_failed_receipt_sha256':protocol['original_failed_receipt_sha256'],
        'numerical_execution':False,'performance_measurement':False}
    outputs={};metadata_by_artifact={};variant_shared={'baseline':{},'candidate':{}}
    save(receipt,record)
    def verify():
        assert sha(protocol_path)==reviewed,'Protocol changed'
        for raw,expected in {**protocol['protected_sha256'],**protocol['tool_sha256']}.items():
            budget.remaining();path=Path(raw)if Path(raw).is_absolute()else ROOT/raw
            assert sha(path)==expected,'Changed input: '+raw
        inventory=read(protocol['closed_lower_inventory'])
        folder=Path(protocol['closed_lower_inventory']).parent/'closed-lower-deps'
        assert {str(p)for p in folder.iterdir()}==set(inventory),'Closed lower search members changed'
        for raw,item in inventory.items():
            budget.remaining();path=Path(raw)
            assert path.is_symlink()and os.readlink(path)==item['target'],'Closed lower alias changed'
            assert sha(path)==item['sha256'] and path.stat().st_size==item['bytes']
        for path,expected in outputs.items():
            budget.remaining();assert sha(path)==expected,'Changed stage output: '+str(path)

    def prove_probe(step,item):
        # Rustc's exact --extern paths plus successfully type-checked metadata
        # select these roots before ThinLTO. The native linker map is not a list
        # of those already-merged Rust archives; retain its actual scope.
        bindings={}
        for name in ['symbolica','oneloop','iregi_masters','iregi_rust']:
            path=step['explicit_externs'][name]
            assert path in metadata_by_artifact,'Missing admitted predecessor metadata: '+path
            root=metadata_by_artifact[path]
            assert root['name']==name
            bindings[name]={'path':path,'sha256':sha(path),'crate_hash':root['crate_hash'],
                'stable_crate_id':root['stable_crate_id'],'proof':'actual upstream metadata + recorded successful exact compiler extern'}
        core=metadata_by_artifact[step['explicit_externs']['iregi_rust']]
        admit(core,expected_root_name='iregi_rust',allowed_lower=allowed,
              required_fresh={name:metadata_by_artifact[step['explicit_externs'][name]]for name in ['symbolica','oneloop','iregi_masters']})
        linkmap=Path(step['link_map']);text=linkmap.read_text()
        oldpool=ROOT/'target/benchmark/dependency-closures/6b24c03-complete-kinds/deps'
        stale=re.findall(re.escape(str(oldpool))+r'/lib(?:symbolica|oneloop|iregi_[A-Za-z0-9_]+)-[^\s()]*?\.rlib',text)
        assert not stale,'Native link map includes a stale project archive: '+repr(stale)
        item['archive_binding']=bindings
        item['link_map']={'path':str(linkmap),'sha256':sha(linkmap),'bytes':linkmap.stat().st_size,
            'scope':'final transformed native-link map; original pure Rust archive paths are not guaranteed after ThinLTO'}
        outputs[linkmap]=item['link_map']['sha256']
        item['rust_archive_provenance']='exact successful compiler argv + hash-bound externs + actual upstream metadata identity and compiler hash matching; not original-path map presence'

    budget.arm()
    try:
        for name in ['RUSTC_BOOTSTRAP','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER']:
            assert not os.environ.get(name),'Unexpected inherited compiler override: '+name
        verify();record['guard_before']=True
        proof=read(protocol['proof']);assert proof['status']=='completed_readonly_project_dependency_identity_proof_no_build'
        allowed=lower_from_proof(proof)
        fresh=proof['fresh']
        oldsteps=protocol['original_all_steps']
        for step in oldsteps[:4]:
            item=record['reused_products'][step['label']]
            saved=fresh[step['command'][step['command'].index('--crate-name')+1]]
            root=parse(Path(saved['metadata_path']).read_text())
            assert root=={key:saved[key]for key in ['name','crate_hash','stable_crate_id','dependencies']}
            required={name:variant_shared['baseline'][name]for name in variant_shared['baseline']}
            admit(root,expected_root_name=root['name'],allowed_lower=allowed,required_fresh=required)
            metadata_by_artifact[item['path']]=root
            item['actual_metadata']=root;item['provenance_admission']='passed-v3'
            if step['product']!='core':variant_shared['baseline'][root['name']]=root
        probe_step=oldsteps[4]
        probe=record['reused_products'][probe_step['label']]
        prove_probe(probe_step,probe);probe['provenance_admission']='passed-v3'
        save(receipt,record)
        for step in record['steps']:
            verify();output=Path(step['output']);output.parent.mkdir(parents=True,exist_ok=True)
            env=dict(os.environ);env.update(step['environment'])
            def persist(result):step.update(result);save(receipt,record)
            log=attempt/(step['label']+'.log')
            result=execute(step['command'],log,budget,step['compiler_cap_seconds'],record['cleanup_errors'],persist,env)
            assert result['status']=='exited','Compiler failed/timed out; preserve first terminal result'
            verify()
            with output.open('rb')as stream:header=stream.read(8)
            assert header==(b'\x7fELF\x02\x01\x01\x00'if step['product']=='probe'else b'!<arch>\n')
            item={'path':str(output),'sha256':sha(output),'bytes':output.stat().st_size}
            outputs[output]=item['sha256']
            # Store the successful compiler output before any provenance read.
            record['outputs'][step['label']]=item
            step.update(log_sha256=sha(log),output_sha256=item['sha256'])
            save(receipt,record)
            if step['product']=='probe':
                prove_probe(step,item)
            else:
                command=[part.replace('<new-archive>',str(output))for part in protocol['metadata_read_command']]
                event={'label':step['label'],'artifact':str(output),'artifact_sha256':item['sha256'],'command':command,'status':'unrun'}
                record['metadata_reads'].append(event)
                metadata_log=attempt/(step['label']+'.metadata.txt')
                metadata_env=dict(os.environ);metadata_env.update(protocol['metadata_read_environment_override'])
                def persist_metadata(result):event.update(result);save(receipt,record)
                result=execute(command,metadata_log,budget,protocol['metadata_read_cap_seconds'],record['cleanup_errors'],persist_metadata,metadata_env)
                assert result['status']=='exited','Metadata inspection failed; no retry'
                root=parse(metadata_log.read_text())
                name=step['command'][step['command'].index('--crate-name')+1]
                required=variant_shared[step['variant']]
                admit(root,expected_root_name=name,allowed_lower=allowed,required_fresh=required)
                metadata_by_artifact[str(output)]=root
                if step['product']!='core':variant_shared[step['variant']][name]=root
                item['actual_metadata']=root
                item['metadata_log']={'path':str(metadata_log),'sha256':sha(metadata_log),'bytes':metadata_log.stat().st_size}
                outputs[metadata_log]=item['metadata_log']['sha256']
                event.update(status='passed',metadata_sha256=sha(metadata_log),actual_root_hash=root['crate_hash'])
            item['provenance_admission']='passed-v3';step['status']='passed'
            verify();save(receipt,record)
        record['status']='completed-awaiting-final-guards'
    except Exception as error:record.update(status='failed',error=repr(error))
    save(receipt,record)
    try:verify();record['guard_after']=True
    except Exception as error:record.update(guard_after=False,guard_error=repr(error))
    record['elapsed_seconds_diagnostic']=budget.elapsed()
    record['deadline_exceeded']=record['elapsed_seconds_diagnostic']>protocol['aggregate_budget_seconds']
    if budget.cancelled:record['cancellation']=budget.cancelled
    record['success']=(all(s['status']=='passed'for s in record['steps'])and record.get('guard_after')is True
        and not record['cleanup_errors']and not record['deadline_exceeded']and not budget.cancelled and 'error'not in record)
    record['status']='passed'if record['success']else'failed';save(receipt,record);budget.disarm()
    if record['success']:
        merged={'status':'passed','success':True,'scope':'Compiler/provenance admission only; no numerical or timing qualification',
            'protocol_sha256':reviewed,'guard_before':record['guard_before'],'guard_after':record['guard_after'],'cleanup_errors':[],
            'original_failed_receipt':protocol['original_failed_receipt'],'original_failed_receipt_sha256':protocol['original_failed_receipt_sha256'],
            'original_failure_preserved':'ThinLTO original-archive-path map gate failed after five successful compilers; v3 corrects provenance without rebuilding those products',
            'continuation_receipt':str(receipt),'continuation_receipt_sha256':sha(receipt),
            'outputs':{**record['reused_products'],**record['outputs']},
            'steps':[dict(s,status='passed',original_step_status='exited'if s['product']=='probe'else'passed',admission='v3-metadata')for s in protocol['original_all_steps'][:5]]+record['steps'],
            'rust_archive_metadata_count':len(metadata_by_artifact),'numerical_qualified':False,'performance_qualified':False}
        save(attempt/'complete-build-admission.json',merged)
    print(json.dumps({'status':record['status'],'receipt_sha256':sha(receipt),'new_compiler_outputs':len(record['outputs']),
        'reused_products':len(record['reused_products']),'elapsed_seconds_diagnostic':record['elapsed_seconds_diagnostic']}))
    return 0 if record['success']else 1

if __name__=='__main__':raise SystemExit(main())
