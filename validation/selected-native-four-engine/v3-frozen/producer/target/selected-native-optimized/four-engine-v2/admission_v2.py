"""Four-engine interface admission. Existing numeric core and reference drivers are unchanged."""
from pathlib import Path
import hashlib,importlib.util,json,math,sys
ROOT=Path.cwd();HERE=ROOT/'target/selected-native-optimized';V2=HERE/'four-engine-v2'
sys.path.insert(0,str(HERE))
import admission as base
h=base.h
COLLIER_HELPER=ROOT/'validation/collier-reference/ready-initial8-v3/producer/validation/collier-reference/run.py'
spec=importlib.util.spec_from_file_location('frozen_collier_request_support',COLLIER_HELPER)
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
COLLIER_BUILD=ROOT/'validation/collier-reference/ready-initial8-v3/build.json'
COLLIER_QUAL=ROOT/'validation/collier-reference/ready-initial8-v3/correctness.json'
COLLIER_BINARY=ROOT/'target/reference/collier/build-attempt001/collier-benchmark'

def collier_bindings():
    assert sha(COLLIER_BUILD)=='654d6221d0169ba06d0f2ae7f9615737d6b67aae0f0b57539e74ad518902fc80'
    assert sha(COLLIER_QUAL)=='de40173c8ec11c8750c4cb614bb73a64e3037eac90402c9f1a39696e0ade135b'
    assert sha(COLLIER_BINARY)=='33704d629e547fe817a3982451cde1fc796d832fb51476c6ef07dffbe37c175a'
    assert sha(COLLIER_HELPER)=='979046300446dc037c52927436696b4bcac2a289439abb699d85f6b19a63d134'
    build=read(COLLIER_BUILD);q=read(COLLIER_QUAL)
    assert build['status']=='built' and q['status']=='passed'
    assert q['identity']['collier_mode']==1 and q['identity']['batches']==[1,32]
    assert q['identity']['input_sha256']=='65d0d2fd554807478569ac88b6d689c9132ce541e98cfb2a3a55b8ef98e5c7ef'
    assert build['binary']['sha256']==q['identity']['binaries']['collier']['sha256']==sha(COLLIER_BINARY)
    bindings={p:sha(p) for p in [COLLIER_BUILD,COLLIER_QUAL,COLLIER_BINARY,COLLIER_HELPER]}
    driver=ROOT/'validation/collier-reference/driver.f90'
    assert sha(driver)==build['driver_sha256'];bindings[driver]=sha(driver)
    library=ROOT/build['library']['path'];assert sha(library)==build['library']['sha256'];bindings[library]=sha(library)
    source=ROOT/build['generated_source_root']
    for name,expected in build['generated_source_sha256'].items():
        path=source/name;assert sha(path)==expected;bindings[path]=expected
    return bindings

def check_collier(response,case,samples,*,pole_check):
    assert response['id']==case['id'] and response['stable'] is True
    assert type(response['collier_mode']) is int and response['collier_mode']==1
    assert type(response['clock_ticks_per_second']) is int and response['clock_ticks_per_second']>0
    h.validate_response(response,case)
    assert h.compare(response,response,case,samples)['status']=='passed'
    assert len(response['lanes'])==len(samples)
    if pole_check:c.validate_poles(response,samples)
    else:assert response['pole_check_errors'] is None
    identities=c.uv_identities(response,case,samples);assert identities['status']=='passed'
    return identities

def canonical_collier(response,*,include_poles=True):
    keys=['id','stable','collier_mode','clock_ticks_per_second','lanes']
    if include_poles:keys.append('pole_check_errors')
    return json.dumps({k:response[k]for k in keys},sort_keys=True)

def compare_collier(response,pair,reference,case,samples):
    checks={f'{engine} TIRust / COLLIER numerical agreement':h.compare(pair[engine],response,case,samples) for engine in ['baseline','candidate']}
    checks['COLLIER and IREGI numerical agreement']=h.compare(response,reference,case,samples)
    assert all(x['status']=='passed' for x in checks.values())
    return checks

def timed_collier(response,expected,iterations,case,samples):
    check_collier(response,case,samples,pole_check=False)
    assert canonical_collier(response,include_poles=False)==canonical_collier(expected,include_poles=False),'COLLIER own native arrays/status changed'
    return response['total_ns'][0]*iterations
