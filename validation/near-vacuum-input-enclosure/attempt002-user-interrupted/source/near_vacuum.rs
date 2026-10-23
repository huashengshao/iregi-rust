//! Finite D0 series and component enclosures in a bounded near-vacuum domain.
//! Polynomial operations, parameter integration, Taylor jets and ball evaluation
//! use Symbolica and Numerica. The ordinary master evaluator is unchanged.

use oneloop::NativeFloat;
use std::sync::Arc;
use symbolica::{
    atom::{Atom, AtomCore},
    domains::{
        atom::AtomField,
        dual::{DualNumberStructure, HyperDual},
        float::{Complex, ComplexBall, Real, RealBall},
        integer::Integer,
        rational::{Q, Rational},
    },
    evaluate::{
        BatchExpressionEvaluator, Dualizer, EvaluationDomain, ExpressionEvaluator, Instruction,
    },
    poly::PolyVariable,
    tensors::matrix::Matrix,
};

pub type Exact = Complex<Rational>;
pub const PHYSICAL_ARGUMENTS: usize = 10; // six invariants, four squared masses
const PREPARED_ARGUMENTS: usize = 11; // normalized invariants/deviations, fixed M

pub fn pow2_minus(bits: u32) -> Rational {
    Rational::from((Integer::from(1), Integer::from(2).pow(u64::from(bits))))
}
pub fn zero() -> Exact {
    Complex::new(Rational::from(0), Rational::from(0))
}
pub fn abs(x: &Rational) -> Rational {
    if x < &Rational::from(0) {
        -x.clone()
    } else {
        x.clone()
    }
}
fn upper_abs(x: &Exact) -> Rational {
    abs(&x.re) + abs(&x.im)
}

