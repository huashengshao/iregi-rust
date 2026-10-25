"""Saved-data/pure-negative provenance tests. Never starts a child process."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode = True
ROOT = Path('/shared/external/iregi/iregi-rust')
HERE = ROOT/'target/guard-performance-review/optimized-performance-proposal/v3'
RESEARCH = HERE.parent/'provenance-v3-research'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    assert Path.cwd() == ROOT
    spec = importlib.util.spec_from_file_location('private_provenance_saved_test', HERE/'provenance.py')
    p = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p)
    proof_path = RESEARCH/'lower-admission-inputs.json'
    proof = json.loads(proof_path.read_text())
    lower = p.lower_from_proof(proof)
    bindings = p.binding_requirements(proof)
    for path, expected in bindings.items():
        assert sha(Path(path)) == expected, path
    metadata_count = 0
    for name, record in proof['lower_roots'].items():
        actual = p.parse(Path(record['metadata_path']).read_text())
        assert actual == {key: record[key] for key in ['name','crate_hash','stable_crate_id','dependencies']}
        assert actual['name'] == name
        metadata_count += 1
    predecessors = {}
    chain = []
    for name in ['symbolica','oneloop','iregi_masters','iregi_rust']:
        raw = proof['fresh'][name]
        actual = p.parse(Path(raw['metadata_path']).read_text())
        assert actual == {key: raw[key] for key in ['name','crate_hash','stable_crate_id','dependencies']}
        result = p.admit(actual, expected_root_name=name, allowed_lower=lower,
                         required_fresh=predecessors)
        chain.append(result)
        predecessors[name] = actual
    negative = []
    def reject(label, fn):
        try:
            fn()
        except p.ProvenanceError:
            negative.append(label)
        else:
            raise AssertionError('Admitted negative case: ' + label)
    text = Path(proof['fresh']['symbolica']['metadata_path']).read_text()
    first_dep = text.split('=External Dependencies=\n')[1].splitlines()[0]
    reject('duplicate dependency row', lambda: p.parse(text+'\n'+first_dep+'\n'))
    reject('duplicate root name', lambda: p.parse(text.replace('name symbolica','name symbolica\nname symbolica',1)))
    reject('duplicate root hash', lambda: p.parse(text.replace('hash '+predecessors['symbolica']['crate_hash'], 'hash '+predecessors['symbolica']['crate_hash']+' stable_crate_id StableCrateId(1)\nhash '+predecessors['symbolica']['crate_hash'],1)))
    reject('unparsed dependency', lambda: p.parse(text+'\n999 invalid row\n'))
    reject('unsupported linkage', lambda: p.parse(text.replace('kind Unconditional public','kind Unconditional public linkage Some(Unknown)',1)))
    reject('omitted dependency index', lambda: p.parse(text.replace('\n1 std-', '\n2 std-', 1)))
    reject('wrong root', lambda: p.admit(predecessors['symbolica'], expected_root_name='oneloop', allowed_lower=lower, required_fresh={}))
    reject('wrong expected root hash', lambda: p.admit(predecessors['symbolica'], expected_root_name='symbolica', allowed_lower=lower, required_fresh={}, expected_root_hash='1'))
    def bad_actual(label, name, mutate, required):
        bad=copy.deepcopy(predecessors[name]);mutate(bad)
        reject(label, lambda: p.admit(bad, expected_root_name=name, allowed_lower=lower, required_fresh=required))
    required={'symbolica':predecessors['symbolica']}
    bad_actual('wrong fresh hash','oneloop',lambda x:x['dependencies'].__setitem__('symbolica','1'),required)
    bad_actual('missing fresh root','oneloop',lambda x:x['dependencies'].pop('symbolica'),required)
    bad_actual('unexpected stale alias','oneloop',lambda x:x['dependencies'].__setitem__('symbolica-2ae1abcc9fd9c0db','1'),required)
    bad_actual('unknown lower','symbolica',lambda x:x['dependencies'].__setitem__('unknown','1'),{})
    bad_actual('actual root hash collision','symbolica',lambda x:x.__setitem__('crate_hash',next(iter(lower.values()))),{})
    keys=list(predecessors['symbolica']['dependencies'])
    bad_actual('actual dependency hash collision','symbolica',lambda x:x['dependencies'].__setitem__(keys[1],x['dependencies'][keys[0]]),{})
    bad_actual('missing inherited transitive','oneloop',lambda x:x['dependencies'].pop(keys[0]),required)
    alias=copy.deepcopy(predecessors['symbolica']);alias['name']='symbolica-2ae1abcc9fd9c0db'
    reject('root stale alias even when requested',lambda:p.admit(alias,expected_root_name=alias['name'],allowed_lower=lower,required_fresh={}))
    badlower=copy.deepcopy(lower);badlower['iregi_rust']='1'
    reject('project in lower allowlist',lambda:p.admit(predecessors['symbolica'],expected_root_name='symbolica',allowed_lower=badlower,required_fresh={}))
    badlower=copy.deepcopy(lower);badlower['unknown']=next(iter(lower.values()))
    reject('allowlist hash collision',lambda:p.admit(predecessors['symbolica'],expected_root_name='symbolica',allowed_lower=badlower,required_fresh={}))
    def bad_proof(label, mutate):
        bad=copy.deepcopy(proof);mutate(bad)
        reject(label,lambda:p.lower_from_proof(bad))
    bad_proof('partial lower proof status',lambda x:x.__setitem__('status','preparing'))
    bad_proof('original search directory relabelled guarded',lambda x:x.__setitem__('original_full_search_directory_was_pre_guarded',True))
    first=next(iter(proof['lower_roots']))
    bad_proof('omitted observed lower root',lambda x:x['lower_roots'].pop(first))
    bad_proof('missing file hash binding',lambda x:x['lower_roots'][first].__setitem__('sha256',''))
    bad_proof('unknown lower metadata dependency',lambda x:x['lower_roots'][first]['dependencies'].__setitem__('unknown','1'))
    bad_proof('missing closed inventory root',lambda x:x['closed_lower_symlink_inventory'].pop(next(iter(x['closed_lower_symlink_inventory']))))
    bad_proof('closed inventory wrong hash',lambda x:x['closed_lower_symlink_inventory'][next(iter(x['closed_lower_symlink_inventory']))].__setitem__('crate_hash','1'))
    sysroot=next(name for name,raw in proof['lower_roots'].items() if raw['artifact'].endswith('.rmeta'))
    bad_proof('sysroot new-binding scope erased',lambda x:x['lower_roots'][sysroot].__setitem__('metadata_context_origin','old pre-run rmeta binding'))
    bad_proof('missing new sysroot binding',lambda x:x['new_sysroot_rmeta_bindings'].pop(next(iter(x['new_sysroot_rmeta_bindings']))))
    bad_proof('wrong edge count',lambda x:x.__setitem__('validated_metadata_dependency_edges',0))
    bad_proof('numeric qualification overclaim',lambda x:x.__setitem__('numerical_qualified',True))
    bad_proof('erased stale observations',lambda x:x.__setitem__('stale_root_observations',[]))
    report={
        'status':'passed-pure-saved-data-tests-only',
        'helper_sha256':sha(HERE/'provenance.py'),'test_source_sha256':sha(Path(__file__)),
        'scoped_lower_proof_sha256':sha(proof_path),'actual_declared_file_hashes_checked':len(bindings),
        'saved_lower_metadata_roundtrips':metadata_count,'saved_fresh_chain_roots':len(chain),
        'scoped_lower_root_pairs':len(lower),'scoped_closed_metadata_edges':proof['validated_metadata_dependency_edges'],
        'negative_cases':negative,'negative_case_count':len(negative),
        'fresh_chain_admissions':chain,
        'compiler_or_numerical_subprocesses_launched':False,
        'qualification_scope':'Saved metadata/hash identity checks only; no new build, numerical or performance qualification.',
    }
    out=HERE/'provenance-pure-tests.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:value for key,value in report.items() if key!='fresh_chain_admissions'}))

if __name__=='__main__':
    main()
