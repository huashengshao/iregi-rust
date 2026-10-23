"""Bind nonempty complete libtest module results to the frozen candidate."""
from pathlib import Path
import hashlib
import json
import re
import subprocess


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    build_path = here / 'use-dedup-full-build.json'
    build = json.loads(build_path.read_text())
    run_path = here / 'use-dedup-full-tests-run.json'
    run = json.loads(run_path.read_text())
    assert build['status'] == run['status'] == 'passed'
    assert build['exit_codes'] == [0, 0, 0] and build['changed_inputs'] == {}
    assert run['changed_inputs'] == {}
    assert run['build_manifest_sha256'] == sha(build_path)
    assert build['instrumentation_patch_sha256'] == sha(here / 'use-dedup-full-instrumentation.patch')
    for name, value in build['protected_input_hashes'].items():
        assert sha(root / name) == value, name
    for name, value in run['protected_input_hashes'].items():
        assert sha(root / name) == value, name
    binary = root / build['test_binary_path']
    assert sha(binary) == build['test_binary_sha256']
    listed = subprocess.run([str(binary), '--list'], capture_output=True, text=True, check=True, timeout=30)
    listing_path = here / 'use-dedup-full-tests-list.txt'
    if listing_path.exists():
        assert listing_path.read_text() == listed.stdout
    else:
        listing_path.write_text(listed.stdout)
    tests = re.findall(r'^(\S+): test$', listed.stdout, re.M)
    assert len(tests) == 174
    counts = {'stability::': 38, 'execution::': 35}
    assert [record['module'] for record in run['records']] == list(counts)
    artifacts = [build_path, run_path, listing_path, Path(__file__)]
    for record in run['records']:
        assert record['status'] == 'passed' and record['exit_code'] == 0
        assert record['command'] == ['taskset', '-c', '14', str(binary), record['module'], '--test-threads=1', '--nocapture']
        log_path = root / record['log_path']
        assert sha(log_path) == record['log_sha256']
        log = log_path.read_text()
        summary = re.findall(r'^test result: ok\. (\d+) passed; 0 failed; 0 ignored; 0 measured; (\d+) filtered out; finished in [0-9.]+s$', log, re.M)
        assert len(summary) == 1
        expected = {name for name in tests if name.startswith(record['module'])}
        assert len(expected) == counts[record['module']] == int(summary[0][0]) > 0
        assert int(summary[0][1]) == len(tests) - len(expected)
        observed = re.findall(r'^test (\S+) \.\.\.', log, re.M)
        assert len(observed) == len(expected) and set(observed) == expected
        artifacts.append(log_path)
    record = dict(status='passed', build_manifest_sha256=sha(build_path),
                  exact_complete_module_counts=counts, total_passed=sum(counts.values()),
                  scope='All 38 stability and 35 execution unit tests pass in the isolated 6b24 core plus reviewed collector delta and phase timers; complete module membership is bound to the frozen binary listing. No high-point numerical-array or performance claim.',
                  artifacts={str(path.relative_to(root)): sha(path) for path in artifacts})
    output = here / 'use-dedup-full-tests-qualification.json'
    output.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
