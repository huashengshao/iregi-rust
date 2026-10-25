#!/usr/bin/env python3
"""Seal saved Hybrid evidence only; omit native products with recorded hashes."""
from pathlib import Path
import gzip,hashlib,importlib.util,io,json,sys,tarfile
sys.dont_write_bytecode=True
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;DEST=ROOT/'validation/six-point-hybrid-rank6';PARENT=ROOT/'validation/public-six-point-precision-rescue-rank6';PREFIX=str(ROOT)+'/'
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'sha256':sha(b),'bytes':len(b)}
def require(ok,why):
 if not ok:raise ValueError(why)
def j(p):return json.loads(p.read_text())
def main():
 require(not DEST.exists(),'preserve sealed capsule');require(sha((PARENT/'manifest.json').read_bytes())=='e6f75d74e678ca954df98b5f349de39cde2cf80b94df8390498872e5335afeea','fixed public rescue parent')
 spec=importlib.util.spec_from_file_location('hybrid_capsule_parent',PARENT/'check.py');parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent);files=parent.restore_files(j(PARENT/'manifest.json'));known={sha(b):n for n,b in files.items()};members={};aliases={}
 def add(p):
  n=str(p.relative_to(ROOT));b=p.read_bytes();d=sha(b);require(not b.startswith(b'\x7fELF'),'never archive native executable');require(b'SYMBOLICA_LICENSE=S-' not in b,'no license literal');require(n not in files or files[n]==b,'alias identity collision')
  if d in known:aliases[n]={'source':known[d],**desc(b)}
  else:members[n]=b;known[d]=n
  files[n]=b
 for folder in ['target/six-point-hybrid-focused-tests-v1','target/six-point-hybrid-r6-v1','target/six-point-hybrid-r6-v2','target/six-point-hybrid-r6-observer-correction']:
  for p in sorted((ROOT/folder).rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts:add(p)
 for label in ['build-005','build-006']:
  folder=ROOT/'target/certified-tensor-qualification'/label
  for p in sorted(folder.rglob('*')):
   if p.is_file() and p.name not in ['frozen-tests','frozen-capture'] and '__pycache__' not in p.parts:add(p)
 for name in ['target/quad-iregi-source-audit/capture-v6-001/request-4.stdout','target/quad-iregi-source-audit/capture-v6-001/run.json','target/quad-iregi-source-audit/independent/resume-auditor-v6-full-array-numeric-review.json']:add(ROOT/name)
 omitted={}
 for name in ['target/six-point-hybrid-focused-tests-v1/tests-001/receipt.json','target/six-point-hybrid-r6-v1/capture-001/receipt.json','target/six-point-hybrid-r6-v2/capture-001/receipt.json']:
  for absolute,d in j(ROOT/name)['inputs'].items():
   alias=absolute.removeprefix(PREFIX)
   if alias in files:require(sha(files[alias])==d,'available historical guard '+alias)
   else:omitted[absolute]=d
 raw=io.BytesIO()
 with tarfile.open(fileobj=raw,mode='w')as a:
  for n,b in sorted(members.items()):item=tarfile.TarInfo(n);item.mode=0o644;item.size=len(b);item.mtime=0;a.addfile(item,io.BytesIO(b))
 DEST.mkdir();(DEST/'payload.tar.gz').write_bytes(gzip.compress(raw.getvalue(),mtime=0));(DEST/'check.py').write_bytes((HERE/'hybrid_capsule_check.py').read_bytes());(DEST/'package.py').write_bytes(Path(__file__).read_bytes())
 qualification={'status':'scoped_actual_ordinary_six_point_rank6_Hybrid_numerical_admission','focused_tests_passed':13,'complete_complex_reference_comparisons':840,'exact_specialized_PV_delegations':840,'independent_zero_pole_checks':630,'maximum_normalized_reference_error':'9.334130176410016041e-17','fixture':'one real-mass unit-power N6 rank6 Float128/requested53 point; invalid-mu neighbor and empty lifecycle','requested_algorithm':'Hybrid','actual_primary':'specialized six-point PV','outer_generic_IBP_fallback_rows':0,'nested_PV_fallback_flags_preserved':True,'old_nested_flag_observer_failure_preserved':True,'corrected_native_assertion_test_exit':0,'corrected_controller_status':'failed_saved_parser_only_preserved','additive_saved_extraction_passed':True,'no_additional_integral_for_extraction':True,'actual_N6_generic_IBP_fallback_success_qualified':False,'Dual_dotted_dimension_shift_complex_mass_exceptional_or_performance_qualified':False,'historical_process_absence':'saved attestation, no new PID proof in portable replay','native_products_omitted':True}
 (DEST/'qualification.json').write_text(json.dumps(qualification,indent=2)+'\n')
 (DEST/'README.md').write_text('''# Ordinary six-point rank-six Hybrid closure\n\nThirteen focused tests validate lazy immutable IBP preparation, one batched retry of\nUnstable rows, independent numeric workspaces, full component scatter/context, failure\nisolation, counters, and real low-N IBP work. The actual ordinary N6 rank-six fixture\nthen uses specialized PV as Hybrid primary. All840 complex native Laurent coefficients\nagree exactly with explicit PV and pass the admitted original quad IBP prefix gate at\n1e-10; maximum dimensionally normalized error is9.334130176410016e-17. All630 massive\nzero-pole checks pass. The fixture uses Float128/requested53, one valid sample plus an\ninvalid-mu neighbor; successful input preservation, coupled-context and empty reset\nassertions remain in the native test.\n\nThe outer IBP fallback was not needed on this point. Existing nested PV child retries\nremain visible and are not counted as outer Hybrid retries. Synthetic multicomponent\ntests plus a real A0 IBP control verify fallback orchestration; this does not qualify\na genuine numerical N6 IBP fallback success.\n\nThe first numeric invocation failed an overly restrictive observer assertion after\nits coefficient comparisons. It is preserved. The corrected native test passed, but\nits controller could not parse a payload sharing libtest's test-name line. That\nfailed controller receipt is also preserved. Additive saved-only extraction recovers\nthe unique complete payload from immutable stdout; no integral was repeated for\nthis extraction. The portable checker independently repeats the840 reference,840PV\nand630 pole decisions from quoted rational arrays.\n\nActual76- and77-source Cargo snapshots are restored via exact hashes, inheriting\nidentical generated master/source bodies from the public precision-rescue parent.\nNative binaries/toolchain files are omitted with historical recorded identities.\nSaved process absence and bounds remain historical attestations; portable replay\ndoes not inspect PIDs or run any compiler, evaluator or network operation. No public\nDual, generalized/dotted/dimension-shift, complex/exceptional or performance\nqualification is claimed. Engineering durations are not timing benchmarks.\n\nReproduce:\n\n    python3 -B validation/six-point-hybrid-rank6/check.py\n''')
 m={'schema_version':1,'status':qualification['status'],'capsule_directory':str(DEST.relative_to(ROOT)),'parent_files':{str(p.relative_to(ROOT)):desc(p.read_bytes())for p in [PARENT/'manifest.json',PARENT/'check.py']},'payload_members':{n:desc(b)for n,b in members.items()},'preserved_aliases':aliases,'omitted_native_inputs':omitted,'actual_source_counts':[76,77],'focused_tests':13,'reference_comparisons':840,'exact_PV_delegations':840,'zero_pole_checks':630,'full_N6_IBP_fallback_success_qualified':False,'public_Dual_generalized_or_performance_qualified':False,'capsule_files':{p.name:desc(p.read_bytes())for p in DEST.iterdir()if p.is_file()}}
 (DEST/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'manifest':sha((DEST/'manifest.json').read_bytes()),'payload_bytes':(DEST/'payload.tar.gz').stat().st_size,'payload_members':len(members),'same_body_aliases':len(aliases),'omitted_native_inputs':len(omitted)},indent=2))
if __name__=='__main__':main()
