#!/usr/bin/env python3
"""Create this compact capsule from saved bytes only; no producer execution."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import re
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
G = 'target/e6-gh-correlation-repair'
A = 'target/e6-exact-d0-parameter-anchor'
R = 'target/ordinary-gh-parent-requalification'
E = R+'/e6-proposal'
B = 'target/e6-terminal0-precision-trace'
PREFIX = '/shared/external/iregi/iregi-rust/'


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {'sha256':sha(body),'bytes':len(body)}


def main():
    if (HERE/'manifest.json').exists():
        raise FileExistsError('sealed manifest already exists')
    sources = {}
    origins = {}

    def add(alias, origin=None):
        origin = origin or alias
        body = (ROOT/origin).read_bytes()
        if body.startswith((b'\x7fELF',b'!<arch>\n')) or re.search(
                rb'S-[0-9]{3}-[0-9]{4}[.][0-9]{2}[.][0-9]{2}-[A-Z2-7]{20,}',body):
            raise ValueError('compiled product or literal license in payload')
        if alias in sources and sources[alias] != body:
            raise ValueError('conflicting historical alias: '+alias)
        sources[alias] = body
        origins[alias] = origin

    # Small source-stage/controller/protocol history, without cache or ELFs.
    for base in (G,A,E):
        for path in (ROOT/base).iterdir():
            if path.is_file() and path.suffix in ('.py','.rs','.tsv','.md','.patch','.json'):
                add(str(path.relative_to(ROOT)))
    for directory in (G+'/source',G+'/source-v2',G+'/minimal-source',A+'/source',A+'/source-v2'):
        path = ROOT/directory
        if path.exists():
            for item in path.rglob('*'):
                if item.is_file() and '__pycache__' not in item.parts:
                    add(str(item.relative_to(ROOT)))
    receipts = []
    selected_contexts = {}
    omitted = {}
    for base, names in ((G,('build-001','build-002','build-003','build-004','normal-001','diagnostic-001','diagnostic-minimal-001')),
                        (A,('build-001','capture-001')),(R,('build-001',)),(E,('capture-001',)),
                        (B,('build-002','capture-001'))):
        for name in names:
            directory = base+'/'+name
            receipt_alias = directory+'/receipt.json'
            add(receipt_alias)
            receipts.append(receipt_alias)
            receipt = json.loads(sources[receipt_alias])
            for filename in receipt.get('outputs',{}):
                path = ROOT/directory/filename
                if path.is_file() and filename.endswith(('.json','.jsonl','.log','.tsv')):
                    add(directory+'/'+filename)
                else:
                    omitted[PREFIX+directory+'/'+filename] = receipt['outputs'][filename]
            for product in receipt.get('products',{}).values():
                omitted[product['path']] = product['sha256']
            for absolute, digest in receipt.get('inputs',{}).items():
                if any(token in absolute for token in ('/frozen-gh-repair-tests','/frozen-master-regression-tests','/frozen-exact-D0-worker',
                        '/frozen-current-cli','/frozen-current-master-tests','/frozen-e6-diagnostic-tests')):
                    omitted[absolute] = digest
            snapshot = ROOT/directory/'source-snapshot'
            if snapshot.exists():
                selected_contexts[receipt_alias] = {}
                for relative, digest in receipt.get('source_files',{}).items():
                    relevant = relative in ('Cargo.toml','Cargo.lock','crates/iregi-rust/Cargo.toml','crates/iregi-masters/Cargo.toml',
                        'crates/iregi-masters/tests/masters.rs','dependencies/oneloopmaster/Cargo.toml',
                        'dependencies/oneloopmaster/src/box_complex.rs','dependencies/oneloopmaster/src/expressions.rs')
                    relevant |= relative.startswith(('crates/iregi-rust/examples/parameter_oracle/',
                                                     'crates/iregi-rust/examples/e6_exact_d0_anchor/'))
                    if base in (R,B):
                        relevant |= (relative.startswith(('crates/iregi-masters/src/','dependencies/oneloopmaster/'))
                                     and '/generated/' not in relative)
                    if relevant:
                        alias = directory+'/source-snapshot/'+relative
                        add(alias)
                        if sha(sources[alias]) != digest:
                            raise ValueError('immutable selected snapshot differs from actual receipt')
                        selected_contexts[receipt_alias][relative] = alias
    for alias in (A+'/independent-saved-review/check.py', A+'/independent-saved-review/review.json',
                  'target/affine-power-post-memo-current-cli/lifecycle.py',
                  'target/e6-terminal0-precision-trace/early-D0-fixture.json',
                  'target/e6-terminal0-precision-trace/dual-germ-source-audit.md',
                  'target/low-n-complex-rank7-oracle/engineering-v3/python/quadrature.py',
                  'dependencies/oneloopmaster/PATCHES.md',R+'/build.py',R+'/build-protocol.json',
                  B+'/check_trace.py',E+'/capture-001/same-node-comparison.json'):
        add(alias)
    for name in ('receipt.json','check.py','package.py','manifest.json','README.md'):
        add('target/ordinary-complex-box-capsule-packaging/attempt-001/'+name)
    for name in ('receipt.json','check.py'):
        add('target/ordinary-complex-box-capsule-packaging/attempt-002/'+name)
    # Public canonical source aliases refer to the appropriate immutable build,
    # never an unrelated later live-main body.
    for relative in ('dependencies/oneloopmaster/src/box_complex.rs','dependencies/oneloopmaster/src/expressions.rs'):
        add(relative,G+'/build-004/source-snapshot/'+relative)
    for relative in ('crates/iregi-rust/examples/parameter_oracle/kernel.rs',
                     'crates/iregi-rust/examples/parameter_oracle/transport.rs',
                     'crates/iregi-rust/examples/parameter_oracle/kernel_tests.rs',
                     'crates/iregi-rust/examples/parameter_oracle/transport_tests.rs',
                     'crates/iregi-rust/examples/e6_exact_d0_anchor/main.rs',
                     'crates/iregi-rust/examples/e6_exact_d0_anchor/early-D0-input.tsv'):
        add(relative,A+'/build-001/source-snapshot/'+relative)
    # A historical receipt's full dependency/input closure is NOT implied.
    bindings, unrestored = {}, {}
    for alias in receipts:
        receipt = json.loads(sources[alias])
        bindings[alias] = {}
        unrestored[alias] = {}
        for absolute, digest in receipt.get('inputs',{}).items():
            relative = absolute.removeprefix(PREFIX)
            if relative in sources and sha(sources[relative]) == digest:
                bindings[alias][absolute] = relative
            elif absolute in omitted:
                if omitted[absolute] != digest:
                    raise ValueError('omitted artifact identity conflicts')
            else:
                unrestored[alias][absolute] = digest
    objects = {sha(body):body for body in sources.values()}
    archive_bytes = io.BytesIO()
    with gzip.GzipFile(fileobj=archive_bytes,mode='wb',mtime=0) as compressed:
        with tarfile.open(fileobj=compressed,mode='w') as archive:
            for digest,body in sorted(objects.items()):
                info = tarfile.TarInfo('objects/'+digest)
                info.size = len(body)
                info.mode = 0o644
                archive.addfile(info,io.BytesIO(body))
    (HERE/'payload.tar.gz').write_bytes(archive_bytes.getvalue())
    qualification = {
        'ordinary_Symbolica_repair_source_and_regressions':True,
        'one_copied_D0_two_rule_value_anchor':True,
        'one_actual_E6_kernel_convergence':True,
        'E6_or_parent_tensor':False,'new_Dual_domain':False,
        'native_or_generated_backend':False,'Float256_accuracy_certified':False,
        'quadrature_error_bound_certified':False,'performance':False,
    }
    manifest = {
        'schema_version':1,'capsule_directory':str(HERE.relative_to(ROOT)),
        'status':'sealed_ordinary_Symbolica_one_D0_anchor_ten_regressions_and_E6_kernel_convergence',
        'qualification':qualification,
        'capsule_files':{name:desc((HERE/name).read_bytes()) for name in ('README.md','check.py','package.py','payload.tar.gz')},
        'payload_members':{'objects/'+digest:desc(body) for digest,body in sorted(objects.items())},
        'aliases':{alias:{'member':'objects/'+sha(body),**desc(body)} for alias,body in sorted(sources.items())},
        'copy_origins':dict(sorted(origins.items())),
        'receipts':receipts,'selected_source_contexts':selected_contexts,'selected_input_bindings':bindings,
        'unrestored_historical_input_hashes':unrestored,
        'omitted_native_artifacts':dict(sorted(omitted.items())),
        'production_prefix_definition':'box_complex.rs bytes before first newline #[cfg(test)] newline; separator excluded',
        'production_prefix_sha256':sha(sources['dependencies/oneloopmaster/src/box_complex.rs'].split(b'\n#[cfg(test)]\n',1)[0]),
        'explanatory_source_not_claimed_compiled':['dependencies/oneloopmaster/PATCHES.md'],
        'source_scope':'selected relevant immutable actual Cargo inputs, not a full dependency closure/rebuild kit',
        'raw_producer_bytes_modified':False,'native_execution_by_packager':False,
    }
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest_sha256':sha((HERE/'manifest.json').read_bytes()),'aliases':len(sources),
                      'unique_objects':len(objects),'payload_bytes':len(archive_bytes.getvalue()),
                      'omitted_native_identities':len(omitted)}))


if __name__ == '__main__':
    main()
