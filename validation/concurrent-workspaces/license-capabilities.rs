use symbolica::license::LicenseManager;
fn main() {
    let capabilities = LicenseManager::execution_capabilities();
    println!("licensed={} max_threads={} requested_2={}", capabilities.is_licensed, capabilities.max_threads, LicenseManager::max_threads(2));
    assert!(capabilities.is_licensed);
}
