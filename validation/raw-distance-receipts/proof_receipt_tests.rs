use super::*;
use crate::{Algorithm, Convention, InputPolicy, InvariantInput, ReductionSettings};
use iregi_masters::Float;
use symbolica::domains::float::FloatLike;

fn c(x: f64) -> Complex<f64> {
    Complex::new(x, 0.)
}
fn plan() -> ReductionPlan {
    let mut settings = ReductionSettings::new(2, 0);
    settings.algorithm = Algorithm::Ibp;
    settings.convention = Convention::OneLoop;
    ReductionPlan::new(settings).unwrap()
}
fn row(q: [f64; 4], masses: [f64; 2]) -> Vec<Complex<f64>> {
    [0.; 4]
        .into_iter()
        .chain(q)
        .chain(masses)
        .chain([1.])
        .map(c)
        .collect()
}
fn lightlike_batch() -> KinematicsBatch<f64> {
    KinematicsBatch {
        rows: 1,
        components: 1,
        values: row([1., 1., 0., 0.], [4., 4.]),
    }
}
fn domain(shape: Option<Vec<Vec<usize>>>) -> Arc<RawDistanceProofDomain> {
    let plan = plan();
    let dual = shape.map(HyperDual::<Complex<Rational>>::new);
    Arc::new(RawDistanceProofDomain::new(
        &plan,
        &[(0, 1)],
        &[plan.raw_distances[0][1].clone()],
        dual.as_ref(),
    ))
}

#[test]
fn receipt_domain_requires_complete_ordered_semantics_and_context() {
    let original = domain(Some(vec![vec![0, 0], vec![1, 0], vec![0, 1], vec![1, 1]]));
    let batch = lightlike_batch();
    let receipt = RawDistanceReceipts::new(&batch, original.clone(), 128, 53);
    let incoming = IncomingDistanceReceipts {
        receipt: &receipt,
        source_lanes: &[0],
    };
    assert!(incoming.matches(&original, 128, 53));
    assert!(!incoming.matches(&original, 256, 53));
    assert!(!incoming.matches(&original, 128, 64));
    let mut variants = Vec::new();
    let mut changed = original.as_ref().clone();
    changed.parameters.swap(0, 1);
    variants.push(changed);
    let mut changed = original.as_ref().clone();
    changed.polynomials[0] = Atom::num(0);
    variants.push(changed);
    let mut changed = original.as_ref().clone();
    changed.pairs[0] = (1, 0);
    variants.push(changed);
    let mut changed = original.as_ref().clone();
    changed.layout.scale -= 1;
    variants.push(changed);
    let mut changed = original.as_ref().clone();
    changed.authority = InvariantInput::SuppliedScalarProducts;
    variants.push(changed);
    let mut changed = original.as_ref().clone();
    changed.shape.as_mut().unwrap().swap(1, 2);
    variants.push(changed);
    let mut changed = original.as_ref().clone();
    changed.policy = InputPolicy::legacy_onshell();
    variants.push(changed);
    for changed in variants {
        assert!(!incoming.matches(&changed, 128, 53));
    }
}

#[test]
fn receipt_rows_use_explicit_source_mapping_and_live_batch_identity() {
    let batch = KinematicsBatch {
        rows: 4,
        components: 1,
        values: lightlike_batch().values.repeat(4),
    };
    let identical = batch.clone();
    let mut receipt = RawDistanceReceipts::new(&batch, domain(None), 53, 53);
    receipt.proven[1] = vec![(0, 0)];
    receipt.proven[3] = vec![(0, 2)];
    let incoming = IncomingDistanceReceipts {
        receipt: &receipt,
        source_lanes: &[3, 1, 3],
    };
    assert_eq!(incoming.coverage(0), [(0, 2)]);
    assert_eq!(incoming.coverage(1), [(0, 0)]);
    assert_eq!(incoming.coverage(2), [(0, 2)]);
    assert!(std::ptr::eq(receipt.source, &batch));
    assert!(!std::ptr::eq(receipt.source, &identical));
}

