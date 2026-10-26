#!/usr/bin/env python3
"""Saved-only generalized N6 replay. No producer imports or execution."""
from contextlib import redirect_stdout, chdir
from pathlib import Path, PurePosixPath
import hashlib
import importlib.util
import io
import json
import re
import sys
import tarfile
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = 'validation/ordinary-complex-box-correlation'
PARENT_SHA = 'aec684253e59a73944b1e5a8e58c6b385bf9a81d5acf17f81643f6eec3aed2e0'
R = 'target/ordinary-gh-parent-requalification'
P = R+'/parent-proposal'
I = R+'/independent-parent-saved-review'
PREFIX = '/shared/external/iregi/iregi-rust/'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {'sha256':sha(body),'bytes':len(body)}


def load(body):
    def unique(pairs):
        out = {}
        for key,value in pairs:
            require(key not in out,'duplicate JSON key')
            out[key] = value
        return out
    return json.loads(body,object_pairs_hook=unique)


def safe(name):
    p = PurePosixPath(name)
    require(name and not p.is_absolute() and '..' not in p.parts and str(p)==name,'canonical relative alias')


def module(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def restore_files(manifest):
    own = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    require(own==set(manifest['capsule_files'])|{'manifest.json'},'closed child capsule')
    for name,expected in manifest['capsule_files'].items():
        safe(name)
        require(desc((HERE/name).read_bytes())==expected,'exact child file')
    for name,expected in manifest['parent_files'].items():
        safe(name)
        require(desc((ROOT/name).read_bytes())==expected,'exact shallow parent file')
    raw = (ROOT/PARENT/'manifest.json').read_bytes()
    require(sha(raw)==manifest['parent_manifest_sha256']==PARENT_SHA,'pinned ordinary-box parent')
    parent = module('ordinary_gh_scalar_saved_parent',ROOT/PARENT/'check.py')
    files = parent.restore_files(parent.load(raw))
    members = {}
    with tarfile.open(fileobj=io.BytesIO((HERE/'payload.tar.gz').read_bytes()),mode='r:gz') as archive:
        for item in archive:
            safe(item.name)
            require(item.isfile() and item.name not in members,'unique regular object')
            body = archive.extractfile(item).read()
            require(desc(body)==manifest['payload_members'].get(item.name) and item.name=='objects/'+sha(body),'exact addressed object')
            require(not body.startswith((b'\x7fELF',b'!<arch>\n')) and not re.search(
                rb'S-[0-9]{3}-[0-9]{4}[.][0-9]{2}[.][0-9]{2}-[A-Z2-7]{20,}',body),'no compiled products or license literal')
            members[item.name] = body
    require(set(members)==set(manifest['payload_members']),'closed object archive')
    for alias,row in manifest['aliases'].items():
        safe(alias)
        require(len(set(row)&{'member','parent_alias'})==1,'one byte selector')
        body = members[row['member']] if 'member' in row else files[row['parent_alias']]
        require(desc(body)=={k:row[k] for k in ('sha256','bytes')},'exact source/data alias')
        require(alias not in files or files[alias]==body,'no parent-byte overwrite')
        files[alias] = body
    require(set(members)=={r['member'] for r in manifest['aliases'].values() if 'member' in r},'no unreferenced own object')
    for name in own:
        files[manifest['capsule_directory']+'/'+name] = (HERE/name).read_bytes()
    return files


def logical(value,temporary_root):
    """Retain original comparator path keys while replaying a relocated tree."""
    if isinstance(value,str):
        return value.replace(str(temporary_root),PREFIX.rstrip('/'))
    if isinstance(value,list):
        return [logical(v,temporary_root) for v in value]
    if isinstance(value,dict):
        return {logical(k,temporary_root):logical(v,temporary_root) for k,v in value.items()}
    return value


def replay(files,manifest):
    read = lambda name:load(files[name])
    require(manifest['first_dot_owner_terminal_notice_sha256']==sha(files[P+'/captures/first_dot-Float256-001/receipt.json']),
            'explicit terminal notice binds final first-dot receipt')
    built = read(R+'/build-001/receipt.json')
    require(sha(files[R+'/build-001/receipt.json'])=='faa4ea0e4ea4029a8e61dbdbb02c5324f985793008e4cdc3aec1d8341fa64845'
            and built['status']=='passed' and built['products']['cli']['sha256']=='7005b0966709525945f7e1b330b4a3b23b6b63ccfb1faf3566f893dfe8ac5890'
            and built['inputs_unchanged'] is True and built['cleanup_errors']==[]
            and all(s['returncode']==0 and s['owned_group_gone'] is True for s in built['steps']),
            'actual fresh Cargo CLI identity')
    event = read(R+'/build-001/'+built['products']['cli']['cargo_event'])
    require(event['reason']=='compiler-artifact' and event['executable']==built['products']['cli']['cargo_executable'],
            'actual Cargo emitted artifact, omitted executable is historical identity only')
    require(len(built['source_files'])==len(manifest['fresh_source_aliases'])==128,'all128actual fresh frozen source inputs exposed')
    for relative,alias in manifest['fresh_source_aliases'].items():
        require(sha(files[alias])==built['source_files'][relative],'exact128source context for future inheritance')
    copy = read(P+'/copy-provenance.json')
    for row in copy['copies']:
        require(sha(files[row['copy']])==row['sha256'] and files[row['source']]==files[row['copy']], 'small preserved prior/reference copy')
    require(sha(files[I+'/check.py'])=='1ce0418b7a5c7e8ead69f7e341415ecbdd4f4a12b12df763e35c5c7920725ff2',
            'unchanged independent saved Fraction checker')
    require(sha(files[I+'/D2-review.json'])=='a41c895df2ba9c1c48e5702f88a5320e320e49d6be51c1974fee6d1784dbe318'
            and sha(files[I+'/first_dot-review.json'])=='4ea40f590bcb8cadd11c298ed0c89b5902766f732d85f98b9e51154ad5f63c71',
            'the two exact terminal independent reviews admitted by owner')
    old_alias = 'target/affine-power-post-memo-current-d2-pair/captures/Float256-001'
    old = read(old_alias+'/receipt.json')
    old_output = read(old_alias+'/stdout.json')
    require(sha(files[old_alias+'/receipt.json'])=='f4e9f3fd7ac1f7fa6fd675c2d0a10d69ebda8d9d70c21e5be0659463a6e817f0'
            and sha(files[old_alias+'/stdout.json'])=='2a7c9154293f445c09ca96fcf5a2c4b8c123047888ffba62b76440ed27e63040'
            and old['outputs']['stdout.json']==old['stdout_sha256']==sha(files[old_alias+'/stdout.json'])
            and old['status']=='failed_or_incomplete' and old_output['samples'][0]['status']=='failed'
            and 'moments' not in old_output['samples'][0]
            and 'NonConvergent' in old_output['samples'][0]['reason'], 'oldD2actual failure retained without parent arrays')
    cases = {}
    with tempfile.TemporaryDirectory(prefix='ordinary-gh-n6-saved-') as tmp:
        root = Path(tmp)
        for alias,body in files.items():
            path = root/alias
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(body)
        independent = module('ordinary_gh_independent_saved_parent',root/I/'check.py')
        for case in ('D2','first_dot'):
            directory = P+'/captures/'+case+'-Float256-001'
            receipt = read(directory+'/receipt.json')
            require(receipt.get('finished_utc') and receipt['case']==case,'owner terminal receipt before arrays')
            require(receipt['same_source_precision_convergence_qualified'] is False
                    and receipt['comparison_scope']=='CROSS-SOURCE old Float128 versus current Float256','honest cross-source semantics')
            for name,digest in receipt.get('outputs',{}).items():
                require(sha(files[directory+'/'+name])==digest,'immutable terminal raw output')
            for absolute,alias in manifest['selected_input_bindings'][case].items():
                require(sha(files[alias])==receipt['inputs'][absolute],'unchanged selected capture input')
            successful = receipt['status']=='passed_current256_quad_and_CROSS_SOURCE_840_pairs'
            if not successful:
                # Raw failures remain hashed evidence. Never parse an incomplete
                # stdout tensor or call successful-array comparators here.
                cases[case] = {'owner_status':receipt['status'],'qualified':False,
                               'error':receipt.get('error'),'array_comparison_replayed':False,
                               'saved_cleanup_errors':receipt.get('cleanup_errors'),
                               'inputs_unchanged':receipt.get('inputs_unchanged')}
                continue
            require(receipt['inputs_unchanged'] is True and receipt['cleanup_errors']==[] and receipt['cancellation'] is None
                    and receipt['post_cancellation'] is None and all(s['returncode']==0 and s['owned_group_gone'] is True for s in receipt['steps']),
                    'successful saved lifecycle joins')
            sample_path = root/P/'cases'/case/'input.json'
            sample = load(sample_path.read_bytes())
            comparator = module('ordinary_gh_saved_'+case,root/P/'cases'/case/'compare_saved.py')
            original_sha = comparator.sha
            def restored_sha(path, original=original_sha):
                text = str(path)
                return original(root/text.removeprefix(PREFIX) if text.startswith(PREFIX) else path)
            # D2's metadata-only reference admission uses cwd plus a captured
            # absolute request name. Redirect only file lookup, keeping every
            # hashed byte and all comparator arithmetic unchanged.
            comparator.sha = restored_sha
            for bits,path in ((128,root/P/'prior-128'/case/'stdout.json'),(256,root/directory/'stdout.json')):
                with chdir(root):
                    result = comparator.audit(path,root/P/'cases'/case/'reference.stdout',sample,bits)
                require(result==load(path.with_name('comparison.json').read_bytes()) and result['failures']==[],
                        'complete original840reference and630pole gates at eachprecision')
            pair = module('ordinary_gh_saved_pair_'+case,root/P/'cases'/case/'compare_pair.py')
            paired = pair.audit_pair(root/P/'prior-128'/case/'stdout.json',root/directory/'stdout.json',sample)
            require(logical(paired,root)==read(directory+'/pair-raw.json') and paired['failures']==[],'exact strict840pair replay')
            cross = read(directory+'/cross-source-comparison.json')
            require(cross['status']=='passed_complete_840_CROSS_SOURCE_pairs'
                    and cross['raw_comparator_status']==paired['status']
                    and cross['same_source_precision_convergence_qualified'] is False
                    and cross['current_build_receipt_sha256']==sha(files[R+'/build-001/receipt.json']), 'pair not relabeled same-source convergence')
            paths = {'receipt':root/directory/'receipt.json','current':root/directory/'stdout.json',
                     'prior':root/P/'prior-128'/case/'stdout.json','prior_receipt':root/P/'prior-128'/case/'receipt.json',
                     'sample':sample_path,'reference':root/P/'cases'/case/'reference.stdout','protocol':root/P/'protocol.json'}
            independent_result = independent.audit(case,paths)
            saved_review = read(I+'/'+case+'-review.json')
            require(saved_review['checker_source_sha256']==sha(files[I+'/check.py'])
                    and saved_review['authorized_receipt_sha256']==sha(files[directory+'/receipt.json']),
                    'two owner-added independent report provenance bindings')
            require(independent_result=={k:v for k,v in saved_review.items() if k not in ('checker_source_sha256','authorized_receipt_sha256')}
                    and independent_result['status']=='passed_saved_original_and_CROSS_SOURCE_gates', 'full independent Fraction checker API replay')
            cases[case] = {'owner_status':receipt['status'],'qualified':True,'reference_slots_each_precision':840,
                           'cross_source_slots':840,'independent_groups':independent_result['counts_and_results'],
                           'actual_contexts':independent_result['actual_contexts']}
    require({case:row['qualified'] for case,row in cases.items()}==manifest['case_qualified'],'honest final outcome inventory')
    return {'status':'passed_portable_saved_generalized_N6_integrity_replay','cases':cases,'restored_aliases':len(files),
            'fresh_source_bodies':128,'same_source_precision_convergence_qualified':False,'full_domain_qualified':False,
            'native_backend_qualified':False,'performance_qualified':False,'D6_qualified':False,
            'old_D2_Float256_failure_preserved':True,'reference_hash_lookup_relocated_to_saved_aliases':True,
            'compiler_or_integral_producer_or_live_process_probe_executed':False}


if __name__=='__main__':
    manifest = load((HERE/'manifest.json').read_bytes())
    result = replay(restore_files(manifest),manifest)
    result['manifest_sha256'] = sha((HERE/'manifest.json').read_bytes())
    print(json.dumps(result,indent=2))
