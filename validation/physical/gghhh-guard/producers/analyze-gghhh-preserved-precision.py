from pathlib import Path
from decimal import Decimal, localcontext
import hashlib,json
root=Path.cwd();base=root/'target/physical-gghhh-guard'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records={bits:load(base/f'float{bits}-from-binary64/response.json') for bits in [128,256,512]}
assert records[128]['status']=='error' and 'pv_node_852' in records[128]['error']
a,b=(records[bits]['output'] for bits in [256,512])
assert records[256]['status']==records[512]['status']=='prepared'
for bits,out in [(256,a),(512,b)]:
 assert out['precision_bits']==bits and out['precision_control']['accuracy_bits']==53
 assert out['settings']['input_policy']=='Preserve' and out['settings']['algorithm']=='Hybrid'
 assert out['settings']['rank']==4 and out['settings']['propagators']==5
 assert out['poles']==['uv1','ir1','ir2','finite']
 assert len(out['samples'])==1 and out['samples'][0]['status']=='success'
 assert len(out['basis'])==len(out['samples'][0]['moments'])==70
 assert all(len(m)==4 and all(len(s)==2 for s in m) for m in out['samples'][0]['moments'])
 assert len(out['samples'][0]['integral'])==4
assert a['basis']==b['basis']
requests=[load(base/f'float{bits}-from-binary64/request.json')['configuration'] for bits in [256,512]]
for k in ['model','dot','component','input','algorithm','accuracy_bits']:assert requests[0][k]==requests[1][k]
def finitepair(pair):
 assert all(isinstance(x,str) for x in pair)
 pair=list(map(Decimal,pair));assert all(x.is_finite() for x in pair);return pair
def magnitude(pair):return sum(x*x for x in pair).sqrt()
with localcontext() as ctx:
 ctx.prec=200
 maxerror=Decimal(0);worst=None;count=0
 for i,(ma,mb) in enumerate(zip(a['samples'][0]['moments'],b['samples'][0]['moments'],strict=True)):
  dimension=4+sum(a['basis'][i])-10;scale=Decimal(750)**dimension
  for slot,(pa,pb) in enumerate(zip(ma,mb,strict=True)):
   va,vb=map(finitepair,[pa,pb]);error=magnitude([x-y for x,y in zip(va,vb)])/max(scale,magnitude(vb));count+=1
   if error>maxerror:maxerror=error;worst=dict(moment=i,exponents=a['basis'][i],slot=slot,output256=pa,output512=pb)
 ga,gb=a['samples'][0]['integral'],b['samples'][0]['integral'];gerrors=[]
 for pa,pb in zip(ga,gb,strict=True):
  va,vb=map(finitepair,[pa,pb]);gerrors.append(magnitude([x-y for x,y in zip(va,vb)])/max(Decimal(750)**-1,magnitude(vb)))
 result=dict(schema_version=1,status='passed',method='Decimal200 numerical comparison of preserved textual outputs; no binary64 conversion in convergence',working_bits=[256,512],accuracy_bits=53,input_policy='Preserve',same_exact_binary64_input_components=True,complex_tensor_slots_checked=count,native_graph_slots_checked=4,normalization='complex absolute difference / max(Q^dimension,abs(higher precision reference)),Q=750',tolerance='1e-10',max_normalized_tensor_difference=str(maxerror),worst=worst,normalized_graph_differences=list(map(str,gerrors)),full_tensor_convergence_passed=maxerror<=Decimal('1e-10'),graph_convergence_passed=max(gerrors)<=Decimal('1e-10'))
 assert count==280 and result['full_tensor_convergence_passed'] and result['graph_convergence_passed']
 result['response_sha256']={str(bits):sha(base/f'float{bits}-from-binary64/response.json') for bits in [128,256,512]}
 result['external_comparison']={str(bits):load(base/f'float{bits}-from-binary64/comparison.json') for bits in [256,512]}
 assert all(x['passed'] for x in result['external_comparison'].values())
 (base/'convergence.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['external_comparison','worst']},indent=2))
