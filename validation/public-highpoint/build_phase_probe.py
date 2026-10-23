"""Build diagnostic-only phase markers onto the frozen timed-out candidate.

Only stderr/Instant/counter instrumentation is added. No production sources,
algebra, branches, precision targets, or stability policies are changed.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text, needle, replacement):
    if text.count(needle) != 1:
        raise ValueError(f"Expected exactly one frozen-source anchor: {needle[:100]}")
    return text.replace(needle, replacement)


def main():
    root = Path.cwd()
    here = root / "validation/public-highpoint"
    parent = json.loads((here / "candidate-build.json").read_text())
    target = root / "target/public-highpoint/phase"
    snapshot = target / "source/crates/iregi-rust"
    if target.exists():
        raise ValueError("Keep existing phase snapshot immutable; use a new build name")
    original = root / parent["frozen_core_source"]
    for name, expected in parent["library_source_hashes"].items():
        assert sha(original / Path(name).relative_to("crates/iregi-rust")) == expected
    snapshot.parent.mkdir(parents=True)
    shutil.copytree(original, snapshot)
    path = snapshot / "src/stability.rs"
    source = path.read_text()
    source = replace_once(source, "        let definitions: HashMap<_, _> = plan.aliases.iter().cloned().collect();", '''        eprintln!("HIGHPOINT_PHASE stability definitions START aliases={}", plan.aliases.len());
        let phase_started = std::time::Instant::now();
        let definitions: HashMap<_, _> = plan.aliases.iter().cloned().collect();
        eprintln!("HIGHPOINT_PHASE stability definitions END elapsed={:?}", phase_started.elapsed());''')
    source = replace_once(source, "        for expression in plan.moments.iter().flatten() {", '''        eprintln!("HIGHPOINT_PHASE root alias uses START roots={}", plan.moments.len()*4);
        let phase_started = std::time::Instant::now();
        for expression in plan.moments.iter().flatten() {''')
    source = replace_once(source, "        let mut reachable = HashMap::new();", '''        eprintln!("HIGHPOINT_PHASE root alias uses END elapsed={:?} uses={}", phase_started.elapsed(), uses.len());
        let mut reachable = HashMap::new();
        eprintln!("HIGHPOINT_PHASE reverse alias uses START");
        let phase_started = std::time::Instant::now();''')
    source = replace_once(source, "        for (alias, body) in plan.aliases.iter().rev() {", '''        for (phase_index, (alias, body)) in plan.aliases.iter().rev().enumerate() {
            if phase_index % 4096 == 0 {
                eprintln!("HIGHPOINT_PHASE reverse alias uses PROGRESS index={} elapsed={:?} uses={} reachable={}", phase_index, phase_started.elapsed(), uses.len(), reachable.len());
            }''')
    source = replace_once(source, "        let mut denominators = BTreeSet::new();", '''        eprintln!("HIGHPOINT_PHASE reverse alias uses END elapsed={:?} reachable={}", phase_started.elapsed(), reachable.len());
        eprintln!("HIGHPOINT_PHASE local checks START");
        let phase_started = std::time::Instant::now();
        let mut denominators = BTreeSet::new();''')
    source = replace_once(source, "        let mut denominators = BTreeSet::new();\n        for (alias, body) in &plan.aliases {", '''        let mut denominators = BTreeSet::new();
        for (phase_index, (alias, body)) in plan.aliases.iter().enumerate() {
            if phase_index % 4096 == 0 {
                eprintln!("HIGHPOINT_PHASE local checks PROGRESS index={} elapsed={:?} checks={} roots={}", phase_index, phase_started.elapsed(), monitor.checks.len(), monitor.expressions.len());
            }''')
    source = replace_once(source, "        let base_dimension = 4 + 2 * i32::from(plan.settings.dimension_shift)", '''        eprintln!("HIGHPOINT_PHASE alias checks END elapsed={:?} checks={} roots={}", phase_started.elapsed(), monitor.checks.len(), monitor.expressions.len());
        let base_dimension = 4 + 2 * i32::from(plan.settings.dimension_shift)''')
    source = replace_once(source, "        for (denominator, active) in denominators {", '''        eprintln!("HIGHPOINT_PHASE moment checks END elapsed={:?}; denominator checks START count={}", phase_started.elapsed(), denominators.len());
        for (denominator, active) in denominators {''')
    source = replace_once(source, "        monitor.prepare_primal_amplitudes(plan, &reachable, base_dimension)?;", '''        eprintln!("HIGHPOINT_PHASE local checks END elapsed={:?} checks={} roots={}", phase_started.elapsed(), monitor.checks.len(), monitor.expressions.len());
        eprintln!("HIGHPOINT_PHASE primal amplitudes START");
        let phase_started = std::time::Instant::now();
        monitor.prepare_primal_amplitudes(plan, &reachable, base_dimension)?;
        eprintln!("HIGHPOINT_PHASE primal amplitudes END elapsed={:?}", phase_started.elapsed());''')
    source = replace_once(source, "        monitor.prepare_master_activations(plan);", '''        eprintln!("HIGHPOINT_PHASE master activations START");
        let phase_started = std::time::Instant::now();
        monitor.prepare_master_activations(plan);
        eprintln!("HIGHPOINT_PHASE master activations END elapsed={:?}", phase_started.elapsed());''')
    path.write_text(source)
    path = snapshot / "src/execution.rs"
    source = path.read_text()
    source = replace_once(source, "        let distance_zeros = if distance_polynomials.is_empty() {", '''        eprintln!("HIGHPOINT_PHASE distance certificates START count={}", distance_polynomials.len());
        let phase_started = Instant::now();
        let distance_zeros = if distance_polynomials.is_empty() {''')
    source = replace_once(source, "        let stability = Arc::new(StabilityPlan::prepare(plan)?);", '''        eprintln!("HIGHPOINT_PHASE distance certificates END elapsed={:?}", phase_started.elapsed());
        eprintln!("HIGHPOINT_PHASE stability prepare START");
        let stability = Arc::new(StabilityPlan::prepare(plan)?);''')
    source = replace_once(source, "    let mut exact: ExpressionEvaluator<Complex<Rational>> =", '''    eprintln!("HIGHPOINT_PHASE exact evaluator START expressions={} parameters={} aliases={}", expressions.len(), parameters.len(), aliases.len());
    let phase_started = Instant::now();
    let mut exact: ExpressionEvaluator<Complex<Rational>> =''')
    source = replace_once(source, "    Ok(exact)\n}", '''    eprintln!("HIGHPOINT_PHASE exact evaluator END elapsed={:?}", phase_started.elapsed());
    Ok(exact)
}''')
    path.write_text(source)
    sources = {str(p.relative_to(snapshot)): sha(p) for p in (snapshot / "src").rglob("*.rs")}
    diff = subprocess.run(["diff", "-ru", str(original / "src"), str(snapshot / "src")], text=True, capture_output=True)
    if diff.returncode != 1:
        raise ValueError("Expected only the diagnostic source diff")
    (here / "phase-instrumentation.patch").write_text(diff.stdout)
    commands = []
    for parent_command in [parent["core_command"], parent["probe_command"]]:
        commands.append([part.replace(str(original), str(snapshot)).replace(
            str(root / "target/public-highpoint/candidate"), str(target)).replace(
            "metadata=public_highpoint_promoted", "metadata=public_highpoint_phase") for part in parent_command])
    guards = [Path(part.split("=", 1)[1]) for part in parent["core_command"]
              if part.startswith(("iregi_masters=", "symbolica=", "serde=", "thiserror="))]
    shared = root / "target/cargo-build/debug/deps"
    guards.extend(p for p in shared.iterdir() if p.suffix in [".rlib", ".so"])
    before = {str(p.relative_to(root)): sha(p) for p in guards}
    env = os.environ.copy()
    env.update(CARGO_MANIFEST_DIR=str(snapshot), CARGO_CRATE_NAME="iregi_rust")
    start = time.monotonic()
    codes = []
    for label, command in zip(["core", "probe"], commands):
        with (here / f"phase-{label}-build.log").open("w") as log:
            code = subprocess.call(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
        codes.append(code)
        if code:
            break
    after = {str(p.relative_to(root)): sha(p) for p in guards}
    changed = {key: [value, after.get(key)] for key, value in before.items() if after.get(key) != value}
    unchanged = all(sha(snapshot/name) == value for name, value in sources.items())
    record = {"status": "passed" if codes == [0, 0] and not changed and unchanged else "failed",
              "commands": commands, "exit_codes": codes, "changed_inputs": changed,
              "frozen_core_source": str(snapshot.relative_to(root)),
              "library_source_hashes": {"crates/iregi-rust/"+key: value for key, value in sources.items()},
              "frozen_core_sources_verified_after_build": unchanged,
              "parent_build_manifest_sha256": sha(here / "candidate-build.json"),
              "instrumentation_patch_sha256": sha(here / "phase-instrumentation.patch"),
              "build_script_sha256": sha(Path(__file__)),
              "source_sha256": parent["source_sha256"], "elapsed_seconds": time.monotonic()-start,
              "scope": "Frozen timed-out candidate plus stderr/Instant/count instrumentation only; phase discovery, not a new numerical implementation or performance comparison."}
    if codes == [0, 0]:
        record["binary_sha256"] = sha(target / "highpoint_public")
    (here / "phase-build.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({key: record[key] for key in ["status", "exit_codes", "elapsed_seconds", "changed_inputs"]}), flush=True)
    if record["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
