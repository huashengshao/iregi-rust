"""Package saved joint004 evidence; no compiler, evaluator, or numerical call."""
from pathlib import Path
import gzip,hashlib,io,json,tarfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def info(b):return {'sha256':sha(b),'bytes':len(b)}
def j(p):return json.loads(p.read_text())
base=ROOT/'target/affine-component-joint-current-cargo'; plan=j(base/'source-inheritance-plan.json'); archive_rel=str(HERE.relative_to(ROOT)/'payload.tar.gz'); parent_archives={r['archive'] for r in plan['matches'].values()}; files={};payload={};sources={}
with tarfile.open(base/'build-004/actual-main-source-context.tar.gz') as t:
 for m in t:
  if m.isfile():sources[m.name]=t.extractfile(m).read()
for alias,body in sources.items():
 r=plan['sources'][alias];assert info(body)==r
 if alias in plan['matches']:
  inherited=plan['matches'][alias];files[alias]={**r,'archive':inherited['archive'],'member':inherited['member']}
 else:
  member='sources/'+alias;payload[member]=body;files[alias]={**r,'archive':archive_rel,'member':member}
def add(path):
 body=path.read_bytes();alias=str(path.relative_to(ROOT));member='evidence/'+alias
 assert not body.startswith(b'\x7fELF');assert b'SYMBOLICA_LICENSE=S-' not in body
 if alias in files:
  assert info(body)=={k:files[alias][k] for k in ['sha256','bytes']};return
 payload[member]=body;files[alias]={**info(body),'archive':archive_rel,'member':member}
for p in base.rglob('*'):
 if p.is_file() and p.suffix in ['.json','.py','.log','.patch','.before'] and '__pycache__' not in p.parts and p.name!='source-inheritance-plan.json':add(p)
for directory in ['target/checked-facade-focused-current','target/n6-component-coefficient-intern-v1']:
 for p in (ROOT/directory).rglob('*'):
  if p.is_file() and p.suffix in ['.json','.py','.log','.patch'] and '__pycache__' not in p.parts:add(p)
proof=ROOT/'target/zero-gram-triangle-affine-proposal'
for rel in ['README.md','research/REUSE.md','independent/source-review.json','integration-v2/README.md','integration-v2/manifest.json','integration-v2/core-integration.patch','integration-v3/README.md','integration-v3/JET-REUSE.txt','integration-v3/manifest.json','integration-v3/review-amendments.patch','integration-v3/source-peer-review.json']:add(proof/rel)
# Reuse selected existing oracle payload leaves, without broad parent source restoration.
op='validation/collinear-rank6-parameter-oracle';om=j(ROOT/op/'manifest.json');oa=op+'/payload.tar.gz';parent_archives.add(oa)
for alias in ['target/collinear-rank6-parameter-oracle-refinement-v3/capture-001/grids/n3-order48-identity/result.json','target/collinear-rank6-parameter-oracle-refinement-v3/capture-001/comparison.json','target/collinear-rank6-parameter-oracle-refinement-v3/independent/receipt.json','target/collinear-rank6-parameter-oracle-refinement-v3/anchor-admission.json']:
 r=om['payload_members'][alias];files[alias]={**r,'archive':oa,'member':alias}
# Deterministic payload, regular files only.
with (HERE/'payload.tar.gz').open('wb') as f:
 with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0,compresslevel=9) as gz:
  with tarfile.open(fileobj=gz,mode='w',format=tarfile.PAX_FORMAT) as t:
   for name,body in sorted(payload.items()):
    m=tarfile.TarInfo(name);m.size=len(body);m.mode=0o600;m.mtime=0;t.addfile(m,io.BytesIO(body))
parents=['validation/python-interface/checkpoint-wheel-004/manifest.json','validation/python-interface/facade-wheel-002/manifest.json',op+'/manifest.json']
q={'status':'scoped_collinear_current_core_tests_pass_with_two_expensive_stress_timeouts_preserved','compiled_source_bodies':349,'inherited_source_bodies':305,'own_source_delta':44,'affine_core_passed':16,'affine_core_fixed90_timeouts':2,'component_tests_passed':10,'checked_facade_tests_passed':4,'plain_numeric_test_passed':True,'plain_reference_coefficients':1680,'plain_precision_pairs':840,'plain_invalid_lane_isolated_and_duplicates_equal':True,'selected_dilation_dual_numeric_test_passed':True,'dual_reference_primal_and_jet_coefficients':3360,'dual_precision_pairs':1680,'reference_tolerance':'1e-10, dimensionally normalized','precision_tolerance':'2^-80','native_arrays_exported':False,'independently_recomputed_native_arrays':False,'numeric_evidence_kind':'actual source-bound Rust test assertions against independently admitted empirical quadrature anchor; exact test logs archived','independent_oracle_anchor_manifest':op+'/manifest.json','original_failed_builds_preserved':[1,2,3],'general_N_or_arbitrary_N_qualified':False,'general_or_public_highpoint_Dual_qualified':False,'derivative_uncertainty_qualified':False,'performance_qualified':False,'license_literal_included':False,'compiled_binary_included':False,'fresh_PID_or_binary_attestation_reenacted_by_portable_checker':False}
(HERE/'qualification.json').write_text(json.dumps(q,indent=2)+'\n')
manifest={'schema_version':1,'status':q['status'],'capsule_directory':str(HERE.relative_to(ROOT)),'archives':{p:sha((ROOT/p).read_bytes()) for p in sorted(parent_archives|{archive_rel})},'parent_manifests':{p:sha((ROOT/p).read_bytes()) for p in parents},'compiled_source_aliases':sorted(sources),'files':dict(sorted(files.items())),'original_source_archive_sha256':sha((base/'build-004/actual-main-source-context.tar.gz').read_bytes()),'omitted_binary':j(base/'build-004/receipt.json')['frozen_binary'],'oracle_alias':'target/collinear-rank6-parameter-oracle-refinement-v3/capture-001/grids/n3-order48-identity/result.json','qualification':q,'capsule_files':{p.name:info(p.read_bytes()) for p in HERE.iterdir() if p.is_file() and p.name!='manifest.json'}}
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'manifest_sha256':sha((HERE/'manifest.json').read_bytes()),'payload_bytes':(HERE/'payload.tar.gz').stat().st_size,'aliases':len(files),'own_payload_members':len(payload),'compiled_sources':len(sources)},indent=2))
