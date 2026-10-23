//! Independent exact five-pinch oracle at x=1/2 on the E6 mass contour.
//! No production reduction or scalar-master code is linked or evaluated.
//! Symbolica owns routing polynomials, matrix inversion, series, Jacobians,
//! polynomial integration, and exact rational-function evaluation.

use serde_json::{Value, json};
use std::{error::Error, path::PathBuf, sync::Arc, time::Instant};
use symbolica::{
    atom::{Atom, AtomCore},
    domains::{
        atom::AtomField,
        float::Complex,
        integer::{Integer, Z},
        rational::{Q, Rational},
    },
    id::Replacement,
    poly::PolyVariable,
    tensors::matrix::Matrix,
};

type Exact = Complex<Rational>;
const BOX_ORDER: u32 = 8;
const PENTAGON_ORDER: u32 = 4;
const MAX_PARAMETER_TERMS: usize = 1_000_000;
const METRIC: [i64; 4] = [1, -1, -1, -1];
const BOX_EDGES: [(usize, usize); 6] = [(0, 1), (1, 2), (2, 3), (0, 3), (0, 2), (1, 3)];

fn field() -> AtomField {
    AtomField {
        statistical_zero_test: false,
        cancel_check_on_division: false,
        custom_normalization: None,
    }
}
fn fraction(bits: u64) -> Rational {
    Rational::from((Integer::from(1), Integer::from(2).pow(bits)))
}
fn exact(re: i64, im: i64) -> Exact {
    Complex::new(Rational::from(re), Rational::from(im))
}
fn abs(value: &Rational) -> Rational {
    if value < &Rational::from(0) { -value.clone() } else { value.clone() }
}
fn norm_upper(value: &Exact) -> Rational {
    abs(&value.re) + abs(&value.im)
}
fn exact_constant(expression: &Atom) -> Result<Rational, Box<dyn Error>> {
    let polynomial = expression.try_to_polynomial::<_, u16>(&Q, None)?;
    if !polynomial.is_constant() {
        return Err(format!("expected rational constant: {expression}").into());
    }
    Ok(polynomial.get_constant())
}
fn evaluate_exact(expression: &Atom, parameters: &[Atom], point: &[Exact]) -> Result<Exact, Box<dyn Error>> {
    let variables = Arc::new(parameters.iter().cloned().map(PolyVariable::try_from).collect::<Result<Vec<_>, _>>()?);
    let rational = expression.try_to_rational_polynomial::<_, _, u16>(&Q, &Z, Some(variables.clone()))?;
    if rational.numerator.get_vars_ref() != variables.as_slice()
        || rational.denominator.get_vars_ref() != variables.as_slice()
        || point.len() != variables.len()
    {
        return Err("unexpected variables in exact oracle evaluation".into());
    }
    let map = |value: &Integer| Complex::new(Rational::from(value), Rational::from(0));
    let numerator = rational.numerator.evaluate(map, point);
    let denominator = rational.denominator.evaluate(map, point);
    if denominator == exact(0, 0) {
        return Err("zero exact oracle denominator".into());
    }
    Ok(numerator / denominator)
}
fn encode_complex(value: &Exact) -> Value {
    json!({"real_exact_rational":value.re.to_string(), "imaginary_exact_rational":value.im.to_string()})
}

struct IntegralOracle {
    center: Exact,
    radius: Rational,
    metadata: Value,
}

