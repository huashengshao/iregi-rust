from pathlib import Path
import hashlib,json,shutil,tarfile
root=Path.cwd();base=root/'target/native-master-replay';dest=root/'validation/native-master-replay';dest.mkdir(exist_ok=True);sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
prep=json.loads((base/'preparation.json').read_text());build=json.loads((base/'capture-build.json').read_text());capture=json.loads((base/'capture-results.json').read_text())
assert capture['status']=='passed' and capture['binary_unchanged'] and capture['reference_unchanged'] and capture['sources_unchanged']
assert build['sources_before']==build['sources_after']
for path,digest in build['sources_before'].items():assert sha(base/path)==digest,path
summary={'status':'actual-master-capture-qualified-replay-unrun','source_revision':prep['source_revision'],'excluded_working_changes':prep['working_differences_excluded'],'scope':capture['scope'],'captures_sha256':sha(base/'capture-results.json'),'input_sha256':sha(base/'inputs.json'),'build_sha256':sha(base/'capture-build.json'),'rows':[]}
total_master=0;total_tensors=0
for row in capture['rows']:
 assert row['status']=='passed';actual=row['capture'];groups=actual['master_captures'];order=[{'family':g['family'],'master_rows':g['rows'],'leaf_major_requests':g['requests'],'input_components':g['components'],'valid_master_rows':all(e is None for e in g['errors'])} for g in groups]
 tensors=sum(len(l['moments'])*4 for l in actual['lanes']);total_tensors+=tensors;total_master+=sum(g['rows'] for g in groups)
 summary['rows'].append({'id':row['id'],'outer_batch':row['outer_batch'],'group_order':order,'final_complex_laurent_outputs':tensors,'reference_agreement':row['correctness'],'execution':actual['execution']})
summary.update(total_master_rows=total_master,total_raw_master_complex_outputs_to_replay=6*total_master,total_final_complex_laurent_outputs=total_tensors,production_changed=False,timing='Unrun. Capture is correctness-only; no latency/throughput claim.')
(base/'capture-qualification.json').write_text(json.dumps(summary,indent=2)+'\n')
names=['README.md','preparation.json','capture-build.json','capture-results.json','capture-qualification.json','inputs.json','capture.patch','prepare.py','build_capture.py','run_capture.py','package_capture.py','core-build.log','capture-build.log','capture.stderr.log','reference.stderr.log','native-source.json','prepare_replay.py']
for name in names:
 if (base/name).exists():shutil.copy2(base/name,dest/name)
shutil.copytree(base/'source',dest/'source',dirs_exist_ok=True)
prior=base/'earlier-attempts/working-source-moved/failure.json'
if prior.exists():shutil.copy2(prior,dest/'preparation-guard.json')
archive=dest/'captured-core-sources.tar.gz';members=[]
with tarfile.open(archive,'w:gz') as tar:
 for p in sorted((base/'core').rglob('*')):
  if p.is_file():
   name=str(p.relative_to(base/'core'));tar.add(p,arcname=name);members.append({'path':name,'sha256':sha(p),'bytes':p.stat().st_size})
(dest/'source-archive.json').write_text(json.dumps({'archive_sha256':sha(archive),'members':members},indent=2)+'\n')
files=[{'path':str(p.relative_to(dest)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(dest.rglob('*')) if p.is_file() and p.name!='manifest.json']
(dest/'manifest.json').write_text(json.dumps({'scope':'Actual core request capture; private replay preparation only; production unchanged','files':files},indent=2)+'\n')
print(json.dumps({'files':len(files),'source_members':len(members),'master_rows':total_master,'final_complex_outputs':total_tensors,'qualification_sha256':sha(dest/'capture-qualification.json'),'manifest_sha256':sha(dest/'manifest.json')},indent=2))
