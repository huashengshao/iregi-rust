//! Replay unchanged A0/B0/C0 kernels on captured, publicly validated master rows.
use std::{hint::black_box,path::Path,time::Instant};
use iregi_masters::{NativeFloat,ScalarIntegral};
use oneloop::rust_codegen::runtime::{BatchWorkspace,Context};
use serde_json::{json,Value};
use symbolica::{domains::{float::Complex,integer::Integer,rational::Rational},evaluate::BatchExpressionEvaluator};
use symbolica::prelude::SingleFloat;
mod native;
type C=Complex<f64>;
fn decode_component(v:&Value)->Result<f64,String>{
 if v["finite"]!=true||v["precision"]!=53{return Err("capture must retain finite binary64 inputs".into());}
 let text=v["rational"].as_str().ok_or("missing exact rational")?;
 let (num,den)=text.split_once('/').unwrap_or((text,"1"));
 let q=Rational::from((num.parse::<Integer>().map_err(|e|e.to_string())?,den.parse::<Integer>().map_err(|e|e.to_string())?));
 let sign=v["negative_sign"].as_bool().ok_or("missing represented sign")?;
 let mut value=0_f64.from_rational(&q);if value==0.&&sign{value=-0.;}
 if !value.is_finite()||value.exact_rational().as_ref()!=Some(&q)||value.is_sign_negative()!=sign{return Err(format!("captured representation did not roundtrip: {text}"));}
 Ok(value)
}
fn decode(v:&Value)->Result<C,String>{let parts=v.as_array().ok_or("invalid complex representation")?;if parts.len()!=2{return Err("invalid complex width".into());}Ok(C::new(decode_component(&parts[0])?,decode_component(&parts[1])?))}
fn same(a:&C,b:&C)->bool{a.re.to_bits()==b.re.to_bits()&&a.im.to_bits()==b.im.to_bits()}
fn finite(a:&C)->bool{a.re.is_finite()&&a.im.is_finite()}
struct Group{
 family:ScalarIntegral,rows:usize,input:Vec<C>,captured:Vec<C>,
 symbolic:BatchExpressionEvaluator<C>,native:BatchWorkspace<f64>,output:[Vec<C>;2],
}
impl Group{
 fn prepare(v:&Value)->Result<Self,String>{
  let family=match v["family"].as_str(){Some("A0")=>ScalarIntegral::A0,Some("B0")=>ScalarIntegral::B0,Some("C0")=>ScalarIntegral::C0,_=>return Err("unsupported captured family".into())};
  let rows=v["rows"].as_u64().ok_or("missing rows")? as usize;
  if rows==0||v["components"]!=1||!v["whole_batch_error"].is_null(){return Err("requires successful ordinary nonempty batch".into());}
  let errors=v["errors"].as_array().ok_or("missing lane errors")?;
  if errors.len()!=rows||errors.iter().any(|e|!e.is_null()){return Err("raw replay must not bypass invalid-lane compaction".into());}
  let input=v["input"].as_array().ok_or("missing input")?.iter().map(decode).collect::<Result<Vec<_>,_>>()?;
  if input.len()!=rows*family.arity(){return Err("captured input shape mismatch".into());}
  let expected=v["output"].as_array().ok_or("missing public outputs")?;
  if v["output_order"]!=json!(["finite","total_single","ir_double","uv_single","ir_single"]){return Err("public Laurent ordering changed".into());}
  if expected.len()!=rows{return Err("public result row count mismatch".into());}
  let mut captured=Vec::new();
  for row in expected{let row=row.as_array().ok_or("failed public row")?;if row.len()!=5{return Err("incomplete public Laurent outputs".into());}for value in row{captured.push(decode(value)?);}}
  let exact=iregi_masters::exact_scalar_master_evaluator(family).map_err(|e|e.to_string())?;
  let symbolic=exact.map_coeff_with_prec(&|v|C::new(0_f64.from_rational(&v.re),0_f64.from_rational(&v.im)),53).into_batch_evaluator();
  Ok(Self{family,rows,input,captured,symbolic,native:BatchWorkspace::new(0.),output:[vec![C::new(0.,0.);rows*6],vec![C::new(0.,0.);rows*6]]})
 }
 fn evaluate(&mut self,candidate:bool,ctx:&Context<f64>)->Result<(),String>{
  let input=black_box(self.input.as_slice());
  if candidate{native::evaluate(self.family,input,black_box(self.output[1].as_mut_slice()),self.rows,ctx,&mut self.native)}
  else{self.symbolic.evaluate_batch(input,black_box(self.output[0].as_mut_slice()),self.rows).map_err(|e|e.to_string())}
 }
 fn check(&self)->Result<Value,String>{
  let mut max_error=0_f64;let mut different_components=0;let mut sign_differences=0;
  for lane in 0..self.rows{
   let squared_scale=self.input[lane*self.family.arity()..(lane+1)*self.family.arity()].iter().map(|z|z.re.hypot(z.im)).fold(1_f64,f64::max);
   if !squared_scale.is_finite()||squared_scale<=0.{return Err("nonfinite or nonpositive dimensional scale".into());}
   let unit=match self.family{ScalarIntegral::A0=>squared_scale,ScalarIntegral::C0=>1./squared_scale,_=>1.};
   for coefficient in 0..6{
    let slot=lane*6+coefficient;let a=&self.output[0][slot];let b=&self.output[1][slot];
    if !finite(a)||!finite(b){return Err(format!("nonfinite {} lane{lane} coefficient{coefficient}",self.family.name()));}
    if coefficient<5&&!same(a,&self.captured[lane*5+coefficient]){return Err(format!("raw Symbolica differs from captured public adapter {} lane{lane} coefficient{coefficient}",self.family.name()));}
    if coefficient==5&&(a.re!=0.||a.im!=0.||b.re!=0.||b.im!=0.){return Err("ordinary derivative-domain coefficient is not zero".into());}
    let denominator=(if coefficient==5{1.}else{unit})+a.re.hypot(a.im);
    let error=(a.re-b.re).hypot(a.im-b.im)/denominator;
    if !unit.is_finite()||unit<=0.||!denominator.is_finite()||denominator<=0.||!error.is_finite()||error>1e-10{return Err(format!("native/Symbolica {} lane{lane} coefficient{coefficient}: normalized error{error}",self.family.name()));}max_error=max_error.max(error);
    for (a,b) in [(a.re,b.re),(a.im,b.im)]{different_components+=usize::from(a.to_bits()!=b.to_bits());sign_differences+=usize::from(a==0.&&b==0.&&a.to_bits()!=b.to_bits());}
   }
  }
  Ok(json!({"family":self.family.name(),"rows":self.rows,"complex_outputs":self.rows*6,"max_normalized_error":max_error,"represented_component_differences":different_components,"signed_zero_differences":sign_differences,"symbolica_matches_public_capture_exactly":true,"native_cells":self.native.storage_len()}))
 }
}
fn evaluate(groups:&mut[Group],candidate:bool,ctx:&Context<f64>)->Result<(),String>{for group in groups{group.evaluate(candidate,ctx)?;}Ok(())}
fn verify(groups:&[Group],snapshot:Option<&Vec<[Vec<C>;2]>>)->Result<Vec<Value>,String>{
 let mut result=Vec::new();for(i,group)in groups.iter().enumerate(){
  result.push(group.check()?);
  if let Some(snapshot)=snapshot{for variant in 0..2{if group.output[variant].len()!=snapshot[i][variant].len()||group.output[variant].iter().zip(&snapshot[i][variant]).any(|(a,b)|!same(a,b)){return Err(format!("repeat output changed in group{i}/backend{variant}"));}}}
 }Ok(result)
}
fn fixed_block(groups:&mut[Group],candidate:bool,ctx:&Context<f64>,iterations:u64)->Result<u128,String>{
 let start=Instant::now();for _ in 0..iterations{evaluate(black_box(&mut *groups),candidate,ctx)?;}Ok(start.elapsed().as_nanos())
}
fn benchmark(groups:&mut[Group],ctx:&Context<f64>,snapshot:&Vec<[Vec<C>;2]>)->Result<Value,String>{
 for _ in 0..10{evaluate(groups,false,ctx)?;evaluate(groups,true,ctx)?;}verify(groups,Some(snapshot))?;
 let pilot_target=2_000_000_u128;let target=30_000_000_u128;let mut pilots=[(0_u64,0_u128);2];
 for variant in 0..2{let mut count=8;loop{let elapsed=fixed_block(groups,variant==1,ctx,count)?;if elapsed>=pilot_target||count>=(1<<26){pilots[variant]=(count,elapsed);break;}count*=2;}}
 verify(groups,Some(snapshot))?;
 let numerator=2*target*u128::from(pilots[0].0)*u128::from(pilots[1].0);let denominator=pilots[0].1*u128::from(pilots[1].0)+pilots[1].1*u128::from(pilots[0].0);
 if denominator==0{return Err("zero-duration pilots".into());}let iterations=numerator.div_ceil(denominator).clamp(1,1<<26) as u64;
 // Frozen Python random.Random(173).shuffle([0; 11] + [1; 10]); no runtime RNG overhead.
 let first_variants=[0,0,1,0,0,1,0,0,1,0,1,0,0,1,1,1,0,1,1,1,0];
 let mut blocks=Vec::new();for (block,first) in first_variants.into_iter().enumerate(){let order=[first,1-first];let mut elapsed=[0_u128;2];for &variant in &order{elapsed[variant]=fixed_block(groups,variant==1,ctx,iterations)?;}verify(groups,Some(snapshot))?;blocks.push(json!({"block":block,"order":order,"iterations":iterations,"elapsed_ns":elapsed}));}
 Ok(json!({"protocol":"actual-master-replay-fixed-loop-v1","pair_order_seed":173,"pair_order_algorithm":"Python random.Random(seed).shuffle([0]*11+[1]*10)","pilot_target_ns":pilot_target,"block_target_ns":target,"pilots":pilots,"iterations":iterations,"blocks":blocks,"postcheck":verify(groups,Some(snapshot))?}))
}
fn run()->Result<(),String>{
 let benchmark_mode=std::env::args().any(|a|a=="--benchmark");let base=Path::new("target/native-master-replay");
 let captured:Value=serde_json::from_slice(&std::fs::read(base.join("capture-results.json")).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
 if captured["status"]!="passed"{return Err("capture corpus not qualified".into());}
 let context_started=Instant::now();let ctx=native::context();let context_ns=context_started.elapsed().as_nanos();
 let corpus=captured["rows"].as_array().ok_or("missing captured rows")?;if corpus.len()!=8{return Err("expected all eight original families".into());}
 let mut seen=std::collections::BTreeSet::new();let mut failures=0;
 for row in corpus{
  let mut report=json!({"id":row["id"],"outer_batch":row["outer_batch"],"native_context_preparation_ns":context_ns,"status":"pending","mode":if benchmark_mode{"timing"}else{"qualification"}});
  let work=(||->Result<Value,String>{
   if row["status"]!="passed"||row["capture"]["execution"]["fallback_rows"]!=0||row["capture"]["execution"]["analytic_rows"]!=0{return Err("unqualified or recursive capture row".into());}
   let n=row["n"].as_u64().ok_or("missing topology")?;let rank=row["rank"].as_u64().ok_or("missing rank")?;let width=row["outer_batch"].as_u64().ok_or("missing outer width")? as usize;
   if ![2,3].contains(&n)||rank>1||![1,32].contains(&width)||row["id"]!=format!("n{n}-r{rank}-massive")||!seen.insert((n,rank,width)){return Err("duplicate or unsupported capture coordinate".into());}
   let records=row["capture"]["master_captures"].as_array().ok_or("missing captured groups")?;
   let expected=match(n,rank){(2,0)=>vec![("B0",width)],(2,1)=>vec![("B0",width),("A0",2*width)],(3,0)=>vec![("C0",width)],(3,1)=>vec![("C0",width),("B0",3*width)],_=>unreachable!()};
   if records.len()!=expected.len()||row["capture"]["execution"]["master_family_batches"]!=records.len()||row["capture"]["execution"]["master_rows"]!=expected.iter().map(|(_,n)|n).sum::<usize>(){return Err("captured master/execution counts differ".into());}
   for (record,(family,rows)) in records.iter().zip(&expected){if record["family"]!=*family||record["rows"]!=*rows||record["requests"].as_array().map(Vec::len)!=Some(*rows)||record["valid_lanes"]!=json!((0..width).collect::<Vec<_>>()){return Err("captured family/order/request layout differs".into());}}
   let started=Instant::now();let mut groups=records.iter().map(Group::prepare).collect::<Result<Vec<_>,_>>()?;let preparation_ns=started.elapsed().as_nanos();
   evaluate(&mut groups,false,&ctx)?;evaluate(&mut groups,true,&ctx)?;let qualification=verify(&groups,None)?;
   let snapshot:Vec<_>=groups.iter().map(|g|g.output.clone()).collect();
   let timing=if benchmark_mode{Some(benchmark(&mut groups,&ctx,&snapshot)?)}else{
    for _ in 0..2{evaluate(&mut groups,true,&ctx)?;evaluate(&mut groups,false,&ctx)?;verify(&groups,Some(&snapshot))?;}None
   };
   Ok(json!({"preparation_ns":preparation_ns,"groups":qualification,"timing":timing,"represented_outputs":snapshot.iter().map(|pair|pair.iter().map(|v|v.iter().map(|z|[z.re.to_bits(),z.im.to_bits()]).collect::<Vec<_>>()).collect::<Vec<_>>()).collect::<Vec<_>>()}))
  })();
  match work{Ok(value)=>{report["status"]=json!("passed");report["result"]=value;},Err(error)=>{failures+=1;report["status"]=json!("failed");report["error"]=json!(error);}}
  println!("{report}");
 }
 if failures!=0||seen.len()!=8{Err(format!("{failures} failed replay rows;{} unique coordinates",seen.len()))}else{Ok(())}
}
fn main(){std::thread::Builder::new().stack_size(128*1024*1024).spawn(run).unwrap().join().unwrap().unwrap();}
