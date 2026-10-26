"""Parametric terminal-only collection. Missing accepted external handoff fails closed.

SOURCE PREPARATION ONLY until root authorizes actual collection. No work occurs
on import. Native artifacts are never read. No grid/integral is evaluated.
"""
from pathlib import Path,PurePosixPath
import argparse,gzip,hashlib,io,json,runpy,shutil,sys,tarfile
sys.dont_write_bytecode=True
PREFIX='/shared/external/iregi/iregi-rust/'
PARENT='validation/e6-dual-rank6-precision-boundary'
PARENT_SHA='cd656689a9c02dd92c401a0ad9009be7e7f7e655d1f62d337b44fd66555777fa'
RAW384='target/e6-dual-restored-zero-profile-opt3-384-256g'
PRODUCT='749b2ae3489eb0096267421b120fa3586f2243c7eaf78fc9c02b0f9f30895906'
BUILD='b0695760d975d4c0f789400699861f3b4581f7fae5677d682748f2cf0e075da2'
FROZEN={
 'target/e6-dual-restored-precision-extension/check_saved_mechanism.py':'dc6905601b9b60edbd97abe89efd091c57cd452c6986d6e7379f4139ccf67e56',
 'target/n6-sample-d6-mass-second-anchor-dd/compare_saved_precision_384.py':'783e26b4ab27b3702d4b3e5e2d47c9a868aa3f1122e2554c192098b566cae2ec',
 'target/e6-dual-restored-precision-extension/compare_saved_pair256_384.py':'9eb24f13702a6e8e32e25c10971a95024ba44352f0dd45a6743ebaebea731be7',
 'target/rank6-independent-complete-pair-review.py':'a6e79be973f31ff0e47978d333c74996470392c66db453343e9625d1a9317e1b',
 'target/rank6-independent256384-history-wrapper.py':'4ff7a7f01c8f3200f3c507a1bd35cea17489d67ea6e265e62bcc90fa5fa03a23'}
def need(v,m):
 if not v:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'sha256':sha(b),'bytes':len(b)}
def safe(a):
 need(type(a)is str and bool(a)and '\0'not in a,'string alias')
 p=PurePosixPath(a);need(str(p)==a and not p.is_absolute()and '..'not in p.parts,'canonical safe relative alias')
def load(b):
 def pairs(items):
  out={}
  for k,v in items:need(k not in out,'duplicate JSON key');out[k]=v
  return out
 return json.loads(b,object_pairs_hook=pairs)
def accepted_handoff(h):
 need(h.get('status')=='accepted_terminal384_and_strict256384_for_final_capsule'
  and h.get('collection_authorized_by_root')is True,'explicit actual root-authorized terminal handoff required')
 for key in ('actual384','qualifying256384_pair','independent256384'):
  need(type(h.get(key))is dict and h[key].get('accepted_by_owner_and_root')is True,'actual accepted external gate: '+key)
 need(type(h.get('owner_inventory'))is dict and type(h.get('root_terminal_review'))is dict,'actual inventory/root review descriptors required')
 need(type(h['actual384'].get('expected_input_bindings'))is int and h['actual384']['expected_input_bindings']>=210,
  'actual externally reviewed terminal guard inventory required')

