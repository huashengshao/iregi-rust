#!/usr/bin/env python3
"""Seal finalized D2 partial evidence: Float128 pass plus Float256 stability failure."""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=Path.cwd().resolve()
LOW='target/affine-power-post-memo-current-d2'
HIGH='target/affine-power-post-memo-current-d2-pair'
PARENT='validation/checked-g-generalized-core-tests'
PARENT_SHA='ee4bc172dd8b87e3242158afacab425e6b13376f72dd3fbb6678feb701a97417'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--review',required=True,help='Project-relative finalized independent failure review alias')
    parser.add_argument('--review-sha256',required=True)
    parser.add_argument('--review-source',action='append',default=[],help='Additional independent audit source aliases')
    args=parser.parse_args()
    if ROOT!=Path('/shared/external/iregi/iregi-rust'):raise ValueError('run from project root')
    own={name:(HERE/name).read_bytes()for name in ['check.py','package.py','README.md']}
    spec=importlib.util.spec_from_file_location('d2_partial_own_portable_checker',HERE/'check.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    need,sha,desc,load=checker.need,checker.sha,checker.desc,checker.parse
    output=args.output.resolve();need(output.is_relative_to(ROOT)and not output.exists(),'fresh project-local destination')
    parent_dir=ROOT/PARENT
    pm_raw=(parent_dir/'manifest.json').read_bytes();need(sha(pm_raw)==PARENT_SHA,'frozen source parent')
    pm=load(pm_raw)
    for name,witness in pm['capsule_files'].items():
        need(desc((parent_dir/name).read_bytes())==witness,'parent file before checker import '+name)
    spec=importlib.util.spec_from_file_location('d2_partial_source_parent_checker',parent_dir/'check.py')
    parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
    inherited=parent.restore_files(pm)
    parent.replay(inherited,pm)
    parent_files={PARENT+'/'+p.name:desc(p.read_bytes())for p in parent_dir.iterdir()if p.is_file()}
    need(len(parent_files)==7,'exact seven-file source parent')
    files={};borrowed={};omitted={};before={}
    def add(name,expected=None):
        checker.safe(name)
        path=ROOT/name;need(path.is_file()and not path.is_symlink(),'regular saved alias '+name)
        raw=path.read_bytes();checker.scan(name,raw)
        need(expected is None or sha(raw)==expected,'exact saved artifact '+name)
        need(name not in files or files[name]==raw,'same-alias byte collision')
        files[name]=raw;before[name]=desc(raw);return raw
    # Terminal admission occurs BEFORE any enumeration of the newer capture.
    low_r=load(add(LOW+'/captures/Float128-001/receipt.json',checker.LOW_RECEIPT))
    high_raw=add(HIGH+'/captures/Float256-001/receipt.json');high_r=load(high_raw)
    need(low_r['status']=='passed_complete_840_native_coefficients'and low_r['working_bits']==128,'original128 terminal pass')
    need(sha(high_raw)==checker.HIGH_RECEIPT and high_r['status']=='failed_or_incomplete'and high_r['working_bits']==256,'actual256 terminal failure')
    for r in [low_r,high_r]:
        need(r['inputs_unchanged']is True and not r['cleanup_errors']and r['cancellation']is None and r['post_cancellation']is None,'both actual terminals have complete postguards/cleanup')
    review=load(add(args.review,args.review_sha256))
    need(str(review.get('status','')).startswith('passed')and review.get('findings')==[], 'independent failure audit must pass')
    review_pins=set(checker.strings(review))
    need(checker.HIGH_PROTOCOL in review_pins and sha(high_raw)in review_pins,'review must bind exact new protocol/actual receipt')
    for name in args.review_source:add(name)
    # Preserve the unexecuted passing-pair draft as source history only.
    for name in ['check.py','package.py','README.md','PLAN.md','source-status.json']:
        add('target/d2-pair-capsule-preparation/'+name)
    protocols={}
    for prefix,bits,expected in[(LOW,128,checker.LOW_PROTOCOL),(HIGH,256,checker.HIGH_PROTOCOL)]:
        protocol=load(add(prefix+'/protocol.json',expected));protocols[bits]=protocol
        for path in (ROOT/prefix).iterdir():
            if path.is_file()and path.suffix in['.json','.py','.txt','.stdout']:
                add(str(path.relative_to(ROOT)))
        folder=ROOT/prefix/'captures'/('Float'+str(bits)+'-001')
        for path in folder.rglob('*'):
            if not path.is_file()or'__pycache__'in path.parts:continue
            if path.name=='cli-owned':
                omitted[str(path.relative_to(ROOT))]=checker.CLI;continue
            need(path.suffix not in['.partial','.tmp'],'partial capture output cannot seal')
            add(str(path.relative_to(ROOT)))
        omitted[checker.alias(protocol['cli'])]=checker.CLI
    # Only the original D2 raw/request and existing scoped admission metadata;
    # no duplicate original-reference executable/source archive is copied.
    for name in['anchor-admission.json','anchor-index.json','independent-saved-review.json','protocol.json']:
        add('target/n6-rank6-generalized-quad/'+name)
    add('target/n6-rank6-generalized-quad/requests/n6_rank6_unit_D2.txt','0d148e3eee18fd977778baa144617ab8081d236f2f8233f820e7899c738b5429')
    add('target/n6-rank6-generalized-quad/capture-001/request-5.stdout',checker.REFERENCE)
    need(load(files[LOW+'/independent-saved-audit.json'])['status']=='passed_independent_saved_D2_Float128_audit','old independent audit preserved')
    # No physical compiled artifact is read by this package operation.
    build=inherited['target/checked-g-generalized-qualification/build-003/receipt.json']
    need(load(build)['products']['cli']['sha256']==checker.CLI,'metadata-only omitted CLI/source coupling')
    omitted.update({name:digest for name,digest in pm['omitted_compiled_products'].items()
                    if name.endswith('/build-003/frozen-cli')})
    # Preserve same-alias inherited objects once through the central parent.
    for name in list(files):
        if name in inherited:
            need(files[name]==inherited[name],'inherited alias byte equality')
            borrowed[name]=desc(files.pop(name))
    members={};preserved={}
    for name,raw in sorted(files.items()):
        member='objects/'+sha(raw)
        need(member not in members or members[member]==raw,'content-address collision')
        members[member]=raw;preserved[name]={'member':member,**desc(raw)}
    buffer=io.BytesIO()
    with gzip.GzipFile(fileobj=buffer,filename='',mode='wb',mtime=0)as gz:
        with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT)as archive:
            for name,raw in sorted(members.items()):
                entry=tarfile.TarInfo(name);entry.size=len(raw);entry.mode=0o644;entry.mtime=0;entry.uid=entry.gid=0;entry.uname=entry.gname=''
                archive.addfile(entry,io.BytesIO(raw))
    capsule={**own,'payload.tar.gz':buffer.getvalue()}
    manifest={'schema_version':1,'status':'source_bound_saved_D2_Float128_pass_Float256_failure',
        'parent_files':parent_files,'parent_manifest_sha256':PARENT_SHA,
        'capsule_files':{name:desc(raw)for name,raw in capsule.items()},
        'payload_members':{name:desc(raw)for name,raw in members.items()},'preserved_files':preserved,'borrowed_files':borrowed,
        'source_epoch':'CLI003-pre-Gh-repair-source158','compiled_source_count':158,'compiled_source_parent_context':'build-003',
        'cli_sha256':checker.CLI,'omitted_compiled_products':omitted,
        'high_receipt_sha256':sha(high_raw),'independent_failure_review':{'path':args.review,'sha256':args.review_sha256},
        'current_main_equality_claimed':False,'new_native_hash_or_process_probe':False,
        'source_and_process_provenance_historical':True,'D6_hold':True,
        'performance_qualified':False,'public_Dual_qualified':False,'finite_reference_independently_certified':False,
        'Float256_qualified':False,'precision_pair_qualified':False}
    combined=dict(inherited);combined.update(files)
    replay=checker.replay(combined,manifest,pm)
    manifest['saved_replay_counts']={k:replay[k]for k in ['Float128_reference_slots_passed','Float256_reference_slots_run','precision_pairs_run','Float256_reference_slots_unrun','precision_pairs_unrun']}
    # Recheck every admitted saved input after replay; do not seal a drifted file.
    for name,witness in before.items():need(desc((ROOT/name).read_bytes())==witness,'postguard byte drift '+name)
    need((parent_dir/'manifest.json').read_bytes()==pm_raw,'parent manifest postguard')
    for name,witness in parent_files.items():need(desc((ROOT/name).read_bytes())==witness,'parent byte postguard')
    for name,value in own.items():need((HERE/name).read_bytes()==value,'own source postguard '+name)
    output.mkdir(parents=True)
    for name,raw in capsule.items():(output/name).write_bytes(raw)
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':'sealed_saved_D2_partial_evidence','directory':str(output),'manifest_sha256':sha((output/'manifest.json').read_bytes()),
        'own_aliases':len(preserved),'own_objects':len(members),'borrowed_aliases':len(borrowed),'parent_source_bodies_reused':158,
        'native_products_omitted':len(omitted),'replay':replay},indent=2))
if __name__=='__main__':main()
