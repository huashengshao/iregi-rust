"""Recover completed Cargo artifacts after verbose-stdout parser failure; no build."""
from pathlib import Path
import hashlib,json,shutil,sys
root=Path.cwd();out=root/'target/benchmark/workspace-builds/80949db-default-resume'
bundle=out/'recovery-builder';bundle.mkdir(exist_ok=True)
for name in ['build_workspace.py','build_physical.py','run.py']:
 source=root/'validation/benchmark'/name if name=='build_workspace.py' else out/'builder'/name
 shutil.copy2(source,bundle/name)
sys.path.insert(0,str(bundle))
import build_workspace as b
from build_physical import retained_source,physical_asset_hashes
from run import source_hashes
failed=out/'workspace-build.json';data=json.loads(failed.read_text())
assert data['status']=='failed' and data['resources']['returncode']==0
assert data['error'].startswith('JSONDecodeError:') or 'Expecting value' in data['error']
source=Path(data['source_root']);revision=data['source_revision']
retained_source(root,revision);b.verify_snapshot_tree(source,revision);b.verify_builder(out)
assert data['source_sha256_before']==data['source_sha256']==source_hashes(source)
assert data['assets_sha256_before']==data['assets_sha256']==physical_asset_hashes(source)
reference_path,reference_binary,reference=b.reference_manifest(root,source)
assert b.digest(out/'bin/iregi-benchmark')==reference['binary_sha256']
examples,libraries=b.inspect_artifacts(out/'cargo.jsonl',False)
for name,event in examples.items():assert event['target']['src_path'].startswith(str(source))
recovered=out/'workspace-build-recovered.json';data['manifest_path']=str(recovered)
data['recovery']={'original_failed_manifest':str(failed),'original_failed_manifest_sha256':b.digest(failed),'original_error':data['error'],'recovery_script':str(Path(__file__).resolve()),'recovery_script_sha256':b.digest(Path(__file__)),'recovered_at':b.timestamp(),'recompiled':False,'reason':'Cargo -vv interleaves package-prefixed build-script stdout with JSON compiler events. Strict artifact parser now accepts that diagnostic format. Raw stream retained; malformed JSON and unrecognized text still fail.','recovery_builder':{str(p):b.digest(p) for p in sorted(bundle.glob('*.py'))}}
data['cargo_artifacts']={'examples':examples,'libraries':libraries}
data['cargo_verbose_stdout_lines']=sum(bool(l.strip()) and not l.lstrip().startswith('{') for l in (out/'cargo.jsonl').read_text().splitlines())
data['binaries']={name:b.retain_file(event['executable'],out/'bin'/name) for name,event in examples.items()}
data['archives']=[b.retain_file(path,out/'deps'/Path(path).name) for path in sorted({filename for event in libraries for filename in event['filenames'] if filename.endswith('.rlib')})]
data.pop('error',None);data.update(status='complete',provenance_qualified=True,finished_at=b.timestamp())
b.save(recovered,data);b.publish(root,out,data)
print(json.dumps({'manifest':str(recovered),'status':data['status'],'resources':data['resources'],'binaries':data['binaries'],'verbose_stdout_lines':data['cargo_verbose_stdout_lines']},indent=2))
