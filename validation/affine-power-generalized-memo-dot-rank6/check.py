#!/usr/bin/env python3
"""Replay saved public N6 mixed-Dual PV evidence; Python standard library only."""
from pathlib import Path, PurePosixPath
import hashlib
import importlib.util
import io
import json
import sys
import tarfile
import types
import re

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = 'validation/checked-g-generalized-core-tests'
PARENT_HASH = 'ee4bc172dd8b87e3242158afacab425e6b13376f72dd3fbb6678feb701a97417'
PREFIX = '/shared/external/iregi/iregi-rust/'
PRIVATE = 'target/n6-affine-facade-dual-probe-v1'
BUILD = 'target/affine-power-observed-quadrature-proposal/build-001'
AUDITOR = PRIVATE + '/independent_saved_audit_v1.py'
AUDITOR_HASH = 'eda59c1b5486ac611856ff551aef78b1bfc75449c3ad338949f2519f0e564c0c'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return dict(sha256=sha(body), bytes=len(body))


def load(body):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(body, object_pairs_hook=unique)


def safe(name):
    p = PurePosixPath(name)
    require(name and not p.is_absolute() and '..' not in p.parts and str(p) == name,
            'safe project-relative identity')


def restore_files(manifest):
    """Return immutable project-relative bytes, including the pinned parent."""
    own = {str(p.relative_to(HERE)) for p in HERE.rglob('*')
           if p.is_file() and '__pycache__' not in p.parts}
    require(own == set(manifest['capsule_files']) | {'manifest.json'}, 'closed capsule files')
    for name, expected in manifest['capsule_files'].items():
        safe(name)
        require(desc((HERE / name).read_bytes()) == expected, 'exact capsule bytes: ' + name)
    for name, expected in manifest['parent_files'].items():
        safe(name)
        require(desc((ROOT / name).read_bytes()) == expected, 'exact parent bytes: ' + name)
    raw = (ROOT / PARENT / 'manifest.json').read_bytes()
    require(sha(raw) == manifest['parent_manifest_sha256'] == PARENT_HASH, 'fixed affine-power parent')
    spec = importlib.util.spec_from_file_location('public_n6_dual_saved_parent', ROOT / PARENT / 'check.py')
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    files = parent.restore_files(parent.load(raw))
    members = {}
    with tarfile.open(fileobj=io.BytesIO((HERE / 'payload.tar.gz').read_bytes()), mode='r:gz') as archive:
        for item in archive:
            safe(item.name)
            require(item.isfile() and item.name not in members, 'unique regular archive member')
            body = archive.extractfile(item).read()
            require(desc(body) == manifest['payload_members'].get(item.name), 'exact archived bytes')
            require(not body.startswith((b'\x7fELF', b'!<arch>\n')) and not re.search(rb'S-[0-9]{3}-[0-9]{4}[.][0-9]{2}[.][0-9]{2}-[A-Z2-7]{20,}', body),
                    'no compiled product or literal license')
            members[item.name] = body
    require(set(members) == set(manifest['payload_members']), 'closed archive inventory')
    for alias, row in manifest['aliases'].items():
        safe(alias)
        require(len(set(row) & {'member', 'parent_alias'}) == 1, 'one archived byte selector')
        body = members[row['member']] if 'member' in row else files[row['parent_alias']]
        require(desc(body) == {key: row[key] for key in ('sha256', 'bytes')}, 'exact saved alias')
        require(alias not in files or files[alias] == body, 'no parent alias overwrite')
        files[alias] = body
    for name in own:
        files[manifest['capsule_directory'] + '/' + name] = (HERE / name).read_bytes()
    return files


BASE = 'target/affine-power-post-memo-current-cli'

