"""Saved-only CLI/physical replay. No compiler, native host or integral."""
from pathlib import Path
from fractions import Fraction
import ast,hashlib,io,json,math,re,tarfile
HERE=Path(__file__).resolve().parent;checks=0
ROOT_PREFIX='/shared/external/iregi/iregi-rust/'
def require(condition,reason):
 global checks
 checks+=1
 if not condition:raise ValueError(reason)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(b):return json.loads(b)
def unpack(path,descriptor):
 data=path.read_bytes();require(sha(data)==descriptor['sha256'] and len(data)==descriptor['bytes'],'archive binding')
 result={}
 with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tar:
  for m in tar:
   require(m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts and m.name not in result,'safe regular member')
   body=tar.extractfile(m).read();require(not body.startswith((b'\x7fELF',b'!<arch>')),'excluded native binary payload')
   require(m.name in descriptor['members'],'declared member');d=descriptor['members'][m.name]
   require(sha(body)==d['sha256'] and len(body)==d['bytes'],'member binding');result[m.name]=body
 require(set(result)==set(descriptor['members']),'exact member inventory');return result

def definitions(body,names,globals):
 tree=ast.parse(body);nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.Assign)) and ((isinstance(n,ast.FunctionDef) and n.name in names) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in n.targets)))]
 require(len(nodes)==len(names),'exact saved helper definitions')
 exec(compile(ast.Module(body=nodes,type_ignores=[]),'<saved helper definitions>','exec',optimize=0),globals)
 return globals

