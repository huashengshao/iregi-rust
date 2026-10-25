"""Independent saved-only six-array audit; stdlib/Fraction, no producer imports."""
from pathlib import Path, PurePosixPath
from fractions import Fraction as F
from decimal import Decimal, localcontext
from collections import Counter
import hashlib
import json
import re

PREFIX = '/shared/external/iregi/iregi-rust/'
BASE = 'target/quad-low-n-rank6-dot-triple'
FIXED_PROTOCOL = '6c36ac2a890cb526ab9c89e2b6b11c3fa82fc4783014616695a2e648bf3506af'
FIXED_CAPTURE = '7f02de0501efd2ec6063ffb568788ef58cd00da7b8143b43ee4179d855dfbd9d'
FIXED_COMPARISON = '495d25d18a643769669a39e64ae19789c66a04e6d0380f0f905fc5a9bd6fa948'
TOKEN = re.compile(r'\s*[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?\s*')
POINTS = [(F(0),F(0),F(0),F(0)),(F(0),F(1),F(0),F(0)),(F(0),F(0),F(1),F(0)),(F(0),F(0),F(0),F(1)),(F(1,2),F(0),F(0),F(0))]
MASSES = [1,2,3,4,2]
LIMIT = F(1,10**20)


def audit(read_bytes):
    """Return deterministic receipt from original project-relative alias bytes."""
    checked = {}; checks = 0
    def need(ok, message):
        nonlocal checks
        checks += 1
        if not ok: raise AssertionError(message)
    def alias(path):
        name = str(path)
        if name.startswith(PREFIX): name = name[len(PREFIX):]
        p = PurePosixPath(name)
        need(not p.is_absolute() and '..' not in p.parts and str(p)==name, 'safe saved alias')
        return name
    def raw(path):
        name = alias(path); data = read_bytes(name)
        need(type(data) is bytes, 'raw saved bytes')
        checked[name] = {'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
        return data
    def digest(path): return hashlib.sha256(raw(path)).hexdigest()
    def unique(items):
        result = {}
        for key,value in items:
            need(key not in result, 'duplicate JSON key'); result[key]=value
        return result
    def decode(body):
        return json.loads(body,parse_float=Decimal,object_pairs_hook=unique,
                          parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    def load(path): return decode(raw(path))
    def cumulative(rank):
        rows=[]
        for degree in range(rank+1):
            for time in range(degree,-1,-1):
                for x in range(degree-time,-1,-1):
                    for y in range(degree-time-x,-1,-1):rows.append([time,x,y,degree-time-x-y])
        return rows
    basis=cumulative(6); need(len(basis)==210 and cumulative(7)[:210]==basis,'native cumulative Cartesian ordering')
    def native(body,ident,moments):
        lines=body.decode().splitlines()
        need(lines.count('READY IREGI_REFERENCE_QP_V1')==1,'one ready marker')
        precision=[decode(x[len('PRECISION '):])for x in lines if x.startswith('PRECISION ')]
        need(precision==[{'dbl_kind':16,'olo_kind':16,'storage_bits':128,'binary_digits':113,'decimal_digits':33}],'quad precision metadata')
        responses=[decode(x[len('RESULT '):])for x in lines if x.startswith('RESULT ')]
        need(len(responses)==1 and type(responses[0])is dict,'one result object')
        d=responses[0]
        need(d.get('id')==ident and type(d.get('stable'))is bool and d['stable']is True,'stable typed response identity')
        need(d.get('error')is None and d.get('poles')==['uv1','ir1','ir2','finite'],'native Laurent separation/error')
        need(type(d.get('moments'))is list and len(d['moments'])==moments,'complete native moment array')
        values=[]
        for moment in d['moments']:
            need(type(moment)is list and len(moment)==4,'four native slots')
            row=[]
            for z in moment:
                need(type(z)is list and len(z)==2 and all(type(s)is str and TOKEN.fullmatch(s)for s in z),'finite quoted decimal pair')
                row.append(tuple(F(s)for s in z))
            values.append(row)
        return d,values
    def request(body,ident,api,n,rank,powers):
        lines=body.decode().splitlines();header=lines[0].split()
        need(len(header)==10 and header[:7]==['EVAL',ident,api,'0',str(n),str(rank),'0'] and list(map(F,header[7:]))==[F(3),F(0),F(1,10**6)],'exact API/idim=2h/scale/real-mass/threshold mapping')
        need(len(lines)==n+2 and lines[-1]=='QUIT','one complete request')
        for i,line in enumerate(lines[1:-1]):
            need(list(map(F,line.split()))==list(POINTS[i])+[F(MASSES[i]),F(0),F(powers[i])],'exact canonical kinematics and power placement')
    def norm(z):return z[0]**2+z[1]**2
    def display(e):
        with localcontext()as c:
            c.prec=100;return str((Decimal(e.numerator)/Decimal(e.denominator)).sqrt())
    protocol=load(BASE+'/protocol.json'); need(digest(BASE+'/protocol.json')==FIXED_PROTOCOL,'frozen protocol')
    capture=load(BASE+'/capture-001/receipt.json'); need(digest(BASE+'/capture-001/receipt.json')==FIXED_CAPTURE,'frozen capture')
    compared=load(BASE+'/comparison.json'); need(digest(BASE+'/comparison.json')==FIXED_COMPARISON,'frozen producer comparison')
    release=load(BASE+'/numerical-release.json')
    source_review=load(BASE+'/source-review.json'); grant=load(BASE+'/root-grant.json')
    need(source_review['status']=='passed_independent_source_runner_comparator_review'and source_review['findings']==[]and source_review['protocol_sha256']==FIXED_PROTOCOL,'source/call review pin')
    need(grant['status']=='granted'and grant['grantor']=='/root'and grant['protocol_sha256']==FIXED_PROTOCOL and grant['review_sha256']==digest(BASE+'/source-review.json'),'root authorization pin')
    ids=[f'n{n}_rank6_first_'+suffix for n in(1,4,5)for suffix in('dot2','power3')]
    need([x['id']for x in protocol['cases']]==ids==grant['cases']==capture['native_cases_executed'],'all six exact cases')
    need(capture['status']=='terminal_capture'and capture['protocol_sha256']==FIXED_PROTOCOL and capture['inputs_unchanged']is True and capture['cleanup_errors']==[]and capture['cancellation']is None,'terminal capture/guards')
    need(capture['aggregate_seconds']==600 and capture['cleanup_reserve_seconds']==60 and capture['cpu']==26 and 0<=F(str(capture['elapsed_seconds']))<=600,'finite aggregate cap')
    need(capture['automatic_retry']is False and capture['new_compilation']is False and capture['finite_accuracy_qualified']is False and capture['performance_evidence']is False,'scope exclusions')
    need(len(capture['steps'])==6 and release['status']=='released'and len(release['groups'])==6 and release['capture_receipt_sha256']==FIXED_CAPTURE and release['comparison_sha256']==FIXED_COMPARISON,'saved release correspondence')
    need(all(capture['inputs'].get(name)==value for name,value in protocol['bindings'].items()),'declared narrow input hashes retained in terminal receipt')
    need(capture['inputs'][protocol['binary']]==protocol['binary_sha256']=='9d89e79be5e844e0f9c5d4a125968d1545e4412965eea68d5848abf78a9693d2','qualified historical binary digest attestation')
    for path in [BASE+'/protocol.json',BASE+'/source-review.json',BASE+'/root-grant.json']:
        need(capture['inputs'][PREFIX+path]==digest(path),'guarded protocol/review/grant source')
    for name,value in capture['outputs'].items():need(digest(BASE+'/capture-001/'+name)==value,'complete saved small output hash')
    anchors=[]
    for n in(1,4,5):
        a=protocol['ordinary_unit_anchors'][str(n)]
        need(digest(a['raw'])==a['raw_sha256']and digest(a['request'])==a['request_sha256'],'unit routing anchor pins')
        request(raw(a['request']),a['id'],'tensor',n,7,[1]*n)
        _,v=native(raw(a['raw']),a['id'],330)
        need(a['mu']=='3'and a['rank']==7 and a['moments']==330,'ordinary unit anchor metadata')
        expected=[{'shift':[str(x)for x in POINTS[i]],'mass_squared':[str(MASSES[i]),'0'],'power':1}for i in range(n)]
        need(a['unit_propagators']==expected,'unit anchor canonical routing')
        anchors.append({'n':n,'id':a['id'],'moments':330,'complex_slots':1320,'finite_compared_to_dotted':False,'native_values_sha256':hashlib.sha256(json.dumps([[[str(x)for x in z]for z in row]for row in v],separators=(',',':')).encode()).hexdigest()})
    records=[];case_reports=[];all_values=[]
    for index,(case,ident)in enumerate(zip(protocol['cases'],ids)):
        n=(1,4,5)[index//2];power=(2,3)[index%2];powers=[power]+[1]*(n-1);expected_absent=[0,1,2,3]if n==1 else[0]if n==4 else[]
        need(case['id']==ident and case['n']==n and case['rank']==6 and case['api']=='general'and case['mode']==case['h']==case['idim']==0 and case['mu']=='3'and case['powers']==powers and case['dotted_propagator_index']==0 and case['absent_axes']==expected_absent,'six accepted request semantics')
        need(case['cap_seconds']==60 and case['moments']==210 and case['complex_slots']==840,'case bounds/output shape')
        need(digest(case['request'])==case['request_sha256'],'new exact request hash');request(raw(case['request']),ident,'general',n,6,powers)
        expected_props=[{'shift':[str(x)for x in POINTS[i]],'mass_squared':[str(MASSES[i]),'0'],'power':powers[i]}for i in range(n)]
        need(case['propagators']==expected_props,'protocol exact propagators')
        need([dict(x,power=1)for x in case['propagators']]==protocol['ordinary_unit_anchors'][str(n)]['unit_propagators'],'only powers differ from unit anchor')
        need(min(MASSES[:n])>=1 and max(x[0]for x in POINTS[:n])-min(x[0]for x in POINTS[:n])<=F(1,2),'retained positive-F bound applicability')
        need(all(all(point[axis]==0 for point in POINTS[:n])for axis in expected_absent),'reflection parity axes absent from every denominator')
        step=capture['steps'][index];rel=release['groups'][index]
        expected_command=[protocol['tools']['taskset'],'-c','26',protocol['tools']['python'],protocol['capture_worker'],'--binary',protocol['binary'],'--input',case['request'],'--stdout',protocol['directory']+f'/request-{index}.stdout','--stderr',protocol['directory']+f'/request-{index}.stderr']
        need(step['label']==ident and step['command']==expected_command and step['status']=='exited'and step['returncode']==0 and step['owned_group_gone']is True and step['timeout_seconds']==60 and not step.get('timeout')and 'error'not in step,'bounded exact native command outcome')
        need(rel['label']==ident and rel['owned_process_group']==step['owned_process_group']and rel['actually_absent']is True,'saved PG release attestation only')
        body=raw(BASE+f'/capture-001/request-{index}.stdout');_,values=native(body,ident,210);all_values.extend(values)
        before=len(records)
        for moment,alpha in enumerate(basis):
            delta=sum(alpha)+4-2*sum(powers);unit=F(9)**delta
            targets=[('positive_F_IR_zero',1),('positive_F_IR_zero',2)]
            if delta<0:targets.append(('convergent_UV_zero',0))
            if any(alpha[axis]%2 for axis in expected_absent):targets.extend(('origin_tadpole_or_absent_axis_parity_zero',slot)for slot in range(4))
            for kind,slot in targets:
                e=norm(values[moment][slot])/unit
                records.append({'kind':kind,'case':ident,'moment':moment,'exponents':alpha,'slot':slot,'squared_error':str(e),'error':display(e),'limit_squared':str(LIMIT),'passed':e<=LIMIT})
        counts=Counter(x['kind']for x in records[before:])
        case_reports.append({'id':ident,'complete_complex_slots':840,'stable':True,'gate_counts':dict(counts),'raw_nonzero_by_slot':[sum(norm(row[s])!=0 for row in values)for s in range(4)],'finite_coefficients_independently_certified':False})
    need(len(all_values)*4==5040 and len(records)==5321,'all5040values and5321control records')
    counts=Counter(x['kind']for x in records);need(counts=={'positive_F_IR_zero':2520,'convergent_UV_zero':761,'origin_tadpole_or_absent_axis_parity_zero':2040},'all applicable identity gates')
    need(all(x['passed']for x in records),'every applicable identity passes without projection')
    need(len(compared['records'])==len(records),'complete saved records')
    for a,b in zip(compared['records'],records):
        need(type(a['passed'])is bool and all(type(x)is int for x in a['exponents'])and type(a['slot'])is int and type(a['moment'])is int,'strict record types')
        need(a==b,'independent exact identity error/labels/decision')
    need(compared['status']=='passed_restricted_low_N_rank6_dot_triple_reference_controls'and compared['failures']==[]and compared['complete_complex_slots']==5040,'producer restricted outcome')
    need(compared['finite_coefficients_independently_certified']is False and compared['Rust_Dual_physical_or_performance_qualified']is False and compared['native_poles_projected_or_merged']is False,'finite/reference scope retained')
    need(all(x['eligible_reference']is True for x in compared['cases'])and [x['represented_nonzero_by_slot']for x in compared['cases']]==[x['raw_nonzero_by_slot']for x in case_reports],'all reference availability/nonzero poles retained')
    need(all(x['finite_compared_to_dotted']is False for x in compared['ordinary_unit_correspondence']),'unit anchors are correspondence only')
    controls=[]
    sample=raw(BASE+'/capture-001/request-0.stdout')
    def rejects(label,body):
        try:native(body,ids[0],210)
        except(AssertionError,ValueError,KeyError,TypeError):controls.append(label)
        else:raise AssertionError('parser control accepted '+label)
    lines=sample.decode().splitlines();resultline=next(x for x in lines if x.startswith('RESULT '));response=decode(resultline[7:])
    rejects('duplicate_result',sample+b'\n'+resultline.encode()+b'\n')
    altered=dict(response);altered['moments']=response['moments'][:-1];rejects('partial_array','\n'.join([x for x in lines if not x.startswith('RESULT ')]+['RESULT '+json.dumps(altered)]).encode())
    altered=decode(resultline[7:]);altered['moments'][0][0]=[0,'0'];rejects('unquoted_component','\n'.join([x for x in lines if not x.startswith('RESULT ')]+['RESULT '+json.dumps(altered)]).encode())
    rejects('duplicate_JSON_key','\n'.join([x for x in lines if not x.startswith('RESULT ')]+['RESULT '+resultline[7:-1]+',"id":"duplicate"}']).encode())
    return {'status':'passed_independent_saved_low_N_rank6_dot_triple_reference_audit','reviewer':'/root/dual_pilot_finish/runner_review','checks':checks,'protocol_sha256':FIXED_PROTOCOL,'capture_receipt_sha256':FIXED_CAPTURE,'comparison_sha256':FIXED_COMPARISON,'complete_new_complex_slots':5040,'ordinary_unit_anchor_complex_slots_parsed':3960,'identity_records_recomputed':5321,'identity_gate_counts':dict(counts),'identity_failed':0,'all_native_values_sha256':hashlib.sha256(json.dumps([[[str(x)for x in z]for z in row]for row in all_values],separators=(',',':')).encode()).hexdigest(),'cases':case_reports,'ordinary_unit_anchors':anchors,'negative_controls_rejected':controls,'checked_aliases':checked,'declared_guard_map_matched_without_broad_live_source_rehash':True,'finite_coefficients_independently_certified':False,'Rust_Dual_physical_or_performance_qualified':False,'new_native_compilers_integrals_producer_imports_or_PID_probes':False,'omitted_native_or_external_tool_hashes_freshly_verified':False,'scope':'Six originalquad reference arrays: exact routing/powers/schema and applicable positive-F IR, superficial-degree UV and absent-axis parity identities only. Unit anchors establish routing and schema, not equality to dotted finite coefficients.113-bit storage does not certify33-digit achieved accuracy.'}


def main():
    root=Path.cwd().resolve();out=root/BASE/'independent/review.json'
    if out.exists():raise ValueError('preserve prior audit')
    result=audit(lambda name:(root/name).read_bytes())
    result['checker_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(out,hashlib.sha256(out.read_bytes()).hexdigest(),result['checks'])


if __name__=='__main__':main()
