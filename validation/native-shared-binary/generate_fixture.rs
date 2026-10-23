#![allow(dead_code,unused_imports)]
use std::{fs,path::PathBuf};
use symbolica::{atom::{Atom,AtomCore,Symbol},evaluate::Instruction};
#[path="baseline/rust_codegen.rs"] mod baseline_codegen;
#[path="candidate/rust_codegen.rs"] mod candidate_codegen;
fn run()->Result<(),String>{
 let context=oneloop::OneLoopExpressions::new();
 let p:Vec<_>=(0..3).map(|i|symbolica::symbol!(format!("iregi_dense_fixture::p{i}")).to_atom()).collect();
 // Test expression preparation uses only existing Symbolica Atom operations.
 // Inactive rows have p1=-1; evaluating their first reciprocal would be invalid.
 let mut expression=Atom::num(0);
 for k in 1..=140{expression=expression+&p[2]/(&p[1]+Atom::num(k));}
 let guarded=Symbol::IF.call((&p[0],&expression,Atom::num(0)));
 let outputs=vec![guarded.clone(),&guarded+&p[2],&guarded*&p[1],p[0].clone(),p[1].clone(),p[2].clone()];
 let exact=context.evaluator_with_stack_reuse(&outputs,&p).map_err(|e|e.to_string())?;
 let graph=exact.export_instructions();
 let aliases=graph.instructions.iter().filter(|i|match i{Instruction::Add(dst,args,_)|Instruction::Mul(dst,args,_)=>args.contains(dst),_=>false}).count();
 assert!(aliases>0,"fixture must exercise an arithmetic source/destination alias");
 assert!(graph.instructions.iter().enumerate().any(|(pc,i)|pc>128&&matches!(i,Instruction::Label(_))),"fixture must reactivate beyond an outline boundary");
 let mut baseline=baseline_codegen::RustEmitter::default();let old=baseline.emit_batch(exact.clone(),baseline_codegen::EmitOptions{inline_arithmetic:true})?;
 let mut candidate=candidate_codegen::RustEmitter::default();let new=candidate.emit_batch(exact,candidate_codegen::EmitOptions{inline_arithmetic:true})?;
 assert_eq!(baseline.constants_source(),candidate.constants_source());
 let directory=PathBuf::from("target/native-shared-binary/fixture");fs::create_dir_all(&directory).map_err(|e|e.to_string())?;
 for(name,source)in[("fixture_baseline.rs",old.source),("fixture_candidate.rs",new.source),("constants.rs",candidate.constants_source())]{fs::write(directory.join(name),source).map_err(|e|e.to_string())?;}
 fs::write(directory.join("instruction-provenance.txt"),format!("{:?}\n{:?}\n{:?}",graph.instructions,graph.constants,graph.constant_functions)).map_err(|e|e.to_string())?;
 println!("instructions,temporary_slots,source_destination_aliases,outputs");println!("{},{},{},{}",graph.instructions.len(),graph.temporary_count,aliases,graph.output_count);Ok(())
}
fn main(){std::thread::Builder::new().stack_size(128*1024*1024).spawn(run).unwrap().join().unwrap().unwrap();}
