"""Saved-only adapters preserving the actual failed128/256 precision boundary.

All arithmetic remains
in the pinned e0/a82/df350 programs; this file provides saved-byte I/O and report
identity checks. The read-only I/O pattern is reused from the already replayed
validation/affine-power-generalized-current-d6-rank6/check.py saved_filesystem.
"""
from pathlib import Path
from contextlib import contextmanager, redirect_stdout
import builtins
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import tempfile

sys.dont_write_bytecode = True
PREFIX = '/shared/external/iregi/iregi-rust/'
COMPARATOR = 'target/n6-sample-d6-mass-second-anchor-dd/compare_saved_parents.py'
COMPARATOR_SHA = 'df3504e3c21e2bd5b0d5fa67a9877aa9103bf1942bf5d10e8ae6f458fd354115'
SINGLE = 'target/n6-sample-d6-mass-second-anchor-dd/compare_saved_precision.py'
SINGLE_SHA = 'a82bdfa56762dee1002f8504bad38d75a806b45ac920aa230d105609761e1963'
MECHANISM_SHA = 'e0b6889dfed8101579477f584dd52a26e0d484454f753be02ff10d9654e198e0'
DDROOT = 'target/n6-sample-d6-mass-second-anchor-dd'
DD_REPLAY = DDROOT + '/independent-stream-replay-001.json'
DD_REPLAY_SHA = '461859d575417ca26d8bd755dd81f47448c685a20ae8de4b3dfedc193fd8903a'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def read_json(body):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate report JSON key')
            result[key] = value
        return result
    def bad(value):
        raise ValueError('nonfinite report JSON token ' + value)
    return json.loads(body, object_pairs_hook=pairs, parse_constant=bad)


@contextmanager
def saved_filesystem(files, source_aliases=None):
    """Read actual saved bytes at original names; unknown project paths fail."""
    source_aliases = source_aliases or {}
    missing = object()
    names = ['open', 'cwd', 'resolve', 'exists', 'stat']
    owned = {name: Path.__dict__.get(name, missing) for name in names}
    previous = {name: getattr(Path, name) for name in names}
    old_loader = importlib.machinery.SourceFileLoader.get_data
    old_builtin = builtins.open

    def virtual(path):
        value = str(path)
        if value.startswith(PREFIX):
            alias = value[len(PREFIX):]
            alias = source_aliases.get(alias, alias)
            if alias not in files:
                raise FileNotFoundError('unsaved project path: ' + alias)
            return files[alias]
        return None

    def vopen(path, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        body = virtual(path)
        if body is None:
            return previous['open'](path, mode, buffering, encoding, errors, newline)
        need(mode in ['r', 'rt', 'rb'], 'saved project is read-only')
        stream = io.BytesIO(body)
        return stream if 'b' in mode else io.TextIOWrapper(stream, encoding=encoding or 'utf-8',
                                                          errors=errors or 'strict', newline=newline)

    def vresolve(path, strict=False):
        value = str(path)
        return path if value == PREFIX.rstrip('/') or value.startswith(PREFIX) else previous['resolve'](path, strict=strict)

    def vexists(path, **kwargs):
        value = str(path)
        return value[len(PREFIX):] in files if value.startswith(PREFIX) else previous['exists'](path, **kwargs)

    def vstat(path, *, follow_symlinks=True):
        body = virtual(path)
        return previous['stat'](path, follow_symlinks=follow_symlinks) if body is None else os.stat_result(
            (0o100644, 0, 0, 1, 0, 0, len(body), 0, 0, 0))

    def get_data(loader, path):
        body = virtual(path)
        return old_loader(loader, path) if body is None else body

    def builtin_open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None,
                     closefd=True, opener=None):
        if not isinstance(file, int) and str(file).startswith(PREFIX):
            return vopen(Path(file), mode, buffering, encoding, errors, newline)
        return old_builtin(file, mode, buffering, encoding, errors, newline, closefd, opener)

    Path.open = vopen
    Path.cwd = classmethod(lambda cls: cls(PREFIX.rstrip('/')))
    Path.resolve = vresolve
    Path.exists = vexists
    Path.stat = vstat
    importlib.machinery.SourceFileLoader.get_data = get_data
    builtins.open = builtin_open
    try:
        yield
    finally:
        for name, value in owned.items():
            if value is missing:
                delattr(Path, name)
            else:
                setattr(Path, name, value)
        importlib.machinery.SourceFileLoader.get_data = old_loader
        builtins.open = old_builtin


