"""Archive clean standalone qualification, retaining incomplete mixed outcomes."""
from pathlib import Path
import hashlib,json,shutil

root=Path.cwd();raw=root/'target/planar-adoption';dest=root/'validation/planar-adoption'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
load=lambda p:json.loads(p.read_text())
build=load(raw/'build.json');small=load(raw/'runs/small-suite.json');mixed=load(raw/'runs/rank7-mixed.json')
assert build['exit_code']==0 and build['all_closure_hashes_rechecked']
assert small['status']=='passed' and small['expected_passed_tests']==9
assert mixed['status']!='running'
for path,digest in build['source_hashes'].items():assert sha(raw/'source-snapshot'/path)==digest
for report in (small,mixed):
 assert report['binary_sha256']==build['binary_sha256']
 assert report['build_manifest_sha256']==sha(raw/'build.json')
 assert report['source_hashes_unchanged'] and report['binary_unchanged']
artifact=load(raw/'mixed-rank7.json')
assert mixed['output_artifact_sha256']==sha(raw/'mixed-rank7.json')
assert not dest.exists()
dest.mkdir()
for name in ('base.json','candidate.json','build.json','build.log','build_complete.py','run.py','archive.py',
             'standalone-api.patch','symbolica-nway.patch','mixed-rank7.json',
             'retained-historical-success-expectation.rs','automatic-followup.md'):
 shutil.copy2(raw/name,dest/name)
shutil.copytree(raw/'source-snapshot',dest/'source');shutil.copytree(raw/'runs',dest/'runs')
closure=Path(build['dependency_closure']);(dest/'dependencies').mkdir()
for name in ('manifest.json','workspace-completion.json','completed-workspace-build.json','cargo-library-events.json'):
 shutil.copy2(closure/name,dest/'dependencies'/name)
