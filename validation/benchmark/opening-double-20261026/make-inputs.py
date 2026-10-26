#!/usr/bin/env python3
"""Derive the same 18 input tensors with binary64-only public candidate choices."""
import copy
import hashlib
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'validation/benchmark/opening-rank6-20261026/inputs.json'
suite = json.loads(OLD.read_text())
suite['schema_version'] = 2
suite['suite_id'] = 'opening-double-20261026'
suite['purpose'] = 'Optimistic binary64 timings, with measured accuracy shown independently'
suite['prior_input_suite'] = str(OLD.relative_to(ROOT))
suite['prior_input_suite_sha256'] = hashlib.sha256(OLD.read_bytes()).hexdigest()
suite['timing_contract'].update({
    'api': 'Public TensorReductionPlan / TensorWorkspace, explicitly selected algorithm and master policy; all arithmetic f64',
    'selection': 'Fastest arithmetic mean among the fixed candidate list producing complete finite tensors with measured array-relative error <=1e-3; if none, retain fastest observed timing with a warning and explicit failure/accuracy status',
    'precision': 'All rows ordinary Rust f64: 53 significant bits. Ordinary N5R5/N5R6/N6R6 requested bits39 (internal 2^(19-bits) target approximately1e-6); remaining rows bits53. No higher-precision fallback or promotion.',
    'blocks': 'N<=4: three warmup calls, 11 fixed blocks, loop count calibrated once from final warmup for target30ms capped10000 calls. N>=5: one warmup then five one-call blocks fixed in advance.',
    'accuracy': 'Array-relative discrepancy E/A: E=max_j |computed_j-reference_j|/mu^(degree_j+4+2h-2sum(powers)), A=max_j |reference_j|/the same weight. All cumulative tensor moments and four Laurent slots. Also retain historical componentwise mixed normalized error.',
    'failure_policy': 'Successful finite full arrays, internal refusal/Unstable statuses, nonfinite and missing results remain distinct. Refused guarded lanes are null, never unchecked or fabricated zero arrays.',
})
for case in suite['cases']:
    req = case['driver_request']
    req.update(numeric_type='f64', working_bits=53,
               requested_bits=39 if case['id'] in ('ordinary-n5-r5','ordinary-n5-r6','ordinary-n6-r6') else 53,
               target_block_ns=30_000_000 if req['n'] <=4 else None)
    candidates=[]
    for policy, suffix in [('NativeF64Abc','native-abc'),('Symbolica','symbolica')]:
        cand=copy.deepcopy(req)
        cand.update(id=case['id']+'--'+suffix, master_policy=policy, postconstruction_profiling=False)
        candidates.append({'id':suffix,'request':cand})
    if case['id']=='ordinary-n6-r6':
        for algorithm, suffix in [('Hybrid','hybrid'),('PassarinoVeltman','pv')]:
            cand=copy.deepcopy(req)
            cand.update(id=case['id']+'--thin-'+suffix,algorithm=algorithm,
                        master_policy='Symbolica',postconstruction_profiling=True)
            candidates.append({'id':'thin-'+suffix,'request':cand})
    case['candidates']=candidates
suite['candidate_policy']='Fixed before running: each row explicit NativeF64Abc and Symbolica master policies under its original algorithm; ordinary N6R6 additionally existing Symbolica thin Hybrid/PV with profiling enabled after construction. NativeF64Abc only selects supported A/B/C masters and retains existing Rust/Symbolica fallback for unsupported scalar families. All candidate attempts retained.'
(HERE/'inputs.json').write_text(json.dumps(suite,indent=2)+'\n')
print(json.dumps({'cases':len(suite['cases']),'candidates':sum(len(c['candidates']) for c in suite['cases'])}))
