from pathlib import Path
from collections import Counter
import csv, hashlib, json
root=Path.cwd();base=root/'target/native-stack-batch'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=json.loads((base/'d0-parity.json').read_text());build=json.loads((base/'d0-build.json').read_text())
assert run['status']=='passed' and run['exit_code']==0 and run['binary_unchanged']
assert build['exit_code']==0 and not build['changed']
assert run['binary_sha256']==build['binary_sha256']
for name,digest in run['artifacts'].items():assert sha(root/name)==digest,(name,'changed')
for name,digest in build['inputs'].items():assert sha(root/name)==digest,(name,'changed')
rows=list(csv.DictReader((base/'d0-parity.csv').open()))
expected=Counter((domain,order,n) for domain,ns in [('f64',[0,1,3,7,32,3]),('DoubleFloat',[7,1]),('Float256',[7,1])] for n in ns for order in ['homogeneous','interleaved','grouped','reversed'])
assert Counter((r['domain'],r['ordering'],int(r['rows'])) for r in rows)==expected
assert all(r['kind']=='parity' and int(r['complex_outputs'])==int(r['rows'])*6 for r in rows)
keys=['complex_outputs','interpreter_value_mismatches','interpreter_precision_mismatches','interpreter_signed_zero_mismatches']
by_domain={d:{'configurations':sum(r['domain']==d for r in rows),**{k:sum(int(r[k]) for r in rows if r['domain']==d) for k in keys}} for d in ['f64','DoubleFloat','Float256']}
events=[json.loads(line) for line in (base/'build-pauses.jsonl').read_text().splitlines()]
assert len(events)%2==0
pauses=[]
for stop,resume in zip(events[::2],events[1::2]):
 assert stop['action']=='stop' and resume['action']=='continue' and stop['driver_pid']==resume['driver_pid']==19758 and resume['unix_time']>stop['unix_time']
 pauses.append({'stop_unix_time':stop['unix_time'],'resume_unix_time':resume['unix_time'],'paused_seconds':resume['unix_time']-stop['unix_time']})
paused=sum(p['paused_seconds'] for p in pauses)
report={'status':'passed','family':'d0','configurations':len(rows),'complex_outputs':sum(int(r['complex_outputs']) for r in rows),'strict_old_new':'exact represented value, precision, signed zero, all six outputs','by_domain':by_domain,'native_interpreter_exact_agreement':False,'interpreter_differences_are_separate_from_strict_native_parity':True,'interpreter_nonfinite_controls':'fail qualification','binary_sha256':run['binary_sha256'],'parity_csv_sha256':sha(base/'d0-parity.csv'),'runtime_seconds':run['elapsed_seconds'],'runtime_cpu_affinity':[20,21],'build':{'elapsed_wall_seconds':build['elapsed_seconds'],'recorded_paused_wall_seconds':paused,'elapsed_wall_excluding_recorded_pauses_seconds':build['elapsed_seconds']-paused,'elapsed_excluding_pauses_is_cpu_time':False,'pause_intervals':pauses},'performance':'unmeasured with corrected fixed-loop protocol; no adoption claim','numerical_domains':['f64','DoubleFloat','Float256']}
(base/'d0-qualification.json').write_text(json.dumps(report,indent=2)+'\n')
q=json.loads((base/'qualification.json').read_text())
q['status']='all-five-families-native-parity-passed-performance-rejected-pending-d0-timing'
q['runtime_cpu_affinity']={'a0_b0_db0_c0':[12,13],'d0':[20,21]}
q['qualifications']=[r for r in q['qualifications'] if r['family']!='d0']+[{'family':'d0','status':'passed','configurations':40,'complex_outputs':report['complex_outputs'],'strict_old_new':report['strict_old_new'],'interpreter_comparison':{k:sum(int(r[k]) for r in rows) for k in keys[1:]},'run_report':'target/native-stack-batch/d0-parity.json','binary_sha256':run['binary_sha256'],'detailed_qualification':'target/native-stack-batch/d0-qualification.json'}]
q['configurations']=sum(r['configurations'] for r in q['qualifications']);q['complex_outputs']=sum(r['complex_outputs'] for r in q['qualifications'])
q['pending']=['D0 f64-only fixed-loop compile, qualification and kernel timings in separately granted quiet window']
(base/'qualification.json').write_text(json.dumps(q,indent=2)+'\n')
print(json.dumps(report,indent=2))
