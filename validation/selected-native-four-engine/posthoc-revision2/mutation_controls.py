"""Saved-metadata/source controls only; no corrected cohort analysis or kernels."""
from pathlib import Path
import ast,copy,hashlib,json,math,sys
HERE=Path(__file__).resolve().parent;V3=HERE.parent
sys.path.insert(0,str(HERE))
import analyze_posthoc as candidate
from terminal_admission import validate_terminal,validate_rows
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=V3/'timing-quiet254';receipt=json.loads((source/'receipt.json').read_text())
# Keep exactly the metadata and duration fields consumed by terminal admission.
# Full numerical/raw/source admission remains in the original analyzer code.
raw=[]
for line in(source/'raw.jsonl').read_text().splitlines():
    item=json.loads(line);response=item.pop('response')
    item['response']={k:response[k]for k in ['total_ns','elapsed_ns']if k in response}
    raw.append(item)
coordinates=[(r['id'],r['outer_batch'])for r in receipt['rows']]
def validate(r,data):validate_terminal(r);validate_rows(r,data,coordinates,candidate.ORDERS)
validate(receipt,raw)
# A synthetic all-completed control changes only the known short duration.
clean=copy.deepcopy(receipt);cleanraw=copy.deepcopy(raw)
short=clean['rows'][0]['blocks'][32]['engines'][-1]
assert short['engine']=='collier'and short['raw_serial']==159
short['elapsed_ns']=101_000_000.;short['ns_per_call']=short['elapsed_ns']/short['iterations']
# Match the producer's actual floating reconstruction, including its rounding.
short['elapsed_ns']=short['ns_per_call']*short['iterations']
cleanraw[159]['response']['total_ns']=[short['ns_per_call']]
clean['rows'][0].update(status='completed',short_blocks=0);clean['status']='completed'
validate(clean,cleanraw)
controls=[]
def reject(name,mutator,*,all_completed=False):
    r=copy.deepcopy(clean if all_completed else receipt);data=copy.deepcopy(cleanraw if all_completed else raw)
    mutator(r,data)
    try:validate(r,data)
    except (AssertionError,KeyError,TypeError,IndexError,ValueError) as error:controls.append({'name':name,'rejected':True,'reason':str(error)});return
    raise AssertionError('malformed control accepted: '+name)
for key in ['error','guard_error','raw_hash_error']:
    reject('global '+key,lambda r,d,k=key:r.__setitem__(k,''))
    reject('row '+key,lambda r,d,k=key:r['rows'][1].__setitem__(k,''))
for name,key,value in [('wrong mode','mode','preflight'),('running status','status','running'),('arbitrary status','status','failed'),('cleanup error','cleanup_errors',['failed close']),('deadline','deadline_exceeded',True),('input guard','inputs_unchanged',False),('missing raw hash','raw_sha256',None),('child failure','process_exit_codes',{'probe':0,'iregi':1,'collier':0}),('missing child','process_exit_codes',{'probe':0,'iregi':0})]:
    reject(name,lambda r,d,k=key,v=value:r.__setitem__(k,v))
for key in ['numerical_elapsed_seconds','cleanup_finished_elapsed_seconds','elapsed_seconds']:
    for label,value in [('nan',float('nan')),('infinite',float('inf')),('negative',-1.),('bool',True),('over-cap',701.)]:
        reject(key+' '+label,lambda r,d,k=key,v=value:r.__setitem__(k,v))
reject('elapsed order',lambda r,d:r.__setitem__('cleanup_finished_elapsed_seconds',1.))
for key in ['initialization','controls_before','controls_after']:
    reject(key+' failed',lambda r,d,k=key:r[k].__setitem__('status','failed'))
reject('missing family',lambda r,d:r['rows'].pop())
reject('reordered families',lambda r,d:r['rows'].reverse())
reject('bool outer batch',lambda r,d:r['rows'][0].__setitem__('outer_batch',True))
for status in ['failed','pending','running','calibration-inconclusive','budget-inconclusive']:
    reject('row status '+status,lambda r,d,s=status:r['rows'][1].__setitem__('status',s))
