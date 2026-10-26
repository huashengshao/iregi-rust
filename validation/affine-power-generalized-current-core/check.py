#!/usr/bin/env python3
"""Portable saved-only affine-power replay; Python stdlib, no native jobs."""
from pathlib import Path, PurePosixPath
from fractions import Fraction as Q
from decimal import Decimal, localcontext
import hashlib
import importlib.util
import io
import json
import re
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = 'target/affine-power-reduction-proposal'
PARENT = 'validation/quad-original-iregi-generalized-n6-rank6'
PREFIX = '/shared/external/iregi/iregi-rust/'
PARENT_HASH = '90e4ede40dbf46e537064dea0e85309b0079bfd12d245f7dc9ba658aa16d2f0e'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return dict(sha256=sha(body), bytes=len(body))


def load(body):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(body, object_pairs_hook=unique)


def safe(name):
    p = PurePosixPath(name)
    require(name and not p.is_absolute() and '..' not in p.parts and str(p) == name, 'safe relative alias')


def unpack(name, inventory):
    result = {}
    with tarfile.open(fileobj=io.BytesIO((HERE / name).read_bytes()), mode='r:gz') as archive:
        for item in archive:
            safe(item.name)
            require(item.isfile() and item.name not in result, 'unique regular archive members')
            body = archive.extractfile(item).read()
            require(desc(body) == inventory.get(item.name), 'exact archive member bytes')
            require(not body.startswith(b'\x7fELF') and b'S-130-' not in body, 'no native ELF or license literal')
            result[item.name] = body
    require(set(result) == set(inventory), 'closed archive inventory')
    return result


def restore_files(m):
    require({str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts} == set(m['capsule_files']) | {'manifest.json'}, 'closed capsule inventory')
    for name, value in m['capsule_files'].items():
        safe(name)
        require(desc((HERE / name).read_bytes()) == value, 'exact capsule file ' + name)
    for name, value in m['parent_files'].items():
        safe(name)
        require(desc((ROOT / name).read_bytes()) == value, 'exact declared parent ' + name)
    require(m['parent_manifest_sha256'] == sha((ROOT / PARENT / 'manifest.json').read_bytes()) == PARENT_HASH, 'fixed admitted quad parent')
    spec = importlib.util.spec_from_file_location('affine_power_portable_quad_parent', ROOT / PARENT / 'check.py')
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    files = parent.restore_files(parent.load((ROOT / PARENT / 'manifest.json').read_bytes()))
    sources = unpack('sources.tar.gz', m['source_members'])
    members = unpack('payload.tar.gz', m['payload_members'])
    require(len(sources) == 145, 'actual145-source archive')
    origins = load((HERE / 'payload-origins.json').read_bytes())
    require(set(origins) == set(m['aliases']), 'closed saved origin inventory')
    for alias, row in m['aliases'].items():
        safe(alias)
        selectors = set(row) & {'member', 'source_member', 'inherited_source'}
        require(len(selectors) == 1, 'one saved byte selector')
        body = members[row['member']] if 'member' in row else sources[row['source_member']] if 'source_member' in row else files[row['inherited_source']]
        require(desc(body) == {k: row[k] for k in ['sha256', 'bytes']} == {k: origins[alias][k] for k in ['sha256', 'bytes']}, 'saved alias descriptor')
        require(origins[alias]['origin'] == alias, 'exact recorded source-copy origin')
        require(alias not in files or files[alias] == body, 'saved alias collision')
        files[alias] = body
    for name in set(m['capsule_files']) | {'manifest.json'}:
        files[m['capsule_directory'] + '/' + name] = (HERE / name).read_bytes()
    return files


