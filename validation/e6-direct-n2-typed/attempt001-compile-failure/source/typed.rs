//! Typed private qualification; the N2 engine is byte-identical to its first checkpoint.
#[path = "near_vacuum_e6.rs"] mod candidate;
use candidate::{AccuracyContext, Exact, Lane, NearVacuumPlan, Status, abs, pow2_minus, zero};
use iregi_masters::NativeFloat;
use serde_json::{Value,json};
use std::{error::Error,path::PathBuf,time::Instant};
use symbolica::{atom::{Atom,AtomCore},domains::{dual::{DualNumber,DualNumberStructure,HyperDual},
    float::{Complex,DoubleFloat,Float,FloatLike,SingleFloat},integer::Integer,rational::Rational},
    evaluate::{EvaluationDomain,ExpressionEvaluator}};

symbolica::create_hyperdual_from_components!(Mixed4,[[0,0],[1,0],[0,1],[1,1]]);
symbolica::create_hyperdual_from_components!(Mixed6,[[0,0],[1,0],[0,1],[2,0],[1,1],[2,1]]);

fn real(r:Rational)->Exact {Complex::new(r,Rational::from(0))}
fn exact<T:NativeFloat>(v:&Complex<T>)->Exact {
    Complex::new(v.re.exact_rational().expect("finite input"),v.im.exact_rational().expect("finite input"))
}
fn bound_json(b:&candidate::ComponentBound)->Value {
    json!({"truncation":b.truncation.to_string(),"real_interval":[b.real_lower.to_string(),b.real_upper.to_string()],
        "imaginary_interval":[b.imaginary_lower.to_string(),b.imaginary_upper.to_string()],
        "maximum_error_squared":b.maximum_error_squared.to_string(),"allowed_error_squared":b.allowed_error_squared.to_string()})
}
fn lane_json<T:NativeFloat>(l:&Lane<T>)->Value {
    json!({"status":format!("{:?}",l.status),"rho":l.rho.as_ref().map(ToString::to_string),
        "bounds":l.bounds.iter().map(bound_json).collect::<Vec<_>>(),
        "values":l.values.as_ref().map(|vs|vs.iter().map(|v|{let e=exact(v);json!({"real":e.re.to_string(),"imaginary":e.im.to_string()})}).collect::<Vec<_>>())})
}
fn execution_json(e:&candidate::Execution)->Value {
    json!({"packed_rows":e.input_rows,"active_rows":e.active_rows,"numeric_batch_calls":e.numeric_batch_calls,
        "enclosure_batch_calls":e.enclosure_batch_calls,"tail_batch_calls":e.tail_batch_calls,
        "instruction_lane_visits":e.estimated_exported_instruction_lane_visits})
}
fn physical_batch<T:NativeFloat>(w:&mut candidate::Workspace<T>,input:&[Complex<T>],rows:usize,c:usize,
    a:&AccuracyContext)->Result<Vec<Lane<T>>,String> where Complex<T>:EvaluationDomain {
    a.validate(c)?;
    let width=16usize.checked_mul(c).ok_or("width overflow")?;
    if input.len()!=rows.checked_mul(width).ok_or("size overflow")? {return Err("physical row length".into());}
    let mut out:Vec<_>=(0..rows).map(|_|Lane{status:Status::InvalidInput("invalid physical mu_squared".into()),values:None,bounds:vec![],rho:None}).collect();
    let mut packed=Vec::new();let mut active=Vec::new();
    for (lane,row) in input.chunks_exact(width).enumerate() {
        let s:Option<Vec<_>>=row[15*c..].iter().map(|v|Some(Complex::new(v.re.exact_rational()?,v.im.exact_rational()?))).collect();
        if !s.as_ref().is_some_and(|v|v[0].re>Rational::from(0)&&v[0].im==Rational::from(0)){continue;}
        packed.extend_from_slice(&row[..15*c]);active.push(lane);
    }
    let values=w.evaluate_batch(&packed,active.len(),a)?;
    assert_eq!(values.len(),active.len());
    for (lane,v) in active.into_iter().zip(values){out[lane]=v;}
    Ok(out)
}

