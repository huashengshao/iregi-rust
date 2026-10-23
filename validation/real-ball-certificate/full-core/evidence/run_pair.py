"""Bounded private correctness witnesses; durations are not performance evidence."""
from pathlib import Path
import argparse,copy,importlib.util,json,os,subprocess,sys,time
sys.dont_write_bytecode=True
import verify_artifacts as provenance
import witness_inputs as inputs
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('kind',choices=['kernel','physical','typed']);p.add_argument('--output',required=True,type=Path);p.add_argument('--timeout',type=int,default=120);args=p.parse_args()
assert args.timeout>0
args.output.mkdir(parents=True,exist_ok=False)
sha=provenance.sha
scripts={str(path.relative_to(ROOT)):sha(path) for path in [Path(__file__).resolve(),OUT/'verify_artifacts.py',OUT/'witness_inputs.py']}
bindings={variant:provenance.bind_build(variant,args.kind) for variant in ['baseline','candidate']}
closure=provenance.closure_binding()
ledger={'schema':1,'status':'verifying_before','kind':args.kind,'scope':'immutable6b24 baseline versus the same source plus slim9a89286f certificate only; no receipts','performance_gate':False,'cpu_affinity':sorted(os.sched_getaffinity(0)),'closure':closure,'builds':bindings,'scripts':scripts,'rows':[]}
record=args.output/'qualification.json'
def save():record.write_text(json.dumps(ledger,indent=2)+'\n')
def verify():
 for binding in bindings.values():provenance.verify_build(binding)
 for path,digest in scripts.items():assert sha(ROOT/path)==digest,path
 assert provenance.verify_closure(closure)==865
save();verify();ledger['verified_before']=True;ledger['status']='running';save()
bundle=inputs.build_bundle();(args.output/'input-catalog.json').write_bytes(inputs.json_bytes(bundle));ledger['input_catalog_sha256']=sha(args.output/'input-catalog.json');save()
if args.kind=='typed':
 families=['ggh','lightlike_first_static','lightlike_first_dynamic','lightlike_mixed_static','lightlike_mixed_dynamic']
 packets=[{'id':f'{family}_{precision}'} for family in families for precision in ['f64','dd','float128']]
else:packets=bundle[args.kind]

