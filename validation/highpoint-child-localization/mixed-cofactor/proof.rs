use symbolica::{atom::{Atom,AtomCore},domains::{atom::AtomField,dual::HyperDual,float::Complex,rational::{Rational,Q}},evaluate::{Dualizer,ExpressionEvaluator},tensors::matrix::Matrix};
use serde_json::json;
fn field()->AtomField {AtomField{statistical_zero_test:false,cancel_check_on_division:true,custom_normalization:Some(Box::new(|v,o|{*o=v.together();true}))}}
fn dot(a:&[Atom;4],b:&[Atom;4])->Atom{&a[0]*&b[0]-&a[1]*&b[1]-&a[2]*&b[2]-&a[3]*&b[3]}
fn distance(a:&[Atom;4],b:&[Atom;4])->Atom{let d=std::array::from_fn(|mu|&a[mu]-&b[mu]);dot(&d,&d)}
fn main(){
 let x=Atom::var(symbolica::symbol!("thin_cofactor::x"));let y=Atom::var(symbolica::symbol!("thin_cofactor::y"));
 let shape=vec![vec![0,0],vec![1,0],vec![0,1],vec![1,1]];let mut cases=Vec::new();
 for (omitted,axis,perturbation_axis) in [(3usize,3usize,0usize),(4,0,3)] {
  let points=[[0,0,0,0],[0,2,0,0],[0,0,2,0],[0,0,0,2],[1,0,0,0],[0,2,2,0]];
  let mut p:Vec<[Atom;4]>=points.iter().map(|p|p.map(|n|Atom::num(n)/Atom::num(2))).collect();let masses:Vec<_>=[1,2,3,4,2,3].into_iter().map(Atom::num).collect();
  p[5][perturbation_axis]=&p[5][perturbation_axis]+&x*&y;
  let active:Vec<_>=(0..6).filter(|&i|i!=omitted).collect();let mut rows:Vec<Vec<_>>=(0..4).map(|mu|active[1..].iter().map(|&i|&p[i][mu]-&p[active[0]][mu]).collect()).collect();
  let coordinate=Matrix::from_nested_vec(rows.clone(),field()).unwrap();let coordinate_det=coordinate.det().unwrap();assert!(coordinate_det.is_zero());
  rows.push(active[1..].iter().map(|&i|distance(&p[active[0]],&p[i])-&masses[i]+&masses[active[0]]).collect());
  let mut chart_rows:Vec<_>=rows.into_iter().enumerate().filter_map(|(row,x)|(row!=axis).then_some(x)).collect();let chart=Matrix::from_nested_vec(chart_rows.clone(),field()).unwrap();let det=chart.det().unwrap();
  let rhs=Matrix::new_vec(vec![Atom::new(),Atom::new(),Atom::new(),Atom::num(1)],field());let solution=chart.solve(&rhs).unwrap();let weight=solution[(2,0)].clone();
  for row in 0..4 {chart_rows[row][2]=rhs[(row as u32,0)].clone();}
  let cofactor=Matrix::from_nested_vec(chart_rows,field()).unwrap().det().unwrap();assert!((&weight*&det-&cofactor).together().is_zero());
  let expressions=vec![coordinate_det,det.clone(),cofactor.clone(),weight.clone()];let exact:ExpressionEvaluator<Complex<Rational>>=Atom::evaluator_multiple(&expressions,&[x.clone(),y.clone()]).direct_translation(true).cores(1).horner_iterations(0).build().unwrap();
  let mut evaluator=exact.vectorize(&Dualizer::new(HyperDual::<Complex<Rational>>::new(shape.clone()),vec![])).unwrap().map_to_ring(&Q).unwrap();let mut controls=Vec::new();
  for mixed in [false,true] {
   let mut input=vec![Rational::from(0);8];if mixed {input[1]=Rational::from(1);input[6]=Rational::from(1);}
   let mut output=vec![Rational::from(0);16];evaluator.evaluate_in_ring(&input,&mut output,&Q);
   assert!(output[..4].iter().all(|v|*v==Rational::from(0)));assert_ne!(output[4],Rational::from(0));assert_eq!(output[8],Rational::from(0));assert_eq!(output[12],Rational::from(0));
   if mixed {assert_eq!(output[9],Rational::from(0));assert_eq!(output[10],Rational::from(0));assert_ne!(output[11],Rational::from(0));assert_ne!(output[15],Rational::from(0));}else{assert!(output[8..].iter().all(|v|*v==Rational::from(0)));}
   controls.push(json!({"mixed_direction_enabled":mixed,"input_jets":input.iter().map(ToString::to_string).collect::<Vec<_>>(),"coordinate_determinant_jet":output[0..4].iter().map(ToString::to_string).collect::<Vec<_>>(),"chart_determinant_jet":output[4..8].iter().map(ToString::to_string).collect::<Vec<_>>(),"cofactor_jet":output[8..12].iter().map(ToString::to_string).collect::<Vec<_>>(),"weight_jet":output[12..16].iter().map(ToString::to_string).collect::<Vec<_>>()}));
  }
  cases.push(json!({"omitted_original":omitted,"omitted_coordinate_row":axis,"perturbed_original_line":5,"perturbed_coordinate":perturbation_axis,"perturbation":"x*y","coefficient_local_index":3,"coefficient_original_index":active[3],"chart_determinant":det.to_string(),"cofactor_numerator":cofactor.to_string(),"coefficient":weight.to_string(),"controls":controls}));
 }
 std::fs::write(std::env::args().nth(1).unwrap(),serde_json::to_string_pretty(&json!({"status":"passed","shape":shape,"scope":"Exact Symbolica mixed-Dual chart-cofactor proof; no floating numeric masters. All planar constraints vanish in full shape, chart determinant has nonzero primal, but excluded child weight has nonzero mixed coefficient.","cases":cases})).unwrap()+"\n").unwrap();
}
