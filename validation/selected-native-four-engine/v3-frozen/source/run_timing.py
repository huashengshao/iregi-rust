"""V3: explicit qualification-order preparation; timing requires a separate quiet grant."""
from pathlib import Path
import datetime,hashlib,itertools,json,math,os,random,signal,sys,time
import admission_v3 as four
import preparation
a=four.base
ROOT=Path.cwd();HERE=ROOT/'target/selected-native-optimized';V3=HERE/'four-engine-v3';V2=HERE/'four-engine-v2';h=a.h
ENGINES=['baselineTIRust','candidateTIRust','iregi','collier']
SELECTOR={'baselineTIRust':'baseline','candidateTIRust':'candidate'}
RATIOS=[('baselineTIRust','iregi'),('candidateTIRust','iregi'),('baselineTIRust','collier'),('candidateTIRust','collier'),('candidateTIRust','baselineTIRust')]
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
save=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n')
assert len(sys.argv)>=2 and sys.argv[1]in ['preflight','timing']
mode=sys.argv[1]
assert len(sys.argv)==(5 if mode=='preflight'else 7),'preflight build-id run-id CPU OR timing build-id run-id CPU quiet-manifest quiet-sha256'
build_dir=HERE/('build-'+sys.argv[2]);build=read(build_dir/'build.json');assert build['status']=='passed'
run_dir=V3/(mode+'-'+sys.argv[3]);run_dir.mkdir(exist_ok=False)
cpu=int(sys.argv[4]);window=None
if mode=='timing':
    window=Path(sys.argv[5]).resolve();assert sha(window)==sys.argv[6]
cap=120 if mode=='preflight'else 700
binary=build_dir/'probe';assert sha(binary)==build['outputs']['probe']['sha256']
reference=ROOT/'target/benchmark/iregi-benchmark';ref_manifest=ROOT/'target/benchmark/reference-build.json'
assert sha(reference)=='4c2241f6dd557db4e9348f0fd397484a72d71f83b953a6efc8010c61d1bdd389'
assert sha(ref_manifest)=='488782471657193e0e09f69c283cb82d8534577bb4fccd23f3087192c0f2f782'
inputs=ROOT/'validation/native-master-replay/inputs.json';assert sha(inputs)=='65d0d2fd554807478569ac88b6d689c9132ce541e98cfb2a3a55b8ef98e5c7ef'
inventory=read(HERE/'control-inventory.json')['controls']
qualified=HERE/'qualification-001/results.json';q=read(qualified);assert q['status']=='passed'
assert q['build_sha256']==sha(build_dir/'build.json') and q['binary_sha256']==sha(binary)
assert q['reference_sha256']==sha(reference) and q['input_sha256']==sha(inputs)
assert q['inputs_unchanged'] is True
assert q['input_bindings'][str(build_dir/'build.json')]==sha(build_dir/'build.json')
assert q['input_bindings'][str(binary)]==sha(binary)
collier=four.COLLIER_BINARY
collier_qualified=V2/'qualification-001/results.json';cq=read(collier_qualified)
assert cq['status']=='passed' and cq['inputs_unchanged'] is True and cq['process_exit_code']==0
assert cq['input_bindings'][str(qualified)]==sha(qualified)
assert cq['input_bindings'][str(binary)]==sha(binary)
# Guard immutable compiled archives/prototype snapshots, not ROOT's changing production tree.
assert cq['input_bindings'][str(V2/'admission_v2.py')]==sha(V2/'admission_v2.py')
assert sha(HERE/'timing-ready.json')=='d7aa3a076a1c304754e644f4e858b832637781068cae32bb966e8ab85a86a707'
bindings=preparation.historical_bindings()
for p,expected in four.collier_bindings().items():
    if p in bindings:assert bindings[p]==expected,f'conflicting historical binding: {p}'
    bindings[p]=expected
