# Paused: four-engine preflight diagnosis

User requested pause. No owned build, numerical probe, timing process, or analysis job remains running. Do not rerun or change frozen gates without ROOT coordination.

The single authorized four-engine timing attempt failed initial CONTROLS admission before calibration or performance samples. Preserve `timing-quiet254/{receipt.json,raw.jsonl}` and frozen readiness/source/protocol unchanged. All eight cases are unmeasured; raw pending statuses remain visible. Three child processes exited zero, source/input guards passed, and the raw response count is one.

Exactly one leaf differs between `../qualification-001/results.json` controls and the initial raw response: `/controls/masters/selected_families/2/cases/10/baseline/lanes/1/six_outputs/0/1/rational`. It is C0, `physical_complex_mixed_branches`, lane 1, the finite imaginary component of the Symbolica baseline. Inputs are [-1,-2,30,2,3,5,1]; this lane has real masses and an absorptive branch.

Qualified value: -6854632527929679/36028797018963968, f64 -0.19025427144630178, bits bfc85a4080e4a14f. Fresh CONTROL-first value: -428414532995605/2251799813685248, f64 -0.1902542714463018, bits bfc85a4080e4a150. Difference is -2^-55, one ULP. All other JSON leaves agree, including statuses, flags, precision, signs, all candidate native values, all other baseline values, and unchanged numeric/Dual controls. The case maximum normalized difference remains 7.03880642109349e-16; represented differences remain eight and signed-zero differences zero.

Qualification runs all eight whole-reduction cases and their repeats before CONTROLS. Timing invokes CONTROLS in a fresh process first. This schedule distinction is established; its causal mechanism is unresolved. This is a represented floating-value difference, not incidental metadata. No tolerance or exact-own-snapshot gate has been weakened.

Source findings: master_controls.rs records exact represented rationals and checks two exact repeats within each evaluator. ExactMasterPlan constructs fresh expressions and uses evaluator_with_stack_reuse; oneloopmaster compile uses direct_translation(true), horner_iterations(0). The shared function map is initialized through OnceLock. Symbolica symbols compare IDs and Atom ordering uses encoded data, but no evidence yet proves initialization order caused the difference. No paired evaluator exports from the failed and qualified sessions exist.

Next concrete action after resume: continue bounded read-only inspection of oneloopmaster normalize_inputs and Symbolica direct-translation operand ordering, and propose a diagnostic that explicitly exports and compares CONTROL-first versus CASE-first evaluator graphs. Obtain ROOT authorization before running such a numerical diagnostic. Preserve this failed attempt even if a later protocol is qualified. Do not begin timing until ROOT grants a new immutable quiet window.

Bindings: frozen v2 readiness SHA256 43a3fb5a008398871242441dcd603fa3e9912da4367f8d23ccf3f769a34fe618; failed raw SHA256 dc04acc0afce3d1fb86a9a1f36177c25b5251d622945692f554fc4f5d0a5bb17; quiet-window manifest validation/benchmark-quiet/20261023e/window.json SHA256 fea087f50a1aed956f9326dfde916639c5b99ea11f791de17635e011ec3584fd. The ongoing sibling lazy cohort is ROOT-owned and independent.

Handoff preparation initially attempted an unsourced python command, which exited127 without writing a file; sourcing scripts/env.sh corrected this documentation-only command. No numerical or timing retry occurred.
