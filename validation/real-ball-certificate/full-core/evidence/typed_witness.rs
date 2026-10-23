//! Private full-core witness. Select a baseline/candidate archive with --extern.
//! Emits one JSON object per case, retaining every successful Laurent/Taylor slot.
//! No timing claims, numerical downcasts, reference normalization, or input snapping.
use std::io::{self, Write};

use iregi_masters::{Complex, DoubleFloat, Float, NativeFloat};
use iregi_rust::{
    Algorithm, BatchResult, ExecutionStats, KinematicsBatch, LaneStatus, ReductionPlan,
    ReductionSettings, Workspace,
};
use serde_json::{Value, json};
use symbolica::{
    domains::{dual::HyperDual, rational::Rational},
    evaluate::EvaluationDomain,
};

symbolica::create_hyperdual_from_components!(FirstDual, [[0], [1]]);
// Deliberately retain this component order: primal, v, u, uv.
symbolica::create_hyperdual_from_components!(MixedDual, [[0, 0], [0, 1], [1, 0], [1, 1]]);

const ACCURACY_BITS: u32 = 53;
const INVALID_LANE: usize = 2;
const ROWS: usize = 5;

fn number<T: NativeFloat>(prototype: &T, numerator: i64, denominator: i64) -> T {
    prototype.from_rational(&Rational::from((numerator, denominator)))
}

fn real<T: NativeFloat>(prototype: &T, numerator: i64, denominator: i64) -> Complex<T> {
    Complex::new(number(prototype, numerator, denominator), prototype.zero())
}

fn seed<T: NativeFloat>(prototype: &T, imaginary: bool, denominator: i64) -> Complex<T> {
    let value = number(prototype, 1, denominator);
    if imaginary {
        Complex::new(prototype.zero(), value)
    } else {
        Complex::new(value, prototype.zero())
    }
}

fn scalar_json<T: NativeFloat>(value: &T) -> Value {
    let digits = (u64::from(value.get_precision()) * 30103 / 100000 + 3) as usize;
    json!({
        "decimal": format!("{:.*e}", digits, value),
        "exact_rational": value.exact_rational().map(|r| r.to_string()),
        "precision_bits": value.get_precision(),
        "negative_zero": value.is_zero() && value.negative_sign(),
        "finite": value.is_finite(),
    })
}

fn complex_json<T: NativeFloat>(value: &Complex<T>) -> Value {
    json!([scalar_json(&value.re), scalar_json(&value.im)])
}

fn status_json(status: &LaneStatus) -> Value {
    match status {
        LaneStatus::Success => json!({"kind": "success"}),
        LaneStatus::InvalidInput(reason) => json!({"kind": "invalid_input", "reason": reason}),
        LaneStatus::MasterFailure(reason) => json!({"kind": "master_failure", "reason": reason}),
        LaneStatus::Unstable(reason) => json!({"kind": "unstable", "reason": reason}),
    }
}

fn stats_json(stats: ExecutionStats) -> Value {
    json!({
        "input_rows": stats.input_rows,
        "argument_rows": stats.argument_rows,
        "master_family_batches": stats.master_family_batches,
        "master_rows": stats.master_rows,
        "pentagon_box_rows": stats.pentagon_box_rows,
        "reduction_rows": stats.reduction_rows,
        "fallback_rows": stats.fallback_rows,
        "fallback_successes": stats.fallback_successes,
        "analytic_rows": stats.analytic_rows,
    })
}

