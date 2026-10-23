
#[cfg(test)]
mod highpoint_rank_lowering_tests {
    use super::*;

    fn fixture() -> (Vec<[Atom; 4]>, Vec<Atom>) {
        let points = [
            [0, 0, 0, 0], [0, 2, 0, 0], [0, 0, 2, 0],
            [0, 0, 0, 2], [1, 0, 0, 0], [0, 2, 2, 0], [0, 0, 2, 2],
        ];
        (points.iter().map(|p| p.map(|v| Atom::num(v) / Atom::num(2))).collect(),
         [1, 2, 3, 4, 2, 3, 4].into_iter().map(Atom::num).collect())
    }

    fn assert_identity(shifts: Vec<[Atom; 4]>, masses: Vec<Atom>, active: &[usize]) {
        let mut compiler = PvCompiler::new(shifts.clone(), masses.clone()).unwrap();
        compiler.enable_highpoint_rank_lowering().unwrap();
        let weights = compiler.highpoint_coordinate_identity(active).unwrap().expect("regular fixture");
        let q: [Atom; 4] = std::array::from_fn(|mu| Atom::var(symbolica::symbol!(format!("rank_lowering::q{mu}"))));
        let q_perp_squared = Atom::var(symbolica::symbol!("rank_lowering::q_perp_squared"));
        let denominators: Vec<_> = active.iter().map(|&i| {
            let shifted = std::array::from_fn(|mu| &q[mu] + &shifts[i][mu]);
            dot(&shifted, &shifted) + &q_perp_squared - &masses[i]
        }).collect();
        for mu in 0..4 {
            assert!(Atom::add_many(&weights[mu]).together().is_zero());
            for nu in 0..4 {
                let sum = Atom::add_many(&active.iter().zip(&weights[mu]).map(|(&i, w)|
                    w * &shifts[i][nu] * Atom::num(if nu == 0 { 2 } else { -2 })
                ).collect::<Vec<_>>());
                assert!((sum - Atom::num(i64::from(mu == nu))).together().is_zero());
            }
            let constant = Atom::add_many(&active.iter().zip(&weights[mu]).map(|(&i, w)|
                w * (dot(&shifts[i], &shifts[i]) - &masses[i])
            ).collect::<Vec<_>>());
            assert!(constant.together().is_zero());
            let rhs = Atom::add_many(&denominators.iter().zip(&weights[mu]).map(|(d, w)| d * w).collect::<Vec<_>>());
            assert!((&rhs - &q[mu]).expand().together().is_zero(), "direction {mu}");
            for w in &weights[mu] {
                assert!(!w.get_all_indeterminates(true).iter().any(|v| *v == q_perp_squared.as_view()));
                for component in &q { assert!(!w.get_all_indeterminates(true).iter().any(|v| *v == component.as_view())); }
            }
            // Nonuniform rank-seven monomials: no combinatorial factors are
            // introduced when one Cartesian component is removed.
            let mut exponents = [1, 2, 3, 1];
            exponents[mu] -= 1;
            let rest = monomial(&q, &exponents);
            assert!((rest * (&rhs - &q[mu])).expand().together().is_zero());
        }
        let old_scalar = compiler.denominator_identity(active).unwrap();
        let rhs = Atom::add_many(&denominators.iter().zip(&old_scalar).map(|(d, w)| d * w).collect::<Vec<_>>());
        assert!((rhs - Atom::num(1)).expand().together().is_zero());
    }

    #[test]
    fn cartesian_integrand_identity_all_directions_and_routes() {
        let (base, masses) = fixture();
        let mut count = 0;
        for n in [6, 7] {
            for variant in 0..7 {
                let mut p = base[..n].to_vec();
                let mut m = masses[..n].to_vec();
                match variant {
                    1 => { for q in &mut p { for c in q { *c = &*c * Atom::num(2); } } for mass in &mut m { *mass = &*mass * Atom::num(4); } },
                    2 => m[0] = &m[0] + Atom::num(1),
                    3 => for q in &mut p { for (mu, c) in q.iter_mut().enumerate() { *c = &*c + Atom::num((mu + 1) as i64) / Atom::num(3); } },
                    4 => for q in &mut p { for c in q { *c = -&*c; } },
                    5 => { p.reverse(); m.reverse(); },
                    6 => for (i, mass) in m.iter_mut().enumerate() { *mass = &*mass - Atom::i() * Atom::num((i + 1) as i64) / Atom::num(16); },
                    _ => (),
                }
                assert_identity(p, m, &(0..n).collect::<Vec<_>>());
                count += 1;
            }
        }
        // Pinching original line zero changes the origin used by the RHS.
        assert_identity(base, masses, &[1, 2, 3, 4, 5, 6]);
        count += 1;
        eprintln!("exact Cartesian integrand fixtures={count}, directions={}, six constraints plus qperp identity and rank7 monomial per direction", count * 4);
    }

    #[test]
    fn structural_deficiency_retains_old_constant_identity() {
        let (mut shifts, masses) = fixture();
        for p in &mut shifts { p[0] = Atom::new(); }
        let mut compiler = PvCompiler::new(shifts[..6].to_vec(), masses[..6].to_vec()).unwrap();
        compiler.enable_highpoint_rank_lowering().unwrap();
        assert!(compiler.highpoint_coordinate_identity(&[0, 1, 2, 3, 4, 5]).unwrap().is_none());
        assert!(compiler.denominator_identity(&[0, 1, 2, 3, 4, 5]).is_ok());
        let (shifts, _) = fixture();
        let masses = shifts.iter().map(|p| dot(p, p) + Atom::num(1)).collect();
        let mut compiler = PvCompiler::new(shifts, masses).unwrap();
        compiler.enable_highpoint_rank_lowering().unwrap();
        for n in [6, 7] {
            let active = (0..n).collect::<Vec<_>>();
            assert!(compiler.highpoint_coordinate_identity(&active).unwrap().is_none());
            assert!(compiler.denominator_identity(&active).is_err());
        }
    }

    #[test]
    fn direct_supplied_distances_keep_policy_disabled() {
        let (shifts, masses) = fixture();
        let distances = shifts.iter().map(|p| shifts.iter().map(|q| {
            let delta = std::array::from_fn(|mu| &p[mu] - &q[mu]); dot(&delta, &delta)
        }).collect()).collect();
        let compiler = PvCompiler::with_distances(shifts, masses, distances, true).unwrap();
        assert!(!compiler.highpoint_rank_lowering);
        assert!(!compiler.coordinate_identities);
    }
}
