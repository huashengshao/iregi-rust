use iregi_masters::NativeFloat;
use iregi_rust::{
    Algorithm, Convention, KinematicsBatch, LaneStatus, ReductionPlan, ReductionSettings,
    TensorWeights, Workspace,
    basis::{Monomial, tensor_basis},
};
use serde_json::{Value, json};
use std::{path::Path, time::Instant};
use symbolica::{
    atom::{Atom, AtomCore},
    domains::{
        dual::HyperDual,
        float::{Complex, Float, FloatLike, Real, SingleFloat},
        rational::Rational,
    },
    evaluate::{Dualizer, ExpressionEvaluator},
};

fn save(path: &Path, value: &Value) {
    let pending = path.with_extension("pending.json");
    std::fs::write(&pending, serde_json::to_vec_pretty(value).unwrap()).unwrap();
    std::fs::rename(pending, path).unwrap();
}
fn rational(value: &Value, key: &str) -> Rational {
    let atom = Atom::parse(
        value[key].as_str().unwrap(),
        "iregi_planar_mixed_reference",
        Default::default(),
    )
    .unwrap();
    Rational::try_from(atom).unwrap()
}
fn exact_values(value: &Value, count: usize) -> Vec<Complex<Rational>> {
    let values = value.as_array().unwrap();
    assert_eq!(values.len(), count);
    values
        .iter()
        .map(|v| {
            for key in ["real_precision", "imaginary_precision"] {
                let bits = v[key].as_u64().unwrap();
                assert!((1..=128).contains(&bits));
            }
            Complex::new(rational(v, "real"), rational(v, "imaginary"))
        })
        .collect()
}
fn floating(prototype: &Float, values: &[Complex<Rational>]) -> Vec<Complex<Float>> {
    values
        .iter()
        .map(|v| {
            Complex::new(
                prototype.from_rational(&v.re),
                prototype.from_rational(&v.im),
            )
        })
        .collect()
}
fn serialize(values: &[Complex<Float>]) -> Value {
    Value::Array(
        values
            .iter()
            .map(|v| {
                json!({
                    "real":v.re.exact_rational().unwrap().to_string(),
                    "imaginary":v.im.exact_rational().unwrap().to_string(),
                    "real_precision":v.re.get_precision(),"imaginary_precision":v.im.get_precision()
                })
            })
            .collect(),
    )
}
fn expected_inputs() -> Vec<Complex<Rational>> {
    let zero = Complex::new(Rational::from(0), Rational::from(0));
    let mut tangent = vec![zero; 104];
    let points = [
        [0, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 1, 1, 1],
    ];
    for (i, value) in points.into_iter().flatten().enumerate() {
        tangent[i * 4].re = Rational::from(value);
    }
    for (i, value) in [4, 9, 16, 25, 36].into_iter().enumerate() {
        tangent[(20 + i) * 4].re = Rational::from(value);
    }
    tangent[25 * 4].re = Rational::from(3);
    for (argument, component) in [
        (4, 2),
        (8, 1),
        (16, 2),
        (16, 1),
        (20, 3),
        (21, 3),
        (22, 3),
        (23, 3),
        (24, 3),
    ] {
        tangent[argument * 4 + component].re = Rational::from(1);
    }
    let mut transverse = tangent.clone();
    transverse[16 * 4 + 3].re = Rational::from(1);
    [tangent.clone(), transverse, tangent].concat()
}
fn expected_coefficients() -> Vec<Complex<Rational>> {
    let mut values = vec![Complex::new(Rational::from(0), Rational::from(0)); 20];
    for (i, weight) in [2_i64, -1, -1, -1, 1].into_iter().enumerate() {
        values[i * 4].re = Rational::from((weight, 6));
        values[i * 4 + 3].re = Rational::from((-weight, 18));
    }
    values
}
fn dimensional_reference(
    prototype: &Float,
    row: &[Complex<Float>],
    monomial: &Monomial,
    value: &Complex<Float>,
) -> Float {
    let mut scale = prototype.zero();
    for argument in 0..20 {
        let v = &row[argument * 4];
        let magnitude = NativeFloat::hypot(&v.re, &v.im);
        if magnitude > scale {
            scale = magnitude;
        }
    }
    for argument in 20..25 {
        let v = &row[argument * 4];
        let magnitude = NativeFloat::hypot(&v.re, &v.im).sqrt();
        if magnitude > scale {
            scale = magnitude;
        }
    }
    if scale.is_zero() {
        scale = row[25 * 4].re.clone();
    }
    let dimension = i32::try_from(monomial.rank()).unwrap() - 6;
    let power = scale.pow(u64::from(dimension.unsigned_abs()));
    let natural = if dimension < 0 { power.inv() } else { power };
    assert!(natural.is_finite() && !natural.is_zero());
    let magnitude = NativeFloat::hypot(&value.re, &value.im);
    if magnitude > natural {
        magnitude
    } else {
        natural
    }
}