fn report<T: NativeFloat>(
    plan: &ReductionPlan,
    workspace: &Workspace<T>,
    input: &KinematicsBatch<T>,
    result: &BatchResult<T>,
    labels: &[&str],
    carrier: &str,
) -> Value
where
    Complex<T>: EvaluationDomain,
{
    let components = result.components;
    let lanes: Vec<_> = (0..result.rows())
        .map(|lane| {
            // Failed-lane scratch is never exposed as numerical output.
            let moments = result.lane(lane).ok().map(|values| {
                values.chunks_exact(4 * components)
                    .map(|moment| moment.chunks_exact(components)
                        .map(|pole| pole.iter().map(complex_json).collect::<Vec<_>>())
                        .collect::<Vec<_>>())
                    .collect::<Vec<_>>()
            });
            json!({
                "lane": lane, "label": labels[lane],
                "status": status_json(&result.statuses[lane]),
                "analytic_used": result.analytic_used[lane],
                "fallback_used": result.fallback_used[lane],
                "diagnostics": workspace.last_diagnostics().get(lane),
                "moments": moments,
            })
        })
        .collect();
    let valid_lanes_successful = result.statuses.iter().enumerate()
        .all(|(lane, status)| lane == INVALID_LANE || *status == LaneStatus::Success);
    let invalid_lane_rejected = matches!(
        result.statuses.get(INVALID_LANE), Some(LaneStatus::InvalidInput(_))
    );
    let finite_successful_values = (0..result.rows()).all(|lane| {
        result.lane(lane).map_or(true, |values| {
            values.iter().all(|v| v.re.is_finite() && v.im.is_finite())
        })
    });
    let input_width = input.values.len() / input.rows;
    json!({
        "status": "completed", "carrier": carrier,
        "settings": plan.settings(),
        "working_bits": workspace.binary_precision(), "accuracy_bits": ACCURACY_BITS,
        "sample_rows": input.rows, "components": components,
        "dual_shape": result.metadata().dual_shape(),
        "basis": result.basis.iter().map(|m| m.0).collect::<Vec<_>>(),
        "laurent_order": ["uv_single", "ir_single", "ir_double", "finite"],
        "output_order": "lane -> basis -> Laurent -> Taylor -> [real,imaginary]",
        "input_order": "lane -> argument -> Taylor -> [real,imaginary]",
        "inputs": input.values.chunks_exact(input_width)
            .map(|row| row.chunks_exact(input.components)
                .map(|argument| argument.iter().map(complex_json).collect::<Vec<_>>())
                .collect::<Vec<_>>()).collect::<Vec<_>>(),
        "lanes": lanes, "execution": stats_json(workspace.last_execution()),
        "invalid_scale_lane": INVALID_LANE,
        "invalid_lane_rejected": invalid_lane_rejected,
        "valid_lanes_successful": valid_lanes_successful,
        "finite_successful_values": finite_successful_values,
        // A valid branch may still receive a stability diagnostic. Such a case
        // remains visible and cannot count as a successful witness.
        "qualification_pass": valid_lanes_successful && invalid_lane_rejected
            && finite_successful_values,
        "certificate_counters_available_via_public_api": false,
        "performance_gate": false,
    })
}

fn ggh<T: NativeFloat>(prototype: T) -> Result<Value, String>
where
    Complex<T>: EvaluationDomain,
{
    let mut settings = ReductionSettings::new(3, 2);
    settings.algorithm = Algorithm::Hybrid;
    let plan = ReductionPlan::new(settings).map_err(|e| e.to_string())?;
    let mut workspace = Workspace::new(&plan, prototype.clone()).map_err(|e| e.to_string())?;
    workspace.set_accuracy_precision(ACCURACY_BITS).map_err(|e| e.to_string())?;
    let mut values = Vec::new();
    for lane in 0..ROWS {
        // Every number is an exact integer/dyadic fixture value in each domain.
        let mut row = [0, 0, 0, 0, 125, 0, 0, -125, -125, 0, 0, -125]
            .map(|twice| real(&prototype, twice, 2)).to_vec();
        row[9].re = -prototype.zero();
        row[10].re = -prototype.zero();
        let imaginary_mass = match lane { 1 => -1, 4 => -2, _ => 0 };
        row.extend((0..3).map(|_| Complex::new(
            number(&prototype, 29929, 1), number(&prototype, imaginary_mass, 4),
        )));
        row.push(real(&prototype, if lane == INVALID_LANE { -125 } else { 125 }, 1));
        values.extend(row);
    }
    let input = KinematicsBatch { rows: ROWS, components: 1, values };
    let result = workspace.reduce_batch(&input).map_err(|e| e.to_string())?;
    Ok(report(&plan, &workspace, &input, &result, &[
        "real_mass", "mass_squared_imaginary_minus_quarter", "invalid_negative_scale",
        "real_mass_after_invalid", "mass_squared_imaginary_minus_half",
    ], "ordinary"))
}

