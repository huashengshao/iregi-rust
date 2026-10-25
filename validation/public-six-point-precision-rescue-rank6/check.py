#!/usr/bin/env python3
"""Portable stdlib replay of the saved actual public N6 precision-rescue gate."""
from pathlib import Path,PurePosixPath
import hashlib,importlib.util,io,json,tarfile,types,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PRIVATE='target/tensor-rescue-proposal';PARENT='validation/n6-rank6-generalized-current-cli';PREFIX='/shared/external/iregi/iregi-rust/'
def require(ok,why):
 if not ok:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def desc(body):return {'sha256':sha(body),'bytes':len(body)}
def read(body):return json.loads(body)
def safe(name):
 p=PurePosixPath(name);require(bool(name) and not p.is_absolute() and '..' not in p.parts and str(p)==name,'safe alias')
def restore_files(m):
 require({str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}==set(m['capsule_files'])|{'manifest.json'},'closed capsule file inventory')
 for name,value in m['capsule_files'].items():safe(name);require(desc((HERE/name).read_bytes())==value,'capsule exact bytes '+name)
 for name,value in m['parent_files'].items():require(desc((ROOT/name).read_bytes())==value,'fixed currentCLI/quad inherited parent '+name)
 spec=importlib.util.spec_from_file_location('public_rescue_saved_cli_parent',ROOT/PARENT/'check.py');parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent);files=parent.restore_files(read((ROOT/PARENT/'manifest.json').read_bytes()))
 members={}
 with tarfile.open(fileobj=io.BytesIO((HERE/'payload.tar.gz').read_bytes()),mode='r:gz') as archive:
  for item in archive:
   safe(item.name);require(item.isfile() and item.name not in members,'unique regular payload members');body=archive.extractfile(item).read();require(desc(body)==m['payload_members'].get(item.name),'payload exact bytes');members[item.name]=body
 require(set(members)==set(m['payload_members']),'closed payload inventory')
 for name,body in members.items():require(name not in files or files[name]==body,'payload alias collision');files[name]=body
 for name,row in m['preserved_aliases'].items():
  safe(name);body=files[row['source']];require(desc(body)=={'sha256':row['sha256'],'bytes':row['bytes']},'preserved same-body source alias');require(name not in files or files[name]==body,'preserved alias collision');files[name]=body
 for name in set(m['capsule_files'])|{'manifest.json'}:files[m['capsule_directory']+'/'+name]=(HERE/name).read_bytes()
 return files

def replay(files,m):
 build=read(files[PRIVATE+'/build-002/receipt.json']);old=read(files[PRIVATE+'/build-001/receipt.json']);test=read(files[PRIVATE+'/tests-001/receipt.json']);capture=read(files[PRIVATE+'/capture-001/receipt.json'])
 require(build['status']=='passed' and build['inputs_unchanged'] and not build['cleanup_errors'] and old['status']=='failed','actual successful build and initial compile-only failure preserved')
 require(sha(files[PRIVATE+'/build-002/receipt.json'])=='c3a619c759966f3612416538eff38be9bbf9b28ab19ac2d8d778b50fb907fe0f' and sha(files[PRIVATE+'/capture-001/receipt.json'])=='4be12f0b0bbc929fb6867728828e4da5e6042be8725adef146e2416f0c547321','fixed actual build and capture')
 for build_id in ['build-001','build-002']:
  r=read(files[PRIVATE+'/'+build_id+'/receipt.json'])
  for name,value in r['source_files'].items():require(sha(files[PRIVATE+'/'+build_id+'/source-snapshot/'+name])==value,'selected actual source snapshot '+build_id+'/'+name)
 require(len(build['source_files'])==85 and build['products']['cli']['sha256']==m['owned_cli_sha256'],'restricted actual85-source context and CLI product')
 for name,value in build['outputs'].items():
  if name not in ['frozen-cli','frozen-tests']:require(sha(files[PRIVATE+'/build-002/'+name])==value,'actual Cargo event/log bytes')
 for label,r in [('test',test),('capture',capture)]:
  require(r['inputs_unchanged'] and not r['cleanup_errors'] and r['cancellation'] is None and r['post_cancellation'] is None,'historical terminal success '+label)
  for step in r['steps']:require(step['status']=='exited' and step['returncode']==0 and step['owned_group_gone'],'historical owned groups gone '+label)
  for absolute,value in r['inputs'].items():
   alias=absolute.removeprefix(PREFIX)
   if alias in files:require(sha(files[alias])==value,'available exact saved guard '+alias)
   else:require(m['omitted_native_inputs'].get(absolute)==value,'explicit omitted native/tool guard '+absolute)
  for name,value in r['outputs'].items():require(sha(files[PRIVATE+'/tests-001/'+name] if label=='test' else files[PRIVATE+'/capture-001/'+name])==value,'all saved phase output bytes '+label+'/'+name)
 require(len(test['selected_tests'])==9 and not test['unrun_tests'] and len(test['steps'])==10,'five new three legacy plus actual constructor/cache tests all retained')
 checker=files[PRIVATE+'/independent-rescue-saved-check.py'];module=types.ModuleType('independent_saved_public_rescue');exec(compile(checker,'independent-rescue-saved-check.py','exec'),module.__dict__);actual=module.audit_saved(lambda alias:files[alias]);saved=read(files[PRIVATE+'/independent-rescue-saved-review.json'])
 require(saved['checker_sha256']==sha(checker) and all(saved[key]==value for key,value in actual.items()),'unchanged independent full1470-gate replay')
 require(saved['actual_capture_bindings_verified']==23 and saved['owned_group_freshly_absent']==capture['steps'][0]['owned_process_group'],'saved independent terminal metadata retained without newprocessprobe')
 require(read(files[PRIVATE+'/independent-build002-review-failed-001.json'])['status']=='failed_independent_auditor_check' and read(files[PRIVATE+'/independent-build002-review.json'])['status']=='passed_independent_compact_saved_build002_audit','auditor initial wrong-history-hash control and corrected pass retained')
 return {'status':'passed_portable_saved_public_six_point_precision_rescue','counts':actual['counts'],'maximum_normalized_errors':actual['maximum_normalized_errors'],'actual_stages':actual['actual_stages'],'source_files':85,'all9_focused_tests_passed':True,'primary_failure_retained':True,'native_internal_precision_arrays_exported':False,'internal_convergence_independently_reconstructed':False,'accepted_scalar_sensitivity_context_unavailable':True,'Dual_dots_D6_or_performance_qualified':False,'new_native_compiler_or_process_jobs':0}
if __name__=='__main__':
 m=read((HERE/'manifest.json').read_bytes());files=restore_files(m);print(json.dumps(replay(files,m),indent=2))
