//! Call-local exact raw-distance zero-proof coverage for analytic children.

use super::*;
use crate::types::{InputPolicy, InvariantInput};

/// Exact ordered semantics, independent of any evaluated sample.
#[derive(Clone, Debug, PartialEq, Eq)]
pub(super) struct RawDistanceProofDomain {
    pub(super) parameters: Vec<Atom>,
    pub(super) polynomials: Vec<Atom>,
    pub(super) pairs: Vec<(usize, usize)>,
    pub(super) layout: InputLayout,
    pub(super) authority: InvariantInput,
    pub(super) shape: Option<Vec<Vec<usize>>>,
    pub(super) policy: InputPolicy,
}

impl RawDistanceProofDomain {
    pub(super) fn new<D: DualNumberStructure>(
        plan: &ReductionPlan,
        pairs: &[(usize, usize)],
        polynomials: &[Atom],
        dual: Option<&D>,
    ) -> Self {
        Self {
            parameters: plan.parameters.clone(),
            polynomials: polynomials.to_vec(),
            pairs: pairs.to_vec(),
            layout: plan.layout.clone(),
            authority: plan.settings.invariants,
            shape: dual.map(|d| d.get_shape().into_iter().map(<[usize]>::to_vec).collect()),
            policy: plan.settings.input_policy.clone(),
        }
    }

    pub(super) fn reusable(&self) -> bool {
        self.policy == InputPolicy::Preserve
    }
}

/// This value borrows one immutable original local batch and cannot survive
/// the call. Masks are indexed by that batch's original row, never a compact row.
pub(super) struct RawDistanceReceipts<'source, T: NativeFloat> {
    pub(super) source: &'source KinematicsBatch<T>,
    pub(super) domain: Arc<RawDistanceProofDomain>,
    pub(super) working_bits: u32,
    pub(super) accuracy_bits: u32,
    pub(super) proven: Vec<Vec<(usize, usize)>>,
}

impl<'source, T: NativeFloat> RawDistanceReceipts<'source, T> {
    pub(super) fn new(
        source: &'source KinematicsBatch<T>,
        domain: Arc<RawDistanceProofDomain>,
        working_bits: u32,
        accuracy_bits: u32,
    ) -> Self {
        Self {
            source,
            domain,
            working_bits,
            accuracy_bits,
            proven: vec![Vec::new(); source.rows],
        }
    }
}

/// Only dispatch_profile constructs this view, immediately after cloning exactly
/// these source rows into the child batch. The source identity check precedes
/// construction; there is no numerical equality or persistent input cache.
pub(super) struct IncomingDistanceReceipts<'receipt, 'source, T: NativeFloat> {
    pub(super) receipt: &'receipt RawDistanceReceipts<'source, T>,
    pub(super) source_lanes: &'receipt [usize],
}

impl<T: NativeFloat> IncomingDistanceReceipts<'_, '_, T> {
    pub(super) fn matches(
        &self,
        domain: &RawDistanceProofDomain,
        working_bits: u32,
        accuracy_bits: u32,
    ) -> bool {
        domain.reusable()
            && self.receipt.domain.as_ref() == domain
            && self.receipt.working_bits == working_bits
            && self.receipt.accuracy_bits == accuracy_bits
    }

    pub(super) fn coverage(&self, local_row: usize) -> &[(usize, usize)] {
        &self.receipt.proven[self.source_lanes[local_row]]
    }
}

/// Private instrumentation only; ordinary public ExecutionStats stay unchanged.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub(super) struct DistanceProofWork {
    pub(super) certificate_rows: usize,
    pub(super) certificate_passes: usize,
    pub(super) reused_pairs: usize,
    pub(super) covered_rows: usize,
}

impl DistanceProofWork {
    pub(super) fn add(&mut self, other: Self) -> Result<(), ReductionError> {
        self.certificate_rows = self
            .certificate_rows
            .checked_add(other.certificate_rows)
            .ok_or_else(size_error)?;
        self.certificate_passes = self
            .certificate_passes
            .checked_add(other.certificate_passes)
            .ok_or_else(size_error)?;
        self.reused_pairs = self
            .reused_pairs
            .checked_add(other.reused_pairs)
            .ok_or_else(size_error)?;
        self.covered_rows = self
            .covered_rows
            .checked_add(other.covered_rows)
            .ok_or_else(size_error)?;
        Ok(())
    }
}
