//! One untimed reduction per JSONL request, retaining every actual master row.
use std::io::{self,BufRead,Write};
use iregi_rust::{Algorithm,KinematicsBatch,ReductionPlan,ReductionSettings,Workspace,LaneStatus,take_master_captures};
use serde::Deserialize;
use serde_json::{Value,json};
use symbolica::domains::float::Complex;
#[derive(Deserialize)]struct Sample{shifts:Vec<[f64;4]>,masses:Vec<[f64;2]>,mu:f64}
#[derive(Deserialize)]struct Request{id:String,n:usize,rank:u16,algorithm:Algorithm,samples:Vec<Sample>}
struct Prepared{key:(usize,u16,Algorithm),workspace:Workspace<f64>,degrees:Vec<usize>}
fn run(request:&Request,prepared:&mut Option<Prepared>)->Result<Value,String>{
 if ![2,3].contains(&request.n)||request.rank>1||request.samples.is_empty(){return Err("capture scope is nonempty N2/N3 rank0/1".into());}
 let mut values=Vec::new();
 for sample in &request.samples{
  if sample.shifts.len()!=request.n||sample.masses.len()!=request.n{return Err("kinematic shape mismatch".into());}
  values.extend(sample.shifts.iter().flatten().map(|&v|Complex::new(v,0.)));
  values.extend(sample.masses.iter().map(|v|Complex::new(v[0],v[1])));values.push(Complex::new(sample.mu,0.));
 }
 let batch=KinematicsBatch{rows:request.samples.len(),components:1,values};
 let key=(request.n,request.rank,request.algorithm);let reused=prepared.as_ref().is_some_and(|p|p.key==key);
 if !reused{
  let mut settings=ReductionSettings::new(request.n,request.rank);settings.algorithm=request.algorithm;
  let plan=ReductionPlan::new(settings).map_err(|e|e.to_string())?;
  *prepared=Some(Prepared{key,workspace:Workspace::new(&plan,0.).map_err(|e|e.to_string())?,degrees:plan.basis().iter().map(|m|m.rank()).collect()});
 }
 assert!(take_master_captures().is_empty(),"unconsumed prior captures");
 let p=prepared.as_mut().unwrap();let result=p.workspace.reduce_batch(&batch).map_err(|e|e.to_string())?;
 let captures=take_master_captures();let stats=p.workspace.last_execution();
 let lanes:Vec<_>=(0..batch.rows).map(|lane|match result.lane(lane){
  Ok(values)=>json!({"status":"success","moments":values.chunks_exact(4).map(|pole|pole.iter().map(|v|[v.re,v.im]).collect::<Vec<_>>()).collect::<Vec<_>>(),"fallback_used":result.fallback_used[lane],"analytic_used":result.analytic_used[lane]}),
  Err(error)=>json!({"status":format!("{error:?}"),"moments":null}),
 }).collect();
 Ok(json!({"id":request.id,"n":request.n,"rank":request.rank,"batch":batch.rows,"plan_reused":reused,"degrees":p.degrees,
  "stable":result.statuses.iter().all(|s|*s==LaneStatus::Success),"lanes":lanes,"diagnostics":p.workspace.last_diagnostics(),
  "master_backend":format!("{:?}",iregi_masters::default_master_backend()),"master_captures":captures,
  "execution":{"input_rows":stats.input_rows,"argument_rows":stats.argument_rows,"master_family_batches":stats.master_family_batches,"master_rows":stats.master_rows,"reduction_rows":stats.reduction_rows,"fallback_rows":stats.fallback_rows,"analytic_rows":stats.analytic_rows},
  "scope":"Untimed diagnostic capture; no benchmark latency or throughput recorded"}))
}
fn main(){let stdin=io::stdin();let mut out=io::stdout().lock();let mut prepared=None;
 for line in stdin.lock().lines(){let line=line.unwrap();if line.trim()=="QUIT"{break;}if line.trim().is_empty(){continue;}
  let result=match serde_json::from_str::<Request>(&line){Ok(request)=>run(&request,&mut prepared).unwrap_or_else(|e|json!({"id":request.id,"status":"error","error":e})),Err(e)=>json!({"status":"invalid_request","error":e.to_string()})};
  writeln!(out,"RESULT {result}").unwrap();out.flush().unwrap();
 }
}