for p in [binary,reference,ref_manifest,inputs,qualified,HERE/'control-inventory.json',HERE/'admission.py',V2/'admission_v2.py',V2/'qualification-001/results.json',V2/'timing-ready.json',V3/'run_timing.py',V3/'preparation.py',V3/'admission_v3.py',V3/'adopted-timing-protocol.md',V3/'analyze.py',V3/'source-manifest.json',V3/'interface_controls.py',V3/'interface-controls.json',V3/'statistics_controls.py',V3/'statistics-controls.json',collier_qualified,HERE/'timing-ready.json',ROOT/'validation/benchmark/run.py',build_dir/'build.json',build_dir/'source-qualification-admission.json']:
    current=sha(p)
    if p in bindings:assert current==bindings[p],f'changed historical artifact: {p}'
    bindings[p]=current
source_manifest=read(V3/'source-manifest.json')
for name,expected in source_manifest['source_sha256'].items():assert sha(V3/name)==expected,name
for name,expected in source_manifest['parser_receipt_sha256'].items():assert sha(V3/name)==expected,name
if mode=='timing':
    ready=read(V3/'timing-ready.json');assert ready['status']=='ready-not-measured'
    assert ready['source_manifest_sha256']==sha(V3/'source-manifest.json')
    preflight=read(V3/'preflight-001/receipt.json')
    assert preflight['status']=='admitted-without-timings'and preflight['mode']=='preflight'
    assert ready['preflight_receipt_sha256']==sha(V3/'preflight-001/receipt.json')
    assert ready['preflight_raw_sha256']==preflight['raw_sha256']==sha(V3/'preflight-001/raw.jsonl')
    assert preflight['initialization']['schedule']==preparation.SCHEDULE
    for name,expected in preflight['input_sha256'].items():assert sha(Path(name))==expected,name
    for p in [window,V3/'timing-ready.json',V3/'preflight-001/receipt.json',V3/'preflight-001/raw.jsonl']:bindings[p]=sha(p)
def verify():
    for p,v in bindings.items():assert sha(p)==v,f'changed input: {p}'
verify();assert read(build_dir/'source-qualification-admission.json')['status']=='passed'
cases=read(inputs);assert len(cases)==4
coordinates=[(c['id'],b) for c in cases for b in [1,32]];assert len(set(coordinates))==8
assert [(r['id'],r['outer_batch']) for r in q['rows']]==coordinates
assert [(r['id'],r['batch']) for r in cq['rows']]==coordinates
for row,(case,batch) in zip(cq['rows'],((c,b) for c in cases for b in [1,32])):
    assert row['status']=='passed'
    four.check_collier(row['before'],case,case['samples'][:batch],pole_check=True)
    four.check_collier(row['after'],case,case['samples'][:batch],pole_check=True)
    assert four.canonical_collier(row['before'])==four.canonical_collier(row['after'])
for row,(case,batch) in zip(q['rows'],((c,b) for c in cases for b in [1,32])):
    samples=case['samples'][:batch];assert row['status']=='passed' and row['reference']['id']==case['id']
    a.validate_response(row['response'],case,samples)
    a.validate_response(row['repeat_response'],case,samples)
    assert a.canonical(row['response'])==a.canonical(row['repeat_response'])
    for engine in ['baseline','candidate']:
        assert h.compare(row['response'][engine],row['reference'],case,samples)['status']=='passed'
