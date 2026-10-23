"""Numerical historical comparison; paired current captures still require exact equality."""
from decimal import Decimal, localcontext
from fractions import Fraction
import compare_public as public


NUMERIC_FIELDS = ['moments', 'repeat', 'contracted']


def sample(row, lane):
    n, components = row['propagators'], row['components']
    width = (5*n + 1)*components
    assert len(row['input']) == 5*width
    values = row['input'][lane*width:(lane+1)*width:components]
    assert len(values) == 5*n+1
    assert all(Fraction(value[1]['rational']) == 0 for value in values[:4*n])
    return dict(mu=values[-1][0]['rational'], propagators=[
        dict(shift=[value[0]['rational'] for value in values[4*i:4*i+4]],
             mass_squared=[part['rational'] for part in values[4*n+i]]) for i in range(n)])


def error(left, right, normalization):
    a = [public.decimal_rational(part['rational'])/normalization for part in left]
    b = [public.decimal_rational(part['rational'])/normalization for part in right]
    assert all(value.is_finite() for value in a+b)
    return public.norm([x-y for x,y in zip(a,b)])/max(Decimal(1), public.norm(a))


def compare(original, retained, expected_cases=27):
    assert len(original) == len(retained) == expected_cases
    counts = {key: 0 for key in NUMERIC_FIELDS}
    maxima = {key: Decimal(0) for key in NUMERIC_FIELDS}
    unscaled_contraction_maximum = Decimal(0)
    changed_leaves = []
    maximum_raw_difference = Fraction(0)
    with localcontext() as context:
        context.prec = 100
        for case, (old, new) in enumerate(zip(original, retained)):
            for key in ['domain', 'propagators', 'rank', 'components', 'input']:
                assert old[key] == new[key], ('Historical input/layout changed', case, key)
            assert old['result'].keys() == new['result'].keys()
            for key in old['result']:
                if key not in NUMERIC_FIELDS:
                    assert old['result'][key] == new['result'][key], ('Historical status/flags/metadata changed', case, key)
            n, rank, components = old['propagators'], old['rank'], old['components']
            basis = public.canonical_basis(rank)
            assert old['result']['basis'] == '[' + ', '.join('Monomial(' + str(powers) + ')' for powers in basis) + ']'
            for key in NUMERIC_FIELDS:
                left, right = old['result'][key], new['result'][key]
                assert len(left) == len(right) == 5
                for lane, (a,b) in enumerate(zip(left,right)):
                    success = old['result']['lane_successes'][lane]
                    if not success:
                        assert a is None and b is None
                        continue
                    expected = 4*components*(len(basis) if key != 'contracted' else 1)
                    assert len(a) == len(b) == expected
                    q = public.scale(sample(old,lane),n)
                    for index, (x,y) in enumerate(zip(a,b)):
                        assert len(x) == len(y) == 2
                        moment_rank = sum(basis[index//(4*components)]) if key != 'contracted' else 0
                        normalization = q**(4-2*n+moment_rank)
                        discrepancy = error(x,y,normalization)
                        maxima[key] = max(maxima[key],discrepancy)
                        assert discrepancy <= Decimal('1e-10'), ('Historical numerical mismatch',case,key,lane,index,str(discrepancy))
                        if key == 'contracted':
                            unscaled = error(x,y,Decimal(1))
                            unscaled_contraction_maximum = max(unscaled_contraction_maximum,unscaled)
                            assert unscaled <= Decimal('1e-10')
                        counts[key] += 1
                        for part, (u,v) in enumerate(zip(x,y)):
                            assert u.keys() == v.keys() == {'rational','bits','negative_sign'}
                            for name in u:
                                if u[name] != v[name]:
                                    changed_leaves.append(dict(case=case,field=key,lane=lane,index=index,part=part,
                                                               property=name,historical=u[name],current=v[name]))
                            maximum_raw_difference = max(maximum_raw_difference,abs(Fraction(u['rational'])-Fraction(v['rational'])))
    return dict(status='passed', tolerance='1e-10', arithmetic_precision_decimal_digits=100,
                compared_complex_components=counts, maximum_normalized_errors={key:str(value) for key,value in maxima.items()},
                maximum_unscaled_contraction_error=str(unscaled_contraction_maximum),
                maximum_raw_difference_exact=str(maximum_raw_difference), changed_leaves=changed_leaves,
                normalization='Tensor moments and repeats: existing q^(4-2N+moment rank), using primal kinematics and the same scale for all dimensionless Taylor-parameter components. Mixed-rank contractions: scalar-integral scale q^(4-2N), plus an unscaled mixed absolute/relative check. No homogeneous numerator degree is inferred.',
                historical_bitwise_identical=not changed_leaves,
                scope='All successful historical slots and components are compared. Rejected lanes require unchanged statuses and absent arrays. Current baseline/candidate exact equality is a separate prerequisite. Precision and signed-zero differences are recorded, not hidden.')
