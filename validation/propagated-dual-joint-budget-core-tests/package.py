#!/usr/bin/env python3
"""Seal explicitly named saved evidence only; never runs a native producer."""
import gzip, io, json, sys, tarfile
from pathlib import Path
sys.dont_write_bytecode = True
import check as c

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def encoded(value): return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()

def main():
    parent=HERE.parent/c.PARENT
    pb=(parent/'manifest.json').read_bytes()
    c.need(c.sha(pb)==c.PARENT_SHA,'fixed sibling byte-source parent')
    pm=c.load(pb)
    archive=(parent/'payload.tar.gz').read_bytes()
    c.need(c.desc(archive)==pm['capsule_files']['payload.tar.gz'],'fixed parent payload')
    by_hash={d['sha256']:(name,d) for name,d in pm['payload_members'].items()}
    preserved={};local={};contexts={};products={}

    def add(alias, physical=None, expected=None):
        c.safe(alias)
        if alias in preserved:
            c.need(expected is None or preserved[alias]['sha256']==expected,'unambiguous saved alias '+alias)
            return
        if expected in by_hash:
            member,d=by_hash[expected];row=dict(store='parent',member=member,**d)
        else:
            path=physical or ROOT/alias
            c.need(path.is_file() and not path.is_symlink(),'explicit regular saved input '+alias)
            body=path.read_bytes();c.scan(alias,body);d=c.desc(body)
            c.need(expected is None or d['sha256']==expected,'pinned saved input '+alias)
            if d['sha256'] in by_hash:
                member,pd=by_hash[d['sha256']];c.need(d==pd,'parent content-size identity')
                row=dict(store='parent',member=member,**d)
            else:
                member='objects/'+d['sha256'];local[member]=body;row=dict(store='self',member=member,**d)
        preserved[alias]=row

    q=ROOT/c.Q
    # Small, explicit observer/release/source histories. No compiled products.
    direct=['README.md','application.json','base-sources.json','build.py','build_v2.py','build_v3.py',
            'build-runner.delta.patch','candidate.patch','execution-recipe.json','execution-release.json',
            'functional-qualification.json','independent-root-review.json','independent-source-review-v1.json',
            'native-hold.json','numeric-plan.md','proposal.json','qualification-plan.json','review-admission.json',
            'review-research.md','run_tests.py','run_tests_v2.py','run_tests_v3.py','source-delta.json',
            'source-delta-v2.json','source-delta-v3.json','source-mechanics.json','test-selection.json']
    for name in direct:add(c.Q+'/'+name)
    fixes=['before.rs','after.rs','after-v3.rs','candidate.patch','change.json',
           'arc-ownership-change.json','arc-ownership-fix.patch']
    for name in fixes:add(c.Q+'/narrow-fallback-fixture-fix/'+name)
    original=c.load((q/'source-delta.json').read_bytes())
    for path,row in original['subjects'].items():
        if row['base_sha256'] is not None:add(c.Q+'/base/'+path,expected=row['base_sha256'])
        add(c.Q+'/candidate/'+path,expected=row['candidate_sha256'])

    builds={}
    for name,expected in c.BUILD.items():
        alias=c.Q+'/'+name+'/receipt.json';add(alias,expected=expected)
        b=c.load((ROOT/alias).read_bytes());builds[name]=b
        contexts[name]=dict(receipt_sha256=expected,source_files=b['source_files'])
        snapshot=q/name/'source-snapshot'
        for path,digest in b['source_files'].items():
            add(c.Q+'/'+name+'/source-snapshot/'+path,snapshot/path,digest)
        for product in b['products'].values():
            products[product['path'].removeprefix(c.PREFIX)]=product['sha256']
        for path,digest in b['outputs'].items():
            alias=c.Q+'/'+name+'/'+path
            if alias not in products:add(alias,expected=digest)
        for path,digest in b['inputs'].items():
            alias=path.removeprefix(c.PREFIX)
            c.need(alias!=path,'project-relative historical build input')
            if alias in products or alias in b['source_files']:continue
            add(alias,expected=digest)

    for name,expected in c.TEST.items():
        alias=c.Q+'/'+name+'/receipt.json';add(alias,expected=expected)
        r=c.load((ROOT/alias).read_bytes())
        for output,digest in r['outputs'].items():add(c.Q+'/'+name+'/'+output,expected=digest)
        for path,digest in r['inputs'].items():
            alias=path.removeprefix(c.PREFIX)
            c.need(alias!=path,'project-relative historical test input')
            if alias not in products:add(alias,expected=digest)

    inherited={row['member'] for row in preserved.values() if row['store']=='parent'}
    manifest=dict(schema_version=1,scope='source_build_and_15_strict_core_tests_only',
                  parent_files={f'../{c.PARENT}/manifest.json':c.desc(pb),
                                f'../{c.PARENT}/payload.tar.gz':c.desc(archive)},
                  parent_used_members={k:pm['payload_members'][k] for k in sorted(inherited)},
                  preserved_files=dict(sorted(preserved.items())),
                  payload_members={k:c.desc(v) for k,v in sorted(local.items())},
                  source_contexts=contexts,omitted_compiled_products=products)
    parent_values=c.selected_archive(archive,pm['payload_members'],inherited,False)
    files={alias:(local if row['store']=='self' else parent_values)[row['member']]
           for alias,row in preserved.items()}
    qualification=c.replay(files,manifest)
    (HERE/'qualification.json').write_bytes(encoded(qualification))
    raw=io.BytesIO()
    with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0,compresslevel=9) as gz:
        with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT) as tf:
            for name,body in sorted(local.items()):
                entry=tarfile.TarInfo(name);entry.size=len(body);entry.mode=0o644
                entry.uid=entry.gid=entry.mtime=0;entry.uname=entry.gname=''
                tf.addfile(entry,io.BytesIO(body))
    (HERE/'payload.tar.gz').write_bytes(raw.getvalue())
    manifest['capsule_files']={name:c.desc((HERE/name).read_bytes()) for name in
                               ['README.md','check.py','package.py','qualification.json','payload.tar.gz']}
    (HERE/'manifest.json').write_bytes(encoded(manifest))
    c.need(c.verify(HERE)==qualification,'first saved replay agrees')
    print(json.dumps(dict(status='passed_saved_seal',manifest_sha256=c.sha((HERE/'manifest.json').read_bytes()),
                          preserved_aliases=len(preserved),local_objects=len(local),inherited_objects=len(inherited),
                          payload_bytes=len(raw.getvalue()),qualification=qualification),indent=2))

if __name__=='__main__':main()