assert q['controls']['status']=='passed'
a.validate_controls(q['controls'],inventory)
qc=q['controls']['controls'];assert qc['baseline']==qc['candidate'] and len(qc['baseline'])==1
qm=qc['masters'];assert qm['status']=='passed'
assert [g['family'] for g in qm['selected_families']]==['A0','B0','C0']
assert sum(len(g['cases']) for g in qm['selected_families'])==34
assert len(qm['unchanged_paths'])==6 and sum(len(g['cases']) for g in qm['unchanged_paths'])==21
assert all(g['status']=='passed' for g in qm['selected_families']+qm['unchanged_paths'])
orders=list(itertools.permutations(ENGINES))*2
random.Random(173).shuffle(orders);assert len(orders)==48
record={'status':'running','scope':'private matched complete TIRust public calls, original IREGI and validated COLLIER; no production adoption','engine_labels':{'baselineTIRust':'baseline TIRust (Symbolica masters)','candidateTIRust':'candidate TIRust (selected native masters)','iregi':'original IREGI','collier':'COLLIER1.2.10 COLI mode1'},'ratio_inventory':[{'numerator':n,'denominator':d,'definition':n+' / '+d}for n,d in RATIOS],'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cpu':cpu,'mode':mode,'current_production_source_equality_claimed':False,'initialization':{'status':'pending','schedule':preparation.SCHEDULE,'raw_serials':[]},'runtime_cap_seconds':cap,'target_minimum_block_ns':100_000_000,'calibration_margin':1.10,'calibration_max_rounds':8,'quartets':48,'orders':orders,'input_sha256':{str(p):v for p,v in bindings.items()},'license_environment_present':any('SYMBOLICA' in k and 'LICENSE' in k for k in os.environ),'rows':[{'id':id,'outer_batch':b,'status':'pending'} for id,b in coordinates],'controls_before':{'status':'pending'},'controls_after':{'status':'pending'}}
save(run_dir/'receipt.json',record)
os.sched_setaffinity(0,{cpu});started=time.monotonic();deadline=started+cap
probe=oracle=collier_process=None
owned={};raw=None;serial=0
record['process_exit_codes']={'probe':None,'iregi':None,'collier':None}
record['frozen_executables']={}
def launch(path,label):
    frozen=h.freeze_executable(path,bindings[path],f'tirust-v3-{mode}-{label}')
    record['frozen_executables'][label]={'path':str(frozen),'sha256':bindings[path]}
    bindings[frozen]=bindings[path]
    record['input_sha256'][str(frozen)]=bindings[path]
    owner=h.Process.__new__(h.Process);owned[label]=owner
    h.Process.__init__(owner,frozen,label,run_dir,max(.001,deadline-time.monotonic()))
    return owner

def request(process,payload,meta):
    global serial
    process.timeout=max(.001,deadline-time.monotonic());assert process.timeout>.001,'runtime cap reached'
    response=process.request(payload)
    raw.write(json.dumps({'serial':serial,**meta,'response':response},separators=(',',':'))+'\n');raw.flush();serial+=1
    return response

def controls(stage):
    out=request(probe,'CONTROLS\n',{'stage':stage,'engine':'bothTIRust','kind':'controls'})
    assert out['status']=='passed';assert out['controls']['baseline']==out['controls']['candidate']
    a.validate_controls(out,inventory)
    assert out==q['controls'],'live controls differ from previously qualified own snapshots'
    for row in out['controls']['candidate']:
        for group in row['result']['master_captures']:assert group['backend']=='SymbolicaBatch'
    return out

def qualification(case,samples,stage):
    pair=request(probe,h.rust_request(case,samples,'Hybrid',0,1),{'stage':stage,'id':case['id'],'batch':len(samples),'engine':'bothTIRust','kind':'qualification'})
    a.validate_response(pair,case,samples)
    ref=request(oracle,h.fortran_request(case,samples,'Hybrid',0,1),{'stage':stage,'id':case['id'],'batch':len(samples),'engine':'iregi','kind':'qualification'})
    assert ref['stable'] is True and ref['id']==case['id']
    for engine in ['baseline','candidate']:assert h.compare(pair[engine],ref,case,samples)['status']=='passed'
    col=request(collier_process,four.c.collier_request(case,samples,1,0,1,check=True),{'stage':stage,'id':case['id'],'batch':len(samples),'engine':'collier','kind':'qualification'})
    four.check_collier(col,case,samples,pole_check=True)
    four.compare_collier(col,pair,ref,case,samples)
    return pair,ref,col

