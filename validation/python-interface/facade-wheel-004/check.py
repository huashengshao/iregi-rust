"""Replay current-wheel saved evidence without a native host or integral."""
from pathlib import Path
import hashlib,io,json,tarfile,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;checks=0;PREFIX='/shared/external/iregi/iregi-rust/'
COUNTS={'upstream':25,'historical':29,'generic_low':3,'checked_constructor':1,'checked_plain':1,'checked_profile':1,'checked_dual':1,'affine_capability':1,'legacy':1,'n6':1,'n7':1,'gallery':7}
STAGES=('build','install','import','typing',*COUNTS)
def require(value,why):
 global checks
 checks+=1
 if not value:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def read(body):return json.loads(body)
def unpack(name,descriptor):
 body=(HERE/name).read_bytes();require(sha(body)==descriptor['sha256'] and len(body)==descriptor['bytes'],'archive binding')
 result={}
 with tarfile.open(fileobj=io.BytesIO(body),mode='r:gz') as archive:
  for member in archive:
   require(member.isfile() and not member.name.startswith('/') and '..' not in Path(member.name).parts and member.name not in result,'safe regular member')
   data=archive.extractfile(member).read();require(not data.startswith((b'\x7fELF',b'!<arch>')),'no native binary payload')
   require(member.name in descriptor['members'],'declared member');d=descriptor['members'][member.name]
   require(sha(data)==d['sha256'] and len(data)==d['bytes'],'member binding');result[member.name]=data
 require(set(result)==set(descriptor['members']),'exact member inventory');return result

