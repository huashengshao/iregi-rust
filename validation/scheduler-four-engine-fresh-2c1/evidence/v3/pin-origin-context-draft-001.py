"""Pin live provenance origins to their committed bytes, not active build inputs.

This performs only Git blob reads, hashes and protocol preparation. All actual
private source/compiler/archive inputs remain guarded. No compiler is launched.
"""
from pathlib import Path
import copy, hashlib, json, shutil, subprocess, sys
ROOT=Path('/shared/external/iregi/iregi-rust')
HERE=ROOT/'target/guard-performance-review/optimized-performance-proposal/v3'
PIN='2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2'
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def main():
    assert Path.cwd()==ROOT and not(HERE/'build-001').exists()
    path=HERE/'protocol.json'
    assert sha(path)=='32166bee3cb21e6cd7c1536766f940c78a54ee102ad065657c3c7395d974d19a'
    old=json.loads(path.read_text())
    origins={name:value for name,value in old['protected_sha256'].items()
        if name.startswith(('crates/','dependencies/'))or name in ['Cargo.toml','Cargo.lock','AGENTS.md','PLAN.md']}
    assert len(origins)==257
    request=''.join(PIN+':'+name+'\n'for name in origins)
    result=subprocess.run(['git','cat-file','--batch'],input=request.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,check=True)
    raw=result.stdout;position=0
    for name,expected in origins.items():
        end=raw.index(b'\n',position);header=raw[position:end].decode();fields=header.rsplit(' ',2)
        assert fields[0]==PIN+':'+name and fields[1]=='blob',header
        size=int(fields[2]);body=raw[end+1:end+1+size]
        assert hashlib.sha256(body).hexdigest()==expected,'Pinned Git origin differs: '+name
        position=end+1+size
        assert raw[position:position+1]==b'\n';position+=1
    assert position==len(raw)
    # Verify that none of the actual observed archive/metadata proof bindings is
    # being removed. This distinction is also checked by independent review.
    from provenance import binding_requirements
    proof=json.loads(Path(old['proof']).read_text())
    actual=set(binding_requirements(proof))
    assert not actual.intersection(str(ROOT/name)for name in origins)
    previous=HERE/'protocol-with-live-origins.json'
    assert not previous.exists();shutil.copyfile(path,previous)
    context={'scope':'Committed provenance origins only; not active compiler inputs. Actual compilation uses frozen private source copies and explicit target/Nix archives.',
        'git_revision':PIN,'file_count':len(origins),'pinned_file_sha256':origins,
        'all_hashes_verified_against_git_blobs':True,
        'original_guarded_current_context':'Original first compiler stage and initial continuation preparation matched these live files before any production integration.',
        'future_label':'Pinned2c1f334 source cohort in inherited frozen optimized lower dependency context; not necessarily latest production main after integration.',
        'actual_compiler_inputs_still_guarded':True,'no_compiler_or_integral_executed':True}
    context_path=HERE/'pinned-origin-context.json';save(context_path,context)
    new=copy.deepcopy(old)
    for name in origins:del new['protected_sha256'][name]
    for item in [previous,context_path,Path(__file__),HERE.parent/'reviews/v3-continuation-independent-source-review.json']:
        new['protected_sha256'][str(item.relative_to(ROOT))]=sha(item)
    new['scope']='Pinned2c1f334 source cohort; '+old['scope']
    new['pinned_origin_context']=str(context_path)
    new['pinned_origin_context_sha256']=sha(context_path)
    new['pinned_source_revision']=PIN
    new['live_origin_files_are_not_active_guards']=True
    new['prior_reviewed_protocol_sha256']=sha(previous)
    new['source_review_required_for_origin_decoupling']=True
    save(path,new)
    assert new['steps']==old['steps']
    print(json.dumps({'protocol_sha256':sha(path),'active_guards':len(new['protected_sha256']),
        'pinned_origin_files':len(origins),'all_compiler_commands_unchanged':True,'no_compiler_or_integral_executed':True}))
if __name__=='__main__':main()
