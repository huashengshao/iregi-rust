"""Use the already qualified scoped loader closure, with no installation."""
import json,os,pathlib
root=pathlib.Path.cwd();loader=json.loads((root/'validation/python-notebooks/benchmark-browser/attempt002/loader-environment.json').read_text());os.environ['LD_LIBRARY_PATH']=loader['library_path'];os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(root/'.local/playwright-browsers')
python=root/'.local/notebooks-browser-env/bin/python';script=root/'target/notebook-wheel004-protocol/browser.py';os.execve(str(python),[str(python),str(script)],os.environ)
