from pathlib import Path
import hashlib,json,shutil,subprocess
root=Path.cwd();base=root/'target/native-shared-binary';old=root/'target/native-dense-span'
assert not (base/'source-inputs.json').exists(), 'do not overwrite frozen sources'
p=base/'candidate/rust_codegen.rs';s=p.read_text()
assert s.count('batch::emit(graph, &mut staged.constants)?')==1
s=s.replace('batch::emit(graph, &mut staged.constants)?','batch::emit(graph, &mut staged.constants, options.inline_arithmetic)?')
p.write_text(s)
p=base/'candidate/rust_codegen/batch.rs';s=p.read_text()
s=s.replace('    controlled: bool,\n    outlines: Outlines,','    controlled: bool,\n    inline_arithmetic: bool,\n    outlines: Outlines,')
s=s.replace('pub(super) fn emit(graph: &Graph, constants: &mut Constants)', 'pub(super) fn emit(graph: &Graph, constants: &mut Constants, inline_arithmetic: bool)')
s=s.replace('        controlled: has_control_flow(graph),','        controlled: has_control_flow(graph),\n        inline_arithmetic,')
s=s.replace('    if generator.controlled {\n        // Metadata only:', '    source.push_str("use super::shared_binary_kernel::{BinaryOperand, shared_binary};\\n");\n    if generator.controlled {\n        // Metadata only:')
needle='''                    } else {
                        // Preserve exported operand order. Finish all reads before'''
replacement='''                    } else if args.len() == 2 {
                        let operand = |slot: Slot| -> Result<String, String> {
                            match slot {
                                Slot::Const(i) => constants.get(i)
                                    .map(|i| format!("BinaryOperand::Constant({i})"))
                                    .ok_or_else(|| format!("invalid batch constant slot {i}")),
                                _ => Ok(format!("BinaryOperand::Column(base + {})", index(slot)?)),
                            }
                        };
                        let multiply = matches!(instruction, Instruction::Mul(..));
                        let inline = self.inline_arithmetic;
                        let left = operand(args[0])?;
                        let right = operand(args[1])?;
                        let (lanes, span) = if self.controlled {
                            ("&active[..active_len]", "dense_span")
                        } else { ("&[]", "Some((0, rows))") };
                        writeln!(body, "    shared_binary::<T, {multiply}, {inline}>(v, stride, {lanes}, {span}, base + {destination}, {left}, {right}, ctx);").unwrap();
                        None
                    } else {
                        // Preserve exported operand order. Finish all reads before'''
assert s.count(needle)==1;s=s.replace(needle,replacement)
start=s.index('                if self.controlled && matches!(instruction, Instruction::Add(..) | Instruction::Mul(..)) {')
end=s.index('\n            }',start)
s=s[:start]+'''                writeln!(body, "    {loop_header} {{ v[(base + {destination}) * stride + lane] = {expression}; }}").unwrap();'''+s[end:]
p.write_text(s)
for name in ['generate.rs','generate_fixture.rs','build_generator.py','build_fixture_generator.py','run_generator.py','run_fixture_generator.py']:
 s=(old/name).read_text().replace('native-dense-span','native-shared-binary').replace('native_dense_','native_shared_')
 (base/name).write_text(s)
for family in ['b0','c0','fixture']:
 (base/family).mkdir(exist_ok=True)
 s=(old/family/'module.rs').read_text()
 s='use crate::shared_binary_kernel;\n'+s
 if family=='fixture':s=s.replace('pub fn scalar(input:&[C<f64>],context:&Context<f64>)->[C<f64>;6]','pub fn scalar<T:NativeFloat>(input:&[C<T>],context:&Context<T>)->[C<T>;6]')
 (base/family/'module.rs').write_text(s)
records={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*old.glob('candidate/rust_codegen.rs'),*old.glob('candidate/rust_codegen/batch.rs'),*base.rglob('*.rs')]}
(base/'source-inputs.json').write_text(json.dumps({'inputs':records,'scope':'Private binary Add/Mul column dispatch; existing primitives and baseline IR preserved. Span tracking from previously qualified private emitter. Production unchanged.'},indent=2)+'\n')
with (base/'shared-binary.patch').open('w') as out:
 for name in ['rust_codegen.rs','rust_codegen/batch.rs']:
  subprocess.run(['diff','-u',str(base/'baseline'/name),str(base/'candidate'/name)],stdout=out,check=False)
print('Private shared-binary emitter prepared.')
