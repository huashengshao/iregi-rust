"""Saved-only memo N5 R6 dotted precision-pair replay. No native execution."""
from pathlib import Path, PurePosixPath
from contextlib import contextmanager
import argparse, hashlib, importlib.machinery, importlib.util, io, json, sys, tarfile, types
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT='validation/low-n-generalized-rank6-current-cli'
PARENT_SHA='966a55d19371f821900fb648593e4855e3b0b1d90f7eb16084d897282468aaa6'
PREFIX='/shared/external/iregi/iregi-rust/'
BUILD='target/primal-amplitude-memo/build-001'
LONG='target/low-n-explicit-generalized-rank6-memo-long-001'
PARTNER='target/low-n-explicit-generalized-rank6-memo-partner-001'
PAIR='target/low-n-explicit-generalized-rank6-memo-pair-001'
CHECKER=PAIR+'/independent_pair_check.py'
CHECKER_SHA='6eccf00777354f2cbf9d529531ab07fee79c7809577bec19b2e7fd865bd4fef3'

def need(value,reason):
 if not value:raise ValueError(reason)
def sha(body):return hashlib.sha256(body).hexdigest()
def desc(body):return dict(sha256=sha(body),bytes=len(body))
def load(body):
 def pairs(items):
  result={}
  for k,v in items:need(k not in result,'duplicate JSON key');result[k]=v
  return result
 return json.loads(body,object_pairs_hook=pairs)
def safe(name):
 p=PurePosixPath(name);need(name and str(p)==name and not p.is_absolute() and '..' not in p.parts,'safe relative alias')
