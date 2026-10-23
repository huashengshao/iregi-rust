from pathlib import Path
import csv,hashlib,json,re
from collections import Counter
base=Path('target/native-shared-binary');root=Path.cwd();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((base/'probe-build.json').read_text());parity=json.loads((base/'parity.json').read_text());shape=json.loads((base/'shared-source-equivalence.json').read_text());baseline=json.loads((base/'baseline-source-equivalence.json').read_text())
assert build['exit_code']==0 and not build['changed'] and parity['status']=='passed'
assert parity['inputs_unchanged'] and parity['binary_unchanged']
assert sha(base/'parity.csv')==parity['csv_sha256'] and sha(base/'parity.log')==parity['log_sha256'] and sha(base/'probe')==build['binary_sha256']
assert all(row['scalar_source_identical'] and row['full_ordered_primitive_control_slot_and_helper_source_identical'] for row in shape['families'])
assert all(row['exact_after_constant_index_expansion'] for row in baseline)
rows=list(csv.DictReader((base/'parity.csv').open()));assert len(rows)==80
physical=[]
for family,points in [('B0',6),('C0',7)]:
 for domain,sizes in [('f64',[0,1,3,7,32,3]),('DoubleFloat',[points,1]),('Float256',[points,1])]:
  selected=[r for r in rows if r['domain']==family+'-'+domain]
  expected=[(order,n) for n in sizes for order in ['homogeneous','interleaved','grouped','reversed']]
  assert [(r['ordering'],int(r['rows'])) for r in selected]==expected
  assert all(r['kind']=='parity' and int(r['complex_outputs'])==6*int(r['rows']) and r['baseline_cells']==r['candidate_cells'] for r in selected)
  physical.append({'family':family,'domain':domain,'configurations':len(selected),'complex_outputs':sum(int(r['complex_outputs']) for r in selected),'interpreter_value_differences':sum(int(r['interpreter_value_mismatches']) for r in selected),'interpreter_precision_differences':sum(int(r['interpreter_precision_mismatches']) for r in selected),'interpreter_signed_zero_differences':sum(int(r['interpreter_signed_zero_mismatches']) for r in selected)})
log=(base/'parity.log').read_text();controls=[]
for domain in ['f64','DoubleFloat','Float256']:
 match=re.search(r'control,symbolica-generated-fixture,'+domain+r',configurations=(\d+),complex-outputs=(\d+),.*?,passed',log);assert match,domain
 assert (int(match[1]),int(match[2]))==(36,2856)
 controls.append({'scope':'Symbolica generated guarded alias/outline fixture','domain':domain,'configurations':36,'complex_outputs':2856})
for domain in ['f64','DoubleFloat','Float256-mixed80-128-256']:
 match=re.search(r'control,direct-shared-kernel,'+domain+r',configurations=(\d+),all-arena-complex-comparisons=(\d+),.*?,passed',log);assert match,domain
 assert (int(match[1]),int(match[2]))==(240,31680)
 controls.append({'scope':'Direct shared kernel active and inactive arena comparisons','domain':domain,'configurations':240,'complex_comparisons':31680})
assert log.count('control,invalid-neighbor,rows7,retained-stride32,bad-lane3,all-six-complex-outputs,passed')==2
assert log.count('control,malformed-shape,output-unchanged-including-signed-zero,passed')==2
records={name:sha(base/name) for name in ['probe-build.json','parity.json','parity.csv','parity.log','shared-source-equivalence.json','baseline-source-equivalence.json','shared_binary_kernel.rs','kernel_controls.rs','probe.rs']}
result={'status':'numerically-qualified-timing-unrun','production_changed':False,'adoption':'Not adopted. Performance qualification pending coordinated quiet window.','native_numeric_policy':'Exact represented rational, precision, and signed zero equality required for every finite old/new complex output. All six Laurent/boundary outputs compared. Interpreter differences recorded separately and nonfinite interpreter controls rejected.','physical':physical,'controls':controls,'invalid_neighbor_controls':'Both families: valid adjacent lanes unchanged, raw invalid classifications equal, public NonFiniteInput error, shape sentinel values/precision/signed zeros preserved.','source':shape,'evidence_sha256':records,'limitations':['B0/C0 only; D0 and Dual paths unchanged.','All-type combined probe uses frozen dev-profile dependencies and opt3 generated code, not an end-to-end release IREGI comparison.','Native versus interpreter exact differences predate this candidate and are not claimed as exact cross-backend agreement.','Direct mixed precision tests qualify storage/primitive behavior; they are not physical higher-precision convergence tests.']}
if (base/'timing-fixed-summary.json').exists():
 timing=json.loads((base/'timing-fixed-summary.json').read_text());assert len(timing['rows'])==12
 result['status']='numerically-qualified-performance-rejected'
 result['adoption']='Rejected: not all requested per-family/order/batch performance gates pass. Production unchanged; no selective adoption based on the one favorable homogeneous group.'
 result['timing']={'summary_sha256':sha(base/'timing-fixed-summary.json'),'groups':len(timing['rows']),'gates':dict(Counter(r['ratio']['gate'] for r in timing['rows'])),'all_type_before_after_csv_identical':True,'interpretation':'Seven regressions and two noisy groups remain visible. C0 grouped batch32 is noisy under the interval-width gate despite a wholly slower confidence interval. Singleton scalar source is unchanged; singleton differences are layout/cohort effects, not shared-batch arithmetic benefits.'}
(base/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['source','evidence_sha256','limitations']},indent=2))