assert sha(dest/'dependencies/manifest.json')==build['closure_manifest_sha256']
assert sha(dest/'dependencies/workspace-completion.json')==build['workspace_completion_sha256']
parent=root/'validation/planar-integrated/qualification.json'
record={
 'schema_version':1,'kind':'clean-standalone-certified-planar-adoption-candidate',
 'status':'recorded-qualification-passed' if mixed['status']=='passed' and artifact['status']=='passed' else 'mixed-rank7-qualification-incomplete',
 'production_promoted':False,'automatic_workspace_fallback':False,
 'base_revision':'6b24c0372022e22606a1ac85f30c7fa579fb41f0',
 'binary_sha256':build['binary_sha256'],'build_manifest_sha256':sha(raw/'build.json'),
 'build_seconds':build['elapsed_seconds'],'closure_files_rehashed':build['closure_files'],
 'source':'source/','standalone_patch':'standalone-api.patch','standalone_patch_sha256':sha(raw/'standalone-api.patch'),
 'independent_symbolica_accumulator_patch':'symbolica-nway.patch',
 'independent_symbolica_accumulator_patch_sha256':sha(raw/'symbolica-nway.patch'),
 'ordinary_rank7_parent':{'path':str(parent.relative_to(root)),'sha256':sha(parent),
    'scope':'Float128 and Float256/request53, all330×4 complex slots against five boxes and full exact-artifact128→256 normalized2^-65 convergence',
    'source_difference':'candidate removes optional phase diagnostics/unused fallback helper, turns historical f64 expectation mismatch into explicit Unstable regression, and strengthens artifact metadata assertions; production numerical formulas/guards unchanged apart from retained separately labeled four-line n-way accumulator'},
 'small_suite':{'status':small['status'],'passed':9,'ignored':small['ignored_tests'],
    'selected':small['selected_tests'],'elapsed_seconds':small['elapsed_seconds'],
    'report':'runs/small-suite.json','log':'runs/small-suite.log'},
 'mixed_rank7':{'status':mixed['status'],'artifact_status':artifact['status'],
    'report':'runs/rank7-mixed.json','log':'runs/rank7-mixed.log','artifact':'mixed-rank7.json',
    'artifact_sha256':sha(raw/'mixed-rank7.json'),'elapsed_seconds':mixed['elapsed_seconds'],
    'timeout_seconds':mixed['timeout_seconds'],'working_precision':128,'requested_precision':53,
    'shape':artifact['shape'],'components':4,'moments':330,'complex_slots_per_successful_lane':5280,
    'rows':3,'primary_statuses':artifact.get('primary_statuses'),
    'returned_metadata':artifact.get('returned_metadata'),
    'independent_box_statuses':artifact.get('independent_box_statuses'),
    'max_normalized_error':artifact.get('independent_max_normalized_error'),
    'comparison_tolerance':'1/10000000000','execution':artifact.get('execution')},
 'interface':{'propagators':5,'rank_maximum':7,'powers':[1,1,1,1,1],
    'dimension_shift':0,'algorithm':'PassarinoVeltman','invariants':'FromShifts','input_policy':'Preserve',
    'certificate':'Every requested Taylor component of the exact represented coordinate determinant vanishes; selected constant-one chart primal is certified nonzero.'},
 'source_review':{'owners':['batch_execution','ROOT'],'outcome':'No correctness blocker found',
    'scope':['ordinary validator exact check order','chart grouping and shape preservation','checked counters and profile/error accounting','private chart solver refactor and certificate determinant domain','mixed C=6+2st/inverse1/6-st/18 identity','actual returned metadata and exact output capture','transverse mixed component3 and inaccessible failed lane'],
    'runner_scope':'Exact named test membership, exit status, artifact passed status, source/binary hashes and ordinary previous-artifact joins.'},
 'limitations':[
    'No production promotion and no automatic ordinary Workspace fallback in this artifact.',
    'The historical binary64 spatial family remains Unstable with unchanged conditioning guards; this is visible in the new expected-rejection test and original retained failures.',
    'Rank-seven ordinary128/256 results belong to the preceding source/binary; the clean candidate requalifies small cases and the recorded mixed probe only.',
    'Rectangular four-component rank-seven coverage does not establish six-component or arbitrary higher mixed rank-seven coverage.',
    'No performance-parity claim; build/runtime durations include preparation and differ in profile/bounds from historical runs.',
    'Lower-rank external spans and homogeneous-only families without a regular constant-one chart remain unsupported.',
    'Exact rational artifact encoding does not retain signed-zero bits.'
 ],
 'historical_evidence':['validation/planar-certified/qualification.json','validation/planar-certified-nway/qualification.json'],
 'evidence_manifest':'files.json'
}
(dest/'qualification.json').write_text(json.dumps(record,indent=2)+'\n')
(dest/'README.md').write_text('''# Clean certified planar standalone candidate

This bundle retains the standalone public API patch against6b24, its separately
labeled four-line Symbolica accumulation patch, a complete source snapshot and
the coherent completed-workspace dependency closure records. All retained closure
files were hashed before and after compilation; source/binary hashes were checked
at every runtime boundary. Large binaries and archives remain hash-bound in target.

The focused suite passes all9 nonignored planar tests. Three bounded rank-seven
tests are explicitly ignored there and are not silently included in its count.
The exact historical binary64 spatial fixture remains Unstable. Its new regression
asserts that rejection and the attempted-chart diagnostics; the old failed Success
expectation and original failure logs remain visible. Positive tetrahedral,
higher-precision and rank-two mixed cases are separate tests.

The bounded rectangular rank-seven probe outcome is recorded without filtering in
qualification.json. Its artifact preserves partial progress on failure or timeout;
only status passed with a successful bound runner establishes numerical agreement.
For each accepted lane it stores all330×4×4 complex values, exact real/imaginary
rationals, component precision and actual output metadata. The independent box
result uses the analytically known constant-one identity with C(s,t)=6+2st.

The preceding validation/planar-integrated bundle establishes ordinary rank-seven
Float128/256 convergence. Its source/binary distinction is explicit. No automatic
Workspace fallback or production promotion is claimed here. The follow-up dispatch
design is retained as source planning only. Timings here are qualification bounds
and progress evidence, not a matched performance benchmark.

Reproduction commands are in source/docs/research/certified-planar-api.md and the
actual frozen build/run scripts. files.json binds every retained file.
''')
files={str(p.relative_to(dest)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'files.json').write_text(json.dumps(files,indent=2)+'\n')
assert all(sha(dest/path)==entry['sha256'] for path,entry in files.items())
print(json.dumps({'qualification':str((dest/'qualification.json').relative_to(root)),
 'qualification_sha256':sha(dest/'qualification.json'),'files':len(files),
 'files_sha256':sha(dest/'files.json'),'bytes':sum(entry['bytes'] for entry in files.values())},indent=2))
