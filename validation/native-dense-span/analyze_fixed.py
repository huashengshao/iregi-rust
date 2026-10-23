from pathlib import Path
import csv, importlib.util, json, math, hashlib
from collections import Counter
root=Path.cwd();base=root/'target/native-dense-span'
spec=importlib.util.spec_from_file_location('iregi_benchmark_run',root/'validation/benchmark/run.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
expected={(order,batch) for order in ['homogeneous','interleaved','grouped'] for batch in [1,32]}
def parse_rows(lines):
 groups={};iteration_counts={};count=0
 for row in csv.reader(lines):
  if len(row)!=7 or row[0]!='timing':raise ValueError('unexpected timing row shape or marker')
  _,order,batch,variant,block,iterations,elapsed=row;key=(order,int(batch));variant=int(variant);block=int(block);iterations=int(iterations);elapsed=int(elapsed)
  if key not in expected or variant not in [0,1] or not 0<=block<21 or iterations<=0 or elapsed<=0:raise ValueError('invalid timing coordinate/count')
  iteration_counts.setdefault(key,set()).add(iterations)
  records=groups.setdefault(key,[{},{}])[variant]
  if block in records:raise ValueError('duplicate timing block')
  value=elapsed/iterations
  if not math.isfinite(value) or value<=0:raise ValueError('nonfinite timing')
  records[block]=value;count+=1
 if set(groups)!=expected or count!=252 or any(set(values)!=set(range(21)) for group in groups.values() for values in group):raise ValueError('incomplete timing matrix')
 if any(len(counts)!=1 for counts in iteration_counts.values()):raise ValueError('fixed protocol requires identical iteration count across paired blocks')
 return groups
fixture=[f'timing,{order},{batch},{variant},{block},10,100' for order,batch in sorted(expected) for variant in [0,1] for block in range(21)]
assert len(parse_rows(fixture))==6
checks={'complete':True}
for name,bad in [('missing',fixture[:-1]),('duplicate',fixture+[fixture[0]]),('zero_iterations',[fixture[0].replace(',10,100',',0,100'),*fixture[1:]]),('invalid_variant',[fixture[0].replace(',0,0,10,100',',2,0,10,100'),*fixture[1:]]),('shape',[fixture[0]+',extra',*fixture[1:]]),('varying_fixed_count',[fixture[0].replace(',10,100',',11,100'),*fixture[1:]])]:
 try:parse_rows(bad)
 except ValueError:checks[name]=True
 else:raise AssertionError(f'{name} malformed fixture accepted')
rows=[];families=[];cpu_by_family={}
for family in ['b0','c0']:
 p=base/f'{family}-timing-fixed.csv'
 if not p.exists():continue
 timing=json.loads((base/f'{family}-timing-fixed.json').read_text())
 assert timing['command'][:2]==['taskset','-c']
 assigned=[int(v) for v in timing['command'][2].split(',')]
 assert len(assigned)==1 and assigned[0]>=0,'timings require one pinned core'
 cpu_by_family[family]=assigned
 quals=[json.loads((base/f'{family}-fixed-parity-{phase}.json').read_text()) for phase in ['before','after']]
 assert timing['protocol']=='dense-span-fixed-loop-v2' and timing['status']=='passed' and timing['binary_unchanged']
 for phase,qual in zip(['before','after'],quals):
  assert qual['status']=='passed' and qual['binary_unchanged'] and timing['binary_sha256']==qual['binary_sha256'] and qual['protocol']=='dense-span-fixed-loop-v2'
  csv_path=base/f'{family}-fixed-parity-{phase}.csv'
  assert hashlib.sha256(csv_path.read_bytes()).hexdigest()==qual['artifacts'][str(csv_path.relative_to(root))]
  parity=list(csv.DictReader(csv_path.open()))
  expected_parity=Counter((order,rows) for order in ['homogeneous','interleaved','grouped','reversed'] for rows in [0,1,3,7,32,3])
  assert len(parity)==24 and all(r['domain']=='f64' and r['kind']=='parity' and int(r['complex_outputs'])==int(r['rows'])*6 for r in parity)
  assert Counter((r['ordering'],int(r['rows'])) for r in parity)==expected_parity
 assert quals[0]['finished_unix_time']<=timing['started_unix_time']<=timing['finished_unix_time']<=quals[1]['started_unix_time']
 assert hashlib.sha256(p.read_bytes()).hexdigest()==timing['artifacts'][str(p.relative_to(root))]
 groups=parse_rows(p.read_text().splitlines());families.append(family)
 for (order,batch),(old,new) in sorted(groups.items()):
  common=list(range(21));ratio=h.ratio_summary([new[k] for k in common],[old[k] for k in common],{'status':'passed'})
  ratio['definition']='Dense-span native / original native SSA paired block latency; 99% bootstrap median interval; CI width must be <=2% of median'
  rows.append({'family':family,'order':order,'batch':batch,'baseline_ns':h.summarize([old[k] for k in common]),'candidate_ns':h.summarize([new[k] for k in common]),'ratio':ratio})
result={'scope':'isolated generated scalar-kernel microbenchmark, excludes preparation and public core; shared frozen opt2 runtime, generated generic kernels opt3/codegen16; NOT original IREGI or release end-to-end parity','protocol':'dense-span-fixed-loop-v2','measurement_overhead':'One Instant start/elapsed pair per fixed loop block; black_box input/output each call; no overhead subtraction; independent 2ms pilots choose shared iteration count targeting30ms mean cost' ,'qualification':'24 f64 configurations before and after timing on exact measured binary; dense-span candidate qualifies f64 only; prior allocator-domain evidence does not qualify this candidate','cpu_affinity':sorted({cpu for assigned in cpu_by_family.values() for cpu in assigned}),'cpu_affinity_by_family':cpu_by_family,'blocks':21,'block_target_ms':30,'quiet_window':'root coordinated; all project compute held; owned build stop/resume records retained when applicable','parser_controls':checks,'qualified_families':families,'invalid_neighbor_control':'Raw NaN lane classifications match; all valid neighbors match clean outputs; existing public guard reports NonFiniteInput for injected lane','rows':rows}
assert families,'no complete fixed-protocol measurements yet'
(base/'timing-fixed-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ['family','order','batch']}|{'ratio':r['ratio']['median'],'ci99':r['ratio']['ci99'],'gate':r['ratio']['gate']} for r in rows],indent=2))
