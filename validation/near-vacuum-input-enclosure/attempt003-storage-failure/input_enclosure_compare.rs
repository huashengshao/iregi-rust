//! Private contour-input enclosure experiment; no production or E6 quadrature.
#[path="source/near_vacuum.rs"]
mod near_vacuum;
use near_vacuum::{AccuracyContext, InputRectangle, NearVacuumPlan, Status};
use oneloop::NativeFloat;
use serde_json::{Value, json};
use std::{error::Error, path::PathBuf, time::Instant};
use symbolica::{
    atom::{Atom, AtomCore},
    domains::{float::{Complex, ComplexBall, Float, RealBall, SingleFloat}, integer::Integer, rational::Rational},
    evaluate::ExpressionEvaluator,
};
type Exact=Complex<Rational>;
const WORKING_BITS:u32=256;
const REQUESTED_BITS:u32=128;

fn number(value:&Value)->Result<Rational,Box<dyn Error>> {
    let text=value.as_str().ok_or("expected exact rational string")?;
    let (n,d)=text.split_once('/').unwrap_or((text,"1"));
    let d=d.parse::<Integer>()?;
    if d==Integer::from(0){return Err("zero rational denominator".into());}
    Ok(Rational::from((n.parse::<Integer>()?,d)))
}
fn point(value:&Value)->Result<Exact,Box<dyn Error>> {
    Ok(Complex::new(number(&value["real_exact_rational"])?,number(&value["imaginary_exact_rational"])?))
}
fn zero()->Exact{Complex::new(Rational::from(0),Rational::from(0))}
fn abs(value:&Rational)->Rational{if value<&Rational::from(0){-value.clone()}else{value.clone()}}
fn encode(value:&Exact)->Value{json!({"real_exact_rational":value.re.to_string(),"imaginary_exact_rational":value.im.to_string()})}
fn represented(value:&Complex<Float>)->Result<Exact,Box<dyn Error>>{
    Ok(Complex::new(value.re.exact_rational().ok_or("nonfinite real output")?,value.im.exact_rational().ok_or("nonfinite imaginary output")?))
}
fn numeric(value:&Exact,prototype:&Float)->Complex<Float>{
    Complex::new(prototype.from_rational(&value.re),prototype.from_rational(&value.im))
}
fn budget(value:&Exact)->Rational{
    let eps=Rational::from((Integer::from(1),Integer::from(2).pow(u64::from(REQUESTED_BITS))));
    eps.pow(2)*(value.re.pow(2)+value.im.pow(2)).max(Rational::from(1))
}

#[derive(Clone)]
struct Rectangle {rl:Rational,ru:Rational,il:Rational,iu:Rational}
impl Rectangle {
    fn from_ball(ball:&ComplexBall)->Result<Self,Box<dyn Error>>{
        Ok(Self{rl:ball.re.lower_bound().exact_rational().ok_or("nonfinite rectangle")?,
            ru:ball.re.upper_bound().exact_rational().ok_or("nonfinite rectangle")?,
            il:ball.im.lower_bound().exact_rational().ok_or("nonfinite rectangle")?,
            iu:ball.im.upper_bound().exact_rational().ok_or("nonfinite rectangle")?})
    }
    fn ball(&self)->ComplexBall{
        Complex::new(RealBall::from_rational_bounds(&self.rl,&self.ru,WORKING_BITS),
            RealBall::from_rational_bounds(&self.il,&self.iu,WORKING_BITS))
    }
    fn farthest_squared(&self,center:&Exact)->Rational{
        abs(&(&center.re-&self.rl)).max(abs(&(&center.re-&self.ru))).pow(2)
            +abs(&(&center.im-&self.il)).max(abs(&(&center.im-&self.iu))).pow(2)
    }
    fn report(&self)->Value{json!({"real":[self.rl.to_string(),self.ru.to_string()],"imaginary":[self.il.to_string(),self.iu.to_string()]})}
}

