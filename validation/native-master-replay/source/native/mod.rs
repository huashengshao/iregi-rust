use oneloop::rust_codegen::runtime::{BatchWorkspace,C,ConstantSpec,Context,NativeFloat,batch,primitives};
#[allow(clippy::all,unused_assignments,dead_code)]mod a0;
#[allow(clippy::all,unused_assignments,dead_code)]mod b0;
#[allow(clippy::all,unused_assignments,dead_code)]mod c0;
mod constants;
pub fn context()->Context<f64>{Context::new(constants::CONSTANTS,53).unwrap()}
pub fn evaluate(family:oneloop::ScalarIntegral,input:&[C<f64>],output:&mut[C<f64>],rows:usize,context:&Context<f64>,work:&mut BatchWorkspace<f64>)->Result<(),String>{
 match family{
  oneloop::ScalarIntegral::A0=>a0::evaluate_batch(input,output,rows,context,work),
  oneloop::ScalarIntegral::B0=>b0::evaluate_batch(input,output,rows,context,work),
  oneloop::ScalarIntegral::C0=>c0::evaluate_batch(input,output,rows,context,work),
  _=>Err("replay only admits A0/B0/C0; no D0 module compiled".into()),
 }
}
