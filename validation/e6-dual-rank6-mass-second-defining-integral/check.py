"""Replay archived DD defining-integral evidence; core agreement remains pending.

Only shallow archives and stdlib saved arithmetic are used. No parent checker,
native binary, numerical producer, symbolic engine or full core capture runs.
"""
from pathlib import Path, PurePosixPath
from fractions import Fraction
import argparse
import gzip
import hashlib
import io
import json
import re
import sys
import tarfile
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = '/shared/external/iregi/iregi-rust/'
RAW = 'target/n6-sample-d6-mass-second-anchor-dd'
BUILD = RAW+'/build-001'
NUMERIC = RAW+'/numeric-001'
STREAM_CHECKER = 'target/rank6-final-dd-stream-independent-replay.py'
PARENT_CHECKER = RAW+'/compare_saved_parents.py'
CORE_MANIFEST = 'validation/e6-dual-optional-zero-profile-core-tests/manifest.json'
CORE_MANIFEST_SHA = '403dfee66f69447e6f9f97eb14ec1e839789e3859e30dbb762d8e7350d0a4917'
PINS = {
    BUILD+'/receipt.json': '0f4b69215a69574b5f25be044784950987cc39a45789388b237b77ff13da4b97',
    NUMERIC+'/receipt.json': 'ae85d9330fcf42b7ef8dfdaa975e579bd8d5504b50eaf41772c7e620018d74e0',
    RAW+'/independent-stream-replay-001.json': '461859d575417ca26d8bd755dd81f47448c685a20ae8de4b3dfedc193fd8903a',
    RAW+'/dd-parent-rule-pair-001.json': '6cabc12043930774842b4017faf9f2e1f733b8a16921648ebb5d783935602018',
    RAW+'/dd210-current210-source-bridge.json': '9a6ad8409fd6b82bb48c8077cd35ba887fc4ac9f228a97a230021b45532ef167',
    STREAM_CHECKER: '50f51f3ec294881e30163a5f96f8197762d979348891631e9d88db3436c46481',
    PARENT_CHECKER: 'df3504e3c21e2bd5b0d5fa67a9877aa9103bf1942bf5d10e8ae6f458fd354115',
}
TESTS = [
    'kernel::source_proofs::duplicate_origin_partial_fraction_and_mass_jet_identity',
    'kernel::source_proofs::n5_D6_scalar_time_and_rank4_UV_contact_are_retained',
    'stream::tests::wire_lift_is_exact_binary64_in_doublefloat',
]


def need(value, why):
    if not value:
        raise ValueError(why)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {'sha256': sha(body), 'bytes': len(body)}


def load(body):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate saved JSON key')
            result[key] = value
        return result
    def reject(value):
        raise ValueError('nonfinite saved JSON token '+value)
    return json.loads(body, object_pairs_hook=pairs, parse_constant=reject)


def safe(name):
    path = PurePosixPath(name)
    need(type(name) is str and name and str(path) == name and not path.is_absolute()
         and '..' not in path.parts, 'safe relative alias')


def unpack(body, selected, complete=False):
    result, seen = {}, set()
    with tarfile.open(fileobj=io.BytesIO(body), mode='r:gz') as archive:
        for item in archive:
            safe(item.name)
            need(item.isfile() and item.name not in seen, 'unique regular archive member')
            seen.add(item.name)
            if item.name in selected:
                need(item.size == selected[item.name]['bytes'], 'selected archived size')
                data = archive.extractfile(item).read()
                need(desc(data) == selected[item.name], 'selected archive member identity')
                need(not data.startswith((b'\x7fELF', b'!<arch>')) and b'S-130-' not in data,
                     'text or saved evidence only; no native artifact or license')
                result[item.name] = data
    need(set(result) == set(selected), 'every selected member present')
    if complete:
        need(seen == set(selected), 'closed own payload inventory')
    return result


