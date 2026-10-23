//! Bounded, untimed public-adapter controls for the private selection experiment.
use iregi_masters::{
    Complex, DoubleFloat, ExactMasterPlan, Float, FloatLike, HyperDual, LaneError,
    MasterBackend, MasterBatch, MasterError, MasterEvaluator, NativeFloat, ScalarIntegral,
};
use serde_json::{Value, json};
use symbolica::{domains::float::SingleFloat, evaluate::EvaluationDomain};

fn c(x: f64) -> Complex<f64> { Complex::new(x, 0.) }
fn real(xs: &[f64]) -> Vec<Complex<f64>> { xs.iter().copied().map(c).collect() }
fn repeated<T: Clone>(point: &[T], rows: usize) -> Vec<T> {
    (0..rows).flat_map(|_| point.iter().cloned()).collect()
}
fn represented<T: NativeFloat>(x: &T) -> Value {
    assert!(x.is_finite(), "nonfinite successful output");
    json!({"rational":x.exact_rational().expect("exact represented value").to_string(),
        "precision":x.get_precision(),"negative_sign":x.negative_sign()})
}
fn input_metadata<T: NativeFloat>(input: &[Complex<T>]) -> Value {
    json!(input.iter().map(|z| [&z.re,&z.im].into_iter().map(|x| {
        let rational=x.exact_rational().map(|q|q.to_string());
        assert_eq!(rational.is_some(),x.is_finite(),"input exact representation unavailable");
        json!({"finite":x.is_finite(),"rational":rational,
            "precision":x.get_precision(),"negative_sign":x.negative_sign()})
    }).collect::<Vec<_>>()).collect::<Vec<_>>())
}
fn snapshot<T: NativeFloat>(batch: &MasterBatch<T>, components: usize,
    expected: &[Option<LaneError>]) -> Value {
    assert_eq!(batch.row_count(), expected.len());
    assert_eq!(batch.component_count(), components);
    assert_eq!(batch.errors(), expected, "unexpected lane status");
    assert_eq!(batch.private_six_values().len(), expected.len()*6*components);
    let lanes: Vec<_> = expected.iter().enumerate().map(|(lane,error)| {
        if let Some(error)=error {
            assert_eq!(batch.lane(lane).unwrap_err(), error);
            json!({"error":format!("{error:?}"),"six_outputs":Value::Null})
        } else {
            assert!(batch.lane(lane).is_ok());
            let values=&batch.private_six_values()[lane*6*components..(lane+1)*6*components];
            json!({"error":Value::Null,"six_outputs":values.iter().map(|z|
                json!([represented(&z.re),represented(&z.im)])).collect::<Vec<_>>()})
        }
    }).collect();
    json!({"rows":expected.len(),"components":components,"lanes":lanes})
}

fn invalid_layout<T: NativeFloat>(evaluator: &mut MasterEvaluator<T>)
where Complex<T>: EvaluationDomain {
    assert!(matches!(evaluator.evaluate_batch(&[],1),Err(MasterError::InputLength{..})));
    assert!(matches!(evaluator.evaluate_batch(&[],usize::MAX),Err(MasterError::SizeOverflow)));
}

