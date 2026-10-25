"""Saved-only full-array gates. The finite parent owns deadlines and provenance."""
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path('/shared/external/iregi/iregi-rust')
HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
QUAD = ROOT / 'target/quad-iregi-source-audit/future-positive-rank-requests'
QUAD_AUDIT_SHA = 'f0b8f0774d901957fac3369165212b0efac3bf6921cea3c940269f191af373fd'
FIXTURE_SHA = '6c78096e83a399acd111137115505eae10da620b9dd68b6ead56eb2fa06489d2'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(), parse_float=str)


def capture(path, rank, bits, fixture, helper):
    d = load(path)
    assert d['status'] == 'all_lanes_success' and d['lane_statuses'] == ['Success']
    assert d['private_validation_overlay'] is True and d['public_positive_rank_support'] is False
    assert d['independent_reference_qualified'] is False
    assert d['working_bits'] == bits and d['requested_bits'] == 53
    assert d['rows'] == d['components'] == 1 and d['parameter_count'] == 36
    assert d['basis'] == helper.canonical_basis(rank)
    assert d['settings'] == dict(propagators=7, rank=rank, powers=[1]*7,
        dimension_shift=0, algorithm='PassarinoVeltman', convention='IregiNative',
        tensor_weights='Components', invariants='FromShifts', input_policy='Preserve')
    sample = fixture['samples'][0]
    expected = [[str(Fraction(v)), '0'] for p in sample['propagators'] for v in p['shift']]
    expected += [[str(Fraction(v)) for v in p['mass_squared']] for p in sample['propagators']]
    expected += [[str(Fraction(sample['mu'])), '0']]
    assert d['input_exact_rational'] == [expected]
    assert d['metadata'] == {'convention':'IregiNative', 'tensor_weights':'Components', 'dual_shape':None}
    assert all(len(d[key]) == 1 and type(d[key][0]) is bool for key in ['fallback_used','analytic_used'])
    assert len(d['lanes']) == 1 and d['lanes'][0]['row'] == 0 and d['lanes'][0]['status'] == 'Success'
    moments = d['lanes'][0]['moments']
    assert len(moments) == len(d['basis']) and all(len(row) == 4 for row in moments)
    values = []
    precision = []
    for row in moments:
        numeric = []
        for value in row:
            assert set(value) == {'real','imaginary','real_precision','imaginary_precision'}
            numeric.append(tuple(helper.decimal_rational(value[k]) for k in ['real','imaginary']))
            assert all(x.is_finite() for x in numeric[-1])
            for key in ['real_precision','imaginary_precision']:
                assert type(value[key]) is int and value[key] > 0
                precision.append(value[key])
        values.append(numeric)
    stats = d['execution']
    assert all(stats[k] == v for k,v in dict(parent_input_rows=1,child_batch_calls=1,
        packed_child_rows=21,parent_batch_calls=1,packed_parent_rows=1).items())
    child, parent = stats['child_execution'], stats['parent_execution']
    expected_keys = {'input_rows','argument_rows','master_family_batches','master_rows','pentagon_box_rows',
        'reduction_rows','fallback_rows','fallback_successes','analytic_rows'}
    for record in [child,parent]:
        assert set(record) == expected_keys and all(type(x) is int and x >= 0 for x in record.values())
    assert child['input_rows'] == 21 and child['reduction_rows'] >= 21
    assert child['master_family_batches'] > 0 and child['master_rows'] >= 21
    assert parent['input_rows'] == parent['argument_rows'] == parent['reduction_rows'] == 1
    assert parent['master_rows'] == parent['master_family_batches'] == 0
    if rank in [1,2]:
        # Both ranks use the unchanged, qualified rank-zero N5 child program.
        # This assertion selects the retained baseline route. A legitimate
        # planar retry would remain a different route needing its own audit.
        assert child['reduction_rows'] == 21
        assert child['master_family_batches'] == 1 and child['master_rows'] == 105
    return d, values, min(precision)


