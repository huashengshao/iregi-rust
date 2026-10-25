#!/usr/bin/env python3
"""Verify saved focused Cargo proof using stdlib only; starts no native jobs."""
from pathlib import Path
import hashlib,json,re,tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
def sha(data): return hashlib.sha256(data).hexdigest()
def read(p): return json.loads(p.read_text())
m=read(HERE/'manifest.json'); origin=m['original_root']+'/'
for name,value in m['capsule_files'].items(): assert sha((HERE/name).read_bytes())==value,name
for name,value in m['parents'].items(): assert sha((ROOT/name).read_bytes())==value,name
with tarfile.open(HERE/'evidence.tar.gz') as t:
 assert set(t.getnames())==set(m['payload_members'])
 payload={n:t.extractfile(n).read() for n in t.getnames()}
for n,data in payload.items():
 assert sha(data)==m['payload_members'][n]['sha256'] and len(data)==m['payload_members'][n]['bytes'],n
parent=read(ROOT/m['source_parent'])
with tarfile.open(ROOT/m['source_parent_archive']) as t: inherited={n:t.extractfile(n).read() for n in t.getnames() if t.getmember(n).isfile()}
with tarfile.open(ROOT/m['source_overlay_archive']) as t:
 for member in t:
  prefix='target/routing-rational-cayley-adoption/after/'
  if member.isfile() and member.name.startswith(prefix): inherited[member.name[len(prefix):]]=t.extractfile(member).read()
for n,value in parent['source_files'].items():
 # Parent also names its unrelated examples, not needed by this focused build.
 if n in inherited: assert sha(inherited[n])==value,n
base='target/typed-dual-reset-proposal/'
receipts={name:json.loads(payload[name]) for name in m['receipts']}
sources={}
for name,d in receipts.items():
 if d['operation']!='build':continue
 directory=name.rsplit('/',1)[0]
 table={}
 for n,value in d['source_files'].items():
  snapshot=directory+'/source-snapshot/'+n
  data=payload.get(snapshot,payload.get(n,inherited.get(n)))
  assert data is not None and sha(data)==value,(snapshot,value)
  table[n]=data
 sources[directory]=table

def lookup(name):
 name=name.removeprefix(origin)
 if name in payload:return payload[name]
 if '/source-snapshot/' in name:
  directory,n=name.split('/source-snapshot/',1)
  return sources[directory][n]
 if name in inherited:return inherited[name]
 raise AssertionError(('unavailable saved binding',name))
checks=0; omissions=0
for name,d in receipts.items():
 assert d['inputs_unchanged'] and d['cleanup_errors']==[],name
 assert d['elapsed_seconds']<=d['total_seconds'],name
 directory=name.rsplit('/',1)[0]
 for p,value in d['inputs'].items():
  relative=p.removeprefix(origin)
  if relative in m['omitted_compiled_binaries']:
   assert m['omitted_compiled_binaries'][relative]==value;omissions+=1;continue
  if d['operation']=='build' and relative in d['source_files']:
   data=sources[directory][relative]
  else:data=lookup(p)
  assert sha(data)==value,p;checks+=1
 for p,value in d['saved_files'].items():
  if p in m['omitted_compiled_binaries']:
   assert m['omitted_compiled_binaries'][p]==value;omissions+=1;continue
  assert sha(lookup(p))==value,p;checks+=1
 for step in d['steps']:
  assert step['owned_group_gone'] and not step['group_existed_at_cleanup'],(name,step)
  assert step['elapsed_seconds']<=step['timeout_seconds'],(name,step)
  assert step['returncode']==(0 if step['status']=='exited' else 101),(name,step)
final_build=receipts[base+'build-003/receipt.json']; final_tests=receipts[base+'tests-003/receipt.json']
assert final_build['status']==final_tests['status']=='passed'
q=read(HERE/'qualification.json');names=q['tests'];assert len(names)==2
listing=payload[base+'tests-003/listing.log'].decode()
assert set(re.findall(r'^(.+): test$',listing,re.M))==set(names)
for i,name in enumerate(names):
 text=payload[base+f'tests-003/exact-{i}.log'].decode()
 assert re.search(r'^test '+re.escape(name)+r' \.\.\. ok$',text,re.M)
 assert 'test result: ok. 1 passed; 0 failed; 0 ignored;' in text
assert final_tests['admitted_tests']==names
assert receipts[base+'build-001/receipt.json']['status']=='failed'
assert 'E0624' in payload[base+'build-001/cargo-build.log'].decode()
assert receipts[base+'tests-002/receipt.json']['status']=='failed'
assert 'a real recorded diagnostic must be cleared' in payload[base+'tests-002/exact-0.log'].decode()
before=payload[base+'execution-before.rs'].decode();after=payload['crates/iregi-rust/src/execution.rs'].decode()
reset='''        // Typed-input validation can return before reduce_batch resets the
        // observable state. Attribute every early error to this requested call.
        self.stats = ExecutionStats { input_rows: rows, ..ExecutionStats::default() };
        self.profile = ExecutionProfile::default();
        self.diagnostics.clear();
'''
assert after.replace(reset,'        // Typed-input validation can return before reduce_batch resets counters.\n',1)==before
assert after.index(reset)<after.index('let expected = checked_mul(rows, self.parameters)?;',after.index(reset))
print(json.dumps({'status':'passed','selected_tests':2,'successful_build_seconds':final_build['elapsed_seconds'],
 'successful_test_seconds':final_tests['elapsed_seconds'],'verified_saved_bindings':checks,
 'omitted_binary_hash_occurrences':omissions,'preserved_failed_attempts':2,
 'native_jobs_started':0,'performance_claim':False}))
