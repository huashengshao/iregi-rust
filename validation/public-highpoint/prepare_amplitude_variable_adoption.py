"""Prepare a minimal review patch; never write the production source."""
from pathlib import Path
import difflib
import hashlib
import json
import subprocess


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def function(source,name):
    start=source.index('fn '+name+'(\n')
    opening=source.index('{',start);depth=1;end=opening+1
    # This collector contains no braces in literals or comments.
    while depth:
        if source[end]=='{':depth+=1
        elif source[end]=='}':depth-=1
        end+=1
    return start,end,source[start:end]


def main():
    root=Path.cwd();here=root/'validation/public-highpoint'
    source_path=root/'crates/iregi-rust/src/stability.rs'
    checks_path=here/'amplitude-vars-checks.json';build_path=here/'amplitude-vars-build-final.json'
    checks,build=[json.loads(p.read_text()) for p in [checks_path,build_path]]
    assert checks['status']==build['status']=='passed'
    assert checks['build_manifest_sha256']==sha(build_path)
    assert [r['checked_cases'] for r in checks['runs']]==[82,38,35]
    frozen=root/build['frozen_source_root']/'crates/iregi-rust/src/stability.rs'
    assert sha(frozen)==build['source_hashes']['crates/iregi-rust/src/stability.rs']
    before=source_path.read_text();before_hash=sha(source_path)
    current_start,current_end,current=function(before,'collect_amplitude_variables')
    _,_,legacy=function(frozen.read_text(),'collect_amplitude_variables_legacy')
    _,_,candidate=function(frozen.read_text(),'collect_amplitude_variables_candidate')
    legacy=legacy.replace('collect_amplitude_variables_legacy','collect_amplitude_variables')
    candidate=candidate.replace('collect_amplitude_variables_candidate','collect_amplitude_variables')
    assert current==legacy,'Production collector changed; review before rebasing'
    after=before[:current_start]+candidate+before[current_end:]
    target=root/'target/public-highpoint/amplitude-vars-adoption';target.mkdir()
    (target/'before-stability.rs').write_text(before);(target/'stability.rs').write_text(after)
    patch=here/'amplitude-vars-adoption.patch';assert not patch.exists()
    patch.write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
                     fromfile='a/crates/iregi-rust/src/stability.rs',tofile='b/crates/iregi-rust/src/stability.rs')))
    assert sha(source_path)==before_hash
    record=dict(status='prepared_not_applied',target_revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                production_source_sha256=before_hash,prepared_source_sha256=sha(target/'stability.rs'),patch_sha256=sha(patch),
                build_manifest_sha256=sha(build_path),checks_manifest_sha256=sha(checks_path),
                frozen_stability_sha256=sha(frozen),script_sha256=sha(Path(__file__)),
                scope='Only the independently exact-qualified amplitude-variable collector fastpath; no modes, legacy duplicate, counters, phase hooks, threshold changes or production edits. FullN6 runtime remains separate. No controlled performance or full high-point numerical claim.')
    destination=here/'amplitude-vars-adoption.json';assert not destination.exists();destination.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))


if __name__=='__main__':main()
