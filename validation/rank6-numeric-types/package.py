"""Package new text evidence once, borrowing exact committed reference/source capsules."""
from pathlib import Path
import gzip,hashlib,importlib.util,io,json,sys,tarfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=Path.cwd();DEST=ROOT/'validation/rank6-numeric-types'
spec=importlib.util.spec_from_file_location('_r6_capsule_check',HERE/'check.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
def main():
 inventory=ROOT/'target/lower-n-rank6-numeric-v1/independent-fraction-input-inventory-v1.json';i=c.document(inventory.read_bytes())
 inherited,parent_pins=c.parent_files(ROOT);aliases={};objects={}
 selected=set(i['callback_inputs'])|set(i['checker_and_receipts'])|{str(inventory.relative_to(ROOT))}
 # Preserve exact producer/controller/catalog history and stop records without an
 # archive/dependency walk. The 24 capture payloads come from the reviewed list.
 for directory in ['target/lower-n-rank6-numeric-v1','target/n2-rank6-typed-low-domains-v1']:
  selected.update(str(p.relative_to(ROOT)) for p in (ROOT/directory).iterdir() if p.is_file() and p.suffix in ['.py','.json'])
 selected.update(str(p.relative_to(ROOT)) for p in (ROOT/'target/lower-n-rank6-numeric-v1').glob('*/STOPPED.json'))
 selected.update(str(p.relative_to(ROOT)) for p in (ROOT/'target/lower-n-rank6-numeric-v1').glob('*/qualification.json'))
 for alias in sorted(selected):
  c.safe(alias);path=ROOT/alias;c.require(path.is_file() and not path.is_symlink(),'regular selected text')
  b=path.read_bytes();c.require(not b.startswith((b'\x7fELF',b'\x1f\x8b',b'!<arch>\n',b'MZ',b'PK\x03\x04')),'no native/archive products')
  expected=i['callback_inputs'].get(alias,i['checker_and_receipts'].get(alias))
  if expected:c.require(c.desc(b)==expected,'reviewed selected identity')
  row=c.desc(b)
  if alias in inherited:
   c.require(inherited[alias]==b,'inherited exact alias');row['inherited_alias']=alias
  else:
   member='objects/'+row['sha256'];objects[member]=b;row['member']=member
  aliases[alias]=row
 saved=c.document((ROOT/c.REPORT).read_bytes());qualification={k:saved[k] for k in ['status','passed','capture_count','successful_capture_count','preserved_guard_failure_count','comparison_totals','complete_complex_comparisons','max_normalized_errors','authorship','limitations']}
 qualification.update(independent_saved_audit_sha256=c.digest((ROOT/c.REPORT).read_bytes()),independent_checker_sha256=c.digest((ROOT/c.AUDIT).read_bytes()),independent_semantic_mutations_sha256=c.digest((ROOT/c.MUTATION_REPORT).read_bytes()),scope='one real massive spacelike unit-power h0 PV family per N1..5 at rank6; all24 actual attempts included; no public highpoint Dual, performance or all-feature claim')
 DEST.mkdir(exist_ok=False)
 for name in ['check.py','package.py','README.md']:(DEST/name).write_bytes((HERE/name).read_bytes())
 (DEST/'qualification.json').write_text(json.dumps(qualification,indent=2)+'\n')
 raw=io.BytesIO()
 with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as zipped:
  with tarfile.open(fileobj=zipped,mode='w') as archive:
   for name,b in sorted(objects.items()):
    info=tarfile.TarInfo(name);info.size=len(b);info.mode=0o644;info.mtime=0;archive.addfile(info,io.BytesIO(b))
 (DEST/'payload.tar.gz').write_bytes(raw.getvalue())
 manifest=dict(schema_version=1,status='saved_rank6_numeric_types_scoped_admission',capsule_directory='validation/rank6-numeric-types',parent_files=parent_pins,capsule_files={name:c.desc((DEST/name).read_bytes()) for name in ['check.py','package.py','README.md','qualification.json','payload.tar.gz']},aliases=aliases,payload_members={name:c.desc(b) for name,b in objects.items()},omitted_compiled_artifacts={'target/rank7-numeric-jets-execution/build-002/program-frozen':'480a47a84d28d53597c751f4f5aafa7fa4a0c39ad66a707f6a15c759251828d8'},counts=dict(callback_inputs=147,selected_aliases=len(aliases),new_objects=len(objects),inherited_aliases=sum('inherited_alias' in row for row in aliases.values())))
 (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest_sha256=c.digest((DEST/'manifest.json').read_bytes()),payload_bytes=len(raw.getvalue()),counts=manifest['counts'])))
if __name__=='__main__':main()