def _run_frozen_main(files, source_alias, source_sha, arguments, expected_exit=0, source_aliases=None):
    """Run saved-only program unchanged, writing only a fresh temporary report."""
    need(sha(files[source_alias]) == source_sha, 'unchanged saved-only program identity')
    original_argv = sys.argv
    module_name = '_capsule_saved_main_' + source_sha
    previous_module = sys.modules.get(module_name)
    try:
        with tempfile.TemporaryDirectory(prefix='tirust-terminal-saved-report-') as temp:
            output = Path(temp) / 'report.json'
            with saved_filesystem(files, source_aliases), redirect_stdout(io.StringIO()):
                spec = importlib.util.spec_from_file_location(module_name, PREFIX + source_alias)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                sys.argv = [PREFIX + source_alias] + list(arguments) + ['--output', str(output)]
                code = module.main()
            need(code == expected_exit, 'frozen saved-only program preserved its expected exit outcome')
            return read_json(output.read_bytes())
    finally:
        sys.argv = original_argv
        if previous_module is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous_module


def _check_report_inputs(report, files):
    for absolute, digest in report.get('inputs', {}).items():
        need(absolute.startswith(PREFIX), 'original saved report input key')
        alias = absolute[len(PREFIX):]
        need(alias in files and sha(files[alias]) == digest, 'actual saved report input bytes')


def _terminal_case(case, bits, files, expected_build, expected_product):
    receipt = read_json(files[case['receipt_alias']])
    protocol = read_json(files[case['protocol_alias']])
    need(receipt['working_bits'] == bits and receipt['requested_bits'] == 53
         and receipt['inputs_unchanged'] is True and receipt['cleanup_errors'] == [],
         'actual terminal unchanged precision/lifecycle evidence')
    need(len(receipt['steps']) == 1 and receipt['steps'][0]['status'] == 'exited'
         and receipt['steps'][0]['returncode'] == 0 and receipt['steps'][0]['owned_group_gone'] is True,
         'actual complete producer, not a partial snapshot')
    need(protocol['binary']['sha256'] == expected_product
         and protocol['source_context']['build_receipt_sha256'] == expected_build
         and protocol['source_context']['count'] == 210,
         'same actual current-source210 and frozen product')
    return receipt