/// Explicit error contract. Each component has a natural absolute budget;
/// relative accuracy uses that component's returned complex magnitude.
/// Acceptance is error² <= max(absolute², relative²*|returned|²).
#[derive(Clone)]
pub struct AccuracyContext {
    /// Diagnostic bit target; the explicit budgets below define acceptance.
    pub requested_bits: u32,
    pub absolute_per_component: Vec<Rational>,
    pub relative: Rational,
}
impl AccuracyContext {
    pub fn binary(bits: u32, components: usize) -> Self {
        Self {
            requested_bits: bits,
            absolute_per_component: vec![pow2_minus(bits); components],
            relative: pow2_minus(bits),
        }
    }
    pub(crate) fn validate(&self, components: usize) -> Result<(), String> {
        if self.requested_bits == 0
            || self.absolute_per_component.len() != components
            || self
                .absolute_per_component
                .iter()
                .any(|x| x <= &Rational::from(0))
            || self.relative < Rational::from(0)
        {
            return Err("invalid requested accuracy context".into());
        }
        Ok(())
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Status {
    Success,
    InvalidInput(String),
    OutsideAnalyticDomain,
    UncertifiedComponent(usize),
    NonFiniteOutput,
}
#[derive(Clone, Debug)]
pub struct ComponentBound {
    pub truncation: Rational,
    pub real_lower: Rational,
    pub real_upper: Rational,
    pub imaginary_lower: Rational,
    pub imaginary_upper: Rational,
    pub maximum_error_squared: Rational,
    pub allowed_error_squared: Rational,
}
pub struct Lane<T: NativeFloat> {
    pub status: Status,
    // Rejected lanes deliberately expose no coefficients.
    pub values: Option<Vec<Complex<T>>>,
    pub bounds: Vec<ComponentBound>,
    pub rho: Option<Rational>,
}
#[derive(Clone, Debug, Default)]
pub struct Execution {
    pub input_rows: usize,
    pub active_rows: usize,
    pub numeric_batch_calls: usize,
    pub enclosure_batch_calls: usize,
    pub tail_batch_calls: usize,
    pub estimated_exported_instruction_lane_visits: usize,
}

#[derive(Clone)]
pub struct NearVacuumPlan {
    pub order: usize,
    pub shape: Vec<Vec<usize>>,
    pub integrated_polynomial: Atom,
    pub instructions: usize,
    exact: ExpressionEvaluator<Exact>,
    tail: ExpressionEvaluator<Exact>,
}

fn checked_program(exact: &ExpressionEvaluator<Exact>) -> Result<usize, String> {
    let exported = exact.export_instructions();
    if !exported.sub_evaluators.is_empty()
        || !exported.constant_functions.is_empty()
        || exported.instructions.iter().any(|instruction| {
            !matches!(
                instruction,
                Instruction::Add(..)
                    | Instruction::Mul(..)
                    | Instruction::Pow(..)
                    | Instruction::Assign(..)
            )
        })
    {
        return Err(
            "certificate program contains an operation outside certified rational arithmetic"
                .into(),
        );
    }
    if exported.instructions.len() > 500_000 {
        return Err("near-vacuum program exceeds the 500000-instruction preparation limit".into());
    }
    Ok(exported.instructions.len())
}

fn compile(
    expression: &Atom,
    parameters: &[Atom],
    shape: &[Vec<usize>],
) -> Result<ExpressionEvaluator<Exact>, String> {
    let exact = expression
        .evaluator(parameters)
        .direct_translation(true)
        .horner_iterations(0)
        .cores(1)
        .build()
        .map_err(|e| e.to_string())?;
    let exact = if shape.len() == 1 {
        exact
    } else {
        exact.vectorize(&Dualizer::new(
            HyperDual::<Exact>::new(shape.to_vec()),
            Vec::new(),
        ))?
    };
    checked_program(&exact)?;
    Ok(exact)
}

impl NearVacuumPlan {
    pub(crate) fn validate_shape(shape: &[Vec<usize>]) -> Result<(), String> {
        if shape.is_empty()
            || shape.len() > 32
            || shape[0].iter().any(|&n| n != 0)
            || shape.iter().any(|x| {
                x.len() != shape[0].len()
                    || x.iter()
                        .try_fold(0usize, |sum, &n| sum.checked_add(n))
                        .is_none_or(|n| n > 4)
            })
        {
            return Err("invalid or oversized near-vacuum Dual shape".into());
        }
        for (i, component) in shape.iter().enumerate() {
            if shape[..i].contains(component) {
                return Err("duplicate Dual component".into());
            }
            for axis in 0..component.len() {
                if component[axis] > 0 {
                    let mut parent = component.clone();
                    parent[axis] -= 1;
                    if !shape.contains(&parent) {
                        return Err("Dual shape is not ancestor-closed".into());
                    }
                }
            }
        }
        Ok(())
    }

    pub fn from_dual<D: DualNumberStructure>(order: usize, dual: &D) -> Result<Self, String> {
        Self::new(order, dual.get_shape().iter().map(|x| x.to_vec()).collect())
    }

    pub fn new(order: usize, shape: Vec<Vec<usize>>) -> Result<Self, String> {
        if ![2, 4].contains(&order) {
            return Err("near-vacuum series supports only orders two and four".into());
        }
        Self::validate_shape(&shape)?;
        let parameters: Vec<_> = (0..PREPARED_ARGUMENTS)
            .map(|i| Atom::var(symbolica::symbol!(format!("iregi_near_vacuum::p{i}"))))
            .collect();
        let cube_symbols: Vec<_> = (0..3)
            .map(|i| symbolica::symbol!(format!("iregi_near_vacuum::u{i}")))
            .collect();
        let cube: Vec<_> = cube_symbols.iter().copied().map(Atom::var).collect();
        let mut remaining = Atom::num(1);
        let mut simplex = Vec::new();
        for coordinate in &cube {
            simplex.push(&remaining * coordinate);
            remaining *= Atom::num(1) - coordinate;
        }
        simplex.push(remaining);
        let field = AtomField {
            statistical_zero_test: false,
            cancel_check_on_division: false,
            custom_normalization: None,
        };
        let jacobian = Matrix::from_nested_vec(
            simplex[..3]
                .iter()
                .map(|coordinate| {
                    cube_symbols
                        .iter()
                        .map(|&variable| coordinate.derivative(variable))
                        .collect()
                })
                .collect(),
            field,
        )
        .map_err(|e| format!("Jacobian construction: {e:?}"))?
        .det()
        .map_err(|e| format!("Jacobian: {e:?}"))?;
        let mut deviation: Atom = (0..4).map(|i| &parameters[6 + i] * &simplex[i]).sum();
        for (i, (a, b)) in [(0, 1), (1, 2), (2, 3), (0, 3), (0, 2), (1, 3)]
            .into_iter()
            .enumerate()
        {
            deviation -= &parameters[i] * &simplex[a] * &simplex[b];
        }
        let lambda_symbol = symbolica::symbol!("iregi_near_vacuum::lambda");
        let lambda = Atom::var(lambda_symbol);
        let series = (Atom::num(1) / (Atom::num(1) + &lambda * deviation).pow(2))
            .series(lambda_symbol, 0, order as u32)
            .map_err(|e| e.to_string())?
            .to_atom()
            .replace(lambda_symbol)
            .with(Atom::num(1));
        // Exact rational coefficients avoid expression-coefficient swell.
        // Physical parameters follow the three cube variables in Symbolica's
        // variable map and remain variables after definite integration.
        let variables = Arc::new(
            cube.iter()
                .cloned()
                .map(PolyVariable::try_from)
                .collect::<Result<Vec<_>, _>>()?,
        );
        let mut polynomial = (series * jacobian)
            .try_to_polynomial::<_, u16>(&Q, Some(variables))
            .map_err(|e| e.to_string())?;
        // N4 in the complete ten-parameter basis has 103243 cube-expanded
        // monomials before exact integration reduces it to 1001 terms.
        if polynomial.nterms() > 150_000 {
            return Err("near-vacuum parameter polynomial exceeds term limit".into());
        }
        for variable in 0..3 {
            let antiderivative = polynomial.integrate(variable);
            polynomial = &antiderivative.replace(variable, &Rational::from(1))
                - &antiderivative.replace(variable, &Rational::from(0));
        }
        if (0..3).any(|coordinate| polynomial.degree(coordinate) != 0) {
            return Err("parameter integration left coordinates".into());
        }
        let integrated_polynomial = polynomial.to_expression() / parameters[10].pow(2);
        let exact = compile(&integrated_polynomial, &parameters, &shape)?;
        let instructions = checked_program(&exact)?;
        let b = Atom::var(symbolica::symbol!("iregi_near_vacuum::bound"));
        let l = Atom::var(symbolica::symbol!("iregi_near_vacuum::scale_lower"));
        let one_minus = Atom::num(1) - &b;
        let tail = b.pow((order + 1) as i64)
            * (Atom::num(order + 1) / &one_minus + Atom::num(1) / one_minus.pow(2))
            / (Atom::num(6) * l.pow(2));
        let tail = compile(&tail, &[b, l], &shape)?;
        Ok(Self {
            order,
            shape,
            integrated_polynomial,
            instructions,
            exact,
            tail,
        })
    }

    pub fn instantiate<T: NativeFloat>(&self, prototype: T) -> Workspace<T>
    where
        Complex<T>: EvaluationDomain,
    {
        let bits = prototype.get_precision();
        Workspace {
            plan: self.clone(),
            prototype: prototype.clone(),
            numeric: self
                .exact
                .clone()
                .map_coeff_with_prec(
                    &|x| {
                        Complex::new(
                            prototype.from_rational(&x.re),
                            prototype.from_rational(&x.im),
                        )
                    },
                    bits,
                )
                .into_batch_evaluator(),
            enclosure: self
                .exact
                .clone()
                .map_coeff_with_prec(
                    &|x| ComplexBall::from_rational_ball(x, &Rational::from(0), bits),
                    bits,
                )
                .into_batch_evaluator(),
            tail: self
                .tail
                .clone()
                .map_coeff_with_prec(
                    &|x| {
                        assert_eq!(x.im, Rational::from(0));
                        RealBall::from_rational_bounds(&x.re, &x.re, bits)
                    },
                    bits,
                )
                .into_batch_evaluator(),
            execution: Execution::default(),
        }
    }
}

pub struct Workspace<T: NativeFloat> {
    plan: NearVacuumPlan,
    prototype: T,
    numeric: BatchExpressionEvaluator<Complex<T>>,
    enclosure: BatchExpressionEvaluator<ComplexBall>,
    tail: BatchExpressionEvaluator<RealBall>,
    pub execution: Execution,
}

/// Experimental side input enclosing the intended physical input component.
/// It must contain the separately supplied represented numeric component.
#[derive(Clone, Debug)]
pub struct InputRectangle {
    pub real_lower: Rational,
    pub real_upper: Rational,
    pub imaginary_lower: Rational,
    pub imaginary_upper: Rational,
}

impl InputRectangle {
    pub fn from_ball(ball: &ComplexBall) -> Option<Self> {
        Some(Self {
            real_lower: ball.re.lower_bound().exact_rational()?,
            real_upper: ball.re.upper_bound().exact_rational()?,
            imaginary_lower: ball.im.lower_bound().exact_rational()?,
            imaginary_upper: ball.im.upper_bound().exact_rational()?,
        })
    }

    pub fn exact(point: &Exact) -> Self {
        Self {
            real_lower: point.re.clone(),
            real_upper: point.re.clone(),
            imaginary_lower: point.im.clone(),
            imaginary_upper: point.im.clone(),
        }
    }

    pub fn contains(&self, point: &Exact) -> bool {
        self.real_lower <= point.re && point.re <= self.real_upper
            && self.imaginary_lower <= point.im && point.im <= self.imaginary_upper
    }

    fn ball(&self, bits: u32) -> ComplexBall {
        Complex::new(
            RealBall::from_rational_bounds(&self.real_lower, &self.real_upper, bits),
            RealBall::from_rational_bounds(&self.imaginary_lower, &self.imaginary_upper, bits),
        )
    }
}

fn ball_l1_upper(value: &ComplexBall) -> Option<Rational> {
    (value.re.norm() + value.im.norm()).upper_bound().exact_rational()
}

impl<T: NativeFloat> Workspace<T>
where
    Complex<T>: EvaluationDomain,
{
    pub fn evaluate_batch(
        &mut self,
        input: &[Complex<T>],
        rows: usize,
        accuracy: &AccuracyContext,
    ) -> Result<Vec<Lane<T>>, String> {
        self.evaluate_batch_impl(input, rows, accuracy, None)
    }

    /// Private experiment: propagate supplied physical-input rectangles through
    /// both the retained Symbolica polynomial and the complete Taylor tail.
    pub fn evaluate_batch_enclosed(
        &mut self,
        input: &[Complex<T>],
        rows: usize,
        accuracy: &AccuracyContext,
        input_bounds: &[InputRectangle],
    ) -> Result<Vec<Lane<T>>, String> {
        self.evaluate_batch_impl(input, rows, accuracy, Some(input_bounds))
    }

    fn evaluate_batch_impl(
        &mut self,
        input: &[Complex<T>],
        rows: usize,
        accuracy: &AccuracyContext,
        input_bounds: Option<&[InputRectangle]>,
    ) -> Result<Vec<Lane<T>>, String> {
        let components = self.plan.shape.len();
        accuracy.validate(components)?;
        if input.len()
            != rows
                .checked_mul(PHYSICAL_ARGUMENTS * components)
                .ok_or("batch size overflow")?
        {
            return Err("invalid row-major input length".into());
        }
        if input_bounds.is_some_and(|bounds| bounds.len() != input.len()) {
            return Err("invalid physical-input enclosure length".into());
        }
        self.execution = Execution {
            input_rows: rows,
            ..Execution::default()
        };
        let mut results: Vec<_> = (0..rows)
            .map(|_| Lane {
                status: Status::OutsideAnalyticDomain,
                values: None,
                bounds: Vec::new(),
                rho: None,
            })
            .collect();
        let mut active = Vec::new();
        let mut exact_arguments = Vec::new();
        let mut enclosed_arguments = Vec::new();
        let mut bounds_input = Vec::new();
        let bits = self.prototype.get_precision();
        for (lane, row) in input
            .chunks_exact(PHYSICAL_ARGUMENTS * components)
            .enumerate()
        {
            let point: Option<Vec<_>> = row
                .iter()
                .map(|v| Some(Complex::new(v.re.exact_rational()?, v.im.exact_rational()?)))
                .collect();
            let Some(point) = point else {
                results[lane].status =
                    Status::InvalidInput("nonfinite or nonexact-representable input".into());
                continue;
            };
            if (0..6)
                .any(|i| (0..components).any(|j| point[i * components + j].im != Rational::from(0)))
                || (6..10).any(|i| {
                    point[i * components].re <= Rational::from(0)
                        || point[i * components].im > Rational::from(0)
                })
                || (6..10).any(|i| {
                    point[i * components].im == Rational::from(0)
                        && (1..components)
                            .any(|j| point[i * components + j].im != Rational::from(0))
                })
            {
                results[lane].status =
                    Status::InvalidInput("physical invariant/mass input domain".into());
                continue;
            }
            let supplied = input_bounds.map(|bounds| {
                let width = PHYSICAL_ARGUMENTS * components;
                &bounds[lane * width..(lane + 1) * width]
            });
            if let Some(bounds) = supplied {
                if bounds.iter().zip(&point).any(|(bound, value)| !bound.contains(value)) {
                    results[lane].status = Status::InvalidInput(
                        "input rectangle is unordered or omits its represented component".into(),
                    );
                    continue;
                }
                let zero = Rational::from(0);
                if (0..6).any(|i| (0..components).any(|j| {
                    let bound = &bounds[i * components + j];
                    bound.imaginary_lower != zero || bound.imaginary_upper != zero
                })) || (6..10).any(|i| {
                    let bound = &bounds[i * components];
                    bound.real_lower <= zero || bound.imaginary_upper > zero
                }) || (6..10).any(|i| {
                    bounds[i * components].imaginary_upper == zero
                        && (1..components).any(|j| {
                            let bound = &bounds[i * components + j];
                            bound.imaginary_lower != zero || bound.imaginary_upper != zero
                        })
                }) {
                    results[lane].status = Status::InvalidInput(
                        "physical invariant/mass enclosure domain".into(),
                    );
                    continue;
                }
            }
            let mass = point[6 * components].clone();
            let lower = abs(&mass.re).max(abs(&mass.im));
            let physical_balls = supplied.map(|bounds| {
                bounds.iter().map(|bound| bound.ball(bits)).collect::<Vec<_>>()
            });
            let reference_ball = ComplexBall::from_rational_ball(&mass, &Rational::from(0), bits);
            let mut envelope = Vec::new();
            for component in 0..components {
                if let Some(balls) = &physical_balls {
                    let sigma = (0..6)
                        .map(|i| ball_l1_upper(&balls[i * components + component]))
                        .collect::<Option<Vec<_>>>();
                    let mu = (6..10).map(|i| {
                        let value = &balls[i * components + component];
                        if component == 0 {
                            ball_l1_upper(&(value - &reference_ball))
                        } else {
                            ball_l1_upper(value)
                        }
                    }).collect::<Option<Vec<_>>>();
                    let (Some(sigma), Some(mu)) = (sigma, mu) else {
                        break;
                    };
                    envelope.push((mu.into_iter().max().unwrap()
                        + Rational::from((3, 8)) * sigma.into_iter().max().unwrap()) / &lower);
                    continue;
                }
                let sigma = (0..6)
                    .map(|i| upper_abs(&point[i * components + component]))
                    .max()
                    .unwrap();
                let mu = (6..10)
                    .map(|i| {
                        upper_abs(
                            &(&point[i * components + component]
                                - if component == 0 { mass.clone() } else { zero() }),
                        )
                    })
                    .max()
                    .unwrap();
                envelope.push((mu + Rational::from((3, 8)) * sigma) / &lower);
            }
            if envelope.len() != components {
                results[lane].status = Status::NonFiniteOutput;
                continue;
            }
            results[lane].rho = Some(envelope[0].clone());
            if envelope[0] > Rational::from((1, 4)) {
                continue;
            }
            for argument in 0..PHYSICAL_ARGUMENTS {
                for component in 0..components {
                    let mut value = point[argument * components + component].clone();
                    if argument >= 6 && component == 0 {
                        value -= &mass;
                    }
                    exact_arguments.push(value / &mass);
                }
            }
            exact_arguments.extend(
                (0..components).map(|component| if component == 0 { mass.clone() } else { zero() }),
            );
            if let Some(balls) = physical_balls {
                for argument in 0..PHYSICAL_ARGUMENTS {
                    for component in 0..components {
                        let mut value = balls[argument * components + component].clone();
                        if argument >= 6 && component == 0 {
                            value -= &reference_ball;
                        }
                        enclosed_arguments.push(value / &reference_ball);
                    }
                }
                enclosed_arguments.extend((0..components).map(|component| {
                    if component == 0 { reference_ball.clone() }
                    else { ComplexBall::from_rational_ball(&zero(), &Rational::from(0), bits) }
                }));
            }
            bounds_input.extend(envelope);
            bounds_input.extend((0..components).map(|component| {
                if component == 0 {
                    lower.clone()
                } else {
                    Rational::from(0)
                }
            }));
            active.push(lane);
        }
        let count = active.len();
        self.execution.active_rows = count;
        if count == 0 {
            return Ok(results);
        }
        let numeric_input: Vec<_> = exact_arguments
            .iter()
            .map(|x| {
                Complex::new(
                    self.prototype.from_rational(&x.re),
                    self.prototype.from_rational(&x.im),
                )
            })
            .collect();
        let ball_input: Vec<_> = if input_bounds.is_some() {
            enclosed_arguments
        } else { exact_arguments
            .iter()
            .map(|x| ComplexBall::from_rational_ball(x, &Rational::from(0), bits))
            .collect() };
        let mut numeric_output =
            vec![Complex::new(self.prototype.zero(), self.prototype.zero()); count * components];
        let mut ball_output =
            vec![
                ComplexBall::from_rational_ball(&zero(), &Rational::from(0), bits);
                count * components
            ];
        let bound_inputs: Vec<_> = bounds_input
            .iter()
            .map(|x| RealBall::from_rational_bounds(x, x, bits))
            .collect();
        let mut tails =
            vec![
                RealBall::from_rational_bounds(&Rational::from(0), &Rational::from(0), bits);
                count * components
            ];
        self.numeric
            .evaluate_batch(&numeric_input, &mut numeric_output, count)
            .map_err(|e| e.to_string())?;
        self.execution.numeric_batch_calls = 1;
        self.enclosure
            .evaluate_batch(&ball_input, &mut ball_output, count)
            .map_err(|e| e.to_string())?;
        self.execution.enclosure_batch_calls = 1;
        self.tail
            .evaluate_batch(&bound_inputs, &mut tails, count)
            .map_err(|e| e.to_string())?;
        self.execution.tail_batch_calls = 1;
        self.execution.estimated_exported_instruction_lane_visits = self.plan.instructions * count;
        for (compact, lane) in active.into_iter().enumerate() {
            results[lane].status = Status::Success;
            for component in 0..components {
                let index = compact * components + component;
                let Some(tail) = tails[index].upper_bound().exact_rational() else {
                    results[lane].status = Status::NonFiniteOutput;
                    break;
                };
                if tail < Rational::from(0) {
                    return Err("positive tail program returned an invalid bound".into());
                }
                let value = &numeric_output[index];
                let ball = &ball_output[index];
                let raw = || -> Option<_> {
                    Some((
                        value.re.exact_rational()?,
                        value.im.exact_rational()?,
                        ball.re.lower_bound().exact_rational()?,
                        ball.re.upper_bound().exact_rational()?,
                        ball.im.lower_bound().exact_rational()?,
                        ball.im.upper_bound().exact_rational()?,
                    ))
                };
                let Some((re, im, rl, ru, il, iu)) = raw() else {
                    results[lane].status = Status::NonFiniteOutput;
                    break;
                };
                let rl = rl - &tail;
                let ru = ru + &tail;
                let il = il - &tail;
                let iu = iu + &tail;
                let real_distance = abs(&(&re - &rl)).max(abs(&(&re - &ru)));
                let imaginary_distance = abs(&(&im - &il)).max(abs(&(&im - &iu)));
                let maximum_error_squared = real_distance.pow(2) + imaginary_distance.pow(2);
                let allowed_error_squared = accuracy.absolute_per_component[component]
                    .pow(2)
                    .max(accuracy.relative.pow(2) * (re.pow(2) + im.pow(2)));
                if maximum_error_squared > allowed_error_squared
                    && results[lane].status == Status::Success
                {
                    results[lane].status = Status::UncertifiedComponent(component);
                }
                results[lane].bounds.push(ComponentBound {
                    truncation: tail,
                    real_lower: rl,
                    real_upper: ru,
                    imaginary_lower: il,
                    imaginary_upper: iu,
                    maximum_error_squared,
                    allowed_error_squared,
                });
            }
            if results[lane].status == Status::Success {
                results[lane].values =
                    Some(numeric_output[compact * components..(compact + 1) * components].to_vec());
            }
        }
        Ok(results)
    }
}
