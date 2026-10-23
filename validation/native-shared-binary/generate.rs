#![allow(dead_code,unused_imports)]
use oneloop::ScalarIntegral;
use std::{collections::BTreeMap,fmt::Write as _,path::PathBuf,fs};
use symbolica::{atom::{Atom,AtomCore,Symbol},domains::{float::Complex,rational::Rational},evaluate::{ExportedInstructions,Instruction,Slot}};
#[path="baseline/rust_codegen.rs"] mod baseline_codegen;
#[path="candidate/rust_codegen.rs"] mod candidate_codegen;
type Graph=ExportedInstructions<Complex<Rational>>;
fn expressions(
    family: ScalarIntegral,
    _with_boundary: bool,
) -> (oneloop::OneLoopExpressions, Vec<Atom>, Vec<Atom>) {
    let context = oneloop::OneLoopExpressions::new();
    let p: Vec<_> = (0..family.arity())
        .map(|i| {
            symbolica::symbol!(format!("iregi_masters::{}_argument_{i}", family.name())).to_atom()
        })
        .collect();
    let series = match family {
        ScalarIntegral::A0 => oneloop::a0(&p[0], &p[1]),
        ScalarIntegral::B0 => oneloop::b0(&p[0], &p[1], &p[2], &p[3]),
        ScalarIntegral::DB0 => oneloop::db0(&p[0], &p[1], &p[2], &p[3]),
        ScalarIntegral::C0 => context.c0([&p[0], &p[1], &p[2]], [&p[3], &p[4], &p[5]], &p[6]),
        ScalarIntegral::D0 => context.d0(
            [&p[0], &p[1], &p[2], &p[3], &p[4], &p[5]],
            [&p[6], &p[7], &p[8], &p[9]],
            &p[10],
        ),
    };
    let mut coefficients = series.into_coefficients();
    if matches!(family, ScalarIntegral::C0 | ScalarIntegral::D0) {
        // The integral of a scaleless scalar integrand vanishes in dimensional
        // regularization. This branch also prevents evaluating singular formulas
        // in inactive lanes. The scaleless derivative dB0 is handled separately.
        let any_nonzero = p[..p.len() - 1]
            .iter()
            .fold(Atom::num(0), |previous, value| {
                Symbol::IF.call((value, Atom::num(1), previous))
            });
        coefficients =
            coefficients.map(|coefficient| Symbol::IF.call((&any_nonzero, coefficient, 0)));
    }
    let uv = match family {
        ScalarIntegral::A0 => p[0].clone(),
        ScalarIntegral::B0 => Atom::num(1),
        _ => Atom::num(0),
    };
    let ir = &coefficients[1] - &uv;
    let mut outputs = Vec::from(coefficients);
    outputs.push(uv);
    outputs.push(ir);
    outputs.push(Atom::num(0));
    (context, p, outputs)
}
fn provenance(graph: &Graph) -> Result<String, String> {
    let mut bindings: BTreeMap<Slot, String> = (0..graph.input_count)
        .map(|i| (Slot::Param(i), format!("p{i}")))
        .chain((0..graph.constants.len()).map(|i| (Slot::Const(i), format!("c{i}"))))
        .collect();
    let mut output = format!(
        "inputs={} outputs={}\nconstants={:?}\nregistered={:?}\n",
        graph.input_count, graph.output_count, graph.constants, graph.constant_functions,
    );
    for (pc, instruction) in graph.instructions.iter().enumerate() {
        let source = |slot: &Slot| {
            bindings
                .get(slot)
                .cloned()
                .ok_or_else(|| format!("undefined source {slot} at instruction {pc}"))
        };
        let sources = |slots: &[Slot]| slots.iter().map(source).collect::<Result<Vec<_>, _>>();
        let (destination, description) = match instruction {
            Instruction::Add(dst, args, real) => {
                (Some(*dst), format!("add {:?} real={real}", sources(args)?))
            }
            Instruction::Mul(dst, args, real) => {
                (Some(*dst), format!("mul {:?} real={real}", sources(args)?))
            }
            Instruction::Pow(dst, base, power, real) => (
                Some(*dst),
                format!("pow {} {power} real={real}", source(base)?),
            ),
            Instruction::Powf(dst, base, power, real) => (
                Some(*dst),
                format!("powf {} {} real={real}", source(base)?, source(power)?),
            ),
            Instruction::Fun(dst, call, real) => (
                Some(*dst),
                format!(
                    "call {} {:?} {:?} real={real}",
                    call.0.get_name(),
                    call.1,
                    sources(&call.2)?,
                ),
            ),
            Instruction::Assign(dst, src) => (Some(*dst), format!("assign {}", source(src)?)),
            Instruction::Join(dst, condition, yes, no) => (
                Some(*dst),
                format!(
                    "join {} {} {}",
                    source(condition)?,
                    source(yes)?,
                    source(no)?
                ),
            ),
            Instruction::IfElse(condition, label) => {
                (None, format!("if {} goto {label}", source(condition)?))
            }
            Instruction::Goto(label) => (None, format!("goto {label}")),
            Instruction::Label(label) => (None, format!("label {label}")),
        };
        writeln!(output, "v{pc}: {description}").unwrap();
        if let Some(destination) = destination {
            bindings.insert(destination, format!("v{pc}"));
        }
    }
    for i in 0..graph.output_count {
        writeln!(output, "output {i} = {:?}", bindings.get(&Slot::Out(i))).unwrap();
    }
    Ok(output)
}

