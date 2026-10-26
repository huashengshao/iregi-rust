#!/usr/bin/env python3
"""Portable exact saved-array replay; never starts native work or imports a producer."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
import argparse,hashlib,importlib.util,io,json,re,sys,tarfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT='validation/checked-g-generalized-core-tests'
PARENT_HASH='ee4bc172dd8b87e3242158afacab425e6b13376f72dd3fbb6678feb701a97417'
Q='target/checked-g-generalized-numeric'
CORE='target/checked-g-generalized-qualification'
PREFIX='/shared/external/iregi/iregi-rust/'
QUAL='fec2dab0ba9ad66c5fd41a17d69078c912963297e100c32160bd4fc6eb322264'
ARTIFACT='0b28ce2428f7719da1acf9eee9584365d2a6bf62f83ee63db950d30b2b0bc58d'
def need(x,why):
    if not x:raise ValueError(why)
def sha(x):return hashlib.sha256(x).hexdigest()
def desc(x):return dict(sha256=sha(x),bytes=len(x))
def load(x):
    def unique(items):
        out={}
        for k,v in items:need(k not in out,'duplicate JSON key');out[k]=v
        return out
    def invalid(x):raise ValueError('nonfinite JSON '+x)
    return json.loads(x,object_pairs_hook=unique,parse_float=str,parse_constant=invalid)
def safe(name):
    p=Path(name);need(name and not p.is_absolute() and '..'not in p.parts and str(p)==name,'safe relative alias')
def scan(name,body):
    safe(name);need(Path(name).suffix not in{'.pyc','.so','.a','.o','.mod','.smod','.dll','.dylib'} and '__pycache__'not in Path(name).parts,'no compiled/cache payload')
    need(not body.startswith((b'\x7fELF',b'!<arch>',b'MZ')),'no native payload')
    need(not re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}',body),'no license literal')
def restore_files(manifest):
    own={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    need(own==set(manifest['capsule_files'])|{'manifest.json'} and len(own)==7,'closed seven-file child')
    for name,want in manifest['capsule_files'].items():
        body=(HERE/name).read_bytes();scan(name,body);need(desc(body)==want,'exact child file '+name)
    for name,want in manifest['parent_files'].items():safe(name);need(desc((ROOT/name).read_bytes())==want,'exact parent file '+name)
    raw=(ROOT/PARENT/'manifest.json').read_bytes();need(sha(raw)==manifest['parent_manifest_sha256']==PARENT_HASH,'fixed sole central parent')
    spec=importlib.util.spec_from_file_location('checked_g_central_saved_parent',ROOT/PARENT/'check.py');parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
    pm=parent.load(raw);files=parent.restore_files(pm)
    need(parent.replay(files,pm)['strict_named_passes']==120,'inherited120 strict saved normal tests')
    members={}
    with tarfile.open(fileobj=io.BytesIO((HERE/'payload.tar.gz').read_bytes()),mode='r:gz')as archive:
        for entry in archive:
            need(entry.isfile() and entry.name not in members,'unique regular archive entry');body=archive.extractfile(entry).read();scan(entry.name,body);need(desc(body)==manifest['payload_members'].get(entry.name),'exact member');members[entry.name]=body
    need(set(members)==set(manifest['payload_members']),'closed member inventory')
    origins=load((HERE/'payload-origins.json').read_bytes());need(set(origins)==set(manifest['aliases']),'closed alias origins')
    for alias,row in manifest['aliases'].items():
        safe(alias);need(len(set(row)&{'member','parent_alias'})==1,'one byte selector')
        body=members[row['member']]if'member'in row else files[row['parent_alias']]
        want={k:row[k]for k in['sha256','bytes']};need(desc(body)==want=={k:origins[alias][k]for k in['sha256','bytes']},'exact alias '+alias)
        need(alias not in files or files[alias]==body,'no inherited overwrite');files[alias]=body
    need(files[Q+'/qualification.json']==(HERE/'qualification.json').read_bytes()and sha(files[Q+'/qualification.json'])==QUAL,'original numerical qualification unchanged')
    return files
def basis():return [[t,x,y,d-t-x-y]for d in range(7)for t in range(d,-1,-1)for x in range(d-t,-1,-1)for y in range(d-t-x,-1,-1)]
def z(value):
    need(isinstance(value,list)and len(value)==2 and all(type(x)is str for x in value),'lossless complex strings');return list(map(F,value))
def norm(x):return sum(v*v for v in x)
def display(x):
    with localcontext()as c:c.prec=100;return str((Decimal(x.numerator)/Decimal(x.denominator)).sqrt())
def replay(files,manifest):
    read=lambda name:load(files[name])
    pin=lambda name,want:need(sha(files[name])==want,'saved pin '+name)
    qualified=read(Q+'/qualification.json');need(qualified['numeric_record_counts']=={'original_quad':3360,'working_precision_pairs':1680,'total':5040,'independently_recomputed':5040},'all5040 records')
    need(qualified['nested_compound_proof_counters_observable']is False and qualified['performance_qualified']is False and qualified['public_Dual_qualified']is False and qualified['full_domain_qualified']is False and qualified['achieved_80bit_accuracy_claimed']is False,'explicit scope limits')
    protocol=read(Q+'/protocol.json');built=read(CORE+'/build-003/receipt.json');need(built['products']['cli']['sha256']==protocol['artifact_sha256']==ARTIFACT,'actual CLI003 identity')
    omitted={CORE+'/build-003/frozen-cli'}|{Q+f'/{name}-{bits}-001/frozen-cli'for name in['unit_control','first_dot2']for bits in[128,256]}
    need(set(manifest['omitted_native_artifacts'])==omitted and set(manifest['omitted_native_artifacts'].values())=={ARTIFACT},'only five exact historical native identities omitted')
    need(manifest['own_compiled_sources']=={} and len(manifest['inherited_compiled_sources'])==158,'all158 source bodies inherited, none duplicated')
    for name,row in manifest['inherited_compiled_sources'].items():need(sha(files[row['parent_alias']])==built['source_files'][name]==row['sha256'],'compiled central source '+name)
    def bound(mapping):
        for name,want in mapping.items():
            alias=name.removeprefix(PREFIX)
            if alias in files:pin(alias,want)
            else:need(manifest['omitted_native_artifacts'].get(alias)==want,'only historical native artifact omitted '+alias)
    bound(qualified['bindings']);bound(protocol['guards'])
    witness=read('target/checked-g-packed-qualification/128-001/result.json')['input_exact_rational'];need(len(witness)==52,'full52 witness')
    outputs={};groups=[];maxima={};count=0
    for name in['unit_control','first_dot2']:
        case=read(protocol['cases'][name]['input']);original=read('target/n6-rank6-generalized-current-cli/inputs/n6_rank6_'+name+'.json');need({k:v for k,v in case.items()if k!='scalar_products'}==original,'only suppliedG added to original case')
        expected=[1]*6 if name=='unit_control'else[2,1,1,1,1,1];need([p['power']for p in case['propagators']]==expected and case['rank']==6 and case['dimension_shift']==0,'exact requested family')
        flat=[[x,'0']for p in case['propagators']for x in p['shift']]+[p['mass_squared']for p in case['propagators']]+[[case['mu'],'0']]
        need([z(x)for x in flat]==[z(x)for x in witness[:24]+witness[45:]],'exact original Cartesian/mass/mu geometry')
        need(case['scalar_products']==[x[0]for x in witness[24:45]]and all(F(x[1])==0 for x in witness[24:45]),'providedG copied without reconstruction')
        scale=max(F(case['mu'])**2,F(1),*(abs(F(p['mass_squared'][0]))for p in case['propagators']))
        for a in case['propagators']:
            for b in case['propagators']:
                d=[F(x)-F(y)for x,y in zip(a['shift'],b['shift'])];scale=max(scale,abs(d[0]**2-sum(v*v for v in d[1:])))
        need(scale==9,'Q squared9')
        lines=files[protocol['cases'][name]['reference']].decode().splitlines();canary=[load(s[10:])for s in lines if s.startswith('PRECISION ')];need(canary==[{'dbl_kind':16,'olo_kind':16,'storage_bits':128,'binary_digits':113,'decimal_digits':33}],'quad113 bit canary')
        refs=[load(s[7:])for s in lines if s.startswith('RESULT ')];need(len(refs)==1,'one native reference');ref=refs[0];need(ref['id']==case['id']and ref['stable']is True and ref['poles']==['uv1','ir1','ir2','finite']and len(ref['moments'])==210,'complete original native reference')
        for bits in[128,256]:
            base=Q+f'/{name}-{bits}-001';receipt=read(base+'/receipt.json');out=read(base+'/result.json');saved=read(base+'/comparison.json');bound(receipt['guards']);bound({base+'/'+k:v for k,v in receipt['outputs'].items()})
            need(receipt['status']=='passed_native_complete_array_pending_saved_comparison'and receipt['guard_inputs_unchanged']is True and receipt['owned_artifact_unchanged']is True and receipt['cleanup_errors']==[] and receipt['automatic_retry']is False and receipt['runtime_cpu']==26 and F(receipt['elapsed_seconds'])<=2520,'actual bounded stage')
            need(len(receipt['steps'])==1,'one native child');step=receipt['steps'][0];need(step['status']=='exited'and step['returncode']==0 and step['owned_group_gone']is True and not step.get('timeout')and F(step['elapsed_seconds'])<=F(step['timeout_seconds'])<=2400,'terminal owned group')
            groups.append(step['owned_process_group']);command=step['command'];need(command[0].endswith('/taskset')and command[1:3]==['-c','26']and command[4:]==['reduce','--input',PREFIX+protocol['cases'][name]['input'],'--check-scalar-products','--precision','float','--bits',str(bits),'--accuracy-bits','53','--rank','6','--convention','native'],'exact actual defaultHybrid command')
            parsed=[load(files[base+'/stdout.log'])];need(parsed==[out],'raw CLI stdout equals saved result')
            settings={'algorithm':'Hybrid','convention':'IregiNative','dimension_shift':0,'input_policy':'Preserve','invariants':'SuppliedScalarProducts','powers':expected,'propagators':6,'rank':6,'tensor_weights':'Components'}
            need(out['settings']==settings and out['algorithm_requested']==out['algorithm_used']=='Hybrid'and out['precision_bits']==bits and out['precision_control']['accuracy_bits']==53 and out['basis']==basis()and out['poles']==ref['poles'],'actual settings/order/precision')
            need(len(out['samples'])==1 and out['samples'][0]['id']==case['id']and out['samples'][0]['status']=='success'and len(out['samples'][0]['moments'])==210,'actual complete lane')
            e=out['engine_execution'];need(e['engine']=='CertifiedTensor','checked engine')
            for tag in['cartesian','gram']:need(e['certificate_execution'][tag]['input_rows']==1 and e['certificate_execution'][tag]['evaluated_rows']==1 and e['certificate_execution'][tag]['passes']==1,'outer proof work')
            need(e['certificate_execution']['gram']['reduction_batches']==1,'one chart dispatch');notes=out['diagnostics'][0];need(sum('fresh complete auxiliary-mass x user' in n for n in notes)==(3 if name=='first_dot2' else 0)and sum('actual scalar method Some(PassarinoVeltman)'in n for n in notes)==4,'observed child diagnostics, not numeric proof counters')
            actual=out['samples'][0]['moments'];records=[];maximum=F(0);witness_max=None
            for m,alpha in enumerate(basis()):
                need(len(actual[m])==len(ref['moments'][m])==4,'four native slots');unit=scale**(sum(alpha)+4-2*sum(expected))
                for pole in range(4):
                    a,b=z(actual[m][pole]),z(ref['moments'][m][pole]);err=norm([x-y for x,y in zip(a,b)])/max(unit,norm(b));records.append({'moment':m,'monomial':alpha,'slot':pole,'normalized_squared_error':str(err),'passed':err<=F(1,10**20)})
                    if err>maximum:maximum=err;witness_max=[m,pole]
            need(saved['records']==records and len(records)==840 and all(r['passed']for r in records)and saved['failures']==[]and saved['maximum_normalized_error']==display(maximum)and saved['maximum_witness']==witness_max and saved['status']=='passed_complete_checkedG_quad_array','all840 exact quad records');bound(saved['source_inputs']);count+=840;outputs[name,bits]=out;maxima[name+'_'+str(bits)+'_quad']=display(maximum)
        saved=read(Q+'/'+name+'-working-precision-pair-80bit-gate.json');records=[];maximum=F(0);witness_max=None;a=outputs[name,128]['samples'][0]['moments'];b=outputs[name,256]['samples'][0]['moments']
        for m,alpha in enumerate(basis()):
            unit=scale**(sum(alpha)+4-2*sum(expected))
            for pole in range(4):
                x,y=z(a[m][pole]),z(b[m][pole]);err=norm([u-v for u,v in zip(x,y)])/max(unit,norm(x),norm(y));records.append({'moment':m,'monomial':alpha,'slot':pole,'normalized_squared_difference':str(err),'passed':err<=F(1,2**160)})
                if err>maximum:maximum=err;witness_max=[m,pole]
        need(saved['records']==records and len(records)==840 and all(r['passed']for r in records)and saved['failures']==[]and saved['squared_difference_limit']==str(F(1,2**160))and saved['maximum_normalized_difference']==display(maximum)and saved['maximum_witness']==witness_max and saved['status']=='passed_saved_normalized_pair_agreement_2pow_minus80','all840 exact strict pair records');bound(saved['source_inputs']);count+=840;maxima[name+'_working_pair']=display(maximum)
    need(count==5040 and len(set(groups))==4,'all5040 and four fresh groups')
    for name in['independent-unit-audit.json','independent-dot-audit.json']:
        audit=read(Q+'/'+name);need(audit['status'].startswith('passed_')and audit['native_execution']is False and audit['build_execution']is False,'saved independent audit');bound(audit['bindings'])
    note=read(Q+'/source-proof-observability-note.json');need(note['compound_aux_mass_proof_numerical_counts_observable']is False and len(note['selected_qualified_normal_tests'])==13,'source/test-only compound proof qualification')
    gate=read(CORE+'/focused-qualification.json')
    for test in note['selected_qualified_normal_tests']:
        need(test in gate['tests'],'selected source-proof normal test qualified in central gate');pin(CORE+'/'+test['log'],test['log_sha256'])
    for name,want in note['source_sha256'].items():pin(CORE+'/build-003/source-snapshot/'+name,want)
    return {'status':'passed_saved_checked_G_numeric_replay','numeric_records':5040,'original_quad_records':3360,'working_pair_records':1680,'inherited_compiled_sources':158,'inherited_strict_normal_tests':120,'own_compiled_sources':0,'actual_native_groups_absent_in_receipts':4,'maxima':maxima,'compound_proof_counts_observable':False,'source_and_normal_test_enforcement_plus_acceptance_diagnostics_only':True,'performance_qualified':False,'public_Dual_qualified':False,'producer_execution':False}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--json',action='store_true');parser.parse_args();manifest=load((HERE/'manifest.json').read_bytes());files=restore_files(manifest);summary=replay(files,manifest);print(json.dumps(summary,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
