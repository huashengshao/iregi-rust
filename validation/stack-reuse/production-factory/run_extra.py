from pathlib import Path
import hashlib, json, os, re, signal, subprocess, sys, time
root = Path.cwd()
base = root / 'target/stack-reuse-production'
variant, stage, filter_text, limit = sys.argv[1:]
assert variant in ['baseline', 'candidate']
assert stage in ['core_tests', 'master_tests', 'e6', 'master_integration', 'e6_capture']
folder = base / variant
binary = folder / ('shifted_pentagon' if stage == 'e6' else stage)
name = f'{stage}-{filter_text.replace("::", "_") or "all"}'
args = [str(binary), filter_text, '--nocapture', '--test-threads=1']
env = os.environ.copy()
env['RUST_TEST_THREADS'] = '1'
start = time.monotonic()
status = None
expired = False
usage = None

def interrupted(signum, frame):
    raise SystemExit(128 + signum)

signal.signal(signal.SIGTERM, interrupted)
with (folder / f'{name}.log').open('w') as log:
    child = subprocess.Popen(args, cwd=root, env=env, stdout=log,
                             stderr=subprocess.STDOUT, start_new_session=True)
    try:
        while True:
            pid, wait_status, usage = os.wait4(child.pid, os.WNOHANG)
            if pid:
                status = os.waitstatus_to_exitcode(wait_status)
                child.returncode = status
                break
            if time.monotonic() - start >= float(limit):
                expired = True
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                _, wait_status, usage = os.wait4(child.pid, 0)
                status = os.waitstatus_to_exitcode(wait_status)
                child.returncode = status
                break
            time.sleep(0.05)
    finally:
        if child.returncode is None:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            _, wait_status, usage = os.wait4(child.pid, 0)
            child.returncode = os.waitstatus_to_exitcode(wait_status)
log_text = (folder / f'{name}.log').read_text()
match = re.search(r'test result: (?:ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored;', log_text)
counts = None if match is None else dict(zip(['passed', 'failed', 'ignored'], map(int, match.groups())))
selected = counts is not None and counts['passed'] + counts['failed'] > 0
report = {
    'variant': variant, 'stage': stage, 'filter': filter_text, 'command': args,
    'timeout_seconds': float(limit), 'exit_code': status, 'timed_out': expired,
    'elapsed_seconds': time.monotonic() - start,
    'max_rss_kib': usage.ru_maxrss, 'user_seconds': usage.ru_utime,
    'system_seconds': usage.ru_stime, 'test_counts': counts,
    'nonempty_test_selection': selected,
    'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
    'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'resource_accounting': 'per-child os.wait4; excludes earlier shell children',
    'diagnostic_only': True,
    'performance_gate': 'Not a controlled statistical benchmark; elapsed time and peak RSS are diagnostic observations.'
}
(folder / f'{name}.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report), flush=True)
if expired or status or not selected:
    print(log_text[-12000:], flush=True)
sys.exit(124 if expired else (status or (0 if selected else 2)))
