"""Portable saved-only replay. No compiler, integral, native binary or PID access."""
import argparse,ast,contextlib,hashlib,io,json,re,tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
Q='target/checked-g-zero-mass-fallback-qualification/'
CENTRAL='validation/checked-g-generalized-core-tests/'

def digest(body):return hashlib.sha256(body).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def safe(alias):
 p=Path(alias);require(not p.is_absolute()and '..'not in p.parts,'unsafe alias '+alias)
 require('__pycache__'not in p.parts and p.suffix not in {'.pyc','.so','.a','.o','.mod','.smod','.dll','.dylib'},'omitted native/cache alias '+alias)
 require(p.name not in {'frozen-tests','iregi-reference-quad-generalized'},'native alias '+alias)
 return alias

def object_archive(path,members):
 data={}
 with tarfile.open(path,'r:gz')as tar:
  infos=tar.getmembers();require(len(infos)==len(members),'payload member count')
  for info in infos:
   require(info.isfile()and re.fullmatch(r'objects/[0-9a-f]{64}',info.name)is not None,'unsafe payload member')
   require(info.name in members and info.name not in data,'unexpected/repeated member')
   body=tar.extractfile(info).read();meta=members[info.name]
   require(len(body)==meta['bytes']and digest(body)==meta['sha256'],'payload object hash '+info.name)
   require(not body.startswith((b'\x7fELF',b'!<arch>',b'MZ')),'native bytes forbidden')
   require(re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}',body)is None,'license literal forbidden')
   data[info.name]=body
 return data

def restore_files(manifest=None):
 manifest=json.loads((HERE/'manifest.json').read_text())if manifest is None else manifest
 for name,meta in manifest['capsule_files'].items():
  body=(HERE/name).read_bytes();require(len(body)==meta['bytes']and digest(body)==meta['sha256'],'capsule file '+name)
 for name,meta in manifest['parent_files'].items():
  body=(ROOT/name).read_bytes();require(len(body)==meta['bytes']and digest(body)==meta['sha256'],'declared parent file '+name)
 parent=json.loads((ROOT/CENTRAL/'manifest.json').read_text());require(digest((ROOT/CENTRAL/'manifest.json').read_bytes())==manifest['central_parent_manifest_sha256'],'central manifest')
 parent_objects=object_archive(ROOT/CENTRAL/'payload.tar.gz',parent['payload_members'])
 objects=object_archive(HERE/'payload.tar.gz',manifest['payload_members']);files={}
 for alias,meta in manifest['preserved_files'].items():
  safe(alias)
  if 'parent_alias'in meta:
   source=parent['preserved_files'][meta['parent_alias']];body=parent_objects[source['member']]
  else:body=objects[meta['member']]
  require(len(body)==meta['bytes']and digest(body)==meta['sha256'],'preserved hash '+alias);files[alias]=body
 return files
restore=restore_files

def j(files,alias):return json.loads(files[alias])

def replay_consumer(files,alias,output):
 # The two archived consumers only read saved JSON/raw arrays and use Fraction.
 # AST adaptation redirects Path I/O to already hash-checked bytes, and fixes the
 # original project prefix. No source/producer/native module is imported.
 source=files[alias];tree=ast.parse(source,filename=alias)
 allowed={'pathlib','fractions','hashlib','json'}
 for node in ast.walk(tree):
  if isinstance(node,ast.Import):require(all(n.name in allowed for n in node.names),'non-stdlib consumer import')
  if isinstance(node,ast.ImportFrom):require(node.module in allowed,'non-stdlib consumer from-import')
  if isinstance(node,ast.Call)and isinstance(node.func,ast.Name):require(node.func.id not in {'open','eval','exec','compile','__import__'},'consumer native/dynamic I/O')
 writes={};original_root=Path('/shared/external/iregi/iregi-rust')
 def key(path):return str(Path(path).relative_to(original_root))
 def read_bytes(path):return files[key(path)]
 def read_text(path):return read_bytes(path).decode()
 def write_text(path,text):
  name=key(path);require(name==output,'consumer may only write its declared in-memory result');writes[name]=text.encode();return len(text)
 class SavedIO(ast.NodeTransformer):
  def visit_Call(self,node):
   node=self.generic_visit(node)
   if isinstance(node.func,ast.Attribute)and node.func.attr in {'read_text','read_bytes','write_text'}:
    target={'read_text':'_saved_read_text','read_bytes':'_saved_read_bytes','write_text':'_saved_write_text'}[node.func.attr]
    return ast.copy_location(ast.Call(ast.Name(target,ast.Load()),[node.func.value,*node.args],node.keywords),node)
   if isinstance(node.func,ast.Attribute)and isinstance(node.func.value,ast.Name)and node.func.value.id=='Path'and node.func.attr=='cwd':
    return ast.copy_location(ast.Call(ast.Name('Path',ast.Load()),[ast.Constant(str(original_root))],[]),node)
   return node
 tree=ast.fix_missing_locations(SavedIO().visit(tree));scope={'__name__':'saved_only_consumer','__file__':str(original_root/alias),'_saved_read_bytes':read_bytes,'_saved_read_text':read_text,'_saved_write_text':write_text}
 with contextlib.redirect_stdout(io.StringIO()):exec(compile(tree,alias,'exec'),scope);scope['main']()
 require(set(writes)=={output}and writes[output]==files[output],'complete saved consumer result byte replay '+output)
 return json.loads(writes[output])

