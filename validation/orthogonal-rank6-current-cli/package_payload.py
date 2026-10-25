#!/usr/bin/env python3
"""Package only missing saved byte aliases over two fixed portable parents.

No native binaries are read; no producers, compilers, integral evaluators,
PID/process functions or Git are called. Parent restore_files is the admitted
stdlib saved-data restore API. All writes stay under this capsule's _work.
"""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile

sys.dont_write_bytecode=True
WORK=Path('validation/orthogonal-rank6-current-cli/_work')
PRIVATE=Path('target/orthogonal-rank6-current-cli')
PARENTS=[('validation/n6-rank6-generalized-current-cli',
          'aa6af6c5a40f012331b17b21aa4c338a38c55789e59109fb8b8aabc1b24d19f1',
          'fd9634b1cd949bbfccfd3a58295813d61ed5b5d535b59ece1f0c1848c459532d'),
         ('validation/complex-parameter-tensor-oracle',
          'e6c801800b8edfd4f7b63e3573134dd5a1153f2e87b379584aac24d17d22e604',
          '0b0fc79417c66352e5724388a392d298863d2859a36094922dd85911ffb97207')]
LITERAL=re.compile(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z0-9]{25,}')
COMPILED_MAGIC={'ELF':b'\x7fELF','PE_DOS':b'MZ','MachO64le':b'\xcf\xfa\xed\xfe',
 'MachO32le':b'\xce\xfa\xed\xfe','MachO64be':b'\xfe\xed\xfa\xcf','MachO32be':b'\xfe\xed\xfa\xce',
 'ar':b'!<arch>\n','WebAssembly':b'\0asm','ZIP':b'PK\x03\x04'}
NATIVE_NAMES={'owned-executable','frozen-example','cli-frozen','frozen-tests'}

def require(ok,message):
    if not ok:raise ValueError(message)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(raw):return {'sha256':sha(raw),'bytes':len(raw)}

def safe(alias):
    path=PurePosixPath(alias)
    require(alias and not path.is_absolute() and '..' not in path.parts and str(path)==alias,'safe original alias')

def load(path):return json.loads(Path(path).read_bytes())

