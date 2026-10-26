"""Replay saved evidence honestly: both DD validations pass; strict128/256 fails."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PREFIX='/shared/external/iregi/iregi-rust/'
PARENT='validation/e6-dual-restored-zero-profile-core-tests'
RAW384='target/e6-dual-restored-zero-profile-opt3-384-256g'
def need(v,m):
 if not v:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'sha256':sha(b),'bytes':len(b)}
def safe(a):
 need(type(a)is str and bool(a)and '\0'not in a,'string alias')
 p=PurePosixPath(a)
 need(str(p)==a and not p.is_absolute()and '..'not in p.parts,'safe canonical relative path')
 need(a!=RAW384 and not a.startswith(RAW384+'/'),'active384 evidence excluded')
def load(b):
 def pairs(items):
  result={}
  for k,v in items:need(k not in result,'duplicate JSON key');result[k]=v
  return result
 return json.loads(b,object_pairs_hook=pairs)
def restore_files(m):
 need(m['status']=='sealed_saved_precision_boundary_with_failed128256_gate','honest boundary status')
 for name,row in m['capsule_files'].items():safe(name);need(desc((HERE/name).read_bytes())==row,'capsule file hash')
 for name,row in m['parent_files'].items():safe(name);need(desc((ROOT/name).read_bytes())==row,'pinned shallow parent file')
 pb=(ROOT/PARENT/'manifest.json').read_bytes()
 need(sha(pb)==m['parent_manifest_sha256']=='1f1a41fdbc30ca1b3d5a18ce59db9f23fa0bb774950dba464aadfd05aabc5d04','current source parent')
 parent=runpy.run_path(str(ROOT/PARENT/'check.py'),run_name='boundary_source_parent')
 inherited=parent['restore_files'](load(pb))
 reader=runpy.run_path(str(ROOT/'validation/e6-dual-postfix-resource-boundaries/check.py'),run_name='boundary_archive_reader')
 safe(m['payload_file']);own=reader['unpack']((HERE/m['payload_file']).read_bytes(),m['payload_members'],complete=True)
 files=dict(inherited)
 for a,row in m['aliases'].items():
  safe(a)
  if 'parent_alias'in row:safe(row['parent_alias']);b=inherited[row['parent_alias']]
  elif 'parent_file'in row:
   safe(row['parent_file']);need(row['parent_file']in m['parent_files'],'pinned parent selector');b=(ROOT/row['parent_file']).read_bytes()
  else:b=own[row['member']]
  need(desc(b)=={k:row[k]for k in('sha256','bytes')},'saved body identity')
  need(a not in files or files[a]==b,'no historical canonical overwrite');files[a]=b
 return files
def replay(m,files):
 def read(a):return load(files[a])
 q=m['qualification']
 need(q['strict_precision_pair_qualified']is False and q['full_objective_met']is False
  and q['default_Hybrid_qualified']is False and q['actual384']is None,'no final convergence/Hybrid/384 qualification')
 need(m['counts']['historical_failed_native_captures']==10
  and m['counts']['strict_failure_is_additional_native_failure']is False,'strict failure is not another native capture failure')
 inventory_rows=0
 for a,digest in m['owner_inventories'].items():
  need(sha(files[a])==digest,'immutable owner inventory')
  for alias,row in read(a)['files'].items():need(desc(files[alias])==row,'exact owner-frozen evidence row');inventory_rows+=1
 build=read(m['actual_current_build_receipt_alias'])
 need(sha(files[m['actual_current_build_receipt_alias']])=='b0695760d975d4c0f789400699861f3b4581f7fae5677d682748f2cf0e075da2'
  and len(build['sources'])==len(m['current_source_aliases'])==210,'actual source210 build')
 for canonical,digest in build['sources'].items():
  a=m['current_source_aliases'][canonical];safe(a);need(sha(files[a])==digest,'actual compiled source snapshot')
 guards=[]
 for key,bits,expected in [('complete128',128,237),('complete256',256,248)]:
  c=m[key];r=read(c['receipt_alias']);p=read(c['protocol_alias'])
  need(r['working_bits']==bits and r['requested_bits']==53 and len(r['inputs'])==expected
   and r['inputs_unchanged']is True and r['cleanup_errors']==[]and r['cancellation']is None,'actual terminal precision/source guards')
  need(len(r['steps'])==1 and r['steps'][0]['status']=='exited'and r['steps'][0]['returncode']==0
   and r['steps'][0]['owned_group_gone']is True,'actual terminal native producer cleanup')
  need(p['source_context']['count']==210 and p['source_context']['build_receipt_sha256']==sha(files[m['actual_current_build_receipt_alias']])
   and p['binary']['sha256']==build['products']['tests']['sha256'],'same source and actual frozen product')
  checked=outputs=omitted=0
  for absolute,digest in r['inputs'].items():
   if absolute in m['omitted_native_artifacts']:need(m['omitted_native_artifacts'][absolute]==digest,'historical native hash only');omitted+=1;continue
   need(absolute.startswith(PREFIX),'project-local saved input');a=absolute[len(PREFIX):]
   a=m['current_source_aliases'].get(a,a);safe(a);need(sha(files[a])==digest,'actual nonbinary input bytes');checked+=1
  base=c['receipt_alias'].rsplit('/',1)[0]
  for name,digest in r['outputs'].items():
   a=base+'/'+name;safe(a)
   if PREFIX+a in m['omitted_native_artifacts']:need(m['omitted_native_artifacts'][PREFIX+a]==digest,'omitted output native hash')
   else:need(sha(files[a])==digest,'actual nonbinary output bytes');outputs+=1
  mechanism=read(c['mechanism_alias']);root=read(c['root_review_alias'])
  need(mechanism['status']=='passed_saved_mechanism_gate_only'and mechanism['capture_sha256']==sha(files[c['capture_alias']])
   and mechanism['mechanism']['successful_parent_rows']==3 and mechanism['mechanism']['successful_child_rows']==6,'complete mechanism scope')
  expected_root_status={128:'root_reviewed_complete_Float128_numeric_mechanism_lifecycle_pass',
   256:'root_reviewed_complete_Float256_DD_mechanism_lifecycle_pass_strict128256_failed'}
  need(root['status']==expected_root_status[bits],'actual root terminal acceptance with retained strict failure')
  guards.append({'working_bits':bits,'historical_input_bindings':expected,'nonbinary_inputs_rehashed':checked,
   'nonbinary_outputs_rehashed':outputs,'native_inputs_historical_hash_only':omitted})
 note=read('target/rank6-final-feature-report-20261026/algorithm-scope-equivalence.json')
 need(len(note['source_files'])==11 and note['observed_full_h1_default_Hybrid_capture']is False
  and note['new_numerical_qualification']is False,'shared-route source note remains source-only')
 for canonical,row in note['source_files'].items():need(desc(files[m['current_source_aliases'][canonical]])=={k:row[k]for k in('sha256','bytes')},'11 current-source note pins')
 pins=read(m['diagnosis']['pins_alias'])
 for canonical,digest in dict(pins['build_selected_sources'],**pins['dependency_inspection_only_sources']).items():
  a=m['source_read_aliases'][canonical];safe(a);need(sha(files[a])==digest,'scoped source-only diagnosis read projection')
 math=runpy.run_path(str(HERE/'saved_math.py'),run_name='boundary_frozen_math_adapters')
 result=math['replay_boundary_math'](m,files)
 result.update(owner_inventory_rows_verified=inventory_rows,actual_source_files_verified=210,
  lifecycle_guards=guards,source_note_current_pins_verified=11,
  mutable384_capture_read_or_bound=False,historical_failed_native_captures=10,
  strict_failure_is_additional_native_failure=False,source_and_DD_bodies_duplicated=0)
 return result
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output');a=p.parse_args()
 m=load((HERE/'manifest.json').read_bytes());result=replay(m,restore_files(m))
 if a.output:Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
