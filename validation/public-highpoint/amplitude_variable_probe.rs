fn main() {
    assert_eq!(std::env::var("IREGI_AMPLITUDE_VARIABLE_MODE").as_deref(), Ok("verify"), "exact probe requires independent old/new collector verification");
    assert_eq!(std::env::var("IREGI_PRIMAL_SUM_MODE").as_deref(), Ok("verify"), "exact probe requires independent old/new complete amplitude verification");
    let retained = iregi_rust::diagnostic_amplitude_exact_cases();
    let variables = iregi_rust::diagnostic_amplitude_variable_cases();
    println!("{}", serde_json::to_string_pretty(&serde_json::json!({
        "retained_amplitude_cases": retained,
        "variable_and_extra_amplitude_cases": variables,
    })).unwrap());
}