def restore_files(manifest):
    own = set(manifest['capsule_files']) | {'manifest.json'}
    need({str(p.relative_to(HERE)) for p in HERE.rglob('*')
          if p.is_file() and '__pycache__' not in p.parts} == own, 'closed own capsule inventory')
    for name, row in manifest['capsule_files'].items():
        safe(name)
        need(desc((HERE/name).read_bytes()) == row, 'own file identity')
    for name, row in manifest['parent_files'].items():
        safe(name)
        need(desc((ROOT/name).read_bytes()) == row, 'shallow parent file identity')
    archives = {}
    for name, row in manifest['direct_archives'].items():
        need(manifest['parent_files'][name] == {k: row[k] for k in ['sha256', 'bytes']},
             'direct archive identity is pinned')
        archives[name] = unpack((ROOT/name).read_bytes(), row['members'])
    delta = unpack((HERE/'payload.tar.gz').read_bytes(), manifest['payload_members'], complete=True)
    files = {}
    for alias, row in manifest['aliases'].items():
        safe(alias)
        if 'archive' in row:
            need(row['archive'] in archives, 'direct borrowed locator')
            body = archives[row['archive']][row['member']]
        else:
            body = delta[row['member']]
        need(desc(body) == {k: row[k] for k in ['sha256', 'bytes']}, 'restored alias identity')
        files[alias] = body
    return files


