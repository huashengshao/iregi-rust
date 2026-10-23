from pathlib import Path
import csv,hashlib,importlib.util,json,math
base=Path('target/native-shared-binary');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('frozen_benchmark_helper',base/'benchmark_helper.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
expected={(order,batch) for order in ['homogeneous','interleaved','grouped'] for batch in [1,32]}
def parse(lines):
 groups={};iterations={};coordinates=[]
 for row in csv.reader(lines):
  if len(row)!=7 or row[0]!='timing':raise ValueError('invalid row')
  _,order,batch,variant,block,count,elapsed=row;key=(order,int(batch));variant=int(variant);block=int(block);count=int(count);elapsed=int(elapsed)
  if key not in expected or variant not in [0,1] or not 0<=block<21 or count<=0 or elapsed<=0:raise ValueError('invalid coordinate/count/elapsed')
  slots=groups.setdefault(key,[{},{}])[variant]
  if block in slots:raise ValueError('duplicate block')
  slots[block]=elapsed/count;iterations.setdefault(key,set()).add(count);coordinates.append((key,variant,block))
 if set(groups)!=expected or len(coordinates)!=252 or any(set(v)!=set(range(21)) for group in groups.values() for v in group):raise ValueError('incomplete matrix')
 if any(len(v)!=1 for v in iterations.values()):raise ValueError('iteration count differs across pairs/blocks')
 expected_order=[((order,batch),(block+offset)%2,block) for batch in [1,32] for order in ['homogeneous','interleaved','grouped'] for block in range(21) for offset in [0,1]]
 if coordinates!=expected_order:raise ValueError('balanced alternating pair order changed')
 return groups
fixture=[f'timing,{order},{batch},{(block+offset)%2},{block},10,100' for batch in [1,32] for order in ['homogeneous','interleaved','grouped'] for block in range(21) for offset in [0,1]]
assert len(parse(fixture))==6;controls={'complete':True}
for name,rows in [('missing',fixture[:-1]),('duplicate',fixture+[fixture[0]]),('zero_elapsed',[fixture[0].replace(',10,100',',10,0'),*fixture[1:]]),('zero_count',[fixture[0].replace(',10,100',',0,100'),*fixture[1:]]),('shape',[fixture[0]+',extra',*fixture[1:]]),('variable_count',[fixture[0].replace(',10,100',',11,100'),*fixture[1:]]),('pair_order',[fixture[1],fixture[0],*fixture[2:]])]:
 try:parse(rows)
 except ValueError:controls[name]=True
 else:raise AssertionError(name)
before=json.loads((base/'parity-before.json').read_text());after=json.loads((base/'parity-after.json').read_text());initial=json.loads((base/'parity.json').read_text())
for stem,record in [('parity',initial),('parity-before',before),('parity-after',after)]:
 assert record['status']=='passed' and record['binary_unchanged'] and record['inputs_unchanged']
 assert record['csv_sha256']==sha(base/f'{stem}.csv') and record['log_sha256']==sha(base/f'{stem}.log')
 assert record['binary_sha256']==initial['binary_sha256']
 assert (base/f'{stem}.csv').read_bytes()==(base/'parity.csv').read_bytes(),'before/after qualification changed'
rows=[];metadata=[]
for family in ['b0','c0']:
 record=json.loads((base/f'{family}-timing-fixed.json').read_text());csvfile=base/f'{family}-timing-fixed.csv';logfile=base/f'{family}-timing-fixed.log'
 assert record['status']=='passed' and record['binary_unchanged'] and record['protocol']=='shared-binary-fixed-loop-v2'
 assert record['binary_sha256']==initial['binary_sha256'] and record['csv_sha256']==sha(csvfile) and record['log_sha256']==sha(logfile)
 qualification_path=base/'qualification-before-timing.json'
 if not qualification_path.exists():qualification_path=base/'qualification.json'
 assert record['qualification_sha256']==sha(qualification_path),'pre-timing numerical qualification binding changed'
 assert before['finished_unix_time']<=record['started_unix_time']<=record['finished_unix_time']<=after['started_unix_time']
 assert record['command'][:2]==['taskset','-c'] and str(int(record['command'][2]))==record['command'][2]
 groups=parse(csvfile.read_text().splitlines());metadata.append(record)
 for (order,batch),(old,new) in sorted(groups.items()):
  a=[old[k] for k in range(21)];b=[new[k] for k in range(21)];ratio=h.ratio_summary(b,a,{'status':'passed'})
  ratio['definition']='Shared binary native / original native SSA paired block latency;99% bootstrap median CI;CI width <=2% of median required'
  strata={label:h.ratio_summary([new[k] for k in range(parity,21,2)],[old[k] for k in range(parity,21,2)],{'status':'passed'}) for label,parity in [('baseline_first',0),('candidate_first',1)]}
  for stratum in strata.values():stratum['definition']=ratio['definition']
  rows.append({'family':family,'ordering':order,'batch':batch,'baseline_ns':h.summarize(a),'candidate_ns':h.summarize(b),'ratio':ratio,'order_strata':strata,'pairs_candidate_slower':sum(new[k]>old[k] for k in range(21))})
result={'scope':'Isolated B0/C0 generated native paired microbenchmark; no public reduction or original IREGI comparison. Frozen opt2 dependencies/generated opt3 codegen16;one combined all-type executable.','protocol':'shared-binary-fixed-loop-v2','blocks':21,'block_target_ms':30,'calibration':'Separate2ms pilots choose one shared fixed iteration count;one timer pair per block;black_box input/output each call;no timing subtraction','order':'Alternating baseline/candidate first,11/10 pairs. Exact f64 value/precision/signedzero checks before and after calibration and every pair.','all_type_before_after':'80 physical configurations plus guarded and direct alias/precision fixtures on identical binary;before/after CSVs byte-identical to initial qualification','measurement_metadata':metadata,'parser_controls':controls,'benchmark_helper_sha256':sha(base/'benchmark_helper.py'),'rows':rows}
(base/'timing-fixed-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps([{'family':r['family'],'ordering':r['ordering'],'batch':r['batch'],'ratio':r['ratio']['median'],'ci99':r['ratio']['ci99'],'gate':r['ratio']['gate']} for r in rows],indent=2))
