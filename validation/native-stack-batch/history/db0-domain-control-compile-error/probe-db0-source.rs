#![allow(dead_code,unused_mut)]
use oneloop::{ScalarIntegral, NativeFloat};
use oneloop::rust_codegen::runtime::BatchWorkspace;
use symbolica::{domains::{float::{Complex,DoubleFloat,Float},rational::Rational},evaluate::{EvaluationDomain, ExpressionEvaluator}};
use std::{hint::black_box,time::{Duration,Instant}};
#[cfg(family_c0)] #[path="c0/module.rs"] mod generated;
#[cfg(family_d0)] #[path="d0/module.rs"] mod generated;
#[cfg(family_a0)] #[path="a0/module.rs"] mod generated;
#[cfg(family_b0)] #[path="b0/module.rs"] mod generated;
#[cfg(family_db0)] #[path="db0/module.rs"] mod generated;
type Exact=ExpressionEvaluator<Complex<Rational>>;
fn point(values:&[f64],mass:std::ops::Range<usize>,width:bool)->Vec<Complex<f64>>{values.iter().enumerate().map(|(i,&re)|Complex::new(re,if width&&mass.contains(&i){-0.1}else{0.})).collect()}
fn cases(f:ScalarIntegral)->Vec<Vec<Complex<f64>>>{
 let mut p=match f{
  ScalarIntegral::A0=>vec![point(&[4.,1.],0..1,false),point(&[4.,1.],0..1,true),point(&[0.,1.],0..1,false)],
  ScalarIntegral::B0|ScalarIntegral::DB0=>vec![point(&[-1.,4.,9.,1.],1..3,false),point(&[30.,2.,3.,1.],1..3,false),point(&[1.,4.,9.,1.],1..3,true),point(&[-1.,0.,0.,1.],1..3,false),point(&[0.,0.,0.,1.],1..3,false)],
  ScalarIntegral::C0=>vec![point(&[1.,2.,3.,5.,7.,11.,1.],3..6,false),point(&[-1.,-2.,30.,2.,3.,5.,1.],3..6,false),point(&[1.,2.,3.,0.5,0.7,1.4,1.],3..6,true),point(&[-1.,-2.,30.,2.,3.,5.,1.],3..6,true),point(&[0.,0.,0.,0.,0.,0.,1.],3..6,false),point(&[0.,0.,-1.,0.,0.,0.,1.],3..6,false)],
  ScalarIntegral::D0=>vec![point(&[1.,1.,1.,1.,8.,-2.,20.,30.,40.,50.,1.],6..10,false),point(&[1.,1.,1.,1.,40.,-8.,2.,3.,4.,5.,1.],6..10,false),point(&[-1.,-2.,-3.,-4.,12.,-5.,2.,3.,4.,5.,1.],6..10,true),point(&[-1.,-2.,-3.,-4.,12.,-5.,2.,2.,2.,2.,1.],6..10,true),point(&[0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,1.],6..10,false),point(&[0.,0.,0.,0.,-2.,-3.,0.,0.,0.,0.,1.],6..10,false)]
 };
 if f==ScalarIntegral::DB0{p.remove(4);}
 // Scaled copy exercises the final squared-renormalization-scale argument.
 let mut scaled=p[0].clone();for z in &mut scaled{z.re*=4.;z.im*=4.;}p.push(scaled);p
}
fn same<T:NativeFloat>(a:&T,b:&T)->bool{a.is_finite()&&b.is_finite()&&a.exact_rational()==b.exact_rational()&&a.get_precision()==b.get_precision()&&(!a.is_zero()||a.negative_sign()==b.negative_sign())}
fn input<T:NativeFloat>(points:&[Vec<Complex<f64>>],rows:usize,ordering:&str,prototype:&T)->Vec<Complex<T>>{(0..rows).flat_map(|lane|{let index=match ordering{"homogeneous"=>0,"interleaved"=>lane%points.len(),"grouped"=>(lane*points.len()/rows).min(points.len()-1),_=>(rows-1-lane)%points.len()};points[index].iter().map(|v|Complex::new(prototype.from_rational(&v.re.exact_rational().unwrap()),prototype.from_rational(&v.im.exact_rational().unwrap())))}).collect()}
fn verify<T:NativeFloat>(label:&str,exact:&Exact,points:&[Vec<Complex<f64>>],prototype:T,rowsizes:&[usize])->Result<(),String> where Complex<T>:EvaluationDomain{
 let zero=Complex::new(prototype.zero(),prototype.zero());let context=generated::context(&prototype);
 let mut work=[BatchWorkspace::new(prototype.clone()),BatchWorkspace::new(prototype.clone())];
 let convert=|v:&Complex<Rational>|Complex::new(prototype.from_rational(&v.re),prototype.from_rational(&v.im));
 let mut interpreter=exact.clone().map_coeff_with_prec(&convert,prototype.get_precision()).into_batch_evaluator();
 #[cfg(family_db0)] {
  let mut invalid=vec![zero.clone();4];invalid[3].re=prototype.one();
  let mut raw=[vec![zero.clone();6],vec![zero.clone();6]];
  for i in 0..2{generated::evaluate(i==1,&invalid,&mut raw[i],1,&context,&mut work[i])?;}
  if raw[0][0].re.is_finite()||raw[1][0].re.is_finite(){return Err("expected nonfinite fully-scaleless raw dB0 control".into());}
  for (a,b) in raw[0].iter().zip(&raw[1]){for(a,b)in[(&a.re,&b.re),(&a.im,&b.im)]{
   let equal=if a.is_finite()&&b.is_finite(){same(a,b)}else{a.is_finite()==b.is_finite()&&a.is_nan()==b.is_nan()&&a.negative_sign()==b.negative_sign()&&a.get_precision()==b.get_precision()};
   if !equal{return Err(format!("unsupported raw dB0 control classification changed {label}: {a:?} != {b:?}"));}
  }}
  eprintln!("unsupported-control,{label},fully-scaleless-dB0,old-new-nonfinite-classification-equal");
 }
 for &rows in rowsizes{for order in ["homogeneous","interleaved","grouped","reversed"]{
  let input=input(points,rows,order,&prototype);let mut outputs=[vec![zero.clone();rows*6],vec![zero.clone();rows*6]];let mut expected=vec![zero.clone();rows*6];
  interpreter.evaluate_batch(&input,&mut expected,rows).map_err(|e|e.to_string())?;
  for i in 0..2{generated::evaluate(i==1,&input,&mut outputs[i],rows,&context,&mut work[i])?;}
  let mut represented_mismatch=0;let mut precision_mismatch=0;let mut zero_sign_mismatch=0;
  for (slot,((a,b),reference)) in outputs[0].iter().zip(&outputs[1]).zip(&expected).enumerate(){
   if !same(&a.re,&b.re)||!same(&a.im,&b.im){return Err(format!("native storage parity {label}/{order}/rows{rows}/slot{slot}: {a:?} != {b:?}"));}
   for (actual,reference) in [(&b.re,&reference.re),(&b.im,&reference.im)]{
    if !reference.is_finite(){return Err(format!("nonfinite interpreter control {label}/{order}/{rows}/{slot}: {reference:?}"));}
    if actual.exact_rational()!=reference.exact_rational(){represented_mismatch+=1;if represented_mismatch<=2{eprintln!("interpreter-value-difference {label}/{order}/{rows}/{slot}: native={actual:?} interpreter={reference:?}");}}
    if actual.get_precision()!=reference.get_precision(){precision_mismatch+=1;}
    if actual.is_zero()&&reference.is_zero()&&actual.negative_sign()!=reference.negative_sign(){zero_sign_mismatch+=1;}
   }
  }
  println!("parity,{label},{order},{rows},{},{},{},{},{},{}",rows*6,represented_mismatch,precision_mismatch,zero_sign_mismatch,work[0].storage_len(),work[1].storage_len());
 }}Ok(())
}
fn benchmark(points:&[Vec<Complex<f64>>])->Result<(),String>{
 let blocks=21;let time=Duration::from_millis(30);let context=generated::context(&0.);
 for rows in [1,32]{for order in ["homogeneous","interleaved","grouped"]{
  let input=input(points,rows,order,&0.);let mut work=[BatchWorkspace::new(0.),BatchWorkspace::new(0.)];let mut output=[vec![Complex::new(0.,0.);rows*6],vec![Complex::new(0.,0.);rows*6]];
  for i in 0..2{for _ in 0..10{generated::evaluate(i==1,&input,&mut output[i],rows,&context,&mut work[i])?;}}
  assert_eq!(output[0],output[1]);
  for block in 0..blocks{for offset in 0..2{let i=(block+offset)%2;let start=Instant::now();let mut iterations=0_u64;loop{generated::evaluate(i==1,black_box(&input),black_box(&mut output[i]),rows,&context,&mut work[i])?;iterations+=1;if start.elapsed()>=time{break;}}let ns=start.elapsed().as_nanos();println!("timing,{order},{rows},{i},{block},{iterations},{ns}");}}
 }}Ok(())
}
fn run()->Result<(),String>{
 #[cfg(family_a0)]let family=ScalarIntegral::A0;
 #[cfg(family_b0)]let family=ScalarIntegral::B0;
 #[cfg(family_db0)]let family=ScalarIntegral::DB0;
 #[cfg(family_c0)]let family=ScalarIntegral::C0;
 #[cfg(family_d0)]let family=ScalarIntegral::D0;
 let points=cases(family);
 #[cfg(family_db0)] {
  let mut public=iregi_masters::MasterEvaluator::new(ScalarIntegral::DB0,0.).unwrap();
  let invalid=vec![Complex::new(0.,0.),Complex::new(0.,0.),Complex::new(0.,0.),Complex::new(1.,0.)];
  let result=public.evaluate_batch(&invalid,1).unwrap();
  assert!(matches!(result.errors()[0],Some(iregi_masters::LaneError::UndefinedScalelessDerivative)));
  assert!(result.lane(0).is_err());
  eprintln!("unsupported-control,public-f64,fully-scaleless-dB0,UndefinedScalelessDerivative");
 }

 if std::env::args().any(|a|a=="--benchmark"){return benchmark(&points);}
 eprintln!("building {} exact interpreter",family.name());let exact=iregi_masters::exact_scalar_master_evaluator(family).map_err(|e|e.to_string())?;
 println!("kind,domain,ordering,rows,complex_outputs,interpreter_value_mismatches,interpreter_precision_mismatches,interpreter_signed_zero_mismatches,baseline_cells,candidate_cells");
 verify("f64",&exact,&points,0.,&[0,1,3,7,32,3])?;
 verify("DoubleFloat",&exact,&points,DoubleFloat::default(),&[points.len(),1])?;
 verify("Float256",&exact,&points,Float::new(256),&[points.len(),1])?;
 Ok(())
}
fn main(){std::thread::Builder::new().stack_size(128*1024*1024).spawn(run).unwrap().join().unwrap().unwrap();}