fn compare(value:&Exact,rectangle:&Rectangle,oracle:&Value)->Result<(bool,Value),Box<dyn Error>>{
    let center=point(&oracle["center"])?;
    let radius=number(&oracle["absolute_complex_remainder_bound_exact_rational"])?;
    if radius<Rational::from(0)||rectangle.rl>rectangle.ru||rectangle.il>rectangle.iu{return Err("invalid enclosure".into());}
    let error_upper=(abs(&(&value.re-&center.re))+&radius).pow(2)+(abs(&(&value.im-&center.im))+&radius).pow(2);
    let rectangle_error_upper=(abs(&(&rectangle.rl-&center.re)).max(abs(&(&rectangle.ru-&center.re)))+&radius).pow(2)
        +(abs(&(&rectangle.il-&center.im)).max(abs(&(&rectangle.iu-&center.im)))+&radius).pow(2);
    let lower_re=(&center.re-&radius).max(rectangle.rl.clone());
    let upper_re=(&center.re+&radius).min(rectangle.ru.clone());
    let lower_im=(&center.im-&radius).max(rectangle.il.clone());
    let upper_im=(&center.im+&radius).min(rectangle.iu.clone());
    let overlap=lower_re<=upper_re&&lower_im<=upper_im;
    let oracle_contained=rectangle.rl<=&center.re-&radius&&rectangle.ru>=&center.re+&radius
        &&rectangle.il<=&center.im-&radius&&rectangle.iu>=&center.im+&radius;
    let allowed=budget(value);
    let certified=rectangle.farthest_squared(value);
    let passed=error_upper<=allowed&&rectangle_error_upper<=allowed&&certified<=allowed&&overlap;
    Ok((passed,json!({"numeric_value":encode(value),"candidate_rectangle":rectangle.report(),"oracle_center":encode(&center),
        "oracle_radius":radius.to_string(),"numeric_error_squared_upper":error_upper.to_string(),
        "entire_candidate_rectangle_error_squared_upper":rectangle_error_upper.to_string(),
        "numeric_to_candidate_rectangle_error_squared_upper":certified.to_string(),"allowed_error_squared":allowed.to_string(),
        "candidate_and_oracle_rectangles_overlap":overlap,"oracle_rectangle_contained_in_candidate":oracle_contained,
        "all_bounds_within_requested_budget":passed})))
}

fn emit(report:&Value,output:&Option<PathBuf>)->Result<(),Box<dyn Error>>{
    let encoded=serde_json::to_string_pretty(report)?+"\n";
    if let Some(output)=output{std::fs::write(output,&encoded)?;}
    print!("{encoded}");Ok(())
}