fn check<'a>(
    workspace: &mut Workspace<f64>,
    batch: &'a KinematicsBatch<f64>,
    incoming: Option<&IncomingDistanceReceipts<'_, '_, f64>>,
) -> (
    Vec<(usize, String)>,
    RawDistanceReceipts<'a, f64>,
    DistanceProofWork,
) {
    let width = workspace.parameters * workspace.components;
    let argument_width = workspace.argument_count * workspace.components;
    let mut arguments = vec![c(0.); batch.rows * argument_width];
    workspace
        .arguments
        .evaluate_batch(&batch.values, &mut arguments, batch.rows)
        .unwrap();
    let mut receipt = RawDistanceReceipts::new(
        batch,
        workspace.distance_zeros.as_ref().unwrap().domain.clone(),
        workspace.prototype.get_precision(),
        workspace.accuracy_bits,
    );
    let lanes = (0..batch.rows).collect::<Vec<_>>();
    let mut work = DistanceProofWork::default();
    let failures = workspace
        .distance_zeros
        .as_mut()
        .unwrap()
        .failures(
            &batch.values,
            &arguments,
            width,
            argument_width,
            workspace.components,
            &workspace.prototype,
            workspace.accuracy_bits,
            &lanes,
            incoming,
            Some(&mut receipt),
            &mut work,
        )
        .unwrap();
    (failures, receipt, work)
}

#[test]
fn receipt_partial_selection_certifies_uncovered_complex_taylor_components() {
    let mut p = plan();
    p.special_kinematics = true;
    let dual = HyperDual::<Complex<Rational>>::new(vec![vec![0], vec![1], vec![2]]);
    let mut workspace = Workspace::new_dual(&p, 0., dual).unwrap();
    let mut values = Vec::new();
    for (i, x) in lightlike_batch().values.into_iter().enumerate() {
        values.extend([
            x,
            if i == 4 || i == 5 {
                Complex::new(0., 1.)
            } else {
                c(0.)
            },
            c(0.),
        ]);
    }
    let batch = KinematicsBatch {
        rows: 1,
        components: 3,
        values,
    };
    let (_, full, first) = check(&mut workspace, &batch, None);
    assert_eq!(full.proven[0], [(0, 0), (0, 1), (0, 2)]);
    assert!(first.certificate_rows > 0);
    let mut partial = RawDistanceReceipts::new(&batch, full.domain.clone(), 53, 53);
    partial.proven[0] = vec![(0, 0)];
    let incoming = IncomingDistanceReceipts {
        receipt: &partial,
        source_lanes: &[0],
    };
    let (failures, second, work) = check(&mut workspace, &batch, Some(&incoming));
    assert!(failures.is_empty(), "{failures:?}");
    assert_eq!(second.proven[0], full.proven[0]);
    assert_eq!(work.reused_pairs, 1);
    assert_eq!(
        workspace.distance_zeros.as_ref().unwrap().selected,
        [vec![(0, 1), (0, 2)]]
    );
    assert!(work.certificate_rows > 0);
    let incoming = IncomingDistanceReceipts {
        receipt: &full,
        source_lanes: &[0],
    };
    let (failures, third, work) = check(&mut workspace, &batch, Some(&incoming));
    assert!(failures.is_empty());
    assert_eq!(third.proven[0], full.proven[0]);
    assert_eq!(work.reused_pairs, 3);
    assert_eq!(work.covered_rows, 1);
    assert_eq!(work.certificate_rows, 0);
}

#[test]
fn receipt_precision_context_mismatch_runs_a_fresh_certificate() {
    let p = plan();
    let mut workspace = Workspace::new(&p, 0.).unwrap();
    let batch = lightlike_batch();
    let (_, receipt, _) = check(&mut workspace, &batch, None);
    workspace.set_accuracy_precision(52).unwrap();
    let incoming = IncomingDistanceReceipts {
        receipt: &receipt,
        source_lanes: &[0],
    };
    let (failures, _, work) = check(&mut workspace, &batch, Some(&incoming));
    assert!(failures.is_empty());
    assert_eq!(work.reused_pairs, 0);
    assert!(work.certificate_rows > 0);
    // A high-precision workspace does not upgrade lower-precision represented
    // operands or cap the requested accuracy. This is an independent control.
    let prototype = Float::new(256);
    let mut precise = Workspace::new(&p, prototype).unwrap();
    let weak = KinematicsBatch {
        rows: 1,
        components: 1,
        values: batch
            .values
            .iter()
            .map(|v| Complex::new(Float::with_val(80, v.re), Float::with_val(80, v.im)))
            .collect(),
    };
    let result = precise.reduce_batch(&weak).unwrap();
    assert!(
        matches!(result.statuses[0], LaneStatus::Unstable(_)),
        "{:?}",
        result.statuses
    );
}

