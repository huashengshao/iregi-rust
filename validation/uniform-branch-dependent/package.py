"""Standard-library evidence packaging only: no compiler/kernel/test execution."""
from pathlib import Path
import datetime,gzip,hashlib,json,os,shutil,sys,tarfile,time
ROOT=Path('/shared/external/iregi/iregi-rust')
HERE=ROOT/'target/guard-performance-review/dependent-capsule-preparation'
R=ROOT/'target/guard-performance-review/dependent-runtime-proposal'
H=ROOT/'target/guard-performance-review/dependent-chain-proposal'
S=ROOT/'target/guard-performance-review/dependent-relink-qualification'
OUT=ROOT/'validation/uniform-branch-dependent'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert Path.cwd()==ROOT and len(sys.argv)==3,'independent-review-path exact-review-sha256'
 os.sched_setaffinity(0,{34,35})
 review=Path(sys.argv[1]);assert sha(review)==sys.argv[2]
 audit=read(review);assert audit['status']=='saved-evidence-audit-passed'and audit['findings']==[]
 assert audit['raw_reconstruction']['requests']==60 and audit['raw_reconstruction']['full_cross_archive_response_pairs']==30
 assert audit['raw_reconstruction']['all_response_records_equal_corresponding_stdout_RESULT']is True
 assert audit['numerical_record_checks']['all_tensor_laurent_and_taylor_slots_present']is True
 assert audit['numerical_record_checks']['all_six_master_outputs_present']is True
 r=read(R/'qualification-001/results.json');assert sha(R/'qualification-001/results.json')=='7d6e7bd39be493228187c6392224e1b9e6191627c6c9f92f4e85bc862697a9d7'
 assert r['status']=='passed-awaiting-independent-saved-data-review'and r['guard_after']is True and not r['cleanup_errors']and r['request_count']==60 and not r['deadline_exceeded']
 release=ROOT/'target/guard-performance-review/dependent-runtime-lease-release-001.json'
 assert sha(release)=='00d875ba808e1a65305cbab63d1bb7a107765d69fcfc08a2d44611758335b713'and read(release)['numerical_lease_released']is True
 protocol=read(R/'protocol.json');assert sha(R/'protocol.json')=='3eaba2080aed332358fbbf3d1e9e89a04d731089f85ccc3820a342b01d8a68fe'
 guards={Path(p)if Path(p).is_absolute()else ROOT/p:v for p,v in{**protocol['protected_sha256'],**protocol['tool_sha256']}.items()}
 for p in [review,release,R/'qualification-001/results.json',R/'manifest.json']:
  guards[p]=sha(p)
 for raw,value in audit['bindings_sha256'].items():
  p=Path(raw)if Path(raw).is_absolute()else ROOT/raw;assert sha(p)==value;guards[p]=value
 def verify():
  for p,v in guards.items():assert sha(p)==v,'Changed evidence: '+str(p)
 verify();OUT.mkdir(exist_ok=False);origins={};archives={}
 def register(p):
  p=Path(p);value=sha(p)
  if p in guards:assert guards[p]==value
  guards[p]=value;return value
 def copy(p,name):
  p=Path(p);value=register(p);q=OUT/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
  assert sha(q)==value
  origins[name]={'path':str(p.relative_to(ROOT))if p.is_relative_to(ROOT)else str(p),'sha256':value,'bytes':p.stat().st_size}
 def archive(name,members):
  # Sorted regular files, normalized tar ownership/mode/time, deterministic gzip.
  inventory=[];q=OUT/name
  with q.open('xb')as stream,gzip.GzipFile(filename='',fileobj=stream,mode='wb',mtime=0,compresslevel=6)as zipped,tarfile.open(fileobj=zipped,mode='w|',format=tarfile.PAX_FORMAT)as tar:
   for member,p in sorted(members):
    p=Path(p);value=register(p);info=tarfile.TarInfo(member);info.size=p.stat().st_size;info.uid=info.gid=0;info.uname=info.gname='';info.mode=0o644;info.mtime=0
    with p.open('rb')as source:tar.addfile(info,source)
    inventory.append({'member':member,'origin':str(p.relative_to(ROOT)),'sha256':value,'bytes':info.size})
  index=name+'.members.json';save(OUT/index,{'archive':name,'regular_files':inventory,'member_count':len(inventory),'metadata':'uid/gid0,empty owner names,mode0644,mtime0; gzip empty filename/mtime0; sorted regular members; path-only PAX when needed'})
  archives[name]={'sha256':sha(q),'bytes':q.stat().st_size,'members':len(inventory),'inventory':index}
 sources=[]
 for prefix,folder in [('symbolica',S),('dependent',H),('runtime',R)]:
  manifest=read(folder/'manifest.json')
  for name,item in manifest['files'].items():
   p=folder/name;assert sha(p)==item['sha256']and p.stat().st_size==item['bytes'];sources.append((prefix+'/'+name,p))
  sources.append((prefix+'/manifest.json',folder/'manifest.json'))
 archive('source-context.tar.gz',sources)
 maps=[]
 for variant in ['baseline','candidate']:maps.append((variant+'/probe.link-map',H/'chain-build-001'/variant/'probe.link-map'))
 archive('link-maps.tar.gz',maps)
 archive('numerical-records.tar.gz',[(name,R/'qualification-001'/name)for name in ['responses.jsonl','baseline.stdout.log','candidate.stdout.log','baseline.stderr.log','candidate.stderr.log']])
 for prefix,folder,receipt in [('symbolica',S/'symbolica-build-001','build.json'),('dependent',H/'chain-build-001','build.json')]:
  copy(folder/receipt,'build/'+prefix+'/build.json')
  for p in sorted(folder.glob('*.log')):copy(p,'build/'+prefix+'/'+p.name)
 for prefix,folder in [('symbolica',S),('dependent',H),('runtime',R)]:
  for p in sorted((folder/'reviews').rglob('*')):
   if p.is_file():copy(p,'reviews/'+prefix+'/'+str(p.relative_to(folder/'reviews')))
 # Ensure the exact final reviewer receipt is directly visible even if external.
 copy(review,'reviews/final-independent-runtime-review.json')
 copy(R/'qualification-001/results.json','runtime/results.json')
 for raw,name in [('target/guard-performance-review/dependent-chain-build-grant-001.json','build/grant.json'),('target/guard-performance-review/dependent-runtime-grant-001.json','runtime/grant.json'),('target/guard-performance-review/dependent-runtime-prior-lease-check-001.json','runtime/prior-lease-check.json'),('target/guard-performance-review/dependent-runtime-lease-release-001.json','runtime/lease-release.json'),('target/public-six-point-cargo/runtime/owned-groups-final-check.json','runtime/prior-owner-release.json')]:copy(ROOT/raw,name)
 for raw,name in [('validation/core-fused-cse-census/dependency-closure.json','environment/dependency-closure.json'),('Cargo.toml','environment/Cargo.toml'),('Cargo.lock','environment/Cargo.lock')]:copy(ROOT/raw,name)
 # Retain the complete already committed local-test capsule, including both
 # failed constructor fixtures and repaired actual15-test evidence, unchanged.
 prior=ROOT/'validation/uniform-branch-scheduler';prior_q=read(prior/'qualification.json')
 assert sha(prior/'qualification.json')=='5f8d8d5d925cc0c1e6d429e6182d041e8f0f50ed52cd3b7fb26b00168416d19a'
 for name,item in prior_q['files'].items():
  p=prior/name;assert sha(p)==item['sha256']and p.stat().st_size==item['bytes'];copy(p,'prior-local/'+name)
 copy(prior/'qualification.json','prior-local/qualification.json')
 copy(Path(__file__),'package.py')
 external=[]
 for stage in [read(S/'symbolica-build-001/build.json'),read(H/'chain-build-001/build.json')]:
  for name,item in stage['outputs'].items():
   p=Path(item['path']);assert register(p)==item['sha256'];external.append({'label':name,'path':str(p),'sha256':item['sha256'],'bytes':item['bytes'],'included':False,'reason':'Large build product; exact source/command/archive linkage retained.'})
 for name,item in r['executed_executables'].items():
  p=Path(item['path']);assert register(p)==item['sha256'];external.append({'label':name+'-executed-copy','path':str(p),'sha256':item['sha256'],'bytes':p.stat().st_size,'included':False,'reason':'Exact read-only execution copy, hash-identical to its linked probe.'})
 save(OUT/'external-artifacts.json',{'scope':'Compiled products are hash/size-bound, not copied; full source/commands/inputs/raw records/maps are retained. Frozen dependency archives/native libraries are inventoried by environment/dependency-closure.json.','artifacts':external})
 save(OUT/'payload-origins.json',{'direct_copies':origins,'archives':archives})
 (OUT/'README.md').write_text('''# Private uniform-branch scheduler: dependent fixture qualification

The original and candidate uninstrumented Symbolica schedulers were linked into
two separate fresh generic OneLoop/masters/core/probe chains. Exactly eight
dependent compiler invocations passed once. Each complete linker map contains
only that variant's own four selected archives. The fixed untimed cohort then
passed60requests,30perisolated copied probe, with all inputs guarded and both
owned groups normally exited. Independent saved-data review recomputed every
complete exact comparison, expected failure mask and source/build/run binding.

The domain is the existing N2/N3rank0/1batch1/32 fixtures and retained precision,
Dual, complex-branch, scaleless, invalid-neighbor and workspace-reuse controls.
One eight-family pass contains1584 tensor/Laurent complex values and1782 master
complex values. Direct controls retain67cases/133rows,106successful and27expected
error rows, with774successful six-output components. All requested Taylor
components, exact rational values, precision/sign metadata, every tensor/native
Laurent slot and all six master outputs are retained. This is a narrow relative
scheduler qualification, not the full TIRust acceptance envelope.

Source archives preserve both uninstrumented Symbolica variants, identical
observation-only core hooks, the complete generic dependency snapshot, exact
commands, the initial blocked documentation preflight, old09c5admission schema,
and all strict-schema corrections before numerical execution. The complete
prior-local capsule preserves the two failed compiler fixtures, repaired
15-test source qualification and independent reviews byte for byte. No failed
numerical attempt or numerical retry occurred in this dependent cohort.

The numerical-records archive contains untouched raw JSONL and complete stdout
and stderr; the runtime receipt is also directly visible. Full linker maps are
compressed separately. Archive inventories and direct origins allow independent
byte/hash verification. Large compiled libraries and executables are external
hash/size-bound products, and the pinned frozen dependency closure is retained.
Reproduction requires that closure (or rebuilding it from the pinned repository
sources), the exact compiler/toolchain and a valid Symbolica license. Rebuild
commands and the fixed request protocol are inside source-context.tar.gz.

All elapsed durations are build/lifecycle diagnostics. No kernel timing,
performance parity, full-domain acceptance, native-backend composition,
production source application or adoption is claimed. The candidate is private.
''')
 verify()
 files={str(p.relative_to(OUT)):{'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(OUT.rglob('*'))if p.is_file()and p!=OUT/'qualification.json'}
 qualification={'schema_version':1,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Private generic-only uniform-branch scheduler dependent fixture qualification; no performance or full-domain claim','files':files,'producer_receipt_sha256':sha(R/'qualification-001/results.json'),'independent_review_origin':str(review),'independent_review_sha256':sha(review),'runtime_protocol_sha256':sha(R/'protocol.json'),'source_manifest_sha256':sha(R/'manifest.json'),'numerical_lease_release_sha256':sha(release),'requests':60,'responses_per_process':30,'eight_families':{'tensor_complex_values':1584,'master_complex_values':1782},'direct_master_controls':{'cases':67,'rows':133,'successful_rows':106,'expected_error_rows':27,'successful_six_output_components':774},'local15_test_qualification_preserved':True,'both_failed_constructor_compiles_preserved':True,'old_schema_and_preflight_preserved':True,'dependent_fixture_qualified':True,'production_source_applied':False,'full_reduction_coverage_qualified':False,'native_master_composition_qualified':False,'performance_qualified':False,'adoption_authorized':False,'self_exclusion':'qualification.json only; every other regular file is inventoried','external_build_products_included':False}
 save(OUT/'qualification.json',qualification);verify()
 print(json.dumps({'status':'packaged-awaiting-independent-copy-review','qualification_sha256':sha(OUT/'qualification.json'),'payload_files':len(files),'archives':archives,'total_bytes':sum(v['bytes']for v in files.values()),'no_compiler_or_kernel_execution':True}))
if __name__=='__main__':main()
