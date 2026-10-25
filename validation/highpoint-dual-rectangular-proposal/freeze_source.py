"""Freeze the isolated rectangular source proposal. Never builds or evaluates."""
from pathlib import Path
import datetime
import difflib
import hashlib
import json
import shutil

ROOT=Path.cwd().resolve()
HERE=ROOT/'target/highpoint-dual-sensitivity/rectangular-v1'
BASE=HERE.parent/'numerical-v1/source-v2'
PROPOSED=HERE/'proposed'
FROZEN=HERE/'source-v1'
BASE_SHA='dfd61c594979b41057d3ef745eab60cf96ffb5b86fbd1c8aa97828da673ca045'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory(folder):
    return {str(p.relative_to(folder)):{'sha256':sha(p),'bytes':p.stat().st_size}
            for p in sorted(folder.rglob('*')) if p.is_file()}


def main():
    assert ROOT==Path('/shared/external/iregi/iregi-rust'),'commands must run in project'
    assert sha(HERE.parent/'numerical-v1/source-v2.json')==BASE_SHA,'parent freeze changed'
    base_manifest=json.loads((HERE.parent/'numerical-v1/source-v2.json').read_text())
    assert {n:v['sha256'] for n,v in inventory(BASE).items()}=={n:v['sha256'] for n,v in base_manifest['files'].items()}
    helper=HERE/'rectangular_inputs.rs'
    destination=PROPOSED/'core/crates/iregi-rust/src/rectangular_inputs.rs'
    assert helper.exists() and (HERE/'helper-source-review.json').exists(),'helper review required'
    review=json.loads((HERE/'helper-source-review.json').read_text())
    assert review['status']=='passed-independent-source-review-only' and review['blocking_findings']==[], 'helper review not clear'
    assert review['inputs']['rectangular_inputs.rs']['sha256']==sha(helper),'helper review differs'
    assert not FROZEN.exists() and not (HERE/'source-v1.json').exists(),'immutable freeze exists'
    shutil.copyfile(helper,destination)
    shutil.copytree(PROPOSED,FROZEN)
    files=inventory(FROZEN)
    original=inventory(BASE)
    changed=[n for n in files if n not in original or files[n]['sha256']!=original[n]['sha256']]
    assert changed==['core/crates/iregi-rust/src/highpoint_component_probe.rs','core/crates/iregi-rust/src/rectangular_inputs.rs'],'unexpected source delta'
    assert len(files)==93,'complete source inventory differs'
    patch=[]
    for name in changed:
        previous=(BASE/name).read_text().splitlines(keepends=True) if (BASE/name).exists() else []
        new=(FROZEN/name).read_text().splitlines(keepends=True)
        patch.extend(difflib.unified_diff(previous,new,fromfile='a/'+name if previous else '/dev/null',tofile='b/'+name))
    patch_path=HERE/'rectangular-capture-v1.patch'
    with patch_path.open('x') as stream:stream.writelines(patch)
    manifest={'schema_version':1,'status':'source_only_rectangular_capture_proposal_not_compiled_or_evaluated',
      'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'base_numerical_source_manifest':{'path':str((HERE.parent/'numerical-v1/source-v2.json').relative_to(ROOT)),'sha256':BASE_SHA},
      'parent_completed_cohort':{'path':str((HERE.parent/'numerical-v1/qualification-summary.json').relative_to(ROOT)),'sha256':sha(HERE.parent/'numerical-v1/qualification-summary.json')},
      'frozen_source':str(FROZEN.relative_to(ROOT)),'files':files,'changed_or_added_files':changed,
      'patch':{'path':str(patch_path.relative_to(ROOT)),'sha256':sha(patch_path)},
      'helper_review':{'path':str((HERE/'helper-source-review.json').relative_to(ROOT)),'sha256':sha(HERE/'helper-source-review.json')},
      'shape':[[0,0],[1,0],[0,1],[1,1]],'directions':['additive first squared mass, seed1','independent common dilation1+b, seed1'],
      'target_identity':'F(a,b)=(1+b)^-8 I6(m0_squared+a/(1+b)^2); rectangular first-order response=(1+b)^-8*unit+a*(1+b)^-10*dot0',
      'expected_component_columns':['unit','dot0'],'expected_matrix_source':'ordinary Symbolica derivatives of abstract unit/dot response, not literal production matrix',
      'schedule':[['singleton_rectangular',[0]],['mixed_rectangular_invalid',[0,1,0]],['reordered_rectangular',[0,0,1]],['empty',[]],['singleton_again',[0]]],
      'expected_successful_lanes':6,'expected_invalid_rejections':2,'helper_tests_written_not_executed':6,
      'compilation':False,'tests_executed':False,'numeric_execution_authorized':False,'public_promotion':False,'performance_claim':False,
      'limitations':['Independent one mass-direction/dilation cross, no pure second mass derivative or arbitrary mixed directions.','No finite differences, current-Cargo qualification, or rigorous uncertainty enclosure.','Same private full-component guard/transport implementation; E6 backend error transport remains unsupported.','Root must freeze and review a separate finite execution recipe before any compiler/evaluator/integral execution.']}
    with (HERE/'source-v1.json').open('x') as stream:json.dump(manifest,stream,indent=2);stream.write('\n')
    print({'source_manifest_sha256':sha(HERE/'source-v1.json'),'files':len(files),'changed':changed,'patch_sha256':sha(patch_path)})


if __name__=='__main__':
    main()
