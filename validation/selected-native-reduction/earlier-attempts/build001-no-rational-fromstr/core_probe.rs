// Included independently against the baseline and selected private core crates.
use core_impl::{Algorithm, KinematicsBatch, LaneStatus, ReductionPlan, ReductionSettings, Workspace};
use iregi_masters::NativeFloat;
use serde_json::{Value, json};
use symbolica::{domains::{dual::HyperDual, float::{Complex, DoubleFloat, Float}, rational::Rational}, evaluate::EvaluationDomain};

pub struct Prepared {
    key: (usize, u16, String),
    workspace: Workspace<f64>,
    degrees: Vec<usize>,
}

fn numbers<T: NativeFloat>(z: &Complex<T>) -> Value {
    json!([number(&z.re), number(&z.im)])
}
fn number<T: NativeFloat>(x: &T) -> Value {
    json!({"rational":x.exact_rational().map(|q|q.to_string()), "precision":x.get_precision(), "negative_sign":x.negative_sign(), "finite":x.is_finite()})
}
fn execution<T: NativeFloat>(workspace: &Workspace<T>) -> Value where Complex<T>: EvaluationDomain {
    let s=workspace.last_execution();
    json!({"input_rows":s.input_rows,"argument_rows":s.argument_rows,"master_family_batches":s.master_family_batches,"master_rows":s.master_rows,"pentagon_box_rows":s.pentagon_box_rows,"reduction_rows":s.reduction_rows,"fallback_rows":s.fallback_rows,"fallback_successes":s.fallback_successes,"analytic_rows":s.analytic_rows})
}
fn algorithm(name: &str) -> Result<Algorithm,String> {
    match name {"Hybrid"=>Ok(Algorithm::Hybrid),"Ibp"=>Ok(Algorithm::Ibp),"PassarinoVeltman"=>Ok(Algorithm::PassarinoVeltman),_=>Err("unknown algorithm".into())}
}

pub fn run(request: &crate::Request, prepared: &mut Option<Prepared>) -> Result<Value,String> {
    if ![2,3].contains(&request.n) || request.rank>1 || request.samples.is_empty() {return Err("qualification scope is nonempty N2/N3 rank0/1".into());}
    let mut values=Vec::new();
    for sample in &request.samples {
        if sample.shifts.len()!=request.n || sample.masses.len()!=request.n {return Err("kinematic shape mismatch".into());}
        values.extend(sample.shifts.iter().flatten().map(|&v|Complex::new(v,0.)));
        values.extend(sample.masses.iter().map(|v|Complex::new(v[0],v[1])));
        values.push(Complex::new(sample.mu,0.));
    }
    let batch=KinematicsBatch{rows:request.samples.len(),components:1,values};
    let key=(request.n,request.rank,request.algorithm.clone());
    let reused=prepared.as_ref().is_some_and(|p|p.key==key);
    if !reused {
        let mut settings=ReductionSettings::new(request.n,request.rank);
        settings.algorithm=algorithm(&request.algorithm)?;
        let plan=ReductionPlan::new(settings).map_err(|e|e.to_string())?;
        *prepared=Some(Prepared{key,workspace:Workspace::new(&plan,0.).map_err(|e|e.to_string())?,degrees:plan.basis().iter().map(|m|m.rank()).collect()});
    }
    assert!(core_impl::take_master_captures().is_empty(),"unconsumed capture");
    core_impl::set_master_capture(true);
    let p=prepared.as_mut().unwrap();
    let result=p.workspace.reduce_batch(&batch);
    let captures=core_impl::take_master_captures();
    core_impl::set_master_capture(false);
    let result=result.map_err(|e|e.to_string())?;
    let lanes:Vec<_>=(0..batch.rows).map(|lane|match result.lane(lane){
        Ok(values)=>json!({"status":"success","moments":values.chunks_exact(4).map(|pole|pole.iter().map(|v|[v.re,v.im]).collect::<Vec<_>>()).collect::<Vec<_>>(),"represented":values.iter().map(numbers).collect::<Vec<_>>(),"fallback_used":result.fallback_used[lane],"analytic_used":result.analytic_used[lane]}),
        Err(error)=>json!({"status":format!("{error:?}"),"moments":null,"fallback_used":result.fallback_used[lane],"analytic_used":result.analytic_used[lane]}),
    }).collect();
    Ok(json!({"id":request.id,"n":request.n,"rank":request.rank,"batch":batch.rows,"plan_reused":reused,"degrees":p.degrees,"stable":result.statuses.iter().all(|s|*s==LaneStatus::Success),"lanes":lanes,"diagnostics":p.workspace.last_diagnostics(),"master_captures":captures,"execution":execution(&p.workspace),"private_selected_native":core_impl::PRIVATE_SELECTED_NATIVE,"scope":"untimed whole-reduction qualification"}))
}

fn unchanged<T: NativeFloat>(label: &str, prototype: T, dual: bool, mixed: bool) -> Value
where Complex<T>: EvaluationDomain {
    let mut settings=ReductionSettings::new(2,1);
    settings.algorithm=Algorithm::Hybrid;
    let plan=ReductionPlan::new(settings).unwrap();
    let mut workspace=if dual {
        Workspace::new_dual(&plan,prototype.clone(),HyperDual::<f64>::new(vec![vec![0],vec![1]])).unwrap()
    } else { Workspace::new(&plan,prototype.clone()).unwrap() };
    let components=if dual{2}else{1};
    // Existing concurrent-workspace fixture: spacelike unequal-mass bubble.
    let row=[0,0,0,0,0,1,0,0,2,3,1];
    let mut values=Vec::new();
    for (argument,value) in row.into_iter().enumerate() {
        let mut re=prototype.from_rational(&Rational::from(value));
        if mixed && argument==8 { re=prototype.from_rational(&"18014398509481985/9007199254740992".parse::<Rational>().unwrap()); }
        values.push(Complex::new(re,prototype.zero()));
        if dual {values.push(Complex::new(if argument==8{prototype.one()}else{prototype.zero()},prototype.zero()));}
    }
    let batch=KinematicsBatch{rows:1,components,values};
    assert!(core_impl::take_master_captures().is_empty());
    core_impl::set_master_capture(true);
    let mut records=Vec::new();
    for _ in 0..2 {
        let result=workspace.reduce_batch(&batch).unwrap();
        let values=result.lane(0).unwrap();
        records.push(json!({"values":values.iter().map(numbers).collect::<Vec<_>>(),"statuses":format!("{:?}",result.statuses),"diagnostics":workspace.last_diagnostics(),"fallback_used":result.fallback_used,"analytic_used":result.analytic_used,"execution":execution(&workspace),"master_captures":core_impl::take_master_captures()}));
    }
    core_impl::set_master_capture(false);
    assert_eq!(records[0],records[1],"own repeated outputs changed: {label}");
    json!({"label":label,"components":components,"input":batch.values.iter().map(numbers).collect::<Vec<_>>(),"result":records.remove(0)})
}

pub fn unchanged_controls() -> Value {
    json!([
        unchanged("DoubleFloat N2r1 beyond53",DoubleFloat::from(0.),false,true),
        unchanged("Float256 N2r1 beyond53",Float::new(256),false,true),
        unchanged("f64 Dual N2r1",0f64,true,false),
    ])
}
