//! Source-only lifecycle capture for the frozen private thin N6 mask candidate.
//! This does not qualify numerical tolerances: the independent Python qualifier
//! compares every successful native slot at the existing normalized 1e-10 gate.

use iregi_masters::NativeFloat;
use iregi_rust::{
    Algorithm, Convention, ExecutionStats, KinematicsBatch,
    ReductionSettings, TensorWeights,
    thin_n6::{ThinSixReductionPlan, ThinSixWorkspace},
};
use serde_json::{Value, json};
use std::{error::Error, path::Path, time::Instant};
use symbolica::domains::{
    float::{Complex, Float, FloatLike, SingleFloat},
    integer::Integer,
    rational::Rational,
};

type DriverResult<T> = Result<T, Box<dyn Error>>;

fn number(value: &Value) -> DriverResult<Rational> {
    let text = value.as_str().ok_or("expected an exact rational string")?;
    let (n, d) = text.split_once('/').unwrap_or((text, "1"));
    let d = d.parse::<Integer>()?;
    if d == Integer::from(0) { return Err("zero rational denominator".into()); }
    Ok(Rational::from((n.parse::<Integer>()?, d)))
}

fn write(path: &Path, record: &Value) -> DriverResult<()> {
    std::fs::write(path, serde_json::to_string_pretty(record)? + "\n")?;
    Ok(())
}

fn represented(value: &Complex<Float>) -> DriverResult<Value> {
    Ok(json!({
        "real": value.re.exact_rational().ok_or("nonfinite real output")?.to_string(),
        "imaginary": value.im.exact_rational().ok_or("nonfinite imaginary output")?.to_string(),
        "real_precision": value.re.get_precision(),
        "imaginary_precision": value.im.get_precision(),
        "real_negative": value.re.is_sign_negative(),
        "imaginary_negative": value.im.is_sign_negative(),
    }))
}