#[test]
fn receipt_compaction_reordering_calls_and_clones_preserve_outputs_and_work_counts() {
    let p = plan();
    let mut workspace = Workspace::new(&p, 0.).unwrap();
    let large = 134_217_728.;
    let previous = large - 2_f64.powi(-26);
    let mut invalid = lightlike_batch().values;
    invalid[10] = c(-1.);
    let rows = vec![
        invalid,
        row([large, previous, 2., 0.], [0., 0.]),
        row([1., 1., 0., 0.], [4., 4.]),
        row([1., 1., 0., 0.], [4., 9.]),
        row([0., 1., 0., 0.], [4., 9.]),
    ];
    let batch = KinematicsBatch {
        rows: 5,
        components: 1,
        values: rows.concat(),
    };
    let result = workspace.reduce_batch(&batch).unwrap();
    assert!(matches!(result.statuses[0], LaneStatus::InvalidInput(_)));
    assert!(matches!(result.statuses[1], LaneStatus::Unstable(_)));
    assert_eq!(result.statuses[2..], vec![LaneStatus::Success; 3]);
    assert_eq!(result.analytic_used, [false, false, true, true, false]);
    assert_eq!(workspace.proof_work.reused_pairs, 2);
    assert_eq!(workspace.proof_work.covered_rows, 2);
    assert_eq!(workspace.last_execution().argument_rows, 6);
    let work = workspace.proof_work;
    let again = workspace.reduce_batch(&batch.clone()).unwrap();
    assert_eq!(again.values, result.values);
    assert_eq!(again.statuses, result.statuses);
    assert_eq!(workspace.proof_work, work); // each public call proves its own parent rows
    let mut clone = workspace.clone();
    let again = clone.reduce_batch(&batch).unwrap();
    assert_eq!(again.values, result.values);
    assert_eq!(clone.proof_work, work);
    let order = [4, 3, 0, 2, 1];
    let reordered = KinematicsBatch {
        rows: 5,
        components: 1,
        values: order.iter().flat_map(|&i| rows[i].clone()).collect(),
    };
    let permuted = workspace.reduce_batch(&reordered).unwrap();
    for (i, &source) in order.iter().enumerate() {
        assert_eq!(permuted.statuses[i], result.statuses[source]);
        assert_eq!(permuted.analytic_used[i], result.analytic_used[source]);
        if result.statuses[source] == LaneStatus::Success {
            assert_eq!(permuted.lane(i).unwrap(), result.lane(source).unwrap());
        }
    }
    assert_eq!(workspace.proof_work, work);
}

#[test]
fn receipt_legacy_policy_never_creates_reusable_coverage() {
    let mut settings = ReductionSettings::new(2, 0);
    settings.input_policy = InputPolicy::legacy_onshell();
    let p = ReductionPlan::new(settings).unwrap();
    let mut workspace = Workspace::new(&p, 0.).unwrap();
    assert!(!workspace.distance_zeros.as_ref().unwrap().domain.reusable());
    let result = workspace.reduce_batch(&lightlike_batch()).unwrap();
    assert_eq!(result.statuses[0], LaneStatus::Success);
    assert_eq!(workspace.proof_work.reused_pairs, 0);
    assert_eq!(workspace.proof_work.covered_rows, 0);
}

