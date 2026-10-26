"""Replay four saved post-fix resource failures; no native or mathematical evaluation."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import io
import json
import re
import runpy
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = '/shared/external/iregi/iregi-rust/'
CORE = 'validation/e6-dual-optional-zero-profile-core-tests'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {'sha256': sha(body), 'bytes': len(body)}


def load(body):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(body, object_pairs_hook=pairs)


def safe(name):
    p = PurePosixPath(name)
    need(name and str(p) == name and not p.is_absolute() and '..' not in p.parts, 'safe relative path')


def unpack(body, expected, complete=False):
    result = {}
    seen = set()
    with tarfile.open(fileobj=io.BytesIO(body), mode='r:gz') as archive:
        for member in archive:
            safe(member.name)
            need(member.isfile() and member.name not in seen, 'unique regular archived member')
            seen.add(member.name)
            if member.name in expected:
                data = archive.extractfile(member).read()
                need(desc(data) == expected[member.name], 'selected archive member identity')
                need(not data.startswith((b'\x7fELF', b'!<arch>')) and b'S-130-' not in data,
                     'saved text/source object only')
                result[member.name] = data
    need(set(result) == set(expected), 'all selected archive members exist')
    if complete:
        need(seen == set(expected), 'closed own payload inventory')
    return result


def restore_files(manifest):
    need({str(p.relative_to(HERE)) for p in HERE.rglob('*')
          if p.is_file() and '__pycache__' not in p.parts} == set(manifest['capsule_files']) | {'manifest.json'},
         'closed own capsule inventory')
    for name, row in manifest['capsule_files'].items():
        safe(name)
        need(desc((HERE / name).read_bytes()) == row, 'own file identity')
    for name, row in manifest['parent_files'].items():
        safe(name)
        need(desc((ROOT / name).read_bytes()) == row, 'shallow parent file identity')
    core_manifest = load((ROOT / CORE / 'manifest.json').read_bytes())
    need(sha((ROOT / CORE / 'manifest.json').read_bytes()) == manifest['core_manifest_sha256'],
         'actual 210-source focused-test parent identity')
    core = runpy.run_path(str(ROOT / CORE / 'check.py'), run_name='saved_core_source_loader')
    inherited = core['restore_files'](core_manifest)
    extra = {}
    for name, row in manifest['direct_archives'].items():
        need(manifest['parent_files'][name] == {k: row[k] for k in ['sha256', 'bytes']},
             'direct selected DD archive identity is pinned')
        extra[name] = unpack((ROOT / name).read_bytes(), row['members'])
    own = unpack((HERE / 'payload.tar.gz').read_bytes(), manifest['payload_members'], complete=True)
    result = dict(inherited)
    for alias, row in manifest['aliases'].items():
        safe(alias)
        if 'parent_alias' in row:
            body = inherited[row['parent_alias']]
        elif 'archive' in row:
            body = extra[row['archive']][row['member']]
        else:
            body = own[row['member']]
        need(desc(body) == {k: row[k] for k in ['sha256', 'bytes']}, 'exact saved alias bytes')
        need(alias not in result or result[alias] == body, 'no conflicting parent alias')
        result[alias] = body
    return result


def replay(manifest, files):
    def read(alias):
        return load(files[alias])

    omitted = manifest['omitted_native_artifacts']
    source_manifest = read('target/e6-dual-optional-zero-profile-qualification/build-001/receipt.json')
    need(len(source_manifest['sources']) == 210 and source_manifest['status'] ==
         'passed_fresh_core_libtest_build_and_freeze', 'actual inherited source build')
    actual_binary = source_manifest['products']['tests']['sha256']
    summaries = []
    guard_count = 0
    for item in manifest['attempts']:
        base = item['capture_alias']
        receipt = read(base + '/receipt.json')
        protocol = read(item['root_alias'] + '/protocol.json')
        capture = read(base + '/capture.json')
        audit = read(base + '/mechanism-audit.json')
        summary = read(base + '/failure-summary.json')
        native = files[base + '/native.log'].decode()
        need(sha(files[base + '/receipt.json']) == item['receipt_sha256'], 'actual terminal failure receipt')
        need(receipt['status'] == 'failed_capture_retained' and receipt['inputs_unchanged'] is True
             and receipt['cleanup_errors'] == [] and len(receipt['steps']) == 1,
             'terminal failure with unchanged bindings and clean ownership')
        need(len(receipt['inputs']) == item['guarded_inputs']
             and receipt['address_space_limit_bytes'] == 64 * 1024**3, 'actual input count and 64 GiB ceiling')
        for absolute, digest in receipt['inputs'].items():
            if absolute in omitted:
                need(omitted[absolute] == digest == actual_binary, 'explicit omitted native input hash')
                continue
            need(absolute.startswith(PREFIX), 'guarded project-local input')
            alias = absolute[len(PREFIX):]
            need(alias in files and sha(files[alias]) == digest, 'guarded saved input ' + alias)
            guard_count += 1
        for name, digest in receipt['outputs'].items():
            alias = base + '/' + name
            if PREFIX + alias in omitted:
                need(omitted[PREFIX + alias] == digest == actual_binary, 'explicit omitted native output hash')
            else:
                need(sha(files[alias]) == digest, 'saved guarded output')
        for absolute, digest in protocol['bindings'].items():
            if absolute in omitted:
                need(omitted[absolute] == digest == actual_binary, 'protocol native identity')
            else:
                need(absolute.startswith(PREFIX) and sha(files[absolute[len(PREFIX):]]) == digest,
                     'immutable protocol bound input')
        need(protocol['binary']['sha256'] == actual_binary
             and protocol['source_context']['count'] == 210
             and protocol['source_context']['build_receipt_sha256'] == manifest['actual_build_receipt_sha256'],
             'actual current frozen source and artifact provenance')
        need(protocol['working_bits'] == receipt['working_bits'] == item['working_bits']
             and receipt['requested_bits'] == 53 and receipt['dimension_shift_h'] == 1,
             'actual precision and D6 request')
        need(capture['status'] == 'evaluating_batch' and capture['calls'] == []
             and capture['active_call'] == 'odd_repeated_with_invalid', 'no returned numerical arrays')
        need(capture['public_Dual_qualified'] is False and capture['numerically_qualified'] is False
             and capture['performance_qualified'] is False, 'no mathematical or performance success')
        need(summary['returned_calls'] == summary['returned_parent_arrays'] == 0
             and summary['inputs_bound'] == item['guarded_inputs']
             and summary['kernel_accuracy_or_branch_verdict'] is None
             and summary['mechanism_qualified'] is False, 'saved resource-only failure scope')
        for field, alias in [('receipt_sha256', base + '/receipt.json'),
                             ('capture_sha256', base + '/capture.json'),
                             ('native_log_sha256', base + '/native.log'),
                             ('mechanism_audit_sha256', base + '/mechanism-audit.json')]:
            need(summary[field] == sha(files[alias]), 'failure summary binding ' + field)
        step = receipt['steps'][0]
        need(step['status'] == 'failed' and step['owned_group_gone'] is True
             and step['timeout_seconds'] == item['native_limit_seconds'], 'actual owned terminal boundary')
        need('PV prepare end affine-power N5 full-rank 6 child h=1 powers [1, 1, 1, 1, 1]:' in native
             and 'reachability 0/12318 aliases' not in native, 'generic constructor complete without duplicate optional pass')
        if item['boundary'] == 'native_deadline':
            need(step.get('timeout') is True and step['returncode'] == -15
                 and summary['timeout'] is True and summary['allocation_failure_observed'] is False,
                 'preserved 2400-second deadline boundary')
        else:
            need(not step.get('timeout', False) and step['returncode'] == -6
                 and summary['timeout'] is False and summary['failure'] in native,
                 'preserved GMP allocation SIGABRT boundary')
        namespace = {'__name__': 'frozen_saved_mechanism'}
        checker_alias = item['root_alias'] + '/check_saved_mechanism.py'
        exec(compile(files[checker_alias], checker_alias, 'exec'), namespace)
        findings = []
        try:
            namespace['audit'](capture)
        except (AssertionError, KeyError, TypeError, ValueError) as error:
            findings.append(str(error))
        expected_audit = {'status': 'failed_saved_mechanism_gate',
                          'capture_sha256': sha(files[base + '/capture.json']),
                          'independent_numeric_agreement_qualified': False,
                          'performance_qualified': False, 'full_objective_met': False,
                          'default_Hybrid_qualified': False,
                          'algorithm_scope': 'explicit PV only; retained Hybrid preparation failures remain failures',
                          'findings': findings}
        need(audit == expected_audit and findings == ['complete fixed capture'],
             'entire original saved mechanism failure audit reproduced')
        observations = [load(line) for line in files[base + '/resource-observations.jsonl'].splitlines()]
        need(observations and all(row['working_bits'] == item['working_bits'] for row in observations),
             'saved resource observations retain their actual precision scope')
        # The deadline observers stop before final cleanup in the original data.
        # Terminal ownership comes from the receipt, not a fabricated last sample.
        summaries.append({'working_bits': item['working_bits'], 'boundary': item['boundary'],
                          'receipt_sha256': item['receipt_sha256'],
                          'native_seconds': step['elapsed_seconds'], 'total_seconds': receipt['elapsed_seconds'],
                          'guarded_inputs': len(receipt['inputs']), 'returned_calls': 0,
                          'saved_resource_observations': len(observations),
                          'last_observer_process_gone': observations[-1].get('process_gone'),
                          'returncode': step['returncode']})

    profile = manifest['profile_root_alias']
    recorded = read(profile + '/Float128-sample-001/receipt.json')
    offline = read(profile + '/Float128-sample-001/offline-no-inline-001/receipt.json')
    need(recorded['sample_seconds'] == 2 and recorded['frequency_hz'] == 49
         and recorded['user_stack_bytes'] == 4096 and recorded['bits'] == 128,
         'bounded original Float128 sampling instant')
    need(recorded['steps'][0]['returncode'] == 0 and recorded['steps'][1]['timeout'] is True
         and recorded['steps'][1]['returncode'] == -15, 'first offline symbolization timeout retained')
    need(recorded['same_native_kernel_identity_after'] is True and recorded['no_native_stop_or_kill'] is True,
         'saved sampling ownership and unchanged target identity')
    for absolute, digest in recorded['inputs'].items():
        need(absolute.startswith(PREFIX) and sha(files[absolute[len(PREFIX):]]) == digest,
             'saved sampling controller binding')
    for name, digest in recorded['outputs'].items():
        if name == 'perf.data':
            need(digest == manifest['omitted_raw_profile']['sha256'], 'omitted raw trace historical hash')
        else:
            need(sha(files[profile + '/Float128-sample-001/' + name]) == digest, 'sampling text output binding')
    need(offline['no_native_attachment'] is True and offline['status'] == 'passed_saved_symbolized_profile_report'
         and offline['sample_sha256'] == manifest['omitted_raw_profile']['sha256']
         and offline['steps'][0]['status'] == 'exited' and offline['steps'][0]['returncode'] == 0,
         'later offline no-inline report succeeded without another native attachment')
    symbol_text = files[profile + '/Float128-sample-001/offline-no-inline-001/report.txt']
    need(sha(symbol_text) == offline['report_sha256'] and b'# Total Lost Samples: 0' in symbol_text
         and b"# Samples: 96  of event 'cpu-clock:u'" in symbol_text,
         'actual saved 96-sample, zero-lost symbol text')
    note = files[manifest['memory_review_alias']]
    need(sha(note) == manifest['memory_review_sha256'], 'memory review exact immutable bytes')
    need(b'does **not** prove that a 96 GiB address-space ceiling is sufficient' in note,
         '96 GiB sufficiency remains explicitly unproved')
    return {'status': 'passed_saved_postfix_resource_boundaries_replay',
            'preserved_current_source_failed_attempts': 4,
            'preserved_pre_fix_failed_attempts_in_parent': 4,
            'actual_source_bodies_in_parent': 210, 'actual_focused_distinct_passes_in_parent': 24,
            'attempts': summaries, 'checked_nonbinary_capture_input_guards': guard_count,
            'original_failed_mechanism_audits_reproduced': 4,
            'source_bodies_duplicated_in_this_payload': 0, 'dd_anchor_bodies_duplicated_in_this_payload': 0,
            'profile_seconds': 2, 'profile_samples': 96, 'profile_lost_samples': 0,
            'profile_scope': 'one original Float128/64 GiB numerical instant; not whole-run dominance or a benchmark',
            'raw_profile_trace_omitted': True, 'initial_offline_symbolization_timeout_preserved': True,
            'later_offline_report_native_attachment': False,
            'address_space_96gib_sufficiency_proved': False, 'active_96gib_captures_archived': False,
            'mathematical_success_qualified': False, 'full_rank6_dual_qualified': False,
            'native_execution': False, 'native_artifact_rehash': False,
            'new_integral_evaluation': False, 'performance_qualified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output')
    args = parser.parse_args()
    manifest = load((HERE / 'manifest.json').read_bytes())
    summary = replay(manifest, restore_files(manifest))
    if args.output:
        Path(args.output).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
