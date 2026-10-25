"""Capture-only rank2/rank7 adapter with compact immutable runtime inputs."""
import importlib.util
import os
from pathlib import Path
import sys

DELTA = Path(__file__).resolve().parent
HERE = DELTA.parent
WARM = HERE / 'probe-fix-v2'
sys.path.insert(0, str(HERE))
import common as primitive

ROOT, BUNDLE, SOURCE = primitive.ROOT, primitive.BUNDLE, primitive.SOURCE
CONTEXT = 'private_N7_rank2_then_rank7_same_generic_Cargo_probe_v1'
REQUIRES = {'capture128': [], 'capture256': [], 'compare': ['capture128', 'capture256']}
ACTIVE_RANK = None
require, load, save, sha = primitive.require, primitive.load, primitive.save, primitive.sha
key, absolute, merge, verify = primitive.key, primitive.absolute, primitive.merge, primitive.verify
BOUNDS = {2: {'capture128': (900, 120, 600), 'capture256': (1200, 150, 960)},
          7: {'capture128': (1680, 120, 1500), 'capture256': (1980, 120, 1800)}}
ENVIRONMENT_KEYS = ['PATH', 'LD_LIBRARY_PATH', 'LD_PRELOAD', 'NIX_LD', 'NIX_LD_LIBRARY_PATH',
    'PYTHONPATH', 'PYTHONHOME', 'SYMBOLICA_LOCK_DIR', 'SYMBOLICA_HIDE_BANNER',
    'RAYON_NUM_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS']
PROBE_SHA = '213ea01fd30a8acf2a794474db09ad9fc367fb9561667c23f73c76c4953a7e19'
BUILD_SHA = '688a0a0d269a38996075044721321f2aeafe0ab15e549c406c45af19ba1916c6'
RANK1_GATE_SHA = '1d65ca0fd43ea574e1b5b04e5766483ee376e5239b7d04f7901cb1a3db2553a1'
RANK1_MATH_SHA = 'a6e1a41c364423e10ecbe2f11394fdd0952d643cf7c69034dc4316a3604fa935'
QUAD_AUDIT_SHA = 'f0b8f0774d901957fac3369165212b0efac3bf6921cea3c940269f191af373fd'


def select_rank(value):
    global ACTIVE_RANK
    require(value in [2, 7] and ACTIVE_RANK is None, 'select exactly one proposed rank per process')
    ACTIVE_RANK = value


def rank():
    require(ACTIVE_RANK in [2, 7], 'rank must be selected before stage policy')
    return ACTIVE_RANK


def policy(operation):
    require(operation in REQUIRES, 'capture-only adapter has no compiler/cache/preparation operation')
    seconds, reserve, cap = (120, 15, 0) if operation == 'compare' else BOUNDS[rank()][operation]
    return dict(bound_seconds=seconds, postwork_reserve_seconds=reserve,
        per_child_cap_seconds=cap, cpu_affinity=([20, 21] if operation == 'compare'
            else [6] if operation == 'capture128' else [7]))


def stage_directory(operation, selected_rank=None):
    require(operation in REQUIRES, 'only captures/saved comparison create new outputs')
    return DELTA / 'runs' / ('rank' + str(rank() if selected_rank is None else selected_rank)) / (operation + '-001')


def check_context(protocol, closures=(), budget=None):
    require(not closures, 'compact runtime must not add historical/transitive source walks')
    require(set(protocol['frozen_environment']) == set(ENVIRONMENT_KEYS)
        and {name: os.environ.get(name) for name in ENVIRONMENT_KEYS} == protocol['frozen_environment'],
        'required runtime environment differs')
    binary = absolute(protocol['shared_executable'])
    require(not binary.is_symlink() and binary.is_file() and binary.stat().st_mode & 0o222 == 0,
            'shared generic executable must stay a read-only regular file')


