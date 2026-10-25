"""Independent standard-library replay of saved complex decimal arrays only."""
from decimal import Decimal, localcontext
from fractions import Fraction
import json

LIMIT = Fraction(1, 10**20)
BASIS = [(t, x, y, degree-t-x-y) for degree in range(8)
         for t in range(degree, -1, -1) for x in range(degree-t, -1, -1)
         for y in range(degree-t-x, -1, -1)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def display(squared):
    with localcontext() as ctx:
        ctx.prec = 100
        return str((Decimal(squared.numerator)/Decimal(squared.denominator)).sqrt())


def norm2(z):
    return sum(c*c for c in z)


def scale2(props):
    shifts = [tuple(Fraction(x) for x in p['shift']) for p in props]
    candidates = [Fraction(1)] + [abs(Fraction(p['mass_squared'][0])) for p in props]
    for i, p in enumerate(shifts):
        for q in shifts[:i]:
            delta = tuple(x-y for x, y in zip(p,q))
            candidates.append(abs(delta[0]*delta[0]-sum(x*x for x in delta[1:])))
    return max(candidates)


def parse_raw(body, identifier, missing=False):
    lines = body.decode().splitlines()
    precision = [json.loads(line[10:]) for line in lines if line.startswith('PRECISION ')]
    require(precision == [{'dbl_kind':16,'olo_kind':16,'storage_bits':128,'binary_digits':113,'decimal_digits':33}], 'complete raw precision witness')
    require(lines.count('READY IREGI_REFERENCE_QP_V1') == 1, 'exact readiness witness')
    responses = [json.loads(line[7:]) for line in lines if line.startswith('RESULT ')]
    if missing:
        require(not responses and 'ERROR:out of range of pave_UV' in body.decode(), 'preserved N2 PV missing RESULT/error')
        return None, None
    require(len(responses) == 1, 'one complete response')
    response = responses[0]
    require(response['id'] == identifier and response['stable'] is True and response['poles'] == ['uv1','ir1','ir2','finite'], 'raw ID/stable/ordering')
    require(len(response['moments']) == len(BASIS) == 330, 'full 330 moments')
    values = []
    for moment in response['moments']:
        require(len(moment) == 4, 'all four Laurent coefficients')
        row = []
        for slot in moment:
            require(len(slot) == 2 and all(isinstance(x,str) and Decimal(x).is_finite() for x in slot), 'finite quoted real/imaginary components')
            row.append(tuple(Fraction(x) for x in slot))
        values.append(row)
    return response, values


def replay(protocol, saved, raw_bodies, archived_raw, archived_props):
    require(protocol['basis'] == [list(x) for x in BASIS], 'exact cumulative component order')
    require(len(protocol['runtime']['cases']) == len(saved['cases']) == len(raw_bodies) == 26, 'all 26 cases/raw attempts')
    require(saved['squared_threshold_exact'] == str(LIMIT) and saved['comparison_threshold'] == '1e-10', 'unmodified exact squared gate')
    expected_records = []
    record_keys = set()
    values_by_key = {}
    cases_by_key = {}
    counts_by_kind = {}
    identity_failures = 0
    complete_slots = 0
    missing_ids = []
    cases = []

    def record(identifier, kind, moment, slot, squared):
        key = (identifier,kind,moment,slot)
        require(key not in record_keys, 'unique independent record')
        record_keys.add(key)
        counts_by_kind[kind] = counts_by_kind.get(kind,0)+1
        row = {'id':identifier,'kind':kind,'moment':moment,'slot':slot,'error':display(squared),'passed':squared <= LIMIT}
        expected_records.append(row)
        return row['passed']

    for case, item, raw in zip(protocol['runtime']['cases'],saved['cases'],raw_bodies):
        key = (case['propagators'],case['sample'],case['mode'])
        require(key not in cases_by_key and case['id'] == item['id'], 'unique case identity')
        cases_by_key[key] = (case,item)
        n = case['propagators']
        missing = n == 2 and case['mode'] == 1
        response, values = parse_raw(raw,case['id'],missing)
        if missing:
            require(item['status'] == 'invalid_response' and item['complete_complex_slots'] == 0 and 'response' not in item
                    and item['eligible_IBP_reference_anchor'] is False and item['accepted_PV_reference'] is False, 'missing arrays remain failure without invented zeros')
            missing_ids.append(case['id'])
            continue
        require(item['response'] == response and item['status'] == 'captured' and item['complete_complex_slots'] == 1320 and item['native_stable'] is True, 'complete exact copied response')
        complete_slots += 1320
        values_by_key[key] = values
        q2 = scale2(case['exact_propagators'])
        require(Fraction(item['natural_scale_squared_exact']) == q2, 'exact natural scale')
        counts = {'IR_zero':0,'UV_convergent_zero':0,'N1_odd_component_zero':0}
        failures = dict.fromkeys(counts,0)
        uv_nonzero = 0
        for moment,(powers,row) in enumerate(zip(BASIS,values)):
            exponent = sum(powers)+4-2*n
            unit2 = q2**exponent
            uv_nonzero += norm2(row[0]) != 0
            for slot,z in enumerate(row):
                kinds = (['IR_zero'] if slot in (1,2) else [])
                if slot == 0 and exponent < 0:
                    kinds.append('UV_convergent_zero')
                if n == 1 and any(p%2 for p in powers):
                    kinds.append('N1_odd_component_zero')
                for kind in kinds:
                    counts[kind] += 1
                    failures[kind] += not record(case['id'],kind,moment,slot,norm2(z)/unit2)
        require(item['exact_nonzero_UV_slots'] == uv_nonzero and item['identity_counts'] == counts and item['identity_failures'] == failures
                and item['applicable_identities_pass'] is (not any(failures.values())), 'all per-case identity counts/results')
        identity_failures += sum(failures.values())
        cases.append({'id':case['id'],'n':n,'sample':case['sample'],'mode':case['mode'],'slots':1320,'identity_counts':counts,'nonzero_UV_slots':uv_nonzero})

    archived_response, archived_values = parse_raw(archived_raw,protocol['N5_base']['id'])
    parent_counts = {'IR_zero':0,'UV_convergent_zero':0}
    parent_failures = dict.fromkeys(parent_counts,0)
    parent_q2 = scale2(archived_props)
    for moment,(powers,row) in enumerate(zip(BASIS,archived_values)):
        exponent = sum(powers)+4-10
        unit2 = parent_q2**exponent
        for slot,z in enumerate(row[:3]):
            kind = 'IR_zero' if slot in (1,2) else 'UV_convergent_zero' if exponent < 0 else None
            if kind is not None:
                parent_counts[kind] += 1
                parent_failures[kind] += not record(protocol['N5_base']['id'],'archived_N5_'+kind,moment,slot,norm2(z)/unit2)
    require(saved['archived_N5_base_controls'] == {'native_stable':True,'counts':parent_counts,'failures':parent_failures,'passed':not any(parent_failures.values())}, 'all archived N5 IR/UV controls')

    scale_rows = []
    for n in range(1,6):
        case,item = cases_by_key[(n,'scaled_by_two',0)]
        reference = archived_values if n == 5 else values_by_key[(n,'base',0)]
        scaled = values_by_key[(n,'scaled_by_two',0)]
        q2 = scale2(case['exact_propagators'])
        maximum = Fraction(0)
        failures = 0
        for moment,(powers,row,base) in enumerate(zip(BASIS,scaled,reference)):
            exponent = sum(powers)+4-2*n
            factor = Fraction(2)**exponent
            for slot,(left,base_value) in enumerate(zip(row,base)):
                expected = tuple(factor*x for x in base_value)
                squared = norm2(tuple(x-y for x,y in zip(left,expected))) / max(q2**exponent,norm2(expected))
                maximum = max(maximum,squared)
                failures += not record(case['id'],'IBP_scale_identity',moment,slot,squared)
        summary = saved['scaling'][n-1]
        require(summary['propagators'] == n and summary['status'] == 'compared' and summary['compared_complex_slots'] == 1320
                and summary['failures'] == failures and summary['maximum_error'] == display(maximum) and summary['numerical_scale_identity_pass'] is (failures == 0), 'all complete IBP scale pairs')
        require(item['IBP_scaling_pass'] is True and (n==5 or cases_by_key[(n,'base',0)][1]['IBP_scaling_pass'] is True), 'scale acceptance remains controlled')
        scale_rows.append({'n':n,'compared_slots':1320,'failures':failures,'maximum_error':display(maximum)})

    pairs = []
    pv_failing_slots = []
    for n in range(1,5):
        for sample in ('base','scaled_by_two','first_mass_squared_plus_one'):
            ibp_case,ibp_item = cases_by_key[(n,sample,0)]
            pv_case,pv_item = cases_by_key[(n,sample,1)]
            summary = saved['PV_IBP_pairs'][len(pairs)]
            if n == 2:
                require(summary['status'] == 'not_comparable' and summary['compared_complex_slots'] == 0 and summary['failures'] is None
                        and pv_item['accepted_PV_reference'] is False, 'missing PV cannot be promoted')
                pairs.append({'n':n,'sample':sample,'complete':False,'failures':None})
                continue
            values,reference = values_by_key[(n,sample,1)],values_by_key[(n,sample,0)]
            maximum = Fraction(0)
            failed = 0
            q2 = scale2(pv_case['exact_propagators'])
            for moment,(powers,row,base) in enumerate(zip(BASIS,values,reference)):
                unit2 = q2**(sum(powers)+4-2*n)
                for slot,(left,right) in enumerate(zip(row,base)):
                    squared = norm2(tuple(x-y for x,y in zip(left,right))) / max(unit2,norm2(right))
                    maximum = max(maximum,squared)
                    ok = record(pv_case['id'],'PV_vs_same_input_IBP',moment,slot,squared)
                    failed += not ok
                    if not ok:
                        pv_failing_slots.append({'id':pv_case['id'],'moment':moment,'slot':slot})
            require(summary['status'] == 'compared' and summary['compared_complex_slots'] == 1320 and summary['failures'] == failed and summary['maximum_error'] == display(maximum), 'full PV/IBP all-slot comparisons')
            require(pv_item['accepted_PV_reference'] is (n==1) and pv_item['PV_agrees_with_eligible_IBP'] is (n==1), 'stable wrong PV remains rejected')
            require(failed == (0 if n == 1 else 71 if n == 3 else 91), 'explicit per-family PV failure counts')
            pairs.append({'n':n,'sample':sample,'complete':True,'failures':failed,'maximum_error':display(maximum)})

    require(len(expected_records) == 42018 and expected_records == saved['records'], 'every saved record independently rederived in original order')
    require(complete_slots == 30360 and len(cases) == 23 and len(missing_ids) == 3, 'all complete and missing requests counted')
    require(identity_failures == 0 and not any(parent_failures.values()) and all(r['failures'] == 0 for r in scale_rows), 'all applicable identities pass')
    require(len(pv_failing_slots) == 486 and all(r['slot'] == 3 for r in pv_failing_slots), '486 finite errors preserved, no pole-only exclusion')
    for (n,sample,mode),(case,item) in cases_by_key.items():
        require(item['eligible_IBP_reference_anchor'] is (mode==0), 'exact restricted IBP anchor admission')
    require(saved['total_complete_complex_slots'] == 30360 and saved['eligible_IBP_reference_anchors'] == 14 and saved['accepted_PV_references'] == 3
            and saved['failed_identity_or_pair_records'] == 486 and saved['all_requested_arrays_complete'] is False, 'complete saved summary preserves failures')
    require(saved['zero_projection_performed'] is False and saved['compared_TIRust_slots'] == 0
            and saved['currentCargo_or_full_rank7_domain_or_performance_qualified'] is False
            and saved['finite_coefficients_independently_certified_by_identities'] is False, 'no zero/proof/scope promotion')
    return {'complete_arrays':23,'complete_complex_slots':complete_slots,'N2_PV_missing_arrays':missing_ids,
            'independently_rederived_records':len(expected_records),'record_counts':counts_by_kind,
            'applicable_identity_failures':identity_failures,'archived_N5_controls':parent_counts,'scaling':scale_rows,
            'PV_IBP_pairs':pairs,'stable_incorrect_N3_N4_PV_arrays':6,'PV_finite_disagreement_slots':len(pv_failing_slots),
            'eligible_new_IBP_arrays':14,'accepted_N1_PV_arrays':3,'cases':cases}
