use crate::{same,shared_binary_kernel::{BinaryOperand,shared_binary}};
use oneloop::rust_codegen::runtime::{C,Context,ConstantSpec,NativeFloat,primitives};
use symbolica::domains::{rational::Rational,integer::Integer};

fn check<T:NativeFloat,const MUL:bool,const INLINE:bool>(label:&str,prototype:&T)->Result<(usize,usize),String>{
 let specs=[ConstantSpec::Rational{re:"1208925819614629174706177/1208925819614629174706176",im:"-2/3"},ConstantSpec::Rational{re:"-7/11",im:"5/13"}];
 let ctx=Context::new(&specs,prototype.get_precision())?;
 let precise=Rational::from(("1208925819614629174706177".parse::<Integer>().unwrap(),"1208925819614629174706176".parse::<Integer>().unwrap()));
 let stride=33;
 let arena:Vec<_>=(0..4*stride).map(|i|{
  let bits=if T::FIXED_BITS.is_some(){prototype.get_precision()}else{[80,128,256][i%3]};
  let p=prototype.at_precision(bits);
  let re=match i%5{0=>-p.zero(),1=>p.zero(),2=>p.from_rational(&precise),3=>-p.from_rational(&precise),_=>p.from_rational(&Rational::from((7,11)))};
  let im=if i%2==0{-p.zero()}else{p.from_rational(&Rational::from((-5,13)))};
  C::new(re,im)
 }).collect();
 let pairs=[(BinaryOperand::Column(0),BinaryOperand::Column(1)),(BinaryOperand::Column(0),BinaryOperand::Constant(0)),(BinaryOperand::Constant(0),BinaryOperand::Column(1)),(BinaryOperand::Constant(0),BinaryOperand::Constant(1)),(BinaryOperand::Column(0),BinaryOperand::Column(0))];
 let patterns=[(vec![],Some((0,0))),(vec![3,4,5,6],Some((3,7))),(vec![1,3,9,31],None),((0..stride).collect(),Some((0,stride)))];
 let mut configurations=0;let mut comparisons=0;
 for (left,right) in pairs{for destination in [0,1,2]{for (lanes,span) in &patterns{
  let mut expected=arena.clone();let mut actual=arena.clone();
  for &lane in lanes{
   let read=|operand|match operand{BinaryOperand::Column(column)=>&arena[column*stride+lane],BinaryOperand::Constant(index)=>ctx.constant(index)};
   let (a,b)=(read(left),read(right));
   let value=if MUL{if INLINE{primitives::inline_mul(a,b)}else{primitives::mul(a,b)}}else if INLINE{primitives::inline_add(a,b)}else{primitives::add(a,b)};
   expected[destination*stride+lane]=value;
  }
  shared_binary::<T,MUL,INLINE>(&mut actual,stride,lanes,*span,destination,left,right,&ctx);
  for (index,(a,b)) in expected.iter().zip(&actual).enumerate(){
   if !same(&a.re,&b.re)||!same(&a.im,&b.im){return Err(format!("kernel operand/alias control {label}: MUL={MUL}/INLINE={INLINE}/{left:?}/{right:?}/destination={destination}/span={span:?}/cell={index}: {a:?} != {b:?}"));}
   comparisons+=1;
  }
  configurations+=1;
 }}}
 Ok((configurations,comparisons))
}
pub fn run<T:NativeFloat>(label:&str,prototype:T)->Result<(),String>{
 let counts=[check::<T,false,false>(label,&prototype)?,check::<T,true,false>(label,&prototype)?,check::<T,false,true>(label,&prototype)?,check::<T,true,true>(label,&prototype)?];
 let configurations:usize=counts.iter().map(|x|x.0).sum();let comparisons:usize=counts.iter().map(|x|x.1).sum();
 eprintln!("control,direct-shared-kernel,{label},configurations={configurations},all-arena-complex-comparisons={comparisons},both-primitives,positional-constants,aliases,signed-zero,empty,dense-offset,sparse,inactive-cells-unchanged,passed");
 Ok(())
}
