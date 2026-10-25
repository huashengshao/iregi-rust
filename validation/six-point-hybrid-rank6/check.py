#!/usr/bin/env python3
"""Portable saved-source/receipt/Fraction replay; never runs native producers."""
from pathlib import Path,PurePosixPath
from fractions import Fraction as F
from decimal import Decimal,localcontext
import gzip,hashlib,importlib.util,io,json,re,sys,tarfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PARENT='validation/public-six-point-precision-rescue-rank6';PREFIX='/shared/external/iregi/iregi-rust/'
FOCUS='target/six-point-hybrid-focused-tests-v1';V1='target/six-point-hybrid-r6-v1';V2='target/six-point-hybrid-r6-v2';BUILD='target/certified-tensor-qualification/'
def require(ok,why):
 if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'sha256':sha(b),'bytes':len(b)}
def read(b):return json.loads(b)
def safe(n):
 p=PurePosixPath(n);require(bool(n) and not p.is_absolute() and '..' not in p.parts and str(p)==n,'safe payload alias')
def restore_files(m):
 require({str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}==set(m['capsule_files'])|{'manifest.json'},'closed outer inventory')
 for n,v in m['capsule_files'].items():safe(n);require(desc((HERE/n).read_bytes())==v,'outer byte identity '+n)
 for n,v in m['parent_files'].items():require(desc((ROOT/n).read_bytes())==v,'fixed inherited parent '+n)
 spec=importlib.util.spec_from_file_location('hybrid_saved_rescue_parent',ROOT/PARENT/'check.py');parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
 files=parent.restore_files(read((ROOT/PARENT/'manifest.json').read_bytes()));members={}
 with tarfile.open(fileobj=io.BytesIO((HERE/'payload.tar.gz').read_bytes()),mode='r:gz') as a:
  for item in a:
   safe(item.name);require(item.isfile() and item.name not in members,'unique regular member');body=a.extractfile(item).read();require(desc(body)==m['payload_members'].get(item.name),'payload hash '+item.name);members[item.name]=body
 require(set(members)==set(m['payload_members']),'closed archive members')
 for n,b in members.items():require(n not in files or files[n]==b,'body collision');files[n]=b
 for n,v in m['preserved_aliases'].items():
  safe(n);b=files[v['source']];require(desc(b)=={'sha256':v['sha256'],'bytes':v['bytes']},'same-body alias '+n);require(n not in files or files[n]==b,'alias collision');files[n]=b
 return files