def main(save=False):
 manifest=read((HERE/'manifest.json').read_bytes());require(sha((HERE/'check.py').read_bytes())==manifest['checker_sha256'],'checker binding')
 src=unpack(HERE/'sources.tar.gz',manifest['sources']);data=unpack(HERE/'evidence.tar.gz',manifest['evidence'])
 parent_path=HERE/manifest['inherits']['manifest'];require(sha(parent_path.read_bytes())==manifest['inherits']['manifest_sha256'],'parent manifest binding')
 parent=read(parent_path.read_bytes());require(parent['source_context_sha256']==manifest['inherits']['source_context_sha256'],'same actual build source context')
 require(parent['cli_binary_product']==manifest['cli_product'] and parent['cli_test_product']==manifest['cli_test_product'],'same actual owned CLI/test products')
 parent_data=unpack(parent_path.parent/'evidence.tar.gz',parent['evidence'])
 require(parent['sources']['sha256']==manifest['inherits']['source_archive_sha256'] and parent['evidence']['sha256']==manifest['inherits']['evidence_archive_sha256'],'inherited archive identities')
 parent_src=unpack(parent_path.parent/'sources.tar.gz',parent['sources'])
 context=read(parent_data['context.json']);require(sha(parent_data['context.json'])==manifest['inherits']['source_context_sha256'],'actual parent source freeze')
 for path,digest in context['inputs'].items():
  rel=path.removeprefix(ROOT_PREFIX);require(rel in parent_src and sha(parent_src[rel])==digest,'inherited selected source body')
 def receipt(path,status):
  r=read(data[path]);require(r['status']==status and not r['cleanup_errors'] and r['inputs_unchanged'],'actual saved process receipt')
  for name,digest in r['inputs'].items():
   rel=name.removeprefix(ROOT_PREFIX)
   if rel in manifest['binary_relationships']:require(manifest['binary_relationships'][rel]==digest,'excluded binary identity')
   else:require(rel in src and sha(src[rel])==digest,'saved guarded source/input')
  for step in r['steps']:require(step['owned_group_gone'],'saved owned process cleanup')
  return r
 cli=receipt('root-frontend-check/cli-tests-current-004/receipt.json','passed')
 listing=data['root-frontend-check/cli-tests-current-004/step-0.log'].decode();log=data['root-frontend-check/cli-tests-current-004/step-1.log'].decode()
 names=[s[:-6] for s in listing.splitlines() if s.endswith(': test')];require(names==cli['selected_tests'] and len(set(names))==14,'fourteen exact listed cases')
 require(all('test '+name+' ...' in log for name in names),'each actual CLI test ran')
 require(re.search(r'^test result: ok\. 14 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;',log,re.M),'strict CLI pass summary')
 require(all(s['returncode']==0 and s['status']=='exited' for s in cli['steps']),'CLI actual success')
 initial=receipt('current-physical-20261026/qualification-001/receipt.json','failed')
 hi256=receipt('current-physical-20261026/gghhh-256-001/receipt.json','passed');hi384=receipt('current-physical-20261026/gghhh-384-001/receipt.json','passed')
 require(len(initial['steps'])==4 and initial['steps'][-1]['returncode']==1,'initial controller failed at actual pentagon128')
 require(all(s['returncode']==0 for s in initial['steps'][:3]),'box and first pair succeeded before failure')
 for r in (initial,hi256,hi384):require(r['source_context_sha256']==manifest['inherits']['source_context_sha256'],'physical CLI uses same actual source context')
 binary_names={'target/python-current-qualification-retry/cli-binary-001/owned-iregi-rust':manifest['cli_product']['sha256'],'target/python-current-qualification-retry/build-001/owned-cli-tests':manifest['cli_test_product']['sha256']}
 for n,d in binary_names.items():require(manifest['binary_relationships'][n]==d,'actual binary to source relationship')
 namespace=definitions(src['validation/physical/compare_cli.py'],{'CASES','number','pair','normalized_error','kinematic_scale','one_loop_slots','compare_tensors','compare_physical'},{'math':math})
 pair_ns=definitions(src['target/current-cli-physical-capsule/tight-pairs.py'],{'number','pair','serial','compare'},{'Fraction':Fraction})
 cases=[];tensor_checks=0;physical_checks=0
 paths=[('gghh',128,'qualification-001'),('gghh',256,'qualification-001'),('gghhh',256,'gghhh-256-001'),('gghhh',384,'gghhh-384-001')]
 runs={}
 for case,bits,folder in paths:
  stem=f'current-physical-20261026/{folder}/{case}-{bits}'
  report=read(data[stem+'.json']);run=read(data[stem+'.cli.json']);oracle=read(data[stem+'.oracle.json']);runs[(case,bits)]=run
  sample=read(src[f'validation/physical/{case}-cli-input.json']);madloop=read(src[f'validation/physical/madloop/fixtures/{case}-helicity-1.json'])
  require(report['passed'] and report['cli_status']=={'status':'success','executed':True,'returncode':0},'actual physical graph success')
  require(run['precision_bits']==bits and report['requested_accuracy_bits']==53,'unchanged working/requested precision')
  require(report['provenance']['cli_sha256']==manifest['cli_product']['sha256'],'actual owned CLI provenance')
  for key,path in [('input_sha256',f'validation/physical/{case}-cli-input.json'),('madloop_fixture_sha256',f'validation/physical/madloop/fixtures/{case}-helicity-1.json'),('graph_sha256',f'examples/graphs/{namespace["CASES"][case][0]}.dot'),('model_sha256','fixtures/models/sm.json'),('script_sha256','validation/physical/compare_cli.py')]:require(report['provenance'][key]==sha(src[path]),'physical source/data binding')
  require(run['graph']['name']==namespace['CASES'][case][0] and run['samples'][0]['id']==sample['id'],'actual graph/sample correspondence')
  require(run['settings']['rank']==4 and len(run['basis'])==70 and len(run['samples'][0]['moments'])==70,'complete rank4 array')
  modes=[0,1,2] if case=='gghh' else [1,2];require([x['mode'] for x in oracle]==modes,'explicit original IREGI mode coverage')
  maxima=[]
  for record in oracle:
   require(record['returncode']==0 and len(record['results'])==1 and record['results'][0]['stable'],'successful original reference array')
   r=namespace['compare_tensors'](run,sample,record['results'][0],1e-10)
   require(r['passed'] and r['moments']==70 and r['slots_per_moment']==4,'replayed every original reference tensor slot')
   tensor_checks+=280;maxima.append(r['max_normalized_error'])
  physical=namespace['compare_physical'](run,sample,madloop,namespace['CASES'][case],1e-10)
  require(physical['passed'],'replayed graph-isolated MadLoop comparison');physical_checks+=3
  require(physical['excludes']==['R2','UV counterterms'] and physical['includes']==['bare UV and IR poles','R1'],'physical contribution scope')
  cases.append({'case':case,'working_bits':bits,'propagators':run['settings']['propagators'],'rank':4,'tensor_moments':70,'complex_slots_per_reference':280,'original_modes':modes,'tensor_max_normalized_errors':maxima,'madloop_errors':physical['errors'],'madloop_group':physical['group'],'graph_factor':physical['factor'],'algorithm_requested':report['algorithm_requested'],'algorithm_used':report['algorithm_used']})
 bad='current-physical-20261026/qualification-001/gghhh-128'
 failed_report=read(data[bad+'.json']);failed_run=read(data[bad+'.cli.json']);lane=failed_run['samples'][0]
 require(not failed_report['passed'] and lane['status']=='failed' and 'pv_node_852' in lane['reason'],'actual retained conservative precision guard')
 require('moments' not in lane and 'integral' not in lane and not read(data[bad+'.oracle.json']),'failed128 has no successful zero array or new reference evaluations')
 require(failed_report['tensor_comparisons']==[] and failed_report['physical_comparison']['status']=='not_run','failed physical comparisons remain not run')
 pairs=[]
 for case,lo,hi in [('gghh',128,256),('gghhh',256,384)]:
  p=pair_ns['compare'](case,runs[(case,lo)],runs[(case,hi)],read(src[f'validation/physical/{case}-cli-input.json']));pairs.append(p)
 require(pairs==read(data['current-cli-physical-capsule/tight-precision-pairs.json'])['pairs'],'independent exact precision pair replay')
 for name in ('current-physical-20261026/qualification-001/gghh-precision.json','current-physical-20261026/gghhh-256-384-precision.json'):require(read(data[name])['passed'] and read(data[name])['tolerance']==1e-10,'original binary64 pair gate retained separately')
 summary={'status':'passed_saved_cli_physical_replay','source_context_sha256':manifest['inherits']['source_context_sha256'],'cli_tests':14,'successful_physical_recomputations':4,'failed_physical_recomputations':1,'external_tensor_complex_checks':tensor_checks,'madloop_merged_complex_checks':physical_checks,'exact_precision_pair_complex_checks':568,'cases':cases,'precision_pairs':pairs,'preserved_failure':{'case':'gghhh','working_bits':128,'requested_accuracy_bits':53,'reason':lane['reason'],'returned_tensor_array':False,'new_original_reference_modes':[],'madloop_comparison':'not_run'},'not_run_in_initial_controller':['gghhh256 after failed128','gghhh128/256 pair'],'not_requested':['gghhh original IREGI IBP mode0 (historical disagreement retained elsewhere)'],'scope':'Physical graph spot checks at rank4; agreement is not a certified achieved precision bound; no new native execution or performance measurement.'}
 if 'qualification_sha256' in manifest:
  body=(HERE/'qualification.json').read_bytes();require(sha(body)==manifest['qualification_sha256'],'qualification summary binding');require(read(body)==summary,'qualification recomputes')
 if save:(HERE/'qualification.json').write_text(json.dumps(summary,indent=2)+'\n')
 output={'status':'passed','checks':checks,'source_files':len(src),'inherited_source_files':len(parent_src),'evidence_files':len(data),'cli_tests':14,'external_tensor_complex_checks':tensor_checks,'madloop_merged_complex_checks':physical_checks,'exact_precision_pair_complex_checks':568,'native_or_integral_execution':False,'manifest_sha256':sha((HERE/'manifest.json').read_bytes())}
 print(json.dumps(output,indent=2));return output
if __name__=='__main__':
 import sys
 main('--save' in sys.argv)