def replay(files, manifest):
    read = lambda alias: load(files[alias])
    require(manifest['full_precision_cohort_qualified'] is False and manifest['performance_qualified'] is False,
            'partial cohort never promoted by portable replay')
    q = load((HERE/'qualification.json').read_bytes())
    require(q['Float128_native_reference_slots_qualified'] == 840
            and q['Float256_native_reference_slots_qualified'] == q['precision_pairs_qualified'] == 0
            and q['full_precision_cohort_qualified'] is False, 'honest scoped acceptance')
    protocol = read(BASE+'/protocol.json')
    require(sha(files[BASE+'/protocol.json']) == '48c71eaee8ea5d3da316a8c89b8347d04e3c0dfac84f9e24a2f381e7ca1b2903'
            and protocol['cli_sha256'] == '0b28ce2428f7719da1acf9eee9584365d2a6bf62f83ee63db950d30b2b0bc58d',
            'same root-released actualCLI003 context')
    for bits in (128, 256):
        directory = BASE+f'/captures/Float{bits}-001'
        r = read(directory+'/receipt.json')
        require(r['inputs_unchanged'] is True and r['cleanup_errors'] == []
                and r['cancellation'] is None and r['post_cancellation'] is None,
                'saved unchanged capture inputs and clean owned termination')
        require((r['total_seconds'],r['native_child_cap_seconds'],r['cleanup_reserve_seconds'],r['cpu'],r['address_space_limit_bytes']) == (2580,2400,120,16,None),
                'unchanged finite engineering bounds without address-space acceptance cap')
        for absolute, digest in r['inputs'].items():
            if absolute in manifest['omitted_native_inputs']:
                require(digest == manifest['omitted_native_inputs'][absolute], 'explicit omitted executable metadata')
            else:
                alias=absolute.removeprefix(PREFIX)
                require(alias in files and sha(files[alias]) == digest, 'available exact capture input '+alias)
        for name,digest in r['outputs'].items():
            require(sha(files[directory+'/'+name]) == digest, 'unchanged raw saved capture output')
        require(len(r['steps']) == 1 and r['steps'][0]['owned_group_gone'] is True,
                'one historical owned group and successful saved cleanup')
    auditor_alias=BASE+'/independent_saved_audit.py'
    require(sha(files[auditor_alias]) == '36ebefe4f12a9af60be18cd37877892de18630a4793d4f141480f96ea75d9911',
            'unchanged independent complete-array saved checker')
    auditor=types.ModuleType('frozen_partial_dot_independent_arithmetic')
    exec(compile(files[auditor_alias],'<frozen saved arithmetic>','exec'),auditor.__dict__)
    actual=auditor.audit_saved(lambda alias:files[alias],128,False)
    saved=read(BASE+'/audit-attempts/Float128-direct-001.json')
    require(actual == {k:v for k,v in saved.items() if k != 'checker_sha256'},
            'all1935independent checks exactly replay from saved values')
    require(actual['status'] == 'passed_independent_saved_first_dot_audit'
            and actual['counts'] == {'quad_reference_slots':840,'IR_zero_slots':420,'UV_zero_slots':210,'precision_pairs':0}
            and actual['failures'] == [], 'complete scoped Float128 reference and pole controls')
    directory=BASE+'/captures/Float256-001';r=read(directory+'/receipt.json');d=read(directory+'/stdout.json')
    require(sha(files[directory+'/receipt.json']) == '3671d809732aef26c205b9ea71df1861e62249d34a7915f816c124180cd67584'
            and r['status'] == 'failed_or_incomplete' and r['steps'][0]['returncode'] == 1
            and not r['steps'][0].get('timeout',False), 'actual256numericfailure,not timeout or fabricated success')
    require(d['precision_bits'] == 256 and d['settings'] == read(BASE+'/captures/Float128-001/stdout.json')['settings']
            and len(d['samples']) == 1 and d['samples'][0]['status'] == 'failed'
            and 'moments' not in d['samples'][0], 'failed upper precision exposes no parent tensor coefficients')
    e=d['engine_execution']
    require(e['engine']=='AffinePower' and e['parent_batch_calls']==e['parent_rows']==e['quadrature_work_rows']==0
            and e['packed_child_rows']==7 and e['child_batch_calls']==2
            and [m['actual']for m in e['child_methods']]==['Ibp','PassarinoVeltman'],
            'actual dotted IBP and documented unit PV completion retained; failed parent not executed')
    require(e['child_execution']['pentagon_box_rows']==2440
            and any('NonConvergent' in line and '2.3794e-4' in line and '128' in line for line in d['diagnostics'][0]),
            'actual E6 nonconvergence diagnostics retained')
    require(directory+'/comparison.json' not in files and directory+'/pair-comparison.json' not in files,
            'no unavailable upper comparison or precision pair')
    negative=manifest['prior_failed_capture'];old=read(negative+'/receipt.json')
    require(old['status'] in ['failed','failed_or_incomplete'] and old['inputs_unchanged'] is True
            and old['cleanup_errors']==[] and old['steps'][0]['owned_group_gone'] is True
            and files[negative+'/stdout.json']==b'', 'earlier810s preparation failure and empty array retained')
    failure=read(BASE+'/failure-metadata-audit-attempts/attempt-001.json')
    require(failure['status']=='passed_saved_failure_metadata_and_partial_cohort_audit'
            and failure['checks']==974 and failure['full_precision_cohort_qualified'] is False,
            'independent terminal-failure review retained without relabeling acceptance')
    return {'status':'passed_portable_incomplete_N6_rank6_first_dot_saved_replay',
            'restored_aliases':len(files),'inherited_source_bodies':158,'inherited_strict_core_tests':120,
            'Float128_reference_slots':840,'Float128_pole_controls':630,'Float128_independent_checks':actual['checks'],
            'maximum_Float128_reference_error':q['Float128_maximum_normalized_reference_error'],
            'Float256_reference_slots':0,'precision_pairs':0,'full_precision_cohort_qualified':False,
            'preserved_failures':['prior810s preparation timeout','Float256 E6NonConvergent'],
            'native_or_compiler_or_live_PID_execution':False,'performance_qualified':False}

if __name__=='__main__':
    manifest=load((HERE/'manifest.json').read_bytes())
    result=replay(restore_files(manifest),manifest)
    result['manifest_sha256']=sha((HERE/'manifest.json').read_bytes())
    print(json.dumps(result,indent=2))
