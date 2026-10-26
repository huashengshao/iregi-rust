#!/usr/bin/env python3
"""Replay saved sources, Cargo events and15 libtests; stdlib, no native jobs."""
import argparse
from fractions import Fraction as F
import hashlib, io, json, re, tarfile
from pathlib import Path, PurePosixPath as P
import sys
sys.dont_write_bytecode = True

Q = 'target/n6-propagated-dual-budget-proposal'
PREFIX = '/shared/external/iregi/iregi-rust/'
PARENT = 'checked-g-generalized-core-tests'
PARENT_SHA = 'ee4bc172dd8b87e3242158afacab425e6b13376f72dd3fbb6678feb701a97417'
PATCH = '7782172f7a4a09a6e295c31fdd1089550e763eca2a8bd80d0df78aed67ff6bab'
BUILD = {'build-001':'3dc85417493c4643cb89a693b906332b1a778d9220e9143068d1fae9f624b599',
         'build-002':'90744bbd1bd5cbbee15fa150bec502f61011979968868ab992de98ae70854285',
         'build-003':'bee0be2fb260cd38983fa07293c084b55f362351dab33efda37be3b280d76653'}
TEST = {'tests-001':'d775718b7e73cc2722298ad0b4035ac6b0ef41ad74d07e4218038b698ecff6ab',
        'tests-003':'265b07d9e283200107db6fb1589fb43d6795123e3015acde0b6a3ac7bb9949c4'}
FIXTURE = 'crates/iregi-rust/src/execution/quadrature_context_tests.rs'
FINAL_FIXTURE = '48de67f950ec52f81a6e00a723089e09e2efdde5d5af541e0428c468cb2d179b'

def need(ok, message):
    if not ok: raise ValueError(message)

def sha(body): return hashlib.sha256(body).hexdigest()
def desc(body): return dict(sha256=sha(body),bytes=len(body))
def load(body):
    def pairs(items):
        out = {}
        for k,v in items:
            need(k not in out,'duplicate JSON key');out[k] = v
        return out
    return json.loads(body,object_pairs_hook=pairs,parse_float=str,
                      parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))

def safe(name):
    p = P(name)
    need(name and not p.is_absolute() and '..' not in p.parts and str(p) == name and name != '.', 'safe relative alias')

def scan(name, body):
    safe(name)
    need(P(name).suffix not in {'.so','.a','.o','.rlib','.dll','.dylib','.pyc','.mod','.smod'}
         and '__pycache__' not in P(name).parts,'no native payload/cache')
    need(not body.startswith((b'\x7fELF',b'!<arch>',b'MZ')),'no compiled payload')
    need(not re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}',body),'no license literal')

def selected_archive(body, inventory, wanted, closed):
    result = {};seen = set()
    with tarfile.open(fileobj=io.BytesIO(body),mode='r:gz') as archive:
        for entry in archive:
            need(entry.isfile() and entry.name not in seen and entry.name in inventory,'regular unique indexed archive member')
            seen.add(entry.name)
            if entry.name not in wanted: continue
            value = archive.extractfile(entry).read();scan(entry.name,value)
            need(desc(value) == inventory[entry.name],'selected archived source identity')
            result[entry.name] = value
    need(set(result) == wanted and (not closed or seen == set(inventory)),'complete selected archive inventory')
    return result

