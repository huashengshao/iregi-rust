#!/usr/bin/env python3
"""Deterministic packaging of terminal evidence; no producer or compiler calls."""
from pathlib import Path
import gzip,hashlib,importlib.util,io,json,sys,tarfile,time
sys.dont_write_bytecode=True
ROOT=Path.cwd().resolve();HERE=ROOT/'validation/checked-g-generalized-numeric';Q=ROOT/'target/checked-g-generalized-numeric'
def main():
    deadline=json.loads((Q/'packaging-deadline.json').read_text())['deadline_monotonic']
    def remaining():
        if time.monotonic()>deadline-30:raise TimeoutError('finite packaging work budget exhausted')
    remaining();spec=importlib.util.spec_from_file_location('checked_g_numeric_packaging_checker',HERE/'check.py');check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
    parent=ROOT/check.PARENT;raw=(parent/'manifest.json').read_bytes();check.need(check.sha(raw)==check.PARENT_HASH,'frozen parent')
    spec=importlib.util.spec_from_file_location('checked_g_core_packaging_parent',parent/'check.py');central=importlib.util.module_from_spec(spec);spec.loader.exec_module(central);pm=central.load(raw);inherited=central.restore_files(pm);remaining()
    inventory=json.loads((Q/'capsule-inventory.json').read_text());check.need(inventory['missing_aliases']==[],'closed inventory')
    aliases={};origins={};omitted={};objects={}
    rows=list(inventory['aliases'])
    for p in[Q/'qualification.json',Q/'capsule-inventory.json']:
        alias=str(p.relative_to(ROOT))
        if not any(r['alias']==alias for r in rows):rows.append(dict(alias=alias,sha256=check.sha(p.read_bytes()),classification='own_raw_file_alias'))
    for row in rows:
        remaining();alias=row['alias'];expected=row['sha256'];kind=row['classification']
        if kind=='omitted_native_artifact_hash':omitted[alias]=expected;continue
        if kind=='inherited_parent_alias':
            source=row['parent_alias'];body=inherited[source];check.need(check.sha(body)==expected,'inherited bytes '+alias);selector={'parent_alias':source}
        else:
            body=(ROOT/alias).read_bytes();check.need(check.sha(body)==expected,'owned bytes '+alias);check.scan(alias,body);member='objects/'+expected;objects[member]=body;selector={'member':member}
        aliases[alias]={**selector,**check.desc(body)};origins[alias]={**check.desc(body),'origin':'central_parent'if'parent_alias'in selector else'owned_terminal_evidence'}
    archive=io.BytesIO()
    with gzip.GzipFile(fileobj=archive,mode='wb',mtime=0)as compressed:
        with tarfile.open(fileobj=compressed,mode='w')as tar:
            for member,body in sorted(objects.items()):
                info=tarfile.TarInfo(member);info.size=len(body);info.mode=0o644;info.mtime=0;tar.addfile(info,io.BytesIO(body))
    (HERE/'payload.tar.gz').write_bytes(archive.getvalue());(HERE/'payload-origins.json').write_text(json.dumps(origins,indent=2)+'\n');(HERE/'qualification.json').write_bytes((Q/'qualification.json').read_bytes());remaining()
    files=['README.md','check.py','package.py','qualification.json','payload.tar.gz','payload-origins.json']
    manifest={'schema_version':1,'capsule_directory':'validation/checked-g-generalized-numeric','parent_manifest_sha256':check.PARENT_HASH,'parent_files':{str(p.relative_to(ROOT)):check.desc(p.read_bytes())for p in sorted(parent.iterdir())if p.is_file()},'capsule_files':{f:check.desc((HERE/f).read_bytes())for f in files},'payload_members':{name:check.desc(body)for name,body in sorted(objects.items())},'aliases':dict(sorted(aliases.items())),'omitted_native_artifacts':dict(sorted(omitted.items())),'inherited_compiled_sources':{name:{'parent_alias':row['alias'],'snapshot_alias':row['snapshot_alias'],'sha256':row['sha256'],'bytes':row['bytes']}for name,row in pm['compiled_sources'].items()},'own_compiled_sources':{},'qualification_sha256':check.QUAL,'numeric_records':5040,'original_quad_records':3360,'working_pair_records':1680,'own_source_bodies':0,'nested_compound_proof_counters_observable':False,'scope':'fixed checked-G N6R6 h0 defaultHybrid massive unit/firstdot Float128/256, accuracy53, one sample/user component','performance_qualified':False,'public_Dual_qualified':False,'full_domain_qualified':False,'native_execution_by_packager':False,'build_execution_by_packager':False}
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');remaining();print(json.dumps({'manifest_sha256':check.sha((HERE/'manifest.json').read_bytes()),'payload_sha256':check.sha(archive.getvalue()),'payload_bytes':len(archive.getvalue()),'aliases':len(aliases),'owned_members':len(objects),'inherited_compiled_sources':158,'remaining_seconds':deadline-time.monotonic()}))
if __name__=='__main__':main()
