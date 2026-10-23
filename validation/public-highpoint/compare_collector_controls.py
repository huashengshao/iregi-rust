"""Compare actual full-run N4 control primals to the captured untouched original."""
from decimal import Decimal, localcontext
import json
import compare_collector_history_v4 as history
import compare_public as public


def compare(rows, reference):
    assert [(r['domain'],r['propagators'],r['rank'],r['components'],r['fixture']) for r in rows] == [
        ('f64',4,2,1,'orthogonal_unit_n4'),('f64',4,1,3,'orthogonal_unit_n4')]
    assert reference['reference'] == 'untouched original IREGI' and reference['exit_code'] == 0
    samples = [history.sample(row,0) for row in rows]
    assert samples[0] == samples[1]
    sample = samples[0]
    label = 'collector_v2_orthogonal_n4_rank2'
    request = f'EVAL {label} tensor 0 4 2 0 {sample["mu"]} 0 1e-6\n'
    request += ''.join(' '.join(p['shift']+p['mass_squared'])+' 1\n' for p in sample['propagators'])+'QUIT\n'
    assert reference['request'] == request
    parsed = [json.loads(line[7:],parse_float=str) for line in reference['stdout'].splitlines() if line.startswith('RESULT ')]
    assert len(parsed) == 1 and parsed[0]['id'] == label and parsed[0]['stable'] is True
    answer = parsed[0]
    assert answer['poles'] == ['uv1','ir1','ir2','finite'] and len(answer['moments']) == 15
    assert all(len(moment)==4 and all(len(slot)==2 for slot in moment) for moment in answer['moments'])
    reports = []
    with localcontext() as context:
        context.prec = 100
        q = public.scale(sample,4)
        for row in rows:
            components = row['components']
            assert row['result']['lane_successes'][0] is True
            values = row['result']['moments'][0]
            basis = public.canonical_basis(row['rank'])
            assert len(values) == len(basis)*4*components
            maximum = Decimal(0)
            for index,powers in enumerate(basis):
                normalization = q**(sum(powers)-4)
                for slot in range(4):
                    value = [public.decimal_rational(part['rational'])/normalization for part in values[(index*4+slot)*components]]
                    old = [Decimal(str(part))/normalization for part in answer['moments'][index][slot]]
                    assert all(v.is_finite() for v in value+old)
                    discrepancy = public.norm([a-b for a,b in zip(value,old)])/max(Decimal(1),public.norm(old))
                    maximum = max(maximum,discrepancy)
                    assert discrepancy <= Decimal('1e-10'), (row['rank'],components,index,slot,str(discrepancy))
                    if slot<3: assert max(public.norm(value),public.norm(old)) <= Decimal('1e-10')
            reports.append(dict(rank=row['rank'],components=components,compared_primal_complex_slots=len(basis)*4,
                                maximum_normalized_reference_error=str(maximum)))
    return dict(status='passed',tolerance='1e-10',comparisons=reports,
                scope='Actual full29-capture ordinary/primal arrays, every requested Laurent slot, against untouched original IREGI at identical represented inputs. No independent higher-Dual derivative or complex-mass-lane reference claim.')
