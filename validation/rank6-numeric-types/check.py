"""Portable saved-only rank-six numeric/Taylor audit; no numerical libraries or integrals."""
from pathlib import Path,PurePosixPath
import argparse,gzip,hashlib,importlib.util,io,json,sys,tarfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
N2='validation/rank7-numeric-jets'
LOW='validation/quad-original-iregi-low-n-rank6-dot-triple'
PARENTS={N2:'46a4024858aa9abc3c59c35e29f3e14850f333a368972f50e967360218929d38',LOW:'af3530adb2d91c9d188f0303daedc4f7547ebc288617c75f8721c37c646e6e29'}
AUDIT='target/lower-n-rank6-numeric-v1/independent_fraction_audit_v1.py'
REPORT='target/lower-n-rank6-numeric-v1/independent-fraction-audit-v1.json'
MUTATIONS='target/lower-n-rank6-numeric-v1/independent_fraction_mutations_v1.py'
MUTATION_REPORT='target/lower-n-rank6-numeric-v1/independent-fraction-mutations-v1.json'
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
 """Restore exact inherited capsules without invoking their numerical audits."""
 pins={};files={}
 def merge(values):
  for name,body in values.items():
   safe(name);require(name not in files or files[name]==body,'parent alias collision');files[name]=body
 for name,manifest_sha in PARENTS.items():
  body=(root/name/'manifest.json').read_bytes();require(digest(body)==manifest_sha,'fixed parent manifest')
  m=document(body);local={name+'/manifest.json':body}
  for file,row in m['capsule_files'].items():
   b=(root/name/file).read_bytes();require(desc(b)==row,'parent capsule descriptor');local[name+'/'+file]=b
  if name==N2:
   helper=imported(root/name/'portable.py','_r6_parent_portable')
   pp,sources,borrowed=helper.load_parents(root,m['parent_files'])
   blobs=helper.unpack(local[name+'/payload.tar.gz'],m['payload_members'])
   restored,_=helper.materialize(m,blobs,sources,borrowed)
   for alias,row in pp.items():pins[alias]=row
  else:
   helper=imported(root/name/'check.py','_r6_parent_low_quad')
   restored=helper.restore_files(m)
   for alias,row in m['parent_files'].items():pins[alias]=row
  merge(restored);merge(local)
  for alias,b in local.items():pins[alias]=desc(b)
 # Parents already checked the bytes of their directly declared committed files.
 for alias,row in pins.items():
  b=(root/alias).read_bytes();require(desc(b)==row,'parent physical file identity');merge({alias:b})
 if expected is not None:require(pins==expected,'closed parent inventory')
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
def run(manifest,files,mutations=False):
 saved=document(files[REPORT]);require(saved['passed'] is True and saved['capture_count']==24 and saved['successful_capture_count']==21 and saved['preserved_guard_failure_count']==3,'saved21+3 admission')
 ns={};exec(compile(files[AUDIT],AUDIT,'exec'),ns)
 fresh=ns['audit'](files.__getitem__)
 for key,value in fresh.items():
  if key!='elapsed_seconds':require(value==saved[key],'independent replay differs: '+key)
 require(fresh['passed'] is True and fresh['complete_complex_comparisons']==446880,'all saved math checks passed')
 if mutations:
  ms={};exec(compile(files[MUTATIONS],MUTATIONS,'exec'),ms)
  m=ms['reject_probes'](files.__getitem__,ns['audit']);old=document(files[MUTATION_REPORT])
  for key,value in m.items():require(value==old[key],'mutation replay differs: '+key)
  require(len(m['probes'])==5 and m['passed'],'five semantic probes')
 return dict(status='passed_saved_rank6_numeric_types_with_three_preserved_guard_failures',capture_count=24,successful_capture_count=21,preserved_guard_failure_count=3,complete_complex_comparisons=446880,comparison_totals=fresh['comparison_totals'],max_normalized_errors=fresh['max_normalized_errors'],authorship=fresh['authorship'],mutations_replayed=mutations,no_integral_execution=True,no_producer_import=True,performance_qualified=False)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mutations',action='store_true');p.add_argument('--output');a=p.parse_args()
 manifest=document((HERE/'manifest.json').read_bytes());r=run(manifest,restore_files(manifest),a.mutations)
 if a.output:Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({k:v for k,v in r.items() if k!='max_normalized_errors'},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
