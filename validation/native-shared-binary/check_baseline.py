from pathlib import Path
import re,hashlib,json,difflib
root=Path.cwd();base=root/'target/native-shared-binary';prod=root/'crates/iregi-masters/src/generated'
sha=lambda x:hashlib.sha256(x.encode()).hexdigest()
def canonical(source,table):
 constants=[x.strip().removesuffix(',') for x in table.read_text().splitlines() if x.strip().startswith('ConstantSpec::')]
 return re.sub(r'ctx\.constant\((\d+)\)',lambda m:'ctx.constant('+constants[int(m[1])]+')',source.read_text())
results=[]
for fam in ['b0','c0']:
 a=canonical(base/fam/f'{fam}_baseline.rs',base/fam/'constants.rs');b=canonical(prod/f'{fam}.rs',prod/'constants.rs')
 record={'family':fam,'exact_after_constant_index_expansion':a==b,'paired_expanded_sha256':sha(a),'production_expanded_sha256':sha(b),'method':'Only replace ctx.constant integer indices by the exact ConstantSpec text at those indices; no symbolic or numeric rewriting.'}
 results.append(record)
 if a!=b:(base/f'{fam}-baseline-diff.txt').write_text(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='paired',tofile='production')))
(base/'baseline-source-equivalence.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
