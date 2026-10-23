from pathlib import Path
import hashlib,json,os,signal,subprocess,time

root=Path.cwd();base=root/'target/e6-direct-n2-typed';closure=root/'target/e6-direct-n2'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
build=json.loads((base/'build.json').read_text());prep=json.loads((closure/'preparation.json').read_text())
assert build['exit_code']==0 and build['sources_unchanged'] and build['closure_unchanged']
assert sha(base/'validate')==build['binary_sha256']
groups=base/'groups';groups.mkdir(exist_ok=True)
records=[]
for kind in ['f64','dd','float128','float256','float384']:
    for components in [4,6]:
        stem=f'{kind}-c{components}';record_path=groups/f'{stem}-run.json'
        assert not record_path.exists(),'preserve earlier group attempts'
        for path,digest in build['sources'].items():assert sha(root/path)==digest,path
        for x in prep['files']:assert sha(root/x['frozen'])==x['sha256'],x['frozen']
        output=groups/f'{stem}.json';log_path=groups/f'{stem}.log'
        cmd=['taskset','-c','18,19',str(base/'validate'),kind,str(components),str(output)]
        env=os.environ.copy();env['RAYON_NUM_THREADS']='1';env['OMP_NUM_THREADS']='1'
        record={'scope':'Private typed correctness only; unchanged N2 engine; not benchmark/public E6',
                'kind':kind,'component_count':components,'command':cmd,'timeout_seconds':120,
                'build_sha256':sha(base/'build.json'),'binary_sha256':build['binary_sha256'],
                'source_manifest_sha256':sha(base/'source-manifest.json'),'runner_sha256':sha(Path(__file__)),
                'started_unix_time':time.time(),'environment_overrides':{'RAYON_NUM_THREADS':'1','OMP_NUM_THREADS':'1'},
                'concurrency':'Two explicitly independent evaluator workspaces in scoped threads; Symbolica preparation cores1'}
        start=time.monotonic()
        with log_path.open('w') as log:
            p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
            record['pid']=p.pid
            try:record['exit_code']=p.wait(timeout=120)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGTERM)
                try:p.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
                record.update(exit_code=p.returncode,timed_out=True)
        record.update(elapsed_seconds_diagnostic=time.monotonic()-start,
                      sources_unchanged=all(sha(root/path)==digest for path,digest in build['sources'].items()),
                      closure_unchanged=all(sha(root/x['frozen'])==x['sha256'] for x in prep['files']),
                      log_sha256=sha(log_path))
        if output.exists():record['output_sha256']=sha(output)
        record_path.write_text(json.dumps(record,indent=2)+'\n');records.append(record)
        print(json.dumps({'group':stem,'exit_code':record['exit_code'],'seconds_diagnostic':record['elapsed_seconds_diagnostic']}),flush=True)
        if record['exit_code']!=0 or not record['sources_unchanged'] or not record['closure_unchanged']:
            (base/'stopped.json').write_text(json.dumps({'status':'stopped_at_first_failed_group','records':records},indent=2)+'\n')
            raise SystemExit(1)
(base/'run-summary.json').write_text(json.dumps({'status':'all_ten_private_groups_passed','records':records},indent=2)+'\n')
