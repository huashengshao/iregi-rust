"""Freeze a reviewable finite catalogue. Does not compile or evaluate anything."""
import ast,hashlib,json,shutil,tarfile
from pathlib import Path
ROOT=Path.cwd().resolve();HERE=Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    destination=HERE/'catalog.json'
    if destination.exists():raise ValueError('preserve frozen catalogue; explicitly archive any source-only supersession')
    p=json.loads((HERE/'catalog-draft.json').read_text())
    p.pop('native_jobs_authorized',None);p['execution_requires_root_grant']=True;p['status']='frozen_finite_catalog_requires_exact_root_grant_and_independent_review'
    tools={name:str(Path(shutil.which(command)).resolve())for name,command in [('cargo','cargo'),('rustc','rustc'),('taskset','taskset'),('python','python3')]}
    p['tools']=tools;p['build']['kind']='build'
    p['build']['command']=[tools.get(arg.strip('{}'),arg)for arg in p['build']['command']]
    source_files=['fixture.json','oracle.py','ORACLE.md','compare_saved.py','run.py','lifecycle.py','prepare.py','catalog-draft.json','README.md','COMPARISON.md']
    bindings={str(HERE/name):sha(HERE/name)for name in source_files}
    for path in tools.values():bindings[path]=sha(path)
    quadrature=ROOT/'validation/shifted-pentagon/adjudicate.py';bindings[str(quadrature)]=sha(quadrature)
    archive=ROOT/'validation/public-rank7-current-cargo-n1-n5/sources.tar.gz';bindings[str(archive)]=sha(archive)
    with tarfile.open(archive,'r:gz')as stream:names=[member.name for member in stream if member.isfile()]
    names+=['crates/iregi-rust/src/dispatch.rs','crates/iregi-rust/examples/certified_planar_scalar.rs',
        'validation/reference/fixtures.json','validation/reference/snapping/reductions.json','validation/pv-high-rank/lightlike-feynman-parameters.json',
        'dependencies/symbolica/src/evaluate/tree.rs','dependencies/symbolica/src/evaluate.rs','dependencies/symbolica/Cargo.toml']
    p['live_build_source_bindings']={str(ROOT/name):sha(ROOT/name)for name in sorted(set(names))}
    p['bindings']=bindings
    p['source_guard_scope']='Current root/core/master/facade/example plus compile fixtures and three relevant Symbolica source/manifest leaves, snapshot before build and guarded until artifact freeze only; no full compiler/dependency closure. Captures guard frozen snapshot/artifact, not subsequently mutable main.'
    p['native_artifact_storage']='One retained readonly frozen actualCargo example plus readonly same-inode per-job aliases; hashes guarded on both, no independent byte-copy claim. Native contents omitted from portable output replay and future source archives.'
    for path in HERE.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
    destination.write_text(json.dumps(p,indent=2)+'\n')
    print(json.dumps({'catalog_sha256':sha(destination),'common_bindings':len(bindings),'live_build_source_files':len(p['live_build_source_bindings']),'jobs':len(p['jobs']),'new_native_jobs':0}))
if __name__=='__main__':main()
