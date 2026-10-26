"""Replay focused primal-amplitude memo source/build/test evidence; no native execution."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, io, json, re, sys, tarfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = 'target/primal-amplitude-memo'
PREFIX = '/shared/external/iregi/iregi-rust/'
POWER = 'validation/affine-power-generalized-current-core'
WHEEL = 'validation/python-interface/facade-wheel-003'
SOURCE = 'crates/iregi-rust/src/stability.rs'

def need(value, why):
    if not value: raise ValueError(why)
def sha(body): return hashlib.sha256(body).hexdigest()
def desc(body): return dict(sha256=sha(body), bytes=len(body))
def load(body):
    def pairs(items):
        result = {}
        for key,value in items:
            need(key not in result, 'duplicate JSON key'); result[key] = value
        return result
    return json.loads(body,object_pairs_hook=pairs)
def safe(name):
    p=PurePosixPath(name)
    need(name and str(p)==name and not p.is_absolute() and '..' not in p.parts,'safe relative path')
def unpack(body, expected):
    result={}
    with tarfile.open(fileobj=io.BytesIO(body),mode='r:gz') as tar:
        for item in tar:
            safe(item.name);need(item.isfile() and item.name not in result,'unique regular member')
            data=tar.extractfile(item).read()
            need(not data.startswith((b'\x7fELF',b'!<arch>')) and b'S-130-' not in data,'no native product or license literal')
            need(desc(data)==expected.get(item.name),'exact archive member bytes');result[item.name]=data
    need(set(result)==set(expected),'closed archive inventory');return result

def restore_files(manifest):
    own=set(manifest['capsule_files'])|{'manifest.json'}
    need({str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}==own,'closed own inventory')
    for name,row in manifest['capsule_files'].items():safe(name);need(desc((HERE/name).read_bytes())==row,'own file identity')
    for name,row in manifest['parent_files'].items():safe(name);need(desc((ROOT/name).read_bytes())==row,'parent file identity')
    pm=load((ROOT/POWER/'manifest.json').read_bytes());wm=load((ROOT/WHEEL/'manifest.json').read_bytes())
    power=unpack((ROOT/POWER/'sources.tar.gz').read_bytes(),pm['source_members'])
    wheel=unpack((ROOT/WHEEL/'sources.tar.gz').read_bytes(),wm['sources']['members'])
    need(len(power)==145 and len(wheel)==147,'actual inherited source inventories')
    delta=unpack((HERE/'payload.tar.gz').read_bytes(),manifest['payload_members'])
    result={}
    for alias,row in manifest['aliases'].items():
        safe(alias)
        selectors=set(row)&{'power_source','wheel_source','member'}
        need(len(selectors)==1,'one exact byte selector')
        body=power[row['power_source']] if 'power_source' in row else wheel[row['wheel_source']] if 'wheel_source' in row else delta[row['member']]
        need(desc(body)=={key:row[key] for key in ['sha256','bytes']},'selected saved alias identity');result[alias]=body
    return result

def replay(manifest, files):
    def read(alias):return load(files[alias])
    def phase(name, buildname):
        base=PRIVATE+'/'+name;r=read(base+'/receipt.json')
        need(r['inputs_unchanged'] is True and not r['cleanup_errors'],'terminal source guards/cleanup '+name)
        need(0<r['elapsed_seconds']<=r['total_seconds'],'finite saved phase bound '+name)
        for absolute,digest in r['inputs'].items():
            if absolute in manifest['omitted_native_artifacts']:
                need(manifest['omitted_native_artifacts'][absolute]==digest,'explicit historical native hash');continue
            alias=absolute.removeprefix(PREFIX)
            if alias in r.get('source_files',{}):alias=base+'/source-snapshot/'+alias
            elif alias==SOURCE:alias=PRIVATE+'/'+buildname+'/source-snapshot/'+SOURCE
            need(alias in files and sha(files[alias])==digest,'exact selected guarded input '+name+'/'+alias)
        for rel,digest in r.get('outputs',{}).items():
            alias=base+'/'+rel
            if PREFIX+alias in manifest['omitted_native_artifacts']:
                need(manifest['omitted_native_artifacts'][PREFIX+alias]==digest,'omitted native output hash')
            else:need(alias in files and sha(files[alias])==digest,'exact saved output '+alias)
        for step in r['steps']:need(step['owned_group_gone'] is True,'owned process group gone')
        return r
    builds={n:phase(n,n) for n in ['build-001','build-002']}
    for name,built in builds.items():
        need(built['status']=='passed' and len(built['source_files'])==119,'actual passed selected119-source build')
        need(built.get('cancellation') is None and built.get('post_cancellation') is None,'uncancelled build')
        for alias,digest in built['source_files'].items():need(sha(files[PRIVATE+'/'+name+'/source-snapshot/'+alias])==digest,'actual compiled selected source body')
        for i,step in enumerate(built['steps']):
            need(step['status']=='exited' and step['returncode']==0,'successful actual Cargo child')
            events=[load(s) for s in files[PRIVATE+'/'+name+'/cargo-'+str(i)+'.log'].decode().splitlines() if s.startswith('{')]
            need([e['success'] for e in events if e.get('reason')=='build-finished']==[True],'successful Cargo terminal event')
        for label,product in built['products'].items():
            event=read(PRIVATE+'/'+name+'/'+product['cargo_event'])
            need(event['reason']=='compiler-artifact' and event['executable']==product['cargo_executable'],'selected actual Cargo product event')
            need(manifest['omitted_native_artifacts'][product['path']]==product['sha256'],'owned historical product hash')
    one,two=builds['build-001'],builds['build-002']
    need(len(one['steps'])==2 and len(two['steps'])==1,'core+CLI build and revised libtest-only build')
    differing=[p for p in set(one['source_files'])|set(two['source_files']) if one['source_files'].get(p)!=two['source_files'].get(p)]
    need(differing==[SOURCE],'only test-bearing stability source differs across builds')
    a=files[PRIVATE+'/build-001/source-snapshot/'+SOURCE];b=files[PRIVATE+'/build-002/source-snapshot/'+SOURCE]
    change=read(PRIVATE+'/change.json');before=files[PRIVATE+'/stability-before.rs']
    need(sha(before)==change['base_sha256'] and sha(a)==change['candidate_sha256'],'preserved original memo patch endpoints')
    bridge=read(PRIVATE+'/test-only-bridge.json')
    need(bridge['status']=='passed' and a.split(b'#[cfg(test)]')[0]==b.split(b'#[cfg(test)]')[0]
         and sha(a.split(b'#[cfg(test)]')[0])==bridge['sha256'],'preserved original narrow prefix attestation')
    marker=b'\n#[cfg(test)]\nmod tests {'
    need(a.count(marker)==b.count(marker)==1 and a.split(marker)[0]==b.split(marker)[0],'entire production module prefix identical, including memo code')
    production_hash=sha(a.split(marker)[0])
    addendum=read(PRIVATE+'/test-only-bridge-addendum.json')
    need(addendum['status']=='passed' and addendum['complete_production_prefix_identical'] is True
         and addendum['production_prefix_sha256']==production_hash and addendum['memo_function_in_prefix'] is True
         and b'master_amplitude_cached' in a.split(marker)[0],'root additive entire-production-prefix attestation')
    need(b'master_amplitude_cached(expression, amplitudes, &mut HashMap::new())' in a
         and b'memo.insert(expression.clone(), value.clone())' in a,'per-call immutable-environment Symbolica result memo source')
    initial=phase('tests-001','build-001');final=phase('tests-002','build-002')
    need(initial['status']=='failed' and len(initial['steps'])==2,'initial stress timeout retained')
    need(initial['steps'][0]['returncode']==0 and initial['steps'][1].get('timeout') is True
         and initial['steps'][1]['returncode']==-15,'one prior success then original40-deep timeout')
    need(b'conditional input and expected recipes constructed' not in files[PRIVATE+'/tests-001/1.log'],'initial timeout has no phase attribution')
    need(final['tests']==manifest['focused_test_names'],'six declared exact test identities')
    need(final['status']=='passed' and len(final['steps'])==len(final['tests'])==6 and len(set(final['tests']))==6,'six actual focused exact tests')
    for i,(name,step) in enumerate(zip(final['tests'],final['steps'])):
        text=files[PRIVATE+'/tests-002/'+str(i)+'.log'].decode()
        need(step['name']==name and step['returncode']==0 and step['status']=='exited','successful exact named child')
        need(step['command'][-4:]==[name,'--exact','--nocapture','--test-threads=1'],'exact owned test selector')
        need(re.findall(r'^running .*$',text,re.M)==['running 1 test'] and 'test '+name+' ... ' in text,'one actual selected test')
        need(len(re.findall(r'^test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; 436 filtered out; finished in [0-9.]+s$',text,re.M))==1,'strict one-pass saved terminal summary')
    stress=files[PRIVATE+'/tests-002/1.log']
    need(b'conditional input and expected recipes constructed' in stress
         and b'cached amplitude traversal completed: 21 unique expressions' in stress,'completed revised10-deep preparation and memo traversal witnesses')
    need(b'for index in 0..40 {' in a and b'for index in 0..10 {' in b,'stress reduction retained explicitly')
    need(one['products']['cli']['sha256']=='6f074ee17c665dce438c1c0c19c07d8bfab0e82f4a74b3c1bb7d89d284f4fbb9','actual memo CLI product')
    return dict(status='passed_saved_focused_memo_evidence_replay',actual_build_selected_source_bodies=119,
                inherited_power_context_sources=145,focused_tests_passed=6,focused_test_names=final['tests'],prior_classic_test_passed=1,
                preserved_initial_stress_timeout=True,initial_stress_depth=40,qualified_stress_depth=10,
                qualified_unique_amplitude_recipes=21,entire_production_module_prefix_sha256=production_hash,
                production_prefix_identical_between_actual_builds=True,
                actual_cli_sha256=one['products']['cli']['sha256'],
                full_dotted_numerical_pass_claimed=False,current_098_cli_equivalence_claimed=False,
                native_execution=False,new_integral_evaluation=False,performance_qualified=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output');args=p.parse_args()
    manifest=load((HERE/'manifest.json').read_bytes());result=replay(manifest,restore_files(manifest))
    if args.output:Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
