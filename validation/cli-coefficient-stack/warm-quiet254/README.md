# Quiet paired CLI coefficient timing (private candidate)

All eight physical graph/batch families and all 168 paired blocks passed exact represented-value, precision and signed-zero checks. The candidate remains private. **Do not adopt it across all cases based on these results:** ggHH batch 32 was slower in20 of 21pairs, with a wholly-above-one 99% interval. That possible regression remains visible even though its interval is wider than the 2% qualification limit.

The frozen binary ran on CPU 254 in the coordinator's project-quiet window, exiting 0 after 20.0835 seconds. The coordinator identified unrelated host work on CPU 0; the snapshot is retained in `coordinator-window.json`. This is an opt2 caller linked against the coherent 6b24 optimized dependency closure, not the whole-workspace opt3 IREGI or end-to-end benchmark. The existing 6b24 benchmark gates exclude this private candidate.

| Graph | Batch | Baseline median µs/batch | Candidate median µs/batch | Paired median ratio | 99% interval | Diagnostic classification |
|---|---:|---:|---:|---:|---|---|
| ggh | 1 | 1.221 | 1.181 | 0.968043 | [0.964164, 0.971175] | improvement |
| ggh | 32 | 45.345 | 45.030 | 0.996474 | [0.975599, 1.021092] | inconclusive-noise |
| gghh | 1 | 20.237 | 19.736 | 0.977467 | [0.973291, 0.979127] | improvement |
| gghh | 32 | 749.698 | 779.879 | 1.036676 | [1.023664, 1.050137] | inconclusive-noise |
| gghhh | 1 | 92.432 | 90.023 | 0.974097 | [0.967964, 0.979164] | improvement |
| gghhh | 32 | 3309.746 | 3295.853 | 0.995965 | [0.993408, 1.000035] | parity |
| gggg-up | 1 | 493.625 | 475.564 | 0.963491 | [0.958654, 0.967362] | improvement |
| gggg-up | 32 | 16579.099 | 15921.481 | 0.962866 | [0.957716, 0.972370] | improvement |

Ratios are candidate/baseline, computed pairwise before taking the median. The existing benchmark helper supplies 10,000 bootstrap resamples. A classification requires relative interval width at most 2%; wider intervals are labeled inconclusive. This label must not conceal ggHH batch 32's evidence of a slowdown: its median is about3.7% slower and interval spans about2.4–5.0% slower. No aggregate score excludes or hides that family.

The protocol uses 21 balanced seeded-random pairs, shared fixed iteration counts calibrated from 2 ms pilots to a 30 ms mean per-variant block, and 64 warmup calls per variant. Every call black-boxes inputs and the returned batch. Each block includes N public output allocations and N−1 predecessor drops; its final output survives for exact checking and is dropped outside the interval. Graph preparation, exact lowering, workspace mapping, packing, proof checks and JSON output are outside timed intervals and recorded separately. Their single observations support no amortization claim. Each graph/batch-size uses fresh numerical workspaces, with retained storage within its warmup and measured blocks; there is no numerical memoization.

`audit.json` independently validates all raw elapsed pairs are positive finite integers, every 21-entry ordering is balanced 11/10 and exactly reproduces its seed, all block indices and shared counts agree, and final outputs equal the initial expected arrays. `raw-index.json` hashes every uncompressed raw file in `raw.tar.gz`. Source, assets and binary hashes are checked before/after in `results.json`; `compile.json` binds the coherent closure, exact command and compiler. `run.py` is the unchanged frozen runner used in this window; the stronger raw checks were applied afterward without rewriting it.

## Read-only regression investigation

For ggHH batch 32, candidate/baseline median ratios were 1.04215 when baseline ran first and 1.03425 when candidate ran first. Chronological thirds were 1.04215, 1.04412 and 1.03183. Simple order imbalance or monotone drift therefore does not explain the observed slowdown. The 8-call pilots predicted 0.99493, while the measured 40-call blocks showed the slowdown.

The exact graph retains 2,617 multiplications, 57 additions and 12 assignments, with no branches or shared evaluators. Root batch storage falls from 1,389,568 to 276,480 bytes, including 28 inputs and 12 constants. CPU 254 reports 32 KiB L1 data, 1 MiB L2 and 16 MiB shared L3. Symbolica's batch evaluator uses its scalar path for a singleton and a separate indexed instruction-major loop for larger batches. Stack allocation changes addresses and storage lifetimes; it does not change those operations or operand order. A cache/address-layout effect is a hypothesis, not an identified cause, and reduced storage alone does not establish a speedup.

No further runs are scheduled for this candidate. A future confirmation could retain this result and use independent fresh-process repetitions of the same frozen binary, examining ggHH batch 32 alongside ggHH batch 1 and the improving/parity controls. A separate 41×100 ms protocol would need its own source/binary provenance. No graph-name allocation policy is proposed.

To reproduce only after a coordinated quiet grant, source the project environment and local license environment, then use a fresh directory name:

```sh
python3 target/cli-coefficient-timing/run.py new-quiet-run 254
```

The runner retains all eight planned rows, including failure or not-run statuses. The candidate binary SHA-256 is `74e250011b4c2fe5d9dfb765def25cdc100e5bb421e81b37416b929fced1cd4d`.
