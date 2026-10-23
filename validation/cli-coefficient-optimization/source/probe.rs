#![allow(dead_code)]
mod input;
mod coefficients;
mod proof;
use std::{path::Path,time::Instant};
use coefficients::{CoefficientPlan,CoefficientWorkspace,Mode};
use iregi_masters::{Complex,DoubleFloat,Float,NativeFloat};
use iregi_prepare::{prepare_dot,NumeratorSource,PrepareOptions,PolynomialTerm};
use input::{Sample,ComplexLiteral,Literal};
use serde_json::{Value,json};
use symbolica::{atom::{Atom,AtomCore},domains::{SelfRing,float::SingleFloat,rational::Rational},evaluate::EvaluationDomain};
const MODES:[Mode;4]=[Mode::Direct,Mode::Allocated,Mode::Cse,Mode::Pair1];
fn scalar<T:NativeFloat>(v:&T)->Value{if v.is_finite(){json!({"rational":v.exact_rational().unwrap().to_string(),"precision":v.get_precision(),"negative_sign":v.negative_sign()})}else{json!({"nonfinite":true,"precision":v.get_precision(),"negative_sign":v.negative_sign()})}}
fn values<T:NativeFloat>(v:&[Complex<T>])->Value{json!(v.iter().map(|z|json!([scalar(&z.re),scalar(&z.im)])).collect::<Vec<_>>())}
fn magnitude(q:Rational)->Rational{if q<Rational::from(0){-q}else{q}}
fn comparison<T:NativeFloat,U:NativeFloat>(actual:&[Complex<T>],expected:&[Complex<U>],digits:u64)->Value{
 assert_eq!(actual.len(),expected.len());let tolerance=Rational::from((1,10)).pow(digits);let mut maximum=Rational::from(0);let mut failures=Vec::new();
 for (index,(actual,expected)) in actual.iter().zip(expected).enumerate(){for (component,(a,b)) in [(&actual.re,&expected.re),(&actual.im,&expected.im)].into_iter().enumerate(){
  let (Some(a),Some(b))=(a.exact_rational(),b.exact_rational())else{failures.push(json!({"index":index,"component":component,"reason":"nonfinite coefficient"}));continue};
  let aa=magnitude(a.clone());let bb=magnitude(b.clone());let scale=if aa>bb{aa}else{bb};let scale=if scale>Rational::from(1){scale}else{Rational::from(1)};let relative=magnitude(a-b)/scale;
  if relative>maximum{maximum=relative.clone();}if relative>tolerance{failures.push(json!({"index":index,"component":component,"normalized_error":relative.to_string()}));}
 }}
 json!({"complex_outputs":actual.len(),"real_comparisons":actual.len()*2,"metric":"absolute error / max(1, abs(actual component), abs(reference component))","tolerance":tolerance.to_string(),"maximum_normalized_error":maximum.to_string(),"failures":failures,"passed":failures.is_empty()})
}
fn lift<T:NativeFloat>(input:&[Complex<T>],p:&Float)->Vec<Complex<Float>>{input.iter().map(|v|Complex::new(p.from_rational(&v.re.exact_rational().unwrap()),p.from_rational(&v.im.exact_rational().unwrap()))).collect()}
fn domain<T:NativeFloat>(name:&str,p:T,plans:&[CoefficientPlan],samples:&[Sample],digits:u64)->Value where Complex<T>:EvaluationDomain{
 let mut workspaces:Vec<_>=plans.iter().map(|plan|CoefficientWorkspace::new(plan,p.clone())).collect();let mut reference=CoefficientWorkspace::<Float>::new(&plans[0],Float::new(256));let mut batches=Vec::new();
 for (step,rows) in [0_usize,1,3,7,32,3].into_iter().enumerate(){
  let selected:Vec<_>=(0..rows).map(|lane|samples[(lane+step)%samples.len()].clone()).collect();let input=plans[0].pack(&selected,&p).unwrap();
  for plan in plans{assert_eq!(values(&plan.pack(&selected,&p).unwrap()),values(&input));}
  let oracle=reference.evaluate(&lift(&input,&Float::new(256)),rows).unwrap();let mut results=Vec::new();
  for (mode,workspace) in MODES.into_iter().zip(&mut workspaces){let result=workspace.evaluate(&input,rows).unwrap();assert_eq!(result.rows,rows);assert_eq!(result.components,1);assert_eq!(result.values.len(),rows*plans[0].support().len());
   results.push(json!({"mode":mode.name(),"outputs":values(&result.values),"agreement_1e10":comparison(&result.values,&oracle.values,10),"precision_agreement":comparison(&result.values,&oracle.values,digits)}));}
  batches.push(json!({"step":step,"rows":rows,"sample_ids":selected.iter().map(|s|&s.id).collect::<Vec<_>>(),"input":values(&input),"reference256_same_represented_input":values(&oracle.values),"results":results}));
 }
 let canonical=plans[0].pack(&samples[..1],&p).unwrap();let zero=plans[0].pack(&samples[4..5],&p).unwrap();let mut controls=Vec::new();
 for (mode,workspace) in MODES.into_iter().zip(&mut workspaces){assert!(workspace.evaluate(&canonical,2).is_err());let recovered=workspace.evaluate(&canonical,1).unwrap();assert!(recovered.values.iter().any(|z|!z.re.is_zero()||!z.im.is_zero()));let z=workspace.evaluate(&zero,1).unwrap();assert!(z.values.iter().all(|z|z.re.is_zero()&&z.im.is_zero()));
  let mut beyond=false;if p.get_precision()>53{let a=workspace.evaluate(&plans[0].pack(&samples[1..2],&p).unwrap(),1).unwrap();let b=workspace.evaluate(&plans[0].pack(&samples[2..3],&p).unwrap(),1).unwrap();beyond=a.values.iter().zip(b.values).any(|(a,b)|a.re.exact_rational()!=b.re.exact_rational()||a.im.exact_rational()!=b.im.exact_rational());assert!(beyond);}
  controls.push(json!({"mode":mode.name(),"post_error_reuse":true,"canonical_nonzero":true,"zero_coupling_zero":true,"beyond53_distinguished":beyond}));
 }
 json!({"domain":name,"prototype_precision":p.get_precision(),"higher_precision_digits":digits,"batches":batches,"controls":controls})
}
fn mixed(plans:&[CoefficientPlan],samples:&[Sample])->Value{
 let p=Float::new(256);let mut workspaces:Vec<_>=plans.iter().map(|plan|CoefficientWorkspace::new(plan,p.clone())).collect();let mut reference=CoefficientWorkspace::new(&plans[0],p.clone());let mut records=Vec::new();
 for rows in [3_usize,1,7]{let selected:Vec<_>=(0..rows).map(|i|samples[i%samples.len()].clone()).collect();let mut input=plans[0].pack(&selected,&p).unwrap();let width=samples[0].parameters.len();for(lane,row)in input.chunks_exact_mut(width).enumerate(){for(i,z)in row.iter_mut().enumerate(){let context=Float::new([80,128,256][(lane+i)%3]);z.re=context.from_rational(&z.re.exact_rational().unwrap());z.im=context.from_rational(&z.im.exact_rational().unwrap());}}
  let oracle=reference.evaluate(&lift(&input,&p),rows).unwrap();let mut results=Vec::new();for(mode,workspace)in MODES.into_iter().zip(&mut workspaces){let result=workspace.evaluate(&input,rows).unwrap();results.push(json!({"mode":mode.name(),"outputs":values(&result.values),"agreement_1e10":comparison(&result.values,&oracle.values,10),"precision_agreement":comparison(&result.values,&oracle.values,18)}));}
  records.push(json!({"rows":rows,"inputs":values(&input),"reference256_same_represented_input":values(&oracle.values),"results":results}));
 }
 json!({"prototype_precision":256,"input_precisions":[80,128,256],"batches":records})
}
fn failures(value:&Value)->usize{match value{Value::Object(m)=>usize::from(m.get("passed")==Some(&Value::Bool(false)))+m.values().map(failures).sum::<usize>(),Value::Array(a)=>a.iter().map(failures).sum(),_=>0}}
fn run()->Result<(),String>{
 let args:Vec<_>=std::env::args().collect();let case=args.get(1).ok_or("case")?;let out=Path::new(args.get(2).ok_or("output directory")?);std::fs::create_dir(out).map_err(|e|e.to_string())?;let root=Path::new("target/cli-coefficient-optimization/assets");
 let(graphname,axes)=match case.as_str(){"ggh"=>("ggh_top_triangle",2),"gghh"=>("gghh_top_box",2),"gghhh"=>("gghhh_top_pentagon",2),"gggg-up"=>("gggg_up_box",4),_=>return Err("unknown graph".into())};
 let start=Instant::now();eprintln!("OPTIMIZE {case} prepare graph");let graph=prepare_dot(&std::fs::read_to_string(root.join("fixtures/models/sm.json")).unwrap(),&std::fs::read_to_string(root.join(format!("examples/graphs/{graphname}.dot"))).unwrap(),&PrepareOptions{source:NumeratorSource::FeynmanRules,external_wavefunctions:true,component:Some(vec![0;axes])}).map_err(|e|e.to_string())?;let graph_seconds=start.elapsed().as_secs_f64();
 let sample:Sample=serde_json::from_slice(&std::fs::read(root.join(format!("validation/physical/{case}-cli-input.json"))).unwrap()).unwrap();let names:Vec<_>=sample.parameters.keys().cloned().collect();let parameters=names.iter().map(|name|Atom::parse(name,"iregi_cli",Default::default()).unwrap()).collect::<Vec<_>>();let expressions:Vec<_>=graph.numerator.terms.iter().map(|term|term.coefficient.clone()).collect();
 let graph_record=json!({"case":case,"name":graph.name,"parameters":names,"terms":graph.numerator.terms.iter().map(|term|json!({"powers":term.exponents,"coefficient":term.coefficient.to_string()})).collect::<Vec<_>>(),"graph_preparation_seconds":graph_seconds});std::fs::write(out.join("prepared-graph.json"),serde_json::to_vec_pretty(&graph_record).unwrap()).unwrap();
 let mut plans=Vec::new();let mut structures=Vec::new();for mode in MODES{let before=Instant::now();eprintln!("OPTIMIZE {case} build {}",mode.name());let plan=CoefficientPlan::new(mode,&graph,names.clone())?;let compile_seconds=before.elapsed().as_secs_f64();let proof_start=Instant::now();let identity=proof::prove(plan.proof_exact().unwrap(),&parameters,&expressions)?;let proof_seconds=proof_start.elapsed().as_secs_f64();let record=json!({"mode":mode.name(),"prepare_seconds":compile_seconds,"proof_seconds":proof_seconds,"structure":identity});eprintln!("OPTIMIZE {case} {record}");structures.push(record);std::fs::write(out.join("structures.json"),serde_json::to_vec_pretty(&structures).unwrap()).unwrap();plans.push(plan);}
 for plan in &plans{assert_eq!(plan.support(),plans[0].support());}
 let mut samples=vec![sample.clone();6];for(i,s)in samples.iter_mut().enumerate(){s.id=format!("{case}-control-{i}");}let key="UFO::{}::G";assert!(sample.parameters.contains_key(key));for(index,value)in [(1,"1"),(2,"1180591620717411303425/1180591620717411303424"),(4,"0"),(5,"-0")]{samples[index].parameters.insert(key.into(),ComplexLiteral::Real(Literal::Text(value.into())));}samples[3].parameters.insert(key.into(),ComplexLiteral::Pair([Literal::Text("1".into()),Literal::Text("-1/7".into())]));
 let domains=vec![domain("f64",0f64,&plans,&samples,10),domain("DoubleFloat",DoubleFloat::from(0f64),&plans,&samples,20),domain("Float128",Float::new(128),&plans,&samples,28),domain("Float256",Float::new(256),&plans,&samples,55)];let mixed=mixed(&plans,&samples);
 let mut empty=graph.clone();empty.numerator.terms.clear();let mut constant=graph.clone();constant.numerator.terms=vec![PolynomialTerm{exponents:[0;4],coefficient:Atom::parse("2/7","iregi_cli",Default::default()).unwrap()}];
 for mode in MODES{let ep=CoefficientPlan::new(mode,&empty,names.clone())?;assert!(ep.proof_exact().is_none());for rows in [0,1,3]{let p=ep.pack(&vec![sample.clone();rows],&0f64)?;let result=CoefficientWorkspace::new(&ep,0f64).evaluate(&p,rows)?;assert!(result.values.is_empty());assert_eq!(result.rows,rows);assert_eq!(result.components,1);}
  let cp=CoefficientPlan::new(mode,&constant,vec![])?;proof::prove(cp.proof_exact().unwrap(),&[],&[constant.numerator.terms[0].coefficient.clone()])?;let p=Float::new(128);let result=CoefficientWorkspace::new(&cp,p.clone()).evaluate(&[],3)?;let expected=p.from_rational(&Rational::from((2,7)));assert!(result.values.iter().all(|z|z.re==expected&&SingleFloat::is_zero(&z.im)));let mut missing=sample.clone();missing.parameters.pop_last();assert!(plans[0].pack(&[missing],&p).is_err());}
 let mut result=json!({"status":"completed","case":case,"structures":structures,"domains":domains,"mixed":mixed,"empty_and_constant_controls":true,"elapsed_seconds":start.elapsed().as_secs_f64(),"timing_scope":"Single preparation diagnostics only; no throughput measurement or performance acceptance"});let count=failures(&result);result["failed_comparisons"]=json!(count);result["status"]=json!(if count==0{"passed"}else{"numerical_failures"});std::fs::write(out.join("outputs.json"),serde_json::to_vec_pretty(&result).unwrap()).unwrap();eprintln!("OPTIMIZE_DONE {case} failures={count}");if count>0{return Err(format!("{count} numerical comparisons failed; all retained"))}Ok(())
}
fn main(){std::thread::Builder::new().stack_size(128*1024*1024).spawn(run).unwrap().join().unwrap().unwrap();}
