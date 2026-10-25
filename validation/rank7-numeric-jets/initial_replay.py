"""Portable saved-only replay of the independently audited initial eleven N2 captures.

Transport-only version of independent_saved_audit.py SHA256
5cfafa336a12b3d8d37bb9c1f7a3e5c7b2c455bc44c7f568a6af7e60fd45b1f5.
No producer import, filesystem read/write, process probe or numerical engine.
Call audit(read_bytes), where read_bytes(project_relative_name) returns exact
archived bytes. Historical absolute paths remain nominal provenance identities.
Each call owns isolated counters and snapshots; no previous replay state is reused.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
import datetime
import hashlib
import json
import tarfile
import time
import io


def audit(read_bytes):
    """Return the full independent report using only supplied saved byte streams.

    A changed/missing virtual postguard input fails closed by raising; numerical
    and schema failures inside reconstruction are retained in the report.
    """
    ROOT = Path("/shared/external/iregi/iregi-rust") # Nominal historical identity only; no filesystem access.
    HERE = ROOT / 'target/rank7-numeric-jets-execution'
    PIN = {}
    def _bytes(path):
        path=Path(path); path=path if path.is_absolute() else ROOT/path
        relative=str(path.relative_to(ROOT))
        demand(".." not in Path(relative).parts,"virtual path escapes nominal project")
        body=read_bytes(relative)
        demand(type(body) is bytes,"read_bytes must return immutable bytes")
        return body
    def digest(body): return hashlib.sha256(body).hexdigest()
    def demand(ok, message):
        if not ok: raise ValueError(message)
    def parse(body):
        def pairs(items):
            d = {}
            for k,v in items:
                demand(k not in d,'duplicate JSON key'); d[k]=v
            return d
        return json.loads(body,parse_float=str,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)),object_pairs_hook=pairs)
    def read(path, expected=None):
        path=Path(path);path=path if path.is_absolute() else ROOT/path
        body=_bytes(path);actual=digest(body)
        demand(expected is None or actual==expected,'changed input '+str(path))
        PIN[str(path.relative_to(ROOT))]=actual
        return parse(body)
    def q(value):
        demand(type(value)==dict and set(value)=={'rational','precision','negative_sign','finite'},'operand metadata')
        demand(value['finite'] is True and type(value['rational']) is str,'native finite')
        result=F(value['rational'])
        demand(type(value['precision']) is int and value['precision']>0,'native precision')
        demand(type(value['negative_sign']) is bool and (result==0 or value['negative_sign']==(result<0)),'native sign')
        return result
    def z(value):
        demand(type(value) is list and len(value)==2,'complex width')
        return q(value[0]),q(value[1])
    def decimal(v):
        with localcontext() as c:
            c.prec=90
            return str(Decimal(v.numerator)/Decimal(v.denominator))
    def normdiff(a,b,degree,massorder,mu):
        natural=F(mu)**(degree-2*massorder)
        return sum(abs(x-y) for x,y in zip(a,b))/(natural+sum(abs(x) for x in b))

    BASIS=[[t,x,y,r-t-x-y] for r in range(8) for t in range(r,-1,-1) for x in range(r-t,-1,-1) for y in range(r-t-x,-1,-1)]
    SHAPE=[[0,0],[1,0],[0,1],[2,0],[1,1],[0,2]]
    NODES=range(-2,3)
    WEIGHTS=[[F(0),F(0),F(1),F(0),F(0)],[F(1,12),F(-2,3),F(0),F(2,3),F(-1,12)],[F(-1,24),F(2,3),F(-5,4),F(2,3),F(-1,24)]]
    TOL=F(1,10**10);PAIR=F(1,2**80);FD=F(1,2**70)
    CASES=['plain-f64','plain-dd','first-float128','first-float256','mixed-float128','mixed-float256','dot0-float128','dot0-float256','triple0-float128','triple0-float256','fd-float384']
    COUNTS={};MAX={};FAIL=[];EUCLIDEAN={}
    def test(a,b,d,k,mu,target,tolerance):
        err=normdiff(a,b,d,k,mu)
        COUNTS[target]=COUNTS.get(target,0)+1;MAX[target]=max(MAX.get(target,F(0)),err)
        if err>tolerance:FAIL.append(dict(target=target,index=COUNTS[target],error=decimal(err),limit=str(tolerance)))
        # Additional independent full-complex max(abs,relative) check. This is
        # reported separately and cannot silently replace the frozen gate metric.
        squared=sum((x-y)**2 for x,y in zip(a,b))/max(F(mu)**(2*(d-2*k)),sum(x*x for x in b))
        EUCLIDEAN[target]=max(EUCLIDEAN.get(target,F(0)),squared)

    def reconstruct():
        started=time.monotonic()
        report=dict(schema_version=1,status='failed_independent_saved_audit',passed=False,failures=FAIL,
            independent_of_producer=True,authorship_conflict=False,producer_imports=False,
            evaluator_or_integral_execution=False,native_execution=False,performance_qualified=False,
            rigorous_derivative_error_qualified=False,public_highpoint_Dual_qualified=False,
            typed_f64_or_DoubleFloat_Dual_tested=False,mutation_evidence_reviewed=False)
        try:
            manifest=read(HERE/'captures-manifest.json');comparison=read(HERE/'comparison-fixed.json')
            demand(set(manifest['captures'])==set(CASES) and comparison['passed'] is True and comparison['failures']==[], 'complete eleven saved cases')
            capsule=ROOT/'validation/quad-original-iregi-generalized-rank7'
            cm=read(capsule/'manifest.json','ccda92bdd0be40484b2d8762d479658ada0beb98eb610df7c96b44f7f521a0b0')
            payload=capsule/'payload.tar.gz';payloadbody=_bytes(payload)
            demand(digest(payloadbody)==cm['capsule_files']['payload.tar.gz']['sha256'],'quad archive hash')
            PIN[str(payload.relative_to(ROOT))]=digest(payloadbody)
            names={f'target/quad-generalized-rank7-anchors/capture-001/request-{i}.stdout':role for i,role in [(0,'unit'),(2,'dot0'),(4,'triple0')]}
            protocolname='target/quad-generalized-rank7-anchors/protocol.json'
            anchors={};quadprotocol=None
            with tarfile.open(fileobj=io.BytesIO(payloadbody),mode='r:gz') as archive:
                for member in archive:
                    if member.name not in names and member.name!=protocolname:continue
                    body=archive.extractfile(member).read();expect=cm['payload_members'][member.name]
                    demand(digest(body)==expect['sha256'] and len(body)==expect['bytes'],'quad member hash')
                    PIN['archive:'+member.name]=digest(body)
                    if member.name==protocolname:quadprotocol=parse(body);continue
                    text=body.decode();demand(text.splitlines().count('READY IREGI_REFERENCE_QP_V1')==1,'quad ready')
                    witness=[parse(line[10:]) for line in text.splitlines() if line.startswith('PRECISION ')]
                    demand(witness==[dict(dbl_kind=16,olo_kind=16,storage_bits=128,binary_digits=113,decimal_digits=33)],'quad precision')
                    result=[parse(line[7:]) for line in text.splitlines() if line.startswith('RESULT ')]
                    demand(len(result)==1 and result[0]['stable'] is True and result[0]['poles']==['uv1','ir1','ir2','finite'] and len(result[0]['moments'])==330,'quad array')
                    arrays=result[0]['moments'];demand(all(len(m)==4 and all(len(v)==2 for v in m) for m in arrays),'quad complete slots')
                    anchors[names[member.name]]=[tuple(F(v) for v in item) for moment in arrays for item in moment]
            demand(set(anchors)=={'unit','dot0','triple0'} and quadprotocol is not None,'quad anchor inventory')
            for i,power in [(0,1),(2,2),(4,3)]:
                case=quadprotocol['runtime']['cases'][i]
                demand(case['n']==2 and case['rank']==7 and case['powers']==[power,1] and case['h']==case['idim']==0 and case['mu']=='3','quad powers/dimensions')
                demand(case['propagators']==[dict(shift=['0','0','0','0'],mass_squared=['1','0'],power=power),dict(shift=['0','1','0','0'],mass_squared=['2','0'],power=1)],'quad exact routing')
            build=read(HERE/'build-002/receipt.json');demand(build['status']=='passed' and build['inputs_unchanged'] is True and not build['cleanup_errors'],'actual build receipt')
            demand(all(s['status']=='exited' and s['returncode']==0 and s['owned_group_gone'] is True for s in build['steps']),'build terminal groups')
            for name in ['main.rs','jets.rs']:
                path=HERE/'build-002/source-snapshot/crates/iregi-rust/examples/rank7_numeric_jets'/name
                raw=_bytes(path);expected=build['source_files']['crates/iregi-rust/examples/rank7_numeric_jets/'+name]
                demand(digest(raw)==expected,'actual built helper source');PIN[str(path.relative_to(ROOT))]=digest(raw)
            records={};decoded={};runtime=[];operandcount=0
            base=[F(v) for v in ['0','0','0','0','0','1','0','0','1','2','3']]
            for ci,name in enumerate(CASES):
                entry=manifest['captures'][name];record=read(entry['path'],entry['sha256']);records[name]=record
                folder=HERE/'captures'/(name+'-001');receipt=read(folder/'receipt.json');prereq=read(folder/'prerequisite.json')
                demand(receipt['status']=='passed' and receipt['stage']==name and receipt['inputs_unchanged'] is True and receipt['cleanup_errors']==[],'native terminal receipt')
                demand(receipt['driver_ledger_sha256']==entry['sha256'] and len(receipt['steps'])==1,'receipt ledger association')
                step=receipt['steps'][0]
                demand(step['status']=='exited' and step['returncode']==0 and step['owned_group_gone'] is True,'native owned group terminal')
                demand(step['command'][3]==build['product']['path'] and receipt['inputs'][build['product']['path']]==build['product']['sha256'],'same owned executable metadata')
                demand(prereq['runtime_receipt_sha256']==PIN[str((folder/'receipt.json').relative_to(ROOT))] and prereq['driver_ledger_sha256']==entry['sha256'] and prereq['failures']==[] and prereq['attempted_cases']==CASES[:ci+1],'incremental prerequisite association')
                demand(record['status']=='capture_complete_not_yet_qualified' and record['all_expected_outcomes'] is True and record['basis']==BASIS and record['settings']['propagators']==2 and record['settings']['rank']==7,'capture complete basis')
                demand(record['base_exact_rational']==list(map(str,base)),'fixed exact base')
                c=2 if name.startswith('first') else 6 if name.startswith('mixed') else 1
                shape=SHAPE[:2] if c==2 else SHAPE if c==6 else None
                demand(record['ordered_shape']==shape,'ordered jet shape')
                power=2 if name.startswith('dot0') else 3 if name.startswith('triple0') else 1
                demand(record['settings']['powers']==[power,1] and record['settings']['dimension_shift']==0 and record['algorithm_used']==('Ibp' if power>1 else 'PassarinoVeltman'),'actual method/powers')
                if c>1:
                    expected=[]
                    for rank in range(8):expected.append([[1,0,0],[0,1,0],[rank,0,0],[0,0,1],[0,rank-2,0],[rank*(rank-1)//2,0,0]])
                    demand([[[F(v) for v in row] for row in r] for r in record['exact_response_columns']]==expected,'independent Symbolica coefficients')
                if name=='fd-float384':
                    demand([[F(v) for v in row] for row in record['fd_exact_taylor_weights']]==WEIGHTS,'Symbolica saved FD weights')
                    expectedrows=[[v*((1+b*F(1,2**e))**2 if 8<=i<10 else 1+b*F(1,2**e))+(a*F(1,2**e) if i==8 else 0) for i,v in enumerate(base)] for e in [12,18,24] for a in NODES for b in NODES]
                    demand([[F(v) for v in row] for row in record['input_exact_rational']]==expectedrows,'all75exactFD inputs')
                else:
                    expectedrows=[]
                    for scale in [1,2]:
                        row=[]
                        for i,v0 in enumerate(base):
                            v=v0*scale**(2 if 8<=i<10 else 1)
                            jet=[v,F(i==8),v*(2 if 8<=i<10 else 1),F(0),F(0),v if 8<=i<10 else F(0)]
                            row.extend(jet[:2] if c==2 else jet if c==6 else [v])
                        expectedrows.append(row)
                    demand([[F(v) for v in row] for row in record['input_exact_rational']]==expectedrows,'independent exact jet inputs')
                calls=record['calls'];schedule=[('ordinary_fd75',list(range(75)))] if name=='fd-float384' else [('ordinary_odd3',[0,None,1])] if c==1 else [('static_base',[0]),('dynamic_odd3',[1,None,0]),('dynamic_empty',[])]
                demand(len(calls)==len(schedule),'full fixed schedule');decoded[name]={}
                for call,(label,indices) in zip(calls,schedule):
                    demand(call['name']==label and call['status']=='captured' and call['expected_outcomes'] is True and call['input_preserved'] is True and call['input_before']==call['input_after'],'call/input preservation')
                    demand(call['basis']==BASIS and call['components']==c and call['metadata']==dict(convention='IregiNative',tensor_weights='Components',dual_shape=shape),'call interpretation')
                    inp=[z(v) for v in call['input_before']];expectedinput=[]
                    for index in indices:
                        vals=list(expectedrows[0 if index is None else index])
                        if index is None:vals[10*c:11*c]=[F(0)]*c
                        expectedinput.extend((v,F(0)) for v in vals)
                    demand(inp==expectedinput and len(call['lanes'])==len(indices) and len(call['diagnostics'])==len(indices),'input/lane inventory')
                    work=call['execution'];active=sum(i is not None for i in indices)
                    demand(work['input_rows']==len(indices) and work['argument_rows']==work['reduction_rows']==active and not any(work[k] for k in ['fallback_rows','fallback_successes','analytic_rows','pentagon_box_rows']),'batched work attribution')
                    if not active:demand(not any(work.values()),'empty reset')
                    else:demand(work['master_rows']>=active and work['master_rows']%active==0 and work['master_family_batches']>0,'master batch evidence')
                    out=[]
                    for row,(lane,index) in enumerate(zip(call['lanes'],indices)):
                        demand(lane['lane']==row and lane['expected_outcome'] is True and lane['fallback_used'] is False and lane['analytic_used'] is False,'lane flags')
                        if index is None:
                            demand(lane['status'].startswith('InvalidInput(') and lane['values'] is None and call['diagnostics'][row]==[],'invalid lane null');out.append(None)
                        else:
                            demand(lane['status']=='Success' and len(lane['values'])==1320*c,'full array')
                            out.append([z(v) for v in lane['values']]);operandcount+=2*len(lane['values'])
                    decoded[name][label]=out
                if c>1:demand(calls[0]['lanes'][0]['values']==calls[1]['lanes'][2]['values'],'static/dynamic fullmetadata equality')
                runtime.append(dict(case=name,owned_group=step['owned_process_group'],owned_group_gone=True,receipt_elapsed=str(step['elapsed_seconds']),complete=True))
            def positives(name):
                return [('ordinary_odd3',0,1),('ordinary_odd3',2,2)] if not name.startswith(('first','mixed')) else [('static_base',0,1),('dynamic_odd3',0,2),('dynamic_odd3',2,1)]
            for name in CASES[:-1]:
                c=2 if name.startswith('first') else 6 if name.startswith('mixed') else 1
                power=2 if name.startswith('dot0') else 3 if name.startswith('triple0') else 1
                for call,row,scale in positives(name):
                    values=decoded[name][call][row]
                    for index,actual in enumerate(values):
                        moment,rem=divmod(index,4*c);slot,component=divmod(rem,c);d=sum(BASIS[moment]);k=power-1 if c==1 else SHAPE[component][0]
                        if c==1:expected=tuple(v*F(scale)**(d-2*k) for v in anchors[['unit','dot0','triple0'][k]][4*moment+slot])
                        else:
                            role,mult=[('unit',1),('dot0',1),('unit',d),('triple0',1),('dot0',d-2),('unit',d*(d-1)//2)][component]
                            expected=tuple(v*mult*F(scale)**(d-2*k) for v in anchors[role][4*moment+slot])
                        test(actual,expected,d,k,3*scale,'quad',TOL)
                p=positives(name);a=decoded[name][p[1][0]][p[1][1]];b=decoded[name][p[0][0]][p[0][1]]
                for index,(actual,previous) in enumerate(zip(a,b)):
                    moment,rem=divmod(index,4*c);component=rem%c;d=sum(BASIS[moment]);k=power-1 if c==1 else SHAPE[component][0]
                    test(actual,tuple(v*F(2)**(d-2*k) for v in previous),d,k,6,'scale',PAIR if 'float' in name else TOL)
            for prefix in ['first','mixed','dot0','triple0']:
                name=prefix+'-float128';high=prefix+'-float256';c=2 if prefix=='first' else 6 if prefix=='mixed' else 1;k0=1 if prefix=='dot0' else 2 if prefix=='triple0' else 0
                for call,row,scale in positives(name):
                    for index,(a,b) in enumerate(zip(decoded[name][call][row],decoded[high][call][row])):
                        moment,rem=divmod(index,4*c);k=k0 if c==1 else SHAPE[rem%c][0]
                        test(a,b,sum(BASIS[moment]),k,3*scale,'pair',PAIR)
            for bits in [128,256]:
                for profile in ['first','mixed']:
                    name=f'{profile}-float{bits}';c=2 if profile=='first' else 6
                    for call,row,scale in positives(name):
                        v=decoded[name][call][row]
                        for component,prefix,k in [(1,'dot0',1)]+([(3,'triple0',2)] if c==6 else []):
                            anchor=decoded[f'{prefix}-float{bits}']['ordinary_odd3'][0 if scale==1 else 2]
                            for index,expected in enumerate(anchor):test(v[index*c+component],expected,sum(BASIS[index//4]),k,3*scale,'mass',PAIR)
            for row,call,hr in [(0,'static_base',0),(2,'dynamic_odd3',0)]:
                for index,a in enumerate(decoded['plain-dd']['ordinary_odd3'][row]):
                    test(a,decoded['first-float128'][call][hr][index*2],sum(BASIS[index//4]),0,3 if row==0 else 6,'dd',PAIR)
            samples=decoded['fd-float384']['ordinary_fd75'];target=decoded['mixed-float256']['static_base'][0]
            fdmax=[F(0)]*3;resolved=unresolved=0;witness=[];fdvalues=0
            # Precompute only scalar stencil weights from the saved Symbolica
            # values. This is numeric contraction, not differentiation or AD.
            products={tuple(p):[(ai*5+bi,wa*wb) for ai,wa in enumerate(WEIGHTS[p[0]]) for bi,wb in enumerate(WEIGHTS[p[1]]) if wa and wb] for p in SHAPE}
            for index,expected in enumerate(target):
                moment,rem=divmod(index,24);slot,component=divmod(rem,6);ao,bo=SHAPE[component];errors=[]
                for level,exponent in enumerate([12,18,24]):
                    weighted=[(samples[level*25+node][moment*4+slot],weight) for node,weight in products[(ao,bo)]]
                    multiplier=F(2)**(exponent*(ao+bo))
                    actual=tuple(sum(weight*value[part] for value,weight in weighted)*multiplier for part in range(2))
                    err=normdiff(actual,expected,sum(BASIS[moment]),ao,3);errors.append(err);fdmax[level]=max(fdmax[level],err);fdvalues+=1
                if errors[-1]>FD:FAIL.append(dict(target='FD_accuracy',index=index,error=decimal(errors[-1])))
                for earlier,later in zip(errors,errors[1:]):
                    if earlier>FD:
                        demand(later<=earlier/16,'FD resolved transition insufficient')
                        resolved+=int(moment==0 and slot==3 and component==1)
                    else:
                        unresolved+=1;demand(later<=FD,'FD subthreshold transition left tolerance')
                if moment==0 and slot==3 and component==1:witness=list(map(decimal,errors))
            demand(resolved>0,'resolved nonpolynomial FD witness missing')
            expectedcounts={'quad':79200,'pair':36960,'mass':23760,'dd':2640,'scale':29040}
            demand(COUNTS==expectedcounts,'independent total comparison coverage')
            demand(comparison['comparison_counts']==dict(original_quad_response=79200,precision_128_256=36960,Rust_raised_power_mass_identity=23760,DoubleFloat_to_Float128=2640,scaled2_identity=29040),'producer count drift')
            mapping={'quad':'original_quad_response','pair':'precision_128_256','mass':'Rust_raised_power_mass_identity','dd':'DoubleFloat_to_Float128','scale':'scaled2_identity'}
            for k,v in MAX.items():demand(decimal(v)==comparison['max_errors'][mapping[k]] or abs(F(decimal(v))-F(comparison['max_errors'][mapping[k]]))<F(1,10**85),'producer numeric maximum differs')
            demand(resolved==comparison['fd_resolved_nonpolynomial_transitions'] and unresolved==comparison['fd_accuracy_floor_transitions'],'FD convergence counts drift')
            for actual,expected in zip(fdmax,comparison['fd_max_errors_by_step']):demand(abs(F(decimal(actual))-F(expected))<F(1,10**85),'FD maximum drift')
            report.update(passed=not FAIL,status='passed_independent_N2_initial11_saved_audit' if not FAIL else report['status'],comparison_counts=COUNTS,max_errors={k:decimal(v) for k,v in MAX.items()},additional_euclidean_max_squared={k:str(v) for k,v in EUCLIDEAN.items()},fd_reconstructed_components=fdvalues,fd_max_errors_by_step=list(map(decimal,fdmax)),fd_resolved_nonpolynomial_transitions=resolved,fd_accuracy_floor_transitions=unresolved,fd_nonpolynomial_witness_errors=witness,native_operands_checked=operandcount,capture_count=11,runtime_terminal_metadata=runtime,original_quad_arrays=3,original_quad_complex_slots=3960,authorship_note='This reviewer did not author or import compare_fixed.py or its N2 ancestors. Separate earlier N6 comparator authorship has no runtime/code import relationship.',scope='One massive spacelike N2 rank7 cumulative330moment family; ordinaryf64/DD and Float128/256static/dynamic first/mixed Dual paths, raisedpowers and saved ordinaryFloat384 finite differences.',limitations=['No typed f64 or DoubleFloat Dual carriers tested.','No public highpoint Dual or generalized alltopology qualification, rigorous backenderror enclosure or performance claim.','Build/native receipts and terminal process-group absence are checked as saved metadata, with selected helper source bindings; no executable, massive dependency closure or live process census rehashed.','Mutation-probe outcomes belong to the separate immutable companion and are not recomputed by this numeric replay.'])
        except Exception as exc:
            FAIL.append(dict(target='audit_structure',message=f'{type(exc).__name__}: {exc}'))
        report['input_sha256']=PIN;report['elapsed_seconds']=time.monotonic()-started;report['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        # Saved inputs must stay unchanged during this independent reconstruction.
        for name,expected in PIN.items():
            if not name.startswith('archive:'):demand(digest(_bytes(ROOT/name))==expected,'postguard '+name)
        report['portable_replay'] = True
        report['filesystem_or_process_access'] = False
        return report
    return reconstruct()
