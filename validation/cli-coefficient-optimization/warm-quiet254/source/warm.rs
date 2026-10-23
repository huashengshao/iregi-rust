#![allow(dead_code)]
mod input;
mod coefficients;
mod proof;
use std::{hint::black_box,path::Path,time::Instant,io::Write};
use iregi_masters::{FloatLike,NativeFloat,Float,Complex};
use coefficients::{CoefficientPlan,CoefficientWorkspace,Mode};
use symbolica::{atom::Atom,domains::rational::Rational};
use iregi_rust::NumeratorBatch;
use iregi_prepare::{prepare_dot,NumeratorSource,PrepareOptions};
use serde_json::{json,Value};
use input::Sample;

fn values(output:&NumeratorBatch<f64>)->Value {
 json!({"rows":output.rows,"components":output.components,"values":output.values.iter().map(|z|json!({"real":z.re,"imaginary":z.im,"real_bits":z.re.to_bits(),"imaginary_bits":z.im.to_bits(),"real_precision":z.re.get_precision(),"imaginary_precision":z.im.get_precision()})).collect::<Vec<_>>()})
}
fn exact_check(a:&NumeratorBatch<f64>,b:&NumeratorBatch<f64>,expected:&[NumeratorBatch<f64>;2],scales:&[f64],stage:&str)->Result<(),String>{
 for (variant,result) in [a,b].into_iter().enumerate(){let reference=&expected[variant];
  if result.rows!=reference.rows||result.components!=1||reference.components!=1||result.values.len()!=reference.values.len()||result.values.len()!=scales.len(){return Err(format!("metadata mismatch at {stage}"));}
  for(slot,(a,b))in result.values.iter().zip(&reference.values).enumerate(){for(component,(a,b))in[(a.re,b.re),(a.im,b.im)].into_iter().enumerate(){if !a.is_finite()||!b.is_finite()||a.to_bits()!=b.to_bits()||a.get_precision()!=b.get_precision(){return Err(format!("variant {variant} changed own value/precision/sign at {stage}/{slot}/{component}"));}}}
 }
 for(slot,(a,b))in a.values.iter().zip(&b.values).enumerate(){for(component,(a,b))in[(a.re,b.re),(a.im,b.im)].into_iter().enumerate(){let scale=scales[slot].max(a.abs()).max(b.abs());if (a-b).abs()>1e-10*scale{return Err(format!("cross-mode dimensional mismatch at {stage}/{slot}/{component}"));}}}
 Ok(())
}
fn abs(q:Rational)->Rational{if q<Rational::from(0){-q}else{q}}
fn high_precision_check(actual:&NumeratorBatch<f64>,expected:&NumeratorBatch<Float>,scales:&[f64])->Result<Value,String>{
 if actual.rows!=expected.rows||actual.components!=expected.components||actual.values.len()!=expected.values.len()||actual.values.len()!=scales.len(){return Err("reference shape mismatch".into());}
 if scales.iter().any(|scale|!scale.is_finite()||*scale<=0.){return Err("invalid reference scale".into());}
 let tolerance=Rational::from((1,10_000_000_000_i64));let mut raw_failed=0usize;let mut normalized_max=Rational::from(0);let mut raw_max=Rational::from(0);
 for(slot,(a,b))in actual.values.iter().zip(&expected.values).enumerate(){for(a,b)in[(&a.re,&b.re),(&a.im,&b.im)]{let a=a.exact_rational().ok_or("nonfinite value")?;let b=b.exact_rational().ok_or("nonfinite reference")?;let error=abs(a.clone()-b.clone());let scale=abs(a).max(abs(b));let raw=error.clone()/scale.clone().max(Rational::from(1));let normalized=error/scale.max(scales[slot].exact_rational().unwrap());raw_failed+=usize::from(raw>tolerance);raw_max=raw_max.max(raw);normalized_max=normalized_max.max(normalized);}}
 if normalized_max>tolerance{return Err(format!("256-bit dimensional reference mismatch {normalized_max}"));}
 Ok(json!({"complex_outputs":actual.values.len(),"raw_1e10_failed_components_retained":raw_failed,"raw_max":raw_max.to_string(),"dimension_normalized_max":normalized_max.to_string(),"dimension_metric_passed":true}))
}
// Every call allocates the public NumeratorBatch output, consumes it through
// black_box, and drops its predecessor inside the measured interval.
// Only the final output survives for an exact check after the interval.
fn fixed_block<F:FnMut()->Result<NumeratorBatch<f64>,String>>(mut evaluate:F,iterations:u64)->Result<(u128,NumeratorBatch<f64>),String>{
 assert!(iterations>0);let mut last=None;let started=Instant::now();
 for _ in 0..iterations{last=Some(black_box(evaluate()?));}
 let elapsed=started.elapsed().as_nanos();Ok((elapsed,last.unwrap()))
}
fn next(seed:&mut u64)->u64{*seed^=*seed<<13;*seed^=*seed>>7;*seed^=*seed<<17;*seed}
fn order(seed:&mut u64)->Vec<usize>{let mut sequence:Vec<_>=(0..21).map(|i|i%2).collect();for i in(1..sequence.len()).rev(){let j=next(seed)as usize%(i+1);sequence.swap(i,j);}sequence}
fn write(path:&Path,value:&Value){let tmp=path.with_extension("pending.json");std::fs::write(&tmp,serde_json::to_vec_pretty(value).unwrap()).unwrap();std::fs::rename(tmp,path).unwrap();}
fn suite(case:&str,index:usize,mode:Mode,root:&Path,output:&Path)->Result<Value,String>{
 let(graphname,axes,expected_count)=match case{"ggh"=>("ggh_top_triangle",2,15),"gghh"=>("gghh_top_box",2,69),"gghhh"=>("gghhh_top_pentagon",2,69),"gggg-up"=>("gggg_up_box",4,70),_=>return Err("unknown graph".into())};
 let start=Instant::now();let graph=prepare_dot(&std::fs::read_to_string(root.join("fixtures/models/sm.json")).unwrap(),&std::fs::read_to_string(root.join(format!("examples/graphs/{graphname}.dot"))).unwrap(),&PrepareOptions{source:NumeratorSource::FeynmanRules,external_wavefunctions:true,component:Some(vec![0;axes])}).map_err(|e|e.to_string())?;let graph_ns=start.elapsed().as_nanos();
 if graph.numerator.terms.len()!=expected_count{return Err("physical coefficient count changed".into());}
 let sample:Sample=serde_json::from_slice(&std::fs::read(root.join(format!("validation/physical/{case}-cli-input.json"))).unwrap()).unwrap();
 let names:Vec<_>=sample.parameters.keys().cloned().collect();
 let start=Instant::now();let a=CoefficientPlan::new(Mode::Direct,&graph,names.clone())?;let baseline_plan_ns=start.elapsed().as_nanos();
 let start=Instant::now();let b=CoefficientPlan::new(mode,&graph,names.clone())?;let candidate_plan_ns=start.elapsed().as_nanos();
 if a.support()!=b.support(){return Err("support order changed".into());}
 let start=Instant::now();let parameters:Vec<_>=names.iter().map(|name|Atom::parse(name,"iregi_cli",Default::default()).unwrap()).collect();let expressions:Vec<_>=graph.numerator.terms.iter().map(|term|term.coefficient.clone()).collect();let aa=a.proof_exact().unwrap().export_instructions();let bb=b.proof_exact().unwrap().export_instructions();
 let baseline_proof=proof::prove(a.proof_exact().unwrap(),&parameters,&expressions)?;let candidate_proof=proof::prove(b.proof_exact().unwrap(),&parameters,&expressions)?;let proof_ns=start.elapsed().as_nanos();
 let dimension_proof:Value=serde_json::from_slice(&std::fs::read(root.join("homogeneity.json")).unwrap()).unwrap();let dimension=dimension_proof["cases"].as_array().unwrap().iter().find(|c|c["case"]==case).ok_or("missing dimension proof")?;
 if dimension["parameter_map"].as_array().unwrap().iter().map(|p|p["qualified"].as_str().unwrap()).ne(names.iter().map(String::as_str)){return Err("dimension parameter layout changed".into());}
 if dimension["homogeneity"].as_array().ok_or("invalid homogeneity entries")?.len()!=graph.numerator.terms.len(){return Err("dimension coefficient count mismatch".into());}
 for(term,identity)in graph.numerator.terms.iter().zip(dimension["homogeneity"].as_array().unwrap()){if identity["powers"]!=json!(term.exponents)||identity["scaling_identity_literal_zero"]!=true{return Err("dimension support mismatch".into());}}
 let mut result=json!({"case":case,"candidate_mode":mode.name(),"baseline_exact_proof":baseline_proof,"candidate_exact_proof":candidate_proof,"status":"prepared","coefficient_count":expected_count,"instructions":aa.instructions.len(),"baseline_temporary_slots":aa.temporary_count,"candidate_temporary_slots":bb.temporary_count,"setup":{"graph_preparation_ns":graph_ns,"baseline_exact_plan_ns":baseline_plan_ns,"candidate_exact_plan_ns":candidate_plan_ns,"structural_proof_ns":proof_ns},"rows":[]});
 write(output,&result);
 for rows in [1usize,32]{
  let start=Instant::now();let samples=vec![sample.clone();rows];let packed=a.pack(&samples,&0f64)?;if packed!=b.pack(&samples,&0f64)?{return Err("packed values differ".into());}let packing_ns=start.elapsed().as_nanos();
  let start=Instant::now();let mut aw=CoefficientWorkspace::new(&a,0f64);let baseline_map_ns=start.elapsed().as_nanos();
  let start=Instant::now();let mut bw=CoefficientWorkspace::new(&b,0f64);let candidate_map_ns=start.elapsed().as_nanos();
  let expected=[aw.evaluate(&packed,rows)?,bw.evaluate(&packed,rows)?];if expected[0].values.len()!=rows*expected_count||!expected[0].values.iter().any(|v|v.re!=0.||v.im!=0.){return Err("canonical nonzero control failed".into());}
  let input_width=names.len();let mut scales=Vec::new();for lane in 0..rows{let mut q=0f64;for(i,p)in dimension["parameter_map"].as_array().unwrap().iter().enumerate(){if p["dimension"]==1{let z=&packed[lane*input_width+i];if z.im!=0.{return Err("dimension scale requires real dimension-one inputs".into());}q=q.max(z.re.abs());}}if q<=0.||!q.is_finite(){return Err("invalid dimensional scale".into());}for identity in dimension["homogeneity"].as_array().unwrap(){scales.push(q.powi(identity["coefficient_dimension"].as_i64().unwrap()as i32));}}
  let p=Float::new(256);let lifted:Vec<_>=packed.iter().map(|v|Complex::new(symbolica::domains::float::SingleFloat::from_rational(&p,&v.re.exact_rational().unwrap()),symbolica::domains::float::SingleFloat::from_rational(&p,&v.im.exact_rational().unwrap()))).collect();let oracle=CoefficientWorkspace::<Float>::new(&a,p).evaluate(&lifted,rows)?;let reference_checks=[high_precision_check(&expected[0],&oracle,&scales)?,high_precision_check(&expected[1],&oracle,&scales)?];
  let mut outputs=[aw.evaluate(&packed,rows)?,bw.evaluate(&packed,rows)?];exact_check(&outputs[0],&outputs[1],&expected,&scales,"initial")?;
  for _ in 0..64 {outputs[0]=black_box(aw.evaluate(black_box(&packed),black_box(rows))?);outputs[1]=black_box(bw.evaluate(black_box(&packed),black_box(rows))?);}
  exact_check(&outputs[0],&outputs[1],&expected,&scales,"warmup")?;
  let mut pilots=[(0u64,0u128);2];
  for variant in 0..2{let mut iterations=8u64;loop{
   let(elapsed,last)=if variant==0{fixed_block(||aw.evaluate(black_box(&packed),black_box(rows)),iterations)?}else{fixed_block(||bw.evaluate(black_box(&packed),black_box(rows)),iterations)?};outputs[variant]=last;
   exact_check(&outputs[0],&outputs[1],&expected,&scales,"pilot")?;
   if elapsed>=2_000_000||iterations>=(1<<26){pilots[variant]=(iterations,elapsed);break;}iterations*=2;
  }}
  let numerator=2*30_000_000u128*u128::from(pilots[0].0)*u128::from(pilots[1].0);
  let denominator=pilots[0].1*u128::from(pilots[1].0)+pilots[1].1*u128::from(pilots[0].0);if denominator==0{return Err("zero-duration calibration".into());}
  let iterations=numerator.div_ceil(denominator).clamp(1,1<<26)as u64;
  let initial_seed=0x8ae4_d723_f209_16c5u64^(index as u64*97)^rows as u64;let mut seed=initial_seed;let ordering=order(&mut seed);
  let mut row=json!({"rows":rows,"status":"running","iterations_per_variant_per_block":iterations,"seed":initial_seed,"first_variant_by_block":ordering,"pilots":pilots,"setup":{"packing_ns":packing_ns,"baseline_workspace_mapping_ns":baseline_map_ns,"candidate_workspace_mapping_ns":candidate_map_ns},"parameter_names":names,"packed_input_bits":packed.iter().map(|v|[v.re.to_bits(),v.im.to_bits()]).collect::<Vec<_>>(),"expected_outputs_by_variant":[values(&expected[0]),values(&expected[1])],"reference_checks":reference_checks,"dimension_scales":scales,"blocks":[]});
  result["rows"].as_array_mut().unwrap().push(row.clone());write(output,&result);
  for(block,&first)in ordering.iter().enumerate(){
   exact_check(&outputs[0],&outputs[1],&expected,&scales,"before-paired-block")?;let mut elapsed=[0u128;2];
   for variant in [first,1-first]{let(ns,last)=if variant==0{fixed_block(||aw.evaluate(black_box(&packed),black_box(rows)),iterations)?}else{fixed_block(||bw.evaluate(black_box(&packed),black_box(rows)),iterations)?};elapsed[variant]=ns;outputs[variant]=last;}
   exact_check(&outputs[0],&outputs[1],&expected,&scales,"after-paired-block")?;
   let record=json!({"block":block,"first_variant":first,"iterations":iterations,"elapsed_ns":elapsed,"each_variant_matches_own_exact_value_precision_signed_zero":true,"cross_variant_dimension_metric_passed":true});println!("CLI_COEFFICIENT_TIMING {case} rows={rows} {record}");std::io::stdout().flush().unwrap();
   row["blocks"].as_array_mut().unwrap().push(record);let last=result["rows"].as_array_mut().unwrap().last_mut().unwrap();*last=row.clone();write(output,&result);
  }
  exact_check(&outputs[0],&outputs[1],&expected,&scales,"final")?;row["status"]="passed".into();row["final_outputs_by_variant"]=json!([values(&outputs[0]),values(&outputs[1])]);*result["rows"].as_array_mut().unwrap().last_mut().unwrap()=row;write(output,&result);
 }
 result["status"]="passed".into();write(output,&result);Ok(result)
}
fn run()->Result<(),String>{let args:Vec<_>=std::env::args().collect();let mode=match args.get(1).map(String::as_str){Some("cse0")=>Mode::Cse,Some("pair1")=>Mode::Pair1,_=>return Err("cse0 or pair1 required".into())};let output=Path::new(args.get(2).ok_or("new output directory required")?);std::fs::create_dir(output).map_err(|e|e.to_string())?;let root=Path::new("target/cli-coefficient-cse-timing/assets");let mut record=json!({"schema_version":2,"candidate_mode":mode.name(),"numerical_scope":"Retains raw coefficient failures; per-mode exact repeated outputs and cross-mode scale-aware metric are distinct checks","status":"started","domain":"f64","protocol":"fixed-loop seeded-balanced-random pairs v1","blocks":21,"target_ns_per_variant_block":30_000_000,"pilot_ns":2_000_000,"cache_policy":"immutable coefficient plans reused; fresh numerical workspaces for each graph/batch-size;64warmup evaluations each variant; no numerical memoization","allocation_policy":"each block includes N public output allocations and N-1 predecessor drops; final output retained for checking outside timer; exact plan and numerical workspace construction excluded","setup_scope":"one observation per setup stage, diagnostic only; no amortization claim","cases":[]});write(&output.join("results.json"),&record);
 for(index,case)in["ggh","gghh","gghhh","gggg-up"].into_iter().enumerate(){eprintln!("CLI_TIMING_START {case}");match suite(case,index,mode,root,&output.join(format!("{case}.json"))){Ok(result)=>record["cases"].as_array_mut().unwrap().push(result),Err(error)=>{record["status"]="failed".into();record["failure"]=json!({"case":case,"error":error});write(&output.join("results.json"),&record);return Err(error);}}write(&output.join("results.json"),&record);}
 record["status"]="passed".into();write(&output.join("results.json"),&record);Ok(())}
fn main(){std::thread::Builder::new().stack_size(128*1024*1024).spawn(run).unwrap().join().unwrap().unwrap();}