struct Identity {programs:Vec<ExpressionEvaluator<Exact>>}
impl Identity {
    fn new(shape:&[Vec<usize>])->Result<Self,Box<dyn Error>> {
        let x_symbol=symbolica::symbol!("iregi_e6_typed_identity::x");
        let y_symbol=symbolica::symbol!("iregi_e6_typed_identity::y");
        let vars=[Atom::var(x_symbol),Atom::var(y_symbol)];
        let parameters:Vec<_>=(0..shape.len()).map(|i|Atom::var(symbolica::symbol!(format!("iregi_e6_typed_identity::m{i}")))).collect();
        let mass:Atom=shape.iter().zip(&parameters).map(|(degree,p)|p*vars[0].pow(degree[0] as i64)*vars[1].pow(degree[1] as i64)).sum();
        let identity=-Atom::num(1)/(Atom::num(24)*mass.pow(2));
        let mut programs=Vec::new();
        for degree in shape {
            let mut expression=identity.clone();
            for (axis,&symbol) in [x_symbol,y_symbol].iter().enumerate(){
                for _ in 0..degree[axis] {expression=expression.derivative(symbol);}
                expression/=Atom::num(Integer::factorial(degree[axis] as u32));
            }
            expression=expression.replace(x_symbol).with(Atom::num(0)).replace(y_symbol).with(Atom::num(0));
            programs.push(expression.evaluator(&parameters).direct_translation(true).horner_iterations(0).cores(1).build()?);
        }
        Ok(Self{programs})
    }
    fn evaluate<T:NativeFloat>(&mut self,row:&[Complex<T>],c:usize)->Vec<Exact> {
        assert!(row[..10*c].iter().all(|v|exact(v)==zero()),"common-mass oracle requires zero invariants and jets");
        let mass:Vec<_>=row[10*c..11*c].iter().map(exact).collect();
        for i in 11..15 {assert_eq!(row[i*c..(i+1)*c].iter().map(exact).collect::<Vec<_>>(),mass);}
        self.programs.iter_mut().map(|p|{let mut out=[zero()];p.evaluate(&mass,&mut out);out[0].clone()}).collect()
    }
}

fn compare<T:NativeFloat>(lane:&Lane<T>,centers:&[Exact],c:usize)->Value {
    assert_eq!(lane.status,Status::Success);
    let values=lane.values.as_ref().unwrap();assert_eq!(values.len(),c);assert_eq!(lane.bounds.len(),c);assert_eq!(centers.len(),c);
    json!(values.iter().zip(&lane.bounds).zip(centers).enumerate().map(|(i,((v,b),center))|{
        let actual=exact(v);let difference=&actual-center;
        let error=difference.re.pow(2)+difference.im.pow(2);
        let dr=abs(&(&b.real_lower-&center.re)).max(abs(&(&b.real_upper-&center.re)));
        let di=abs(&(&b.imaginary_lower-&center.im)).max(abs(&(&b.imaginary_upper-&center.im)));
        let rectangle=dr.pow(2)+di.pow(2);
        assert!(error<=b.allowed_error_squared,"numeric component{i}");
        assert!(rectangle<=b.allowed_error_squared,"rectangle component{i}");
        assert!(b.real_lower<=center.re&&center.re<=b.real_upper);
        assert!(b.imaginary_lower<=center.im&&center.im<=b.imaginary_upper);
        json!({"component":i,"center_real":center.re.to_string(),"center_imaginary":center.im.to_string(),
            "actual_error_squared":error.to_string(),"rectangle_error_squared":rectangle.to_string(),
            "allowed_error_squared":b.allowed_error_squared.to_string(),
            "rounding_real_width":(&b.real_upper-&b.real_lower-Rational::from(2)*&b.truncation).to_string(),
            "rounding_imaginary_width":(&b.imaginary_upper-&b.imaginary_lower-Rational::from(2)*&b.truncation).to_string()})
    }).collect::<Vec<_>>())
}

