    #[test]
    fn actual_moment_dispatch_preserves_rank_and_all_laurent_slots() {
        let mut cases=0;
        for n in [6,7] {
            for mode in 0..6 {
                let (mut shifts,masses)=fixture();
                if mode==5 { for p in &mut shifts { p[0]=Atom::new(); } }
                let mut compiler=PvCompiler::new(shifts[..n].to_vec(),masses[..n].to_vec()).unwrap();
                compiler.enable_highpoint_rank_lowering().unwrap();
                let active=(0..n).collect::<Vec<_>>();
                let exponents=match mode {
                    0=>[2,1,3,1], 1=>[0,3,3,1], 2=>[0,0,4,3], 3=>[0,0,0,7],
                    4=>[0,0,0,0], _=>[1,2,3,1],
                };
                let (factors,wanted_child_rank)=if mode<4 {
                    let directions=compiler.highpoint_coordinate_identity(&active).unwrap().unwrap();
                    let mut rest=exponents;rest[mode]-=1;
                    (directions[mode].clone(),rest)
                } else {
                    if mode==5 { assert!(compiler.highpoint_coordinate_identity(&active).unwrap().is_none()); }
                    (compiler.denominator_identity(&active).unwrap(),exponents)
                };
                let mut seeds=Vec::new();
                for i in 0..n {
                    let child=without(&active,i);
                    let values:[Atom;4]=std::array::from_fn(|slot| Atom::var(symbolica::symbol!(format!("rank_lowering::sentinel_{n}_{mode}_{i}_{slot}"))));
                    compiler.moments.insert((child.clone(),wanted_child_rank),values.clone());
                    if wanted_child_rank!=exponents {
                        let wrong:[Atom;4]=std::array::from_fn(|slot| Atom::var(symbolica::symbol!(format!("rank_lowering::wrong_rank_{n}_{mode}_{i}_{slot}"))));
                        compiler.moments.insert((child,exponents),wrong);
                    }
                    seeds.push(values);
                }
                let actual=compiler.moment(&active,exponents).unwrap();
                for slot in 0..4 {
                    let expected=Atom::add_many(&(0..n).map(|i| &factors[i]*&seeds[i][slot]).collect::<Vec<_>>());
                    assert!((&actual[slot]-expected).expand().together().is_zero(),"N={n} mode={mode} slot={slot}");
                }
                assert!(compiler.leaves().is_empty(),"sentinel children should prevent any scalar-master preparation");
                if mode==4 { assert!(compiler.highpoint_coordinate_identities.is_empty(),"rank-zero must retain the old constant path"); }
                cases+=1;
            }
        }
        eprintln!("actual moment dispatch: {cases} cases, {} independent Laurent-slot identities",cases*4);
    }