fn execution(value:&near_vacuum::Execution)->Value {
    json!({"input_rows":value.input_rows,"active_rows":value.active_rows,
        "numeric_batch_calls":value.numeric_batch_calls,"enclosure_batch_calls":value.enclosure_batch_calls,
        "tail_batch_calls":value.tail_batch_calls,"estimated_exported_instruction_lane_visits":value.estimated_exported_instruction_lane_visits})
}
fn bound_rectangle(bound:&near_vacuum::ComponentBound)->Rectangle {
    Rectangle{rl:bound.real_lower.clone(),ru:bound.real_upper.clone(),il:bound.imaginary_lower.clone(),iu:bound.imaginary_upper.clone()}
}
fn run()->Result<u8,Box<dyn Error>> {
    let started=Instant::now();let mut args=std::env::args_os().skip(1);
    let oracle_path=PathBuf::from(args.next().ok_or("usage: input_enclosure_compare oracle.json [output.json]")?);
    let output=args.next().map(PathBuf::from);
    if args.next().is_some(){return Err("unexpected argument".into());}
    let oracle:Value=serde_json::from_str(&std::fs::read_to_string(&oracle_path)?)?;
    if oracle["status"]!="exact_five_pinch_oracle_generated"||oracle["fixture"]["x_exact_rational"]!="2/5" {
        return Err("unexpected non-dyadic oracle fixture".into());
    }
    let boxes=oracle["boxes"].as_array().ok_or("missing boxes")?;
    if boxes.len()!=5{return Err("expected five pinches".into());}
    let prototype=Float::new(WORKING_BITS);
    let x_symbol=symbolica::symbol!("iregi_input_enclosure::x");
    let x_atom=Atom::var(x_symbol);
    let direction=Atom::var(symbolica::symbol!("iregi_input_enclosure::direction"));
    let b:Vec<_>=(0..5).map(|i|Atom::var(symbolica::symbol!(format!("iregi_input_enclosure::b{i}")))).collect();
    let b_sum=Atom::var(symbolica::symbol!("iregi_input_enclosure::B"));
    let t=&direction*&x_atom/(Atom::num(1)-&x_atom);
    let jacobian=t.derivative(x_symbol);
    let mut expressions=vec![t.clone(),Atom::num(1)+&t,jacobian.clone()];
    expressions.extend(b.iter().map(|value|value/(Atom::num(1)-Atom::num(2)*&t*&b_sum)));
    let parameters:Vec<_>=vec![x_atom,direction].into_iter().chain(b).chain([b_sum]).collect();
    let mut exact_inputs=vec![Complex::new(number(&oracle["fixture"]["x_exact_rational"])?,Rational::from(0)),point(&oracle["fixture"]["contour_direction"])?];
    exact_inputs.extend(oracle["geometry"]["b_exact_rational"].as_array().ok_or("missing b")?.iter().map(|v|number(v).map(|r|Complex::new(r,Rational::from(0)))).collect::<Result<Vec<_>,_>>()?);
    exact_inputs.push(Complex::new(number(&oracle["geometry"]["B_exact_rational"])?,Rational::from(0)));
    if exact_inputs.len()!=8{return Err("invalid contour input arity".into());}
    let contour_program:ExpressionEvaluator<Exact>=Atom::evaluator_multiple(&expressions,&parameters)
        .direct_translation(true).horner_iterations(0).cores(1).build()?;
    let mut contour_numeric=contour_program.clone().map_coeff_with_prec(&|v|numeric(v,&prototype),WORKING_BITS).into_batch_evaluator();
    let mut contour_balls=contour_program.map_coeff_with_prec(&|v|ComplexBall::from_rational_ball(v,&Rational::from(0),WORKING_BITS),WORKING_BITS).into_batch_evaluator();
    let numeric_contour_inputs:Vec<_>=(0..5).flat_map(|_|exact_inputs.iter().map(|v|numeric(v,&prototype))).collect();
    let ball_contour_inputs:Vec<_>=(0..5).flat_map(|_|exact_inputs.iter().map(|v|ComplexBall::from_rational_ball(v,&Rational::from(0),WORKING_BITS))).collect();
    let mut contour_values=vec![numeric(&zero(),&prototype);40];
    let mut contour_bounds=vec![ComplexBall::from_rational_ball(&zero(),&Rational::from(0),WORKING_BITS);40];
    contour_numeric.evaluate_batch(&numeric_contour_inputs,&mut contour_values,5)?;
    contour_balls.evaluate_batch(&ball_contour_inputs,&mut contour_bounds,5)?;
    let intended_mass=point(&oracle["fixture"]["common_shifted_mass_squared"])?;
    let intended_t=point(&oracle["fixture"]["t"])?;
    let intended_jacobian=point(&oracle["mapped_integrand_at_x"]["dt_dx"])?;
    let intended_coefficients:Vec<_>=oracle["geometry"]["C_i_at_t"].as_array().ok_or("missing C")?.iter().map(point).collect::<Result<_,_>>()?;
    let mut input=Vec::new();let mut rectangles=Vec::new();let mut shifted_inputs_rounded=0usize;
    let mut contour_reports=Vec::new();
    for (pinch,row) in boxes.iter().enumerate() {
        if row["pinch"].as_u64()!=Some(pinch as u64){return Err("unexpected pinch ordering".into());}
        let physical=row["inputs"].as_array().ok_or("missing box inputs")?;
        if physical.len()!=11{return Err("incorrect box arity".into());}
        let mut contour_components=Vec::new();
        for j in 0..8 {
            let intended=match j {0=>&intended_t,1=>&intended_mass,2=>&intended_jacobian,_=>&intended_coefficients[j-3]};
            let enclosure=InputRectangle::from_ball(&contour_bounds[8*pinch+j]).ok_or("nonfinite contour enclosure")?;
            if !enclosure.contains(intended)||!enclosure.contains(&represented(&contour_values[8*pinch+j])?) {
                return Err("contour program failed to enclose intended and represented outputs".into());
            }
            contour_components.push(json!({"index":j,"role":match j {0=>"contour_t",1=>"shifted_mass_squared",2=>"dt_dx",_=>"coefficient_update"},
                "intended":encode(intended),"represented":encode(&represented(&contour_values[8*pinch+j])?),
                "rectangle":Rectangle::from_ball(&contour_bounds[8*pinch+j])?.report()}));
        }
        for argument in 0..10 {
            let intended=point(&physical[argument])?;
            let (value,enclosure)=if argument<6 {
                (numeric(&intended,&prototype),InputRectangle::exact(&intended))
            } else {
                (contour_values[8*pinch+1].clone(),InputRectangle::from_ball(&contour_bounds[8*pinch+1]).ok_or("nonfinite mass enclosure")?)
            };
            if argument>=6&&represented(&value)?!=intended {shifted_inputs_rounded+=1;}
            if !enclosure.contains(&intended)||!enclosure.contains(&represented(&value)?) {return Err("physical input enclosure lost its intended or represented point".into());}
            input.push(value);rectangles.push(enclosure);
        }
        contour_reports.push(json!({"pinch":pinch,"components":contour_components,"intended_mass":encode(&intended_mass),
            "represented_mass":encode(&represented(&contour_values[8*pinch+1])?),
            "mass_enclosure":Rectangle::from_ball(&contour_bounds[8*pinch+1])?.report(),
            "coefficient_enclosure":Rectangle::from_ball(&contour_bounds[8*pinch+3+pinch])?.report(),
            "all_eight_outputs_contain_exact_oracle_values_and_represented_outputs":true}));
    }
    if shifted_inputs_rounded!=20{return Err("non-dyadic fixture failed to exercise all shifted-mass rounding".into());}
    eprintln!("contour preparation and physical-input enclosures ready: {:?}",started.elapsed());
    let context=AccuracyContext::binary(REQUESTED_BITS,1);
    let plan=NearVacuumPlan::new(2,vec![vec![]])?;
    let mut workspace=plan.instantiate(prototype.clone());
    eprintln!("N2 plan ready: {:?}",started.elapsed());
    let mut mixed_input=input.clone();let mut mixed_rectangles=rectangles.clone();
    for _ in 0..4 {mixed_input.extend_from_slice(&input[..10]);mixed_rectangles.extend_from_slice(&rectangles[..10]);}
    // Same numerical points, but four distinct enclosure faults. All hide values.
    let wide=near_vacuum::pow2_minus(80);
    mixed_rectangles[5*10+6].real_lower-=&wide;mixed_rectangles[5*10+6].real_upper+=&wide;
    mixed_rectangles[6*10+6].imaginary_upper=Rational::from(1);
    let excluded=represented(&mixed_input[7*10+6])?.re+&wide;
    mixed_rectangles[7*10+6].real_lower=excluded.clone();mixed_rectangles[7*10+6].real_upper=excluded;
    mixed_rectangles[8*10].imaginary_lower=-wide.clone();mixed_rectangles[8*10].imaginary_upper=wide;
    let lanes=workspace.evaluate_batch_enclosed(&mixed_input,9,&context,&mixed_rectangles)?;
    let primary_execution=execution(&workspace.execution);
    if lanes.len()!=9{return Err("incorrect mixed lane count".into());}
    let controls:Vec<_>=(5..9).map(|lane| {
        let argument=if lane==8{0}else{6};let bound=&mixed_rectangles[lane*10+argument];
        Ok(json!({"lane":lane,"status":format!("{:?}",lanes[lane].status),"values_hidden":lanes[lane].values.is_none(),
            "affected_argument":argument,"represented_input":encode(&represented(&mixed_input[lane*10+argument])?),
            "input_rectangle":{"real":[bound.real_lower.to_string(),bound.real_upper.to_string()],"imaginary":[bound.imaginary_lower.to_string(),bound.imaginary_upper.to_string()]}}))
    }).collect::<Result<Vec<_>,Box<dyn Error>>>()?;
    if !matches!(lanes[5].status,Status::UncertifiedComponent(0))||lanes[5].values.is_some()
        ||(6..9).any(|i|!matches!(lanes[i].status,Status::InvalidInput(_))||lanes[i].values.is_some()) {
        emit(&json!({"status":"rejection_control_failed","controls":controls}),&output)?;return Ok(2);
    }
    let reverse_input:Vec<_>=mixed_input.chunks_exact(10).rev().flat_map(|row|row.iter().cloned()).collect();
    let reverse_rectangles:Vec<_>=mixed_rectangles.chunks_exact(10).rev().flat_map(|row|row.iter().cloned()).collect();
    let mut reverse_workspace=plan.instantiate(prototype.clone());
    let reverse=reverse_workspace.evaluate_batch_enclosed(&reverse_input,9,&context,&reverse_rectangles)?;
    for (a,b) in lanes.iter().zip(reverse.iter().rev()) {
        if a.status!=b.status||a.values!=b.values||a.bounds.len()!=b.bounds.len()
            ||a.bounds.iter().zip(&b.bounds).any(|(a,b)|a.maximum_error_squared!=b.maximum_error_squared||a.real_lower!=b.real_lower||a.real_upper!=b.real_upper||a.imaginary_lower!=b.imaginary_lower||a.imaginary_upper!=b.imaginary_upper) {
            return Err("reversed independent workspace changed values/status/enclosure".into());
        }
    }
    if !reverse_workspace.evaluate_batch_enclosed(&[],0,&context,&[])?.is_empty(){return Err("empty batch produced lanes".into());}
    if reverse_workspace.evaluate_batch_enclosed(&input,5,&context,&rectangles[..49]).is_ok(){return Err("incorrect rectangle length accepted".into());}
    let mut reports=Vec::new();let mut passed=true;let mut box_values=Vec::new();let mut box_bounds=Vec::new();
    for (pinch,reference) in boxes.iter().enumerate() {
        let lane=&lanes[pinch];
        if lane.status!=Status::Success {
            emit(&json!({"status":"candidate_rejected","pinch":pinch,"candidate_status":format!("{:?}",lane.status),"values":null,"execution":primary_execution}),&output)?;return Ok(3);
        }
        let values=lane.values.as_ref().ok_or("successful lane hid value")?;
        if values.len()!=1||lane.bounds.len()!=1{return Err("wrong component count".into());}
        let value=represented(&values[0])?;let bound=&lane.bounds[0];let rectangle=bound_rectangle(bound);
        if rectangle.farthest_squared(&value)!=bound.maximum_error_squared||budget(&value)!=bound.allowed_error_squared{return Err("certificate metadata mismatch".into());}
        let (good,comparison)=compare(&value,&rectangle,&reference["oracle"])?;passed&=good;
        reports.push(json!({"pinch":pinch,"status":"Success","order":2,"truncation_radius":bound.truncation.to_string(),
            "rho":lane.rho.as_ref().map(ToString::to_string),"comparison":comparison}));
        box_values.push(values[0].clone());box_bounds.push(rectangle);
    }
    // Approximate coefficient and dt/dx outputs enter the same Symbolica
    // contraction mapped to Float and Numerica. No exact oracle substitutions.
    let contraction_parameters:Vec<_>=(0..11).map(|i|Atom::var(symbolica::symbol!(format!("iregi_input_enclosure::a{i}")))).collect();
    let contraction:Atom=(0..5).map(|i|&contraction_parameters[i]*&contraction_parameters[5+i]).sum();
    let mapped=&contraction*&contraction_parameters[10];
    let exact_program:ExpressionEvaluator<Exact>=Atom::evaluator_multiple(&[contraction.clone(),mapped.clone()],&contraction_parameters)
        .direct_translation(true).horner_iterations(0).cores(1).build()?;
    let mut numeric_program=exact_program.clone().map_coeff_with_prec(&|v|numeric(v,&prototype),WORKING_BITS).into_batch_evaluator();
    let mut ball_program=exact_program.map_coeff_with_prec(&|v|ComplexBall::from_rational_ball(v,&Rational::from(0),WORKING_BITS),WORKING_BITS).into_batch_evaluator();
    let numeric_inputs:Vec<_>=(0..5).map(|i|contour_values[i*8+3+i].clone()).chain(box_values).chain([contour_values[2].clone()]).collect();
    let ball_inputs:Vec<_>=(0..5).map(|i|contour_bounds[i*8+3+i].clone()).chain(box_bounds.iter().map(Rectangle::ball)).chain([contour_bounds[2].clone()]).collect();
    let mut numeric_output=vec![numeric(&zero(),&prototype);2];
    let mut ball_output=vec![ComplexBall::from_rational_ball(&zero(),&Rational::from(0),WORKING_BITS);2];
    numeric_program.evaluate_batch(&numeric_inputs,&mut numeric_output,1)?;
    ball_program.evaluate_batch(&ball_inputs,&mut ball_output,1)?;
    let mut contraction_reports=Vec::new();
    for (index,reference) in [&oracle["independent_direct_J5_D4"],&oracle["mapped_integrand_at_x"]].into_iter().enumerate() {
        let value=represented(&numeric_output[index])?;let enclosure=Rectangle::from_ball(&ball_output[index])?;
        let (good,comparison)=compare(&value,&enclosure,reference)?;passed&=good;contraction_reports.push(comparison);
    }
    // Exact vacuum with zero represented mass jets, but intervals containing
    // a nonzero common-mass derivative. For D0=1/[6(1+u)^2], coefficient u^3
    // is -2/3. The N2 tail must enclose it even when nominal rho is exactly0.
    let jet_plan=NearVacuumPlan::new(2,vec![vec![0],vec![1],vec![2],vec![3]])?;
    let mut jet_workspace=jet_plan.instantiate(prototype.clone());
    let mut jet_exact=vec![zero();80];
    for row in 0..2 {for mass in 6..10 {jet_exact[row*40+mass*4]=Complex::new(Rational::from(1),Rational::from(0));}}
    let jet_input:Vec<_>=jet_exact.iter().map(|v|numeric(v,&prototype)).collect();
    let mut jet_bounds:Vec<_>=jet_exact.iter().map(InputRectangle::exact).collect();
    for mass in 6..10 {jet_bounds[40+mass*4+1].real_lower=Rational::from(-1);jet_bounds[40+mass*4+1].real_upper=Rational::from(1);}
    let jet_lanes=jet_workspace.evaluate_batch_enclosed(&jet_input,2,&AccuracyContext::binary(REQUESTED_BITS,4),&jet_bounds)?;
    if jet_lanes[0].status!=Status::Success||!matches!(jet_lanes[1].status,Status::UncertifiedComponent(_))
        ||jet_lanes[1].values.is_some()||jet_lanes[1].bounds.len()!=4||jet_lanes[1].rho!=Some(Rational::from(0))
        ||jet_lanes[1].bounds[3].truncation<Rational::from((2,3)) {
        return Err("exact-vacuum jet-uncertainty tail control failed".into());
    }
    let jet_control=json!({"shape":[[0],[1],[2],[3]],"input_rows":2,"nominal_first_mass_jets":"0",
        "uncertain_first_mass_jets":"[-1,1] for each of four masses", "exact_point_status":format!("{:?}",jet_lanes[0].status),
        "uncertain_status":format!("{:?}",jet_lanes[1].status),"uncertain_values_hidden":true,"rho_exactly_zero":true,"uncertain_rho":jet_lanes[1].rho.as_ref().map(ToString::to_string),
        "independent_common_mass_third_coefficient":"-2/3","uncertain_third_component_truncation":jet_lanes[1].bounds[3].truncation.to_string(),
        "execution":execution(&jet_workspace.execution)});
    emit(&json!({"status":if passed{"non_dyadic_input_enclosure_passed"}else{"accuracy_not_certified"},
        "working_bits":WORKING_BITS,"requested_bits":REQUESTED_BITS,"oracle_input":oracle_path,
        "input_uncertainty":"Exact x=2/5 and exact unshifted Cayley coefficients converted outward, then all contour/shift/coefficient/normalization arithmetic evaluated with Numerica ComplexBall256",
        "rounded_shifted_mass_components":shifted_inputs_rounded,"rounded_mass_count_meaning":"20 complex mass argument slots, four copies in each of five boxes","contour_outputs":contour_reports,
        "contour_execution":{"rows":5,"numeric_batch_calls":1,"enclosure_batch_calls":1,"output_components_per_row":8},
        "series_execution":primary_execution,"rejection_controls":controls,
        "reversed_independent_workspace_identical":true,"empty_batch_passed":true,"incorrect_rectangle_length_rejected":true,
        "boxes":reports,"exact_vacuum_jet_uncertainty_control":jet_control,"five_box_contraction_vs_independent_J5_D4":contraction_reports[0],
        "mapped_integrand_vs_independent_oracle":contraction_reports[1],
        "contraction_expressions":[contraction.to_string(),mapped.to_string()],"diagnostic_seconds":started.elapsed().as_secs_f64(),
        "scope":"Private primal N2 input-enclosure experiment at one exact non-dyadic contour point, including shifted-input rounding, coefficient update, contraction and contour Jacobian. Exact unshifted Cayley geometry is supplied. No production master/reduction changes, general geometry certificate, Gauss nodes/weights, quadrature tail, E6 result, mixed-jet interval validation, or performance qualification."}),&output)?;
    Ok(if passed{0}else{4})
}
fn main()->std::process::ExitCode {match run(){Ok(code)=>std::process::ExitCode::from(code),Err(error)=>{eprintln!("{error}");std::process::ExitCode::FAILURE}}}
