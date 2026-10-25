#!/usr/bin/env python3
"""Portable saved-only replay of this restricted N6/rank6 CLI record."""
import argparse,hashlib,importlib.util,io,json,tarfile,types
from pathlib import Path,PurePosixPath
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIVATE='target/n6-rank6-generalized-current-cli'
PARENT='validation/quad-original-iregi-generalized-n6-rank6'
PREFIX='/shared/external/iregi/iregi-rust/'
def require(ok,why):
 if not ok:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def desc(body):return {'sha256':sha(body),'bytes':len(body)}
def read(body):return json.loads(body)
def safe(name):
 p=PurePosixPath(name);require(bool(name) and not p.is_absolute() and '..' not in p.parts and str(p)==name,'safe alias')
def restore_files(m):
 require({str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}==set(m['capsule_files'])|{'manifest.json'},'closed capsule files')
 for name,expected in m['capsule_files'].items():safe(name);require(desc((HERE/name).read_bytes())==expected,'capsule byte identity '+name)
 for name,expected in m['parent_files'].items():require(desc((ROOT/name).read_bytes())==expected,'fixed admitted quad parent '+name)
 spec=importlib.util.spec_from_file_location('n6_r6_quad_parent',ROOT/PARENT/'check.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 files=module.restore_files(read((ROOT/PARENT/'manifest.json').read_bytes()))
 members={}
 with tarfile.open(fileobj=io.BytesIO((HERE/'payload.tar.gz').read_bytes()),mode='r:gz') as archive:
  for item in archive:
   safe(item.name);require(item.isfile() and item.name not in members,'unique regular payload')
   body=archive.extractfile(item).read();require(desc(body)==m['payload_members'].get(item.name),'payload byte identity '+item.name);members[item.name]=body
 require(set(members)==set(m['payload_members']),'closed payload inventory')
 for name,body in members.items():require(name not in files or files[name]==body,'saved alias collision');files[name]=body
 for name in set(m['capsule_files'])|{'manifest.json'}:files[m['capsule_directory']+'/'+name]=(HERE/name).read_bytes()
 return files

def comparison(files,source,output,reference,sample,bits,rescue=False):
 # Execute only the pinned pure saved comparator. Its file readers are supplied
 # byte aliases; no native evaluator, producer, compiler or process probe runs.
 module=types.ModuleType('restricted_n6_saved_comparator');exec(compile(files[source],source,'exec'),module.__dict__)
 module.read=lambda alias:read(files[str(alias)])
 class SavedPath:
  def __init__(self,alias):self.alias=str(alias)
  def read_text(self):return files[self.alias].decode()
 module.Path=SavedPath
 return module.audit(output,reference,sample,bits,rescue)

def replay(files,m):
 build=read(files[PRIVATE+'/build-001/receipt.json'])
 require(build['status']=='passed' and build['inputs_unchanged'] and not build['cleanup_errors'],'actual Cargo owned CLI build')
 product=build['products']['cli'];require(product['sha256']==m['owned_cli_sha256'],'actual selected product hash')
 for name,digest in build['source_files'].items():require(sha(files[PRIVATE+'/build-001/source-snapshot/'+name])==digest,'actual selected source snapshot')
 require(len(build['source_files'])==77,'restricted77-file build snapshot')
 expected=['n6_rank6_first_dot2-128-001','n6_rank6_unit_control-f64-001','n6_rank6_unit_control-pv-dd-001','n6_rank6_unit_control-f64-rescue-001','n6_rank6_unit_control-pv-f64-001','n6_rank6_unit_D6-128-001']
 require([row['directory'] for row in m['captures']]==expected,'six fixed distinct owned attempts')
 summaries=[];successful=0;reference_slots=0
 for row in m['captures']:
  base=PRIVATE+'/captures/'+row['directory'];r=read(files[base+'/receipt.json'])
  require(r['status']==row['status'] and r['status']!='preflight' and r['inputs_unchanged'] and not r['cleanup_errors'] and r['elapsed_seconds']<=r['total_seconds'],'historical bounded terminal capture')
  require(len(r['steps'])==1 and r['steps'][0]['owned_group_gone'] is True,'historical owned group cleanup')
  for absolute,digest in r['inputs'].items():
   alias=absolute.removeprefix(PREFIX)
   if alias in files:require(sha(files[alias])==digest,'available exact historical input '+alias)
   else:require(m['omitted_native_inputs'].get(absolute)==digest,'explicit omitted native input '+absolute)
  output=files[base+'/stdout.json'];require(sha(output)==r['stdout_sha256'],'exact captured stdout')
  if r['status']=='passed_complete_capture_and_840_quad_slots':
   require(r['steps'][0]['status']=='exited' and r['steps'][0]['returncode']==0,'successful native step')
   sample=read(files[PRIVATE+'/inputs/'+r['case']+'.json']);reference='target/n6-rank6-generalized-quad/capture-001/request-'+('6' if r['case']=='n6_rank6_unit_D6' else '0')+'.stdout'
   source=base+'/controller-snapshot/'+('compare_saved.py' if r['case']=='n6_rank6_unit_D6' else 'compare_saved_pv.py')
   actual=comparison(files,source,base+'/stdout.json',reference,sample,r['working_bits'])
   saved=read(files[base+'/comparison.json']);require(actual==saved and actual['status']=='passed_complete_N6_rank6_quad_comparison' and not actual['failures'],'complete native840 saved gate replay')
   require(sha(files[base+'/comparison.json'])==r['comparison_sha256'],'saved numerical gate identity');successful+=1;reference_slots+=840
   summaries.append({'directory':row['directory'],'status':r['status'],'counts':actual['counts'],'maxima':actual['maximum_normalized_errors'],'actual_algorithm':actual['actual_algorithm'],'engine':actual['engine_execution']['engine']})
  else:
   require(r['status']=='failed_or_incomplete' and base+'/comparison.json' not in files,'failure not upgraded to full numerical gate')
   if output:
    d=read(output);require(len(d['samples'])==1 and d['samples'][0]['status']=='failed' and 'moments' not in d['samples'][0],'failed lane never supplies successful scratch zeros')
    sample=d['samples'][0];require(sample['reason']==row['reason'],'exact retained failure reason')
    if row['directory'].endswith('f64-rescue-001'):require(sample['precision_rescue']['status']=='rejected' and d['rescue_execution']['accepted_rows']==0,'explicit generic rescue remains rejected')
   else:require(row['no_array'] is True,'empty timeout remains no array')
   summaries.append({'directory':row['directory'],'status':r['status'],'failure':row.get('reason'),'no_array':True})
 require(successful==m['successful_arrays'] and reference_slots==m['replayed_reference_slots'],'restricted completion counts')
 return {'status':'passed_portable_restricted_N6_rank6_CLI_record','successful_arrays':successful,'reference_slots':reference_slots,'attempts':summaries,'generic_dotted_and_shifted_domain_qualified':False,'all_numeric_types_qualified':False,'native_jobs':0,'compiler_jobs':0,'fresh_process_probes':0,'performance_qualified':False}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.parse_args();m=read((HERE/'manifest.json').read_bytes());files=restore_files(m);print(json.dumps(replay(files,m),indent=2))
if __name__=='__main__':main()
