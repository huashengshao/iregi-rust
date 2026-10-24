"""Source/artifact freeze only; never launches the unit binary, examples or numerics."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
ROOT=Path.cwd();HERE=ROOT/'target/public-six-point-cargo/runtime';BUILD=HERE.parent
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
key=lambda p:str(Path(p).resolve().relative_to(ROOT))
freeze=json.loads((BUILD/'source-freeze.json').read_text());inputs={path:r['sha256'] for path,r in freeze['files'].items()}
for path,digest in inputs.items():assert sha(ROOT/path)==digest,path
for label in ['lib-no-run','example-build']:
    record=json.loads((BUILD/(label+'.json')).read_text());assert record['pass'] and record['terminal_before_hash'] and not record['remaining_owned_processes']
    for suffix in ['.json','-start.json','-terminal.json','-artifacts.json','-stdout.jsonl','-stderr.log']:inputs[key(BUILD/(label+suffix))]=sha(BUILD/(label+suffix))
    data=json.loads((BUILD/(label+'-artifacts.json')).read_text())
    for row in data['artifacts']:
        for path in row['filenames']:
            p=Path(path)
            if p.is_file():inputs[key(p)]=sha(p)
for name in ['source-freeze.json','preparation.json','grant.json','build-owned.py']:inputs[key(BUILD/name)]=sha(BUILD/name)
prep=json.loads((BUILD/'preparation.json').read_text())
for row in prep['tools'].values():inputs[row['path']]=row['sha256']
for name in ['lifecycle.py','compare.py','harness_common.py','run.py','selection.json','prepare.py']:inputs[key(HERE/name)]=sha(HERE/name)
canonical=ROOT/'validation/highpoint-six-point-api/qualified-v2'
for path in [canonical/'protocol.json',canonical/'integration.patch',canonical/'harness_common.py',canonical/'compare.py',canonical/'lifecycle.py',ROOT/'target/six-point-live-application.json',ROOT/'target/root-six-point-capsule-audit.json',ROOT/'validation/public-highpoint/fixture-conditioned_masses.json',ROOT/'validation/public-highpoint/reference-conditioned_masses.json',ROOT/'validation/public-highpoint/compare_public.py']:
    inputs[key(path)]=sha(path)
assert sha(HERE/'lifecycle.py')=='c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824'
assert sha(HERE/'compare.py')=='5e786bc33b23e96cf71e4c16250e5eed08427f93dc887b35fa85e3facf7cdad3'
folder=HERE/'bin';folder.mkdir()
artifacts={}
for label,name,owner in [('lib-no-run','current-tests','iregi_rust'),('example-build','current-six_point','six_point')]:
    record=json.loads((BUILD/(label+'.json')).read_text());row=next(r for r in record['selected_current_artifact_identities'][owner] if r['executable']);src=Path(row['executable']);expected=row['files'][str(src)]['sha256'];assert sha(src)==expected
    dst=folder/name;shutil.copyfile(src,dst);dst.chmod(0o500);assert sha(dst)==expected;inputs[key(dst)]=expected
    artifacts[name]={'emitted_path':key(src),'frozen_exact_copy':key(dst),'sha256':expected,'bytes':dst.stat().st_size,'actual_current_cargo_profile':row['profile']}
selection=json.loads((HERE/'selection.json').read_text())
protocol={'schema_version':1,'status':'frozen_pending_root_runtime_grant','context':'actual_current_locked_cargo_not_private_extern_build','source_freeze_sha256':sha(BUILD/'source-freeze.json'),'current_cargo_artifacts':artifacts,'selection':selection,'owned_group_helper_sha256':sha(HERE/'lifecycle.py'),'comparator_sha256':sha(HERE/'compare.py'),'bounds_seconds':{'list':40,'exact':240,'128':120,'256':120},'postwork_reserve_seconds':20,'runtime_cpu':14,'runtime_environment':{'RAYON_NUM_THREADS':'1','RUST_TEST_THREADS':'1','IREGI_PREPARATION_PROFILE':'1','IREGI_PV_PREPARATION_PROFILE':'1'},'inputs':inputs,'reference_gates':{'native_slots_per_precision':140,'original_mixed_tolerance':'1e-10','convergence_tolerance':'2^-80','normalization':'unchanged canonical compare_public.py and qualifiedV2 compare.py','complete_inputs_outputs_precision_order_status_work_metadata':True},'prior_private_lifecycle_context':'Preserved qualifiedV2 evidence; no current-Cargo lifecycle/ordinary paired rebuild or performance claim.','dependency_policy':'list membership before exact34; exact gate before128; original128 gate before256; stop every dependent stage on any failure; no retry/extension/threshold change','production_application_note':'52 private candidate files matched application receipt; current module doc-only delta ea256a4e→8e4341a8 is bound by current382-source freeze; private canonical capsule remains production_build_qualified=false.'}
(HERE/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
print(json.dumps({'protocol':key(HERE/'protocol.json'),'protocol_sha256':sha(HERE/'protocol.json'),'input_count':len(inputs),'actual_current_cargo_artifacts':artifacts,'runtime_executed':False},indent=2))
