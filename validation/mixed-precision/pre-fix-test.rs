//! Public regression for a high-precision workspace receiving lower-precision
//! Float values. A requested accuracy must not be inferred from the prototype
//! when the actual scalar-master arithmetic retained the input precision.

use iregi_masters::NativeFloat;
use iregi_rust::{
    Algorithm, Convention, KinematicsBatch, LaneStatus, ReductionPlan, ReductionSettings, Workspace,
};
use symbolica::domains::float::{Complex, Float, FloatLike, Real};

fn tadpole_row(bits: u32, mass: i64) -> Vec<Complex<Float>> {
    [0, 0, 0, 0, mass, 1]
        .into_iter()
        .map(|value| Complex::new(Float::with_val(bits, value), Float::new(bits)))
        .collect()
}

#[test]
fn requested_accuracy_respects_actual_float_arithmetic_precision() {
    let mut settings = ReductionSettings::new(1, 0);
    settings.algorithm = Algorithm::PassarinoVeltman;
    settings.convention = Convention::OneLoop;
    let plan = ReductionPlan::new(settings).unwrap();
    let mut workspace = Workspace::new(&plan, Float::new(256)).unwrap();
    // The mathematical inputs are exactly representable at every precision.
    // There is no uncertainty about the supplied mass or renormalization scale.
    let batch = KinematicsBatch {
        rows: 3,
        components: 1,
        values: [tadpole_row(80, 2), tadpole_row(256, 2), tadpole_row(80, 0)].concat(),
    };
    let two = Float::with_val(512, 2);
    let expected = two.clone() * (Float::with_val(512, 1) - two.log());
    let mut failed_targets = Vec::new();
    for accuracy_bits in [53, 128, 256] {
        workspace.set_accuracy_precision(accuracy_bits).unwrap();
        let result = workspace.reduce_batch(&batch).unwrap();
        let tolerance = Float::with_val(512, 2)
            .pow(u64::from(accuracy_bits - 19))
            .inv();
        println!("accuracy_bits={accuracy_bits} statuses={:?}", result.statuses);
        for lane in 0..2 {
            if let Ok(values) = result.lane(lane) {
                let error = (values[3].re.at_precision(512) - &expected).norm();
                let scaled = error / Float::with_val(512, 2);
                println!(
                    "lane={lane} finite={} precision={} scaled_error={scaled:e} target={tolerance:e}",
                    values[3].re,
                    values[3].re.get_precision(),
                );
                if scaled > tolerance {
                    failed_targets.push((accuracy_bits, lane));
                }
            }
        }
        assert_eq!(result.statuses[1], LaneStatus::Success);
        assert_eq!(result.statuses[2], LaneStatus::Success);
        if accuracy_bits == 53 {
            assert_eq!(result.statuses[0], LaneStatus::Success);
        }
    }
    assert!(
        failed_targets.is_empty(),
        "successful lanes missed their requested accuracy: {failed_targets:?}"
    );
}
