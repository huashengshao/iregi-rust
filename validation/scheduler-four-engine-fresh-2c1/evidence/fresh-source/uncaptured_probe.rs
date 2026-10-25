//! One generic-only TIRust instance; scheduler variants run in separate processes.
#[cfg(iregi_qualification_capture)]
compile_error!("timing product must not compile capture hooks");
use serde::Deserialize;
use serde_json::json;
use std::{collections::HashMap, io::{self, BufRead, Write}};
#[derive(Deserialize)]
pub struct Sample { shifts: Vec<[f64;4]>, masses: Vec<[f64;2]>, mu: f64 }
#[derive(Deserialize)]
pub struct Request {
    id:String,n:usize,rank:u16,algorithm:String,samples:Vec<Sample>,
    #[serde(default)]engine:Option<String>,#[serde(default)]warmup:usize,
    #[serde(default)]repeats:usize,#[serde(default)]iterations:usize,
}
type PlanCache=HashMap<(usize,u16,String),iregi_rust::ReductionPlan>;
mod core {use iregi_rust as core_impl;include!("uncaptured_core_probe.rs");}
mod master_controls;
fn main() {
    assert_eq!(iregi_masters::default_master_backend(),iregi_masters::MasterBackend::SymbolicaBatch);
    let mut prepared=None;let mut plans=PlanCache::new();
    let stdin=io::stdin();let mut out=io::stdout().lock();
    for line in stdin.lock().lines() {
        let line=line.unwrap();if line.trim()=="QUIT"{break;}if line.trim().is_empty(){continue;}
        let result=std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            if line.trim()=="CONTROLS" {
                json!({"id":"controls","status":"passed","core":core::unchanged_controls(),
                    "extended_core":core::extended_unchanged_controls(),"masters":master_controls::run(),
                    "cache_interleaving":core::cache_interleaving(),"backend":"SymbolicaBatch"})
            } else {
                match serde_json::from_str::<Request>(&line) {
                    Ok(r) if r.engine.is_some() || (r.warmup==0&&r.repeats==0&&r.iterations==0) =>
                        json!({"id":r.id,"result":core::run(&r,&mut prepared,&mut plans).unwrap_or_else(|e|json!({"error":e}))}),
                    Ok(_)=>json!({"status":"invalid_request","error":"untimed request must not carry timing counts"}),
                    Err(e)=>json!({"status":"invalid_request","error":e.to_string()}),
                }
            }
        }));
        let result=result.unwrap_or_else(|_| {json!({"status":"failed","error":"qualification assertion failed; see stderr"})});
        writeln!(out,"RESULT {result}").unwrap();out.flush().unwrap();
    }
}