def restore(here):
    manifest = load((here/'manifest.json').read_bytes())
    need({p.name for p in here.iterdir()} == set(manifest['capsule_files'])|{'manifest.json'}
         and all(p.is_file() and not p.is_symlink() for p in here.iterdir()),'closed flat capsule inventory')
    for name,expected in manifest['capsule_files'].items():
        body=(here/name).read_bytes();scan(name,body);need(desc(body)==expected,'capsule file identity '+name)
    parent = here.parent/PARENT
    pb=(parent/'manifest.json').read_bytes();need(sha(pb)==PARENT_SHA,'fixed source-byte parent manifest')
    pm=load(pb);archive=(parent/'payload.tar.gz').read_bytes()
    need(desc(archive)==pm['capsule_files']['payload.tar.gz'],'fixed source-byte parent archive')
    need(manifest['parent_files']=={f'../{PARENT}/manifest.json':desc(pb),f'../{PARENT}/payload.tar.gz':desc(archive)},'only two explicit sibling parent files')
    wanted={row['member'] for row in manifest['preserved_files'].values() if row['store']=='parent'}
    inherited=selected_archive(archive,pm['payload_members'],wanted,False)
    local=selected_archive((here/'payload.tar.gz').read_bytes(),manifest['payload_members'],set(manifest['payload_members']),True)
    files={}
    for name,row in manifest['preserved_files'].items():
        safe(name);need(row['store'] in ['self','parent'],'explicit source store')
        value=(local if row['store']=='self' else inherited)[row['member']]
        need(desc(value)=={k:row[k] for k in ['sha256','bytes']},'preserved source/evidence alias '+name)
        files[name]=value
    need(set(inherited)==set(manifest['parent_used_members'])
         and all(pm['payload_members'][k]==v for k,v in manifest['parent_used_members'].items()),'exact inherited object descriptors')
    return files,manifest

def apply_unified(base, patch):
    """Exact text-hunk application for stored source diffs; never invokes git."""
    lines=patch.decode().splitlines(True);out={};i=0
    while i<len(lines):
        if not lines[i].startswith('--- '):i+=1;continue
        old=lines[i][4:].strip().split('\t')[0];i+=1
        need(i<len(lines) and lines[i].startswith('+++ '),'paired unified path')
        new=lines[i][4:].strip().split('\t')[0];i+=1
        old=None if old=='/dev/null' else old.removeprefix('a/')
        new=None if new=='/dev/null' else new.removeprefix('b/')
        need(new is not None,'no source deletions in this patch');safe(new)
        src=[] if old is None else base[old].decode().splitlines(True)
        dst=[];cursor=0
        while i<len(lines) and lines[i].startswith('@@ '):
            m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i]);need(m is not None,'valid text hunk')
            start=max(0,int(m[1])-1);need(cursor<=start<=len(src),'ordered bounded hunk');dst.extend(src[cursor:start]);cursor=start;i+=1
            removed=added=0
            while i<len(lines) and lines[i][:1] in [' ','+','-'] and not lines[i].startswith(('--- ','+++ ')):
                kind=lines[i][0];body=lines[i][1:]
                if kind in [' ','-']:need(cursor<len(src) and src[cursor]==body,'exact historical hunk context');cursor+=1;removed+=1
                if kind in [' ','+']:dst.append(body);added+=1
                i+=1
            need(removed==int(m[2] or 1) and added==int(m[4] or 1),'exact hunk line counts')
        dst.extend(src[cursor:]);need(new not in out,'one diff per path');out[new]=''.join(dst).encode()
    need(out,'nonempty source patch');return out

