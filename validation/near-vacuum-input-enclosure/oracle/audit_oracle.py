#!/usr/bin/env python3
"""Audit exact recorded numbers and provenance; never rerun oracle integration."""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EXPECTED_SOURCE = 'a12d96533f48983bd38f5835c2085dfcb8579707363371385aabc8df33460081'
EXPECTED_OUTPUT = 'ea6073e9d6bddcc5cff7e401e3c6b50a5e31192ecd8619526f87bec53374e1b6'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    destination = HERE / 'oracle-audit.json'
    assert not destination.exists(), 'Never overwrite an audit result'
    checks = []
    recorded_hashes = {}

    def check(condition, label):
        checks.append({'label': label, 'passed': bool(condition)})

    def hashed(path):
        digest = sha(path)
        recorded_hashes[str(path.relative_to(ROOT))] = digest
        return digest

    def point(value):
        return Q(value['real_exact_rational']), Q(value['imaginary_exact_rational'])

    def add(a, b):
        return a[0]+b[0], a[1]+b[1]

    def mul(a, b):
        return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]

    def norm1(a):
        return abs(a[0])+abs(a[1])

    report = json.loads((HERE/'output.json').read_text())
    build = json.loads((HERE/'build.json').read_text())
    run = json.loads((HERE/'run.json').read_text())
    prep = json.loads((HERE/'source-preparation.json').read_text())
    source = ROOT/'target/near-vacuum-input-enclosure/oracle/five_pinch_oracle.rs'
    binary = source.with_suffix('')
    check(hashed(source) == hashed(HERE/'five_pinch_oracle.rs') == build['source_sha256'] == run['source_sha256'] == prep['source_sha256'] == EXPECTED_SOURCE, 'source bytes match preparation/build/run')
    check(hashed(HERE/'output.json') == run['output_sha256'] == EXPECTED_OUTPUT, 'output bytes match completed run')
    check(hashed(binary) == build['binary_sha256'] == run['binary_sha256'], 'binary bytes match build and run')
    check(hashed(HERE/'build.json') == run['build_manifest_sha256'], 'run binds completed build manifest')
    check(hashed(HERE/'build.log') == build['build_log_sha256'], 'build log hash')
    check(hashed(HERE/'run.log') == run['run_log_sha256'], 'run log hash')
    check(build['exit_code'] == run['exit_code'] == 0, 'build and oracle exit zero')
    check(build['cwd'] == run['cwd'] == str(ROOT), 'project working directory')
    check(build['command'][:3] == run['command'][:3] == ['taskset', '-c', '19'], 'both commands pinned to CPU19')
    check(run['runtime_limit_seconds'] == 120 and '120s' in run['command'], 'bounded runtime')
    check('opt-level=3' in build['command'] and 'lto=thin' in build['command'] and 'embed-bitcode=yes' in build['command'] and 'codegen-units=1' in build['command'], 'optimized compatible ThinLTO flags')
    check(set(build['selected']) == {'symbolica', 'serde_json'}, 'only symbolic and JSON direct dependencies')
    snapshots = [json.loads((HERE/name).read_text()) for name in ['closure-before.json', 'closure-after-build.json', 'closure-after-run.json']]
    check(snapshots[0] == snapshots[1] == snapshots[2], 'full retained closure unchanged across build/run')
    for name, manifest, field in [('closure-before.json', build, 'closure_before_sha256'), ('closure-after-build.json', build, 'closure_after_build_sha256'), ('closure-after-run.json', run, 'closure_after_run_sha256')]:
        check(hashed(HERE/name) == manifest[field], name + ': manifest link')
    check(len(snapshots[0]) == build['closure_files_verified'] == 870, 'complete 870-file closure')
    closure = ROOT/build['dependency_closure']
    actual_paths = {str(path.relative_to(ROOT)) for path in closure.rglob('*') if path.is_file()}
    check(actual_paths == set(snapshots[0]), 'current retained file set equals snapshot')
    for path, digest in snapshots[0].items():
        check(hashed(ROOT/path) == digest, 'current retained byte hash: '+path)
    completion = json.loads((closure/'workspace-completion.json').read_text())
    check(completion['cargo_returncode'] == 0, 'whole workspace Cargo success provenance')
    check(completion['dependency_closure_manifest_sha256'] == hashed(closure/'manifest.json'), 'closure completion manifest link')
    check(completion['workspace_manifest_sha256'] == hashed(closure/'completed-workspace-build.json'), 'whole workspace completion link')
    events = json.loads((closure/'cargo-library-events.json').read_text())
    for name, selected in build['selected'].items():
        matching = [event for event in events if event['target']['name'] == name and event['profile']['opt_level'] == '3' and event['profile']['test'] is False]
        check(len(matching) == 1 and matching[0] == selected['cargo_event'], name+': unique matching optimized non-test event')
        check(hashed(ROOT/selected['retained_archive']) == selected['sha256'], name+': selected archive hash')
    for index, token in enumerate(build['command'][:-1]):
        if token == '-L':
            search = Path(build['command'][index+1].split('=', 1)[1])
            check(search.is_relative_to(closure), 'retained-only dependency/native search '+str(search))

    fixture = report['fixture']
    eta, delta = Q(fixture['eta_exact_rational']), Q(fixture['delta_exact_rational'])
    check(report['status'] == 'exact_five_pinch_oracle_generated', 'successful oracle status')
    check(eta == Q(1,2**64) and delta == Q(1,2**32) and delta*delta == eta, 'tiny exact geometry scale')
    check(Q(fixture['x_exact_rational']) == Q(2,5), 'exact non-dyadic contour point')
    check(point(fixture['t']) == (Q(2,3),Q(-2,3)), 'exact contour t')
    mass = point(fixture['common_shifted_mass_squared'])
    check(mass == (Q(5,3),Q(-2,3)), 'exact shifted mass')
    check(point(fixture['contour_direction']) == (1,-1), 'exact contour direction')
    check(fixture['metric'] == [1,-1,-1,-1], 'Lorentz metric')
    check(Q(fixture['doubled_external_gram_determinant_exact_rational']) == -16*eta**4, 'exact Gram determinant')
    geometry = report['geometry']
    b = [Q(value) for value in geometry['b_exact_rational']]
    check(b == [1/(2+eta)]+[-1/(2*(2+eta))]*4, 'independent Cayley b identities')
    check(Q(geometry['B_exact_rational']) == sum(b) == -1/(2+eta), 'Cayley B identity')
    coefficients = [point(value) for value in geometry['C_i_at_t']]
    a, b_im = Q(10,3)+eta, Q(4,3)
    c0 = (a/(a*a+b_im*b_im), b_im/(a*a+b_im*b_im))
    check(coefficients == [c0]+[(-c0[0]/2,-c0[1]/2)]*4, 'exact shifted Cayley coefficients')
    check(norm1(c0) <= Q(21,58), 'coefficient norm bound')
    metric = fixture['metric']
    routing = [[int(i == mu+1) for mu in range(4)] for i in range(5)]
    distances = [[sum(metric[mu]*(routing[i][mu]-routing[j][mu])**2 for mu in range(4)) for j in range(5)] for i in range(5)]
    for i in range(5):
        check(sum((eta*distances[i][j]-2)*b[j] for j in range(5)) == 1, f'unshifted Cayley row {i}')
        total = (Q(0),Q(0))
        for j in range(5):
            total = add(total, mul((eta*distances[i][j]-2*mass[0],-2*mass[1]),coefficients[j]))
        check(total == (1,0), f'shifted Cayley row {i}')

    L, rho = Q(5,3), Q(3,5)*eta
    check(L*L <= mass[0]**2+mass[1]**2 and 0 < rho < Q(1,4), 'rigorous lower mass norm and analytic radius')
    box_radius = rho**9*(10-9*rho)/(6*L**2*(1-rho)**2)
    pentagon_radius = rho**5*(21-35*rho+15*rho*rho)/(12*L**3*(1-rho)**3)
    edges = [(0,1),(1,2),(2,3),(0,3),(0,2),(1,3)]
    centers, radii = [], []
    check(len(report['boxes']) == 5, 'five pinches present')
    for index, row in enumerate(report['boxes']):
        oracle = row['oracle']
        retained = [i for i in range(5) if i != index]
        check(row['pinch'] == index and oracle['retained_original_propagators'] == retained, f'pinch {index}: routing')
        expected_inputs = [(eta*distances[retained[i]][retained[j]],Q(0)) for i,j in edges]+[mass]*4+[(Q(1),Q(0))]
        check([point(value) for value in row['inputs']] == expected_inputs, f'pinch {index}: all exact scalar inputs')
        check(oracle['series_order_inclusive'] == 8 and oracle['denominator_power'] == 2 and oracle['normalization_factor'] == 1, f'pinch {index}: N8 box normalization')
        check(Q(oracle['simplex_volume_exact_rational']) == Q(1,6), f'pinch {index}: simplex volume')
        check(Q(oracle['rho_exact_rational']) == rho and Q(oracle['lower_mass_norm_exact_rational']) == L, f'pinch {index}: tail parameters')
        radius = Q(oracle['absolute_complex_remainder_bound_exact_rational'])
        check(radius == box_radius and 0 < radius < Q(1,2**320), f'pinch {index}: exact omitted-tail bound')
        check(oracle['remainder_less_than_2_pow_minus_320'] is True, f'pinch {index}: threshold metadata')
        check(0 < oracle['expanded_parameter_terms'] <= 1_000_000, f'pinch {index}: term cap')
        centers.append(point(oracle['center']))
        radii.append(radius)
    pentagon = report['independent_direct_J5_D4']
    check(pentagon['series_order_inclusive'] == 4 and pentagon['denominator_power'] == 3 and pentagon['normalization_factor'] == -2, 'direct pentagon N4 normalization')
    check(pentagon['retained_original_propagators'] == list(range(5)), 'direct pentagon routing')
    check(Q(pentagon['simplex_volume_exact_rational']) == Q(1,24), 'direct pentagon volume')
    check(Q(pentagon['rho_exact_rational']) == rho and Q(pentagon['lower_mass_norm_exact_rational']) == L, 'direct pentagon tail parameters')
    check(Q(pentagon['absolute_complex_remainder_bound_exact_rational']) == pentagon_radius and 0 < pentagon_radius < Q(1,2**320), 'exact pentagon omitted-tail bound')
    check(pentagon['remainder_less_than_2_pow_minus_320'] is True, 'direct pentagon threshold metadata')
    check(0 < pentagon['expanded_parameter_terms'] <= 1_000_000, 'direct pentagon term cap')
    contraction_center = (Q(0),Q(0))
    for coefficient, center in zip(coefficients, centers):
        contraction_center = add(contraction_center, mul(coefficient,center))
    contraction_radius = sum(norm1(c)*r for c,r in zip(coefficients,radii))
    contraction = report['five_box_contraction']
    check(point(contraction['center']) == contraction_center, 'exact five-box numerical contraction center')
    check(Q(contraction['absolute_complex_remainder_bound_exact_rational']) == contraction_radius < Q(1,2**320), 'exact coefficient-weighted contraction radius')
    direct = point(pentagon['center'])
    distance_squared = (contraction_center[0]-direct[0])**2+(contraction_center[1]-direct[1])**2
    combined = contraction_radius+pentagon_radius
    check(Q(contraction['difference_to_direct_series_center_squared_exact_rational']) == distance_squared, 'exact independent-center distance squared')
    check(Q(contraction['combined_remainder_bound_exact_rational']) == combined, 'exact combined radius')
    check(distance_squared <= combined**2 and contraction['independent_enclosures_compatible'] is True, 'independent direct/contraction enclosures overlap')
    mapped = report['mapped_integrand_at_x']
    weight = (Q(25,9),Q(-25,9))
    check(point(mapped['dt_dx']) == weight, 'exact contour Jacobian')
    check(point(mapped['center']) == mul(weight,contraction_center), 'exact mapped center')
    check(Q(mapped['radius_norm_upper_exact_rational']) == norm1(weight) == Q(50,9), 'mapped multiplier norm')
    check(Q(mapped['absolute_complex_remainder_bound_exact_rational']) == norm1(weight)*contraction_radius < Q(1,2**320), 'exact mapped radius and strict target')
    check(mapped['remainder_less_than_2_pow_minus_320'] is True, 'mapped threshold metadata')
    for name in ['audit_oracle.py', 'source-preparation.json', 'build-control-events.jsonl', 'README.md', 'independent-review.md']:
        hashed(HERE/name)
    failures = [row for row in checks if not row['passed']]
    result = {'schema_version': 1, 'status': 'passed' if not failures else 'failed',
              'checks': len(checks), 'failures': failures, 'details': checks,
              'input_hashes': recorded_hashes,
              'scope': 'Exact rational numerical audit of retained oracle output and build/run provenance. No oracle rerun, symbolic integration, candidate evaluation, or production change.',
              'limitations': 'Integrated series centers come from the independently reviewed Symbolica oracle; this audit checks their recorded contraction and rigorous tails without reimplementing symbolic integration. Build wall duration includes the recorded quiet-window pause and is diagnostic only.'}
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':len(checks),'failures':len(failures),'hashes':len(recorded_hashes),'output':str(destination.relative_to(ROOT)),'sha256':sha(destination)}))
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()
