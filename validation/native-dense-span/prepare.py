from pathlib import Path
import hashlib,json,shutil
root=Path.cwd();base=root/'target/native-dense-span';source=root/'dependencies/oneloopmaster/src'
manifest={}
for variant in ['baseline','candidate']:
 dst=base/variant;dst.mkdir(exist_ok=True);(dst/'rust_codegen').mkdir(exist_ok=True)
 for relative in ['rust_codegen.rs','rust_codegen/batch.rs']:
  data=(source/relative).read_bytes();manifest[relative]=hashlib.sha256(data).hexdigest();(dst/relative).write_bytes(data)
 code=(dst/'rust_codegen.rs').read_text()
 old='''    pub use crate::native::batch::{self, BatchExecutionPolicy, BatchWorkspace};
    pub use crate::native::{ConstantContext as Context, ConstantSpec, primitives};
    pub use primitives::{C, NativeFloat};'''
 assert code.count(old)==1
 code=code.replace(old,'    pub use oneloop::rust_codegen::runtime::*;').replace('mod batch;', '#[path="rust_codegen/batch.rs"] mod batch;')
 (dst/'rust_codegen.rs').write_text(code)
p=base/'candidate/rust_codegen/batch.rs';s=p.read_text()
s=s.replace('    let preparation = if generator.controlled {','''    if generator.controlled {
        // Metadata only: sorted unique lanes are inherited from root/filter/Label.
        source.push_str("\\n#[inline]\\nfn contiguous_active_span(lanes: &[usize]) -> Option<(usize, usize)> {\\n    if lanes.is_empty() { return Some((0, 0)); }\\n    let first = lanes[0];\\n    if lanes[lanes.len() - 1].checked_sub(first) != Some(lanes.len() - 1) { return None; }\\n    first.checked_add(lanes.len()).map(|end| (first, end))\\n}\\n\\n");
    }
    let preparation = if generator.controlled {''')
s=s.replace('active_len = kept; }}", read(*condition)?', 'active_len = kept; dense_span = contiguous_active_span(&active[..active_len]); }}", read(*condition)?')
s=s.replace('active_len = 0;"\n', 'active_len = 0; dense_span = Some((0, 0));"\n')
s=s.replace('active_len += 1; }} }}").unwrap();', 'active_len += 1; }} }} dense_span = contiguous_active_span(&active[..active_len]);").unwrap();')
old='''                writeln!(body, "    {loop_header} {{ v[(base + {destination}) * stride + lane] = {expression}; }}").unwrap();'''
new='''                if self.controlled && matches!(instruction, Instruction::Add(..) | Instruction::Mul(..)) {
                    writeln!(body, "    if let Some((begin, end)) = dense_span {{ for lane in begin..end {{ v[(base + {destination}) * stride + lane] = {expression}; }} }} else {{ {loop_header} {{ v[(base + {destination}) * stride + lane] = {expression}; }} }}").unwrap();
                } else {
                    writeln!(body, "    {loop_header} {{ v[(base + {destination}) * stride + lane] = {expression}; }}").unwrap();
                }'''
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('for &lane in lanes {{ resume[lane] = 0; }}\\n{body}', 'for &lane in lanes {{ resume[lane] = 0; }}\\n    let mut dense_span = contiguous_active_span(&active[..active_len]);\\n{body}')
s=s.replace('count: &mut usize, resume:', 'count: &mut usize, span: &mut Option<(usize, usize)>, resume:')
s=s.replace('let mut active_len = *count;\\n{body}    *count = active_len;', 'let mut active_len = *count;\\n    let mut dense_span = *span;\\n{body}    *count = active_len;\\n    *span = dense_span;')
s=s.replace('active, &mut active_len, resume, children', 'active, &mut active_len, &mut dense_span, resume, children')
assert s.count('dense_span = contiguous_active_span')==3
assert 'active_len = 0; dense_span = Some((0, 0));' in s
p.write_text(s)
(base/'source-inputs.json').write_text(json.dumps({'upstream_sources':manifest,'scope':'Private copies of existing emitter; runtime re-export only in both variants, dense metadata/loop change only in candidate; no production edits'},indent=2)+'\n')
print('Prepared private emitter copies; existing primitive/control IR unchanged.')
