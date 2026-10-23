"""Recheck retained protocol, every response, and bootstrap statistics; no engine run."""
from pathlib import Path
from copy import deepcopy
import hashlib,importlib.util,json,math
root=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads((root/p).read_text())
files=read('files.json');actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name!='files.json' and '__pycache__' not in p.parts};assert actual==set(files)
for p,digest in files.items():assert sha(root/p)==digest,p
load=lambda name,p:importlib.util.spec_from_file_location(name,root/p)
spec=load('retained_statistics','frozen_statistics.py');statistics=importlib.util.module_from_spec(spec);spec.loader.exec_module(statistics)
spec=load('retained_witness','witness_inputs.py');witness=importlib.util.module_from_spec(spec);spec.loader.exec_module(witness)
q=read('qualification.json');raw=read('raw/qualification.json');reg=read('kernel-long-registration.json');completion=read('completion.json');catalog=read('raw/input-catalog.json');packets={p['id']:p for p in catalog['kernel']}
assert raw['status']=='completed' and raw['verified_before'] and raw['verified_after'] and raw['performance_provenance_qualified']
assert set(raw['producer_exit_codes'])=={'baseline','candidate'} and all(type(c) is int and c==0 for c in raw['producer_exit_codes'].values())
assert q['raw_qualification_sha256']==sha(root/'raw/qualification.json')==completion['cohorts']['real_ball_long']['raw_sha256']
assert q['registration_sha256']==sha(root/'kernel-long-registration.json')==raw['preregistration']['sha256']
assert q['runner_sha256']==reg['source_sha256']==sha(root/'run_kernel_timing_long.py')
assert q['window_sha256']==sha(root/'window.json')==completion['immutable_manifests_sha256']['window.json'];assert q['completion_sha256']==sha(root/'completion.json')
assert q['production_adoption'] is False and q['all_families_passed'] is False
assert raw['builds']==reg['builds']==q['builds'];assert raw['input_catalog_sha256']==reg['input_catalog_sha256']==sha(root/'raw/input-catalog.json')
assert raw['cpu_affinity']==[254] and raw['protocol']['blocks']==41 and raw['protocol']['warmup_blocks']==5 and raw['protocol']['minimum_target_block_ms']==200
assert [r['id'] for r in raw['rows']]==reg['protocol']['case_ids']
assert [r['ratio']['gate'] for r in raw['rows']]==['improvement','inconclusive-noise','regression','regression']
count=slots=0
for row,summary in zip(raw['rows'],q['rows'],strict=True):
 assert row['status']=='measured' and len(row['blocks'])==41 and len(row['warmup'])==5
 last=row['calibration'][-1];assert min(last['timings_ns_per_batch'].values())*last['iterations']>=200_000_000
 for block in row['calibration']+row['warmup']+row['blocks']:
  packet=deepcopy(packets[row['id']]);request=packet['request'];identifier=f'{row["id"]}:{block["phase"]}:{block["index"]}'
  request.update(id=identifier,profile=False,iterations=block['iterations'],warmup=5 if block['phase']=='calibration' else 0,repeats=1)
  packet.update(id=identifier,request_sha256=witness.json_sha256(request));assert packet['request_sha256']==block['request_sha256']
  responses={}
  for variant,record in block['responses'].items():
   path=root/'raw'/record['path'];assert sha(path)==record['sha256'];responses[variant]=json.loads(path.read_text())
   assert len(responses[variant]['total_ns'])==1 and responses[variant]['total_ns'][0]==block['timings_ns_per_batch'][variant]
  check=witness.compare_kernel(packet,responses['baseline'],responses['candidate']);assert check['passed'],check['errors'];assert check['complex_slots_checked']==block['full_output_slots_checked'];count+=1;slots+=check['complex_slots_checked']
  assert block['order']==(['baseline','candidate'] if block['index']%2==0 else ['candidate','baseline'])
 a=[b['timings_ns_per_batch']['baseline'] for b in row['blocks']];b=[b['timings_ns_per_batch']['candidate'] for b in row['blocks']]
 assert statistics.summarize(a)==row['baseline'];assert statistics.summarize(b)==row['candidate']
 ratio=statistics.ratio_summary(b,a,{'status':'passed'})
 assert {k:v for k,v in ratio.items() if k!='definition'}=={k:v for k,v in row['ratio'].items() if k!='definition'}
 assert summary['paired_ratio_median']==ratio['median'] and summary['ci99']==ratio['ci99'] and summary['gate']==ratio['gate']
assert count==q['full_output_validation']['paired_responses']==192;assert slots==q['full_output_validation']['complex_laurent_slots_compared']==190080
print(json.dumps({'status':'passed','files_verified':len(files),'paired_responses_rechecked':count,'raw_responses_rechecked':count*2,'complex_laurent_slots_rechecked':slots,'gates':[r['ratio']['gate'] for r in raw['rows']]},indent=2))
