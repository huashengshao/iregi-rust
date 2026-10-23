from pathlib import Path
import hashlib,json,re
base=Path('target/native-dense-span')
original=Path('target/native-stack-batch/check_operand_shape.py').read_text()
namespace={'re':re};exec(original[original.index('def flatten_outlines'):original.index('def storage_shape')],namespace);flatten=namespace['flatten_outlines']
classifier='''#[inline]
fn contiguous_active_span(lanes: &[usize]) -> Option<(usize, usize)> {
    if lanes.is_empty() { return Some((0, 0)); }
    let first = lanes[0];
    if lanes[lanes.len() - 1].checked_sub(first) != Some(lanes.len() - 1) { return None; }
    first.checked_add(lanes.len()).map(|end| (first, end))
}'''
def strip_dense(text):
 assert text.count(classifier)==1,'span classifier source differs'
 text=text.replace(classifier,'');lines=[];dense_loops=0;refreshes=0
 pattern=re.compile(r'\s*if let Some\(\(begin, end\)\) = dense_span \{ for lane in begin\.\.end \{ (.+;) \} \} else \{ for &lane in &active\[\.\.active_len\] \{ (.+;) \} \}')
 for line in text.splitlines():
  if 'if let Some((begin, end)) = dense_span' in line:
   m=pattern.fullmatch(line);assert m,'unknown dense loop form';assert m[1]==m[2],'dense/sparse arithmetic differs';assert '= add(' in m[1] or '= mul(' in m[1]
   line='    for &lane in &active[..active_len] { '+m[1]+' }';dense_loops+=1
  if line.strip() in ['let mut dense_span = contiguous_active_span(&active[..active_len]);','let mut dense_span = *span;','*span = dense_span;']:continue
  refreshes+=line.count('dense_span = contiguous_active_span(&active[..active_len]);')
  line=line.replace(' dense_span = contiguous_active_span(&active[..active_len]);','').replace(' dense_span = Some((0, 0));','')
  line=line.replace(', span: &mut Option<(usize, usize)>','').replace(', &mut dense_span','')
  lines.append(line)
 result='\n'.join(lines);assert 'dense_span' not in result and 'contiguous_active_span' not in result
 return result,dense_loops,refreshes
def canonical(text):return re.sub(r'\s+',' ',text).strip()
results=[]
for family in ['b0','c0','fixture']:
 if not (base/family/f'{family}_baseline.rs').exists():continue
 before=(base/family/f'{family}_baseline.rs').read_text();after=(base/family/f'{family}_candidate.rs').read_text();marker='\nuse super::BatchWorkspace;'
 scalar_old,batch_old=before.split(marker,1);scalar_new,batch_new=after.split(marker,1);stripped,loops,refreshes=strip_dense(batch_new)
 old_flat,old_blocks,old_calls=flatten(batch_old);new_flat,new_blocks,new_calls=flatten(stripped);a=canonical(old_flat);b=canonical(new_flat)
 row={'family':family,'scalar_source_identical':scalar_old==scalar_new,'full_ordered_primitive_control_slot_and_helper_source_identical':a==b,'dense_loop_pairs_verified':loops,'predicate_or_label_refreshes':refreshes,'baseline_bytes':len(before.encode()),'candidate_bytes':len(after.encode()),'baseline_outlines':old_blocks,'candidate_outlines':new_blocks,'baseline_calls':old_calls,'candidate_calls':new_calls,'baseline_shape_sha256':hashlib.sha256(a.encode()).hexdigest(),'candidate_shape_sha256':hashlib.sha256(b.encode()).hexdigest()}
 if a!=b:
  n=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)));row['first_difference']={'offset':n,'baseline':a[max(0,n-80):n+180],'candidate':b[max(0,n-80):n+180]}
 results.append(row)
 assert row['scalar_source_identical'] and row['full_ordered_primitive_control_slot_and_helper_source_identical'],row
(base/'dense-source-equivalence.json').write_text(json.dumps({'scope':'Read-only source audit: remove only exact validated span metadata and one duplicate of each verified-identical dense/sparse Add/Mul expression; expand existing transparent outline wrappers. No slot, operand, constant, label, helper name, arithmetic or stride is erased.','families':results},indent=2)+'\n')
print(json.dumps(results,indent=2))