def replay(files,manifest=None):
 manifest=json.loads((HERE/'manifest.json').read_text())if manifest is None else manifest
 contexts=manifest['source_contexts'];observations=0
 for build,context in contexts.items():
  receipt=j(files,context['receipt_alias']);require(receipt['status']==context['status'],'actual build status '+build)
  require(receipt['source_files']==context['source_files'],'source receipt map '+build)
  for canonical,expected in receipt['source_files'].items():
   alias=Q+build+'/source-snapshot/'+canonical;require(digest(files[alias])==expected,'actual compiled source '+alias);observations+=1
  if build!='build-001':require(receipt['inputs_unchanged']and not receipt['cleanup_errors'],'successful build guards '+build)
 require(observations==638,'all four actual source contexts')
 # Latest canonical overlays are intentionally permitted over the older parent.
 for canonical,expected in contexts['build-004']['source_files'].items():require(digest(files[canonical])==expected,'latest canonical source '+canonical)
 require(len(contexts['build-004']['source_files'])==161,'latest coherent source count')
 positive={'normal-001':5,'normal-002':5,'ordinary-002':1,'scale-001':1}
 for stage,count in positive.items():
  receipt=j(files,Q+stage+'/receipt.json');require(receipt['status']=='passed'and not receipt['unrun_tests']and receipt['inputs_unchanged']and not receipt['cleanup_errors'],'strict successful stage '+stage)
  tests=[step for step in receipt['steps']if step['name']!='listing'];require(len(tests)==count,'strict actual test count '+stage)
  for i,step in enumerate(tests,1):
   require(step['status']=='exited'and step['owned_group_gone']and step['strict_exact_gate']=='passed','actual named test '+stage)
   text=files[Q+stage+'/step-'+str(i)+'.log'].decode();summaries=[s for s in text.splitlines()if s.startswith('test result:')]
   require(len(summaries)==1 and re.fullmatch(r'test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; [0-9]+ filtered out; finished in [^\n]+',summaries[0]),'strict one-test summary '+stage)
 failed=j(files,Q+'ordinary-001/receipt.json');require(failed['status']=='failed'and 'assertion `left == right` failed'in files[Q+'ordinary-001/step-1.log'].decode(),'preserved exact-equality observer failure')
 derivative=j(files,Q+'dual-002/result.json');require(j(files,Q+'dual-002/receipt.json')['status']=='failed'and derivative['calls'][0]['lanes'][0]['moments']is None,'preserved kinematic derivative refusal')
 ordinary=replay_consumer(files,Q+'compare-saved-current.py',Q+'current-qualification.json')
 scale=replay_consumer(files,Q+'compare-saved-scale.py',Q+'scale-qualification.json')
 require(ordinary['gate_count']==34 and scale['gate_count']==68,'all102 saved math gates')
 qualification=j(files,Q+'qualification.json');require(qualification==json.loads((HERE/'qualification.json').read_text()),'qualification exact copy')
 require(qualification['saved_math_gates']==102 and qualification['successful_distinct_tests']==7 and not qualification['full_massless_kinematic_dual_qualified']and not qualification['highrank_zero_mass_qualified'],'honest scope')
 rejected='target/checked-g-zero-mass-quad-reference/zero_dot-001/'
 require(j(files,rejected+'receipt.json')['status']=='failed'and b'tensor requires unit powers'in files[rejected+'request.stderr'],'rejected tensor header preserved')
 return {'status':'passed_saved_only_zero_mass_ordinary_and_scale_dual','preserved_aliases':len(files),'actual_source_contexts':4,'source_hash_observations':observations,'latest_source_files':161,'saved_math_gates':102,'successful_distinct_tests':7,'other_mass_dual_qualified':False,'highrank_qualified':False,'native_process_or_compiler_execution':False,'parent_math_replayed':False}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reconstruct',type=Path);args=parser.parse_args();manifest=json.loads((HERE/'manifest.json').read_text());files=restore_files(manifest);result=replay(files,manifest)
 if args.reconstruct:
  args.reconstruct.mkdir(parents=True,exist_ok=False)
  for alias,body in files.items():
   p=args.reconstruct/safe(alias);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body)
  result['reconstructed_files']=len(files)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