fn helpers(
    graph: &Graph,
    found: &mut BTreeMap<String, (usize, usize, String)>,
) -> Result<(), String> {
    for helper in &graph.sub_evaluators {
        let name = format!("{} {:?}", helper.symbol.get_name(), helper.tags);
        if found.contains_key(&name) {
            continue;
        }
        found.insert(
            name,
            (
                helper.instructions.temporary_count,
                helper.instructions.instructions.len(),
                provenance(&helper.instructions)?,
            ),
        );
        helpers(&helper.instructions, found)?;
    }
    Ok(())
}

fn run()->Result<(),String>{
 let family=match std::env::args().nth(1).as_deref(){Some("b0")=>ScalarIntegral::B0,Some("c0")=>ScalarIntegral::C0,_=>return Err("expected b0 or c0".into())};
 let directory=PathBuf::from("target/native-shared-binary").join(family.name().to_ascii_lowercase());fs::create_dir_all(&directory).map_err(|e|e.to_string())?;
 let(context,parameters,outputs)=expressions(family,false);
 // Reuse the original unallocated scalar constructor, separately from allocator candidate.
 let evaluator=context.evaluator(&outputs,&parameters).map_err(|e|e.to_string())?;
 let graph=evaluator.export_instructions();let signature=provenance(&graph)?;let mut helper_signatures=BTreeMap::new();helpers(&graph,&mut helper_signatures)?;
 let inline_arithmetic=family==ScalarIntegral::B0;
 let mut public=oneloop::rust_codegen::RustEmitter::default();
 let original=public.emit_batch(evaluator.clone(),oneloop::rust_codegen::EmitOptions{inline_arithmetic})?;
 let mut baseline=baseline_codegen::RustEmitter::default();
 let old=baseline.emit_batch(evaluator.clone(),baseline_codegen::EmitOptions{inline_arithmetic})?;
 assert_eq!(original.source,old.source,"private baseline emitter differs from frozen public emitter");
 assert_eq!(public.constants_source(),baseline.constants_source());
 let mut candidate=candidate_codegen::RustEmitter::default();
 let new=candidate.emit_batch(evaluator.clone(),candidate_codegen::EmitOptions{inline_arithmetic})?;
 assert_eq!(baseline.constants_source(),candidate.constants_source(),"dense candidate changed exact constants");
 assert_eq!(old.source.split("\nuse super::BatchWorkspace;").next(),new.source.split("\nuse super::BatchWorkspace;").next(),"dense candidate changed scalar source");
 assert_eq!(signature,provenance(&evaluator.export_instructions())?);
 let mut after_helpers=BTreeMap::new();helpers(&evaluator.export_instructions(),&mut after_helpers)?;assert_eq!(helper_signatures,after_helpers);
 let name=family.name().to_ascii_lowercase();
 for(label,source)in[("baseline",old.source),("candidate",new.source)]{fs::write(directory.join(format!("{name}_{label}.rs")),source).map_err(|e|e.to_string())?;}
 fs::write(directory.join("constants.rs"),candidate.constants_source()).map_err(|e|e.to_string())?;
 fs::write(directory.join("root-provenance.txt"),signature).map_err(|e|e.to_string())?;
 fs::write(directory.join("helper-provenance.txt"),format!("{helper_signatures:#?}")).map_err(|e|e.to_string())?;
 println!("family,root_instructions,root_temporary_slots,unique_helpers,outputs");println!("{},{},{},{},{}",family.name(),graph.instructions.len(),graph.temporary_count,helper_signatures.len(),graph.output_count);
 Ok(())
}
fn main(){std::thread::Builder::new().stack_size(128*1024*1024).spawn(run).unwrap().join().unwrap().unwrap();}
