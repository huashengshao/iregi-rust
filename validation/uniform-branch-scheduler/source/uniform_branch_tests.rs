//! Unexecuted private qualification source for the uniform-branch scheduler.
//! Loaded only by the separately instrumented private batch.rs; not production.
use super::*;
use std::cell::RefCell;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Kind { IfElse, Goto, Label, Join, External, Other }

#[derive(Clone, Debug, PartialEq, Eq)]
struct Step { pc: usize, kind: Kind, callers: usize, active: usize, active_lanes: Vec<usize>, instruction: String }

#[derive(Clone, Copy, Debug)]
struct Jump { pc: usize, target: usize, kind: Kind, callers: usize }

#[derive(Default, Debug)]
struct Trace { steps: Vec<Step>, jumps: Vec<Jump> }

thread_local! {
    static TRACE: RefCell<Option<Trace>> = const { RefCell::new(None) };
}

fn kind(instruction: &Instr) -> Kind {
    match instruction {
        Instr::IfElse(..) => Kind::IfElse,
        Instr::Goto(..) => Kind::Goto,
        Instr::Label(..) => Kind::Label,
        Instr::Join(..) => Kind::Join,
        Instr::ExternalFun(..) => Kind::External,
        _ => Kind::Other,
    }
}

pub(in crate::evaluate) fn record_step(pc: usize, instruction: &Instr, callers: usize, active: &[usize]) {
    TRACE.with(|trace| {
        if let Some(trace) = trace.borrow_mut().as_mut() {
            trace.steps.push(Step { pc, kind: kind(instruction), callers, active: active.len(), active_lanes: active.to_vec(), instruction: format!("{instruction:?}") });
        }
    });
}

pub(super) fn record_jump(pc: usize, target: usize, instruction: &Instr, callers: usize) {
    TRACE.with(|trace| {
        if let Some(trace) = trace.borrow_mut().as_mut() {
            trace.jumps.push(Jump { pc, target, kind: kind(instruction), callers });
        }
    });
}

fn traced<R>(operation: impl FnOnce() -> R) -> (R, Trace) {
    TRACE.with(|trace| assert!(trace.borrow_mut().replace(Trace::default()).is_none()));
    let result = operation();
    let trace = TRACE.with(|trace| trace.borrow_mut().take().unwrap());
    (result, trace)
}

fn active_trace(trace: &Trace) -> Vec<Step> {
    // Empty-control dispatch is intentionally skipped. Every instruction with
    // actual caller lanes must retain descriptor, order and lane membership.
    trace.steps.iter().filter(|s| s.active != 0).cloned().collect()
}

fn nested_program() -> ExpressionEvaluator<f64> {
    // This is the existing Symbolica CSE branch fixture, with two joins at the
    // inner merge. Raw construction tests the scheduler without simplification.
    let instructions = vec![
        Instr::IfElse(0, Label(0)),
        Instr::IfElse(1, Label(1)),
        Instr::Add(5, vec![2, 2]),
        Instr::Goto(Label(2)),
        Instr::Label(Label(1)),
        Instr::Mul(8, vec![2, 2]),
        Instr::Label(Label(2)),
        Instr::Join(10, 1, 5, 8),
        Instr::Join(11, 1, 5, 8),
        Instr::Mul(12, vec![2, 2]),
        Instr::Add(13, vec![10, 11, 12]),
        Instr::Goto(Label(3)),
        Instr::Label(Label(0)),
        Instr::Mul(16, vec![2, 2]),
        Instr::Label(Label(3)),
        Instr::Join(18, 0, 13, 16),
    ];
    let mut evaluator = ExpressionEvaluator {
        stack: vec![0.; 20],
        param_count: 3,
        reserved_indices: 3,
        instructions: instructions.into_iter().map(|i| (i, ComplexPhase::Any)).collect(),
        result_indices: vec![18],
        external_fns: vec![],
        settings: OptimizationSettings::default(),
    };
    evaluator.fix_labels();
    evaluator
}

