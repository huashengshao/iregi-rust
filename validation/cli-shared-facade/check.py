"""Portable stdlib replay of the focused CLI facade evidence; no native jobs."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,importlib.util,io,json,re,tarfile
HERE=Path(__file__).resolve().parent;COUNT=0
FIELDS=('input_rows','argument_rows','master_family_batches','master_rows','pentagon_box_rows','reduction_rows','fallback_rows','fallback_successes','analytic_rows')
POLES=['uv1','ir1','ir2','finite']
TESTS=['facade_cli_keeps_default_hybrid_and_real_failed_lane','facade_cli_rescue_retains_actual_generic_primary_metadata','precision_policy_defaults_preserve_behavior_and_scale_rescue','precision_policy_rejects_inconsistent_accuracy_and_verification','decimal_negative_zero_survives_input_conversion','decimal_input_keeps_bits_beyond_binary64','rationals_and_number_policy_are_explicit','reference_json_numbers_preserve_original_decimal_digits','legacy_policy_defaults_and_threshold_tokens_are_forwarded_exactly','unsupported_or_invalid_legacy_configuration_is_rejected_by_core','full_dimension_offset_maps_to_core_half_shift','supplied_scalar_products_keep_precision_and_packing','comparison_scale_accounts_for_kinematics_beyond_mu']
TESTS=['tests::'+n for n in TESTS]
def require(ok,why):
 global COUNT
 if not ok:raise ValueError(why)
 COUNT+=1
def sha(b):return hashlib.sha256(b).hexdigest()
def read(b):return json.loads(b)
def restore_files(manifest=None):
 if manifest is None:manifest=read((HERE/'manifest.json').read_bytes())
 for name,digest in manifest['capsule_files'].items():require(sha((HERE/name).read_bytes())==digest,'capsule file '+name)
 parent=HERE/manifest['parent']['directory'];parent_manifest=parent/'manifest.json';checker=parent/'check.py'
 require(sha(parent_manifest.read_bytes())==manifest['parent']['manifest_sha256'],'exact durable source parent')
 require(sha(checker.read_bytes())==manifest['parent']['checker_sha256'],'exact parent restoration checker')
 spec=importlib.util.spec_from_file_location('cli_qualified_source_parent',checker);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 values=module.restore_files(read(parent_manifest.read_bytes()));root=manifest['historical_root']
 values.update({root+'/'+k:b for k,b in list(values.items()) if not Path(k).is_absolute()})
 objects={}
 with tarfile.open(HERE/'evidence.tar.gz','r:gz') as tar:
  for item in tar:
   p=Path(item.name);require(item.isfile() and not p.is_absolute() and '..' not in p.parts and item.name not in objects,'safe unique evidence member');objects[item.name]=tar.extractfile(item).read()
 require({n:{'sha256':sha(b),'bytes':len(b)} for n,b in objects.items()}==manifest['evidence'],'complete evidence archive')
 for name,item in manifest['inherited_aliases'].items():
  body=values[item['parent_alias']];require(sha(body)==item['sha256'],'reused source binding');values[name]=body
 for name,item in manifest['aliases'].items():
  body=objects[item['member']];require(sha(body)==item['sha256'],'local source/evidence binding');values[name]=body
 return values

def replay(files,m):
 root=m['historical_root'];prefix=root+'/'+m['private_prefix'];by_sha={sha(b) for b in files.values()}
 def data(path):return read(files[path if path.startswith('/') else root+'/'+path])
 def local(path):return data(prefix+'/'+path)
 def binding(name,digest):
  if name in m['omitted_compiled_artifacts']:require(m['omitted_compiled_artifacts'][name]==digest,'declared compiled omission');return
  if name in files and sha(files[name])==digest:require(True,'exact captured path binding');return
  # The two actual builds intentionally saw different test-only main.rs bytes.
  require(name==root+'/crates/iregi-cli/src/main.rs' and digest in by_sha,'explicit before/after test source context')
 def receipt(phase,status):
  r=local(phase+'/receipt.json');require(r['status']==status and r.get('inputs_unchanged') is True and not r['cleanup_errors'],'terminal guarded phase '+phase)
  require(r['elapsed_seconds']<=r['total_seconds'],'finite total '+phase)
  for name,digest in r.get('inputs',{}).items():binding(name,digest)
  for name,digest in r.get('saved_files',{}).items():binding(name if name.startswith('/') else root+'/'+name,digest)
  for step in r['steps']:require(step['owned_group_gone'] is True,'saved owned-group cleanup '+phase)
  return r
 first=local('build-001/receipt.json');require(first['status']=='failed' and first['steps']==[],'preserved zero-command preflight failure')
 original=receipt('build-002','passed');require(len(original['steps'])==3 and len(original['source_files'])==77,'three actual Cargo products/source context')
 for step in original['steps']:require(step['status']=='exited' and step['returncode']==0 and step['command'][:3]==['taskset','-c','18,20,22,24'],'successful exact Cargo products')
 for label,key,test in [('highpoint-example-build','highpoint_public',False),('cli-build','cli',False),('cli-tests-build','tests',True)]:
  a=local('build-002/'+label+'-artifact.json');require(bool(a['executable']) and a['profile']['test'] is test,'actual tagged Cargo artifact')
  product=original['products'][key];binding(product['path'],product['sha256'])
 failed=receipt('tests-001','failed');require(failed['admitted_tests']==[] and len(failed['steps'])==2 and failed['steps'][1]['returncode']==101,'preserved first test-only failure')
 require('contains("scale")' in files[prefix+'/tests-001/exact-0.log'].decode(),'exact original wording failure')
 initial_n7=receipt('n7-001','failed');require(initial_n7['error']=="RuntimeError('cancelled by signal 14')",'preserved first N7 resource-bound timeout')
 require(local('n7-001/capture/report.json')['status']=='running' and not local('n7-001/capture/report.json')['checks'],'no incomplete N7 numerical success')
 fixed=receipt('test-fix-build-001','passed');require(len(fixed['steps'])==1 and len(fixed['source_files'])==77,'one corrected test product only')
 require({n for n,h in original['source_files'].items() if fixed['source_files'][n]!=h}=={'crates/iregi-cli/src/main.rs'},'only test assertion source changes')
 old=files[prefix+'/build-002/source-snapshot/crates/iregi-cli/src/main.rs'];new=files[prefix+'/test-fix-build-001/source-snapshot/crates/iregi-cli/src/main.rs']
 before=b'assert!(output["samples"][1]["reason"].as_str().unwrap().contains("scale"));'
 after=b'assert_eq!(output["samples"][1]["reason"], "InvalidInput(\\\"mu must be positive and real\\\")");'
 require(old.count(before)==1 and old.replace(before,after)==new,'one exact test-only assertion fix')
 tests=receipt('test-fix-tests-001','passed');require(tests['admitted_tests']==TESTS and len(tests['steps'])==14,'all thirteen strict corrected tests')
 listing=files[prefix+'/test-fix-tests-001/listing.log'].decode();require(set(re.findall(r'^(.+): test$',listing,re.M))==set(TESTS),'strict complete listing')
 for i,name in enumerate(TESTS):
  log=files[prefix+'/test-fix-tests-001/exact-'+str(i)+'.log'].decode()
  require(re.search(r'^test '+re.escape(name)+r' \.\.\. ok$',log,re.M) is not None and 'test result: ok. 1 passed; 0 failed; 0 ignored;' in log,'strict real test '+name)
  require(tests['steps'][i+1]['status']=='exited' and tests['steps'][i+1]['returncode']==0,'actual strict test child')
 counts={'low_complex_slots':0,'n6_complex_slots':0,'n7_complex_slots':0};maxima={k:F(0) for k in counts}
 def pair(v):
  require(isinstance(v,list) and len(v)==2 and all(isinstance(x,str) for x in v),'complete represented complex pair');return tuple(map(F,v))
 def compare(got,expected,key,scale=F(1)):
  value=pair(got);error=sum(abs(a-b) for a,b in zip(value,expected))/(scale+sum(map(abs,expected)))
  require(error<=F(1,10**10),'every complex coefficient '+key);counts[key]+=1;maxima[key]=max(maxima[key],error)
 def execution(v,kind,packed=None):
  s=v['execution'];d=v['engine_execution'];require(set(s)==set(FIELDS) and d['engine']==kind and s['input_rows']==2,'actual tagged logical rows')
  require(all(type(x)is int and x>=0 for x in s.values()) and s['master_rows']>0,'nonzero actual work')
  if kind=='Generic':require(s==d['execution'],'generic summary uses actual counters')
  else:
   require(d['parent_input_rows']==2 and d['child_batch_calls']==d['parent_batch_calls']==1 and d['packed_child_rows']==packed and d['packed_parent_rows']==1,'actual thin packing')
   require(d['child_execution']['input_rows']==packed and d['parent_execution']['input_rows']==1,'actual child/parent logical rows')
   for name in FIELDS[1:]:require(s[name]==d['child_execution'][name]+d['parent_execution'][name],'summary counts nested work once')
   for name in ['child_certificate_execution','parent_certificate_execution']:require(set(d[name])=={'input_rows','evaluated_rows','passes','reduction_batches'},'separate certificate counters')
 def smoke(phase,names):
  r=receipt(phase,'passed');report=local(phase+'/capture/report.json')
  require(report['status']=='passed' and report['checks']==names and report['binary_sha256']==original['products']['cli']['sha256'],'complete smoke '+phase)
  require(sha(files[r['smoke_report']['path']])==r['smoke_report']['sha256'],'exact smoke report')
  for name,h in report['inputs'].items():binding(name if name.startswith('/') else root+'/'+name,h)
  return report
 smoke('low-001',['compare-bubble','run-default-hybrid','doublefloat-bubble','rescue-invalid-neighbor'])
 low=lambda name:local('low-001/capture/'+name+'.stdout')
 compared=low('compare-bubble');require(compared['passed']==1 and compared['failed']==0 and len(compared['cases'])==1,'existing full reference compare')
 case=compared['cases'][0];require(case['engine_execution']['engine']=='Generic' and case['execution']==case['engine_execution']['execution'],'actual compare engine counters')
 ordinary=low('run-default-hybrid');dd=low('doublefloat-bubble');rescue=low('rescue-invalid-neighbor')
 basis=[[t,x,y,r-t-x-y] for r in range(3) for t in range(r,-1,-1) for x in range(r-t,-1,-1) for y in range(r-t-x,-1,-1)]
 require(len(basis)==15 and ordinary['algorithm_requested']=='Hybrid','default Hybrid with full rank2')
 for value,statuses in [(ordinary,['success','success']),(dd,['success','success']),(rescue,['success','failed'])]:
  execution(value,'Generic');require(value['basis']==basis and value['poles']==POLES and len(value['samples'])==2,'complete low inventory')
  require([s['status'] for s in value['samples']]==statuses,'lane outcomes remain independent')
  for row in value['samples']:
   if row['status']=='success':require(len(row['moments'])==15 and all(len(z)==4 for z in row['moments']),'full successful rank2 array')
   else:require(row.get('moments') is None,'failed lane has no successful-zero array')
 for row in range(2):
  for a,b in zip(dd['samples'][row]['moments'],ordinary['samples'][row]['moments']):
   for actual,expected in zip(a,b):compare(actual,pair(expected),'low_complex_slots')
  require(len(ordinary['samples'][row]['integral'])==4,'Symbolica graph numerator contraction returned')
 for a,b in zip(rescue['samples'][0]['moments'],dd['samples'][0]['moments']):
  for actual,expected in zip(a,b):compare(actual,pair(expected),'low_complex_slots')
 require(rescue['diagnostics'] is None and rescue['engine_execution']['certificate_execution'] is None,'rescue unavailable observations honestly null')
 require([r['precision_rescue']['status'] for r in rescue['samples']]==['converged','not_requested'] and rescue['rescue_execution']['accepted_rows']==1,'precision verification and failed-lane isolation')
 for phase,n,rank,saved_path,fixture_path in [('n6-001',6,3,'validation/highpoint-six-point-rank7-current/rank7-128/result.json','validation/public-highpoint/fixture-conditioned_masses.json'),('n7-retry-001',7,0,'validation/highpoint-seven-point-current-cargo/captures/capture128.json','validation/highpoint-seven-point-current-cargo/fixture.json')]:
  report=smoke(phase,['n6' if n==6 else 'n7']);value=local(phase+'/capture/'+('n6' if n==6 else 'n7')+'.stdout');saved=data(saved_path);fixture=data(fixture_path);sample=fixture['samples'][0];props=sample['propagators'][:n]
  exact=[[str(F(v)),'0'] for p in props for v in p['shift']]+[[str(F(v)) for v in p['mass_squared']] for p in props]+[[str(F(sample['mu'])),'0']]
  require([[F(a),F(b)] for a,b in exact]==[[F(a),F(b)] for a,b in saved['input_exact_rational'][0]],'every same-input retained highpoint parameter')
  expected=dict(saved['settings']);expected['rank']=rank
  require(value['settings']==expected and expected['powers']==[1]*n and expected['dimension_shift']==0 and expected['convention']=='IregiNative' and expected['tensor_weights']=='Components','same highpoint mathematical settings')
  require(value['algorithm_requested']==value['algorithm_used']=='PassarinoVeltman' and value['precision_bits']==128 and value['precision_control']['accuracy_bits']==53,'actual requested highpoint precision/method')
  require(value['poles']==POLES and value['basis']==saved['basis'][:len(value['basis'])] and len(value['basis'])==(35 if n==6 else 1),'full requested basis and Laurent order')
  require([s['status'] for s in value['samples']]==['success','failed'] and value['samples'][1].get('moments') is None and len(value['diagnostics'])==2,'highpoint invalid neighbor isolated')
  execution(value,'SixPoint' if n==6 else 'SevenPoint',6 if n==6 else 21)
  moments=value['samples'][0]['moments'];require(len(moments)==len(value['basis']),'complete successful highpoint moments')
  key='n6_complex_slots' if n==6 else 'n7_complex_slots'
  for alpha,moment,prior in zip(value['basis'],moments,saved['lanes'][0]['moments']):
   require(len(moment)==len(prior)==4,'all four highpoint slots')
   for actual,expected in zip(moment,prior):compare(actual,(F(expected['real']),F(expected['imaginary'])),key,F(sample['mu'])**(sum(alpha)+4-2*n))
  require(report['saved_comparison']['complex_slots']==counts[key] and F(report['saved_comparison']['maximum_error_exact'])==maxima[key],'independently reconstructed highpoint maximum/count')
 require(counts=={'low_complex_slots':180,'n6_complex_slots':140,'n7_complex_slots':4},'complete saved comparison inventory')
 return {'status':'passed_portable_focused_CLI_facade','checks':COUNT,'strict_tests':13,'complex_comparisons':counts,'maximum_errors_exact':{k:str(v) for k,v in maxima.items()},'preserved_failed_phases':['build-001','tests-001','n7-001'],'native_jobs':0,'compiler_jobs':0,'performance_qualified':False,'blanket_reduction_domain_qualified':False}
if __name__=='__main__':
 manifest=read((HERE/'manifest.json').read_bytes());print(json.dumps(replay(restore_files(manifest),manifest)))
