from pathlib import Path
import hashlib,json,shutil,subprocess,datetime
root=Path.cwd();out=root/'target/real-ball-planar';candidate=out/'candidate';candidate.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=list((root/'crates/iregi-rust').rglob('*'))+[root/'validation/reference/fixtures.json',root/'validation/reference/snapping/reductions.json',root/'validation/pv-high-rank/lightlike-feynman-parameters.json']
original={}
for p in files:
 if not p.is_file():continue
 name=str(p.relative_to(root));original[name]=sha(p);q=candidate/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
core=candidate/'crates/iregi-rust/src'
shutil.copyfile(core/'invariant_certificate.rs',core/'original_invariant_certificate.rs')
text=(core/'exact_zero_certificate.rs').read_text().replace('    invariant_certificate::{','    original_invariant_certificate::{')
(core/'original_exact_zero_certificate.rs').write_text(text)
shutil.copyfile(root/'target/real-ball-core/candidate/crates/iregi-rust/src/invariant_certificate.rs',core/'invariant_certificate.rs')
with (core/'lib.rs').open('a') as f:f.write('\n#[cfg(test)] mod original_invariant_certificate;\n#[cfg(test)] mod original_exact_zero_certificate;\n')
with (core/'certified_planar/public_api_tests.rs').open('a') as f:f.write('\n'+(out/'interaction_test.rs').read_text())
variant={str(p.relative_to(candidate)):sha(p) for p in candidate.rglob('*') if p.is_file()}
data={'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_root':'live current core snapshot at capture; includes uncommitted stability collector','live_source_sha256':original,'variants':{'candidate':variant},'changed_existing_files':[p for p in original if original[p]!=variant[p]],'added_private_modules':[p for p in variant if p not in original],'candidate_patch_source_sha256':sha(core/'invariant_certificate.rs'),'scope':'Current core/planar API interaction with only slim certificate production replacement; original certificate pair and one extra test are validation-only. Uses immutable6b24 dependency arithmetic,not new publicmaster API.'}
(out/'sources.json').write_text(json.dumps(data,indent=2)+'\n');(candidate/'artifacts').mkdir()
s=(root/'target/real-ball-core/build_next.py').read_text().replace("'scope':'Full core source snapshot6b24 + only qualified slim certificate on candidate; no receipts. Unit opt1; matched numerical binary builds opt3.'","'scope':'Current core/planar private snapshot plus slim only and paired certificate validation modules. Immutable6b24 dependency arithmetic; no new public-master qualification.'")
(out/'build_next.py').write_text(s)
print(len(variant),'snapshotted files',data['changed_existing_files'])
