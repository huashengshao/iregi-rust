#![allow(dead_code,unused_mut)]
use oneloop::{ScalarIntegral, NativeFloat};
use oneloop::rust_codegen::runtime::BatchWorkspace;
use symbolica::{domains::{float::{Complex,DoubleFloat,Float},rational::Rational},evaluate::{EvaluationDomain, ExpressionEvaluator}};
use std::{hint::black_box,time::{Duration,Instant}};
#[path="b0/module.rs"] mod b0;
#[path="c0/module.rs"] mod c0;
#[path="fixture/module.rs"] mod fixture;
mod shared_binary_kernel;
mod kernel_controls;
fn generated_context<T:NativeFloat>(family:ScalarIntegral,prototype:&T)->oneloop::rust_codegen::runtime::Context<T>{
 match family{ScalarIntegral::B0=>b0::context(prototype),ScalarIntegral::C0=>c0::context(prototype),_=>unreachable!()}
}
fn generated_evaluate<T:NativeFloat>(family:ScalarIntegral,candidate:bool,input:&[Complex<T>],output:&mut[Complex<T>],rows:usize,context:&oneloop::rust_codegen::runtime::Context<T>,work:&mut BatchWorkspace<T>)->Result<(),String>{
 match family{ScalarIntegral::B0=>b0::evaluate(candidate,input,output,rows,context,work),ScalarIntegral::C0=>c0::evaluate(candidate,input,output,rows,context,work),_=>unreachable!()}
}
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
fn verify<T:NativeFloat>(family:ScalarIntegral,label:&str,exact:&Exact,points:&[Vec<Complex<f64>>],prototype:T,rowsizes:&[usize])->Result<(),String> where Complex<T>:EvaluationDomain{
 let zero=Complex::new(prototype.zero(),prototype.zero());let context=generated_context(family,&prototype);
 let mut work=[BatchWorkspace::new(prototype.clone()),BatchWorkspace::new(prototype.clone())];
 let convert=|v:&Complex<Rational>|Complex::new(prototype.from_rational(&v.re),prototype.from_rational(&v.im));
 let mut interpreter=exact.clone().map_coeff_with_prec(&convert,prototype.get_precision()).into_batch_evaluator();
 #[cfg(family_db0)] {
  let mut invalid=vec![zero.clone();4];invalid[3].re=prototype.one();
  let mut raw=[vec![zero.clone();6],vec![zero.clone();6]];
  for i in 0..2{generated_evaluate(family,i==1,&invalid,&mut raw[i],1,&context,&mut work[i])?;}
  if raw[0][0].re.is_finite()||raw[1][0].re.is_finite(){return Err("expected nonfinite fully-scaleless raw dB0 control".into());}
  for (a,b) in raw[0].iter().zip(&raw[1]){for(a,b)in[(&a.re,&b.re),(&a.im,&b.im)]{
   let equal=if a.is_finite()&&b.is_finite(){same(a,b)}else{a.is_finite()==b.is_finite()&&(a!=a)==(b!=b)&&a.negative_sign()==b.negative_sign()&&a.get_precision()==b.get_precision()};
   if !equal{return Err(format!("unsupported raw dB0 control classification changed {label}: {a:?} != {b:?}"));}
  }}
  eprintln!("unsupported-control,{label},fully-scaleless-dB0,old-new-nonfinite-classification-equal");
 }
 for &rows in rowsizes{for order in ["homogeneous","interleaved","grouped","reversed"]{
  let input=input(points,rows,order,&prototype);let mut outputs=[vec![zero.clone();rows*6],vec![zero.clone();rows*6]];let mut expected=vec![zero.clone();rows*6];
  interpreter.evaluate_batch(&input,&mut expected,rows).map_err(|e|e.to_string())?;
  for i in 0..2{generated_evaluate(family,i==1,&input,&mut outputs[i],rows,&context,&mut work[i])?;}
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
fn exact_native_pair<T:NativeFloat>(outputs:&[Vec<Complex<T>>;2],stage:&str,order:&str,rows:usize)->Result<(),String>{
 for (slot,(a,b)) in outputs[0].iter().zip(&outputs[1]).enumerate(){
  if !same(&a.re,&b.re)||!same(&a.im,&b.im){return Err(format!("native fixed-loop parity {stage}/{order}/rows{rows}/slot{slot}: {a:?} != {b:?}"));}
 }
 Ok(())
}
// Fixed-loop protocol v2: calibration is excluded from the measured blocks.
// A shared iteration count gives both variants identical work in each block.
fn fixed_block(family:ScalarIntegral,candidate:bool,input:&[Complex<f64>],output:&mut [Complex<f64>],rows:usize,context:&oneloop::rust_codegen::runtime::Context<f64>,work:&mut BatchWorkspace<f64>,iterations:u64)->Result<u128,String>{
 let started=Instant::now();
 for _ in 0..iterations{
  generated_evaluate(family,candidate,black_box(input),black_box(&mut *output),rows,context,work)?;
 }
 Ok(started.elapsed().as_nanos())
}
fn benchmark(family:ScalarIntegral,points:&[Vec<Complex<f64>>])->Result<(),String>{
 let blocks=21;let target_ns=Duration::from_millis(30).as_nanos();let pilot_ns=Duration::from_millis(2).as_nanos();let context=generated_context(family,&0.);
 eprintln!("timing-protocol,shared-binary-fixed-loop-v2,blocks={blocks},target_ns={target_ns},pilot_ns={pilot_ns},paired_shared_iterations=true");
 for rows in [1,32]{for order in ["homogeneous","interleaved","grouped"]{
  let input=input(points,rows,order,&0.);let mut work=[BatchWorkspace::new(0.),BatchWorkspace::new(0.)];let mut output=[vec![Complex::new(0.,0.);rows*6],vec![Complex::new(0.,0.);rows*6]];
  for i in 0..2{for _ in 0..10{generated_evaluate(family,i==1,&input,&mut output[i],rows,&context,&mut work[i])?;}}
  exact_native_pair(&output,"warmup",order,rows)?;
  let mut pilots=[(0_u64,0_u128);2];
  for i in 0..2{
   let mut iterations=8_u64;
   loop{
    let elapsed=fixed_block(family,i==1,&input,&mut output[i],rows,&context,&mut work[i],iterations)?;
    if elapsed>=pilot_ns||iterations>=(1<<26){pilots[i]=(iterations,elapsed);break;}
    iterations*=2;
   }
   eprintln!("calibration,{order},{rows},{i},{},{}",pilots[i].0,pilots[i].1);
  }
  exact_native_pair(&output,"after-calibration",order,rows)?;
  // Target the mean pilot cost; integer arithmetic avoids conversion-dependent counts.
  let numerator=2*target_ns*u128::from(pilots[0].0)*u128::from(pilots[1].0);
  let denominator=pilots[0].1*u128::from(pilots[1].0)+pilots[1].1*u128::from(pilots[0].0);
  if denominator==0{return Err("zero-duration fixed-loop calibration".into());}
  let iterations=numerator.div_ceil(denominator).clamp(1,1<<26) as u64;
  eprintln!("calibrated-iterations,{order},{rows},{iterations}");
  for block in 0..blocks{for offset in 0..2{
   let i=(block+offset)%2;
   let elapsed=fixed_block(family,i==1,&input,&mut output[i],rows,&context,&mut work[i],iterations)?;
   println!("timing,{order},{rows},{i},{block},{iterations},{elapsed}");
  }
   exact_native_pair(&output,"after-paired-block",order,rows)?;
  }
  exact_native_pair(&output,"final",order,rows)?;
 }}Ok(())
}
fn invalid_neighbor_and_shape_controls(family:ScalarIntegral,points:&[Vec<Complex<f64>>])->Result<(),String>{
 let context=generated_context(family,&0.);let mut work=[BatchWorkspace::new(0.),BatchWorkspace::new(0.)];
 let warm=input(points,32,"interleaved",&0.);let mut warm_output=vec![Complex::new(0.,0.);32*6];
 for i in 0..2{generated_evaluate(family,i==1,&warm,&mut warm_output,32,&context,&mut work[i])?;}
 let rows=7;let clean=input(points,rows,"interleaved",&0.);let mut bad=clean.clone();let bad_lane=3;bad[bad_lane*family.arity()].re=f64::NAN;
 let mut clean_output=[vec![Complex::new(0.,0.);rows*6],vec![Complex::new(0.,0.);rows*6]];let mut bad_output=clean_output.clone();
 for i in 0..2{
  generated_evaluate(family,i==1,&clean,&mut clean_output[i],rows,&context,&mut work[i])?;
  generated_evaluate(family,i==1,&bad,&mut bad_output[i],rows,&context,&mut work[i])?;
 }
 for lane in 0..rows{for coefficient in 0..6{let slot=lane*6+coefficient;
  for component in 0..2{
   let part=|z:&Complex<f64>|if component==0{z.re}else{z.im};let a=part(&bad_output[0][slot]);let b=part(&bad_output[1][slot]);
   if lane==bad_lane{
    let equal=if a.is_finite()&&b.is_finite(){same(&a,&b)}else if a.is_nan()&&b.is_nan(){true}else{a.to_bits()==b.to_bits()};
    if !equal{return Err(format!("invalid-lane classification differs slot{slot}: {a:?} versus {b:?}"));}
   }else{
    for i in 0..2{let clean_value=part(&clean_output[i][slot]);let invalid_neighbor_value=part(&bad_output[i][slot]);if !same(&clean_value,&invalid_neighbor_value){return Err(format!("invalid neighbor corrupted variant{i}/lane{lane}/slot{slot}"));}}
    if !same(&a,&b){return Err(format!("dense parity failed beside invalid lane at slot{slot}"));}
   }
  }
 }}
 // The raw kernel has no input validator. Confirm the existing public boundary
 // explicitly rejects the injected lane while allowing its valid neighbors.
 let mut public=iregi_masters::MasterEvaluator::new(family,0.).map_err(|e|e.to_string())?;
 let guarded=public.evaluate_batch(&bad,rows).map_err(|e|e.to_string())?;
 if !matches!(guarded.errors()[bad_lane],Some(iregi_masters::LaneError::NonFiniteInput{..})){return Err("public invalid-neighbor control was not rejected".into());}
 for lane in 0..rows{if lane!=bad_lane&&guarded.errors()[lane].is_some(){return Err(format!("public neighbor failed at lane{lane}: {:?}",guarded.errors()[lane]));}}
 for i in 0..2{
  let sentinel=Complex::new(99.,-0.);let mut untouched=vec![sentinel;rows*6];
  if generated_evaluate(family,i==1,&clean[..clean.len()-1],&mut untouched,rows,&context,&mut work[i]).is_ok(){return Err("malformed input shape accepted".into());}
  if untouched.iter().any(|z|!same(&z.re,&sentinel.re)||!same(&z.im,&sentinel.im)){return Err("shape failure modified output".into());}
 }
 eprintln!("control,invalid-neighbor,rows7,retained-stride32,bad-lane3,all-six-complex-outputs,passed; raw NaN classifications matched, public NonFiniteInput rejected");
 eprintln!("control,malformed-shape,output-unchanged-including-signed-zero,passed");
 Ok(())
}
fn fixture_control_flow<T:NativeFloat>(label:&str,prototype:T)->Result<(),String>{
 let context=fixture::context(&prototype);let mut work=[BatchWorkspace::new(prototype.clone()),BatchWorkspace::new(prototype.clone())];
 let mut configurations=0;let mut comparisons=0;
 for rows in [32,0,1,3,7,8,32,33,3]{for pattern in ["all","offset-span","holes","empty"]{
  let input:Vec<_>=(0..rows).flat_map(|lane|{
   let active=match pattern{"all"=>true,"offset-span"=>(3..7).contains(&lane),"holes"=>lane%2==1,_=>false};
   [Complex::new(if active{prototype.one()}else{-prototype.zero()},prototype.zero()),Complex::new(prototype.from_rational(&Rational::from(if active{2+lane as i64}else{-1})),prototype.zero()),Complex::new(prototype.from_rational(&Rational::from(1+(lane%3) as i64)),prototype.zero())]
  }).collect();
  let mut output=[vec![Complex::new(prototype.zero(),prototype.zero());rows*6],vec![Complex::new(prototype.zero(),prototype.zero());rows*6]];
  for i in 0..2{fixture::evaluate(i==1,&input,&mut output[i],rows,&context,&mut work[i])?;}
  exact_native_pair(&output,"control-fixture",pattern,rows)?;
  for lane in 0..rows{
   let expected=fixture::scalar(&input[lane*3..(lane+1)*3],&context);
   for component in 0..6{let slot=lane*6+component;
    for i in 0..2{let a=&output[i][slot];let b=&expected[component];if !same(&a.re,&b.re)||!same(&a.im,&b.im){return Err(format!("fixture scalar parity variant{i}/{pattern}/rows{rows}/lane{lane}/component{component}: {a:?} != {b:?}"));}}
    comparisons+=1;
   }
  }
  configurations+=1;
 }}
 eprintln!("control,symbolica-generated-fixture,{label},configurations={configurations},complex-outputs={comparisons},all-six-outputs,nonzero-origin-span,sparse-holes,empty-reactivation-after-outline,alias,reused-stride,scalar-and-batch-exact,passed");
 Ok(())
}
fn run()->Result<(),String>{
 for family in [ScalarIntegral::B0,ScalarIntegral::C0]{
  let points=cases(family);
  if std::env::args().any(|a|a==format!("--benchmark-{}",family.name().to_ascii_lowercase())){return benchmark(family,&points);}
 }
 println!("kind,domain,ordering,rows,complex_outputs,interpreter_value_mismatches,interpreter_precision_mismatches,interpreter_signed_zero_mismatches,baseline_cells,candidate_cells");
 for family in [ScalarIntegral::B0,ScalarIntegral::C0]{
  let points=cases(family);
  eprintln!("building {} exact interpreter",family.name());
  let exact=iregi_masters::exact_scalar_master_evaluator(family).map_err(|e|e.to_string())?;
  verify(family,&format!("{}-f64",family.name()),&exact,&points,0.,&[0,1,3,7,32,3])?;
  invalid_neighbor_and_shape_controls(family,&points)?;
  verify(family,&format!("{}-DoubleFloat",family.name()),&exact,&points,DoubleFloat::default(),&[points.len(),1])?;
  verify(family,&format!("{}-Float256",family.name()),&exact,&points,Float::new(256),&[points.len(),1])?;
 }
 fixture_control_flow("f64",0.)?;
 fixture_control_flow("DoubleFloat",DoubleFloat::default())?;
 fixture_control_flow("Float256",Float::new(256))?;
 kernel_controls::run("f64",0.)?;
 kernel_controls::run("DoubleFloat",DoubleFloat::default())?;
 kernel_controls::run("Float256-mixed80-128-256",Float::new(256))?;
 Ok(())
}
fn main(){std::thread::Builder::new().stack_size(128*1024*1024).spawn(run).unwrap().join().unwrap().unwrap();}
