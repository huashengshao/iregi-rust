from pathlib import Path
import hashlib,json,os,re,subprocess,time
root=Path.cwd();out=Path(__file__).resolve().parent;dest=out/'candidate/artifacts';build_path=dest/'unit-build.json';build=json.loads(build_path.read_text());assert build['status']=='compiled' and build['returncode']==0
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();binary=dest/'core_tests';closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds';m=json.loads((closure/'manifest.json').read_text())
checks={'execution':(['execution::tests::'],180,35,0),'certificate':(['invariant_certificate::tests::'],90,8,0),'exact-zero':(['exact_zero_certificate::tests::'],90,4,0),'stability':(['stability::'],120,38,0),'rescue':(['rescue::tests::'],120,3,2)}
def verify():
 assert sha(binary)==build['binary_sha256'];assert sha(out/'build.py')==build['build_script_sha256'];assert sha(closure/'cargo-library-events.json')==build['cargo_library_events_sha256']
 for name,digest in build['source_sha256'].items():assert sha(out/'candidate'/name)==digest,name
 for r in m['files']+m['native_files']:
  p=Path(r['retained']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],str(p)
verify();listing=subprocess.run([str(binary),'--list'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,check=True).stdout;(dest/'test-membership.txt').write_text(listing)
ledger={'schema':1,'status':'running','build_manifest_sha256':sha(build_path),'binary_sha256':build['binary_sha256'],'source_inventory_sha256':build['source_inventory_sha256'],'closure_manifest_sha256':build['closure_manifest_sha256'],'complete_closure_verified_before':True,'build_script_and_event_hashes_independently_verified':True,'cpu_affinity':sorted(os.sched_getaffinity(0)),'performance_gate':False,'explicit_exclusions':['all ignored tests','certified_scalar full six/seven-point reduction tests','other test namespaces outside the recorded filters'],'test_membership_sha256':sha(dest/'test-membership.txt'),'groups':{}}
record=dest/'unit-run.json';save=lambda:record.write_text(json.dumps(ledger,indent=2)+'\n');save()
for label,(filters,timeout,expected,ignored) in checks.items():
 command=[str(binary),*filters,'--test-threads=1','--nocapture'];row={'status':'running','command':command,'timeout_seconds':timeout,'expected_passed':expected,'expected_ignored':ignored,'membership':[line for line in listing.splitlines() if any(line.startswith(f) for f in filters)]};ledger['groups'][label]=row;save();start=time.monotonic()
 with (dest/f'{label}-tests.log').open('w') as log:
  try:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=timeout);row['returncode']=r.returncode
  except subprocess.TimeoutExpired:row['returncode']=None;row['timed_out']=True
 row['wall_seconds']=time.monotonic()-start;text=(dest/f'{label}-tests.log').read_text();match=re.search(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored;',text)
 if match:row['test_result']={'status':match[1],'passed':int(match[2]),'failed':int(match[3]),'ignored':int(match[4])}
 row['log_sha256']=sha(dest/f'{label}-tests.log');row['status']='passed' if row['returncode']==0 and row.get('test_result')=={'status':'ok','passed':expected,'failed':0,'ignored':ignored} else 'failed';save();print(label,row['status'],row.get('test_result'),flush=True)
verify();ledger['complete_closure_verified_after']=True;ledger['status']='passed' if all(row['status']=='passed' for row in ledger['groups'].values()) else 'failed';save();raise SystemExit(0 if ledger['status']=='passed' else 1)
