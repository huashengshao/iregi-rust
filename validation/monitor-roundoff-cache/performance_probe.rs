//! Standalone diagnostic linked to two core archives built with identical flags.
//! This is not the complete reference-code acceptance benchmark.
use std::{hint::black_box, time::{Duration, Instant}};
use symbolica::domains::float::Complex;

trait Case {
    fn snapshot(&mut self) -> Vec<u64>;
    fn timed(&mut self, iterations: usize) -> Duration;
}

macro_rules! implementation {
    ($module:ident, $library:ident) => {
        mod $module {
            use super::*;
            use $library::{Algorithm, Convention, KinematicsBatch, ReductionPlan,
                ReductionSettings, Workspace};
            pub struct Runner {
                workspace: Workspace<f64>,
                batch: KinematicsBatch<f64>,
            }
            impl Runner {
                pub fn new(n: usize, rank: u16, rows: usize) -> Self {
                    let mut settings = ReductionSettings::new(n, rank);
                    settings.algorithm = Algorithm::PassarinoVeltman;
                    settings.convention = Convention::OneLoop;
                    let plan = ReductionPlan::new(settings).unwrap();
                    let workspace = Workspace::new(&plan, 0.0).unwrap();
                    let shifts = [[0.0; 4], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]];
                    let masses = [2.0, 3.0, 5.0];
                    let row: Vec<_> = shifts[..n].iter().flatten().copied()
                        .chain(masses[..n].iter().copied()).chain([1.0])
                        .map(|re| Complex::new(re, 0.0)).collect();
                    Self { workspace, batch: KinematicsBatch {
                        rows, components: 1, values: row.repeat(rows),
                    }}
                }
            }
            impl Case for Runner {
                fn snapshot(&mut self) -> Vec<u64> {
                    let output = self.workspace.reduce_batch(&self.batch).unwrap();
                    let mut bits = Vec::new();
                    for row in 0..self.batch.rows {
                        for value in output.lane(row).expect("benchmark lane must succeed") {
                            bits.extend([value.re.to_bits(), value.im.to_bits()]);
                        }
                    }
                    bits
                }
                fn timed(&mut self, iterations: usize) -> Duration {
                    let start = Instant::now();
                    for _ in 0..iterations {
                        black_box(self.workspace.reduce_batch(black_box(&self.batch)).unwrap());
                    }
                    start.elapsed()
                }
            }
        }
    }
}
implementation!(baseline, iregi_cache_baseline);
implementation!(candidate, iregi_cache_candidate);

fn main() {
    println!("workload,rows,block,order,implementation,iterations,ns_per_batch");
    for (n, rank) in [(1, 0), (1, 7), (2, 1), (2, 3), (3, 1), (3, 3)] {
        for rows in [1, 32] {
            eprintln!("PREPARE n={n} rank={rank} rows={rows}");
            let mut baseline = baseline::Runner::new(n, rank, rows);
            let mut candidate = candidate::Runner::new(n, rank, rows);
            assert_eq!(baseline.snapshot(), candidate.snapshot(), "all tensor/Laurent values must match bitwise");
            baseline.timed(20);
            candidate.timed(20);
            let probe = baseline.timed(20).max(candidate.timed(20)).as_secs_f64() / 20.0;
            let iterations = (0.02 / probe).ceil().clamp(1.0, 100_000.0) as usize;
            eprintln!("PARITY PASS n={n} rank={rank} rows={rows}; iterations={iterations}");
            for block in 0..21 {
                let order = if block % 2 == 0 { "baseline-first" } else { "candidate-first" };
                let (old, new) = if block % 2 == 0 {
                    (baseline.timed(iterations), candidate.timed(iterations))
                } else {
                    let new = candidate.timed(iterations);
                    (baseline.timed(iterations), new)
                };
                println!("n{n}-rank{rank},{rows},{block},{order},baseline,{iterations},{:.6}", old.as_secs_f64() * 1e9 / iterations as f64);
                println!("n{n}-rank{rank},{rows},{block},{order},candidate,{iterations},{:.6}", new.as_secs_f64() * 1e9 / iterations as f64);
            }
            assert_eq!(baseline.snapshot(), candidate.snapshot());
        }
    }
}
