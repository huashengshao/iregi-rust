"""Collect terminal128/256 saved evidence; retain the FAILED strict precision gate."""
from pathlib import Path,PurePosixPath
import argparse,gzip,hashlib,io,json,runpy,shutil,sys,tarfile
sys.dont_write_bytecode=True
ROOT=Path.cwd(); HERE=Path(__file__).resolve().parent
DEST=ROOT/'validation/e6-dual-rank6-precision-boundary'
PARENT='validation/e6-dual-restored-zero-profile-core-tests'
PREFIX='/shared/external/iregi/iregi-rust/'
RAW128='target/e6-dual-restored-zero-profile-opt3-128-192g'
RAW256='target/e6-dual-restored-zero-profile-opt3-256-256g'
RAW384='target/e6-dual-restored-zero-profile-opt3-384-256g'
INVENTORIES={
 'target/e6-dual-final-immutable128-inventory.json':'ce5e593bbdef2aac4d89cee3aff8e7006105b8da1cda6a7d2ee0698357d2aac5',
 'target/e6-dual-immutable256-boundary-inventory.json':'358dfeb47bfefcae11b7b6d6843b70792c63a0d1d6911b5e665aacf87940ec6c'}
def need(v,m):
 if not v:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'sha256':sha(b),'bytes':len(b)}
def safe(a):
 need(type(a)is str and bool(a)and '\0'not in a,'string alias')
 p=PurePosixPath(a)
 need(str(p)==a and not p.is_absolute()and '..'not in p.parts,'canonical relative alias')
 need(a!=RAW384 and not a.startswith(RAW384+'/'),'active384 producer is wholly excluded')
need(ROOT==Path(PREFIX.rstrip('/')),'project cwd required')
need(HERE==ROOT/'target/e6-dual-rank6-precision-boundary-capsule','target-only builder')
pb=(ROOT/PARENT/'manifest.json').read_bytes()
need(sha(pb)=='1f1a41fdbc30ca1b3d5a18ce59db9f23fa0bb774950dba464aadfd05aabc5d04','current source parent')
pm=json.loads(pb)
loader=runpy.run_path(str(ROOT/PARENT/'check.py'),run_name='boundary_parent_loader')
inherited=loader['restore_files'](pm)
parents=dict(pm['parent_files'])
for n in list(pm['capsule_files'])+['manifest.json']:
 a=PARENT+'/'+n;safe(a);parents[a]=desc((ROOT/a).read_bytes())
byhash={}
for a,b in inherited.items():byhash.setdefault(sha(b),a)
objects={};aliases={}
def add(a,expected):
 safe(a)
 need(not a.endswith(('/frozen-tests','/frozen-cli','perf.data','.so','.a')),'native/trace reads prohibited')
 if expected in byhash:b=inherited[byhash[expected]]
 elif a in parents:b=(ROOT/a).read_bytes();need(desc(b)==parents[a],'pinned physical parent')
 elif a in inherited and sha(inherited[a])==expected:b=inherited[a]
 else:
  need(a.startswith(('target/','dependencies/')),'new evidence source allowlist')
  b=(ROOT/a).read_bytes()
 need(sha(b)==expected and not b.startswith((b'\x7fELF',b'!<arch>')),'exact nonnative evidence '+a)
 row=desc(b)
 if a in parents:row['parent_file']=a
 elif expected in byhash:row['parent_alias']=byhash[expected]
 else:row['member']='objects/'+expected;objects[row['member']]=b
 need(a not in inherited or inherited[a]==b,'no historical canonical alias replacement')
 need(a not in aliases or aliases[a]==row,'one immutable alias identity')
 aliases[a]=row;return b
inventory_data={}
for a,digest in INVENTORIES.items():
 data=json.loads(add(a,digest));inventory_data[a]=data
 for name,row in data['files'].items():need(desc(add(name,row['sha256']))==row,'immutable owner inventory row')
add('target/n6-sample-d6-mass-second-anchor-dd/compare_saved_precision.py','a82bdfa56762dee1002f8504bad38d75a806b45ac920aa230d105609761e1963')
add('target/e6-dual-full-rank6-mass-second-support-source-bindings.json','8e0cd12e11578b639f62ceb93b4d16c9f9d4608f10e5420b378df279b5def396')
omitted=dict(pm['omitted_native_artifacts'])
for data in inventory_data.values():
 native=data.get('actual_owned_native_binary_hash_only',data.get('native_binary_hash_only'))
 omitted[PREFIX+native['path']]=native['sha256']
for raw in (RAW128,RAW256):
 bits=128 if raw==RAW128 else 256
 receipt=json.loads((ROOT/(raw+f'/capture-Float{bits}-001/receipt.json')).read_bytes())
 for absolute,digest in receipt['inputs'].items():
  if absolute in omitted:need(omitted[absolute]==digest,'omitted native guard');continue
  need(absolute.startswith(PREFIX),'project-local input guard')
  a=absolute[len(PREFIX):];a=pm['current_source_aliases'].get(a,a);add(a,digest)
 base=raw+'/capture-Float'+('128'if raw==RAW128 else'256')+'-001/'
 for name,digest in receipt['outputs'].items():
  a=base+name
  if PREFIX+a in omitted:need(omitted[PREFIX+a]==digest,'omitted native output')
  else:add(a,digest)
