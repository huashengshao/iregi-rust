// One generic Symbolica-only module per separately linked scheduler archive.
use core_impl::{Algorithm, KinematicsBatch, LaneStatus, ReductionPlan, ReductionSettings, Workspace};
use iregi_masters::NativeFloat;
use serde_json::{Value, json};
use symbolica::{domains::{dual::HyperDual, float::{Complex, DoubleFloat, Float}, rational::Rational}, evaluate::EvaluationDomain};

pub struct Prepared {
    key: (usize, u16, String),
    workspace: Workspace<f64>,
    degrees: Vec<usize>,
}

fn numbers<T: NativeFloat>(z: &Complex<T>) -> Value { json!([number(&z.re),number(&z.im)]) }
fn number<T: NativeFloat>(x: &T) -> Value {
    json!({"rational":x.exact_rational().map(|q|q.to_string()),"precision":x.get_precision(),"negative_sign":x.negative_sign(),"finite":x.is_finite()})
}
fn execution<T: NativeFloat>(workspace: &Workspace<T>) -> Value where Complex<T>: EvaluationDomain {
    let s=workspace.last_execution();
    json!({"input_rows":s.input_rows,"argument_rows":s.argument_rows,"master_family_batches":s.master_family_batches,"master_rows":s.master_rows,"pentagon_box_rows":s.pentagon_box_rows,"reduction_rows":s.reduction_rows,"fallback_rows":s.fallback_rows,"fallback_successes":s.fallback_successes,"analytic_rows":s.analytic_rows})
}


fn observe<T: NativeFloat>(workspace: &mut Workspace<T>, batch: &KinematicsBatch<T>,
    moments: usize, dual: bool) -> Result<Value,String>
where Complex<T>: EvaluationDomain {
    workspace.set_profiling(false);
    let result=workspace.reduce_batch(batch);
    assert!(workspace.last_profile().is_none(),"profiling unexpectedly enabled");
    let result=result.map_err(|e|e.to_string())?;
    assert_eq!(result.statuses.len(),batch.rows);
    let lanes:Vec<_>=(0..batch.rows).map(|lane|match result.lane(lane){
        Ok(values)=>{
            assert_eq!(values.len(),moments*4*batch.components);
            assert!(values.iter().all(|z|z.re.is_finite()&&z.im.is_finite()));
            let mut record=json!({"status":"success","represented":values.iter().map(numbers).collect::<Vec<_>>(),
                "fallback_used":result.fallback_used[lane],"analytic_used":result.analytic_used[lane]});
            if std::any::TypeId::of::<T>()==std::any::TypeId::of::<f64>() && !dual {
                assert_eq!(batch.components,1);
                record["moments"]=json!(values.chunks_exact(4).map(|pole|pole.iter().map(|z| {
                    let re=(&z.re as &dyn std::any::Any).downcast_ref::<f64>().unwrap();
                    let im=(&z.im as &dyn std::any::Any).downcast_ref::<f64>().unwrap();
                    [*re,*im]
                }).collect::<Vec<_>>()).collect::<Vec<_>>());
            }
            record
        },
        Err(error)=>json!({"status":format!("{error:?}"),"represented":null,"moments":null,"fallback_used":result.fallback_used[lane],"analytic_used":result.analytic_used[lane]}),
    }).collect();
    Ok(json!({"stable":result.statuses.iter().all(|s|*s==LaneStatus::Success),"lanes":lanes,
        "diagnostics":workspace.last_diagnostics(),"master_captures":[],"execution":execution(workspace)}))
}

