"""Bounded independent comparison; the original primary timeout stays a timeout."""
from pathlib import Path
import datetime, hashlib, json, os, signal, subprocess, time

root = Path.cwd()
base = root / 'target/planar-mixed-reference'
producer = root / 'validation/planar-adoption'
original = root / 'target/planar-adoption'
sha = lambda p: hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()
load = lambda p: json.loads(p.read_text())
primary = producer / 'mixed-rank7.json'
assert sha(primary) == '0f68d0dd5ea589fe49d84e8217ddfd93bddc644054d7e0969951c1466c96c4d9'
assert sha(producer / 'qualification.json') == 'cb2fdd2043009db641aab53baa9b429166d1d05ccaf68e3622009ea237a86c14'
prior = load(producer / 'runs/rank7-mixed.json')
assert prior['status'] == 'timeout' and prior['exit_code'] == 124
assert prior['output_artifact_status'] == 'primary_complete'
assert prior['source_hashes_unchanged'] and prior['binary_unchanged']
assert prior['output_artifact_sha256'] == sha(primary)
assert prior['build_manifest_sha256'] == sha(producer / 'build.json') == sha(original / 'build.json')
producer_build = load(producer / 'build.json')
assert producer_build['exit_code'] == 0
assert producer_build['binary_sha256'] == prior['binary_sha256'] == sha(original / 'core-tests')
for path, digest in producer_build['source_hashes'].items():
    assert sha(producer / 'source' / path) == digest
    assert sha(original / 'source-snapshot' / path) == digest
assert sha(original / 'mixed-rank7.json') == sha(primary)
assert sha(original / 'runs/rank7-mixed.json') == sha(producer / 'runs/rank7-mixed.json')
build = load(base / 'build.json')
assert build['exit_code'] == 0 and build['all_closure_hashes_rechecked']
binary = base / 'compare'
assert sha(binary) == build['binary_sha256']
for path, digest in build['source_hashes'].items():
    assert sha(base / 'source' / path) == digest
artifact = base / 'comparison.json'
report = base / 'run.json'
log_path = base / 'run.log'
assert not any(p.exists() for p in (artifact, report, log_path))
command = [str(binary), str(primary), str(artifact)]
env = os.environ.copy()
env.update(RAYON_NUM_THREADS='1', OMP_NUM_THREADS='1', IREGI_PREPARATION_PROFILE='1')
tracked = [primary, producer / 'qualification.json', producer / 'runs/rank7-mixed.json',
           producer / 'build.json', original / 'core-tests', original / 'mixed-rank7.json',
           original / 'runs/rank7-mixed.json', base / 'build.json', binary]
tracked += [base / 'source' / p for p in build['source_hashes']]
tracked += [producer / 'source' / p for p in producer_build['source_hashes']]
hashes = {str(p): sha(p) for p in tracked}
record = dict(status='running', command=command, timeout_seconds=600,
              started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              cpu_affinity=sorted(os.sched_getaffinity(0)), runner_sha256=sha(Path(__file__)),
              binary_sha256=sha(binary), build_manifest_sha256=sha(base / 'build.json'),
              primary_artifact_sha256=sha(primary), original_run_status='timeout',
              original_artifact_status='primary_complete', original_report_sha256=sha(producer / 'runs/rank7-mixed.json'),
              producer_build_manifest_sha256=sha(producer / 'build.json'),
              environment={k: env[k] for k in ('RAYON_NUM_THREADS', 'OMP_NUM_THREADS', 'IREGI_PREPARATION_PROFILE')},
              input_hashes=hashes)
report.write_text(json.dumps(record, indent=2) + '\n')
started = time.monotonic()
with log_path.open('w') as log:
    child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
    try:
        code = child.wait(timeout=600)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGTERM)
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
        code = 124
record.update(exit_code=code, status='passed' if code == 0 else 'timeout' if code == 124 else 'failed',
              elapsed_seconds=time.monotonic() - started,
              finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              inputs_unchanged=all(sha(Path(p)) == digest for p, digest in hashes.items()))
if artifact.exists():
    result = load(artifact)
    record.update(output_artifact_sha256=sha(artifact), output_artifact_status=result['status'])
    if code == 0 and (result['status'] != 'passed' or result['compared_complex_slots'] != 10560
                      or result['validated_primary_lanes'] != [0, 2]
                      or result['box_statuses'] != ['Success'] * 5
                      or any(len(x) != 5280 for x in result['box_values'])
                      or len(result['independent_values']) != 5280):
        code = 1
        record['status'] = 'invalid-artifact'
elif code == 0:
    code = 1
    record['status'] = 'missing-artifact'
if not record['inputs_unchanged']:
    code = 1
    record['status'] = 'invalid-provenance'
report.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({k: record[k] for k in ('status', 'exit_code', 'elapsed_seconds', 'inputs_unchanged')}), flush=True)
print(log_path.read_text()[-10000:], flush=True)
raise SystemExit(code)
