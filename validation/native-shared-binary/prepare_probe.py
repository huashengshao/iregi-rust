from pathlib import Path
base=Path('target/native-shared-binary');old=Path('target/native-dense-span')
s=(old/'probe-fixed.rs').read_text()
start=s.index('#[cfg(family_c0)]');end=s.index('type Exact=',start)
s=s[:start]+'''#[path="b0/module.rs"] mod b0;
#[path="c0/module.rs"] mod c0;
#[path="fixture/module.rs"] mod fixture;
mod shared_binary_kernel;
mod kernel_controls;
fn generated_context<T:NativeFloat>(family:ScalarIntegral,prototype:&T)->oneloop::rust_codegen::runtime::Context<T>{
 match family{ScalarIntegral::B0=>b0::context(prototype),ScalarIntegral::C0=>c0::context(prototype),_=>unreachable!()}
}
fn generated_evaluate<T:NativeFloat>(family:ScalarIntegral,candidate:bool,input:&[Complex<T>],output:&mut[Complex<T>],rows:usize,context:&oneloop::rust_codegen::runtime::Context<T>,work:&mut BatchWorkspace<T>)->Result<(),String>{
 match family{ScalarIntegral::B0=>b0::evaluate(candidate,input,output,rows,context,work),ScalarIntegral::C0=>c0::evaluate(candidate,input,output,rows,context,work),_=>unreachable!()}
}
'''+s[end:]
s=s.replace('fn verify<T:NativeFloat>(label:', 'fn verify<T:NativeFloat>(family:ScalarIntegral,label:')
s=s.replace('generated::context(', 'generated_context(family,')
s=s.replace('generated::evaluate(', 'generated_evaluate(family,')
s=s.replace('fn exact_native_pair(outputs:&[Vec<Complex<f64>>;2]', 'fn exact_native_pair<T:NativeFloat>(outputs:&[Vec<Complex<T>>;2]')
s=s.replace('fn fixed_block(candidate:', 'fn fixed_block(family:ScalarIntegral,candidate:')
s=s.replace('fn benchmark(points:', 'fn benchmark(family:ScalarIntegral,points:')
s=s.replace('fixed_block(i==1,', 'fixed_block(family,i==1,')
s=s.replace('dense-span-fixed-loop-v2','shared-binary-fixed-loop-v2')
s=s.replace('fn fixture_control_flow()->', 'fn fixture_control_flow<T:NativeFloat>(label:&str,prototype:T)->')
s=s.replace('let context=fixture::context(&0.);let mut work=[BatchWorkspace::new(0.),BatchWorkspace::new(0.)];', 'let context=fixture::context(&prototype);let mut work=[BatchWorkspace::new(prototype.clone()),BatchWorkspace::new(prototype.clone())];')
s=s.replace('''[Complex::new(if active{1.}else{-0.},0.),Complex::new(if active{2.+lane as f64}else{-1.},0.),Complex::new(1.+(lane%3) as f64,0.)]''', '''[Complex::new(if active{prototype.one()}else{-prototype.zero()},prototype.zero()),Complex::new(prototype.from_rational(&Rational::from(if active{2+lane as i64}else{-1})),prototype.zero()),Complex::new(prototype.from_rational(&Rational::from(1+(lane%3) as i64)),prototype.zero())]''')
start=s.index('fn fixture_control_flow');end=s.index('fn run()',start)
fixture=s[start:end].replace('Complex::new(0.,0.)','Complex::new(prototype.zero(),prototype.zero())').replace('control,symbolica-generated-fixture,','control,symbolica-generated-fixture,{label},')
s=s[:start]+fixture+s[end:]
start=s.index('fn run()');s=s[:start]+'''fn run()->Result<(),String>{
 for family in [ScalarIntegral::B0,ScalarIntegral::C0]{
  let points=cases(family);
  if std::env::args().any(|a|a==format!("--benchmark-{}",family.name().to_ascii_lowercase())){return benchmark(family,&points);}
 }
 println!("kind,domain,ordering,rows,complex_outputs,interpreter_value_mismatches,interpreter_precision_mismatches,interpreter_signed_zero_mismatches,baseline_cells,candidate_cells");
 for family in [ScalarIntegral::B0,ScalarIntegral::C0]{
  let points=cases(family);
  eprintln!("building {} exact interpreter",family.name());
  let exact=iregi_masters::exact_scalar_master_evaluator(family).map_err(|e|e.to_string())?;
  verify(family,&format!("{}-f64",family.name()),&exact,&points,0.,&[0,1,3,7,32,3])?;
  invalid_neighbor_and_shape_controls(family,&points)?;
  verify(family,&format!("{}-DoubleFloat",family.name()),&exact,&points,DoubleFloat::default(),&[points.len(),1])?;
  verify(family,&format!("{}-Float256",family.name()),&exact,&points,Float::new(256),&[points.len(),1])?;
 }
 fixture_control_flow("f64",0.)?;
 fixture_control_flow("DoubleFloat",DoubleFloat::default())?;
 fixture_control_flow("Float256",Float::new(256))?;
 kernel_controls::run("f64",0.)?;
 kernel_controls::run("DoubleFloat",DoubleFloat::default())?;
 kernel_controls::run("Float256-mixed80-128-256",Float::new(256))?;
 Ok(())
}
fn main(){std::thread::Builder::new().stack_size(128*1024*1024).spawn(run).unwrap().join().unwrap().unwrap();}
'''
(base/'probe.rs').write_text(s)
