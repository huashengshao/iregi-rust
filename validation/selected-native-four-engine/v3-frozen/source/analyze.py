"""Post-release quartet analysis; every reported ratio has TIRust in its numerator."""
from pathlib import Path
import itertools,json,math,random,sys
import admission_v3 as a
from preparation import validate_initialization
h=a.h
ENGINES=['baselineTIRust','candidateTIRust','iregi','collier']
RATIOS=[('baselineTIRust','iregi'),('candidateTIRust','iregi'),('baselineTIRust','collier'),('candidateTIRust','collier'),('candidateTIRust','baselineTIRust')]
ORDERS=list(itertools.permutations(ENGINES))*2
random.Random(173).shuffle(ORDERS)

def ratio(numerator,denominator,name,correct):
    assert len(numerator)==len(denominator)>0
    assert name[0] in ['baselineTIRust','candidateTIRust']
    result=h.ratio_summary(numerator,denominator,{'status':'passed' if correct else 'failed'})
    result['definition']=name[0]+' / '+name[1]+' paired quartet latency;99% bootstrap median CI;relative width<=2%'
    return result

def summarize_family(row,admitted=True):
    blocks=row.get('blocks',[]);timings={e:[]for e in ENGINES};short=0
    assert len(blocks)<=48
    for index,block in enumerate(blocks):
        assert block['index']==index and tuple(block['order'])==ORDERS[index]
        assert [v['engine']for v in block['engines']]==list(ORDERS[index]),'incomplete quartet'
        for value in block['engines']:
            assert type(value['iterations'])is int and value['iterations']==row['iterations']>0
            assert type(value['elapsed_ns'])in[int,float]and math.isfinite(value['elapsed_ns'])and value['elapsed_ns']>0
            assert type(value['ns_per_call'])in[int,float]and math.isfinite(value['ns_per_call'])and value['ns_per_call']>0
            if value['engine']in ['iregi','collier']:
                assert value['elapsed_ns']==value['ns_per_call']*value['iterations']
            else:assert value['ns_per_call']==value['elapsed_ns']/value['iterations']
            timings[value['engine']].append(value['ns_per_call']);short+=value['elapsed_ns']<100_000_000
    complete=admitted and len(blocks)==48 and row['status']=='completed' and row.get('before_after_qualification')=='passed'and short==0
    output={'id':row['id'],'batch':row['outer_batch'],'status':row['status'],'quartets':len(blocks),'short_blocks':short,'ratios':[],'engine_samples_ns':timings}
    for names in RATIOS:
        r={'numerator':names[0],'denominator':names[1],'definition':names[0]+' / '+names[1],'gate':'inconclusive-incomplete-family','statistics':None}
        if len(blocks)==48:
            stat=ratio(timings[names[0]],timings[names[1]],names,complete)
            r.update(statistics=stat,gate=stat['gate']if complete else ('inconclusive-short-block'if short else 'correctness-or-cohort-failed'))
            r['order_strata']={}
            for before in [True,False]:
                indices=[i for i,b in enumerate(blocks)if (b['order'].index(names[0])<b['order'].index(names[1]))==before]
                assert len(indices)==24
                r['order_strata']['numerator_first'if before else'denominator_first']=ratio([timings[names[0]][i]for i in indices],[timings[names[1]][i]for i in indices],names,complete)
            r['slower_pairs']=sum(x>y for x,y in zip(timings[names[0]],timings[names[1]]))
        output['ratios'].append(r)
    return output

def validate_terminal(receipt):
    assert receipt['mode']=='timing'
    assert receipt['status']=='completed'
    assert receipt['cleanup_errors']==[]
    assert receipt['deadline_exceeded'] is False
    elapsed=[receipt[key]for key in ['numerical_elapsed_seconds','cleanup_finished_elapsed_seconds','elapsed_seconds']]
    assert all(type(value)in[int,float]and math.isfinite(value)for value in elapsed)
    assert 0<=elapsed[0]<=elapsed[1]<=elapsed[2]<=700

