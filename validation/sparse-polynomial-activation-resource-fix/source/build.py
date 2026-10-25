"""One finite, independently reviewed actual-main Cargo libtest build.

Source-only preparation until exact protocol, source review, Symbolica18 gate and
cache release are frozen. No operation runs on import. Runtime captures are a
separate controller and require the root N2 postfix feedback.
"""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import io
import json
import os
import signal
import sys
import tarfile
import time

ROOT = Path('/shared/external/iregi/iregi-rust')
HERE = Path(__file__).resolve().parent


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def save(path, record):
    temporary = path.with_suffix('.partial')
    temporary.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
    temporary.replace(path)


def require(value, reason):
    if not value:
        raise ValueError(reason)


def verify_context(protocol):
    for name,expected in protocol['configuration_path_inventory'].items():
        require((ROOT/name).exists() is expected, 'changed configuration presence '+name)
    for name,expected in protocol['source_directory_inventory'].items():
        directory=ROOT/name
        pattern='*' if name.endswith('/assets') else '*.rs'
        actual=sorted(str(p.relative_to(ROOT)) for p in directory.rglob(pattern) if p.is_file())
        require(actual == expected, 'changed owned source directory membership '+name)


class Budget:
    """Absolute stage deadline starts before protocol/source filesystem reads."""
    def __init__(self, seconds):
        self.started = time.monotonic()
        self.seconds = seconds
        self.deadline = self.started+seconds
        self.work_deadline = self.deadline-8
        self.cancelled = None
        self.previous = {}
    def remaining(self):
        if self.cancelled is not None:
            raise RuntimeError(self.cancelled)
        value = self.work_deadline-time.monotonic()
        if value <= 0:
            raise TimeoutError('aggregate work budget exhausted; cleanup reserve retained')
        return value
    def arm(self):
        def interrupt(number, frame):
            self.cancelled = 'cancelled by signal '+str(number)
            for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGALRM):
                signal.signal(sig,signal.SIG_IGN)
            raise RuntimeError(self.cancelled)
        for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGALRM):
            self.previous[sig] = signal.signal(sig,interrupt)
        signal.setitimer(signal.ITIMER_REAL,max(.001,self.work_deadline-time.monotonic()))
    def disarm(self):
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in self.previous.items():
            signal.signal(sig,handler)
    def elapsed(self):
        return time.monotonic()-self.started