def replay_boundary_math(collection, files):
    """Reproduce complete successes and the unchanged FAILED strict pair."""
    a, b = collection['complete128'], collection['complete256']
    for case in (a, b):
        need(case['accepted_by_owner_and_root'] is True, 'accepted complete terminal handoff')
    build = collection['actual_current_build_receipt_alias']
    build_sha = sha(files[build])
    product = read_json(files[build])['products']['tests']['sha256']
    for case, bits in [(a, 128), (b, 256)]:
        _terminal_case(case, bits, files, build_sha, product)
    need(sha(files[COMPARATOR]) == COMPARATOR_SHA and sha(files[SINGLE]) == SINGLE_SHA,
         'unchanged existing mathematical programs')
    need(sha(files[DD_REPLAY]) == DD_REPLAY_SHA, 'archived independent DD stream proof, no stream rerun')
    for case, bits in [(a, 128), (b, 256)]:
        mechanism = _run_frozen_main(files, case['checker_source_alias'], MECHANISM_SHA,
                                     ['--capture', PREFIX + case['capture_alias']])
        need(mechanism == read_json(files[case['mechanism_alias']]),
             'entire frozen full mechanism report exactly reproduced')
        _check_report_inputs(mechanism, files)
        numerical = _run_frozen_main(files, SINGLE, SINGLE_SHA,
                                     ['--bits', str(bits), '--capture', PREFIX + case['capture_alias'],
                                      '--audit', PREFIX + case['mechanism_alias'],
                                      '--dd-directory', PREFIX + DDROOT + '/numeric-001/data'])
        need(numerical == read_json(files[case['numeric_alias']]),
             'entire frozen single-precision report exactly reproduced')
        _check_report_inputs(numerical, files)
    joint = _run_frozen_main(files, COMPARATOR, COMPARATOR_SHA,
                              ['--pv128', PREFIX + a['capture_alias'], '--pv256', PREFIX + b['capture_alias'],
                               '--audit128', PREFIX + a['mechanism_alias'], '--audit256', PREFIX + b['mechanism_alias'],
                               '--dd-directory', PREFIX + DDROOT + '/numeric-001/data'], expected_exit=1)
    need(joint == read_json(files[collection['failed_pair']['report_alias']]),
         'entire original failed six-comparison report exactly reproduced')
    _check_report_inputs(joint, files)
    need(joint['status'] == 'failed_or_incomplete_saved_parent_comparison'
         and joint['all_parent_numeric_gates_passed'] is False and joint['findings'] == []
         and joint['comparison_count'] == 6 and len(joint['UV_IR_controls']) == 4,
         'complete failed numerical boundary, without incomplete data')
    need(all(row['failures'] == 0 for row in joint['comparisons'][:5] + joint['UV_IR_controls'])
         and joint['comparisons'][5]['dataset'] == 'PV128_vs_PV256'
         and joint['comparisons'][5]['threshold'] == str(__import__('fractions').Fraction(1, 2**80))
         and joint['comparisons'][5]['failures'] == 628,
         'four core/DD and rule-pair passes; strict2^-80 remains628 failures')
    hook = collection['independent_full_pair']
    independent = _run_frozen_main(files, hook['source_alias'], hook['source_sha256'],
        ['--lower-capture', PREFIX+a['capture_alias'], '--higher-capture', PREFIX+b['capture_alias'],
         '--lower-receipt', PREFIX+a['receipt_alias'], '--higher-receipt', PREFIX+b['receipt_alias'],
         '--lower-audit', PREFIX+a['mechanism_alias'], '--higher-audit', PREFIX+b['mechanism_alias'],
         '--dd-estimates', PREFIX+DDROOT+'/numeric-001/data/estimates.json',
         '--dd-ready', PREFIX+DDROOT+'/numeric-001/data/ready.json',
         '--numeric-report', PREFIX+collection['failed_pair']['report_alias'],
         '--lower-bits', '128', '--higher-bits', '256'], expected_exit=1)
    saved = read_json(files[hook['report_alias']])
    need(independent['status'] == saved['status'] == 'completed_independent_complete_pair_review'
         and independent['findings'] == saved['findings'] == []
         and independent['precision_pair_qualified'] is saved['precision_pair_qualified'] is False,
         'independent reviewer completed and preserved actual numerical failure')
    # Only historical live-file rehash observations differ in portable mode;
    # all arithmetic, layout, contexts, source SHA and all input hashes are exact.
    for replay_row, historical, count in zip(independent['terminal_provenance'], saved['terminal_provenance'], (237,248)):
        need(replay_row['terminal_input_files_independently_rehashed'] == 0
             and replay_row['verify_live_terminal_files_requested'] is False,
             'portable independent reviewer omits actual native rehash')
        need(historical['terminal_input_files_independently_rehashed'] == count
             and historical['verify_live_terminal_files_requested'] is True,
             'historical independent live-file observations preserved')
        replay_row['terminal_input_files_independently_rehashed'] = historical['terminal_input_files_independently_rehashed']
        replay_row['verify_live_terminal_files_requested'] = historical['verify_live_terminal_files_requested']
    need(independent == saved, 'entire independent review reproduced except two explicitly scoped historical guard observations')
    diagnosis = collection['diagnosis']
    need(sha(files[diagnosis['source_alias']]) == diagnosis['source_sha256'], 'unchanged source-only diagnosis helper')
    module_name = '_capsule_saved_diagnosis'
    old = sys.modules.get(module_name)
    try:
        with saved_filesystem(files, collection['source_read_aliases']), redirect_stdout(io.StringIO()):
            spec = importlib.util.spec_from_file_location(module_name, PREFIX+diagnosis['source_alias'])
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            with module.localcontext() as context:
                context.prec = 120
                result = module.analyze(Path(PREFIX.rstrip('/')))
        need(result == read_json(files[diagnosis['report_alias']]), 'entire deterministic heuristic diagnosis reproduced')
    finally:
        if old is None: sys.modules.pop(module_name, None)
        else: sys.modules[module_name] = old
    return {'status':'passed_saved_replay_preserving_actual_failed_precision_boundary',
        'mechanism_reports_exactly_reproduced':2, 'single_precision_reports_exactly_reproduced':2,
        'failed_joint_report_exactly_reproduced':True, 'independent_review_reproduced':True,
        'independent_portable_rehash_observations_normalized_per_precision':
            ['terminal_input_files_independently_rehashed','verify_live_terminal_files_requested'],
        'heuristic_diagnosis_exactly_reproduced':True, 'joint_comparisons':6,
        'complex_fields_per_comparison':2520, 'strict_precision_failures':628,
        'strict_precision_threshold':'2^-80', 'strict_precision_pair_qualified':False,
        'raw_UV_IR_datasets':4, 'raw_controls_per_dataset':1806,
        'DD_stream_reexecuted':False, 'archived_DD_stream_proof_sha256':DD_REPLAY_SHA,
        'native_artifact_rehash':False, 'native_execution':False, 'new_integral_evaluation':False,
        'rigorous_error_bound':False, 'achieved_precision_bits_claimed':False,
        'default_Hybrid_qualified':False, 'full_objective_met':False, 'performance_qualified':False}
