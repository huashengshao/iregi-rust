fn main() {
    let result=iregi_rust::diagnostic_amplitude_exact_cases();
    println!("{}",serde_json::to_string_pretty(&result).unwrap());
}
