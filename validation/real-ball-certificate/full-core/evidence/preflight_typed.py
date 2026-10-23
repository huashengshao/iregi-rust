from pathlib import Path
import json,subprocess,time
import verify_artifacts as p
import witness_inputs as w
out=Path(__file__).resolve().parent/'typed-preflight';out.mkdir(exist_ok=False)
binding=p.bind_build('candidate','typed');closure=p.closure_binding();p.verify_build(binding);p.verify_closure(closure)
state={'scope':'candidate-only diagnostic preflight; matched full-shape comparison remains pending','performance_gate':False,'build':binding,'closure':closure,'rows':[]};path=out/'preflight.json'
def save():path.write_text(json.dumps(state,indent=2)+'\n')
save()
for family in ['ggh','lightlike_first_static','lightlike_first_dynamic','lightlike_mixed_static','lightlike_mixed_dynamic']:
 for precision in ['f64','dd','float128']:
  case=f'{family}_{precision}';row={'case':case};state['rows'].append(row);save();start=time.monotonic()
  with (out/f'{case}.stdout').open('wb') as stdout,(out/f'{case}.stderr').open('wb') as stderr:
   try:process=subprocess.run([str(p.ROOT/binding['binary']),case],stdout=stdout,stderr=stderr,timeout=90);row['returncode']=process.returncode
   except subprocess.TimeoutExpired:row['returncode']=None;row['timed_out']=True
  row['wall_seconds_not_benchmark']=time.monotonic()-start
  parsed=w.read_responses(out/f'{case}.stdout');row['record_count']=len(parsed['records']);row['stdout_sha256']=p.sha(out/f'{case}.stdout');row['stderr_sha256']=p.sha(out/f'{case}.stderr')
  row['local_pass']=row['returncode']==0 and len(parsed['records'])==1 and parsed['records'][0].get('case')==case and parsed['records'][0].get('qualification_pass') is True
  if len(parsed['records'])==1:row['record']=parsed['records'][0]
  save();print(case,row['local_pass'],row['returncode'],flush=True)
p.verify_build(binding);p.verify_closure(closure);state['verified_after']=True;save()