fn main() {
    let arguments: Vec<_> = std::env::args().collect();
    assert_eq!(arguments.len(), 3);
    let input_path = Path::new(&arguments[1]);
    let output_path = Path::new(&arguments[2]);
    assert!(!output_path.exists());
    let saved: Value = serde_json::from_slice(&std::fs::read(input_path).unwrap()).unwrap();
    assert_eq!(saved["schema_version"], 1);
    assert_eq!(
        saved["fixture"],
        "planar-spatial-rotating-rectangular-mixed-v1"
    );
    assert_eq!(saved["status"], "primary_complete");
    assert_eq!(saved["working_precision"], 128);
    assert_eq!(saved["requested_precision"], 53);
    assert_eq!(saved["rows"], 3);
    assert_eq!(saved["components"], 4);
    let shape = vec![vec![0, 0], vec![0, 1], vec![1, 0], vec![1, 1]];
    assert_eq!(saved["shape"], json!(shape));
    let mut settings = ReductionSettings::new(5, 7);
    settings.algorithm = Algorithm::PassarinoVeltman;
    settings.convention = Convention::MadLoop;
    settings.tensor_weights = TensorWeights::Multinomial;
    assert_eq!(saved["settings"], json!(settings));
    let basis = tensor_basis(7);
    let basis_json = json!(basis.iter().map(|m| m.0).collect::<Vec<_>>());
    assert_eq!(basis.len(), 330);
    assert_eq!(saved["basis"], basis_json);
    assert_eq!(
        saved["returned_metadata"],
        json!({"convention":settings.convention,
        "tensor_weights":settings.tensor_weights,"dual_shape":shape,"components":4,"basis":basis_json})
    );
    let statuses = saved["primary_statuses"].as_array().unwrap();
    assert_eq!(statuses.len(), 3);
    assert_eq!(statuses[0], "Success");
    assert_eq!(statuses[2], "Success");
    assert_eq!(
        statuses[1],
        "InvalidInput(\"planar coordinate determinant is certified nonzero in Taylor component 3; transverse jets and nonplanar points require the ordinary interface\")"
    );
    assert_eq!(saved["analytic_used"], json!([true, false, true]));
    assert_eq!(saved["fallback_used"], json!([false, false, false]));
    let all_inputs = exact_values(&saved["inputs"], 312);
    assert_eq!(all_inputs, expected_inputs());
    let lane_values = saved["lane_values"].as_array().unwrap();
    assert_eq!(lane_values.len(), 3);
    assert!(lane_values[1].is_null());
    let primary0 = exact_values(&lane_values[0], 5280);
    let primary2 = exact_values(&lane_values[2], 5280);
    assert_eq!(primary0, primary2);
    let coefficients = exact_values(&saved["independent_coefficients"], 20);
    let exact_coefficients = expected_coefficients();
    let rounded_coefficients: Vec<_> = floating(&Float::new(128), &exact_coefficients)
        .iter()
        .map(|v| {
            Complex::new(
                v.re.exact_rational().unwrap(),
                v.im.exact_rational().unwrap(),
            )
        })
        .collect();
    assert_eq!(coefficients, rounded_coefficients);
    let prototype = Float::new(256);
    let tangent = floating(&prototype, &all_inputs[..104]);
    let coefficient_values = floating(&prototype, &exact_coefficients);
    let mut record = json!({"schema_version":1,"status":"primary_validated","source_primary":input_path,
        "fixture":saved["fixture"],"working_precision":256,"requested_precision":53,"components":4,"shape":shape,
        "settings":settings,"basis":basis_json,"validated_primary_lanes":[0,2],"primary_complex_slots_per_lane":5280,
        "validated_inputs":saved["inputs"],"validated_primary_metadata":saved["returned_metadata"],
        "primary_statuses":saved["primary_statuses"],"saved_primary_coefficients":saved["independent_coefficients"],
        "independent_coefficients":serialize(&coefficient_values)});
    save(output_path, &record);
    let started = Instant::now();
    eprintln!("PLANAR_REFERENCE validated complete primary artifact; independent boxes START");
    settings.propagators = 4;
    settings.powers = vec![1; 4];
    let plan = ReductionPlan::new(settings.clone()).unwrap();
    eprintln!(
        "PLANAR_REFERENCE box plan complete elapsed={:?}",
        started.elapsed()
    );
    let mut workspace = Workspace::new_dual(
        &plan,
        prototype.clone(),
        HyperDual::<u8>::new(shape.clone()),
    )
    .unwrap();
    workspace.set_accuracy_precision(53).unwrap();
    workspace.set_profiling(true);
    eprintln!(
        "PLANAR_REFERENCE box workspace complete elapsed={:?}",
        started.elapsed()
    );
    let mut packed = KinematicsBatch {
        rows: 5,
        components: 4,
        values: Vec::with_capacity(5 * 21 * 4),
    };
    for omitted in 0..5 {
        for i in 0..5 {
            if i != omitted {
                packed
                    .values
                    .extend_from_slice(&tangent[16 * i..16 * (i + 1)]);
            }
        }
        for i in 0..5 {
            if i != omitted {
                packed
                    .values
                    .extend_from_slice(&tangent[(20 + i) * 4..(21 + i) * 4]);
            }
        }
        packed.values.extend_from_slice(&tangent[100..104]);
    }
    assert_eq!(packed.values.len(), 420);
    let boxes = workspace.reduce_batch(&packed).unwrap();
    eprintln!(
        "PLANAR_REFERENCE box reduction complete elapsed={:?} statuses={:?}",
        started.elapsed(),
        boxes.statuses
    );
    record["status"] = "boxes_complete".into();
    record["box_statuses"] = json!(
        boxes
            .statuses
            .iter()
            .map(|s| format!("{s:?}"))
            .collect::<Vec<_>>()
    );
    record["box_values"] = Value::Array(
        (0..5)
            .map(|i| boxes.lane(i).map_or(Value::Null, serialize))
            .collect(),
    );
    record["box_metadata"] = json!({"convention":boxes.metadata().convention(),"tensor_weights":boxes.metadata().tensor_weights(),
        "dual_shape":boxes.metadata().dual_shape(),"components":boxes.components,"basis":boxes.basis.iter().map(|m|m.0).collect::<Vec<_>>()});
    save(output_path, &record);
    assert_eq!(boxes.statuses, vec![LaneStatus::Success; 5]);
    assert_eq!(boxes.basis, basis);
    assert_eq!(boxes.components, 4);
    assert_eq!(boxes.metadata().convention(), Convention::MadLoop);
    assert_eq!(
        boxes.metadata().tensor_weights(),
        TensorWeights::Multinomial
    );
    assert_eq!(boxes.metadata().dual_shape(), Some(shape.as_slice()));
    let parameters: Vec<_> = (0..10)
        .map(|i| Atom::var(symbolica::symbol!(format!("iregi_planar_reference::v{i}"))))
        .collect();
    let expression = (0..5).fold(Atom::Zero, |sum, i| {
        sum + &parameters[i] * &parameters[i + 5]
    });
    let evaluator: ExpressionEvaluator<Complex<Rational>> =
        Atom::evaluator_multiple(&[expression], &parameters)
            .direct_translation(true)
            .horner_iterations(0)
            .cores(1)
            .build()
            .unwrap();
    let evaluator = evaluator
        .vectorize(&Dualizer::new(HyperDual::<u8>::new(shape), Vec::new()))
        .unwrap();
    let mut evaluator = evaluator
        .map_coeff_with_prec(
            &|v| {
                Complex::new(
                    prototype.from_rational(&v.re),
                    prototype.from_rational(&v.im),
                )
            },
            256,
        )
        .into_batch_evaluator();
    let mut contraction_inputs = Vec::with_capacity(1320 * 40);
    for slot in 0..1320 {
        contraction_inputs.extend_from_slice(&coefficient_values);
        for pinch in 0..5 {
            contraction_inputs
                .extend_from_slice(&boxes.lane(pinch).unwrap()[slot * 4..(slot + 1) * 4]);
        }
    }
    let mut expected = vec![Complex::new(prototype.zero(), prototype.zero()); 5280];
    evaluator
        .evaluate_batch(&contraction_inputs, &mut expected, 1320)
        .unwrap();
    record["independent_values"] = serialize(&expected);
    record["status"] = "identity_evaluated".into();
    save(output_path, &record);
    let tolerance = prototype.from_rational(&Rational::from((1, 10_000_000_000_i64)));
    let mut maxima = Vec::new();
    for (lane, exact) in [(0, primary0), (2, primary2)] {
        let actual = floating(&prototype, &exact);
        let mut maximum = prototype.zero();
        for (index, (actual, reference)) in actual.iter().zip(&expected).enumerate() {
            let error = NativeFloat::hypot(
                &(actual.re.clone() - &reference.re),
                &(actual.im.clone() - &reference.im),
            );
            let scale = dimensional_reference(&prototype, &tangent, &basis[index / 16], reference);
            let normalized = error / scale;
            assert!(
                normalized <= tolerance,
                "primary lane{lane} normalized slot{index}"
            );
            if normalized > maximum {
                maximum = normalized;
            }
        }
        maxima.push(json!({"lane":lane,"complex_slots":5280,"maximum_normalized_error":maximum.exact_rational().unwrap().to_string()}));
    }
    record["comparisons"] = json!(maxima);
    record["tolerance"] = "1/10000000000".into();
    record["compared_complex_slots"] = 10560.into();
    record["box_execution"] = json!({"input_rows":workspace.last_execution().input_rows,"master_rows":workspace.last_execution().master_rows,
        "reduction_rows":workspace.last_execution().reduction_rows,"analytic_rows":workspace.last_execution().analytic_rows});
    record["status"] = "passed".into();
    save(output_path, &record);
    eprintln!("PLANAR_REFERENCE COMPLETE elapsed={:?}", started.elapsed());
}
