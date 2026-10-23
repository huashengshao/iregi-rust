#[test]
fn slim_planar_complex_full_jet_partition_matches_original_certificate() {
    use crate::original_exact_zero_certificate as original;
    let shape = vec![vec![0,0],vec![0,1],vec![1,0],vec![1,1],vec![2,0],vec![0,2]];
    let components = shape.len();
    let plan = CertifiedPlanarReductionPlan::new(settings(0)).unwrap();
    let parameters = [variable("slim_planar_u"), variable("slim_planar_v")];
    let zero = Complex::new(Rational::from(0),Rational::from(0));
    let real = exact_row(&row(&0_f64, &points(), components));
    let make_jet = |quadratic: bool| {
        let mut expressions: Vec<Atom> = points().iter().flatten().copied().chain([4,9,16,25,36,3]).map(Atom::num).collect();
        expressions[4] = parameters[0].clone();
        if quadratic {
            // Symbolica prepares p4=p2+p3-v*p1; with u=i*s,v=i*t,
            // its time component -u*v has a real mixed coefficient +1.
            expressions[9] = parameters[1].clone();
            expressions[16] = -(&parameters[0] * &parameters[1]);
            expressions[17] = &parameters[1] - &parameters[1];
        } else {
            expressions[8] = parameters[1].clone();
            expressions[16] = &parameters[0] + &parameters[1];
        }
        let exact: ExpressionEvaluator<Complex<Rational>> = Atom::evaluator_multiple(&expressions,&parameters)
            .direct_translation(true).horner_iterations(0).cores(1).build().unwrap();
        // Every coefficient/intermediate here is a small integer. Mapping the
        // prepared Symbolica polynomial to Float256 is exact for this fixture.
        let prototype=Float::new(256);
        let mut evaluator = exact.vectorize(&Dualizer::new(HyperDual::<u8>::new(shape.clone()),Vec::new())).unwrap()
            .map_coeff_with_prec(&|value|Complex::new(prototype.from_rational(&value.re),prototype.from_rational(&value.im)),256).into_batch_evaluator();
        let mut seeds = vec![zero.clone();2*components];
        seeds[2].im = Rational::from(1);
        seeds[components+1].im = Rational::from(1);
        let output = vec![zero.clone();26*components];
        let seeds:Vec<_>=seeds.iter().map(|value|Complex::new(prototype.from_rational(&value.re),prototype.from_rational(&value.im))).collect();
        let mut output=vec![Complex::new(Float::new(256),Float::new(256));output.len()];
        evaluator.evaluate_batch(&seeds,&mut output,1).unwrap();
        output.iter().map(|value|Complex::new(value.re.exact_rational().unwrap(),value.im.exact_rational().unwrap())).collect::<Vec<_>>()
    };
    let rotated=make_jet(false); let quadratic=make_jet(true);
    assert_eq!(quadratic[16*components+3],Complex::new(Rational::from(1),Rational::from(0)));
    let mut transverse=rotated.clone();transverse[16*components+3].im=Rational::from(1);
    let mut omitted=quadratic.clone();omitted[16*components+3]=zero.clone();
    let mut tiny=quadratic.clone();tiny[16*components+3].re+=Rational::from((1,2)).pow(300);
    let rows=[real.clone(),rotated.clone(),transverse.clone(),real.clone(),quadratic.clone(),omitted.clone(),tiny.clone()];
    let input=rows.concat();
    let mut candidate=plan.certificate(&Some(shape.clone())).unwrap().instantiate();
    let mut baseline=original::ExactZeroConstraintPlan::new_dual(&plan.parameters,&plan.constraints,&HyperDual::<u8>::new(shape.clone())).unwrap().instantiate();
    let rank:Vec<_>=(0..rows.len()).map(|_|(0..components).map(|component|(0,component)).collect::<Vec<_>>()).collect();
    for maximum in [128,512] {
        candidate.set_precision_budget(128,maximum).unwrap();baseline.set_precision_budget(128,maximum).unwrap();
        let actual=candidate.check_selected_batch(&input,rows.len(),&rank).unwrap();
        let expected=baseline.check_selected_batch(&input,rows.len(),&rank).unwrap();
        assert_eq!(format!("{actual:?}"),format!("{expected:?}"));
        for lane in [0,1,3,4] {assert_eq!(actual[lane],ExactZeroCertificate::Zero);}
        for lane in [2,5] {assert_eq!(actual[lane],ExactZeroCertificate::Nonzero{constraint:0,component:3});}
        if maximum==128 {assert_eq!(actual[6],ExactZeroCertificate::Unresolved{working_bits:128});}
        else {assert_eq!(actual[6],ExactZeroCertificate::Nonzero{constraint:0,component:3});}
        assert_eq!(candidate.passes(),baseline.passes());assert_eq!(candidate.evaluated_rows(),baseline.evaluated_rows());
        let charts=vec![(1..5).map(|constraint|(constraint,0)).collect::<Vec<_>>();rows.len()];
        let actual=candidate.check_selected_batch(&input,rows.len(),&charts).unwrap();
        let expected=baseline.check_selected_batch(&input,rows.len(),&charts).unwrap();
        assert_eq!(format!("{actual:?}"),format!("{expected:?}"));
        assert!(actual.iter().all(|value|matches!(value,ExactZeroCertificate::Nonzero{component:0,..})));
    }
    // Reorder mixed real/complex rows with an empty selection in the middle;
    // then reuse the same workspaces for empty and all-complex batches.
    for order in [vec![6,4,0,2,1,3,5],vec![1,2,4,5]] {
        let values=order.iter().flat_map(|&lane|rows[lane].clone()).collect::<Vec<_>>();
        let mut selected=vec![(0..components).map(|c|(0,c)).collect::<Vec<_>>();order.len()];selected[1].clear();
        let a=candidate.check_selected_batch(&values,order.len(),&selected).unwrap();
        let b=baseline.check_selected_batch(&values,order.len(),&selected).unwrap();assert_eq!(format!("{a:?}"),format!("{b:?}"));
        assert_eq!(a[1],ExactZeroCertificate::Zero);assert_eq!(candidate.passes(),baseline.passes());assert_eq!(candidate.evaluated_rows(),baseline.evaluated_rows());
        assert!(candidate.check_selected_batch(&[],0,&[]).unwrap().is_empty());assert!(baseline.check_selected_batch(&[],0,&[]).unwrap().is_empty());
        assert_eq!(candidate.evaluated_rows(),0);assert_eq!(baseline.evaluated_rows(),0);
    }
}
