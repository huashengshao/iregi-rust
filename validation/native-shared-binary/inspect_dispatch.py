from pathlib import Path
import hashlib,json,re,subprocess
base=Path('target/native-shared-binary');report=json.loads((base/'code-size.json').read_text());symbols=report['symbols'];binary=base/'probe'
assert hashlib.sha256(binary.read_bytes()).hexdigest()==report['binary_sha256']
selected=[]
for family in ['b0','c0']:
 selected.append((family+'-candidate-block0',next(r for r in symbols if r['name']==f'native_shared_binary_probe::{family}::candidate::batch_block_0::<f64>')))
for op in ['false','true']:
 selected.append(('shared-'+('mul' if op=='true' else 'add'),next(r for r in symbols if r['name']==f'native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, {op}, false>')))
results=[]
for name,symbol in selected:
 start=int(symbol['address'],16);text=subprocess.check_output(['objdump','-d','-C',f'--start-address={start}',f'--stop-address={start+symbol["bytes"]}',str(binary)],text=True)
 target=base/f'{name}.asm';target.write_text(text)
 shared_calls=[line.strip() for line in text.splitlines() if re.search(r'\bcallq?\b',line) and 'shared_binary_kernel::shared_binary' in line]
 results.append({'label':name,'symbol':symbol,'assembly_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'direct_calls_to_shared_binary':len(shared_calls),'sample_shared_calls':shared_calls[:4]})
assert all(r['direct_calls_to_shared_binary']>0 for r in results[:2]),'dispatcher was unexpectedly inlined or calls not found'
(base/'dispatch-assembly.json').write_text(json.dumps({'scope':'Static machine-code evidence that generated B0/C0 blocks call the shared non-inlined arithmetic loop. Does not establish speedup or dynamic cache behavior.','symbols':results},indent=2)+'\n');print(json.dumps(results,indent=2))