def read_protocol():
    require(Path.cwd().resolve() == ROOT, 'run only from project root')
    p = load(DELTA / 'protocol.json')
    require(p['status'] == 'capture_only_next_ranks_frozen_awaiting_root_grants'
        and p['context'] == CONTEXT and p['ranks'] == [2, 7]
        and p['warm_build_receipt_sha256'] == BUILD_SHA and p['owned_generic_probe_sha256'] == PROBE_SHA
        and p['rank1_gate_sha256'] == RANK1_GATE_SHA and p['rank1_math_sha256'] == RANK1_MATH_SHA
        and p['quad_review_sha256'] == QUAD_AUDIT_SHA
        and p['source_snapshot']['files'] == 128 and p['no_recursive_historical_guards'] is True,
        'wrong compact actual-Cargo/source/reference lineage')
    required = {key(DELTA / name) for name in
        ['rank_adapter.py', 'run.py', 'prepare.py', 'recipe.json', 'source-manifest.json', 'source-snapshot.tar.gz']}
    required |= {key(HERE / name) for name in ['common.py', 'lifecycle.py', 'compare_positive_saved.py']}
    required |= {key(BUNDLE / 'fixture.json'), p['shared_executable'],
        'validation/highpoint-thin-n6-rank7-phase/reference/compare_public.py',
        'target/quad-iregi-source-audit/future-positive-rank-requests/independent-saved-review.json'}
    require(required <= set(p['inputs']) and p['inputs'][p['shared_executable']] == PROBE_SHA
        and p['inputs'][key(DELTA / 'source-snapshot.tar.gz')] == p['source_snapshot']['sha256'],
        'compact active source/executable/reference bindings incomplete')
    return p


def command(operation, protocol, budget=None):
    require(operation in ['capture128', 'capture256'], 'only full capture is a producer')
    folder = stage_directory(operation)
    return [protocol['tools']['taskset'], '-c', str(policy(operation)['cpu_affinity'][0]),
        str(absolute(protocol['shared_executable'])), str(BUNDLE / 'fixture.json'), '7', str(rank()),
        'pv', operation.removeprefix('capture'), '53', '1', str(folder / 'result.json')]


def terminal(record, operation, selected_rank):
    seconds, reserve, cap = ((120, 15, 0) if operation == 'compare' else BOUNDS[selected_rank][operation])
    require(record['status'] == 'passed' and record['context'] == CONTEXT
        and record['tensor_rank'] == selected_rank and record['operation'] == operation
        and record['attempt'] == 1 and record['bound_seconds'] == seconds
        and record['postwork_reserve_seconds'] == reserve and record['per_child_cap_seconds'] == cap
        and record['cpu_affinity'] == ([20, 21] if operation == 'compare' else [6] if operation == 'capture128' else [7])
        and record['elapsed_seconds'] <= seconds and record['inputs_unchanged'] is True
        and not record['cleanup_errors'] and not any(record.get(name) for name in
            ['error', 'cancellation', 'postguard_error', 'postguard_cancellation', 'finalization_error']),
        'preceding rank/stage did not complete')
    if operation != 'compare':
        require(len(record['steps']) == 1 and record['steps'][0]['status'] == 'exited'
            and record['steps'][0]['returncode'] == 0 and record['steps'][0]['owned_group_gone'] is True
            and not record['steps'][0].get('timeout') and record['executed_binary_sha256'] == PROBE_SHA,
            'preceding capture owned process or binary failed')


def rank1_gate(record, mathematical):
    require(record['status'] == 'passed' and record['context'] == 'private_N7_rank1_probe_only_fix_v2_warm_actual_Cargo'
        and record['operation'] == 'compare' and record['attempt'] == 1
        and record['inputs_unchanged'] is True and not record['cleanup_errors']
        and record['saved_math_status'] == mathematical['status'] == 'passed_saved_math'
        and mathematical['rank'] == 1 and mathematical['complex_slots_per_capture'] == 20,
        'exact rank-one paired gate absent')


