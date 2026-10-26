"""Independent capsule byte/copy audit and two stdlib saved replays; no native jobs."""
from pathlib import Path
import hashlib,io,json,shutil,subprocess,sys,tarfile
ROOT=Path.cwd();CAP=ROOT/'validation/ordinary-complex-box-correlation';HERE=ROOT/'target/ordinary-complex-box-capsule-independent-copy-review'
def sha(body):return hashlib.sha256(body).hexdigest()
def require(ok,why):
 if not ok:raise ValueError(why)
def run(command,cwd,stem):
 r=subprocess.run(command,cwd=cwd,stdin=subprocess.DEVNULL,capture_output=True,timeout=60)
 (HERE/(stem+'.stdout')).write_bytes(r.stdout);(HERE/(stem+'.stderr')).write_bytes(r.stderr)
 require(r.returncode==0,stem+' actual saved replay exited successfully')
 return json.loads(r.stdout),{'command':command,'returncode':r.returncode,'stdout_sha256':sha(r.stdout),'stderr_sha256':sha(r.stderr)}
manifest_bytes=(CAP/'manifest.json').read_bytes();m=json.loads(manifest_bytes)
require(sha(manifest_bytes)=='aec684253e59a73944b1e5a8e58c6b385bf9a81d5acf17f81643f6eec3aed2e0','exact frozen final capsule')
for name,desc in m['capsule_files'].items():
 b=(CAP/name).read_bytes();require(len(b)==desc['bytes']and sha(b)==desc['sha256'],'capsule file '+name)
objects={}
with tarfile.open(fileobj=io.BytesIO((CAP/'payload.tar.gz').read_bytes()),mode='r:gz')as ar:
 for member in ar:
  require(member.isfile()and member.name not in objects,'unique regular content-addressed member')
  b=ar.extractfile(member).read();desc=m['payload_members'][member.name]
  require(len(b)==desc['bytes']and sha(b)==desc['sha256']and member.name=='objects/'+sha(b),'exact object '+member.name)
  objects[member.name]=b
require(set(objects)==set(m['payload_members']),'closed content-addressed payload')
for alias,desc in m['aliases'].items():
 b=objects[desc['member']];require(sha(b)==desc['sha256']and len(b)==desc['bytes'],'exact canonical alias '+alias)
expected_files=set(m['capsule_files'])|{'manifest.json'}
require(expected_files=={'manifest.json','payload.tar.gz','README.md','check.py','package.py'},'exact five-file portable capsule')
default,first=run([sys.executable,'-I','-S',str(CAP/'check.py')],ROOT,'default')
mini=HERE/'minimal-checkout';mini.mkdir();dest=mini/m['capsule_directory'];dest.mkdir(parents=True)
for name in expected_files:shutil.copyfile(CAP/name,dest/name)
minimal,second=run([sys.executable,'-I','-S',str(dest/'check.py')],mini,'minimal')
require(default==minimal,'default and isolated fresh-root saved replays identical')
require(default['status']=='passed_portable_ordinary_box_and_E6_convergence_saved_evidence','all replayed gates successful')
for field,value in {'strict_regressions':10,'copied_input_components':22,'raw_D0_coefficients_against_anchor':6,'raw_rule_pairs':4,'native_and_raw_complex_pole_controls':12,'old_E6_kernel_returned_success':False,'new_E6_kernel_returned_success':True,'old_E6_D0_rows':1240,'new_E6_D0_rows':600,'new_E6_orders':[8,16,32,64],'identical_old_new_D0_input_components':13200,'unchanged_finite_D0_records':480,'changed_finite_D0_records':120,'E6_or_parent_tensor_qualified':False,'new_Dual_domain_qualified':False,'native_or_generated_backend_qualified':False,'Float256_accuracy_certified':False,'quadrature_error_bound_certified':False,'performance_qualified':False,'compiler_or_integral_producer_or_live_process_probe_executed':False}.items():require(default[field]==value,'honest saved scope '+field)
report={'status':'passed_independent_capsule_copy_and_minimal_stdlib_replay','reviewer':'/root/highpoint_generalized_research','manifest_sha256':sha(manifest_bytes),'capsule_files':5,'archived_aliases':len(m['aliases']),'unique_content_addressed_bodies':len(objects),'omitted_compiled_identities':len(m['omitted_native_artifacts']),'commands':[first,second],'replayed_result':default,'source_review':'Checker executes preserved stdlib saved arithmetic/parser functions in a disposable tree; independent checker top-level path assumptions are explicitly replaced by unchanged pure helper AST nodes, retaining original full program and failed packaging context. No controllers/native artifacts/compilers/process probes run. Exact test footers and actual artifact hashes are historical receipt evidence only.','scope':'one ordinary Symbolica D0 correlation repair, independently anchored copied point, and actual E6 convergence; parent tensors/seededDual/native/performance outside scope','source_sha256':sha(Path(__file__).read_bytes())}
(HERE/'review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'review_sha256':sha((HERE/'review.json').read_bytes()),'manifest_sha256':report['manifest_sha256']}))