fn fixtures(shape:&[Vec<usize>])->Vec<Vec<Exact>> {
    let c=shape.len();let seed=pow2_minus(64);
    let mut common=vec![zero();16*c];
    for i in 10..15 {
        common[i*c]=Complex::new(Rational::from(2),Rational::from(-1));
        for (j,d) in shape.iter().enumerate(){
            if d.as_slice()==[1,0] {common[i*c+j]=Complex::new(seed.clone(),&seed/Rational::from(2));}
            if d.as_slice()==[0,1] {common[i*c+j]=Complex::new(-&seed/Rational::from(2),seed.clone());}
        }
    }
    common[15*c]=real(Rational::from(1));
    let mut rows=vec![common;13];
    rows[1][15*c]=real(Rational::from(4));rows[1][15*c+1]=real(Rational::from(7));
    for i in 10..15 {rows[2][i*c].re+=pow2_minus(80);rows[4][i*c]=Complex::new(Rational::from(3),Rational::from((-1,2)));}
    rows[3][10*c].im=Rational::from(1);rows[5][0]=real(Rational::from(2));
    for i in 10..15 {rows[6][i*c+1]=Complex::new(Rational::from(1),Rational::from((1,2)));rows[6][i*c+2]=Complex::new(Rational::from((-1,2)),Rational::from(1));}
    rows[7][15*c]=real(Rational::from(-1));
    for i in 10..15 {for j in 1..c {rows[8][i*c+j]=zero();}}
    rows[9][0].im=seed;
    for i in 10..15 {rows[11][i*c].im=Rational::from(0);}
    rows[12][10*c]=zero();
    rows
}

fn carriers<T:NativeFloat>(shape:&[Vec<usize>],input:&[Complex<T>]) {
    let c=shape.len();
    for components in input.chunks_exact(c) {
        let dynamic=HyperDual::from_values(shape.to_vec(),components.to_vec());
        if c==4 {
            let carrier=Mixed4{values:std::array::from_fn(|i|components[i].clone())};
            assert_eq!(carrier.get_shape(),dynamic.get_shape());assert_eq!(carrier.get_len(),c);
            assert_eq!(carrier.values(),dynamic.values());
        } else {
            let carrier=Mixed6{values:std::array::from_fn(|i|components[i].clone())};
            assert_eq!(carrier.get_shape(),dynamic.get_shape());assert_eq!(carrier.get_len(),c);
            assert_eq!(carrier.values(),dynamic.values());
        }
    }
}
fn assert_same<T:NativeFloat>(a:&[Lane<T>],b:&[Lane<T>]) {
    assert_eq!(a.len(),b.len());for (a,b) in a.iter().zip(b){assert_eq!(lane_json(a),lane_json(b));}
}