fn compare_scalar_f64(batch: &mut BatchExpressionEvaluator<f64>, scalar: &mut ExpressionEvaluator<f64>, input: &[f64], rows: usize) -> Trace {
    let mut output = vec![f64::NAN; rows];
    let (result, trace) = traced(|| batch.evaluate_batch(input, &mut output, rows));
    result.unwrap();
    let mut frozen = scalar.clone().into_frozen_batch_evaluator();
    let mut original_output = vec![f64::NAN; rows];
    let (original_result, original_trace) = traced(|| frozen.evaluate_batch(input, &mut original_output, rows));
    original_result.unwrap();
    assert_eq!(active_trace(&trace), active_trace(&original_trace));
    for (actual, original) in output.iter().zip(original_output) {
        assert!(actual.is_finite() && original.is_finite());
        assert_eq!(actual.to_bits(), original.to_bits());
    }
    for (row, actual) in input.chunks_exact(3).zip(output) {
        let expected = scalar.evaluate_single(row);
        assert_eq!(actual.to_bits(), expected.to_bits());
    }
    trace
}

#[test]
fn uniform_nested_paths_skip_dispatch_and_keep_destination_labels_and_joins() {
    let mut scalar = nested_program();
    let mut batch = scalar.clone().into_batch_evaluator();
    for rows in [2, 5, 33, 3] {
        let input = (0..rows).flat_map(|i| [0., 1., i as f64 + 2.]).collect::<Vec<_>>();
        let trace = compare_scalar_f64(&mut batch, &mut scalar, &input, rows);
        assert_eq!(trace.steps.iter().map(|s| s.pc).collect::<Vec<_>>(), [0, 12, 13, 14, 15]);
        assert_eq!(trace.steps.iter().filter(|s| s.kind == Kind::IfElse).count(), 1);
        assert_eq!(trace.steps.iter().filter(|s| s.kind == Kind::Goto).count(), 0);
        assert_eq!(trace.steps.iter().filter(|s| s.kind == Kind::Label).count(), 2);
        assert_eq!(trace.steps.iter().filter(|s| s.kind == Kind::Join).count(), 1);
        assert_eq!(trace.jumps.len(), 1);
        assert_eq!((trace.jumps[0].pc, trace.jumps[0].target, trace.jumps[0].kind, trace.jumps[0].callers), (0, 12, Kind::IfElse, rows));
        for d in [0., 1.] {
            let input = (0..rows).flat_map(|i| [1., d, i as f64 + 2.]).collect::<Vec<_>>();
            let trace = compare_scalar_f64(&mut batch, &mut scalar, &input, rows);
            assert_eq!(trace.steps.len(), 12);
            assert_eq!(trace.steps.iter().filter(|s| s.kind == Kind::Join).count(), 3);
            assert!(trace.jumps.iter().any(|j| j.pc == 11 && j.target == 14 && j.kind == Kind::Goto));
            assert!(!trace.steps.iter().any(|s| s.pc == 12 || s.pc == 13));
        }
    }
}

#[test]
fn prior_inactive_lanes_forbid_jumps_and_rejoin_in_original_order() {
    let mut scalar = nested_program();
    let mut batch = scalar.clone().into_batch_evaluator();
    for rows in [0, 1, 7, 32, 3, 33, 2] {
        let input = (0..rows).flat_map(|i| [if i % 2 == 0 { 1. } else { 0. }, if i % 3 == 0 { 1. } else { 0. }, i as f64 + 2.]).collect::<Vec<_>>();
        let trace = compare_scalar_f64(&mut batch, &mut scalar, &input, rows);
        if rows <= 1 {
            assert!(trace.steps.is_empty());
            assert!(trace.jumps.is_empty());
        } else {
            assert!(trace.steps.iter().any(|s| s.pc == 12 && s.kind == Kind::Label));
            assert!(!trace.jumps.iter().any(|j| j.pc == 0 || j.pc == 11));
            assert!(trace.steps.iter().any(|s| s.active < s.callers));
        }
    }
    let mut sentinel = [42.; 3];
    assert!(batch.evaluate_batch(&[1.; 4], &mut sentinel, 3).is_err());
    assert_eq!(sentinel, [42.; 3]);
    let trace = compare_scalar_f64(&mut batch, &mut scalar, &[1., 0., 2., 0., 1., 3.], 2);
    assert!(!trace.steps.is_empty());
}

