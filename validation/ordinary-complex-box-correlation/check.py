#!/usr/bin/env python3
"""Portable ordinary-box saved evidence replay; Python standard library only."""
from contextlib import redirect_stdout
from pathlib import Path, PurePosixPath
import ast
import hashlib
import io
import json
import re
import sys
import tarfile
import tempfile
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
G = 'target/e6-gh-correlation-repair'
A = 'target/e6-exact-d0-parameter-anchor'
R = 'target/ordinary-gh-parent-requalification'
E = R+'/e6-proposal'
B = 'target/e6-terminal0-precision-trace'
PREFIX = '/shared/external/iregi/iregi-rust/'
TESTS = (
    'box_complex::tests::ordered_shared_line_sum_matches_root_relation_exactly',
    'box_complex::tests::orthogonal_box_line_sum_coefficients_vanish_exactly',
    'box_complex::tests::dual_compiler_keeps_legacy_ordered_body',
    'box_complex::tests::composite_norms_keep_real_comparisons',
    'box_complex::tests::contour_quadratic_roots_preserve_exact_axes',
    'box_complex::tests::complex_box_finite_continuation_regression',
    'dual_transcendentals_keep_doublefloat_and_arbitrary_precision',
    'static_dynamic_dual_agree_and_keep_taylor_components',
    'finite_triangle_and_box_dual_homogeneity',
    'lightlike_bubble_jets_and_threshold_errors_are_preserved',
)


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {'sha256': sha(body), 'bytes': len(body)}


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
    require(name and not p.is_absolute() and '..' not in p.parts and str(p) == name,
            'canonical project-relative path')


def restore_files(manifest):
    own = {str(p.relative_to(HERE)) for p in HERE.rglob('*')
           if p.is_file() and '__pycache__' not in p.parts}
    require(own == set(manifest['capsule_files']) | {'manifest.json'}, 'closed capsule inventory')
    for name, expected in manifest['capsule_files'].items():
        safe(name)
        require(desc((HERE / name).read_bytes()) == expected, 'exact capsule file: ' + name)
    members = {}
    with tarfile.open(fileobj=io.BytesIO((HERE / 'payload.tar.gz').read_bytes()), mode='r:gz') as archive:
        for item in archive:
            safe(item.name)
            require(item.isfile() and item.name not in members, 'unique regular archive member')
            body = archive.extractfile(item).read()
            require(desc(body) == manifest['payload_members'].get(item.name), 'exact archived bytes')
            require(item.name == 'objects/' + sha(body), 'content-addressed object name')
            require(not body.startswith((b'\x7fELF', b'!<arch>\n')) and not re.search(
                rb'S-[0-9]{3}-[0-9]{4}[.][0-9]{2}[.][0-9]{2}-[A-Z2-7]{20,}', body),
                'no compiled product or literal license')
            members[item.name] = body
    require(set(members) == set(manifest['payload_members']), 'closed archive inventory')
    files = {}
    for alias, row in manifest['aliases'].items():
        safe(alias)
        body = members[row['member']]
        require(desc(body) == {k: row[k] for k in ('sha256', 'bytes')}, 'exact canonical alias')
        files[alias] = body
    require(set(members) == {r['member'] for r in manifest['aliases'].values()}, 'no unreferenced object')
    for name in own:
        files[manifest['capsule_directory'] + '/' + name] = (HERE / name).read_bytes()
    return files


