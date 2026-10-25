"""Portable saved-only public N4 rank-six mixed Dual precision-rescue qualification."""
from pathlib import Path,PurePosixPath
import argparse,gzip,hashlib,importlib.util,io,json,sys,tarfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PARENT='validation/rank6-numeric-types'
PARENT_SHA='0627daec0b72aba02e5dcd36f3c02129c03e7e4e044a5b95dd2efaf4e3b6fc62'
PREFIX='target/n4-rank6-public-dual-rescue-v1'
AUDIT=PREFIX+'/independent_saved_audit.py'
REPORT=PREFIX+'/independent-saved-audit.json'
def require(v,m):
 if not v:raise ValueError(m)
def digest(b):return hashlib.sha256(b).hexdigest()
def desc(b):return dict(sha256=digest(b),bytes=len(b))
def document(b):
 def pairs(items):
  d={}
  for k,v in items:require(k not in d,'duplicate JSON key');d[k]=v
  return d
 return json.loads(b,object_pairs_hook=pairs)
def safe(n):
 p=PurePosixPath(n);require(n and str(p)==n and not p.is_absolute() and '..' not in p.parts,'safe relative alias')
def imported(path,label):
 spec=importlib.util.spec_from_file_location(label,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def parent_files(root,expected=None):
 """Borrow exact source/reference/result parent bytes without its math replay."""
 body=(root/PARENT/'manifest.json').read_bytes();require(digest(body)==PARENT_SHA,'fixed rank6 parent manifest')
 m=document(body);pins=dict(m['parent_files']);local={PARENT+'/manifest.json':body}
 for name,row in m['capsule_files'].items():
  b=(root/PARENT/name).read_bytes();require(desc(b)==row,'parent capsule identity');local[PARENT+'/'+name]=b
 for name,b in local.items():pins[name]=desc(b)
 for name,row in pins.items():require(desc((root/name).read_bytes())==row,'parent physical identity')
 if expected is not None:require(pins==expected,'closed parent inventory')
 helper=imported(root/PARENT/'check.py','_n4_rescue_rank6_parent')
 files=helper.restore_files(m,root)
 for name,b in local.items():require(name not in files or files[name]==b,'parent alias collision');files[name]=b
 return files,pins
def restore_files(manifest,root=None):
 root=HERE.parents[1] if root is None else Path(root)
 own=set(manifest['capsule_files'])|{'manifest.json'}
 require({str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}==own,'closed capsule inventory')
 for name,row in manifest['capsule_files'].items():safe(name);require(desc((HERE/name).read_bytes())==row,'own file identity '+name)
 files,_=parent_files(root,manifest['parent_files']);members={}
 with tarfile.open(fileobj=io.BytesIO((HERE/'payload.tar.gz').read_bytes()),mode='r:gz') as archive:
  for member in archive:
   safe(member.name);require(member.isfile() and member.name not in members,'unique regular payload member')
   b=archive.extractfile(member).read();require(desc(b)==manifest['payload_members'].get(member.name),'payload member identity');members[member.name]=b
 require(set(members)==set(manifest['payload_members']),'closed payload inventory')
 for alias,row in manifest['aliases'].items():
  safe(alias);b=files[row['inherited_alias']] if 'inherited_alias' in row else members[row['member']]
  require(desc(b)=={k:row[k] for k in ['sha256','bytes']},'restored alias identity '+alias)
  require(alias not in files or files[alias]==b,'own alias collision');files[alias]=b
 return files
def run(manifest,files):
 saved=document(files[REPORT]);require(saved['passed'] is True and saved['status']=='passed_independent_saved_public_N4R6_dual_rescue_audit','independent rescue admission')
 ns={};exec(compile(files[AUDIT],AUDIT,'exec'),ns);fresh=ns['audit'](files.__getitem__)
 for key,value in fresh.items():
  if key!='elapsed_seconds':require(value==saved[key],'unchanged independent saved replay '+key)
 require(fresh['passed'] is True and sum(fresh['comparison_counts'].values())==35280,'all35280 complex gates')
 built=document(files['target/root-frontend-check/build-004/receipt.json'])
 require(built['status']=='passed' and built['inputs_unchanged'] is True and built['cleanup_errors']==[],'actual example build')
 for name,sha in built['source_files'].items():require(digest(files['target/root-frontend-check/build-004/source-snapshot/'+name])==sha,'all106 actual source snapshots')
 require(len(built['source_files'])==106,'exact selected source scope')
 old=document(files['target/root-frontend-check/build-003/receipt.json'])
 require(old['status']=='failed' and old['inputs_unchanged'] is True and [step['returncode'] for step in old['steps']]==[0,0,101],'initial third-only compile failure retained')
 require(b'E0277' in files['target/root-frontend-check/build-003/cargo-2.log'],'original compile diagnostic')
 rescue='crates/iregi-rust/examples/rank7_numeric_jets/rescue.rs'
 before=files['target/root-frontend-check/build-003/source-snapshot/'+rescue]
 after=files['target/root-frontend-check/build-004/source-snapshot/'+rescue]
 require(after==before.replace(b'.collect::<Fallible<Vec<_>>>()?;',b'.collect::<Result<Vec<_>,String>>()?;',1),'one-line typed error collection correction')
 return dict(status='passed_saved_public_N4R6_f64_mixed_Dual_rescue',complete_complex_comparisons=35280,comparison_counts=fresh['comparison_counts'],max_normalized_errors=fresh['max_normalized_errors'],binary64_coordinates=fresh['binary64_representable_coordinates_checked'],external128_rounding_diagnostics=fresh['external_Float128_rounding_diagnostics'],preserved_previous_guard_failures=fresh['preserved_previous_guard_failures'],internal_128_256_arrays_independently_audited=False,all106selectedsource_snapshots_checked=True,no_integral_execution=True,no_producer_import=True,performance_qualified=False)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output');a=p.parse_args()
 manifest=document((HERE/'manifest.json').read_bytes());r=run(manifest,restore_files(manifest))
 if a.output:Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({k:v for k,v in r.items() if k!='max_normalized_errors'},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
