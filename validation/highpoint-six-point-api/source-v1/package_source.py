"""Freeze the isolated integration for source review; no compiler or evaluator."""
from pathlib import Path
import datetime, difflib, gzip, hashlib, io, json, subprocess, tarfile
BASE = Path('target/public-highpoint/six-point-integration')
CORE = BASE / 'core'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    p = BASE / name
    if p.exists(): raise RuntimeError(f'refusing to replace {p}')
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    return p
baseline = json.loads((BASE/'baseline.json').read_text())
original = {}
for rel, expected in baseline['source_files'].items():
    name = 'crates/iregi-rust/' + rel
    source = Path(name)
    assert sha(source) == expected, name
    original[name] = source.read_bytes()
# A bound baseline independent of future production edits.
for name, data in original.items():
    p=BASE/'production-baseline'/name
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists(): assert p.read_bytes()==data
    else: p.write_bytes(data)
candidate = {str(p.relative_to(CORE)): p for p in CORE.rglob('*') if p.is_file()}
code_docs = {n:p for n,p in candidate.items() if n.startswith(('crates/', 'docs/'))}
patch=[]; changes=[]
for name,p in sorted(code_docs.items()):
    before=original.get(name,b''); after=p.read_bytes()
    if before==after: continue
    assert name in original or not Path(name).exists(), name
    patch.append(f'diff --git a/{name} b/{name}\n')
    if name not in original: patch.append('new file mode 100644\n')
    patch.extend(difflib.unified_diff(before.decode().splitlines(keepends=True),after.decode().splitlines(keepends=True),fromfile='a/'+name if name in original else '/dev/null',tofile='b/'+name,n=3))
    changes.append({'path':name,'before_sha256':hashlib.sha256(before).hexdigest() if name in original else None,'after_sha256':sha(p)})
patch_path=BASE/'integration.patch'
assert not patch_path.exists()
patch_path.write_text(''.join(patch))
check=subprocess.run(['git','apply','--check',str(patch_path)],capture_output=True,text=True)
(BASE/'patch-check.stdout').write_text(check.stdout)
(BASE/'patch-check.stderr').write_text(check.stderr)
assert check.returncode==0,check.stderr
# Complete exact source archive, including every include_str target.
archive_members={}
for prefix,root in [('candidate',CORE),('production-baseline',BASE/'production-baseline')]:
    for p in sorted(root.rglob('*')):
        if p.is_file(): archive_members[f'{prefix}/{p.relative_to(root)}']=p
archive=BASE/'sources.tar.gz'
assert not archive.exists()
with archive.open('wb') as raw:
    with gzip.GzipFile(filename='', mode='wb',fileobj=raw,mtime=0) as gz:
        with tarfile.open(fileobj=gz,mode='w') as tar:
            for name,p in archive_members.items():
                data=p.read_bytes();info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;info.mtime=0
                tar.addfile(info,io.BytesIO(data))
archive_info={n:{'sha256':sha(p),'bytes':p.stat().st_size} for n,p in archive_members.items()}
manifest = {
    'schema_version':1,
    'status':'source_only_integration_ready_for_root_review',
    'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'baseline_git_head':baseline['git_head'],
    'baseline_live_files_checked':len(original),
    'candidate_files':{name:{'sha256':sha(p),'bytes':p.stat().st_size} for name,p in sorted(candidate.items())},
    'changes':changes,
    'archive':{'path':str(archive),'sha256':sha(archive),'members':archive_info},
    'patch':{'path':str(patch_path),'sha256':sha(patch_path),'check_returncode':check.returncode},
    'artifact_bindings':{str(p):sha(p) for p in [BASE/'baseline.json',BASE/'fixture-closure.json',BASE/'math-reuse.json',BASE/'qualified-math-imports.json',BASE/'independent-review.json',BASE/'independent-review-final.json',BASE/'execution-independent-review.json',BASE/'package_source.py',BASE/'patch-check.stdout',BASE/'patch-check.stderr']},
    'public_domain':{'propagators':6,'maximum_rank':3,'powers':[1]*6,'dimension_shift':0,'algorithm':'PassarinoVeltman','invariants':'FromShifts','input_policy':'Preserve','convention':'IregiNative','tensor_weights':'Components','numerical_components':1},
    'production_edits':False,'compiler_or_test_execution':False,'numerical_execution':False,
    'build_qualified':False,'integrated_numerical_qualification':False,'performance_qualified':False,
    'review_limit':'Source-only review and named-function byte identity do not qualify a new build or its numerical behavior.',
}
write('source.json',manifest)
print(json.dumps({'source_json_sha256':sha(BASE/'source.json'),'patch_sha256':sha(patch_path),'changed_files':len(changes),'candidate_files':len(candidate),'archive_members':len(archive_members)}))