def replay(files, manifest):
    require(__debug__, 'independent saved checker uses assertions; do not use Python -O')
    require(manifest['qualification'] == {
        'ordinary_Symbolica_repair_source_and_regressions': True,
        'one_copied_D0_two_rule_value_anchor': True,
        'one_actual_E6_kernel_convergence': True,
        'E6_or_parent_tensor': False, 'new_Dual_domain': False,
        'native_or_generated_backend': False, 'Float256_accuracy_certified': False,
        'quadrature_error_bound_certified': False, 'performance': False,
    }, 'strictly scoped qualification')
    read = lambda name: load(files[name])
    omitted = manifest['omitted_native_artifacts']
    # These are historical receipt claims, never reconstructed or rehashed ELFs.
    for path, digest in omitted.items():
        require(path.startswith(PREFIX) and re.fullmatch('[0-9a-f]{64}', digest), 'explicit omitted artifact identity')
    for receipt_alias in manifest['receipts']:
        receipt = read(receipt_alias)
        directory = receipt_alias.rsplit('/', 1)[0]
        require(receipt.get('inputs_unchanged') is True and receipt.get('cleanup_errors') == []
                and receipt.get('cancellation') is None and receipt.get('post_cancellation') is None,
                'saved clean unchanged terminal context: ' + receipt_alias)
        for name, digest in receipt.get('outputs', {}).items():
            alias = directory + '/' + name
            require((alias in files and sha(files[alias]) == digest)
                    or omitted.get(PREFIX + alias) == digest, 'saved output or explicit omitted native product')
        for step in receipt.get('steps', []):
            require(step['owned_group_gone'] is True, 'saved owned group cleanup, not a live probe')
        for source, alias in manifest['selected_source_contexts'].get(receipt_alias, {}).items():
            require(sha(files[alias]) == receipt['source_files'][source], 'selected actual build snapshot')
    for receipt_alias, bindings in manifest['selected_input_bindings'].items():
        receipt = read(receipt_alias)
        for absolute, alias in bindings.items():
            require(sha(files[alias]) == receipt['inputs'][absolute], 'selected unchanged receipt input')

    snapshots = [G + '/build-' + n + '/source-snapshot/dependencies/oneloopmaster/src/box_complex.rs'
                 for n in ('001', '003', '004')]
    prefix = lambda body: body.split(b'\n#[cfg(test)]\n', 1)[0]
    require(len({prefix(files[p]) for p in snapshots + ['dependencies/oneloopmaster/src/box_complex.rs']}) == 1,
            'all historical test-only corrections preserve ordinary production prefix')
    require(sha(prefix(files[snapshots[-1]])) == manifest['production_prefix_sha256'], 'fixed production prefix')
    expression_alias = 'dependencies/oneloopmaster/src/expressions.rs'
    require(all(files[expression_alias] == files[G + '/build-' + n + '/source-snapshot/' + expression_alias]
                for n in ('001', '003', '004')), 'unchanged full Dual-map replacement source')
    for build in (G+'/build-003', G+'/build-004', A+'/build-001',R+'/build-001',B+'/build-002'):
        receipt = read(build+'/receipt.json')
        require(receipt['status'] == 'passed' and receipt['steps']
                and all(step['returncode'] == 0 for step in receipt['steps']), 'actual saved successful Cargo commands')
        for product in receipt['products'].values():
            event = read(build+'/'+product['cargo_event'])
            require(event['reason'] == 'compiler-artifact' and event['executable'] == product['cargo_executable']
                    and omitted[product['path']] == product['sha256'], 'actual Cargo artifact and omitted frozen identity')

    normal = read(G+'/normal-001/receipt.json')
    require(normal['status'] == 'passed' and len(normal['steps']) == 12, 'actual ten regressions plus two listings')
    for index, name in enumerate(TESTS):
        family, ordinal = ('test',index) if index < 6 else ('master-test',index-6)
        text = files[f'{G}/normal-001/{family}-{ordinal}.log'].decode()
        listing = files[G+'/normal-001/'+('listing.log' if index < 6 else 'masters-listing.log')].decode()
        require(len(re.findall(r'^running 1 test$', text, re.M)) == 1
                and len(re.findall(r'^test '+re.escape(name)+r' \.\.\. ok$', text, re.M)) == 1
                and len(re.findall(r'^test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; \d+ filtered out; finished in .+$', text, re.M)) == 1,
                'strict exact singleton success: '+name)
        require(listing.splitlines().count(name+': test') == 1, 'exact listed test')
        step = normal['steps'][index+2]
        require(step['returncode'] == 0 and step['command'][step['command'].index('--exact')+1] == name
                and '--ignored' not in step['command'], 'actual exact selected command')
    require(normal['actual_product'] == read(G+'/build-003/receipt.json')['products']['library-tests'],
            'regressions joined to actual build003 product')
    minimal = read(G+'/diagnostic-minimal-001/receipt.json')
    require(minimal['status'] == 'passed' and minimal['actual_product'] == read(G+'/build-004/receipt.json')['products']['library-tests']
            and all(s['returncode'] == 0 for s in minimal['steps']), 'actual minimal build004 observer complete')
    require(sha(files[G+'/build-001/receipt.json']) == 'f879266878a3365fcb7139a878253fe9bef66648eec849bdc8d2ca4bdc505424'
            and read(G+'/build-001/receipt.json')['steps'][0]['returncode'] == 101, 'first compiler failure retained')
    preflight = read(G+'/build-002/receipt.json')
    require(sha(files[G+'/build-002/receipt.json']) == '3dee3a7d95a89e5038f6b92653b8819ef91446f9e873b53a701e4668c8136a0a'
            and preflight['status'] == 'failed' and preflight['steps'] == [], 'preflight-only failure retained')
    broad = read(G+'/diagnostic-001/receipt.json')
    require(sha(files[G+'/diagnostic-001/receipt.json']) == '671e77adc3d37c259cfe94c9001612a302dfba64a61fe75a3cde4f62c7c983c2'
            and broad['status'] == 'failed_or_incomplete' and broad['steps'][1]['timeout'] is True,
            'broad observer preparation timeout never upgraded')

    # Only saved stdlib arithmetic/checker sources execute, in a disposable tree.
    # No producer/controller/native code is imported or invoked.
    with tempfile.TemporaryDirectory(prefix='ordinary-d0-saved-') as tmp:
        root = Path(tmp)
        for alias, body in files.items():
            path = root / alias
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        checker = types.ModuleType('frozen_minimal_trace_checker')
        exec(compile(files[G+'/check_tsv_minimal.py'],'<saved trace parser>','exec'), checker.__dict__)
        audit = checker.audit(root/G/'diagnostic-minimal-001/trace.tsv',root/G/'early-D0-input.tsv')
        require(audit == read(G+'/diagnostic-minimal-001/trace-audit.json'), 'exact complete staged trace replay')
        comparator = types.ModuleType('frozen_one_D0_saved_comparator')
        exec(compile(files[A+'/compare_saved.py'],'<saved Fraction comparator>','exec'),comparator.__dict__)
        actual = comparator.audit(root/A/'capture-001/result.json',root/G/'diagnostic-minimal-001/trace.tsv',
                                  root/G/'early-D0-input.tsv',root/A/'capture-001/rules.tsv')
        require(actual == read(A+'/capture-001/comparison.json') and actual['failures'] == [], 'exact six scalar coefficients and four rule pairs replay')
        independent_alias = A+'/independent-saved-review/check.py'
        require(sha(files[A+'/independent-saved-review/review.json']) == 'ad633af0d01b421808b6b01712fa418005b0f123b1b617da350c0f9135c8a2f7', 'independent saved review identity')
        # Its top-level program hard-codes original absolute receipt keys, so
        # replay only its unchanged import/function AST nodes, then reconstruct
        # the same ten checks explicitly from the canonical saved records.
        tree = ast.parse(files[independent_alias])
        helpers = ast.Module(body=[node for node in tree.body if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[])
        namespace = {}
        exec(compile(helpers,'<unchanged independent saved arithmetic helpers>','exec'),namespace)
        output = read(A+'/capture-001/result.json')
        independent = read(A+'/independent-saved-review/review.json')
        independent_checks = []
        c,error2 = namespace['c'],namespace['error2']
        fixed = audit['full_fixed_D0']
        for result in output['results']:
            for slot,new_slot in enumerate((3,1,2)):
                error = error2(c(result['oneloop_raw_slots'][new_slot]),c(fixed[slot]))
                independent_checks.append({'kind':f"order{result['order']}_raw_slot{slot}",
                                           'normalized_error_squared':str(error),'gate':'1e-10'})
        for slot in range(4):
            error = error2(c(output['results'][0]['oneloop_raw_slots'][slot]),c(output['results'][1]['oneloop_raw_slots'][slot]))
            independent_checks.append({'kind':f'fixed_rule_pair_slot{slot}','normalized_error_squared':str(error),'gate':'1e-12'})
        require(independent_checks==independent['checks'], 'all ten unchanged independent Fraction arithmetic checks replay')
        maximum = max(namespace['Q'](row['normalized_error_squared']) for row in independent_checks)
        require(namespace['decimal_sqrt'](maximum)==independent['maximum_normalized_error'], 'independent arithmetic maximum replay')
        require(files[E+'/check_trace.py'] == files[B+'/check_trace.py'], 'unchanged E6 trace checker')
        trace_checker = types.ModuleType('frozen_old_and_new_E6_trace_checker')
        exec(compile(files[E+'/check_trace.py'],'<saved E6 trace checker>','exec'),trace_checker.__dict__)
        e6_reports = []
        for base in (B,E):
            result = trace_checker.audit(root/base/'capture-001/trace.jsonl')
            require(result == read(base+'/capture-001/trace-audit.json'), 'exact old/new full E6 trace audit replay')
            e6_reports.append(result)
        nodes_checker = types.ModuleType('frozen_same_node_metadata_checker')
        exec(compile(files[E+'/compare_nodes_saved.py'],'<saved identical node metadata>','exec'),nodes_checker.__dict__)
        nodes = nodes_checker.audit(root/B/'capture-001/trace.jsonl',root/E/'capture-001/trace.jsonl')
        require(sha(files[E+'/capture-001/same-node-comparison.json'])=='f816196b345122755c01f9902d7f3564b583a67feaa144412857edadd4279213'
                and nodes==read(E+'/capture-001/same-node-comparison.json'), 'exact all600same-node metadata replay')
    capture = read(A+'/capture-001/receipt.json')
    require(capture['status'] == 'passed_one_exact_D0_value_anchor' and capture['point_count'] == 1
            and sum(result['points'] for result in read(A+'/capture-001/result.json')['results'])==40768
            and capture['orders'] == [20,32] and capture['actual_product'] == read(A+'/build-001/receipt.json')['products']['worker']
            and all(s['returncode'] == 0 for s in capture['steps']), 'exact finite two-rule anchor context')
    old,new = e6_reports
    require(old['kernel_returned_success'] is False and old['final_kernel_error']=='NonConvergent'
            and old['orders']==[8,16,32,64,128] and old['D0_rows']==1240
            and len(old['low_precision_nonzero_box_components'])==488, 'original E6 failure and precision collapse preserved')
    require(new['kernel_returned_success'] is True and new['final_kernel_error'] is None
            and new['orders']==[8,16,32,64] and new['D0_rows']==600
            and new['low_precision_nonzero_box_components']==[], 'actual repaired E6 convergence, no low-precision nonzero box components')
    e6_receipt = read(E+'/capture-001/receipt.json')
    require(sha(files[E+'/capture-001/receipt.json'])=='234ec3a42f787d5aab7a355f583ab3b351eb40b7734c4edec3db48319c1787ce'
            and e6_receipt['status']=='diagnostic_capture_complete' and e6_receipt['kernel_returned_success'] is True
            and all(s['returncode']==0 for s in e6_receipt['steps']), 'actual patched E6 saved terminal receipt')
    acceptance = read(E+'/capture-001/acceptance.json')
    fresh = read(R+'/build-001/receipt.json')
    require(acceptance['status']=='passed_one_patched_E6_scalar_kernel'
            and acceptance['binary_sha256']==fresh['products']['masters-tests']['sha256']=='007c4e33808627bf3daac4dc300d61233c327eb1bf12890073f905d98478e93e'
            and acceptance['trace_sha256']==sha(files[E+'/capture-001/trace.jsonl'])
            and acceptance['independent_integral_accuracy_qualified'] is False
            and acceptance['full_N6_fix_or_precision_pair_qualified'] is False, 'actual fresh master artifact; convergence separate from independent integral/parent acceptance')
    return {'status':'passed_portable_ordinary_box_and_E6_convergence_saved_evidence', 'restored_aliases':len(files),
            'strict_regressions':10,'copied_input_components':22,'raw_D0_coefficients_against_anchor':6,
            'raw_rule_pairs':4,'native_and_raw_complex_pole_controls':12,
            'maximum_normalized_error':actual['maximum_normalized_error'],
            'old_E6_kernel_returned_success':False,'old_E6_D0_rows':1240,
            'new_E6_kernel_returned_success':True,'new_E6_D0_rows':600,'new_E6_orders':[8,16,32,64],
            'new_E6_error_estimate':new['final_error_estimate']['display'],
            'identical_old_new_D0_input_components':nodes['identical_input_real_components'],
            'unchanged_finite_D0_records':nodes['bitwise_identical_finite_result_records'],
            'changed_finite_D0_records':nodes['changed_finite_result_records'],
            'independent_saved_arithmetic_helpers_replayed':True,'independent_top_level_script_reexecuted':False,
            'preserved_failures':['initial exact-test E0282 compiler failure','preflight-only missing file','447-output observer preparation timeout','original E6 NonConvergent'],
            'E6_or_parent_tensor_qualified':False,'new_Dual_domain_qualified':False,'native_or_generated_backend_qualified':False,
            'Float256_accuracy_certified':False,'quadrature_error_bound_certified':False,'performance_qualified':False,
            'compiler_or_integral_producer_or_live_process_probe_executed':False}


if __name__ == '__main__':
    manifest = load((HERE/'manifest.json').read_bytes())
    result = replay(restore_files(manifest),manifest)
    result['manifest_sha256'] = sha((HERE/'manifest.json').read_bytes())
    print(json.dumps(result,indent=2))
