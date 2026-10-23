"""Prepare isolated Symbolica-based alias-use deduplication, with exact reference."""

def once(s,a,b):
    assert s.count(a)==1,a[:100]
    return s.replace(a,b)


def prepare_source(s, original, cases):
    begin=s.index('fn collect_alias_uses(\n');end=s.index('\nfn collect_denominators(',begin)
    baseline=s[begin:end]
    legacy=baseline.replace('collect_alias_uses(', 'collect_alias_uses_legacy(')
    candidate=once(baseline,'''    if let Some((condition, yes, no)) = if_parts(value) {''','''    match value {
        AtomView::Num(_) => return,
        AtomView::Var(_) => {
            let alias = value.to_owned();
            if definitions.contains_key(&alias) { record_alias_use(alias, active, uses); }
            return;
        }
        _ => {}
    }
    if !value.contains_symbol(Symbol::IF) {
        // This Symbolica traversal deliberately ignores Num coefficient internals,
        // matching the prior walker; function names are not variable references.
        for indeterminate in value.get_all_indeterminates(true) {
            if matches!(indeterminate, AtomView::Var(_)) {
                let alias = indeterminate.to_owned();
                if definitions.contains_key(&alias) { record_alias_use(alias, active, uses); }
            }
        }
        return;
    }
    if let Some((condition, yes, no)) = if_parts(value) {''')
    candidate=once(candidate,'''                uses.entry(alias).or_default().insert(active.clone());''','''                record_alias_use(alias, active, uses);''')
    helper='''fn record_alias_use(alias: Atom, active: &Atom, uses: &mut HashMap<Atom, BTreeSet<Atom>>) {
    let paths = uses.entry(alias).or_default();
    let always = Atom::num(1);
    if paths.contains(&always) { return; }
    if active == &always { paths.clear(); }
    paths.insert(active.clone());
}

'''
    s=s[:begin]+helper+candidate+'\n\n'+legacy+s[end:]
    s=once(s,'''        let mut reachable = HashMap::new();
        eprintln!("HIGHPOINT_PHASE reverse alias uses START");''','''        let verify_alias_uses = std::env::var_os("IREGI_ALIAS_USE_VERIFY").is_some();
        let mut reference_monitor = monitor.clone();
        let mut reference_uses = HashMap::new();
        let mut reference_indices = HashMap::new();
        let mut reference_reachable = HashMap::new();
        if verify_alias_uses {
            for expression in plan.moments.iter().flatten() {
                collect_alias_uses_legacy(expression.as_view(), &always, &definitions, &mut reference_uses);
            }
            assert_eq!(normalized_use_map(&uses), normalized_use_map(&reference_uses), "initial normalized alias uses differ");
        }
        let mut legacy_collect_seconds = 0.0f64;
        let mut candidate_collect_seconds = 0.0f64;
        let mut verified_aliases = 0usize;
        let mut reachable = HashMap::new();
        eprintln!("HIGHPOINT_PHASE reverse alias uses START");''')
    s=once(s,'''            if let Some(paths) = uses.remove(alias) {
                let active = monitor.intern_predicate(union_paths(paths), &mut predicate_indices);
                collect_alias_uses(body.as_view(), &active, &definitions, &mut uses);
                reachable.insert(alias.clone(), active);
            }''','''            let candidate_paths = uses.remove(alias);
            let reference_paths = if verify_alias_uses { reference_uses.remove(alias) } else { None };
            if verify_alias_uses {
                assert_eq!(candidate_paths.is_some(), reference_paths.is_some(), "reachable alias presence differs at {phase_index}");
            }
            if let Some(paths) = candidate_paths {
                let union = union_paths(paths);
                let active = monitor.intern_predicate(union.clone(), &mut predicate_indices);
                if verify_alias_uses {
                    let reference_union = union_paths(reference_paths.unwrap());
                    assert_eq!(union, reference_union, "complete normalized lazy predicate differs at {phase_index}");
                    let reference_active = reference_monitor.intern_predicate(reference_union, &mut reference_indices);
                    assert_eq!(active, reference_active, "root predicate identity differs at {phase_index}");
                    let started = std::time::Instant::now();
                    collect_alias_uses_legacy(body.as_view(), &reference_active, &definitions, &mut reference_uses);
                    legacy_collect_seconds += started.elapsed().as_secs_f64();
                    reference_reachable.insert(alias.clone(), reference_active);
                    verified_aliases += 1;
                }
                let started = std::time::Instant::now();
                collect_alias_uses(body.as_view(), &active, &definitions, &mut uses);
                candidate_collect_seconds += started.elapsed().as_secs_f64();
                reachable.insert(alias.clone(), active);
            }''')
    s=once(s,'''        eprintln!("HIGHPOINT_PHASE reverse alias uses END elapsed={:?} reachable={}", phase_started.elapsed(), reachable.len());''','''        eprintln!("HIGHPOINT_PHASE reverse alias uses END elapsed={:?} reachable={}", phase_started.elapsed(), reachable.len());
        if verify_alias_uses {
            assert_eq!(reachable, reference_reachable, "full reverse reachable maps differ");
            assert_eq!(monitor.predicate_aliases, reference_monitor.predicate_aliases, "complete predicate alias definitions differ");
            assert_eq!(predicate_indices, reference_indices, "predicate cache identities differ");
            assert_eq!(normalized_use_map(&uses), normalized_use_map(&reference_uses), "remaining normalized use maps differ");
        }
        eprintln!("HIGHPOINT_USE_DEDUP reverse_verified={} reachable={} predicate_aliases={} legacy_collect_seconds={} candidate_collect_seconds={}", verified_aliases, reachable.len(), monitor.predicate_aliases.len(), legacy_collect_seconds, candidate_collect_seconds);
        if std::env::var_os("IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE").is_some() {
            return Err(ReductionError::Preparation("diagnostic stop after alias-use reverse pass".into()));
        }''')
    s+='''
fn normalized_use_map(uses: &HashMap<Atom, BTreeSet<Atom>>) -> HashMap<Atom, Atom> {
    uses.iter().map(|(alias, paths)| (alias.clone(), union_paths(paths.clone()))).collect()
}
'''+cases
    test_names=['conditional_alias_monitors_preserve_inactive_poles_and_union_paths','inactive_master_requests_are_skipped_per_sample','master_dependent_activation_is_conservative_and_not_circular']
    s+='\nmod diagnostic_use_semantics {\n    use super::*;\n    fn complex(x: f64) -> Complex<f64> { Complex::new(x, 0.0) }\n'
    for name in test_names:
        a=original.index('    fn '+name+'() {')
        # All selected existing tests end immediately before another test or module end.
        next_test=original.find('    #[test]',a)
        b=next_test if next_test>=0 else original.rfind('\n}')
        s+=original[a:b].replace('    fn '+name+'()', '    pub(super) fn '+name+'()',1)
    s+='}\n'
    return s
