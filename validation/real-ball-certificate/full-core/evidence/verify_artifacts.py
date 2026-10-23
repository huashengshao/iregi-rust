"""Private immutable-source/closure checks; no numerical engine imports."""
from pathlib import Path
import hashlib,json
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
CLOSURE=ROOT/'target/benchmark/dependency-closures/6b24c03-complete-kinds'
def sha(path):
    with Path(path).open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()
def closure_binding():
    paths={name:CLOSURE/name for name in ['manifest.json','cargo-library-events.json','workspace-completion.json']}
    manifest=json.loads(paths['manifest.json'].read_text());completion=json.loads(paths['workspace-completion.json'].read_text())
    assert completion['cargo_returncode']==0
    assert completion['dependency_closure_manifest_sha256']==sha(paths['manifest.json'])
    assert completion['workspace_manifest_sha256']==sha(Path(manifest['workspace_build_manifest']))
    return {name:sha(path) for name,path in paths.items()}
def verify_closure(expected):
    assert closure_binding()==expected
    manifest=json.loads((CLOSURE/'manifest.json').read_text())
    for record in manifest['files']+manifest['native_files']:
        path=Path(record['retained']);assert path.stat().st_size==record['bytes'] and sha(path)==record['sha256'],str(path)
    return len(manifest['files'])+len(manifest['native_files'])
def bind_build(variant,kind):
    if variant=='baseline' and kind=='physical':
        path=ROOT/'target/benchmark/workspace-builds/6b24c03-default/workspace-build.json';data=json.loads(path.read_text());binary=data['binaries']['physical_benchmark']
        binding={'producer_kind':'completed_workspace','manifest':str(path.relative_to(ROOT)),'manifest_sha256':sha(path),'binary':str(Path(binary['path']).relative_to(ROOT)),'binary_sha256':binary['sha256'],'scope':'Correctness-only baseline reused from completed immutable6b24 workspace; Cargo and private candidate link recipes differ; excluded from paired timing.'}
        verify_build(binding);return binding
    path=OUT/variant/'artifacts'/f'{kind}-build.json';data=json.loads(path.read_text())
    assert data['variant']==variant and data['kind']==kind and data['status']=='compiled' and data['returncode']==0
    assert data['verified_before'] and data['verified_after']
    binary=Path(data['command'][-1]);assert sha(binary)==data['binary_sha256']
    return {'manifest':str(path.relative_to(ROOT)),'manifest_sha256':sha(path),'binary':str(binary.relative_to(ROOT)),'binary_sha256':sha(binary)}
def verify_build(binding):
    path=ROOT/binding['manifest'];assert sha(path)==binding['manifest_sha256'];data=json.loads(path.read_text())
    assert sha(ROOT/binding['binary'])==binding['binary_sha256']
    if binding.get('producer_kind')=='completed_workspace':
        assert data['status']=='complete' and data['provenance_qualified'] is True
        assert type(data['resources']['returncode']) is int and data['resources']['returncode']==0
        assert data['source_revision']=='6b24c0372022e22606a1ac85f30c7fa579fb41f0' and data['master_backend']=='SymbolicaBatch'
        assert data['source_sha256_before']==data['source_sha256'] and data['assets_sha256_before']==data['assets_sha256']
        source=Path(data['source_root'])
        for name,digest in (data['source_sha256']|data['assets_sha256']).items():assert sha(source/name)==digest,name
        event=data['cargo_artifacts']['examples']['physical_benchmark'];binary=data['binaries']['physical_benchmark']
        assert event['target']['name']=='physical_benchmark' and event['profile']['opt_level']=='3' and event['profile']['test'] is False
        assert event['target']['src_path']==str(source/'crates/iregi-cli/examples/physical_benchmark.rs')
        assert event['executable']==binary['original_path'] and event['executable'] in event['filenames']
        assert binding['binary_sha256']==binary['sha256'] and ROOT/binding['binary']==Path(binary['path'])
        completion=json.loads((CLOSURE/'workspace-completion.json').read_text())
        assert completion['workspace_manifest_sha256']==binding['manifest_sha256'] and completion['cargo_returncode']==0
        return
    variant=OUT/data['variant']
    for name,digest in data['source_sha256'].items():assert sha(variant/name)==digest,name
    for name,digest in data.get('supplemental_source_sha256',{}).items():assert sha(Path(name))==digest,name
    for name,digest in data['extern_sha256'].items():assert sha(ROOT/name)==digest,name
    for record in data.get('producer_builds',{}).values():assert sha(ROOT/record['manifest'])==record['sha256']
    assert sha(OUT/'sources.json')==data['source_inventory_sha256']
    assert sha(CLOSURE/'manifest.json')==data['closure_manifest_sha256']
    assert sha(CLOSURE/'cargo-library-events.json')==data['cargo_library_events_sha256']
    assert sha(CLOSURE/'workspace-completion.json')==data['workspace_completion_sha256']
    script=OUT/('build.py' if data['kind']=='unit' else 'build_next.py')
    assert sha(script)==data['build_script_sha256']
