from pathlib import Path
import csv, importlib.util, json, math, hashlib
root=Path.cwd();base=root/'target/native-stack-batch'
spec=importlib.util.spec_from_file_location('iregi_benchmark_run',root/'validation/benchmark/run.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
expected={(order,batch) for order in ['homogeneous','interleaved','grouped'] for batch in [1,32]}
def parse_rows(lines):
 groups={};count=0
 for row in csv.reader(lines):
  if len(row)!=7 or row[0]!='timing':raise ValueError('unexpected timing row shape or marker')
  _,order,batch,variant,block,iterations,elapsed=row;key=(order,int(batch));variant=int(variant);block=int(block);iterations=int(iterations);elapsed=int(elapsed)
  if key not in expected or variant not in [0,1] or not 0<=block<21 or iterations<=0 or elapsed<=0:raise ValueError('invalid timing coordinate/count')
  records=groups.setdefault(key,[{},{}])[variant]
  if block in records:raise ValueError('duplicate timing block')
  value=elapsed/iterations
  if not math.isfinite(value) or value<=0:raise ValueError('nonfinite timing')
  records[block]=value;count+=1
 if set(groups)!=expected or count!=252 or any(set(values)!=set(range(21)) for group in groups.values() for values in group):raise ValueError('incomplete timing matrix')
 return groups
fixture=[f'timing,{order},{batch},{variant},{block},10,100' for order,batch in sorted(expected) for variant in [0,1] for block in range(21)]
assert len(parse_rows(fixture))==6
checks={'complete':True}
for name,bad in [('missing',fixture[:-1]),('duplicate',fixture+[fixture[0]]),('zero_iterations',[fixture[0].replace(',10,100',',0,100'),*fixture[1:]]),('invalid_variant',[fixture[0].replace(',0,0,10,100',',2,0,10,100'),*fixture[1:]]),('shape',[fixture[0]+',extra',*fixture[1:]])]:
 try:parse_rows(bad)
 except ValueError:checks[name]=True
 else:raise AssertionError(f'{name} malformed fixture accepted')
rows=[];families=[]
for family in ['a0','b0','db0','c0','d0']:
 p=base/f'{family}-timing.csv'
 if not p.exists():continue
 timing=json.loads((base/f'{family}-timing.json').read_text());qual=json.loads((base/f"{family}-parity{'-2' if family=='db0' else ''}.json").read_text())
 assert timing['status']==qual['status']=='passed' and timing['binary_unchanged'] and qual['binary_unchanged'] and timing['binary_sha256']==qual['binary_sha256']
 assert hashlib.sha256(p.read_bytes()).hexdigest()==timing['artifacts'][str(p.relative_to(root))]
 groups=parse_rows(p.read_text().splitlines());families.append(family)
 for (order,batch),(old,new) in sorted(groups.items()):
  common=list(range(21));ratio=h.ratio_summary([new[k] for k in common],[old[k] for k in common],{'status':'passed'})
  ratio['definition']='Allocated native / baseline native paired block latency; 99% bootstrap median interval; CI width must be <=2% of median'
  rows.append({'family':family,'order':order,'batch':batch,'baseline_ns':h.summarize([old[k] for k in common]),'candidate_ns':h.summarize([new[k] for k in common]),'ratio':ratio})
result={'scope':'isolated generated scalar-kernel microbenchmark, excludes preparation and public core; shared frozen opt2 runtime, generated generic kernels opt3/codegen16; NOT original IREGI or release end-to-end parity','measurement_overhead':'Instant checked after every kernel call within each30ms block, identical in both variants, not subtracted','cpu_affinity':[0],'blocks':21,'block_target_ms':30,'quiet_window':'root coordinated; owned D0 compile SIGSTOP; all other project compute paused','parser_controls':checks,'qualified_families':families,'unsupported_visible':[{'family':'db0','input':'s=m1_squared=m2_squared=0,mu_squared=1','status':'UndefinedScalelessDerivative','timing':None,'initial_raw_failure':'db0-parity.json','public_guard_and_raw_classification_control':'db0-parity-2.log'}],'rows':rows}
(base/'timing-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ['family','order','batch']}|{'ratio':r['ratio']['median'],'ci99':r['ratio']['ci99'],'gate':r['ratio']['gate']} for r in rows],indent=2))
