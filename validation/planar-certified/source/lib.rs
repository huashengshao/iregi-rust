//! Batched one-loop tensor integral reduction.
//!
//! Graph import and numerator preparation belong to `iregi-prepare`.
#![forbid(unsafe_code)]

pub mod basis;
pub mod certified_planar;
pub mod certified_scalar;
pub mod contraction;
mod convention;
mod exact_zero_certificate;
pub mod execution;
pub mod ibp;
mod invariant_certificate;
pub mod plan;
pub mod pv;
pub mod rescue;
pub mod scalar;
pub mod snapping;
mod stability;
pub mod types;
pub use certified_planar::{CertifiedPlanarReductionPlan, CertifiedPlanarWorkspace};
pub use certified_scalar::{
    CertificateExecutionStats, CertifiedScalarReductionPlan, CertifiedScalarWorkspace,
};
pub use contraction::{ContractionPlan, ContractionResult, ContractionWorkspace, NumeratorBatch};
pub use execution::{ExecutionProfile, ExecutionStats, Workspace, reduce_batch};
pub use invariant_certificate::ExactInvariantScalar;
pub use plan::ReductionPlan;
pub use rescue::{
    PrecisionRescueWorkspace, RescueScalar, RescueSettings, RescueStats, RescueStatus,
    RescueTrigger,
};
pub use scalar::{ScalarKinematicsBatch, ScalarReductionPlan, ScalarWorkspace};
pub use types::*;
