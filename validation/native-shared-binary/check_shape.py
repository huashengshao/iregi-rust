"""Expand only shared binary calls and transparent outline wrappers; no algebra."""
from pathlib import Path
import hashlib,json,re
base=Path('target/native-shared-binary')
original=Path('target/native-stack-batch/check_operand_shape.py').read_text()
namespace={'re':re};exec(original[original.index('def flatten_outlines'):original.index('def storage_shape')],namespace);flatten=namespace['flatten_outlines']
classifier='''#[inline]
fn contiguous_active_span(lanes: &[usize]) -> Option<(usize, usize)> {
    if lanes.is_empty() { return Some((0, 0)); }
    let first = lanes[0];
    if lanes[lanes.len() - 1].checked_sub(first) != Some(lanes.len() - 1) { return None; }
    first.checked_add(lanes.len()).map(|end| (first, end))
}'''
def expand(text,inline):
 assert text.count(classifier)==1,'span classifier differs'
 text=text.replace(classifier,'').replace('use super::shared_binary_kernel::{BinaryOperand, shared_binary};','');lines=[];shared_calls=0;refreshes=0;categories={}
 operand=r'BinaryOperand::(?:Column\(base \+ \d+\)|Constant\(\d+\))'
 pattern=re.compile(r'\s*shared_binary::<T, (true|false), (true|false)>\(v, stride, &active\[\.\.active_len\], dense_span, base \+ (\d+), ('+operand+r'), ('+operand+r'), ctx\);')
 def read(s):
  m=re.fullmatch(r'BinaryOperand::(Column|Constant)\((?:base \+ )?(\d+)\)',s);assert m
  return f'&v[(base + {m[2]}) * stride + lane]' if m[1]=='Column' else f'ctx.constant({m[2]})'
 for line in text.splitlines():
  if 'shared_binary::<T,' in line:
   m=pattern.fullmatch(line);assert m,('unexpected dispatch syntax',line)
   assert (m[2]=='true')==inline,'native primitive policy changed'
   operation='mul' if m[1]=='true' else 'add'
   left,right=read(m[4]),read(m[5])
   category=f'{operation}:{m[4].split("(")[0]}:{m[5].split("(")[0]}'
   categories[category]=categories.get(category,0)+1
   line=f'    for &lane in &active[..active_len] {{ v[(base + {m[3]}) * stride + lane] = {operation}({left}, {right}); }}'
   shared_calls+=1
  if line.strip() in ['let mut dense_span = contiguous_active_span(&active[..active_len]);','let mut dense_span = *span;','*span = dense_span;']:continue
  refreshes+=line.count('dense_span = contiguous_active_span(&active[..active_len]);')
  line=line.replace(' dense_span = contiguous_active_span(&active[..active_len]);','').replace(' dense_span = Some((0, 0));','')
  line=line.replace(', span: &mut Option<(usize, usize)>','').replace(', &mut dense_span','')
  lines.append(line)
 result='\n'.join(lines)
 assert 'dense_span' not in result and 'contiguous_active_span' not in result and 'shared_binary' not in result
 return result,shared_calls,refreshes,categories
canonical=lambda s:re.sub(r'\s+',' ',s).strip()
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
rows=[]
for family in ['b0','c0','fixture']:
 before=(base/family/f'{family}_baseline.rs').read_text();after=(base/family/f'{family}_candidate.rs').read_text();marker='\nuse super::BatchWorkspace;'
 scalar_old,batch_old=before.split(marker,1);scalar_new,batch_new=after.split(marker,1)
 inline='use super::primitives::{inline_add as add, inline_mul as mul};' in scalar_old
 stripped,calls,refreshes,categories=expand(batch_new,inline)
 old_flat,old_blocks,old_calls=flatten(batch_old);new_flat,new_blocks,new_calls=flatten(stripped);a,b=canonical(old_flat),canonical(new_flat)
 row={'family':family,'scalar_source_identical':scalar_old==scalar_new,'full_ordered_primitive_control_slot_and_helper_source_identical':a==b,'inline_arithmetic':inline,'shared_binary_calls':calls,'operand_categories':categories,'predicate_or_label_refreshes':refreshes,'baseline_bytes':len(before.encode()),'candidate_bytes':len(after.encode()),'baseline_outlines':old_blocks,'candidate_outlines':new_blocks,'baseline_calls':old_calls,'candidate_calls':new_calls,'baseline_shape_sha256':sha(a),'candidate_shape_sha256':sha(b)}
 if a!=b:
  n=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)));row['first_difference']={'offset':n,'baseline':a[max(0,n-80):n+180],'candidate':b[max(0,n-80):n+180]}
 rows.append(row)
 assert row['scalar_source_identical'] and row['full_ordered_primitive_control_slot_and_helper_source_identical'],row
report={'scope':'Expand each positional shared binary call to exactly its selected existing primitive and original slot/constant reads, remove only validated span metadata, expand transparent outlines. No arithmetic, slot, operand order, real-prefix IR, constant, label, helper name or stride is erased. Complements source review and direct alias/precision/branch tests of shared kernel implementation.','shared_kernel_sha256':hashlib.sha256((base/'shared_binary_kernel.rs').read_bytes()).hexdigest(),'families':rows}
(base/'shared-source-equivalence.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(rows,indent=2))
