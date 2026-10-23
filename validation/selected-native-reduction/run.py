"""Untimed complete whole-reduction qualification; one120-second budget."""
from pathlib import Path
from fractions import Fraction
import datetime, hashlib, importlib.util, json, math, os, signal, struct, sys, time

ROOT=Path.cwd(); HERE=ROOT/'target/selected-native-reduction'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
save=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n')
build_dir=HERE/('build-'+sys.argv[1]); run_dir=HERE/('qualification-'+sys.argv[2]);run_dir.mkdir(exist_ok=False)
build=read(build_dir/'build.json');assert build['status']=='passed'
binary=build_dir/'probe';assert sha(binary)==build['outputs']['probe']['sha256']
reference=ROOT/'target/benchmark/iregi-benchmark';ref_build=read(ROOT/'target/benchmark/reference-build.json');assert sha(reference)==ref_build['binary_sha256']
inputs=ROOT/'validation/native-master-replay/inputs.json'
assert sha(inputs)=='65d0d2fd554807478569ac88b6d689c9132ce541e98cfb2a3a55b8ef98e5c7ef'
helper=ROOT/'validation/benchmark/run.py'
spec=importlib.util.spec_from_file_location('whole_benchmark_helper',helper);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
bindings={ROOT/p:v for p,v in build['input_sha256'].items()}
for p in [binary,reference,ROOT/'target/benchmark/reference-build.json',inputs,helper,HERE/'run.py',build_dir/'build.json']:bindings[p]=sha(p)
def verify():
    for p,v in bindings.items():assert sha(p)==v, f'changed qualification input: {p}'