fn selected_case(label: &str, family: ScalarIntegral,
    baseline: &mut MasterEvaluator<f64>, candidate: &mut MasterEvaluator<f64>,
    input: &[Complex<f64>], expected: &[Option<LaneError>]) -> Value {
    assert_eq!(baseline.backend(), MasterBackend::SymbolicaBatch);
    assert_eq!(candidate.backend(), MasterBackend::RustBatch);
    assert!(baseline.dual_shape().is_none() && candidate.dual_shape().is_none());
    assert_eq!(input.len(), expected.len()*family.arity());
    let original_input=input_metadata(input);
    let a=baseline.evaluate_batch(input,expected.len()).unwrap();
    let b=candidate.evaluate_batch(input,expected.len()).unwrap();
    let av=snapshot(&a,1,expected);let bv=snapshot(&b,1,expected);
    let mut maximum=0_f64;let mut differences=0usize;let mut signed_zero_differences=0usize;
    for lane in 0..expected.len() {
        if expected[lane].is_some() { continue; }
        let point=&input[lane*family.arity()..(lane+1)*family.arity()];
        let scale=point.iter().map(|z|z.re.hypot(z.im)).fold(1_f64,f64::max);
        let unit=match family { ScalarIntegral::A0=>scale,ScalarIntegral::C0=>1./scale,_=>1. };
        for coefficient in 0..6 {
            let x=&a.private_six_values()[lane*6+coefficient];
            let y=&b.private_six_values()[lane*6+coefficient];
            let denominator=(if coefficient==5 {1.} else {unit})+x.re.hypot(x.im);
            let error=(x.re-y.re).hypot(x.im-y.im)/denominator;
            assert!(denominator.is_finite() && denominator>0. && error.is_finite() && error<=1e-10,
                "{label} {} lane{lane} coefficient{coefficient}: {error}",family.name());
            maximum=maximum.max(error);
            for (x,y) in [(x.re,y.re),(x.im,y.im)] {
                differences+=usize::from(x.to_bits()!=y.to_bits());
                signed_zero_differences+=usize::from(x==0. && y==0. && x.to_bits()!=y.to_bits());
            }
            if coefficient==5 { assert_eq!((x.re,x.im,y.re,y.im),(0.,0.,0.,0.)); }
        }
        if label=="scaleless" {
            for batch in [&a,&b] {
                let value=batch.lane(lane).unwrap();
                assert_eq!(value.finite,&[c(0.)]);assert_eq!(value.total_single,&[c(0.)]);
                assert_eq!(value.ir2,&[c(0.)]);
                assert_eq!(value.uv,&[c(if family==ScalarIntegral::B0 {1.} else {0.})]);
                assert_eq!(value.ir,&[c(if family==ScalarIntegral::B0 {-1.} else {0.})]);
            }
        }
    }
    // Two repeated public calls check each backend's own value, precision and zero sign.
    for _ in 0..2 {
        assert_eq!(snapshot(&baseline.evaluate_batch(input,expected.len()).unwrap(),1,expected),av);
        assert_eq!(snapshot(&candidate.evaluate_batch(input,expected.len()).unwrap(),1,expected),bv);
    }
    assert_eq!(input_metadata(input),original_input,"selected input mutated");
    json!({"label":label,"family":family.name(),"status":"passed","baseline_backend":"SymbolicaBatch",
        "candidate_backend":"RustBatch","maximum_normalized_error":maximum,
        "represented_component_differences":differences,"signed_zero_differences":signed_zero_differences,
        "own_repeated_outputs_exact":true,"input_metadata":original_input,"input_unchanged":true,
        "baseline":av,"candidate":bv})
}

type Control<T> = (String,Vec<Complex<T>>,Vec<Option<LaneError>>);
fn unchanged<T: NativeFloat>(label: &str, plan: &ExactMasterPlan, prototype: T,
    cases: Vec<Control<T>>) -> Value where Complex<T>: EvaluationDomain {
    let mut baseline=plan.instantiate(prototype).unwrap();
    let mut candidate=baseline.clone().private_select_f64().unwrap();
    assert_eq!(baseline.backend(),MasterBackend::SymbolicaBatch);
    assert_eq!(candidate.backend(),MasterBackend::SymbolicaBatch);
    assert_eq!(baseline.dual_shape(),candidate.dual_shape());
    assert_eq!(baseline.component_count(),candidate.component_count());
    assert_eq!(baseline.binary_precision(),candidate.binary_precision());
    invalid_layout(&mut baseline);invalid_layout(&mut candidate);
    let mut results=Vec::new();
    for (name,input,expected) in cases {
        assert_eq!(input.len(),expected.len()*plan.family().arity()*plan.component_count());
        let original_input=input_metadata(&input);
        let a=baseline.evaluate_batch(&input,expected.len()).unwrap();
        let b=candidate.evaluate_batch(&input,expected.len()).unwrap();
        let av=snapshot(&a,plan.component_count(),&expected);
        let bv=snapshot(&b,plan.component_count(),&expected);
        assert_eq!(av,bv,"unchanged path {label}/{name}");
        for _ in 0..2 {
            assert_eq!(snapshot(&baseline.evaluate_batch(&input,expected.len()).unwrap(),plan.component_count(),&expected),av);
            assert_eq!(snapshot(&candidate.evaluate_batch(&input,expected.len()).unwrap(),plan.component_count(),&expected),bv);
        }
        assert_eq!(input_metadata(&input),original_input,"unchanged-path input mutated");
        results.push(json!({"label":name,"status":"passed","represented_outputs":av,
            "candidate_exactly_matches_baseline":true,"own_repeated_outputs_exact":true,
            "input_metadata":original_input,"input_unchanged":true}));
    }
    json!({"label":label,"family":plan.family().name(),"status":"passed","backend":"SymbolicaBatch",
        "shape":plan.dual_shape(),"components":plan.component_count(),"cases":results})
}

