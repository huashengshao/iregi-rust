"""Saved-only current CLI003 unit-power N6/R6 D6 replay. No native execution."""
from pathlib import Path, PurePosixPath
from contextlib import contextmanager
import argparse, builtins, contextlib, hashlib, importlib.machinery, importlib.util, io, json, os, re, sys, tarfile, tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PREFIX='/shared/external/iregi/iregi-rust/'
CORE='validation/checked-g-generalized-core-tests'
POWER='validation/affine-power-generalized-current-core'
PARENTS={CORE:'ee4bc172dd8b87e3242158afacab425e6b13376f72dd3fbb6678feb701a97417',POWER:'0f9207da517720f4919ab8232fb3ea47dd8c50663e93cdd98b7b928b027dfbf3'}
PRIVATE='target/affine-power-post-memo-current-d6'
AUDITOR=PRIVATE+'/independent_terminal_check.py'
AUDITOR_SHA='27060f53d5a33d2a245dd1c3faf35f6e8468f6bbd0729c6f4888259a3c055ec4'

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
 result={}
 for directory,expected in PARENTS.items():
  body=(ROOT/directory/'manifest.json').read_bytes();need(sha(body)==expected,'fixed central/source or reference parent')
  helper=imported(ROOT/directory/'check.py','_d6_parent_'+str(len(result)))
  restored=helper.restore_files(load(body))
  for alias,data in restored.items():
   need(alias not in result or result[alias]==data,'exact parent alias collision');result[alias]=data
  m=load(body)
  for name in ['manifest.json',*m['capsule_files']]:result[directory+'/'+name]=(ROOT/directory/name).read_bytes()
 return result

def restore_files(manifest):
 need({str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}==set(manifest['capsule_files'])|{'manifest.json'},'closed own inventory')
 for name,row in manifest['capsule_files'].items():safe(name);need(desc((HERE/name).read_bytes())==row,'own file identity')
 result=parent_files(manifest);members={}
 with tarfile.open(fileobj=io.BytesIO((HERE/'payload.tar.gz').read_bytes()),mode='r:gz') as archive:
  for item in archive:
   safe(item.name);need(item.isfile() and item.name not in members,'unique regular payload member')
   body=archive.extractfile(item).read();need(not body.startswith((b'\x7fELF',b'!<arch>')) and b'S-130-' not in body,'no native or literal license payload')
   need(desc(body)==manifest['payload_members'].get(item.name),'member identity');members[item.name]=body
 need(set(members)==set(manifest['payload_members']),'closed payload inventory')
 for alias,row in manifest['aliases'].items():
  safe(alias);need(len(set(row)&{'parent_alias','member'})==1,'one exact byte selector')
  body=result[row['parent_alias']] if 'parent_alias'in row else members[row['member']]
  need(desc(body)=={k:row[k] for k in ['sha256','bytes']},'selected exact alias')
  need(alias not in result or result[alias]==body,'no inherited alias overwrite');result[alias]=body
 return result

