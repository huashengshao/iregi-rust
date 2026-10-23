//! Private adapter v3 contracts: native-valid unsupported jets and N4 scheduling.
use iregi_masters_certified_v3::{
    Complex, LaneError, MasterEvaluator, MasterLane, NativeFloat, ScalarIntegral,
    certified::{AccuracyMasterBatch, AccuracyMasterEvaluator, CertificatePolicy, Formula, MasterAccuracyContext, SeriesStatus},
};
use serde_json::{Value,json};
use std::{error::Error,time::Instant};
use symbolica::domains::{dual::HyperDual,rational::Rational,float::SingleFloat};

fn c(re:f64,im:f64)->Complex<f64>{Complex::new(re,im)}
fn assert_same(actual:MasterLane<'_,f64>,expected:MasterLane<'_,f64>){
    for (a,b) in [actual.uv,actual.ir,actual.ir2,actual.total_single,actual.finite].into_iter()
        .zip([expected.uv,expected.ir,expected.ir2,expected.total_single,expected.finite]){
        assert_eq!(a.len(),b.len());
        for (a,b) in a.iter().zip(b){assert_eq!((a.re.to_bits(),a.im.to_bits()),(b.re.to_bits(),b.im.to_bits()));}
    }
}
fn record(batch:&AccuracyMasterBatch<f64>)->Value{
    json!({"rows":(0..batch.row_count()).map(|lane|{
        let d=&batch.diagnostics()[lane];
        json!({"lane":lane,"error":batch.errors()[lane].as_ref().map(ToString::to_string),"formula":format!("{:?}",d.formula),
            "requested_bits":d.requested_bits,"series_unavailable":d.series_unavailable,"finite_certificate_present":d.finite.is_some(),
            "attempts":d.attempts.iter().map(|a|json!({"order":a.order,"status":format!("{:?}",a.status),"rho":a.rho.as_ref().map(ToString::to_string)})).collect::<Vec<_>>(),
            "finite_values":batch.lane(lane).ok().map(|v|v.finite.iter().map(|x|json!({"real":x.re.exact_rational().unwrap().to_string(),"imaginary":x.im.exact_rational().unwrap().to_string()})).collect::<Vec<_>>())})
    }).collect::<Vec<_>>(),"ordinary_rows":batch.ordinary_rows,
        "series_execution":batch.series_execution.iter().map(|(order,w)|json!({"order":order,"input_rows":w.input_rows,"active_rows":w.active_rows,"numeric_batch_calls":w.numeric_batch_calls,"enclosure_batch_calls":w.enclosure_batch_calls,"tail_batch_calls":w.tail_batch_calls})).collect::<Vec<_>>()})
}

