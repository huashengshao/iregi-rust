"""Source-only preparation for a bounded ThinLTO provenance correction.

Preserve the original failed map gate and all five successful compiler products.
No product is rebuilt here and no executable/kernel is launched.
"""
from pathlib import Path
import copy, datetime, hashlib, json, os, shutil, sys

ROOT=Path('/shared/external/iregi/iregi-rust')
BASE=ROOT/'target/guard-performance-review/optimized-performance-proposal'
HERE=BASE/'v3'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def read(path):return json.loads(Path(path).read_text())
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')

def main():
    assert Path.cwd()==ROOT and not (HERE/'protocol.json').exists()
    original_protocol=BASE/'fresh-build-protocol.json'
    assert sha(original_protocol)=='4821d86ef2ecfc5be1490da7b88f631a22db9386cc02697f7b506897dd1fac67'
    original=read(original_protocol)
    receipt=Path(original['attempt_directory'])/'build.json'
    assert sha(receipt)=='9069bc03597f0a423ef1271257472ce90e79b685b8f2e5f7d6f8824ee88386d8'
    old=read(receipt)
    assert old['status']=='failed' and old['guard_before'] and old['guard_after']
    assert not old['cleanup_errors'] and not old['deadline_exceeded']
    assert old['error']=="AssertionError('symbolica archive contamination: []')"
    assert len(old['outputs'])==4
    assert all(s['status']=='passed' for s in old['steps'][:4])
    assert old['steps'][4]['status']=='exited' and old['steps'][4]['returncode']==0 and old['steps'][4]['owned_group_gone']
    assert all(s['status']=='unrun' for s in old['steps'][5:])
    protected=dict(original['protected_sha256'])
    tools=dict(original['tool_sha256'])
    tools[str(Path(sys.executable))]=sha(Path(sys.executable))

    def bind(path,expected=None):
        value=sha(path)
        assert expected is None or value==expected,str(path)
        protected[str(Path(path).relative_to(ROOT)) if Path(path).is_relative_to(ROOT) else str(path)]=value
        return value

    for raw,expected in {**protected,**tools}.items():
        assert sha(Path(raw) if Path(raw).is_absolute() else ROOT/raw)==expected,raw
    # These named research receipts distinguish observed identities from the
    # preserved metadata-stub decoding failure and supplemental rmeta context.
    proof_path=BASE/'provenance-v3-research/lower-admission-inputs.json'
    proof=read(proof_path)
    assert proof['status']=='completed_readonly_project_dependency_identity_proof_no_build'
    from provenance import lower_from_proof,binding_requirements
    allowed=lower_from_proof(proof)
    assert len(allowed)==127
    for raw,expected in binding_requirements(proof).items():bind(Path(raw),expected)
    for path in [original_protocol,receipt,proof_path,
                 BASE/'reviews/thinlto-link-map-source-followup.json',HERE/'prepare_continuation.py',
                 HERE/'build_continuation.py',HERE/'provenance.py']:
        bind(path)
    research_bindings=dict(proof['source_sha256'])
    research_bindings.update({item['artifact']:item['sha256']for item in proof['lower_roots'].values()})
    research_bindings.update(proof['original_guarded_sysroot_rlibs'])
    for raw,expected in research_bindings.items():bind(Path(raw),expected)
    for path in (BASE/'provenance-v3-research').rglob('*'):
        if path.is_file() and path.suffix in ['.json','.py','.txt','.log']:
            bind(path)
    reused={name:copy.deepcopy(item) for name,item in old['outputs'].items()}
    prior_probe=old['steps'][4]
    output=Path(prior_probe['output'])
    assert sha(output)=='c951c1e4cbe1885069181f58e22308387468694862599aabf10ca2e92c2c4587'
    linkmap=Path(prior_probe['link_map'])
    assert sha(linkmap)=='caf71d700d99d19167e72a4f21fee75e2cbc5d668dedc8647052f7455dab2206'
    reused[prior_probe['label']]={'path':str(output),'sha256':sha(output),'bytes':output.stat().st_size,
        'link_map':{'path':str(linkmap),'sha256':sha(linkmap),'bytes':linkmap.stat().st_size},
        'original_compiler_returncode':0,'original_owned_group_gone':True,
        'original_exact_map_gate':'failed-as-preserved','provenance_admission':'pending-v3-review'}
    for item in reused.values():
        bind(Path(item['path']),item['sha256'])
        if 'link_map'in item:bind(Path(item['link_map']['path']),item['link_map']['sha256'])

    # Closed lower search space for all nine new compiler invocations. Symlinks
    # preserve existing artifact bytes without another large dependency copy.
    closed=HERE/'closed-lower-deps'
    closed.mkdir(exist_ok=False)
    link_inventory={}
    for filename,entry in proof['closed_lower_symlink_inventory'].items():
        source=Path(entry['target']);expected=entry['sha256']
        assert source.suffix in ['.rlib','.so']
        assert not source.name.startswith(('libsymbolica-','liboneloop-','libiregi_'))
        assert filename==source.name
        destination=closed/filename
        destination.symlink_to(source)
        assert sha(destination)==expected
        link_inventory[str(destination)]={'target':str(source),'sha256':expected,'bytes':source.stat().st_size}
    original_pool=ROOT/'target/benchmark/dependency-closures/6b24c03-complete-kinds/deps'
    for step in original['steps']:
        for value in step['explicit_externs'].values():
            path=Path(value)
            if path.parent==original_pool:
                assert str(closed/path.name) in link_inventory,path
    save(HERE/'closed-search-inventory.json',link_inventory)
    bind(HERE/'closed-search-inventory.json')
    remaining=[]
    for old_step in original['steps'][5:]:
        step=copy.deepcopy(old_step)
        command=step['command']
        command=[f'dependency={closed}' if value==f'dependency={original_pool}' else value for value in command]
        for name,value in list(step['explicit_externs'].items()):
            path=Path(value)
            if path.parent==original_pool:
                alias=closed/path.name
                command=[f'{name}={alias}' if part==f'{name}={path}' else part for part in command]
                step['explicit_externs'][name]=str(alias)
        step['command']=command
        step['rust_archive_admission']='actual-metadata-root-and-transitive-identity; successful exact compiler argv/externs; guarded inputs/outputs and closed lower search'
        step.pop('expected_link_archives',None)
        remaining.append(step)
    assert len(remaining)==9
    protocol={
        'schema_version':1,'status':'SOURCE_REVIEW_REQUIRED_NO_COMPILER_GRANT',
        'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cwd':str(ROOT),
        'scope':'Reuse five successful compiler products from preserved failed literal-map stage; compile exactly nine previously unrun products. Correct ThinLTO provenance using actual fresh archive metadata identities and a closed lower search space. No numerical or timing execution.',
        'aggregate_budget_seconds':2400,'cleanup_postguard_reserve_seconds':30,'effective_work_deadline_seconds':2370,
        'cpu_affinity':'32,33','attempt_directory':str(HERE/'build-001'),'steps':remaining,
        'original_protocol':str(original_protocol),'original_protocol_sha256':sha(original_protocol),
        'original_failed_receipt':str(receipt),'original_failed_receipt_sha256':sha(receipt),
        'original_all_steps':original['steps'],'reused_products':reused,
        'proof':str(proof_path),'proof_sha256':sha(proof_path),
        'closed_lower_inventory':str(HERE/'closed-search-inventory.json'),'closed_lower_inventory_sha256':sha(HERE/'closed-search-inventory.json'),
        'protected_sha256':protected,'tool_sha256':tools,
        'metadata_read_command':[original['steps'][0]['command'][0],'-c','32,33',original['steps'][0]['command'][3],'-Zls=root','<new-archive>'],
        'metadata_read_environment_override':{'RUSTC_BOOTSTRAP':'1'},
        'metadata_read_cap_seconds':10,
        'literal_map_policy':'Full maps retained as final transformed native-link evidence; original Rust rlib paths need not survive ThinLTO. Never claim a map directly names all fresh Rust archives.',
        'old_search_scope':'Original five compilers used the recorded historical broad pool, not retroactively a closed inventory. Their guarded explicit externs and actual fresh archive dependency identities bind the project chain; stale same-name archive hashes are rejected by rustc metadata selection. The new nine compilers use closed lower aliases.',
        'failure_policy':'Stop first codegen/metadata/parser/guard/cleanup failure; preserve first evidence. No automatic retry or budget extension. Never alter original failed receipt.',
        'success_is_compiler_and_provenance_only':True,'numerical_qualified':False,'performance_qualified':False,'production_adoption_authorized':False}
    save(HERE/'protocol.json',protocol)
    print(json.dumps({'protocol_sha256':sha(HERE/'protocol.json'),'reused_products':5,'new_compilers':9,'closed_lower_files':len(link_inventory),'protected_inputs':len(protected),'no_compiler_or_integral_run':True}))

if __name__=='__main__':main()