def imported(path,label):
 spec=importlib.util.spec_from_file_location(label,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def parent_files(manifest):
 for name,row in manifest['parent_files'].items():safe(name);need(desc((ROOT/name).read_bytes())==row,'pinned physical parent '+name)
 parent_bytes=(ROOT/PARENT/'manifest.json').read_bytes();need(sha(parent_bytes)==PARENT_SHA,'fixed low-N parent')
 pm=load(parent_bytes);helper=imported(ROOT/PARENT/'check.py','_memo_dot_low_n_parent')
 result=helper.restore_files(pm)
 # The low-N capsule already pins the complete numeric parent, but selects only
 # N1/N4 historical jets for its own replay. This pair additionally uses its N5
 # operands from that same sealed numeric inventory; no new parent is invented.
 numeric,_=helper.parents(pm)
 for name,body in numeric.items():
  need(name not in result or result[name]==body,'exact inherited alias collision');result[name]=body
 for name in ['manifest.json',*pm['capsule_files']]:result[PARENT+'/'+name]=(ROOT/PARENT/name).read_bytes()
 return result

def restore_files(manifest):
 actual={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 need(actual==set(manifest['capsule_files'])|{'manifest.json'},'closed capsule inventory')
 for name,row in manifest['capsule_files'].items():safe(name);need(desc((HERE/name).read_bytes())==row,'own file identity')
 result=parent_files(manifest);members={}
 with tarfile.open(fileobj=io.BytesIO((HERE/'payload.tar.gz').read_bytes()),mode='r:gz') as archive:
  for item in archive:
   safe(item.name);need(item.isfile() and item.name not in members,'unique regular payload member')
   body=archive.extractfile(item).read();need(not body.startswith((b'\x7fELF',b'!<arch>')) and b'S-130-' not in body,'no native product or literal license')
   need(desc(body)==manifest['payload_members'].get(item.name),'member identity');members[item.name]=body
 need(set(members)==set(manifest['payload_members']),'closed payload inventory')
 for alias,row in manifest['aliases'].items():
  safe(alias);need(len(set(row)&{'parent_alias','member'})==1,'one exact byte selector')
  body=result[row['parent_alias']] if 'parent_alias'in row else members[row['member']]
  need(desc(body)=={k:row[k] for k in ['sha256','bytes']},'selected alias byte identity')
  need(alias not in result or result[alias]==body,'no inherited alias overwrite');result[alias]=body
 return result

@contextmanager
def saved_filesystem(files):
 """Keep immutable absolute paths/hash keys intact while denying unsaved reads."""
 previous_bytes=Path.read_bytes;previous_text=Path.read_text;previous_cwd=Path.__dict__.get('cwd');previous_resolve=Path.resolve
 previous_loader=importlib.machinery.SourceFileLoader.get_data
 def saved(path):
  value=str(path)
  if value.startswith(PREFIX):
   alias=value.removeprefix(PREFIX)
   if alias not in files:raise FileNotFoundError('unsaved project path: '+alias)
   return files[alias]
  return None
 def read_bytes(path):
  body=saved(path);return previous_bytes(path) if body is None else body
 def read_text(path,encoding=None,errors=None,newline=None):
  body=saved(path)
  if body is None:return previous_text(path,encoding=encoding,errors=errors,newline=newline)
  text=body.decode(encoding or 'utf-8',errors or 'strict')
  return text if newline=='' else text.replace('\r\n','\n').replace('\r','\n')
 def get_data(loader,path):
  body=saved(path);return previous_loader(loader,path) if body is None else body
 def resolve(path,strict=False):
  value=str(path)
  if value==PREFIX.rstrip('/') or value.startswith(PREFIX):return path
  return previous_resolve(path,strict=strict)
 Path.read_bytes=read_bytes;Path.read_text=read_text;Path.cwd=classmethod(lambda cls:cls(PREFIX.rstrip('/')));Path.resolve=resolve
 importlib.machinery.SourceFileLoader.get_data=get_data
 try:yield
 finally:
  Path.read_bytes=previous_bytes;Path.read_text=previous_text;Path.resolve=previous_resolve
  if previous_cwd is None:delattr(Path,'cwd')
  else:Path.cwd=previous_cwd
  importlib.machinery.SourceFileLoader.get_data=previous_loader

def replay(manifest,files):
 need(manifest['precision_pair_qualified'] is True,'pair may be sealed only after actual terminal qualification')
 need(sha(files[CHECKER])==CHECKER_SHA,'unchanged independent pair checker')
 build=load(files[BUILD+'/receipt.json'])
 need(build['status']=='passed' and build['inputs_unchanged'] is True and not build['cleanup_errors'],'actual memo build terminal guards')
 need(len(build['source_files'])==119 and build['source_files']==manifest['actual_source_files'],'all119 actual selected source identities')
 for name,digest in build['source_files'].items():need(sha(files[BUILD+'/source-snapshot/'+name])==digest,'actual compiled selected source body')
 for receipt_alias,resolutions in manifest['receipt_input_aliases'].items():
  receipt=load(files[receipt_alias])
  for absolute,digest in receipt.get('inputs',{}).items():
   resolved=resolutions[absolute]
   if resolved is None:need(manifest['omitted_native_inputs'].get(absolute)==digest,'explicit omitted native input')
   else:need(sha(files[resolved])==digest,'actual guarded saved input')
  for name,digest in receipt.get('outputs',{}).items():
   absolute=PREFIX+str(Path(receipt_alias).parent/name)
   if absolute in manifest['omitted_native_inputs']:need(manifest['omitted_native_inputs'][absolute]==digest,'omitted historical native output')
   else:need(sha(files[str(Path(receipt_alias).parent/name)])==digest,'actual saved output guard')
 with saved_filesystem(files):
  namespace={'__file__':PREFIX+CHECKER,'__name__':'_memo_dot_frozen_saved_pair'}
  exec(compile(files[CHECKER],PREFIX+CHECKER,'exec'),namespace)
  args=types.SimpleNamespace(protocol128=Path(PREFIX+LONG+'/protocol-per-capture.json'),capture128=Path(PREFIX+LONG+'/capture-n5-001'),
      protocol256=Path(PREFIX+PARTNER+'/protocol-per-capture.json'),capture256=Path(PREFIX+PARTNER+'/capture-n5-001'),
      protocol256_sha=namespace['PROTOCOL256_SHA'])
  fresh=namespace['compare'](args)
 saved=load(files[manifest['pair_review']])
 need(fresh==saved,'entire unchanged independent saved pair review recomputed exactly')
 need(fresh['status']=='passed_scoped_actual_N5R6_firstdot_Float128_256_pair' and not fresh['failures']
      and fresh['two_complete_actual_captures_admitted'] is True and fresh['precision128_256_convergence_qualified'] is True,'two actual admitted complete precision partners')
 need(fresh['precision_pair_slots']==2520 and fresh['reference_slots']==fresh['mass_Taylor_identity_slots']==5040
      and len(fresh['records'])==19740,'complete uncontracted tensor/identity/precision gates')
 for alias in manifest['preserved_short_timeout_receipts']:
  receipt=load(files[alias]);need(any(step.get('timeout') for step in receipt['steps']),'earlier short timeout remains explicit')
 return dict(status='passed_saved_actual_memo_N5R6_firstdot_precision_pair_replay',actual_selected_source_bodies=119,
   actual_cli_sha256=build['products']['cli']['sha256'],actual_completed_precision_captures=2,numerical_gates=len(fresh['records']),
   original_reference_slots=5040,mass_Taylor_consistency_slots=5040,precision_pair_slots=2520,
   preserved_short_timeout_receipts=len(manifest['preserved_short_timeout_receipts']),
   current_G_Mass_source_equivalence_claimed=False,current_public_Dual_qualified=False,performance_qualified=False,
   native_execution=False,producer_import=False,old_three_unrun_cases_retained_in_parent=True)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output');args=p.parse_args()
 m=load((HERE/'manifest.json').read_bytes());r=replay(m,restore_files(m))
 if args.output:Path(args.output).write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2))
if __name__=='__main__':main()
