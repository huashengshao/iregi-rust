from pathlib import Path
import hashlib,json
root=Path.cwd();out=root/'target/real-ball-certificate';s=(out/'profiled.rs').read_text()
def replace(old,new):
 global s
 assert s.count(old)==1,(old[:80],s.count(old));s=s.replace(old,new)
replace('float::{Complex, ComplexBall, DoubleFloat, Float, SingleFloat}', 'float::{Complex, ComplexBall, DoubleFloat, Float, RealBall, SingleFloat}')
replace('            trace: CertificateTrace::default(),', '''            trace: CertificateTrace::default(),
            real_evaluators: Vec::new(),
            real_input: Vec::new(),
            real_output: Vec::new(),
            complex_output: Vec::new(),
            allow_real: true,
            // Certified plans are built only from Q polynomials. No callback or
            // shared function may hide coefficients from this root-IR proof.
            real_coefficients: self.exact.count_operations().function_calls == 0
                && self.exact.get_constants().iter().all(|value| value.im.is_zero()),''')
replace('    pub(crate) trace: CertificateTrace,\n}', '''    pub(crate) trace: CertificateTrace,
    real_evaluators: Vec<(u32, BatchExpressionEvaluator<RealBall>)>,
    real_input: Vec<RealBall>,
    real_output: Vec<RealBall>,
    complex_output: Vec<ComplexBall>,
    allow_real: bool,
    real_coefficients: bool,
}''')
start=s.index('            let mapped_started = std::time::Instant::now();')
end=s.index('            let mut unresolved = Vec::new();',start)
s=s[:start]+'''            let width = self.exact.get_output_len();
            let output_len = width.checked_mul(active.len()).ok_or_else(size_error)?;
            let zero_real = RealBall::from_rational_ball(&radius, &radius, bits);
            let zero_complex = ComplexBall::new(zero_real.clone(), zero_real.clone());
            self.output.resize(output_len, zero_complex.clone());
            let real_lane = |lane: usize| self.allow_real && self.real_coefficients
                && input[lane * input_width..(lane + 1) * input_width]
                    .iter().all(|value| value.im.is_zero());
            let grouped: [Vec<(usize, usize)>; 2] = [
                active.iter().enumerate().filter(|(_, lane)| real_lane(**lane))
                    .map(|(slot, &lane)| (slot, lane)).collect(),
                active.iter().enumerate().filter(|(_, lane)| !real_lane(**lane))
                    .map(|(slot, &lane)| (slot, lane)).collect(),
            ];
            for (group, lanes) in grouped.iter().enumerate() {
                if lanes.is_empty() { continue; }
                let mapped_started = std::time::Instant::now();
                if group == 0 {
                    let index = if let Some(index) = self.real_evaluators.iter().position(|entry| entry.0 == bits) {
                        index
                    } else {
                        let evaluator = self.exact.clone().map_coeff_with_prec(&|value| {
                            assert!(value.im.is_zero(), "real certificate coefficient proof lost");
                            RealBall::from_rational_ball(&value.re, &radius, bits)
                        }, bits).into_batch_evaluator();
                        self.real_evaluators.push((bits, evaluator));
                        self.real_evaluators.len() - 1
                    };
                    self.trace.mapping_ns += mapped_started.elapsed().as_nanos();
                    let packing_started = std::time::Instant::now();
                    self.real_input.clear();
                    for &(_, lane) in lanes {
                        self.real_input.extend(input[lane * input_width..(lane + 1) * input_width]
                            .iter().map(|value| RealBall::from_rational_ball(&value.re, &radius, bits)));
                    }
                    self.real_output.resize(width * lanes.len(), zero_real.clone());
                    self.trace.packing_ns += packing_started.elapsed().as_nanos();
                    let evaluation_started = std::time::Instant::now();
                    self.real_evaluators[index].1.evaluate_batch(&self.real_input, &mut self.real_output, lanes.len())
                        .map_err(|error| ReductionError::Evaluation(error.to_string()))?;
                    self.trace.evaluation_ns += evaluation_started.elapsed().as_nanos();
                    let scatter_started = std::time::Instant::now();
                    for (&(slot, _), point) in lanes.iter().zip(self.real_output.chunks_exact(width)) {
                        for (destination, value) in self.output[slot * width..(slot + 1) * width].iter_mut().zip(point) {
                            *destination = ComplexBall::new(value.clone(), zero_real.clone());
                        }
                    }
                    self.trace.packing_ns += scatter_started.elapsed().as_nanos();
                    self.trace.real_batch_calls += 1;
                    self.trace.real_rows += lanes.len();
                } else {
                    let index = if let Some(index) = self.evaluators.iter().position(|entry| entry.0 == bits) {
                        index
                    } else {
                        let evaluator = self.exact.clone().map_coeff_with_prec(
                            &|value| ComplexBall::from_rational_ball(value, &radius, bits), bits).into_batch_evaluator();
                        self.evaluators.push((bits, evaluator));
                        self.evaluators.len() - 1
                    };
                    self.trace.mapping_ns += mapped_started.elapsed().as_nanos();
                    let packing_started = std::time::Instant::now();
                    self.input.clear();
                    for &(_, lane) in lanes {
                        self.input.extend(input[lane * input_width..(lane + 1) * input_width]
                            .iter().map(|value| ComplexBall::from_rational_ball(value, &radius, bits)));
                    }
                    self.complex_output.resize(width * lanes.len(), zero_complex.clone());
                    self.trace.packing_ns += packing_started.elapsed().as_nanos();
                    let evaluation_started = std::time::Instant::now();
                    self.evaluators[index].1.evaluate_batch(&self.input, &mut self.complex_output, lanes.len())
                        .map_err(|error| ReductionError::Evaluation(error.to_string()))?;
                    self.trace.evaluation_ns += evaluation_started.elapsed().as_nanos();
                    let scatter_started = std::time::Instant::now();
                    for (&(slot, _), point) in lanes.iter().zip(self.complex_output.chunks_exact(width)) {
                        self.output[slot * width..(slot + 1) * width].clone_from_slice(point);
                    }
                    self.trace.packing_ns += scatter_started.elapsed().as_nanos();
                    self.trace.complex_batch_calls += 1;
                    self.trace.complex_rows += lanes.len();
                }
                self.evaluated_rows = self.evaluated_rows.checked_add(lanes.len()).ok_or_else(size_error)?;
            }
            self.passes += 1;
            let inspection_started = std::time::Instant::now();
''' + s[end:]
s += '''
impl InvariantCertificateWorkspace {
 pub(crate) fn probe_allow_real(&mut self, enabled: bool) { self.allow_real = enabled; }
}
'''
(out/'candidate.rs').write_text(s)
print(json.dumps(dict(candidate_sha256=hashlib.sha256(s.encode()).hexdigest(),production_edited=False)))
