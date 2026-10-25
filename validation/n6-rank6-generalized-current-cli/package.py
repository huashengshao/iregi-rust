#!/usr/bin/env python3
"""Seal the six terminal saved CLI attempts; never run a native job."""
from pathlib import Path
import gzip,hashlib,importlib.util,io,json,tarfile,sys
sys.dont_write_bytecode=True
ROOT=Path.cwd().resolve();HERE=Path(__file__).resolve().parent
DEST=ROOT/'validation/n6-rank6-generalized-current-cli';PARENT=ROOT/'validation/quad-original-iregi-generalized-n6-rank6'
PREFIX='/shared/external/iregi/iregi-rust/'
def sha(body):return hashlib.sha256(body).hexdigest()
def desc(body):return {'sha256':sha(body),'bytes':len(body)}
def read(p):return json.loads(p.read_text())
def require(ok,why):
 if not ok:raise ValueError(why)
def main():
 names=['n6_rank6_first_dot2-128-001','n6_rank6_unit_control-f64-001','n6_rank6_unit_control-pv-dd-001','n6_rank6_unit_control-f64-rescue-001','n6_rank6_unit_control-pv-f64-001','n6_rank6_unit_D6-128-001']
 captures=[]
 for name in names:
  p=HERE/'captures'/name;r=read(p/'receipt.json');require(r['status'] in ['passed_complete_capture_and_840_quad_slots','failed_or_incomplete'],'all six attempts must be terminal before sealing')
  stdout=(p/'stdout.json').read_bytes();d=json.loads(stdout) if stdout else None
  captures.append({'directory':name,'status':r['status'],'elapsed_seconds':r['elapsed_seconds'],'reason':d['samples'][0].get('reason') if d and d['samples'][0]['status']=='failed' else None,'no_array':not d or d['samples'][0]['status']!='success'})
 require(not DEST.exists(),'preserve any existing capsule')
 require(sha((PARENT/'manifest.json').read_bytes())=='90e4ede40dbf46e537064dea0e85309b0079bfd12d245f7dc9ba658aa16d2f0e','exact admitted seven-quad parent')
 spec=importlib.util.spec_from_file_location('restricted_n6_quad_parent',PARENT/'check.py');parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent);inherited=parent.restore_files(read(PARENT/'manifest.json'))
 payload={}
 for path in HERE.rglob('*'):
  if not path.is_file() or '__pycache__' in path.parts or path.name in ['cli-frozen','cli-owned'] or path.name.endswith('.partial'):continue
  alias=str(path.relative_to(ROOT));body=path.read_bytes();require(alias not in inherited or inherited[alias]==body,'no inherited alias collision');payload[alias]=body
 life=ROOT/'target/ibp-workspace-preparation-research/profile-n2-rank7-128/lifecycle-profile.py';payload[str(life.relative_to(ROOT))]=life.read_bytes()
 merged={**inherited,**payload};omitted={}
 for name in names:
  r=read(HERE/'captures'/name/'receipt.json')
  for absolute,digest in r['inputs'].items():
   alias=absolute.removeprefix(PREFIX)
   if alias in merged:require(sha(merged[alias])==digest,'preserved exact historical input '+alias)
   else:
    require(Path(absolute).name in ['cli-frozen','cli-owned'],'only owned native products omitted '+absolute)
    require(absolute not in omitted or omitted[absolute]==digest,'omitted binary hash collision');omitted[absolute]=digest
 raw=io.BytesIO()
 with tarfile.open(fileobj=raw,mode='w') as archive:
  for alias,body in sorted(payload.items()):
   item=tarfile.TarInfo(alias);item.size=len(body);item.mode=0o644;item.mtime=0;archive.addfile(item,io.BytesIO(body))
 DEST.mkdir(parents=True);(DEST/'payload.tar.gz').write_bytes(gzip.compress(raw.getvalue(),mtime=0));(DEST/'check.py').write_bytes((HERE/'capsule_check.py').read_bytes());(DEST/'package.py').write_bytes(Path(__file__).read_bytes())
 successful=sum(row['status'].startswith('passed') for row in captures)
 (DEST/'README.md').write_text('''# Restricted N6/rank6 current-CLI record

This capsule retains six distinct owned attempts from one actual Cargo CLI
artifact, its77 selected immutable source files, original inputs, complete JSON
stdout, profile logs, controller source snapshots and historical lifecycle
receipts. The large native executable is omitted with its exact recorded hash;
no fresh current-main, compiler, native or performance qualification is implied.

Ordinary DD requestedPV/SixPoint passes all840 independent original-quad slots
at1e-10;106 working bits do not imply106-bit achieved accuracy. Generic first-dot
Float128 timed out at its original900s preparation cap without arrays. Generic
f64, its explicit128/256 rescue and separate specializedPVf64 retain their
Unstable/rejected outcomes. The independent unitD6Float128 outcome is retained
as captured. No failed or unrun result is replaced by successful zero; D6
Float256/hminus and other dotted partners remain unrun here. Consult manifest
capture statuses and replay output for the actual successful-array count.

The admitted seven-array repaired original-quad reference parent is inherited
by exact byte pins; its generalized finite-identity/precision limitations remain.
All UV/IR slots, including84possible degree6 D6UV coefficients, are retained.
The checker uses only Python standard library and saved bytes. It restores the
parent, verifies exact payload/source/controller identities, replays every
available840-slot success gate, and confirms preserved failures. No compiler,
native evaluator, subprocess, PID probe or network is used.

Reproduce from project root:

    python3 validation/n6-rank6-generalized-current-cli/check.py

This is a restricted saved correctness record with visible open feature gaps,
not a full generalized-power, dimension-shift, numeric-type or performance claim.
''')
 m={'schema_version':1,'status':'restricted_saved_current_CLI_N6_rank6_record_with_visible_failures','capsule_directory':str(DEST.relative_to(ROOT)),'owned_cli_sha256':'82b9865a153e31f93e99e192773db56137e441cc009b0c6c1b8f7007743f766c','parent_files':{str(p.relative_to(ROOT)):desc(p.read_bytes()) for p in [PARENT/'manifest.json',PARENT/'check.py']},'payload_members':{alias:desc(body) for alias,body in payload.items()},'omitted_native_inputs':omitted,'captures':captures,'successful_arrays':successful,'replayed_reference_slots':840*successful,'capsule_files':{p.name:desc(p.read_bytes()) for p in DEST.iterdir() if p.is_file()},'full_generalized_numeric_domain_qualified':False,'performance_qualified':False}
 (DEST/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'manifest_sha256':sha((DEST/'manifest.json').read_bytes()),'saved_files':len(payload),'payload_bytes':(DEST/'payload.tar.gz').stat().st_size,'successful_arrays':successful},indent=2))
if __name__=='__main__':main()
