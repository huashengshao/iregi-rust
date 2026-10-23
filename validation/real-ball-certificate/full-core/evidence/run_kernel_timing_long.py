"""Separate preregistered longer run; do not overwrite the original 21-block evidence."""
from pathlib import Path
import argparse,copy,datetime,importlib.util,json,math,os,platform,sys,time
import verify_artifacts as provenance
import witness_inputs as inputs
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);parser.add_argument('--quiet-note',required=True);parser.add_argument('--cpu',type=int,default=254);args=parser.parse_args()
assert args.cpu>=0 and args.cpu in os.sched_getaffinity(0),'selected CPU is outside current allowed affinity'
args.output.mkdir(parents=True,exist_ok=False);os.sched_setaffinity(0,{args.cpu})
source=inputs.FROZEN/'validation/benchmark/run.py';spec=importlib.util.spec_from_file_location('frozen_kernel_harness',source);kernel=importlib.util.module_from_spec(spec);spec.loader.exec_module(kernel)
sha=provenance.sha;parent_manifest=json.loads((provenance.CLOSURE/'manifest.json').read_text())['workspace_build_manifest'];parent=json.loads(Path(parent_manifest).read_text());assert sha(source)==parent['source_sha256']['validation/benchmark/run.py']
bindings={v:provenance.bind_build(v,'kernel') for v in ['baseline','candidate']};closure=provenance.closure_binding()
correctness_path=OUT/'kernel-paired/qualification.json';correctness=json.loads(correctness_path.read_text());assert correctness['status']=='passed' and correctness['verified_before'] and correctness['verified_after'];assert correctness['builds']==bindings
scripts={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__).resolve(),OUT/'verify_artifacts.py',OUT/'witness_inputs.py',source]}
bundle=inputs.build_bundle();(args.output/'input-catalog.json').write_bytes(inputs.json_bytes(bundle))
packets=[p for p in bundle['kernel'] if len(p['lane_roles']) in [1,32] and 'mixed-invalid' not in p['id']]
assert len(packets)==4
cpu_info={}
for block in Path('/proc/cpuinfo').read_text().split('\n\n'):
 fields={k.strip():v.strip() for line in block.splitlines() if ':' in line for k,v in [line.split(':',1)]}
 if fields.get('processor')==str(args.cpu):cpu_info=fields;break
frequency=Path(f'/sys/devices/system/cpu/cpu{args.cpu}/cpufreq')
environment={'cpu_index':args.cpu,'python':sys.version,'platform':platform.platform(),'hostname':platform.node(),'cpu':cpu_info,'frequency':{p.name:p.read_text().strip() for p in frequency.glob('*') if p.is_file() and os.access(p,os.R_OK)}}
state={'schema':1,'status':'verifying_before','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Isolated immutable6b24 binary64 Hybrid ggH tensor kernel: original ComplexBall versus slim RealBall certificate. No receipts; no IREGI/MadLoop/end-to-end performance claim.','quiet_note':args.quiet_note,'environment':environment,'input_catalog_sha256':sha(args.output/'input-catalog.json'),'cpu_affinity':[args.cpu],'builds':bindings,'closure':closure,'scripts':scripts,'correctness_qualification_sha256':sha(correctness_path),'protocol':{'blocks':41,'warmup_blocks':5,'calibration_initial_warmup_calls':5,'minimum_target_block_ms':200,'calibration_acceptance':'Both observed calibration block durations >=200ms; at most8 attempts;1.10 scaling margin','order':'alternating baseline-first/candidate-first','same_iterations_for_both':True,'profile':False,'cache':'Persistent warm topology/rank plans; repeated fixed-point lanes; no output memoization; identical post-timing full outputs requested.','statistics':'existing validation/benchmark/run.py ratio_summary; 10000 paired bootstrap median resamples;99%CI;width<=2%','request_timeout_seconds':90},'rows':[{'id':p['id'],'status':'not-run','blocks':[]} for p in packets]}
registration_path=OUT/'kernel-long-registration.json';registration=json.loads(registration_path.read_text());assert registration['status']=='registered_not_run' and registration['source_sha256']==sha(Path(__file__));assert registration['builds']==bindings and registration['input_catalog_sha256']==state['input_catalog_sha256'];assert registration['protocol']['case_ids']==[p['id'] for p in packets];assert registration['protocol']['cpu']==args.cpu
state['preregistration']={'path':str(registration_path.relative_to(ROOT)),'sha256':sha(registration_path),'content':registration}
record=args.output/'qualification.json'
def save():kernel.save(record,state)
def verify():
 assert sha(registration_path)==state['preregistration']['sha256']
 for b in bindings.values():provenance.verify_build(b)
 for path,digest in scripts.items():assert sha(ROOT/path)==digest,path
 assert sha(args.output/'input-catalog.json')==state['input_catalog_sha256'];assert sha(correctness_path)==state['correctness_qualification_sha256'];assert provenance.verify_closure(closure)==865
 inputs.frozen_assets()
