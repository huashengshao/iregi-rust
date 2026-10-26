"""Parametric final saved adapters; execution requires accepted complete384 handoff.

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
    old_open_code = io.open_code

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
    io.open_code = lambda path: (io.BytesIO(virtual(path)) if str(path).startswith(PREFIX) else old_open_code(path))
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
        io.open_code = old_open_code


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


MECHANISM384_SHA = 'dc6905601b9b60edbd97abe89efd091c57cd452c6986d6e7379f4139ccf67e56'
SINGLE384 = 'target/n6-sample-d6-mass-second-anchor-dd/compare_saved_precision_384.py'
SINGLE384_SHA = '783e26b4ab27b3702d4b3e5e2d47c9a868aa3f1122e2554c192098b566cae2ec'
PAIR = 'target/e6-dual-restored-precision-extension/compare_saved_pair256_384.py'
PAIR_SHA = '9eb24f13702a6e8e32e25c10971a95024ba44352f0dd45a6743ebaebea731be7'
INDEPENDENT = 'target/rank6-independent-complete-pair-review.py'
INDEPENDENT_SHA = 'a6e79be973f31ff0e47978d333c74996470392c66db453343e9625d1a9317e1b'
HISTORY = 'target/rank6-independent256384-history-wrapper.py'
HISTORY_SHA = '4ff7a7f01c8f3200f3c507a1bd35cea17489d67ea6e265e62bcc90fa5fa03a23'
FAILED_SHA = '2472628367171ba81589e18c949a3e2681489d76d2395693a7c23610b1be0b7a'


def _history_main(files, arguments):
    """Execute frozen wrapper and frozen base through saved bytes, no live guard flag."""
    need(sha(files[HISTORY]) == HISTORY_SHA and sha(files[INDEPENDENT]) == INDEPENDENT_SHA,
         'exact unchanged independent wrapper and base reviewer')
    previous_argv = sys.argv
    name = '_final_saved_history_wrapper'
    previous_module = sys.modules.get(name)
    try:
        with tempfile.TemporaryDirectory(prefix='tirust-final-saved-history-') as temporary:
            base_output = Path(temporary)/'base.json'
            history_output = Path(temporary)/'history.json'
            with saved_filesystem(files), redirect_stdout(io.StringIO()):
                spec = importlib.util.spec_from_file_location(name, PREFIX+HISTORY)
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                sys.argv = [PREFIX+HISTORY, '--base-reviewer', PREFIX+INDEPENDENT,
                    '--producer-pair-source', PREFIX+PAIR,
                    '--failed-128256-report', PREFIX+arguments['failed_alias'],
                    '--history-review-output', str(history_output)] + arguments['forwarded'] + ['--output', str(base_output)]
                code = module.main()
            need(code == 0, 'actual complete independent higher-precision convergence/history must pass')
            body = base_output.read_bytes()
            return read_json(body), sha(body), read_json(history_output.read_bytes())
    finally:
        sys.argv = previous_argv
        if previous_module is None: sys.modules.pop(name, None)
        else: sys.modules[name] = previous_module


def replay_final_math(manifest, files):
    """Only actual accepted full384/strict256384 can enter any mathematics."""
    higher = manifest.get('actual384')
    pair = manifest.get('qualifying256384_pair')
    independent = manifest.get('independent256384')
    need(type(higher) is dict and higher.get('accepted_by_owner_and_root') is True,
         'external actual terminal384 handoff required; absent means no execution')
    need(type(pair) is dict and pair.get('accepted_by_owner_and_root') is True,
         'external accepted strict256384 report required')
    need(type(independent) is dict and independent.get('accepted_by_owner_and_root') is True,
         'external actual independent complete/history reports required')
    lower = manifest['inherited_complete256']
    build_alias = manifest['actual_current_build_receipt_alias']
    build_sha = sha(files[build_alias])
    product = read_json(files[build_alias])['products']['tests']['sha256']
    for case, bits in [(lower,256),(higher,384)]:
        _terminal_case(case,bits,files,build_sha,product)
    need(sha(files[COMPARATOR]) == COMPARATOR_SHA and sha(files[DD_REPLAY]) == DD_REPLAY_SHA,
         'unchanged mathematical functions and inherited independent DD stream proof')
    failed_alias = manifest['preserved_failed128256']['report_alias']
    need(sha(files[failed_alias]) == FAILED_SHA, 'actual old complete failed comparison preserved byte-exact')
    old = read_json(files[failed_alias])
    need(old['all_parent_numeric_gates_passed'] is False and old['comparisons'][5]['failures'] == 628,
         'historical128256 remains failed rather than relabelled')
    mechanism = _run_frozen_main(files,higher['checker_source_alias'],MECHANISM384_SHA,
        ['--capture',PREFIX+higher['capture_alias']])
    need(mechanism == read_json(files[higher['mechanism_alias']]), 'entire frozen full384 mechanism report exact')
    _check_report_inputs(mechanism,files)
    numeric = _run_frozen_main(files,SINGLE384,SINGLE384_SHA,
        ['--bits','384','--capture',PREFIX+higher['capture_alias'],'--audit',PREFIX+higher['mechanism_alias'],
         '--dd-directory',PREFIX+DDROOT+'/numeric-001/data'])
    need(numeric == read_json(files[higher['numeric_alias']]), 'entire frozen384 two-DD report exact')
    _check_report_inputs(numeric,files)
    joint = _run_frozen_main(files,PAIR,PAIR_SHA,
        ['--pv256',PREFIX+lower['capture_alias'],'--pv384',PREFIX+higher['capture_alias'],
         '--audit256',PREFIX+lower['mechanism_alias'],'--audit384',PREFIX+higher['mechanism_alias'],
         '--receipt256',PREFIX+lower['receipt_alias'],'--receipt384',PREFIX+higher['receipt_alias'],
         '--dd-directory',PREFIX+DDROOT+'/numeric-001/data','--failed128256',PREFIX+failed_alias])
    need(joint == read_json(files[pair['report_alias']]), 'entire actual256384 joint report exactly reproduced')
    _check_report_inputs(joint,files)
    need(joint['status'] == 'passed_all2520_parent_gates_pending_independent_stream_replay'
         and joint['all_parent_numeric_gates_passed'] is True and joint['findings'] == []
         and joint['comparison_count'] == 6 and len(joint['UV_IR_controls']) == 4
         and all(row['failures'] == 0 for row in joint['comparisons']+joint['UV_IR_controls'])
         and joint['comparisons'][5]['dataset'] == 'PV256_vs_PV384'
         and joint['comparisons'][5]['threshold'] == str(__import__('fractions').Fraction(1,2**80)),
         'all complete higher-precision comparisons/raw controls at unchanged thresholds')
    arguments = {'failed_alias':failed_alias,'forwarded':[
        '--lower-bits','256','--higher-bits','384',
        '--lower-capture',PREFIX+lower['capture_alias'],'--higher-capture',PREFIX+higher['capture_alias'],
        '--lower-receipt',PREFIX+lower['receipt_alias'],'--higher-receipt',PREFIX+higher['receipt_alias'],
        '--lower-audit',PREFIX+lower['mechanism_alias'],'--higher-audit',PREFIX+higher['mechanism_alias'],
        '--dd-estimates',PREFIX+DDROOT+'/numeric-001/data/estimates.json',
        '--dd-ready',PREFIX+DDROOT+'/numeric-001/data/ready.json','--numeric-report',PREFIX+pair['report_alias']]}
    replay_base,replay_base_sha,replay_history = _history_main(files,arguments)
    saved_base = read_json(files[independent['base_report_alias']])
    saved_history = read_json(files[independent['history_report_alias']])
    need(replay_base['status'] == saved_base['status'] == 'completed_independent_complete_pair_review'
         and replay_base['all_parent_numeric_gates_passed'] is saved_base['all_parent_numeric_gates_passed'] is True
         and replay_base['precision_pair_qualified'] is saved_base['precision_pair_qualified'] is True
         and replay_base['findings'] == saved_base['findings'] == [], 'actual independent arithmetic convergence passes')
    # Historical live guard observations stay archived; portable execution never
    # claims to rehash omitted native artifacts. No mathematical field differs.
    for replay_row,historical,case in zip(replay_base['terminal_provenance'],saved_base['terminal_provenance'],(lower,higher)):
        need(replay_row['terminal_input_files_independently_rehashed'] == 0
             and replay_row['verify_live_terminal_files_requested'] is False, 'no portable native guard rehash')
        live = historical['verify_live_terminal_files_requested']
        need(type(live) is bool and historical['terminal_input_files_independently_rehashed'] ==
             (len(read_json(files[case['receipt_alias']])['inputs']) if live else 0), 'actual historical independent guard count')
        for key in ('terminal_input_files_independently_rehashed','verify_live_terminal_files_requested'):
            replay_row[key] = historical[key]
    need(replay_base == saved_base, 'independent base exact except explicitly checked historical live guard observations')
    need(replay_history['status'] == saved_history['status'] == 'passed_saved_history_supplement'
         and replay_history['findings'] == saved_history['findings'] == []
         and replay_history['base_math_receipt_sha256'] == replay_base_sha
         and saved_history['base_math_receipt_sha256'] == sha(files[independent['base_report_alias']]),
         'history supplement binds its actual base report bytes')
    replay_history['base_math_receipt_sha256'] = saved_history['base_math_receipt_sha256']
    need(replay_history == saved_history, 'history supplement exact except derived portable/live base-receipt metadata digest')
    return {'status':'passed_final_saved384_and_strict256384_replay',
        'new_complete384_mechanism_reproduced':True,'new_complete384_two_DD_report_reproduced':True,
        'new_complete256384_joint_report_reproduced':True,'independent_base_and_history_reports_reproduced':True,
        'joint_complete_comparisons':6,'complex_fields_per_comparison':2520,'raw_controls_per_dataset':1806,
        'raw_control_datasets':4,'strict_precision_threshold':'2^-80','strict256384_qualified':True,
        'historical128256_strict_failures_preserved':628,'historical128256_failure_relabelled':False,
        'portable_historical_guard_metadata_only_normalized':True,'DD_stream_reexecuted':False,
        'archived_DD_stream_proof_sha256':DD_REPLAY_SHA,'native_execution':False,'native_artifact_rehash':False,
        'new_integral_evaluation':False,'default_Hybrid_qualified':False,'performance_qualified':False,
        'rigorous_error_bound':False,'achieved_precision_bits_claimed':False,'full_objective_met':False}
