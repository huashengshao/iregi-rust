//! Optional private observation; no numeric or symbolic transformation.
use iregi_masters::{MasterBackend, MasterBatch, MasterError, NativeFloat};
use serde::Serialize;
use std::sync::{Mutex, atomic::{AtomicBool, Ordering}};
use symbolica::domains::float::Complex;

#[derive(Clone, Debug, Serialize)]
pub struct Number {
    rational: Option<String>,
    precision: u32,
    negative_sign: bool,
    finite: bool,
}
fn number<T: NativeFloat>(x: &T) -> Number {
    Number { rational: x.exact_rational().map(|q| q.to_string()), precision: x.get_precision(), negative_sign: x.negative_sign(), finite: x.is_finite() }
}
fn complex<T: NativeFloat>(z: &Complex<T>) -> [Number; 2] { [number(&z.re), number(&z.im)] }

#[derive(Clone, Debug, Serialize)]
pub struct MasterCapture {
    family: String,
    backend: String,
    components: usize,
    rows: usize,
    requests: Vec<(usize, usize)>,
    valid_lanes: Vec<usize>,
    input: Vec<[Number; 2]>,
    output_order: [&'static str; 6],
    output: Vec<Option<Vec<[Number; 2]>>>,
    errors: Vec<Option<String>>,
    whole_batch_error: Option<String>,
}
static ENABLED: AtomicBool = AtomicBool::new(false);
static CAPTURES: Mutex<Vec<MasterCapture>> = Mutex::new(Vec::new());
pub(crate) fn enabled() -> bool { ENABLED.load(Ordering::Relaxed) }
pub fn set_master_capture(enabled: bool) { ENABLED.store(enabled, Ordering::Relaxed); }
pub fn take_master_captures() -> Vec<MasterCapture> { std::mem::take(&mut *CAPTURES.lock().expect("private capture mutex poisoned")) }

pub(crate) fn record<T: NativeFloat>(family: &str, backend: MasterBackend, components: usize, input: &[Complex<T>], requests: &[(usize, usize)], valid_lanes: &[usize], result: &Result<MasterBatch<T>, MasterError>) {
    let (output, errors, whole_batch_error) = match result {
        Ok(batch) => (
            (0..batch.row_count()).map(|lane| batch.lane(lane).ok().map(|_| batch.private_six_values()[lane*6*components..(lane+1)*6*components].iter().map(complex).collect())).collect(),
            batch.errors().iter().map(|e| e.as_ref().map(ToString::to_string)).collect(), None),
        Err(error) => (Vec::new(), Vec::new(), Some(error.to_string())),
    };
    CAPTURES.lock().expect("private capture mutex poisoned").push(MasterCapture {
        family: family.to_owned(), backend: format!("{backend:?}"), components, rows: requests.len(), requests: requests.to_vec(), valid_lanes: valid_lanes.to_vec(), input: input.iter().map(complex).collect(),
        output_order: ["finite", "total_single", "ir_double", "uv_single", "ir_single", "derivative_discriminant"], output, errors, whole_batch_error,
    });
}
