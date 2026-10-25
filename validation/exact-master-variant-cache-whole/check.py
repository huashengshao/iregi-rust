#!/usr/bin/env python3
"""Portable source and independent saved WHOLE38 replay; no native execution."""
from pathlib import Path
import argparse,hashlib,io,json,math,re,tarfile,types,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PRIVATE='target/exact-master-variant-cache-whole'
OLD='target/native-f64-sixpoint-port/whole'
CACHE='target/exact-master-variant-cache-proposal'
PARENT='validation/native-f64-sixpoint-whole'
CACHE_PARENT='validation/exact-master-variant-cache'
COMPOSITION='validation/winddown/native-f64-sixpoint-composition.tar.gz'
AUDIT='target/resume-20261025-review/cache-whole-independent-saved-audit'
SUPPLEMENT='target/resume-20261025-review/cache-whole-independent-closure-supplement.json'
HISTORICAL_ROOT='/shared/external/iregi/iregi-rust/'
def require(x,m):
    if not x:raise ValueError(m)
def digest(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'sha256':digest(b),'bytes':len(b)}
def safe(n):
    p=Path(n);require(bool(n)and not p.is_absolute()and'..'not in p.parts and str(p)==n,'unsafe path')
def archive(body,expected):
    result={}
    with tarfile.open(fileobj=io.BytesIO(body),mode='r:gz')as f:
        for item in f:
            safe(item.name);require(item.isfile()and item.name not in result,'non-file/duplicate member')
            b=f.extractfile(item).read();require(not b.startswith((b'\x7fELF',b'!<arch>')),'compiled member')
            require(not re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}',b),'license literal')
            result[item.name]=b
    require({n:desc(b)for n,b in result.items()}=={n:{k:v[k]for k in['sha256','bytes']}for n,v in expected.items()},'archive inventory')
    return result
def apply_source_patch(base, patch):
    """Strict mechanical unified-diff replay. No compiler, git, or algebra."""
    result = dict(base)
    lines = patch.decode().splitlines(keepends=True); index=0; changed=[]
    while index < len(lines):
        require(lines[index].startswith('--- '), 'unexpected patch record')
        old_name = lines[index][4:].rstrip('\n');index+=1
        require(index < len(lines) and lines[index].startswith('+++ '), 'missing patch destination')
        new_name = lines[index][4:].rstrip('\n');index+=1
        require(new_name.startswith('b/'), 'unsupported patch destination')
        name = new_name[2:];safe(name);require(name not in changed,'duplicate patch target');changed.append(name)
        require(old_name == 'a/'+name or old_name == '/dev/null','patch path pair')
        old = [] if old_name == '/dev/null' else result[name].decode().splitlines(keepends=True)
        require(old_name != '/dev/null' or name not in result,'new patch file already exists')
        new=[];cursor=0;hunks=0
        while index < len(lines) and lines[index].startswith('@@ '):
            match=re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*\n',lines[index]);index+=1
            require(match is not None,'bad hunk header')
            a, ac, b, bc = [int(x) if x is not None else 1 for x in match.groups()]
            start=max(0,a-1); require(cursor <= start <= len(old),'hunk overlap/range')
            new.extend(old[cursor:start]);cursor=start
            require(len(new) == max(0,b-1),'new hunk position')
            old_count=new_count=0
            while index < len(lines) and not lines[index].startswith(('@@ ','--- ')):
                line=lines[index];index+=1
                require(line[:1] in [' ','+','-'],'unsupported patch line')
                body=line[1:]
                if line[0] in ' -':
                    require(cursor < len(old) and old[cursor] == body,'patch context mismatch')
                    cursor+=1;old_count+=1
                if line[0] in ' +':new.append(body);new_count+=1
            require((old_count,new_count) == (ac,bc),'hunk line counts')
            hunks+=1
        require(hunks > 0,'patch has no hunks');new.extend(old[cursor:]);result[name]=''.join(new).encode()
    return result, changed


