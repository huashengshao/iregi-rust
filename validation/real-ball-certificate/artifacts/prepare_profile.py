from pathlib import Path
import hashlib,json
root=Path.cwd();out=root/'target/real-ball-certificate';p=root/'crates/iregi-rust/src/invariant_certificate.rs';s=p.read_text();(out/'original.rs').write_text(s)
def replace(old,new):
 global s
 assert s.count(old)==1,(old[:80],s.count(old));s=s.replace(old,new)
replace('            input: Vec::new(),\n            output: Vec::new(),', '            input: Vec::new(),\n            output: Vec::new(),\n            trace: CertificateTrace::default(),')
replace('    output: Vec<ComplexBall>,\n}', '    output: Vec<ComplexBall>,\n    pub(crate) trace: CertificateTrace,\n}')
replace('        self.evaluated_rows = 0;\n        self.passes = 0;', '        self.evaluated_rows = 0;\n        self.passes = 0;\n        self.trace = CertificateTrace::default();')
replace('        loop {\n            let index =', '        loop {\n            let mapped_started = std::time::Instant::now();\n            let index =')
replace('            let evaluator = &mut self.evaluators[index].1;', '            self.trace.mapping_ns += mapped_started.elapsed().as_nanos();\n            let packing_started = std::time::Instant::now();\n            let evaluator = &mut self.evaluators[index].1;')
replace('            evaluator\n                .evaluate_batch', '            self.trace.packing_ns += packing_started.elapsed().as_nanos();\n            let evaluation_started = std::time::Instant::now();\n            evaluator\n                .evaluate_batch')
replace('            self.evaluated_rows = self', '            self.trace.evaluation_ns += evaluation_started.elapsed().as_nanos();\n            self.trace.complex_batch_calls += 1;\n            self.trace.complex_rows += active.len();\n            let inspection_started = std::time::Instant::now();\n            self.evaluated_rows = self')
replace('            if unresolved.is_empty() || bits == self.maximum_bits {', '            self.trace.inspection_ns += inspection_started.elapsed().as_nanos();\n            if unresolved.is_empty() || bits == self.maximum_bits {')
s += '''
#[derive(Clone,Debug,Default)]
pub(crate) struct CertificateTrace {
 pub(crate) mapping_ns:u128,
 pub(crate) packing_ns:u128,
 pub(crate) evaluation_ns:u128,
 pub(crate) inspection_ns:u128,
 pub(crate) real_batch_calls:usize,
 pub(crate) complex_batch_calls:usize,
 pub(crate) real_rows:usize,
 pub(crate) complex_rows:usize,
}
impl InvariantCertificatePlan {
 pub(crate) fn probe_operation_counts(&self)->symbolica::evaluate::OperationCount { self.exact.count_operations() }
}
'''
(out/'profiled.rs').write_text(s)
manifest=dict(source=str(p.relative_to(root)),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),profiled_sha256=hashlib.sha256(s.encode()).hexdigest(),scope='Instrumentation only; same ComplexBall evaluator, precision budgets, selected masks, and inspection')
(out/'profile-source.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest))
