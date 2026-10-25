#!/usr/bin/env python3
"""Reconstruct an unexecuted source proposal from committed parent bytes only."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode=True


def require(value,message):
    if not value:raise ValueError(message)


def sha(body):return hashlib.sha256(body).hexdigest()


def main():
    here=Path(__file__).resolve().parent
    manifest=json.loads((here/'manifest.json').read_text())
    require(manifest['status']=='uncompiled_unexecuted_rectangular_source_proposal','source scope changed')
    actual={str(p.relative_to(here)) for p in here.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    require(actual==set(manifest['files'])|{'manifest.json'},'source proposal inventory differs')
    for name,expected in manifest['files'].items():
        p=here/name
        require(name==str(Path(name)) and not Path(name).is_absolute() and '..' not in Path(name).parts
                and not p.is_symlink(),'unsafe source proposal member')
        body=p.read_bytes()
        require({'sha256':sha(body),'bytes':len(body)}==expected,'source proposal file changed: '+name)
    candidates=[here]+list(here.parents)
    root=next((p for p in candidates if (p/'Cargo.toml').is_file() and (p/manifest['parent_capsule']['path']/'manifest.json').is_file()),None)
    require(root is not None,'committed full-component parent capsule not found')
    parent=root/manifest['parent_capsule']['path']
    body=(parent/'manifest.json').read_bytes();require(sha(body)==manifest['parent_capsule']['manifest_sha256'],'parent capsule changed')
    parent_manifest=json.loads(body)
    require(parent_manifest['status']=='sealed_private_full_component_n6_saved_correctness','parent capsule not sealed')
    for name,expected in parent_manifest['files'].items():
        body=(parent/name).read_bytes();require({'sha256':sha(body),'bytes':len(body)}==expected,'parent file changed: '+name)
    spec=importlib.util.spec_from_file_location('_committed_component_source',parent/'portable.py')
    tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
    base,_,borrowed=tools.load_parent(root)
    payload=tools.archive((parent/'payload.tar.gz').read_bytes(),parent_manifest['payload_archive']['members'])
    snapshots=tools.reconstruct_sources(base,payload,borrowed)
    source=json.loads((here/'source-manifest.json').read_text())
    require(sha((here/'proposal.patch').read_bytes())==source['patch']['sha256'],'source patch provenance differs')
    require(sha(payload[tools.NUMERIC+'/qualification-summary.json'])==source['parent_completed_cohort']['sha256'],'wrong completed cohort parent')
    require(sha(payload[tools.NUMERIC+'/source-v2.json'])==source['base_numerical_source_manifest']['sha256'],'wrong numerical source parent')
    result,changed=tools.apply_source_patch(snapshots['numerical-v2'],(here/'proposal.patch').read_bytes())
    require(changed==source['changed_or_added_files'] and len(result)==93,'rectangular source delta differs')
    require({n:tools.descriptor(b) for n,b in result.items()}==source['files'],'complete93-source reconstruction differs')
    require(source['shape']==[[0,0],[1,0],[0,1],[1,1]] and source['helper_tests_written_not_executed']==6,'shape/source-test scope differs')
    require(all(source[k] is False for k in ['compilation','tests_executed','numeric_execution_authorized','public_promotion','performance_claim']),'source proposal scope promoted')
    print(json.dumps({'status':'passed_source_reconstruction_only','source_files':len(result),'changed_source_files':changed,'rust_compilation_tests_or_evaluators_executed':False,'numerical_execution_authorized':False,'public_dual_qualified':False},sort_keys=True))


if __name__=='__main__':main()
