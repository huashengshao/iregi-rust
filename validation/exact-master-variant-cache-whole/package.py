#!/usr/bin/env python3
"""Freeze terminal WHOLE38 saved evidence; never compile or evaluate integrals."""
from pathlib import Path
import difflib,gzip,hashlib,io,json,re,tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PRIVATE='target/exact-master-variant-cache-whole'
OLD='target/native-f64-sixpoint-port/whole'
CACHE='target/exact-master-variant-cache-proposal'
PARENT='validation/native-f64-sixpoint-whole'
CACHE_PARENT='validation/exact-master-variant-cache'
COMPOSITION='validation/winddown/native-f64-sixpoint-composition.tar.gz'
AUDIT='target/resume-20261025-review/cache-whole-independent-saved-audit'
SUPPLEMENT='target/resume-20261025-review/cache-whole-independent-closure-supplement.json'

def need(x,m):
    if not x:raise ValueError(m)
def digest(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'sha256':digest(b),'bytes':len(b)}
def load(p):return json.loads(Path(p).read_text())
def safe(n):
    p=Path(n);need(bool(n)and not p.is_absolute()and'..'not in p.parts and str(p)==n,'unsafe path')
def allowed(n,b):
    safe(n);need(not b.startswith((b'\x7fELF',b'!<arch>')),'compiled payload')
    need(not re.search(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}',b),'license literal')
def archive(p):
    result={}
    with tarfile.open(p,'r:gz')as f:
        for item in f:
            need(item.isfile()and item.name not in result,'non-file/duplicate archive member')
            b=f.extractfile(item).read();allowed(item.name,b);result[item.name]=b
    return result
def patch(base,observed):
    chunks=[]
    for name in sorted(set(base)|set(observed)):
        if base.get(name)==observed.get(name):continue
        need(name in observed,'unexpected source deletion')
        chunks.extend(difflib.unified_diff(base.get(name,b'').decode().splitlines(keepends=True),observed[name].decode().splitlines(keepends=True),fromfile='a/'+name if name in base else'/dev/null',tofile='b/'+name))
    return ''.join(chunks).encode()

def main():
    need(Path.cwd()==ROOT,'run from project root');need(not(HERE/'manifest.json').exists(),'sealed capsule immutable')
    need(digest((ROOT/PRIVATE/'qualification.json').read_bytes())=='79b526cff3aac6db4d0fea46f76dba40b792d5c9dbae79ece9e2c3cb9b97f793','qualification anchor')
    need(digest((ROOT/(AUDIT+'.json')).read_bytes())=='d9d687f590b8c7ea701bdb4981805e57ff4880b8e30e7a9171f0aa3dec66a51f','independent audit anchor')
    need(digest((ROOT/(AUDIT+'.py')).read_bytes())=='b87120ee996dc189535dc5b8918a29838d172bfb7f6ccc001e9d88e6002ffc69','independent source anchor')
    composition=archive(ROOT/COMPOSITION);old=archive(ROOT/PARENT/'evidence.tar.gz');old_parent=load(ROOT/PARENT/'parent.json')
    for name,item in old_parent['inherited_source_files'].items():
        b=composition[item['parent_member']];need(desc(b)=={k:item[k]for k in['bytes','sha256']},'old inherited source');old.setdefault(name,b)
    cache=archive(ROOT/CACHE_PARENT/'payload.tar.gz');source=json.loads(cache[CACHE+'/source-proposal.json'])
    base={n:composition['proposed/'+n]for n in source['base_files']};candidate=dict(base)
    for n in source['changed_files']:candidate[n]=cache[CACHE+'/proposed/'+n]
    need({n:desc(b)for n,b in base.items()}==source['base_files'],'base85')
    need({n:desc(b)for n,b in candidate.items()}==source['proposed_files'],'cache88')
    old_source={n[len('source/candidate/'):]:b for n,b in old.items()if n.startswith('source/candidate/')}
    prep=load(ROOT/PRIVATE/'preparation.json')
    need({n:digest(b)for n,b in old_source.items()}==prep['overlay_source_mapping']['baseline'],'old86')
    new_source={str(p.relative_to(ROOT/PRIVATE/'source/candidate')):p.read_bytes()for p in sorted((ROOT/PRIVATE/'source/candidate').rglob('*'))if p.is_file()}
    need({n:digest(b)for n,b in new_source.items()}==prep['overlay_source_mapping']['candidate'],'new89')
    payload={};aliases={};current={};omitted={}
    for path in sorted((ROOT/PRIVATE).rglob('*')):
        need(not path.is_symlink(),'symlink evidence')
        if not path.is_file():continue
        name=str(path.relative_to(ROOT));local=str(path.relative_to(ROOT/PRIVATE))
        if '__pycache__'in path.parts or path.suffix in['.pyc','.pyo']:
            omitted[name]={'reason':'generated Python bytecode','bytes':path.stat().st_size};continue
        with path.open('rb')as f:start=f.read(8)
        if start.startswith((b'\x7fELF',b'!<arch>')):
            with path.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
            omitted[name]={'reason':'compiled product; saved digest evidence only','sha256':sha,'bytes':path.stat().st_size};continue
        b=path.read_bytes();allowed(name,b);current[name]=b
        if local.startswith('source/candidate/'):
            aliases[name]={'kind':'observed','member':local[len('source/candidate/'):]}
        elif old.get(local)==b:aliases[name]={'kind':'old_whole','member':local}
        else:payload[name]=b
    for suffix in['.json','.py']:
        name=AUDIT+suffix;payload[name]=(ROOT/name).read_bytes();current[name]=payload[name]
    payload[SUPPLEMENT]=(ROOT/SUPPLEMENT).read_bytes();current[SUPPLEMENT]=payload[SUPPLEMENT]
    payload['source-patches/baseline85-to-observed86.patch']=patch(base,old_source)
    payload['source-patches/cache88-to-observed89.patch']=patch(candidate,new_source)
    tar=io.BytesIO()
    with tarfile.open(fileobj=tar,mode='w',format=tarfile.PAX_FORMAT)as f:
        for n,b in sorted(payload.items()):
            allowed(n,b);item=tarfile.TarInfo(n);item.size=len(b);item.mode=0o644;item.mtime=0;f.addfile(item,io.BytesIO(b))
    (HERE/'payload.tar.gz').write_bytes(gzip.compress(tar.getvalue(),compresslevel=9,mtime=0))
    (HERE/'qualification.json').write_bytes(current[PRIVATE+'/qualification.json'])
    (HERE/'independent-saved-audit.json').write_bytes(current[AUDIT+'.json'])
    borrowed=[COMPOSITION,'validation/winddown/manifest.json',PARENT+'/manifest.json',PARENT+'/parent.json',PARENT+'/evidence.tar.gz',PARENT+'/qualification.json',CACHE_PARENT+'/manifest.json',CACHE_PARENT+'/payload.tar.gz',CACHE_PARENT+'/qualification.json',CACHE_PARENT+'/cache-test-qualification.json','validation/native-master-replay/inputs.json']
    own={str(p.relative_to(HERE)):desc(p.read_bytes())for p in sorted(HERE.rglob('*'))if p.is_file()and'__pycache__'not in p.parts}
    for n in own:allowed(n,(HERE/n).read_bytes())
    manifest={'schema_version':1,'status':'sealed_private_native_policy85_cache88_whole38_preservation',
        'files':own,'borrowed_inputs':{n:desc((ROOT/n).read_bytes())for n in borrowed},
        'payload_archive':{'path':'payload.tar.gz','members':{n:desc(b)for n,b in payload.items()}},
        'source_aliases':aliases,'reconstructed_private_files':{n:desc(b)for n,b in current.items()},
        'source_snapshots':{'base85':{n:desc(b)for n,b in base.items()},'cache88':{n:desc(b)for n,b in candidate.items()},'observed_baseline86':{n:desc(b)for n,b in old_source.items()},'observed_cache89':{n:desc(b)for n,b in new_source.items()}},
        'omitted_private_files':omitted,'counts':{'new_private_noncompiled_files':len(current),'payload_members':len(payload),'compiled_product_instances_omitted':4,'python_cache_instances_omitted':5,'requests':38,'raw_entries':76,'tensor_slots_per_engine':1584,'master_slots_per_engine':1782},
        'parent_source_policy':'Exact committed native-WHOLE and shared-cache capsules plus composition parent; source patches mechanically reconstruct observed86 from base85 and observed89 from cache88.',
        'native_guard_policy':'Reconstructed/borrowed guarded bytes are checked; omitted native products, unbundled tool/dependency inputs and historical process absence remain saved attestations, not fresh native requalification.',
        'ordinary_metadata_exception':'Only structural plan_reused is removed by the documented ordinary canonicalization.',
        'control_metadata_exception':'Only the historical top-level baseline requested policy label is rebound; every control value/sign/precision/error/route remains exact.',
        'baseline_n7less':True,'current_cargo_qualified':False,'production_adoption':False,'full_typed_dual_qualified':False,'public_dual_qualified':False,'derivative_uncertainty_transport_qualified':False,'performance_qualified':False,
        'no_compiler_integral_reference_profile_or_benchmark_executed_by_packaging':True,
        'commands':['python3 validation/exact-master-variant-cache-whole/check.py','python3 validation/exact-master-variant-cache-whole/check.py --reconstruct target/exact-master-cache-whole-restored']}
    need(sum('sha256'in v for v in omitted.values())==4 and len(omitted)==9,'compiled/bytecode omissions')
    with(HERE/'manifest.json').open('x')as f:json.dump(manifest,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'status':'sealed','manifest_sha256':digest((HERE/'manifest.json').read_bytes()),'archive_bytes':(HERE/'payload.tar.gz').stat().st_size,'payload_members':len(payload),'reconstructed_private_files':len(current)}))

if __name__=='__main__':main()
