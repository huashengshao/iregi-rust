//! Isolated equivalence qualification, not a production implementation.
//! Both complete scalar compilers use the same deterministic master symbols.
//! The comparison is exact Symbolica algebra, not a physical numerical oracle.
#![allow(dead_code)]

#[path = "alias-source/crates/iregi-rust/src/ibp.rs"]
mod baseline;
#[path = "vector-source/crates/iregi-rust/src/ibp.rs"]
mod candidate;

use symbolica::atom::{Atom, AtomCore};

fn regular_r(n: usize) -> Vec<Vec<Atom>> {
    // R = -u u^T - I: every principal submatrix is negative definite.
    // This is an analytic scalar-domain fixture, not a real-Minkowski oracle.
    (0..n)
        .map(|i| {
            (0..n)
                .map(|j| Atom::num(-(((i + 2) * (j + 2)) as i64) - i64::from(i == j)))
                .collect()
        })
        .collect()
}

#[test]
fn regular_unit_power_recurrences_match_full_inverse_for_all_shifts() {
    let mut successes = 0;
    let mut expected_errors = 0;
    for n in 1..=5 {
        for h in -3..=4 {
            for e6 in [false, true] {
                if e6 && n != 5 {
                    continue;
                }
                // Fresh caches are essential: a prior raised-power request
                // would precompute the full inverse and mask the new path.
                let mut old = baseline::ScalarCompiler::new(regular_r(n)).unwrap();
                let mut new = candidate::ScalarCompiler::new(regular_r(n)).unwrap();
                if e6 {
                    old.enable_six_dimensional_pentagon().unwrap();
                    new.enable_six_dimensional_pentagon().unwrap();
                }
                let before = old.compile(baseline::ScalarRequest {
                    powers: vec![1; n],
                    dimension_shift: h,
                });
                let after = new.compile(candidate::ScalarRequest {
                    powers: vec![1; n],
                    dimension_shift: h,
                });
                match (before, after) {
                    (Ok(before), Ok(after)) => {
                        assert!(!(n == 5 && h > 0 && !e6));
                        for slot in 0..4 {
                            assert!(
                                (&before[slot] - &after[slot]).together().is_zero(),
                                "N={n}, h={h}, E6={e6}, slot={slot}: {} versus {}",
                                before[slot], after[slot]
                            );
                        }
                        successes += 1;
                    }
                    (Err(before), Err(after)) => {
                        assert!(n == 5 && h > 0 && !e6, "unexpected failure: {before}");
                        assert_eq!(before, after, "N={n}, h={h}, E6={e6}");
                        expected_errors += 1;
                    }
                    (before, after) => panic!(
                        "N={n}, h={h}, E6={e6}: baseline {before:?}, candidate {after:?}"
                    ),
                }
            }
        }
    }
    assert_eq!(successes, 44);
    assert_eq!(expected_errors, 4);
    eprintln!("exact regular-R comparison: {successes} successful requests x 4 slots; {expected_errors} matching unsupported requests");
}

#[test]
fn regular_constrained_triangle_and_box_remain_original_master_leaves() {
    // p0=0, p1=ex, p2=ey, p3=ez and m^2=(0,9,16,25).
    // The zero mass is an exact structural constraint; neither full R nor B
    // vanishes. The constrained-profile dispatch must preserve C0/D0.
    let rows = [
        [0, -10, -17, -26],
        [-10, -18, -27, -36],
        [-17, -27, -32, -43],
        [-26, -36, -43, -50],
    ];
    for n in [3, 4] {
        let r: Vec<Vec<Atom>> = rows[..n]
            .iter()
            .map(|row| row[..n].iter().map(|&entry| Atom::num(entry)).collect())
            .collect();
        let mask: Vec<_> = (0..n).map(|i| i == 0).collect();
        let mut old = baseline::ScalarCompiler::with_zero_invariants(r.clone(), &mask, &[]).unwrap();
        let mut new = candidate::ScalarCompiler::with_zero_invariants(r, &mask, &[]).unwrap();
        let before = old.compile(baseline::ScalarRequest {
            powers: vec![1; n], dimension_shift: 0,
        }).unwrap();
        let after = new.compile(candidate::ScalarRequest {
            powers: vec![1; n], dimension_shift: 0,
        }).unwrap();
        assert_eq!(old.leaves.len(), 1);
        assert_eq!(new.leaves.len(), 1);
        assert_eq!(old.leaves[0].active, (0..n).collect::<Vec<_>>());
        assert_eq!(new.leaves[0].active, old.leaves[0].active);
        assert_eq!(old.leaves[0].kind, baseline::MasterLeafKind::FourDimensional);
        assert_eq!(new.leaves[0].kind, candidate::MasterLeafKind::FourDimensional);
        for slot in 0..4 {
            assert!((&before[slot] - &old.leaves[0].slots[slot]).together().is_zero());
            assert!((&after[slot] - &new.leaves[0].slots[slot]).together().is_zero());
            assert!((&before[slot] - &after[slot]).together().is_zero());
        }
    }
}
