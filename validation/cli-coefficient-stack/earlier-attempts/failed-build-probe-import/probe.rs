#![allow(dead_code)]
mod input;
mod baseline;
mod candidate;
mod proof;
use std::{collections::BTreeMap,path::Path,time::Instant};
use iregi_masters::{Complex,DoubleFloat,Float,NativeFloat};
use iregi_prepare::{prepare_dot,NumeratorSource,PrepareOptions,PreparedGraph,PolynomialTerm};
use serde_json::{json,Value};
use symbolica::{atom::{Atom,AtomCore},domains::rational::Rational,evaluate::EvaluationDomain};
use input::{Sample,ComplexLiteral,Literal};
fn number<T:NativeFloat>(v:&T)->Value {
 assert!(v.is_finite(),"finite coefficient control produced nonfinite value");
 json!({"rational":v.exact_rational().expect("supported exact numeric domain").to_string(),"precision":v.get_precision(),"negative_sign":v.negative_sign()})
}
fn values<T:NativeFloat>(v:&[Complex<T>])->Value {json!(v.iter().map(|z|json!([number(&z.re),number(&z.im)])).collect::<Vec<_>>())}
fn structural(a:&baseline::CoefficientPlan,b:&candidate::CoefficientPlan,out:&Path,label:&str)->Value {
 assert_eq!(a.support(),b.support());
 match (a.proof_exact(),b.proof_exact()) {
  (None,None)=>json!({"label":label,"empty":true,"unchanged":true}),
  (Some(a),Some(b))=>{
   let aa=a.export_instructions();let bb=b.export_instructions();
   let text=proof::provenance(&aa).unwrap();assert_eq!(text,proof::provenance(&bb).unwrap());
   let mut ah=BTreeMap::new();let mut bh=BTreeMap::new();proof::helpers(&aa,&mut ah).unwrap();proof::helpers(&bb,&mut bh).unwrap();assert_eq!(ah,bh);
   std::fs::write(out.join(format!("{label}.semantics")),text).unwrap();
   json!({"label":label,"empty":false,"inputs":aa.input_count,"outputs":aa.output_count,"instructions":aa.instructions.len(),"before_temporaries":aa.temporary_count,"after_temporaries":bb.temporary_count,"unchanged":true,"unchanged_helpers":true,"helper_count":ah.len()})
  },_=>panic!("empty-plan behavior changed")
 }
}
fn domain<T:NativeFloat>(name:&str,p:T,a:&baseline::CoefficientPlan,b:&candidate::CoefficientPlan,samples:&[Sample])->Value where Complex<T>:EvaluationDomain {
 let mut aw=baseline::CoefficientWorkspace::new(a,p.clone());let mut bw=candidate::CoefficientWorkspace::new(b,p.clone());let mut records=Vec::new();
 for (step,rows) in [0_usize,1,3,7,32,3].into_iter().enumerate(){
  let selected:Vec<_>=(0..rows).map(|lane|samples[(lane+step)%samples.len()].clone()).collect();
  let aa=a.pack(&selected,&p).unwrap();let bb=b.pack(&selected,&p).unwrap();assert_eq!(values(&aa),values(&bb));
  let ar=aw.evaluate(&aa,rows).unwrap();let br=bw.evaluate(&bb,rows).unwrap();assert_eq!(ar.rows,br.rows);assert_eq!(ar.components,br.components);assert_eq!(ar.components,1);assert_eq!(values(&ar.values),values(&br.values));
  assert_eq!(ar.values.len(),rows*a.support().len());
  records.push(json!({"step":step,"rows":rows,"sample_ids":selected.iter().map(|s|&s.id).collect::<Vec<_>>(),"input":values(&aa),"outputs":values(&ar.values),"rows_match":true,"components":ar.components,"all_values_exact":true}));
 }
 // Invalid shape must not poison a retained workspace.
 let packed=a.pack(&samples[..1],&p).unwrap();
 assert!(aw.evaluate(&packed,2).is_err());assert!(bw.evaluate(&packed,2).is_err());
 let ar=aw.evaluate(&packed,1).unwrap();let br=bw.evaluate(&packed,1).unwrap();assert_eq!(values(&ar.values),values(&br.values));
 assert!(ar.values.iter().any(|v|!v.re.is_zero()||!v.im.is_zero()),"canonical physical control unexpectedly has no nonzero coefficient");
 let zero_input=a.pack(&samples[4..5],&p).unwrap();let zero_a=aw.evaluate(&zero_input,1).unwrap();let zero_b=bw.evaluate(&zero_input,1).unwrap();
 assert_eq!(values(&zero_a.values),values(&zero_b.values));assert!(zero_a.values.iter().all(|v|v.re.is_zero()&&v.im.is_zero()),"zero strong coupling did not eliminate numerator");
 let mut missing=samples[0].clone();missing.parameters.pop_last();assert!(a.pack(&[missing.clone()],&p).is_err());assert!(b.pack(&[missing],&p).is_err());
 if p.get_precision()>53 && !a.support().is_empty(){
  let one=a.pack(&samples[1..2],&p).unwrap();let distinct=a.pack(&samples[2..3],&p).unwrap();
  assert!(one.iter().zip(&distinct).any(|(a,b)|a.re.exact_rational()!=b.re.exact_rational()||a.im.exact_rational()!=b.im.exact_rational()),"packing lost beyond-binary64 parameter");
  let one=aw.evaluate(&one,1).unwrap();let distinct=aw.evaluate(&distinct,1).unwrap();
  assert!(one.values.iter().zip(&distinct.values).any(|(a,b)|a.re.exact_rational()!=b.re.exact_rational()||a.im.exact_rational()!=b.im.exact_rational()),"physical coefficient lost beyond-binary64 perturbation");
 }
 json!({"domain":name,"working_precision":p.get_precision(),"batches":records,"post_error_reuse_exact":true,"canonical_nonzero":true,"zero_coupling_vanishes":true,"beyond53_exact_values_distinguished":p.get_precision()>53,"bad_parameter_names_rejected":true})
}
fn mixed_float(a:&baseline::CoefficientPlan,b:&candidate::CoefficientPlan,samples:&[Sample])->Value {
 let p=Float::new(256);let mut aw=baseline::CoefficientWorkspace::new(a,p.clone());let mut bw=candidate::CoefficientWorkspace::new(b,p.clone());let mut records=Vec::new();
 for rows in [3_usize,1,7] {
  let selected:Vec<_>=(0..rows).map(|lane|samples[lane%samples.len()].clone()).collect();
  let mut packed=a.pack(&selected,&p).unwrap();let width=samples[0].parameters.len();
  for(lane,row)in packed.chunks_exact_mut(width).enumerate(){
   for(argument,value)in row.iter_mut().enumerate(){
    let precision=[80,128,256][(lane+argument)%3];let context=Float::new(precision);
    value.re=context.from_rational(&value.re.exact_rational().unwrap());
    value.im=context.from_rational(&value.im.exact_rational().unwrap());
   }
  }
  let ar=aw.evaluate(&packed,rows).unwrap();let br=bw.evaluate(&packed,rows).unwrap();
  assert_eq!(values(&ar.values),values(&br.values));assert_eq!(ar.rows,br.rows);assert_eq!(ar.components,br.components);
  records.push(json!({"rows":rows,"inputs":values(&packed),"outputs":values(&ar.values),"all_values_exact":true}));
 }
 json!({"working_precision":256,"input_precisions":[80,128,256],"batches":records})
}
fn run()->Result<(),String>{
 let args:Vec<_>=std::env::args().collect();let case=args.get(1).ok_or("case")?;let out=Path::new(args.get(2).ok_or("output")?);std::fs::create_dir(out).map_err(|e|e.to_string())?;
 let root=Path::new("target/cli-coefficient-stack/assets");
 let (graphname,axes)=match case.as_str(){"ggh"=>("ggh_top_triangle",2),"gghh"=>("gghh_top_box",2),"gghhh"=>("gghhh_top_pentagon",2),"gggg-up"=>("gggg_up_box",4),_=>return Err("unknown case".into())};
 let started=Instant::now();eprintln!("CLI_COEFFICIENT {case} graph preparation start");
 let graph=prepare_dot(&std::fs::read_to_string(root.join("fixtures/models/sm.json")).unwrap(),&std::fs::read_to_string(root.join(format!("examples/graphs/{graphname}.dot"))).unwrap(),&PrepareOptions{source:NumeratorSource::FeynmanRules,external_wavefunctions:true,component:Some(vec![0;axes])}).map_err(|e|e.to_string())?;
 eprintln!("CLI_COEFFICIENT {case} graph ready {:?}; {} coefficients",started.elapsed(),graph.numerator.terms.len());
 let sample:Sample=serde_json::from_slice(&std::fs::read(root.join(format!("validation/physical/{case}-cli-input.json"))).unwrap()).unwrap();
 let mut samples=vec![sample.clone();6];for(i,s)in samples.iter_mut().enumerate(){s.id=format!("{case}-parameter-control-{i}");}
 let key="UFO::{}::G";assert!(sample.parameters.contains_key(key));
 samples[1].parameters.insert(key.into(),ComplexLiteral::Real(Literal::Text("1".into())));
 samples[2].parameters.insert(key.into(),ComplexLiteral::Real(Literal::Text("1180591620717411303425/1180591620717411303424".into())));
 samples[3].parameters.insert(key.into(),ComplexLiteral::Pair([Literal::Text("1".into()),Literal::Text("-1/7".into())]));
 samples[4].parameters.insert(key.into(),ComplexLiteral::Real(Literal::Text("0".into())));
 samples[5].parameters.insert(key.into(),ComplexLiteral::Real(Literal::Text("-0".into())));
 let names:Vec<_>=sample.parameters.keys().cloned().collect();let a=baseline::CoefficientPlan::new(&graph,names.clone())?;let b=candidate::CoefficientPlan::new(&graph,names.clone())?;
 let structure=structural(&a,&b,out,"physical");eprintln!("CLI_COEFFICIENT {case} structural proof {structure}");
 let graphrecord=json!({"name":graph.name,"rank":graph.numerator.rank(),"parameters":names,"terms":graph.numerator.terms.iter().map(|t|json!({"powers":t.exponents,"coefficient":t.coefficient.to_string()})).collect::<Vec<_>>()});
 std::fs::write(out.join("prepared-graph.json"),serde_json::to_vec_pretty(&graphrecord).unwrap()).unwrap();
 let domains=vec![domain("f64",0f64,&a,&b,&samples),domain("DoubleFloat",DoubleFloat::from(0f64),&a,&b,&samples),domain("Float128",Float::new(128),&a,&b,&samples)];
 let mixed=mixed_float(&a,&b,&samples);
 let mut empty=graph.clone();empty.numerator.terms.clear();let ae=baseline::CoefficientPlan::new(&empty,names.clone())?;let be=candidate::CoefficientPlan::new(&empty,names.clone())?;let emptyproof=structural(&ae,&be,out,"empty");
 for rows in [0,1,3]{let selected=vec![sample.clone();rows];let input=ae.pack(&selected,&0f64)?;let av=baseline::CoefficientWorkspace::new(&ae,0f64).evaluate(&input,rows)?;let bv=candidate::CoefficientWorkspace::new(&be,0f64).evaluate(&input,rows)?;assert!(av.values.is_empty());assert_eq!(av.rows,bv.rows);assert_eq!(av.components,bv.components);assert!(bv.values.is_empty());}
 let mut constant=graph.clone();constant.numerator.terms=vec![PolynomialTerm{exponents:[0;4],coefficient:Atom::parse("2/7","iregi_cli",Default::default()).unwrap()}];
 let ac=baseline::CoefficientPlan::new(&constant,vec![])?;let bc=candidate::CoefficientPlan::new(&constant,vec![])?;let constantproof=structural(&ac,&bc,out,"constant");
 let av=baseline::CoefficientWorkspace::new(&ac,Float::new(128)).evaluate(&[],3)?;let bv=candidate::CoefficientWorkspace::new(&bc,Float::new(128)).evaluate(&[],3)?;assert_eq!(values(&av.values),values(&bv.values));assert_eq!(av.values.len(),3);
 let result=json!({"status":"passed","case":case,"precision_domains":3,"batch_configurations_per_domain":6,"structure":structure,"empty":emptyproof,"constant":constantproof,"domains":domains,"mixed_float":mixed,"elapsed_seconds":started.elapsed().as_secs_f64(),"performance_scope":"Correctness and structural storage only; graph preparation/proof serialization excluded from any future kernel timing."});
 std::fs::write(out.join("outputs.json"),serde_json::to_vec_pretty(&result).unwrap()).unwrap();println!("CLI_COEFFICIENT_PASS {case}");Ok(())
}
fn main(){std::thread::Builder::new().stack_size(128*1024*1024).spawn(run).unwrap().join().unwrap().unwrap();}
