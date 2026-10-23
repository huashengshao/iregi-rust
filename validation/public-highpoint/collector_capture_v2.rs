//! Version2 collector-only capture: retain all prior cases and append success controls.
//! Extends the retained 12-case stack-storage driver to N4 and N5 and additional
//! second-order Dual topologies. This is numerical acceptance, not graph or
//! performance qualification.
use iregi_masters::NativeFloat;
use std::io::Write;
use serde_json::{Value,json};
use symbolica::{domains::{dual::HyperDual,float::{Complex,DoubleFloat,Float,FloatLike},rational::Rational},evaluate::EvaluationDomain};
fn component<T:NativeFloat>(v:&T)->Value {assert!(v.is_finite(),"successful output must be finite");json!({"rational":v.exact_rational().map(|r|r.to_string()),"bits":v.get_precision(),"negative_sign":v.negative_sign()})}
fn values<T:NativeFloat>(v:&[Complex<T>])->Value {json!(v.iter().map(|c|json!([component(&c.re),component(&c.im)])).collect::<Vec<_>>())}
fn make_input<T:NativeFloat>(p:&T,n:usize,components:usize)->Vec<Complex<T>> {
 let zero=p.zero();let mut out=Vec::new();
 for lane in 0..5 {
  let mut row=vec![Complex::new(zero.clone(),zero.clone());(n*5+1)*components];
  let integer=|x:i64|p.from_rational(&Rational::from(x));
  for i in 1..n {
   row[(i*4+1)*components].re=integer(i as i64);
   if lane==1 {row[i*4*components].re=integer(i as i64);}
   if lane==2 {row[(i*4+2)*components].re=integer(1);}
  }
  if n>2 {row[(2*4+2)*components].re=integer(1);}
  if n>3 {row[(3*4+3)*components].re=integer(1);}
  if n>4 {row[(4*4)*components].re=p.from_rational(&Rational::from((1,2)));}
  for i in 0..n {
   let mass=if lane==1 {4}else {4+5*i as i64};
   row[(n*4+i)*components].re=integer(mass);
   if lane==2 {row[(n*4+i)*components].im=p.from_rational(&Rational::from((-1,8)));}
   if components>1 {row[(n*4+i)*components+1].re=integer(1);}
  }
  row[n*5*components].re=integer(if lane==4 {0}else {3});
  if lane==3 && n>1 {
   row[4*components].re=integer(134217728);row[5*components].re=integer(134217727);
   row[6*components].re=integer(16384);row[7*components].re=integer(2);
  }
  if components>1 {row[n*5*components+1].re=integer(1);}
  out.extend(row);
 }
 out
}
macro_rules! evaluate {
 ($api:ident,$p:expr,$n:expr,$rank:expr,$components:expr,$input:expr)=>{{
  let mut settings=$api::ReductionSettings::new($n,$rank);settings.algorithm=$api::Algorithm::Hybrid;
  let plan=$api::ReductionPlan::new(settings).unwrap();
  let shape=HyperDual::<f64>::new(vec![vec![0],vec![1],vec![2]]);
  let mut workspace=if $components==1 {$api::Workspace::new(&plan,$p.clone()).unwrap()}else{$api::Workspace::new_dual(&plan,$p.clone(),shape.clone()).unwrap()};
  workspace.set_accuracy_precision(53).unwrap();
  let batch=$api::KinematicsBatch{rows:5,components:$components,values:$input.clone()};
  let result=workspace.reduce_batch(&batch).unwrap();
  let first_diagnostics=workspace.last_diagnostics().to_vec();
  let first_statistics=format!("{:?}",workspace.last_execution());
  let again=workspace.reduce_batch(&batch).unwrap();
  let ordinary_lane_success=matches!(result.statuses[0],$api::LaneStatus::Success);
  let invalid_scale_guard=matches!(result.statuses[4],$api::LaneStatus::InvalidInput(_));
  assert_eq!(format!("{:?}",result.metadata()),format!("{:?}",again.metadata()));
  assert_eq!(result.statuses,again.statuses);assert_eq!(result.fallback_used,again.fallback_used);assert_eq!(result.analytic_used,again.analytic_used);
  for i in 0..5 {assert_eq!(result.lane(i).ok().map(values),again.lane(i).ok().map(values));}
  let cp=$api::ContractionPlan::new(&plan,plan.basis()).unwrap();
  let mut cw=if $components==1 {$api::ContractionWorkspace::new(&cp,$p.clone()).unwrap()}else{$api::ContractionWorkspace::new_dual(&cp,$p.clone(),shape).unwrap()};
  let mut coefficients=Vec::new();
  for _ in 0..5 {for i in 0..cp.term_count() {for k in 0..$components {
   let c=if k==0 {$p.from_rational(&Rational::from((if i%2==0 {1}else{-1},(i+1) as i64)))}else if k==1 {$p.one()}else {$p.zero()};
   coefficients.push(Complex::new(c,$p.zero()));
  }}}
  let contracted=cw.contract_batch(&result,&$api::NumeratorBatch{rows:5,components:$components,values:coefficients}).unwrap();
  json!({"metadata":format!("{:?}",result.metadata()),"basis":format!("{:?}",result.basis),"components":result.components,
   "ordinary_lane_success":ordinary_lane_success,"invalid_scale_guard":invalid_scale_guard,
   "lane_successes":result.statuses.iter().map(|status|matches!(status,$api::LaneStatus::Success)).collect::<Vec<_>>(),
   "statuses":format!("{:?}",result.statuses),"fallback":result.fallback_used,"analytic":result.analytic_used,
   "diagnostics":first_diagnostics,"statistics":first_statistics,
   "repeat_diagnostics":workspace.last_diagnostics(),"repeat_statistics":format!("{:?}",workspace.last_execution()),
   "repeat_metadata":format!("{:?}",again.metadata()),"repeat_statuses":format!("{:?}",again.statuses),"repeat_fallback":again.fallback_used,"repeat_analytic":again.analytic_used,
   "moments":(0..5).map(|i|result.lane(i).ok().map(values)).collect::<Vec<_>>(),
   "repeat":(0..5).map(|i|again.lane(i).ok().map(values)).collect::<Vec<_>>(),
   "contraction_statuses":format!("{:?}",contracted.statuses),"contraction_fallback":contracted.fallback_used,"contraction_analytic":contracted.analytic_used,
   "contracted":(0..5).map(|i|contracted.lane(i).ok().map(values)).collect::<Vec<_>>()})
 }};
}
fn domain<T:NativeFloat>(name:&str,p:T,variant:&str,out:&std::path::Path,selection:&str)->Vec<Value> where Complex<T>:EvaluationDomain {
 let mut reports=Vec::new();
 let mut settings=vec![(1,2,1,false),(2,2,1,false),(3,1,1,false),(2,1,3,false),(1,1,3,false),(3,1,3,false),(4,2,1,false),(4,1,3,false),(5,1,1,false)];
 if name=="f64" {settings.extend([(4,2,1,true),(4,1,3,true)]);}
 for (n,rank,components,conditioned) in settings {
  if selection=="conditioned-f64" && !conditioned {continue;}
  assert!(selection=="all" || selection=="conditioned-f64");
  let fixture=if conditioned {"orthogonal_unit_n4"}else{"retained_v1"};
  eprintln!("COLLECTOR_CAPTURE BEGIN variant={variant} domain={name} n={n} rank={rank} components={components} fixture={fixture}");
  let started=std::time::Instant::now();
  let mut input=make_input(&p,n,components);
  if conditioned {
   assert_eq!(n,4);
   // Only new controls change regular lanes0/2. Retained inputs and deliberate
   // exceptional/invalid lanes remain visible with their original values.
   for lane in [0usize,2] {
    let offset=lane*(n*5+1)*components;
    for i in 0..n {for coordinate in 0..4 {
     input[offset+(i*4+coordinate)*components].re=p.from_i64(i64::from(i>0 && coordinate==i));
    }}
    for i in 0..n {input[offset+(n*4+i)*components].re=p.from_i64((i+1) as i64);}
   }
  }
  let result=match variant {"baseline"=>evaluate!(baseline,p,n,rank,components,input),"candidate"=>evaluate!(candidate,p,n,rank,components,input),_=>panic!("bad variant")};
  let required=n<4 || name!="f64" || conditioned;
  let report=json!({"domain":name,"propagators":n,"rank":rank,"components":components,"fixture":fixture,
   "input":values(&input),"result":result,"requires_ordinary_lane_success":required,
   "validation_role":if required {"positive"}else{"known_guard_parity"}});
  let mut checkpoint=std::fs::OpenOptions::new().create(true).append(true).open(out.with_extension("progress.jsonl")).unwrap();
  writeln!(checkpoint,"{}",serde_json::to_string(&report).unwrap()).unwrap();
  eprintln!("COLLECTOR_CAPTURE END variant={variant} domain={name} n={n} rank={rank} components={components} fixture={fixture} elapsed={} success_lanes={}",started.elapsed().as_secs_f64(),report["result"]["lane_successes"]);
  reports.push(report);
 }
 reports
}
fn main() {
 let args:Vec<_>=std::env::args().collect();let out=std::path::Path::new(args.get(1).expect("output path"));
 if let Some(variant)=args.get(2) {
  let selection=args.get(3).map(String::as_str).unwrap_or("all");
  let mut all=domain("f64",0f64,variant,out,selection);all.extend(domain("DoubleFloat",DoubleFloat::from(0f64),variant,out,selection));all.extend(domain("Float128",Float::new(128),variant,out,selection));
  std::fs::write(out,serde_json::to_string_pretty(&all).unwrap()).unwrap();return;
 }
 let mut reports=Vec::new();
 for variant in ["baseline","candidate"] {
  let file=out.with_extension(format!("{variant}.json"));
  let success=std::process::Command::new(std::env::current_exe().unwrap()).arg(&file).arg(variant)
    .status().unwrap();
  assert!(success.success(),"{variant} capture failed");
  reports.push(serde_json::from_str::<Value>(&std::fs::read_to_string(file).unwrap()).unwrap());
 }
 assert_eq!(reports[0],reports[1],"paired complete output differs");
 assert_eq!(reports[0].as_array().unwrap().len(),29);
 std::fs::write(out,serde_json::to_string_pretty(&reports[0]).unwrap()).unwrap();
 for report in reports[0].as_array().unwrap() {
  assert_eq!(report["result"]["invalid_scale_guard"],true,"zero-scale guard missing: {}",report);
  if report["requires_ordinary_lane_success"]==true {
   assert_eq!(report["result"]["ordinary_lane_success"],true,"required ordinary lane failed; full captures retained: {}",report);
  } else {
   assert_eq!(report["result"]["ordinary_lane_success"],false,"retained known guard control changed: {}",report);
  }
 }
 println!("PASS 29 complete paired cases across f64, DoubleFloat, Float128; statuses, metadata, flags, diagnostics, precision and signed zeros included");
}
