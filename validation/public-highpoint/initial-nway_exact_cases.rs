/// Private snapshot-only witness: equality checks use complete canonical Atoms.
pub fn diagnostic_amplitude_exact_cases() -> Vec<(String, String)> {
    let x = Atom::var(symbolica::symbol!("iregi_nway_diagnostic::x"));
    let y = Atom::var(symbolica::symbol!("iregi_nway_diagnostic::y"));
    let p = Atom::var(symbolica::symbol!("iregi_nway_diagnostic::p"));
    let q = Atom::var(symbolica::symbol!("iregi_nway_diagnostic::q"));
    let mut amplitudes = HashMap::from([
        (x.clone(), Symbol::ABS.call((&x,))),
        (y.clone(), Symbol::ABS.call((&y,))),
    ]);
    let branch = Symbol::IF.call((&p, &x, Atom::num(-2) * &y));
    let nested = Symbol::IF.call((&q, &branch, &x + &y));
    let mut cases = vec![
        ("zero".into(), Atom::num(0)),
        ("constant".into(), Atom::num(-7)),
        ("direct_alias".into(), x.clone()),
        ("mixed_affine".into(), Atom::num(-3)*&x + Atom::num(5)*&y + Atom::num(-7)),
        ("cancellation".into(), &x-&x+&y),
        ("factored_coefficient".into(), (&p+&q)*(&x+&y)+(&p-&q)*&x),
        ("rational_coefficient".into(), (&p+&q).pow(-1)*&x+&p*&y),
        ("top_if".into(), branch.clone()),
        ("nested_if_product".into(), (&p+&q)*&nested+Atom::num(3)*&branch+Atom::num(7)),
        ("nonlinear_power_error".into(), x.pow(2)),
        ("nonlinear_product_error".into(), &x*&y),
        ("nonlinear_function_error".into(), Symbol::EXP.call((&x,))),
        ("nonlinear_hidden_branch_error".into(), Symbol::IF.call((&p, x.pow(2), &y))),
    ];
    for size in [32usize,128,512] {
        let terms = (0..size).map(|i| {
            let variable=Atom::var(symbolica::symbol!(format!("iregi_nway_diagnostic::master_{i}")));
            amplitudes.insert(variable.clone(), Symbol::ABS.call((&variable,)));
            (Atom::num((i%7) as i64-3)*&p + Atom::num((i%11) as i64+1))*variable
        }).collect::<Vec<_>>();
        cases.push((format!("wide_{size}"), Atom::add_many(terms)));
    }
    let mut results=Vec::new();
    for (name, expression) in cases {
        let begin=std::time::Instant::now();
        let legacy=master_amplitude_legacy(&expression,&amplitudes);
        let legacy_seconds=begin.elapsed().as_secs_f64();
        let begin=std::time::Instant::now();
        let candidate=master_amplitude_nway(&expression,&amplitudes);
        let candidate_seconds=begin.elapsed().as_secs_f64();
        let full_result=match (legacy,candidate) {
            (Ok(left),Ok(right))=> {assert_eq!(left,right,"full expression differs: {name}");right.to_string()},
            (Err(left),Err(right))=> {assert_eq!(left.to_string(),right.to_string());format!("ERROR: {right}")},
            _=>panic!("success/error mismatch: {name}"),
        };
        eprintln!("HIGHPOINT_EXACT name={name} equal=true legacy_seconds={legacy_seconds} nway_seconds={candidate_seconds}");
        results.push((name, full_result));
    }
    results
}