/// Integrate the chosen face of the original five-parameter Symanzik form.
/// For a box, power=2 and normalization=1. For J5^D4, power=3 and
/// normalization=-2, including (-1)^5 Gamma(5-D/2).
fn integrate_face(
    retained: &[usize],
    distances: &[Vec<Atom>],
    eta: &Rational,
    mass: &Exact,
    power: u32,
    normalization: i64,
    order: u32,
    label: &str,
) -> Result<IntegralOracle, Box<dyn Error>> {
    let started = Instant::now();
    let n = retained.len();
    assert!((n == 4 && power == 2 && normalization == 1)
        || (n == 5 && power == 3 && normalization == -2));
    let z_symbol = symbolica::symbol!(format!("iregi_five_pinch_oracle::{label}_z"));
    let z = Atom::var(z_symbol);
    let parameters: Vec<_> = (0..n)
        .map(|i| Atom::var(symbolica::symbol!(format!("iregi_five_pinch_oracle::{label}_x{i}"))))
        .collect();
    let cube_symbols: Vec<_> = (0..n-1)
        .map(|i| symbolica::symbol!(format!("iregi_five_pinch_oracle::{label}_u{i}")))
        .collect();
    let cube: Vec<_> = cube_symbols.iter().copied().map(Atom::var).collect();

    // On sum(x)=1, F=M-eta*Q, with Q derived from the actual routing.
    let mut q = Atom::num(0);
    for i in 0..n {
        for j in i+1..n {
            q += &parameters[i] * &parameters[j] * &distances[retained[i]][retained[j]];
        }
    }
    let mut remaining = Atom::num(1);
    let mut simplex = Vec::with_capacity(n);
    for coordinate in &cube {
        simplex.push(&remaining * coordinate);
        remaining *= Atom::num(1) - coordinate;
    }
    simplex.push(remaining);
    assert!((simplex.iter().cloned().sum::<Atom>() - 1).expand().is_zero());
    let jacobian = Matrix::from_nested_vec(
        simplex[..n-1].iter().map(|coordinate| {
            cube_symbols.iter().map(|&symbol| coordinate.derivative(symbol)).collect()
        }).collect(), field(),
    ).map_err(|error| format!("Jacobian construction: {error:?}"))?
        .det().map_err(|error| format!("Jacobian determinant: {error:?}"))?;
    let replacements: Vec<_> = parameters.iter().zip(&simplex)
        .map(|(parameter, value)| Replacement::new(parameter.clone(), value.clone())).collect();
    let q_cube = q.replace_multiple(replacements.iter());

    // This identity proves the common bound for every face, including pinch0.
    // Each x_i*(1-x_i) is nonnegative and <=x_i; hence |Q|<=sum_(i>=1)x_i<=1.
    let q_bounded: Atom = parameters.iter().zip(retained).filter(|(_, original)| **original != 0)
        .map(|(coordinate, &original)| Atom::num(METRIC[original-1]) * coordinate * (Atom::num(1)-coordinate))
        .sum();
    assert!((&q_cube - q_bounded.replace_multiple(replacements.iter())).expand().is_zero());

    let series = (Atom::num(normalization) / (Atom::num(1)-&z*&q_cube).pow(i64::from(power)))
        .series(z_symbol, 0, order)?.to_atom();
    let variables = Arc::new(std::iter::once(z.clone()).chain(cube.iter().cloned())
        .map(PolyVariable::try_from).collect::<Result<Vec<_>, _>>()?);
    // Avoid Atom.expand here: Symbolica's Q polynomial conversion handles
    // products/powers directly and avoids the earlier expression blow-up.
    let mut integrated = (&jacobian*series).try_to_polynomial::<_, u16>(&Q, Some(variables))?;
    let parameter_terms = integrated.nterms();
    if parameter_terms > MAX_PARAMETER_TERMS {
        return Err(format!("{label}: parameter polynomial exceeds {MAX_PARAMETER_TERMS} terms").into());
    }
    eprintln!("{label}: series converted, {parameter_terms} terms, {:?}", started.elapsed());
    for variable in 1..n {
        let antiderivative = integrated.integrate(variable);
        integrated = &antiderivative.replace(variable, &Rational::from(1))
            - &antiderivative.replace(variable, &Rational::from(0));
    }
    assert!((1..n).all(|variable| integrated.degree(variable)==0));
    let volume = &integrated.get_constant() / &Rational::from(normalization);
    assert_eq!(volume, if n==4 {Rational::from((1,6))} else {Rational::from((1,24))});
    let mass_symbol = Atom::var(symbolica::symbol!(format!("iregi_five_pinch_oracle::{label}_mass")));
    let center_expression = integrated.to_expression() / mass_symbol.pow(i64::from(power));
    let center = evaluate_exact(&center_expression, &[z.clone(), mass_symbol], &[
        Complex::new(eta.clone(), Rational::from(0))/mass, mass.clone()
    ])?;

    // Positive generating-function tail, integrated with volume(Delta).
    // L=2<=|2-i|; evaluating the exact rational tail does not lose digits.
    let lower_norm = Rational::from(2);
    assert!(mass.re==lower_norm && mass.im==Rational::from(-1));
    let rho = eta/&lower_norm;
    let generating = Atom::num(1)/(Atom::num(1)-&z).pow(i64::from(power));
    let tail = (&generating-generating.series(z_symbol,0,order)?.to_atom()).together();
    let radius_expression = Atom::num(abs(&Rational::from(normalization))*&volume)
        * tail / Atom::num(lower_norm.pow(u64::from(power)));
    let radius = exact_constant(&radius_expression.replace_multiple([
        Replacement::new(z, Atom::num(rho.clone()))
    ].iter()))?;
    assert!(radius>Rational::from(0) && radius<fraction(320));
    eprintln!("{label}: exact integration complete, {:?}",started.elapsed());
    Ok(IntegralOracle {
        metadata:json!({
            "retained_original_propagators":retained,
            "series_order_inclusive":order,
            "denominator_power":power,
            "normalization_factor":normalization,
            "simplex_volume_exact_rational":volume.to_string(),
            "parameter_Q":q.to_string(),
            "cube_jacobian":jacobian.to_string(),
            "expanded_parameter_terms":parameter_terms,
            "integrated_series_in_z":integrated.to_expression().to_string(),
            "z":"eta/M",
            "center":encode_complex(&center),
            "absolute_complex_remainder_bound_exact_rational":radius.to_string(),
            "rho_exact_rational":rho.to_string(),
            "uniform_bound":"|Q|<=1, verified by the face restriction of sum_(i=1..4) sigma_i*x_i*(1-x_i)",
            "tail_proof":"abs(normalization)*volume/L^power times the positive omitted Taylor tail of (1-rho)^(-power), L=2<=|M|",
            "remainder_less_than_2_pow_minus_320":true,
        }), center,radius,
    })
}

