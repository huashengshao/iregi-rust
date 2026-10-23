//! Private fixed-loop diagnostic: same slim-only baseline versus exact receipts.
//! No preparation timing, input/output change, tolerance change, or IREGI gate.
use std::{
    hint::black_box,
    time::{Duration, Instant},
};
use symbolica::domains::{dual::HyperDual, float::Complex, rational::Rational};

#[derive(Clone, Copy, Debug)]
enum Workload {
    BubbleOrdinary,
    TriangleOrdinary,
    BubbleZeroReal,
    BubbleZeroComplex,
    BubbleMixedDual,
    GghZeroReal,
    GghMixedComplex,
}
impl Workload {
    fn label(self) -> &'static str {
        match self {
            Self::BubbleOrdinary => "bubble-ordinary",
            Self::TriangleOrdinary => "triangle-ordinary",
            Self::BubbleZeroReal => "bubble-zero-real",
            Self::BubbleZeroComplex => "bubble-zero-complex",
            Self::BubbleMixedDual => "bubble-mixed-dual",
            Self::GghZeroReal => "ggh-zero-real",
            Self::GghMixedComplex => "ggh-mixed-complex",
        }
    }
    fn iterations(self, rows: usize) -> usize {
        let (single, batch) = match self {
            Self::BubbleOrdinary => (1024, 64),
            Self::TriangleOrdinary => (256, 16),
            Self::BubbleZeroReal => (512, 32),
            Self::BubbleZeroComplex => (256, 16),
            _ => (128, 8),
        };
        if rows == 1 { single } else { batch }
    }
    fn ggh(self) -> bool {
        matches!(self, Self::GghZeroReal | Self::GghMixedComplex)
    }
    fn triangle(self) -> bool {
        self.ggh() || matches!(self, Self::TriangleOrdinary)
    }
    fn components(self) -> usize {
        if matches!(self, Self::BubbleMixedDual) {
            4
        } else {
            1
        }
    }
    fn row(self, lane: usize) -> Vec<Complex<f64>> {
        let c = |x| Complex::new(x, 0.);
        let primal = match self {
            Self::TriangleOrdinary => vec![
                0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0., 2., 3., 5., 1.,
            ],
            Self::GghZeroReal | Self::GghMixedComplex => vec![
                0., 0., 0., 0., 62.5, 0., 0., -62.5, -62.5, -0., -0., -62.5, 29929., 29929.,
                29929., 125.,
            ],
            Self::BubbleOrdinary => vec![0., 0., 0., 0., 0., 1., 0., 0., 4., 9., 1.],
            Self::BubbleMixedDual if lane % 4 == 2 => {
                vec![0., 0., 0., 0., 0., 1., 0., 0., 4., 4., 1.]
            }
            _ => vec![0., 0., 0., 0., 1., 1., 0., 0., 4., 4., 1.],
        };
        let components = self.components();
        let mut row = primal
            .into_iter()
            .flat_map(|value| std::iter::once(c(value)).chain((1..components).map(|_| c(0.))))
            .collect::<Vec<_>>();
        let width = if self.triangle() { 3 } else { 2 };
        let imaginary_mass = match self {
            Self::BubbleZeroComplex => -0.25,
            Self::GghMixedComplex if lane % 3 == 1 => 0.,
            Self::GghMixedComplex if lane % 3 == 2 => -0.5,
            Self::GghMixedComplex => -0.25,
            Self::BubbleMixedDual if lane % 4 == 3 => -0.25,
            _ => 0.,
        };
        for argument in width * 4..width * 5 {
            row[argument * components].im = imaginary_mass;
        }
        if components == 4 {
            // Ordered shape: primal,v,u,uv. Preserve complex transverse seeds.
            let seed = if lane % 2 == 0 {
                Complex::new(0., 1.)
            } else {
                c(1.)
            };
            row[4 * components + 2] = seed;
            row[8 * components + 1] = seed;
            row[4 * components + 3] = seed * 0.25;
        }
        row
    }
}

