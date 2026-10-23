from pathlib import Path
from fractions import Fraction
import hashlib,json
base=Path('target/cli-coefficient-optimization')
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
homogeneity=json.loads((base/'homogeneity.json').read_text());assert homogeneity['status']=='passed'
rows=[];structures=[]
for case in ['ggh','gghh','gghhh','gggg-up']:
 result=json.loads((base/f'qualification/{case}/outputs.json').read_text());graph=json.loads((base/f'qualification/{case}/prepared-graph.json').read_text());proof=next(c for c in homogeneity['cases'] if c['case']==case)
 assert len(graph['terms'])==len(proof['homogeneity'])
 for i,(term,identity)in enumerate(zip(graph['terms'],proof['homogeneity'])):assert identity['index']==i and identity['powers']==term['powers'] and identity['scaling_identity_literal_zero']
 dimensions=[i['coefficient_dimension'] for i in proof['homogeneity']];massive=[i for i,v in enumerate(proof['parameter_map']) if v['dimension']==1];width=len(proof['parameter_map']);outputs=len(dimensions)
 structures += [dict(case=case,**s) for s in result['structures']]
 for domain in result['domains']+[dict(domain='Float256-mixed-input',batches=result['mixed']['batches'])]:
  records={mode:dict(case=case,domain=domain['domain'],mode=mode,real_comparisons=0,raw_failed_components=0,dimension_failed_components=0,raw_max=Fraction(0),dimension_max=Fraction(0),output_precision_differences_from_direct=0,zero_sign_differences_from_direct=0,scale_values=set(),strict_failed_batches=0) for mode in ['direct','allocated','cse0','pair1']}
  for batch in domain['batches']:
   packed=batch.get('input',batch.get('inputs'));reference=batch['reference256_same_represented_input'];assert len(packed)==batch['rows']*width and len(reference)==batch['rows']*outputs
   scales=[]
   for lane in range(batch['rows']):
    row=packed[lane*width:(lane+1)*width]
    assert all(Fraction(row[i][1]['rational'])==0 for i in massive),'This scale diagnostic currently admits real dimension-one inputs only'
    q=max(abs(Fraction(row[i][0]['rational'])) for i in massive);assert q>0;scales.append(q)
   direct=next(r for r in batch['results'] if r['mode']=='direct')['outputs']
   for variant in batch['results']:
    r=records[variant['mode']];r['strict_failed_batches']+=not variant['precision_agreement']['passed'];actual=variant['outputs'];assert len(actual)==len(reference)
    for index,(av,bv) in enumerate(zip(actual,reference)):
     lane=index//outputs;dimension=dimensions[index%outputs];q=scales[lane];r['scale_values'].add(str(q));normalization=q**dimension
     for component,(a,b)in enumerate(zip(av,bv)):
      assert 'nonfinite' not in a and 'nonfinite' not in b
      a_value=Fraction(a['rational']);b_value=Fraction(b['rational']);difference=abs(a_value-b_value)
      raw=difference/max(Fraction(1),abs(a_value),abs(b_value));normalized=difference/max(normalization,abs(a_value),abs(b_value))
      r['real_comparisons']+=1;r['raw_failed_components']+=raw>Fraction(1,10**10);r['dimension_failed_components']+=normalized>Fraction(1,10**10);r['raw_max']=max(r['raw_max'],raw);r['dimension_max']=max(r['dimension_max'],normalized)
      same=direct[index][component];r['output_precision_differences_from_direct']+=a['precision']!=same['precision']
      if a_value==Fraction(same['rational'])==0:r['zero_sign_differences_from_direct']+=a['negative_sign']!=same['negative_sign']
  for r in records.values():
   for key in ['raw_max','dimension_max']:r[key+'_decimal_display']=float(r[key]);r[key]=str(r[key])
   r['scale_values']=sorted(r['scale_values']);rows.append(r)
summary={'status':'research_diagnostics_only','adoption':'not adopted; no timing qualification','raw_criterion':'|a-b|/max(1,|a|,|b|)<=1e-10 for each real/imaginary coefficient component; original failures retained unchanged','dimensional_diagnostic':'|a-b|/max(Q^(N-rank),|a|,|b|), Q=max absolute real component among all dimension-one masses and external momenta, dimension-one imaginary components required zero. Every coefficient homogeneity established exactly with Symbolica. This diagnostic does not replace the raw criterion or constitute physical end-to-end acceptance.','high_precision_scope':'DD and Float128 compare to256-bit exact-represented-input baseline. Float256 candidate comparisons test same-precision consistency; near-zero256-bit references may have few tracked bits, with selected exact substitution additionally recorded.','corpus_scope':'Four canonical physical graphs/kinematic points, coupling controls and original batch sizes; no general conditioning/overflow coverage','homogeneity_sha256':sha(base/'homogeneity.json'),'runtime_manifest_sha256':sha(base/'qualification/runtime-manifest.json'),'analyzer_sha256':sha(Path(__file__)),'structures':structures,'rows':rows}
(base/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for r in rows:
 if r['domain']=='f64':print(r['case'],r['mode'],'raw_failed',r['raw_failed_components'],'dim_failed',r['dimension_failed_components'],'rawmax',r['raw_max_decimal_display'],'dimmax',r['dimension_max_decimal_display'])
