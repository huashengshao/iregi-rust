//! Exact-only census. Every algebra operation is delegated to Symbolica Atom.
//! Exported helper calls are opaque exact functions; no floating evaluation occurs.
use std::{collections::BTreeMap, fs, path::Path, time::Instant};
use iregi_masters::{ScalarIntegral, exact_scalar_master_evaluator};
use serde_json::{json, Value};
use symbolica::{
    atom::{Atom, AtomCore, Symbol},
    domains::{float::Complex, rational::Rational},
    evaluate::{ExportedInstructions, Instruction, Slot},
};
type Graph = ExportedInstructions<Complex<Rational>>;

fn helper_descriptions(graph: &Graph, found: &mut BTreeMap<String, String>, pointers: &mut BTreeMap<String, usize>) -> Result<(), String> {
    for helper in &graph.sub_evaluators {
        let name = format!("{} {:?}", helper.symbol.get_name(), helper.tags);
        let body = &helper.instructions;
        let callees: Vec<_> = body.sub_evaluators.iter().map(|h| (h.symbol.get_name(), &h.tags, h.input_count, h.output_count)).collect();
        let description = format!("signature={:?}\ninputs={} outputs={} temporary={}\nconstants={:?}\nregistered={:?}\ninstructions={:?}\ncallees={callees:?}",
            (helper.input_count, helper.output_count), body.input_count, body.output_count, body.temporary_count, body.constants, body.constant_functions, body.instructions);
        if let Some(previous) = found.get(&name) {
            if previous != &description || pointers.get(&name) != Some(&(std::sync::Arc::as_ptr(body) as usize)) { return Err(format!("conflicting shared helper or nonshared descendant occurrence {name}")); }
            continue;
        }
        pointers.insert(name.clone(),std::sync::Arc::as_ptr(body) as usize);
        found.insert(name, description);
        helper_descriptions(body, found, pointers)?;
    }
    Ok(())
}

#[derive(Default)]
struct Signatures(BTreeMap<String, Symbol>);
impl Signatures {
    fn function(&mut self, signature: String) -> Symbol {
        let index = self.0.len();
        *self.0.entry(signature).or_insert_with(|| symbolica::symbol!(format!("master_cse_proof::opaque_{index}")))
    }
}
type Control = (String, Option<Atom>, Option<usize>);
fn symbolic_roots(graph: &Graph, parameters: &[Atom], signatures: &mut Signatures) -> Result<(Vec<Atom>, Vec<Control>), String> {
    if graph.input_count != parameters.len() { return Err("parameter shape changed".into()); }
    let mut bindings: BTreeMap<Slot, Atom> = parameters.iter().cloned().enumerate().map(|(i,p)| (Slot::Param(i),p)).collect();
    if graph.constant_functions.iter().any(|f| f.index>=graph.constants.len()) {return Err("registered constant index out of range".into());}
    for (index, constant) in graph.constants.iter().enumerate() {
        let registered: Vec<_> = graph.constant_functions.iter().filter(|f| f.index == index).collect();
        if registered.len() > 1 { return Err("duplicate registered constant descriptor".into()); }
        let value = if let Some(function) = registered.first() {
            signatures.function(format!("constant {} {:?} {:?}", function.symbol.get_name(), function.tags, function.fixed_args)).to_atom()
        } else { Atom::num(constant.clone()) };
        bindings.insert(Slot::Const(index), value);
    }
    let labels: BTreeMap<_,_> = graph.instructions.iter().filter_map(|instruction| if let Instruction::Label(label)=instruction {Some(*label)} else {None}).enumerate().map(|(ordinal,label)|(label,ordinal)).collect();
    if labels.len()!=graph.instructions.iter().filter(|i|matches!(i,Instruction::Label(_))).count(){return Err("duplicate label identity".into());}
    let label = |value: &usize| labels.get(value).copied().ok_or_else(|| format!("missing label {value}"));
    let mut controls = Vec::new();
    // Symbolica's own undo_stack_optimization uses this same linear RHS-before-write
    // restoration for its structured allocated IR. This is a validation reconstruction,
    // not a rewrite or a runtime interpreter. Join operands remain live through the Join.
    for (pc, instruction) in graph.instructions.iter().enumerate() {
        let read = |slot: &Slot| bindings.get(slot).cloned().ok_or_else(|| format!("unbound {slot} at {pc}"));
        let terms = |args: &[Slot]| args.iter().map(read).collect::<Result<Vec<_>,_>>();
        let result = match instruction {
            Instruction::Add(dst,args,_) => Some((*dst,terms(args)?.into_iter().reduce(|a,b|a+b).ok_or("empty addition")?)),
            Instruction::Mul(dst,args,_) => Some((*dst,terms(args)?.into_iter().reduce(|a,b|a*b).ok_or("empty product")?)),
            Instruction::Pow(dst,base,power,_) => Some((*dst,read(base)?.pow(*power))),
            Instruction::Powf(dst,base,power,_) => Some((*dst,read(base)?.pow(read(power)?))),
            Instruction::Fun(dst,call,_) => {
                let arguments = terms(&call.2)?;
                let function = signatures.function(format!("function {} {:?}", call.0.get_name(), call.1));
                Some((*dst,function.call_args(arguments)))
            }
            Instruction::Assign(dst,src) => Some((*dst,read(src)?)),
            Instruction::Join(dst,condition,yes,no) => {
                let condition = read(condition)?;
                controls.push(("join".into(),Some(condition.clone()),None));
                Some((*dst,Symbol::IF.call((condition,read(yes)?,read(no)?))))
            }
            Instruction::IfElse(condition,target) => { controls.push(("if".into(),Some(read(condition)?),Some(label(target)?))); None }
            Instruction::Goto(target) => { controls.push(("goto".into(),None,Some(label(target)?))); None }
            Instruction::Label(target) => { controls.push(("label".into(),None,Some(label(target)?))); None }
        };
        if let Some((destination, value)) = result { bindings.insert(destination,value); }
    }
    let outputs = (0..graph.output_count).map(|i| bindings.get(&Slot::Out(i)).cloned().ok_or_else(||format!("missing output {i}"))).collect::<Result<Vec<_>,_>>()?;
    Ok((outputs,controls))
}

