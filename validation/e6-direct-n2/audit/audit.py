#!/usr/bin/env python3
"""Audit emitted scalar rational bounds and frozen provenance; no symbolic work."""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'target/e6-direct-n2'
HERE = Path(__file__).resolve().parent
ORACLE_SHA = '0cf780289cf24e409aebc27d4cc51ccca3e4c02d386b4198cf16f0656cc974c3'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    destination = HERE/'result.json'
    assert not destination.exists(), 'Preserve completed audit evidence'
    checks, hashes = [], {}

    def check(value, label):
        checks.append({'label':label, 'passed':bool(value)})

    def hashed(path):
        digest = sha(path)
        hashes[str(path.relative_to(ROOT))] = digest
        return digest

    def read(name):
        return json.loads((BASE/name).read_text())

    output, run, build = read('output.json'), read('run.json'), read('build.json')
    prep, sources, review = read('preparation.json'), read('source-manifest.json'), read('review-before-compute.json')
    oracle, upstream = read('series-oracle.json'), read('upstream-preparation.json')
    check(run['exit_code'] == build['exit_code'] == 0, 'build and runtime succeeded')
    check(hashed(BASE/'output.json') == run['output_sha256'], 'runtime output hash')
    check(hashed(BASE/'build.json') == run['build_sha256'], 'runtime binds completed build')
    check(hashed(BASE/'validate') == run['binary_sha256'] == build['binary_sha256'], 'actual binary bound by build/runtime')
    check((BASE/'validate').stat().st_size == build['binary_bytes'], 'binary size')
    check(hashed(BASE/'source-manifest.json') == run['source_manifest_sha256'], 'source manifest runtime binding')
    check(build['sources'] == sources == review['source_sha256'], 'review/build/frozen source maps identical')
    check(set(sources) == {str(path.relative_to(ROOT)) for path in (BASE/'source').iterdir() if path.is_file()}, 'complete frozen source file set')
    for path, digest in sources.items():
        check(hashed(ROOT/path) == digest, 'actual reviewed built source: '+path)
    check(hashed(BASE/'preparation.json') == build['preparation_sha256'], 'frozen dependency preparation build link')
    check(hashed(BASE/'upstream-preparation.json') == prep['upstream_preparation_sha256'], 'upstream artifact preparation link')
    check(hashed(BASE/'series-oracle.json') == prep['oracle_sha256'] == run['oracle_sha256'] == ORACLE_SHA, 'frozen independent oracle hash')
    check(hashed(ROOT/'validation/shifted-pentagon/series-oracle.json') == ORACLE_SHA, 'frozen oracle byte-identical to retained independent reference')
    check(hashed(BASE/'source/near_vacuum_d0_original.rs') == prep['d0_source_sha256'] == review['production_base_sha256'], 'frozen original D0 source provenance')
    check(prep['d0_source_sha256'] == upstream['source_sha256']['crates/iregi-masters/src/near_vacuum.rs'], 'frozen D0 original matches upstream Cargo source revision')
    for stage, record in [('build',build),('run',run)]:
        check(hashed(BASE/f'{stage}.py') == record['runner_sha256'], stage+': runner hash')
        check(hashed(BASE/f'{stage}.log') == record[f'{stage}_log_sha256'], stage+': log hash')
        check(record['sources_unchanged'] and record['closure_unchanged'], stage+': captured pre/post source and dependency checks')
    check(build['command'][:3] == ['taskset','-c','18,19'], 'build CPU18/19 affinity')
    expected_build = ['taskset','-c','18,19','rustc','--edition=2024','--crate-name','e6_direct_n2_validate',
                      str(BASE/'source/validate.rs'),'-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo',
                      '-L',f'dependency={BASE/"deps"}','-L',f'native={BASE/"native"}']
    for name, artifact in prep['artifacts'].items():
        expected_build += ['--extern',f'{name}={ROOT/artifact["frozen"]}']
    expected_build += ['-o',str(BASE/'validate')]
    check(build['command'] == expected_build, 'complete exact build command with frozen source/output/dependencies')
    check(run['command'] == ['taskset','-c','18',str(BASE/'validate'),str(BASE/'series-oracle.json'),str(BASE/'output.json')], 'exact runtime binary/input/output command')
    check(build['timeout_seconds'] == 180 and run['timeout_seconds'] == 120, 'bounded build/runtime policies')
    check(run['environment_overrides'] == {'RAYON_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}, 'single-thread runtime environment')
    check(build['compile_environment_overrides'] == {'CARGO_CRATE_NAME':'e6_direct_n2_validate'}, 'explicit compile crate environment')
    check('opt-level=0' in build['command'] and 'debuginfo=0' in build['command'], 'diagnostic private build optimization recorded')
    frozen = {item['frozen']:item for item in prep['files']}
    check(len(frozen) == len(prep['files']) == 116, '116 unique frozen dependency/native files')
    actual = {str(path.relative_to(ROOT)) for directory in ['deps','native'] for path in (BASE/directory).iterdir() if path.is_file()}
    check(set(frozen) == actual, 'complete retained dependency/native file set')
    for path, item in frozen.items():
        check(hashed(ROOT/path) == item['sha256'], 'frozen dependency bytes: '+path)
        check((ROOT/path).stat().st_size == item['bytes'], 'frozen dependency size: '+path)
    for name, artifact in prep['artifacts'].items():
        check({key:value for key,value in artifact.items() if key != 'frozen'} == upstream['artifacts'][name], 'selected archive metadata matches upstream provenance: '+name)
        check(artifact['frozen'] in frozen and artifact['sha256'] == frozen[artifact['frozen']]['sha256'], 'selected archive retained: '+name)
        check(artifact['event']['target']['name'] == name and artifact['event']['profile']['test'] is False, 'selected non-test Cargo artifact: '+name)
        check(artifact['first_object_magic'] == '7f454c46' and artifact['native_object_members'] > 0, 'native-object artifact evidence: '+name)
        check(f'{name}={ROOT/artifact["frozen"]}' in build['command'], 'build uses selected retained archive: '+name)
    for index, argument in enumerate(build['command'][:-1]):
        if argument == '-L':
            check(Path(build['command'][index+1].split('=',1)[1]).is_relative_to(BASE), 'private-only link search: '+build['command'][index+1])
    for filename, field in [('Cargo.lock','Cargo.lock'),('Cargo.toml','Cargo.toml')]:
        check(hashed(BASE/filename) == upstream['source_sha256'][field], 'frozen upstream '+filename)
    check(hashed(ROOT/upstream['cargo_build_log']) == upstream['cargo_build_log_sha256'], 'upstream Cargo build log provenance')
    check(hashed(ROOT/upstream['cargo_qualification']) == upstream['cargo_qualification_sha256'], 'upstream Cargo qualification provenance')
    check(review['status'] == 'passed_source_only_review_before_compute' and not review['unresolved_material_source_findings'], 'source review complete without unresolved material finding')
    check(review['transformation_replay']['replayed_output_byte_identical_to_candidate'], 'reviewed algebra delegation transformation replay')

    check(output['status'] == 'passed_private_direct_e6_n2', 'private candidate pass status')
    check(output['working_bits'] == 256 and output['requested_bits'] == 128, '256 working /128 requested precision')
    check(output['series_order'] == 2 and output['shape'] == [[0],[1],[2],[3]], 'N2 with four native one-axis Taylor components')
    expected_names = ['retained_tiny','same_tiny_different_mu_and_mu_jet','vacuum','outside_radius','upper_mass','invalid_mu','vacuum_unit_mass_jet_cubic_rejected','vacuum_small_mass_jet','nonreal_invariant']
    lanes = output['lanes']
    check([row['name'] for row in lanes] == expected_names, 'all nine named lanes in expected order')
    check(len(lanes) == output['physical_rows'] == 9, 'nine physical sample rows')
    results = [row['result'] for row in lanes]
    successful = [index for index, row in enumerate(results) if row['status'] == 'Success']
    check(successful == [0,1,2,7] and len(successful) == output['success_rows'] == 4, 'exact four successful lanes')
    check(len(lanes)-len(successful) == output['rejected_rows'] == 5, 'exact five rejected lanes')
    for index in [3,4,5,6,8]:
        check(results[index]['values'] is None, f'lane {index}: rejected values hidden')
    check(results[3]['status'] == 'OutsideAnalyticDomain' and Q(results[3]['rho']) == Q(2,5), 'outside-radius rejection at rho2/5')
    for index in [4,5,8]:
        check(results[index]['status'].startswith('InvalidInput(') and results[index]['bounds'] == [] and results[index]['rho'] is None, f'lane {index}: invalid physical input rejection')
    check(results[0] == results[1], 'mu_squared and mu jet changes leave entire result identical')
    check(output['execution'] == {'packed_rows':8,'active_rows':5,'numeric_batch_calls':1,'enclosure_batch_calls':1,'tail_batch_calls':1}, 'one instruction-major batch call per evaluator over five active/eight packed lanes')
    check(output['empty_reverse_independent_workspace'] == 'passed', 'reported empty/reverse independent-workspace control')
    check(output['malformed_physical_length'] == output['oversized_shape'] == 'rejected', 'reported malformed input and oversized shape controls')

    entry = next(row for row in oracle['approximations'] if row['order_in_eta_inclusive'] == 4)
    center, radius = Q(entry['center_exact_rational']), Q(entry['absolute_remainder_bound_exact_rational'])
    eta = Q(oracle['fixture']['eta_exact_rational'])
    check(oracle['status'] == 'exact_oracle_generated' and eta == Q(1,2**64), 'independent tiny oracle fixture')
    check(oracle['schema_version'] == 1, 'pinned oracle schema')
    check(oracle['normalization'] == 'J1 = - integral_simplex F^-2 dx; native OneLoop slots [UV,IR,IR2,finite]=[0,0,0,J1]', 'pinned D6 scalar normalization')
    check([Q(value) for value in oracle['fixture']['mass_squared']] == [Q(1)]*5, 'pinned oracle five unit squared masses')
    check([Q(value) for value in oracle['fixture']['squared_distances_lexicographic_i_less_than_j']] == [eta,-eta,-eta,-eta,Q(0),Q(0),Q(0),-2*eta,-2*eta,-2*eta], 'pinned oracle exactly ten ordered invariants')
    check(Q(oracle['fixture']['mu_squared']) == 1 and oracle['fixture']['metric'] == [1,-1,-1,-1], 'pinned oracle scale and metric')
    check(radius == eta**5*(6-5*eta)/(24*(1-eta)**2) and 0 < radius < Q(1,2**321), 'retained N4 oracle exact scalar tail and strict bound')
    check(Q(entry['lower_bound_exact_rational']) == center-radius and Q(entry['upper_bound_exact_rational']) == center+radius, 'retained oracle interval endpoints')
    independent_centers = {
        0:[center,Q(0),Q(0),Q(0)], 1:[center,Q(0),Q(0),Q(0)],
        2:[Q(-1,24),Q(0),Q(0),Q(0)],
        7:[Q(-1,24),eta/12,-eta**2/8,eta**3/6],
    }
    comparison_names = {0:'retained_tiny',1:'scale_transport',2:'vacuum',7:'small_mass_jet'}
    epsilon_squared = Q(1,2**256)
    component_reports = []
    for index in successful:
        lane = results[index]
        values, bounds = lane['values'], lane['bounds']
        comparisons = output['independent_oracle_comparisons'][comparison_names[index]]
        check(len(values) == len(bounds) == len(comparisons) == 4, f'lane {index}: complete four-component arrays')
        check(Q(lane['rho']) == (Q(4,5)*eta if index in [0,1] else Q(0)), f'lane {index}: independent primal convergence envelope')
        for component, (value, bound, comparison) in enumerate(zip(values,bounds,comparisons)):
            label = f'lane {index} component {component}'
            re, im = Q(value['real']),Q(value['imaginary'])
            rl,ru = map(Q,bound['real_interval'])
            il,iu = map(Q,bound['imaginary_interval'])
            oracle_center = independent_centers[index][component]
            oracle_radius = radius if index in [0,1] and component == 0 else Q(0)
            check(comparison['component'] == component, label+': explicit coefficient ordering')
            check(Q(comparison['oracle_center']) == oracle_center and Q(comparison['oracle_radius']) == oracle_radius, label+': independent oracle values')
            check(rl <= ru and il <= iu and Q(bound['truncation']) >= 0, label+': valid candidate rectangle and tail')
            numeric_error = (abs(re-oracle_center)+oracle_radius)**2+abs(im)**2
            rectangle_error = (max(abs(rl-oracle_center),abs(ru-oracle_center))+oracle_radius)**2+max(abs(il),abs(iu))**2
            output_error = max(abs(re-rl),abs(re-ru))**2+max(abs(im-il),abs(im-iu))**2
            allowed = epsilon_squared*max(Q(1),re*re+im*im)
            check(Q(comparison['numeric_error_squared_upper']) == numeric_error, label+': recomputed numeric/oracle error')
            check(Q(comparison['rectangle_error_squared_upper']) == rectangle_error, label+': recomputed full rectangle/oracle error')
            check(Q(bound['maximum_error_squared']) == output_error, label+': recomputed output/rectangle error')
            check(Q(bound['allowed_error_squared']) == Q(comparison['allowed_error_squared']) == allowed, label+': explicit mixed absolute/relative budget')
            check(numeric_error <= allowed and rectangle_error <= allowed and output_error <= allowed, label+': all three accuracy gates pass')
            check(rl <= oracle_center-oracle_radius and ru >= oracle_center+oracle_radius and il <= 0 <= iu, label+': full real oracle interval contained')
            check(rl <= re <= ru and il <= im <= iu, label+': returned point in candidate rectangle')
            component_reports.append({'lane':index,'component':component,'all_budgets_passed':numeric_error <= allowed and rectangle_error <= allowed and output_error <= allowed,'full_oracle_interval_contained':rl <= oracle_center-oracle_radius and ru >= oracle_center+oracle_radius and il <= 0 <= iu})
    rejected = results[6]
    check(rejected['status'] == 'UncertifiedComponent(3)' and Q(rejected['rho']) == 0 and len(rejected['bounds']) == 4, 'unit mass jet rejected exactly cubic component at zero primal rho')
    unit_centers = [Q(-1,24),Q(1,12),Q(-1,8),Q(1,6)]
    check(Q(output['independent_oracle_comparisons']['unit_mass_jet_rejected_cubic_exact']) == Q(1,6), 'independent unit mass cubic identity')
    for component,bound in enumerate(rejected['bounds']):
        rl,ru = map(Q,bound['real_interval']);il,iu = map(Q,bound['imaginary_interval'])
        check(rl <= unit_centers[component] <= ru and il <= 0 <= iu, f'rejected unit jet component {component}: exact identity enclosed')
        check(Q(bound['allowed_error_squared']) == epsilon_squared, f'rejected unit jet component {component}: explicit budget')
        check((Q(bound['maximum_error_squared']) <= epsilon_squared) == (component < 3), f'rejected unit jet component {component}: correct first failed budget')
    check(Q(rejected['bounds'][3]['truncation']) >= Q(1,6), 'zero-rho full Taylor tail covers independent cubic1/6')
    check(all(Q(bound['truncation']) == 0 for bound in rejected['bounds'][:3]), 'unit-jet lower-order truncation zero')
    check(Q(results[7]['values'][3]['real']) == 0 and independent_centers[7][3] > 0, 'small cubic accepted only within explicit absolute error; not asserted exact zero')
    check(Q(results[7]['bounds'][3]['truncation']) >= independent_centers[7][3], 'small-jet cubic tail covers its nonzero exact value')

    # Static source anchors are evidence bindings, not a substitute for traces.
    driver = (BASE/'source/validate.rs').read_text()
    anchors = ['assert_eq!(lane_json(a),lane_json(b))','assert!(physical_batch(&mut other,&[],0,&accuracy)?.is_empty())',
               'assert!(physical_batch(&mut workspace,&input[..EXTERNAL_WIDTH-1],1,&accuracy).is_err())',
               'assert_eq!(v.re.exact_rational().as_ref(),Some(&e.re))','assert_eq!(v.im.exact_rational().as_ref(),Some(&e.im))',
               'rows[1][15*COMPONENTS] = real(Rational::from(4))','rows[1][15*COMPONENTS+1] = real(Rational::from(7))',
               'assert_eq!(execution.numeric_batch_calls,1)','assert_eq!(execution.enclosure_batch_calls,1)','assert_eq!(execution.tail_batch_calls,1)']
    for anchor in anchors:
        check(anchor in driver,'source/runtime assertion present: '+anchor)
    for name in ['run.json','review-before-compute.json']:
        hashed(BASE/name)
    hashed(Path(__file__).resolve())
    failures = [row for row in checks if not row['passed']]
    result = {'schema_version':1,'status':'passed' if not failures else 'failed','checks':len(checks),'failures':failures,
              'details':checks,'accepted_component_checks':component_reports,'input_hashes':hashes,
              'scope':'Private direct E6 N2 exact rational audit of sixteen successful Taylor components, five failure lanes, frozen tiny oracle, common-mass identity, and source/build/run/binary/dependency provenance. No Symbolica runtime, build or symbolic algebra was performed.',
              'limits':['Single retained routing and common-mass jets; no public/core E6 qualification.',
                        'Reversed/empty execution and counters are bound reviewed source/runtime assertions; full reversed traces are not serialized. Independent workspaces were exercised sequentially, not concurrently.',
                        'The independent frozen oracle supplied its Symbolica-integrated center; this checker audits emitted scalar tails and numerical bounds without reimplementing integration.',
                        'Runtime duration is diagnostic only; no performance claim.']}
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':len(checks),'failures':len(failures),'hashes':len(hashes),'components':len(component_reports),'output':str(destination.relative_to(ROOT)),'sha256':sha(destination)}))
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()