def stage_context(operation, protocol):
    bindings = dict(protocol['inputs'])
    # Historical maps/products are attestations only; never recursively merged.
    for name, digest in protocol['historical_attestations'].items():
        merge(bindings, name, digest)
    review_path = DELTA / 'source-review.json'
    grant_path = DELTA / 'grants' / ('rank' + str(rank()) + '-' + operation + '.json')
    review, grant = load(review_path), load(grant_path)
    require(review['status'] == 'source_review_passed' and review['findings'] == []
        and review['reviewer'] not in [None, '/root/seven_point_api', '/root/seven_point_api/seven_lifecycle_audit'],
        'independent capture-adapter review absent')
    seal_path = DELTA / 'prepare-001/run.json'
    seal = load(seal_path)
    require(seal['status'] == 'compact_source_seal_passed_awaiting_independent_review_and_root_grants'
        and seal['inputs_unchanged'] is True and seal['snapshot_files'] == 128
        and seal['outputs']['protocol.json'] == review['protocol_sha256'], 'compact source seal not admitted')
    require(grant['status'] == 'root_execution_granted' and grant['grantor'] == '/root'
        and grant['context'] == CONTEXT and grant['rank'] == rank() and grant['operation'] == operation
        and grant['attempt'] == 1 and grant['correctness_only'] is True
        and grant['protocol_sha256'] == review['protocol_sha256']
        and all(grant[name] == value for name, value in policy(operation).items()), 'exact root rank/resource grant absent')
    if operation.startswith('capture'):
        require(grant['numerical_lease'] is True, 'root correctness numerical lease absent')
    merge(bindings, key(DELTA / 'protocol.json'), grant['protocol_sha256'])
    merge(bindings, key(review_path), grant['review_sha256'])
    merge(bindings, key(grant_path), sha(grant_path))
    merge(bindings, key(seal_path), review['preparation_receipt_sha256'])
    if rank() == 2:
        previous_folder = WARM / 'runs/compare-001'
        rank1_gate(load(previous_folder / 'run.json'), load(previous_folder / 'comparison.json'))
        merge(bindings, key(previous_folder / 'run.json'), RANK1_GATE_SHA)
        merge(bindings, key(previous_folder / 'comparison.json'), RANK1_MATH_SHA)
        require(grant['previous_rank_receipt_sha256'] == RANK1_GATE_SHA, 'wrong rank-one gate pin')
    else:
        previous_folder = stage_directory('compare', 2)
        previous = load(previous_folder / 'run.json')
        terminal(previous, 'compare', 2)
        require(previous['saved_math_status'] == 'passed_saved_math', 'rank-two paired numerical gate absent')
        merge(bindings, key(previous_folder / 'run.json'), grant['previous_rank_receipt_sha256'])
        merge(bindings, key(previous_folder / 'comparison.json'), previous['outputs']['comparison.json'])
    require(set(grant['required_receipts']) == set(REQUIRES[operation]), 'wrong current pair receipt set')
    for prior in REQUIRES[operation]:
        folder = stage_directory(prior)
        record = load(folder / 'run.json')
        terminal(record, prior, rank())
        merge(bindings, key(folder / 'run.json'), grant['required_receipts'][prior])
        for name, digest in record['outputs'].items():
            merge(bindings, key(folder / name), digest)
    return bindings, [], {}


def capture_shape(record, bits):
    source = ROOT / 'validation/highpoint-thin-n6-rank7-phase/reference/compare_public.py'
    spec = importlib.util.spec_from_file_location('retained_rank_basis_shape', source)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    basis = helper.canonical_basis(rank())
    require(record['private_validation_overlay'] is True and record['public_positive_rank_support'] is False
        and record['working_bits'] == bits and record['requested_bits'] == 53
        and record['rows'] == record['components'] == 1 and record['basis'] == basis
        and record['parameter_count'] == 36 and record['fixture'] == str(BUNDLE / 'fixture.json'),
        'capture rank/basis/context differs')
    require(record['settings'] == dict(propagators=7, rank=rank(), powers=[1]*7, dimension_shift=0,
        algorithm='PassarinoVeltman', convention='IregiNative', tensor_weights='Components',
        invariants='FromShifts', input_policy='Preserve'), 'capture mathematical settings differ')
    require(len(record['lanes']) == len(record['lane_statuses']) == 1
        and len(record['fallback_used']) == len(record['analytic_used']) == 1, 'lane/flag shapes incomplete')
    lane = record['lanes'][0]
    if record['status'] == 'all_lanes_success':
        require(record['lane_statuses'] == ['Success'] and lane['status'] == 'Success'
            and len(lane['moments']) == len(basis) and all(len(moment) == 4 for moment in lane['moments'])
            and all(isinstance(slot[name], str) and slot[name] for moment in lane['moments']
                for slot in moment for name in ['real', 'imaginary']), 'successful full array incomplete')
    else:
        require(record['status'] == 'lanes_rejected' and lane['moments'] is None,
                'failed coefficients cannot appear as successful zero values')