@contextmanager
def saved_filesystem(files):
 """Virtual read-only project paths preserve all original absolute hash keys."""
 missing=object();names=['open','cwd','resolve','exists','stat'];owned={n:Path.__dict__.get(n,missing) for n in names}
 previous={n:getattr(Path,n) for n in names};old_loader=importlib.machinery.SourceFileLoader.get_data;old_builtin=builtins.open
 def virtual(path):
  value=str(path)
  if value.startswith(PREFIX):
   alias=value.removeprefix(PREFIX)
   if alias not in files:raise FileNotFoundError('unsaved project path: '+alias)
   return files[alias]
  return None
 def vopen(path,mode='r',buffering=-1,encoding=None,errors=None,newline=None):
  body=virtual(path)
  if body is None:return previous['open'](path,mode,buffering,encoding,errors,newline)
  need(mode in ['r','rt','rb'],'saved project is read-only')
  stream=io.BytesIO(body)
  return stream if 'b'in mode else io.TextIOWrapper(stream,encoding=encoding or 'utf-8',errors=errors or 'strict',newline=newline)
 def vresolve(path,strict=False):
  s=str(path)
  return path if s==PREFIX.rstrip('/') or s.startswith(PREFIX) else previous['resolve'](path,strict=strict)
 def vexists(path,**kwargs):
  s=str(path)
  return s.removeprefix(PREFIX) in files if s.startswith(PREFIX) else previous['exists'](path,**kwargs)
 def vstat(path,*,follow_symlinks=True):
  body=virtual(path)
  return previous['stat'](path,follow_symlinks=follow_symlinks) if body is None else os.stat_result((0o100644,0,0,1,0,0,len(body),0,0,0))
 def get_data(loader,path):
  body=virtual(path);return old_loader(loader,path) if body is None else body
 Path.open=vopen;Path.cwd=classmethod(lambda cls:cls(PREFIX.rstrip('/')));Path.resolve=vresolve;Path.exists=vexists;Path.stat=vstat
 def builtin_open(file,mode='r',buffering=-1,encoding=None,errors=None,newline=None,closefd=True,opener=None):
  if not isinstance(file,int) and str(file).startswith(PREFIX):return vopen(Path(file),mode,buffering,encoding,errors,newline)
  return old_builtin(file,mode,buffering,encoding,errors,newline,closefd,opener)
 importlib.machinery.SourceFileLoader.get_data=get_data;builtins.open=builtin_open
 try:yield
 finally:
  for name,value in owned.items():
   if value is missing:delattr(Path,name)
   else:setattr(Path,name,value)
  importlib.machinery.SourceFileLoader.get_data=old_loader;builtins.open=old_builtin

DD='target/n6-d6-full-rank6-dd-oracle-proposal'
MPFR='target/n6-d6-full-rank6-oracle-proposal'
SELECTED='target/n6-d6-positive-f-oracle-proposal'
REPORT=DD+'/independent-saved-replay-001.json'
REPLAY=DD+'/replay_saved.py'

