#!/usr/bin/env python3
"""Portable saved-evidence replay. Standard library; no native or producer code."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
PROJECT_PREFIX = '/shared/external/iregi/iregi-rust/'
ORIGINAL_SCRIPT = 'target/planar-scalar-independent-saved-review/audit.py'
REFINED_SCRIPT = 'target/planar-scalar-independent-saved-review/audit_refined.py'
ORIGINAL_RECEIPT = 'target/planar-scalar-independent-saved-review/receipt.json'
REFINED_RECEIPT = 'target/planar-scalar-independent-saved-review/refined/receipt.json'
ALLOWED_IMPORTS = {'pathlib', 'fractions', 'collections', 'decimal', 'datetime', 'hashlib', 'json', 'copy'}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique(items):
    result = {}
    for name, value in items:
        require(name not in result, 'duplicate JSON key: ' + name)
        result[name] = value
    return result


def decode(data):
    return json.loads(data, object_pairs_hook=unique,
                      parse_constant=lambda name: (_ for _ in ()).throw(ValueError(name)))


def safe(alias):
    path = PurePosixPath(alias)
    require(isinstance(alias, str) and alias and not path.is_absolute()
            and '..' not in path.parts and str(path) == alias, 'unsafe archive alias')
    return alias


def restore_files(manifest=None):
    """Return exact archived aliases as bytes; never read historical live paths."""
    manifest = decode((HERE / 'manifest.json').read_bytes()) if manifest is None else manifest
    for name, expected in manifest['capsule_files'].items():
        require('/' not in name and name != 'manifest.json', 'unsafe capsule file name')
        data = (HERE / name).read_bytes()
        require(sha(data) == expected['sha256'] and len(data) == expected['bytes'],
                'capsule file mismatch: ' + name)
    origins = decode((HERE / 'origins.json').read_bytes())
    entries = {safe(item['alias']): item for item in origins['members']}
    require(len(entries) == len(origins['members']) == manifest['archived_aliases'], 'origin inventory cardinality')
    files = {}
    with tarfile.open(fileobj=io.BytesIO((HERE / 'payload.tar.gz').read_bytes()), mode='r:gz') as archive:
        for member in archive:
            alias = safe(member.name)
            require(member.isfile() and not member.issym() and not member.islnk(), 'nonregular archive member')
            require(alias in entries and alias not in files, 'unlisted or duplicate archive member')
            data = archive.extractfile(member).read()
            require(sha(data) == entries[alias]['sha256'] and len(data) == entries[alias]['bytes'],
                    'archived bytes mismatch: ' + alias)
            require(not data.startswith(b'\x7fELF') and '__pycache__' not in PurePosixPath(alias).parts,
                    'compiled payload forbidden')
            files[alias] = data
    require(set(files) == set(entries), 'missing archived aliases')
    for item in origins['receipt_small_output_bindings']:
        alias = item['output_alias']
        require(alias in files and sha(files[alias]) == item['sha256'], 'receipt output mismatch: ' + alias)
    for item in origins['captured_source_restore_map']:
        alias = item['snapshot_alias']
        require(alias in files and sha(files[alias]) == item['sha256'], 'source snapshot mismatch')
        safe(item['project_relative_source_path'])
    require(len(origins['captured_source_restore_map']) == manifest['captured_source_files'] == 75,
            'complete captured source context')
    for item in origins['omitted']:
        require(item['sha256'] == manifest['historical_native_artifact_sha256'] and item['bytes'] == 558710824,
                'historical native alias attestation')
    require(len(origins['omitted']) == 31, 'all native aliases explicitly omitted')
    return files


def reconstructed_files(files, origins):
    result = dict(files)
    for item in origins['captured_source_restore_map']:
        alias = item['project_relative_source_path']
        data = files[item['snapshot_alias']]
        require(alias not in result or result[alias] == data, 'source reconstruction collision')
        result[alias] = data
    return result


def write_files(files, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for alias, data in files.items():
        target = destination / safe(alias)
        target.parent.mkdir(parents=True, exist_ok=True)
        require(not target.exists(), 'refuse to overwrite: ' + str(target))
        target.write_bytes(data)


def run_independent_checker(files, temporary, script_alias, receipt_alias, output_name):
    """Execute the unchanged independent saved-only checker with path globals redirected.

    The module entry guard is disabled by __name__; ROOT/DATA/REF/OUT are then
    redirected to the temporary archived tree before its main() runs. No source
    bytes or mathematical functions are patched. Only stdlib imports are allowed.
    """
    source = files[script_alias]
    expected = decode(files[receipt_alias])
    require(sha(source) == expected['checker_sha256'], 'independent checker source pin')
    tree = ast.parse(source, filename=script_alias)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            require(all(name.name in ALLOWED_IMPORTS for name in node.names), 'nonstdlib audit import')
        elif isinstance(node, ast.ImportFrom):
            require(node.level == 0 and node.module in ALLOWED_IMPORTS, 'nonstdlib audit import')
    namespace = {'__name__': 'archived_independent_saved_math', '__file__': str(temporary / script_alias)}
    exec(compile(tree, script_alias, 'exec'), namespace)
    namespace['ROOT'] = temporary
    namespace['DATA'] = temporary / 'target/certified-planar-generalized-scalar-numeric'
    namespace['REF'] = temporary / 'target/certified-planar-generalized-scalar-oracle-refinement'
    namespace['OUT'] = temporary / '_portable_replay' / output_name
    namespace['OUT'].mkdir(parents=True)
    namespace['main']()
    actual = decode((namespace['OUT'] / 'receipt.json').read_bytes())
    keys = ['status', 'checks', 'checker_sha256', 'final_comparison_sha256',
            'raw_Rust_captures', 'raw_independent_oracle_captures', 'oracle_nodes',
            'saved_numeric_decisions_recomputed', 'passed', 'failed', 'failed_categories',
            'failure_details', 'gate_counts', 'maxima_normalized',
            'all1592_nonoracle_gates_passed', 'negative_controls_rejected',
            'source_and_raw_bindings', 'public_generalized_or_full_goal_qualified',
            'rigorous_error_or_performance_qualified', 'compiler_evaluator_integral_or_process_probe_run',
            'producer_modules_imported']
    for key in keys:
        require(actual[key] == expected[key], 'independent replay differs: ' + output_name + '/' + key)
    return {'decisions': actual['saved_numeric_decisions_recomputed'], 'passed': actual['passed'],
            'failed': actual['failed'], 'checks': actual['checks'],
            'negative_controls': len(actual['negative_controls_rejected'])}


def replay(files):
    """Recompute all original and refined decisions from raw saved numeric arrays."""
    origins = decode((HERE / 'origins.json').read_bytes())
    with tempfile.TemporaryDirectory(prefix='.saved-replay-', dir=HERE) as directory:
        temporary = Path(directory)
        write_files(files, temporary)
        original = run_independent_checker(files, temporary, ORIGINAL_SCRIPT, ORIGINAL_RECEIPT, 'original')
        refined = run_independent_checker(files, temporary, REFINED_SCRIPT, REFINED_RECEIPT, 'refined')
    require((original['passed'], original['failed']) == (2040, 24), 'original failed refinement retained')
    require((refined['passed'], refined['failed']) == (2064, 0), 'refined complete qualification')
    final_alias = 'target/certified-planar-generalized-scalar-oracle-refinement/qualification-after-independent.json'
    final = decode(files[final_alias])
    require(final['new_independent_refined_review_completed'] is True
            and final['independent_refined_review']['sha256'] == sha(files[REFINED_RECEIPT]), 'final qualification audit pin')
    require(final['qualifying_Rust_complex_native_components'] == 880
            and final['qualifying_successful_Rust_sample_rows'] == 196
            and final['explicit_invalid_Rust_sample_rows'] == 26, 'complete native values and null failures')
    for key in ['signed_zero_preservation_qualified', 'rigorous_quadrature_enclosure',
                'all_generalized_rank7_or_numeric_domains_qualified', 'genuine_full_rank_D6_pentagon_qualified',
                'current_mutable_main_binary_claimed', 'physical_graph_or_MadLoop_validation', 'performance_qualified']:
        require(final[key] is False, 'scope improperly promoted: ' + key)
    return {'status': 'passed_portable_saved_math_and_source_reconstruction', 'archived_aliases': len(files),
            'captured_source_files': len(origins['captured_source_restore_map']),
            'original_inconclusive_cohort': original, 'refined_qualifying_cohort': refined,
            'historical_omitted_native_aliases': len(origins['omitted']),
            'new_native_compiler_integral_or_PID_work': False,
            'fresh_external_tool_or_native_hash_verification': False,
            'full_generalized_domain_or_performance_qualified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reconstruct', type=Path, help='write archived evidence and the75source context into a new empty directory')
    args = parser.parse_args()
    manifest = decode((HERE / 'manifest.json').read_bytes())
    files = restore_files(manifest)
    summary = replay(files)
    if args.reconstruct is not None:
        destination = args.reconstruct.resolve()
        require(not destination.exists() or (destination.is_dir() and not any(destination.iterdir())), 'reconstruction destination must be empty')
        restored = reconstructed_files(files, decode((HERE / 'origins.json').read_bytes()))
        write_files(restored, destination)
        summary['reconstructed_files'] = len(restored)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
