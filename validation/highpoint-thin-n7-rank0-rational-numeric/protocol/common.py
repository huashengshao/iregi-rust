"""Frozen-source qualification helpers; importing this module executes no work."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import signal
import subprocess
import time

ROOT = Path('/shared/external/iregi/iregi-rust')
BUNDLE = ROOT / 'target/public-highpoint/thin-n7-rank0-rational-numeric'
PROTOCOL = BUNDLE / 'protocol/protocol.json'
_interruption = None


class QualificationInterrupted(BaseException):
    pass


def install_signal_handlers():
    def interrupted(signum, _frame):
        # Record only: asynchronous exceptions must not interrupt Popen or the
        # kill/reap sequence. Bounded wait polling notices this within250ms.
        global _interruption
        if _interruption is None:
            _interruption = f'interrupted by signal {signum}'
    for kind in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(kind, interrupted)


def check_interruption():
    if _interruption is not None:
        raise QualificationInterrupted(_interruption)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, record):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(record, indent=2) + '\n')
    temporary.replace(path)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def load_protocol():
    assert Path.cwd().resolve() == ROOT
    protocol = json.loads(PROTOCOL.read_text())
    assert protocol['status'] == 'source_only_frozen_awaiting_root_execution_grant'
    assert protocol['stages'] == ['build_driver', 'capture128', 'capture256', 'compare']
    return protocol


def bindings(protocol, stage):
    files = {ROOT / path: digest for path, digest in protocol['inputs'].items()}
    files[PROTOCOL] = sha(PROTOCOL)
    review = BUNDLE / 'protocol/independent-review.json'
    approval = BUNDLE / 'protocol/grants' / f'{stage}.json'
    # These receipts are created only after source review and an explicit ROOT
    # execution grant. They are evidence, not a user-facing approval mechanism.
    reviewed = json.loads(review.read_text())
    granted = json.loads(approval.read_text())
    assert reviewed['status'] == 'source_review_passed'
    assert reviewed['protocol_sha256'] == sha(PROTOCOL)
    assert granted['status'] == 'root_execution_granted'
    assert granted['protocol_sha256'] == sha(PROTOCOL)
    assert granted['review_sha256'] == sha(review)
    assert stage in protocol['stages'] and granted['stages'] == [stage]
    assert set(granted['stages']).issubset(protocol['stages'])
    files[review] = sha(review)
    files[approval] = sha(approval)
    return files


def verify(files, protocol):
    for path, digest in files.items():
        check_interruption()
        assert sha(path) == digest, f'changed input: {path}'
    # Rust dependency/native lookup must not discover an unbound extra archive.
    for relative in protocol['closed_search_directories']:
        folder = ROOT / relative
        actual = {path for path in folder.iterdir() if path.is_file()}
        expected = {path for path in files if path.parent == folder}
        assert actual == expected, f'unbound dependency search contents: {relative}'


def execute(command, log_path, seconds, env, input_path=None):
    """Own a process group, reserve cleanup time, and return terminal metadata."""
    started = time.monotonic()
    result = {'command': command, 'bound_seconds': seconds, 'started_utc': utc(),
              'exit_code': None, 'timeout': False, 'cleanup_errors': []}
    child = None
    stdin = None
    try:
        assert seconds > 2, 'stage budget exhausted before spawn'
        if input_path is not None:
            stdin = Path(input_path).open('r')
        with Path(log_path).open('w') as log:
            child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log,
                                     stderr=subprocess.STDOUT, stdin=stdin, start_new_session=True)
            result['pid'] = child.pid
            deadline = started + seconds - 2
            while True:
                check_interruption()
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    result['timeout'] = True
                    break
                try:
                    result['exit_code'] = child.wait(timeout=min(0.25, remaining))
                    break
                except subprocess.TimeoutExpired:
                    continue
    except BaseException as error:
        result['error'] = f'{type(error).__name__}: {error}'
        result['interrupted'] = isinstance(error, (QualificationInterrupted, KeyboardInterrupt, SystemExit))
    finally:
        if stdin is not None:
            stdin.close()
        # Preserve observed exit/timeout before process-group cleanup or hashes.
        result['observed_terminal_utc'] = utc()
        terminal_path = Path(log_path).with_suffix('.terminal.json')
        try:
            save(terminal_path, result)
        except BaseException as error:
            result['terminal_save_error'] = f'{type(error).__name__}: {error}'
            result['cleanup_errors'].append(result['terminal_save_error'])
        if child is not None:
            # Also close descendants if the direct child exited unexpectedly.
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            except OSError as error:
                result['cleanup_errors'].append(str(error))
            try:
                child.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                pass
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except OSError as error:
                result['cleanup_errors'].append(str(error))
            try:
                result['exit_code'] = child.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                result['cleanup_errors'].append('direct child did not reap after SIGKILL')
        result['elapsed_seconds'] = time.monotonic() - started
        result['finished_utc'] = utc()
        if _interruption is not None:
            result.update(interrupted=True, error=f'QualificationInterrupted: {_interruption}')
        result['within_bound'] = result['elapsed_seconds'] <= seconds
        result['passed'] = (result['exit_code'] == 0 and not result['timeout']
                            and not result['cleanup_errors'] and 'error' not in result
                            and result['within_bound'])
    return result


def finish(record, path, files, protocol, start):
    # Always save the terminal result before risky hashing/provenance checks.
    record.update(finished_utc=utc(), elapsed_seconds=time.monotonic() - start)
    save(path, record)
    try:
        record['retained_log_hashes'] = {log.name: sha(log) for log in sorted(Path(path).parent.glob('*.log'))}
    except BaseException as error:
        record.update(status='failed', log_hash_error=f'{type(error).__name__}: {error}')
    try:
        verify(files, protocol)
        record['inputs_unchanged'] = True
    except BaseException as error:
        record.update(status='failed', inputs_unchanged=False,
                      post_guard_error=f'{type(error).__name__}: {error}')
    record['elapsed_seconds_including_postguards'] = time.monotonic() - start
    if record['elapsed_seconds_including_postguards'] > record['bound_seconds']:
        record.update(status='failed', total_bound_exceeded=True)
    save(path, record)

