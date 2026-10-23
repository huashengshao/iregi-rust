from pathlib import Path
from collections import Counter
import csv,hashlib,json
root=Path.cwd();base=root/'target/native-dense-span';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for family in ['b0','c0']:
 path=base/f'{family}-fixed-parity-before.json'
 if not path.exists():continue
 run=json.loads(path.read_text());build=json.loads((base/f'fixed-{family}-build.json').read_text())
 assert run['status']=='passed' and run['binary_unchanged'] and build['exit_code']==0 and not build['changed']
 assert run['binary_sha256']==build['binary_sha256'] and run['protocol']=='dense-span-fixed-loop-v2'
 for name,digest in run['artifacts'].items():assert sha(root/name)==digest,(name,'changed')
 rows=list(csv.DictReader((base/f'{family}-fixed-parity-before.csv').open()))
 expected=Counter((order,n) for order in ['homogeneous','interleaved','grouped','reversed'] for n in [0,1,3,7,32,3])
 assert Counter((r['ordering'],int(r['rows'])) for r in rows)==expected
 assert all(r['domain']=='f64' and r['kind']=='parity' and int(r['complex_outputs'])==int(r['rows'])*6 for r in rows)
 log=(base/f'{family}-fixed-parity-before.log').read_text()
 markers=['control,invalid-neighbor,rows7,retained-stride32,bad-lane3,all-six-complex-outputs,passed','control,malformed-shape,output-unchanged-including-signed-zero,passed','control,symbolica-generated-fixture,configurations=36,complex-outputs=2856,all-six-outputs,nonzero-origin-span,sparse-holes,empty-reactivation-after-outline,alias,reused-stride,scalar-and-batch-exact,passed']
 assert all(log.count(marker)==1 for marker in markers)
 records.append({'family':family,'status':'passed','physical_configurations':len(rows),'physical_complex_outputs':sum(int(r['complex_outputs']) for r in rows),'fixture_configurations':36,'fixture_complex_outputs':2856,'malformed_shape_output_untouched':True,'bad_lane_neighbors_unchanged':True,'strict_old_new':'represented values, precision, signed zeros of all six complex outputs','interpreter_comparison':{k:sum(int(r[k]) for r in rows) for k in ['interpreter_value_mismatches','interpreter_precision_mismatches','interpreter_signed_zero_mismatches']},'compile_elapsed_seconds':build['elapsed_seconds'],'binary_sha256':run['binary_sha256']})
result={'status':'f64-qualified-timing-pending' if len(records)==2 else 'partial','production_changes':False,'domains':['f64'],'higher_precision_and_dual_status':'unqualified for this dense-active-span candidate; allocator experiment does not cover this patch','source_audit':'check_dense_shape.py removes only span metadata and exact duplicate Add/Mul loop; ordered primitives, operand slots, helpers, labels and constants remain unchanged','qualifications':records}
(base/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
