from pathlib import Path
import hashlib,json,sys,statistics
sys.dont_write_bytecode=True
from benchmark_helper import summarize
from timing_parser import validate
base=Path('target/cli-coefficient-cse-timing');output=base/sys.argv[1]
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
record=json.loads((output/'manifest.json').read_text())
assert record['runner_sha256']==sha(base/'run.py') and record['parser_sha256']==sha(base/'timing_parser.py')
for name,digest in record['raw_artifacts'].items():assert sha(output/name)==digest

def estimate(ratios):
    summary=summarize(ratios);median=summary['median_ns'];low,high=summary['ci99_ns'];width=(high-low)/median
    return {'samples':ratios,'median':median,'ci99':[low,high],'relative_ci_width':width,'classification':'inconclusive-noise' if width>0.02 else 'improvement' if high<1 else 'regression' if low>1 else 'parity'}
rows=[]
for mode in ['cse0','pair1']:
    for case in ['ggh','gghh','gghhh','gggg-up']:
        path=output/f'raw-{mode}'/f'{case}.json'
        try:
            relative=str(path.relative_to(output))
            if relative not in record['raw_artifacts']:raise ValueError('raw case not bound by runtime manifest')
            run=[r for r in record.get('runs',[]) if r.get('mode')==mode]
            if len(run)!=1 or run[0].get('returncode')!=0 or run[0].get('status')!='passed':raise ValueError('mode process failed or incomplete')
            raw=json.loads(path.read_text());validated=validate(case,mode,raw)
        except Exception as error:
            rows.extend({'case':case,'candidate_mode':mode,'batch':n,'status':'failed-or-incomplete','reason':str(error)} for n in [1,32]);continue
        for row in validated:
            a,b=row['baseline_ns'],row['candidate_ns'];ratios=row['paired_elapsed_ratios'];ordering=row['first_variant_by_block']
            rows.append(row|{'status':'passed','baseline_median_ns':statistics.median(a),'candidate_median_ns':statistics.median(b),'candidate_over_baseline':estimate(ratios),'order_strata':{label:estimate([r for r,first in zip(ratios,ordering) if first==variant]) for label,variant in [('baseline_first',0),('candidate_first',1)]},'pairs_candidate_slower':sum(x>1 for x in ratios)})
summary={'scope':record['scope'],'status':'passed' if record['status']=='passed' and len(rows)==16 and all(r['status']=='passed' for r in rows) else 'failed-or-incomplete','cpu':record['cpu'],'binary_sha256':record['binary_sha256'],'runtime_manifest_sha256':sha(output/'manifest.json'),'analysis_source_sha256':sha(Path(__file__)),'analysis_helper_sha256':sha(base/'benchmark_helper.py'),'protocol':'21 seeded-balanced-random paired30ms blocks, shared fixed iterations calibrated by2ms pilots, no per-call timer','allocation_policy':record['allocation_policy'],'setup_scope':record['setup_scope'],'original_raw_accuracy_failures_preserved':True,'adoption':'No production adoption implied by these diagnostics','rows':rows}
(output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps([{k:r[k]for k in ['case','candidate_mode','batch','status']}|({'ratio':r['candidate_over_baseline']['median'],'ci99':r['candidate_over_baseline']['ci99'],'classification':r['candidate_over_baseline']['classification']}if r['status']=='passed'else{})for r in rows],indent=2))
