#!/usr/bin/env python3
from pathlib import Path
from decimal import Decimal,localcontext
from fractions import Fraction
import hashlib,importlib.util,json,sys
R=Path.cwd();H=R/'target/public-highpoint/thin-n6'
def sha(p):return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
p=R/'validation/public-highpoint/compare_public.py';spec=importlib.util.spec_from_file_location('shared',p);S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)
fixture_path=R/'validation/public-highpoint/fixture-conditioned_masses.json';f=json.loads(fixture_path.read_text());refpath=R/'validation/public-highpoint/reference-conditioned_masses.json';ref=json.loads(refpath.read_text());S.validate_reference(ref,f,sha(fixture_path))
exe=R/'target/reference/iregi-reference-original';assert sha(exe)==ref['executable_sha256'];historic=R/'validation/public-highpoint/qualification.json';history=json.loads(historic.read_text());assert history['artifacts'][refpath.name]==sha(refpath) and history['artifacts'][fixture_path.name]==sha(fixture_path)
exact_path=H/'exact-001/run.json';exact=json.loads(exact_path.read_text());assert exact['status']=='passed' and exact['inputs_unchanged'] and len(exact['steps'])==2 and all(step['exit_code']==0 for step in exact['steps']);assert all(sha(Path(n))==h for n,h in exact['inputs'].items());assert all(sha(H/'exact-001'/n)==h for n,h in exact['outputs'].items())
records=[];inputs={str(x):sha(x) for x in [p,fixture_path,refpath,exe,historic,exact_path,Path(__file__).resolve()]}
for bits in sys.argv[1:]:
 a=H/f'n6-rank2-{bits}-001';run=json.loads((a/'run.json').read_text());d=json.loads((a/'result.json').read_text());assert run['status']=='passed' and run['inputs_unchanged'];assert all(sha(Path(n))==v for n,v in run['inputs'].items());assert all(sha(a/n)==v for n,v in run['outputs'].items())
 expected_command=['taskset','-c','14',str(H/'build-002/driver'),str(fixture_path),'6','2','pv',bits,'53','1',str(a/'result.json')];assert len(run['steps'])==1 and run['steps'][0]['command']==expected_command and run['steps'][0]['exit_code']==0 and d['fixture']==str(fixture_path)
 assert d['status']=='all_lanes_success' and d['lane_statuses']==['Success'] and d['rows']==1 and d['components']==1
 assert d['settings']==dict(propagators=6,rank=2,powers=[1]*6,dimension_shift=0,algorithm='PassarinoVeltman',convention='IregiNative',tensor_weights='Components',invariants='FromShifts',input_policy='Preserve')
 assert d['basis']==S.canonical_basis(2) and len(d['lanes'])==1 and len(d['lanes'][0]['moments'])==15
 sample=f['samples'][0];ps=sample['propagators'][:6];expected=[[str(Fraction(v)),'0'] for p in ps for v in p['shift']]+[[str(Fraction(v)) for v in p['mass_squared']] for p in ps]+[[str(Fraction(sample['mu'])),'0']]
 assert d['input_exact_rational']==[expected] and d['requested_bits']==53 and d['working_bits']==int(bits)
 assert d['execution']['child_batch_calls']==1 and d['execution']['packed_child_rows']==6 and d['execution']['parent_batch_calls']==1 and d['execution']['packed_parent_rows']==1
 cases=[x for x in ref['cases'] if x['id']==f'n6_{sample["id"]}_mode0'];assert len(cases)==1 and cases[0]['response']['stable'] is True
 errors=[];failures=[];slots=0;zeros=0
 with localcontext() as ctx:
  ctx.prec=170;q=S.scale(sample,6)
  for i,monomial in enumerate(d['basis']):
   normalization=q**(sum(monomial)-8);moment=d['lanes'][0]['moments'][i];assert len(moment)==4
   for pole,slot in enumerate(moment):
    assert set(slot)=={'real','imaginary','real_precision','imaginary_precision'}
    value=tuple(S.decimal_rational(slot[k])/normalization for k in ['real','imaginary']);old=tuple(Decimal(str(x))/normalization for x in cases[0]['response']['moments'][i][pole])
    error=S.norm(tuple(a-b for a,b in zip(value,old)))/max(Decimal(1),S.norm(old));errors.append(error);slots+=1
    if pole<3:assert all(x==0 for x in value);zeros+=1
    if error>Decimal('1e-10'):failures.append(dict(moment=i,pole=pole,error=str(error)))
 assert not failures,failures
 records.append(dict(working_bits=int(bits),slots=slots,exact_zero_poles=zeros,maximum_original_error=str(max(errors)),result=d))
 inputs.update({str(a/n):sha(a/n) for n in ['run.json','result.json','step-0.log']})
convergence=None
if len(records)==2:
 assert [x['working_bits'] for x in records]==[128,256]
 errors=[]
 with localcontext() as ctx:
  ctx.prec=170;q=S.scale(f['samples'][0],6)
  for i,monomial in enumerate(records[0]['result']['basis']):
   natural=q**(sum(monomial)-8)
   for pole in range(4):
    values=[tuple(S.decimal_rational(r['result']['lanes'][0]['moments'][i][pole][k])/natural for k in ['real','imaginary']) for r in records]
    errors.append(S.norm(tuple(a-b for a,b in zip(*values)))/max(Decimal(1),S.norm(values[1])))
  assert max(errors)<=Decimal(2)**-80
  convergence=str(max(errors))
for r in records:del r['result']
out=H/('comparison-'+ '-'.join(sys.argv[1:])+'.json');assert not out.exists();out.write_text(json.dumps(dict(status='passed',records=records,normalized_tolerance='1e-10',convergence_tolerance='2^-80' if convergence else None,maximum_precision_difference=convergence,input_sha256=inputs,scope='Private thin N6 rank2 retained base fixture only; complete native raw 60 complex Laurent slots; no rank7/N7/general-domain or performance claim.'),indent=2)+'\n');print(out.read_text())
