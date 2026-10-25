"""Package new text evidence once, borrowing exact committed reference/source capsules."""
from pathlib import Path
import gzip,hashlib,importlib.util,io,json,sys,tarfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=Path.cwd();DEST=ROOT/'validation/public-four-point-dual-rescue-rank6'
spec=importlib.util.spec_from_file_location('_r6_capsule_check',HERE/'check.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
def main():
 inventory=ROOT/'target/n4-rank6-public-dual-rescue-v1/independent-saved-audit-inventory.json';i=c.document(inventory.read_bytes())
 inherited,parent_pins=c.parent_files(ROOT);aliases={};objects={}
 selected=set(i['callback_inputs'])|set(i['checker_and_receipts'])|{str(inventory.relative_to(ROOT))}
 # Retain actual selected build context as hash-deduplicated Rust/text deltas,
 # plus only the failed product evidence needed for the one-line harness repair.
 build=ROOT/'target/root-frontend-check/build-004';built=c.document((build/'receipt.json').read_bytes())
 selected.update(str((build/'source-snapshot'/name).relative_to(ROOT)) for name in built['source_files'])
 selected.update('target/root-frontend-check/'+name for name in ['build-v4.py','build-004-correction.json','build-004/cargo-0.log','build-004/cargo-numeric-jets-artifact.json','build-003/receipt.json','build-003/cargo-2.log','build-003/source-snapshot/crates/iregi-rust/examples/rank7_numeric_jets/rescue.rs'])
 selected.update(str(p.relative_to(ROOT)) for p in (ROOT/'target/n4-rank6-public-dual-rescue-v1').iterdir() if p.is_file() and p.suffix in ['.py','.json'])
 by_hash={c.digest(body):alias for alias,body in inherited.items()}
 for alias in sorted(selected):
  c.safe(alias);path=ROOT/alias;c.require(path.is_file() and not path.is_symlink(),'regular selected text')
  b=path.read_bytes();c.require(not b.startswith((b'\x7fELF',b'\x1f\x8b',b'!<arch>\n',b'MZ',b'PK\x03\x04')),'no native/archive products')
  expected=i['callback_inputs'].get(alias,i['checker_and_receipts'].get(alias))
  if expected:c.require(c.desc(b)==expected,'reviewed selected identity')
  row=c.desc(b)
  if row['sha256'] in by_hash:
   source=by_hash[row['sha256']];c.require(inherited[source]==b,'inherited exact bytes');row['inherited_alias']=source
  else:
   member='objects/'+row['sha256'];objects[member]=b;row['member']=member
  aliases[alias]=row
 saved=c.document((ROOT/c.REPORT).read_bytes());qualification={k:saved[k] for k in ['status','passed','comparison_counts','max_normalized_errors','binary64_representable_coordinates_checked','actual_stage_counters_and_statuses','preserved_previous_guard_failures','limitations']}
 qualification.update(independent_saved_audit_sha256=c.digest((ROOT/c.REPORT).read_bytes()),independent_checker_sha256=c.digest((ROOT/c.AUDIT).read_bytes()),scope='one actual public TensorRescueWorkspace::new_dual massive spacelike N4R6 unit/h0/PV f64 mixed-Dual cohort; internal128/256 arrays not serialized or independently audited; exact returned values and retained originating guards are qualified')
 DEST.mkdir(exist_ok=False)
 for name in ['check.py','package.py','README.md']:(DEST/name).write_bytes((HERE/name).read_bytes())
 (DEST/'qualification.json').write_text(json.dumps(qualification,indent=2)+'\n')
 raw=io.BytesIO()
 with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as zipped:
  with tarfile.open(fileobj=zipped,mode='w') as archive:
   for name,b in sorted(objects.items()):
    info=tarfile.TarInfo(name);info.size=len(b);info.mode=0o644;info.mtime=0;archive.addfile(info,io.BytesIO(b))
 (DEST/'payload.tar.gz').write_bytes(raw.getvalue())
 manifest=dict(schema_version=1,status='saved_public_four_point_dual_rescue_rank6_scoped_admission',capsule_directory='validation/public-four-point-dual-rescue-rank6',parent_files=parent_pins,capsule_files={name:c.desc((DEST/name).read_bytes()) for name in ['check.py','package.py','README.md','qualification.json','payload.tar.gz']},aliases=aliases,payload_members={name:c.desc(b) for name,b in objects.items()},omitted_compiled_artifacts={'target/root-frontend-check/build-004/frozen-rank6-dual-rescue-jets':'f11bb4c02540fa7adfc849747551cbd52ea7ba8c68b5e999088318da213f3b2f'},counts=dict(callback_inputs=23,selected_aliases=len(aliases),new_objects=len(objects),inherited_aliases=sum('inherited_alias' in row for row in aliases.values())))
 (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest_sha256=c.digest((DEST/'manifest.json').read_bytes()),payload_bytes=len(raw.getvalue()),counts=manifest['counts'])))
if __name__=='__main__':main()
