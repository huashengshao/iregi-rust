"""Add stderr phase timers to a frozen full-execution source only."""
from pathlib import Path

def replace_once(text, needle, replacement):
    assert text.count(needle) == 1, needle[:100]
    return text.replace(needle, replacement)

def apply_phase_hooks(snapshot):
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
    path = snapshot / "src/stability.rs"
    source = path.read_text()
    source = replace_once(source, "        for (alias, body) in &plan.aliases {\n            if !reachable.contains_key(alias)", "        let primal_started = std::time::Instant::now();\n        for (primal_index, (alias, body)) in plan.aliases.iter().enumerate() {\n            if primal_index % 1024 == 0 {\n                eprintln!(\"HIGHPOINT_PHASE primal aliases PROGRESS index={} elapsed={:?} amplitudes={}\", primal_index, primal_started.elapsed(), amplitudes.len());\n            }\n            if !reachable.contains_key(alias)")
    path.write_text(source)
