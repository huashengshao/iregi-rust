#!/usr/bin/env python3
"""Seal immutable saved public-rescue records; no native invocation."""
from pathlib import Path
import gzip,hashlib,importlib.util,io,json,tarfile,sys
sys.dont_write_bytecode=True
ROOT=Path.cwd().resolve();HERE=Path(__file__).resolve().parent;DEST=ROOT/'validation/public-six-point-precision-rescue-rank6';PARENT=ROOT/'validation/n6-rank6-generalized-current-cli';PREFIX=str(ROOT)+'/'
def sha(body):return hashlib.sha256(body).hexdigest()
def desc(body):return {'sha256':sha(body),'bytes':len(body)}
def read(path):return json.loads(Path(path).read_text())
def require(ok,why):
 if not ok:raise ValueError(why)
def main():
 require(not DEST.exists(),'preserve sealed capsule');require(read(HERE/'capture-001/receipt.json')['status']=='passed_public_specialized_precision_rescue_840','terminal actual public capture');require(read(HERE/'independent-rescue-saved-review.json')['status']=='passed_independent_saved_public_specialized_rescue','independent full saved gate passed')
 require(sha((PARENT/'manifest.json').read_bytes())=='aa6af6c5a40f012331b17b21aa4c338a38c55789e59109fb8b8aabc1b24d19f1','fixed retained failures/DD parent')
 spec=importlib.util.spec_from_file_location('tensor_rescue_capsule_cli_parent',PARENT/'check.py');parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent);inherited=parent.restore_files(read(PARENT/'manifest.json'))
 known={sha(body):alias for alias,body in inherited.items()};payload={};aliases={};all_files=dict(inherited)
 for path in sorted(HERE.rglob('*')):
  if not path.is_file() or '__pycache__' in path.parts or path.name in ['frozen-tests','frozen-cli'] or path.name.endswith('.partial'):continue
  alias=str(path.relative_to(ROOT));body=path.read_bytes();digest=sha(body)
  if digest in known:aliases[alias]={'source':known[digest],**desc(body)}
  else:payload[alias]=body;known[digest]=alias
  require(alias not in all_files or all_files[alias]==body,'historical alias collision');all_files[alias]=body
 omitted={}
 for directory in ['tests-001','capture-001']:
  r=read(HERE/directory/'receipt.json')
  for absolute,digest in r['inputs'].items():
   alias=absolute.removeprefix(PREFIX)
   if alias in all_files:require(sha(all_files[alias])==digest,'retained phase historical guard '+alias)
   else:omitted[absolute]=digest
 raw=io.BytesIO()
 with tarfile.open(fileobj=raw,mode='w') as archive:
  for alias,body in sorted(payload.items()):item=tarfile.TarInfo(alias);item.size=len(body);item.mode=0o644;item.mtime=0;archive.addfile(item,io.BytesIO(body))
 DEST.mkdir(parents=True);(DEST/'payload.tar.gz').write_bytes(gzip.compress(raw.getvalue(),mtime=0));(DEST/'check.py').write_bytes((HERE/'capsule_check.py').read_bytes());(DEST/'package.py').write_bytes(Path(__file__).read_bytes())
 (DEST/'README.md').write_text('''# Public N6 rank-six binary64 precision rescue

One actual public CLI request uses the specialized six-point engine at output53,
working128 and verification256 bits. Its primary correctly reports cancellation
Unstable; the existing shared Rust convergence/output-roundtrip policy accepts
one rescued f64 sample. Independent saved arithmetic checks all840 native
coefficients against admitted quad IREGI at1e-10, plus420IR and210convergentUV
controls. Maximum normalized reference error1.8669790225160342e-16.

The capsule preserves the actual85-source Cargo context, selected artifact
records, initial compile inference failure, successful second build, five new
and three old focused tests plus an actual N6 constructor/generic-cache test,
all capture/profiling/controller bytes, and independent build/math/terminal
reviews. An auditor-only initial incorrect historical hash control is also
preserved with its corrected pass. Native executables are omitted with exact
recorded hashes. The parent retains the earlier generic/f64/dotted/D6 failures
and DD pass; no failure is erased or upgraded.

CLI exports only the final roundedf64 tensor. Internal128/256 tensor arrays
are not serialized, so the independent saved checker cannot reconstruct their
numerical convergence from absent payloads. Actual shared Rust policy, focused
tests and tagged stage counters are the evidence for that acceptance. Returned
rescued scalar sensitivity context is explicitly unavailable after precision
conversion; no stale envelope is reused. No Dual, dotted, D6, rigorouserror or
performance qualification is claimed. Durations are engineering diagnostics.

Reproduce without compiler/native evaluator/network:

    python3 validation/public-six-point-precision-rescue-rank6/check.py

`restore_files(manifest)` restores project-relative saved byte aliases, including
the85-source snapshot. Identical older source bodies are inherited without
archive duplication. Later live-main edits do not redefine this frozen context.
''')
 m={'schema_version':1,'status':'scoped_actual_public_six_point_rank6_precision_rescue_saved_capsule','capsule_directory':str(DEST.relative_to(ROOT)),'parent_files':{str(p.relative_to(ROOT)):desc(p.read_bytes()) for p in [PARENT/'manifest.json',PARENT/'check.py']},'payload_members':{alias:desc(body) for alias,body in payload.items()},'preserved_aliases':aliases,'omitted_native_inputs':omitted,'owned_cli_sha256':'62694002bc48b71b6b538f0c5d2dad30a73b71dbfb47a638ea394413de7e73cb','independent_saved_review_sha256':sha((HERE/'independent-rescue-saved-review.json').read_bytes()),'capsule_files':{p.name:desc(p.read_bytes()) for p in DEST.iterdir() if p.is_file()},'higher_precision_arrays_exported':False,'Dual_dotted_D6_performance_qualified':False}
 (DEST/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'manifest_sha256':sha((DEST/'manifest.json').read_bytes()),'payload_bytes':(DEST/'payload.tar.gz').stat().st_size,'new_bodies':len(payload),'inherited_or_shared_body_aliases':len(aliases)},indent=2))
if __name__=='__main__':main()
