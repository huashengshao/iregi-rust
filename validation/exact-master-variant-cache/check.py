#!/usr/bin/env python3
"""Portable source and saved-evidence audit; never build or evaluate an integral."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import math
import re
import tarfile
import sys
sys.dont_write_bytecode = True

from saved_numeric import check_saved

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = 'target/exact-master-variant-cache-proposal'
FAILED = 'target/public-highpoint/numeric-types-dual-shared-cache'
TYPED = FAILED + '-link-closure'
OLD = 'target/public-highpoint/numeric-types-dual'
OLD_CAPSULE = 'validation/highpoint-six-point-numeric-types'
HISTORICAL_ROOT = '/shared/external/iregi/iregi-rust/'


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def descriptor(data):
    return {'sha256':digest(data),'bytes':len(data)}


def read(path):
    return json.loads(Path(path).read_text())


def safe(name):
    p = Path(name)
    require(bool(name) and not p.is_absolute() and '..' not in p.parts and str(p) == name, 'unsafe path '+name)


def allowed(name, body):
    safe(name)
    require(not body.startswith((b'\x7fELF',b'!<arch>')), 'compiled archive member '+name)
    require(not re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}',body), 'license literal')


def archive(body, expected):
    result = {}
    with tarfile.open(fileobj=io.BytesIO(body), mode='r:gz') as stream:
        for item in stream:
            require(item.isfile() and item.name not in result, 'invalid archive member')
            data = stream.extractfile(item).read();allowed(item.name,data);result[item.name]=data
    require({n:descriptor(b) for n,b in result.items()} == expected, 'archive inventory mismatch')
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


def stage(record, count, bound, reserve, successful, groups):
    require(record['status'] == ('passed' if successful else 'failed')
            and record['inputs_unchanged'] is True and record['cleanup_errors'] == [],'stage status/guard/cleanup')
    require(record['bound_seconds'] == bound and record['postwork_reserve_seconds'] == reserve,'stage budget')
    require(type(record['elapsed_seconds']) in [int,float] and math.isfinite(record['elapsed_seconds'])
            and 0 <= record['elapsed_seconds'] <= bound,'elapsed bound')
    require(len(record['steps']) == count,'stage process inventory')
    for step in record['steps']:
        group=step['owned_process_group']
        require(type(group) is int and group > 0 and group not in groups and step['owned_group_gone'] is True,'saved owned group')
        require(0 < step['timeout_seconds'] <= bound-reserve,'finite work budget')
        groups.append(group)
        if successful:
            require(step['status'] == 'exited' and step['returncode'] == 0
                    and not any(step.get(k) for k in ['error','timeout','cancellation']),'successful child failed')


def check_gates(files):
    def load(name):return json.loads(files[name])
    p=load(CACHE+'/qualification-protocol.json'); b=load(CACHE+'/build-001/build.json');t=load(CACHE+'/tests-001/tests.json')
    groups=[];stage(b,2,180,20,True,groups);stage(t,19,300,20,True,groups)
    require(b['commands'] == p['build_commands'] and t['commands'] == p['test_commands'],'frozen build/test commands')
    for step,command in zip(b['steps'],p['build_commands']):
        require([step['name'],step['command']] == command,'executed build command')
        require(digest(files[CACHE+'/build-001/'+step['name']+'.log']) == step['log_sha256'],'build log digest')
    selected=p['selected_tests'];require(len(selected) == len(set(selected)) == 18,'18 distinct tests')
    listing=files[CACHE+'/tests-001/list.log'].decode()
    listed=[line.removesuffix(': test') for line in listing.splitlines() if line.endswith(': test')]
    require(all(listed.count(name) == 1 for name in selected),'selected name missing/duplicated in listing')
    for i,step in enumerate(t['steps']):
        require([step['name'],step['command']] == p['test_commands'][i]
                and step['selected_test_gate_passed'] is True,'executed test command/gate')
        logfile='list.log' if i == 0 else f'test-{i:02}.log'
        body=files[CACHE+'/tests-001/'+logfile];require(digest(body) == step['log_sha256'],'test log digest')
        if i:
            name=selected[i-1];command=step['command']
            require(command[-4:] == ['--exact',name,'--nocapture','--test-threads=1'],'exact test argv')
            text=body.decode()
            require(text.count('test '+name+' ...') == 1 and text.count('running 1 test\n') == 1
                    and (text.count('test '+name+' ... ok') == 1 or len(re.findall(r'^ok$',text,re.MULTILINE)) == 1),
                    'one selected passing test, allowing caught-panic diagnostics')
            summaries=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured;',text)
            require(summaries == [('ok','1','0','0','0')],'exact test summary')
    expected=b['outputs']['cache-tests']
    require(t['executed_binary_sha256'] == t['outputs']['frozen-cache-tests'] == expected,'saved selected binary hash chain')
    q=load(CACHE+'/qualification.json');require(q['build_qualified'] is True and q['private_exact_tests_qualified'] is True
        and q['exact_tests_passed'] == 18 and q['full_cargo_suite_qualified'] is False
        and q['build_products'] == b['outputs'] and q['all_owned_process_groups_absent'] is True
        and q['owned_process_groups'] == groups,'test qualification scope/hash chain')
    review=json.loads(files[CACHE+'/independent-qualification-review.json'])
    require(review['findings'] == [] and [x['owned_process_group'] for x in review['owned_process_group_checks']] == groups
            and all(x['currently_absent'] is True for x in review['owned_process_group_checks']),
            'saved independent21 group attestations')
    for name in ['full_cargo_suite_qualified','numerical_typed_pilot_qualified',
                 'cold_symbolica_construction_on_worker_threads_qualified','public_dual_qualified',
                 'derivative_uncertainty_transport_qualified','performance_qualified','production_adoption']:
        require(q[name] is False,'cache scope promoted: '+name)
    for name,expected in q['artifacts'].items():require(digest(files[CACHE+'/'+name]) == expected,'cache qualification artifact')
    oldb=load(FAILED+'/build-001/build.json');stage(oldb,2,90,25,False,groups)
    require(oldb['steps'][0]['returncode'] == 0 and oldb['steps'][1]['returncode'] != 0,'retained link failure')
    require('E0460' in files[FAILED+'/build-001/driver.log'].decode(),'retained exact link error')
    require(all(v['status'] == 'not_attempted_build_prerequisite_failed' and v['numeric_result_available'] is False
                for v in load(FAILED+'/qualification.json')['domains'].values()),'failed link ran numeric domain')
    p2=load(TYPED+'/protocol.json');b2=load(TYPED+'/build-001/build.json');stage(b2,1,90,25,True,groups)
    require(set(b2['outputs']) == {'typed_n6'},'driver-only output inventory')
    deps=HISTORICAL_ROOT+'target/e6-direct-n2/deps'
    supplemental=HISTORICAL_ROOT+'target/core-fused-cse-census/supplemental-deps'
    native=HISTORICAL_ROOT+'target/e6-direct-n2/native'
    selective=HISTORICAL_ROOT+'target/native-f64-opt-in/qualification/observation-build-001/selective'
    expected_command=[p2['taskset_path'],'-c','14,15',p2['compiler_path'],'--edition=2024',
        '-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo','-C','linker='+p2['linker_path'],
        '-L','dependency='+deps,'-L','dependency='+supplemental,'-L','native='+native,
        '-L','dependency='+selective,'--cfg','feature=\"default\"','--cfg','feature=\"native-f64-abc\"',
        '--crate-name','typed_n6',HISTORICAL_ROOT+TYPED+'/source/main.rs',
        '--extern','candidate='+HISTORICAL_ROOT+FAILED+'/build-001/libcandidate.rlib',
        '--extern','iregi_masters='+selective+'/libiregi_masters.rlib',
        '-o',HISTORICAL_ROOT+TYPED+'/build-001/typed_n6']
    require(b2['steps'][0]['command'] == expected_command,'exact corrected driver command')
    require(b2['steps'][0]['manifest_dir'] == HISTORICAL_ROOT+FAILED+'/core/crates/iregi-rust','driver source manifest')
    require(b2['outputs']['typed_n6'] == 'a284dc379535fd4ed9634becd59796a5083e1a4748592825b8df436eacc728cd','saved driver digest')
    command=b2['steps'][0]['command'];core=HISTORICAL_ROOT+FAILED+'/build-001/libcandidate.rlib'
    require('candidate='+core in command and '--crate-type' not in command,'reused core driver-only')
    require(oldb['outputs']['libcandidate.rlib'] == '405cbb2b6a09989b7355f167d6463606ea3532f59cc0266bf233df3504ffcc99','saved reused core digest')
    for domain in ['f64','DoubleFloat','Float128Dual','Float256Dual']:
        run=load(TYPED+'/run-'+domain+'-001/run.json');stage(run,1,180,20,domain in ['f64','DoubleFloat'],groups)
        require(run['executed_binary_sha256'] == run['outputs']['frozen-typed_n6'] == b2['outputs']['typed_n6'],'saved run binary chain')
        require(run['operation'] == domain,'domain operation')
        require(run['steps'][0]['command'] == [p2['taskset_path'],'-c','14',
                HISTORICAL_ROOT+TYPED+'/run-'+domain+'-001/frozen-typed_n6',domain,
                'validation/public-highpoint/fixture-conditioned_masses.json',
                HISTORICAL_ROOT+TYPED+'/run-'+domain+'-001/result.json'],'exact capture command')
        for name,expected in run['outputs'].items():
            if name != 'frozen-typed_n6':require(digest(files[TYPED+'/run-'+domain+'-001/'+name]) == expected,'capture output hash')
        g=load(TYPED+'/grant-'+domain+'.json')
        require(g['status'] == 'granted' and g['grantor'] == '/root' and g['operation'] == domain and g['protocol_sha256'] == digest(files[TYPED+'/protocol.json'])
                and g['bound_seconds'] == 180 and g['postwork_reserve_seconds'] == 20
                and g['cpu_affinity'] == [14] and g['previous_numerical_lease_released'] is True,'domain finite grant')
    grant=load(TYPED+'/grant-build.json')
    require(grant['status'] == 'granted' and grant['grantor'] == '/root' and grant['operation'] == 'build'
            and grant['protocol_sha256'] == digest(files[TYPED+'/protocol.json'])
            and grant['bound_seconds'] == 90 and grant['postwork_reserve_seconds'] == 25
            and grant['cpu_affinity'] == [14,15], 'driver build finite grant')
    require(grant['root_engineering_continuation_authorization_sha256'] == digest(files[TYPED+'/root-engineering-continuation-authorization.json']),
            'driver build root authorization binding')
    release=load(TYPED+'/numerical-release.json')
    require(release['owned_groups'] == groups[21:] and release['all_owned_groups_absent'] is True
        and release['scalar_master_or_numeric_retries'] is False and release['new_source_or_budget_extensions'] is False,'saved numerical release')
    q2=load(TYPED+'/qualification.json')
    for name,expected in q2['artifacts'].items():require(digest(files[TYPED+'/'+name]) == expected,'typed qualification artifact')
    for name in ['public_dual_qualified','derivative_uncertainty_transport_qualified','performance_qualified','full_cargo_suite_qualified',
                 'complete_precision_convergence_qualified','all_four_numeric_domains_qualified','automatic_numeric_retry_performed','runtime_budget_or_tolerance_extended']:
        require(q2[name] is False,'typed scope promoted: '+name)
    return dict(selected_tests_checked=18,saved_owned_groups_checked=len(groups),
                historical_process_absence_attestations_checked=True,historical_process_identifiers_probed=False,
                source_test_executable_hash_chain_checked=True,compiled_products_rehashed=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reconstruct',type=Path,help='write exact noncompiled source/evidence trees to a new directory')
    args=parser.parse_args();manifest=read(HERE/'manifest.json')
    actual={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    require(actual == set(manifest['files'])|{'manifest.json'},'capsule inventory mismatch')
    for name,item in manifest['files'].items():
        safe(name);require(descriptor((HERE/name).read_bytes()) == item,'capsule file changed '+name)
    borrowed={}
    for name,item in manifest['borrowed_inputs'].items():
        safe(name);body=(ROOT/name).read_bytes();require(descriptor(body) == item,'borrowed input changed '+name);borrowed[name]=body
    winddown=json.loads(borrowed['validation/winddown/manifest.json'])
    parent_name=manifest['composition_parent']['path']
    composition=archive(borrowed[parent_name],winddown['archives']['native-f64-sixpoint-composition']['members'])
    payload=archive((HERE/'payload.tar.gz').read_bytes(),manifest['payload_archive']['members'])
    source=json.loads(payload[CACHE+'/source-proposal.json'])
    base={name:composition['proposed/'+name] for name in source['base_files']}
    require({n:descriptor(b) for n,b in base.items()} == source['base_files'] and len(base) == 85,'base85 reconstruction')
    candidate=dict(base)
    for name in source['changed_files']:candidate[name]=payload[CACHE+'/proposed/'+name]
    require({n:descriptor(b) for n,b in candidate.items()} == source['proposed_files'] and len(candidate) == 88,'candidate88 reconstruction')
    patched,changed=apply_source_patch(base,payload[CACHE+'/proposal.patch'])
    require(patched == candidate and changed == source['changed_files'],'patch exact reconstruction')
    files=dict(payload)
    for name,alias in manifest['source_aliases'].items():
        safe(name);kind,member=alias['kind'],alias['member'];safe(member)
        body={'composition':composition,'candidate':candidate,'payload':payload,'repository':borrowed}[kind][member]
        require(name not in files,'source alias duplicate');files[name]=body
    require({n:descriptor(b) for n,b in files.items()} == manifest['reconstructed_private_files'],'full source/evidence reconstruction')
    build_source={n[len(CACHE+'/build-source/'):]:b for n,b in files.items() if n.startswith(CACHE+'/build-source/')}
    compile_fixtures={'validation/reference/fixtures.json',
                      'validation/pv-high-rank/lightlike-feynman-parameters.json',
                      'validation/reference/snapping/reductions.json'}
    require(set(build_source) == set(candidate)|compile_fixtures and len(build_source) == 91,'isolated build91 inventory')
    require(all(build_source[name] == body for name,body in candidate.items()),'isolated build candidate bytes')
    typed=json.loads(files[FAILED+'/source.json']);core={n[len(FAILED+'/core/'):]:digest(b) for n,b in files.items() if n.startswith(FAILED+'/core/')}
    require(core == typed['candidate_files'] and len(core) == 90,'typed90 reconstruction')
    declaration=typed['full_byte_restoration']['removed_only'].encode()
    for name,expected in typed['full_byte_restoration']['restored_original_files'].items():
        body=files[FAILED+'/core/'+name]
        if name == 'crates/iregi-rust/src/lib.rs':
            require(body.endswith(declaration),'capture declaration is not append-only');body=body[:-len(declaration)]
        require(digest(body) == expected == source['proposed_files'][name]['sha256'],'restore candidate88 from typed90')
    require(len(typed['full_byte_restoration']['restored_original_files']) == 88,'restoration inventory')
    # Original typed evidence is already committed as an exact parent+delta capsule.
    old_manifest=json.loads(borrowed[OLD_CAPSULE+'/manifest.json'])
    old_parent=old_manifest['parent_archive'];old_delta=old_manifest['delta_archive']
    original=archive(borrowed[old_parent['path']],old_parent['members'])
    original.update(archive(borrowed[OLD_CAPSULE+'/'+old_delta['path']],old_delta['members']))
    require({n:descriptor(b) for n,b in original.items()} == old_manifest['reconstructed_private_tree'],'original typed capsule mismatch')
    files.update({OLD+'/'+n:b for n,b in original.items()})
    for name in ['source/capture.rs','source/jet_inputs.rs','source/main.rs']:
        require(files[FAILED+'/'+name] == files[TYPED+'/'+name] == files[OLD+'/'+name],
                'original capture/numeric helper changed')
    # All present guard bytes must match. Missing native tools/dependencies are
    # counted as historical-only evidence, never silently rehashed or qualified.
    available_guards=historical_guards=0
    records=[CACHE+'/qualification-protocol.json',CACHE+'/build-001/build.json',CACHE+'/tests-001/tests.json',
             FAILED+'/protocol.json',FAILED+'/build-001/build.json',TYPED+'/protocol.json',TYPED+'/build-001/build.json']
    records += [TYPED+'/run-'+domain+'-001/run.json' for domain in ['f64','DoubleFloat','Float128Dual','Float256Dual']]
    for record in records:
        data=json.loads(files[record])
        for name,expected in data['inputs'].items():
            key=name.removeprefix(HISTORICAL_ROOT)
            body=files.get(key,borrowed.get(key))
            if body is None:historical_guards+=1
            else:require(digest(body) == expected,'reconstructed guarded source mismatch '+name);available_guards+=1
    for prefix,receipt in [(CACHE,'qualification-runner-review.json'),
                           (FAILED,'runner-comparator-source-review.json'),
                           (TYPED,'runner-comparator-source-review.json')]:
        review=json.loads(files[prefix+'/'+receipt])
        require(review['status'] == 'passed' and review['findings'] == [],'runner review admission')
        for name,expected in review['subject_sha256'].items():
            require(digest(files[prefix+'/'+name]) == expected,'reviewed runner source changed')
        draft_key='draft_sha256' if prefix == CACHE else 'protocol_draft_sha256'
        draft='qualification-draft.json' if prefix == CACHE else 'protocol-draft.json'
        require(digest(files[prefix+'/'+draft]) == review[draft_key],'reviewed draft changed')
    source_review=json.loads(files[CACHE+'/independent-source-review.json'])
    require(source_review['findings'] == [] and source_review['source_proposal_sha256'] == digest(files[CACHE+'/source-proposal.json'])
            and source_review['patch_sha256'] == digest(files[CACHE+'/proposal.patch']),'source review admission')
    for name,expected in source_review['changed_source_sha256'].items():
        require(digest(candidate[name]) == expected,'reviewed implementation changed')
    checked=check_gates(files)
    # Omitted binaries have historical producer digest evidence only. No binary
    # or native-library read is performed by this portable check.
    omissions=manifest['omitted_private_files']
    expected_omitted={}
    for prefix,record in [(CACHE,'build-001/build.json'),(FAILED,'build-001/build.json'),(TYPED,'build-001/build.json')]:
        for name,expected in json.loads(files[prefix+'/'+record])['outputs'].items():
            expected_omitted[prefix+'/build-001/'+name]=expected
    expected_omitted[CACHE+'/tests-001/frozen-cache-tests']=json.loads(files[CACHE+'/tests-001/tests.json'])['executed_binary_sha256']
    for domain in ['f64','DoubleFloat','Float128Dual','Float256Dual']:
        record=TYPED+'/run-'+domain+'-001/run.json'
        expected_omitted[TYPED+'/run-'+domain+'-001/frozen-typed_n6']=json.loads(files[record])['executed_binary_sha256']
    require({name:item['sha256'] for name,item in omissions.items() if 'sha256' in item} == expected_omitted
            and len(expected_omitted) == 9, 'historical omitted product digest chain')
    require(sum(name.endswith('.pyc') for name in omissions) == 8 and len(omissions) == 17, 'omission inventory')
    numeric=check_saved(files,lambda name:borrowed[name])
    numeric['domains']={domain:{key:value[key] for key in ['full_gate','complete_calls','available_slots','successful_lanes','runtime_status']}
                        for domain,value in numeric['domains'].items()}
    if args.reconstruct:
        destination=args.reconstruct.resolve()
        require(destination != ROOT and not destination.exists(),'reconstruction destination must be new')
        destination.mkdir(parents=True)
        for name,body in files.items():
            safe(name);path=destination/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    print(json.dumps(dict({**dict(base_files=85,candidate_files=88,typed_capture_files=90,build_source_files=91,
        exact_source_patch_reconstructed=True,reconstructed_noncompiled_files=len(files),
        available_guard_occurrences_checked=available_guards,historical_unbundled_guard_occurrences_not_rehashed=historical_guards,
        reconstruction_destination=str(args.reconstruct) if args.reconstruct else None),**checked,**numeric,
        'status':'passed','saved_numeric_status':numeric['status'],
        'no_compiler_integral_reference_profile_or_benchmark_executed':True,
        'native_build_or_numerical_requalification':False,'performance_qualified':False}),sort_keys=True))


if __name__ == '__main__':main()
