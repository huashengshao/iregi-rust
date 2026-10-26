"""Replay sealed partial low-N R6 explicit-power evidence; stdlib only, no integrals."""
from pathlib import Path, PurePosixPath
import argparse, contextlib, gzip, hashlib, importlib.util, io, json, os, sys, tarfile, tempfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = 'target/low-n-explicit-generalized-rank6'
ORIGINAL = '/shared/external/iregi/iregi-rust'
NUMERIC = 'validation/rank6-numeric-types'
WHEEL = 'validation/python-interface/facade-wheel-003'

def need(v, message):
    if not v:
        raise ValueError(message)

def sha(body): return hashlib.sha256(body).hexdigest()
def desc(body): return dict(sha256=sha(body), bytes=len(body))
def load(body):
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    return json.loads(body, object_pairs_hook=pairs)

def safe(name):
    p = PurePosixPath(name)
    need(name and str(p) == name and not p.is_absolute() and '..' not in p.parts, 'safe relative path')

def imported(path, label):
    spec = importlib.util.spec_from_file_location(label, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def archive(body, members):
    out = {}
    with tarfile.open(fileobj=io.BytesIO(body), mode='r:gz') as tar:
        for item in tar:
            safe(item.name)
            need(item.isfile() and item.name not in out, 'unique regular archive member')
            data = tar.extractfile(item).read()
            need(not data.startswith((b'\x7fELF', b'!<arch>')), 'no native payload')
            need(desc(data) == members.get(item.name), 'archive member byte identity')
            out[item.name] = data
    need(set(out) == set(members), 'closed archive inventory')
    return out

def parents(manifest):
    for name, expected in manifest['parent_files'].items():
        safe(name)
        need(desc((ROOT/name).read_bytes()) == expected, 'parent committed file identity: '+name)
    numeric = imported(ROOT/NUMERIC/'check.py', '_explicit_low_n_numeric_parent')
    nmanifest = load((ROOT/NUMERIC/'manifest.json').read_bytes())
    files = numeric.restore_files(nmanifest, ROOT)
    files[NUMERIC+'/manifest.json'] = (ROOT/NUMERIC/'manifest.json').read_bytes()
    wm = load((ROOT/WHEEL/'manifest.json').read_bytes())
    sources = archive((ROOT/WHEEL/'sources.tar.gz').read_bytes(), wm['sources']['members'])
    return files, sources

def restore_files(manifest):
    own = set(manifest['capsule_files']) | {'manifest.json'}
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    need(actual == own, 'closed capsule inventory')
    for name, expected in manifest['capsule_files'].items():
        safe(name); need(desc((HERE/name).read_bytes()) == expected, 'capsule identity: '+name)
    numeric, sources = parents(manifest)
    packed = archive((HERE/'payload.tar.gz').read_bytes(), manifest['payload_members'])
    files = {}
    for alias, row in manifest['aliases'].items():
        safe(alias)
        if 'numeric_alias' in row: body = numeric[row['numeric_alias']]
        elif 'wheel_source' in row: body = sources[row['wheel_source']]
        else: body = packed[row['member']]
        need(desc(body) == {k: row[k] for k in ('sha256', 'bytes')}, 'restored selected identity: '+alias)
        files[alias] = body
    return files

def normalize(value, temp_root):
    # Only filesystem prefixes change. Numeric records, guards and statuses are exact.
    if isinstance(value, str):
        text = value.replace(str(temp_root), ORIGINAL)
        if text.startswith('target/') or text.startswith('validation/'):
            text = ORIGINAL+'/'+text
        return text
    if isinstance(value, list): return [normalize(v, temp_root) for v in value]
    if isinstance(value, dict): return {normalize(k, temp_root):normalize(v, temp_root) for k,v in value.items()}
    return value

def replay(manifest, files):
    build = load(files[manifest['actual_build_receipt']])
    need(build['status'] == 'passed' and build['inputs_unchanged'] is True and not build['cleanup_errors'], 'actual coherent build passed')
    need(build['products']['cli']['sha256'] == manifest['actual_cli_sha256'], 'actual CLI product; no current CLI substitution')
    for name, expected in build['source_files'].items():
        alias = manifest['actual_source_snapshot']+'/'+name
        need(sha(files[alias]) == expected, 'actual compiled selected source: '+name)
    need(len(build['source_files']) == 145, '145 actual compiled selected source bodies')
    with tempfile.TemporaryDirectory(prefix='tirust-low-n-saved-') as td:
        root = Path(td)
        for alias, body in files.items():
            p = root/alias; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(body)
        concrete = type(Path())
        class RelocatedPath(concrete):
            def __new__(cls, *args):
                p = Path(*args)
                s = str(p)
                if s == ORIGINAL or s.startswith(ORIGINAL+'/'):
                    p = root/s.removeprefix(ORIGINAL+'/') if s != ORIGINAL else root
                return super().__new__(cls, p)
            def __init__(self, *args):
                p = Path(*args)
                s = str(p)
                if s == ORIGINAL or s.startswith(ORIGINAL+'/'):
                    p = root/s.removeprefix(ORIGINAL+'/') if s != ORIGINAL else root
                try:
                    super().__init__(p)
                except TypeError:
                    # Python <=3.11 initializes pure paths in __new__.
                    super().__init__()
        prior = Path.cwd()
        try:
            os.chdir(root)
            c = imported(root/PRIVATE/'independent_saved_check.py', '_explicit_low_n_saved_checker')
            c.Path = RelocatedPath
            dirs = [root/PRIVATE/n for n in ['capture-n1-001','capture-n4-001','capture-n4-002','capture-n5-001']]
            actual = c.compare(root/PRIVATE/'protocol.json', dirs)
            saved = load(files[PRIVATE+'/independent-all-N-final-review.json'])
            
            def differing(a,b,path='root'):
                if type(a) is dict and type(b) is dict:
                    if set(a)!=set(b): return path+': keys '+repr(set(a)^set(b))+' reason='+str(a.get('reason',''))
                    for k in a:
                        if a[k]!=b[k]: return differing(a[k],b[k],path+'/'+str(k))
                if type(a) is list and type(b) is list:
                    if len(a)!=len(b): return path+': lengths '+str((len(a),len(b)))
                    for i,(x,y) in enumerate(zip(a,b)):
                        if x!=y: return differing(x,y,path+'/'+str(i))
                return path+': '+repr(a)[:300]+' != '+repr(b)[:300]
            aa,bb=normalize(actual,root),normalize(saved,root)
            need(aa == bb, 'entire saved main review recomputed exactly after path relocation; '+differing(aa,bb)+' admission='+repr([x for x in actual['capture_history'] if x['status'] != 'saved_capture_admitted'])[:2000])
            need(actual['summary']['records'] == 68046 and actual['summary']['complete_cases'] == 8
                 and len(actual['failures']) == 4 and not any(not r['passed'] for r in actual['records']), '68046 passed math gates and four visible missing/failed cases')
            need([r['kind'] for r in actual['failures']] == ['native_timeout','unrun','unrun','unrun'], 'N5 timeout and three unrun partners preserved')
            mass = imported(root/PRIVATE/'independent_mass_identity.py', '_explicit_low_n_saved_mass')
            mass.c.Path = RelocatedPath
            identity_counts = {}
            for n, selected in [(1,[dirs[0]]),(4,dirs[1:3]),(5,[dirs[3]])]:
                output = root/f'fresh-mass-{n}.json'
                argv = ['saved-mass']
                for directory in selected: argv += ['--capture',str(directory)]
                argv += ['--output',str(output)]
                oldargv = sys.argv
                try:
                    sys.argv = argv
                    with contextlib.redirect_stdout(io.StringIO()): mass.main()
                finally: sys.argv = oldargv
                fresh = load(output.read_bytes())
                name = f'independent-n{n}-final-mass-identity.json' if n != 5 else 'independent-n5-failed-mass-identity.json'
                old = load(files[PRIVATE+'/'+name])
                need(normalize(fresh,root) == normalize(old,root), 'entire saved mass-Taylor review recomputed exactly N'+str(n))
                identity_counts[str(n)] = len(fresh['records'])
            need(identity_counts == {'1':10080,'4':10080,'5':0}, '20160 actual mass-Taylor checks; none invented for N5')
        finally: os.chdir(prior)
    return dict(status='passed_saved_partial_capsule_replay', actual_cli_sha256=manifest['actual_cli_sha256'],
                actual_selected_source_bodies=145, completed_native_calls=8, completed_complex_slots=20160,
                numerical_gates=68046, numerical_gate_failures=0, mass_Taylor_checks=identity_counts,
                timed_out_native_calls=1, unrun_native_cases=3, preserved_controller_stop=True,
                native_execution=False, producer_import=False, performance_qualified=False,
                current_098_cli_equivalence_claimed=False)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output')
    args = parser.parse_args()
    manifest = load((HERE/'manifest.json').read_bytes())
    result = replay(manifest, restore_files(manifest))
    if args.output: Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__ == '__main__': main()