fn census(graph:&Graph)->Value {
    let mut counts=BTreeMap::<&str,usize>::new();
    for instruction in &graph.instructions {
        let name=match instruction {Instruction::Add(..)=>"add",Instruction::Mul(..)=>"multiply",Instruction::Pow(..)=>"integer_power",Instruction::Powf(..)=>"power",Instruction::Fun(..)=>"function",Instruction::Assign(..)=>"assign",Instruction::IfElse(..)=>"if",Instruction::Goto(..)=>"goto",Instruction::Label(..)=>"label",Instruction::Join(..)=>"join"};
        *counts.entry(name).or_default()+=1;
    }
    json!({"inputs":graph.input_count,"outputs":graph.output_count,"instructions":graph.instructions.len(),"temporary_slots":graph.temporary_count,"constants":graph.constants.len(),"registered_constants":graph.constant_functions.len(),"instruction_kinds":counts})
}

fn one(family:ScalarIntegral,directory:&Path)->Result<Value,String>{
    let parameters:Vec<Atom>=(0..family.arity()).map(|i|symbolica::symbol!(format!("iregi_masters::{}_argument_{i}",family.name())).to_atom()).collect();
    let start=Instant::now();
    let baseline=exact_scalar_master_evaluator(family).map_err(|e|e.to_string())?;
    let construction_ns=start.elapsed().as_nanos();
    let before=baseline.export_instructions();
    if before.output_count!=6||before.input_count!=parameters.len(){return Err("master shape differs".into());}
    let empty_expressions:Vec<Atom>=vec![];
    let empty=Atom::evaluator_multiple(&empty_expressions,&parameters).direct_translation(true).horner_iterations(0).build().map_err(|e|e.to_string())?;
    let e=empty.export_instructions();
    if e.input_count!=parameters.len()||e.output_count!=0||!e.instructions.is_empty()||!e.constants.is_empty()||!e.constant_functions.is_empty()||!e.sub_evaluators.is_empty(){return Err("incoming evaluator is not empty with identical input count".into());}
    let mut candidate=baseline.clone();let start=Instant::now();candidate.merge(empty,Some(0)).map_err(|e|e.to_string())?;let merge_ns=start.elapsed().as_nanos();
    let after=candidate.export_instructions();
    if before.input_count!=after.input_count||before.output_count!=after.output_count||before.constants!=after.constants||format!("{:?}",before.constant_functions)!=format!("{:?}",after.constant_functions){return Err("root metadata changed".into());}
    let mut old_helpers=BTreeMap::new();let mut new_helpers=BTreeMap::new();helper_descriptions(&before,&mut old_helpers,&mut BTreeMap::new())?;helper_descriptions(&after,&mut new_helpers,&mut BTreeMap::new())?;
    if old_helpers!=new_helpers{return Err("shared helper body/signature changed".into());}
    let mut signatures=Signatures::default();
    let (old_roots,old_controls)=symbolic_roots(&before,&parameters,&mut signatures)?;
    let (new_roots,new_controls)=symbolic_roots(&after,&parameters,&mut signatures)?;
    if old_controls.len()!=new_controls.len(){return Err("control count changed".into());}
    for (old,new) in old_controls.iter().zip(&new_controls) {
        if old.0!=new.0||old.2!=new.2{return Err("control structure changed".into());}
        match (&old.1,&new.1) {(Some(a),Some(b)) if !(a-b).expand().is_zero()=>return Err("branch condition exact expression changed".into()),(None,None)|(Some(_),Some(_))=>{},_=>return Err("control predicate shape changed".into())}
    }
    for (i,(old,new)) in old_roots.iter().zip(&new_roots).enumerate(){if !(old-new).expand().is_zero(){return Err(format!("exact output identity failed at {i}"));}}
    fs::write(directory.join(format!("{}-root-before.txt",family.name())),format!("{:?}",before.instructions)).map_err(|e|e.to_string())?;
    fs::write(directory.join(format!("{}-root-after.txt",family.name())),format!("{:?}",after.instructions)).map_err(|e|e.to_string())?;
    fs::write(directory.join(format!("{}-exact-roots.txt",family.name())),old_roots.iter().enumerate().map(|(i,a)|format!("output{i}: {a}\n")).collect::<String>()).map_err(|e|e.to_string())?;
    fs::write(directory.join(format!("{}-helpers.json",family.name())),serde_json::to_vec_pretty(&old_helpers).unwrap()).map_err(|e|e.to_string())?;
    let operations=|v:&symbolica::evaluate::OperationCount|json!({"additions":v.additions,"multiplications":v.multiplications,"inversions":v.inversions,"function_calls":v.function_calls});
    Ok(json!({"family":family.name(),"status":"passed","parameters":parameters.iter().map(ToString::to_string).collect::<Vec<_>>(),"before":census(&before),"after":census(&after),"operations_before":operations(&baseline.count_operations()),"operations_after":operations(&candidate.count_operations()),"exact_outputs_proved":old_roots.len(),"control_records_proved":old_controls.len(),"helpers_unchanged":old_helpers.len(),"registered_descriptors_unchanged":true,"constructor_ns":construction_ns,"merge_ns":merge_ns,"scope":"Exact symbolic root/control identities conditional on trusted Symbolica structured SSA, liveness and CSE dominance; all algebra delegated to Symbolica; helpers opaque and unchanged. No independent branch-definedness, floating, mixed-precision, Dual or performance qualification"}))
}
fn run()->Result<(),String>{
    let directory=Path::new("target/master-cse-census/results");fs::create_dir_all(directory).map_err(|e|e.to_string())?;
    let mut failed=0;
    for family in [ScalarIntegral::A0,ScalarIntegral::B0,ScalarIntegral::C0] {
        match one(family,directory){Ok(row)=>println!("{row}"),Err(error)=>{failed+=1;println!("{}",json!({"family":family.name(),"status":"failed","error":error}));}}
    }
    if failed==0{Ok(())}else{Err(format!("{failed} failed census families"))}
}
fn main(){std::thread::Builder::new().stack_size(128*1024*1024).spawn(run).unwrap().join().unwrap().unwrap();}
