"""Portable sealed saved-data replay; no compiler, reducer or native integral.

Compiled binaries and current-host process checks are deliberately excluded;
the original independent build/terminal audits remain historical evidence.
"""
from pathlib import Path,PurePosixPath
from contextlib import redirect_stdout
import hashlib,io,json,tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent

def require(c,m):
 if not c:raise ValueError(m)
def digest(b):return hashlib.sha256(b).hexdigest()
def load_archive(raw):
 data={}
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
  for item in t.getmembers():
   name=PurePosixPath(item.name)
   require(item.isfile() and not item.issym() and not item.islnk() and not name.is_absolute() and '..' not in name.parts and item.name not in data,'safe regular unique archive member')
   data[item.name]=t.extractfile(item).read()
 return data

def main():
 m=json.loads((HERE/'manifest.json').read_text())
 for name,h in m['capsule_files'].items():require(digest((HERE/name).read_bytes())==h,'capsulefile '+name)
 data=load_archive((HERE/'evidence.tar.gz').read_bytes());require(set(data)==set(m['payload_members']),'closed payload inventory')
 for name,v in m['payload_members'].items():require(len(data[name])==v['bytes'] and digest(data[name])==v['sha256'],'payload bytes '+name)
 for name,record in m['external_files'].items():
  b=(ROOT/record['path']).read_bytes();require(digest(b)==record['sha256'],'durable parent '+name);require(name not in data,'parent/payload collision');data[name]=b
 parent=load_archive(data[m['source_parent_archive']]);inventory=json.loads(data[m['source_parent_inventory']])
 require(set(parent)==set(inventory['members']) and len(parent)==64,'closed exact64source parent')
 for name,v in inventory['members'].items():require(len(parent[name])==v['bytes'] and digest(parent[name])==v['sha256'],'parent source bytes '+name)
 for name,h in m['source_files'].items():
  b=data[name] if name in data else parent[name];require(digest(b)==h,'captured source '+name);data[name]=b
  for prefix,names in m['snapshot_aliases'].items():
   if name in names:data[prefix+name]=b
 original=m['original_root']
 def canonical(p):
  p=str(p);return p[len(original)+1:] if p.startswith(original+'/') else p
 def get(p):
  k=canonical(p);require(k in data,'missing saved evidence '+k);return data[k]
 omitted=m['omitted_compiled_binaries'];verified=omissions=0
 for name in m['receipts']:
  r=json.loads(get(name));require(r['status']=='passed' and r['inputs_unchanged'] is True and r['cleanup_errors']==[] and r.get('cancellation') is None,'successful fixed terminalreceipt')
  for key,h in {**r['inputs'],**r.get('saved_files',{})}.items():
   k=canonical(key)
   if k in omitted:require(omitted[k]==h,'declared omittedcompiledbinary');omissions+=1
   else:require(digest(get(k))==h,'replayed source/output guard '+k);verified+=1
 for name in m['independent_reviews']:require(str(json.loads(get(name))['status']).startswith('passed'),'preserved independentreview '+name)
 tests=json.loads(get(m['ibp_test_receipt']));require(tests['all_51_ibp_tests_passed'] is True and len(set(tests['test_names']))==51,'actual51IBP tests retained')
 replay={};logical_output=original+'/'+m['comparison']
 class SavedPath:
  def __init__(self,p):self.p=str(p)
  def __str__(self):return self.p
  def __truediv__(self,p):return SavedPath(str(PurePosixPath(self.p)/str(p)))
  def read_text(self):return get(self.p).decode()
  def read_bytes(self):return get(self.p)
  def open(self,mode='r'):
   require(mode in ('r','rb'),'savedinput only');return io.BytesIO(get(self.p)) if mode=='rb' else io.StringIO(get(self.p).decode())
  def exists(self):return False if self.p==logical_output and not replay else canonical(self.p) in data
  def write_text(self,text):
   require(self.p==logical_output and not replay,'one isolated replay output');replay[self.p]=text
 class SavedTar:
  @staticmethod
  def open(path,mode):return tarfile.open(fileobj=io.BytesIO(get(path)),mode=mode)
 comp=m['comparator'];ns={'__name__':'tirust_saved_capsule','__file__':original+'/'+comp};exec(compile(get(comp),'<frozen-saved-comparator>','exec'),ns)
 ns.update(Path=SavedPath,ROOT=SavedPath(original),HERE=SavedPath(original+'/'+m['logical_directory']),tarfile=SavedTar)
 with redirect_stdout(io.StringIO()):code=ns['main']()
 actual=json.loads(get(m['comparison']));again=json.loads(replay[logical_output]);require(code==0 and actual==again and actual['status']=='passed','identical complete numerical replay')
 print(json.dumps({'status':'passed','source_files':len(m['source_files']),'payload_members':len(m['payload_members']),'replayed_guard_occurrences':verified,'omitted_compiled_binary_guard_occurrences':omissions,'ibp_tests':51,'counts':actual['counts'],'new_integrals':0,'new_compilers':0,'current_host_process_absence_claim':False}))
if __name__=='__main__':main()