def replay(files,inputs):
    source=files[AUDIT+'.py'];expected=json.loads(files[AUDIT+'.json'])
    require(digest(source)=='b87120ee996dc189535dc5b8918a29838d172bfb7f6ccc001e9d88e6002ffc69','independent checker source')
    require(digest(files[AUDIT+'.json'])=='d9d687f590b8c7ea701bdb4981805e57ff4880b8e30e7a9171f0aa3dec66a51f','independent checker report')
    # Load only the preserved independent stdlib definitions, never its native
    # main or a producer validator. All calls below consume supplied saved data.
    a=types.ModuleType('preserved_independent_whole38');a.__file__=str(HERE/'preserved-independent-saved-audit.py')
    exec(compile(source,a.__file__,'exec'),a.__dict__)
    current=json.loads(files[PRIVATE+'/whole-qualification-001/results.json'])
    events=[json.loads(line)for line in files[PRIVATE+'/whole-qualification-001/responses.jsonl'].splitlines()]
    old_events=[json.loads(line)for line in files[OLD+'/whole-qualification-001/responses.jsonl'].splitlines()]
    previous={tuple(e['key']):e['response']['candidate']for e in old_events if e['event']=='response'and e['stage']=='initial'}
    prior_controls=[e['response']for e in old_events if e['event']=='response'and e['stage']=='controls']
    require(len(previous)==8 and len(prior_controls)==1,'old native85 inventory')
    cases=json.loads(inputs);schedule=[]
    def text(c,s):return json.dumps(dict(id=c['id'],n=c['n'],rank=c['rank'],algorithm='Hybrid',samples=s))+'\n'
    def fortran(c,s):
        mu=s[0]['mu'];require(all(x['mu']==mu for x in s),'common scale')
        lines=[f'BENCH {c["id"]} 2 {c["n"]} {c["rank"]} {mu:.17g} {len(s)} 0 1 1']
        for sample in s:
            for shift,mass in zip(sample['shifts'],sample['masses']):lines.append(' '.join(f'{x:.17g}'for x in shift)+f' ({mass[0]:.17g},{mass[1]:.17g})')
        return'\n'.join(lines)+'\n'
    for c in cases:
        for batch in[1,32]:
            key=[c['id'],batch];s=c['samples'][:batch];p=text(c,s)
            schedule.extend([('TIRust','initial',key,p),('TIRust','own-repeat',key,p),('IREGI','reference',key,fortran(c,s))])
    schedule.extend([('TIRust','controls',['controls',0],'CONTROLS\n'),('TIRust','controls-repeat',['controls',1],'CONTROLS\n')])
    for c in cases:
        for batch in[1,32]:schedule.append(('TIRust','retained',[c['id'],batch],text(c,c['samples'][:batch])))
    base=json.loads(text(cases[0],cases[0]['samples'][:1]))
    for f,v in[('engine','baseline'),('warmup',1),('repeats',1),('iterations',1)]:schedule.append(('TIRust','invalid-request',[f,v],json.dumps({**base,f:v})+'\n'))
    require(len(cases)==4 and len(schedule)==current['request_count']==38 and len(events)==76,'complete schedule')
    initial={};case_map={c['id']:c for c in cases};counts={s:dict(tensor_slots=0,master_slots=0,iregi_comparisons=0,iregi_maximum=0.)for s in a.POLICIES}
    stats=dict(represented_real_operands=0,failed_master_lanes=0)
    for serial,(engine,stage,key,payload)in enumerate(schedule,1):
        req,res=events[2*(serial-1):2*serial]
        for e,kind in[(req,'request'),(res,'response')]:
            require(e['serial']==serial and e['event']==kind and e['engine']==engine and e['stage']==stage and e['key']==key and e['payload']==payload,'raw event/order')
            require(set(e)=={'serial','event','engine','stage','key','payload'}|({'response'}if kind=='response'else set()),'raw event schema')
        value=res['response']
        if stage=='initial':
            c=case_map[key[0]];samples=c['samples'][:key[1]];initial[tuple(key)]=value
            for side in a.POLICIES:
                require(a.same(a.canon(value[side]),a.canon(previous[tuple(key)])),'historical native85 record')
                counts[side]['tensor_slots']+=a.represented_tensors(value[side],c,samples)
                counts[side]['master_slots']+=a.masters(value[side],c,key[1])
            require(a.same(a.canon(value['baseline']),a.canon(value['candidate'])),'native85/cache88 record')
            a.walk(value,stats)
        elif stage in['own-repeat','retained']:
            require(a.same(a.canon(value),a.canon(initial[tuple(key)])),'complete repeated record');a.walk(value,stats)
        elif stage=='reference':
            c=case_map[key[0]];samples=c['samples'][:key[1]];require(value['id']==key[0],'IREGI id')
            for side in a.POLICIES:
                n,error=a.tensors(initial[tuple(key)][side],value,c,samples)
                counts[side]['iregi_comparisons']+=n;counts[side]['iregi_maximum']=max(counts[side]['iregi_maximum'],error)
        elif stage=='controls':control_result=a.controls(value,prior_controls[0],stats);controls=value
        elif stage=='controls-repeat':require(a.same(value,controls),'control repeat');a.walk(value,stats)
        else:require(value=={'status':'invalid_request','error':'qualification is untimed; engine and timing counts are forbidden'},'four timing rejections')
    require(a.same(counts,expected['per_engine'])and a.same(control_result,expected['controls'])and a.same(stats,expected['metadata']),'independent replay result')
    for label,n in[('TIRust',30),('IREGI',8)]:
        raw=files[PRIVATE+'/whole-qualification-001/'+label+'.stdout.log'];require(raw.endswith(b'\n'),'incomplete stdout')
        emitted=[json.loads(line[7:])for line in raw.splitlines()if line.startswith(b'RESULT ')]
        captured=[e['response']for e in events if e['event']=='response'and e['engine']==label]
        require(len(emitted)==n and a.same(emitted,captured),'stdout RESULT count/order')
    return dict(requests=38,raw_entries=76,per_engine=counts,control_checks=control_result,metadata=stats)

