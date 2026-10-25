"""Portable stdlib replay of the fixed seven-family rank-seven saved record.

No compiler, native evaluator, producer comparator or process probe is invoked.
The two durable parents provide the exact 77-source selected Cargo product and
already qualified PV/reference arrays; they are not rebuilt or rebenchmarked.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
import hashlib,importlib.util,io,json,re,sys,tarfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];CHECKS=0
def require(ok,reason):
 global CHECKS
 if not ok:raise ValueError(reason)
 CHECKS+=1
def sha(body):return hashlib.sha256(body).hexdigest()
def describe(body):return {'sha256':sha(body),'bytes':len(body)}
def read(body):return json.loads(body)
def restore_files(manifest=None):
 if manifest is None:manifest=read((HERE/'manifest.json').read_bytes())
 require({str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}==set(manifest['capsule_files'])|{'manifest.json'},'closed own capsule membership')
 for name,expected in manifest['capsule_files'].items():require(describe((HERE/name).read_bytes())==expected,'capsule member '+name)
 files={}
 for number,parent in enumerate(manifest['parents']):
  path=ROOT/parent['path'];require(describe((path/'manifest.json').read_bytes())==parent['manifest'] and describe((path/'check.py').read_bytes())==parent['checker'],'fixed parent identities')
  spec=importlib.util.spec_from_file_location('ordinary_rank7_parent_'+str(number),path/'check.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);inherited=module.restore_files(read((path/'manifest.json').read_bytes()))
  for name,body in inherited.items():
   if number==1:
    # Old source files belong to the old PV product, not the new 77-source
    # context. Only inherit its retained target/reference evidence aliases.
    relative=name.removeprefix(manifest['historical_root'])
    if not relative.startswith(('target/','validation/')):continue
    name=manifest['historical_root']+relative
   require(name not in files or files[name]==body,'parent evidence alias collision '+name);files[name]=body
 own={}
 with tarfile.open(fileobj=io.BytesIO((HERE/'evidence.tar.gz').read_bytes()),mode='r:gz') as tar:
  for member in tar:
   p=Path(member.name);require(member.isfile() and not p.is_absolute() and '..' not in p.parts and member.name not in own,'safe exact archive')
   body=tar.extractfile(member).read();require(not body.startswith((b'\x7fELF',b'!<arch>')) and not re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}',body),'no compiled payload or literal license');own[member.name]=body
 require({n:describe(b) for n,b in own.items()}==manifest['evidence'],'exact own archive inventory')
 for alias,member in manifest['aliases'].items():
  body=own[member];require(alias not in files or files[alias]==body,'own inherited alias collision '+alias);files[alias]=body
 return files
def replay(files,m):
 prefix=m['historical_root']+m['private_prefix'];catalog=read(files[prefix+'/catalog.json']);fixture=read(files[catalog['fixture']]);sample=fixture['samples'][0];oracle=read(files[catalog['oracle_subset']['path']]);counts={'reference_slots':0,'precision_pairs':0,'IR_zero_slots':0,'inherited_PV_slots':0,'N5_actual_PV_diagnostic_quad_slots':0,'N5_actual_PV_diagnostic_old_PV_slots':0};maximums={k:F(0) for k in counts};witness={k:None for k in counts};summaries=[]
 require(sha(files[prefix+'/catalog.json'])==m['catalog_sha256'] and len(catalog['families'])==7 and sum(f['family_total_seconds'] for f in catalog['families'])==7560<=7800-180,'original finite seven-family catalog')
 require(sha(files[catalog['fixture']])==catalog['fixture_sha256']==oracle['fixture_sha256'] and sha(files[catalog['oracle_subset']['path']])==catalog['oracle_subset']['sha256'],'exact fixture and admitted subset')
 product=read(files[catalog['fresh_owned_artifact']['receipt']]);require(sha(files[catalog['fresh_owned_artifact']['receipt']])==catalog['fresh_owned_artifact']['receipt_sha256'] and product['status']=='passed-owned-highpoint-product' and product['product']['sha256']==catalog['fresh_owned_artifact']['sha256']==m['omitted_source_executable_sha256'],'actual selected Cargo product identity')
 require(len(product['source_files'])==77 and product['inputs_unchanged_at_product_capture'] and product['owned_process_group_absent'] and not product['live_source_lease_required_for_numerical_use'],'exact owned source context/no live lease')
 for name,digest in product['inputs'].items():
  if name==catalog['fresh_owned_artifact']['path']:require(digest==m['omitted_source_executable_sha256'],'declared omitted historical ELF identity')
  else:require(name in files and sha(files[name])==digest,'selected product historical input '+name)
 require(sha(files[catalog['lifecycle']])==catalog['lifecycle_sha256'],'longer reviewed lifecycle helper')
 original=read(files[oracle['original_provenance']['reference_validation']['path']]);n5validation=read(files[m['historical_root']+'target/quad-iregi-source-audit/future-positive-rank-requests/capture-001/validation.json'])
 for item in oracle['original_provenance'].values():require(sha(files[item['path']])==item['sha256'],'admitted oracle provenance')
 for anchor in oracle['anchors']:
  n=anchor['n'];source=next(a for a in (original if n<5 else n5validation)['cases'] if a['id']==(f'n{n}_base_mode0' if n<5 else 'quad_n5_first_five_conditioned_rank7'))
  require(source['response']==anchor['response'] and anchor['mode']==0 and anchor['native_stable'] and (source['eligible_IBP_reference_anchor'] if n<5 else source['accepted_reference']),'unchanged independent quad anchor '+str(n))
 basis=[[t,x,y,r-t-x-y] for r in range(8) for t in range(r,-1,-1) for x in range(r-t,-1,-1) for y in range(r-t-x,-1,-1)];require(len(basis)==330,'native 330-moment IREGI order')
 def compare(a,b,unit,threshold,key,where):
  ratio=sum((x-y)**2 for x,y in zip(a,b))/max(unit,sum(v*v for v in b));require(ratio<=threshold,key+' '+str(where));counts[key]+=1
  if ratio>maximums[key]:maximums[key]=ratio;witness[key]=where
 elapsed=0;native_captures=0
 for family in catalog['families']:
  h=prefix+'/families/'+family['id'];receipt=read(files[h+'/receipt.json']);elapsed+=receipt['elapsed_seconds'];require(receipt['catalog_sha256']==m['catalog_sha256'] and receipt['inputs_unchanged'] and not receipt['cleanup_errors'] and receipt['cancellation'] is None and not receipt['common_unsafe_failure'] and receipt['elapsed_seconds']<=family['family_total_seconds'],'bounded terminal family '+family['id'])
  if receipt['status']!='passed_complete_family':
   require(family['id']=='n5-rank7-ibp' and receipt['status']=='failed_or_incomplete_family' and receipt['unrun_labels']==['n5-rank7-ibp-Float256-001'] and len(receipt['cases'])==1 and 'actualIBPmustnotPVfallback' in files[h+'/reference-gate-128.log'].decode(),'preserved strict N5 actual-method failure/256UNRUN')
   require(h+'/comparison.json' not in files and h+'/reference-gate-128.json' not in files,'no invented N5 pure-IBP mathematical gate')
   c=h+'/n5-rank7-ibp-Float128-001';r=read(files[c+'/receipt.json']);d=read(files[c+'/result.json']);oldbase=m['historical_root']+'target/public-rank7-n1-n5-current-cargo/captures/n5-rank7-Float128-001';old=read(files[oldbase+'/result.json']);oldreceipt=read(files[oldbase+'/receipt.json'])
   require(r['status']=='terminal_capture' and r['inputs_unchanged'] and not r['cleanup_errors'] and r['steps'][0]['returncode']==0 and r['steps'][0]['owned_group_gone'] and sha(files[c+'/result.json'])==r['driver_ledger_sha256'] and sha(files[c+'/receipt.json'])==receipt['cases'][0]['receipt_sha256'],'N5 completed native case retained')
   require(d['algorithm_used']=='PassarinoVeltman' and d['settings']=={'propagators':5,'rank':7,'powers':[1]*5,'dimension_shift':0,'algorithm':'Ibp','convention':'IregiNative','tensor_weights':'Components','invariants':'FromShifts','input_policy':'Preserve'} and d['working_bits']==128 and d['requested_bits']==53 and d['rows']==d['components']==1 and d['status']=='all_lanes_success' and d['lane_statuses']==['Success'] and d['basis']==basis and any('zero epsilon-independent divisor' in note for note in d['preparation_notes']),'N5 PV-completion semantics retained')
   props=sample['propagators'][:5];exact=[[str(F(v)),'0'] for prop in props for v in prop['shift']]+[[str(F(v)) for v in prop['mass_squared']] for prop in props]+[[str(F(sample['mu'])),'0']];require(d['input_exact_rational']==[exact] and old['input_exact_rational'][0]==exact and oldreceipt['driver_ledger_sha256']==sha(files[oldbase+'/result.json']) and old['settings']['algorithm']=='PassarinoVeltman' and old['working_bits']==128 and old['basis']==basis and old['lane_statuses']==['Success']*3,'same qualified old PV base fixture')
   scale=max(F(1),*(abs(F(prop['mass_squared'][0])) for prop in props))
   for i,a in enumerate(props):
    for b in props[:i]:
     q=[F(x)-F(y) for x,y in zip(a['shift'],b['shift'])];scale=max(scale,abs(q[0]**2-sum(v*v for v in q[1:])))
   anchor=next(a for a in oracle['anchors'] if a['n']==5);require(len(d['lanes'][0]['moments'])==330,'complete N5 actual PV diagnostic tensor')
   for i,(alpha,moment,reference,oldmoment) in enumerate(zip(basis,d['lanes'][0]['moments'],anchor['response']['moments'],old['lanes'][0]['moments'])):
    require(len(moment)==len(reference)==len(oldmoment)==4,'four N5 diagnostic Laurent slots')
    for slot,z in enumerate(moment):
     require(set(z)=={'real','imaginary','real_precision','imaginary_precision'} and all(type(z[k]) is int and 1<=z[k]<=128 for k in ('real_precision','imaginary_precision')),'N5 represented precision metadata');a=(F(z['real']),F(z['imaginary']));unit=scale**(sum(alpha)-6);where=[family['id'],128,i,slot]
     compare(a,tuple(map(F,reference[slot])),unit,F(1,10**20),'N5_actual_PV_diagnostic_quad_slots',where);compare(a,(F(oldmoment[slot]['real']),F(oldmoment[slot]['imaginary'])),unit,F(1,2**160),'N5_actual_PV_diagnostic_old_PV_slots',where)
   diagnostic=read(files[prefix+'/n5-requested-IBP-128-actual-PV-diagnostic.json']);require(diagnostic['status']=='passed_actual_PV_completion_output_diagnostic' and diagnostic['pure_IBP_coverage_qualified'] is False and diagnostic['Float256']=='UNRUN unchanged','diagnostic does not upgrade strict actual-method coverage')
   summaries.append({'family':family['id'],'status':receipt['status'],'actual_algorithms':['PassarinoVeltman'],'unrun_labels':receipt['unrun_labels']});native_captures+=1;continue
  require(not receipt['unrun_labels'] and len(receipt['cases'])==2 and sha(files[h+'/comparison.json'])==receipt['comparison_sha256'],'complete family saved comparison binding')
  saved=read(files[h+'/comparison.json']);require(saved['status']=='passed_complete_family' and not saved['failures'] and saved['counts']=={'reference_slots':2640,'precision_pairs':1320,'IR_zero_slots':1320} and saved['comparator_sha256']==sha(files[prefix+'/compare.py']),'saved full gate exact source/counts')
  props=sample['propagators'][:family['n']];scale=max(F(1),*(abs(F(prop['mass_squared'][0])) for prop in props))
  for i,a in enumerate(props):
   for b in props[:i]:
    q=[F(x)-F(y) for x,y in zip(a['shift'],b['shift'])];scale=max(scale,abs(q[0]**2-sum(v*v for v in q[1:])))
  exact=[[str(F(v)),'0'] for prop in props for v in prop['shift']]+[[str(F(v)) for v in prop['mass_squared']] for prop in props]+[[str(F(sample['mu'])),'0']];anchor=next(a for a in oracle['anchors'] if a['n']==family['n']);parsed={};metadata=[]
  for case,record in zip(family['cases'],receipt['cases']):
   c=h+'/'+case['id'];r=read(files[c+'/receipt.json']);d=read(files[c+'/result.json']);bits=case['working_bits'];native_captures+=1
   require(sha(files[c+'/receipt.json'])==record['receipt_sha256'] and record['status']==r['status']=='terminal_capture' and r['inputs_unchanged'] and not r['cleanup_errors'] and r['cancellation'] is None and sha(files[c+'/result.json'])==r['driver_ledger_sha256'],'exact complete saved capture')
   step=r['steps'][0];require(step['status']=='exited' and step['returncode']==0 and step['owned_group_gone'] and step['elapsed_seconds']<=case['child_cap_seconds'],'historical terminal owned cleanup')
   require(d['settings']=={'propagators':family['n'],'rank':7,'powers':[1]*family['n'],'dimension_shift':0,'algorithm':'Ibp' if family['requested_algorithm']=='ibp' else 'Hybrid','convention':'IregiNative','tensor_weights':'Components','invariants':'FromShifts','input_policy':'Preserve'} and d['working_bits']==bits and d['requested_bits']==53 and d['rows']==d['components']==1 and d['status']=='all_lanes_success' and d['lane_statuses']==['Success'] and d['basis']==basis and d['input_exact_rational']==[exact],'every original exact input/settings/complete tensor')
   require(d['algorithm_used'] in (['Ibp'] if family['requested_algorithm']=='ibp' else ['Ibp','PassarinoVeltman','Hybrid']) and (family['requested_algorithm']!='ibp' or d['fallback_used']==[False]),'actual method separate from requested method')
   require(set(d['execution'])=={'input_rows','argument_rows','master_family_batches','master_rows','pentagon_box_rows','reduction_rows','fallback_rows','fallback_successes','analytic_rows'} and d['execution']['input_rows']==1 and all(type(v) is int and v>=0 for v in d['execution'].values()) and len(d['diagnostics'])==1 and len(d['fallback_used'])==len(d['analytic_used'])==1 and all(type(v) is bool for v in d['fallback_used']+d['analytic_used']),'actual counters and branch diagnostics')
   lane=d['lanes'][0];require(lane['row']==0 and lane['status']=='Success' and len(lane['moments'])==330,'complete tensor lane')
   oldbase=m['historical_root']+f'target/public-rank7-n1-n5-current-cargo/captures/n{family["n"]}-rank7-Float{bits}-001';old=read(files[oldbase+'/result.json']);oldreceipt=read(files[oldbase+'/receipt.json']);require(oldreceipt['status']=='terminal_capture' and oldreceipt['driver_ledger_sha256']==sha(files[oldbase+'/result.json']) and old['input_exact_rational'][0]==exact and old['settings']['algorithm']=='PassarinoVeltman' and old['working_bits']==bits and old['basis']==basis and old['lane_statuses']==['Success']*3,'qualified inherited PV same input')
   values=[]
   for i,(alpha,moment,reference,oldmoment) in enumerate(zip(basis,lane['moments'],anchor['response']['moments'],old['lanes'][0]['moments'])):
    require(len(moment)==len(reference)==len(oldmoment)==4,'all four Laurent slots');row=[];unit=scale**(sum(alpha)+4-2*family['n'])
    for slot,z in enumerate(moment):
     require(set(z)=={'real','imaginary','real_precision','imaginary_precision'} and all(type(z[k]) is int and 1<=z[k]<=bits for k in ('real_precision','imaginary_precision')),'finite saved component precisions');a=(F(z['real']),F(z['imaginary']));row.append(a);where=[family['id'],bits,i,slot]
     compare(a,tuple(map(F,reference[slot])),unit,F(1,10**20),'reference_slots',where)
     if slot in (1,2):compare(a,(F(0),F(0)),unit,F(1,10**20),'IR_zero_slots',where)
     compare(a,(F(oldmoment[slot]['real']),F(oldmoment[slot]['imaginary'])),unit,F(1,2**160),'inherited_PV_slots',where)
    values.append(row)
   parsed[bits]=values;metadata.append({k:d[k] for k in ['algorithm_used','preparation_notes','master_count','alias_count','execution','fallback_used','analytic_used','diagnostics']})
  require(metadata==saved['metadata'],'exact retained raw-method/counter metadata')
  for i,alpha in enumerate(basis):
   for slot in range(4):compare(parsed[128][i][slot],parsed[256][i][slot],scale**(sum(alpha)+4-2*family['n']),F(1,2**160),'precision_pairs',[family['id'],i,slot])
  summaries.append({'family':family['id'],'status':'passed_complete_family','actual_algorithms':[d['algorithm_used'] for d in metadata],'unrun_labels':[]})
 require(elapsed<7800-180 and native_captures==m['native_captures'] and counts==m['replayed_counts'],'whole finite accounting and complete available gates')
 with localcontext() as ctx:
  ctx.prec=100;display={key:str((Decimal(v.numerator)/Decimal(v.denominator)).sqrt()) for key,v in maximums.items()}
 return {'status':'passed_portable_saved_seven_family_record_with_explicit_N5_IBP_gap','families':summaries,'all_requested_method_families_qualified':False,'native_captures':native_captures,'counts':counts,'maximum_normalized_errors':display,'maximum_witnesses':witness,'historical_terminal_family_seconds':elapsed,'checks':CHECKS,'native_jobs':0,'compiler_jobs':0,'fresh_process_probes':0,'performance_qualified':False,'full_rank7_domain_qualified':False}
def main():
 m=read((HERE/'manifest.json').read_bytes());files=restore_files(m);print(json.dumps(replay(files,m)))
if __name__=='__main__':main()
