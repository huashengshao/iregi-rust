//! Validation interpreter: all expression arithmetic/normalization is Symbolica's.
//! The checked subset is straight-line physical coefficient programs, not a new algebra engine.
use std::collections::BTreeMap;
use symbolica::{atom::{Atom,AtomCore},domains::{float::Complex,rational::Rational},evaluate::{ExpressionEvaluator,Instruction,Slot}};
use serde_json::{json,Value};
pub fn prove(exact:&ExpressionEvaluator<Complex<Rational>>,parameters:&[Atom],expected:&[Atom])->Result<Value,String>{
 let graph=exact.export_instructions();
 if !graph.constant_functions.is_empty()||!graph.sub_evaluators.is_empty(){return Err("proof does not admit registered constants/helpers".into())}
 if graph.input_count!=parameters.len()||graph.output_count!=expected.len(){return Err("proof layout mismatch".into())}
 let mut values:BTreeMap<Slot,Atom>=parameters.iter().cloned().enumerate().map(|(i,a)|(Slot::Param(i),a)).chain(graph.constants.iter().cloned().enumerate().map(|(i,c)|(Slot::Const(i),Atom::num(c)))).collect();
 for (pc,instruction) in graph.instructions.iter().enumerate(){
  let read=|slot:&Slot|values.get(slot).cloned().ok_or_else(||format!("unbound {slot} at {pc}"));
  let (destination,value)=match instruction{
   Instruction::Add(dst,args,_)=>{let terms=args.iter().map(read).collect::<Result<Vec<_>,_>>()?;(*dst,terms.into_iter().reduce(|a,b|a+b).ok_or("empty add")?)},
   Instruction::Mul(dst,args,_)=>{let terms=args.iter().map(read).collect::<Result<Vec<_>,_>>()?;(*dst,terms.into_iter().reduce(|a,b|a*b).ok_or("empty product")?)},
   Instruction::Pow(dst,base,power,_)=> (*dst,read(base)?.pow(*power)),
   Instruction::Powf(dst,base,power,_)=> (*dst,read(base)?.pow(read(power)?)),
   Instruction::Fun(dst,call,_)=>{
    if !call.1.is_empty()||call.0.get_name()!="symbolica::sqrt"||call.2.len()!=1{return Err(format!("unsupported proof function at {pc}: {}",call.0.get_name()))}
    (*dst,call.0.call_args(call.2.iter().map(read).collect::<Result<Vec<_>,_>>()?))
   },
   Instruction::Assign(dst,src)=>(*dst,read(src)?),
   _=>return Err(format!("proof rejects control flow at {pc}")),
  };
  // Read the complete RHS first; allocated destinations can alias an operand.
  values.insert(destination,value);
 }
 for (i,expected) in expected.iter().enumerate(){
  let result=values.get(&Slot::Out(i)).ok_or_else(||format!("missing output {i}"))?;
  if !(result.clone()-expected.clone()).expand().is_zero(){return Err(format!("Symbolica polynomial identity failed at output {i}"))}
 }
 let ops=exact.count_operations();
 Ok(json!({"outputs_proved":expected.len(),"proof":"Symbolica exact expanded differences are literal zero; no statistical zero test","input_count":graph.input_count,"constants":graph.constants.len(),"instructions":graph.instructions.len(),"temporary_count":graph.temporary_count,"arithmetic":{"additions":ops.additions,"multiplications":ops.multiplications,"inversions":ops.inversions,"function_calls":ops.function_calls},"helpers":0,"registered_constants":0}))
}