def collect(root,here,handoff_alias,handoff_sha):
 safe(handoff_alias)
 need(handoff_alias.startswith('target/')and not(handoff_alias==RAW384 or handoff_alias.startswith(RAW384+'/')),
  'external handoff must be outside producer capture directory')
 hb=(root/handoff_alias).read_bytes();need(sha(hb)==handoff_sha,'external root/owner handoff identity')
 h=load(hb);accepted_handoff(h)
 inventory_row=h['owner_inventory'];safe(inventory_row['alias'])
 need(inventory_row['alias']!=RAW384 and not inventory_row['alias'].startswith(RAW384+'/'),'external immutable owner inventory required')
 ib=(root/inventory_row['alias']).read_bytes();need(sha(ib)==inventory_row['sha256'],'actual accepted immutable owner inventory')
 inventory=load(ib);need(type(inventory.get('files'))is dict and bool(inventory['files']),'actual inventory files map')
 for a,row in inventory['files'].items():safe(a);need(set(row)=={'sha256','bytes'},'exact immutable body descriptors')
 higher=h['actual384']
 for key in ('receipt_alias','capture_alias','protocol_alias','mechanism_alias','numeric_alias','checker_source_alias'):
  safe(higher[key]);need(higher[key]in inventory['files'],'actual384 role must be frozen by owner inventory')
 # Only the explicitly accepted terminal receipt is read before any capture body.
 rbody=(root/higher['receipt_alias']).read_bytes()
 need(desc(rbody)==inventory['files'][higher['receipt_alias']],'actual terminal receipt descriptor')
 receipt=load(rbody)
 need(receipt['status']=='completed_explicit_PV_capture_pending_saved_mechanism_gate_and_independent_oracle'
  and receipt['working_bits']==384 and receipt['requested_bits']==53
  and receipt['inputs_unchanged']is True and receipt['cleanup_errors']==[]and receipt['cancellation']is None
  and len(receipt['steps'])==1 and receipt['steps'][0]['status']=='exited'
  and receipt['steps'][0]['returncode']==0 and receipt['steps'][0]['owned_group_gone']is True,
  'real complete terminal384 required before reading archived capture body')
 need(len(receipt['inputs'])==higher['expected_input_bindings'],'actual root-reviewed terminal guard count')
 need(receipt['outputs']['capture.json']==inventory['files'][higher['capture_alias']]['sha256']
  and receipt['outputs']['frozen-tests']==PRODUCT,'actual terminal output and identical749 observation')
 pb=(root/PARENT/'manifest.json').read_bytes();need(sha(pb)==PARENT_SHA,'once-owned immutable128256 boundary')
 pm=load(pb);parent=runpy.run_path(str(root/PARENT/'check.py'),run_name='final_parent_byte_loader')
 inherited=parent['restore_files'](pm)
 parents=dict(pm['parent_files'])
 for n,row in pm['capsule_files'].items():safe(n);parents[PARENT+'/'+n]=row
 parents[PARENT+'/manifest.json']=desc(pb)
 byhash={}
 for a,b in inherited.items():byhash.setdefault(sha(b),a)
 aliases={};objects={};allowed=set(inventory['files'])|set(FROZEN)|{handoff_alias,inventory_row['alias']}
 omitted=dict(pm['omitted_native_artifacts'])
 capture_base=higher['receipt_alias'].rsplit('/',1)[0]
 omitted[PREFIX+capture_base+'/frozen-tests']=PRODUCT
 for absolute,digest in receipt['inputs'].items():
  need(absolute.startswith(PREFIX),'project-local actual native guard')
  a=absolute[len(PREFIX):];safe(a)
  if digest==PRODUCT:omitted[absolute]=digest
  else:allowed.add(pm['current_source_aliases'].get(a,a))
 for n in receipt['outputs']:
  safe(capture_base+'/'+n)
  if n!='frozen-tests':allowed.add(capture_base+'/'+n)
 def add(a,digest):
  safe(a);need(not a.endswith(('/frozen-tests','/frozen-cli','perf.data','.so','.a')),'never read native or raw trace')
  if digest in byhash:b=inherited[byhash[digest]]
  elif a in parents:b=(root/a).read_bytes();need(desc(b)==parents[a],'pinned physical parent guard')
  else:
   need(a in allowed and a.startswith('target/'),'explicit accepted immutable evidence allowlist')
   b=(root/a).read_bytes()
  need(sha(b)==digest and not b.startswith((b'\x7fELF',b'!<arch>')),'exact nonnative evidence')
  row=desc(b)
  if a in parents:row['parent_file']=a
  elif digest in byhash:row['parent_alias']=byhash[digest]
  else:row['member']='objects/'+digest;objects[row['member']]=b
  need(a not in inherited or inherited[a]==b,'historical canonical source aliases remain untouched')
  need(a not in aliases or aliases[a]==row,'one immutable alias identity');aliases[a]=row;return b
 add(handoff_alias,handoff_sha);add(inventory_row['alias'],inventory_row['sha256'])
 for a,row in inventory['files'].items():need(desc(add(a,row['sha256']))==row,'all immutable owner inventory rows')
 for a,d in FROZEN.items():add(a,d)
 for absolute,digest in receipt['inputs'].items():
  if absolute in omitted:need(omitted[absolute]==digest,'recorded native input identity only');continue
  a=absolute[len(PREFIX):];add(pm['current_source_aliases'].get(a,a),digest)
 for n,digest in receipt['outputs'].items():
  a=capture_base+'/'+n
  if PREFIX+a in omitted:need(omitted[PREFIX+a]==digest,'recorded native output identity only')
  else:add(a,digest)
 review=h['root_terminal_review'];safe(review['alias'])
 need(review['alias']in inventory['files']and inventory['files'][review['alias']]['sha256']==review['sha256'],
  'root terminal review actually frozen in immutable owner inventory')
 protocol=load(add(higher['protocol_alias'],inventory['files'][higher['protocol_alias']]['sha256']))
 need(protocol['working_bits']==384 and protocol['requested_bits']==53 and protocol['source_context']['count']==210
  and protocol['source_context']['build_receipt_sha256']==BUILD and protocol['binary']['sha256']==PRODUCT,'unchanged source/build/product protocol')
 for absolute,digest in protocol['bindings'].items():need(receipt['inputs'].get(absolute)==digest,'all released protocol bindings retained by actual terminal')
 for key in ('qualifying256384_pair','independent256384'):
  roles=h[key]
  names=['report_alias']if key=='qualifying256384_pair'else['base_report_alias','history_report_alias']
  for n in names:safe(roles[n]);need(roles[n]in inventory['files'],'actual complete report must be frozen by inventory')
 out=here/'assembled';need(not out.exists(),'new target assembly only; no prior packet mutation');out.mkdir()
 own={'README.md':here/'CAPSULE_README.md','package.py':here/'package.py','check.py':here/'check.py','saved_math.py':here/'saved_math.py'}
 for name,p in own.items():shutil.copyfile(p,out/name)
 payload=out/'payload.tar.gz'
 with payload.open('wb')as stream:
  with gzip.GzipFile(fileobj=stream,filename='',mode='wb',mtime=0)as compressed:
   with tarfile.open(fileobj=compressed,mode='w')as archive:
    for name,b in sorted(objects.items()):
     row=tarfile.TarInfo(name);row.size=len(b);row.mode=0o644;row.mtime=0;archive.addfile(row,io.BytesIO(b))
 m={'schema_version':1,'status':'final_complete384_and_strict256384_saved_witness',
  'parent_manifest_sha256':PARENT_SHA,'parent_files':parents,'aliases':aliases,
  'payload_file':payload.name,'payload_members':{a:desc(b)for a,b in sorted(objects.items())},
  'owner_handoff_alias':handoff_alias,'owner_handoff_sha256':handoff_sha,
  'owner_inventory_alias':inventory_row['alias'],'owner_inventory_sha256':inventory_row['sha256'],
  'root_terminal_review':review,'omitted_native_artifacts':omitted,
  'current_source_aliases':pm['current_source_aliases'],'actual_current_build_receipt_alias':pm['actual_current_build_receipt_alias'],
  'inherited_complete256':pm['complete256'],'preserved_failed128256':pm['failed_pair'],
  'actual384':higher,'qualifying256384_pair':h['qualifying256384_pair'],'independent256384':h['independent256384'],
  'qualification':{'complete384_and_strict256384_accepted_by_owner_and_root':True,
   'full_objective_met':False,'default_Hybrid_qualified':False,'native_execution':False,
   'native_artifact_rehash':False,'new_integral_evaluation':False,'performance_qualified':False},
  'counts':{'new_aliases':len(aliases),'new_content_objects':len(objects),'parent_physical_files':len(parents),
   'actual_current_source_files':210,'historical_failed_native_captures':10,
   'source_DD_or128256_bodies_duplicated':0},
  'capsule_files':{n:desc((out/n).read_bytes())for n in list(own)+[payload.name]}}
 (out/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
 return {'manifest_sha256':sha((out/'manifest.json').read_bytes()),'payload':desc(payload.read_bytes()),'sealed':False,'counts':m['counts']}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--handoff',required=True);p.add_argument('--handoff-sha256',required=True);a=p.parse_args()
 root=Path.cwd();need(root==Path(PREFIX.rstrip('/')),'project cwd required')
 result=collect(root,Path(__file__).resolve().parent,a.handoff,a.handoff_sha256)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
