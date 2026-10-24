#!/usr/bin/env python3
"""Verify this report increment against its committed predecessor.

Run from the repository root. No integral evaluation or benchmark is performed.
Optional argv[1] records the check once; existing output paths are refused.
"""
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path.cwd();BASELINE='4fe1a1e5c07f41fb75fc6cec9ea5b57f54d80e09'
def sha(p):return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
def raw_values(text):
 d=json.JSONDecoder();i=0
 def ws(i):
  while i<len(text) and text[i].isspace():i+=1
  return i
 i=ws(i);assert text[i]=='{';i+=1;out={}
 while True:
  i=ws(i)
  if text[i]=='}':assert not text[i+1:].strip();break
  key,end=d.raw_decode(text,i);assert isinstance(key,str) and key not in out;i=ws(end);assert text[i]==':';i=ws(i+1);start=i;_,end=d.raw_decode(text,i);out[key]=text[start:end];i=ws(end)
  if text[i]==',':i+=1;continue
  assert text[i]=='}'
 return out
base=subprocess.check_output(['git','show',f'{BASELINE}:docs/data/results.json'],text=True);current=(ROOT/'docs/data/results.json').read_text();a=json.loads(base);b=json.loads(current);ar=raw_values(base);br=raw_values(current)
assert all(k in b for k in a),'historical top-level record removed'
changed=[k for k in a if a[k]!=b[k]];assert not changed,('historical objects changed',changed)
changed_bytes=[k for k in ar if ar[k]!=br[k]];assert not changed_bytes,('historical raw value bytes changed',changed_bytes)
kernel_keys=['qualified_benchmark','qualified_native_benchmark','qualified_5c9_benchmark','qualified_80949_benchmark','qualified_6b24_benchmark']
assert sum(len(b[k]['rows']) for k in kernel_keys)==40
assert all(b[k]['rows']==a[k]['rows'] for k in kernel_keys)
assert all(len(row['paired_ratio_ci99'])==2 for k in kernel_keys for row in b[k]['rows'])
rows=b['selected_native_four_engine_row_local']['snapshot']['rows'];ratios=[x for row in rows for x in row['ratios']];assert len(rows)==8 and len(ratios)==40
assert all(x['numerator']in['baselineTIRust','candidateTIRust'] for x in ratios)
assert all(len(x['statistics']['ci99'])==2 for x in ratios)
assert sum(x['gate']=='inconclusive-short-block' for x in ratios)==5
new=[k for k in b if k not in a];allowed={'public_six_point_api_qualification','public_six_point_api_current_cargo','c0d0_dual_identity_qualification','private_n7_rational_domain_qualification'};assert set(new)<=allowed
required={'public_six_point_api_qualification','public_six_point_api_current_cargo','c0d0_dual_identity_qualification','private_n7_rational_domain_qualification'}
assert required<=set(new),'new qualification record missing'
sources=[]
for k in new:
 v=b[k];assert set(v)=={'source','sha256','snapshot'}
 p=ROOT/v['source'];assert sha(p)==v['sha256'];assert json.loads(p.read_text())==v['snapshot'];sources.append({'key':k,'source':v['source'],'sha256':v['sha256']})
if 'public_six_point_api_qualification'in b:
 q=b['public_six_point_api_qualification']['snapshot'];assert q['isolated_build_qualified'] is True and q['production_build_qualified'] is False
 assert q['selected_exact_tests_passed']==34 and q['ordinary_equivalence']['paired_cases']==12
 assert q['public_rank3']['native_slots_per_precision']==140 and q['public_rank3']['working_bits']==[128,256]
 assert q['public_rank2_lifecycle']['complex_slots']==1020 and q['public_rank2_lifecycle']['contracted_complex_slots']==68
 for k in ['performance_qualified','public_numeric_dual_qualified','rank7_qualified','n7_qualified']:assert q[k] is False
if 'public_six_point_api_current_cargo'in b:
 q=b['public_six_point_api_current_cargo']['snapshot'];assert q['status']=='current_cargo_explicit_six_point_rank3_qualified'
 assert q['current_cargo_build_qualified'] and q['current_cargo_runtime_gates_passed'] and q['selected_current_tests_passed']==34
 assert q['public_rank3']['all_passed'] and q['public_rank3']['all_original_comparisons']==280 and q['public_rank3']['all_convergence_comparisons']==140
 assert q['independent_saved_review']['passed'] and q['guard_scope']['runtime_input_bindings']==674
 assert q['guard_scope']['three_native_archives_in_pre_post_runtime_guards'] is False
 assert not q['current_ordinary_paired_rebuilt'] and not q['current_rank2_lifecycle_rebuilt'] and not q['performance_qualified']
if 'private_n7_rational_domain_qualification'in b:
 q=b['private_n7_rational_domain_qualification']['snapshot'];assert q['tests_passed']==22 and q['tests_failed']==0
 assert q['constructor']['constructor_completed'] is True and q['constructor']['workspace_created'] is False and q['constructor']['numerical_arrays'] is False
 assert q['stages']['prepare']['elapsed_seconds_including_postguards']<=q['stages']['prepare']['bound_seconds']==150
if 'c0d0_dual_identity_qualification'in b:
 q=b['c0d0_dual_identity_qualification']['snapshot'];assert q['status']=='passed' and q['native_wheel']=='checkpoint-wheel-004'
 assert q['requested_accuracy_bits']==53 and q['working_precision_bits']==[128,256]
 assert q['totals']['successful_evaluations']==28 and q['totals']['identity_checks']==96 and q['totals']['precision_comparisons']==96
 assert q['native_runtime_attempts']=={'C0':1,'D0':1,'retries':0}
 assert q['native_sha256']==b['python_interface_fixed_wheel_qualification']['snapshot']['native_sha256']
 result={'status':'passed','historical_objects_unchanged':len(a),'historical_raw_value_spans_unchanged':len(ar),'historical_kernel_rows':40,'historical_kernel_ci_endpoints':80,'historical_same_cohort_rows':len(rows),'historical_ratio_cells':len(ratios),'historical_ci_endpoints':80,'historical_short_cells':5,'all_ratio_numerators_TIRust':True,'new_sources':sources,'results_sha256':sha(ROOT/'docs/data/results.json'),'baseline_sha256':hashlib.sha256(base.encode()).hexdigest(),'checker_sha256':sha(pathlib.Path(__file__))}
else:result={'status':'baseline_only_passed','historical_objects_unchanged':len(a),'historical_raw_value_spans_unchanged':len(ar),'historical_ratio_cells':len(ratios)}
if len(sys.argv)>1:
 p=pathlib.Path(sys.argv[1]);assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
