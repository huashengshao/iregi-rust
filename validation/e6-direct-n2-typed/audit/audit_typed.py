#!/usr/bin/env python3
"""Exact recorded-number audit, without symbolic algebra or numerical reruns."""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT/'target/e6-direct-n2-typed'
CLOSURE = ROOT/'target/e6-direct-n2'
KINDS = {'f64':(53,40),'dd':(106,80),'float128':(128,80),'float256':(256,128),'float384':(384,128)}
SHAPES = {4:[[0,0],[1,0],[0,1],[1,1]],6:[[0,0],[1,0],[0,1],[2,0],[1,1],[2,1]]}


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def point(value):
    return Q(value['real']),Q(value['imaginary'])


def mul(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def scale(a,b):
    return a[0]*b,a[1]*b


def divide(a,b):
    norm = b[0]*b[0]+b[1]*b[1]
    assert norm != 0
    return (a[0]*b[0]+a[1]*b[1])/norm,(a[1]*b[0]-a[0]*b[1])/norm


def identity(m,a,b,c):
    """Finite scalar coefficient identities; not a polynomial/series engine."""
    m2=mul(m,m);m3=mul(m2,m);m4=mul(m3,m);m5=mul(m4,m)
    values={(0,0):divide((Q(-1,24),Q(0)),m2),
            (1,0):divide(scale(a,Q(1,12)),m3),
            (0,1):divide(scale(b,Q(1,12)),m3),
            (2,0):divide(scale(mul(a,a),Q(-1,8)),m4),
            (1,1):divide(scale(mul(a,b),Q(-1,4)),m4),
            (2,1):divide(scale(mul(mul(a,a),b),Q(1,2)),m5)}
    return [values[tuple(degree)] for degree in SHAPES[c]]


def expected_inputs(kind,c):
    z=(Q(0),Q(0));seed=Q(1,2**64)
    common=[z]*(16*c)
    for mass in range(10,15):
        common[mass*c]=(Q(2),Q(-1))
        common[mass*c+1]=(seed,seed/2)
        common[mass*c+2]=(-seed/2,seed)
    common[15*c]=(Q(1),Q(0))
    rows=[common.copy() for _ in range(13)]
    rows[1][15*c]=(Q(4),Q(0));rows[1][15*c+1]=(Q(7),Q(0))
    for mass in range(10,15):
        rows[2][mass*c]=(Q(2)+(Q(0) if kind=='f64' else Q(1,2**80)),Q(-1))
        rows[4][mass*c]=(Q(3),Q(-1,2))
        rows[6][mass*c+1]=(Q(1),Q(1,2));rows[6][mass*c+2]=(Q(-1,2),Q(1))
        for component in range(1,c):rows[8][mass*c+component]=z
        rows[11][mass*c]=(Q(2),Q(0))
    rows[3][10*c]=(Q(2),Q(1));rows[5][0]=(Q(2),Q(0))
    rows[7][15*c]=(Q(-1),Q(0));rows[9][0]=(Q(0),seed);rows[12][10*c]=z
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--base',type=Path,default=RUNTIME)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();base=args.base.resolve()
    destination=args.output or base/'audit/result.json'
    assert not destination.exists(),'Preserve prior audit results'
    failures=[];counts={};hashes={};groups={};group_reports=[];convergence=[]

    def check(value,label,category='numerical'):
        counts[category]=counts.get(category,0)+1
        if not value:failures.append({'category':category,'label':label})

    def hashed(path):
        digest=sha(path);hashes[str(path.relative_to(ROOT))]=digest;return digest

    def read(name):return json.loads((base/name).read_text())
    build=read('build.json');prep=read('preparation.json');summary=read('run-summary.json')
    source_manifest=read('source-manifest.json')
    closure_prep=json.loads((ROOT/prep['closure_preparation']).read_text())
    upstream=json.loads((CLOSURE/'upstream-preparation.json').read_text())
    binary_hash=hashed(RUNTIME/'validate');build_hash=hashed(base/'build.json')
    manifest_hash=hashed(base/'source-manifest.json');runner_hash=hashed(base/'run.py')
    check(build['exit_code']==0 and build['sources_unchanged'] and build['closure_unchanged'],'successful unchanged build','provenance')
    check(binary_hash==build['binary_sha256'] and (RUNTIME/'validate').stat().st_size==build['binary_bytes'],'actual compiled binary','provenance')
    check(build['sources']==source_manifest,'build/source manifest equality','provenance')
    for name in ['review-before-compute.json','audit/review-before-compute.json']:
        review=read(name);check(review['source_sha256']==source_manifest,'reviewed compiled sources: '+name,'provenance');hashed(base/name)
        check(not review['unresolved_material_findings'] if 'unresolved_material_findings' in review else not review['unresolved_material_source_findings'],'no unresolved source findings: '+name,'provenance')
    audit_review=read('audit/review-before-compute.json')
    check(hashed(base/'audit/strategy.md')==audit_review['strategy_sha256'],'audit strategy reviewed hash','provenance')
    for path,digest in source_manifest.items():
        relative=Path(path).relative_to(RUNTIME.relative_to(ROOT))
        check(hashed(ROOT/path)==hashed(base/relative)==digest,'retained and audit-base compiled source: '+path,'provenance')
    check(hashed(base/'source/near_vacuum_e6.rs')==hashed(ROOT/prep['engine_source'])==prep['engine_sha256'],'engine unchanged from durable checkpoint','provenance')
    check(hashed(ROOT/prep['prior_qualification'])==prep['prior_qualification_sha256'],'prior qualification immutable','provenance')
    check(hashed(ROOT/prep['closure_preparation'])==prep['closure_preparation_sha256'],'retained closure preparation','provenance')
    check(hashed(base/'preparation.json')==build['preparation_sha256'],'build binds typed preparation','provenance')
    check(hashed(base/'build.py')==build['runner_sha256'] and hashed(base/'build.log')==build['build_log_sha256'],'build runner and log','provenance')
    expected_command=['taskset','-c','18,19','rustc','--edition=2024','--crate-name','e6_direct_n2_typed',str(RUNTIME/'source/typed.rs'),'-C','opt-level=0','-C','debuginfo=0','-C','strip=debuginfo','-L',f'dependency={CLOSURE/"deps"}','-L',f'native={CLOSURE/"native"}']
    for name,item in closure_prep['artifacts'].items():expected_command+=['--extern',f'{name}={ROOT/item["frozen"]}']
    expected_command+=['-o',str(RUNTIME/'validate')]
    check(build['command']==expected_command,'exact frozen build command','provenance')
    check(build['compile_environment_overrides']=={'CARGO_CRATE_NAME':'e6_direct_n2_typed'} and build['timeout_seconds']==180,'explicit bounded compile environment','provenance')
    files={item['frozen']:item for item in closure_prep['files']}
    check(len(files)==len(closure_prep['files'])==116,'116 unique retained dependency files','provenance')
    actual={str(path.relative_to(ROOT)) for directory in ['deps','native'] for path in (CLOSURE/directory).iterdir() if path.is_file()}
    check(set(files)==actual,'complete dependency/native file set','provenance')
    for path,item in files.items():
        check(hashed(ROOT/path)==item['sha256'] and (ROOT/path).stat().st_size==item['bytes'],'retained dependency bytes and size: '+path,'provenance')
    check(hashed(CLOSURE/'upstream-preparation.json')==closure_prep['upstream_preparation_sha256'],'upstream dependency preparation','provenance')
    for name,item in closure_prep['artifacts'].items():
        check({k:v for k,v in item.items() if k!='frozen'}==upstream['artifacts'][name],'selected artifact upstream lineage: '+name,'provenance')
        check(item['sha256']==files[item['frozen']]['sha256'],'selected archive in retained closure: '+name,'provenance')
    check(hashed(ROOT/upstream['cargo_build_log'])==upstream['cargo_build_log_sha256'],'underlying Cargo build log','provenance')
    check(hashed(ROOT/upstream['cargo_qualification'])==upstream['cargo_qualification_sha256'],'underlying Cargo qualification','provenance')
    check(summary['status']=='all_ten_private_groups_passed' and len(summary['records'])==10,'ten successful groups declared','provenance')
    records={(row['kind'],row['component_count']):row for row in summary['records']}
    check(set(records)=={(kind,c) for kind in KINDS for c in SHAPES},'complete type/shape matrix','provenance')
    total_physical=total_success=total_rejected=total_components=0
    for kind,(bits,requested) in KINDS.items():
        for c,shape in SHAPES.items():
            stem=f'{kind}-c{c}';data=read('groups/'+stem+'.json');run=read('groups/'+stem+'-run.json');groups[(kind,c)]=data
            check(records[(kind,c)]==run,stem+': summary/per-run manifest equality','provenance')
            check(run['exit_code']==0 and run['sources_unchanged'] and run['closure_unchanged'],stem+': successful unchanged run','provenance')
            check(run['build_sha256']==build_hash and run['binary_sha256']==binary_hash and run['source_manifest_sha256']==manifest_hash and run['runner_sha256']==runner_hash,stem+': source/binary/build/runner bindings','provenance')
            check(hashed(base/'groups'/f'{stem}.json')==run['output_sha256'] and hashed(base/'groups'/f'{stem}.log')==run['log_sha256'],stem+': output/log hashes','provenance')
            hashed(base/'groups'/f'{stem}-run.json')
            check(run['command']==['taskset','-c','18,19',str(RUNTIME/'validate'),kind,str(c),str(RUNTIME/'groups'/f'{stem}.json')],stem+': exact bounded runtime command','provenance')
            check(run['timeout_seconds']==120 and run['environment_overrides']=={'RAYON_NUM_THREADS':'1','OMP_NUM_THREADS':'1'},stem+': runtime controls','provenance')
            check(data['status']=='passed_private_typed_e6_n2' and data['kind']==kind and data['working_bits']==bits and data['requested_bits']==requested,stem+': exact numeric type/precision settings')
            check(data['shape']==shape and data['static_dynamic_prepared_expression_equal'] is True,stem+': shape and static/dynamic metadata')
            lanes=[entry['result'] for entry in data['lanes']]
            check([entry['lane'] for entry in data['lanes']]==list(range(13)) and data['physical_rows']==13,stem+': complete thirteen lane order')
            accepted=[0,1,2,4,6,8,10] if c==4 else [0,1,2,4,8,10]
            check([i for i,row in enumerate(lanes) if row['status']=='Success']==accepted,stem+': exact accepted row set')
            check(data['successful_rows']==len(accepted) and data['rejected_rows']==13-len(accepted) and data['successful_components']==len(accepted)*c,stem+': exact success/rejection/component counts')
            total_physical+=13;total_success+=len(accepted);total_rejected+=13-len(accepted);total_components+=len(accepted)*c
            for i,row in enumerate(lanes):
                if i not in accepted:check(row['values'] is None,stem+f': rejected lane{i} hides values')
                if i in [3,7,9,11,12]:check(row['status'].startswith('InvalidInput(') and row['bounds']==[] and row['rho'] is None,stem+f': invalid input lane{i}')
            check(lanes[5]['status']=='OutsideAnalyticDomain' and Q(lanes[5]['rho'])==Q(2,5) and lanes[5]['bounds']==[],stem+': radius rejection')
            check(lanes[0]==lanes[1]==lanes[10],stem+': exact scale/mixed-object-precision result equality')
            primary=data['primary_execution'];visits=primary['instruction_lane_visits']
            check(visits>0 and visits%7==0,stem+': integral structural instruction estimate')
            for label,execution,packed,active in [('primary',primary,12,7),('chunk0',data['chunk_execution'][0],5,4),('chunk1',data['chunk_execution'][1],7,3)]+[(f'concurrent{i}',entry,12,7) for i,entry in enumerate(data['concurrent_execution'])]:
                check(execution=={'packed_rows':packed,'active_rows':active,'numeric_batch_calls':1,'enclosure_batch_calls':1,'tail_batch_calls':1,'instruction_lane_visits':visits//7*active},stem+': '+label+' evaluator counters','transport')
            check(len(data['chunk_execution'])==len(data['concurrent_execution'])==2,stem+': two chunks and two concurrent workspaces','transport')
            check(data['empty_malformed_odd_reverse_chunk_fresh_singleton_static_dynamic_concurrent']=='passed',stem+': compiled transport/control assertions passed','transport')
            fixture=expected_inputs(kind,c);physical=data['physical_input'];exact_rows=[]
            check([row['row'] for row in physical]==list(range(13)),stem+': complete serialized physical rows','inputs')
            for row_index,row in enumerate(physical):
                values=row['components'];actual_points=[point(value) for value in values];exact_rows.append(actual_points)
                check(len(values)==16*c and actual_points==fixture[row_index],stem+f': row{row_index} all exact fixture values','inputs')
                for j,value in enumerate(values):
                    expected_bits=53 if kind.startswith('float') and row_index==10 and j%2==0 else bits
                    check(value['real_bits']==value['imaginary_bits']==expected_bits,stem+f': row{row_index} input{j} precision','inputs')
                    check(all(v.denominator&(v.denominator-1)==0 for v in actual_points[j]),stem+f': row{row_index} input{j} dyadic representation','inputs')
            check(exact_rows[0]==exact_rows[10] and exact_rows[0][:15*c]==exact_rows[1][:15*c],stem+': physically identical rows for scale/object precision transport','inputs')
            distinction=exact_rows[2][10*c][0]-exact_rows[0][10*c][0]
            check(distinction==(Q(0) if kind=='f64' else Q(1,2**80)) and data['beyond53_distinct']==(kind!='f64'),stem+': exact beyond53 distinction','inputs')
            check(data['mixed_input_precision']==kind.startswith('float'),stem+': mixed precision metadata','inputs')
            if kind!='f64':check(lanes[0]['values'][0]!=lanes[2]['values'][0],stem+': above53 input distinction reaches output')
            comparisons={row['lane']:row['components'] for row in data['independent_identity_comparisons']}
            check(set(comparisons)==set(accepted) and len(data['independent_identity_comparisons'])==len(accepted),stem+': complete independent comparison rows')
            for lane_index in accepted:
                row=exact_rows[lane_index];mass=row[10*c:11*c]
                check(all(value==(0,0) for value in row[:10*c]) and all(row[i*c:(i+1)*c]==mass for i in range(11,15)),stem+f': row{lane_index} common-mass oracle preconditions')
                check(all(value==(0,0) for value in mass[3:]),stem+f': row{lane_index} no higher mass jets')
                centers=identity(mass[0],mass[1],mass[2],c);result=lanes[lane_index];items=comparisons[lane_index]
                check(len(result['values'])==len(result['bounds'])==len(items)==c,stem+f': row{lane_index} complete coefficient arrays')
                check(Q(result['rho'])==0,stem+f': row{lane_index} common primal rho zero')
                for component,(value,bound,item,center) in enumerate(zip(result['values'],result['bounds'],items,centers)):
                    label=f'{stem}: row{lane_index} component{component}'
                    re,im=point(value);rl,ru=map(Q,bound['real_interval']);il,iu=map(Q,bound['imaginary_interval']);tail=Q(bound['truncation'])
                    check(item['component']==component and (Q(item['center_real']),Q(item['center_imaginary']))==center,label+' independent scalar identity')
                    actual_error=(re-center[0])**2+(im-center[1])**2
                    rectangle_error=max(abs(rl-center[0]),abs(ru-center[0]))**2+max(abs(il-center[1]),abs(iu-center[1]))**2
                    output_error=max(abs(rl-re),abs(ru-re))**2+max(abs(il-im),abs(iu-im))**2
                    allowed=Q(1,2**(2*requested))*max(Q(1),re*re+im*im)
                    check(rl<=ru and il<=iu and tail>=0,label+' valid rectangle/tail')
                    check(Q(item['actual_error_squared'])==actual_error and Q(item['rectangle_error_squared'])==rectangle_error,label+' exact recorded oracle distances')
                    check(Q(bound['maximum_error_squared'])==output_error,label+' exact returned-point rectangle distance')
                    check(Q(item['allowed_error_squared'])==Q(bound['allowed_error_squared'])==allowed,label+' unchanged mixed budget')
                    check(max(actual_error,rectangle_error,output_error)<=allowed,label+' all strict accuracy gates')
                    check(rl<=center[0]<=ru and il<=center[1]<=iu,label+' exact oracle containment')
                    check(rl<=re<=ru and il<=im<=iu,label+' represented output containment')
                    rw,iw=ru-rl-2*tail,iu-il-2*tail
                    check(rw>=0 and iw>=0 and Q(item['rounding_real_width'])==rw and Q(item['rounding_imaginary_width'])==iw,label+' exact nonnegative rounding-only widths')
            if c==6:
                rejected=lanes[6];mass=exact_rows[6][10*c:11*c];centers=identity(mass[0],mass[1],mass[2],c)
                check(rejected['status']=='UncertifiedComponent(5)' and Q(rejected['rho'])==0 and len(rejected['bounds'])==6,stem+': zero-rho cubic rejection')
                check(point(data['large_mixed_cubic_oracle'])==centers[5]!=(0,0),stem+': exact nonzero large mixed cubic')
                for component,(bound,center) in enumerate(zip(rejected['bounds'],centers)):
                    rl,ru=map(Q,bound['real_interval']);il,iu=map(Q,bound['imaginary_interval'])
                    check(rl<=center[0]<=ru and il<=center[1]<=iu,stem+f': rejected component{component} exact identity contained')
                    check((Q(bound['maximum_error_squared'])<=Q(bound['allowed_error_squared']))==(component<5),stem+f': first rejected budget exactly cubic component{component}')
                check(Q(rejected['bounds'][5]['truncation'])>0,stem+': positive mixed cubic tail at zero primal rho')
            else:check(data['large_mixed_cubic_oracle'] is None,stem+': no unrequested cubic identity')
            group_reports.append({'group':stem,'physical_rows':13,'successful_rows':len(accepted),'rejected_rows':13-len(accepted),'successful_components':len(accepted)*c,'working_bits':bits,'requested_bits':requested})
    check((total_physical,total_success,total_rejected,total_components)==(130,65,65,320),'aggregate exact matrix counts')
    for c in SHAPES:
        low,high=groups[('float256',c)],groups[('float384',c)]
        check(low['requested_bits']==high['requested_bits']==128,f'shape{c}: fixed requested budget','convergence')
        check([[point(v) for v in row['components']] for row in low['physical_input']]==[[point(v) for v in row['components']] for row in high['physical_input']],f'shape{c}: identical represented inputs across working precisions','convergence')
        low_comparisons={row['lane']:row['components'] for row in low['independent_identity_comparisons']}
        high_comparisons={row['lane']:row['components'] for row in high['independent_identity_comparisons']}
        strict=zero=to_zero=0;ratios=[]
        for lane in low_comparisons:
            for component,(a,b) in enumerate(zip(low_comparisons[lane],high_comparisons[lane])):
                check((a['center_real'],a['center_imaginary'])==(b['center_real'],b['center_imaginary']),f'shape{c} row{lane} component{component}: identical exact oracle','convergence')
                for coordinate in ['real','imaginary']:
                    old,new=Q(a[f'rounding_{coordinate}_width']),Q(b[f'rounding_{coordinate}_width'])
                    good=(new==0 if old==0 else 0<=new<old)
                    check(good,f'shape{c} row{lane} component{component} {coordinate}: rounding-width convergence','convergence')
                    if old==0:zero+=1
                    else:
                        strict+=1
                        if new==0:to_zero+=1
                        else:ratios.append(new/old)
        check(strict>0,f'shape{c}: nonvacuous strict arithmetic convergence','convergence')
        convergence.append({'components':sum(len(v) for v in low_comparisons.values()),'shape_components':c,'coordinate_widths':strict+zero,'strictly_shrunk_positive_widths':strict,'zero_to_zero_widths':zero,'positive_to_zero_widths':to_zero,'minimum_positive_width_ratio_exact':str(min(ratios)) if ratios else None,'maximum_positive_width_ratio_exact':str(max(ratios)) if ratios else None,'scope':'Arithmetic width after subtracting2*tail, not convergence of fixed N2 truncation error.'})
    for c in SHAPES:
        check(len({groups[(kind,c)]['primary_execution']['instruction_lane_visits'] for kind in KINDS})==1,f'shape{c}: equal structural instruction counts across numeric types','transport')
    driver=(base/'source/typed.rs').read_text()
    for anchor in ['std::thread::scope','scope.spawn','a.join().unwrap()','b.join().unwrap()','assert_same(&primary,&dynamic_result)','assert_same(&primary,&chunked)','assert_eq!(lane_json(&primary[0]),lane_json(&alone[0]))','HyperDual::from_values(shape.to_vec(),components.to_vec())','assert_eq!(carrier.values(),dynamic.values())']:
        check(anchor in driver,'bound source transport assertion: '+anchor,'transport')
    hashed(base/'run-summary.json');hashed(Path(__file__).resolve())
    result={'schema_version':1,'status':'passed' if not failures else 'failed','checks':sum(counts.values()),'checks_by_category':counts,'failures':failures,'input_hashes':hashes,
            'totals':{'groups':10,'physical_rows':total_physical,'successful_rows':total_success,'rejected_rows':total_rejected,'successful_components':total_components},
            'groups':group_reports,'float256_to_float384_rounding_convergence':convergence,
            'scope':'Exact Fraction audit of ten private typed E6 N2 output groups, represented fixtures, independent scalar common-mass identities, all accepted budgets and rectangles, failures, batching/transport evidence, precision convergence and frozen provenance. No Symbolica evaluation or build.',
            'limits':['Common complex masses and zero invariants only; no public/core/default E6 or performance qualification.','Static/dynamic Dual coverage is metadata/component transport with Symbolica Dualizer arithmetic; not Workspace<StaticDual<T>> support.','Full concurrent/reverse/chunk/singleton/static-dynamic arrays are checked by compiled assertions and successful run; serialized counters are independently checked but full traces are absent.','Instruction-lane visit counts are structural estimates.','Float256→384 convergence concerns arithmetic widths after removing the retained truncation radius; omitted N2 mixed cubic error remains visible.']}
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':result['checks'],'failures':len(failures),'hashes':len(hashes),'totals':result['totals'],'convergence':convergence,'output':str(destination.relative_to(ROOT)),'sha256':sha(destination)}))
    raise SystemExit(bool(failures))


if __name__=='__main__':main()
