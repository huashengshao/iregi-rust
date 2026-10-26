"""Saved-only additive D6 CROSS_SOURCE requalification; never runs a native evaluator."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,importlib.util,json,re,sys,tarfile,io
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PREFIX='/shared/external/iregi/iregi-rust/'
DD='validation/affine-power-generalized-current-d6-rank6'
DD_SHA='1b2c3b5067df042858ba1fb62c3163c6318f2ff915b19c876720763123253195'
COMMON='validation/ordinary-gh-n6-generalized-requalification'
PRIVATE='target/ordinary-gh-d6-parent-requalification'
CAPTURE=PRIVATE+'/captures/D6-Float256-001'
LOW='target/affine-power-post-memo-current-d6/captures/Float128-001/stdout.json'
ESTIMATES='target/n6-d6-full-rank6-dd-oracle-proposal/numeric-001/data/estimates.json'

def need(value,reason):
 if not value:raise ValueError(reason)
def sha(body):return hashlib.sha256(body).hexdigest()
def desc(body):return dict(sha256=sha(body),bytes=len(body))
def load(body):
 def unique(items):
  out={}
  for k,v in items:need(k not in out,'duplicate JSON key');out[k]=v
  return out
 return json.loads(body,object_pairs_hook=unique)
def safe(name):
 p=PurePosixPath(name);need(name and str(p)==name and not p.is_absolute() and '..'not in p.parts,'safe relative alias')
def imported(path,label):
 s=importlib.util.spec_from_file_location(label,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def parent_files(m):
 for alias,row in m['parent_files'].items():safe(alias);need(desc((ROOT/alias).read_bytes())==row,'physical parent identity')
 result={};helpers={}
 for directory,pin in [(DD,DD_SHA),(COMMON,m['common_parent_sha256'])]:
  body=(ROOT/directory/'manifest.json').read_bytes();need(sha(body)==pin,'frozen parent identity')
  helper=imported(ROOT/directory/'check.py','_D6_cross_parent_'+str(len(helpers)));helpers[directory]=helper
  restored=helper.restore_files(load(body))
  for alias,data in restored.items():need(alias not in result or result[alias]==data,'exact inherited alias collision');result[alias]=data
  parent=load(body)
  for name in ['manifest.json',*parent['capsule_files']]:result[directory+'/'+name]=(ROOT/directory/name).read_bytes()
 return result,helpers

def restore_files(m):
 need({str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and '__pycache__'not in p.parts}==set(m['capsule_files'])|{'manifest.json'},'closed own inventory')
 for name,row in m['capsule_files'].items():safe(name);need(desc((HERE/name).read_bytes())==row,'own byte identity')
 result,_=parent_files(m);members={}
 with tarfile.open(fileobj=io.BytesIO((HERE/'payload.tar.gz').read_bytes()),mode='r:gz')as archive:
  for item in archive:
   safe(item.name);need(item.isfile()and item.name not in members,'unique regular payload object')
   body=archive.extractfile(item).read();need(not body.startswith((b'\x7fELF',b'!<arch>'))and b'S-130-'not in body,'no native/credential payload');need(desc(body)==m['payload_members'].get(item.name),'payload byte identity');members[item.name]=body
 need(set(members)==set(m['payload_members']),'complete payload inventory')
 for alias,row in m['aliases'].items():
  safe(alias);need(len(set(row)&{'parent_alias','member'})==1,'one exact byte selector')
  body=result[row['parent_alias']]if'parent_alias'in row else members[row['member']]
  need(desc(body)=={k:row[k]for k in ['sha256','bytes']},'selected byte identity');need(alias not in result or result[alias]==body,'no inherited overwrite');result[alias]=body
 return result

def replay(m,files):
 need(m['cross_source_qualified']is True and m['same_source_precision_convergence_qualified']is False,'only actual admitted CROSS_SOURCE result')
 independent=load(files[m['independent_audit']])
 need(sha(files[m['independent_audit']])=='717de82e67a7f6ff40f7720014cf736cc416b510c5612504528221d0bbbfe8ef' and independent['status']=='passed_independent_saved_D6_current256_canonical_and_CROSS_SOURCE_audit' and independent['total_complex_gates']==5332 and not independent['failures'],'preserved independent complete5332-gate audit')
 need(sha(files[PRIVATE+'/independent_saved_check.py'])=='7d79275f158f900d5e838589ee2d96c5b2c9fa9bc756d383476a734c407e1d8d','frozen independent audit source; historical ELF rehash is not repeated')
 receipt=load(files[CAPTURE+'/receipt.json']);protocol=load(files[PRIVATE+'/protocol.json'])
 need(receipt['status']=='passed_current256_canonical_and_CROSS_SOURCE_840_pairs'and receipt['inputs_unchanged']is True and not receipt['cleanup_errors'],'terminal current256 actual source/cleanup guards')
 need(receipt['same_source_precision_convergence_qualified']is False,'actual controller retains source distinction')
 for absolute,digest in receipt['inputs'].items():
  alias=m['receipt_input_aliases'][absolute]
  if alias is None:need(m['omitted_native_inputs'].get(absolute)==digest,'explicit omitted native hash')
  else:need(sha(files[alias])==digest,'exact guarded actual input')
 for name,digest in receipt['outputs'].items():need(sha(files[CAPTURE+'/'+name])==digest,'actual saved output hash')
 for name,digest in protocol['fresh_source_files'].items():
  alias=protocol['fresh_source_root']+'/'+name
  need(sha(files[alias])==digest and 'parent_alias'in m['aliases'][alias],'all128 actual current sources inherited without duplicate archive')
 _,helpers=parent_files(m);adapter=helpers[DD]
 snapshot=CAPTURE+'/controller-snapshot/'
 for name,pin in [('compare_saved.py','4518cbfa8b68398f0efaab44506d787f72e14e36cb607f67b6e0d5f026332296'),('compare_pair.py','00095f97a7b0a0e78396c37f937b25d587da35e40a2dfd775727f04ea7c33c1a')]:need(sha(files[snapshot+name])==pin,'unchanged actual snapshot comparator')
 with adapter.saved_filesystem(files):
  comparator=imported(Path(PREFIX+snapshot+'compare_saved.py'),'_saved_cross_D6_canonical')
  pair=imported(Path(PREFIX+snapshot+'compare_pair.py'),'_saved_cross_D6_pair')
  sample=comparator.read(PREFIX+PRIVATE+'/input.json')
  low=comparator.audit(PREFIX+LOW,PREFIX+ESTIMATES,sample,128)
  high=comparator.audit(PREFIX+CAPTURE+'/stdout.json',PREFIX+ESTIMATES,sample,256)
  paired=pair.audit_pair(PREFIX+LOW,PREFIX+CAPTURE+'/stdout.json',sample)
 need(low==load(files[CAPTURE+'/prior128-canonical-comparison.json'])and high==load(files[CAPTURE+'/comparison.json']),'entire both840x2 canonical reports replayed exactly')
 need(paired==load(files[CAPTURE+'/pair-raw.json'])and paired['pair_gates']==840 and not paired['failures'],'entire strict840 CROSS_SOURCE pairs replayed exactly')
 need(paired['pair_source_relationship']=='historical_native128_vs_current_native256_CROSS_SOURCE'and paired['same_source_precision_convergence_qualified']is False,'different source builds never labeled same-source convergence')
 cross=dict(paired);cross.update(raw_comparator_status=paired['status'],status='passed_complete_840_CROSS_SOURCE_pairs',comparison_scope='CROSS-SOURCE old Float128 versus current Float256',same_source_precision_convergence_qualified=False,current_build_receipt_sha256=protocol['build_receipt']['sha256'],prior_source_provenance=protocol['prior_source_provenance'],scope='One fixed request; strict2^-80 agreement across different source builds. No same-source convergence or full-domain claim.')
 need(cross==load(files[CAPTURE+'/cross-source-comparison.json']),'explicit source-aware interpretation preserved exactly')
 need(not low['failures']and not high['failures']and low['degree6_UV_slots_retained']==high['degree6_UV_slots_retained']==84,'all raw degree6UV coefficients retained')
 return dict(status='passed_saved_current256_D6_canonical_and840_CROSS_SOURCE_pairs',canonical_slots_per_output_per_rule=840,actual_current_source_bodies=128,
  saved_independent_complex_gates=5332,historical_independent_audit_preserved=True,full_independent_binary_rehash_repeated=False,
  current256_canonical_maxima=high['maximum_normalized_errors'],old128_canonical_maxima=low['maximum_normalized_errors'],
  strict_CROSS_SOURCE_pairs=840,strict_pair_maximum=paired['maximum_normalized_error'],same_source_precision_convergence_qualified=False,
  genuine_even_UV_slots_each=20,degree6_UV_slots_retained_each=84,original_finite_reference_used_as_gate=False,
  rigorous_quadrature_accuracy_qualified=False,public_Dual_qualified=False,performance_qualified=False,native_execution=False)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output');a=p.parse_args();m=load((HERE/'manifest.json').read_bytes());r=replay(m,restore_files(m))
 if a.output:Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2))
if __name__=='__main__':main()
