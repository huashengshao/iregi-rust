"""Saved-only complete single-capture reference/pole gate.

The finite parent owns deadlines and source/artifact provenance. This imports
only saved comparison rules; it never imports a producer or evaluates masters.
"""
from decimal import Decimal, localcontext
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = Path('/shared/external/iregi/iregi-rust')


def main():
    assert Path.cwd().resolve() == ROOT and len(sys.argv) == 3
    capture_path, output = map(Path,sys.argv[1:])
    assert not output.exists()
    spec = importlib.util.spec_from_file_location('actual_main_private_saved_rules',HERE/'compare_main_private_saved.py')
    rules = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rules)
    source = ROOT/'validation/highpoint-thin-n6-rank7-phase/reference/compare_public.py'
    spec = importlib.util.spec_from_file_location('retained_numeric_comparison_rules',source)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    fixture_path = ROOT/'target/public-seven-point-positive-rank-proposal/fixture.json'
    assert rules.digest(fixture_path) == rules.FIXTURE_SHA
    fixture = rules.load(fixture_path)
    saved = rules.load(capture_path)
    rank, bits = saved['settings']['rank'], saved['working_bits']
    assert rank == 7 and bits in [128,256]
    record = dict(status='started_saved_single_math',rank=rank,n=7,working_bits=bits,
        reference_tolerance='1e-10',reference_failures=[],pole_failures=[],
        source_scope='actual_main_cfg_test_private_positive_rank_validation_only',
        performance_qualified=False,public_rank_support_claimed=False)
    with localcontext() as context:
        context.prec = 160
        parsed, values, minimum_precision = rules.capture(capture_path,rank,bits,fixture,helper)
        original = rules.reference(rank,fixture,helper)
        q = helper.scale(fixture['samples'][0],7)
        maximum = {'reference':Decimal(0),'pole':Decimal(0)}
        for index,monomial in enumerate(parsed['basis']):
            unit = q**(sum(monomial)+4-14)
            for slot in range(4):
                location = dict(moment=index,monomial=monomial,slot=slot)
                a,ref = [tuple(x/unit for x in value) for value in [values[index][slot],original[index][slot]]]
                assert all(x.is_finite() for pair in [a,ref] for x in pair)
                error = helper.norm(tuple(x-y for x,y in zip(a,ref)))/max(Decimal(1),helper.norm(ref))
                maximum['reference'] = max(maximum['reference'],error)
                if error > Decimal('1e-10'):
                    record['reference_failures'].append(dict(**location,error=str(error)))
                if slot < 3:
                    for name,value in [(str(bits),a),('quad_IBP',ref)]:
                        residue = helper.norm(value)
                        maximum['pole'] = max(maximum['pole'],residue)
                        if residue > Decimal('1e-10'):
                            record['pole_failures'].append(dict(**location,source=name,residue=str(residue)))
        record.update(status='passed_saved_single_math' if not any(record[k] for k in
            ['reference_failures','pole_failures']) else 'failed_saved_single_math',
            complex_slots=1320,reference_comparisons=1320,pole_comparisons=1980,
            maximum_normalized_errors={k:str(v) for k,v in maximum.items()},
            minimum_represented_component_precision=minimum_precision,
            componentwise128_or256_bit_accuracy_claimed=False,
            captured_metadata_and_inputs_validated=True,complete_packed_child_rows=21)
    output.write_text(json.dumps(record,indent=2)+'\n')
    return 0 if record['status'] == 'passed_saved_single_math' else 1


if __name__ == '__main__':
    sys.exit(main())
