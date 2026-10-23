//! Isolated allocation proof: no production source is replaced.
use std::{collections::BTreeMap,fmt::Write as _,io::Write as _,sync::atomic::{AtomicUsize,Ordering}};
use symbolica::{domains::{rational::Rational,float::Complex},evaluate::{ExpressionEvaluator,ExportedInstructions,Instruction,Slot}};
type Graph = ExportedInstructions<Complex<Rational>>;
static COUNTER: AtomicUsize = AtomicUsize::new(0);
// This is instruction provenance accounting, not a graph transformation. Read
// every source before recording a destination: allocated slots can be reused
// by the same instruction, including slots named Out by the exporter.
pub fn provenance(graph: &Graph) -> Result<String, String> {
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

pub fn helpers(
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

pub(crate) fn allocate(exact: &mut ExpressionEvaluator<Complex<Rational>>, factory: &str, enabled: bool) {
    let before = exact.export_instructions();
    let proof = provenance(&before).expect("baseline instruction provenance");
    let mut helpers_before = BTreeMap::new();
    helpers(&before,&mut helpers_before).expect("baseline helper provenance");
    if enabled { exact.optimize_stack(); }
    let after = exact.export_instructions();
    assert_eq!(proof,provenance(&after).expect("allocated instruction provenance"),"allocation changed instruction data flow");
    let mut helpers_after = BTreeMap::new();
    helpers(&after,&mut helpers_after).expect("allocated helper provenance");
    assert_eq!(helpers_before,helpers_after,"allocation changed shared helpers");
    if let Ok(folder) = std::env::var("IREGI_CORE_STACK_PROOF_DIR") {
        let folder = std::path::Path::new(&folder);
        std::fs::create_dir_all(folder).unwrap();
        let index = COUNTER.fetch_add(1,Ordering::Relaxed);
        let record = serde_json::json!({"index":index,"factory":factory,"allocated":enabled,
            "inputs":before.input_count,"outputs":before.output_count,
            "instructions":before.instructions.len(),"before_temporaries":before.temporary_count,
            "after_temporaries":after.temporary_count,"unchanged_provenance":true,
            "unchanged_helpers":true,"helper_count":helpers_before.len()});
        let mut log=std::fs::OpenOptions::new().append(true).create(true).open(folder.join("graphs.jsonl")).unwrap();
        writeln!(log,"{}",record).unwrap();
        std::fs::write(folder.join(format!("{index:05}-{factory}.semantics")),proof).unwrap();
    }
}