fn main()->Result<(),Box<dyn Error>>{
    let started=Instant::now();let mut args=std::env::args().skip(1);
    let output=args.next().ok_or("usage: contract_validate output.json")?;
    if args.next().is_some(){return Err("unexpected argument".into());}
    let shape:Vec<Vec<usize>>=(0..=5).map(|i|vec![i]).collect();let components=shape.len();let width=11*components;
    let mut vacuum=vec![c(0.,0.);width];
    for argument in 6..11{vacuum[argument*components]=c(1.,0.);}
    vacuum[10*components+1]=c(1.,0.); // mu_squared=1+t; physical kinematics constant.
    let mut upper=vacuum.clone();upper[6*components].im=1.;
    let mut invalid_scale=vacuum.clone();invalid_scale[10*components].re=0.;
    let mut constant=vacuum.clone();constant[10*components+1].re=0.;
    let rows=[vacuum,upper,constant,invalid_scale];
    let input:Vec<_>=rows.iter().flatten().cloned().collect();
    eprintln!("contract: preparing native degree-five D0 shape");
    let ordinary=MasterEvaluator::new_dual(ScalarIntegral::D0,0f64,HyperDual::<Rational>::new(shape.clone()))?;
    let mut legacy=ordinary.clone();let mut adapter=AccuracyMasterEvaluator::new(ordinary);
    let context=MasterAccuracyContext::binary(40,components);
    assert!(adapter.prepared_series_orders().is_empty());
    assert_eq!(adapter.evaluate_batch_with_accuracy(&[],0,&context,CertificatePolicy::RequireFiniteCertificate)?.row_count(),0);
    assert!(adapter.prepared_series_orders().is_empty());
    eprintln!("contract: require unsupported degree-five certificate");
    let required=adapter.evaluate_batch_with_accuracy(&input,rows.len(),&context,CertificatePolicy::RequireFiniteCertificate)?;
    assert!(adapter.prepared_series_orders().is_empty());assert!(required.series_execution.is_empty());assert_eq!(required.ordinary_rows,0);
    for lane in [0,2]{
        assert_eq!(required.errors()[lane],Some(LaneError::UncertifiedFinite(None)));
        assert!(required.lane(lane).is_err());let d=&required.diagnostics()[lane];
        assert_eq!(d.formula,Formula::Rejected);assert!(d.series_unavailable.is_some());assert!(d.finite.is_none());assert!(d.attempts.is_empty());
    }
    assert_eq!(required.errors()[1],Some(LaneError::UpperHalfPlaneMass{argument:6}));
    assert_eq!(required.errors()[3],Some(LaneError::InvalidScale));
    for lane in [1,3]{assert!(required.diagnostics()[lane].series_unavailable.is_none());assert!(required.diagnostics()[lane].finite.is_none());}
    eprintln!("contract: allow unsupported-shape ordinary fallback");
    let allowed=adapter.evaluate_batch_with_accuracy(&input,rows.len(),&context,CertificatePolicy::AllowOrdinaryUncertified)?;
    let reference=legacy.evaluate_batch(&input,rows.len())?;
    assert!(adapter.prepared_series_orders().is_empty());assert!(allowed.series_execution.is_empty());assert_eq!(allowed.ordinary_rows,2);
    assert_eq!(allowed.errors(),reference.errors());
    let rounded_one_sixth=0f64.from_rational(&Rational::from((1,6)));
    for lane in [0,2]{
        let value=allowed.lane(lane).unwrap();assert_same(value,reference.lane(lane).unwrap());
        let d=&allowed.diagnostics()[lane];assert_eq!(d.formula,Formula::OrdinaryUncertified);
        assert!(d.series_unavailable.is_some()&&d.finite.is_none()&&d.attempts.is_empty());
        assert_eq!(value.finite[0].re.to_bits(),rounded_one_sixth.to_bits());assert_eq!(value.finite[0].im,0.);
        assert!(value.finite[1..].iter().all(|x|x.re==0.&&x.im==0.));
        assert!(value.uv.iter().chain(value.ir).chain(value.ir2).chain(value.total_single).all(|x|x.re==0.&&x.im==0.));
    }
    for lane in [1,3]{assert!(allowed.lane(lane).is_err());assert!(allowed.diagnostics()[lane].finite.is_none());}
    let mut reversed=rows.to_vec();reversed.reverse();let reversed:Vec<_>=reversed.into_iter().flatten().collect();
    let reversed=adapter.evaluate_batch_with_accuracy(&reversed,rows.len(),&context,CertificatePolicy::AllowOrdinaryUncertified)?;
    assert!(adapter.prepared_series_orders().is_empty());
    for lane in 0..rows.len(){let other=rows.len()-1-lane;assert_eq!(allowed.errors()[lane],reversed.errors()[other]);
        if let Ok(value)=allowed.lane(lane){assert_same(value,reversed.lane(other).unwrap());}}
    let shape_report=json!({"shape":shape,"mu_squared":"1+t in lane0, 1 in lane2; all physical higher jets zero",
        "mathematical_result":"D0=1/6 at equal unit squared masses and zero external invariants; all higher scale-only coefficients and poles zero",
        "required":record(&required),"allowed":record(&allowed),"prepared_series_orders":adapter.prepared_series_orders(),
        "legacy_all_laurent_components_bitwise_equal":true,"analytic_zero_derivative_and_pole_checks":true,"reversed_batch_equal":true});

    // The already-qualified ordinary fixture from v2, not a new degenerate box.
    let mut outside:Vec<_>=[0.,-4.,-4.,0.,0.,-4.].into_iter().map(|x|c(x,0.)).collect();
    outside.extend((0..4).map(|_|c(2.,-1.)));outside.push(c(1.,0.));
    let outside=outside.repeat(3); // odd-size, all-outside batch.
    let ordinary=MasterEvaluator::new(ScalarIntegral::D0,0f64)?;
    let mut legacy=ordinary.clone();let mut adapter=AccuracyMasterEvaluator::new(ordinary);
    let context=MasterAccuracyContext::binary(40,1);
    eprintln!("contract: all-outside batch must not prepare N4");
    let required=adapter.evaluate_batch_with_accuracy(&outside,3,&context,CertificatePolicy::RequireFiniteCertificate)?;
    assert_eq!(adapter.prepared_series_orders(),vec![2]);assert_eq!(required.ordinary_rows,0);assert_eq!(required.series_execution.len(),1);
    let (order,work)=&required.series_execution[0];assert_eq!(*order,2);assert_eq!(work.input_rows,3);assert_eq!(work.active_rows,0);
    assert_eq!(work.numeric_batch_calls,0);assert_eq!(work.enclosure_batch_calls,0);assert_eq!(work.tail_batch_calls,0);
    for lane in 0..3{
        assert!(required.lane(lane).is_err());let d=&required.diagnostics()[lane];assert!(d.finite.is_none());assert_eq!(d.attempts.len(),1);
        assert_eq!(d.attempts[0].order,2);assert_eq!(d.attempts[0].status,SeriesStatus::OutsideAnalyticDomain);
        assert_eq!(d.attempts[0].rho,Some(Rational::from((3,4))));
    }
    let allowed=adapter.evaluate_batch_with_accuracy(&outside,3,&context,CertificatePolicy::AllowOrdinaryUncertified)?;
    let reference=legacy.evaluate_batch(&outside,3)?;
    assert_eq!(adapter.prepared_series_orders(),vec![2]);assert_eq!(allowed.ordinary_rows,3);assert_eq!(allowed.series_execution.len(),1);
    assert_eq!(allowed.errors(),reference.errors());
    for lane in 0..3{
        assert_same(allowed.lane(lane).unwrap(),reference.lane(lane).unwrap());let d=&allowed.diagnostics()[lane];
        assert_eq!(d.formula,Formula::OrdinaryUncertified);assert!(d.finite.is_none());assert_eq!(d.attempts.len(),1);assert_eq!(d.attempts[0].order,2);
    }
    let report=json!({"status":"private_v3_contract_checks_passed","numeric":"f64","working_bits":53,"requested_bits":40,
        "unsupported_native_shape":shape_report,
        "all_outside_domain":{"fixture":"p=[0,-4,-4,0,0,-4], all m_squared=2-i, mu_squared=1; repeated three times",
            "required":record(&required),"allowed":record(&allowed),"prepared_series_orders":adapter.prepared_series_orders(),
            "no_N4_preparation_or_execution":true,"legacy_all_laurent_components_bitwise_equal":true},
        "diagnostic_seconds":started.elapsed().as_secs_f64(),
        "scope":"Private v3 adapter policy and scheduling contracts. Ordinary successes are explicitly uncertified, including degree-five scale-only jets. Production unchanged; no new physical, accuracy, E6, or performance qualification."});
    let text=serde_json::to_string_pretty(&report)?+"\n";std::fs::write(output,&text)?;print!("{text}");Ok(())
}
