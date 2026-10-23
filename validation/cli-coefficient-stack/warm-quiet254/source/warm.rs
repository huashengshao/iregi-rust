#![allow(dead_code)]
mod input;
mod baseline;
mod candidate;
mod proof;
use std::{collections::BTreeMap,hint::black_box,path::Path,time::Instant,io::Write};
use iregi_masters::FloatLike;
use iregi_rust::NumeratorBatch;
use iregi_prepare::{prepare_dot,NumeratorSource,PrepareOptions};
use serde_json::{json,Value};
use input::Sample;

fn values(output:&NumeratorBatch<f64>)->Value {
 json!({"rows":output.rows,"components":output.components,"values":output.values.iter().map(|z|json!({"real":z.re,"imaginary":z.im,"real_bits":z.re.to_bits(),"imaginary_bits":z.im.to_bits(),"real_precision":z.re.get_precision(),"imaginary_precision":z.im.get_precision()})).collect::<Vec<_>>()})
}
fn exact_check(a:&NumeratorBatch<f64>,b:&NumeratorBatch<f64>,expected:&NumeratorBatch<f64>,stage:&str)->Result<(),String>{
 if a.rows!=b.rows||a.rows!=expected.rows||a.components!=1||b.components!=1||expected.components!=1||a.values.len()!=b.values.len()||a.values.len()!=expected.values.len(){return Err(format!("metadata/shape mismatch at {stage}"));}
 for(slot,((a,b),reference))in a.values.iter().zip(&b.values).zip(&expected.values).enumerate(){
  for(component,(a,b,reference))in[(a.re,b.re,reference.re),(a.im,b.im,reference.im)].into_iter().enumerate(){
   if !a.is_finite()||!b.is_finite()||!reference.is_finite(){return Err(format!("nonfinite coefficient at {stage}/{slot}/{component}"));}
   let scale=1f64.max(a.abs()).max(b.abs()).max(reference.abs());
   if (a-b).abs()>1e-10*scale||(a-reference).abs()>1e-10*scale{return Err(format!("mixed absolute/relative mismatch at {stage}/{slot}/{component}"));}
   if a.to_bits()!=b.to_bits()||a.to_bits()!=reference.to_bits()||a.get_precision()!=b.get_precision()||a.get_precision()!=reference.get_precision(){return Err(format!("represented value/precision/signed-zero mismatch at {stage}/{slot}/{component}"));}
  }
 }
 Ok(())
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
fn suite(case:&str,index:usize,root:&Path,output:&Path)->Result<Value,String>{
 let(graphname,axes,expected_count)=match case{"ggh"=>("ggh_top_triangle",2,15),"gghh"=>("gghh_top_box",2,69),"gghhh"=>("gghhh_top_pentagon",2,69),"gggg-up"=>("gggg_up_box",4,70),_=>return Err("unknown graph".into())};
 let start=Instant::now();let graph=prepare_dot(&std::fs::read_to_string(root.join("fixtures/models/sm.json")).unwrap(),&std::fs::read_to_string(root.join(format!("examples/graphs/{graphname}.dot"))).unwrap(),&PrepareOptions{source:NumeratorSource::FeynmanRules,external_wavefunctions:true,component:Some(vec![0;axes])}).map_err(|e|e.to_string())?;let graph_ns=start.elapsed().as_nanos();
 if graph.numerator.terms.len()!=expected_count{return Err("physical coefficient count changed".into());}
 let sample:Sample=serde_json::from_slice(&std::fs::read(root.join(format!("validation/physical/{case}-cli-input.json"))).unwrap()).unwrap();
 let names:Vec<_>=sample.parameters.keys().cloned().collect();
 let start=Instant::now();let a=baseline::CoefficientPlan::new(&graph,names.clone())?;let baseline_plan_ns=start.elapsed().as_nanos();
 let start=Instant::now();let b=candidate::CoefficientPlan::new(&graph,names.clone())?;let candidate_plan_ns=start.elapsed().as_nanos();
 if a.support()!=b.support(){return Err("support order changed".into());}
 let start=Instant::now();let aa=a.proof_exact().unwrap().export_instructions();let bb=b.proof_exact().unwrap().export_instructions();
 if proof::provenance(&aa)?!=proof::provenance(&bb)?{return Err("instruction semantics changed".into());}
 let mut ah=BTreeMap::new();let mut bh=BTreeMap::new();proof::helpers(&aa,&mut ah)?;proof::helpers(&bb,&mut bh)?;if ah!=bh{return Err("shared helpers changed".into());}
 let proof_ns=start.elapsed().as_nanos();
 let mut result=json!({"case":case,"status":"prepared","coefficient_count":expected_count,"instructions":aa.instructions.len(),"baseline_temporary_slots":aa.temporary_count,"candidate_temporary_slots":bb.temporary_count,"setup":{"graph_preparation_ns":graph_ns,"baseline_exact_plan_ns":baseline_plan_ns,"candidate_exact_plan_ns":candidate_plan_ns,"structural_proof_ns":proof_ns},"rows":[]});
 write(output,&result);
 for rows in [1usize,32]{
  let start=Instant::now();let samples=vec![sample.clone();rows];let packed=a.pack(&samples,&0f64)?;if packed!=b.pack(&samples,&0f64)?{return Err("packed values differ".into());}let packing_ns=start.elapsed().as_nanos();
  let start=Instant::now();let mut aw=baseline::CoefficientWorkspace::new(&a,0f64);let baseline_map_ns=start.elapsed().as_nanos();
  let start=Instant::now();let mut bw=candidate::CoefficientWorkspace::new(&b,0f64);let candidate_map_ns=start.elapsed().as_nanos();
  let expected=aw.evaluate(&packed,rows)?;if expected.values.len()!=rows*expected_count||!expected.values.iter().any(|v|v.re!=0.||v.im!=0.){return Err("canonical physical coefficients missing/nonzero control failed".into());}
  let mut outputs=[aw.evaluate(&packed,rows)?,bw.evaluate(&packed,rows)?];exact_check(&outputs[0],&outputs[1],&expected,"initial")?;
  for _ in 0..64 {outputs[0]=black_box(aw.evaluate(black_box(&packed),black_box(rows))?);outputs[1]=black_box(bw.evaluate(black_box(&packed),black_box(rows))?);}
  exact_check(&outputs[0],&outputs[1],&expected,"warmup")?;
  let mut pilots=[(0u64,0u128);2];
  for variant in 0..2{let mut iterations=8u64;loop{
   let(elapsed,last)=if variant==0{fixed_block(||aw.evaluate(black_box(&packed),black_box(rows)),iterations)?}else{fixed_block(||bw.evaluate(black_box(&packed),black_box(rows)),iterations)?};outputs[variant]=last;
   exact_check(&outputs[0],&outputs[1],&expected,"pilot")?;
   if elapsed>=2_000_000||iterations>=(1<<26){pilots[variant]=(iterations,elapsed);break;}iterations*=2;
  }}
  let numerator=2*30_000_000u128*u128::from(pilots[0].0)*u128::from(pilots[1].0);
  let denominator=pilots[0].1*u128::from(pilots[1].0)+pilots[1].1*u128::from(pilots[0].0);if denominator==0{return Err("zero-duration calibration".into());}
  let iterations=numerator.div_ceil(denominator).clamp(1,1<<26)as u64;
  let initial_seed=0x8ae4_d723_f209_16c5u64^(index as u64*97)^rows as u64;let mut seed=initial_seed;let ordering=order(&mut seed);
  let mut row=json!({"rows":rows,"status":"running","iterations_per_variant_per_block":iterations,"seed":initial_seed,"first_variant_by_block":ordering,"pilots":pilots,"setup":{"packing_ns":packing_ns,"baseline_workspace_mapping_ns":baseline_map_ns,"candidate_workspace_mapping_ns":candidate_map_ns},"parameter_names":names,"packed_input_bits":packed.iter().map(|v|[v.re.to_bits(),v.im.to_bits()]).collect::<Vec<_>>(),"expected_outputs":values(&expected),"blocks":[]});
  result["rows"].as_array_mut().unwrap().push(row.clone());write(output,&result);
  for(block,&first)in ordering.iter().enumerate(){
   exact_check(&outputs[0],&outputs[1],&expected,"before-paired-block")?;let mut elapsed=[0u128;2];
   for variant in [first,1-first]{let(ns,last)=if variant==0{fixed_block(||aw.evaluate(black_box(&packed),black_box(rows)),iterations)?}else{fixed_block(||bw.evaluate(black_box(&packed),black_box(rows)),iterations)?};elapsed[variant]=ns;outputs[variant]=last;}
   exact_check(&outputs[0],&outputs[1],&expected,"after-paired-block")?;
   let record=json!({"block":block,"first_variant":first,"iterations":iterations,"elapsed_ns":elapsed,"all_output_bits_precision_signed_zero_equal":true});println!("CLI_COEFFICIENT_TIMING {case} rows={rows} {record}");std::io::stdout().flush().unwrap();
   row["blocks"].as_array_mut().unwrap().push(record);let last=result["rows"].as_array_mut().unwrap().last_mut().unwrap();*last=row.clone();write(output,&result);
  }
  exact_check(&outputs[0],&outputs[1],&expected,"final")?;row["status"]="passed".into();row["final_outputs"]=values(&outputs[1]);*result["rows"].as_array_mut().unwrap().last_mut().unwrap()=row;write(output,&result);
 }
 result["status"]="passed".into();write(output,&result);Ok(result)
}
fn run()->Result<(),String>{let args:Vec<_>=std::env::args().collect();let output=Path::new(args.get(1).ok_or("new output directory required")?);std::fs::create_dir(output).map_err(|e|e.to_string())?;let root=Path::new("target/cli-coefficient-timing/assets");let mut record=json!({"schema_version":1,"status":"started","domain":"f64","protocol":"fixed-loop seeded-balanced-random pairs v1","blocks":21,"target_ns_per_variant_block":30_000_000,"pilot_ns":2_000_000,"cache_policy":"immutable coefficient plans reused; fresh numerical workspaces for each graph/batch-size;64warmup evaluations each variant; no numerical memoization","allocation_policy":"each block includes N public output allocations and N-1 predecessor drops; final output retained for checking outside timer; exact plan and numerical workspace construction excluded","setup_scope":"one observation per setup stage, diagnostic only; no amortization claim","cases":[]});write(&output.join("results.json"),&record);
 for(index,case)in["ggh","gghh","gghhh","gggg-up"].into_iter().enumerate(){eprintln!("CLI_TIMING_START {case}");match suite(case,index,root,&output.join(format!("{case}.json"))){Ok(result)=>record["cases"].as_array_mut().unwrap().push(result),Err(error)=>{record["status"]="failed".into();record["failure"]=json!({"case":case,"error":error});write(&output.join("results.json"),&record);return Err(error);}}write(&output.join("results.json"),&record);}
 record["status"]="passed".into();write(&output.join("results.json"),&record);Ok(())}
fn main(){std::thread::Builder::new().stack_size(128*1024*1024).spawn(run).unwrap().join().unwrap().unwrap();}
