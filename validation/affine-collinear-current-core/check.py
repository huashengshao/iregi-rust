"""Saved-only source and strict-test replay. Never compiles or evaluates integrals."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, io, json, tarfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = '/shared/external/iregi/iregi-rust/'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def require(value, reason):
    if not value:
        raise ValueError(reason)

def safe(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts, 'unsafe archive alias')
    return name

def archive(path, expected):
    payload = path.read_bytes()
    require(digest(payload) == expected, 'archive hash changed: ' + str(path))
    result = {}
    with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as stream:
        for m in stream:
            require(m.isfile(), 'nonregular archive member')
            name = safe(m.name)
            require(name not in result, 'duplicate member: ' + name)
            data = stream.extractfile(m).read()
            require(not data.startswith(b'\x7fELF'), 'compiled executable included')
            result[name] = data
    return result

def restore_files(manifest=None):
    """Restore exact compiled project sources and archived project-relative evidence."""
    m = manifest or json.loads((HERE/'manifest.json').read_text())
    containers = {a: archive(ROOT/a, sha) for a, sha in m['archives'].items()}
    result = {}
    for alias, item in m['files'].items():
        safe(alias)
        data = containers[item['archive']][item['member']]
        require(len(data) == item['bytes'] and digest(data) == item['sha256'], 'changed alias: ' + alias)
        result[alias] = data
    return result

def main():
    a = argparse.ArgumentParser()
    a.add_argument('--source-output', type=Path, help='reconstruct the exact349 compiled source bodies in a new directory')
    args = a.parse_args()
    m = json.loads((HERE/'manifest.json').read_text())
    for name, item in m['capsule_files'].items():
        data = (HERE/name).read_bytes()
        require(digest(data) == item['sha256'] and len(data) == item['bytes'], 'changed capsule file:' + name)
    for name, expected in m['parent_manifests'].items():
        require(digest((ROOT/name).read_bytes()) == expected, 'changed parent manifest:' + name)
    files = restore_files(m)
    def j(name):
        return json.loads(files[name])
    def test_result(folder, receipt_name='receipt.json'):
        r = j(folder+'/'+receipt_name)
        require(not r['cleanup_errors'] and r['inputs_unchanged'], 'failed source or process guard:' + folder)
        for name, expected in r['outputs'].items():
            require(digest(files[folder+'/'+name]) == expected, 'changed emitted log:' + name)
        for step in r['steps']:
            require(step.get('owned_group_gone') is True, 'unterminated historical child')
        return r
    base = 'target/affine-component-joint-current-cargo'
    build = j(base+'/build-004/receipt.json')
    require(build['status'] == 'passed' and build['inputs_unchanged'] and not build['cleanup_errors'], 'actual build not admitted')
    event = j(base+'/build-004/cargo-artifact.json')
    require(event == build['artifact'] and event['fresh'] is False and event['profile']['test'] is True, 'actual fresh default Cargo artifact')
    require(event['features'] == ['default'] and event['target']['kind'] == ['lib'], 'wrong libtest feature/target')
    require(build['frozen_binary']['sha256'] == m['omitted_binary']['sha256'], 'wrong original frozen binary')
    require(build['outputs']['actual-main-source-context.tar.gz'] == m['original_source_archive_sha256'], 'original source archive provenance changed')
    sources = m['compiled_source_aliases']
    require(len(sources) == 349 and len(set(sources)) == 349, 'compiled349 source inventory changed')
    bp = j(base+'/build-protocol-v4.json')
    require(set(bp['source_snapshot_members'].values()) == set(sources), 'compiled source membership changed')
    for source in sources:
        require(digest(files[source]) == bp['inputs'][PREFIX+source], 'source differs from actual build guard:' + source)
    for path, sha in build['inputs'].items():
        if path.startswith(PREFIX) and path[len(PREFIX):] in files:
            require(digest(files[path[len(PREFIX):]]) == sha, 'historical admitted input differs:' + path)
    selection = j(base+'/test-selection.json')
    core = test_result(base+'/core-001')
    require(core['status'] == 'failed_or_partial' and core['completed_tests'] == 16, 'fixed core result changed')
    heavy = {
      'affine_descent_guard::tests::a_vanishing_first_pivot_selects_an_alternate_generic_column_basis',
      'pv::affine_descent::tests::generic_profile_layouts_and_explicit_resource_limits_remain_finite'}
    require(set(core['failed_tests']) == heavy and len(selection['core']) == 18, 'heavy failures hidden')
    def passed(step, data, name):
        require(step.get('returncode') == 0 and not step.get('timeout'), 'non-successful strict test:' + name)
        text = data.decode()
        require('running 1 test' in text and 'test result: ok. 1 passed; 0 failed; 0 ignored;' in text, 'not one exact nonignored test:' + name)
    for i, step in enumerate(core['steps'][1:], 1):
        name = step['label']
        require(name == selection['core'][i-1] and '--exact' in step['command'], 'wrong exact core selector')
        if name in heavy:
            require(step.get('timeout') is True and step['timeout_seconds'] == 90 and step['returncode'] != 0, 'fixed90 timeout rewritten')
        else:
            passed(step, files[base+'/core-001/step-'+str(i)+'.log'], name)
    for phase in ['plain','dual']:
        folder = base+'/'+phase+'-001'
        r = test_result(folder)
        require(r['status'] == 'passed' and r['completed_tests'] == 1, 'numeric test did not pass')
        require(r['steps'][1]['label'] == selection[phase][0], 'wrong numeric selector')
        require('--ignored' in r['steps'][1]['command'] and '--exact' in r['steps'][1]['command'], 'numeric qualification not explicitly selected')
        passed(r['steps'][1], files[folder+'/step-1.log'], selection[phase][0])
    compbase = 'target/n6-component-coefficient-intern-v1'
    comp = test_result(compbase+'/component10-001')
    require(comp['status'] == 'passed' and comp['completed_tests'] == 10, 'component10 result changed')
    require(len(comp['steps']) == 11 and len(comp['actual_listed_tests']) == 10, 'component inventory changed')
    for i, step in enumerate(comp['steps'][1:], 1):
        require('--exact' in step['command'] and step['label'].startswith('stability::components::tests::'), 'component selector changed')
        passed(step, files[compbase+'/component10-001/step-'+str(i).zfill(2)+'.log'], step['label'])
    cb = 'target/checked-facade-focused-current'
    checked = test_result(cb+'/tests-001')
    require(checked['status'] == 'passed' and len(checked['selected_tests']) == 4 and not checked['unrun_tests'], 'checked4 outcome changed')
    for i, step in enumerate(checked['steps'][1:], 1):
        require(step['name'] == checked['selected_tests'][i-1] and '--exact' in step['command'], 'checked selector changed')
        passed(step, files[cb+'/tests-001/step-'+str(i)+'.log'], step['name'])
    source = files['crates/iregi-rust/src/certified_affine_tests.rs'].decode()
    require('for bits in [128,256]' in source.replace(' ', '') or 'forbitsin[128,256]' in source.replace(' ', ''), 'both precision tests source missing')
    for token in ['for slot in 0..4', 'result.basis.len(),210', 'precision_pair(plan.basis()', 'result.lane(1).is_err()', 'result.lane(0).unwrap(),result.lane(2).unwrap()']:
        require(token.replace(' ', '') in source.replace(' ', ''), 'all-array/batch source assertion missing:' + token)
    for token in ['response(3, alpha.rank())', 'actual[(4*moment+slot)*2+component]', '[primal,jet]']:
        require(token.replace(' ', '') in source.replace(' ', ''), 'selected Dual proof assertion missing:' + token)
    anchor = j(m['oracle_alias'])
    require(len(anchor['basis']) == 330 and len(anchor['native_laurent']) == 330, 'oracle raw coverage changed')
    require(anchor['native_slot_order'] == ['uv1','ir1','ir2','finite'], 'oracle Laurent order changed')
    release = j(base+'/numerical-release.json')
    require(sum(len(x['all_groups']) for x in release['attempts']) == 23, 'affine groups lost')
    require(all(g['gone'] for x in release['attempts'] for g in x['all_groups']), 'historical group absence not recorded')
    for n, status in [(1,'failed'),(2,'failed'),(3,'failed')]:
        r = j(base+'/build-'+str(n).zfill(3)+'/receipt.json')
        require(r['status'] == status, 'failed build history hidden')
    if args.source_output:
        require(not args.source_output.exists(), 'source destination must be new')
        for name in sources:
            p = args.source_output/name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(files[name])
    print(json.dumps({'status':'passed_saved_source_and_strict_test_replay','source_bodies':349,'inherited_source_bodies':305,'own_source_delta':44,'core_passed':16,'core_fixed90_timeouts_retained':2,'component_passed':10,'checked_facade_passed':4,'actual_numeric_test_assertions_passed':2,'independently_recomputed_native_arrays':False,'fresh_binary_PID_or_native_execution':False,'general_N_or_public_Dual_qualified':False,'performance_qualified':False},indent=2))
if __name__ == '__main__':
    main()
