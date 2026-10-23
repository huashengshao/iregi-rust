from pathlib import Path
import hashlib,json,subprocess,time,sys,platform
sys.dont_write_bytecode=True
from timing_parser import validate
root=Path.cwd();base=root/'target/cli-coefficient-cse-timing';binary=base/'probe'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
build=json.loads((base/'compile.json').read_text());prepared=json.loads((base/'preparation.json').read_text());assert build['exit_code']==0
assert sha(Path(prepared['qualification']))==prepared['qualification_sha256']
for name,digest in prepared['source_qualified'].items():assert sha(base/'source'/name)==digest
assert sha(base/'assets/homogeneity.json')==prepared['homogeneity_sha256']
assert sha(binary)==build['binary_sha256']
protocol={name:sha(base/name) for name in ['run.py','timing_parser.py','preparation.json','compile.json']}
source={str(p.relative_to(base)):sha(p)for p in sorted((base/'source').glob('*.rs'))};assert source==build['source_after']
assets={str(p.relative_to(base)):sha(p)for p in sorted((base/'assets').rglob('*'))if p.is_file()}
output=base/sys.argv[1];output.mkdir(exist_ok=False);cpu=int(sys.argv[2])if len(sys.argv)>2 else 254
record={'status':'started','scope':'private coefficient CSE paired diagnostic; no IREGI or full-workspace performance acceptance','cpu':cpu,'platform':platform.platform(),'binary_sha256':sha(binary),'compile_manifest_sha256':sha(base/'compile.json'),'preparation_manifest_sha256':sha(base/'preparation.json'),'runner_sha256':sha(Path(__file__)),'parser_sha256':sha(base/'timing_parser.py'),'source_hashes':source,'protocol_hashes':protocol,'assets':assets,'raw_failure_policy':'Raw coefficient criterion failures remain visible; timing qualification uses separately proven dimensional metric and exact same-variant repeatability','allocation_policy':'N public output allocations and N-1 predecessor drops inside each block; final returned output checked/dropped outside timer','setup_scope':'one graph/plan/map/pack/proof observation per stage; excluded from warm loop; diagnostic only, no amortization assumption','runs':[],'rows':[]}
def save(): (output/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
save()
for mode in ['cse0','pair1']:
    command=['timeout','180','taskset','-c',str(cpu),str(binary),mode,str(output/f'raw-{mode}')]
    start=time.time();item={'mode':mode,'command':command,'started_unix_time':start,'status':'running'};record['runs'].append(item);save()
    with(output/f'{mode}.log').open('w')as log:code=subprocess.call(command,stdout=log,stderr=subprocess.STDOUT)
    item.update(returncode=code,elapsed_seconds=time.time()-start,finished_unix_time=time.time(),log_sha256=sha(output/f'{mode}.log'),status='passed'if code==0 else'failed')
    for case in ['ggh','gghh','gghhh','gggg-up']:
        p=output/f'raw-{mode}'/f'{case}.json'
        if not p.exists():record['rows'] += [{'case':case,'candidate_mode':mode,'batch':n,'status':'not-run'}for n in [1,32]];continue
        try:
            rows=validate(case,mode,json.loads(p.read_text()))
            for row in rows:row['status']='passed';record['rows'].append(row)
        except(Exception)as error:
            record['rows'] += [{'case':case,'candidate_mode':mode,'batch':n,'status':'failed-or-incomplete','parser_error':str(error)}for n in [1,32]]
    save()
assert sha(binary)==record['binary_sha256'];assert source=={str(p.relative_to(base)):sha(p)for p in sorted((base/'source').glob('*.rs'))};assert assets=={str(p.relative_to(base)):sha(p)for p in sorted((base/'assets').rglob('*'))if p.is_file()}
assert protocol=={name:sha(base/name) for name in protocol}
record['source_binary_assets_unchanged']=True
record['protocol_unchanged']=True
record['raw_artifacts']={str(p.relative_to(output)):sha(p)for p in sorted(output.rglob('*'))if p.is_file()and p.name!='manifest.json'}
record['status']='passed'if len(record['rows'])==16 and all(r['status']=='passed'for r in record['rows'])and all(r['returncode']==0 for r in record['runs'])else'failed-or-incomplete';save();print(json.dumps({'status':record['status'],'rows':len(record['rows']),'elapsed_seconds':sum(r['elapsed_seconds']for r in record['runs']),'manifest_sha256':sha(output/'manifest.json')}),flush=True)
raise SystemExit(0 if record['status']=='passed' else 1)
