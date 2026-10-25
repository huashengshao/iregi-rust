"""Portable stdlib saved-source/record check; launches no compiler or reducer."""
from pathlib import Path
import hashlib,io,json,re,tarfile,sys
HERE=Path(__file__).resolve().parent
checks=0

def require(ok,why):
    global checks
    if not ok:raise ValueError(why)
    checks+=1

def digest(body):return hashlib.sha256(body).hexdigest()
def archive(name,expected):
    result={}
    with tarfile.open(HERE/name,'r:gz') as tar:
        for member in tar.getmembers():
            p=Path(member.name)
            require(member.isfile() and not p.is_absolute() and '..' not in p.parts and member.name not in result,'safe unique archive member')
            result[member.name]=tar.extractfile(member).read()
    require(set(result)==set(expected),'closed archive inventory '+name)
    for path,body in result.items():require(digest(body)==expected[path]['sha256'] and len(body)==expected[path]['bytes'],'exact archive body '+path)
    return result

def main():
    manifest=json.loads((HERE/'manifest.json').read_text())
    for name,d in manifest['files'].items():require(digest((HERE/name).read_bytes())==d,'exact capsule file '+name)
    sources=archive('sources.tar.gz',json.loads((HERE/'source-inventory.json').read_text()))
    records=archive('records.tar.gz',manifest['records'])
    def read(name):return json.loads(records[name])
    aliases={path:(sources if v['archive']=='sources' else records)[v['name']] for path,v in manifest['aliases'].items()}
    q=json.loads((HERE/'qualification.json').read_text());require(q['selected_tests_passed']==18 and not q['integral_array_qualified'] and not q['performance_qualified'],'limited eighteen-test scope')
    original=read('original/execution/build-001/receipt.json');fast=read('fast/execution/build-001/receipt.json');tests=read('fast/execution/tests-001/receipt.json')
    require(original['status']=='failed_or_incomplete' and original['inputs_unchanged'] is True and original['steps'][0].get('timeout') is True and original['steps'][0]['timeout_seconds']==1080,'original timeout retained')
    require(original['steps'][0]['owned_group_gone'] is True and original['cleanup_errors']==[] and original['elapsed_seconds']<1200,'original bounded successful cleanup')
    require(fast['status']=='passed' and fast['inputs_unchanged'] is True and fast['elapsed_seconds']<600 and fast['cleanup_errors']==[],'corrected build passed in bound')
    require(fast['artifact']['profile']['opt_level']=='0' and fast['artifact']['profile']['debuginfo']==0 and fast['artifact']['profile']['test'] is True,'test-only corrected profile')
    observed=read('original/execution/build-001/actual-rustc-command-observation.json')['owned_rustc'][0]
    features=sorted(v.split('=',1)[1].strip('"') for v in observed['feature_cfgs'])
    require(sorted(fast['artifact']['features'])==features and 'opt-level=2' in observed['codegen_flags'] and 'debuginfo=2' in observed['codegen_flags'],'source-compatible coherent feature set; old flags preserved')
    require(tests['status']=='passed' and tests['completed_selected_tests']==tests['selected_count']==18 and tests['inputs_unchanged'] is True and tests['elapsed_seconds']<300 and not tests['cleanup_errors'],'eighteen successful tests')
    require(len(tests['steps'])==19,'one listing and eighteen exact test processes')
    for receipt in (original,fast,tests):
        for path,sha in receipt['inputs'].items():
            if path in manifest['omitted_compiled_artifacts']:
                require(sha==manifest['omitted_compiled_artifacts'][path],'explicit exact binary omission')
            else:require(path in aliases and digest(aliases[path])==sha,'saved guard binding '+path)
        for step in receipt['steps']:
            require(step.get('owned_group_gone') is True,'recorded owned-group cleanup')
    protocol=read('fast/protocol.json');require(tests['protocol_sha256']==digest(records['fast/protocol.json']) and tests['build_receipt_sha256']==digest(records['fast/execution/build-001/receipt.json']),'matched runtime/build protocol')
    require(len(protocol['selected_tests'])==18 and len(set(protocol['selected_tests']))==18,'eighteen distinct exact names')
    listing=records['fast/execution/tests-001/listing.log'].decode();listed=[line[:-6] for line in listing.splitlines() if line.endswith(': test')]
    for index,name in enumerate(protocol['selected_tests']):
        require(listed.count(name)==1,'exact selected name listed')
        text=records['fast/execution/tests-001/test-'+str(index+1).zfill(2)+'.log'].decode();lines=text.splitlines()
        headers=[line for line in lines if line.startswith('test ') and not line.startswith('test result:')];summaries=[line for line in lines if line.startswith('test result:')]
        require(lines.count('running 1 test')==1 and len(headers)==1 and headers[0].startswith('test '+name+' ... '),'one named test log')
        require(len(summaries)==1 and re.fullmatch(r'test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; [0-9]+ filtered out; finished in [^\n]+',summaries[0]) is not None,'strict successful summary')
        block=text[text.index(headers[0]):text.index(summaries[0])].rstrip();require(re.search(r'(?:^|\s)ok$',block) is not None,'explicit named test completion')
        step=tests['steps'][index+1];require(step['returncode']==0 and step['status']=='exited' and not step.get('timeout') and step['log_sha256']==digest(text.encode()),'strict saved owned step')
    require(sources['dependencies/symbolica/src/evaluate/tree.rs']==records['proposal/tree.candidate.rs'],'actual built source equals reviewed candidate')
    require(digest(records['proposal/0005-reuse-dominating-condition-facts.patch'])=='5582e023c8d293a9e17310637aeee7009a3104a4024b9253c3e108c1ecabf5c5','post-validation series patch exact')
    print(json.dumps({'status':'passed_saved_source_and_records','checks':checks,'source_files':len(sources),'record_files':len(records),'selected_tests':18,'native_jobs':0,'compiler_jobs':0,'integral_array_qualified':False,'performance_qualified':False}))
if __name__=='__main__':main()
