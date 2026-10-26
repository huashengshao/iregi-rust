"""Parametric final saved-only checker. No actual manifest means no execution."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
# Only the two explicit packet layouts are supported; never search live target.
if HERE.name=='assembled'and HERE.parent.name=='e6-dual-full-rank6-mass-second-extension'and HERE.parent.parent.name=='target':
 ROOT=HERE.parents[2]
else:
 ROOT=HERE.parents[1]
PREFIX='/shared/external/iregi/iregi-rust/'
PARENT='validation/e6-dual-rank6-precision-boundary'
PARENT_SHA='cd656689a9c02dd92c401a0ad9009be7e7f7e655d1f62d337b44fd66555777fa'
PRODUCT='749b2ae3489eb0096267421b120fa3586f2243c7eaf78fc9c02b0f9f30895906'
BUILD='b0695760d975d4c0f789400699861f3b4581f7fae5677d682748f2cf0e075da2'
def need(v,m):
 if not v:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'sha256':sha(b),'bytes':len(b)}
def safe(a):
 need(type(a)is str and bool(a)and '\0'not in a,'string alias')
 p=PurePosixPath(a);need(str(p)==a and not p.is_absolute()and '..'not in p.parts,'safe canonical relative saved alias')
def load(b):
 def pairs(items):
  out={}
  for k,v in items:need(k not in out,'duplicate JSON key');out[k]=v
  return out
 return json.loads(b,object_pairs_hook=pairs)
def admitted(m):
 need(m.get('status')=='final_complete384_and_strict256384_saved_witness','actual final witness manifest required')
 for key in ('actual384','qualifying256384_pair','independent256384'):
  need(type(m.get(key))is dict and m[key].get('accepted_by_owner_and_root')is True,'actual accepted terminal independent gate: '+key)
def restore_files(m):
 admitted(m)
 for n,row in m['capsule_files'].items():safe(n);need(desc((HERE/n).read_bytes())==row,'actual final capsule source/payload')
 for a,row in m['parent_files'].items():safe(a);need(desc((ROOT/a).read_bytes())==row,'exact once-owned boundary parent closure')
 pb=(ROOT/PARENT/'manifest.json').read_bytes();need(sha(pb)==m['parent_manifest_sha256']==PARENT_SHA,'immutable published boundary parent')
 parent=runpy.run_path(str(ROOT/PARENT/'check.py'),run_name='final_saved_parent_loader')
 inherited=parent['restore_files'](load(pb))
 reader=runpy.run_path(str(ROOT/'validation/e6-dual-postfix-resource-boundaries/check.py'),run_name='final_safe_archive_reader')
 safe(m['payload_file']);own=reader['unpack']((HERE/m['payload_file']).read_bytes(),m['payload_members'],complete=True)
 files=dict(inherited)
 for a,row in m['aliases'].items():
  safe(a)
  if 'parent_alias'in row:safe(row['parent_alias']);b=inherited[row['parent_alias']]
  elif 'parent_file'in row:
   safe(row['parent_file']);need(row['parent_file']in m['parent_files'],'pinned physical parent selector');b=(ROOT/row['parent_file']).read_bytes()
  else:b=own[row['member']]
  need(desc(b)=={k:row[k]for k in('sha256','bytes')},'exact actual saved body')
  need(a not in files or files[a]==b,'global inherited canonical source aliases stay historical')
  files[a]=b
 return files

def replay(m,files):
 admitted(m)
 def read(a):return load(files[a])
 h=read(m['owner_handoff_alias'])
 need(sha(files[m['owner_handoff_alias']])==m['owner_handoff_sha256']
  and h['status']=='accepted_terminal384_and_strict256384_for_final_capsule'
  and h['collection_authorized_by_root']is True,'actual root/owner accepted handoff bytes')
 for key in ('actual384','qualifying256384_pair','independent256384'):need(h[key]==m[key],'exact admitted external role descriptors')
 need(sha(files[m['owner_inventory_alias']])==m['owner_inventory_sha256']==h['owner_inventory']['sha256'],
  'actual immutable owner384 inventory')
 inventory=read(m['owner_inventory_alias'])
 for a,row in inventory['files'].items():safe(a);need(desc(files[a])==row,'every actual owner-frozen body')
 need(m['root_terminal_review']==h['root_terminal_review'],'actual root terminal review descriptor')
 rr=m['root_terminal_review'];safe(rr['alias']);need(sha(files[rr['alias']])==rr['sha256'],'exact accepted root terminal review')
 build_alias=m['actual_current_build_receipt_alias'];build=read(build_alias)
 need(sha(files[build_alias])==BUILD and len(build['sources'])==len(m['current_source_aliases'])==210,'actual same b069source210 build')
 for canonical,digest in build['sources'].items():
  a=m['current_source_aliases'][canonical];safe(a);need(sha(files[a])==digest,'actual coherent saved current source body')
 higher=m['actual384'];receipt=read(higher['receipt_alias']);protocol=read(higher['protocol_alias'])
 need(receipt['status']=='completed_explicit_PV_capture_pending_saved_mechanism_gate_and_independent_oracle'
  and receipt['working_bits']==384 and receipt['requested_bits']==53
  and receipt['inputs_unchanged']is True and receipt['cleanup_errors']==[]and receipt['cancellation']is None
  and len(receipt['steps'])==1 and receipt['steps'][0]['status']=='exited'
  and receipt['steps'][0]['returncode']==0 and receipt['steps'][0]['owned_group_gone']is True,'actual clean full384 terminal lifecycle')
 need(len(receipt['inputs'])==higher['expected_input_bindings'],'actual reviewed guard inventory count')
 need(protocol['working_bits']==384 and protocol['requested_bits']==53
  and protocol['source_context']['count']==210 and protocol['source_context']['build_receipt_sha256']==BUILD
  and protocol['binary']['sha256']==PRODUCT==build['products']['tests']['sha256'],'sameactualsource/product/precisionprotocol')
 for absolute,digest in protocol['bindings'].items():need(receipt['inputs'].get(absolute)==digest,'all released protocol bindings survive actualterminal')
 for canonical,digest in build['sources'].items():need(receipt['inputs'].get(PREFIX+m['current_source_aliases'][canonical])==digest,'all210actualbuildsnapshotguards observed by nativeproducer')
 checked=outputs=omitted=0
 for absolute,digest in receipt['inputs'].items():
  if absolute in m['omitted_native_artifacts']:need(m['omitted_native_artifacts'][absolute]==digest,'historical native guard identity only');omitted+=1;continue
  need(absolute.startswith(PREFIX),'saved project-local input')
  a=absolute[len(PREFIX):];a=m['current_source_aliases'].get(a,a);safe(a)
  need(sha(files[a])==digest,'actual terminal nonbinary input bytes');checked+=1
 base=higher['receipt_alias'].rsplit('/',1)[0]
 for n,digest in receipt['outputs'].items():
  a=base+'/'+n;safe(a)
  if PREFIX+a in m['omitted_native_artifacts']:need(m['omitted_native_artifacts'][PREFIX+a]==digest,'recorded outputnativeSHA only')
  else:need(sha(files[a])==digest,'actual terminal nonbinary output bytes');outputs+=1
 need(receipt['outputs']['capture.json']==sha(files[higher['capture_alias']])
  and receipt['outputs']['frozen-tests']==PRODUCT,'actual output capture/product binding')
 old=read(m['preserved_failed128256']['report_alias'])
 need(sha(files[m['preserved_failed128256']['report_alias']])=='2472628367171ba81589e18c949a3e2681489d76d2395693a7c23610b1be0b7a'
  and old['all_parent_numeric_gates_passed']is False and old['comparisons'][5]['failures']==628,
  'original failed128256 comparison retained byte-exact without relabelling')
 need(m['counts']['historical_failed_native_captures']==10
  and m['qualification']['full_objective_met']is False
  and m['qualification']['default_Hybrid_qualified']is False,'fixed witness scope leaves overall goal and other methods to root')
 program=runpy.run_path(str(HERE/'saved_math.py'),run_name='final_saved_only_adapters')
 result=program['replay_final_math'](m,files)
 result.update(actual_source_files_verified=210,new384_nonbinary_inputs_verified=checked,
  new384_nonbinary_outputs_verified=outputs,new384_native_inputs_historical_hash_only=omitted,
  owner_inventory_rows_verified=len(inventory['files']),source_DD_or128256_bodies_duplicated=0,
  historical_failed_native_captures=10)
 return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output');a=p.parse_args()
 m=load((HERE/'manifest.json').read_bytes());result=replay(m,restore_files(m))
 if a.output:Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