def replay(manifest,files):
 need(sha(files[REPORT])=='c113bfee896ad19069225632788b45ed1c99f4a96001c78b821f5514acb4be65','accepted full defining-integral saved report')
 need(sha(files[REPLAY])=='3615ef7a55b227fbc18f37078df4136e343e58de37c988c47c1f05bd0edd4a82','unchanged independent full DD replay')
 for receipt_alias,mapping in manifest['receipt_input_aliases'].items():
  receipt=load(files[receipt_alias])
  for absolute,digest in receipt.get('inputs',{}).items():
   alias=mapping[absolute]
   if alias is None:need(manifest['omitted_native_inputs'].get(absolute)==digest,'explicit historical native guard')
   else:need(sha(files[alias])==digest,'saved actual receipt input body')
  for name,digest in receipt.get('outputs',{}).items():
   alias=str(Path(receipt_alias).parent/name)
   if PREFIX+alias in manifest['omitted_native_inputs']:need(manifest['omitted_native_inputs'][PREFIX+alias]==digest,'omitted native output')
   else:need(sha(files[alias])==digest,'saved actual receipt output')
 for receipt_alias,source_map in manifest['source_maps'].items():
  prefix=str(Path(receipt_alias).parent)+'/source-snapshot/'
  for name,digest in source_map.items():need(sha(files[prefix+name])==digest,'actual immutable compiled source body')
 build=load(files[DD+'/build-001/receipt.json'])
 need(build['status']=='passed_full_worker_two_exact_tests_and_preparation_inventory' and build['symbolic_inventory_equal_mpfr'] is True and len(build['sources'])==179,'actual full DD build and shared symbolic inventory')
 for i,name in enumerate(build['two_exact_tests']):
  text=files[DD+'/build-001/exact-test-'+str(i)+'.log'].decode()
  need('test '+name+' ... ok' in text and re.search(r'test result: ok\. 1 passed; 0 failed;',text),'actual exact named oracle test passed')
 inventory=load(files[DD+'/build-001/prepared-inventory.json'])
 need(sha(files[DD+'/build-001/prepared-inventory.json'])==build['prepared_inventory_sha256'],'actual prepared inventory byte binding')
 with tempfile.TemporaryDirectory(prefix='tirust-D6-saved-') as td:
  output=Path(td)/'fresh-replay.json'
  with saved_filesystem(files):
   namespace={'__file__':PREFIX+REPLAY,'__name__':'_saved_full_DD_replay'}
   exec(compile(files[REPLAY],PREFIX+REPLAY,'exec'),namespace)
   prior=sys.argv
   try:
    sys.argv=['saved-full-DD','--directory',PREFIX+DD+'/numeric-001/data','--output',str(output)]
    with contextlib.redirect_stdout(io.StringIO()):status=namespace['main']()
   finally:sys.argv=prior
  fresh=load(output.read_bytes())
 saved=load(files[REPORT]);need(status==0 and fresh==saved,'entire unchanged independent full840 report replayed exactly')
 need(fresh['status']=='saved_full840_fixed_family_agrees_numerical_evidence_only' and not fresh['failures'] and fresh['canonical_failed_slots']==fresh['sum_replay_failures']==0,'all defining-integral comparison and window reconstruction gates passed')
 need(fresh['stream_counts']['ACKs']==5068 and fresh['stream_counts']['records']==5076 and fresh['stream_counts']['windows']==40,'complete fixed stream and40windows')
 need(len(fresh['canonical_comparisons'])==2 and all(r['complex_slots']==840 and r['failures']==0 for r in fresh['canonical_comparisons']) and fresh['two_rule_difference']['complex_slots']==840 and fresh['two_rule_difference']['failures']==0,'all840perrule plus840rule difference')
 old=load(files[PRIVATE+'/captures/Float128-001/comparison.json'])
 need(len(old['failures'])==210 and all(r['slot']==3 for r in old['failures']),'all original210finite disagreements remain visible')
 target=load(files[PRIVATE+'/captures/Float128-001/stdout.json']);need(target['samples'][0]['status']=='success' and len(target['samples'][0]['moments'])==210,'original actual native full successful array preserved')
 bound=load(files[PRIVATE+'/independent-first-moment-bound.json']);need(bound['status']=='original_D6_finite_reference_violates_necessary_positive_F_first_moment_bound','original finite reference rejected by stored independent bound')
 cost=load(files[MPFR+'/numeric-001/data/estimates.json'])
 need(cost['status']=='INCOMPLETE_measured_first_window_cost' and cost['worker_rows']==32768 and cost['worker_batches']==128 and cost['windows']==1 and cost['accuracy_qualified'] is False,'MPFR cost stop retained, final arrays not invented')
 selected=load(files[SELECTED+'/independent-saved-comparison.json']);need(selected['full210_moments_qualified'] is False and selected['accuracy_qualified'] is False,'selected pilot remains diagnostic history')
 qualification=dict(status='saved_full840_fixed_family_agrees_numerical_evidence_only',canonical_rule_slots=1680,two_rule_difference_slots=840,moments=210,
  canonical_maximum_errors=[r['maximum_normalized_error'] for r in fresh['canonical_comparisons']],two_rule_maximum_error=fresh['two_rule_difference']['maximum_normalized_error'],
  stream_windows=40,stream_ACKs=5068,stream_records=5076,recorded_component_replays=5040,weight_sum_replays=2,
  original_finite_disagreements_preserved=210,original_pole_comparisons_passed=630,MPFR_cost_stop_preserved=True,
  DD_nominal_bits=106,quadrature_node_weight_bits=53,actual_native128_256_pair_qualified=False,rigorous_quadrature_accuracy_qualified=False,
  public_Dual_qualified=False,performance_qualified=False,native_execution=False,producer_import=False)
 need(qualification==manifest['qualification'],'sealed qualification matches exact replay')
 return qualification

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output');args=p.parse_args()
 m=load((HERE/'manifest.json').read_bytes());r=replay(m,restore_files(m))
 if args.output:Path(args.output).write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2))
if __name__=='__main__':main()