def replay(files, m):
    def read(alias):
        return load(files[alias])

    def text(alias):
        return files[alias].decode()

    def phase(directory, success=True):
        base = PRIVATE + '/' + directory
        r = read(base + '/receipt.json')
        require(r['inputs_unchanged'] and not r['cleanup_errors'] and r['cancellation'] is None and r['post_cancellation'] is None, 'saved terminal guards and cleanup ' + directory)
        require(0 < r['elapsed_seconds'] <= r['total_seconds'], 'finite saved total ' + directory)
        for absolute, digest in r['inputs'].items():
            alias = absolute.removeprefix(PREFIX)
            if absolute in m['omitted_native_inputs']:
                require(m['omitted_native_inputs'][absolute] == digest, 'explicit historical native omission')
                continue
            if alias in r.get('source_files', {}):
                alias = base + '/source-snapshot/' + alias
            elif directory == 'tests-001' and alias == PRIVATE + '/focused-test-inventory.json':
                alias = base + '/focused-test-inventory.json'
            require(alias in files and sha(files[alias]) == digest, 'available exact saved input ' + directory + '/' + alias)
        for name, digest in r['outputs'].items():
            absolute = PREFIX + base + '/' + name
            if absolute in m['omitted_native_inputs']:
                require(m['omitted_native_inputs'][absolute] == digest, 'explicit omitted frozen output')
            else:
                require(sha(files[base + '/' + name]) == digest, 'saved output hash')
        for step in r['steps']:
            require(step['owned_group_gone'] is True, 'saved owned group gone')
            if success:
                require(step['status'] == 'exited' and step['returncode'] == 0, 'saved successful child')
        return r

    built = phase('build-002')
    old_build = phase('build-001', False)
    require(built['status'] == 'passed' and sha(files[PRIVATE + '/build-002/receipt.json']) == m['build002_receipt_sha256'], 'fixed completed actual Cargo build')
    require(len(built['source_files']) == len(old_build['source_files']) == 145, 'both selected source inventories')
    for directory, r in [('build-001', old_build), ('build-002', built)]:
        for name, digest in r['source_files'].items():
            require(sha(files[PRIVATE + '/' + directory + '/source-snapshot/' + name]) == digest, 'actual immutable selected source copy')
    require(old_build['status'] == 'failed' and old_build['products'] == {} and len(old_build['steps']) == 1 and old_build['steps'][0]['returncode'] == 101, 'initial compile-only failure retained')
    old_events = [load(v) for v in text(PRIVATE + '/build-001/cargo-0.log').splitlines() if v.startswith('{')]
    errors = [v['message'] for v in old_events if v.get('reason') == 'compiler-message' and v['message'].get('level') == 'error']
    require(len(errors) == 3 and all(v['code']['code'] == 'E0277' and 'BorrowReplacement' in v['message'] for v in errors), 'three original cfgtest compile diagnostics')
    require(len(built['steps']) == 4 and built['cpu_affinity'] == [18, 19] and built['total_seconds'] == 888, 'actual four-command Cargo build bounds')
    for index in range(4):
        events = [load(v) for v in text(PRIVATE + '/build-002/cargo-' + str(index) + '.log').splitlines() if v.startswith('{')]
        require([v['success'] for v in events if v.get('reason') == 'build-finished'] == [True], 'successful actual Cargo terminal event')
        if index < 3:
            key = ['tests', 'cli', 'checked_tensor_public'][index]
            product = built['products'][key]
            event = read(PRIVATE + '/build-002/' + product['cargo_event'])
            require(event in events and event['reason'] == 'compiler-artifact' and event['executable'] == product['cargo_executable'] and product['sha256'] == m['omitted_native_inputs'][product['path']], 'actual selected Cargo product event and omitted ELF identity')
    require(built['products']['python_check']['features'] == 'standalone,native', 'actual selected PyO3 feature check')
    require(read(PRIVATE + '/independent-build-review.json')['status'] == 'passed_saved_build_evidence_audit', 'independent build audit retained')
    tests = phase('tests-002')
    first_tests = phase('tests-001')
    names = read(PRIVATE + '/focused-test-inventory.json')['selected_tests']
    require(tests['status'] == 'passed' and len(names) == len(set(names)) == 56 and names == tests['selected_tests'] and not tests['unrun_tests'] and len(tests['steps']) == 57, 'all56 focused exact tests')
    listing = [v[:-6] for v in text(PRIVATE + '/tests-002/step-0.log').splitlines() if v.endswith(': test')]
    require(len(listing) == len(set(listing)) == 434 and all(listing.count(n) == 1 for n in names), 'actual listing contains each selected name once')
    for i, name in enumerate(names, 1):
        log = text(PRIVATE + '/tests-002/step-' + str(i) + '.log')
        require(re.findall(r'^running .*$', log, re.M) == ['running 1 test'], 'one exact running header')
        require(re.findall(r'^test (?!result:)(.*)$', log, re.M) == [name + ' ... ok'], 'exact named successful completion')
        summaries = re.findall(r'^test result:.*$', log, re.M)
        require(len(summaries) == 1 and re.fullmatch(r'test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; 433 filtered out; finished in [0-9]+\.[0-9]+s', summaries[0]), 'strict one-pass summary')
        require(tests['steps'][i]['command'][-4:] == ['--exact', name, '--nocapture', '--test-threads=1'], 'actual exact test command')
    correction = read(PRIVATE + '/test-inventory-correction.json')
    require(first_tests['status'] == 'failed' and len(first_tests['steps']) == 1 and first_tests['unrun_tests'] == first_tests['selected_tests'], 'initial listing-only failure retained')
    require([(a, b) for a, b in zip(first_tests['selected_tests'], names) if a != b] == [(correction['old_name'], correction['actual_name'])], 'only one inventory module path corrected')
    require(files[PRIVATE + '/tests-001/step-0.log'] == files[PRIVATE + '/tests-002/step-0.log'], 'same actual binary listing before and after path correction')
    require(read(PRIVATE + '/independent-focused-tests-review.json')['exact_tests_passed'] == 56, 'independent56-log review retained')
    guard = phase('guard-001')
    log = text(PRIVATE + '/guard-001/step.log')
    require(guard['status'] == 'passed_preparation_only' and guard['no_integral_or_scalar_master_request'] and len(guard['steps']) == 1 and 'N6 rank6 constant-one guard structural preparation completed; no integral evaluated' in log and re.search(r'^ok$', log, re.M) and re.search(r'^test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; 433 filtered out;', log, re.M), 'actual guard preparation test only')
    config = read(PRIVATE + '/numeric/cases.json')
    fixture = read(config['cases']['unit']['input'].removeprefix(PREFIX))
    basis = [[a, b, c, d - a - b - c] for d in range(7) for a in range(d, -1, -1) for b in range(d - a, -1, -1) for c in range(d - a - b, -1, -1)]
    powers = [p['power'] for p in fixture['propagators']]
    scale = max(Q(1), Q(fixture['mu']) ** 2, *(abs(Q(p['mass_squared'][0])) for p in fixture['propagators']))
    for i, p in enumerate(fixture['propagators']):
        for other in fixture['propagators'][:i]:
            q = [Q(a) - Q(b) for a, b in zip(p['shift'], other['shift'])]
            scale = max(scale, abs(q[0] ** 2 - sum(x * x for x in q[1:])) )
    require(scale == 9 and fixture['rank'] == 6 and fixture['dimension_shift'] == 0 and powers == [1] * 6, 'exact positive unit fixture scale/domain')
    reference_lines = text(config['cases']['unit']['reference_raw'].removeprefix(PREFIX)).splitlines()
    precision = [load(v[10:]) for v in reference_lines if v.startswith('PRECISION ')]
    require(precision == [{'dbl_kind': 16, 'olo_kind': 16, 'storage_bits': 128, 'binary_digits': 113, 'decimal_digits': 33}], 'original quad storage witness')
    results = [load(v[7:]) for v in reference_lines if v.startswith('RESULT ')]
    require(len(results) == 1 and results[0]['stable'] is True and results[0]['id'] == fixture['id'] and len(results[0]['moments']) == 210, 'same admitted stable original reference')
    reference = results[0]['moments']
    maxima, captured = {}, []
    totals = dict(reference_complex_slots=0, IR_zero_slots=0, convergent_UV_zero_slots=0, precision_pairs=0)
    for bits in [128, 256]:
        directory = 'numeric/captures/unit-' + str(bits) + '-001'
        r = phase(directory)
        require(r['status'] == 'passed_complete_capture_and_840_quad_slots' and r['working_bits'] == bits and sha(files[PRIVATE + '/' + directory + '/receipt.json']) == m['unit' + str(bits) + '_receipt_sha256'], 'terminal positive unit precision capture')
        d = read(PRIVATE + '/' + directory + '/stdout.json')
        require(d['precision_bits'] == bits and d['basis'] == basis and d['poles'] == ['uv1', 'ir1', 'ir2', 'finite'] and len(d['samples']) == 1, 'complete native precision output')
        require(d['settings'] == {'algorithm': 'Ibp', 'convention': 'IregiNative', 'dimension_shift': 0, 'input_policy': 'Preserve', 'invariants': 'FromShifts', 'powers': powers, 'propagators': 6, 'rank': 6, 'tensor_weights': 'Components'} and d['precision_control']['accuracy_bits'] == 53, 'unchanged exact settings/target')
        lane = d['samples'][0]
        require(lane['id'] == fixture['id'] and lane['status'] == 'success' and len(lane['moments']) == 210, 'one successful complete unit lane')
        maximum = Q(0)
        for i, (actual, target) in enumerate(zip(lane['moments'], reference)):
            require(len(actual) == len(target) == 4, 'all native Laurent slots')
            unit = scale ** (sum(basis[i]) + 4 - 2 * sum(powers))
            for slot, (z, ref) in enumerate(zip(actual, target)):
                require(len(z) == len(ref) == 2 and all(type(v) is str for v in z + ref), 'quoted complete complex values')
                a, b = tuple(map(Q, z)), tuple(map(Q, ref))
                error = sum((x - y) ** 2 for x, y in zip(a, b)) / max(unit, sum(x * x for x in b))
                require(error <= Q(1, 10 ** 20), 'every normalized1e-10 reference gate')
                maximum = max(maximum, error)
                totals['reference_complex_slots'] += 1
                if slot in (1, 2) or (slot == 0 and sum(basis[i]) + 4 - 2 * sum(powers) < 0):
                    require(a == (0, 0), 'actual IR/powercounted UV exact zero')
                    totals['IR_zero_slots' if slot in (1, 2) else 'convergent_UV_zero_slots'] += 1
        maxima['reference' + str(bits)] = maximum
        e = d['engine_execution']
        require(e['engine'] == 'AffinePower' and (e['dag_nodes'], e['dag_edges'], e['packed_child_rows'], e['child_batch_calls'], e['parent_batch_calls']) == (5, 4, 4, 1, 1), 'actual grouped affine work')
        require(e['child_execution']['master_rows'] == 120 and e['child_execution']['master_family_batches'] == 4 and e['parent_execution']['master_rows'] == 0, 'actual child masters and masterfree parent')
        require(len(e['child_methods']) == 1 and e['child_methods'][0]['requested'] == 'Ibp' and e['child_methods'][0]['actual'] == 'PassarinoVeltman' and e['child_methods'][0]['rows'] == 4 and any('IBP tensor completion uses PV' in s for s in e['child_methods'][0]['notes']), 'PV child completion explicit, no pureIBP claim')
        report = read(PRIVATE + '/' + directory + '/comparison.json')
        require(report['status'] == 'passed_complete_N6_rank6_quad_comparison' and report['counts']['quad_reference_slots'] == 840 and not report['failures'] and report['engine_execution'] == e and report['diagnostics'] == d['diagnostics'], 'direct report agrees with saved actual contexts')
        captured.append(lane['moments'])
    maximum = Q(0)
    for i, (low, high) in enumerate(zip(*captured)):
        unit = scale ** (sum(basis[i]) + 4 - 2 * sum(powers))
        for a, b in zip(low, high):
            a, b = tuple(map(Q, a)), tuple(map(Q, b))
            error = sum((x - y) ** 2 for x, y in zip(a, b)) / max(unit, sum(x * x for x in b))
            require(error <= Q(1, 2 ** 160), 'all840 normalized2^-80 precision pairs')
            maximum = max(maximum, error)
            totals['precision_pairs'] += 1
    maxima['precision_pair'] = maximum
    pair_body = files[PRIVATE + '/numeric/pair-unit.json']
    pair = load(pair_body)
    require(sha(pair_body) == m['unit_pair_sha256'] and pair['status'] == 'passed_complete_840_precision_pairs' and pair['pair_gates'] == 840 and not pair['failures'] and Q(pair['maximum_normalized_error_squared']) == maximum, 'saved pair report exact maximum and pass')
    for case in ['dot', 'd6']:
        directory = 'numeric/captures/' + case + '-128-001'
        r = phase(directory, False)
        step = r['steps'][0]
        require(r['status'] == 'failed_or_incomplete' and len(r['steps']) == 1 and step['timeout'] is True and step['timeout_seconds'] == 810 and step['returncode'] == -15 and step['owned_group_gone'] and files[PRIVATE + '/' + directory + '/stdout.json'] == b'', 'preserved810s timeout no fabricated array')
        require(PRIVATE + '/' + directory + '/comparison.json' not in files, 'failed case has no comparison')
        require(not any(name.startswith(PRIVATE + '/numeric/captures/' + case + '-256-') for name in m['aliases']), 'no admitted256partner for failed128case')
    require(m['full_requested_generalized_corpus_qualified'] is False and m['Dual_physical_or_performance_qualified'] is False, 'full requested corpus remains incomplete')
    with localcontext() as ctx:
        ctx.prec = 100
        displays = {key: str((Decimal(v.numerator) / Decimal(v.denominator)).sqrt()) for key, v in maxima.items()}
    return {'status': 'passed_portable_saved_affine_power_integrity_and_scoped_unit_math', 'source_files': 145, 'restored_aliases': len(files), 'counts': totals, 'maximum_normalized_errors': displays, 'focused_exact_tests_passed': 56, 'preserved_compile_and_listing_failures': True, 'preparation_only_guard_seconds': guard['elapsed_seconds'], 'unit_precisions': [128, 256], 'dot128_and_D6_128': 'preserved810second_timeouts_with_cleanup_pass_and_no_arrays', 'dot256_and_D6_256': 'unrun', 'actual_child_completion': 'PassarinoVeltman_requested_Ibp', 'full_requested_generalized_corpus_qualified': False, 'Dual_physical_or_performance_qualified': False, 'omitted_ELFs_rehashed_or_executed': False, 'new_native_or_process_jobs': 0}


if __name__ == '__main__':
    manifest = load((HERE / 'manifest.json').read_bytes())
    print(json.dumps(replay(restore_files(manifest), manifest), indent=2))
