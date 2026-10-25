#!/usr/bin/env python3
"""Portable saved-only replay. The14-case numerical corpus remains partial."""
import argparse,ast,hashlib,importlib.util,io,json,sys,tarfile
from pathlib import Path,PurePosixPath
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIVATE='target/orthogonal-rank6-current-cli'
PREFIX='/shared/external/iregi/iregi-rust/'
ALLOWED={'pathlib','fractions','decimal','collections','hashlib','json','re'}
def require(ok,why):
 if not ok:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def desc(body):return {'sha256':sha(body),'bytes':len(body)}
def read(body):return json.loads(body)
def safe(name):
 p=PurePosixPath(name);require(name and not p.is_absolute()and '..'not in p.parts and str(p)==name,'safe archive alias')
def parent_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

def restore_files(manifest=None):
 m=manifest or read((HERE/'manifest.json').read_bytes())
 actual={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and '_work'not in p.relative_to(HERE).parts and '__pycache__'not in p.relative_to(HERE).parts}
 require(actual==set(m['capsule_files'])|{'manifest.json'},'closed capsule inventory')
 for name,pin in m['capsule_files'].items():safe(name);require(desc((HERE/name).read_bytes())==pin,'capsule bytes '+name)
 for name,pin in m['parent_files'].items():safe(name);require(desc((ROOT/name).read_bytes())==pin,'exact declared parent file '+name)
 files={}
 for i,row in enumerate(m['parent_roots']):
  directory=ROOT/row['capsule_directory'];require(sha((directory/'manifest.json').read_bytes())==row['manifest_sha256']and sha((directory/'check.py').read_bytes())==row['check_sha256'],'exact admitted parent')
  module=parent_module('orthogonal_r6_parent_'+str(i),directory/'check.py');inherited=module.restore_files(read((directory/'manifest.json').read_bytes()))
  for name,body in inherited.items():require(name not in files or files[name]==body,'parent alias collision');files[name]=body
 require(len(files)==m['parent_union_aliases'],'exact merged parent alias count')
 origins=read((HERE/'origins.json').read_bytes());entries={x['alias']:x for x in origins['members']};members={}
 with tarfile.open(fileobj=io.BytesIO((HERE/'payload.tar.gz').read_bytes()),mode='r:gz')as archive:
  for item in archive:
   safe(item.name);require(item.isfile()and item.name not in members and item.name in entries,'unique regular payload member');body=archive.extractfile(item).read();require(desc(body)=={k:entries[item.name][k]for k in['sha256','bytes']},'own preserved bytes');require(not body.startswith(b'\x7fELF')and '__pycache__'not in PurePosixPath(item.name).parts,'compiled payload forbidden');members[item.name]=body
 require(set(members)==set(entries),'complete own payload inventory')
 for row in origins['inherited_aliases']:
  require(row['parent_source_alias']in files and desc(files[row['parent_source_alias']])=={k:row[k]for k in['sha256','bytes']},'exact borrowed alias')
  require(row['alias']not in files or files[row['alias']]==files[row['parent_source_alias']],'borrowed alias collision');files[row['alias']]=files[row['parent_source_alias']]
 for name,body in members.items():require(name not in files or files[name]==body,'own versus parent alias collision');files[name]=body
 require(len(members)==m['own_aliases']and len(files)==m['restored_evidence_aliases'],'complete preserved evidence aliases')
 for name in set(m['capsule_files'])|{'manifest.json'}:files['validation/orthogonal-rank6-current-cli/'+name]=(HERE/name).read_bytes()
 return files

def replay(files,manifest=None):
 m=manifest or read((HERE/'manifest.json').read_bytes());source=PRIVATE+'/independent/audit_saved.py';saved=read(files[PRIVATE+'/independent/review.json']);raw=files[source]
 require(sha(raw)==saved.pop('checker_sha256')==m['independent_checker_sha256'],'unchanged independent checker')
 tree=ast.parse(raw,filename=source)
 for node in ast.walk(tree):
  if isinstance(node,ast.Import):require(all(x.name in ALLOWED for x in node.names),'stdlib audit imports only')
  elif isinstance(node,ast.ImportFrom):require(node.level==0 and node.module in ALLOWED,'stdlib audit imports only')
 namespace={'__name__':'restored_orthogonal_independent_math','__file__':source};exec(compile(tree,source,'exec'),namespace)
 computed=namespace['audit'](lambda name:files[name]);require(computed==saved,'entire independent24444-decision receipt equality')
 require(computed['numeric_records_recomputed']==computed['numeric_records_passed']==24444 and computed['complete_cases']==12 and computed['terminal_calls']==14 and computed['available_complex_slots']==11760 and computed['unavailable_complex_slots']==1680,'all available and missing values counted')
 require(len(computed['unqualified_collinear_failures'])==2 and computed['original_overall_cohort_remains_partial']is True and computed['old_stable_zero_N4_reference_rejected']is True and computed['new_N4_order32_oracle_independently_admitted']is True,'failed routes and rejected reference remain visible')
 p=read(files[PRIVATE+'/protocol.json']);source_prefix=p['source_snapshot_root'].removeprefix(PREFIX)
 require(len(p['source_snapshot_files'])==77,'selected source count')
 for name,pin in p['source_snapshot_files'].items():require(sha(files[source_prefix+'/'+name])==pin,'inherited exact selected source snapshot')
 q=read(files[PRIVATE+'/qualification.json']);require(sha(files[PRIVATE+'/qualification.json'])==m['qualification_sha256']and q['independent_saved_review_sha256']==sha(files[PRIVATE+'/independent/review.json']),'final partial qualification pins')
 require(q['whole_corpus_qualified']is False and q['complete_cases']==12 and q['failed_cases']==2 and q['unavailable_failed_complex_slots']==1680 and q['all_available_saved_math_records_passed']is True,'partial cohort never upgraded')
 for key in['full_generic_rank6_goal_qualified','arbitrary_N_denominator_descent_qualified','new_performance_measurements','broad_threshold_or_complex_domain_qualified','Dual_qualified','later_supplied_G_Legacy_Hybrid_source_context_inherited']:require(q[key]is False,'scope improperly promoted '+key)
 return {'status':'passed_saved_evidence_replay_corpus_remains_partial','terminal_calls':14,'complete_cases':12,'unqualified_collinear_cases':2,'successful_lane_arrays':14,'available_complex_slots':11760,'unavailable_complex_slots':1680,'independent_numeric_records':24444,'all_available_numeric_records_passed':True,'independent_checks':computed['checks'],'selected_source_files':77,'old_N4_stable_zero_reference_rejected':True,'new_N4_fixed_order32_oracle_admitted':True,'whole_corpus_or_generic_domain_qualified':False,'new_native_evaluator_compiler_or_PID_work':False,'fresh_omitted_native_or_external_tool_hash_verification':False,'Dual_or_performance_qualified':False}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reconstruct',type=Path);args=parser.parse_args();m=read((HERE/'manifest.json').read_bytes());files=restore_files(m);summary=replay(files,m)
 if args.reconstruct is not None:
  destination=args.reconstruct.resolve();require(not destination.exists()or(destination.is_dir()and not any(destination.iterdir())),'new empty reconstruction directory');destination.mkdir(parents=True,exist_ok=True)
  for name,body in files.items():safe(name);path=destination/name;path.parent.mkdir(parents=True,exist_ok=True);require(not path.exists(),'no overwrite');path.write_bytes(body)
  summary['reconstructed_files']=len(files)
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