#[test]
fn receipt_exact_zero_component_cannot_skip_other_component_conditioning() {
    let mut p = plan();
    p.special_kinematics = true;
    let dual = HyperDual::<Complex<Rational>>::new(vec![vec![0], vec![1]]);
    let mut workspace = Workspace::new_dual(&p, 0., dual).unwrap();
    let large = 134_217_728.;
    let previous = large - 2_f64.powi(-26);
    let mut values = Vec::new();
    for (i, x) in lightlike_batch().values.into_iter().enumerate() {
        values.extend([
            x,
            c(if i == 4 {
                large
            } else if i == 5 {
                previous
            } else {
                0.
            }),
        ]);
    }
    let batch = KinematicsBatch {
        rows: 1,
        components: 2,
        values,
    };
    // Establish a genuine exact proof of the primal component independently.
    // Its transverse component is nonzero and badly conditioned; the proof
    // alone never grants permission to skip that independent child monitor.
    let exact = batch
        .values
        .iter()
        .map(|v| {
            Complex::new(
                v.re.exact_rational().unwrap(),
                v.im.exact_rational().unwrap(),
            )
        })
        .collect::<Vec<_>>();
    let certificates = workspace
        .distance_zeros
        .as_mut()
        .unwrap()
        .certificate
        .check_selected_batch(&exact, 1, &[vec![(0, 0)]])
        .unwrap();
    assert_eq!(certificates, [ExactZeroCertificate::Zero]);
    let mut receipt = RawDistanceReceipts::new(
        &batch,
        workspace.distance_zeros.as_ref().unwrap().domain.clone(),
        53,
        53,
    );
    receipt.proven[0] = vec![(0, 0)];
    let incoming = IncomingDistanceReceipts {
        receipt: &receipt,
        source_lanes: &[0],
    };
    let (failures, outgoing, work) = check(&mut workspace, &batch, Some(&incoming));
    assert_eq!(failures.len(), 1);
    assert!(
        failures[0].1.contains("derived distance") && failures[0].1.contains("Taylor component 1"),
        "{failures:?}"
    );
    assert!(outgoing.proven[0].is_empty());
    assert_eq!(work.reused_pairs, 0);
    assert_eq!(work.certificate_rows, 0);
}

#[test]
fn receipt_partial_coverage_cannot_hide_new_false_zero_component() {
    let mut p = plan();
    p.special_kinematics = true;
    let dual = HyperDual::<Complex<Rational>>::new(vec![vec![0], vec![1], vec![2]]);
    let mut workspace = Workspace::new_dual(&p, 0., dual).unwrap();
    let large = 134_217_728.;
    let previous = large - 2_f64.powi(-26);
    let tangent = [large, previous, 2., 0.];
    let mut values = Vec::new();
    for (i, x) in row([0.; 4], [4., 4.]).into_iter().enumerate() {
        values.extend([
            x,
            c(if (4..8).contains(&i) {
                tangent[i - 4]
            } else {
                0.
            }),
            c(0.),
        ]);
    }
    let batch = KinematicsBatch {
        rows: 1,
        components: 3,
        values,
    };
    let exact = batch
        .values
        .iter()
        .map(|v| {
            Complex::new(
                v.re.exact_rational().unwrap(),
                v.im.exact_rational().unwrap(),
            )
        })
        .collect::<Vec<_>>();
    let certificates = workspace
        .distance_zeros
        .as_mut()
        .unwrap()
        .certificate
        .check_selected_batch(&exact, 1, &[vec![(0, 0), (0, 1)]])
        .unwrap();
    assert_eq!(certificates, [ExactZeroCertificate::Zero]);
    let mut receipt = RawDistanceReceipts::new(
        &batch,
        workspace.distance_zeros.as_ref().unwrap().domain.clone(),
        53,
        53,
    );
    receipt.proven[0] = vec![(0, 0), (0, 1)];
    let incoming = IncomingDistanceReceipts {
        receipt: &receipt,
        source_lanes: &[0],
    };
    let (failures, outgoing, work) = check(&mut workspace, &batch, Some(&incoming));
    assert_eq!(failures.len(), 1);
    assert!(
        failures[0].1.contains("rounded-zero distance")
            && failures[0].1.contains("Taylor component 2")
            && failures[0].1.contains("exact represented"),
        "{failures:?}"
    );
    assert!(outgoing.proven[0].is_empty());
    assert_eq!(work.reused_pairs, 2);
    assert!(work.certificate_rows > 0);
    assert_eq!(
        workspace.distance_zeros.as_ref().unwrap().selected,
        [vec![(0, 2)]]
    );
}

