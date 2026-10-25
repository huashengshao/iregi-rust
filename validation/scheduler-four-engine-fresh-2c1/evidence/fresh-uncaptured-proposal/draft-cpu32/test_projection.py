"""Pure schema/projection tests using historical saved records as fixtures only.

No newly built executable is run. Constructed capture-free fixtures are not new
numerical results and cannot qualify any fresh artifact or performance gate.
"""
from pathlib import Path
import ast
import copy
import hashlib
import json
import sys
sys.dont_write_bytecode = True
import admission as a
import captured_admission as cap
import projection
ROOT=Path('/shared/external/iregi/iregi-rust')
HERE=ROOT/'target/guard-performance-review/optimized-performance-proposal/fresh-uncaptured-proposal'
OLD=ROOT/'target/guard-performance-review/dependent-runtime-proposal'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def fixture(value):
    if type(value) is dict:
        result={key:([] if key=='master_captures' else fixture(item))for key,item in value.items()}
        if set(result)=={'id','result'}:
            result['result']['scope']='untimed capture-free scheduler whole-reduction qualification'
            result['result']['capture_enabled']=False
        return result
    if type(value) is list:
        return[fixture(item)for item in value]
    return copy.deepcopy(value)

def main():
    assert Path.cwd()==ROOT
    cases=json.loads((ROOT/'validation/native-master-replay/inputs.json').read_text())
    shape=json.loads((HERE/'control-shapes.json').read_text())
    receipt=json.loads((OLD/'qualification-001/results.json').read_text())
    raw=[json.loads(line)for line in(OLD/'qualification-001/responses.jsonl').read_text().splitlines()]
    saved=projection.SavedCapture(receipt,raw,cases,shape)
    for serial,record in saved.records.items():
        if record['stage']=='invalid-request':continue
        actual=fixture(record['response'])
        saved.compare(serial,record['stage'],record['key'],record['engine'],record['payload'],actual)
    assert len(saved.compared)==52
    # Direct scalar validators are exactly the original source ASTs.
    def functions(path):
        tree=ast.parse(path.read_text());return {node.name:ast.dump(node,include_attributes=False)for node in tree.body if isinstance(node,ast.FunctionDef)}
    original=functions(OLD/'admission.py');current=functions(HERE/'admission.py')
    changed=sorted(name for name in original if original[name]!=current[name])
    assert changed==['captures','response']
    for name in ['snapshot','selected','unchanged','number','complex_value','numeric_domain','execution','moment_lane','core_control','controls']:
        assert original[name]==current[name],name
    negative=[]
    def reject(label,fn):
        try:fn()
        except (AssertionError,KeyError,ValueError):negative.append(label)
        else:raise AssertionError('Admitted '+label)
    record=saved.records[1]
    def compare_bad(label,mutate,field=None):
        actual=fixture(record['response']);mutate(actual)
        other=projection.SavedCapture(receipt,raw,cases,shape)
        reject(label,lambda:other.compare(1,record['stage'],record['key'],record['engine'],record['payload']if field is None else field,actual))
    compare_bad('plan_reused must match same phase',lambda x:x['result'].__setitem__('plan_reused',not x['result']['plan_reused']))
    compare_bad('nonempty whole-core captures rejected',lambda x:x['result'].__setitem__('master_captures',[{}]))
    compare_bad('unknown result field rejected',lambda x:x['result'].__setitem__('unknown',True))
    compare_bad('capture flag true rejected',lambda x:x['result'].__setitem__('capture_enabled',True))
    compare_bad('scope must explicitly be capture-free',lambda x:x['result'].__setitem__('scope','untimed generic-only scheduler whole-reduction qualification'))
    compare_bad('normal payload must match exactly',lambda x:None,field=record['payload'].rstrip()+' \n')
    # Projection must retain every direct scalar result, even if a caller bypassed
    # schema checks. Change the direct-master control object without touching
    # capture observations; projected objects must differ.
    control=saved.records[33]['response'];altered=fixture(control)
    altered['masters']['status']='changed'
    assert not cap.exact(projection.project(altered),projection.project(control))
    reject('direct master schema still checked',lambda:a.controls(altered,shape))
    altered=fixture(control);altered['cache_interleaving']['steps'][0]['result']['master_captures']=[{}]
    reject('cache observation captures must be empty',lambda:a.controls(altered,shape))
    output={
        'status':'passed-pure-saved-fixture-tests-only',
        'scope':'Historical saved captured records transformed in memory solely to test schemas/projection. These are not observed fresh capture-free results.',
        'historical_fixture_receipt_sha256':sha(OLD/'qualification-001/results.json'),
        'historical_fixture_raw_sha256':sha(OLD/'qualification-001/responses.jsonl'),
        'normal_fixture_projections':52,'historical_raw_events_parsed':120,
        'changed_admission_functions':changed,
        'direct_scalar_and_other_admission_functions_unchanged':True,
        'negative_cases':negative,'negative_case_count':len(negative),
        'source_sha256':{p.name:sha(p)for p in[HERE/'test_projection.py',HERE/'projection.py',HERE/'admission.py',HERE/'captured_admission.py']},
        'preparer_or_runner_invoked':False,'compiler_or_numerical_executable_launched':False,
        'fresh_numerical_qualified':False,'performance_qualified':False,
    }
    path=HERE/'pure-projection-tests.json';path.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output))

if __name__=='__main__':main()