pub fn run(request: &crate::Request, prepared: &mut Option<Prepared>, plans: &mut crate::PlanCache) -> Result<Value,String> {
    if ![2,3].contains(&request.n) || request.rank>1 || ![1,32].contains(&request.samples.len()) || request.algorithm!="Hybrid" {
        return Err("qualification scope is the eight N2/N3 rank0/1 batch1/32 Hybrid families".into());
    }
    let mut values=Vec::new();
    for sample in &request.samples {
        if sample.shifts.len()!=request.n || sample.masses.len()!=request.n {return Err("kinematic shape mismatch".into());}
        values.extend(sample.shifts.iter().flatten().map(|&v|Complex::new(v,0.)));
        values.extend(sample.masses.iter().map(|v|Complex::new(v[0],v[1])));
        values.push(Complex::new(sample.mu,0.));
    }
    let batch=KinematicsBatch{rows:request.samples.len(),components:1,values};
    let input_before=batch.values.iter().map(numbers).collect::<Vec<_>>();
    let key=(request.n,request.rank,request.algorithm.clone());
    let reused=prepared.as_ref().is_some_and(|p|p.key==key);
    if !reused {
        if !plans.contains_key(&key) {
            let mut settings=ReductionSettings::new(request.n,request.rank);
            settings.algorithm=Algorithm::Hybrid;
            plans.insert(key.clone(),ReductionPlan::new(settings).map_err(|e|e.to_string())?);
        }
        let plan=plans.get(&key).unwrap();
        *prepared=Some(Prepared{key,workspace:Workspace::new(plan,0.).map_err(|e|e.to_string())?,degrees:plan.basis().iter().map(|m|m.rank()).collect()});
    }
    let p=prepared.as_mut().unwrap();
    let measured=request.engine.is_some();
    p.workspace.set_profiling(false);
    let mut every_call_successful=true;
    let mut total_ns=Vec::<f64>::new();
    let mut elapsed_ns=Vec::<u128>::new();
    if measured {
        if request.engine.as_deref()!=Some(env!("TIRUST_SCHEDULER_VARIANT")) || request.repeats!=1 || request.iterations==0 || request.iterations>i32::MAX as usize {
            return Err("timing requires own variant and one positive signed32 fixed-count block".into());
        }
        for _ in 0..request.warmup {
            let result=p.workspace.reduce_batch(std::hint::black_box(&batch)).map_err(|e|e.to_string())?;
            every_call_successful &= result.statuses.iter().all(|s|*s==LaneStatus::Success);
            std::hint::black_box(result);
        }
        let start=std::time::Instant::now();
        for _ in 0..request.iterations {
            let result=p.workspace.reduce_batch(std::hint::black_box(&batch)).map_err(|e|e.to_string())?;
            every_call_successful &= result.statuses.iter().all(|s|*s==LaneStatus::Success);
            std::hint::black_box(result);
        }
        let duration=start.elapsed().as_nanos();
        elapsed_ns.push(duration);
        total_ns.push(duration as f64/request.iterations as f64);
    } else if request.warmup!=0 || request.repeats!=0 || request.iterations!=0 {
        return Err("untimed request must not carry timing counts".into());
    }
    let mut record=observe(&mut p.workspace,&batch,p.degrees.len(),false)?;
    assert!(every_call_successful,"timed public call failed");
    assert!(record["stable"].as_bool().unwrap(),"frozen qualification family failed");
    if !measured {
        for _ in 0..2 {
            assert_eq!(observe(&mut p.workspace,&batch,p.degrees.len(),false)?,record,"own complete repeated record changed");
        }
    }
    assert_eq!(batch.values.iter().map(numbers).collect::<Vec<_>>(),input_before);
    let object=record.as_object_mut().unwrap();
    for (key,value) in json!({"id":request.id,"n":request.n,"rank":request.rank,"batch":batch.rows,"plan_reused":reused,"degrees":p.degrees,
        "requested_master_backend":"SymbolicaBatch","scope":if measured{"whole-public-call fixed-count timing"}else{"untimed capture-free scheduler whole-reduction qualification"},
        "total_ns":total_ns,"elapsed_ns":elapsed_ns,"iterations":if measured{request.iterations}else{0},"capture_enabled":false,"profiling_enabled":false,
        "own_repeated_outputs_exact":!measured,"input_unchanged":true}).as_object().unwrap() {object.insert(key.clone(),value.clone());}
    Ok(record)
}

