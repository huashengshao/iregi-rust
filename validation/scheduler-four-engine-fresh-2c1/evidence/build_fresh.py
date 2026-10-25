"""Execute only the reviewed finite compiler recipe, never a test or integral."""
from pathlib import Path
import hashlib, json, os, re, sys
sys.dont_write_bytecode = True
from fresh_lifecycle import Budget, execute

ROOT = Path('/shared/external/iregi/iregi-rust')
HERE = ROOT/'target/guard-performance-review/optimized-performance-proposal'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')

def main():
    assert Path.cwd() == ROOT and len(sys.argv) == 2
    reviewed = sys.argv[1]
    protocol_path = HERE/'fresh-build-protocol.json'
    assert sha(protocol_path) == reviewed
    protocol = json.loads(protocol_path.read_text())
    assert protocol['status'] == 'SOURCE_REVIEW_REQUIRED_NO_COMPILER_OR_RUNTIME_GRANT'
    attempt = Path(protocol['attempt_directory'])
    attempt.mkdir(exist_ok=False)
    budget = Budget(protocol['aggregate_budget_seconds'])
    budget.work_deadline = budget.deadline-protocol['cleanup_postguard_reserve_seconds']
    receipt = attempt/'build.json'
    record = {'status':'preparing','success':False,'protocol_sha256':reviewed,
              'runner_sha256':sha(Path(__file__)), 'steps':[dict(step,status='unrun') for step in protocol['steps']],
              'scope':protocol['scope'],'outputs':{},'cleanup_errors':[],
              'aggregate_budget_seconds':protocol['aggregate_budget_seconds'],
              'cleanup_postguard_reserve_seconds':protocol['cleanup_postguard_reserve_seconds'],
              'numerical_execution':False,'performance_measurement':False}
    outputs = {}
    save(receipt, record)

    def verify():
        assert sha(protocol_path) == reviewed, 'Protocol changed'
        for raw, expected in {**protocol['protected_sha256'], **protocol['tool_sha256']}.items():
            budget.remaining()
            path = Path(raw) if Path(raw).is_absolute() else ROOT/raw
            assert sha(path) == expected, 'Changed input: '+raw
        for path, expected in outputs.items():
            budget.remaining()
            assert sha(path) == expected, 'Changed compiler output: '+str(path)

    budget.arm()
    try:
        for name in ['RUSTC_BOOTSTRAP','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER']:
            assert not os.environ.get(name), 'Unexpected compiler environment override: '+name
        verify()
        record['guard_before'] = True
        for step in record['steps']:
            verify()
            output = Path(step['output'])
            output.parent.mkdir(parents=True, exist_ok=True)
            env = dict(os.environ)
            env.update(step['environment'])
            def persist(result):
                step.update(result)
                save(receipt, record)
            log = attempt/(step['label']+'.log')
            result = execute(step['command'], log, budget, step['compiler_cap_seconds'], record['cleanup_errors'], persist, env)
            assert result['status'] == 'exited', 'Compiler failed or timed out; preserve first attempt'
            verify()
            with output.open('rb') as stream:
                header = stream.read(8)
            assert header == (b'\x7fELF\x02\x01\x01\x00' if step['product']=='probe' else b'!<arch>\n'), 'Unexpected artifact format'
            item = {'path':str(output),'sha256':sha(output),'bytes':output.stat().st_size}
            outputs[output] = item['sha256']
            if step['product']=='probe':
                linkmap = Path(step['link_map'])
                text = linkmap.read_text()
                item['archive_binding'] = {}
                for crate, expected in step['expected_link_archives'].items():
                    found = sorted(set(re.findall(r'(/[^\s()]*?/lib'+re.escape(crate)+r'(?:-[A-Za-z0-9_]+)?\.rlib)', text)))
                    assert found == [expected], f'{crate} archive contamination: {found}'
                    item['archive_binding'][crate] = {'path':expected,'sha256':sha(expected)}
                item['link_map'] = {'path':str(linkmap),'sha256':sha(linkmap),'bytes':linkmap.stat().st_size}
                outputs[linkmap] = item['link_map']['sha256']
            step.update(status='passed',log_sha256=sha(log),output_sha256=item['sha256'])
            record['outputs'][step['label']] = item
            save(receipt, record)
        record['status'] = 'completed-awaiting-final-guards'
    except Exception as error:
        record.update(status='failed',error=repr(error))
    save(receipt, record)
    try:
        verify()
        record['guard_after'] = True
    except Exception as error:
        record.update(guard_after=False,guard_error=repr(error))
    record['elapsed_seconds_diagnostic'] = budget.elapsed()
    record['deadline_exceeded'] = record['elapsed_seconds_diagnostic'] > protocol['aggregate_budget_seconds']
    if budget.cancelled:
        record['cancellation'] = budget.cancelled
    record['success'] = (all(step['status']=='passed' for step in record['steps'])
                         and record.get('guard_after') is True and not record['cleanup_errors']
                         and not record['deadline_exceeded'] and not budget.cancelled and 'error' not in record)
    record['status'] = 'passed' if record['success'] else 'failed'
    save(receipt, record)
    budget.disarm()
    print(json.dumps({'status':record['status'],'receipt_sha256':sha(receipt),
                      'products':len(record['outputs']),'elapsed_seconds_diagnostic':record['elapsed_seconds_diagnostic']}))
    return 0 if record['success'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
