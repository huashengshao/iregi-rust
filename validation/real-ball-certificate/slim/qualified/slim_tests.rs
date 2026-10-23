#![allow(dead_code)]
use symbolica::{atom::{Atom,AtomCore},domains::{float::{Complex,SingleFloat},rational::Rational}};
pub use iregi_rust::ReductionError;
#[path="original.rs"] mod baseline;
#[path="slim.rs"] mod candidate;
fn c(x:i64)->Complex<Rational>{Complex::new(Rational::from(x),Rational::from(0))}
fn parameters()->Vec<Atom>{["x","y"].iter().map(|s|Atom::parse(s,"certificate_comparison",Default::default()).unwrap()).collect()}
fn plain_plans()->(baseline::InvariantCertificatePlan,candidate::InvariantCertificatePlan){let p=parameters();let r=[&p[0]-&p[1],p[0].pow(2)-p[1].pow(2)];(baseline::InvariantCertificatePlan::from_zero_polynomials(&p,&r,None).unwrap(),candidate::InvariantCertificatePlan::from_zero_polynomials(&p,&r,None).unwrap())}
fn basestatus(x:&baseline::InvariantCertificate)->String{match x{baseline::InvariantCertificate::Compatible{basis}=>format!("zero:{basis:?}"),baseline::InvariantCertificate::Incompatible{basis,pair,component,residual}=>{assert!(!residual.contains_zero());format!("nonzero:{basis:?}:{pair:?}:{component}")},baseline::InvariantCertificate::Unresolved{working_bits}=>format!("unresolved:{working_bits}"),baseline::InvariantCertificate::NoRegularChart=>"nochart".into()}}
fn candstatus(x:&candidate::InvariantCertificate)->String{match x{candidate::InvariantCertificate::Compatible{basis}=>format!("zero:{basis:?}"),candidate::InvariantCertificate::Incompatible{basis,pair,component,residual}=>{assert!(!residual.contains_zero());format!("nonzero:{basis:?}:{pair:?}:{component}")},candidate::InvariantCertificate::Unresolved{working_bits}=>format!("unresolved:{working_bits}"),candidate::InvariantCertificate::NoRegularChart=>"nochart".into()}}
fn same(a:&[baseline::InvariantCertificate],b:&[candidate::InvariantCertificate]){assert_eq!(a.iter().map(basestatus).collect::<Vec<_>>(),b.iter().map(candstatus).collect::<Vec<_>>());}
#[test]
fn partitioned_batch_matches_complex_reference_and_retains_refinement(){
 let (pa,pb)=plain_plans();let mut a=pa.instantiate();let mut b=pb.instantiate();
 let mut tiny=c(1);tiny.re+=Rational::from((1,2)).pow(300);
 let z=Complex::new(Rational::from(1),Rational::from(1));
 let mut tiny_im=z.clone();tiny_im.im+=Rational::from((1,2)).pow(300);
 let input=[vec![c(1),c(1)],vec![z.clone(),z.clone()],vec![tiny,c(1)],vec![z.clone(),c(1)],vec![tiny_im,z],vec![c(9),c(0)]].concat();
 let masks=vec![vec![(0,0),(1,0)],vec![(0,0),(1,0)],vec![(0,0)],vec![(0,0)],vec![(0,0)],vec![]];
 for bits in [128,1024] {a.set_precision_budget(128,bits).unwrap();b.set_precision_budget(128,bits).unwrap();let ra=a.check_selected_batch(&input,6,&masks).unwrap();let rb=b.check_selected_batch(&input,6,&masks).unwrap();same(&ra,&rb);assert_eq!(a.evaluated_rows(),b.evaluated_rows());assert_eq!(a.passes(),b.passes());if bits==128 {assert!(matches!(rb[2],candidate::InvariantCertificate::Unresolved{..}));}else{assert!(matches!(rb[2],candidate::InvariantCertificate::Incompatible{..}));}}
 assert!(a.check_batch(&[],0).unwrap().is_empty());assert!(b.check_batch(&[],0).unwrap().is_empty());
}
#[test]
fn nonbinary_rational_equality_remains_uncertified(){
 let (pa,pb)=plain_plans();let mut a=pa.instantiate();let mut b=pb.instantiate();a.set_precision_budget(128,256).unwrap();b.set_precision_budget(128,256).unwrap();
 let q=Complex::new(Rational::from((1,3)),Rational::from(0));let input=[q.clone(),q];let ra=a.check_batch(&input,1).unwrap();let rb=b.check_batch(&input,1).unwrap();same(&ra,&rb);assert!(matches!(rb[0],candidate::InvariantCertificate::Unresolved{working_bits:256}));
}
#[test]
fn full_mixed_dual_shape_and_complex_jets_keep_axes_distinct(){
 let p=parameters();let r=[&p[0]-&p[1],p[0].pow(2)-p[1].pow(2)];let shape=Some(vec![vec![0,0],vec![0,1],vec![1,0],vec![1,1]]);
 let pa=baseline::InvariantCertificatePlan::from_zero_polynomials(&p,&r,shape.clone()).unwrap();let pb=candidate::InvariantCertificatePlan::from_zero_polynomials(&p,&r,shape).unwrap();let mut a=pa.instantiate();let mut b=pb.instantiate();
 let good=[1,2,3,4,1,2,3,4].map(c);let bad=[1,2,3,4,1,2,3,5].map(c);let mut complex=good.clone();complex[1].im=Rational::from(1);complex[5].im=Rational::from(1);
 let input=[good.clone(),complex,bad].concat();let ra=a.check_batch(&input,3).unwrap();let rb=b.check_batch(&input,3).unwrap();same(&ra,&rb);assert!(matches!(rb[2],candidate::InvariantCertificate::Incompatible{component:3,..}));
 let ra=a.check_selected_batch(&input,3,&vec![vec![(0,0)];3]).unwrap();let rb=b.check_selected_batch(&input,3,&vec![vec![(0,0)];3]).unwrap();same(&ra,&rb);assert!(rb.iter().all(|x|matches!(x,candidate::InvariantCertificate::Compatible{..})));
}
#[test]
fn direct_complex_and_mixed_scatter_preserve_every_slot() {
    let (pa,pb)=plain_plans();
    let mut a=pa.instantiate();let mut b=pb.instantiate();
    // Every real/complex pattern through odd/even batches. Residual centers
    // differ by lane so a wrong scatter cannot pass by repeating one status.
    for rows in 1..=8 {
        for pattern in 0..(1usize<<rows) {
            let mut input=Vec::new();
            for lane in 0..rows {
                let mut x=c((lane+2) as i64);
                if pattern&(1<<lane)!=0 {x.im=Rational::from((lane+10) as i64);}
                input.extend([x,c(0)]);
            }
            let ra=a.check_batch(&input,rows).unwrap();
            let rb=b.check_batch(&input,rows).unwrap();
            same(&ra,&rb);
            assert_eq!(a.evaluated_rows(),b.evaluated_rows());
            assert_eq!(a.passes(),b.passes());
            for (left,right) in ra.iter().zip(&rb) {
                match (left,right) {
                    (baseline::InvariantCertificate::Incompatible{residual:x,..},
                     candidate::InvariantCertificate::Incompatible{residual:y,..}) => {
                        assert_eq!(x.re.center,y.re.center);
                        assert_eq!(x.im.center,y.im.center);
                        assert!(x.re.radius.is_zero() && x.im.radius.is_zero());
                        assert!(y.re.radius.is_zero() && y.im.radius.is_zero());
                    },
                    _=>panic!("expected exact nonzero lane residual"),
                }
            }
        }
    }
}
#[test]
fn selected_empty_masks_and_workspace_reuse_preserve_lane_indices() {
    let (pa,pb)=plain_plans();let mut a=pa.instantiate();let mut b=pb.instantiate();
    for rows in [7usize,1,0,3,8,2] {
        let mut input=Vec::new();let mut selected=Vec::new();
        for lane in 0..rows {
            let mut x=c((lane+2) as i64);
            if lane%2!=0 {x.im=Rational::from((lane+5) as i64);}
            input.extend([x,c(0)]);
            selected.push(if lane%3==0 {vec![]} else {vec![(0,0)]});
        }
        let ra=a.check_selected_batch(&input,rows,&selected).unwrap();
        let rb=b.check_selected_batch(&input,rows,&selected).unwrap();same(&ra,&rb);
        assert_eq!(a.evaluated_rows(),b.evaluated_rows());
        assert_eq!(a.passes(),b.passes());
    }
}
#[test]
fn mixed_refinement_transitions_to_direct_complex_only() {
    let (pa,pb)=plain_plans();let mut a=pa.instantiate();let mut b=pb.instantiate();
    a.set_precision_budget(128,1024).unwrap();b.set_precision_budget(128,1024).unwrap();
    let z=Complex::new(Rational::from(1),Rational::from(1));
    let mut tiny=z.clone();tiny.im+=Rational::from((1,2)).pow(300);
    let input=[c(1),c(1),tiny,z];
    let ra=a.check_batch(&input,2).unwrap();let rb=b.check_batch(&input,2).unwrap();same(&ra,&rb);
    assert!(matches!(rb[0],candidate::InvariantCertificate::Compatible{..}));
    assert!(matches!(rb[1],candidate::InvariantCertificate::Incompatible{component:0,..}));
    assert_eq!(a.passes(),3);assert_eq!(b.passes(),3);
    assert_eq!(a.evaluated_rows(),4);assert_eq!(b.evaluated_rows(),4);
}
#[test]
fn imaginary_taylor_seeds_preserve_real_mixed_component() {
    let p=parameters();let r=[p[0].pow(2)-&p[1]];
    let shape=Some(vec![vec![0,0],vec![0,1],vec![1,0],vec![1,1]]);
    let pa=baseline::InvariantCertificatePlan::from_zero_polynomials(&p,&r,shape.clone()).unwrap();
    let pb=candidate::InvariantCertificatePlan::from_zero_polynomials(&p,&r,shape).unwrap();
    let mut a=pa.instantiate();let mut b=pb.instantiate();
    let mut jet=[c(0),c(0),c(0),c(0),c(0),c(0),c(0),c(-2)];
    jet[1].im=Rational::from(1);jet[2].im=Rational::from(1);
    let mut bad=jet.clone();bad[7]=c(-3);
    let input=[jet,bad].concat();
    let ra=a.check_batch(&input,2).unwrap();let rb=b.check_batch(&input,2).unwrap();same(&ra,&rb);
    assert!(matches!(rb[0],candidate::InvariantCertificate::Compatible{..}));
    assert!(matches!(rb[1],candidate::InvariantCertificate::Incompatible{component:3,..}));
}