fn control_batch<T: NativeFloat>(prototype: &T, dual: bool, mixed: bool) -> KinematicsBatch<T> {
    let row=[0,0,0,0,0,1,0,0,2,3,1];
    let mut values=Vec::new();
    for (argument,value) in row.into_iter().enumerate() {
        let mut re=prototype.from_rational(&Rational::from(value));
        if mixed && argument==8 { re=prototype.from_rational(&Rational::from((18014398509481985_i64,9007199254740992_i64))); }
        values.push(Complex::new(re,prototype.zero()));
        if dual {values.push(Complex::new(if argument==8{prototype.one()}else{prototype.zero()},prototype.zero()));}
    }
    KinematicsBatch{rows:1,components:if dual{2}else{1},values}
}
fn control_workspace<T: NativeFloat>(plan: &ReductionPlan, prototype: T, dual: bool) -> Workspace<T>
where Complex<T>: EvaluationDomain {
    if dual { Workspace::new_dual(plan,prototype,HyperDual::<f64>::new(vec![vec![0],vec![1]])).unwrap() }
    else { Workspace::new(plan,prototype).unwrap() }
}
fn control_plan() -> ReductionPlan {
    let mut settings=ReductionSettings::new(2,1);settings.algorithm=Algorithm::Hybrid;
    ReductionPlan::new(settings).unwrap()
}
fn unchanged<T: NativeFloat>(label: &str, prototype: T, dual: bool, mixed: bool) -> Value
where Complex<T>: EvaluationDomain {
    let plan=control_plan();
    let mut workspace=control_workspace(&plan,prototype.clone(),dual);
    let batch=control_batch(&prototype,dual,mixed);
    let input_before=batch.values.iter().map(numbers).collect::<Vec<_>>();
    let expected=observe(&mut workspace,&batch,plan.basis().len(),dual).unwrap();
    assert!(expected["stable"].as_bool().unwrap());
    for _ in 0..2 {assert_eq!(observe(&mut workspace,&batch,plan.basis().len(),dual).unwrap(),expected,"own repeated outputs changed: {label}");}
    assert_eq!(batch.values.iter().map(numbers).collect::<Vec<_>>(),input_before);
    // Preserve the original control schema; every control here has one successful lane.
    let result=json!({"values":expected["lanes"][0]["represented"],"statuses":"[Success]",
        "diagnostics":expected["diagnostics"],"fallback_used":[expected["lanes"][0]["fallback_used"]],
        "analytic_used":[expected["lanes"][0]["analytic_used"]],"execution":expected["execution"],
        "master_captures":expected["master_captures"]});
    json!({"label":label,"components":batch.components,"input":input_before,"result":result,
        "own_repeated_outputs_exact":true,"input_unchanged":true})
}
pub fn unchanged_controls() -> Value {
    json!([unchanged("f64 Dual N2r1",0f64,true,false)])
}
pub fn extended_unchanged_controls() -> Value {
    json!([
        unchanged("DoubleFloat N2r1 beyond53",DoubleFloat::from(0.),false,true),
        unchanged("Float256 N2r1 beyond53",Float::new(256),false,true),
    ])
}

pub fn cache_interleaving() -> Value {
    let plan=control_plan();
    // Preserve the four original context positions and exact interleaving order.
    // All use the generic backend; paired positions have independent workspaces.
    let shapes=[false,true,false,true];
    let mut expected=Vec::new();
    for dual in shapes {
        let batch=control_batch(&0f64,dual,false);
        let mut workspace=control_workspace(&plan,0f64,dual);
        let record=observe(&mut workspace,&batch,plan.basis().len(),dual).unwrap();
        assert!(record["stable"].as_bool().unwrap());expected.push(record);
    }
    let mut steps=Vec::new();
    for index in [2usize,1,0,3,2,0,3,1] {
        let dual=shapes[index];
        let batch=control_batch(&0f64,dual,false);
        let mut workspace=control_workspace(&plan,0f64,dual);
        let record=observe(&mut workspace,&batch,plan.basis().len(),dual).unwrap();
        assert_eq!(record,expected[index],"workspace/shape cache interleaving changed complete record");
        steps.push(json!({"workspace_case":index,"backend":"SymbolicaBatch","dual":dual,"result":record}));
    }
    json!({"status":"passed","same_immutable_plan":true,"expected_current_process_records":expected,"steps":steps})
}
