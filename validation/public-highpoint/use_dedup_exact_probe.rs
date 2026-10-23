fn main() {
    let results=iregi_rust::diagnostic_alias_use_cases();
    println!("{}",serde_json::to_string_pretty(&results).unwrap());
}