fn main() -> Result<(), Box<dyn Error>> {
    let started=Instant::now();
    let mut args=std::env::args_os().skip(1);
    let output=args.next().map(PathBuf::from);
    if args.next().is_some(){return Err("usage: five_pinch_oracle [output.json]".into());}
    let eta=fraction(64);
    let mass=exact(2,-1);
    let t=exact(1,-1);
    let routing:Vec<[Atom;4]>=(0..5).map(|i| std::array::from_fn(|mu| Atom::num(i64::from(i==mu+1)))).collect();
    let distances:Vec<Vec<Atom>>=(0..5).map(|i| (0..5).map(|j| {
        (0..4).map(|mu| Atom::num(METRIC[mu])*(&routing[i][mu]-&routing[j][mu]).pow(2)).sum::<Atom>().expand()
    }).collect()).collect();
    let unit_distances:Vec<Vec<Rational>>=distances.iter().map(|row| row.iter().map(exact_constant).collect()).collect::<Result<_,_>>()?;

    // Independent Cayley solve R*b=1, R_ij=s_ij-m_i^2-m_j^2 at m_i^2=1.
    // The production geometry instead starts from a 4x4 external Gram solve.
    let cayley=Matrix::from_nested_vec((0..5).map(|i| (0..5).map(|j| {
        &eta*&unit_distances[i][j]-Rational::from(2)
    }).collect()).collect(),Q)?;
    let ones=Matrix::from_nested_vec(vec![vec![Rational::from(1)];5],Q)?;
    let inverse=cayley.inv().map_err(|error|format!("Cayley inverse: {error:?}"))?;
    let b_matrix=&inverse*&ones;
    assert_eq!(&cayley*&b_matrix,ones);
    let b:Vec<_>=(0..5).map(|i|b_matrix[(i,0)].clone()).collect();
    let b_sum:Rational=b.iter().sum();
    let expected_denominator=Rational::from(2)+&eta;
    assert_eq!(b_sum,-Rational::from(1)/&expected_denominator);
    assert_eq!(b[0],Rational::from(1)/&expected_denominator);
    assert!(b[1..].iter().all(|value|*value==-Rational::from(1)/(&Rational::from(2)*&expected_denominator)));
    let gram=Matrix::from_nested_vec((1..5).map(|i| (1..5).map(|j| {
        &eta*&(&unit_distances[0][i]+&unit_distances[0][j]-&unit_distances[i][j])
    }).collect()).collect(),Q)?;
    let gram_det=gram.det().map_err(|error|format!("Gram determinant: {error:?}"))?;
    assert_eq!(gram_det,-Rational::from(16)*eta.pow(4));

    let t_symbol=Atom::var(symbolica::symbol!("iregi_five_pinch_oracle::t"));
    let coefficients:Vec<_>=b.iter().map(|value| {
        evaluate_exact(&(Atom::num(value.clone())/(Atom::num(1)-Atom::num(2)*&t_symbol*Atom::num(b_sum.clone()))),
            &[t_symbol.clone()], &[t.clone()])
    }).collect::<Result<_,_>>()?;
    let expected_first=evaluate_exact(&(Atom::num(1)/(Atom::num(expected_denominator)+Atom::num(2)*&t_symbol)),
        &[t_symbol.clone()], &[t.clone()])?;
    assert_eq!(coefficients[0],expected_first);
    assert!(coefficients[1..].iter().all(|value|*value== -coefficients[0].clone()/exact(2,0)));
    // Verify the shifted Cayley relation directly, independently of the update.
    for i in 0..5 {
        let terms:Vec<_>=(0..5).map(|j| Atom::num(&eta*&unit_distances[i][j])-Atom::num(2)*(Atom::num(1)+&t_symbol)).collect();
        let coefficient_symbols:Vec<_>=(0..5).map(|j|Atom::var(symbolica::symbol!(format!("iregi_five_pinch_oracle::c{j}")))).collect();
        let expression:Atom=terms.into_iter().zip(&coefficient_symbols).map(|(term,c)|term*c).sum();
        let params:Vec<_>=std::iter::once(t_symbol.clone()).chain(coefficient_symbols).collect();
        let values:Vec<_>=std::iter::once(t.clone()).chain(coefficients.iter().cloned()).collect();
        assert_eq!(evaluate_exact(&expression,&params,&values)?,exact(1,0));
    }

    let mut boxes=Vec::new();
    let mut box_reports=Vec::new();
    for pinch in 0..5 {
        let retained:Vec<_>=(0..5).filter(|&i|i!=pinch).collect();
        let oracle=integrate_face(&retained,&distances,&eta,&mass,2,1,BOX_ORDER,&format!("pinch{pinch}"))?;
        let mut inputs:Vec<_>=BOX_EDGES.iter().map(|&(i,j)|Complex::new(&eta*&unit_distances[retained[i]][retained[j]],Rational::from(0))).collect();
        inputs.extend((0..4).map(|_|mass.clone()));inputs.push(exact(1,0));
        box_reports.push(json!({"pinch":pinch,"inputs":inputs.iter().map(encode_complex).collect::<Vec<_>>(),"oracle":oracle.metadata}));
        boxes.push(oracle);
    }
    let retained:Vec<_>=(0..5).collect();
    let pentagon=integrate_face(&retained,&distances,&eta,&mass,3,-2,PENTAGON_ORDER,"pentagon4d")?;
    let coefficients_symbols:Vec<_>=(0..5).map(|i|Atom::var(symbolica::symbol!(format!("iregi_five_pinch_oracle::contraction_c{i}")))).collect();
    let box_symbols:Vec<_>=(0..5).map(|i|Atom::var(symbolica::symbol!(format!("iregi_five_pinch_oracle::contraction_d{i}")))).collect();
    let contraction:Atom=coefficients_symbols.iter().zip(&box_symbols).map(|(c,d)|c*d).sum();
    let contraction_parameters:Vec<_>=coefficients_symbols.into_iter().chain(box_symbols).collect();
    let contraction_values:Vec<_>=coefficients.iter().cloned().chain(boxes.iter().map(|value|value.center.clone())).collect();
    let contraction_center=evaluate_exact(&contraction,&contraction_parameters,&contraction_values)?;
    let radius_terms:Vec<_>=coefficients.iter().zip(&boxes).map(|(c,b)|norm_upper(c)*&b.radius).collect();
    let contraction_radius:Rational=radius_terms.iter().sum();
    let difference=&contraction_center-&pentagon.center;
    let distance_squared=difference.re.pow(2)+difference.im.pow(2);
    let combined_radius=&contraction_radius+&pentagon.radius;
    assert!(distance_squared<=combined_radius.pow(2));
    assert!(contraction_radius<fraction(320));
    let mapped_weight=exact(4,-4); // dt/dx at x=1/2, scale=slope=1.
    let mapped_center=&mapped_weight*&contraction_center;
    let mapped_radius=norm_upper(&mapped_weight)*&contraction_radius;

    let report=json!({
        "schema_version":1,"status":"exact_five_pinch_oracle_generated",
        "scope":"Primal independent exact parameter integrals and Cayley geometry; no scalar master, production reduction, or quadrature execution",
        "fixture":{"metric":METRIC,"delta_exact_rational":fraction(32).to_string(),"eta_exact_rational":eta.to_string(),
            "routing":"q0=0; q1..q4=delta times Cartesian basis",
            "x_exact_rational":"1/2","t":encode_complex(&t),"common_shifted_mass_squared":encode_complex(&mass),
            "contour_scale":"1","contour_slope":"1","mu_squared":"1",
            "node_scope":"Exact dyadic contour probe, not an abscissa of the even-order production Gauss rules",
            "doubled_external_gram_determinant_exact_rational":gram_det.to_string()},
        "normalization":{"D0":"+integral_Delta3 F^-2; finite only, zero UV/IR/IR2",
            "J5_D4":"-2 integral_Delta4 F^-3 = sum_i C_i(t) D0_i; finite only",
            "J5_D6":"integral_0^infinity J5_D4(m_squared+t) dt; this oracle evaluates one integrand point only"},
        "geometry":{"method":"Symbolica Matrix<Q> inversion of full Cayley R at unshifted masses; exact R*b=1 and shifted R*C=1 checks",
            "b_exact_rational":b.iter().map(ToString::to_string).collect::<Vec<_>>(),"B_exact_rational":b_sum.to_string(),
            "C_i_at_t":coefficients.iter().map(encode_complex).collect::<Vec<_>>(),
            "closed_identities":"B=-1/(2+eta); b0=1/(2+eta); b1..4=-b0/2; C0=1/(2+eta+2t); C1..4=-C0/2"},
        "boxes":box_reports,"independent_direct_J5_D4":pentagon.metadata,
        "five_box_contraction":{"center":encode_complex(&contraction_center),"absolute_complex_remainder_bound_exact_rational":contraction_radius.to_string(),
            "radius_proof":"sum_i (abs(Re(C_i))+abs(Im(C_i)))*box_radius_i; exact coefficients have no rounding error",
            "difference_to_direct_series_center_squared_exact_rational":distance_squared.to_string(),
            "combined_remainder_bound_exact_rational":combined_radius.to_string(),"independent_enclosures_compatible":true},
        "mapped_integrand_at_x":{"center":encode_complex(&mapped_center),"absolute_complex_remainder_bound_exact_rational":mapped_radius.to_string(),
            "dt_dx":encode_complex(&mapped_weight),"radius_norm_upper":"abs(Re(dt/dx))+abs(Im(dt/dx))=8"},
        "resource_limits":{"box_series_order_inclusive":BOX_ORDER,"pentagon_series_order_inclusive":PENTAGON_ORDER,"maximum_retained_parameter_polynomial_terms":MAX_PARAMETER_TERMS},
        "diagnostic_seconds":started.elapsed().as_secs_f64(),
        "limitations":"Primal only; no general D0/E6 or performance claim. The direct pentagon oracle uses N4 with rigorous radius <2^-320; box series use N8. No inference about quadrature truncation is made."
    });
    let encoded=serde_json::to_string_pretty(&report)?+"\n";
    if let Some(path)=output {std::fs::write(path,&encoded)?;}
    print!("{encoded}");
    Ok(())
}
