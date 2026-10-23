from pathlib import Path
import argparse,copy,hashlib,json,math,os,sys,time,datetime
root=Path.cwd();sys.path.insert(0,str(root/'validation/benchmark'))
import physical_joint as joint
p=argparse.ArgumentParser();p.add_argument('--bits',type=int,required=True);p.add_argument('--timeout',type=float,default=240);a=p.parse_args()
folder=root/f'target/physical-gghhh-guard/float{a.bits}-from-binary64'
folder.mkdir(parents=True,exist_ok=False)
source=root/'target/benchmark/physical-joint/80949db-quiet-physical-002/gghhh/rust-inputs.json'
configuration=copy.deepcopy(joint.load(source)[0]['configuration'])
conversions=[]
def exact(value,path):
 if isinstance(value,list):return [exact(x,path+[i]) for i,x in enumerate(value)]
 if isinstance(value,dict):return {k:exact(v,path+[k]) for k,v in value.items()}
 assert isinstance(value,str),(path,value)
 f=float(value)
 assert math.isfinite(f)
 if f==0.:out='-0' if math.copysign(1,f)<0 else '0'
 else:
  n,d=f.as_integer_ratio();out=str(n) if d==1 else f'{n}/{d}'
 conversions.append({'path':path,'original':value,'exact_binary64':out})
 return out
sample=configuration['input']['samples'][0]
sample['mu']=exact(sample['mu'],['mu']);sample['parameters']=exact(sample['parameters'],['parameters'])
for i,prop in enumerate(sample['propagators']):
 for key in ['mass_squared','shift']:prop[key]=exact(prop[key],['propagators',i,key])
configuration.update(id=f'gghhh-exact-f64-float{a.bits}-accuracy53',precision='float',bits=a.bits,accuracy_bits=53)
request={'op':'prepare','configuration':configuration}
(folder/'request.json').write_text(json.dumps(request,indent=2)+'\n');(folder/'input-conversions.json').write_text(json.dumps(conversions,indent=2)+'\n')
binary=root/'target/benchmark/workspace-builds/80949db-default-resume/bin/physical_benchmark'
meta=dict(status='running',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bits=a.bits,accuracy_bits=53,input_semantics='Every sample numeric component is the exact rational representation of the original binary64 parsed value, including signed zero; fixed model/DOT snapshot unchanged',binary=joint.record_file(binary),frozen_inputs=joint.record_file(source),request=joint.record_file(folder/'request.json'),cpu_affinity=sorted(os.sched_getaffinity(0)),timeout_seconds=a.timeout,producer=joint.record_file(Path(__file__)))
write=lambda:(folder/'run.json').write_text(json.dumps(meta,indent=2)+'\n')
write();engine=None;begin=time.monotonic();print('begin',a.bits,flush=True)
try:
 engine=joint.kernel.Process(binary,'physical',folder,a.timeout)
 result=engine.request(json.dumps(request)+'\n')
 (folder/'response.json').write_text(json.dumps(result,indent=2)+'\n')
 meta.update(status=result.get('status'),response=joint.record_file(folder/'response.json'))
 print('response',result.get('status'),result.get('error'),flush=True)
 if result.get('status')=='prepared':
  refs=joint.load(root/'target/benchmark/physical-joint/80949db-quiet-physical-002/gghhh/gghhh-f64-hybrid-batch1/reference-records.json')
  reference=joint.load(root/'target/benchmark/physical-joint/80949db-quiet-physical-002/gghhh/madloop.json')
  compare_configuration=copy.deepcopy(configuration)
  compare_configuration['input']=joint.load(source)[0]['configuration']['input']
  tensors=joint.rust.check(result['output'],compare_configuration,'gghhh',refs)
  fixture=joint.alignment.preserved_fixture('gghhh',reference)
  graph=joint.rust.physical.compare_physical(result['output'],compare_configuration['input']['samples'][0],fixture,joint.rust.physical.CASES['gghhh'],1e-10)
  checked=dict(canonical_tensors=tensors,preserved_graph=graph,passed=tensors['passed'] and graph['passed'],normalization_input_note='Original decimal strings are used only for binary64 reference normalization; engine receives exact binary64 rational components.')
  (folder/'comparison.json').write_text(json.dumps(checked,indent=2)+'\n')
  meta['comparison']=joint.record_file(folder/'comparison.json')
except Exception as e:
 meta.update(status='failed',error=f'{type(e).__name__}: {e}');print(meta['error'],flush=True)
finally:
 if engine is not None:engine.close()
 meta.update(wall_seconds=time.monotonic()-begin,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());write()
 print('finished',meta['wall_seconds'],flush=True)