#[test]
fn receipt_dispatch_requires_the_same_source_object_not_equal_values() {
    let p = plan();
    let mut parent = Workspace::new(&p, 0.).unwrap();
    let batch = lightlike_batch();
    let expected = parent.reduce_batch(&batch).unwrap();
    let (_, receipt, _) = check(&mut parent, &batch, None);
    let child_plan = ReductionPlan::lightlike_bubble(p.settings.clone(), 0, true).unwrap();
    let mut child = Workspace::new(&child_plan, 0.).unwrap();
    let identical = batch.clone();
    for (source, expected_reuse) in [(&identical, 0), (&batch, 1)] {
        let mut result = expected.clone();
        let mut stats = ExecutionStats::default();
        let mut profile = ExecutionProfile::default();
        let mut diagnostics = vec![Vec::new()];
        let mut work = DistanceProofWork::default();
        dispatch_profile(
            &mut child,
            &[0],
            source,
            &mut result,
            &mut stats,
            &mut profile,
            &mut diagnostics,
            Some(&receipt),
            &mut work,
        )
        .unwrap();
        assert_eq!(result.values, expected.values);
        assert_eq!(result.statuses, expected.statuses);
        assert_eq!(work.reused_pairs, expected_reuse);
        assert_eq!(work.certificate_rows, 1 - expected_reuse);
    }
}

#[test]
fn receipt_recursive_transfer_rekeys_masks_to_each_child_local_batch() {
    let mut p = plan();
    p.special_kinematics = true;
    let dual = HyperDual::<Complex<Rational>>::new(vec![vec![0], vec![1]]);
    let mut workspace = Workspace::new_dual(&p, 0., dual).unwrap();
    let make_row = |zero_tangent: bool| {
        lightlike_batch()
            .values
            .into_iter()
            .enumerate()
            .flat_map(|(i, x)| {
                [
                    x,
                    c(if i == 4 || (zero_tangent && i == 5) {
                        1.
                    } else {
                        0.
                    }),
                ]
            })
            .collect::<Vec<_>>()
    };
    let rows = [
        make_row(true),
        make_row(false),
        make_row(true),
        make_row(false),
    ];
    let batch = KinematicsBatch {
        rows: 4,
        components: 2,
        values: rows.concat(),
    };
    let (failures, parent, first) = check(&mut workspace, &batch, None);
    assert!(failures.is_empty());
    assert_eq!(first.certificate_rows, 4);
    assert_eq!(parent.proven[0], [(0, 0), (0, 1)]);
    assert_eq!(parent.proven[3], [(0, 0)]);
    let child_lanes = [3, 0];
    let child_batch = KinematicsBatch {
        rows: 2,
        components: 2,
        values: [rows[3].clone(), rows[0].clone()].concat(),
    };
    let incoming = IncomingDistanceReceipts {
        receipt: &parent,
        source_lanes: &child_lanes,
    };
    let (failures, child, work) = check(&mut workspace, &child_batch, Some(&incoming));
    assert!(failures.is_empty());
    assert_eq!(work.reused_pairs, 3);
    assert_eq!(work.certificate_rows, 0);
    assert!(std::ptr::eq(child.source, &child_batch));
    assert_eq!(child.proven[0], [(0, 0)]);
    assert_eq!(child.proven[1], [(0, 0), (0, 1)]);
    let grandchild = KinematicsBatch {
        rows: 1,
        components: 2,
        values: rows[0].clone(),
    };
    let incoming = IncomingDistanceReceipts {
        receipt: &child,
        source_lanes: &[1],
    };
    let (failures, proof, work) = check(&mut workspace, &grandchild, Some(&incoming));
    assert!(failures.is_empty());
    assert_eq!(work.reused_pairs, 2);
    assert_eq!(work.certificate_rows, 0);
    assert_eq!(proof.proven[0], [(0, 0), (0, 1)]);
    assert!(std::ptr::eq(proof.source, &grandchild));
}
