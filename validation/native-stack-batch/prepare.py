from pathlib import Path
import hashlib, json, shutil, re
root=Path.cwd(); base=root/'target/native-stack-batch'; deps=base/'deps'; deps.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
archives={}
for name in ['liboneloop-8562c3cbbf948c0e.rlib','libsymbolica-5cca42ee48491872.rlib','libiregi_masters-0d5459afd211649c.rlib']:
 src=root/'target/stack-reuse-current-workspace/deps'/name; dst=deps/name
 if not dst.exists():shutil.copy2(src,dst)
 assert sha(src)==sha(dst)
 archives[str(dst.relative_to(root))]=sha(dst)
for fam in ['c0','d0']:
 target=base/fam; target.mkdir(exist_ok=True)
 for name in [f'{fam}_baseline.rs',f'{fam}_candidate.rs','constants.rs']:
  shutil.copy2(root/'target/stack-reuse-production'/f'actual-{fam}'/name,target/name)
 (target/'module.rs').write_text('''use oneloop::rust_codegen::runtime::{BatchWorkspace, C, ConstantSpec, Context, NativeFloat, batch, primitives};
#[allow(unused_assignments,dead_code)] mod baseline { include!("'''+fam+'''_baseline.rs"); }
#[allow(unused_assignments,dead_code)] mod candidate { include!("'''+fam+'''_candidate.rs"); }
mod constants { include!("constants.rs"); }
pub fn context<T:NativeFloat>(prototype:&T)->Context<T>{Context::new(constants::CONSTANTS,prototype.get_precision()).unwrap()}
pub fn evaluate<T:NativeFloat>(candidate:bool,input:&[C<T>],output:&mut[C<T>],rows:usize,context:&Context<T>,workspace:&mut BatchWorkspace<T>)->Result<(),String>{
 if candidate{self::candidate::evaluate_batch(input,output,rows,context,workspace)}else{baseline::evaluate_batch(input,output,rows,context,workspace)}
}
''')
 # Path modules preserve inner attributes from generated sources.
 text=(target/'module.rs').read_text().replace('mod baseline { include!("'+fam+'_baseline.rs"); }','#[path="'+fam+'_baseline.rs"] mod baseline;').replace('mod candidate { include!("'+fam+'_candidate.rs"); }','#[path="'+fam+'_candidate.rs"] mod candidate;').replace('mod constants { include!("constants.rs"); }','#[path="constants.rs"] mod constants;')
 (target/'module.rs').write_text(text)
(base/'inputs.json').write_text(json.dumps({'archive_hashes':archives,'generated':{str(p.relative_to(root)):sha(p) for f in ['c0','d0'] for p in sorted((base/f).glob('*.rs'))}},indent=2)+'\n')
print('frozen',len(archives),'archives and paired C0/D0 modules')
