"""Exactly inventoried public policy tests; no timings and no broad-feature run."""
from pathlib import Path
import datetime,hashlib,json,os,re,sys
from lifecycle import Budget,execute,freeze_binary
ROOT=Path.cwd();HERE=ROOT/'target/native-f64-opt-in/qualification'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
COMMON_MASTER=['existing_defaults_and_explicit_symbolica_remain_distinct','explicit_dual_policy_keeps_lazy_scalar_children_symbolica']
SELECTED_MASTER=['selective_feature_does_not_enable_the_legacy_broad_constructor','selected_batches_keep_six_outputs_errors_and_own_repeats','higher_precision_and_unselected_families_remain_exact_symbolica','one_component_and_seeded_dual_shapes_never_select_native','static_and_dynamic_dual_adapters_keep_policy_and_shape']
COMMON_CORE=['explicit_symbolica_overrides_the_legacy_feature_and_preserves_default_cache']
SELECTED_CORE=['selective_workspaces_keep_cache_policy_and_recursive_lane_semantics','selective_policy_keeps_high_precision_and_component_one_duals_on_symbolica']
def inventory(configuration,crate):
    if crate=='masters':
        names=COMMON_MASTER+(SELECTED_MASTER if configuration=='selective'else['unavailable_selection_errors_before_fallback_or_preparation'])
        return ['execution_policy_tests::'+name for name in names]+['pentagon6::tests::explicit_policy_keeps_pentagon_boxes_symbolica']
    names=COMMON_CORE+(SELECTED_CORE if configuration=='selective'else['unavailable_selective_policy_fails_before_exact_preparation'])
    return ['execution::master_policy_tests::'+name for name in names]
def main():
    assert len(sys.argv)==3,'public-build-id run-id'
    build_path=HERE/('public-build-'+sys.argv[1])/'build.json';build=read(build_path)
    assert build['status']=='passed'and build['stage']=='public'
    attempt=HERE/('public-tests-'+sys.argv[2]);attempt.mkdir(exist_ok=False)
    prep=read(HERE/'preparation.json');bindings={Path(p):h for p,h in build['input_sha256'].items()}
    bindings[build_path]=sha(build_path)
    assert bindings[Path(__file__).resolve()]==sha(Path(__file__)), 'runtime source differs from frozen build input'
    cases=[]
    for configuration in ['default','selective']:
        for crate in ['masters','core']:
            artifact=build['outputs'][configuration+'-'+crate+'-tests'];binary=Path(artifact['path']);bindings[binary]=artifact['sha256']
            cases.extend({'configuration':configuration,'crate':crate,'name':name,'binary':str(binary),'status':'unrun'}for name in inventory(configuration,crate))
    assert len(cases)==17
    record={'status':'preparing','scope':'public source, no observation overlay, default/selective-only runtime controls','runtime_cap_seconds':180,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_sha256':{str(p):h for p,h in bindings.items()},'cases':cases,'listings':[],'cleanup_errors':[],'license_environment_present':any('SYMBOLICA'in k and'LICENSE'in k for k in os.environ)}
    save(attempt/'results.json',record);budget=Budget(180)
    def verify():
        for p,h in bindings.items():budget.remaining();assert sha(p)==h,f'changed input: {p}'
    frozen={}
    budget.arm()
    try:
        verify()
        for key,artifact in build['outputs'].items():
            if key.endswith('-tests'):
                frozen[key]=freeze_binary(artifact['path'],artifact['sha256'],attempt/(key+'-frozen'),budget)
                bindings[frozen[key]]=artifact['sha256']
        record['executed_executables']={key:{'path':str(value),'sha256':bindings[value]}for key,value in frozen.items()};save(attempt/'results.json',record)
        for configuration in ['default','selective']:
            for crate in ['masters','core']:
                key=configuration+'-'+crate;binary=frozen[key+'-tests']
                command=[prep['tools']['taskset']['path'],'-c','22',str(binary),'--list','--format','terse']
                log=attempt/(key+'-list.log');listing={'configuration':configuration,'crate':crate};record['listings'].append(listing)
                def persist(result):listing.update(result);save(attempt/'results.json',record)
                execute(command,log,budget,15,record['cleanup_errors'],persist)
                listing['log_sha256']=sha(log);save(attempt/'results.json',record)
                assert listing.get('status')=='exited' and listing.get('returncode')==0 and not listing.get('timeout')
                actual=[line.removesuffix(': test')for line in log.read_text().splitlines()if line.endswith(': test')]
                expected=inventory(configuration,crate)
                prefixes=('execution_policy_tests::','pentagon6::tests::explicit_policy_keeps_pentagon_boxes_symbolica')if crate=='masters'else('execution::master_policy_tests::',)
                assert sorted(name for name in actual if name.startswith(prefixes))==sorted(expected),'test inventory mismatch'
        for index,case in enumerate(cases):
            case['status']='running';save(attempt/'results.json',record)
            command=[prep['tools']['taskset']['path'],'-c','22',str(frozen[case['configuration']+'-'+case['crate']+'-tests']),'--exact',case['name'],'--test-threads=1','--nocapture']
            log=attempt/f'case-{index:02d}.log'
            def persist(result):case.update(result);save(attempt/'results.json',record)
            execute(command,log,budget,60,record['cleanup_errors'],persist)
            assert case.get('status')=='exited' and case.get('returncode')==0 and not case.get('timeout'),case['name']
            text=log.read_text();matches=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured;',text)
            assert matches==[('1','0','0','0')], 'missing/failed/ignored test'
            case.update(status='passed',log_sha256=sha(log));save(attempt/'results.json',record)
    except Exception as error:record['error']=repr(error)
    record['status']='terminal-awaiting-guards';record['elapsed_seconds']=budget.elapsed();save(attempt/'results.json',record)
    try:verify();record['inputs_unchanged']=True
    except Exception as error:record.update(inputs_unchanged=False,guard_error=repr(error))
    record['elapsed_seconds']=budget.elapsed();record['deadline_exceeded']=record['elapsed_seconds']>180
    record['status']='passed'if all(c['status']=='passed'for c in cases)and record['inputs_unchanged']and not record['cleanup_errors']and'error'not in record and record['elapsed_seconds']<=180 else'failed'
    record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(attempt/'results.json',record)
    budget.disarm()
    print(json.dumps({'status':record['status'],'cases':len(cases),'elapsed_seconds':record['elapsed_seconds']}))
    return 0 if record['status']=='passed'else 1
if __name__=='__main__':sys.exit(main())
