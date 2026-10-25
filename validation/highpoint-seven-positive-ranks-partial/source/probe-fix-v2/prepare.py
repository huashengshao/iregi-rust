"""Small source-only delta seal; no compiler, evaluator or artifact hashing."""
import ast
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = Path('/shared/external/iregi/iregi-rust')
BASE = HERE.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert Path.cwd().resolve() == ROOT and len(sys.argv) == 1
    assert not (HERE / 'protocol.json').exists()
    correction = json.loads((HERE / 'correction.json').read_text())
    lineage = json.loads((HERE / 'partial-build-lineage.json').read_text())
    assert digest(HERE / 'correction.json') == '6e3f18985f39ff945793e92825ceb524bec564bb07515d90fb22f14395a393a5'
    assert digest(HERE / 'partial-build-lineage.json') == '8181a677fba40e9e988f66e8199f51b80731560073f287bf6cadfeb037f3d0d9'
    probe = ROOT / correction['old_probe_source_path']
    snapshot = ROOT / correction['failed_probe_snapshot']['path']
    old, current = snapshot.read_bytes(), probe.read_bytes()
    removed = b'        || result.values.len() != plan.basis().len() * 4 * rows\n'
    assert old.count(removed) == 1 and old.replace(removed, b'', 1) == current
    assert digest(snapshot) == correction['old_probe_sha256'] == lineage['old_probe_sha256']
    assert digest(probe) == correction['new_probe_sha256'] == '9cc1860aaac2649db4eae850c7ecca4ea25e7013da4db168aa824dd0f2dbc9a1'
    inputs = {}
    paths = [HERE / name for name in ['continuation.py', 'run.py', 'prepare.py', 'README.md',
             'partial-build-lineage.json', 'correction.json', 'failed-probe-source.rs', 'probe-only.patch']]
    review = ROOT / 'target/resume-20261025-review/positive-n7-probe-fix-lineage-independent-review.json'
    assert digest(review) == 'bc97b82ede32fcb0a6806897e05b11c1e44918aab441b6d1b5323005eaa063a5'
    quad = ROOT / 'target/quad-iregi-source-audit/future-positive-rank-requests'
    audit = quad / 'independent-saved-review.json'
    assert digest(audit) == 'f0b8f0774d901957fac3369165212b0efac3bf6921cea3c940269f191af373fd'
    paths.extend([review, audit])
    for path in paths:
        if path.suffix == '.py':
            ast.parse(path.read_text(), filename=str(path))
        inputs[str(path.relative_to(ROOT))] = digest(path)
    protocol = dict(schema_version=1,
        status='probe_only_warm_continuation_frozen_awaiting_root_grants',
        context='private_N7_rank1_probe_only_fix_v2_warm_actual_Cargo',
        base_protocol_sha256=digest(BASE / 'protocol.json'),
        lineage_sha256=digest(HERE / 'partial-build-lineage.json'),
        correction_sha256=digest(HERE / 'correction.json'),
        old_probe_sha256=correction['old_probe_sha256'], new_probe_sha256=correction['new_probe_sha256'],
        changed_source_paths=[correction['old_probe_source_path']], inputs=inputs,
        core_masters_admission='Same preserved partial-build event and filename bytes; fresh flag may become true. Probe must remain freshly compiled false.',
        original_failed_receipt_rewritten=False, original_metadata_or_protocol_rewritten=False,
        new_cache_or_source_closure=False, numerical_qualified=False, performance_qualified=False)
    with (HERE / 'protocol.json').open('x') as output:
        output.write(json.dumps(protocol, indent=2) + '\n')
    print({'status': protocol['status'], 'protocol_sha256': digest(HERE / 'protocol.json')})


if __name__ == '__main__':
    main()