fn run<T:NativeFloat>(kind:&str,prototype:T,requested:u32,c:usize)->Result<Value,Box<dyn Error>>
where Complex<T>:EvaluationDomain {
    let started=Instant::now();
    let (shape,static_plan)=if c==4 {
        let meta=Mixed4::<Rational>{values:std::array::from_fn(|_|Rational::from(0))};
        (meta.get_shape().iter().map(|s|s.to_vec()).collect::<Vec<_>>(),NearVacuumPlan::from_dual(2,&meta)?)
    } else {
        let meta=Mixed6::<Rational>{values:std::array::from_fn(|_|Rational::from(0))};
        (meta.get_shape().iter().map(|s|s.to_vec()).collect::<Vec<_>>(),NearVacuumPlan::from_dual(2,&meta)?)
    };
    let dynamic_meta=HyperDual::<Rational>::new(shape.clone());
    let dynamic_plan=NearVacuumPlan::from_dual(2,&dynamic_meta)?;
    assert_eq!(static_plan.integrated_polynomial,dynamic_plan.integrated_polynomial);
    assert_eq!(static_plan.shape,dynamic_plan.shape);
    let preparation_seconds=started.elapsed().as_secs_f64();
    let original=fixtures(&shape);let rows=original.len();let width=16*c;
    let mut input:Vec<_>=original.iter().flatten().map(|v|Complex::new(prototype.from_rational(&v.re),prototype.from_rational(&v.im))).collect();
    // For arbitrary precision, row10 deliberately mixes53-bit and working-bit
    // physical components. Their exact represented values are the contract.
    if T::FIXED_BITS.is_none() {
        let low=T::zero_at(53);
        for j in 0..width {
            if j%2==0 {let e=&original[10][j];input[10*width+j]=Complex::new(low.from_rational(&e.re),low.from_rational(&e.im));}
        }
        assert!(input[10*width..11*width].iter().any(|v|v.re.get_precision()==53));
        assert!(input[10*width..11*width].iter().any(|v|v.re.get_precision()>53));
    }
    let baseline_mass=exact(&input[10*c]);let beyond_mass=exact(&input[2*width+10*c]);
    if kind=="f64" {assert_eq!(beyond_mass,baseline_mass);} else {assert_ne!(beyond_mass,baseline_mass);assert_eq!(&beyond_mass.re-&baseline_mass.re,pow2_minus(80));}
    carriers(&shape,&input);
    let accuracy=AccuracyContext::binary(requested,c);
    let mut workspace=static_plan.instantiate(prototype.clone());
    assert!(physical_batch(&mut workspace,&[],0,c,&accuracy)?.is_empty());
    assert_eq!(workspace.execution.numeric_batch_calls,0);
    assert!(physical_batch(&mut workspace,&input[..width-1],1,c,&accuracy).is_err());
    let primary=physical_batch(&mut workspace,&input,rows,c,&accuracy)?;
    let counters=workspace.execution.clone();assert_eq!(primary.len(),13);
    assert_eq!(counters.input_rows,12);assert_eq!(counters.active_rows,7);
    assert_eq!((counters.numeric_batch_calls,counters.enclosure_batch_calls,counters.tail_batch_calls),(1,1,1));
    let accepted:Vec<_>=(0..rows).filter(|i|[0,1,2,4,8,10].contains(i)||(*i==6&&c==4)).collect();
    for i in 0..rows {
        eprintln!("{kind} shape{c} lane{i}: {:?}",primary[i].status);
        if accepted.contains(&i){assert_eq!(primary[i].status,Status::Success,"lane{i}");}
        else {assert_ne!(primary[i].status,Status::Success);assert!(primary[i].values.is_none());}
    }
    assert_eq!(primary[5].status,Status::OutsideAnalyticDomain);
    for i in [3,7,9,11,12] {assert!(matches!(primary[i].status,Status::InvalidInput(_)));}
    if c==6 {assert_eq!(primary[6].status,Status::UncertifiedComponent(5));assert_eq!(primary[6].rho,Some(Rational::from(0)));assert!(primary[6].bounds[5].truncation>Rational::from(0));}
    assert_eq!(lane_json(&primary[0]),lane_json(&primary[1]));
    assert_eq!(lane_json(&primary[0]),lane_json(&primary[10]));
    if kind!="f64" {assert_ne!(exact(&primary[0].values.as_ref().unwrap()[0]),exact(&primary[2].values.as_ref().unwrap()[0]));}
    let mut oracle=Identity::new(&shape)?;let mut comparisons=Vec::new();
    for &lane in &accepted {
        let centers=oracle.evaluate(&input[lane*width..(lane+1)*width],c);
        comparisons.push(json!({"lane":lane,"components":compare(&primary[lane],&centers,c)}));
    }
    let cubic_oracle=if c==6 {let center=oracle.evaluate(&input[6*width..7*width],c);assert_ne!(center[5],zero());Some(json!({"real":center[5].re.to_string(),"imaginary":center[5].im.to_string()}))}else{None};
    let mut independent=dynamic_plan.instantiate(prototype.clone());
    let dynamic_result=physical_batch(&mut independent,&input,rows,c,&accuracy)?;assert_same(&primary,&dynamic_result);
    assert_eq!((independent.execution.active_rows,independent.execution.numeric_batch_calls,independent.execution.enclosure_batch_calls,independent.execution.tail_batch_calls),(7,1,1,1));
    let reverse:Vec<_>=input.chunks_exact(width).rev().flatten().cloned().collect();
    let reverse_result=physical_batch(&mut independent,&reverse,rows,c,&accuracy)?;
    let reverse_json:Vec<_>=reverse_result.iter().rev().map(lane_json).collect();
    assert_eq!(primary.iter().map(lane_json).collect::<Vec<_>>(),reverse_json);
    let mut chunked=Vec::new();let mut chunk_counters=Vec::new();
    for range in [0..5,5..13] {
        let part=physical_batch(&mut independent,&input[range.start*width..range.end*width],range.len(),c,&accuracy)?;
        assert_eq!((independent.execution.numeric_batch_calls,independent.execution.enclosure_batch_calls,independent.execution.tail_batch_calls),(1,1,1));
        chunk_counters.push(execution_json(&independent.execution));chunked.extend(part);
    }
    assert_same(&primary,&chunked);
    let mut singleton=static_plan.instantiate(prototype.clone());
    let alone=physical_batch(&mut singleton,&input[..width],1,c,&accuracy)?;
    assert_eq!(lane_json(&primary[0]),lane_json(&alone[0]));
    // Concurrent, independent workspaces; no shared mutable evaluator/cache.
    let mut wa=static_plan.instantiate(prototype.clone());let mut wb=dynamic_plan.instantiate(prototype);
    let (ca,cb)=std::thread::scope(|scope|{
        let input_ref=&input;let accuracy_ref=&accuracy;let reverse_ref=&reverse;
        let a=scope.spawn(move||{let r=physical_batch(&mut wa,input_ref,rows,c,accuracy_ref).unwrap();(r,wa.execution.clone())});
        let b=scope.spawn(move||{let r=physical_batch(&mut wb,reverse_ref,rows,c,accuracy_ref).unwrap();(r,wb.execution.clone())});
        (a.join().unwrap(),b.join().unwrap())
    });
    assert_same(&primary,&ca.0);assert_eq!(primary.iter().map(lane_json).collect::<Vec<_>>(),cb.0.iter().rev().map(lane_json).collect::<Vec<_>>());
    for e in [&ca.1,&cb.1] {assert_eq!((e.active_rows,e.numeric_batch_calls,e.enclosure_batch_calls,e.tail_batch_calls),(7,1,1,1));}
    let physical_input:Vec<_>=input.chunks_exact(width).enumerate().map(|(row,vs)|json!({"row":row,"components":vs.iter().map(|v|{let e=exact(v);json!({"real":e.re.to_string(),"imaginary":e.im.to_string(),"real_bits":v.re.get_precision(),"imaginary_bits":v.im.get_precision()})}).collect::<Vec<_>>()})).collect();
    Ok(json!({"status":"passed_private_typed_e6_n2","kind":kind,"working_bits":workspace_bits(kind),"requested_bits":requested,"shape":shape,
        "metadata":"Static Mixed4/Mixed6 and dynamic HyperDual metadata/component transport; derivative arithmetic uses Symbolica Dualizer",
        "static_dynamic_prepared_expression_equal":true,"physical_rows":rows,"successful_rows":accepted.len(),"successful_components":accepted.len()*c,
        "rejected_rows":rows-accepted.len(),"primary_execution":execution_json(&counters),"chunk_execution":chunk_counters,
        "concurrent_execution":[execution_json(&ca.1),execution_json(&cb.1)],
        "lanes":primary.iter().enumerate().map(|(i,l)|json!({"lane":i,"result":lane_json(l)})).collect::<Vec<_>>(),
        "independent_identity_comparisons":comparisons,"large_mixed_cubic_oracle":cubic_oracle,"physical_input":physical_input,
        "beyond53_distinct":kind!="f64","mixed_input_precision":T::FIXED_BITS.is_none(),
        "empty_malformed_odd_reverse_chunk_fresh_singleton_static_dynamic_concurrent":"passed",
        "invalid_neighbor_isolation":"singleton equals batch row0","scale_and_scalejet_independence":"row0 equalsrow1",
        "input_precision_scope":"exact represented values; no assertion of scientific uncertainty of low-precision inputs",
        "preparation_seconds_diagnostic":preparation_seconds,"total_seconds_diagnostic":started.elapsed().as_secs_f64(),
        "limitations":"Common complex mass and zero invariants only; no general physical/routing coverage, N4, public/core/default integration or benchmark"}))
}
fn workspace_bits(kind:&str)->u32 {match kind{"f64"=>53,"dd"=>106,"float128"=>128,"float256"=>256,"float384"=>384,_=>unreachable!()}}
fn main()->Result<(),Box<dyn Error>> {
    let mut args=std::env::args().skip(1);let kind=args.next().ok_or("numeric kind")?;
    let c:usize=args.next().ok_or("components4or6")?.parse()?;assert!([4,6].contains(&c));
    let output=PathBuf::from(args.next().ok_or("output path")?);assert!(args.next().is_none());
    let result=match kind.as_str(){
        "f64"=>run(&kind,0f64,40,c)?,"dd"=>run(&kind,DoubleFloat::from(0.0),80,c)?,
        "float128"=>run(&kind,Float::new(128),80,c)?,"float256"=>run(&kind,Float::new(256),128,c)?,
        "float384"=>run(&kind,Float::new(384),128,c)?,_=>return Err("unknown numeric kind".into())};
    std::fs::write(output,serde_json::to_vec_pretty(&result)?)?;Ok(())
}