def saved_gates(files,manifest):
    def load(n):return json.loads(files[PRIVATE+'/'+n])
    prep=load('preparation.json');plan=load('command-plan.json');build=load('observation-build-001/build.json');run=load('whole-qualification-001/results.json')
    old_build=json.loads(files[OLD+'/observation-build-001/build.json'])
    old_preparation=json.loads(files[OLD+'/preparation.json'])
    require(build['outputs']['baseline-core']==old_build['outputs']['candidate-core']
            and build['outputs']['baseline-masters']==old_build['outputs']['baseline-masters'], 'exact reused native85 core/legacy masters')
    require(prep['reused_candidate_masters']==old_preparation['reused_candidate_masters'],'selected master archive provenance')
    require(build['status']=='passed'and build['inputs_unchanged']is True and build['cleanup_errors']==[]and build['deadline_exceeded']is False,'build terminal')
    require(build['runtime_cap_seconds']==180 and build['cleanup_reserve_seconds']==25 and 0<=build['elapsed_seconds']<=180,'build budget')
    require(len(build['steps'])==len(plan['steps'])==2,'build products')
    groups=[]
    for step,expected in zip(build['steps'],plan['steps']):
        require(all(step[k]==expected[k]for k in expected),'compiled recipe')
        require(step['status']=='passed'and step['returncode']==0 and step['owned_group_gone']is True and 0<step['timeout_seconds']<=90,'build child terminal')
        groups.append(step['owned_process_group'])
    for path,expected in build['compiler_logs_sha256'].items():require(digest(files[path.removeprefix(HISTORICAL_ROOT)])==expected,'compiler log')
    require(run['status']=='passed-awaiting-independent-raw-validation'and run['inputs_unchanged']is True and not run['cleanup_errors']and run['deadline_exceeded']is False,'runtime terminal')
    require(run['runtime_cap_seconds']==120 and run['cleanup_postguard_reserve_seconds']==20 and 0<=run['elapsed_seconds']<=120,'runtime budget')
    for g,reserve in[(load('build-execution-grant-001.json'),25),(load('whole-runtime-grant-001.json'),20)]:
        require(g['status']=='granted'and g['grantor']=='/root'and g['postwork_reserve_seconds']==reserve,'grant status/authority/reserve')
        require(g['preparation_sha256']==digest(files[PRIVATE+'/preparation.json'])and g['independent_source_review_sha256']==digest(files[PRIVATE+'/independent-source-command-review.json']),'grant source admission')
    build_grant=load('build-execution-grant-001.json');runtime_grant=load('whole-runtime-grant-001.json')
    require(build_grant['aggregate_seconds']==180 and build_grant['command_plan_sha256']==digest(files[PRIVATE+'/command-plan.json'])
            and build_grant['runner_sha256']==digest(files[PRIVATE+'/build.py'])
            and build_grant['lifecycle_sha256']==digest(files[PRIVATE+'/lifecycle.py']),'build grant commands/budget')
    require(runtime_grant['runtime_cap_seconds']==120 and runtime_grant['build_receipt_sha256']==digest(files[PRIVATE+'/observation-build-001/build.json'])
            and runtime_grant['runner_sha256']==digest(files[PRIVATE+'/run_whole.py'])
            and runtime_grant['validator_sha256']==digest(files[PRIVATE+'/validate_whole.py'])
            and runtime_grant['interactive_sha256']==digest(files[PRIVATE+'/interactive.py'])
            and runtime_grant['lifecycle_sha256']==digest(files[PRIVATE+'/lifecycle.py']),'runtime grant commands/budget')
    review=load('independent-source-command-review.json')
    require(review['status']=='passed'and review['findings']==[]
            and review['preparation_sha256']==digest(files[PRIVATE+'/preparation.json'])
            and review['command_plan_sha256']==digest(files[PRIVATE+'/command-plan.json']),'source review admission')
    for n,h in review['subject_sha256'].items():require(digest(files[PRIVATE+'/'+n])==h,'source review subject')
    require(load('build-execution-grant-001.json')['compile_cpus']==[26,27]and load('whole-runtime-grant-001.json')['runtime_cpu']==22,'grant CPU')
    for first,last,label,count in zip(run['processes'],run['process_terminals'],['TIRust','IREGI'],[30,8]):
        require(first['label']==last['label']==label and first['owned_process_group']==last['owned_process_group'],'runtime owner')
        require(last['returncode']==0 and last['owned_group_gone']is True and last['received_responses']==count,'runtime terminal')
        groups.append(last['owned_process_group'])
        exe=run['executed_executables'][label]
        require(first['command']==[prep['tools']['taskset']['path'],'-c','22',exe['path']],'runtime command')
        require(exe['sha256']==(build['outputs']['selective-probe']['sha256']if label=='TIRust'else prep['reference']['sha256']),'saved executed digest chain')
    require(len(set(groups))==4,'four distinct owned groups')
    release=load('whole-qualification-001/numerical-release.json')
    require(release['owned_groups']==groups and release['all_owned_groups_absent']is True,'saved release attestations')
    omissions=manifest['omitted_private_files'];expected={}
    for step in build['steps']:expected[step['output'].removeprefix(HISTORICAL_ROOT)]=step['output_sha256']
    expected.update({e['path'].removeprefix(HISTORICAL_ROOT):e['sha256']for e in run['executed_executables'].values()})
    require({n:v['sha256']for n,v in omissions.items()if'sha256'in v}==expected and len(expected)==4 and len(omissions)==9,'omitted product digest chains')
    for field,ext in[('stderr_sha256','.stderr.log'),('stdout_sha256','.stdout.log')]:
        require(set(run[field])=={'TIRust','IREGI'},'stream inventory')
        for label,expected in run[field].items():require(digest(files[PRIVATE+'/whole-qualification-001/'+label+ext])==expected,'stream hash')
    require(digest(files[PRIVATE+'/whole-qualification-001/responses.jsonl'])==run['raw_sha256'],'raw digest')
    qualification=load('qualification.json')
    for n,h in qualification['artifacts'].items():require(digest(files[PRIVATE+'/'+n])==h,'qualification artifact')
    for field in['production_adoption','current_main_rebase_qualified','current_cargo_feature_graph_qualified','typed_dual_schedule_completed_by_this_gate','public_dual_qualified','derivative_uncertainty_transport_qualified','performance_qualified','automatic_retry_or_budget_extension']:require(qualification[field]is False,'scope promoted')
    require(qualification['baseline_n7less']is True,'N7less baseline scope')
    return dict(saved_owned_group_claims_checked=4,historical_process_identifiers_probed=False,compiled_products_rehashed=False,baseline_n7less=True,current_cargo_qualified=False,full_typed_dual_qualified=False,performance_qualified=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reconstruct',type=Path);args=parser.parse_args()
    manifest=json.loads((HERE/'manifest.json').read_text())
    actual={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
    require(actual==set(manifest['files'])|{'manifest.json'},'capsule membership')
    for n,item in manifest['files'].items():safe(n);require(desc((HERE/n).read_bytes())==item,'capsule hash')
    borrowed={}
    for n,item in manifest['borrowed_inputs'].items():safe(n);b=(ROOT/n).read_bytes();require(desc(b)==item,'borrowed hash');borrowed[n]=b
    winddown=json.loads(borrowed['validation/winddown/manifest.json'])
    composition=archive(borrowed[COMPOSITION],winddown['archives']['native-f64-sixpoint-composition']['members'])
    old_manifest=json.loads(borrowed[PARENT+'/manifest.json']);old=archive(borrowed[PARENT+'/evidence.tar.gz'],old_manifest['archive']['members'])
    old_parent=json.loads(borrowed[PARENT+'/parent.json'])
    for n,item in old_parent['inherited_source_files'].items():
        b=composition[item['parent_member']];require(desc(b)=={k:item[k]for k in['bytes','sha256']},'old source inheritance');old.setdefault(n,b)
    cache_manifest=json.loads(borrowed[CACHE_PARENT+'/manifest.json']);cache=archive(borrowed[CACHE_PARENT+'/payload.tar.gz'],cache_manifest['payload_archive']['members'])
    source=json.loads(cache[CACHE+'/source-proposal.json']);base={n:composition['proposed/'+n]for n in source['base_files']};candidate=dict(base)
    for n in source['changed_files']:candidate[n]=cache[CACHE+'/proposed/'+n]
    require({n:desc(b)for n,b in base.items()}==source['base_files']
            and {n:desc(b)for n,b in candidate.items()}==source['proposed_files'],'frozen parent base85/cache88 identities')
    payload=archive((HERE/'payload.tar.gz').read_bytes(),manifest['payload_archive']['members'])
    old_observed,_=apply_source_patch(base,payload['source-patches/baseline85-to-observed86.patch'])
    observed,_=apply_source_patch(candidate,payload['source-patches/cache88-to-observed89.patch'])
    snapshots={'base85':base,'cache88':candidate,'observed_baseline86':old_observed,'observed_cache89':observed}
    for role,fileset in snapshots.items():require({n:desc(b)for n,b in fileset.items()}==manifest['source_snapshots'][role],'source reconstruction '+role)
    require([len(x)for x in snapshots.values()]==[85,88,86,89],'exact snapshot counts')
    require(all(old['source/candidate/'+n]==b for n,b in old_observed.items()),'old observed86 reconstruction')
    files=dict(payload)
    for n,alias in manifest['source_aliases'].items():
        safe(n);safe(alias['member']);require(n not in files,'source alias duplicate')
        files[n]=({'observed':observed,'old_whole':old}[alias['kind']])[alias['member']]
    require({n:desc(b)for n,b in files.items()if n not in['source-patches/baseline85-to-observed86.patch','source-patches/cache88-to-observed89.patch']}==manifest['reconstructed_private_files'],'complete private reconstruction')
    files.update({OLD+'/'+n:b for n,b in old.items()});files.update(cache)
    files.update({CACHE+'/base/'+n:b for n,b in base.items()});files.update({CACHE+'/proposed/'+n:b for n,b in candidate.items()})
    available=historical=0
    for record in['preparation.json','observation-build-001/build.json','whole-qualification-001/results.json']:
        d=json.loads(files[PRIVATE+'/'+record]);mapping=d['input_sha256']
        for n,h in mapping.items():
            key=n.removeprefix(HISTORICAL_ROOT);body=files.get(key,borrowed.get(key))
            if body is None:historical+=1
            else:require(digest(body)==h,'available historical guard '+key);available+=1
    checked=saved_gates(files,manifest)
    values=replay(files,borrowed['validation/native-master-replay/inputs.json'])
    if args.reconstruct:
        dest=args.reconstruct.resolve();require(not dest.exists(),'reconstruction destination must be new');dest.mkdir(parents=True)
        for n,b in files.items():safe(n);p=dest/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    print(json.dumps(dict(status='passed',base_files=85,candidate_files=88,observed_baseline_files=86,observed_candidate_files=89,
        reconstructed_noncompiled_files=len(files),available_guard_occurrences_checked=available,
        historical_unbundled_guard_occurrences_not_rehashed=historical,**checked,**values,
        no_compiler_integral_reference_or_benchmark_executed=True,native_requalification=False,
        reconstruction_destination=str(args.reconstruct)if args.reconstruct else None),sort_keys=True))

if __name__=='__main__':main()
