"""Private positive-rank Cargo pilot: fixed scope, flat guards, no import work."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import os
import re

ROOT = Path('/shared/external/iregi/iregi-rust')
HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
SOURCE = BUNDLE / 'source'
PROTOCOL = HERE / 'protocol.json'
CONTEXT = 'private_actual_Cargo_N7_rank1_full_array_first_cohort_v1'
HELPER_SHA = 'c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824'
FIXTURE_SHA = '6c78096e83a399acd111137115505eae10da620b9dd68b6ead56eb2fa06489d2'
ARTIFACT_PARSER = ROOT / 'target/public-seven-point-current-cargo/cargo_artifacts.py'
SOURCE_EXCLUSIONS = ['.git', 'target', '__pycache__']
POLICIES = {'source-freeze': (180, 30, 0), 'cache-seed': (300, 60, 210),
            'metadata': (180, 30, 90), 'build': (900, 120, 720),
            'capture128': (900, 120, 600), 'capture256': (1200, 150, 960), 'compare': (120, 15, 0)}
REQUIRES = {'cache-seed': [], 'metadata': ['cache-seed'],
            'build': ['cache-seed', 'metadata'],
            'capture128': ['cache-seed', 'metadata', 'build'],
            'capture256': ['cache-seed', 'metadata', 'build', 'capture128'],
            'compare': ['cache-seed', 'metadata', 'build', 'capture128', 'capture256']}
ENV_EXACT = ['PATH', 'LD_LIBRARY_PATH', 'LD_PRELOAD', 'LIBRARY_PATH', 'COMPILER_PATH',
    'CPATH', 'C_INCLUDE_PATH', 'CPLUS_INCLUDE_PATH', 'LIBCLANG_PATH', 'LLVM_CONFIG_PATH',
    'RUSTC', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER', 'RUSTDOC', 'RUSTDOCFLAGS',
    'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'CARGO_HOME', 'CARGO_TARGET_DIR',
    'CARGO_BUILD_BUILD_DIR', 'CARGO_BUILD_JOBS', 'CARGO_INCREMENTAL', 'CC', 'CXX', 'AR',
    'FC', 'CFLAGS', 'CPPFLAGS', 'CXXFLAGS', 'FFLAGS', 'LDFLAGS', 'GMP_MPFR_SYS_CACHE',
    'GMP_MPFR_SYS_USE_SYSTEM_LIBS', 'GMP_LIB_DIR', 'MPFR_LIB_DIR', 'MPC_LIB_DIR',
    'CARGO_ENCODED_RUSTDOCFLAGS', 'CARGO_NET_OFFLINE', 'RUSTUP_HOME', 'RUSTUP_TOOLCHAIN',
    'XDG_CACHE_HOME', 'SYMBOLICA_LOCK_DIR', 'SYMBOLICA_HIDE_BANNER', 'RAYON_NUM_THREADS',
    'RUST_TEST_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'PYTHONPATH', 'PYTHONHOME']
ENV_PREFIXES = ['CARGO_PROFILE_', 'CARGO_TARGET_', 'CARGO_BUILD_', 'CARGO_CFG_', 'CC_',
    'CXX_', 'AR_', 'CFLAGS_', 'CPPFLAGS_', 'CXXFLAGS_', 'PKG_CONFIG', 'NIX_',
    'GMP_', 'MPFR_', 'MPC_', 'RUG_']


def require(value, message):
    if not value:
        raise ValueError(message)


def absolute(name):
    path = Path(name)
    return path if path.is_absolute() else ROOT / path


def key(path):
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'noncanonical absolute path')
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def load(path):
    def unique(pairs):
        result = {}
        for name, value in pairs:
            require(name not in result, 'duplicate JSON key: ' + name)
            result[name] = value
        return result
    return json.loads(absolute(path).read_text(), object_pairs_hook=unique)


def save(path, value):
    path = absolute(path)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def sha(path, budget=None):
    digest = hashlib.sha256()
    with absolute(path).open('rb') as stream:
        while True:
            if budget is not None:
                budget.remaining()
            block = stream.read(1024 * 1024)
            if not block:
                return digest.hexdigest()
            digest.update(block)


def merge(bindings, name, digest):
    require(isinstance(name, str) and '\x00' not in name and '..' not in Path(name).parts
            and str(Path(name)) == name, 'invalid flat binding path')
    require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest), 'invalid flat digest')
    require(name not in bindings or bindings[name] == digest, 'conflicting flat binding: ' + name)
    bindings[name] = digest


def verify(bindings, budget, phase):
    count, size = 0, 0
    for name, expected in sorted(bindings.items()):
        budget.remaining()
        require(sha(name, budget) == expected, 'changed sealed input: ' + name)
        count += 1
        size += absolute(name).stat().st_size
    return dict(phase=phase, hash_passes=1, unique_files=count, bytes_hashed=size,
                recursive_prior_guards=0)


def relevant_environment(environment):
    names = set(ENV_EXACT)
    names.update(name for name in environment if any(name.startswith(p) for p in ENV_PREFIXES))
    # License values are forwarded only in the unrecorded os.environ copy.
    names = {name for name in names if 'LICENSE' not in name.upper() and 'TOKEN' not in name.upper()}
    return {name: environment.get(name) for name in sorted(names)}


def source_inventory(root, budget=None, exclusions=SOURCE_EXCLUSIONS):
    result = []
    for current, directories, names in os.walk(root, followlinks=False):
        if budget is not None:
            budget.remaining()
        directories[:] = sorted(name for name in directories if name not in exclusions)
        require(not any((Path(current) / name).is_symlink() for name in [*directories, *names]),
                'source/output symlinks require explicit reviewed mapping: ' + current)
        result.extend(str((Path(current) / name).relative_to(root)) for name in sorted(names))
    return sorted(result)


def check_context(protocol, closures=(), budget=None):
    require(relevant_environment(os.environ) == protocol['frozen_environment'],
            'compiler/cache/native environment presence or values changed')
    for closure in [protocol, *closures]:
        for root, entries in closure['source_directory_inventory'].items():
            require(entries['excluded_directory_names'] in [SOURCE_EXCLUSIONS, []]
                    and source_inventory(root, budget, entries['excluded_directory_names']) == entries['files'],
                    'source membership changed: ' + root)
        for name, present in closure['configuration_path_inventory'].items():
            require(absolute(name).is_file() is present, 'configuration presence changed: ' + name)


def policy(operation):
    require(operation in POLICIES, 'unknown positive-rank stage')
    seconds, reserve, cap = POLICIES[operation]
    return dict(bound_seconds=seconds, postwork_reserve_seconds=reserve,
                per_child_cap_seconds=cap, cpu_affinity=[6] if operation.startswith('capture') else [20, 21])


def stage_directory(operation):
    require(operation in POLICIES, 'unknown stage output directory')
    name = {'capture128': 'rank1-capture128', 'capture256': 'rank1-capture256'}.get(operation, operation)
    return BUNDLE / (name + '-001')


def cargo_environment(protocol):
    return dict(CARGO_HOME=protocol['cargo_home'], CARGO_TARGET_DIR=str(BUNDLE / 'cargo-target'),
                CARGO_BUILD_BUILD_DIR=str(BUNDLE / 'cargo-build'), RAYON_NUM_THREADS='1',
                RUST_TEST_THREADS='1', OMP_NUM_THREADS='1', IREGI_PV_PREPARATION_PROFILE='1',
                SYMBOLICA_HIDE_BANNER='1', RUSTC=protocol['tools']['rustc'],
                CC=protocol['tools']['linker'], CXX=protocol['tools']['cxx'], AR=protocol['tools']['ar'])


def command(operation, protocol, budget=None):
    tools = protocol['tools']
    folder = stage_directory(operation)
    prefix = [tools['taskset'], '-c', '20,21']
    if operation == 'cache-seed':
        require(budget is not None, 'cache command needs original absolute work deadline')
        return prefix + [tools['python'], '-B', str(HERE / 'cache_seed.py'),
            str(HERE / 'cache-manifest.json'), str(folder), str(budget.work_deadline)]
    if operation == 'metadata':
        return prefix + [tools['cargo'], 'metadata', '--locked', '--offline', '--manifest-path',
            str(SOURCE / 'Cargo.toml'), '--format-version=1', '--features', 'iregi-rust/native-f64-abc']
    if operation == 'build':
        return prefix + [tools['cargo'], 'build', '--locked', '--offline', '--manifest-path',
            str(SOURCE / 'Cargo.toml'), '-p', 'iregi-rust', '--jobs', '2',
            '--message-format=json-render-diagnostics', '--features', 'native-f64-abc',
            '--example', 'seven_point_public_probe']
    require(operation in ['capture128', 'capture256'], 'not a producer stage')
    return [tools['taskset'], '-c', '6', str(folder / 'frozen-executable'), str(BUNDLE / 'fixture.json'),
        '7', '1', 'pv', operation.removeprefix('capture'), '53', '1', str(folder / 'result.json')]


def terminal(record, operation):
    row = policy(operation)
    require(record['status'] == 'passed' and record['context'] == CONTEXT
            and record['operation'] == operation and record['attempt'] == 1
            and all(record[name] == value for name, value in row.items())
            and record['inputs_unchanged'] is True and record['cleanup_errors'] == []
            and type(record['elapsed_seconds']) in [int, float]
            and math.isfinite(record['elapsed_seconds']) and 0 <= record['elapsed_seconds'] <= row['bound_seconds']
            and not any(record.get(x) for x in ['error', 'cancellation', 'postguard_error',
                'postguard_cancellation', 'finalization_error']), 'prior stage failed or exceeded original bound')
    if operation not in ['source-freeze', 'compare']:
        require(len(record['steps']) == 1 and all(s['status'] == 'exited' and s['returncode'] == 0
                and s['owned_group_gone'] is True and not s.get('timeout') for s in record['steps']),
                'prior owned process did not finish cleanly')


def read_protocol():
    require(Path.cwd().resolve() == ROOT, 'all commands must run from project root')
    p = load(PROTOCOL)
    require(p['schema_version'] == 1 and p['context'] == CONTEXT
            and p['status'] == 'private_positive_Cargo_inputs_frozen_awaiting_independent_review_root_grants'
            and p['stage_policies'] == {name: policy(name) for name in POLICIES}
            and p['fixture_sha256'] == FIXTURE_SHA
            and p['inputs'].get(key(HERE / 'lifecycle.py')) == HELPER_SHA,
            'positive-rank protocol scope/helper differs')
    return p


def stage_context(operation, protocol):
    # The seed receipt admits old cache bytes at the copy boundary. Ordinary
    # shared-cache metadata is not a permanent numerical input thereafter.
    # Actual original native inputs referenced by copied metadata stay guarded.
    def retained(name):
        return (operation == 'cache-seed' or name not in protocol['initial_cache_source_inputs']
                or name in protocol['required_original_native_inputs'])
    bindings = {name: digest for name, digest in protocol['inputs'].items() if retained(name)}
    review_path = HERE / 'source-review.json'
    grant_path = HERE / 'grants' / (operation + '.json')
    review, grant = load(review_path), load(grant_path)
    row = policy(operation)
    require(review['status'] == 'source_review_passed' and review['findings'] == []
            and review['reviewer'] not in [None, '/root/seven_point_api',
                '/root/seven_point_api/seven_lifecycle_audit'], 'independent final source review absent')
    require(grant['status'] == 'root_execution_granted' and grant['grantor'] == '/root'
            and grant['operation'] == operation and grant['attempt'] == 1
            and grant['protocol_sha256'] == review['protocol_sha256']
            and all(grant[name] == value for name, value in row.items())
            and grant['correctness_only'] is True, 'exact root stage/resource grant absent')
    if operation in ['cache-seed', 'metadata', 'build']:
        require(grant['isolated_cache_owner_lease'] is True, 'isolated cache owner lease absent')
    if operation == 'cache-seed':
        require(grant['original_cache_read_copy_lease'] is True, 'original cache read/copy lease absent')
    if operation.startswith('capture'):
        require(grant['numerical_lease'] is True, 'numerical lease absent')
    merge(bindings, key(PROTOCOL), grant['protocol_sha256'])
    merge(bindings, key(review_path), grant['review_sha256'])
    merge(bindings, key(grant_path), sha(grant_path))
    freeze_path = stage_directory('source-freeze') / 'run.json'
    freeze = load(freeze_path)
    terminal(freeze, 'source-freeze')
    merge(bindings, key(freeze_path), protocol['source_freeze_receipt_sha256'])
    require(set(grant['required_receipts']) == set(REQUIRES[operation]), 'wrong prerequisite receipt set')
    closures = []
    for prior in REQUIRES[operation]:
        folder = stage_directory(prior)
        record = load(folder / 'run.json')
        terminal(record, prior)
        merge(bindings, key(folder / 'run.json'), grant['required_receipts'][prior])
        for group in ['inputs', 'artifact_inputs']:
            for name, digest in record.get(group, {}).items():
                if retained(name):
                    merge(bindings, name, digest)
        # Seed files become ordinary mutable build-cache files during Cargo.
        # Guard their byte identity through seed admission, not after Cargo
        # legitimately rebuilds/rebases them. Original seed sources stay bound.
        for name, digest in record['outputs'].items():
            merge(bindings, key(folder / name), digest)
        if prior == 'metadata':
            closure = load(folder / 'metadata-source-freeze.json')
            closures.append(closure)
            for name, digest in closure['inputs'].items():
                merge(bindings, name, digest)
        if prior == 'build':
            closures.append(load(folder / 'cargo-artifacts.json')['artifact_closure'])
    if operation.startswith('capture'):
        spec = grant['required_quad_gate']
        gate = load(spec['path'])
        require(spec['path'] == 'target/quad-iregi-source-audit/future-positive-rank-requests/independent-saved-review.json'
                and spec['sha256'] == 'f0b8f0774d901957fac3369165212b0efac3bf6921cea3c940269f191af373fd'
                and gate['status'] == 'passed_independent_quad_future_reference_raw_and_N7_zero_pole_review'
                and gate['findings'] == []
                and [case for case in gate['cases'] if case['n'] == 7 and case['rank'] == 1]
                    == [dict(id='quad_n7_seventh_time_quarter_rank1', n=7, rank=1,
                        complete_complex_slots=20, maximum_normalized_N7_pole_residual='0',
                        nonzero_raw_uv_slots=0, maximum_raw_uv_magnitude='0')],
                'matching-point full rank1 independent quad gate not admitted')
        merge(bindings, spec['path'], spec['sha256'])
        quad = ROOT / 'target/quad-iregi-source-audit/future-positive-rank-requests'
        for path, digest in [(quad / 'protocol.json', gate['protocol_sha256']),
                             (quad / 'capture-001/run.json', gate['run_sha256']),
                             (quad / 'capture-001/validation.json', gate['validation_sha256']),
                             (quad / 'capture-001/pole-zero-exact.json', gate['pole_gate_sha256'])]:
            merge(bindings, key(path), digest)
    admission = {}
    if operation == 'metadata':
        seeded = load(stage_directory('cache-seed') / 'run.json')
        admission = dict(seeded['seeded_cache_inputs'])
    return bindings, closures, admission


def metadata_document(path):
    documents = []
    for line in Path(path).read_text().splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if isinstance(value, dict) and 'packages' in value and 'resolve' in value:
            documents.append(value)
    require(len(documents) == 1, 'exactly one captured Cargo metadata document required')
    document = documents[0]
    require(document['workspace_root'] == str(SOURCE)
            and document['target_directory'] == str(BUNDLE / 'cargo-target')
            and document['version'] == 1, 'private Cargo workspace/target/schema differs')
    nodes = {entry['id']: entry for entry in document['resolve']['nodes']}
    private = {}
    for name in ['iregi-rust', 'iregi-masters']:
        manifest = str(SOURCE / 'crates' / name / 'Cargo.toml')
        hits = [p for p in document['packages'] if p['manifest_path'] == manifest and p['name'] == name]
        require(len(hits) == 1, 'missing/duplicate exact private package')
        package = hits[0]
        require(package['id'] == 'path+file://' + str(SOURCE / 'crates' / name) + '#0.1.0'
                and package['id'] in document['workspace_members']
                and sorted(nodes[package['id']]['features']) == ['default', 'native-f64-abc'],
                'private package ID/workspace membership/features differ')
        private[name] = package['id']
    dependencies = nodes[private['iregi-rust']]['deps']
    require([d['pkg'] for d in dependencies if d['name'] == 'iregi_masters'] == [private['iregi-masters']],
            'private core does not resolve to private masters')
    return document


def resolved_source_closure(document, protocol, budget):
    files, inventories, configuration = set(), {}, set()
    for package in document['packages']:
        budget.remaining()
        root = Path(package['manifest_path']).parent
        require(root.resolve(strict=True) == root, 'package root has symlink/alias')
        inventory = source_inventory(root, budget)
        inventories[str(root)] = dict(excluded_directory_names=SOURCE_EXCLUSIONS, files=inventory)
        files.update(root / name for name in inventory)
        for ancestor in [root, *root.parents]:
            for suffix in ['Cargo.toml', '.cargo/config', '.cargo/config.toml']:
                configuration.add(ancestor / suffix)
    for root in [ROOT, SOURCE]:
        for ancestor in [root, *root.parents]:
            for suffix in ['Cargo.toml', '.cargo/config', '.cargo/config.toml']:
                configuration.add(ancestor / suffix)
    cargo_home = Path(protocol['cargo_home'])
    configuration.update(cargo_home / name for name in ['config', 'config.toml'])
    configuration.update(SOURCE / name for name in ['Cargo.lock', 'rust-toolchain', 'rust-toolchain.toml'])
    for path in configuration:
        if path.is_file():
            require(path.resolve(strict=True) == path, 'configuration symlink requires explicit mapping')
            files.add(path)
    inputs = {}
    baseline = load(ROOT / 'target/public-seven-point-current-cargo/source-freeze.json')['inputs']
    package_paths = {root / name for root, entry in [(Path(root), value) for root, value in inventories.items()]
                     for name in entry['files']}
    for path in sorted(files):
        digest = sha(path, budget)
        if path in package_paths and not path.is_relative_to(SOURCE):
            require(baseline.get(key(path)) == digest,
                    'external dependency differs from qualified actual-Cargo source freeze: ' + str(path))
        merge(inputs, key(path), digest)
    return dict(status='actual_private_Cargo_resolved_source_closure', inputs=inputs,
        source_directory_inventory=inventories,
        configuration_path_inventory={key(path): path.is_file() for path in sorted(configuration)},
        native_link_closure_qualified=False)


def emitted_artifact_closure(parsed, protocol, budget):
    files, inventories = set(), {}
    allowed = [BUNDLE / 'cargo-target', BUNDLE / 'cargo-build']
    for entry in parsed['compiler_artifacts']:
        for filename in entry['filenames']:
            path = Path(filename)
            require(any(path.is_relative_to(root) for root in allowed)
                    and path.resolve(strict=True) == path, 'Cargo artifact escaped isolated outputs')
            files.add(path)
    for entry in parsed['build_script_executed']:
        event = entry['raw_event']
        out = Path(event['out_dir'])
        require(any(out.is_relative_to(root) for root in allowed), 'build-script OUT_DIR not isolated')
        roots = [out]
        for linked in event.get('linked_paths', []):
            path = Path(linked.split('=', 1)[-1])
            require(path.is_absolute() and path.resolve(strict=True) == path
                    and (any(path.is_relative_to(root) for root in allowed)
                         or path == ROOT / 'target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib'),
                    'unreviewed native link search directory')
            roots.append(path)
        for root in roots:
            inventory = source_inventory(root, budget, [])
            inventories[str(root)] = dict(excluded_directory_names=[], files=inventory)
            files.update(root / name for name in inventory)
    dependency_directory = BUNDLE / 'cargo-build/debug/deps'
    inventory = source_inventory(dependency_directory, budget, [])
    inventories[str(dependency_directory)] = dict(excluded_directory_names=[], files=inventory)
    files.update(dependency_directory / name for name in inventory)
    bindings = {}
    for path in sorted(files):
        merge(bindings, key(path), sha(path, budget))
    return dict(inputs=bindings, source_directory_inventory=inventories,
                configuration_path_inventory={}, native_link_closure_qualified=False)


def parse_build(path, protocol, metadata):
    # Existing source-bound parser supplies all Cargo log/driver semantics;
    # private library products add exact identity/freshness checks below.
    spec = importlib.util.spec_from_file_location('frozen_actual_Cargo_log_parser', ARTIFACT_PARSER)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    core_manifest = str(SOURCE / 'crates/iregi-rust/Cargo.toml')
    master_manifest = str(SOURCE / 'crates/iregi-masters/Cargo.toml')
    packages = {p['manifest_path']: p for p in metadata['packages']}
    core_id, masters_id = packages[core_manifest]['id'], packages[master_manifest]['id']
    parsed = parser.parse_command_log(str(path), {'products': {'driver': {
        'target_name': 'seven_point_public_probe', 'kind': 'example',
        'source_path': str(SOURCE / 'crates/iregi-rust/examples/seven_point_public_probe/main.rs'),
        'features': ['default', 'native-f64-abc']}}}, {'package_id': core_id,
        'cargo_target_directory': str(BUNDLE / 'cargo-target'),
        'cargo_build_directory': str(BUNDLE / 'cargo-build')})
    products = {}
    for name, package_id, manifest, target_name, kind, source in [
        ('core', core_id, core_manifest, 'iregi_rust', 'lib', SOURCE / 'crates/iregi-rust/src/lib.rs'),
        ('masters', masters_id, master_manifest, 'iregi_masters', 'lib', SOURCE / 'crates/iregi-masters/src/lib.rs'),
        ('driver', core_id, core_manifest, 'seven_point_public_probe', 'example',
            SOURCE / 'crates/iregi-rust/examples/seven_point_public_probe/main.rs')]:
        matches = [entry for entry in parsed['compiler_artifacts']
            if entry['package_id'] == package_id and entry['target']['name'] == target_name
            and entry['target']['kind'] == [kind] and entry['target']['src_path'] == str(source)]
        require(len(matches) == 1, 'missing/duplicate private Cargo product: ' + name)
        entry = matches[0]
        event = entry['raw_event']
        require(event['manifest_path'] == manifest and entry['features'] == ['default', 'native-f64-abc']
                and entry['fresh'] is False and entry['profile']['test'] is False
                and entry['profile']['opt_level'] == '0' and entry['profile']['debuginfo'] == 2
                and entry['profile']['debug_assertions'] is True
                and entry['profile']['overflow_checks'] is True, 'private product profile/freshness differs')
        if kind == 'lib':
            require(entry['executable'] is None, 'library unexpectedly executable')
            output = [x for x in entry['filenames'] if x.endswith('.rlib')]
            require(len(output) == 1 and Path(output[0]).is_relative_to(BUNDLE / 'cargo-build'),
                    'private library output outside isolated build directory')
        else:
            require(entry['executable'] in entry['filenames']
                    and Path(entry['executable']).is_relative_to(BUNDLE / 'cargo-target'),
                    'private driver output outside isolated target')
        products[name] = event
    return parsed, products
