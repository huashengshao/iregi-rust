//! Private direct-E6 N2 validation. No production library or dispatch edits.
#[path = "near_vacuum_e6.rs"]
mod candidate;

use candidate::{AccuracyContext, Exact, Lane, NearVacuumPlan, Status, abs, pow2_minus, zero};
use iregi_masters::NativeFloat;
use serde_json::{Value, json};
use std::{error::Error, path::PathBuf, sync::Arc, time::Instant};
use symbolica::{
    atom::{Atom, AtomCore},
    domains::{
        float::{Complex, Float, FloatLike, SingleFloat},
        integer::Integer,
        rational::{Q, Rational},
    },
    poly::PolyVariable,
};

const COMPONENTS: usize = 4;
const EXTERNAL_WIDTH: usize = 16 * COMPONENTS;

fn rational(s: &str) -> Result<Rational, Box<dyn Error>> {
    let (n, d) = s.split_once('/').unwrap_or((s, "1"));
    Ok(Rational::from((n.parse::<Integer>()?, d.parse::<Integer>()?)))
}
fn number(v: &Value) -> Result<Rational, Box<dyn Error>> {
    rational(v.as_str().ok_or("expected exact rational string")?)
}
fn real(v: Rational) -> Exact { Complex::new(v, Rational::from(0)) }

// This adapter explicitly distinguishes physical mu_squared from prepared M.
// It compacts valid physical-scale lanes, then makes one candidate batch call.
fn physical_batch(
    workspace: &mut candidate::Workspace<Float>,
    input: &[Complex<Float>],
    rows: usize,
    accuracy: &AccuracyContext,
) -> Result<Vec<Lane<Float>>, String> {
    accuracy.validate(COMPONENTS)?;
    if input.len() != rows.checked_mul(EXTERNAL_WIDTH).ok_or("size overflow")? {
        return Err("wrong physical sixteen-argument row length".into());
    }
    assert_eq!(candidate::EXTERNAL_ARGUMENTS, 16);
    assert_eq!(candidate::PHYSICAL_ARGUMENTS, 15);
    let mut output: Vec<_> = (0..rows).map(|_| Lane {
        status: Status::InvalidInput("physical scale validation pending".into()),
        values: None, bounds: Vec::new(), rho: None,
    }).collect();
    let mut packed = Vec::new();
    let mut active = Vec::new();
    for (lane, row) in input.chunks_exact(EXTERNAL_WIDTH).enumerate() {
        let scale = &row[15 * COMPONENTS..];
        let exact: Option<Vec<_>> = scale.iter().map(|v|
            Some(Complex::new(v.re.exact_rational()?, v.im.exact_rational()?))
        ).collect();
        let valid = exact.as_ref().is_some_and(|s|
            s[0].re > Rational::from(0) && s[0].im == Rational::from(0)
        );
        if !valid {
            output[lane].status = Status::InvalidInput("invalid physical mu_squared".into());
            continue;
        }
        packed.extend_from_slice(&row[..15 * COMPONENTS]);
        active.push(lane);
    }
    let evaluated = workspace.evaluate_batch(&packed, active.len(), accuracy)?;
    for (lane, value) in active.into_iter().zip(evaluated) { output[lane] = value; }
    Ok(output)
}

fn map(input: &[Exact], prototype: &Float) -> Vec<Complex<Float>> {
    input.iter().map(|v| Complex::new(
        prototype.from_rational(&v.re), prototype.from_rational(&v.im)
    )).collect()
}
fn bound_json(b: &candidate::ComponentBound) -> Value {
    json!({"truncation":b.truncation.to_string(),
        "real_interval":[b.real_lower.to_string(),b.real_upper.to_string()],
        "imaginary_interval":[b.imaginary_lower.to_string(),b.imaginary_upper.to_string()],
        "maximum_error_squared":b.maximum_error_squared.to_string(),
        "allowed_error_squared":b.allowed_error_squared.to_string()})
}
fn lane_json(l: &Lane<Float>) -> Value {
    json!({"status":format!("{:?}",l.status),"rho":l.rho.as_ref().map(ToString::to_string),
        "bounds":l.bounds.iter().map(bound_json).collect::<Vec<_>>(),
        "values":l.values.as_ref().map(|v|v.iter().map(|x|json!({
            "real":x.re.exact_rational().unwrap().to_string(),
            "imaginary":x.im.exact_rational().unwrap().to_string()
        })).collect::<Vec<_>>())})
}

