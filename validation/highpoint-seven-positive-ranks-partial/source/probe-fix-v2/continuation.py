"""Explicit narrow probe-fix adapter; original reviewed helpers stay immutable."""
import importlib.util
from pathlib import Path
import sys

DELTA = Path(__file__).resolve().parent
BASE = DELTA.parent
sys.path.insert(0, str(BASE))
import common as old

ROOT, BUNDLE, SOURCE, HERE = old.ROOT, old.BUNDLE, old.SOURCE, BASE
CONTEXT = 'private_N7_rank1_probe_only_fix_v2_warm_actual_Cargo'
REQUIRES = {'build': [], 'capture128': ['build'], 'capture256': ['build', 'capture128'],
            'compare': ['build', 'capture128', 'capture256']}
require, load, save, sha = old.require, old.load, old.save, old.sha
key, absolute, merge, verify = old.key, old.absolute, old.merge, old.verify
check_context, cargo_environment = old.check_context, old.cargo_environment
metadata_document, emitted_artifact_closure = old.metadata_document, old.emitted_artifact_closure
policy = old.policy


def stage_directory(operation):
    if operation == 'metadata':
        return old.stage_directory('metadata')
    require(operation in REQUIRES, 'continuation allows only build/captures/saved comparison')
    return DELTA / 'runs' / ('build-002' if operation == 'build' else operation + '-001')


def read_protocol():
    require(Path.cwd().resolve() == ROOT, 'run only from project root')
    delta = load(DELTA / 'protocol.json')
    require(delta['status'] == 'probe_only_warm_continuation_frozen_awaiting_root_grants'
            and delta['context'] == CONTEXT
            and delta['correction_sha256'] == '6e3f18985f39ff945793e92825ceb524bec564bb07515d90fb22f14395a393a5'
            and delta['lineage_sha256'] == '8181a677fba40e9e988f66e8199f51b80731560073f287bf6cadfeb037f3d0d9'
            and delta['inputs'].get('target/quad-iregi-source-audit/future-positive-rank-requests/independent-saved-review.json')
                == 'f0b8f0774d901957fac3369165212b0efac3bf6921cea3c940269f191af373fd',
            'wrong narrow correction or partial-build lineage')
    base = load(BASE / 'protocol.json')
    require(sha(BASE / 'protocol.json') == delta['base_protocol_sha256'], 'base protocol changed')
    return dict(base, context=CONTEXT, continuation=delta)


def command(operation, protocol, budget=None):
    if operation == 'build':
        return old.command('build', protocol, budget)
    require(operation in ['capture128', 'capture256'], 'not a continuation producer')
    folder = stage_directory(operation)
    return [protocol['tools']['taskset'], '-c', '6', str(folder / 'frozen-executable'),
        str(BUNDLE / 'fixture.json'), '7', '1', 'pv', operation.removeprefix('capture'), '53', '1',
        str(folder / 'result.json')]


def terminal(record, operation):
    row = policy(operation)
    require(record['status'] == 'passed' and record['context'] == CONTEXT
        and record['operation'] == operation and record['attempt'] == (2 if operation == 'build' else 1)
        and all(record[name] == value for name, value in row.items())
        and record['inputs_unchanged'] is True and not record['cleanup_errors']
        and record['elapsed_seconds'] <= row['bound_seconds']
        and not any(record.get(name) for name in ['error', 'cancellation', 'postguard_error',
            'postguard_cancellation', 'finalization_error']), 'continuation prerequisite failed')
    if operation != 'compare':
        require(len(record['steps']) == 1 and record['steps'][0]['status'] == 'exited'
            and record['steps'][0]['returncode'] == 0 and record['steps'][0]['owned_group_gone'] is True
            and not record['steps'][0].get('timeout'), 'owned continuation group failed')