def main():
    run=Path(sys.argv[1]);receipt={};raw=[];global_errors=[]
    cases=a.read(a.ROOT/'validation/native-master-replay/inputs.json')
    coordinates=[(c['id'],b)for c in cases for b in [1,32]]
    q={};cq={};inventory={}
    try:
        q=a.read(a.HERE/'qualification-001/results.json')
        cq=a.read(a.V2/'qualification-001/results.json')
        inventory=a.read(a.HERE/'control-inventory.json')['controls']
    except Exception as error:global_errors.append('qualification parsing: '+str(error))
    try:
        receipt=a.read(run/'receipt.json')
        validate_terminal(receipt)
        assert receipt['runtime_cap_seconds']==700 and receipt['quartets']==48
        assert receipt['orders']==[list(o)for o in ORDERS]
        assert [(x['numerator'],x['denominator'])for x in receipt['ratio_inventory']]==RATIOS
        assert [(r['id'],r['outer_batch'])for r in receipt['rows']]==coordinates
        assert receipt['inputs_unchanged'] is True and 'error'not in receipt
        assert receipt['process_exit_codes']=={'probe':0,'iregi':0,'collier':0}
        for path,expected in receipt['input_sha256'].items():assert a.sha(Path(path))==expected,path
        assert receipt['input_sha256'][str(a.HERE/'qualification-001/results.json')]==a.sha(a.HERE/'qualification-001/results.json')
        assert receipt['input_sha256'][str(a.V2/'qualification-001/results.json')]==a.sha(a.V2/'qualification-001/results.json')
        assert receipt['input_sha256'][str(a.ROOT/'validation/benchmark/run.py')]==q['helper_sha256']
        for stage in ['controls_before','controls_after']:
            a.base.validate_controls(receipt[stage],inventory)
            assert receipt[stage]==q['controls']
    except Exception as error:global_errors.append('global admission: '+str(error))
    try:
        assert a.sha(run/'raw.jsonl')==receipt['raw_sha256']
        raw=[json.loads(line)for line in (run/'raw.jsonl').read_text().splitlines()]
        assert [r['serial']for r in raw]==list(range(len(raw)))and len(raw)==receipt['raw_response_count']
    except Exception as error:global_errors.append('raw log admission: '+str(error))
    try:
        references=validate_initialization(receipt,raw,q,cases)
        controls=[r for r in raw if r.get('kind')=='controls']
        assert len(controls)==2 and [r['stage']for r in controls]==['before','after']
        for r in controls:
            assert r['engine']=='bothTIRust'and r['response']==receipt['controls_'+r['stage']]
            references.append(r['serial'])
        for row in receipt['rows']:
            references.extend(row.get('before_raw_serials',[]));references.extend(row.get('after_raw_serials',[]))
            for group in row.get('calibration',[]):references.extend(v['raw_serial']for v in group)
            for block in row.get('blocks',[]):references.extend(v['raw_serial']for v in block['engines'])
        assert all(type(i)is int for i in references)
        assert sorted(references)==list(range(len(raw))),'omitted, duplicated or extra raw response'
    except Exception as error:global_errors.append('complete raw accounting: '+str(error))
    rows=[]
    for index,(case,batch)in enumerate((c,b)for c in cases for b in [1,32]):
        try:row=receipt['rows'][index];assert(row['id'],row['outer_batch'])==coordinates[index]
        except Exception:row={'id':case['id'],'outer_batch':batch,'status':'missing-or-misidentified'}
        samples=case['samples'][:batch];family_errors=[]
        try:
            assert row.get('before_after_qualification')=='passed'
            seen=set()
            def captures(stage):
                serials=row[stage+'_raw_serials'];assert type(serials)is list and len(serials)==3
                assert all(type(i)is int and 0<=i<len(raw)for i in serials)
                assert len(set(serials))==3 and not seen.intersection(serials);seen.update(serials)
                values=[raw[i]for i in serials]
                assert [r['engine']for r in values]==['bothTIRust','iregi','collier']
                for r in values:assert r['stage']==stage and r['kind']=='qualification'and r['id']==case['id']and r['batch']==batch
                pair,ref,col=[r['response']for r in values]
                a.base.validate_response(pair,case,samples)
                assert ref['id']==case['id']and ref['stable']is True
                a.check_collier(col,case,samples,pole_check=True)
                a.compare_collier(col,pair,ref,case,samples)
                for engine in ['baseline','candidate']:assert h.compare(pair[engine],ref,case,samples)['status']=='passed'
                return pair,ref,col
            pair,ref,col=captures('before');ap,ar,ac=captures('after')
            assert a.base.canonical(pair)==a.base.canonical(ap)==a.base.canonical(q['rows'][index]['response'])
            assert a.canonical_collier(col)==a.canonical_collier(ac)==a.canonical_collier(cq['rows'][index]['before'])
            for field in ['id','stable','clock_ticks_per_second','lanes']:
                assert json.dumps(ref[field],sort_keys=True)==json.dumps(ar[field],sort_keys=True)==json.dumps(q['rows'][index]['reference'][field],sort_keys=True)
            for stage,groups in [('calibration',row.get('calibration',[])),('acceptance',[b['engines']for b in row.get('blocks',[])])]:
                assert len(groups)<=(8 if stage=='calibration' else 48)
                for block_index,group in enumerate(groups):
                    assert len(group)==4 and [v['engine']for v in group]==(ENGINES if stage=='calibration'else list(ORDERS[block_index]))
                    iterations=group[0]['iterations'];assert type(iterations)is int and iterations>0
                    for value in group:
                        serial=value['raw_serial'];assert type(serial)is int and 0<=serial<len(raw)and serial not in seen;seen.add(serial)
                        rr=raw[serial];assert rr['stage']==stage and rr['id']==row['id']and rr['batch']==batch
                        assert rr['engine']==value['engine']and rr['block']==block_index and rr['iterations']==value['iterations']==iterations
                        if rr['engine']=='collier':elapsed=a.timed_collier(rr['response'],col,iterations,case,samples)
                        elif rr['engine']=='iregi':elapsed=a.base.validate_reference(rr['response'],ref,iterations,case,samples)
                        else:
                            selector={'baselineTIRust':'baseline','candidateTIRust':'candidate'}[rr['engine']]
                            elapsed=a.base.validate_timed(rr['response'],pair[selector],selector,iterations,case,samples)
                        assert math.isfinite(elapsed)and elapsed>0 and elapsed==value['elapsed_ns']and rr['response']['total_ns'][0]==value['ns_per_call']
            assert row['calibration']and len(row['calibration'])<=8
            predicted_n=1
            for round_index,values in enumerate(row['calibration']):
                assert all(v['iterations']==predicted_n for v in values)
                minimum=min(v['elapsed_ns']for v in values)
                if round_index+1<len(row['calibration']):
                    assert minimum<100_000_000,'calibration continued after admission'
                    predicted_n=max(predicted_n+1,math.ceil(predicted_n*110_000_000/minimum))
                else:assert minimum>=100_000_000
            assert predicted_n==row['iterations']
        except Exception as error:family_errors.append(str(error))
        try:
            result=summarize_family(row,admitted=not global_errors and not family_errors)
            result['admission_errors']=global_errors+family_errors;rows.append(result)
        except Exception as error:
            rows.append({'id':case['id'],'batch':batch,'status':'analysis-admission-failed','admission_errors':global_errors+family_errors+[str(error)],'ratios':[{'numerator':n,'denominator':d,'definition':n+' / '+d,'gate':'analysis-admission-failed','statistics':None}for n,d in RATIOS]})
    result={'status':'analyzed-all-eight-families','global_admission_errors':global_errors,'scope':'Only same-quartet TIRust/reference ratios; historical cohorts not combined','receipt_sha256':a.sha(run/'receipt.json')if(run/'receipt.json').exists()else None,'raw_sha256':a.sha(run/'raw.jsonl')if(run/'raw.jsonl').exists()else None,'analysis_source_sha256':a.sha(Path(__file__)),'rows':rows}
    (run/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'families':len(rows),'global_admission_errors':global_errors,'gates':{n+'/'+d:{g:sum(r['gate']==g for row in rows for r in row['ratios']if r['numerator']==n and r['denominator']==d)for g in sorted({r['gate']for row in rows for r in row['ratios']if r['numerator']==n and r['denominator']==d})}for n,d in RATIOS}}))
if __name__=='__main__':main()
