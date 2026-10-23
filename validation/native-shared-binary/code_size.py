from pathlib import Path
import hashlib,json,re,subprocess
base=Path('target/native-shared-binary');binary=base/'probe';build=json.loads((base/'probe-build.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(binary)==build['binary_sha256']
raw=subprocess.check_output(['nm','-S','--size-sort','--demangle',str(binary)],text=True)
(base/'symbols.txt').write_text(raw)
symbols=[]
for line in raw.splitlines():
 m=re.match(r'([0-9a-f]+) ([0-9a-f]+) ([tTwW]) (.*)',line)
 if m and m[4].startswith('native_shared_binary_probe::'):symbols.append({'address':m[1],'bytes':int(m[2],16),'kind':m[3],'name':m[4]})
groups=[]
for family in ['b0','c0','fixture']:
 for variant in ['baseline','candidate']:
  for domain,tag in [('f64','::<f64>'),('DoubleFloat','::double::DoubleFloat>'),('Float','::multiprecision::Float>')]:
   selected=[r for r in symbols if f'::{family}::{variant}::' in r['name'] and (tag in r['name'])]
   batches=[r for r in selected if any(part in r['name'] for part in ['::batch_block_','::batch_body_','::evaluate_batch::'])]
   groups.append({'family':family,'variant':variant,'domain':domain,'named_text_bytes':sum(r['bytes'] for r in selected),'symbol_count':len(selected),'named_batch_text_bytes':sum(r['bytes'] for r in batches),'named_scalar_or_helper_text_bytes':sum(r['bytes'] for r in selected if r not in batches)})
shared=[r for r in symbols if '::shared_binary_kernel::shared_binary::' in r['name']]
unique_shared={(r['address'],r['bytes']) for r in shared}
shared_by_domain={domain:sum(size for address,size in {(r['address'],r['bytes']) for r in shared if tag in r['name']}) for domain,tag in [('f64','::<f64,'),('DoubleFloat','::double::DoubleFloat,'),('Float','::multiprecision::Float,')]}
result={'scope':'Named attributable text only. Shared helpers counted separately with identical address/size aliases deduplicated, not added to every family. Different numeric monomorphizations separated. This does not measure cache misses or runtime performance.','binary_sha256':build['binary_sha256'],'binary_file_bytes':binary.stat().st_size,'source_bytes':{family:{variant:(base/family/f'{family}_{variant}.rs').stat().st_size for variant in ['baseline','candidate']} for family in ['b0','c0','fixture']},'shared_kernel_source_bytes':(base/'shared_binary_kernel.rs').stat().st_size,'named_text_groups':groups,'shared_binary_symbols':shared,'shared_binary_unique_address_count':len(unique_shared),'shared_binary_unique_text_bytes':sum(size for address,size in unique_shared),'shared_binary_unique_text_by_domain':shared_by_domain,'symbols':symbols}
(base/'code-size.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='symbols'},indent=2))
