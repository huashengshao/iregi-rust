"""Bounded read-only Rust emission shape check; no generated files changed."""
from pathlib import Path
import hashlib,json,re
base=Path('target/native-stack-batch');out=[]
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
def flatten_outlines(text):
 lines=text.splitlines();remaining=[];blocks={};i=0
 while i<len(lines):
  if lines[i]=='#[inline(never)]' and i+1<len(lines) and lines[i+1].startswith('fn batch_block_'):i+=1
  m=re.match(r'fn batch_block_(\d+)<',lines[i])
  if not m:remaining.append(lines[i]);i+=1;continue
  depth=lines[i].count('{')-lines[i].count('}');body=[];i+=1
  while depth:
   line=lines[i];depth+=line.count('{')-line.count('}');i+=1
   if depth:body.append(line)
  assert body[0].strip()=='let mut active_len = *count;' and body[-1].strip()=='*count = active_len;'
  blocks[m[1]]=body[1:-1]
 expanded=[];calls=0
 for line in remaining:
  m=re.fullmatch(r'\s*batch_block_(\d+)\((.*)\);',line)
  if m:
   assert m[2]=='v, stride, lanes, active, &mut active_len, resume, children, base, ctx'
   expanded.extend(blocks[m[1]]);calls+=1
  else:expanded.append(line)
 return '\n'.join(line.strip() for line in expanded if line.strip()),len(blocks),calls
def storage_shape(text):
 text=re.sub(r'base \+ \d+','base + STORAGE',text)
 text=re.sub(r'\bv\[\d+ \* stride','v[STORAGE * stride',text)
 text=re.sub(r'workspace\.prepare_controlled\(rows, \d+,','workspace.prepare_controlled(rows, CAPACITY,',text)
 text=re.sub(r'workspace\.prepare\(rows, \d+\)','workspace.prepare(rows, CAPACITY)',text)
 return text
for f in ['a0','b0','db0','c0','d0']:
 a=(base/f/f'{f}_baseline.rs').read_text();b=(base/f/f'{f}_candidate.rs').read_text();marker='\nuse super::BatchWorkspace;'
 scalar_a,batch_a=a.split(marker,maxsplit=1);scalar_b,batch_b=b.split(marker,maxsplit=1)
 before_a=storage_shape(batch_a);before_b=storage_shape(batch_b)
 aa,blocks_a,calls_a=flatten_outlines(batch_a);bb,blocks_b,calls_b=flatten_outlines(batch_b);aa=storage_shape(aa);bb=storage_shape(bb)
 row={'family':f,'scalar_source_exactly_identical':scalar_a==scalar_b,'batch_source_identical_after_storage_address_erasure':before_a==before_b,'batch_ordered_operand_shape_equal_after_transparent_outline_expansion':aa==bb,'baseline_outline_bodies':blocks_a,'candidate_outline_bodies':blocks_b,'baseline_outline_calls':calls_a,'candidate_outline_calls':calls_b,'batch_baseline_expanded_shape_sha256':sha(aa),'batch_candidate_expanded_shape_sha256':sha(bb)}
 if aa!=bb:
  ax=aa.splitlines();bx=bb.splitlines();first=next((i for i,(a,b)in enumerate(zip(ax,bx))if a!=b),min(len(ax),len(bx)));row['first_difference']={'line':first,'baseline':ax[first:first+3],'candidate':bx[first:first+3],'line_counts':[len(ax),len(bx)]}
 out.append(row)
result={'scope':'Read-only source comparison. Exact primitive operations, constants, ordered operand positions, labels and numerical-helper calls retained. Only arena addresses/capacity erased, and validated transparent outline wrappers expanded. Complements factory-probe full instruction-source provenance and runtime slot-alias parity; alone does not prove correct storage addressing.','source_layout_caveat':'Emitter text-size outlines may move boundaries when compact storage indices shorten source. Expanded equality proves ordered operand shape, not identical compiled layout or performance.','families':out}
(base/'operand-shape.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(out,indent=2))