#[test]
fn inactive_external_continue_advances_pc_on_mixed_parent_lanes() {
    crate::symbol!(
        "uniform_jump_continue::trap",
        eval = EvaluationInfo::new().register(|_: &[f64]| -> f64 {
            panic!("inactive callback must never run")
        })
    );
    let scalar = crate::parse!("if(c,if(d,uniform_jump_continue::trap(x),x+1),x+2)")
        .evaluator(&[crate::parse!("c"), crate::parse!("d"), crate::parse!("x")])
        .direct_translation(true).horner_iterations(0).build().unwrap()
        .map_coeff(&|v| v.re.to_f64());
    let mut evaluator = scalar.clone().into_batch_evaluator();
    let mut frozen = scalar.into_frozen_batch_evaluator();
    let input = [1., 0., 2., 0., 1., 3., 1., 0., 4., 0., 1., 5.];
    let mut output = [0.; 4];
    let (result, trace) = traced(|| evaluator.evaluate_batch(&input, &mut output, 4));
    result.unwrap();
    assert_eq!(output, [3., 5., 5., 7.]);
    let mut old_output = [0.; 4];
    let (old_result, old_trace) = traced(|| frozen.evaluate_batch(&input, &mut old_output, 4));
    old_result.unwrap();
    assert_eq!(output, old_output);
    assert_eq!(active_trace(&trace), active_trace(&old_trace));
    // The parent is mixed; the inner false branch cannot take the new jump.
    // Its ExternalFun must be visited with no active lanes, exercising the
    // existing `continue` that would hang an increment-at-the-end pc loop.
    assert!(trace.steps.iter().any(|s| s.kind == Kind::External && s.active == 0));
}

#[test]
fn shared_subset_callers_may_jump_without_waking_root_inactive_lanes() {
    let exact = crate::parse!("if(g,uniform_jump_subset::body(c,x),x)")
        .evaluator(&[crate::parse!("g"), crate::parse!("c"), crate::parse!("x")])
        .add_function_with_options(
            crate::symbol!("uniform_jump_subset::body"),
            vec![crate::symbol!("b"), crate::symbol!("z")],
            crate::parse!("if(b,1/z,z+1)"),
            FunctionRegistrationOptions::new().inlining(InliningPolicy::Never),
        ).unwrap()
        .direct_translation(true).horner_iterations(0).build().unwrap();
    let mut scalar = exact.map_coeff(&|v| v.re.to_f64());
    let mut batch = scalar.clone().into_batch_evaluator();
    // Five root lanes, only lanes 0 and 3 enter the helper. Its uniformly zero
    // b is permitted to skip 1/z even though its caller list is sparse.
    let input = [1., 0., 0., 0., 1., 2., 0., 1., 3., 1., 0., 0., 0., 1., 5.];
    let trace = compare_scalar_f64(&mut batch, &mut scalar, &input, 5);
    assert!(trace.jumps.iter().any(|j| j.callers == 2 && j.kind == Kind::IfElse));
    assert!(trace.steps.iter().any(|s| s.callers == 2 && s.kind == Kind::Join));
    // Reuse the same helper allocation for a mixed helper and a larger root.
    let input = [1., 1., 2., 0., 1., 0., 1., 0., 0., 1., 1., 4., 0., 1., 0., 1., 0., 2., 0., 1., 0.];
    let trace = compare_scalar_f64(&mut batch, &mut scalar, &input, 7);
    assert!(trace.steps.iter().any(|s| s.callers == 4 && s.active < 4));
}

crate::create_hyperdual_from_components!(UniformStaticDual, [[0], [1], [2]]);

fn exact_dual<D: crate::domains::dual::DualNumberStructure>(shape: D) -> ExpressionEvaluator<Complex<Rational>> {
    crate::parse!("if(c,x*x,x+1)")
        .evaluator(&[crate::parse!("c"), crate::parse!("x")])
        .direct_translation(true).horner_iterations(0).build().unwrap()
        .vectorize(&Dualizer::new(shape, vec![])).unwrap()
}

