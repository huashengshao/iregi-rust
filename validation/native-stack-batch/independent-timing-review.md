# Independent arithmetic review

A separate agent (`/root/batch_execution`) reproduced each raw paired median, 99% bootstrap interval and gate using the frozen benchmark helper. All before/after qualification CSVs are byte-identical. No finding was reported.

The dense candidate has 12 groups: two improvements, six parity results and four regressions. The allocator D0 candidate has six groups: three singleton improvements, two batch32 regressions and one noisy batch32 result. This review checks arithmetic and evidence consistency; it does not establish an independent numerical oracle or support adoption. Both candidates remain rejected.

Reviewed summaries:

- `validation/native-dense-span/timing-fixed-summary.json`: SHA-256 `85d329fe6137dbcea11f236815c8f06ba8730b562586c28bfd023fea95d84456`.
- `validation/native-stack-batch/d0-timing-fixed-summary.json`: SHA-256 `77e2d6118f7d7dcc088fb27ae0704041be3968ac949a3f7ec7d2310793098548`.
