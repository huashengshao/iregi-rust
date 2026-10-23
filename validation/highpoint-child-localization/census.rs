use iregi_rust::{pv::PvCompiler,ibp::{ScalarCompiler,ScalarRequest}};
use symbolica::{atom::{Atom,AtomCore},domains::{atom::AtomField,integer::Integer,rational::Rational},tensors::matrix::Matrix};
use serde_json::{json,Value};
fn field()->AtomField {AtomField{statistical_zero_test:false,cancel_check_on_division:true,custom_normalization:Some(Box::new(|v,o|{*o=v.together();true}))}}
fn dot(a:&[Atom;4],b:&[Atom;4])->Atom {&a[0]*&b[0]-&a[1]*&b[1]-&a[2]*&b[2]-&a[3]*&b[3]}
fn delta(a:&[Atom;4],b:&[Atom;4])->[Atom;4]{std::array::from_fn(|mu|&a[mu]-&b[mu])}
fn distance(a:&[Atom;4],b:&[Atom;4])->Atom {let d=delta(a,b);dot(&d,&d)}
fn number(v:&Value)->Atom {let(n,d)=v.as_str().unwrap().split_once('/').unwrap_or((v.as_str().unwrap(),"1"));Atom::num(Rational::from((n.parse::<Integer>().unwrap(),d.parse::<Integer>().unwrap())))}
fn matrix(rows:Vec<Vec<Atom>>)->Matrix<AtomField>{Matrix::from_nested_vec(rows,field()).unwrap()}
fn main(){
 let args:Vec<_>=std::env::args().collect();let fixture:Value=serde_json::from_str(&std::fs::read_to_string(&args[1]).unwrap()).unwrap();let sample=&fixture["samples"][0];
 let p:Vec<[Atom;4]>=sample["propagators"].as_array().unwrap()[..6].iter().map(|x|std::array::from_fn(|mu|number(&x["shift"][mu]))).collect();
 let m:Vec<_>=sample["propagators"].as_array().unwrap()[..6].iter().map(|x|number(&x["mass_squared"][0])+Atom::i()*number(&x["mass_squared"][1])).collect();
 let mut cases=Vec::new();
 for (omitted,omitted_axis) in [(3usize,3usize),(4,0)] {
  let active:Vec<_>=(0..6).filter(|&i|i!=omitted).collect();let points:Vec<_>=active.iter().map(|&i|p[i].clone()).collect();let masses:Vec<_>=active.iter().map(|&i|m[i].clone()).collect();
  let mut rows:Vec<Vec<_>>=(0..4).map(|mu|(1..5).map(|i|&points[i][mu]-&points[0][mu]).collect()).collect();
  let coordinate=matrix(rows.clone());rows.push((1..5).map(|i|distance(&points[0],&points[i])-&masses[i]+&masses[0]).collect());
  let chart=matrix(rows.into_iter().enumerate().filter_map(|(row,x)|(row!=omitted_axis).then_some(x)).collect());
  let rhs=Matrix::new_vec(vec![Atom::new(),Atom::new(),Atom::new(),Atom::num(1)],field());let solution=chart.solve(&rhs).unwrap();
  let mut coefficients=vec![Atom::new()];coefficients.extend((0..4).map(|i|solution[(i,0)].clone()));coefficients[0]=-Atom::add_many(&coefficients[1..]);
  let mut children=Vec::new();
  for pinch in 0..5 {
   let child:Vec<_>=active.iter().enumerate().filter_map(|(i,&n)|(i!=pinch).then_some(n)).collect();let cp:Vec<_>=child.iter().map(|&i|p[i].clone()).collect();let cm:Vec<_>=child.iter().map(|&i|m[i].clone()).collect();
   let relative:Vec<_>=cp[1..].iter().map(|p|delta(p,&cp[0])).collect();let gram=matrix(relative.iter().map(|a|relative.iter().map(|b|Atom::num(2)*dot(a,b)).collect()).collect());
   let cayley_rows:Vec<Vec<_>>=cp.iter().enumerate().map(|(i,a)|cp.iter().enumerate().map(|(j,b)|distance(a,b)-&cm[i]-&cm[j]).collect()).collect();let cayley=matrix(cayley_rows.clone());
   let mut pv=PvCompiler::new(cp.clone(),cm).unwrap();let mut pv_status=Vec::new();
   for mu in 0..4 {let mut powers=[0;4];powers[mu]=1;pv_status.push(match pv.compile_moment(powers){Ok(_)=>"prepared".into(),Err(e)=>e});}
   let mut ibp_status=Vec::new();
   if gram.det().unwrap().is_zero(){let mut ibp=ScalarCompiler::new(cayley_rows).unwrap();ibp.set_routing(cp).unwrap();ibp.enable_physical_poles().unwrap();ibp.enable_gram_regular_bubbles().unwrap();
    for raised in 0..4 {let mut powers=vec![1;4];powers[raised]=2;ibp_status.push(match ibp.compile(ScalarRequest{powers,dimension_shift:1}){Ok(slots)=>json!({"raised":raised,"status":"prepared","slots":slots.map(|s|s.to_string())}),Err(e)=>json!({"raised":raised,"status":"error","error":e})});}
   }
   children.push(json!({"pinch_local":pinch,"pinch_original":active[pinch],"original_lines":child,"coefficient":coefficients[pinch].to_string(),"coefficient_exact_zero":coefficients[pinch].is_zero(),"gram_rank":gram.rank(),"gram_det":gram.det().unwrap().to_string(),"cayley_rank":cayley.rank(),"cayley_det":cayley.det().unwrap().to_string(),"pv_rank_one_status":pv_status,"ibp_raised_h1":ibp_status}));
  }
  cases.push(json!({"omitted_original":omitted,"selected_planar_omitted_coordinate":omitted_axis,"original_lines":active,"coordinate_rank":coordinate.rank(),"coordinate_det":coordinate.det().unwrap().to_string(),"selected_chart_det":chart.det().unwrap().to_string(),"coefficients":coefficients.iter().map(ToString::to_string).collect::<Vec<_>>(),"children":children}));
 }
 std::fs::write(&args[2],serde_json::to_string_pretty(&json!({"status":"exact_census_completed","sample":sample["id"],"scope":"Exact retained-input determinant/rank and preparation census only; no numerical master evaluation or integral agreement.","cases":cases})).unwrap()+"\n").unwrap();
}