// Independent analytic common-mass identity; no candidate integration reused.
fn common_mass_oracle(seed: &Rational) -> Result<Vec<Rational>, Box<dyn Error>> {
    let symbol = symbolica::symbol!("iregi_direct_e6_identity::t");
    let t = Atom::var(symbol);
    let expression = -Atom::num(1)
        / (Atom::num(24) * (Atom::num(1) + Atom::num(seed.clone()) * &t).pow(2));
    let series = expression.series(symbol, 0, 3)?.to_atom();
    let variables = Arc::new(vec![PolyVariable::try_from(t)?]);
    let polynomial = series.try_to_polynomial::<_, u16>(&Q, Some(variables))?;
    Ok((0..4).map(|degree| polynomial.coefficient(&[degree])
        .unwrap_or_else(|| Rational::from(0))).collect())
}

fn compare(
    lane: &Lane<Float>, centers: &[Rational], radii: &[Rational],
) -> Result<Value, Box<dyn Error>> {
    assert_eq!(lane.status, Status::Success);
    let values = lane.values.as_ref().unwrap();
    assert_eq!(values.len(), COMPONENTS);
    assert_eq!(lane.bounds.len(), COMPONENTS);
    assert_eq!(centers.len(), COMPONENTS);
    assert_eq!(radii.len(), COMPONENTS);
    let mut checks = Vec::new();
    for (i, ((value, center), radius)) in values.iter().zip(centers).zip(radii).enumerate() {
        let actual_re = value.re.exact_rational().ok_or("nonfinite output")?;
        let actual_im = value.im.exact_rational().ok_or("nonfinite output")?;
        let b = &lane.bounds[i];
        let numeric_error_squared = (abs(&(&actual_re-center))+radius).pow(2)
            + abs(&actual_im).pow(2);
        // Bound every point of the candidate rectangle against every possible
        // oracle value; interval intersection alone is not acceptance.
        let rectangle_re = abs(&(&b.real_lower-center)).max(abs(&(&b.real_upper-center))) + radius;
        let rectangle_im = abs(&b.imaginary_lower).max(abs(&b.imaginary_upper));
        let rectangle_error_squared = rectangle_re.pow(2) + rectangle_im.pow(2);
        assert!(numeric_error_squared <= b.allowed_error_squared, "numeric oracle component{i}");
        assert!(rectangle_error_squared <= b.allowed_error_squared, "rectangle oracle component{i}");
        assert!(b.real_lower <= center-radius && b.real_upper >= center+radius);
        assert!(b.imaginary_lower <= Rational::from(0) && b.imaginary_upper >= Rational::from(0));
        checks.push(json!({"component":i,"oracle_center":center.to_string(),
            "oracle_radius":radius.to_string(),"numeric_error_squared_upper":numeric_error_squared.to_string(),
            "rectangle_error_squared_upper":rectangle_error_squared.to_string(),
            "allowed_error_squared":b.allowed_error_squared.to_string()}));
    }
    Ok(json!(checks))
}