def stage_context(operation, protocol):
    delta = protocol['continuation']
    lineage = load(DELTA / 'partial-build-lineage.json')
    correction = load(DELTA / 'correction.json')
    require(lineage['status'] == 'partial_build_libraries_source_guard_admitted_for_narrow_probe_fix_only'
            and lineage['source_guard']['status'] == 'passed' and lineage['inputs_unchanged'] is True
            and lineage['original_failed_status_rewritten'] is False,
            'partial failure/source-guard lineage not admitted')
    bindings = dict(lineage['inputs'])
    probe = correction['old_probe_source_path']
    require(bindings[probe] == correction['old_probe_sha256'] == delta['old_probe_sha256'],
            'old source digest does not match failed attempt')
    bindings[probe] = delta['new_probe_sha256']
    for name, digest in delta['inputs'].items():
        merge(bindings, name, digest)
    require(correction['new_probe_sha256'] == delta['new_probe_sha256']
            and correction['changed_files'] == [probe]
            and correction['core_library_changed'] is False
            and correction['scalar_master_library_changed'] is False
            and correction['mathematical_operation_changed'] is False, 'correction scope broadened')
    failed = load(lineage['failed_receipt']['path'])
    require(failed['status'] == 'failed' and failed['operation'] == 'build'
            and failed['steps'][0]['returncode'] == 101 and failed['steps'][0]['owned_group_gone'] is True,
            'original failed build was not retained')
    review_path, grant_path = DELTA / 'source-review.json', DELTA / 'grants' / (operation + '.json')
    review, grant = load(review_path), load(grant_path)
    require(review['status'] == 'source_review_passed' and review['findings'] == []
            and review['reviewer'] not in [None, '/root/seven_point_api',
                '/root/seven_point_api/seven_lifecycle_audit'], 'independent continuation review absent')
    require(grant['status'] == 'root_execution_granted' and grant['grantor'] == '/root'
            and grant['context'] == CONTEXT and grant['operation'] == operation
            and grant['attempt'] == (2 if operation == 'build' else 1)
            and all(grant[name] == value for name, value in policy(operation).items())
            and grant['protocol_sha256'] == review['protocol_sha256']
            and grant['probe_only_correction'] is True and grant['correctness_only'] is True
            and grant['lineage_review_sha256'] == 'bc97b82ede32fcb0a6806897e05b11c1e44918aab441b6d1b5323005eaa063a5',
            'exact root warm-continuation grant absent')
    if operation == 'build':
        require(grant['isolated_cache_owner_lease'] is True and grant['reuse_partial_core_masters'] is True,
                'warm partial-build cache lease/reuse absent')
    if operation.startswith('capture'):
        require(grant['numerical_lease'] is True, 'numerical lease absent')
    merge(bindings, key(DELTA / 'protocol.json'), grant['protocol_sha256'])
    merge(bindings, key(review_path), grant['review_sha256'])
    merge(bindings, key(grant_path), sha(grant_path))
    require(set(grant['required_receipts']) == set(REQUIRES[operation]), 'wrong continuation receipt set')
    closures = [load(old.stage_directory('metadata') / 'metadata-source-freeze.json')]
    if operation == 'build':
        # Before the new producer only: the successful probe will legitimately
        # add files to the old dependency directory. Produced closure guards
        # then bind that new membership under the unchanged original timer.
        check_context(protocol, [lineage['artifact_closure']])
    for prior in REQUIRES[operation]:
        folder = stage_directory(prior)
        record = load(folder / 'run.json')
        terminal(record, prior)
        merge(bindings, key(folder / 'run.json'), grant['required_receipts'][prior])
        for group in ['inputs', 'artifact_inputs']:
            for name, digest in record.get(group, {}).items():
                merge(bindings, name, digest)
        for name, digest in record['outputs'].items():
            merge(bindings, key(folder / name), digest)
        if prior == 'build':
            closures.append(load(folder / 'cargo-artifacts.json')['artifact_closure'])
    return bindings, closures, {}


def parse_build(path, protocol, metadata):
    spec = importlib.util.spec_from_file_location('frozen_continuation_Cargo_parser', old.ARTIFACT_PARSER)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    core_manifest = str(SOURCE / 'crates/iregi-rust/Cargo.toml')
    core = next(p for p in metadata['packages'] if p['manifest_path'] == core_manifest)
    parsed = parser.parse_command_log(str(path), {'products': {'driver': dict(
        target_name='seven_point_public_probe', kind='example',
        source_path=str(SOURCE / 'crates/iregi-rust/examples/seven_point_public_probe/main.rs'),
        features=['default', 'native-f64-abc'])}}, dict(package_id=core['id'],
            cargo_target_directory=str(BUNDLE / 'cargo-target'), cargo_build_directory=str(BUNDLE / 'cargo-build')))
    lineage = load(DELTA / 'partial-build-lineage.json')
    products = {}
    for name in ['core', 'masters']:
        previous = lineage['core_masters'][name]
        admitted = previous['event']
        require(admitted['fresh'] is False, 'partial product was not actually compiled in failed build')
        matches = [entry['raw_event'] for entry in parsed['compiler_artifacts']
            if entry['package_id'] == admitted['package_id'] and entry['target'] == admitted['target']]
        require(len(matches) == 1, 'missing/duplicate partial product identity')
        event = matches[0]
        require(type(event['fresh']) is bool and dict(event, fresh=False) == admitted,
                'reused core/masters event changed beyond the fresh flag')
        require(set(event['filenames']) == set(previous['filenames_sha256']), 'partial library filenames changed')
        for filename, digest in previous['filenames_sha256'].items():
            require(sha(filename) == digest, 'partial core/masters artifact bytes changed')
        products[name] = event
    matches = [entry['raw_event'] for entry in parsed['compiler_artifacts']
        if entry['package_id'] == core['id'] and entry['target']['name'] == 'seven_point_public_probe'
        and entry['target']['kind'] == ['example']]
    require(len(matches) == 1, 'missing/duplicate new private probe')
    event = matches[0]
    require(event['fresh'] is False and event['manifest_path'] == core_manifest
        and event['target']['src_path'] == str(SOURCE / 'crates/iregi-rust/examples/seven_point_public_probe/main.rs')
        and event['features'] == ['default', 'native-f64-abc']
        and event['profile'] == lineage['core_masters']['core']['event']['profile']
        and event['executable'] in event['filenames']
        and Path(event['executable']).is_relative_to(BUNDLE / 'cargo-target'),
        'probe was not newly compiled from the corrected private source')
    products['driver'] = event
    return parsed, products
