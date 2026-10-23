from pathlib import Path
import hashlib,json,subprocess
root=Path.cwd();base=root/'target/native-master-replay';folder=base/'source/native';folder.mkdir(exist_ok=False)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();prep=json.loads((base/'preparation.json').read_text());revision=prep['source_revision'];records={}
for name in ['a0.rs','b0.rs','c0.rs','constants.rs']:
 path='crates/iregi-masters/src/generated/'+name;contents=subprocess.check_output(['git','show',f'{revision}:{path}'])
 assert contents==subprocess.check_output(['git','show',f'6b24c03:{path}'])
 (folder/name).write_bytes(contents);records[path]=sha(folder/name)
(folder/'mod.rs').write_text('''use oneloop::rust_codegen::runtime::{BatchWorkspace,C,ConstantSpec,Context,NativeFloat,batch,primitives};
#[allow(clippy::all,unused_assignments,dead_code)]mod a0;
#[allow(clippy::all,unused_assignments,dead_code)]mod b0;
#[allow(clippy::all,unused_assignments,dead_code)]mod c0;
mod constants;
pub fn context()->Context<f64>{Context::new(constants::CONSTANTS,53).unwrap()}
pub fn evaluate(family:oneloop::ScalarIntegral,input:&[C<f64>],output:&mut[C<f64>],rows:usize,context:&Context<f64>,work:&mut BatchWorkspace<f64>)->Result<(),String>{
 match family{
  oneloop::ScalarIntegral::A0=>a0::evaluate_batch(input,output,rows,context,work),
  oneloop::ScalarIntegral::B0=>b0::evaluate_batch(input,output,rows,context,work),
  oneloop::ScalarIntegral::C0=>c0::evaluate_batch(input,output,rows,context,work),
  _=>Err("replay only admits A0/B0/C0; no D0 module compiled".into()),
 }
}
''')
(base/'native-source.json').write_text(json.dumps({'scope':'Selected unchanged original generated kernels only; rejected allocator/dense/shared candidates excluded; native-batch feature disabled','source_revision':revision,'sources':records,'wrapper_sha256':sha(folder/'mod.rs')},indent=2)+'\n')