fn run() -> Result<(), Box<dyn Error>> {
    let mut args = std::env::args_os().skip(1);
    let oracle_path = PathBuf::from(args.next().ok_or("oracle path required")?);
    let output_path = PathBuf::from(args.next().ok_or("output path required")?);
    assert!(args.next().is_none());
    let oracle: Value = serde_json::from_slice(&std::fs::read(&oracle_path)?)?;
    assert_eq!(oracle["status"], "exact_oracle_generated");
    let entry = oracle["approximations"].as_array().unwrap().iter()
        .find(|v|v["order_in_eta_inclusive"]==4).unwrap();
    let center = number(&entry["center_exact_rational"])?;
    let radius = number(&entry["absolute_remainder_bound_exact_rational"])?;
    assert!(radius > Rational::from(0) && radius < pow2_minus(321));
    let mut tiny = vec![zero(); EXTERNAL_WIDTH];
    for (i, s) in oracle["fixture"]["squared_distances_lexicographic_i_less_than_j"]
        .as_array().unwrap().iter().enumerate() { tiny[i*COMPONENTS] = real(number(s)?); }
    for i in 10..15 { tiny[i*COMPONENTS] = real(Rational::from(1)); }
    tiny[15*COMPONENTS] = real(number(&oracle["fixture"]["mu_squared"])?);
    let mut vacuum = tiny.clone();
    vacuum[..10*COMPONENTS].fill(zero());
    let mut rows = vec![tiny.clone(),tiny.clone(),vacuum.clone(),tiny.clone(),tiny.clone(),tiny.clone(),vacuum.clone(),vacuum,tiny];
    rows[1][15*COMPONENTS] = real(Rational::from(4));
    rows[1][15*COMPONENTS+1] = real(Rational::from(7));
    rows[3][0] = real(Rational::from(1));
    rows[4][10*COMPONENTS].im = Rational::from(1);
    rows[5][15*COMPONENTS] = real(Rational::from(-1));
    for mass in 10..15 {
        rows[6][mass*COMPONENTS+1] = real(Rational::from(1));
        rows[7][mass*COMPONENTS+1] = real(pow2_minus(64));
    }
    rows[8][0].im = pow2_minus(64);
    let names = ["retained_tiny","same_tiny_different_mu_and_mu_jet","vacuum",
        "outside_radius","upper_mass","invalid_mu","vacuum_unit_mass_jet_cubic_rejected",
        "vacuum_small_mass_jet","nonreal_invariant"];
    let shape = vec![vec![0],vec![1],vec![2],vec![3]];
    assert!(NearVacuumPlan::validate_shape(&[vec![0],vec![usize::MAX]]).is_err());
    let prep = Instant::now();
    let plan = NearVacuumPlan::new(2, shape.clone())?;
    let preparation_seconds = prep.elapsed().as_secs_f64();
    let prototype = Float::new(256);
    let exact: Vec<_> = rows.iter().flatten().cloned().collect();
    let input = map(&exact, &prototype);
    for (e,v) in exact.iter().zip(&input) {
        assert_eq!(v.re.exact_rational().as_ref(),Some(&e.re));
        assert_eq!(v.im.exact_rational().as_ref(),Some(&e.im));
    }
    let accuracy = AccuracyContext::binary(128, COMPONENTS);
    let mut workspace = plan.instantiate(prototype.clone());
    assert!(physical_batch(&mut workspace,&[],0,&accuracy)?.is_empty());
    assert_eq!(workspace.execution.numeric_batch_calls,0);
    assert!(physical_batch(&mut workspace,&input[..EXTERNAL_WIDTH-1],1,&accuracy).is_err());
    eprintln!("stage: Float256/request128 nine physical lanes");
    let started = Instant::now();
    let lanes = physical_batch(&mut workspace,&input,rows.len(),&accuracy)?;
    assert_eq!(lanes.len(), rows.len());
    let evaluation_seconds = started.elapsed().as_secs_f64();
    let execution = workspace.execution.clone();
    assert_eq!(execution.input_rows,8); // one invalid physical scale removed
    assert_eq!(execution.active_rows,5);
    assert_eq!(execution.numeric_batch_calls,1);
    assert_eq!(execution.enclosure_batch_calls,1);
    assert_eq!(execution.tail_batch_calls,1);
    for (name,lane) in names.iter().zip(&lanes) { eprintln!("lane {name}: {:?}",lane.status); }
    for i in [0,1,2,7] { assert_eq!(lanes[i].status,Status::Success,"lane{i}"); }
    assert_eq!(lanes[3].status,Status::OutsideAnalyticDomain);
    for i in [4,5,8] { assert!(matches!(lanes[i].status,Status::InvalidInput(_))); }
    assert_eq!(lanes[6].status,Status::UncertifiedComponent(3));
    for i in [3,4,5,6,8] { assert!(lanes[i].values.is_none()); }
    assert_eq!(lanes[6].rho,Some(Rational::from(0)));
    assert_eq!(lanes[6].bounds.len(),COMPONENTS);
    assert!(lanes[6].bounds[3].truncation >= Rational::from((1,6)));
    assert_eq!(lane_json(&lanes[0]),lane_json(&lanes[1]));
    let mut tiny_centers = vec![Rational::from(0); COMPONENTS]; tiny_centers[0]=center;
    let mut tiny_radii = vec![Rational::from(0); COMPONENTS]; tiny_radii[0]=radius;
    let vacuum_centers = common_mass_oracle(&Rational::from(0))?;
    let small_jet_centers = common_mass_oracle(&pow2_minus(64))?;
    let unit_jet_centers = common_mass_oracle(&Rational::from(1))?;
    assert_eq!(unit_jet_centers[3],Rational::from((1,6)));
    let zero_radii = vec![Rational::from(0);COMPONENTS];
    let comparisons = json!({
        "retained_tiny":compare(&lanes[0],&tiny_centers,&tiny_radii)?,
        "scale_transport":compare(&lanes[1],&tiny_centers,&tiny_radii)?,
        "vacuum":compare(&lanes[2],&vacuum_centers,&zero_radii)?,
        "small_mass_jet":compare(&lanes[7],&small_jet_centers,&zero_radii)?,
        "unit_mass_jet_rejected_cubic_exact":unit_jet_centers[3].to_string(),
    });
    let reversed: Vec<_> = input.chunks_exact(EXTERNAL_WIDTH).rev().flatten().cloned().collect();
    let mut other = plan.instantiate(prototype);
    let reversed_lanes = physical_batch(&mut other,&reversed,rows.len(),&accuracy)?;
    for (a,b) in lanes.iter().zip(reversed_lanes.iter().rev()) { assert_eq!(lane_json(a),lane_json(b)); }
    assert!(physical_batch(&mut other,&[],0,&accuracy)?.is_empty());
    let record = json!({"status":"passed_private_direct_e6_n2","scope":"Full15-parameter N2; four native common-mass Taylor components; explicit physical mu_squared adapter; no public/default production path",
        "working_bits":256,"requested_bits":128,"series_order":2,"shape":shape,
        "physical_rows":rows.len(),"success_rows":4,"rejected_rows":5,
        "preparation_seconds_diagnostic":preparation_seconds,"evaluation_seconds_diagnostic":evaluation_seconds,
        "instructions":plan.instructions,"integrated_polynomial":plan.integrated_polynomial.to_string(),
        "execution":{"packed_rows":execution.input_rows,"active_rows":execution.active_rows,
            "numeric_batch_calls":execution.numeric_batch_calls,"enclosure_batch_calls":execution.enclosure_batch_calls,
            "tail_batch_calls":execution.tail_batch_calls},
        "lanes":names.iter().zip(&lanes).map(|(name,l)|json!({"name":name,"result":lane_json(l)})).collect::<Vec<_>>(),
        "independent_oracle_comparisons":comparisons,"empty_reverse_independent_workspace":"passed",
        "malformed_physical_length":"rejected","oversized_shape":"rejected",
        "normalization":"E6=-integral_Delta4 F^-2; vacuum=-1/(24*M^2); finite-only analytic domain",
        "limitations":"Single retained routing family and common-mass jets; no mixed-axis, unequal-complex-mass, other numeric-domain or public-core certificate; no performance benchmark"});
    std::fs::write(output_path,serde_json::to_vec_pretty(&record)?)?;
    eprintln!("stage: all bounded direct E6 N2 controls passed");
    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> { run() }
