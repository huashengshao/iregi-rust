//! Test-only public supplied-invariant probe; source is copied into both
//! isolated compiler variants. No production arithmetic or guards are changed.
use crate::{
    Algorithm, CertifiedScalarReductionPlan, CertifiedScalarWorkspace, Convention,
    LaneStatus, ReductionSettings, ScalarKinematicsBatch,
};
use std::time::Instant;
use iregi_masters::NativeFloat;
use symbolica::domains::float::{Complex, Float, FloatLike, Real};

fn settings() -> ReductionSettings {
    let mut settings = ReductionSettings::new(6, 0);
    settings.algorithm = Algorithm::Ibp;
    settings.convention = Convention::OneLoop;
    settings
}

fn exact_row() -> Vec<i64> {
    let q = [
        [0, 0, 0, 0],
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [1, 1, 1, 1],
    ];
    let mut row = Vec::new();
    for (i, a) in q.iter().enumerate() {
        for b in &q[i..] {
            row.push(a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3]);
        }
    }
    row.extend(30..36);
    row.push(3); // renormalization scale mu, not mu^2
    row
}

fn record(value: serde_json::Value) {
    println!("PROBE_RECORD {value}");
}

#[test]
fn public_certified_n6_binary64_status_before_comparator() {
    let started = Instant::now();
    let plan = CertifiedScalarReductionPlan::new(settings()).unwrap();
    record(serde_json::json!({"phase":"chart_prepared","seconds":started.elapsed().as_secs_f64()}));
    let mut workspace = CertifiedScalarWorkspace::new(&plan, 0_f64).unwrap();
    let row: Vec<_> = exact_row().into_iter().map(|x| Complex::new(x as f64, 0.)).collect();
    let mut bad = row.clone();
    bad[20].re += 1.;
    let result = workspace.reduce_batch(&ScalarKinematicsBatch {
        rows: 3, components: 1, values: [row.clone(), bad, row].concat(),
    }).unwrap();
    record(serde_json::json!({"phase":"certified_result","seconds":started.elapsed().as_secs_f64(),
        "working_bits":53,"accuracy_bits":53,"statuses":format!("{:?}",result.statuses),
        "diagnostics":format!("{:?}",workspace.last_diagnostics())}));
    assert!(matches!(result.statuses[1], LaneStatus::InvalidInput(_)));
    for lane in [0, 2] {
        assert!(matches!(result.statuses[lane], LaneStatus::Success | LaneStatus::Unstable(_)));
        match result.lane(lane) {
            Ok(values) => record(serde_json::json!({"lane":lane,"values":values.iter().map(|x|[x.re.to_string(),x.im.to_string()]).collect::<Vec<_>>()})),
            Err(error) => record(serde_json::json!({"lane":lane,"guard_rejection":format!("{error:?}")})),
        }
    }
    assert_eq!(result.statuses[0], result.statuses[2]);
}

#[test]
fn public_certified_n6_float_converges_and_matches_parameter_integral() {
    let oracle_path = std::env::var("IREGI_N6_PARAMETER_ORACLE")
        .expect("explicit independent parameter-oracle path is required");
    let oracle: serde_json::Value = serde_json::from_slice(&std::fs::read(&oracle_path).unwrap()).unwrap();
    assert_eq!(oracle["status"], "estimated_converged");
    // The oracle is binary64 numerical quadrature. Parse its recorded decimal
    // directly into Float; no reduction input/value passes through binary64.
    let reference = Float::parse(&oracle["comparison"]["oneloop_finite"].to_string(), Some(256)).unwrap();
    let oracle_tolerance = Float::parse("1e-19", Some(256)).unwrap();
    let estimated_uncertainty = Float::parse(&oracle["comparison"]["estimated_uncertainty_oneloop"].to_string(), Some(256)).unwrap();
    assert!(estimated_uncertainty < oracle_tolerance);
    let started = Instant::now();
    let plan = CertifiedScalarReductionPlan::new(settings()).unwrap();
    record(serde_json::json!({"phase":"chart_prepared","seconds":started.elapsed().as_secs_f64()}));
    let mut previous: Option<Vec<Complex<Float>>> = None;
    for bits in [128, 256] {
        let mut workspace = CertifiedScalarWorkspace::new(&plan, Float::new(bits)).unwrap();
        // Keep the original binary64 requested accuracy fixed while increasing
        // working precision, exactly as precision rescue does.
        workspace.set_accuracy_precision(53).unwrap();
        let row: Vec<_> = exact_row().into_iter().map(|x|
            Complex::new(Float::with_val(bits, x), Float::new(bits))).collect();
        let mut bad = row.clone();
        bad[20].re += Float::with_val(bits, 1);
        let result = workspace.reduce_batch(&ScalarKinematicsBatch {
            rows: 3, components: 1, values: [row.clone(), bad, row].concat(),
        }).unwrap();
        record(serde_json::json!({"phase":"certified_result","seconds":started.elapsed().as_secs_f64(),
            "working_bits":bits,"accuracy_bits":53,"statuses":format!("{:?}",result.statuses),
            "diagnostics":format!("{:?}",workspace.last_diagnostics())}));
        assert_eq!(result.statuses[0], LaneStatus::Success);
        assert!(matches!(result.statuses[1], LaneStatus::InvalidInput(_)));
        assert_eq!(result.statuses[2], LaneStatus::Success);
        let values = result.lane(0).unwrap().to_vec();
        assert_eq!(result.lane(2).unwrap(), values.as_slice());
        record(serde_json::json!({"working_bits":bits,"values":values.iter().map(|x|
            [x.re.to_string(),x.im.to_string()]).collect::<Vec<_>>()}));
        let tiny = Float::with_val(256, 2).pow(80).inv();
        for (slot, value) in values.iter().enumerate() {
            assert!(value.im.at_precision(256).norm() * Float::with_val(256, 1_500_625) < tiny);
            if slot < 3 {
                assert!(value.re.at_precision(256).norm() * Float::with_val(256, 1_500_625) < tiny);
            }
        }
        let difference = (values[3].re.at_precision(256) - &reference).norm();
        assert!(difference < oracle_tolerance);
        record(serde_json::json!({"working_bits":bits,"independent_oracle_difference":difference.to_string(),
            "oracle_uncertainty_kind":"estimated, not certified","oracle_path":oracle_path}));
        if let Some(previous) = &previous {
            for (slot, (before, after)) in previous.iter().zip(&values).enumerate() {
                let difference = (before.re.at_precision(256) - &after.re).norm()
                    + (before.im.at_precision(256) - &after.im).norm();
                let normalized = difference * Float::with_val(256, 1_500_625);
                record(serde_json::json!({"slot":slot,"normalized_128_256_difference":normalized.to_string()}));
                assert!(normalized < tiny);
            }
        }
        previous = Some(values);
    }
}
