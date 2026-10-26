"""Small draft payload helper for the parent; deliberately does not seal a capsule.

The parent supplies its final checker/qualification and restores only the pinned
central seven-file parent. No quad-parent restore, mathematical replay, process
probe, compiler, native artifact read, or live source read occurs here.
"""
from pathlib import Path
import gzip,hashlib,io,json,re,tarfile

def draft_payload(root:Path,destination:Path,central_files:dict[str,bytes]):
    """Return manifest fragments after writing only an owned, deduplicated payload.

    destination must be a new preparation directory, chosen by the parent.
    central_files is the already restored exact central-parent alias dictionary.
    This function is not executed by this helper task.
    """
    here=root/'target/checked-g-zero-mass-capsule-prep'
    source=json.loads((here/'source-inventory.json').read_text())
    evidence=json.loads((here/'evidence-inventory.json').read_text())
    reference=json.loads((here/'reference-source-plan.json').read_text())
    supplement=json.loads((here/'terminal-supplement.json').read_text())
    assert source['parent_manifest_sha256']=='ee4bc172dd8b87e3242158afacab425e6b13376f72dd3fbb6678feb701a97417'
    assert evidence['scale_001_terminal_release_received'] is True
    objects={};aliases={};origins={}
    def digest(body):return hashlib.sha256(body).hexdigest()
    def safe(alias,body):
        p=Path(alias);assert not p.is_absolute()and '..'not in p.parts
        assert p.suffix not in{'.so','.a','.o','.mod','.smod','.pyc','.dll','.dylib'}and '__pycache__'not in p.parts
        assert p.name not in{'frozen-tests','frozen-cli','iregi-reference-quad-generalized'}
        assert not body.startswith((b'\x7fELF',b'!<arch>',b'MZ'))
        assert not re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}',body)
    def put(alias,expected,parent_alias=None,source_alias=None):
        body=central_files[parent_alias]if parent_alias is not None else(root/(source_alias or alias)).read_bytes()
        safe(alias,body);assert digest(body)==expected
        selector={'parent_alias':parent_alias}if parent_alias is not None else{'member':'objects/'+expected}
        if parent_alias is None:objects[selector['member']]=body
        row={**selector,'sha256':expected,'bytes':len(body)}
        assert alias not in aliases or aliases[alias]==row
        aliases[alias]=row;origins[alias]={'sha256':expected,'bytes':len(body),'origin':'central_parent'if parent_alias is not None else'owned_terminal_source_or_evidence'}
    for alias,row in source['source_aliases'].items():
        put(alias,row['sha256'],row.get('parent_alias'),row.get('source_alias'))
    # Canonical names describe actual build004 bodies, never current live files.
    anchor=source['source_contexts']['build-004']
    for name,expected in anchor['source_files'].items():
        snapshot='target/checked-g-zero-mass-fallback-qualification/build-004/source-snapshot/'+name
        row=source['source_aliases'][snapshot];put(name,expected,row.get('parent_alias'),snapshot)
    # Own narrow reference provenance; deliberately do not traverse quad parents.
    for row in evidence['aliases']+reference['aliases']+supplement['aliases']:
        alias=row['alias'];expected=row['sha256']
        if alias in central_files and digest(central_files[alias])==expected:put(alias,expected,alias)
        else:put(alias,expected)
    for extra_name in ['PLAN.md','source-inventory.json','evidence-inventory.json','reference-source-plan.json','terminal-supplement.json']:
        extra_alias='target/checked-g-zero-mass-capsule-prep/'+extra_name
        put(extra_alias,digest((root/extra_alias).read_bytes()))
    destination.mkdir(parents=True,exist_ok=False)
    archive=io.BytesIO()
    with gzip.GzipFile(fileobj=archive,mode='wb',mtime=0)as stream:
        with tarfile.open(fileobj=stream,mode='w')as tar:
            for member,body in sorted(objects.items()):
                info=tarfile.TarInfo(member);info.size=len(body);info.mode=0o644;info.mtime=0;tar.addfile(info,io.BytesIO(body))
    (destination/'payload.tar.gz').write_bytes(archive.getvalue())
    (destination/'payload-origins.json').write_text(json.dumps(origins,indent=2)+'\n')
    qualification=supplement['aliases'][0]
    raw_qualification=(root/qualification['alias']).read_bytes()
    assert digest(raw_qualification)==qualification['sha256']
    (destination/'qualification.json').write_bytes(raw_qualification)
    fragment={'aliases':aliases,'payload_members':{name:{'sha256':digest(body),'bytes':len(body)}for name,body in objects.items()},'source_contexts':source['source_contexts'],'anchor_source_context':'build-004','actual_anchor_source_count':161,'distinct_source_versions':166,'central_borrowed_source_bodies':147,'own_source_overlay_bodies':19,'published_quad_manifest_sha256':reference['published_quad_manifest_sha256'],'quad_deep_parent_restore_or_replay':False,'hermetic_reference_build_closure_claimed':False,'seal_performed':False}
    (destination/'draft-fragments.json').write_text(json.dumps(fragment,indent=2)+'\n')
    return fragment