# The diagnosis inspected one extra dependency file; it is not a full dependency closure.
diagroot='target/e6-dual-first-pair-precision-diagnosis'
pins=json.loads((ROOT/diagroot/'pins.json').read_bytes())
source_reads=dict(pm['current_source_aliases'])
for canonical,digest in pins['build_selected_sources'].items():
 a=pm['current_source_aliases'][canonical]
 need(sha(inherited[a])==digest,'diagnosis selected actual source epoch')
 add(a,digest)
for canonical,digest in pins['dependency_inspection_only_sources'].items():
 if digest in byhash:
  a=byhash[digest]
 else:
  safe(canonical);b=(ROOT/canonical).read_bytes();need(sha(b)==digest,'pinned inspection-only dependency')
  a='target/e6-dual-rank6-precision-boundary-capsule/inspection-snapshot/'+canonical
  member='objects/'+digest;objects[member]=b;aliases[a]=dict(desc(b),member=member)
 source_reads[canonical]=a
payload=HERE/'payload.tar.gz'
with payload.open('wb')as stream:
 with gzip.GzipFile(fileobj=stream,filename='',mode='wb',mtime=0)as compressed:
  with tarfile.open(fileobj=compressed,mode='w')as archive:
   for name,b in sorted(objects.items()):
    row=tarfile.TarInfo(name);row.size=len(b);row.mode=0o644;row.mtime=0;archive.addfile(row,io.BytesIO(b))
def case(raw,bits,mechanism,numeric):
 return {'receipt_alias':raw+f'/capture-Float{bits}-001/receipt.json','protocol_alias':raw+'/protocol.json',
  'capture_alias':raw+f'/capture-Float{bits}-001/capture.json','mechanism_alias':raw+'/'+mechanism,
  'numeric_alias':raw+'/'+numeric,'checker_source_alias':('target/e6-dual-restored-profile-saved-schema-correction/check_saved_mechanism.py'if bits==128 else raw+'/check_saved_mechanism.py'),
  'root_review_alias':raw+'/root-terminal-review.json','accepted_by_owner_and_root':True}
m={'schema_version':1,'status':'sealed_saved_precision_boundary_with_failed128256_gate',
 'parent_manifest_sha256':sha(pb),'parent_files':parents,'aliases':aliases,'payload_file':payload.name,
 'payload_members':{a:desc(b)for a,b in sorted(objects.items())},'omitted_native_artifacts':omitted,
 'current_source_aliases':pm['current_source_aliases'],'source_read_aliases':source_reads,
 'actual_current_build_receipt_alias':pm['build_roles']['current'],'owner_inventories':INVENTORIES,
 'complete128':case(RAW128,128,'mechanism-audit-schema-corrected.json','numeric-agreement-128-vs-both-DD.json'),
 'complete256':case(RAW256,256,'mechanism-audit.json','numeric-agreement-256-vs-both-DD.json'),
 'failed_pair':{'report_alias':'target/e6-dual-restored-zero-profile-opt3-128-256-joint-comparison.json',
  'strict_threshold':'2^-80','strict_failures':628,'qualified':False},
 'independent_full_pair':{'source_alias':'target/rank6-independent-complete-pair-review.py',
  'source_sha256':'a6e79be973f31ff0e47978d333c74996470392c66db453343e9625d1a9317e1b',
  'report_alias':'target/rank6-independent-complete128256-review.json'},
 'diagnosis':{'source_alias':diagroot+'/analyze.py','source_sha256':'f606bd00a2695c4f71124ec6cc91bf4114b9c3c286c3375587e1513823635516',
  'report_alias':diagroot+'/analysis.json','pins_alias':diagroot+'/pins.json','rigorous_error_bound':False},
 'qualification':{'complete128_mechanism_and_DD_qualified':True,'complete256_mechanism_and_DD_qualified':True,
  'strict_precision_pair_qualified':False,'default_Hybrid_qualified':False,'full_objective_met':False,
  'native_execution':False,'native_artifact_rehash':False,'new_integral_evaluation':False,'performance_qualified':False,
  'rigorous_error_bound':False,'achieved_precision_bits_claimed':False,'actual384':None},
 'counts':{'owner_inventory_files':sum(len(d['files'])for d in inventory_data.values()),'new_aliases':len(aliases),
  'new_content_objects':len(objects),'parent_physical_files':len(parents),'new_unique_raw_bytes':sum(map(len,objects.values())),
  'actual_current_source_files':len(pm['current_source_aliases']),'historical_failed_native_captures':10,
  'strict_failure_is_additional_native_failure':False,'source_and_DD_bodies_duplicated':0},
 'capsule_files':{n:desc((HERE/n).read_bytes())for n in ['README.md','package.py','check.py','saved_math.py',payload.name]}}
(HERE/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--seal',action='store_true');a=p.parse_args()
if a.seal:
 need(not DEST.exists(),'new capsule path only; no sealed capsule mutation')
 DEST.mkdir()
 for name in list(m['capsule_files'])+['manifest.json']:shutil.copyfile(HERE/name,DEST/name)
print(json.dumps({'manifest_sha256':sha((HERE/'manifest.json').read_bytes()),'payload':desc(payload.read_bytes()),
 'counts':m['counts'],'sealed':a.seal,'full_objective_met':False,'strict_precision_pair_qualified':False},indent=2))
