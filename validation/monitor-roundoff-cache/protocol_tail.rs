fn encode<T: NativeFloat>(output: &BatchResult<T>, stats: ExecutionStats) -> String {
    let mut result = format!("{:?}|{:?}|{:?}|{:?}|{:?}|{:?}|{:?}", output.statuses,
        output.basis, output.components, output.metadata(), output.fallback_used,
        output.analytic_used, stats);
    for row in 0..output.rows() {
        if let Ok(values) = output.lane(row) {
            for value in values {
                for component in [&value.re, &value.im] {
                    result.push_str(&format!("|{:?}:{}:{}", component.exact_rational(),
                        component.get_precision(), component.negative_sign()));
                }
            }
        }
    }
    result
}
pub fn corpus_snapshots() -> Vec<String> {
    let mut workers = prepared_workers();
    let mut snapshots = Vec::new();
    for round in 0..4 {
        for worker in &mut workers {
            worker.check(round);
            for job in &mut worker.ordinary {
                for batch in &job.batches {
                    let result = job.workspace.reduce_batch(batch).unwrap();
                    snapshots.push(encode(&result, job.workspace.last_execution()));
                }
            }
            for batch in &worker.dual.batches {
                let result = worker.dual.workspace.reduce_batch(batch).unwrap();
                snapshots.push(encode(&result, worker.dual.workspace.last_execution()));
            }
            for batch in &worker.precise.batches {
                let result = worker.precise.workspace.reduce_batch(batch).unwrap();
                snapshots.push(encode(&result, worker.precise.workspace.last_execution()));
            }
        }
    }
    snapshots
}