#[derive(Debug, PartialEq, Eq)]
struct Snapshot {
    bits: Vec<u64>,
    meta: String,
}
trait Case {
    fn snapshot(&mut self) -> Snapshot;
    fn timed(&mut self, iterations: usize) -> Duration;
    fn proof_work(&self) -> Option<[usize; 4]>;
}
macro_rules! proof_work {
    (baseline,$s:ident) => {
        None
    };
    (candidate,$s:ident) => {
        Some($s.workspace.experimental_distance_proofs())
    };
}
macro_rules! implementation {
    ($module:ident,$library:ident) => {
        mod $module {
            use super::*;
            use $library::{
                Algorithm, Convention, KinematicsBatch, ReductionPlan, ReductionSettings, Workspace,
            };
            pub struct Runner {
                workspace: Workspace<f64>,
                batch: KinematicsBatch<f64>,
            }
            impl Runner {
                pub fn new(workload: Workload, rows: usize) -> Self {
                    let mut settings = ReductionSettings::new(
                        if workload.triangle() { 3 } else { 2 },
                        if workload.triangle() { 2 } else { 1 },
                    );
                    settings.algorithm = if workload.ggh() {
                        Algorithm::Hybrid
                    } else {
                        Algorithm::Ibp
                    };
                    settings.convention = Convention::OneLoop;
                    let plan = ReductionPlan::new(settings).unwrap();
                    let workspace = if workload.components() == 4 {
                        Workspace::new_dual(
                            &plan,
                            0.,
                            HyperDual::<Complex<Rational>>::new(vec![
                                vec![0, 0],
                                vec![0, 1],
                                vec![1, 0],
                                vec![1, 1],
                            ]),
                        )
                        .unwrap()
                    } else {
                        Workspace::new(&plan, 0.).unwrap()
                    };
                    Self {
                        workspace,
                        batch: KinematicsBatch {
                            rows,
                            components: workload.components(),
                            values: (0..rows).flat_map(|lane| workload.row(lane)).collect(),
                        },
                    }
                }
            }
            impl Case for Runner {
                fn snapshot(&mut self) -> Snapshot {
                    let output = self.workspace.reduce_batch(&self.batch).unwrap();
                    let mut bits = Vec::new();
                    for lane in 0..output.rows() {
                        for value in output.lane(lane).expect("every timing lane must succeed") {
                            assert!(value.re.is_finite() && value.im.is_finite());
                            bits.extend([value.re.to_bits(), value.im.to_bits()]);
                        }
                    }
                    Snapshot {
                        bits,
                        meta: format!(
                            "{:?}|{:?}|{:?}|{:?}|{:?}|{:?}|{:?}|{:?}",
                            output.statuses,
                            output.basis,
                            output.metadata(),
                            output.components,
                            output.analytic_used,
                            output.fallback_used,
                            self.workspace.last_execution(),
                            self.workspace.last_diagnostics()
                        ),
                    }
                }
                fn timed(&mut self, iterations: usize) -> Duration {
                    let start = Instant::now();
                    for _ in 0..iterations {
                        black_box(self.workspace.reduce_batch(black_box(&self.batch)).unwrap());
                    }
                    start.elapsed()
                }
                fn proof_work(&self) -> Option<[usize; 4]> {
                    proof_work!($module, self)
                }
            }
        }
    };
}
implementation!(baseline, receipt_baseline);
implementation!(candidate, receipt_candidate);

fn main() {
    let time = std::env::args().any(|arg| arg == "--time");
    if time {
        println!("workload,rows,block,order,implementation,iterations,ns_per_batch");
    }
    let workloads = [
        Workload::BubbleOrdinary,
        Workload::TriangleOrdinary,
        Workload::BubbleZeroReal,
        Workload::BubbleZeroComplex,
        Workload::BubbleMixedDual,
        Workload::GghZeroReal,
        Workload::GghMixedComplex,
    ];
    let mut cases = 0;
    for workload in workloads {
        for rows in [1, 32] {
            eprintln!("PREPARE {} rows={rows}", workload.label());
            let mut baseline = baseline::Runner::new(workload, rows);
            let mut candidate = candidate::Runner::new(workload, rows);
            let expected = baseline.snapshot();
            assert_eq!(
                expected,
                candidate.snapshot(),
                "preflight {} rows={rows}",
                workload.label()
            );
            for _ in 0..8 {
                assert_eq!(expected, baseline.snapshot());
                assert_eq!(expected, candidate.snapshot());
            }
            let work = candidate.proof_work().unwrap();
            if matches!(
                workload,
                Workload::BubbleOrdinary | Workload::TriangleOrdinary
            ) {
                assert_eq!(work[2], 0, "ordinary control unexpectedly reused a proof");
            } else {
                assert!(work[2] > 0, "zero control did not reuse a proof");
            }
            eprintln!(
                "PARITY_PASS {} rows={rows} fixed_iterations={} candidate_proof_work={work:?}",
                workload.label(),
                workload.iterations(rows)
            );
            if time {
                let iterations = workload.iterations(rows);
                for block in 0..21 {
                    let order = if block % 2 == 0 {
                        "baseline-first"
                    } else {
                        "candidate-first"
                    };
                    let (old, new) = if block % 2 == 0 {
                        (baseline.timed(iterations), candidate.timed(iterations))
                    } else {
                        let new = candidate.timed(iterations);
                        (baseline.timed(iterations), new)
                    };
                    println!(
                        "{},{rows},{block},{order},baseline,{iterations},{:.6}",
                        workload.label(),
                        old.as_secs_f64() * 1e9 / iterations as f64
                    );
                    println!(
                        "{},{rows},{block},{order},candidate,{iterations},{:.6}",
                        workload.label(),
                        new.as_secs_f64() * 1e9 / iterations as f64
                    );
                }
            }
            assert_eq!(expected, baseline.snapshot());
            assert_eq!(expected, candidate.snapshot());
            cases += 1;
        }
    }
    eprintln!(
        "PASS {cases} fixed-loop cases; mode={}",
        if time { "timing" } else { "correctness-only" }
    );
}
