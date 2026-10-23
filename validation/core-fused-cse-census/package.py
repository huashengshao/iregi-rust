#!/usr/bin/env python3
import datetime, gzip, hashlib, io, json, pathlib, shutil, tarfile
ROOT=pathlib.Path.cwd();HERE=ROOT/'target/core-fused-cse-census';OUT=ROOT/'validation/core-fused-cse-census'
def sha(p):return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def archive(dest,entries):
 data=io.BytesIO()
 with tarfile.open(fileobj=data,mode='w',format=tarfile.PAX_FORMAT) as tar:
  for name,path in sorted(entries):
   content=path.read_bytes();info=tarfile.TarInfo(name);info.size=len(content);info.mode=0o644;info.mtime=0;tar.addfile(info,io.BytesIO(content))
 with open(dest,'wb') as raw:
  with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as zipped:zipped.write(data.getvalue())
OUT.mkdir(exist_ok=False)
for f in ['build.py','run.py','package.py','census.rs','source-manifest.json','source-review.json','supplemental-deps.json','thiserror-metadata.txt','thiserror-cargo-fingerprint.json']:
 shutil.copy2(HERE/f,OUT/f)
for name in ['design.md','source-review.json']:
 shutil.copy2(ROOT/'target/core-fused-cse-proposal'/name,OUT/('proposal-'+name))
shutil.copy2(ROOT/'target/e6-direct-n2/preparation.json',OUT/'dependency-closure.json')
for attempt in ['build-001','build-002']:
 d=OUT/attempt;d.mkdir()
 for name in ['build.json','core.log','driver.log']:shutil.copy2(HERE/attempt/name,d/name)
 if (HERE/attempt/'source').exists():shutil.copytree(HERE/attempt/'source',d/'source')
shutil.copytree(HERE/'runs',OUT/'runs')
core=HERE/'core';entries=[(str(p.relative_to(core)),p) for p in core.rglob('*') if p.is_file()]
archive(OUT/'private-core-source.tar.gz',entries)
save(OUT/'private-core-source-index.json',{name:sha(p) for name,p in entries})
supp=json.loads((HERE/'supplemental-deps.json').read_text());event=next(e for e in supp['completed_metadata_and_proc_macro_events'] if e['target']['name']=='thiserror');crate=pathlib.Path(event['manifest_path']).parent
entries=[(name,crate/name) for name in supp['cached_crate_source_hashes']]
assert all(sha(p)==supp['cached_crate_source_hashes'][n] for n,p in entries)
archive(OUT/'thiserror-source.tar.gz',entries)
run=json.loads((OUT/'runs/n2-r1/run.json').read_text());assert run['status']=='passed' and run['inputs_unchanged']
rows=[p['result'] for p in run['processes']]
assert all(r['status']=='passed' and r['instructions_byte_identical'] and r['before']==r['after'] and r['operations_before']==r['operations_after'] for r in rows)
qualification={'status':'exact_census_passed_candidate_stopped_no_structural_savings','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_head':json.loads((OUT/'source-manifest.json').read_text())['base_head'],'production_changes':False,'adopted':False,'candidate':'Existing ordinary fused evaluator.merge(empty evaluator with same ordered inputs, Some(0)); no further allocator call.','tested_topology':{'propagators':2,'rank':1,'conventions':['IregiNative','OneLoop']},'rows':rows,'exact_outputs_proved':sum(r['exact_outputs_proved'] for r in rows),'control_records_proved':sum(r['control_records_proved'] for r in rows),'stopped_before':[{'propagators':n,'rank':r,'status':'not_run_no_savings_in_primary_target'} for n,r in [(2,0),(3,0),(3,1),(4,2)]],'decision':'Stop this candidate: primary N2/rank1 graphs retain identical exported instruction bytes, operation counts and storage. No floating or timing experiment warranted. This does not establish that every topology has no CSE opportunities.','source_review':json.loads((OUT/'source-review.json').read_text()),'build':{'initial_attempt':'build-001/build.json','qualified_attempt':'build-002/build.json','numerical_dependency_rebuild':False,'supplemental_thiserror':'Bound exact2.0.21/defaultstd sources, Cargo fingerprint and metadata/proc-macro events plus native ELF archive; no completed rlib event available.'},'scope_limitations':['Symbolic root/control identities assume trusted Symbolica structured SSA/liveness/CSE dominance. They are not independent proof of branch-local definedness or eager-domain preservation.','No floating-point, arbitrary precision numerical convergence, Dual, runtime timing or IREGI accuracy/performance acceptance tested.','Argument/certificate/snapping/master/contraction evaluators and separate Dual-primal evaluator are untouched.'],'bindings':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}}
save(OUT/'qualification.json',qualification)
(OUT/'README.md').write_text('''# Ordinary fused core CSE census

The bounded private candidate stopped after its primary target, a rank-one bubble in both native IREGI and OneLoop conventions. Symbolica `merge(empty, Some(0))` produced byte-identical root instructions: native 1,013 instructions / 237 temporary slots / 246 outputs; OneLoop 850 / 147 / 176. All 422 exact roots and 730 normalized control records agreed. No operation or storage savings were found, so no floating or performance experiment followed. Other proposed topologies are explicitly unrun.

Only a validation accessor was appended to a copied core source tree. It reconstructs the production ordinary moment/local-monitor/primal-monitor tuple and uses its existing exact lowering. The candidate merger is applied in the external driver. Production files were unchanged. The first successful build is retained; the second adds two reviewed admission checks before the only run.

The proof delegates algebra to Symbolica and treats helper calls as exact opaque functions with unchanged definitions. Structured SSA/liveness and CSE dominance remain trusted; exact Atom identities alone do not prove branch-local definedness. This is neither numerical nor performance qualification.

Reproduce from the repository working directory with the frozen dependency paths described by `dependency-closure.json` and `supplemental-deps.json`: restore `private-core-source.tar.gz` under `target/core-fused-cse-census/core`, retain the bound driver/scripts, source `scripts/env.sh`, and run `python3 target/core-fused-cse-census/build.py NEW_ATTEMPT`. Adjust the private runner's explicit build path to the new attempt and preserve that change as new provenance. With a valid Symbolica license sourced privately, run `python3 target/core-fused-cse-census/run.py 2 1` into a fresh run directory. Existing attempts and logs must not be overwritten. Each topology has a total 120-second external bound across its two conventions. Build flags are native debug code, no ThinLTO or numerical dependency rebuild.

The supplemental thiserror archive is nonnumerical error-derive support. Its exact 2.0.21/default/std sources, Cargo fingerprint, raw rustc metadata, required proc-macro identity and native ELF object are retained. The available Cargo log records metadata and proc-macro completion, not an rlib completion; the evidence does not invent that event.
''')
save(OUT/'package-manifest.json',{'files':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()},'scope':'Immutable completed exact-only census, rejected candidate; no binaries or secret license files included'})
print(json.dumps({'path':str(OUT),'qualification_sha256':sha(OUT/'qualification.json'),'package_sha256':sha(OUT/'package-manifest.json'),'files':len(list(OUT.rglob('*')))}))