fn execution(stats: ExecutionStats) -> Value {
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

fn capture(
    workspace: &mut ThinSixWorkspace<Float>,
    plan: &ThinSixReductionPlan,
    source_rows: &[Vec<Complex<Float>>],
    ids: &[usize],
) -> DriverResult<Value> {
    let input = KinematicsBatch {
        rows: ids.len(), components: 1,
        values: ids.iter().flat_map(|&id| source_rows[id].iter().cloned()).collect(),
    };
    let before = input.values.iter().map(represented).collect::<DriverResult<Vec<_>>>()?;
    let started = Instant::now();
    let reduced = workspace.reduce_batch(&input);
    let elapsed = started.elapsed().as_secs_f64();
    let stats = workspace.last_execution();
    let empty_reset = ids.is_empty()
        && stats.parent_input_rows == 0 && stats.child_batch_calls == 0
        && stats.packed_child_rows == 0 && stats.parent_batch_calls == 0
        && stats.packed_parent_rows == 0
        && stats.child_execution == ExecutionStats::default()
        && stats.parent_execution == ExecutionStats::default()
        && workspace.last_diagnostics().is_empty();
    let packing_ok = if ids.is_empty() { empty_reset } else {
        stats.parent_input_rows == ids.len() && stats.child_batch_calls == 1
            && stats.packed_child_rows == 6 * ids.len()
            && stats.parent_batch_calls <= 1 && stats.packed_parent_rows <= ids.len()
    };
    let mut record = json!({
        "fixture_indices": ids,
        "rows": ids.len(), "components": 1,
        "diagnostic_reduction_seconds": elapsed,
        "diagnostics": workspace.last_diagnostics(),
        "input_preserved_exactly": before == input.values.iter().map(represented).collect::<DriverResult<Vec<_>>>()?,
        "packing_contract_pass": packing_ok,
        "empty_work_and_diagnostics_reset": if ids.is_empty() { json!(empty_reset) } else { Value::Null },
        "execution": {
            "parent_input_rows": stats.parent_input_rows,
            "child_batch_calls": stats.child_batch_calls,
            "packed_child_rows": stats.packed_child_rows,
            "parent_batch_calls": stats.parent_batch_calls,
            "packed_parent_rows": stats.packed_parent_rows,
            "child_execution": execution(stats.child_execution),
            "parent_execution": execution(stats.parent_execution),
        },
    });
    let result = match reduced {
        Ok(result) => result,
        Err(error) => {
            record["capture_status"] = json!("reduction_api_error");
            record["error"] = json!(error.to_string());
            record["status_shape_contract_pass"] = json!(false);
            record["lanes"] = json!([]);
            return Ok(record);
        }
    };
    let shape_ok = result.rows() == ids.len() && result.components == 1
        && result.basis.as_slice() == plan.basis()
        && result.fallback_used.len() == ids.len()
        && result.analytic_used.len() == ids.len()
        && result.metadata().convention() == Convention::IregiNative
        && result.metadata().tensor_weights() == TensorWeights::Components
        && result.metadata().dual_shape().is_none();
    record["basis"] = json!(result.basis);
    record["metadata"] = json!({
        "convention": format!("{:?}", result.metadata().convention()),
        "tensor_weights": format!("{:?}", result.metadata().tensor_weights()),
        "dual_shape": result.metadata().dual_shape(),
    });
    record["lane_statuses"] = json!(result.statuses.iter().map(|s| format!("{s:?}")).collect::<Vec<_>>());
    record["fallback_used"] = json!(result.fallback_used);
    record["analytic_used"] = json!(result.analytic_used);
    if !shape_ok {
        record["capture_status"] = json!("malformed_result_layout");
        record["status_shape_contract_pass"] = json!(false);
        record["lanes"] = json!([]);
        return Ok(record);
    }
    let mut lanes = Vec::new();
    let mut status_ok = true;
    for (lane, &fixture_index) in ids.iter().enumerate() {
        let expected_success = fixture_index < 2;
        let mut item = json!({
            "row": lane, "fixture_index": fixture_index,
            "expected_outcome": if expected_success { "Success" } else { "explicit_rejection" },
            "status": format!("{:?}", result.statuses[lane]),
            "fallback_used": result.fallback_used[lane],
            "analytic_used": result.analytic_used[lane],
            "moments": null,
        });
        match result.lane(lane) {
            Ok(values) => {
                let complete = values.len() == plan.basis().len() * 4;
                item["complete_native_array"] = json!(complete);
                if complete {
                    item["moments"] = json!(values.chunks_exact(4)
                        .map(|slots| slots.iter().map(represented).collect::<DriverResult<Vec<_>>>())
                        .collect::<DriverResult<Vec<_>>>()?);
                }
                status_ok &= expected_success && complete;
            }
            Err(_) => {
                status_ok &= !expected_success;
                item["complete_native_array"] = json!(false);
            }
        }
        lanes.push(item);
    }
    record["lanes"] = json!(lanes);
    record["capture_status"] = json!("captured");
    record["status_shape_contract_pass"] = json!(status_ok && shape_ok);
    Ok(record)
}

fn compare_to_singletons(case: &Value, baselines: &[Option<Value>; 2]) -> Value {
    let mut comparisons = Vec::new();
    for lane in case["lanes"].as_array().into_iter().flatten() {
        let id = lane["fixture_index"].as_u64().unwrap() as usize;
        if id >= 2 {
            comparisons.push(json!({"row": lane["row"], "fixture_index": id,
                "comparison": "failure_control_not_numerical_agreement"}));
            continue;
        }
        let Some(baseline) = &baselines[id] else {
            comparisons.push(json!({"row": lane["row"], "fixture_index": id,
                "comparison": "successful_singleton_unavailable"}));
            continue;
        };
        if lane["status"] != "Success" || lane["moments"].is_null() {
            comparisons.push(json!({"row": lane["row"], "fixture_index": id,
                "comparison": "successful_current_array_unavailable"}));
            continue;
        }
        let mut differences = Vec::new();
        for (moment, slots) in lane["moments"].as_array().unwrap().iter().enumerate() {
            for (pole, value) in slots.as_array().unwrap().iter().enumerate() {
                let reference = &baseline["moments"][moment][pole];
                for part in ["real", "imaginary"] {
                    let precision = format!("{part}_precision");
                    let negative = format!("{part}_negative");
                    let same_value = value[part] == reference[part];
                    let same_precision = value[&precision] == reference[&precision];
                    let same_sign = value[&negative] == reference[&negative];
                    if !(same_value && same_precision && same_sign) {
                        differences.push(json!({
                            "moment": moment, "laurent_slot": pole, "part": part,
                            "same_exact_value": same_value,
                            "same_precision": same_precision, "same_sign_bit": same_sign,
                            "current": {"value": value[part], "precision": value[&precision], "negative": value[&negative]},
                            "singleton": {"value": reference[part], "precision": reference[&precision], "negative": reference[&negative]},
                        }));
                    }
                }
            }
        }
        comparisons.push(json!({
            "row": lane["row"], "fixture_index": id,
            "comparison": "complete_successful_native_arrays",
            "exact_value_precision_sign_identity": differences.is_empty(),
            "differences": differences,
            "numerical_tolerance_qualification": "deferred_to_independent_normalized_1e-10_qualifier",
        }));
    }
    json!(comparisons)
}

fn run() -> DriverResult<u8> {
    let mut args = std::env::args().skip(1);
    let usage = "thin_n6_lifecycle retained-fixture.json output.json";
    let input_path = args.next().ok_or(usage)?;
    let output_path = args.next().ok_or(usage)?;
    if args.next().is_some() { return Err(usage.into()); }
    let output = Path::new(&output_path);
    let fixture: Value = serde_json::from_str(&std::fs::read_to_string(&input_path)?)?;
    let samples = fixture["samples"].as_array().ok_or("missing samples")?;
    let ids = ["base", "scaled_by_two", "first_mass_squared_plus_one"];
    if samples.len() != 3 || samples.iter().zip(ids).any(|(sample, id)| sample["id"] != id) {
        return Err("expected unchanged three-row retained fixture and ordering".into());
    }
    let prototype = Float::new(128);
    let mut source_rows = Vec::new();
    let mut original_inputs = Vec::new();
    for sample in samples {
        let propagators = sample["propagators"].as_array().ok_or("missing propagators")?;
        if propagators.len() < 6 { return Err("insufficient fixture propagators".into()); }
        let mut input = Vec::with_capacity(31);
        for propagator in &propagators[..6] {
            let shift = propagator["shift"].as_array().ok_or("missing shift")?;
            if shift.len() != 4 { return Err("invalid shift length".into()); }
            for component in shift { input.push((number(component)?, Rational::from(0))); }
        }
        for propagator in &propagators[..6] {
            let mass = propagator["mass_squared"].as_array().ok_or("missing mass")?;
            if mass.len() != 2 || propagator["power"] != 1 {
                return Err("fixture requires complex mass pairs and unit powers".into());
            }
            input.push((number(&mass[0])?, number(&mass[1])?));
        }
        input.push((number(&sample["mu"])?, Rational::from(0)));
        let mut values = Vec::new();
        for (re, im) in &input {
            let value = Complex::new(prototype.from_rational(re), prototype.from_rational(im));
            if value.re.exact_rational().as_ref() != Some(re) || value.im.exact_rational().as_ref() != Some(im) {
                return Err("fixture inputs must be exactly represented at Float128".into());
            }
            values.push(value);
        }
        original_inputs.push(input.iter().map(|(re, im)| [re.to_string(), im.to_string()]).collect::<Vec<_>>());
        source_rows.push(values);
    }
    let mut settings = ReductionSettings::new(6, 2);
    settings.algorithm = Algorithm::PassarinoVeltman;
    let schedule: [(&str, &[usize]); 11] = [
        ("singleton_base", &[0]), ("singleton_scaled", &[1]), ("singleton_singular", &[2]),
        ("empty_after_failure", &[]),
        ("mixed", &[0, 2, 1, 0, 2]), ("reordered", &[2, 0, 1, 2, 0]),
        ("mixed_chunk_first", &[0, 2]), ("mixed_chunk_second", &[1, 0, 2]),
        ("repeated_good", &[0, 1, 0, 1, 0]),
        ("empty_after_repetition", &[]), ("base_after_empty", &[0]),
    ];
    let mut record = json!({
        "schema_version": 1, "status": "preparing_plan",
        "interface": "frozen private ThinSixReductionPlan / ThinSixWorkspace<Float>",
        "settings": settings, "working_bits": 128, "requested_bits": 53,
        "fixture": input_path, "input_exact_rational": original_inputs,
        "expected_successful_fixture_indices": [0, 1], "expected_rejected_fixture_indices": [2],
        "workspace_lifecycle": "one owned workspace reused for every scheduled call",
        "schedule": schedule.iter().map(|(name, indices)| json!({"name":name,"fixture_indices":indices})).collect::<Vec<_>>(),
        "cases": [],
        "qualification_policy": "Exact identity is diagnostic only. All complete successful arrays require independent dimensionally normalized 1e-10 comparison and unchanged original-reference controls. Rejections never establish numerical agreement. Diagnostic timings are not performance measurements.",
    });
    write(output, &record)?;
    let total = Instant::now();
    let plan = match ThinSixReductionPlan::new(settings) {
        Ok(plan) => plan,
        Err(error) => {
            record["status"] = json!("preparation_failed"); record["error"] = json!(error.to_string());
            write(output, &record)?; return Ok(2);
        }
    };
    record["basis"] = json!(plan.basis());
    record["status"] = json!("preparing_workspace");
    write(output, &record)?;
    let mut workspace = match ThinSixWorkspace::new(&plan, prototype) {
        Ok(workspace) => workspace,
        Err(error) => {
            record["status"] = json!("workspace_failed"); record["error"] = json!(error.to_string());
            write(output, &record)?; return Ok(2);
        }
    };
    workspace.set_accuracy_precision(53)?;
    let mut baselines: [Option<Value>; 2] = [None, None];
    let mut contract_pass = true;
    for (index, (name, indices)) in schedule.into_iter().enumerate() {
        record["status"] = json!("reducing_case");
        record["active_case"] = json!({"index":index,"name":name,"fixture_indices":indices});
        record["elapsed_seconds"] = json!(total.elapsed().as_secs_f64());
        write(output, &record)?;
        eprintln!("thin N6 lifecycle case {index}: {name} {indices:?}");
        let mut case = match capture(&mut workspace, &plan, &source_rows, indices) {
            Ok(case) => case,
            Err(error) => {
                record["status"] = json!("capture_failed"); record["error"] = json!(error.to_string());
                write(output, &record)?; return Ok(2);
            }
        };
        case["name"] = json!(name);
        if index < 2 && case["lanes"][0]["status"] == "Success"
            && case["lanes"][0]["complete_native_array"] == true {
            baselines[index] = Some(case["lanes"][0].clone());
        }
        case["singleton_comparisons"] = compare_to_singletons(&case, &baselines);
        // Packing and exact-difference evidence are exported for qualification;
        // the driver's exit status only rejects malformed captures or an
        // unexpected successful/rejected lane classification.
        contract_pass &= case["status_shape_contract_pass"] == true;
        record["cases"].as_array_mut().unwrap().push(case);
        write(output, &record)?;
    }
    record["status"] = json!(if contract_pass { "capture_complete_status_contract_passed" } else { "capture_complete_contract_failed" });
    record["active_case"] = Value::Null;
    record["elapsed_seconds"] = json!(total.elapsed().as_secs_f64());
    record["numerical_tolerance_qualification"] = json!("pending_independent_qualifier");
    write(output, &record)?;
    Ok(if contract_pass { 0 } else { 2 })
}

fn main() -> std::process::ExitCode {
    match run() {
        Ok(code) => std::process::ExitCode::from(code),
        Err(error) => { eprintln!("{error}"); std::process::ExitCode::from(1) }
    }
}