def reference(rank, fixture, helper):
    audit = load(QUAD / 'independent-saved-review.json')
    assert digest(QUAD / 'independent-saved-review.json') == QUAD_AUDIT_SHA
    assert audit['status'] == 'passed_independent_quad_future_reference_raw_and_N7_zero_pole_review'
    identifier = f'quad_n7_seventh_time_quarter_rank{rank}'
    case = [x for x in audit['cases'] if x['id'] == identifier]
    assert len(case) == 1 and case[0]['n'] == 7 and case[0]['rank'] == rank
    assert case[0]['complete_complex_slots'] == 4*len(helper.canonical_basis(rank))
    request = (QUAD / (identifier + '.txt')).read_text().splitlines()
    request = [line for line in request if line]
    assert request[0].split() == ['EVAL',identifier,'tensor','0','7',str(rank),'0','3','0','1e-6']
    assert request[-1] == 'QUIT' and len(request) == 9
    for row, propagator in zip(request[1:-1], fixture['samples'][0]['propagators']):
        expected = propagator['shift'] + propagator['mass_squared'] + ['1']
        assert list(map(Fraction,row.split())) == list(map(Fraction,expected))
    index = {1:0,2:1,7:2}[rank]
    text = (QUAD / f'capture-001/request-{index}.stdout').read_text()
    records = [json.loads(line[7:],parse_float=str) for line in text.splitlines() if line.startswith('RESULT ')]
    assert len(records) == 1
    result = records[0]
    assert result['id'] == identifier and result['stable'] is True
    assert result['poles'] == ['uv1','ir1','ir2','finite']
    assert len(result['moments']) == len(helper.canonical_basis(rank))
    assert all(len(row) == 4 and all(len(slot) == 2 for slot in row) for row in result['moments'])
    return [[tuple(Decimal(x) for x in slot) for slot in row] for row in result['moments']]


def main():
    assert Path.cwd().resolve() == ROOT
    assert len(sys.argv) == 4, 'compare_positive_saved capture128 capture256 output'
    low_path, high_path, output = map(Path,sys.argv[1:])
    assert not output.exists()
    fixture_path = BUNDLE / 'fixture.json'
    assert digest(fixture_path) == FIXTURE_SHA
    fixture = load(fixture_path)
    source = ROOT / 'validation/highpoint-thin-n6-rank7-phase/reference/compare_public.py'
    spec = importlib.util.spec_from_file_location('retained_numeric_comparison_rules',source)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    rank = load(low_path)['settings']['rank']
    assert rank in [1,2,7]
    record = dict(status='started_saved_math',rank=rank,n=7,
        reference_tolerance='1e-10',convergence_tolerance='2^-80',
        source_scope='private_positive_rank_validation_only',public_rank_support_claimed=False,
        performance_qualified=False,reference_failures=[],convergence_failures=[],pole_failures=[])
    with localcontext() as context:
        context.prec = 160
        low, lhs, low_precision = capture(low_path,rank,128,fixture,helper)
        high, rhs, high_precision = capture(high_path,rank,256,fixture,helper)
        assert low['settings'] == high['settings'] and low['input_exact_rational'] == high['input_exact_rational']
        original = reference(rank,fixture,helper)
        q = helper.scale(fixture['samples'][0],7)
        maximum = {'reference':Decimal(0),'convergence':Decimal(0),'pole':Decimal(0)}
        for index, monomial in enumerate(low['basis']):
            unit = q**(sum(monomial)+4-14)
            for slot in range(4):
                location = dict(moment=index,monomial=monomial,slot=slot)
                normalized = [tuple(x/unit for x in value) for value in [lhs[index][slot],rhs[index][slot],original[index][slot]]]
                assert all(x.is_finite() for pair in normalized for x in pair)
                a,b,ref = normalized
                convergence = helper.norm(tuple(x-y for x,y in zip(a,b)))/max(Decimal(1),helper.norm(b))
                maximum['convergence'] = max(maximum['convergence'],convergence)
                if convergence > Decimal(2)**-80:
                    record['convergence_failures'].append(dict(**location,error=str(convergence)))
                for bits,value in [(128,a),(256,b)]:
                    error = helper.norm(tuple(x-y for x,y in zip(value,ref)))/max(Decimal(1),helper.norm(ref))
                    maximum['reference'] = max(maximum['reference'],error)
                    if error > Decimal('1e-10'):
                        record['reference_failures'].append(dict(**location,working_bits=bits,error=str(error)))
                if slot < 3:
                    for name,value in [('128',a),('256',b),('quad_IBP',ref)]:
                        residue = helper.norm(value)
                        maximum['pole'] = max(maximum['pole'],residue)
                        if residue > Decimal('1e-10'):
                            record['pole_failures'].append(dict(**location,source=name,residue=str(residue)))
        slots = len(low['basis'])*4
        record.update(status='passed_saved_math' if not any(record[k] for k in
            ['reference_failures','convergence_failures','pole_failures']) else 'failed_saved_math',
            complex_slots_per_capture=slots,reference_comparisons=2*slots,convergence_comparisons=slots,
            maximum_normalized_errors={k:str(v) for k,v in maximum.items()},
            minimum_represented_component_precision=[low_precision,high_precision],
            componentwise128_or256_bit_accuracy_claimed=False,
            captured_metadata_and_inputs_validated=True,complete_packed_child_rows=21)
    output.write_text(json.dumps(record,indent=2)+'\n')
    return 0 if record['status'] == 'passed_saved_math' else 1


if __name__ == '__main__':
    sys.exit(main())