def parents_restore():
    files={};providers={};summary=[];identical_overlaps=0
    for index,(root,pin,checker_pin) in enumerate(PARENTS):
        path=Path(root);manifest=(path/'manifest.json').read_bytes();checker=(path/'check.py').read_bytes()
        require(sha(manifest)==pin and sha(checker)==checker_pin,'fixed parent checker/manifest identity')
        spec=importlib.util.spec_from_file_location('orthogonal_package_parent_'+str(index),path/'check.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        restored=module.restore_files(json.loads(manifest))
        for alias,raw in restored.items():
            safe(alias)
            if alias in files:
                require(files[alias]==raw,'inherited alias conflict '+alias);identical_overlaps+=1
            else:files[alias]=raw
            providers.setdefault(alias,[]).append(root)
        summary.append({'capsule_directory':root,'manifest_sha256':pin,'check_sha256':checker_pin,
                        'restored_aliases':len(restored),'restored_alias_bytes':sum(map(len,restored.values()))})
    return files,providers,summary,identical_overlaps

def required_parent_files():
    """Recursive fixed capsule-file closure, without following external guards."""
    files={};visited=set();topological=[]
    def add(path,expected=None):
        name=str(path);safe(name)
        raw=path.read_bytes();actual=desc(raw)
        require(expected is None or actual==expected,'fixed parent file identity '+name)
        require(name not in files or files[name]==actual,'parent required file conflict '+name)
        files[name]=actual
    def visit(manifest_path):
        name=str(manifest_path)
        if name in visited:return
        visited.add(name);add(manifest_path);manifest=load(manifest_path)
        for alias,expected in manifest.get('parent_files',{}).items():
            safe(alias);add(Path(alias),expected)
            if Path(alias).name=='manifest.json':visit(Path(alias))
        for alias,expected in manifest['capsule_files'].items():
            safe(alias);add(manifest_path.parent/alias,expected)
        topological.append({'capsule_directory':str(manifest_path.parent),'manifest_sha256':files[name]['sha256']})
    for root,_,_ in PARENTS:visit(Path(root)/'manifest.json')
    return dict(sorted(files.items())),topological

def archive_write(destination,members):
    with gzip.GzipFile(filename='',fileobj=destination,mode='wb',mtime=0,compresslevel=9) as compressed:
        with tarfile.open(fileobj=compressed,mode='w',format=tarfile.PAX_FORMAT) as archive:
            for entry,raw in members:
                info=tarfile.TarInfo(entry['alias']);info.size=len(raw);info.mode=0o644
                info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
                archive.addfile(info,io.BytesIO(raw))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualification',type=Path,required=True)
    parser.add_argument('--qualification-sha256',required=True)
    args=parser.parse_args()
    require(args.qualification.is_relative_to(PRIVATE),'final qualification must be inside exact admitted target root')
    require(sha(args.qualification.read_bytes())==args.qualification_sha256,'parent final qualification pin')
    for name in ['payload.tar.gz','origins.json','content-scan.json']:
        require(not (WORK/name).exists(),'preserve prior prepared capsule '+name)
    inherited,providers,parent_roots,overlap=parents_restore()
    parent_files,topological=required_parent_files()
    independent_path=PRIVATE/'independent/review.json';independent=load(independent_path)
    require(sha(independent_path.read_bytes())=='a1522bc7aee97d0425e93397b147ad8a278662b954fbc1ca749aa9f1785ad8a0',
            'fixed independent saved review receipt')
    require(len(independent['checked_aliases'])==86,'exact independent saved byte-read set')
    selected={};omitted=[]
    for path in sorted(PRIVATE.rglob('*')):
        require(not path.is_symlink(),'no evidence symlink '+str(path))
        if not path.is_file():continue
        if path.name in NATIVE_NAMES:
            # No native path currently lives in this root; reject unexpected
            # products until their saved attestation is explicitly inventoried.
            raise ValueError('unexpected compiled native path; do not open '+str(path))
        if '__pycache__' in path.parts or path.suffix=='.pyc':
            omitted.append({'path':str(path),'reason':'compiled Python cache omitted','bytes':path.stat().st_size,
                            'sha256':None,'native_bytes_rehashed':False});continue
        selected[str(path)]=path
    for alias,expected in independent['checked_aliases'].items():
        safe(alias)
        if alias in inherited:
            require(desc(inherited[alias])==expected,'independent alias supplied by fixed parent '+alias)
        else:selected[alias]=Path(alias)
    members=[];requested_inherited={};license_hits=0;magic_hits=0;source_bytes=0
    for alias,path in sorted(selected.items()):
        safe(alias);require(not path.is_symlink() and path.stat().st_size<40_000_000,'safe saved evidence file '+alias)
        raw=path.read_bytes()
        if alias in independent['checked_aliases']:
            require(desc(raw)==independent['checked_aliases'][alias],'independent checked byte identity '+alias)
        if alias in inherited:
            require(inherited[alias]==raw,'own/parent alias conflict '+alias)
            requested_inherited[alias]={**desc(raw),'parent_source_alias':alias,'whichparent':providers[alias]};continue
        require(not any(raw.startswith(prefix) for prefix in COMPILED_MAGIC.values()),'compiled file magic excluded '+alias)
        require(LITERAL.search(raw) is None,'literal Symbolica license excluded '+alias)
        raw.decode('utf-8')
        members.append(({'alias':alias,'source_path':str(path.resolve()),**desc(raw)},raw))
        source_bytes+=len(raw)
    for alias,expected in independent['checked_aliases'].items():
        if alias in inherited:requested_inherited[alias]={**expected,'parent_source_alias':alias,'whichparent':providers[alias]}
    own={entry['alias']:raw for entry,raw in members}
    require(str(args.qualification) in own,'final qualification retained as an own payload member')
    require(all(alias in own or alias in inherited for alias in independent['checked_aliases']),'closed independent replay aliases')
    # The source snapshot/build and admitted complex parameter oracle must be
    # inherited unchanged, without a new live source or compiled artifact read.
    snapshot_prefix='target/n6-rank6-generalized-current-cli/build-001/source-snapshot/'
    snapshot=[alias for alias in inherited if alias.startswith(snapshot_prefix)]
    require(len(snapshot)==77 and not any(alias.startswith(snapshot_prefix) for alias in own),'exact inherited77-file snapshot')
    require('target/low-n-complex-rank7-oracle/quadrature-proposal/anchor-admission.json' in inherited,
            'inherited independent complex admission')
    payload=WORK/'payload.tar.gz'
    with payload.open('xb') as destination:archive_write(destination,members)
    with tarfile.open(payload,'r:gz') as archive:
        observed=[]
        for member in archive:
            safe(member.name);require(member.isfile(),'regular payload files only')
            raw=archive.extractfile(member).read();require(own[member.name]==raw,'payload byte roundtrip')
            require(member.mode==0o644 and member.uid==member.gid==member.mtime==0,'deterministic metadata')
            observed.append(member.name)
    require(observed==list(own),'exact sorted archive inventory')
    rebuilt=io.BytesIO();archive_write(rebuilt,members)
    require(rebuilt.getvalue()==payload.read_bytes(),'independent deterministic second archive build')
    # Saved native binary digest from protocol/receipt only. Do not touch the
    # binary path named by these historical attestations.
    protocol=load(PRIVATE/'protocol.json');capture=load(PRIVATE/'capture-001/receipt.json')
    native={'path':protocol['binary'],'sha256':protocol['binary_sha256'],
            'build_receipt_path':protocol['build_receipt'],'build_receipt_sha256':protocol['build_receipt_sha256'],
            'basis':'immutable protocol and inherited build receipt attestations only; native bytes not opened or rehashed'}
    origins={'schema_version':1,'status':'deterministic_saved_orthogonal_rank6_overlay_prepared',
      'scope':'Own missing saved evidence bytes over two fixed parent maps; all14cases and two failed collinear arrays preserved. No later native/source qualification.',
      'payload':{'path':str(payload),'sha256':sha(payload.read_bytes()),'bytes':payload.stat().st_size,
                 'member_count':len(members),'uncompressed_member_bytes':source_bytes,
                 'format':'sorted original-project-relative aliases; regular pax tar0644 uidgidmtime0; gzip filenameempty mtime0 compression9'},
      'members':[entry for entry,raw in members],
      'inherited_aliases':[{'alias':alias,**row} for alias,row in sorted(requested_inherited.items())],
      'parent_roots':parent_roots,'parent_files':parent_files,'parent_capsules_topological_order':topological,
      'parent_union':{'alias_count':len(inherited),'alias_bytes':sum(map(len,inherited.values())),
                      'identical_overlap_aliases':overlap,'conflicting_aliases':[]},
      'parent_inherited77_snapshot_aliases':snapshot,
      'independent_checked_aliases':independent['checked_aliases'],
      'final_qualification':{'path':str(args.qualification),'sha256':args.qualification_sha256},
      'omitted':omitted,'historical_native_attestations':[native],
      'external_tool_master_compiler_closure_imported':False,
      'literal_symbolica_license_included':False,'all_own_member_bytes_utf8':True,
      'old_N4_stable_zero_reference_rejected':True,'order32_N4_parameter_oracle_admitted':True,
      'overall_failed_cohort_and_two_collinear_failures_preserved':True,
      'package_source_sha256':sha(Path(__file__).read_bytes()),
      'activity':{'native_binary_bytes_opened_or_rehashed':False,'producer_imports':False,'compiler_or_integral_jobs':False,
                  'PID_operations':False,'Git_operations':False,'production_edits':False,
                  'parent_stdlib_saved_restore_API_used':True}}
    origins_path=WORK/'origins.json'
    with origins_path.open('x') as output:json.dump(origins,output,indent=2,sort_keys=True);output.write('\n')
    content={'status':'passed_saved_overlay_archive_content_and_determinism_scan','members_checked':len(members),
       'payload_sha256':sha(payload.read_bytes()),'origins_sha256':sha(origins_path.read_bytes()),
       'compiled_magic_families_checked':list(COMPILED_MAGIC),'compiled_magic_hits':0,
       'literal_Symbolica_license_token_hits':0,'matching_bytes_printed':False,'all_member_bytes_UTF8':True,
       'second_archive_build_byte_identical':True,'native_bytes_opened_or_rehashed':False}
    with (WORK/'content-scan.json').open('x') as output:json.dump(content,output,indent=2,sort_keys=True);output.write('\n')
    print(json.dumps({'status':origins['status'],'payload':origins['payload'],
        'origins_sha256':sha(origins_path.read_bytes()),'contentscan_sha256':sha((WORK/'content-scan.json').read_bytes()),
        'required_parent_files':len(parent_files),'requested_inherited_aliases':len(requested_inherited),
        'own_files':len(members),'inherited_union_aliases':len(inherited)},sort_keys=True))

if __name__=='__main__':main()