def measured(case,samples,engine,n,warmup,stage,index,expected,ref,col):
    assert type(n) is int and n>0
    meta={'stage':stage,'id':case['id'],'batch':len(samples),'engine':engine,'iterations':n,'warmup':warmup,'block':index}
    if engine=='iregi':
        response=request(oracle,h.fortran_request(case,samples,'Hybrid',warmup,n),meta)
        elapsed=a.validate_reference(response,ref,n,case,samples)
    elif engine=='collier':
        response=request(collier_process,four.c.collier_request(case,samples,1,warmup,n),meta)
        elapsed=four.timed_collier(response,col,n,case,samples)
    else:
        selector=SELECTOR[engine]
        data=json.loads(h.rust_request(case,samples,'Hybrid',warmup,n));data['engine']=selector
        response=request(probe,json.dumps(data)+'\n',meta)
        elapsed=a.validate_timed(response,expected[selector],selector,n,case,samples)
    assert math.isfinite(elapsed) and elapsed>0
    return {'engine':engine,'iterations':n,'elapsed_ns':elapsed,'elapsed_provenance':'integer Rust Instant nanoseconds' if engine in SELECTOR else 'reconstructed from reference floating ns/call times integer iterations; raw integer clock ticks not exported','ns_per_call':response['total_ns'][0],'raw_serial':serial-1}

def alarm_handler(signum,frame):raise TimeoutError(f'predeclared{cap}-second runtime cap reached')
signal.signal(signal.SIGALRM,alarm_handler);signal.alarm(cap)
try:
    raw=(run_dir/'raw.jsonl').open('x')
    probe=launch(binary,'probe');oracle=launch(reference,'iregi');collier_process=launch(collier,'collier')
    record['initialization']=preparation.prepare(lambda payload,meta:request(probe,payload,meta),q,cases)
    record['controls_before']=controls('before')
    stop=False
    for index,(case,batch) in enumerate((c,b) for c in cases for b in [1,32]):
        row=record['rows'][index];samples=case['samples'][:batch]
        row.update(status='running',calibration=[],blocks=[])
        try:
            expected,ref,col=qualification(case,samples,'before')
            admitted=q['rows'][index]
            assert a.canonical(expected)==a.canonical(admitted['response']),'initial own outputs differ from optimized admission'
            for field in ['id','stable','clock_ticks_per_second','lanes']:
                assert json.dumps(ref[field],sort_keys=True)==json.dumps(admitted['reference'][field],sort_keys=True),'initial reference differs from optimized admission'
            assert four.canonical_collier(col)==four.canonical_collier(cq['rows'][index]['before']),'initial COLLIER differs from admission'
            row['before_raw_serials']=[serial-3,serial-2,serial-1]
            if mode=='preflight':row['status']='admitted-without-timings'
            else:
                n=1;calibrated=False
                for round_index in range(8):
                    values=[measured(case,samples,engine,n,10 if round_index==0 else 0,'calibration',round_index,expected,ref,col) for engine in ENGINES]
                    row['calibration'].append(values)
                    minimum=min(x['elapsed_ns'] for x in values)
                    if minimum>=100_000_000:
                        calibrated=True;break
                    n=max(n+1,math.ceil(n*110_000_000/minimum))
                row['iterations']=n
                if not calibrated:row['status']='calibration-inconclusive'
                else:
                    predicted=48*sum(x['elapsed_ns'] for x in values)/1e9
                    row['estimated_acceptance_seconds']=predicted
                    row['remaining_runtime_seconds']=deadline-time.monotonic()
                    if predicted+2>row['remaining_runtime_seconds']:
                        row['status']='budget-inconclusive';stop=True
                    else:
                        for block_index,order in enumerate(orders):
                            block={'index':block_index,'order':list(order),'engines':[]}
                            row['blocks'].append(block)
                            for engine in order:block['engines'].append(measured(case,samples,engine,n,0,'acceptance',block_index,expected,ref,col))
                        row['short_blocks']=sum(v['elapsed_ns']<100_000_000 for b in row['blocks'] for v in b['engines'])
                        row['status']='short-block-inconclusive' if row['short_blocks'] else 'completed'
            after,after_ref,after_col=qualification(case,samples,'after')
            row['after_raw_serials']=[serial-3,serial-2,serial-1]
            assert four.canonical_collier(col)==four.canonical_collier(after_col),'COLLIER native arrays or pole probes changed'
            assert a.canonical(expected)==a.canonical(after),'own complete qualification changed'
            for field in ['id','stable','clock_ticks_per_second','lanes']:
                assert json.dumps(ref[field],sort_keys=True)==json.dumps(after_ref[field],sort_keys=True),'reference changed'
            row['before_after_qualification']='passed'
        except Exception as error:
            row.update(status='failed',error=str(error))
            if time.monotonic()>=deadline:stop=True
        save(run_dir/'receipt.json',record)
        if stop:
            for later in record['rows'][index+1:]:later.update(status='budget-inconclusive',error='unrun under fixed total runtime cap')
            break
    record['controls_after']=controls('after')
    assert record['controls_before']==record['controls_after'],'own direct/unchanged controls changed'