def replay(files,m):
 def j(n):return read(files[n])
 def digest(n):return sha(files[n])
 def guards(r):
  require(r['inputs_unchanged'] and not r['cleanup_errors'] and r['cancellation'] is None,'recorded terminal guards/cleanup')
  for n,v in r['inputs'].items():
   alias=n.removeprefix(PREFIX)
   require(digest(alias)==v if alias in files else m['omitted_native_inputs'].get(n)==v,'saved/explicit omitted historical guard '+n)
 def outputs(base,r):
  for n,v in r['outputs'].items():
   if n.startswith('frozen-'):continue
   require(digest(base+'/'+n)==v,'saved output '+base+'/'+n)
 for label,count in [('build-005',76),('build-006',77)]:
  base=BUILD+label;r=j(base+'/receipt.json');require(r['status']=='passed' and r['inputs_unchanged'] and r['source_inputs_unchanged'] and not r['cleanup_errors'],'actual joint build success')
  inv=j(base+'/source-inventory.json');require(len(inv)==count,'exact selected source count')
  for n,v in inv.items():require(digest(base+'/source/'+n)==v,'selected compiler source '+n)
  outputs(base,r)
  require(all(s['returncode']==0 and s['owned_group_gone'] for s in r['steps']),'historical build children collected')
 test=j(FOCUS+'/tests-001/receipt.json');guards(test);outputs(FOCUS+'/tests-001',test)
 require(test['status']=='passed' and len(test['selected_tests'])==13 and not test['unrun_tests'] and len(test['steps'])==14 and not test['numeric_driver_executed'],'thirteen exact focused tests')
 listing=files[FOCUS+'/tests-001/step-0.log'].decode()
 for i,name in enumerate(test['selected_tests'],1):
  log=files[FOCUS+f'/tests-001/step-{i}.log'].decode();require(name+': test' in listing and f'test {name} ... ok' in log,'exact name present and passed')
  require(len(re.findall(r'^test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; \d+ filtered out; finished in .+$',log,re.M))==1,'strict one-test summary')
 require(all(s['returncode']==0 and s['owned_group_gone'] for s in test['steps']),'focused historical terminal children')
 old=j(V1+'/capture-001/receipt.json');guards(old);outputs(V1+'/capture-001',old)
 require(old['status']=='failed' and old['steps'][0]['returncode']==101 and old['steps'][0]['owned_group_gone'],'retained failed nested-flag observer')
 r=j(V2+'/capture-001/receipt.json');guards(r);outputs(V2+'/capture-001',r)
 require(r['status']=='failed' and r['error']=="ValueError('exact one complete raw payload')",'original parser-only failure preserved')
 step=r['steps'][0];require(step['status']=='exited' and step['returncode']==0 and step['owned_group_gone'] and step['elapsed_seconds']<600 and r['elapsed_seconds']<720,'successful bounded native assertion test')
 text=files[V2+'/capture-001/capture.log'].decode();marker='TIRUST_SIX_HYBRID_R6_CAPTURE ';require(text.count(marker)==1,'one raw payload')
 line=next(x for x in text.splitlines() if marker in x);before,_,after=line.partition(marker)
 require(before=='test dispatch::six_hybrid::tests::ordinary_rank_six_hybrid_uses_specialized_pv_and_keeps_fallback_lazy ... ','exact saved libtest prefix')
 require(len(re.findall(r'^test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; \d+ filtered out; finished in .+$',text,re.M))==1,'successful numeric test summary')
 data=j(V2+'/saved-extraction-001/result.json');require(json.loads(after)==data,'extraction equals immutable raw stdout')
 extraction=j(V2+'/saved-extraction-001/receipt.json');require(extraction['parent_controller_receipt_sha256']==digest(V2+'/capture-001/receipt.json') and extraction['outputs']['result.json']==digest(V2+'/saved-extraction-001/result.json') and extraction['native_test_exit_code']==0,'additive extraction binding')
 resources=[json.loads(x.split(' ',1)[1])for x in text.splitlines()if x.startswith('HYBRID_R6_RESOURCE ')];require(len(resources)==1 and resources[0]['pgid']==step['owned_process_group'] and resources[0]['address_space_bytes']==32<<30 and resources[0]['cpu_affinity']==[14],'saved resource/identity witness')
 protocol=j(V2+'/protocol.json');quad='target/quad-iregi-source-audit/capture-v6-001/request-4.stdout';admit='target/quad-iregi-source-audit/independent/resume-auditor-v6-full-array-numeric-review.json'
 require(digest(quad)==protocol['quad_reference_sha256'] and digest(admit)==protocol['quad_admission_sha256'],'qualified original quad hashes')
 admission=j(admit);native=j('target/quad-iregi-source-audit/capture-v6-001/run.json')
 require(admission['retained_private_point_numerically_admitted'] and admission['runtime_receipt_sha256']==digest('target/quad-iregi-source-audit/capture-v6-001/run.json') and native['outputs']['request-4.stdout']==digest(quad),'exact admitted original request')
 refs=[json.loads(x[7:])for x in files[quad].decode().splitlines()if x.startswith('RESULT ')];require(len(refs)==1 and refs[0]['stable'] and len(refs[0]['moments'])==330 and admission['cases'][4]['accepted'],'stable complete IBP reference')
 basis=[[t,x,y,d-t-x-y]for d in range(7)for t in range(d,-1,-1)for x in range(d-t,-1,-1)for y in range(d-t-x,-1,-1)]
 require(data['basis']==basis and data['rank']==6 and data['propagators']==6 and data['components']==1 and data['working_precision']==128 and data['requested_accuracy']==53,'ordinary complete R6 layout')
 require(data['requested_algorithm']=='Hybrid' and data['primary_algorithm']=='PassarinoVeltman' and data['convention']=='IregiNative' and data['tensor_weights']=='Components','requested/actual algorithms and convention')
 def value(s):
  out=[]
  for k,p,n in [('real','real_precision','real_negative_sign'),('imaginary','imaginary_precision','imaginary_negative_sign')]:
   require(isinstance(s[k],str) and type(s[p])is int and 1<=s[p]<=128 and type(s[n])is bool,'rational precision sign snapshot');v=F(s[k]);require(v==0 or s[n]==(v<0),'nonzero sign');out.append(v)
  return tuple(out)
 require(data['input_before']==data['input_after'] and len(data['input_before'])==62,'represented inputs preserved')
 expected=[F(x,4)for q in [[0,0,0,0],[0,4,0,0],[0,0,4,0],[0,0,0,4],[2,0,0,0],[0,4,4,0]]for x in q]+list(map(F,[1,2,3,4,2,3,3]));represented=list(map(value,data['input_before']))
 require(represented[:31]==[(x,F(0))for x in expected] and represented[31:61]==represented[:30] and represented[-1]==(F(0),F(0)),'exact input and invalid-mu neighbor')
 require(data['lane_statuses'][0]=='Success' and data['lane_statuses'][1].startswith('InvalidInput(') and data['lanes'][1]is None and data['fallback_used']==data['pv_fallback_used'] and data['analytic_used']==data['pv_analytic_used'],'statuses/null and actual nested flags')
 require(len(data['lanes'][0])==len(data['pv_lane'])==840,'complete arrays')
 detail=data['execution'];require(detail['engine']=='SixPointHybrid' and detail['primary']['parent_input_rows']==2 and detail['primary']['packed_child_rows']==6 and detail['primary']['packed_parent_rows']==1,'actual packed primary rows')
 require(all(detail[k]==0 for k in ['fallback_rows','fallback_successes','fallback_batches','fallback_preparation_attempts']) and detail['fallback_preparation_error']is None and all(v==0 for v in detail['fallback'].values()),'outer fallback remains genuinely lazy')
 maximum=F(0);count=0;poles=0
 for i,s in enumerate(data['lanes'][0]):
  moment,slot=divmod(i,4);a=value(s);b=tuple(map(F,refs[0]['moments'][moment][slot]));unit=F(2)**(sum(basis[moment])-8)
  require(a==value(data['pv_lane'][i]),'exact PV delegation');err=sum((x-y)**2 for x,y in zip(a,b))/max(unit*unit,sum(x*x for x in b));maximum=max(maximum,err);require(err<=F(1,10**20),'all native Laurent coefficients vs admitted quad');count+=1
  if slot<3:require(sum(x*x for x in a)/(unit*unit)<=F(1,10**20),'massive zero UV/IR control');poles+=1
 saved=j(V2+'/comparison-after-saved-extraction.json');require(saved['status']=='passed' and saved['complete_complex_reference_comparisons']==count and saved['exact_PV_delegations']==count and saved['independent_zero_pole_checks']==poles and saved['failed_comparisons']==0,'saved numeric decision consistency')
 with localcontext()as c:c.prec=100;display=str((Decimal(maximum.numerator)/Decimal(maximum.denominator)).sqrt())
 require(display==saved['maximum_normalized_error'],'exact squared-norm maximum')
 return {'status':'passed_portable_saved_hybrid_rank6_capsule','focused_tests':13,'reference_comparisons':count,'exact_PV_delegations':count,'zero_pole_checks':poles,'maximum_normalized_error':display,'actual_source_files':[76,77],'old_observer_failure_retained':True,'parser_only_controller_failure_retained':True,'one_native_numeric_invocation_in_corrected_cohort':True,'actual_N6_generic_IBP_fallback_success_qualified':False,'public_Dual_generalized_or_performance_qualified':False,'historical_process_absence_replayed_as_saved_attestation_only':True,'new_native_compiler_or_process_jobs':0}
if __name__=='__main__':
 m=read((HERE/'manifest.json').read_bytes());print(json.dumps(replay(restore_files(m),m),indent=2))
