"""Bounded current-planar interaction tests; no timing/production qualification."""
from pathlib import Path
import hashlib,json,os,re,subprocess,time
root=Path.cwd();out=Path(__file__).resolve().parent;artifacts=out/'candidate/artifacts';binary=artifacts/'core_tests';build_path=artifacts/'unit-build.json';build=json.loads(build_path.read_text())
assert build['status']=='compiled' and build['returncode']==0 and build['verified_before'] and build['verified_after']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds';m=json.loads((closure/'manifest.json').read_text())
def verify():
 assert sha(binary)==build['binary_sha256'];assert sha(out/'build_next.py')==build['build_script_sha256'];assert sha(out/'sources.json')==build['source_inventory_sha256'];assert sha(closure/'manifest.json')==build['closure_manifest_sha256'];assert sha(closure/'cargo-library-events.json')==build['cargo_library_events_sha256'];assert sha(closure/'workspace-completion.json')==build['workspace_completion_sha256']
 for name,digest in build['source_sha256'].items():assert sha(out/'candidate'/name)==digest,name
 for r in m['files']+m['native_files']:
  p=Path(r['retained']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],str(p)
verify();listing=subprocess.check_output([str(binary),'--list'],text=True);(artifacts/'membership.txt').write_text(listing)
checks=[('slim_planar_complex_full_jet_partition_matches_original_certificate',60),('planar_constructor_rejects_unsupported_contexts_without_an_unchecked_plan',120),('planar_certificate_checks_full_jets_and_primal_chart_units',120),('rounded_zero_rank_determinant_and_homogeneous_families_never_succeed',120),('certified_planar_spatial_binary64_guard_rejection_is_explicit',120),('certified_planar_float_batches_preserve_binary64_target_and_converge',180),('certified_planar_rotating_mixed_jets_match_independent_box_identity',180),('certified_planar_tetrahedron_rank_two_binary64_isolates_failed_rows',120),('public_planar_statistics_profiles_reordering_and_error_reuse',120),('shared_input_validator_preserves_full_jet_check_order',30)]
state={'schema':1,'status':'running','scope':'Current core/slim certificate interaction with standalone certifiedplanar API.9 existingtests+1 new pairedcertificate test. Uses immutable6b24dependency arithmetic; no new publicmaster API nor performanceclaim.','binary_sha256':sha(binary),'build_manifest_sha256':sha(build_path),'script_sha256':sha(Path(__file__)),'cpu_affinity':sorted(os.sched_getaffinity(0)),'complete_closure_verified_before':True,'performance_gate':False,'excluded_tests':['certified_planar_all_330_moments_match_independent_box_identity','public_planar_rank7_precision_artifacts_and_convergence','public_planar_rank7_rectangular_mixed_artifact'],'rows':[]}
record=artifacts/'planar-tests.json';save=lambda:record.write_text(json.dumps(state,indent=2)+'\n');save()
for name,timeout in checks:
 full='certified_planar::tests::'+name;assert full+': test' in listing,full
 command=[str(binary),full,'--exact','--test-threads=1','--nocapture'];log=artifacts/(name+'.log');row={'name':full,'status':'running','command':command,'timeout_seconds':timeout};state['rows'].append(row);save();start=time.monotonic()
 with log.open('w') as handle:
  try:r=subprocess.run(command,stdout=handle,stderr=subprocess.STDOUT,timeout=timeout);row['returncode']=r.returncode
  except subprocess.TimeoutExpired:row['returncode']=None;row['timed_out']=True
 row['wall_seconds_not_performance']=time.monotonic()-start;row['log_sha256']=sha(log);text=log.read_text();matches=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored;',text);row['summary']=matches
 row['status']='passed' if row['returncode']==0 and matches==[('ok','1','0','0')] else 'failed';save();print(name,row['status'],row['wall_seconds_not_performance'],flush=True)
 if row['status']!='passed':break
verify();state['complete_closure_verified_after']=True;state['status']='passed' if len(state['rows'])==10 and all(r['status']=='passed' for r in state['rows']) else 'failed';save();raise SystemExit(0 if state['status']=='passed' else 1)