except Exception as error:record['error']=str(error)
finally:
    record['numerical_elapsed_seconds']=time.monotonic()-started
    record['deadline_exceeded']=time.monotonic()>=deadline
    if record['deadline_exceeded']:record.setdefault('error','fixed numerical deadline exceeded')
    signal.alarm(0)
    cleanup_errors=[]
    for label,owner in owned.items():
        child=getattr(owner,'process',None)
        if child is not None:
            try:
                if child.poll()is None:
                    if record['deadline_exceeded'] or 'error'in record:child.kill()
                    else:
                        try:
                            os.write(child.stdin.fileno(),b'QUIT\n')
                            child.wait(timeout=max(.001,min(5.,deadline-time.monotonic())))
                        except Exception:child.kill()
                    child.wait(timeout=5)
            except Exception as error:cleanup_errors.append(label+': '+repr(error))
            record['process_exit_codes'][label]=child.poll()
        try:owner.close()
        except Exception as error:cleanup_errors.append(label+' close: '+repr(error))
    if raw is not None:
        try:raw.close()
        except Exception as error:cleanup_errors.append('raw close: '+repr(error))
    record['cleanup_errors']=cleanup_errors
    record['cleanup_finished_elapsed_seconds']=time.monotonic()-started
    record['status']='terminal-awaiting-artifact-guards'
    save(run_dir/'receipt.json',record)
try:
    record['raw_sha256']=sha(run_dir/'raw.jsonl')
except Exception as error:record.update(raw_sha256=None,raw_hash_error=repr(error))
record.update(elapsed_seconds=time.monotonic()-started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),raw_response_count=serial)
try:verify();record['inputs_unchanged']=True
except Exception as error:record.update(inputs_unchanged=False,guard_error=str(error))
record['elapsed_seconds']=time.monotonic()-started
record['deadline_exceeded']=record['deadline_exceeded']or time.monotonic()>=deadline
if record['deadline_exceeded']:record.setdefault('error','fixed cohort deadline exceeded including cleanup/guards')
success='admitted-without-timings'if mode=='preflight'else'completed'
record['status']=success if not record['cleanup_errors'] and not record['deadline_exceeded'] and record.get('raw_sha256')is not None and record['initialization']['status']=='passed' and all(r['status']==success and r.get('before_after_qualification')=='passed' for r in record['rows']) and record['controls_before']['status']==record['controls_after']['status']=='passed' and record['inputs_unchanged'] and record['process_exit_codes']=={'probe':0,'iregi':0,'collier':0} and 'error' not in record else 'inconclusive-or-failed'
save(run_dir/'receipt.json',record)
print(json.dumps({'status':record['status'],'elapsed_seconds':record['elapsed_seconds'],'rows':[{'id':r['id'],'batch':r['outer_batch'],'status':r['status'],'short_blocks':r.get('short_blocks')} for r in record['rows']]}))
sys.exit(0 if record['status']==success else 1)
