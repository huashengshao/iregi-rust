"""Frozen reference interfaces; import starts no process or numerical execution."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
ROOT=Path('/shared/external/iregi/iregi-rust')
HELPER=ROOT/'validation/benchmark/run.py'
spec=importlib.util.spec_from_file_location('fresh_four_engine_statistics_and_reference',HELPER)
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
COLLIER_HELPER=ROOT/'validation/collier-reference/ready-initial8-v3/producer/validation/collier-reference/run.py'
spec=importlib.util.spec_from_file_location('fresh_four_engine_collier_wire',COLLIER_HELPER)
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
COLLIER_BINARY=ROOT/'target/reference/collier/build-attempt001/collier-benchmark'
IREGI_BINARY=ROOT/'target/benchmark/iregi-benchmark'

def sha(path):
 with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())

def bindings():
 paths={HELPER:'22488d58c1cbed9520728f62efa67f98250cffdef8b88ec8b85cc72b9b99e6b7',COLLIER_HELPER:'979046300446dc037c52927436696b4bcac2a289439abb699d85f6b19a63d134',IREGI_BINARY:'4c2241f6dd557db4e9348f0fd397484a72d71f83b953a6efc8010c61d1bdd389',ROOT/'target/benchmark/reference-build.json':'488782471657193e0e09f69c283cb82d8534577bb4fccd23f3087192c0f2f782',COLLIER_BINARY:'33704d629e547fe817a3982451cde1fc796d832fb51476c6ef07dffbe37c175a',ROOT/'validation/collier-reference/ready-initial8-v3/build.json':'654d6221d0169ba06d0f2ae7f9615737d6b67aae0f0b57539e74ad518902fc80',ROOT/'validation/collier-reference/ready-initial8-v3/correctness.json':'de40173c8ec11c8750c4cb614bb73a64e3037eac90402c9f1a39696e0ade135b'}
 for path,wanted in paths.items():assert sha(path)==wanted,str(path)
 build=read(ROOT/'validation/collier-reference/ready-initial8-v3/build.json')
 for path,wanted in [(ROOT/'validation/collier-reference/driver.f90',build['driver_sha256']),(ROOT/build['library']['path'],build['library']['sha256'])]+[(ROOT/build['generated_source_root']/name,wanted)for name,wanted in build['generated_source_sha256'].items()]:
  assert sha(path)==wanted;paths[path]=wanted
 return {str(path):wanted for path,wanted in paths.items()}

def exact(a,b):return json.dumps(a,sort_keys=True,allow_nan=False)==json.dumps(b,sort_keys=True,allow_nan=False)

def reference(response,case,samples):
 assert response['id']==case['id']and response['stable']is True
 assert type(response['clock_ticks_per_second'])is int and response['clock_ticks_per_second']>0
 h.validate_response(response,case)
 assert h.compare(response,response,case,samples)['status']=='passed'
 return {key:response[key]for key in ['id','stable','clock_ticks_per_second','lanes']}

def check_collier(response,case,samples,*,pole_check):
 assert response['id']==case['id']and response['stable']is True
 assert type(response['collier_mode'])is int and response['collier_mode']==1
 reference(response,case,samples)
 if pole_check:c.validate_poles(response,samples)
 else:assert response['pole_check_errors']is None
 identities=c.uv_identities(response,case,samples);assert identities['status']=='passed'
 return identities

def canonical_collier(response,include_poles=True):
 keys=['id','stable','collier_mode','clock_ticks_per_second','lanes']
 if include_poles:keys.append('pole_check_errors')
 return {key:response[key]for key in keys}

def timed_reference(response,expected,n,case,samples):
 observed=reference(response,case,samples)
 assert exact(observed,reference(expected,case,samples))
 return response['total_ns'][0]*n

def timed_collier(response,expected,n,case,samples):
 check_collier(response,case,samples,pole_check=False)
 assert exact(canonical_collier(response,False),canonical_collier(expected,False))
 return response['total_ns'][0]*n