fn scalar_controls(family: ScalarIntegral, plan: &ExactMasterPlan) -> Value {
    let good=match family {
        ScalarIntegral::A0=>real(&[2.,1.]),
        ScalarIntegral::B0=>real(&[-3.,2.,5.,1.]),
        ScalarIntegral::C0=>real(&[-1.,-5.,-4.,2.,3.,5.,1.]),
        _=>unreachable!(),
    };
    let mut baseline=plan.instantiate(0_f64).unwrap();
    let mut candidate=baseline.clone().private_select_f64().unwrap();
    invalid_layout(&mut baseline);invalid_layout(&mut candidate);
    let mut cases=Vec::new();
    for (step,rows) in [0usize,1,5,3,0,1].into_iter().enumerate() {
        let mut input=repeated(&good,rows);let mut errors=vec![None;rows];
        if rows>1 { input[2*family.arity()-1]=c(-1.);errors[1]=Some(LaneError::InvalidScale); }
        cases.push(selected_case(&format!("reuse_step_{step}_rows_{rows}"),family,&mut baseline,&mut candidate,&input,&errors));
    }
    let mut zero=vec![c(0.);family.arity()];*zero.last_mut().unwrap()=c(1.);
    cases.push(selected_case("scaleless",family,&mut baseline,&mut candidate,&repeated(&zero,3),&vec![None;3]));
    let mut badscale=good.clone();*badscale.last_mut().unwrap()=c(-1.);
    cases.push(selected_case("all_invalid_then_recover",family,&mut baseline,&mut candidate,
        &repeated(&badscale,3),&vec![Some(LaneError::InvalidScale);3]));
    cases.push(selected_case("recovery",family,&mut baseline,&mut candidate,&good,&[None]));
    let mut nonfinite=good.clone();nonfinite[0].re=f64::NAN;
    cases.push(selected_case("nonfinite_neighbor",family,&mut baseline,&mut candidate,
        &[good.clone(),nonfinite,good.clone()].concat(),
        &[None,Some(LaneError::NonFiniteInput{argument:0,component:0}),None]));
    let physical=match family {
        ScalarIntegral::A0=>vec![vec![Complex::new(100.,-1.4),c(1.)],good.clone(),zero],
        ScalarIntegral::B0=>vec![real(&[3.,0.,0.,1.]),
            vec![c(3.),Complex::new(0.7,-0.03),Complex::new(1.4,-0.08),c(1.)],
            real(&[0.,2.,2.,1.]),real(&[7.,0.,0.,1.]),zero],
        ScalarIntegral::C0=>{
            let sub=real(&[1.,2.,3.,5.,7.,11.,1.]);
            let abs=real(&[-1.,-2.,30.,2.,3.,5.,1.]);
            let mut complex_sub=real(&[1.,2.,3.,0.5,0.7,1.4,1.]);
            let mut complex_abs=abs.clone();
            for i in 3..6 {complex_sub[i].im=-0.1;complex_abs[i].im=-0.1;}
            vec![sub,abs,complex_sub,complex_abs,zero]
        },_=>unreachable!(),
    };
    cases.push(selected_case("physical_complex_mixed_branches",family,&mut baseline,&mut candidate,
        &physical.concat(),&vec![None;physical.len()]));
    if family==ScalarIntegral::B0 {
        let mut ci=good.clone();ci[0].im=1.;
        let mut upper=good.clone();upper[1].im=1.;
        let mut cs=good.clone();cs[3].im=1.;
        cases.push(selected_case("diagnostic_neighbors",family,&mut baseline,&mut candidate,
            &[good.clone(),ci,upper,cs,good.clone()].concat(),&[None,
                Some(LaneError::ComplexInvariant{argument:0}),Some(LaneError::UpperHalfPlaneMass{argument:1}),
                Some(LaneError::InvalidScale),None]));
    }
    // A valid dynamic Dual value passed to an ordinary plan must reject the shape.
    let wrong=HyperDual::<Complex<f64>>::new(vec![vec![0],vec![1]]);
    let dual_input=vec![wrong;family.arity()];
    assert!(matches!(baseline.evaluate_hyperdual_batch(&dual_input,1),Err(MasterError::InvalidShape(_))));
    assert!(matches!(candidate.evaluate_hyperdual_batch(&dual_input,1),Err(MasterError::InvalidShape(_))));
    let before=snapshot(&candidate.evaluate_batch(&good,1).unwrap(),1,&[None]);
    let mut cloned=candidate.clone();
    assert_eq!(cloned.backend(),MasterBackend::RustBatch);
    assert_eq!(snapshot(&cloned.evaluate_batch(&good,1).unwrap(),1,&[None]),before);
    assert_eq!(snapshot(&candidate.evaluate_batch(&good,1).unwrap(),1,&[None]),before);
    json!({"family":family.name(),"status":"passed","layout_and_overflow_errors_checked":true,
        "ordinary_dual_adapter_rejected":true,"warm_clone_checked":true,"cases":cases})
}

