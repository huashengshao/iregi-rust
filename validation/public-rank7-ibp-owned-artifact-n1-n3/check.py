#!/usr/bin/env python3
"""Portable saved replay of an INCOMPLETE IBP corpus; standard library only.

A successful integrity replay never upgrades either historical timeout/cleanup
failure or qualifies the requested complete corpus. No native/PID probe occurs.
"""
from decimal import Decimal,localcontext
from fractions import Fraction
import argparse,hashlib,importlib.util,json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIVATE="target/public-rank7-n1-n3-ibp-owned-cargo"
PV="target/public-rank7-n1-n5-current-cargo"
HISTORICAL_ROOT="/shared/external/iregi/iregi-rust/"

def require(ok,why):
 if not ok:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def desc(body):return {"sha256":sha(body),"bytes":len(body)}
def load(body):return json.loads(body)
def restore(manifest):
 require({str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}==set(manifest['capsule_files'])|{'manifest.json'},'closed incomplete-corpus inventory')
 for name,expected in manifest['capsule_files'].items():require(desc((HERE/name).read_bytes())==expected,'capsule '+name)
 parent=ROOT/manifest['parent']['path']
 require(desc((parent/'manifest.json').read_bytes())==manifest['parent']['manifest'] and desc((parent/'check.py').read_bytes())==manifest['parent']['checker'],'exact successful PV source parent')
 spec=importlib.util.spec_from_file_location('owned_IBP_PV_source_parent',parent/'check.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 files=module.restore_files(load((parent/'manifest.json').read_bytes()))
 files[str((parent/'manifest.json').relative_to(ROOT))]=(parent/'manifest.json').read_bytes()
 payload=module.unpack((HERE/'evidence.tar.gz').read_bytes(),manifest['evidence_members'])
 for name,body in payload.items():
  require(name not in files or files[name]==body,'unique preserved aliases');files[name]=body
 protocol=load(files[PRIVATE+'/protocol.json'])
 for absolute,expected in protocol['bindings'].items():
  if absolute.startswith(HISTORICAL_ROOT):
   name=absolute[len(HISTORICAL_ROOT):]
   if name==protocol['binary'][len(HISTORICAL_ROOT):]:require(expected==protocol['binary_sha256'],'omitted old frozen artifact identity')
   else:require(name in files and sha(files[name])==expected,'snapshot/helper/input/reference binding '+name)
  else:require(manifest['omitted_immutable_tool_bindings'].get(absolute)==expected,'declared immutable tool')
 require(not any(HISTORICAL_ROOT+name in protocol['bindings'] for name in protocol['source_names']),
         'no new live-main lease/source claim')
 return files,module

def restore_files(manifest):
 return restore(manifest)[0]

def replay(files,parent):
 protocol=load(files[PRIVATE+'/protocol.json']);fixture=load(files['validation/public-highpoint/fixture-conditioned_masses.json']);samples=fixture['samples']
 basis=[[t,x,y,r-t-x-y] for r in range(8) for t in range(r,-1,-1) for x in range(r-t,-1,-1) for y in range(r-t-x,-1,-1)]
 require(len(protocol['cases'])==6 and len(samples)==3 and len(basis)==330,'exact six-case family')
 reference_prefix='target/quad-iregi-source-audit/rank7-n1-n5-corpus'
 reference=load(files[reference_prefix+'/capture-001/validation.json']);anchors={}
 for case in reference['cases']:
  if case['eligible_IBP_reference_anchor'] and case['propagators'] in (1,3):
   r=case['response'];require(case['mode']==0 and r['stable'] is True and len(r['moments'])==330,'independent IBP anchor')
   anchors[case['propagators'],case['sample']]=[[tuple(Fraction(v) for v in z) for z in m] for m in r['moments']]
 counts={'complete_cases':0,'failed_cases':0,'successful_lanes':0,'reference_slots':0,'precision_slots':0,'scaling_slots':0,'mode_pair_slots':0,'IR_exact_zero_slots':0,'UV_convergent_exact_zero_slots':0}
 maxima={k:Fraction(0) for k in ('reference','precision','scaling','mode_pair')};parsed={};failed={}
 for case in protocol['cases']:
  n,bits=case['n'],case['bits'];prefix=PRIVATE+'/captures/'+case['id'];r=load(files[prefix+'/receipt.json']);d=load(files[prefix+'/result.json']);step=r['steps'][0]
  require(r['case']==case and r['inputs_unchanged'] is True and len(r['steps'])==1 and r['elapsed_seconds']<=case['total_seconds'],'sealed case/source/budget')
  require(r['driver_ledger_sha256']==sha(files[prefix+'/result.json']),'preserved partial/full driver ledger')
  require(d['working_bits']==bits and d['requested_bits']==53 and d['rows']==3 and d['components']==1 and d['basis']==basis and d['algorithm_used']=='Ibp','typed method/input metadata')
  expected_settings={'propagators':n,'rank':7,'powers':[1]*n,'dimension_shift':0,'algorithm':'Ibp','convention':'IregiNative','tensor_weights':'Components','invariants':'FromShifts','input_policy':'Preserve'}
  require(d['settings']==expected_settings,'ordinary IBP requested settings')
  for row,sample in enumerate(samples):
   expected=[[str(Fraction(v)),'0'] for p in sample['propagators'][:n] for v in p['shift']]
   expected += [[str(Fraction(v)) for v in p['mass_squared']] for p in sample['propagators'][:n]]
   expected += [[str(Fraction(sample['mu'])),'0']]
   require(d['input_exact_rational'][row]==expected,'exact represented sample')
  if n==2:
   require(r['status']=='failed_or_incomplete' and d['status']=='preparing_workspace' and 'lanes' not in d
           and step.get('timeout') is True and step['timeout_seconds']==255 and step['returncode'] is None and step['owned_group_gone'] is False,
           'historical N2 timeout and missing arrays must remain failed')
   require(r['cleanup_errors']==['owned process leader did not exit after SIGKILL','owned descendant process group remains after cleanup'],
           'historical failed cleanup must not be erased')
   failed[bits]={'receipt_sha256':sha(files[prefix+'/receipt.json']),'group':step['owned_process_group']};counts['failed_cases']+=1
   continue
  require(n in (1,3) and r['status']=='terminal_capture' and d['status']=='all_lanes_success' and not r['cleanup_errors']
          and r['cancellation'] is None and step['returncode']==0 and step['owned_group_gone'] is True,'successful subset capture')
  require(d['lane_statuses']==['Success']*3 and d['fallback_used']==d['analytic_used']==[False]*3 and len(d['diagnostics'])==3,'ordinary successful branch metadata')
  leaves={1:1,3:7}[n]
  require(d['master_count']==leaves and d['execution']=={'input_rows':3,'argument_rows':3,'reduction_rows':3,'master_rows':3*leaves,'master_family_batches':n,'pentagon_box_rows':0,'fallback_rows':0,'fallback_successes':0,'analytic_rows':0},'actual instruction-major counters')
  pv=load(files[PV+'/captures/'+case['id']+'/result.json'])
  require(pv['input_exact_rational']==d['input_exact_rational'] and pv['basis']==basis and pv['working_bits']==bits,'same saved PV implementation inputs')
  rows=[]
  for row,sample in enumerate(samples):
   lane=d['lanes'][row];require(lane['status']=='Success' and lane['row']==row and len(lane['moments'])==330,'complete tensor lane');tensor=[]
   for index,alpha in enumerate(basis):
    moment=lane['moments'][index];require(len(moment)==4,'complete Laurent moment');unit2=parent.scale2(sample,n)**(sum(alpha)+4-2*n);values=[]
    for slot,z in enumerate(moment):
     require(all(type(z[k]) is int and 0<z[k]<=bits for k in ('real_precision','imaginary_precision')),'stored component precision')
     pair=Fraction(z['real']),Fraction(z['imaginary']);values.append(pair)
     maxima['reference']=max(maxima['reference'],parent.compare(pair,anchors[n,sample['id']][index][slot],unit2,Fraction(1,10**20)));counts['reference_slots']+=1
     other=pv['lanes'][row]['moments'][index][slot];pvpair=Fraction(other['real']),Fraction(other['imaginary'])
     maxima['mode_pair']=max(maxima['mode_pair'],parent.compare(pair,pvpair,unit2,Fraction(1,2**160)));counts['mode_pair_slots']+=1
     if slot in (1,2):require(pair==(0,0),'exact IR-zero identity');counts['IR_exact_zero_slots']+=1
     if slot==0 and 4+sum(alpha)-2*n<0:require(pair==(0,0),'exact convergent UV-zero identity');counts['UV_convergent_exact_zero_slots']+=1
    tensor.append(values)
   rows.append(tensor)
  parsed[n,bits]=rows;counts['complete_cases']+=1;counts['successful_lanes']+=3
 for n in (1,3):
  for row,sample in enumerate(samples):
   for index,alpha in enumerate(basis):
    unit2=parent.scale2(sample,n)**(sum(alpha)+4-2*n)
    for slot in range(4):
     maxima['precision']=max(maxima['precision'],parent.compare(parsed[n,128][row][index][slot],parsed[n,256][row][index][slot],unit2,Fraction(1,2**160)));counts['precision_slots']+=1
  for bits in (128,256):
   for index,alpha in enumerate(basis):
    factor=Fraction(2)**(sum(alpha)+4-2*n);unit2=parent.scale2(samples[1],n)**(sum(alpha)+4-2*n)
    for slot in range(4):
     value=tuple(x*factor for x in parsed[n,bits][0][index][slot]);maxima['scaling']=max(maxima['scaling'],parent.compare(parsed[n,bits][1][index][slot],value,unit2,Fraction(1,2**160)));counts['scaling_slots']+=1
 later=load(files[PRIVATE+'/post-timeout-owned-group-observation.json'])
 require(later['status']=='later_owned_groups_observed_absent' and later['historical_failed_captures_reclassified'] is False
         and later['native_retry_or_termination_signal_sent'] is False,'later observation cannot repair historical failure')
 for row in later['groups']:
  old=failed[row['bits']];require(row['historical_receipt_sha256']==old['receipt_sha256'] and row['owned_process_group']==old['group']
       and row['historical_owned_group_gone'] is False and row['historical_returncode'] is None
       and row['group_exists_at_later_observation'] is False and row['leader_proc_exists_at_later_observation'] is False,
       'exact later-absence context retained')
 primary=load(files[PRIVATE+'/comparison.json']);require(primary['status']=='failed_or_incomplete_restricted_corpus' and primary['complete_cases']==4 and len(primary['failures'])==2,'whole-corpus primary failure retained')
 require(counts=={'complete_cases':4,'failed_cases':2,'successful_lanes':12,'reference_slots':15840,'precision_slots':7920,'scaling_slots':5280,'mode_pair_slots':15840,'IR_exact_zero_slots':7920,'UV_convergent_exact_zero_slots':30},'complete incomplete-corpus replay counts')
 with localcontext() as c:
  c.prec=100;display={k:str((Decimal(q.numerator)/Decimal(q.denominator)).sqrt()) for k,q in maxima.items()}
 return {'status':'passed_saved_integrity_and_available_values_with_preserved_INCOMPLETE_IBP_corpus','full_requested_IBP_corpus_qualified':False,
         'counts':counts,'maximum_normalized_complex_errors':display,'historical_N2_cleanup_failures_preserved':True,
         'later_absence_does_not_prove_historical_cleanup_or_no_overlap':True,'new_native_or_process_probe':False,
         'later_main_source_or_full_rank7_domain_or_performance_qualified':False}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reconstruct',type=Path);args=parser.parse_args()
 manifest=load((HERE/'manifest.json').read_bytes());files,parent=restore(manifest);result=replay(files,parent)
 if args.reconstruct is not None:
  require(not args.reconstruct.exists(),'preserve reconstruction output')
  for name,body in files.items():
   parent.safe(name);path=args.reconstruct/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
 print(json.dumps({'capsule_manifest_sha256':sha((HERE/'manifest.json').read_bytes()),'restored_files':len(files),'replay':result},indent=2))
if __name__=='__main__':main()