def main():
    require(Path.cwd().resolve() == ROOT, 'project working directory')
    require(len(sys.argv) == 3, 'build.py source-review.json expected_source_review_sha256')
    budget = Budget(600)
    budget.work_deadline = budget.deadline-45
    budget.arm()  # Absolute alarm precedes protocol reads, hashes and mkdir/save.
    protocol_path = HERE/'build-protocol-v3.json'
    folder = HERE/'build-003'
    record = dict(status='preflight',operation='actual_main_private_N7_libtest_build',
        started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        started_monotonic=budget.started,absolute_deadline_monotonic=budget.deadline,
        work_deadline_monotonic=budget.work_deadline,total_seconds=600,
        cleanup_reserve_seconds=45,child_seconds=510,cpu_affinity=[6,7],
        steps=[],cleanup_errors=[],outputs={},numerical_qualified=False,
        performance_qualified=False,license_recorded=False)
    receipt = folder/'receipt.json'
    guards = {}
    complete = False
    try:
        os.sched_setaffinity(0,{6,7})
        record['controller_cpu_affinity'] = sorted(os.sched_getaffinity(0))
        folder.mkdir(exist_ok=False)
        save(receipt,record)
        protocol = load(protocol_path)
        lifecycle = Path(protocol['lifecycle'])
        require(sha(lifecycle) == protocol['lifecycle_sha256'], 'exact owned lifecycle')
        spec = importlib.util.spec_from_file_location('owned_main_n7_build',lifecycle)
        h = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(h)
        review_path = Path(sys.argv[1]).resolve()
        require(sha(review_path) == sys.argv[2], 'exact independent source review')
        review = load(review_path)
        require(review['status'] == 'passed_concise_independent_source_API_review' and
            sys.argv[2] == protocol['probe_source_review_sha256'],
            'independently passed exact probe source review under root build authorization')
        require(protocol['status'] == 'root_authorized_frozen_actual_main_libtest_build', 'frozen build')
        guards.update(protocol['inputs'])
        guards[str(protocol_path)] = sha(protocol_path)
        guards[str(review_path)] = sys.argv[2]
        record['inputs'] = guards
        verify_context(protocol)
        source_members=protocol['source_snapshot_members']
        with tarfile.open(folder/'actual-main-source-context.tar.gz','w:gz',compresslevel=6) as archive:
            for path,digest in guards.items():
                budget.remaining()
                if path in source_members:
                    payload=Path(path).read_bytes()
                    require(hashlib.sha256(payload).hexdigest() == digest, 'changed build source '+path)
                    member=tarfile.TarInfo(source_members[path])
                    member.size=len(payload); member.mode=0o600; member.mtime=0
                    archive.addfile(member,io.BytesIO(payload))
                else:
                    require(sha(path) == digest, 'changed build input '+path)
        record['archived_source_files']=len(source_members)
        gate = load(protocol['symbolica18_gate_path'])
        require(sha(protocol['symbolica18_gate_path']) == protocol['symbolica18_gate_sha256'], 'exact Symbolica18 gate')
        require(gate['status'] == 'passed' and gate['completed_selected_tests'] == 18 and
            gate['inputs_unchanged'] is True and not gate['cleanup_errors'], 'Symbolica18 must pass')
        env = dict(os.environ)
        for key,value in protocol['environment'].items():
            require(env.get(key) == value, 'changed declared environment '+key)
        require(bool(env.get('SYMBOLICA_LICENSE')), 'license must be forwarded in memory')
        env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',RUST_TEST_THREADS='1')
        record['command'] = protocol['build_command']
        require(protocol['build_command'][0:3] == [protocol['taskset'],'-c','6,7'], 'exact CPU6/7 command')
        step = {}; record['steps'].append(step)
        def persist(value):
            step.update(value)
            save(receipt,record)
        result = h.execute(protocol['build_command'],folder/'cargo.log',budget,510,
                           record['cleanup_errors'],persist,env)
        require(result['status'] == 'exited' and result.get('owned_group_gone') is True,
                'actual main Cargo build failed or owned group remains')
        events = []
        for line in (folder/'cargo.log').read_text().splitlines():
            budget.remaining()
            try: events.append(json.loads(line))
            except json.JSONDecodeError: pass
        require(any(e.get('reason') == 'build-finished' and e.get('success') is True for e in events),
                'Cargo build-finished success event')
        selected = [e for e in events if e.get('reason') == 'compiler-artifact' and
            e.get('target',{}).get('name') == 'iregi_rust' and
            e.get('target',{}).get('kind') == ['lib'] and
            e.get('profile',{}).get('test') is True and e.get('executable')]
        require(len(selected) == 1,'one actual emitted core library test executable')
        artifact = selected[0]
        require(artifact['target']['src_path'] == str(ROOT/'crates/iregi-rust/src/lib.rs') and
            artifact['features'] == ['default'] and artifact['fresh'] is False,'fresh current core default libtest')
        require(artifact['package_id'] == protocol['core_package_id'],'actual main core package')
        executable = Path(artifact['executable'])
        require(executable.is_absolute() and executable.is_file(),'actual executable exists')
        digest = sha(executable)
        owned = h.freeze_binary(executable,digest,folder/'main-private-n7-library-tests',budget)
        guards[str(owned)] = digest
        save(folder/'cargo-artifact.json',artifact)
        record['artifact'] = artifact
        record['frozen_binary'] = dict(path=str(owned),sha256=digest,bytes=owned.stat().st_size)
        record['profile'] = 'default actual main libtest; no public rank override'
        complete = True
        record['status'] = 'completed_awaiting_terminal_guard'
    except BaseException as error:
        record.update(status='failed',error=repr(error))
    finally:
        budget.disarm()
        terminal = Budget(max(0,budget.deadline-time.monotonic()))
        terminal.deadline = budget.deadline
        terminal.work_deadline = budget.deadline-3
        try:
            terminal.arm()
            require(bool(guards),'no completed preflight input admission')
            verify_context(protocol)
            for path,digest in guards.items():
                terminal.remaining()
                require(sha(path) == digest,'changed terminal input '+path)
            record['inputs_unchanged'] = True
            for path in sorted(folder.iterdir()):
                terminal.remaining()
                if path.is_file() and path != receipt and not path.name.endswith('.partial'):
                    record['outputs'][path.name] = sha(path)
            terminal.remaining()
        except BaseException as error:
            record.update(inputs_unchanged=False,postguard_error=repr(error))
        finally:
            terminal.disarm()
        record.update(elapsed_seconds=budget.elapsed(),cancellation=budget.cancelled,
            finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        record['status'] = 'passed' if (complete and record.get('inputs_unchanged') is True and
            not record['cleanup_errors'] and not budget.cancelled and not terminal.cancelled and
            record['elapsed_seconds'] <= 600) else 'failed'
        # Keep final save inside the same absolute deadline, including failure paths.
        final = Budget(max(0,budget.deadline-time.monotonic()))
        final.deadline = final.work_deadline = budget.deadline
        try:
            final.arm(); save(receipt,record); final.remaining()
        finally:
            final.disarm()
    print(json.dumps(dict(status=record['status'],receipt=str(receipt),sha256=sha(receipt))))
    return 0 if record['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
