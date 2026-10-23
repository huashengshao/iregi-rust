from pathlib import Path
import gzip,hashlib,io,json,shutil,tarfile
root=Path.cwd();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
window=root/'target/benchmark/optimization-quiet-20261023'
for name in ['native-stack-batch','native-dense-span']:
 base=root/'target'/name;out=root/'validation'/name;out.mkdir(exist_ok=True)
 for p in sorted(base.iterdir()):
  if p.is_file() and p.suffix in ['.py','.rs','.json','.jsonl','.csv','.log','.txt','.md','.patch'] and p.name not in ['bundle.py']:
   shutil.copyfile(p,out/p.name)
 for p in (base/'history').rglob('*'):
  if p.is_file() and p.suffix in ['.py','.rs','.json','.csv','.log','.txt']:
   dst=out/p.relative_to(base);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
 (out/'quiet-window').mkdir(exist_ok=True)
 for p in window.glob('*.json'):shutil.copyfile(p,out/'quiet-window'/p.name)
 if name=='native-dense-span':
  members={}
  with (out/'generated-sources.tar.gz').open('wb') as raw:
   with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
    with tarfile.open(mode='w',fileobj=gz) as archive:
     for dirname in ['baseline','candidate','b0','c0','fixture']:
      for p in sorted((base/dirname).rglob('*')):
       if p.is_file() and p.suffix in ['.rs','.txt']:
        member=str(p.relative_to(base));data=p.read_bytes();members[member]=hashlib.sha256(data).hexdigest();info=tarfile.TarInfo(member);info.size=len(data);info.mode=0o644;archive.addfile(info,io.BytesIO(data))
     for p in sorted(base.glob('*.asm')):
      member=p.name;data=p.read_bytes();members[member]=hashlib.sha256(data).hexdigest();info=tarfile.TarInfo(member);info.size=len(data);info.mode=0o644;archive.addfile(info,io.BytesIO(data))
  with tarfile.open(out/'generated-sources.tar.gz','r:gz') as archive:
   assert {m.name:hashlib.sha256(archive.extractfile(m).read()).hexdigest() for m in archive}==members
  (out/'generated-source-sha256.json').write_text(json.dumps(members,indent=2)+'\n')
  (out/'restore.py').write_text('''from pathlib import Path
import hashlib,json,shutil,tarfile
root=Path.cwd();out=root/'validation/native-dense-span';base=root/'target/native-dense-span';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((out/'manifest.json').read_text())
for name,digest in m['files'].items():assert sha(out/name)==digest,(name,'evidence digest mismatch')
assert sha(root/'validation/benchmark/run.py')==m['analysis_helper_sha256']
assert not base.exists(),'refusing to overwrite target/native-dense-span'
base.mkdir(parents=True)
for p in out.rglob('*'):
 if p.is_file() and p.name not in ['manifest.json','generated-sources.tar.gz']:
  dst=base/p.relative_to(out);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
expected=json.loads((out/'generated-source-sha256.json').read_text())
with tarfile.open(out/'generated-sources.tar.gz','r:gz') as archive:
 for member in archive:
  assert member.isfile() and member.name in expected
  data=archive.extractfile(member).read();assert hashlib.sha256(data).hexdigest()==expected[member.name]
  dst=base/member.name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
print('Verified/restored dense experiment evidence and exact sources; runtime archives, binaries and private license values are excluded.')
''')
  manifest={'status':'dense-active-span-candidate-rejected','production_changes':False,'qualified_domains':['f64'],'generated_archive_files':len(members),'generated_rust_sources':sum(name.endswith('.rs') for name in members),'generated_assembly_files':sum(name.endswith('.asm') for name in members),'analysis_helper_sha256':sha(root/'validation/benchmark/run.py')}
 else:
  manifest=json.loads((out/'manifest.json').read_text());manifest['status']='native-allocation-candidate-rejected';manifest['pending']=[]
 manifest['files']={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json'}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 for p,digest in manifest['files'].items():assert sha(out/p)==digest
 print(json.dumps({'bundle':str(out.relative_to(root)),'files':len(manifest['files']),'qualification_sha256':sha(out/'qualification.json'),'manifest_sha256':sha(out/'manifest.json')}))