def replay(files, manifest):
    read=lambda name:load(files[Q+'/'+name])
    builds={name:read(name+'/receipt.json') for name in BUILD}
    versions=set();products={};cargo_errors=[];owned_groups=set();version_stores={}
    for name,b in builds.items():
        need(sha(files[Q+'/'+name+'/receipt.json'])==BUILD[name],'pinned historical build receipt')
        need(b['inputs_unchanged'] is True and b['cleanup_errors']==[] and b['cancellation'] is None and b['post_cancellation'] is None,'build postguards and owned cleanup')
        need(b['status']==('failed' if name=='build-002' else 'passed') and len(b['source_files'])==132,'actual build outcome and source inventory')
        need((b['total_seconds'],b['cleanup_reserve_seconds'],b['child_cap_seconds'])==(900,60,780)
             and F(b['elapsed_seconds'])<=900 and len(b['steps'])==1,'finite Cargo bounds')
        step=b['steps'][0];need(step['owned_group_gone'] is True and step['returncode']==(101 if name=='build-002' else 0)
             and step['status']==('failed' if name=='build-002' else 'exited') and F(step['elapsed_seconds'])<=F(step['timeout_seconds'])<=780,'actual owned Cargo terminal')
        owned_groups.add(step['owned_process_group'])
        need(step['command'][:3]==['taskset','-c','18,19'] and step['command'][4:]==['test','--locked','--offline','-p','iregi-rust','--lib','--no-run','--message-format=json','-j2']
             and b['planned_commands']==[step['command']],'exact recorded Cargo command')
        events=[load(line) for line in files[Q+'/'+name+'/cargo-0.log'].splitlines() if line.startswith(b'{')]
        need([e['success'] for e in events if e.get('reason')=='build-finished']==[name!='build-002'],'actual Cargo completion event')
        current_errors=[e['message']['code']['code'] for e in events if e.get('reason')=='compiler-message' and e['message']['level']=='error']
        need(current_errors==(['E0596'] if name=='build-002' else []),'preserved Arc compile failure and successful builds');cargo_errors+=current_errors
        prefix=Q+'/'+name+'/source-snapshot/'
        need(manifest['source_contexts'][name]['source_files']==b['source_files'],'exact source-context receipt map')
        for path,digest in b['source_files'].items():
            need(sha(files[prefix+path])==digest and b['inputs'][PREFIX+path]==digest,'every captured declared compiled source body');versions.add((path,digest))
            store=manifest['preserved_files'][prefix+path]['store'];key=(path,digest)
            need(key not in version_stores or version_stores[key]==store,'consistent inherited source store');version_stores[key]=store
        for product in b['products'].values():
            artifact=load(files[Q+'/'+name+'/'+product['cargo_event']])
            need(artifact in events and artifact['reason']=='compiler-artifact' and artifact['target']['name']=='iregi_rust'
                 and artifact['target']['src_path']==PREFIX+'crates/iregi-rust/src/lib.rs' and artifact['target']['kind']==['lib']
                 and artifact['profile']['test'] is True and artifact['profile']['opt_level']=='0'
                 and artifact['features']==['default'] and artifact['executable']==product['cargo_executable'],'actual selected library test artifact')
            products[product['path'].removeprefix(PREFIX)]=product['sha256']
        for output,digest in b['outputs'].items():
            path=Q+'/'+name+'/'+output
            need((products.get(path)==digest) if path in manifest['omitted_compiled_products'] else sha(files[path])==digest,'build raw log/artifact or omitted product identity')
        for path,digest in b['inputs'].items():
            alias=path.removeprefix(PREFIX)
            if alias in b['source_files']:continue
            need(alias!=path and (products.get(alias)==digest if alias in products else sha(files[alias])==digest),'build controller/protocol/source-review binding')
    final=builds['build-003']['source_files'];need(len(versions)==134 and len(final)==132,'132 paths and134 distinct source versions')
    need(sum(store=='parent' for store in version_stores.values())==119
         and sum(store=='self' for store in version_stores.values())==15,'exact inherited and newly archived source versions')
    for name,b in builds.items():
        need(set(b['source_files'])==set(final) and [p for p in final if final[p]!=b['source_files'][p]]==([] if name=='build-003' else [FIXTURE]),'only the fallback test source changes across builds')
    need(manifest['omitted_compiled_products']==products and final[FIXTURE]==FINAL_FIXTURE,'exact omitted product metadata/final test source')
    original=read('source-delta.json');need(original['patch_sha256']==PATCH and sha(files[Q+'/candidate.patch'])==PATCH,'unchanged reviewed production/source patch')
    bases={p:files[Q+'/base/'+p] for p,r in original['subjects'].items() if r['base_sha256'] is not None}
    applied=apply_unified(bases,files[Q+'/candidate.patch']);need(set(applied)==set(original['subjects']) and len(applied)==11,'exact11-file reviewed patch')
    for path,body in applied.items():
        need(sha(body)==original['subjects'][path]['candidate_sha256'] and body==files[Q+'/candidate/'+path],'reviewed candidate from historical source hunks')
        if path!=FIXTURE:need(final[path]==sha(body),'production sources unchanged through final build')
    first=read('narrow-fallback-fixture-fix/change.json');second=read('narrow-fallback-fixture-fix/arc-ownership-change.json')
    need(sha(files[Q+'/narrow-fallback-fixture-fix/change.json'])=='86ba6f5649d004b0bb8b864c22a1372093ad04434ab099931f88a3615f16cc73'
         and sha(files[Q+'/narrow-fallback-fixture-fix/arc-ownership-change.json'])=='4f6fb4ecbd495db290923190976f194268d4ad15271908166618249445146a60','exact narrow cfgtest amendment records')
    interim=apply_unified({FIXTURE:applied[FIXTURE]},files[Q+'/narrow-fallback-fixture-fix/candidate.patch'])[FIXTURE]
    repaired=apply_unified({FIXTURE:interim},files[Q+'/narrow-fallback-fixture-fix/arc-ownership-fix.patch'])[FIXTURE]
    need(sha(applied[FIXTURE])==first['before_sha256'] and sha(interim)==first['after_sha256']==second['before_sha256']
         and sha(repaired)==second['after_sha256']==FINAL_FIXTURE,'test-only fixture analytic-order and Arc repairs replay exactly')
    need(first['production_math_or_guards_changed'] is False and first['git_index_unchanged'] is True
         and second['production_changed'] is False and second['index_unchanged'] is True,'recorded test-only/worktree-index delta boundary')
    application=read('application.json');release=read('execution-release.json');review=read('independent-source-review-v1.json')
    need(application['patch_sha256']==release['source_patch_sha256']==review['patch_sha256']==PATCH
         and application['selected_git_index_unchanged'] is True and application['git_add_or_commit_executed'] is False
         and sha(files[Q+'/independent-source-review-v1.json'])==application['source_review_sha256']
         and sha(files[Q+'/execution-release.json'])==application['root_release_sha256']
         and release['grantor']=='/root' and release['status']=='released_by_root_after_checkpoint'
         and review['status']=='passed' and review['findings']==[],'saved review/release/applied worktree and index provenance')
    selection=read('test-selection.json')['exact_tests'];need(len(selection)==len(set(selection))==15,'15 distinct exact tests')
    history=[]
    for name,expected in TEST.items():
        r=read(name+'/receipt.json');need(sha(files[Q+'/'+name+'/receipt.json'])==expected,'pinned test receipt')
        good=name=='tests-003';executed=15 if good else 7;build_name='build-003' if good else 'build-001';b=builds[build_name];product=b['products']['library-tests']
        need(r['status']==('passed' if good else 'failed') and r['inputs_unchanged'] is True and r['cleanup_errors']==[]
             and r['cancellation'] is None and r['post_cancellation'] is None and r['passed_tests']==selection[:15 if good else 6]
             and r['exact_tests']==selection and len(r['steps'])==executed+1,'actual complete/early-stop strict test cohorts')
        need((r['total_seconds'],r['cleanup_reserve_seconds'],r['test_cap_seconds'],r['cpu'])==(300,30,90,28)
             and F(r['elapsed_seconds'])<=300,'finite test cohort')
        listing=files[Q+'/'+name+'/listing.log'].decode().splitlines()
        for test in selection:need(listing.count(test+': test')==1,'strict listing contains requested test exactly once')
        listing_step=r['steps'][0]
        need(listing_step['command']==['taskset','-c','28',product['path'],'--list','--format=terse']
             and listing_step['status']=='exited' and listing_step['returncode']==0,'actual test inventory command')
        for i,step in enumerate(r['steps']):
            need(step['owned_group_gone'] is True and F(step['elapsed_seconds'])<=F(step['timeout_seconds'])<=90,'historical finite absent test process group')
            owned_groups.add(step['owned_process_group'])
            if i==0:continue
            test=selection[i-1];passed=good or i<=6;log=files[Q+'/'+name+f'/test-{i-1:02}.log'].decode()
            need(step['command']==['taskset','-c','28',product['path'],'--exact',test,'--nocapture','--test-threads=1'],'exact actual test command')
            need(step['status']==('exited' if passed else 'failed') and step['returncode']==(0 if passed else 101),'actual test terminal state')
            need(re.search(r'^running 1 test$',log,re.M) and re.search(r'^test result: '+('ok' if passed else 'FAILED')+r'\. '+('1 passed; 0 failed' if passed else '0 passed; 1 failed')+r'; 0 ignored; 0 measured;',log,re.M),'exactly one actual nonignored Rust test')
            need(re.search(r'^test '+re.escape(test)+r' \.\.\.'+(' ok' if passed else ''),log,re.M),'requested named Rust test, not a zero-test success')
            if not passed:need('left: [false]' in log and 'right: [true]' in log,'preserved actual fallback fixture failure')
        for output,digest in r['outputs'].items():need(sha(files[Q+'/'+name+'/'+output])==digest,'all raw test logs bound')
        for path,digest in r['inputs'].items():
            alias=path.removeprefix(PREFIX)
            need(alias!=path and (products.get(alias)==digest if alias in products else sha(files[alias])==digest),'test frozen binary/source/runner provenance')
        history.append(dict(cohort=name,passed=15 if good else 6,failed=0 if good else 1,unattempted=0 if good else 8))
    functional=read('functional-qualification.json')
    need(sha(files[Q+'/functional-qualification.json'])=='94aaa1d6555cc4016e3a4741491cb2d0b49695e72840e86faedca478ef050268'
         and functional['build_receipt']['sha256']==BUILD['build-003']
         and functional['tests_receipt']['sha256']==TEST['tests-003']
         and functional['actual_test_count']==15 and functional['production_patch_sha256']==PATCH
         and functional['final_test_source_sha256']==FINAL_FIXTURE,'exact terminal functional qualification')
    absent=functional['owned_groups_absent']
    need(len(owned_groups)==len(absent)==27 and {row['group'] for row in absent}==owned_groups
         and all(row['absent'] is True for row in absent),'all27 historical owned groups independently recorded absent')
    need(functional['source_and_Cargo_released'] is True and functional['performance_claim'] is False
         and functional['reference_finite_coefficients_independently_certified'] is False
         and functional['D6_Dual_native_status'].startswith('HOLD '),'terminal release and unresolved D6 reference boundary')
    return dict(status='passed_saved_propagated_dual_joint_budget_core_tests',passed=True,qualified_distinct_test_count=15,
                source_contexts=3,compiled_source_paths=132,distinct_source_versions=134,
                inherited_source_versions=119,new_source_versions=15,build_outcomes=['passed','failed_E0596','passed'],
                test_history=history,production_patch_sha256=PATCH,final_build_receipt_sha256=BUILD['build-003'],final_tests_receipt_sha256=TEST['tests-003'],
                final_product_sha256=products[Q+'/build-003/frozen-propagated-dual-budget-tests'],
                no_native_products_or_license_payload=True,native_products_rehashed=False,new_process_probes=False,
                historical_owned_process_groups_recorded_absent=27,
                public_Dual_numerically_qualified=False,propagated_Dual_integrals_qualified=False,
                D6_native_hold=True,performance_qualified=False,achieved_precision_qualified=False,
                complete_dependency_closure_claimed=False,
                limits=['Software source/Cargo/libtest evidence only.15 targeted tests do not establish full-Dual propagated-quadrature integral accuracy or convergence.',
                        'D6 native cohort remains on hold pending an unresolved ordinary finite-reference discrepancy; no native D6 or benchmark/report work is admitted here.',
                        'Source snapshots and process/ELF identities are historical receipt evidence. Only declared source bytes are restored; binaries, license literals and a hermetic dependency closure are absent.',
                        'Unchanged bytes come from the exact sibling checked-G parent archive; parent120-test provenance is not replayed or added to this capsule test count.'])

def verify(here):
    files,manifest=restore(here)
    result=replay(files,manifest)
    need(result==load((here/'qualification.json').read_bytes()),'deterministic qualification replay')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--capsule',type=Path,default=Path(__file__).resolve().parent);a=p.parse_args()
    result=verify(a.capsule.resolve());print(json.dumps(result,indent=2))

if __name__=='__main__':main()
