extern crate self as iregi_masters;
#[derive(Debug)]
pub enum ReductionError { InvalidInput(String), Unsupported(String), Preparation(String), Evaluation(String) }
impl std::fmt::Display for ReductionError { fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { write!(f, "{self:?}") } }
#[derive(Debug)]
pub enum MasterError { InvalidShape(String) }
impl std::fmt::Display for MasterError { fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { write!(f, "{self:?}") } }
#[path = "../crates/iregi-masters/src/dual_validation.rs"] mod dual_validation;
pub use dual_validation::validate_dual_structure;
#[path = "../crates/iregi-rust/src/invariant_certificate.rs"] mod invariant_certificate;