fn compare_numeric<T: Real + SingleFloat>(mut scalar: ExpressionEvaluator<Complex<T>>, input: Vec<Complex<T>>, rows: usize, components: usize) {
    let mut batch = scalar.clone().into_batch_evaluator();
    let mut output = vec![<Complex<T> as FloatLike>::new_zero(); rows * components];
    let (candidate_result, candidate_trace) = traced(|| batch.evaluate_batch(&input, &mut output, rows));
    candidate_result.unwrap();
    let mut frozen = scalar.clone().into_frozen_batch_evaluator();
    let mut frozen_output = vec![<Complex<T> as FloatLike>::new_zero(); rows * components];
    let (frozen_result, frozen_trace) = traced(|| frozen.evaluate_batch(&input, &mut frozen_output, rows));
    frozen_result.unwrap();
    assert_eq!(active_trace(&candidate_trace), active_trace(&frozen_trace));
    assert!(output.iter().chain(&frozen_output).all(|value| value.re.is_finite() && value.im.is_finite()));
    assert_eq!(output, frozen_output);
    for (actual, original) in output.iter().zip(&frozen_output) {
        assert_eq!(actual.re.get_precision(), original.re.get_precision());
        assert_eq!(actual.im.get_precision(), original.im.get_precision());
        assert_eq!(format!("{actual:?}"), format!("{original:?}"));
    }
    for (row, actual) in input.chunks_exact(2 * components).zip(output.chunks_exact(components)) {
        let mut expected = vec![<Complex<T> as FloatLike>::new_zero(); components];
        scalar.evaluate(row, &mut expected);
        assert!(actual.iter().chain(&expected).all(|value| value.re.is_finite() && value.im.is_finite()), "polynomial fixture produced a nonfinite value");
        assert_eq!(actual, expected);
        for (actual, expected) in actual.iter().zip(expected) {
            assert_eq!(actual.re.get_precision(), expected.re.get_precision());
            assert_eq!(actual.im.get_precision(), expected.im.get_precision());
            // Preserve signed zeros and any domain debug metadata in addition
            // to numerical equality; f64 has a separate explicit bits check.
            assert_eq!(format!("{actual:?}"), format!("{expected:?}"));
        }
    }
}

crate::create_hyperdual_from_components!(UniformMixedStaticDual, [[0,0],[1,0],[0,1],[2,0],[1,1],[0,2],[2,1],[1,2],[2,2]]);

