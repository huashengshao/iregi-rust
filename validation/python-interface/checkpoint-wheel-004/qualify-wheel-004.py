"""Fresh installed-wheel runtime qualification; exact baseline tests, no source imports."""
from __future__ import annotations
import hashlib,json,os,signal,subprocess,sys,time,xml.etree.ElementTree as ET
from pathlib import Path
root=Path.cwd();base=root/'target/python-interface-build';venv=root/'.local/tirust-wheel-004-env'
wheel=root/'target/python-interface-build/wheels-004/tirust-0.1.0-cp310-abi3-linux_x86_64.whl'
inspection=json.loads((base/'wheel-004-inspection.json').read_text());assert inspection['pass']
assert hashlib.sha256(wheel.read_bytes()).hexdigest()==inspection['wheel_sha256']
assert not venv.exists()
env=os.environ.copy();env.pop('PYTHONPATH',None);env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
start=json.loads((base/'wheel-004-start.json').read_text())
def guard():
    for name,sha in start['input_files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==sha,name
    return True
assert guard()
def run(name,command,cap=300):
    tick=time.monotonic();status='completed'
    with (base/f'{name}.stdout').open('w') as out,(base/f'{name}.stderr').open('w') as err:
        p=subprocess.Popen(command,env=env,stdout=out,stderr=err,start_new_session=True)
        try:code=p.wait(timeout=cap)
        except subprocess.TimeoutExpired:
            status='timeout';os.killpg(p.pid,signal.SIGKILL);code=p.wait()
    receipt={'command':command,'seconds':time.monotonic()-tick,'exit_code':code,'status':status,'cap_seconds':cap,'wheel_sha256':inspection['wheel_sha256'],'source_unchanged':guard(),'pass':code==0 and status=='completed'}
    (base/f'{name}.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
python=json.loads((base/'wheel-003-start.json').read_text())['command'];python=python[python.index('--interpreter')+1]
a=run('wheel-004-create-env',['uv','venv','--python',python,str(venv.relative_to(root))]);assert a['pass']
b=run('wheel-004-fresh-install',['uv','pip','install','--python',str(venv.relative_to(root)/'bin/python'),str(wheel.relative_to(root)),'numpy==2.5.4','pytest==8.4.2','basedpyright==1.40.2']);assert b['pass']
code='''import importlib,json,sys\nimport tirust as t\nn=importlib.import_module("tirust._tirust")\nt.initialize();t.initialize()\nnames=("Expression","Float","ComplexFloat","Model","FeynmanDiagram","TensorExpression","ReductionPlan","Workspace")\nclasses={name:{"module":getattr(t,name).__module__,"name":getattr(t,name).__name__,"native_alias":getattr(t,name) is getattr(n,name)} for name in names}\nassert all(v["native_alias"] for v in classes.values())\nassert issubclass(t.TensorExpression,t.Expression)\ncanonical=[name for name in sys.modules if name=="symbolica" or name.startswith("symbolica.")]\nassert canonical==[]\nassert "tirust-wheel-004-env" in t.__file__\nprint(json.dumps({"file":t.__file__,"native_file":n.__file__,"native_name":n.__name__,"version":t.__version__,"classes":classes,"tensor_is_expression_subclass":True,"canonical_modules":canonical}))\n'''
c=run('wheel-004-import',[str(venv.relative_to(root)/'bin/python'),'-c',code]);assert c['pass']
identity=json.loads((base/'wheel-004-import.stdout').read_text())
actual=Path(identity['native_file']);assert hashlib.sha256(actual.read_bytes()).hexdigest()==inspection['native_sha256']
nm=subprocess.check_output(['nm','-D','--defined-only',str(actual)],text=True)
entrypoints=[line for line in nm.splitlines() if 'PyInit_' in line];assert len(entrypoints)==1 and entrypoints[0].endswith(' PyInit__tirust')
(base/'wheel-004-native-entrypoints.json').write_text(json.dumps({'defined_python_entrypoints':entrypoints,'native_sha256':inspection['native_sha256'],'pass':True},indent=2)+'\n')
command=[str(venv.relative_to(root)/'bin/python'),'-m','pytest','-vv','tests/python/test_tirust_interop.py','tests/python/test_tirust_numerics.py','--junitxml=target/python-interface-build/wheel-004-runtime.junit.xml']
d=run('wheel-004-runtime',command)
if not d['pass']:sys.exit('Focused actual runtime tests failed; receipts preserved.')
cases=list(ET.parse(base/'wheel-004-runtime.junit.xml').iter('testcase'))
assert len(cases)==29 and not any(case.find(tag) is not None for case in cases for tag in ('failure','error','skipped'))
e=run('wheel-004-installed-typing',[str(venv.relative_to(root)/'bin/basedpyright'),'--project','target/python-interface-build/installed-client/pyrightconfig.json','--pythonpath',str(venv/'bin/python'),'--outputjson']);assert e['pass']
typing=json.loads((base/'wheel-004-installed-typing.stdout').read_text());assert typing['summary']['errorCount']==typing['summary']['warningCount']==0
summary={'scope':'same29 actual native interoperability/numerical tests against fresh installed local dev wheel; no Community/release/platform/performance claim','wheel_sha256':inspection['wheel_sha256'],'native_sha256':inspection['native_sha256'],'venv':str(venv.relative_to(root)),'all29tests_pass':True,'test_count':29,'failures':0,'skips':0,'installed_consumer_typing_errors':0,'installed_consumer_typing_warnings':0,'source_unchanged':guard(),'pass':True}
(base/'wheel-004-qualification.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
