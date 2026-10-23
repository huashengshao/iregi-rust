use iregi_rust::{
    Algorithm, KinematicsBatch, PrecisionRescueWorkspace, ReductionPlan, ReductionSettings,
    RescueSettings,
};
use symbolica::domains::float::Complex;

fn main() {
    let source: serde_json::Value = serde_json::from_slice(
        &std::fs::read("target/generalized-pv/reference-capture.json").unwrap(),
    )
    .unwrap();
    let mut reports = Vec::new();
    let mut passed = 0;
    for case in source["cases"]
        .as_array()
        .unwrap()
        .iter()
        .chain(source["translated_scalar_checks"].as_array().unwrap())
    {
        let input = &case["input"];
        let id = input["id"].as_str().unwrap();
        eprintln!("generalized PV comparison: {id}");
        let propagators = input["propagators"].as_array().unwrap();
        let mut settings =
            ReductionSettings::new(propagators.len(), input["rank"].as_u64().unwrap() as u16);
        settings.dimension_shift = (input["dimension_shift"].as_i64().unwrap() / 2) as i16;
        settings.powers = propagators
            .iter()
            .map(|p| p["power"].as_u64().unwrap() as u16)
            .collect();
        settings.algorithm = match input["mode"].as_u64().unwrap() {
            0 => Algorithm::Ibp,
            1 => Algorithm::PassarinoVeltman,
            _ => Algorithm::Hybrid,
        };
        let base_dimension = 4 + 2 * i32::from(settings.dimension_shift)
            - 2 * settings
                .powers
                .iter()
                .map(|&power| i32::from(power))
                .sum::<i32>();
        let mut scale = input["mu"].as_f64().unwrap();
        let mut values = Vec::new();
        for propagator in propagators {
            for value in propagator["shift"].as_array().unwrap() {
                let value = value.as_f64().unwrap();
                scale = scale.max(value.abs());
                values.push(Complex::new(value, 0.));
            }
        }
        for propagator in propagators {
            let mass = &propagator["mass_squared"];
            let re = mass[0].as_f64().unwrap();
            let im = mass[1].as_f64().unwrap();
            scale = scale.max(re.hypot(im).sqrt());
            values.push(Complex::new(re, im));
        }
        values.push(Complex::new(input["mu"].as_f64().unwrap(), 0.));
        let result = (|| -> Result<serde_json::Value, String> {
            if case["expected"]["stable"] != true {
                return Err("reference did not report a stable result".into());
            }
            let plan = ReductionPlan::new(settings).map_err(|e| e.to_string())?;
            let mut workspace = PrecisionRescueWorkspace::new(&plan, 0., RescueSettings::default())
                .map_err(|e| e.to_string())?;
            let output = workspace
                .reduce_batch(&KinematicsBatch {
                    rows: 1,
                    components: 1,
                    values,
                })
                .map_err(|e| e.to_string())?;
            let actual = output.lane(0).map_err(|e| format!("{e:?}"))?;
            let expected = case["expected"]["moments"]
                .as_array()
                .ok_or("missing expected moments")?;
            if actual.len() != expected.len() * 4 {
                return Err("incorrect output shape".into());
            }
            let mut max_error = 0.0_f64;
            let mut failures = Vec::new();
            for (index, expected) in expected.iter().enumerate() {
                let natural = scale.powi(base_dimension + plan.basis()[index].rank() as i32);
                for slot in 0..4 {
                    let re = expected[slot][0].as_f64().unwrap();
                    let im = expected[slot][1].as_f64().unwrap();
                    let value = &actual[4 * index + slot];
                    let error = (value.re - re).hypot(value.im - im) / (natural + re.hypot(im));
                    if !error.is_finite() || error > 1e-10 {
                        failures.push(serde_json::json!({"moment":index,"slot":slot,"error":error,"actual":[value.re,value.im],"expected":[re,im]}));
                    }
                    max_error = max_error.max(error);
                }
            }
            Ok(
                serde_json::json!({"id":id,"passed":failures.is_empty(),"complex_slots":actual.len(),"maximum_normalized_error":max_error,"failures":failures,"algorithm_used":plan.algorithm_used(),"preparation_notes":plan.preparation_notes(),"rescue":format!("{:?}",workspace.last_rescue_statuses())}),
            )
        })();
        let report = match result {
            Ok(report) => report,
            Err(error) => serde_json::json!({"id":id,"passed":false,"error":error}),
        };
        if report["passed"] == true {
            passed += 1;
        }
        reports.push(report);
        let result = serde_json::json!({"passed":passed,"total":reports.len(),"complete":false,"cases":reports});
        std::fs::write(
            "target/generalized-pv/reference-comparison.json",
            serde_json::to_string_pretty(&result).unwrap() + "\n",
        )
        .unwrap();
    }
    let report =
        serde_json::json!({"passed":passed,"total":reports.len(),"complete":true,"cases":reports});
    std::fs::write(
        "target/generalized-pv/reference-comparison.json",
        serde_json::to_string_pretty(&report).unwrap() + "\n",
    )
    .unwrap();
    assert_eq!(
        passed,
        reports.len(),
        "generalized reference comparisons failed"
    );
    println!("validated {passed} generalized reference cases");
}
