pub fn diagnostic_alias_use_cases() -> Vec<(String, String)> {
    let sx=symbolica::symbol!("iregi_use_diagnostic::x");
    let sy=symbolica::symbol!("iregi_use_diagnostic::y");
    let sz=symbolica::symbol!("iregi_use_diagnostic::z");
    let x=Atom::var(sx);let y=Atom::var(sy);let z=Atom::var(sz);
    let definitions=HashMap::from([(x.clone(), Atom::num(0)),(y.clone(), Atom::num(0)),(z.clone(),Atom::num(0))]);
    let polynomial_number=(&x+Atom::num(1)).set_coefficient_ring(sx);
    assert!(matches!(polynomial_number.as_view(), AtomView::Num(_)));
    assert!(polynomial_number.get_all_symbols(false).contains(&sx));
    let conditional=Symbol::IF.call((&x,&y,&z));
    let cases=vec![
        ("constant", Atom::num(7)),
        ("variable", x.clone()),
        ("repeated_variable", &x*&y+&x*&z),
        ("power_exponent", x.pow(&y)),
        ("function_name_is_not_variable", sx.call((&y,))),
        ("function_arguments", Symbol::EXP.call((&x+&y,))),
        ("polynomial_num_ignored", polynomial_number.clone()),
        ("polynomial_num_function_argument", sy.call((&polynomial_number,&z))),
        ("conditional", conditional.clone()),
        ("nested_conditional", Symbol::IF.call((&x,&conditional,&y))),
        ("conditional_in_product", &conditional*(&x+&y)),
        ("conditional_in_power", conditional.pow(-1)),
        ("condition_with_alias", Symbol::IF.call((&x+&y,&z,Atom::num(0)))),
        ("inactive_singular_branch", Symbol::IF.call((&x,&y,&z.pow(-1)))),
    ];
    let mut results=Vec::new();
    for (name, expression) in cases {
        let mut previous=HashMap::new();let mut candidate=HashMap::new();
        collect_alias_uses_legacy(expression.as_view(), &Atom::num(1), &definitions, &mut previous);
        collect_alias_uses(expression.as_view(), &Atom::num(1), &definitions, &mut candidate);
        let expected=normalized_use_map(&previous);let actual=normalized_use_map(&candidate);
        assert_eq!(expected,actual,"normalized complete predicate maps differ: {name}");
        if name=="polynomial_num_ignored" { assert!(actual.is_empty()); }
        if name=="function_name_is_not_variable" { assert!(!actual.contains_key(&x));assert_eq!(actual.len(),1); }
        if name=="polynomial_num_function_argument" { assert!(!actual.contains_key(&x));assert!(!actual.contains_key(&y));assert_eq!(actual.len(),1); }
        if name=="power_exponent" { assert!(actual.contains_key(&x)&&actual.contains_key(&y)); }
        let mut rows=actual.into_iter().map(|(a,p)|format!("{a}={p}")).collect::<Vec<_>>();rows.sort();
        results.push((name.into(),rows.join("\n")));
    }
    for order in [false,true] {
        let mut previous=HashMap::new();let mut candidate=HashMap::new();
        let branch=branch_path(&Atom::num(1),y.as_view(),true);
        let actives=if order {vec![Atom::num(1),branch]}else{vec![branch,Atom::num(1)]};
        for active in actives {
            collect_alias_uses_legacy(x.as_view(),&active,&definitions,&mut previous);
            collect_alias_uses(x.as_view(),&active,&definitions,&mut candidate);
        }
        assert_eq!(normalized_use_map(&previous),normalized_use_map(&candidate));
        assert_eq!(candidate.get(&x),Some(&BTreeSet::from([Atom::num(1)])));
        results.push((format!("unconditional_order_{order}"),"exact normalized paths; one retained literal1".into()));
    }
    let mut previous=HashMap::new();let mut candidate=HashMap::new();
    collect_alias_uses_legacy(x.as_view(),&Atom::num(0),&definitions,&mut previous);
    collect_alias_uses(x.as_view(),&Atom::num(0),&definitions,&mut candidate);
    assert_eq!(normalized_use_map(&previous),normalized_use_map(&candidate));
    assert_eq!(normalized_use_map(&candidate).get(&x),Some(&Atom::num(0)));
    results.push(("inactive_zero_path_retained".into(),"exact zero path and alias presence retained".into()));
    diagnostic_use_semantics::conditional_alias_monitors_preserve_inactive_poles_and_union_paths();
    results.push(("numeric_lazy_inactive_poles".into(),"original three-lane lazy/unstable status assertions passed".into()));
    diagnostic_use_semantics::inactive_master_requests_are_skipped_per_sample();
    results.push(("numeric_master_activation".into(),"original two-lane values and one active scalar-master request passed".into()));
    diagnostic_use_semantics::master_dependent_activation_is_conservative_and_not_circular();
    results.push(("master_dependent_activation_closure".into(),"original conservative activation and master-free predicate assertions passed".into()));
    results
}