fn precise_a0(plan: &ExactMasterPlan) -> Vec<Value> {
    let mut results=Vec::new();
    let one=DoubleFloat::from(1.);let zero=DoubleFloat::from(0.);
    let mass=one+one.from_usize(2).pow(80).inv();assert_ne!(mass,one);
    let point=vec![Complex::new(mass,zero),Complex::new(one,zero)];
    let control=unchanged("DoubleFloat_beyond53",plan,zero,
        vec![("three_lanes".into(),repeated(&point,3),vec![None;3]),("empty_reuse".into(),vec![],vec![]),
            ("singleton_recovery".into(),point.clone(),vec![None])]);
    let mut e=plan.instantiate(zero).unwrap().private_select_f64().unwrap();
    let b=e.evaluate_batch(&point,1).unwrap();assert_eq!(b.lane(0).unwrap().uv[0].re,mass);
    results.push(control);
    // A binary64-precision Float is still a distinct numeric type and must not select native.
    let mut f53=plan.instantiate(Float::new(53)).unwrap().private_select_f64().unwrap();
    assert_eq!(f53.backend(),MasterBackend::SymbolicaBatch);
    let p53=vec![Complex::new(Float::with_val(53,2),Float::new(53)),
        Complex::new(Float::with_val(53,1),Float::new(53))];
    snapshot(&f53.evaluate_batch(&p53,1).unwrap(),1,&[None]);
    results.push(unchanged("Float53_is_not_f64",plan,Float::new(53),
        vec![("singleton".into(),p53,vec![None])]));
    for prototype_bits in [128u32,256] {
        let mut cases=Vec::new();
        for precisions in [vec![128u32,256,64],vec![256],vec![],vec![64,128,256]] {
            let mut input=Vec::new();
            for &bits in &precisions {
                let mass=Float::with_val(bits,1)+Float::with_val(bits,2).pow(u64::from(bits-10)).inv();
                assert_ne!(mass,Float::with_val(bits,1));
                input.extend([Complex::new(mass,Float::new(128)),
                    Complex::new(Float::with_val(128,1),Float::new(64))]);
            }
            let mut e=plan.instantiate(Float::new(prototype_bits)).unwrap().private_select_f64().unwrap();
            let batch=e.evaluate_batch(&input,precisions.len()).unwrap();
            for lane in 0..precisions.len() {
                let uv=&batch.lane(lane).unwrap().uv[0];
                assert_eq!(represented(&uv.re),represented(&input[lane*2].re));
                assert_eq!(represented(&uv.im),represented(&input[lane*2].im));
            }
            cases.push((format!("lane_precisions_{precisions:?}"),input,vec![None;precisions.len()]));
        }
        results.push(unchanged(&format!("Float_mixed_prototype{prototype_bits}"),plan,Float::new(prototype_bits),cases));
    }
    results
}