def main():
 manifest=read((HERE/'manifest.json').read_bytes());require(sha((HERE/'check.py').read_bytes())==manifest['checker_sha256'],'checker binding')
 src=unpack('sources.tar.gz',manifest['sources']);data=unpack('evidence.tar.gz',manifest['evidence'])
 observer_body=(HERE/'saved-replay-observer-failure.json').read_bytes()
 require(sha(observer_body)==manifest['saved_replay_observer_failure_sha256'],'saved checker observer correction binding')
 observer=read(observer_body)
 require(observer['initial_checker_sha256']==sha(data['check-template.py']),'first failed saved observer body retained')
 require(observer['corrected_checker_sha256']==manifest['checker_sha256'] and observer['native_evaluations']==0,'saved observer correction has no native evaluation')
 context=read(data['context.json']);require(sha(data['context.json'])==manifest['source_context_sha256'],'actual source freeze')
 require(len(src)==len(context['inputs'])==manifest['selected_source_files']==201,'selected source bodies')
 for name,digest in context['inputs'].items():require(name.removeprefix(PREFIX) in src and sha(src[name.removeprefix(PREFIX)])==digest,'actual owned source body')
 coherent=context['coherent_body_inputs'];require(len(coherent)==context['coherent_body_context_count']==manifest['coherent_body_context_count']==158,'complete coherent158 bodies')
 for name,digest in coherent.items():require(name in src and sha(src[name])==digest,'actual coherent body hash')
 b3='target/checked-g-generalized-qualification/build-003/receipt.json';b4='target/checked-g-generalized-qualification/build-004/receipt.json';bridge_path='target/checked-g-generalized-qualification/test-selection-bridge.json'
 require(sha(src[b3])==context['production_cli_build_003_sha256'] and sha(src[b4])==context['coherent_build_004_sha256'],'coherent build receipts')
 require(sha(src[bridge_path])==context['test_only_bridge_sha256'],'test-only bridge binding')
 old,new,bridge=read(src[b3]),read(src[b4]),read(src[bridge_path]);require(new['source_files']==coherent and old['status']==new['status']=='passed','currentbody build identity')
 changed={p for p,d in old['source_files'].items() if coherent.get(p)!=d};require(changed==set(bridge['changed_files'])=={'crates/iregi-rust/src/dispatch/mass_taylor_tests.rs'},'only declared test body changed')
 require(bridge['all_other_source_files_byte_identical'] and bridge['cli003_production_unchanged'],'production bridge scope')
 require(b'#[cfg(test)]\n#[path = "dispatch/mass_taylor_tests.rs"]\nmod mass_taylor_tests;' in src['crates/iregi-rust/src/dispatch.rs'],'changed module is cfg test only')
 groups=0
 for stage in STAGES:
  prefix=stage+'-001/';r=read(data[prefix+'receipt.json'])
  require(r['status']=='passed' and not r['cleanup_errors'] and r['cancellation'] is None,'actual bounded successful stage')
  require(r['source_context_sha256']==manifest['source_context_sha256'] and r['elapsed_seconds']<=r['seconds'],'actual stage source and bound')
  for step in r['steps']:
   require(step['status']=='exited' and step['returncode']==0 and step['owned_group_gone'],'saved owned process group terminal');groups+=1
  for name,digest in r['saved_files'].items():require(prefix+name in data and sha(data[prefix+name])==digest,'saved stage log/product binding')
  if stage in COUNTS:
   cases=list(ET.fromstring(data[prefix+'tests.xml']).iter('testcase'))
   require(len(cases)==COUNTS[stage] and all(not list(case) for case in cases),'exact successful cases/no skips')
   require([case.attrib['name'] for case in cases]==r['test_names'],'actual XML case names')
 wheel=read(data['build-001/wheel.json']);require(wheel==manifest['wheel'],'actual owned wheel identity')
 identity=read(data['import-001/identity.json']);require(identity['native'].startswith(PREFIX+'.local/tirust-feature-rank6-env/'),'fresh current installed environment')
 require(set(identity['shared_aliases'])=={'Expression','Float','ComplexFloat','Model','FeynmanDiagram','TensorExpression','ReductionPlan','Workspace'},'shared native owner class identities')
 typing=read(data['typing-001/step-0.log']);require(typing['summary']['errorCount']==typing['summary']['warningCount']==0,'actual installed consumer typing')
 require(b'from tirust._tirust import Engine' in data['installed-client/dispatch_client.py'],'current Engine alias includes new tags')
 require(b'user_components' in data['installed-client/dispatch_client.py'] and b'internal_components' in data['installed-client/dispatch_client.py'],'actual MassTaylor fields checked')
 require(b'typed_child: EngineExecution | None = child' in data['installed-client/typing_legacy_noop_assignability.py'],'recursive child assignability consumer')
 require(b'assert_type(child["execution"], dict[str, int])' in data['installed-client/typing_legacy_noop_assignability.py'],'strict recursive leaf typing')
 require(b'"mass_taylor"' in src['python/tirust/_tirust.pyi'] and b'"legacy_noop"' in src['python/tirust/_tirust.pyi'],'current tagged public schema')
 legacy=read(data['legacy-001/receipt.json']);require(legacy['test_names']==['test_legacy_noop_admits_unchanged_lanes_and_never_executes_rejected_neighbor'],'actual new Legacy test')
 body=src['tests/python/test_tirust_legacy_noop.py']
 for phrase in (b'child_preparation_attempts',b'caller == saved',b'"accepted_rows"] == 2',b'reference_result.lane(0)',b'recovered_detail',b'no Preserve child was executed'):require(phrase in body,'meaningful Legacy routing and state assertions')
 earlier=read(data['preserved-recursive-observer/typing-receipt.json']);earlier_output=read(data['preserved-recursive-observer/typing-output.json'])
 require(earlier['status']=='failed' and earlier['native_evaluations']==0 and not earlier['cleanup_errors'] and earlier['steps'][0]['owned_group_gone'],'earlier static identity observer preserved')
 require(earlier_output['summary']['errorCount']==2 and all(x.get('rule')=='reportAssertTypeFailure' for x in earlier_output['generalDiagnostics']),'two earlier exact identity diagnostics')
 for name,digest in earlier['source_sha256'].items():
  rel=name.split('target/legacy-noop-python-proposal/',1)[1];require(sha(data['preserved-recursive-observer/'+rel])==digest,'earlier observer actual source')
 correction=read(data['installed-client-field-correction.json'])
 require(correction['status']=='corrected_before_typing_execution' and correction['after_sha256']==sha(data['installed-client/dispatch_client.py']),'corrected owned observer field name before execution')
 require(correction['before_sha256']==sha(data['installed-client-control-before-correction.py']),'unrun initial observer retained')
 parent=HERE.parent/'facade-wheel-003/manifest.json';require(sha(parent.read_bytes())==context['historical_qualified_wheel003_manifest_sha256'],'historical003 unchanged')
 require(sum(COUNTS.values())==manifest['tests']['total']==72 and sum(v for k,v in COUNTS.items() if k!='gallery')==manifest['tests']['api_total']==65,'exact current coverage totals')
 output={'status':'passed_saved_current_wheel_replay','checks':checks,'coherent_body_context_count':158,'selected_source_files':201,'evidence_files':len(data),'api_cases':65,'marimo_cases':7,'successful_owned_process_groups':groups,'current_failed_stages':0,'preserved_earlier_static_identity_errors':2,'preserved_saved_observer_corrections':1,'native_or_integral_execution':False,'manifest_sha256':sha((HERE/'manifest.json').read_bytes())}
 print(json.dumps(output,indent=2));return output
if __name__=='__main__':main()