def replay(manifest, files):
    def read(alias):
        return load(files[alias])

    for alias, digest in PINS.items():
        need(alias in files and sha(files[alias]) == digest, 'exact historical evidence '+alias)
    need(CORE_MANIFEST in manifest['parent_files']
         and sha((ROOT/CORE_MANIFEST).read_bytes()) == CORE_MANIFEST_SHA,
         'direct selected source context manifest403')
    core = load((ROOT/CORE_MANIFEST).read_bytes())
    sources = manifest['compiled_sources']
    built = read(BUILD+'/receipt.json')
    bridge = read(RAW+'/dd210-current210-source-bridge.json')
    need(len(sources) == len(core['compiled_sources']) == len(built['sources']) == 210,
         'actual DD selected210 source context')
    same, different = [], []
    for canonical, row in sources.items():
        safe(canonical)
        need(row['snapshot_alias'] == BUILD+'/source-snapshot/'+canonical,
             'actual DD source snapshot alias')
        identity = {k: row[k] for k in ['sha256', 'bytes']}
        need(desc(files[canonical]) == desc(files[row['snapshot_alias']]) == identity
             and built['sources'][canonical] == row['sha256'], 'actual compiled DD source body')
        need(bridge['locators'][canonical]['sha256'] == row['sha256']
             and bridge['locators'][canonical]['bytes'] == row['bytes'], 'source bridge selected body')
        target = core['compiled_sources'][canonical]
        (same if target['sha256'] == row['sha256'] else different).append(canonical)
    need(len(same) == 208 and sorted(different) == sorted([
         'crates/iregi-rust/src/execution.rs',
         'crates/iregi-rust/src/execution/quadrature_context_tests.rs']),
         '208 shared bodies and two explicitly historical pre-profile-fix bodies')
    need(bridge['selected_sources'] == 210 and bridge['same_actual_body_hashes'] == 208
         and bridge['different_actual_body_hashes'] == 2
         and bridge['fresh_core_context_manifest']['sha256'] == CORE_MANIFEST_SHA
         and bridge['DD_build_receipt']['sha256'] == PINS[BUILD+'/receipt.json'],
         'actual immutable source bridge scope')
    omitted = manifest['omitted_native_artifacts']
    external = manifest.get('external_hash_attestations', {})
    raw_aliases = manifest.get('raw_absolute_aliases', {})
    need(omitted == {
         PREFIX+BUILD+'/frozen-worker': '9ad5834593130961488e8ac530ff4e9aa871b0d6eb01f65b1f95fb4a88ca90d1',
         PREFIX+BUILD+'/frozen-tests': 'af7512fdb9377d3fff8ae2b3688668506c50c91b79fd2407730b8e9133597f86',
         PREFIX+NUMERIC+'/worker-owned': '9ad5834593130961488e8ac530ff4e9aa871b0d6eb01f65b1f95fb4a88ca90d1'},
         'only the three declared native artifacts may use historical digest attestations')
    need(not external, 'all nonbinary external guarded inputs are archived as actual source bodies')
    checked = {'nonbinary_hash_reads': 0, 'omitted_native_hash_attestations': 0,
               'external_hash_attestations': 0}

    def alias_for(path):
        text = str(path)
        if text in raw_aliases:
            alias = raw_aliases[text]
        elif text.startswith(PREFIX):
            alias = text[len(PREFIX):]
        else:
            alias = text
        safe(alias)
        need(alias in files, 'unavailable saved path '+text)
        return alias

    def body_for(path):
        return files[alias_for(path)]

    def path_sha(path):
        text = str(path)
        native_key = text if text.startswith('/') else PREFIX+text
        if native_key in omitted:
            checked['omitted_native_hash_attestations'] += 1
            return omitted[native_key]
        if text in external:
            checked['external_hash_attestations'] += 1
            return external[text]
        checked['nonbinary_hash_reads'] += 1
        return sha(body_for(path))

    for absolute, alias in raw_aliases.items():
        need(absolute.startswith('/') and not absolute.startswith(PREFIX),
             'external raw absolute alias only')
        safe(alias)
        need(alias in files, 'archived external source body')

    def phase(base):
        receipt = read(base+'/receipt.json')
        need(receipt['inputs_unchanged'] is True and receipt['cleanup_errors'] == [],
             'actual terminal guards and cleanup '+base)
        for absolute, digest in receipt['inputs'].items():
            need(path_sha(absolute) == digest, 'terminal saved input '+absolute)
        for name, digest in receipt['outputs'].items():
            need(path_sha(PREFIX+base+'/'+name) == digest, 'terminal saved output '+name)
        need(all(step['status'] == 'exited' and step['returncode'] == 0
                 and step['owned_group_gone'] is True for step in receipt['steps']),
             'all owned native groups terminal and successful')
        return receipt

    built = phase(BUILD)
    need(built['status'] == 'passed_anchor_build_three_exact_tests_and_inventory'
         and built['three_exact_tests'] == TESTS and len(built['steps']) == 6
         and built['integral_evaluation_executed'] is False, 'actual build, three exact proofs and inventory')
    for label, test_profile in [('worker', False), ('tests', True)]:
        product = built['products'][label]
        need(product['path'] in omitted and omitted[product['path']] == product['sha256'],
             'omitted actual native product '+label)
        event = read(BUILD+'/'+product['cargo_event'])
        need(event['reason'] == 'compiler-artifact' and event['executable'] == product['cargo_executable']
             and event['target']['name'] == 'n6_sample_mass_second_dd_oracle'
             and event['profile']['test'] is test_profile, 'actual selected Cargo artifact')
    for filename in ['cargo-worker.log', 'cargo-tests.log']:
        events = []
        for line in files[BUILD+'/'+filename].splitlines():
            try:
                events.append(load(line))
            except (ValueError, UnicodeDecodeError):
                pass
        need([e['success'] for e in events if e.get('reason') == 'build-finished'] == [True],
             'actual successful saved Cargo completion')
    for index, name in enumerate(TESTS):
        step = built['steps'][index+2]
        log = files[BUILD+'/exact-test-'+str(index)+'.log'].decode()
        need(step['command'][-3:] == [name, '--exact', '--nocapture']
             and re.findall(r'^running .*$', log, re.M) == ['running 1 test']
             and 'test '+name+' ... ok' in log
             and re.search(r'^test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; '
                           r'2 filtered out; finished in [0-9.]+s$', log, re.M),
             'actual one-test successful proof '+name)
    inventory = read(BUILD+'/prepared-inventory.json')
    need(sha(files[BUILD+'/prepared-inventory.json']) == built['prepared_inventory_sha256']
         and {key: inventory['execution']['kernel_artifact'][key] for key in
              ['unit', 'f_derivatives', 'geometry_programs', 'gap_taylor_program']}
             == built['instruction_inventory'],
         'actual Symbolica preparation instruction inventory')
    freeze = read(RAW+'/source-freeze-rust.json')
    for absolute, digest in freeze['inputs'].items():
        need(path_sha(absolute) == digest, 'saved source installation guard')
    numeric = phase(NUMERIC)
    need(numeric['status'] == 'passed_full5880_child_parent_capture_replay_still_required'
         and numeric['requested_points'] == 86272 and numeric['resource_observer_terminal'] is True
         and len(numeric['steps']) == 1 and numeric['elapsed_seconds'] <= numeric['total_seconds']
         and numeric['accuracy_qualified'] is False and numeric['default_Hybrid_qualified'] is False
         and numeric['performance_qualified'] is False, 'complete bounded reference only, no core qualification')

    class SavedPath:
        def __init__(self, value):
            self.value = str(value)

        def __str__(self):
            return self.value

        def __truediv__(self, other):
            return SavedPath(self.value.rstrip('/')+'/'+str(other))

        def read_bytes(self):
            return body_for(self.value)

        def read_text(self, encoding='utf-8', errors='strict'):
            return self.read_bytes().decode(encoding, errors)

    def saved_gzip_open(path, mode='rt', encoding=None, errors=None, newline=None):
        need(mode in ['rt', 'rb'], 'read-only saved compressed stream')
        stream = gzip.GzipFile(fileobj=io.BytesIO(body_for(path)), mode='rb')
        return io.TextIOWrapper(stream, encoding=encoding or 'utf-8', errors=errors or 'strict',
                                newline=newline) if mode == 'rt' else stream

    def saved_module(alias):
        namespace = {'__name__': 'frozen_saved_only_'+sha(files[alias]), '__file__': PREFIX+alias}
        exec(compile(files[alias], PREFIX+alias, 'exec'), namespace)
        namespace['Path'] = SavedPath
        namespace['sha'] = path_sha
        return namespace

    stream_module = saved_module(STREAM_CHECKER)
    stream_module['gzip'] = SimpleNamespace(open=saved_gzip_open)
    result = {'status': 'failed_independent_saved_DD_stream_replay', 'findings': []}
    result.update(stream_module['audit'](SavedPath(NUMERIC)))
    result['reviewer_source_sha256'] = PINS[STREAM_CHECKER]
    result['terminal_receipt_sha256'] = PINS[NUMERIC+'/receipt.json']
    expected_stream = read(RAW+'/independent-stream-replay-001.json')
    need(result == expected_stream, 'exact full saved independent stream report replay')
    parent_module = saved_module(PARENT_CHECKER)
    parents = parent_module['dd'](SavedPath(PREFIX+NUMERIC+'/data'))
    comparisons = [parent_module['compare'](parents[0], parents[1], 'two_rule_difference', Fraction(1, 10**10))]
    controls = [parent_module['uv_ir_controls'](parents[index], 'DD_rule'+str(index)) for index in range(2)]
    pair = {'status': 'saved_rule_pair_not_PV_qualification', 'comparisons': comparisons,
            'UV_IR_controls': controls, 'default_Hybrid_qualified': False, 'no_native_evaluation': True,
            'all_passed': all(row['failures'] == 0 for row in comparisons+controls)}
    need(pair == read(RAW+'/dd-parent-rule-pair-001.json') and pair['all_passed'] is True,
         'exact saved all2520 parent two-rule comparison and UV/IR controls')
    return {
        'status': 'passed_saved_full_Dual_DD_defining_integral_reference_replay_core_agreement_pending',
        'selected_actual_DD_source_bodies': 210, 'same_bodies_as_selected_core403_context': 208,
        'historical_source_bodies_explicitly_different': different,
        'build_receipt_sha256': PINS[BUILD+'/receipt.json'], 'three_exact_proof_tests_passed': TESTS,
        'numeric_receipt_sha256': PINS[NUMERIC+'/receipt.json'], 'points': 86272, 'batches': 337,
        'windows': 11, 'complete_complex_fields_per_rule': 5880, 'parent_complex_fields_per_rule': 2520,
        'independent_stream_report_exactly_replayed': True,
        'independent_stream_report_sha256': PINS[RAW+'/independent-stream-replay-001.json'],
        'two_rule_parent_report_exactly_replayed': True,
        'two_rule_parent_report_sha256': PINS[RAW+'/dd-parent-rule-pair-001.json'],
        'parent_two_rule_complex_gates': comparisons[0]['complex_slots'],
        'parent_two_rule_maximum_normalized_error': comparisons[0]['maximum_normalized_error'],
        'parent_UV_IR_controls_per_rule': [row['controls'] for row in controls],
        'saved_path_hash_controls': checked, 'actual_integral_source': 'Symbolica DoubleFloat nominal106',
        'core_agreement': 'PENDING', 'full_rank6_Dual_qualified': False, 'default_Hybrid_qualified': False,
        'full_objective_met': False, 'rigorous_quadrature_error_enclosure': False,
        'raw_payload_regeneration': False, 'complete_dependency_closure_claimed': False,
        'native_execution': False, 'native_artifact_rehash': False, 'new_integral_evaluation': False,
        'performance_qualified': False,
        'scope': 'Archived independent defining-integral reference only. Fixed rules and saved stream checks do not certify core agreement or a rigorous integration error enclosure.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output')
    args = parser.parse_args()
    manifest = load((HERE/'manifest.json').read_bytes())
    result = replay(manifest, restore_files(manifest))
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
