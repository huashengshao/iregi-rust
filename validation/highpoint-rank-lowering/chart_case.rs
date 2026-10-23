    #[test]
    fn lazy_seven_point_charts_preserve_exact_mixed_dual_identities() {
        use symbolica::{domains::{dual::HyperDual, float::Complex, rational::Rational},
                        evaluate::{Dualizer, ExpressionEvaluator}};
        let x = Atom::var(symbolica::symbol!("rank_lowering::chart_x"));
        let y = Atom::var(symbolica::symbol!("rank_lowering::chart_y"));
        let points = [[0,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[1,0,0,0],[1,1,1,1],[2,3,5,7]];
        let shifts: Vec<_> = points.iter().map(|p| p.map(Atom::num)).collect();
        let mut masses: Vec<_> = [4,9,16,25,36,74,64].into_iter().map(Atom::num).collect();
        masses[5] = &masses[5] + &x;
        masses[6] = &masses[6] + &y;
        let mut compiler = PvCompiler::with_aliases(shifts.clone(), masses.clone()).unwrap();
        compiler.enable_highpoint_rank_lowering().unwrap();
        let weights = compiler.highpoint_coordinate_identity(&(0..7).collect::<Vec<_>>()).unwrap().unwrap();
        let mut expressions: Vec<_> = weights.iter().flatten().cloned().collect();
        for mu in 0..4 {
            expressions.push(Atom::add_many(&weights[mu]));
            for nu in 0..4 {
                expressions.push(Atom::add_many(&(0..7).map(|i| &weights[mu][i] * &shifts[i][nu] * Atom::num(if nu==0 {2} else {-2})).collect::<Vec<_>>()));
            }
            expressions.push(Atom::add_many(&(0..7).map(|i| &weights[mu][i] * (dot(&shifts[i], &shifts[i]) - &masses[i])).collect::<Vec<_>>()));
        }
        let exact: ExpressionEvaluator<Complex<Rational>> = Atom::evaluator_multiple(&expressions, &[x,y])
            .add_aliases(compiler.aliases().iter().cloned()).unwrap()
            .direct_translation(true).horner_iterations(0).cores(1).build().unwrap();
        let shape = vec![vec![0,0],vec![1,0],vec![0,1],vec![2,0],vec![1,1],vec![0,2]];
        let mut evaluator = exact.vectorize(&Dualizer::new(HyperDual::<Complex<Rational>>::new(shape),vec![])).unwrap();
        let zero = Complex::new(Rational::from(0),Rational::from(0));
        let one = Complex::new(Rational::from(1),Rational::from(0));
        let tiny = Rational::from((Integer::from(1),Integer::from(2).pow(80)));
        for offset in [Rational::from(0),Rational::from(1),Rational::from(-2),tiny] {
            let mut input=vec![zero.clone();12]; input[0]=Complex::new(offset.clone(),Rational::from(0));
            input[1]=one.clone(); input[8]=one.clone();
            let mut output=vec![zero.clone();expressions.len()*6];
            evaluator.evaluate(&input,&mut output);
            if offset==Rational::from(0) {
                assert!((0..4).any(|mu| output[(mu*7+6)*6]!=zero), "regular alternate chart must be selected");
            }
            for mu in 0..4 { for equation in 0..6 { for component in 0..6 {
                let expected=if equation==mu+1 && component==0 {&one} else {&zero};
                assert_eq!(&output[(28+mu*6+equation)*6+component],expected,"direction={mu} equation={equation} Taylor={component}");
            }}}
        }
        eprintln!("exact lazy chart identities: 4 offsets × 4 directions × 6 equations × 6 mixed Taylor components");
    }
