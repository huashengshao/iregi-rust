//! One paired process; qualification and fixed-count timing are distinct request modes.
use serde::Deserialize;
use serde_json::json;
use std::io::{self, BufRead, Write};

#[derive(Deserialize)]
pub struct Sample { shifts:Vec<[f64;4]>, masses:Vec<[f64;2]>, mu:f64 }
#[derive(Deserialize)]
pub struct Request {
    id:String, n:usize, rank:u16, algorithm:String, samples:Vec<Sample>,
    #[serde(default)] engine:Option<String>,
    #[serde(default)] warmup:usize,
    #[serde(default)] repeats:usize,
    #[serde(default)] iterations:usize,
}

mod baseline { use selected_baseline as core_impl; include!("core_probe.rs"); }
mod candidate { use selected_candidate as core_impl; include!("core_probe.rs"); }
mod master_controls;

fn main() {
    assert!(!selected_baseline::PRIVATE_SELECTED_NATIVE && selected_candidate::PRIVATE_SELECTED_NATIVE);
    let mut base=None;
    let mut selected=None;
    let stdin=io::stdin();
    let mut out=io::stdout().lock();
    for line in stdin.lock().lines() {
        let line=line.unwrap();
        if line.trim()=="QUIT" {break;}
        if line.trim().is_empty() {continue;}
        let result=if line.trim()=="CONTROLS" {
            let controls=std::panic::catch_unwind(||json!({"baseline":baseline::unchanged_controls(),"candidate":candidate::unchanged_controls(),"masters":master_controls::run()}));
            match controls {Ok(v)=>json!({"id":"controls","status":"passed","controls":v}),Err(_)=>{
                selected_baseline::set_master_capture(false);selected_candidate::set_master_capture(false);
                let _=selected_baseline::take_master_captures();let _=selected_candidate::take_master_captures();
                json!({"id":"controls","status":"failed","error":"control assertion failed; see stderr"})
            }}
        } else {
            match serde_json::from_str::<Request>(&line) {
                Ok(request)=>match request.engine.as_deref() {
                    None=>json!({"id":request.id,"baseline":baseline::run(&request,&mut base).unwrap_or_else(|e|json!({"error":e})),"candidate":candidate::run(&request,&mut selected).unwrap_or_else(|e|json!({"error":e}))}),
                    Some("baseline")=>baseline::run(&request,&mut base).unwrap_or_else(|e|json!({"error":e})),
                    Some("candidate")=>candidate::run(&request,&mut selected).unwrap_or_else(|e|json!({"error":e})),
                    _=>json!({"status":"invalid_request","error":"unknown engine"}),
                },
                Err(error)=>json!({"status":"invalid_request","error":error.to_string()}),
            }
        };
        writeln!(out,"RESULT {result}").unwrap();
        out.flush().unwrap();
    }
}
