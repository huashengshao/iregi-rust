#![allow(dead_code)]
use std::{hint::black_box,time::Instant};
use symbolica::{atom::{Atom,AtomCore},domains::{float::{Complex,SingleFloat},rational::Rational}};
use iregi_masters::NativeFloat;
use serde_json::{json,Value};
pub use iregi_rust::ReductionError;
#[path="candidate.rs"] mod certificate;
use certificate::{InvariantCertificatePlan,InvariantCertificate};
fn main(){
 let path=std::env::args().nth(1).expect("physical sample path");
 let sample:Value=serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
 let props=sample["propagators"].as_array().unwrap();let n=props.len();assert_eq!(n,3);
 let params:Vec<Atom>=(0..n*5+1).map(|i|Atom::parse(&format!("x{i}"),"certificate_probe",Default::default()).unwrap()).collect();
 let mut residuals=Vec::new();
 for i in 0..n { for j in i+1..n {let mut x=Atom::Zero;for axis in 0..4 {let term=(&params[i*4+axis]-&params[j*4+axis]).pow(2);x=if axis==0{x+term}else{x-term};}residuals.push(x);}}
 let plan=InvariantCertificatePlan::from_zero_polynomials(&params,&residuals,None).unwrap();
 let ops=plan.probe_operation_counts();assert_eq!(ops.function_calls,0);
 let mut scalar=Vec::<Complex<f64>>::new();
 for p in props {for x in p["shift"].as_array().unwrap(){scalar.push(Complex::new(x.as_str().unwrap().parse().unwrap(),0.));}}
 for p in props {scalar.push(Complex::new(p["mass_squared"][0].as_str().unwrap().parse().unwrap(),p["mass_squared"][1].as_str().unwrap().parse().unwrap()));}
 scalar.push(Complex::new(sample["mu"].as_str().unwrap().parse().unwrap(),0.));
 let mut output=Vec::new();
 for rows in [1usize,3,32] {
  let input=scalar.repeat(rows);let selected=vec![vec![(0,0),(1,0)];rows];let mut workspace=plan.instantiate();let mut exact=Vec::<Complex<Rational>>::new();
  let mut records=Vec::new();
  for block in 0..24 {
   let mut convert=0u128;let mut total=0u128;let mut mapping=0u128;let mut packing=0u128;let mut evaluation=0u128;let mut inspection=0u128;
   for _ in 0..32 {
    let t=Instant::now();let c=Instant::now();exact.clear();exact.extend(input.iter().map(|v|Complex::new(v.re.exact_rational().unwrap(),v.im.exact_rational().unwrap())));convert+=c.elapsed().as_nanos();
    let statuses=workspace.check_selected_batch(black_box(&exact),rows,&selected).unwrap();total+=t.elapsed().as_nanos();assert!(statuses.iter().all(|s|matches!(s,InvariantCertificate::Compatible{..})));
    assert_eq!(workspace.passes(),1);assert_eq!(workspace.evaluated_rows(),rows);
    mapping+=workspace.trace.mapping_ns;packing+=workspace.trace.packing_ns;evaluation+=workspace.trace.evaluation_ns;inspection+=workspace.trace.inspection_ns;
   }
   if block>=3 {records.push(json!({"total_ns_per_batch":total as f64/32.,"exact_conversion_ns":convert as f64/32.,"mapping_lookup_ns":mapping as f64/32.,"ball_packing_ns":packing as f64/32.,"evaluation_ns":evaluation as f64/32.,"inspection_ns":inspection as f64/32.,"certificate_passes":workspace.passes(),"evaluated_rows":workspace.evaluated_rows(),"real_batch_calls":workspace.trace.real_batch_calls,"complex_batch_calls":workspace.trace.complex_batch_calls}));}
  }
  output.push(json!({"batch_width":rows,"status":"all_certified_zero","samples":records}));
 }
 println!("{}",json!({"kind":"isolated-certificate-component-profile","backend":"candidate-partitioned-real-ball","input":path,"arguments":params.len(),"residuals":residuals.len(),"selected_constraints":[0,1],"working_bits":128,"operations":{"additions":ops.additions,"multiplications":ops.multiplications,"inversions":ops.inversions,"function_calls":ops.function_calls},"rows":output,"performance_gate":false}));
}
