//! Private adapter comparison at one exact contour probe; no E6 quadrature.
use iregi_masters_certified::{
    MasterEvaluator, NativeFloat, ScalarIntegral,
    certified::{AccuracyMasterEvaluator, CertificatePolicy, Formula, MasterAccuracyContext},
};
use serde_json::{Value, json};
use std::{error::Error, path::PathBuf, time::Instant};
use symbolica::{
    atom::{Atom, AtomCore},
    domains::{
        float::{Complex, ComplexBall, Float, RealBall, SingleFloat},
        integer::Integer,
        rational::Rational,
    },
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

fn run()->Result<u8,Box<dyn Error>>{
    let started=Instant::now();let mut args=std::env::args_os().skip(1);
    let oracle_path=PathBuf::from(args.next().ok_or("usage: five_pinch_compare oracle.json [output.json]")?);
    let output=args.next().map(PathBuf::from);
    if args.next().is_some(){return Err("unexpected argument".into());}
    let oracle:Value=serde_json::from_str(&std::fs::read_to_string(&oracle_path)?)?;
    if oracle["status"]!="exact_five_pinch_oracle_generated"||oracle["fixture"]["x_exact_rational"]!="1/2"{
        return Err("unexpected oracle fixture".into());
    }
    let boxes=oracle["boxes"].as_array().ok_or("missing box oracles")?;
    let coefficient_json=oracle["geometry"]["C_i_at_t"].as_array().ok_or("missing exact coefficients")?;
    if boxes.len()!=5||coefficient_json.len()!=5{return Err("oracle must contain five pinches".into());}
    let coefficients:Vec<_>=coefficient_json.iter().map(point).collect::<Result<_,_>>()?;
    let mut input_exact=Vec::new();
    for (pinch,row) in boxes.iter().enumerate(){
        if row["pinch"].as_u64()!=Some(pinch as u64){return Err("unexpected pinch ordering".into());}
        let input=row["inputs"].as_array().ok_or("missing exact box inputs")?;
        if input.len()!=11{return Err("box arity must be eleven".into());}
        input_exact.extend(input.iter().map(point).collect::<Result<Vec<_>,_>>()?);
    }
    let prototype=Float::new(WORKING_BITS);
    let input:Vec<_>=input_exact.iter().map(|value|numeric(value,&prototype)).collect();
    for (given,value) in input_exact.iter().zip(&input){if *given!=represented(value)?{return Err("fixture input was rounded".into());}}
    let context=MasterAccuracyContext::binary(REQUESTED_BITS,1);
    let ordinary=MasterEvaluator::new(ScalarIntegral::D0,prototype.clone())?;
    let mut adapter=AccuracyMasterEvaluator::new(ordinary);
    let batch=adapter.evaluate_batch_with_accuracy(&input,5,&context,CertificatePolicy::RequireFiniteCertificate)?;
    let errors:Vec<_>=batch.errors().iter().map(|error|error.as_ref().map(ToString::to_string)).collect();
    if errors.iter().any(Option::is_some){
        emit(&json!({"status":"adapter_rejected","errors":errors,"values":null,"working_bits":WORKING_BITS,"requested_bits":REQUESTED_BITS}),&output)?;
        return Ok(2);
    }
    if batch.row_count()!=5||batch.component_count()!=1||batch.ordinary_rows!=0{return Err("unexpected adapter execution layout".into());}
    let mut box_values=Vec::new();let mut box_rectangles=Vec::new();let mut reports=Vec::new();let mut passed=true;
    for (pinch,reference) in boxes.iter().enumerate(){
        let lane=batch.lane(pinch).map_err(Clone::clone)?;
        let poles_zero=lane.uv.iter().chain(lane.ir).chain(lane.ir2).chain(lane.total_single)
            .all(|v|v.re.is_zero()&&v.im.is_zero());
        if !poles_zero||lane.finite.len()!=1{return Err("finite analytic box returned poles or wrong shape".into());}
        let diagnostic=&batch.diagnostics()[pinch];
        if !matches!(diagnostic.formula,Formula::NearVacuum{..}){return Err("missing certified series dispatch".into());}
        let bounds=diagnostic.finite.as_ref().ok_or("missing finite certificate")?;
        if bounds.len()!=1{return Err("incomplete finite certificate".into());}
        let bound=&bounds[0];
        let rectangle=Rectangle{rl:bound.real_lower.clone(),ru:bound.real_upper.clone(),il:bound.imaginary_lower.clone(),iu:bound.imaginary_upper.clone()};
        let value=represented(&lane.finite[0])?;
        if rectangle.farthest_squared(&value)!=bound.maximum_error_squared||budget(&value)!=bound.allowed_error_squared{
            return Err("adapter certificate metadata disagrees with exact recomputation".into());
        }
        let (good,comparison)=compare(&value,&rectangle,&reference["oracle"])?;passed&=good;
        reports.push(json!({"pinch":pinch,"formula":format!("{:?}",diagnostic.formula),"requested_bits":diagnostic.requested_bits,
            "attempts":diagnostic.attempts.iter().map(|attempt|json!({"order":attempt.order,"status":format!("{:?}",attempt.status),"rho":attempt.rho.as_ref().map(ToString::to_string)})).collect::<Vec<_>>(),
            "poles_exactly_zero":poles_zero,"truncation_radius":bound.truncation.to_string(),"comparison":comparison}));
        box_values.push(lane.finite[0].clone());box_rectangles.push(rectangle);
    }

    // One Symbolica program is mapped to both numerical and outward-rounded
    // ball domains. Coefficients are exact Matrix-derived rationals from the
    // independent oracle; box rectangles already include their series tails.
    let parameters:Vec<_>=(0..10).map(|i|Atom::var(symbolica::symbol!(format!("iregi_five_pinch_compare::a{i}")))).collect();
    let expression:Atom=(0..5).map(|i|&parameters[i]*&parameters[5+i]).sum();
    let exact_program:ExpressionEvaluator<Exact>=expression.evaluator(&parameters).direct_translation(true).horner_iterations(0).cores(1).build()?;
    let mut numeric_program=exact_program.clone().map_coeff_with_prec(&|x|numeric(x,&prototype),WORKING_BITS).into_batch_evaluator();
    let mut ball_program=exact_program.map_coeff_with_prec(&|x|ComplexBall::from_rational_ball(x,&Rational::from(0),WORKING_BITS),WORKING_BITS).into_batch_evaluator();
    let numeric_inputs:Vec<_>=coefficients.iter().map(|x|numeric(x,&prototype)).chain(box_values).collect();
    let ball_inputs:Vec<_>=coefficients.iter().map(|x|ComplexBall::from_rational_ball(x,&Rational::from(0),WORKING_BITS))
        .chain(box_rectangles.iter().map(Rectangle::ball)).collect();
    let mut numeric_output=vec![numeric(&zero(),&prototype)];
    let mut ball_output=vec![ComplexBall::from_rational_ball(&zero(),&Rational::from(0),WORKING_BITS)];
    numeric_program.evaluate_batch(&numeric_inputs,&mut numeric_output,1)?;
    ball_program.evaluate_batch(&ball_inputs,&mut ball_output,1)?;
    let contraction_value=represented(&numeric_output[0])?;
    let contraction_rectangle=Rectangle::from_ball(&ball_output[0])?;
    let (contraction_passed,contraction_report)=compare(&contraction_value,&contraction_rectangle,&oracle["independent_direct_J5_D4"])?;
    passed&=contraction_passed;
    let execution:Vec<_>=batch.series_execution.iter().map(|(order,work)|json!({"order":order,"input_rows":work.input_rows,
        "active_rows":work.active_rows,"numeric_batch_calls":work.numeric_batch_calls,"enclosure_batch_calls":work.enclosure_batch_calls,
        "tail_batch_calls":work.tail_batch_calls,"estimated_exported_instruction_lane_visits":work.estimated_exported_instruction_lane_visits})).collect();
    emit(&json!({"status":if passed{"five_pinch_adapter_and_contraction_passed"}else{"accuracy_not_certified"},
        "working_bits":WORKING_BITS,"requested_bits":REQUESTED_BITS,"accuracy_rule":"error_squared <= 2^-256 * max(1, |returned_value|^2)",
        "oracle_input":oracle_path,"input_preservation":"All 55 complex input values exactly equal their rational fixtures after Float256 conversion",
        "policy":"RequireFiniteCertificate","ordinary_rows":batch.ordinary_rows,"series_execution":execution,
        "boxes":reports,"five_box_contraction_vs_independent_J5_D4":contraction_report,
        "contraction_program":expression.to_string(),"contraction_backend":"Same Symbolica rational program mapped to Float256 and ComplexBall256; exact coefficient point enclosures and full D0 rectangles",
        "contour_probe":oracle["fixture"],"diagnostic_seconds":started.elapsed().as_secs_f64(),
        "scope":"Private adapter and exact x=1/2 five-pinch contraction only. Fixed exact shifted inputs and exact Cayley coefficients eliminate upstream geometry/shift uncertainty. No Gauss nodes, rule weights, quadrature truncation, E6 public execution, derivative, or performance qualification."}),&output)?;
    Ok(if passed{0}else{3})
}
fn main()->std::process::ExitCode{match run(){Ok(code)=>std::process::ExitCode::from(code),Err(error)=>{eprintln!("{error}");std::process::ExitCode::FAILURE}}}
