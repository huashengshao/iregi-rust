from pathlib import Path
import hashlib,json,shutil,tarfile
root=Path.cwd();base=root/'target/native-shared-binary';destination=root/'validation/native-shared-binary';destination.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
allowed={'.rs','.py','.md','.json','.log','.csv','.patch','.asm'}
for p in sorted(base.iterdir()):
 if p.is_file() and p.suffix in allowed:shutil.copy2(p,destination/p.name)
if (base/'quiet-window').exists():shutil.copytree(base/'quiet-window',destination/'quiet-window',dirs_exist_ok=True)
archive=destination/'generated-sources.tar.gz';members=[]
with tarfile.open(archive,'w:gz') as tar:
 for folder in ['baseline','candidate','b0','c0','fixture']:
  for p in sorted((base/folder).rglob('*')):
   if p.is_file() and p.suffix in ['.rs','.txt']:
    name=str(p.relative_to(base));tar.add(p,arcname=name);members.append({'path':name,'sha256':sha(p),'bytes':p.stat().st_size})
(destination/'source-archive.json').write_text(json.dumps({'archive_sha256':sha(archive),'members':members},indent=2)+'\n')
record={}
for reportname in ['generator-build.json','fixture-generator-build.json','probe-build.json']:
 report=json.loads((base/reportname).read_text())
 for name,digest in report['inputs'].items():
  if name.startswith('target/native-shared-binary/'):
   p=root/name;assert sha(p)==digest,name;record[name]=digest
(destination/'build-source-verification.json').write_text(json.dumps({'checked_sources':record,'all_match':True},indent=2)+'\n')
files=[{'path':str(p.relative_to(destination)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(destination.rglob('*')) if p.is_file() and p.name!='manifest.json']
(destination/'manifest.json').write_text(json.dumps({'scope':'Private shared binary native candidate; production unchanged. Generated sources archived; binaries, runtime archives and license omitted. Read qualification.json for measured status.','files':files},indent=2)+'\n')
print(json.dumps({'files':len(files),'archived_sources':len(members),'checked_build_sources':len(record),'qualification_sha256':sha(destination/'qualification.json'),'manifest_sha256':sha(destination/'manifest.json')},indent=2))
