#!/usr/bin/env python3
"""Bind the completed candidate run and numerical audit to frozen sources."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
SCRATCH = ROOT/'target/near-vacuum-input-enclosure'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    destination = HERE/'candidate-provenance-audit.json'
    assert not destination.exists(), 'Never overwrite a provenance audit'
    checks, hashes = [], {}

    def check(condition, label):
        checks.append({'label': label, 'passed': bool(condition)})

    def hashed(path):
        digest = sha(path)
        hashes[str(path.relative_to(ROOT))] = digest
        return digest

    build = json.loads((CANDIDATE/'build.json').read_text())
    run = json.loads((CANDIDATE/'run.json').read_text())
    audit = json.loads((HERE/'candidate-audit.json').read_text())
    oracle_run = json.loads((HERE/'run.json').read_text())
    check(hashed(CANDIDATE/'output.json') == run['output_sha256'] == '0b0cdc5bd0754b4bd80faf3ef54a40bb09c860e42e789e2e7492563cc0cc6573', 'completed candidate output bytes')
    check(hashed(CANDIDATE/'run.json') == '96117de9ee19b2386b153d06abe127e0cf86bcdc80998ec176adcd32b81f8570', 'reported completed runtime manifest')
    check(run['exit_code'] == 0 and build['status'] == 'private_input_enclosure_driver_built', 'successful build and run')
    check(hashed(CANDIDATE/'build.json') == run['build_manifest_sha256'], 'runtime binds completed build')
    check(hashed(SCRATCH/'input_enclosure_compare') == build['binary_sha256'] == run['binary_sha256'], 'build and runtime bind actual binary')
    check(build['source_sha256'] == run['source_sha256'], 'source maps identical across build/runtime')
    for relative, digest in build['source_sha256'].items():
        check(hashed(SCRATCH/relative) == hashed(CANDIDATE/relative) == digest, 'source target/durable/build/run: '+relative)
    check(hashed(CANDIDATE/'run.log') == run['run_log_sha256'], 'runtime log hash')
    check(run['cwd'] == str(ROOT), 'project runtime working directory')
    check(run['command'][:3] == ['taskset','-c','18'] and run['cpu'] == 18, 'runtime pinned CPU18')
    check(run['runtime_limit_seconds'] == 60 and '60s' in run['command'], 'runtime bounded60s')
    check(str(SCRATCH/'input_enclosure_compare') in run['command'], 'runtime invokes inspected binary')
    check(str(HERE/'output.json') in run['command'] and str(CANDIDATE/'output.json') in run['command'], 'runtime input/output paths')
    check(hashed(HERE/'output.json') == run['oracle_sha256'] == oracle_run['output_sha256'], 'candidate binds independently generated oracle output')
    check(hashed(HERE/'run.json') == run['oracle_run_sha256'], 'candidate binds oracle runtime manifest')
    check(audit['status'] == 'passed' and audit['checks'] == 366 and not audit['failures'], 'exact numerical audit successful')
    for path, digest in audit['input_hashes'].items():
        check(hashed(ROOT/path) == digest, 'numerical audit bound input: '+path)
    check(hashed(HERE/'candidate-audit.json') == '830e4dda9ee3a6c7fb017a4ffe03b49ae5499c3936d66401abb40a261ddf61e9', 'reported numerical audit bytes')

    closure = ROOT/build['dependency_closure']
    names = ['closure-before-build.json','closure-after-build.json','closure-before-run.json','closure-after-run.json']
    snapshots = [json.loads((CANDIDATE/name).read_text()) for name in names]
    check(all(snapshot == snapshots[0] for snapshot in snapshots), 'four complete dependency snapshots identical')
    check(len(snapshots[0]) == build['closure_files_verified'] == run['closure_files_verified'] == 870, 'all870retained closure files recorded')
    links = [(build,'closure_before_sha256'),(build,'closure_after_sha256'),(run,'closure_before_run_sha256'),(run,'closure_after_run_sha256')]
    for name, (record,field) in zip(names,links):
        check(hashed(CANDIDATE/name) == record[field], 'snapshot hash link: '+name)
    actual_paths = {str(path.relative_to(ROOT)) for path in closure.rglob('*') if path.is_file()}
    check(actual_paths == set(snapshots[0]), 'retained current file set unchanged')
    for path, digest in snapshots[0].items():
        check(hashed(ROOT/path) == digest, 'current retained dependency byte hash: '+path)
    events = json.loads((closure/'cargo-library-events.json').read_text())
    completion = json.loads((closure/'workspace-completion.json').read_text())
    check(completion['cargo_returncode'] == 0, 'whole workspace reference closure completed')
    check(completion['dependency_closure_manifest_sha256'] == hashed(closure/'manifest.json'), 'closure manifest completion hash')
    check(completion['workspace_manifest_sha256'] == hashed(closure/'completed-workspace-build.json'), 'whole workspace completion hash')
    check(set(build['selected']) == {'symbolica','serde_json','oneloop'}, 'selected dependency names')
    for name, selected in build['selected'].items():
        matching = [event for event in events if event['target']['name'] == name and event['profile']['opt_level'] == '3' and event['profile']['test'] is False]
        check(len(matching) == 1 and matching[0] == selected['cargo_event'], 'unique optimized non-test '+name)
        check(hashed(ROOT/selected['archive']) == selected['sha256'], 'selected retained archive '+name)
    check([stage['stage'] for stage in build['builds']] == ['metadata','link'], 'metadata and link stages recorded')
    for stage in build['builds']:
        name, command = stage['stage'], stage['command']
        check(stage['exit_code'] == 0, name+': successful exit')
        check(command[:3] == ['taskset','-c','18'], name+': CPU18')
        check(str(SCRATCH/'input_enclosure_compare.rs') in command, name+': inspected source path')
        check(hashed(CANDIDATE/f'build-{name}.log') == stage['log_sha256'], name+': build log hash')
        for index, token in enumerate(command[:-1]):
            if token == '-L':
                check(Path(command[index+1].split('=',1)[1]).is_relative_to(closure), name+': retained-only search '+command[index+1])
            if token == '--extern':
                dependency, filename = command[index+1].split('=',1)
                check(filename == str(ROOT/build['selected'][dependency]['archive']), name+': exact selected extern '+dependency)
        if name == 'link':
            check(all(flag in command for flag in ['opt-level=3','lto=thin','embed-bitcode=yes','codegen-units=1']), 'compatible optimized ThinLTO flags')

    hashed(HERE/'audit_candidate_provenance.py')
    failures = [row for row in checks if not row['passed']]
    result = {'schema_version':1,'status':'passed' if not failures else 'failed','checks':len(checks),
              'failures':failures,'details':checks,'input_hashes':hashes,
              'scope':'Independent candidate source, binary, build, runtime, oracle-input and exact-numerical-audit provenance check, including every retained dependency byte.',
              'limitations':'No candidate/oracle rerun or production change. Diagnostic runtime duration is not performance qualification.'}
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':len(checks),'failures':len(failures),'hashes':len(hashes),
                      'output':str(destination.relative_to(ROOT)),'sha256':sha(destination)}))
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()
