"""Independent two-level capsule byte/copy review; Python saved replay only."""
from pathlib import Path
import hashlib,io,json,shutil,subprocess,sys,tarfile
ROOT=Path.cwd();CAP=ROOT/'validation/ordinary-gh-n6-generalized-requalification';PAR=ROOT/'validation/ordinary-complex-box-correlation';HERE=ROOT/'target/ordinary-gh-n6-parent-capsule-independent-copy-review'
def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,why):
 if not ok:raise ValueError(why)
def objects(cap,m):
 for n,d in m['capsule_files'].items():
  b=(cap/n).read_bytes();require(sha(b)==d['sha256']and len(b)==d['bytes'],'exact capsule file '+n)
 result={}
 with tarfile.open(fileobj=io.BytesIO((cap/'payload.tar.gz').read_bytes()),mode='r:gz')as ar:
  for item in ar:
   require(item.isfile()and item.name not in result,'unique regular object')
   b=ar.extractfile(item).read();d=m['payload_members'][item.name]
   require(sha(b)==d['sha256']and len(b)==d['bytes']and item.name=='objects/'+sha(b),'exact addressed object')
   result[item.name]=b
 require(set(result)==set(m['payload_members']),'closed payload')
 return result
def run(command,cwd,stem):
 r=subprocess.run(command,cwd=cwd,stdin=subprocess.DEVNULL,capture_output=True,timeout=60)
 (HERE/(stem+'.stdout')).write_bytes(r.stdout);(HERE/(stem+'.stderr')).write_bytes(r.stderr)
 require(r.returncode==0,stem+' saved replay success')
 return json.loads(r.stdout),{'command':command,'returncode':r.returncode,'stdout_sha256':sha(r.stdout),'stderr_sha256':sha(r.stderr)}
m=json.loads((CAP/'manifest.json').read_bytes());pm=json.loads((PAR/'manifest.json').read_bytes())
require(sha((CAP/'manifest.json').read_bytes())=='185b93721a909f94585f9fa0ce2d832bd57c116008d4d5d8eaad010b29c18aa7','exact final parent capsule')
require(sha((PAR/'manifest.json').read_bytes())==m['parent_manifest_sha256']=='aec684253e59a73944b1e5a8e58c6b385bf9a81d5acf17f81643f6eec3aed2e0','exact sole scalar parent')
pobjs=objects(PAR,pm);objs=objects(CAP,m);files={}
for alias,d in pm['aliases'].items():
 b=pobjs[d['member']];require(sha(b)==d['sha256']and len(b)==d['bytes'],'exact scalar alias');files[alias]=b
for name in set(pm['capsule_files'])|{'manifest.json'}:files[pm['capsule_directory']+'/'+name]=(PAR/name).read_bytes()
for alias,d in m['aliases'].items():
 require(len(set(d)&{'member','parent_alias'})==1,'one alias selector')
 b=objs[d['member']]if'member'in d else files[d['parent_alias']]
 require(sha(b)==d['sha256']and len(b)==d['bytes'],'exact child alias')
 require(alias not in files or files[alias]==b,'no overwritten scalar-parent bytes');files[alias]=b
built=json.loads(files['target/ordinary-gh-parent-requalification/build-001/receipt.json'])
require(built['status']=='passed'and built['inputs_unchanged']and built['cleanup_errors']==[],'actual compiled context receipt')
require(len(m['fresh_source_aliases'])==len(built['source_files'])==128,'full128actualsource map')
for canonical,alias in m['fresh_source_aliases'].items():require(sha(files[alias])==built['source_files'][canonical],'exact compiled source '+canonical)
old='target/affine-power-post-memo-current-d2-pair/captures/Float256-001/'
oldr=json.loads(files[old+'receipt.json']);oldd=json.loads(files[old+'stdout.json'])
require(oldr['status']=='failed_or_incomplete'and oldd['samples'][0]['status']=='failed'and'moments'not in oldd['samples'][0],'old D2 failure retained without arrays')
require(m['prior_failed_Float256_reference']['manifest_sha256']=='82e48ff83b92ec0f2193e5125d9b37e95f97adabfeb1db6607e205ff21c15a68','old first-dot failure capsule retained separately')
default,first=run([sys.executable,'-I','-S',str(CAP/'check.py')],ROOT,'default')
mini=HERE/'minimal-checkout';mini.mkdir()
for cap,manifest in [(PAR,pm),(CAP,m)]:
 dest=mini/manifest['capsule_directory'];dest.mkdir(parents=True)
 for name in set(manifest['capsule_files'])|{'manifest.json'}:shutil.copyfile(cap/name,dest/name)
require(len([p for p in mini.rglob('*')if p.is_file()])==10,'exact ten-file isolated physical closure')
minimal,second=run([sys.executable,'-I','-S',str(mini/m['capsule_directory']/'check.py')],mini,'minimal')
require(default==minimal,'identical default and fresh-root saved result')
require(default['status']=='passed_portable_saved_generalized_N6_integrity_replay','saved math/metadata integrity success')
require(set(default['cases'])=={'first_dot','D2'}and all(r['qualified']and r['reference_slots_each_precision']==840 and r['cross_source_slots']==840 for r in default['cases'].values()),'both fixed families fully qualified at existing thresholds')
for key in ['same_source_precision_convergence_qualified','full_domain_qualified','native_backend_qualified','performance_qualified','D6_qualified','compiler_or_integral_producer_or_live_process_probe_executed']:require(default[key]is False,'honest scope '+key)
require(default['fresh_source_bodies']==128 and default['old_D2_Float256_failure_preserved']is True,'shared source and failure integrity')
review={'status':'passed_independent_parent_capsule_copy_and_ten_file_stdlib_replay','reviewer':'/root/highpoint_generalized_research','manifest_sha256':sha((CAP/'manifest.json').read_bytes()),'parent_manifest_sha256':sha((PAR/'manifest.json').read_bytes()),'own_aliases':len(m['aliases']),'own_objects':len(objs),'shared_compiled_source_bodies':128,'minimal_physical_files':10,'commands':[first,second],'replayed_result':default,'source_review':'Metadata-only D2 absolute-request SHA lookup maps to the exact restored request bytes and restored cwd. Numerical comparator bodies/raw data are unchanged; independent full Fraction API is replayed with two owner-added provenance fields separately verified. No controller, compiler, native integral or live-process probe is run.','same_source_precision_convergence_qualified':False,'D6_qualified':False,'performance_qualified':False,'review_source_sha256':sha(Path(__file__).read_bytes())}
(HERE/'review.json').write_text(json.dumps(review,indent=2)+'\n');print(json.dumps({'status':review['status'],'review_sha256':sha((HERE/'review.json').read_bytes()),'manifest_sha256':review['manifest_sha256']}))