fn lightlike<T: NativeFloat>(prototype: T, mixed: bool, static_carrier: bool) -> Result<Value, String>
where
    Complex<T>: EvaluationDomain,
{
    let mut settings = ReductionSettings::new(2, 1);
    settings.algorithm = Algorithm::Hybrid;
    let plan = ReductionPlan::new(settings).map_err(|e| e.to_string())?;
    let shape = if mixed {
        vec![vec![0, 0], vec![0, 1], vec![1, 0], vec![1, 1]]
    } else {
        vec![vec![0], vec![1]]
    };
    let components = shape.len();
    let mut values = Vec::new();
    for lane in 0..ROWS {
        let mut row = vec![real(&prototype, 0, 1); 11 * components];
        // Nonzero lightlike p=(1,1,0,0), equal masses away from thresholds.
        row[4 * components] = real(&prototype, 1, 1);
        row[5 * components] = real(&prototype, 1, 1);
        let imaginary_mass = if lane >= 3 { -1 } else { 0 };
        for argument in [8, 9] {
            row[argument * components] = Complex::new(
                number(&prototype, 4, 1), number(&prototype, imaginary_mass, 4),
            );
        }
        row[10 * components] = real(&prototype, if lane == INVALID_LANE { -1 } else { 1 }, 1);
        let imaginary_seed = matches!(lane, 1 | 4);
        if mixed {
            // u changes time, v changes the first squared mass. An explicit uv
            // input jet checks ordering as well as the product of first jets.
            row[4 * components + 2] = seed(&prototype, imaginary_seed, 1);
            row[8 * components + 1] = seed(&prototype, imaginary_seed, 1);
            row[4 * components + 3] = seed(&prototype, imaginary_seed, 4);
        } else {
            row[4 * components + 1] = seed(&prototype, imaginary_seed, 1);
        }
        values.extend(row);
    }
    let input = KinematicsBatch { rows: ROWS, components, values };
    let dynamic: Vec<_> = input.values.chunks_exact(components)
        .map(|value| HyperDual::from_values(shape.clone(), value.to_vec())).collect();
    let (workspace, result) = if static_carrier && mixed {
        let typed: Vec<_> = dynamic.iter().map(|value| MixedDual {
            values: std::array::from_fn(|i| value.values[i].clone()),
        }).collect();
        let mut workspace = Workspace::new_dual(&plan, prototype, typed[0].clone())
            .map_err(|e| e.to_string())?;
        workspace.set_accuracy_precision(ACCURACY_BITS).map_err(|e| e.to_string())?;
        let result = workspace.reduce_typed_dual_batch(&typed, ROWS).map_err(|e| e.to_string())?;
        (workspace, result)
    } else if static_carrier {
        let typed: Vec<_> = dynamic.iter().map(|value| FirstDual {
            values: std::array::from_fn(|i| value.values[i].clone()),
        }).collect();
        let mut workspace = Workspace::new_dual(&plan, prototype, typed[0].clone())
            .map_err(|e| e.to_string())?;
        workspace.set_accuracy_precision(ACCURACY_BITS).map_err(|e| e.to_string())?;
        let result = workspace.reduce_typed_dual_batch(&typed, ROWS).map_err(|e| e.to_string())?;
        (workspace, result)
    } else {
        let mut workspace = Workspace::new_dual(&plan, prototype, dynamic[0].clone())
            .map_err(|e| e.to_string())?;
        workspace.set_accuracy_precision(ACCURACY_BITS).map_err(|e| e.to_string())?;
        let result = workspace.reduce_hyperdual_batch(&dynamic, ROWS).map_err(|e| e.to_string())?;
        (workspace, result)
    };
    Ok(report(&plan, &workspace, &input, &result, &[
        "real_mass_real_jets", "real_mass_imaginary_jets", "invalid_negative_scale",
        "complex_mass_real_jets", "complex_mass_imaginary_jets",
    ], if static_carrier { "static_dual" } else { "dynamic_hyperdual" }))
}

fn dispatch(case: &str) -> Result<Value, String> {
    let (family, precision) = case.rsplit_once('_').ok_or("case requires a precision suffix")?;
    let run = |mixed, static_carrier| match precision {
        "f64" => lightlike(0_f64, mixed, static_carrier),
        "dd" => lightlike(DoubleFloat::zero_at(106), mixed, static_carrier),
        "float128" => lightlike(Float::new(128), mixed, static_carrier),
        _ => Err(format!("unknown precision {precision}")),
    };
    match family {
        "ggh" => match precision {
            "f64" => ggh(0_f64),
            "dd" => ggh(DoubleFloat::zero_at(106)),
            "float128" => ggh(Float::new(128)),
            _ => Err(format!("unknown precision {precision}")),
        },
        "lightlike_first_static" => run(false, true),
        "lightlike_first_dynamic" => run(false, false),
        "lightlike_mixed_static" => run(true, true),
        "lightlike_mixed_dynamic" => run(true, false),
        _ => Err(format!("unknown case family {family}")),
    }
}

fn main() {
    let available: Vec<_> = [
        "ggh", "lightlike_first_static", "lightlike_first_dynamic",
        "lightlike_mixed_static", "lightlike_mixed_dynamic",
    ].into_iter().flat_map(|family| ["f64", "dd", "float128"]
        .into_iter().map(move |precision| format!("{family}_{precision}"))).collect();
    let requested: Vec<_> = std::env::args().skip(1).collect();
    if requested == ["--list"] {
        println!("{}", json!({"cases": available}));
        return;
    }
    let cases = if requested.is_empty() { available.clone() } else { requested };
    let mut failed = false;
    for case in cases {
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            if available.contains(&case) { dispatch(&case) } else { Err(format!("unknown case {case}")) }
        }));
        let mut output = match outcome {
            Ok(Ok(value)) => value,
            Ok(Err(error)) => json!({"status": "error", "error": error, "qualification_pass": false}),
            Err(_) => json!({"status": "panic", "qualification_pass": false}),
        };
        output["schema"] = json!(1);
        output["kind"] = json!("private_full_core_typed_witness");
        output["case"] = json!(case);
        output["master_backend"] = json!(format!("{:?}", iregi_masters::default_master_backend()));
        failed |= output["qualification_pass"] != json!(true);
        println!("{output}");
        io::stdout().flush().expect("flush witness record");
    }
    if failed { std::process::exit(1); }
}