save();verify();state['verified_before']=True;state['status']='running';save()
processes={};executed={};passed=True
try:
 for variant,binding in bindings.items():
  frozen=kernel.freeze_executable(ROOT/binding['binary'],binding['binary_sha256'],'slim-'+variant);executed[variant]={'path':str(frozen.relative_to(ROOT)),'sha256':sha(frozen)};processes[variant]=kernel.Process(frozen,variant,args.output,90)
 state['executed']=executed;save()
 for packet,row in zip(packets,state['rows'],strict=True):
  row['status']='running';save();directory=args.output/packet['id'];directory.mkdir()
  def pair(phase,index,iterations):
   request=copy.deepcopy(packet['request']);request.update(id=f'{packet["id"]}:{phase}:{index}',profile=False,iterations=iterations,warmup=5 if phase=='calibration' else 0,repeats=1)
   test=copy.deepcopy(packet);test.update(id=request['id'],request=request,request_sha256=inputs.json_sha256(request))
   responses={};order=['baseline','candidate'] if index%2==0 else ['candidate','baseline']
   for variant in order:
    responses[variant]=processes[variant].request(inputs.json_bytes(request).decode())
    path=directory/f'{phase}-{index:02d}-{variant}.json';path.write_bytes(inputs.json_bytes(responses[variant]))
   check=inputs.compare_kernel(test,responses['baseline'],responses['candidate'])
   if not check['passed']:raise ValueError('full-output mismatch: '+repr(check['errors']))
   values={}
   for variant,response in responses.items():
    raw=response.get('total_ns');assert isinstance(raw,list) and len(raw)==1 and type(raw[0]) in [float,int] and math.isfinite(raw[0]) and raw[0]>0
    values[variant]=float(raw[0])
   summary={'phase':phase,'index':index,'order':order,'iterations':iterations,'request_sha256':test['request_sha256'],'timings_ns_per_batch':values,'full_output_slots_checked':check['complex_slots_checked'],'full_outputs_exact':True,'responses':{v:{'path':str((directory/f'{phase}-{index:02d}-{v}.json').relative_to(args.output)),'sha256':sha(directory/f'{phase}-{index:02d}-{v}.json')} for v in responses}}
   return summary
  try:
   initial=pair('calibration',0,1);row['calibration']=[initial];iterations=max(1,math.ceil(1.10*200_000_000/min(initial['timings_ns_per_batch'].values())));assert iterations<=100000
   for attempt in range(1,9):
    calibrated=pair('calibration',attempt,iterations);row['calibration'].append(calibrated);save()
    fastest_block=min(calibrated['timings_ns_per_batch'].values())*iterations
    if fastest_block>=200_000_000:break
    iterations=max(iterations+1,math.ceil(iterations*1.10*200_000_000/fastest_block));assert iterations<=100000
   else:raise ValueError('Unable to calibrate both variants to >=200ms after8 attempts')
   row['iterations']=iterations;row['warmup']=[];save()
   for index in range(5):row['warmup'].append(pair('warmup',index,iterations));save()
   for index in range(41):row['blocks'].append(pair('timing',index,iterations));save()
   baseline=[r['timings_ns_per_batch']['baseline'] for r in row['blocks']];candidate=[r['timings_ns_per_batch']['candidate'] for r in row['blocks']]
   row['baseline']=kernel.summarize(baseline);row['candidate']=kernel.summarize(candidate);row['ratio']=kernel.ratio_summary(candidate,baseline,{'status':'passed'});row['ratio']['definition']='slim candidate / original6b24 paired block latency;99% bootstrap median interval;CI width<=2%'
   row['status']='measured'
  except Exception as error:
   row.update(status='failed',error=f'{type(error).__name__}: {error}');passed=False
  save();print(row['id'],row['status'],row.get('ratio',{}).get('gate'),flush=True)
finally:
 exits={}
 for variant,process in processes.items():
  process.close();exits[variant]=process.process.returncode
 state['producer_exit_codes']=exits
 try:
  verify();assert set(exits)==set(bindings) and all(type(code) is int and code==0 for code in exits.values())
  for item in executed.values():assert sha(ROOT/item['path'])==item['sha256']
  state['verified_after']=True;state['performance_provenance_qualified']=True;state['status']='completed' if passed and all(r['status']=='measured' for r in state['rows']) else 'failed'
 except Exception as error:
  state.update(status='failed',performance_provenance_qualified=False,provenance_error=f'{type(error).__name__}: {error}')
  for row in state['rows']:
   if 'ratio' in row:row['ratio']['unqualified_original_gate']=row['ratio']['gate'];row['ratio']['gate']='unqualified-provenance'
 save()
raise SystemExit(0 if state['status']=='completed' else 1)