verify()
cases=read(inputs);assert len(cases)==4
expected_coordinates=[(c['id'],b) for c in cases for b in [1,32]]
assert len(set(expected_coordinates))==8
records={'status':'running','scope':'opt0 private whole-reduction semantics, no benchmark timing or adoption','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'budget_seconds':120,'production_revision':'06706e2a1e4f0082889a53187c80bbe97803340f','build_sha256':sha(build_dir/'build.json'),'binary_sha256':sha(binary),'reference_sha256':sha(reference),'input_sha256':sha(inputs),'helper_sha256':sha(helper),'license_environment_present':any('SYMBOLICA' in k and 'LICENSE' in k for k in os.environ),'rows':[{'id':id,'outer_batch':b,'status':'pending'} for id,b in expected_coordinates],'controls':{'status':'pending'}}
save(run_dir/'results.json',records)

def finite_complex(value):
    assert type(value) is list and len(value)==2
    for x in value:
        assert type(x) is dict and x['finite'] is True and type(x['precision']) is int and x['precision']==53 and type(x['negative_sign']) is bool
        assert type(x['rational']) is str
    result=[]
    for x in value:
        exact=Fraction(x['rational']); f=float(exact)
        if exact:assert (exact<0)==x['negative_sign']
        else:f=math.copysign(0.,-1. if x['negative_sign'] else 1.)
        result.append(f)
    assert all(math.isfinite(x) for x in result)
    return complex(*result)

def master_compare(base, selected, n, rank, batch):
    groups={(2,0):[('B0',batch)],(2,1):[('B0',batch),('A0',2*batch)],(3,0):[('C0',batch)],(3,1):[('C0',batch),('B0',3*batch)]}[(n,rank)]
    a=base['master_captures'];b=selected['master_captures'];assert len(a)==len(b)==len(groups)
    outputs=0;worst=0.;differences=0
    for x,y,(family,rows) in zip(a,b,groups):
        for field in ['family','components','rows','requests','valid_lanes','input','output_order','errors','whole_batch_error']:assert x[field]==y[field],field
        assert x['family']==family and x['rows']==rows and x['components']==1
        assert x['backend']=='SymbolicaBatch' and y['backend']=='RustBatch'
        assert x['whole_batch_error'] is None and x['errors']==[None]*rows
        assert x['valid_lanes']==list(range(batch))
        assert x['requests']==sorted(x['requests']) and len(x['requests'])==rows
        assert x['output_order']==['finite','total_single','ir_double','uv_single','ir_single','derivative_discriminant']
        arity={'A0':2,'B0':4,'C0':7}[family]
        assert len(x['input'])==arity*rows and len(x['output'])==len(y['output'])==rows
        inputs=[finite_complex(z) for z in x['input']]
        for lane,(xa,ya) in enumerate(zip(x['output'],y['output'])):
            assert len(xa)==len(ya)==6
            squared=max(1.,*(abs(z) for z in inputs[lane*arity:(lane+1)*arity]))
            unit={'A0':squared,'B0':1.,'C0':1./squared}[family]
            for coefficient,(za,zb) in enumerate(zip(xa,ya)):
                va=finite_complex(za);vb=finite_complex(zb)
                error=abs(vb-va)/((1. if coefficient==5 else unit)+abs(va))
                assert math.isfinite(error) and error<=1e-10,(family,lane,coefficient,error)
                worst=max(worst,error);outputs+=1
                differences+=sum(aa!=bb for aa,bb in zip(za,zb))
    return {'status':'passed','master_groups':len(groups),'master_rows':sum(g[1] for g in groups),'complex_outputs':outputs,'max_normalized_error':worst,'represented_component_differences':differences}

def validate_response(response,case,samples):
    base=response['baseline'];selected=response['candidate'];batch=len(samples)
    assert response['id']==case['id']
    assert base['private_selected_native'] is False and selected['private_selected_native'] is True
    for value in [base,selected]:
        assert value['id']==case['id'] and value['n']==case['n'] and value['rank']==case['rank'] and value['batch']==batch and value['stable'] is True
        assert value['degrees']==h.degrees(case['rank']) and len(value['lanes'])==batch
        for lane in value['lanes']:
            assert lane['status']=='success' and lane['fallback_used'] is False and lane['analytic_used'] is False
            assert len(lane['represented'])==4*len(value['degrees'])
            numeric=[z for moment in lane['moments'] for z in moment]
            assert len(numeric)==len(lane['represented'])
            for z,actual in zip(lane['represented'],numeric):
                represented=finite_complex(z)
                assert type(actual) is list and len(actual)==2
                for lhs,rhs in zip([represented.real,represented.imag],actual):
                    assert type(rhs) in [int,float] and math.isfinite(rhs)
                    assert struct.pack('>d',lhs)==struct.pack('>d',rhs),'reported value and represented value differ'
    for field in ['degrees','diagnostics','execution']:assert base[field]==selected[field],field
    assert base['execution']['fallback_rows']==base['execution']['analytic_rows']==0
    cross=h.compare(selected,base,case,samples);assert cross['status']=='passed',cross
    masters=master_compare(base,selected,case['n'],case['rank'],batch)
    assert base['execution']['master_family_batches']==masters['master_groups'] and base['execution']['master_rows']==masters['master_rows']
    return {'whole_cross_backend':cross,'masters':masters}

def canonical(response):
    # Reuse metadata differs once a workspace has been prepared; numerical data cannot.
    result=json.loads(json.dumps(response))
    for backend in ['baseline','candidate']:result[backend].pop('plan_reused',None)
    return result

os.sched_setaffinity(0,{20,21})
started=time.monotonic();deadline=started+120
probe=h.Process(binary,'probe',run_dir,120);oracle=h.Process(reference,'iregi',run_dir,120)
def request(process,payload):
    process.timeout=max(.001,deadline-time.monotonic())
    assert process.timeout>.001,'total qualification budget exhausted'
    return process.request(payload)
def alarm_handler(signum,frame):raise TimeoutError('total120-second qualification bound reached')
signal.signal(signal.SIGALRM,alarm_handler);signal.alarm(120)
try:
    for index,(case,batch) in enumerate((c,b) for c in cases for b in [1,32]):
        row=records['rows'][index];samples=case['samples'][:batch]
        try:
            payload=h.rust_request(case,samples,'Hybrid',0,1)
            response=request(probe,payload);row['response']=response
            row['comparison']=validate_response(response,case,samples)
            repeated=request(probe,payload);row['repeat_response']=repeated
            validate_response(repeated,case,samples)
            assert canonical(response)==canonical(repeated),'own-backend represented values or status changed on repeat'
            ref=request(oracle,h.fortran_request(case,samples,'Hybrid',0,1));ref.pop('total_ns',None);row['reference']=ref
            row['reference_comparisons']={backend:h.compare(response[backend],ref,case,samples) for backend in ['baseline','candidate']}
            assert all(c['status']=='passed' for c in row['reference_comparisons'].values()),row['reference_comparisons']
            row['status']='passed'
        except Exception as error:row.update(status='failed',error=str(error))
        save(run_dir/'results.json',records)
    try:
        controls=request(probe,'CONTROLS\n');records['controls']=controls
        assert controls['status']=='passed'
        assert controls['controls']['baseline']==controls['controls']['candidate'],'unchanged whole-core paths differ'
        for row in controls['controls']['candidate']:
            for group in row['result']['master_captures']:assert group['backend']=='SymbolicaBatch'
    except Exception as error:records['controls'].update(status='failed',error=str(error))
except Exception as error:records['error']=str(error)
finally:
    signal.alarm(0)
    if time.monotonic()>=deadline:
        for process in [probe,oracle]:
            if process.process.poll() is None:process.process.kill();process.process.wait()
    probe.close();oracle.close()
records.update(elapsed_seconds=time.monotonic()-started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
try:verify();records['inputs_unchanged']=True
except Exception as error:records.update(inputs_unchanged=False,guard_error=str(error))
records['status']='passed' if all(r['status']=='passed' for r in records['rows']) and records['controls']['status']=='passed' and records['inputs_unchanged'] else 'failed'
records['input_bindings']={str(p.relative_to(ROOT)):v for p,v in bindings.items()}
save(run_dir/'results.json',records)
print(json.dumps({'status':records['status'],'elapsed_seconds':records['elapsed_seconds'],'rows':[{'id':r['id'],'batch':r['outer_batch'],'status':r['status'],'error':r.get('error')} for r in records['rows']],'controls':records['controls']['status']}))
sys.exit(0 if records['status']=='passed' else 1)
