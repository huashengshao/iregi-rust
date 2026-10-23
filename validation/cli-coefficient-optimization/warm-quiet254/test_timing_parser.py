import copy,json,unittest
from timing_parser import validate,ordered_first

def fixture():
    count=15
    raw={'case':'ggh','candidate_mode':'cse0','status':'passed','coefficient_count':count,'setup':{}}
    for key in ['baseline_exact_proof','candidate_exact_proof']:
        raw[key]={'outputs_proved':count,'proof':'Symbolica exact expanded differences are literal zero; no statistical zero test'}
    raw['rows']=[]
    for n in [1,32]:
        seed=0x8ae4_d723_f209_16c5^n;ordering=ordered_first(seed)
        value={'real':1.0,'imaginary':0.0,'real_bits':4607182418800017408,'imaginary_bits':0,'real_precision':53,'imaginary_precision':53}
        output={'rows':n,'components':1,'values':[copy.deepcopy(value)for _ in range(n*count)]}
        reference={'complex_outputs':n*count,'dimension_metric_passed':True,'dimension_normalized_max':'0','raw_1e10_failed_components_retained':3,'raw_max':'1/1000000'}
        raw['rows'].append({'rows':n,'status':'passed','iterations_per_variant_per_block':10,'pilots':[[8,24000000],[8,24000000]],'seed':seed,'first_variant_by_block':ordering,'parameter_names':['x'],'packed_input_bits':[[0,0]for _ in range(n)],'dimension_scales':[1.0]*(n*count),'reference_checks':[copy.deepcopy(reference),copy.deepcopy(reference)],'expected_outputs_by_variant':[copy.deepcopy(output),copy.deepcopy(output)],'final_outputs_by_variant':[copy.deepcopy(output),copy.deepcopy(output)],'setup':{},'blocks':[{'block':i,'first_variant':ordering[i],'iterations':10,'each_variant_matches_own_exact_value_precision_signed_zero':True,'cross_variant_dimension_metric_passed':True,'elapsed_ns':[100,90]}for i in range(21)]})
    return raw

class ParserTests(unittest.TestCase):
    def test_complete_with_visible_raw_failures(self):
        result=validate('ggh','cse0',fixture());self.assertEqual(len(result),2);self.assertEqual(result[0]['reference_checks'][0]['raw_1e10_failed_components_retained'],3)
    def test_output_bit_fields_are_required_and_consistent(self):
        for name,edit in [
            ('missing',lambda v:v.pop('real_bits')),
            ('mismatched',lambda v:v.update(real_bits=0)),
            ('signed_zero_lost',lambda v:v.update(imaginary_bits=1<<63)),
            ('nan_bits',lambda v:v.update(real_bits=0x7ff8000000000000)),
            ('out_of_range',lambda v:v.update(real_bits=1<<64)),
        ]:
            with self.subTest(name=name):
                value=fixture()
                for field in ['expected_outputs_by_variant','final_outputs_by_variant']:edit(value['rows'][0][field][0]['values'][0])
                with self.assertRaises(ValueError):validate('ggh','cse0',value)
    def test_malformed_matrices_rejected(self):
        mutations={
            'missing_batch':lambda x:x['rows'].pop(),
            'missing_pilots':lambda x:x['rows'][0].pop('pilots'),
            'invalid_pilot_stop':lambda x:x['rows'][0].update(pilots=[[8,1000],[8,24000000]]),
            'calibration_mismatch':lambda x:x['rows'][0].update(pilots=[[8,12000000],[8,24000000]]),
            'negative_reference':lambda x:x['rows'][0]['reference_checks'][0].update(dimension_normalized_max='-1'),
            'missing_raw_max':lambda x:x['rows'][0]['reference_checks'][0].pop('raw_max'),
            'invalid_raw_count':lambda x:x['rows'][0]['reference_checks'][0].update(raw_1e10_failed_components_retained=True),
            'excessive_raw_count':lambda x:x['rows'][0]['reference_checks'][0].update(raw_1e10_failed_components_retained=31),
            'inconsistent_raw_count':lambda x:x['rows'][0]['reference_checks'][0].update(raw_1e10_failed_components_retained=0),
            'missing_block':lambda x:x['rows'][0]['blocks'].pop(),
            'zero_elapsed':lambda x:x['rows'][0]['blocks'][0].update(elapsed_ns=[0,90]),
            'extra_elapsed':lambda x:x['rows'][0]['blocks'][0].update(elapsed_ns=[100,90,80]),
            'variable_iterations':lambda x:x['rows'][0]['blocks'][0].update(iterations=11),
            'changed_order':lambda x:x['rows'][0]['first_variant_by_block'].reverse(),
            'changed_seed':lambda x:x['rows'][0].update(seed=0),
            'missing_scale':lambda x:x['rows'][0]['dimension_scales'].pop(),
            'zero_scale':lambda x:x['rows'][0]['dimension_scales'].__setitem__(0,0),
            'missing_identity':lambda x:x['baseline_exact_proof'].update(outputs_proved=14),
            'wrong_context':lambda x:x['rows'][0]['packed_input_bits'].pop(),
            'dimension_failure':lambda x:x['rows'][0]['reference_checks'][0].update(dimension_normalized_max='1/10'),
            'missing_raw_count':lambda x:x['rows'][0]['reference_checks'][0].pop('raw_1e10_failed_components_retained'),
            'output_bit_changed':lambda x:x['rows'][0]['final_outputs_by_variant'][1]['values'][0].update(real_bits=0),
            'final_zero_number_disagrees_with_bits':lambda x:x['rows'][0]['final_outputs_by_variant'][0]['values'][0].update(imaginary=-0.0),
        }
        for name,mutate in mutations.items():
            with self.subTest(name=name):
                value=fixture();mutate(value)
                with self.assertRaises((ValueError,KeyError)):validate('ggh','cse0',value)
if __name__=='__main__':unittest.main()