#[test]
fn fixed_and_mixed_precision_static_dynamic_duals_keep_primal_branch() {
    use crate::domains::dual::HyperDual;
    let dynamic = exact_dual(HyperDual::<Complex<Rational>>::new(vec![vec![0], vec![1], vec![2]]));
    let static_graph = exact_dual(UniformStaticDual::<Complex<Rational>>::new_zero());
    for exact in [dynamic, static_graph] {
        for rows in [2, 5, 33] {
            for mixed in [false, true] {
                // Nonzero condition derivatives must not activate a zero
                // primal branch. Input values include a >53-bit displacement.
                let rational = (0..rows).flat_map(|lane| {
                    let c = if mixed && lane % 2 == 0 { 1 } else { 0 };
                    let x = Rational::from(2 + lane as i64) + Rational::from((1, 1_i128 << 80));
                    [Complex::new(Rational::from(c), Rational::from(0)),
                     Complex::new(Rational::from(1), Rational::from(0)),
                     Complex::new(Rational::from(0), Rational::from(0)),
                     Complex::new(x, Rational::from(0)),
                     Complex::new(Rational::from(1), Rational::from(0)),
                     Complex::new(Rational::from(0), Rational::from(0))]
                }).collect::<Vec<_>>();
                compare_numeric(exact.clone().map_coeff(&|v| Complex::new(v.re.to_f64(), v.im.to_f64())), rational.iter().map(|v| Complex::new(v.re.to_f64(), v.im.to_f64())).collect(), rows, 3);
                compare_numeric(exact.clone().map_coeff(&|v| Complex::new(DoubleFloat::from(&v.re), DoubleFloat::from(&v.im))), rational.iter().map(|v| Complex::new(DoubleFloat::from(&v.re), DoubleFloat::from(&v.im))).collect(), rows, 3);
                compare_numeric(exact.clone().map_coeff_with_prec(&|v| Complex::new(v.re.to_multi_prec_float(192), v.im.to_multi_prec_float(192)), 192), rational.iter().enumerate().map(|(i,v)| { let bits = if (i / 6) % 2 == 0 { 80 } else { 192 }; Complex::new(v.re.to_multi_prec_float(bits), v.im.to_multi_prec_float(bits)) }).collect(), rows, 3);
            }
        }
    }
    let mixed_shape = vec![vec![0,0],vec![1,0],vec![0,1],vec![2,0],vec![1,1],vec![0,2],vec![2,1],vec![1,2],vec![2,2]];
    let high_expression = crate::parse!("if(c,(1+x)^5,1/(1+x))");
    let high_exact = high_expression.evaluator(&[crate::parse!("c"),crate::parse!("x")]).direct_translation(true).horner_iterations(0).build().unwrap();
    let dynamic = high_exact.clone().vectorize(&Dualizer::new(HyperDual::<Complex<Rational>>::new(mixed_shape),vec![])).unwrap();
    let static_graph = high_exact.vectorize(&Dualizer::new(UniformMixedStaticDual::<Complex<Rational>>::new_zero(),vec![])).unwrap();
    for exact in [dynamic,static_graph] {
        for rows in [2,5,33] {
            for mixed in [false,true] {
                let mut rational = Vec::new();
                for lane in 0..rows {
                    for component in 0..9 {
                        let c = if component==0 { Rational::from(if mixed && lane%2==0 {1} else {0}) } else { Rational::from((1_i64,component as i64+1)) };
                        rational.push(Complex::new(c,Rational::from(0)));
                    }
                    for component in 0..9 {
                        let x = if component==0 { Rational::from(2+lane as i64)+Rational::from((1,1_i128<<80)) } else { Rational::from((component as i64+1,17_i64)) };
                        rational.push(Complex::new(x,Rational::from(0)));
                    }
                }
                compare_numeric(exact.clone().map_coeff(&|v| Complex::new(v.re.to_f64(),v.im.to_f64())),rational.iter().map(|v|Complex::new(v.re.to_f64(),v.im.to_f64())).collect(),rows,9);
                compare_numeric(exact.clone().map_coeff(&|v|Complex::new(DoubleFloat::from(&v.re),DoubleFloat::from(&v.im))),rational.iter().map(|v|Complex::new(DoubleFloat::from(&v.re),DoubleFloat::from(&v.im))).collect(),rows,9);
                compare_numeric(exact.clone().map_coeff_with_prec(&|v|Complex::new(v.re.to_multi_prec_float(192),v.im.to_multi_prec_float(192)),192),rational.iter().enumerate().map(|(i,v)|{let bits=if(i/18)%2==0{80}else{192};Complex::new(v.re.to_multi_prec_float(bits),v.im.to_multi_prec_float(bits))}).collect(),rows,9);
            }
        }
    }
}

#[test]
fn imaginary_conditions_and_signed_zero_inputs_preserve_bit_patterns() {
    let mut scalar = crate::parse!("if(c,x,-x)")
        .evaluator(&[crate::parse!("c"), crate::parse!("x")])
        .direct_translation(true).horner_iterations(0).build().unwrap()
        .map_coeff(&|v| Complex::new(v.re.to_f64(), v.im.to_f64()));
    let mut batch = scalar.clone().into_batch_evaluator();
    let mut frozen = scalar.clone().into_frozen_batch_evaluator();
    for c in [Complex::new(0., -0.), Complex::new(-0., 0.), Complex::new(0., 1.)] {
        let input = [c, Complex::new(-0., 0.), c, Complex::new(0., -0.)];
        let mut output = [Complex::new(f64::NAN, f64::NAN); 2];
        let (candidate_result, candidate_trace) = traced(|| batch.evaluate_batch(&input, &mut output, 2));
        candidate_result.unwrap();
        let mut old_output = [Complex::new(f64::NAN, f64::NAN); 2];
        let (old_result, old_trace) = traced(|| frozen.evaluate_batch(&input, &mut old_output, 2));
        old_result.unwrap();
        assert_eq!(active_trace(&candidate_trace), active_trace(&old_trace));
        for (actual, original) in output.iter().zip(old_output) {
            assert!(actual.re.is_finite() && actual.im.is_finite() && original.re.is_finite() && original.im.is_finite());
            assert_eq!(actual.re.to_bits(), original.re.to_bits());
            assert_eq!(actual.im.to_bits(), original.im.to_bits());
        }
        for (row, actual) in input.chunks_exact(2).zip(output) {
            let expected = scalar.evaluate_single(row);
            assert_eq!(actual.re.to_bits(), expected.re.to_bits());
            assert_eq!(actual.im.to_bits(), expected.im.to_bits());
        }
    }
}