def import_file(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
physical=None
if args.kind=='physical':
 capture_path=inputs.FROZEN/'validation/reference/capture.py';comparer_path=inputs.FROZEN/'validation/physical/compare_cli.py'
 scripts[str(capture_path.relative_to(ROOT))]=sha(capture_path);scripts[str(comparer_path.relative_to(ROOT))]=sha(comparer_path)
 import_file('capture',capture_path);physical=import_file('frozen_physical_comparer',comparer_path)
 refs=json.loads(Path(bundle['independent_references']['canonical_iregi']['path']).read_text());madloop=json.loads(Path(bundle['independent_references']['madloop_preserved']['path']).read_text())
 sample=json.loads((inputs.FROZEN/'validation/physical/ggh-cli-input.json').read_text())
 assert [r['mode'] for r in refs]==[0,1,2] and all(r['returncode']==0 and len(r['results'])==1 for r in refs)
 ledger['independent_comparer_source']=scripts;save()
def validate_typed(value,case):
 inputs.require(value.get('schema')==1 and value.get('kind')=='private_full_core_typed_witness' and value.get('case')==case,'typed response identity differs')
 inputs.require(value.get('status')=='completed' and value.get('master_backend')=='SymbolicaBatch','typed producer failed/backend differs')
 components=1 if case.startswith('ggh_') else (4 if '_mixed_' in case else 2)
 bits={'f64':53,'dd':106,'float128':128}[case.rsplit('_',1)[1]]
 carrier='ordinary' if components==1 else ('static_dual' if '_static_' in case else 'dynamic_hyperdual')
 shape=None if components==1 else ([[0],[1]] if components==2 else [[0,0],[0,1],[1,0],[1,1]])
 n,rank=(3,2) if components==1 else (2,1)
 settings={'propagators':n,'rank':rank,'powers':[1]*n,'dimension_shift':0,'algorithm':'Hybrid','convention':'IregiNative','tensor_weights':'Components','invariants':'FromShifts','input_policy':'Preserve'}
 inputs.require(value.get('working_bits')==bits and value.get('carrier')==carrier and value.get('dual_shape')==shape,'typed precision/carrier/Taylor axes differ')
 inputs.require(value.get('settings')==settings,'typed requested reduction settings differ')
 expected_basis=inputs.BASIS if components==1 else inputs.BASIS[:5]
 inputs.require(value.get('sample_rows')==5 and value.get('components')==components and value.get('basis')==expected_basis,'typed output shape differs')
 inputs.require(value.get('laurent_order')==['uv_single','ir_single','ir_double','finite'] and value.get('accuracy_bits')==53,'typed Laurent/accuracy metadata differs')
 inputs.require(value.get('invalid_scale_lane')==2 and value.get('qualification_pass') is True,'typed lane qualification failed')
 inputs.require(len(value.get('lanes',[]))==5 and len(value.get('inputs',[]))==5,'typed lane/input count differs')
 for row in value['inputs']:
  inputs.require(isinstance(row,list) and len(row)==5*n+1,'typed argument count differs')
  for argument in row:
   inputs.require(isinstance(argument,list) and len(argument)==components,'typed input Taylor width differs')
   for pair in argument:
    inputs.require(isinstance(pair,list) and len(pair)==2,'typed complex input shape differs')
    for scalar in pair:
     inputs.require(isinstance(scalar,dict) and scalar.get('finite') is True and scalar.get('precision_bits')==bits and isinstance(scalar.get('exact_rational'),str) and type(scalar.get('negative_zero')) is bool,'typed input precision/exactness differs')
     inputs._decimal(scalar['decimal'])
 for lane,result in enumerate(value['lanes']):
  inputs.require(result.get('lane')==lane,'typed lane identity differs')
  expected='invalid_input' if lane==2 else 'success'
  inputs.require(result.get('status',{}).get('kind')==expected,'typed lane status differs')
  if lane==2:
   inputs.require(result.get('moments') is None,'failed typed lane exposed coefficients');continue
  moments=result.get('moments');inputs.require(isinstance(moments,list) and len(moments)==len(expected_basis),'typed moment count differs')
  for moment in moments:
   inputs.require(isinstance(moment,list) and len(moment)==4,'typed Laurent count differs')
   for pole in moment:
    inputs.require(isinstance(pole,list) and len(pole)==components,'typed Taylor count differs')
    for pair in pole:
     inputs.require(isinstance(pair,list) and len(pair)==2,'typed complex shape differs')
     for scalar in pair:
      inputs.require(isinstance(scalar,dict) and scalar.get('finite') is True and type(scalar.get('precision_bits')) is int and scalar['precision_bits']>0 and type(scalar.get('negative_zero')) is bool and isinstance(scalar.get('exact_rational'),str),'typed finite/exact scalar metadata differs')
      inputs._decimal(scalar['decimal'])
 for flag in ['invalid_lane_rejected','valid_lanes_successful','finite_successful_values']:
  inputs.require(value.get(flag) is True,'typed outcome flag failed: '+flag)
 inputs._counters(value.get('execution'),value.get('execution'),5,inputs.COUNTERS)

for packet in packets:
 row={'id':packet['id'],'status':'running','runs':{},'performance_gate':False};ledger['rows'].append(row);save();responses={}
 for variant,binding in bindings.items():
  directory=args.output/packet['id']/variant;directory.mkdir(parents=True)
  command=[str(ROOT/binding['binary'])];data=None
  if args.kind=='typed':command.append(packet['id'])
  else:data=inputs.json_bytes(packet['request']);(directory/'request.json').write_bytes(data)
  result={'command':command,'timeout_seconds':args.timeout,'status':'running'};row['runs'][variant]=result;save();started=time.monotonic()
  with (directory/'stdout.log').open('wb') as stdout,(directory/'stderr.log').open('wb') as stderr:
   try:
    process=subprocess.run(command,input=data,stdout=stdout,stderr=stderr,timeout=args.timeout);result['returncode']=process.returncode
   except subprocess.TimeoutExpired:result['returncode']=None;result['timed_out']=True
  result['wall_seconds_not_benchmark']=time.monotonic()-started;result['stdout_sha256']=sha(directory/'stdout.log');result['stderr_sha256']=sha(directory/'stderr.log')
  try:
   parsed=inputs.read_responses(directory/'stdout.log');result['response_count']=len(parsed['records']);result['chatter']=parsed['chatter']
   if len(parsed['records'])==1:responses[variant]=parsed['records'][0]
   result['status']='completed' if result['returncode']==0 and len(parsed['records'])==1 else 'failed'
  except Exception as error:result['status']='failed';result['parse_error']=f'{type(error).__name__}: {error}'
  save()
 if set(responses)==set(bindings):
  if args.kind=='typed':
   errors=[]
   for variant,response in responses.items():
    try:validate_typed(response,packet['id'])
    except Exception as error:errors.append(f'{variant}: {type(error).__name__}: {error}')
   equal=inputs.json_bytes(responses['baseline'])==inputs.json_bytes(responses['candidate'])
   row['comparison']={'passed':equal and not errors,'errors':errors,'complete_responses_equal':equal,'baseline':responses['baseline'],'candidate':responses['candidate'],'performance_gate':False}
  else:row['comparison']=getattr(inputs,'compare_'+args.kind)(packet,responses['baseline'],responses['candidate'])
  if args.kind=='physical':
   checks=[]
   for variant,response in responses.items():
    try:
     for lane,value in enumerate(response['output']['samples']):
      output=copy.deepcopy(response['output']);output['samples']=[value]
      tensor=[{'mode':r['mode'],**physical.compare_tensors(output,sample,r['results'][0],1e-10)} for r in refs]
      graph=physical.compare_physical(output,sample,madloop,physical.CASES['ggh'],1e-10)
      checks.append({'variant':variant,'lane':lane,'tensors':tensor,'graph':graph,'passed':all(c['passed'] for c in tensor) and graph['passed']})
    except Exception as error:checks.append({'variant':variant,'passed':False,'error':f'{type(error).__name__}: {error}'})
   row['independent_checks']=checks
 row['status']='passed' if all(r['status']=='completed' for r in row['runs'].values()) and row.get('comparison',{}).get('passed') is True and all(c['passed'] for c in row.get('independent_checks',[])) else 'failed'
 save();print(args.kind,packet['id'],row['status'],[(k,v['status']) for k,v in row['runs'].items()],flush=True)
verify();inputs.frozen_assets();ledger['verified_after']=True;ledger['status']='passed' if all(row['status']=='passed' for row in ledger['rows']) else 'failed';save();raise SystemExit(0 if ledger['status']=='passed' else 1)