fn dual_controls(family: ScalarIntegral) -> Value {
    let plan=ExactMasterPlan::new_dual(family,HyperDual::<f64>::new(vec![vec![0],vec![1]])).unwrap();
    let values=match family {ScalarIntegral::A0=>vec![2.,1.],ScalarIntegral::B0=>vec![-3.,2.,5.,1.],
        ScalarIntegral::C0=>vec![-1.,-5.,-4.,2.,3.,5.,1.],_=>unreachable!()};
    let seeded:Vec<_>=values.iter().enumerate().flat_map(|(i,&x)|[c(x),c(if i==0 {1.} else {0.})]).collect();
    let constant:Vec<_>=values.iter().flat_map(|&x|[c(x),c(0.)]).collect();
    let mut cases=vec![("seeded_three".into(),repeated(&seeded,3),vec![None;3]),
        ("constant_kinematics".into(),repeated(&constant,3),vec![None;3]),
        ("empty_reuse".into(),vec![],vec![]),("seeded_recovery".into(),seeded.clone(),vec![None])];
    if family==ScalarIntegral::C0 {
        let mut imaginary=seeded.clone();imaginary[1]=Complex::new(0.,1.);
        let mut width=seeded.clone();width[7]=Complex::new(0.,1.);
        let mut gram=seeded.clone();gram[2]=c(-4.);gram[4]=c(-9.);
        cases.push(("invalid_derivative_neighbors".into(),
            [seeded.clone(),imaginary,width,gram,seeded].concat(),
            vec![None,Some(LaneError::UnsupportedDerivativeDomain),Some(LaneError::UnsupportedDerivativeDomain),
                Some(LaneError::UnsupportedDerivativeDomain),None]));
    }
    let wrong=HyperDual::<Complex<f64>>::new(vec![vec![0]]);
    let mut evaluator=plan.instantiate(0_f64).unwrap().private_select_f64().unwrap();
    assert_eq!(evaluator.backend(),MasterBackend::SymbolicaBatch);
    assert!(matches!(evaluator.evaluate_hyperdual_batch(&vec![wrong;family.arity()],1),Err(MasterError::InvalidShape(_))));
    unchanged(&format!("{}_seeded_and_constant_Dual",family.name()),&plan,0_f64,cases)
}

pub fn run() -> Value {
    // Fixture provenance: masters.rs, native_batch.rs and numeric_boundaries.rs;
    // complex A0/B0 points additionally come from oneloopmaster/src/tests.rs.
    let mut selected=Vec::new();let mut untouched=Vec::new();
    for family in [ScalarIntegral::A0,ScalarIntegral::B0,ScalarIntegral::C0] {
        let plan=ExactMasterPlan::new(family).unwrap();
        selected.push(scalar_controls(family,&plan));
        if family==ScalarIntegral::A0 {untouched.extend(precise_a0(&plan));}
    }
    for (family,point) in [(ScalarIntegral::DB0,real(&[-3.,2.,5.,1.])),
        (ScalarIntegral::D0,real(&[-1.,-2.,-3.,-4.,-5.,-6.,2.,3.,4.,5.,1.]))] {
        let plan=ExactMasterPlan::new(family).unwrap();
        let mut bad=point.clone();*bad.last_mut().unwrap()=c(-1.);
        let mut cases=vec![("empty".into(),vec![],vec![]),("singleton".into(),point.clone(),vec![None]),
            ("invalid_neighbor".into(),[point.clone(),bad,point].concat(),vec![None,Some(LaneError::InvalidScale),None])];
        if family==ScalarIntegral::DB0 {cases.push(("scaleless_error".into(),real(&[0.,0.,0.,1.]),
            vec![Some(LaneError::UndefinedScalelessDerivative)]));}
        untouched.push(unchanged("unselected_family",&plan,0_f64,cases));
    }
    let primal=ExactMasterPlan::new_dual(ScalarIntegral::A0,HyperDual::<f64>::new(vec![vec![0]])).unwrap();
    untouched.push(unchanged("primal_only_Dual_shape",&primal,0_f64,
        vec![("singleton".into(),real(&[2.,1.]),vec![None])]));
    for family in [ScalarIntegral::A0,ScalarIntegral::B0,ScalarIntegral::C0] {untouched.push(dual_controls(family));}
    json!({"status":"passed","scope":"untimed private selected f64 master adapter controls; no performance claim",
        "comparison":"all six successful outputs; dimensional abs(delta)/(unit+abs(Symbolica)) <= 1e-10",
        "unchanged_comparison":"exact represented rational, component precision and sign; explicit expected errors",
        "failed_lane_output_policy":"null, never successful zero-valued evidence",
        "selected_families":selected,"unchanged_paths":untouched})
}
