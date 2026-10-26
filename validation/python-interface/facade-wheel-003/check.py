"""Replay saved current-wheel API evidence without native execution."""
from pathlib import Path
import hashlib, io, json, re, tarfile, xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
checks=0
def require(v,m):
 global checks
 checks+=1
 if not v:raise ValueError(m)
def sha(data):return hashlib.sha256(data).hexdigest()
def read(data):return json.loads(data)
def archive(name,descriptor):
 data=(HERE/name).read_bytes();require(sha(data)==descriptor['sha256'] and len(data)==descriptor['bytes'],name+' archive binding')
 output={}
 with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tar:
  for m in tar:
   require(m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts and m.name not in output,'safe regular member')
   body=tar.extractfile(m).read();require(not body.startswith((b'\x7fELF',b'!<arch>')),'no native archive payload')
   require(m.name in descriptor['members'],'declared member')
   d=descriptor['members'][m.name];require(sha(body)==d['sha256'] and len(body)==d['bytes'],'member binding')
   output[m.name]=body
 require(set(output)==set(descriptor['members']),'exact inventory')
 return output

def main():
 manifest=read((HERE/'manifest.json').read_bytes())
 require(sha((HERE/'check.py').read_bytes())==manifest['checker_sha256'],'checker binding')
 sources=archive('sources.tar.gz',manifest['sources']);evidence=archive('evidence.tar.gz',manifest['evidence'])
 require(len(sources)==manifest['source_files'],'selected source count')
 context=read(evidence['context.json']);require(sha(evidence['context.json'])==manifest['source_context_sha256'],'context binding')
 root='/shared/external/iregi/iregi-rust/'
 for name,digest in context['inputs'].items():
  local=name[len(root):] if name.startswith(root) else name
  require(local in sources and sha(sources[local])==digest,'actual selected source body')
 counts={'upstream':25,'historical':29,'checked_dual':1,'n6':1,'n7':1,'gallery':7}
 stages=('build','install','import','upstream','historical','n6','n7','typing','gallery','checked_dual')
 groups=0
 for stage in stages:
  prefix=manifest['phase_directories'][stage]+'/'
  receipt=read(evidence[prefix+'receipt.json'])
  require(receipt['status']=='passed' and not receipt['cleanup_errors'] and receipt['cancellation'] is None,'actual successful bounded stage')
  require(receipt['elapsed_seconds']<=receipt['seconds'],'finite stage bound')
  require(receipt['source_context_sha256']==manifest['source_context_sha256'],'stage context')
  for step in receipt['steps']:
   require(step['status']=='exited' and step['returncode']==0 and step['owned_group_gone'],'saved terminal owned group')
   groups+=1
  for name,digest in receipt['saved_files'].items():
   if name=='owned-cli-tests':
    require(stage=='build' and digest==manifest['cli_test_product']['sha256'],'excluded CLI binary identified')
   else:require(prefix+name in evidence and sha(evidence[prefix+name])==digest,'saved log/product record')
  if stage in counts:
   cases=list(ET.fromstring(evidence[prefix+'tests.xml']).iter('testcase'))
   require(len(cases)==counts[stage] and all(not list(c) for c in cases),'exact successful test cases/no skips')
   require([c.attrib['name'] for c in cases]==receipt['test_names'],'XML names match terminal receipt')
 partial=read(evidence['dispatch-001/receipt.json'])
 require(partial['status']=='failed' and not partial['cleanup_errors'] and partial['steps'][0].get('timeout') and partial['steps'][0]['owned_group_gone'],'preserved aggregate dispatch timeout')
 partial_log=evidence['dispatch-001/step-0.log'].decode()
 passed=re.findall(r'^(tests/python/test_tirust_dispatch\.py::\S+) PASSED(?:\s|$)',partial_log,re.M)
 expected=[
 'test_generic_tag_profile_and_result_snapshot_are_owned',
 'test_explicit_dual_shape_uses_generic_and_preserves_components[shape0]',
 'test_explicit_dual_shape_uses_generic_and_preserves_components[shape1]',
 'test_highpoint_profiling_and_zero_order_dual_keep_affine_capabilities',
 'test_checked_scalar_products_require_explicit_compatible_inputs',
 'test_checked_scalar_products_cannot_bypass_certificates[options0]',
 'test_checked_scalar_products_cannot_bypass_certificates[options1]']
 require(passed==['tests/python/test_tirust_dispatch.py::'+node for node in expected],'seven actual passing exact nodes from original raw pytest log')
 completion_node=manifest['dispatch_coverage']['completion_node']
 require(completion_node not in passed and completion_node.endswith('[options2]'),'only unfinished parametrization completed')
 require(read(evidence['checked_dual-001/receipt.json'])['steps'][0]['command'][-1]==completion_node,'actual completion command')
 cli_receipt=read(evidence['cli-binary-001/receipt.json'])
 require(cli_receipt['status']=='passed' and not cli_receipt['cleanup_errors'] and cli_receipt['steps'][0]['owned_group_gone'],'standalone CLI build suffix')
 require(read(evidence['cli-binary-001/product.json'])==manifest['cli_binary_product'],'excluded standalone CLI identified')
 groups+=1
 cache_miss=read(evidence['preserved-install-cache-miss/receipt.json'])
 require(cache_miss['status']=='failed' and not cache_miss['cleanup_errors'] and all(s['owned_group_gone'] for s in cache_miss['steps']),'preserved offline cache miss cleanup')
 require(b'marimo was not found in the cache' in evidence['preserved-install-cache-miss/step-1.log'],'preserved actual pinned install cache miss')
 identity=read(evidence['import-001/identity.json'])
 wheel=read(evidence['build-001/wheel.json']);require(wheel==manifest['wheel'],'original wheel/native metadata')
 require(identity['native'].startswith(root+'.local/tirust-current-rank6-env/'),'fresh installed native origin')
 require('affine_power' in sources['tests/python/test_tirust_dispatch.py'].decode(),'actual affine routing observer')
 require('check_scalar_products=True' in sources['tests/python/test_tirust_dispatch.py'].decode(),'actual checked input observer')
 typing=read(evidence['typing-001/step-0.log']);require(typing['summary']['errorCount']==typing['summary']['warningCount']==0,'installed consumer typing')
 first_context=read(evidence['preserved-toolchain-failure/context.json'])
 common=set(first_context['inputs']) & set(context['inputs'])
 require(len(common)==manifest['first_failed_build_common_inputs']['count']==146 and all(first_context['inputs'][p]==context['inputs'][p] for p in common),'same project sources across restored-toolchain retry')
 failed=read(evidence['preserved-toolchain-failure/build-001/receipt.json'])
 require(failed['status']=='failed' and not failed['cleanup_errors'] and failed['steps'][0]['owned_group_gone'],'preserved original failure cleanup')
 require(b'No such file or directory' in evidence['preserved-toolchain-failure/build-001/step-0.log'],'preserved original environment failure')
 require('restored' in context['environment_repair'] and all('1.99.0' in row['version'] for path,row in context['toolchain'].items() if 'rustc' in path or 'cargo-' in path),'explicit restored compiler context')
 require(sum(counts.values())+len(passed)==manifest['tests']['total']==71,'scoped total tests')
 output={'status':'passed_saved_replay','checks':checks,'source_files':len(sources),'test_cases':71,'successful_owned_process_groups':groups,'preserved_environment_failures':2,'preserved_aggregate_timeouts':1,'native_or_integral_execution':False,'manifest_sha256':sha((HERE/'manifest.json').read_bytes())}
 print(json.dumps(output,indent=2));return output
if __name__=='__main__':main()
