# Combined native policy / SixPoint: 27 focused tests

This is a separately proposed runtime protocol; no test binary has run while preparing it. Code generation passed and is independently audited, with the unchanged private compiled source. ROOT still owns numerical scheduling and must grant each cohort before launch. The Python owner currently holds the numerical lease. There are no builds, Cargo commands or live mutations in this protocol.

`runtime-inventory.json` enumerates exactly 27 configuration/name pairs and their source files: five prior core master-policy cases, ten prior sidecar-policy cases, five new execution-composition cases, and seven new planar/ThinSix constructor cases. Default runs 12 cases overall; selective runs 15. The complete static inventory is independently reviewed against the cfgs and module registration, and both frozen test binaries must list exactly the tracked default/selective cases before a cohort executes any test. Unrelated existing tests may appear in the listing but are never selected by this protocol.

Two cohorts are independently grantable and never chain automatically:

| Cohort | Exact cases | Per test | Aggregate |
|---|---:|---:|---:|
| `ordinary` | 20 (9 default, 11 selective) | 60 s | 180 s |
| `constructors` | 7 (3 default, 4 selective) | 120 s | 300 s |

Each aggregate includes the exact c193 lifecycle's eight-second cleanup reserve, two bounded 15-second test listings, frozen executable copies, source/artifact verification, tests and final bookkeeping. CPU22 and one test thread are proposed; actual launch requires ROOT's numerical lease. Source `scripts/env.sh` and the private license environment without printing its value. Only license-environment presence is recorded. The earlier source proposal motivated these limits; they are fixed before any run. Timeout or failure preserves all unrun cases and does not authorize a retry or extension.

Execute owned copies whose full hashes match the two audited codegen outputs. Every case uses `--exact <full name> --test-threads=1 --nocapture`. Preserve complete listings, per-case logs, exit/cancellation/timeout/group-cleanup records, elapsed operational durations and input hashes. Require exactly one matching libtest name and exactly `1 passed; 0 failed; 0 ignored; 0 measured` for each case, successful owned cleanup and no hidden zero-test pass. The listing must include every tracked case for its feature configuration, with no duplicate or omitted names.

Verify every bound source/tool/dependency/native/preparation/audit artifact and original test binary before the cohort and after each test, together with the frozen executable copies. The additional guard overhead is included in the fixed cohort cap. Save terminal outcomes before final hashes; any global guard, deadline, cleanup or parser failure disqualifies the cohort. Keep later cases unrun after the first failure. Independently check saved logs and commands after terminal before accepting test completion.

These tests cover policy independence, exact-cache identity/separation, eager/lazy inheritance, shape ordering, native ABC selection, generic/Dual exclusion, unchanged sidecar accounting, and real masked-planar/SixPoint constructor routing. Planar preparation helpers are checked directly, including invalid/empty inputs; they do not independently establish numerically triggered retry/scatter. Planar and ThinSix constructor Dual cases are primal-only. No public SixPoint Dual, broad-native runtime, new domain, whole-array/reference or performance claim follows. Whole-array and retained SixPoint numerical regression stages remain separately planned and granted.
