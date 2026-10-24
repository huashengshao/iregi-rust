"""Saved public unit-test evidence audit; no compiler or runtime execution."""
from pathlib import Path
import hashlib,json,math,re,sys
import run_public_tests as r
HERE=Path.cwd()/'target/native-f64-opt-in/qualification'
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def qualify(result,build,prep,folder):
    assert result['status']=='passed'and result['runtime_cap_seconds']==180
    assert result['inputs_unchanged']is True and result['deadline_exceeded']is False
    assert result['cleanup_errors']==[]and'error'not in result and'guard_error'not in result
    assert type(result['elapsed_seconds'])in[int,float]and math.isfinite(result['elapsed_seconds'])and 0<=result['elapsed_seconds']<=180
    expected=[(cfg,crate,name)for cfg in ['default','selective']for crate in ['masters','core']for name in r.inventory(cfg,crate)]
    assert len(expected)==17 and len(result['cases'])==17
    assert [(case['configuration'],case['crate'],case['name'])for case in result['cases']]==expected
    keys=[cfg+'-'+crate+'-tests'for cfg in ['default','selective']for crate in ['masters','core']]
    assert set(result['executed_executables'])==set(keys)and len(result['listings'])==4
    for key in keys:
        retained=result['executed_executables'][key];original=build['outputs'][key]
        assert retained['sha256']==original['sha256']and sha(retained['path'])==retained['sha256']
    for index,((cfg,crate,name),case)in enumerate(zip(expected,result['cases'])):
        assert case['status']=='passed'and type(case['returncode'])is int and case['returncode']==0 and case.get('timeout',False)is False
        assert case['owned_group_gone']is True and type(case['owned_process_group'])is int and case['owned_process_group']>0
        assert'error'not in case and'cancellation'not in case
        key=cfg+'-'+crate+'-tests';binary=result['executed_executables'][key]['path']
        assert case['binary']==build['outputs'][key]['path']
        assert case['command']==[prep['tools']['taskset']['path'],'-c','22',binary,'--exact',name,'--test-threads=1','--nocapture']
        log=folder/f'case-{index:02d}.log';assert sha(log)==case['log_sha256']
        text=log.read_text()
        assert re.findall(r'^test ([A-Za-z0-9_:]+) \.\.\.',text,re.MULTILINE)==[name],'executed libtest name differs from requested test'
        matches=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured;',text)
        assert matches==[('1','0','0','0')]
    for listing,(cfg,crate)in zip(result['listings'],[(c,k)for c in ['default','selective']for k in ['masters','core']]):
        assert listing['configuration']==cfg and listing['crate']==crate
        assert listing['status']=='exited'and type(listing['returncode'])is int and listing['returncode']==0 and listing.get('timeout',False)is False
        assert listing['owned_group_gone']is True and type(listing['owned_process_group'])is int and listing['owned_process_group']>0
        assert'error'not in listing and'cancellation'not in listing
        binary=result['executed_executables'][cfg+'-'+crate+'-tests']['path']
        assert listing['command']==[prep['tools']['taskset']['path'],'-c','22',binary,'--list','--format','terse']
        log=folder/(cfg+'-'+crate+'-list.log');assert sha(log)==listing['log_sha256']
        names=[line.removesuffix(': test')for line in log.read_text().splitlines()if line.endswith(': test')]
        prefixes=('execution_policy_tests::','pentagon6::tests::explicit_policy_keeps_pentagon_boxes_symbolica')if crate=='masters'else('execution::master_policy_tests::',)
        assert sorted(name for name in names if name.startswith(prefixes))==sorted(r.inventory(cfg,crate))
    return {'status':'passed','tests':17,'listings':4,'scope':'saved complete public test inventory/log/command/exit validation, no new execution'}
def main():
    assert len(sys.argv)==3,'public-build-id tests-id'
    build_path=HERE/('public-build-'+sys.argv[1])/'build.json';build=read(build_path)
    folder=HERE/('public-tests-'+sys.argv[2]);result_path=folder/'results.json';result=read(result_path)
    prep_path=HERE/'preparation.json';prep=read(prep_path)
    assert build['status']=='passed'and build['stage']=='public'
    expected={**prep['input_sha256'],str(prep_path):sha(prep_path)}
    assert build['input_sha256']==expected
    expected[str(build_path)]=sha(build_path)
    for key,value in build['outputs'].items():
        if key.endswith('-tests'):expected[value['path']]=value['sha256']
    assert result['input_sha256']==expected
    for path,value in expected.items():assert sha(path)==value,path
    report=qualify(result,build,prep,folder)
    report.update(build_sha256=sha(build_path),results_sha256=sha(result_path),validator_sha256=sha(__file__))
    with(folder/'independent-admission.json').open('x')as stream:stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
if __name__=='__main__':main()
