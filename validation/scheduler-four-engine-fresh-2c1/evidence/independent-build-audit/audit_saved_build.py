"""Independent saved-file build audit: no subprocess, compiler or kernel.

Does not import the producer's provenance/admission modules.  Reads only files,
hashes, saved compiler events and metadata.  A failed audit writes no admission.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import time

ROOT = Path('/shared/external/iregi/iregi-rust')
BASE = ROOT/'target/guard-performance-review/optimized-performance-proposal'
V3 = BASE/'v3'
PIN = '2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2'
PROTOCOL_SHA = '6100e81c0ca46880003a26d222807ef14e4349d7aca579cff059f23a5854aa74'
ORIGINAL_SHA = '4821d86ef2ecfc5be1490da7b88f631a22db9386cc02697f7b506897dd1fac67'
FAILED_SHA = '9069bc03597f0a423ef1271257472ce90e79b685b8f2e5f7d6f8824ee88386d8'
PROJECT = {'symbolica', 'oneloop', 'iregi_masters', 'iregi_rust'}
META_KEYS = ('name', 'crate_hash', 'stable_crate_id', 'dependencies')


def need(value, why):
    if not value:
        raise ValueError(why)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def metadata(text):
    """Parse pinned rustc listing independently, without silently skipped rows."""
    lines = text.splitlines()
    need(lines.count('Crate info:') == 1, 'metadata header count')
    need(lines.count('=External Dependencies=') == 1, 'metadata dependency section')
    split = lines.index('=External Dependencies=')
    header, tail = lines[:split], lines[split+1:]
    names = [line[5:] for line in header if line.startswith('name ')]
    hashes = [line for line in header if line.startswith('hash ')]
    need(len(names) == len(hashes) == 1, 'metadata root count')
    root = re.fullmatch(r'hash ([0-9a-f]{1,32}) stable_crate_id (StableCrateId\(([0-9]+)\))', hashes[0])
    need(root is not None and int(root[3]) < 2**64, 'metadata root identity')
    need(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:-[0-9a-f]{16})?', names[0]), 'metadata display name')
    need('triple x86_64-unknown-linux-gnu' in header, 'metadata target')
    deps = {}
    for line in tail:
        if not line.strip():
            continue
        match = re.fullmatch(r'([1-9][0-9]*) ([A-Za-z_][A-Za-z0-9_]*(?:-[0-9a-f]{16})?) hash ([0-9a-f]{1,32}) host_hash None kind (?:Unconditional|Conditional|MacrosOnly) (?:public|private)(?: linkage Some\(RequireStatic\))?', line)
        need(match is not None, 'unparsed metadata dependency: '+line)
        need(int(match[1]) == len(deps)+1 and match[2] not in deps, 'metadata duplicate/omitted/reordered dependency')
        deps[match[2]] = match[3]
    need(len(set(deps.values())) == len(deps), 'metadata hash collision')
    need(names[0] not in deps and root[1] not in deps.values(), 'metadata self dependency')
    return {'name': names[0], 'crate_hash': root[1], 'stable_crate_id': root[2], 'dependencies': deps}


def project_like(name):
    return name.startswith(('symbolica', 'oneloop', 'iregi'))


def terminal(event, command):
    need(event['command'] == command, 'saved executed command mismatch')
    need(event['returncode'] == 0 and event['owned_group_gone'] is True, 'nonzero/live compiler group')
    need(type(event['owned_process_group']) is int and event['owned_process_group'] > 0, 'missing owned group')
    need(not any(key in event for key in ('error', 'timeout', 'cancellation')), 'terminal error/timeout/cancellation')
    need(event['status'] in ('passed', 'exited'), 'compiler terminal status')


def flag_values(command, key):
    return [command[index+1] for index, value in enumerate(command[:-1]) if value == key]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--continuation-sha256', required=True)
    ap.add_argument('--merged-sha256', required=True)
    ap.add_argument('--output-directory', type=Path, required=True)
    args = ap.parse_args()
    need(Path.cwd() == ROOT, 'wrong cwd')
    folder = args.output_directory.resolve()
    folder.mkdir(exist_ok=False)
    started = time.monotonic()
    report = {'schema_version': 1, 'reviewer': '/root/scheduler_perf_resume/fresh_recipe_audit',
              'status': 'checking', 'scope': 'Independent saved source/artifact/metadata/terminal build evidence only; no compiler, metadata child, executable-under-test, integral or timing launched.',
              'pinned_source_revision': PIN, 'bound_files': {}, 'compiler_roles': [],
              'archive_metadata': {}, 'probes': {}, 'numerical_qualified': False,
              'performance_qualified': False, 'production_adoption_authorized': False}
    bound = {}

    def bind(path, expected=None):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT/path
        actual = digest(path)
        need(expected is None or actual == expected, 'changed file: '+str(path))
        need(path not in bound or bound[path] == actual, 'conflicting file binding')
        bound[path] = actual
        return actual

    try:
        bind(Path(__file__))
        protocol_path = V3/'protocol.json'
        bind(protocol_path, PROTOCOL_SHA)
        p = read(protocol_path)
        cont_path = Path(p['attempt_directory'])/'build.json'
        merged_path = Path(p['attempt_directory'])/'complete-build-admission.json'
        bind(cont_path, args.continuation_sha256)
        bind(merged_path, args.merged_sha256)
        cont, merged = read(cont_path), read(merged_path)
        for item in (cont, merged):
            need(item['status'] == 'passed' and item['success'] is True, 'build not terminal passed')
            need(item['protocol_sha256'] == PROTOCOL_SHA, 'build protocol mismatch')
            need(item['guard_before'] is True and item['guard_after'] is True and item['cleanup_errors'] == [], 'build guard/cleanup failure')
            need(not any(k in item for k in ('error', 'guard_error', 'cancellation')), 'build failure fields')
        need(cont['aggregate_budget_seconds'] == 2400 and cont['cleanup_postguard_reserve_seconds'] == 30, 'changed continuation budget')
        need(cont['deadline_exceeded'] is False and 0 < cont['elapsed_seconds_diagnostic'] <= 2400, 'continuation deadline')
        need(cont['numerical_execution'] is False and cont['performance_measurement'] is False, 'build scope overclaim')
        need(merged['numerical_qualified'] is False and merged['performance_qualified'] is False, 'merged scope overclaim')
        need(merged['continuation_receipt'] == str(cont_path) and merged['continuation_receipt_sha256'] == args.continuation_sha256, 'merged terminal link')
        for raw, expected in {**p['protected_sha256'], **p['tool_sha256']}.items():
            bind(raw, expected)
        need(len(p['protected_sha256']) == 666 and p['pinned_source_revision'] == PIN, 'cohort/guard split')
        origin = read(p['pinned_origin_context'])
        old_live = read(V3/'protocol-with-live-origins.json')
        removed = set(old_live['protected_sha256'])-set(p['protected_sha256'])
        need(len(removed) == 257 and removed == set(origin['pinned_file_sha256']), 'released origin set')
        need(origin['git_revision'] == PIN and origin['file_count'] == 257, 'pinned origin identity')
        need(all(old_live['protected_sha256'][k] == origin['pinned_file_sha256'][k] for k in removed), 'pinned origin byte declarations')
        origin_review = BASE/'reviews/v3-origin-context-independent-review.json'
        bind(origin_review, '6ca998d205438046ee1fdb43f93a68dac49957ede0b2ff6b4ee1f997079b73da')
        need(read(origin_review)['checks']['independent_git_blob_reads'] == 257, 'prior independent git observation')
        # No new Git/tool process is launched: these are previously independently
        # observed committed origin bytes, not present production-file guards.
        report['origin_context'] = {'revision': PIN, 'committed_origin_files': 257,
            'new_git_process_launched': False, 'prior_independent_git_review_sha256': bound[origin_review],
            'live_origin_files_rehashed': False, 'cohort_is_latest_production_main': False}
        original_path = Path(p['original_protocol'])
        bind(original_path, ORIGINAL_SHA)
        original = read(original_path)
        failed_path = Path(p['original_failed_receipt'])
        bind(failed_path, FAILED_SHA)
        failed = read(failed_path)
        need(failed['status'] == 'failed' and failed['error'] == "AssertionError('symbolica archive contamination: []')", 'original map failure changed')
        need(failed['guard_before'] and failed['guard_after'] and failed['cleanup_errors'] == [] and not failed['deadline_exceeded'], 'original guarded terminal evidence')
        need(failed['elapsed_seconds_diagnostic'] <= 3600 and failed['numerical_execution'] is False, 'original budget/scope')
        need(all(s['status'] == 'unrun' for s in failed['steps'][5:]), 'original unrun tail changed')
        need(len(failed['outputs']) == 4 and len(p['steps']) == 9 and len(cont['steps']) == 9, 'product accounting')
        need(merged['original_failed_receipt_sha256'] == cont['original_failed_receipt_sha256'] == FAILED_SHA, 'preserved original receipt relation')
        need(len(merged['steps']) == 14 and all(s['status'] == 'passed' for s in merged['steps']), 'merged 14 admissions')
        need(merged['outputs'] == {**cont['reused_products'], **cont['outputs']}, 'merged product object altered')
        need(len(merged['outputs']) == 14 and len(cont['outputs']) == 9 and len(cont['reused_products']) == 5, 'merged 5+9 accounting')
        closed_path = Path(p['closed_lower_inventory'])
        inventory = read(closed_path)
        closed = closed_path.parent/'closed-lower-deps'
        need(len(inventory) == 108 and {str(f) for f in closed.iterdir()} == set(inventory), 'closed directory membership')
        for raw, item in inventory.items():
            alias = Path(raw)
            need(alias.is_symlink() and os.readlink(alias) == item['target'], 'closed alias target')
            need(alias.stat().st_size == item['bytes'], 'closed alias size')
            bind(alias, item['sha256'])
            bind(item['target'], item['sha256'])
        proof_path = Path(p['proof'])
        bind(proof_path, p['proof_sha256'])
        proof = read(proof_path)
        need(proof['status'] == 'completed_readonly_project_dependency_identity_proof_no_build', 'wrong metadata proof scope')
        need(proof['original_failure_preserved'] is True and proof['original_full_search_directory_was_pre_guarded'] is False, 'retroactive broad-pool claim')
        lower = {}
        for name, item in proof['lower_roots'].items():
            bind(item['artifact'], item['sha256'])
            bind(item['original_guarded_artifact'], item['original_guarded_sha256'])
            bind(item['metadata_path'], item['metadata_sha256'])
            actual = metadata(Path(item['metadata_path']).read_text())
            need(actual == {k: item[k] for k in META_KEYS} and actual['name'] == name, 'lower observed metadata differs')
            need(not project_like(name), 'project alias in lower metadata')
            lower[name] = actual
        need(len(lower) == 127, 'lower root count')
        all_lower_hashes = {n: x['crate_hash'] for n, x in lower.items()}
        need(len(set(all_lower_hashes.values())) == 127, 'lower root hash collision')
        for item in lower.values():
            need(all(all_lower_hashes.get(n) == h for n, h in item['dependencies'].items()), 'lower metadata closure')
        need(len(proof['new_sysroot_rmeta_bindings']) == 19 and len(proof['closed_lower_symlink_inventory']) == 108, '108+19 scope split')
        for raw, expected in proof['new_sysroot_rmeta_bindings'].items():
            bind(raw, expected)
        for item in proof['stale_root_observations']:
            bind(item['artifact'], item['sha256'])
            bind(item['metadata_path'], item['metadata_sha256'])
            need(metadata(Path(item['metadata_path']).read_text()) == {k: item[k] for k in META_KEYS}, 'stale metadata observation differs')
        pool = ROOT/'target/benchmark/dependency-closures/6b24c03-complete-kinds/deps'
        stage_by_label = {s['label']: s for s in p['steps']}
        all_steps = original['steps'][:5] + p['steps']
        need([s['label'] for s in all_steps] == [s['label'] for s in original['steps']], '14 role ordering')
        known = {'baseline': {}, 'candidate': {}}
        by_artifact = {}
        metadata_events = {e['label']: e for e in cont['metadata_reads']}
        need(len(metadata_events) == len(cont['metadata_reads']) == 6, 'metadata child accounting')
        groups = []
        for index, step in enumerate(all_steps):
            label, product, variant = step['label'], step['product'], step['variant']
            oldstep = original['steps'][index]
            command = step['command']
            if index >= 5:
                expected_command = [f'dependency={closed}' if x == f'dependency={pool}' else x for x in oldstep['command']]
                for name, raw in oldstep['explicit_externs'].items():
                    path = Path(raw)
                    if path.parent == pool:
                        expected_command = [f'{name}={closed/path.name}' if x == f'{name}={path}' else x for x in expected_command]
                need(command == expected_command, 'unexpected continuation argv change: '+label)
                event = cont['steps'][index-5]
                terminal(event, command)
                need(event['label'] == label and event['status'] == 'passed', 'new compiler event label')
                bind(Path(p['attempt_directory'])/(label+'.log'), event['log_sha256'])
            else:
                event = failed['steps'][index]
                terminal(event, command)
                if index < 4:
                    need(event['status'] == 'passed', 'reused archive compiler status')
                    bind(Path(original['attempt_directory'])/(label+'.log'), event['log_sha256'])
                else:
                    need(event['status'] == 'exited', 'reused probe original status')
                    bind(Path(original['attempt_directory'])/(label+'.log'))
            groups.append({'role': label, 'owned_process_group': event['owned_process_group'], 'owned_group_gone': True, 'returncode': 0})
            need(step['environment'] == oldstep['environment'] and step['features'] == oldstep['features'], 'changed source feature/environment')
            need(command[:4] == [original['steps'][0]['command'][0], '-c', '32,33', original['steps'][0]['command'][3]], 'compiler/affinity role')
            options = flag_values(command, '-C')
            need(all(x in options for x in ['opt-level=3', 'debuginfo=0', 'strip=debuginfo', 'codegen-units=16', 'embed-bitcode=yes', 'debug-assertions=no', 'overflow-checks=no']), 'compiler profile')
            need(('lto=thin' if product == 'probe' else 'lto=off') in options, 'LTO role')
            need(command.count('--edition=2024') == 1 and '--edition' not in command, 'edition flag')
            name = flag_values(command, '--crate-name')[0]
            need(name == ('tirust_scheduler_probe' if product == 'probe' else 'iregi_rust' if product == 'core' else 'iregi_masters' if product == 'masters' else product), 'crate role')
            sources = [x for x in command if x.endswith('.rs')]
            need(len(sources) == 1, 'source role count')
            need(str(ROOT/'crates') not in sources[0] and str(ROOT/'dependencies') not in sources[0], 'live production source used')
            need(flag_values(command, '-o') == [step['output']], 'output path role')
            need(dict(x.split('=', 1) for x in flag_values(command, '--extern')) == step['explicit_externs'], 'explicit extern role')
            cfgs = flag_values(command, '--cfg')
            need([x for x in cfgs if x.startswith('feature=')] == [f'feature="{x}"' for x in step['features']], 'cfg feature roles')
            need(('iregi_qualification_capture' in cfgs) == step['capture_cfg'], 'capture cfg role')
            item = merged['outputs'][label]
            need(item['path'] == step['output'] and Path(item['path']).stat().st_size == item['bytes'], 'artifact path/size')
            bind(item['path'], item['sha256'])
            with Path(item['path']).open('rb') as stream:
                need(stream.read(8) == (b'\x7fELF\x02\x01\x01\x00' if product == 'probe' else b'!<arch>\n'), 'artifact format')
            need(item['provenance_admission'] == 'passed-v3', 'product provenance admission')
            if product != 'probe':
                if index < 4:
                    need(item['sha256'] == failed['outputs'][label]['sha256'], 'reused archive durable hash')
                    saved = proof['fresh'][name]
                    log = Path(saved['metadata_path'])
                    bind(log, saved['metadata_sha256'])
                else:
                    logitem = item['metadata_log']
                    log = Path(logitem['path'])
                    bind(log, logitem['sha256'])
                    metaevent = metadata_events[label]
                    expected_meta_command = [x.replace('<new-archive>', item['path']) for x in p['metadata_read_command']]
                    terminal(metaevent, expected_meta_command)
                    need(metaevent['status'] == 'passed' and metaevent['artifact_sha256'] == item['sha256'], 'metadata child source binding')
                    need(metaevent['metadata_sha256'] == logitem['sha256'], 'metadata log hash event')
                    groups.append({'role': label+'-metadata-only', 'owned_process_group': metaevent['owned_process_group'], 'owned_group_gone': True, 'returncode': 0})
                actual = metadata(log.read_text())
                need(actual['name'] == name and actual == item['actual_metadata'], 'actual project metadata item')
                required_names = set(known[variant])
                need({n for n in actual['dependencies'] if project_like(n)} == required_names, 'fresh predecessor set')
                allowed = {**all_lower_hashes, **{n: x['crate_hash'] for n, x in known[variant].items()}}
                need(all(allowed.get(n) == h for n, h in actual['dependencies'].items()), 'project flattened identity mismatch')
                for n, predecessor in known[variant].items():
                    need(actual['dependencies'].get(n) == predecessor['crate_hash'], 'fresh predecessor identity')
                    need(all(actual['dependencies'].get(k) == v for k, v in predecessor['dependencies'].items()), 'inherited transitive identity omitted')
                by_artifact[item['path']] = actual
                report['archive_metadata'][label] = {'artifact': item['path'], 'sha256': item['sha256'], 'metadata_log': str(log), **actual}
                if product != 'core':
                    known[variant][name] = actual
            else:
                need(set(item['archive_binding']) == PROJECT, 'probe upstream binding keys')
                upstream = {}
                for crate in PROJECT:
                    path = step['explicit_externs'][crate]
                    need(path in by_artifact, 'probe upstream has no actual metadata')
                    actual = by_artifact[path]
                    recorded = item['archive_binding'][crate]
                    need(recorded['path'] == path and recorded['sha256'] == bound[Path(path)] and recorded['crate_hash'] == actual['crate_hash'] and recorded['stable_crate_id'] == actual['stable_crate_id'], 'probe upstream identity binding')
                    upstream[crate] = {'path': path, 'sha256': recorded['sha256'], 'crate_hash': actual['crate_hash']}
                lm = item['link_map']
                bind(lm['path'], lm['sha256'])
                need(Path(lm['path']).stat().st_size == lm['bytes'], 'map size')
                text = Path(lm['path']).read_text()
                stale = re.findall(re.escape(str(pool))+r'/lib(?:symbolica|oneloop|iregi_[A-Za-z0-9_]+)-[^\s()]*?\.rlib', text)
                need(not stale, 'stale project archive in native map')
                need('original pure Rust archive paths are not guaranteed' in lm['scope'], 'native map scope missing')
                report['probes'][label] = {'path': item['path'], 'sha256': item['sha256'], 'upstream': upstream, 'map_sha256': lm['sha256'], 'scope': 'successful recorded exact compiler argv and actual upstream archive metadata; not metadata decoded from ELF and not original-path map presence'}
            report['compiler_roles'].append({'label': label, 'product': product, 'variant': variant, 'source': sources[0], 'flags_and_features_checked': True, 'compiler_returncode': 0, 'owned_group_gone': True})
        need(len(report['archive_metadata']) == merged['rust_archive_metadata_count'] == 10 and len(report['probes']) == 4, '10 archives/4 probes')
        need(len(groups) == 20, '14 codegen+6 metadata terminal groups')
        need(len({g['owned_process_group'] for g in groups}) == 20, 'duplicate child group IDs')
        root_hashes = [x['crate_hash'] for x in report['archive_metadata'].values()]
        need(len(set(root_hashes)) == 10 and not set(root_hashes).intersection(all_lower_hashes.values()), 'project root hash collision')
        need(not set(root_hashes).intersection(x['crate_hash'] for x in proof['stale_root_observations']), 'stale/project root hash overlap')
        for path, expected in bound.items():
            need(digest(path) == expected, 'audit postguard file changed: '+str(path))
        need({str(f) for f in closed.iterdir()} == set(inventory), 'audit postguard directory changed')
        for raw, item in inventory.items():
            need(Path(raw).is_symlink() and os.readlink(raw) == item['target'], 'audit postguard symlink changed')
        report.update(status='passed', protocol_sha256=PROTOCOL_SHA,
            original_failed_receipt_sha256=FAILED_SHA, continuation_receipt_sha256=args.continuation_sha256,
            merged_build_admission_sha256=args.merged_sha256, actual_compiler_products_checked=14,
            actual_archive_metadata_checked=10, actual_probes_checked=4,
            lower_metadata_roots_checked=127, closed_lower_entries_checked=108,
            recorded_terminal_groups_checked=groups, all_declared_inputs_artifacts_metadata_maps_hash_checked=True,
            before_after_audit_hash_guards_passed=True,
            original_failure_preserved=True, original_broad_search_was_not_closed=True,
            supplemental_sysroot_rmeta_identity_observations=19,
            supplemental_existing_probe_first_durable_hash_preserved=True,
            compiler_provenance_only=True, independent_parser=True,
            producer_admission_or_provenance_module_imported=False,
            subprocesses_launched=0, mathematical_qualification_implied=False)
    except Exception as error:
        report.update(status='failed', error=repr(error))
    report['bound_files'] = {str(p): h for p, h in bound.items()}
    report['bound_file_count'] = len(bound)
    report['elapsed_seconds_diagnostic'] = time.monotonic()-started
    report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    output = folder/'full-review.json'
    output.write_text(json.dumps(report, indent=2)+'\n')
    if report['status'] == 'passed':
        admission = {'status': 'passed', 'scope': 'Independent saved compiler/provenance build evidence only; no mathematical or performance qualification',
            'protocol_sha256': PROTOCOL_SHA, 'pinned_source_revision': PIN,
            'build_receipt_sha256': args.merged_sha256, 'continuation_receipt_sha256': args.continuation_sha256,
            'compiler_products_checked': 14, 'archive_metadata_checked': 10, 'probes_checked': 4,
            'all_declared_inputs_artifacts_metadata_maps_checked': True,
            'original_failed_receipt_preserved': True, 'full_review_path': str(output),
            'full_review_sha256': digest(output), 'numerical_qualified': False, 'performance_qualified': False}
        (folder/'admission.json').write_text(json.dumps(admission, indent=2)+'\n')
    print(json.dumps({'status': report['status'], 'full_review': str(output), 'full_review_sha256': digest(output), 'bound_files': len(bound), 'error': report.get('error')}))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