reject('short status omitted',lambda r,d:r['rows'][0].__setitem__('status','completed'))
reject('false short status',lambda r,d:r['rows'][1].__setitem__('status','short-block-inconclusive'))
reject('short count omitted',lambda r,d:r['rows'][0].__setitem__('short_blocks',0))
reject('false short count',lambda r,d:r['rows'][1].__setitem__('short_blocks',1))
reject('bool short count',lambda r,d:r['rows'][0].__setitem__('short_blocks',True))
reject('short aggregate says completed',lambda r,d:r.__setitem__('status','completed'))
reject('unexplained inconclusive aggregate',lambda r,d:r.__setitem__('status','inconclusive-or-failed'),all_completed=True)
reject('numerical admission failed',lambda r,d:r['rows'][1].__setitem__('before_after_qualification','failed'))
reject('missing quartet',lambda r,d:r['rows'][1]['blocks'].pop())
reject('missing engine',lambda r,d:r['rows'][1]['blocks'][0]['engines'].pop())
reject('wrong quartet order',lambda r,d:r['rows'][1]['blocks'][0]['order'].reverse())
reject('bool quartet index',lambda r,d:r['rows'][1]['blocks'][1].__setitem__('index',True))
reject('zero iterations',lambda r,d:r['rows'][0].__setitem__('iterations',0))
reject('bool iterations',lambda r,d:r['rows'][0].__setitem__('iterations',True))
reject('raw serial differs',lambda r,d:d[159].__setitem__('serial',158))
reject('raw stage differs',lambda r,d:d[159].__setitem__('stage','calibration'))
reject('raw family differs',lambda r,d:d[159].__setitem__('id','wrong'))
reject('raw batch bool',lambda r,d:d[159].__setitem__('batch',True))
reject('raw block differs',lambda r,d:d[159].__setitem__('block',31))
reject('raw engine differs',lambda r,d:d[159].__setitem__('engine','iregi'))
reject('raw iterations differ',lambda r,d:d[159].__setitem__('iterations',134148))
reject('raw total changed',lambda r,d:d[159]['response'].__setitem__('total_ns',[800.]))
reject('raw total nan',lambda r,d:d[159]['response'].__setitem__('total_ns',[float('nan')]))
reject('raw total extra',lambda r,d:d[159]['response'].__setitem__('total_ns',[1.,2.]))
reject('raw Rust elapsed changed',lambda r,d:d[28]['response'].__setitem__('elapsed_ns',[1]))
reject('raw Rust elapsed float',lambda r,d:d[28]['response'].__setitem__('elapsed_ns',[298868292.]))

# Admission correction must never change observed statistics. These are copied
# frozen statistics with synthetic labels, not recomputed acceptance decisions.
frozen=json.loads((source/'summary.json').read_text());same=copy.deepcopy(frozen)
for row in same['rows']:
    row['admission_errors']=[]
    for ratio in row['ratios']:
        ratio['gate']='synthetic-test-label';ratio['statistics']['gate']='synthetic-test-label'
        for stat in ratio['order_strata'].values():stat['gate']='synthetic-test-label'
candidate.assert_unchanged_statistics(same,frozen)
stat_controls=[]
def reject_stat(name,mutate):
    changed=copy.deepcopy(same);mutate(changed)
    try:candidate.assert_unchanged_statistics(changed,frozen)
    except (AssertionError,KeyError,TypeError,IndexError):stat_controls.append(name);return
    raise AssertionError('changed statistic accepted: '+name)
for key in ['median','relative_ci_width']:
    reject_stat(key,lambda s,k=key:s['rows'][1]['ratios'][0]['statistics'].__setitem__(k,0.))
reject_stat('confidence interval',lambda s:s['rows'][1]['ratios'][0]['statistics']['ci99'].__setitem__(0,0.))
reject_stat('sample',lambda s:s['rows'][1]['ratios'][0]['statistics']['samples'].__setitem__(0,0.))
reject_stat('stratum',lambda s:s['rows'][1]['ratios'][0]['order_strata']['numerator_first'].__setitem__('median',0.))
reject_stat('slower pairs',lambda s:s['rows'][1]['ratios'][0].__setitem__('slower_pairs',999))
reject_stat('engine sample',lambda s:s['rows'][1]['engine_samples_ns']['iregi'].__setitem__(0,0.))
reject_stat('ratio direction',lambda s:s['rows'][1]['ratios'][0].__setitem__('numerator','iregi'))
reject_stat('family omitted',lambda s:s['rows'].pop())
reject_stat('ratio omitted',lambda s:s['rows'][1]['ratios'].pop())
def functions(path):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}
old=functions(V3/'analyze.py');new=functions(HERE/'analyze_posthoc.py')
for name in ['ratio','summarize_family']:assert old[name]==new[name],name
result={'status':'passed-saved-metadata-and-source-controls-only','real_corrected_analysis_executed':False,'new_numerical_or_performance_runs':0,'accepted_terminal_fixtures':['saved-one-short-metadata','synthetic-all-completed'],'terminal_mutations_rejected':len(controls),'terminal_controls':controls,'statistics_mutations_rejected':len(stat_controls),'statistics_controls':stat_controls,'unchanged_function_ast':['ratio','summarize_family'],'all40_frozen_statistics_equality_check':'passed-on-copied-statistics-with-synthetic-gate-labels','source_sha256':{p.name:sha(p)for p in [Path(__file__),HERE/'analyze_posthoc.py',HERE/'terminal_admission.py']},'frozen_summary_sha256':sha(source/'summary.json'),'frozen_receipt_sha256':sha(source/'receipt.json'),'frozen_raw_sha256':sha(source/'raw.jsonl')}
out=HERE/'mutation-controls.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','terminal_mutations_rejected','statistics_mutations_rejected','real_corrected_analysis_executed']}))
