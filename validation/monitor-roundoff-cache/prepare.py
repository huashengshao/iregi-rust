#!/usr/bin/env python3
"""Prepare immutable paired snapshots; never modify production source."""
from pathlib import Path
import hashlib,json,shutil,subprocess,datetime
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'target/monitor-roundoff-cache'
if OUT.exists():
 raise SystemExit(f'refusing to replace existing experiment {OUT}')
BASE_REVISION='80949db'
source_names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE_REVISION,'crates/iregi-rust/src'],cwd=ROOT,text=True).splitlines()
source_names+=['validation/reference/fixtures.json','validation/reference/snapping/reductions.json','validation/pv-high-rank/lightlike-feynman-parameters.json']
for variant in ['baseline','candidate']:
 for name in source_names:
  target=OUT/variant/name;target.parent.mkdir(parents=True,exist_ok=True)
  target.write_bytes(subprocess.check_output(['git','show',f'{BASE_REVISION}:{name}'],cwd=ROOT))
p=OUT/'candidate/crates/iregi-rust/src/stability.rs';s=p.read_text()
anchor='impl StabilityPlan {\n'
cache=r'''/// Successful local-monitor roundoff estimates, retained only for one lane.
/// The sparse structural map allocates numerical slots only for repeated roots.
#[derive(Clone)]
pub(crate) struct MonitorEstimateCache<T> {
    slots: Vec<usize>,
    components: usize,
    estimates: Vec<Option<T>>,
    generations: Vec<u64>,
    generation: u64,
}

impl<T: NativeFloat> MonitorEstimateCache<T> {
    pub(crate) fn new(plan: &StabilityPlan, components: usize) -> Result<Self, ReductionError> {
        let mut uses = vec![0usize; plan.expressions.len()];
        for check in &plan.checks {
            for &index in &check.terms {
                uses[index] = uses[index].saturating_add(1);
            }
        }
        let mut count = 0usize;
        let slots = uses.into_iter().map(|uses| {
            if uses < 2 { usize::MAX } else { let index = count; count += 1; index }
        }).collect();
        let width = count.checked_mul(components).ok_or_else(||
            ReductionError::Preparation("stability estimate-cache size overflow".into()))?;
        Ok(Self { slots, components, estimates: vec![None; width],
            generations: vec![0; width], generation: 0 })
    }

    fn begin_lane(&mut self) {
        match self.generation.checked_add(1) {
            Some(generation) => self.generation = generation,
            None => { self.generations.fill(0); self.generation = 1; }
        }
    }

    fn estimate(&mut self, index: usize, component: usize,
        roundoff: &mut OperandRoundoff<'_, T>, value: &Complex<T>) -> Result<T, &'static str> {
        let slot = self.slots[index];
        if slot == usize::MAX { return roundoff.complex(value); }
        let slot = slot * self.components + component;
        if self.generations[slot] == self.generation {
            return Ok(self.estimates[slot].as_ref().expect("valid cache generation").clone());
        }
        let estimate = roundoff.complex(value)?;
        self.estimates[slot] = Some(estimate.clone());
        self.generations[slot] = self.generation;
        Ok(estimate)
    }
}

'''
assert s.count(anchor)==1;s=s.replace(anchor,cache+anchor,1)
old='''    ) -> Option<String> {
        if components == 0 || values.len() != self.expressions.len() * components {'''
new='''    ) -> Option<String> {
        self.inspect_lane_impl::<T, false>(values, input, components, prototype, accuracy_bits, None)
    }

    pub(crate) fn inspect_lane_cached<T: NativeFloat>(
        &self, values: &[Complex<T>], input: &[Complex<T>], components: usize,
        prototype: &T, accuracy_bits: u32, cache: &mut MonitorEstimateCache<T>,
    ) -> Option<String> {
        cache.begin_lane();
        if cache.estimates.is_empty() {
            return self.inspect_lane_with_accuracy(values, input, components, prototype, accuracy_bits);
        }
        if cache.components != components || cache.slots.len() != self.expressions.len() {
            return Some("invalid stability estimate-cache layout".into());
        }
        self.inspect_lane_impl::<T, true>(values, input, components, prototype, accuracy_bits, Some(cache))
    }

    fn inspect_lane_impl<T: NativeFloat, const CACHED: bool>(
        &self, values: &[Complex<T>], input: &[Complex<T>], components: usize,
        prototype: &T, accuracy_bits: u32, mut cache: Option<&mut MonitorEstimateCache<T>>,
    ) -> Option<String> {
        if components == 0 || values.len() != self.expressions.len() * components {'''
assert s.count(old)==1;s=s.replace(old,new,1)
old='''                    let estimate = match roundoff.complex(term) {
                        Ok(value) => value,
                        Err(reason) => return Some(format!("{reason} for {}", check.label)),
                    };'''
new='''                    let estimate = match if CACHED {
                        cache.as_deref_mut().expect("cached specialization").estimate(index, component, &mut roundoff, term)
                    } else {
                        roundoff.complex(term)
                    } {
                        Ok(value) => value,
                        Err(reason) => return Some(format!("{reason} for {}", check.label)),
                    };'''
assert s.count(old)==1;s=s.replace(old,new,1);p.write_text(s)
p=OUT/'candidate/crates/iregi-rust/src/execution.rs';s=p.read_text()
s=s.replace('        StabilityPlan, arguments::ArgumentStabilityPlan, master_argument_precision_failure,','        MonitorEstimateCache, StabilityPlan, arguments::ArgumentStabilityPlan, master_argument_precision_failure,',1)
# PreparedExecution and Workspace both own a stability Arc; only the latter needs numerical storage.
anchor='pub struct Workspace<T: NativeFloat> {';prefix,body=s.split(anchor,1)
body=body.replace('    stability: Arc<StabilityPlan>,','    stability: Arc<StabilityPlan>,\n    monitor_estimate_cache: MonitorEstimateCache<T>,',1)
body=body.replace('            stability: exact.stability.clone(),','            monitor_estimate_cache: MonitorEstimateCache::new(&exact.stability, exact.shape.as_ref().map_or(1, Vec::len))?,\n            stability: exact.stability.clone(),',1)
body=body.replace('self.stability.inspect_lane_with_accuracy(\n                monitors,','self.stability.inspect_lane_cached(\n                monitors,',1)
old='''                monitors,
                input_row,
                self.components,
                &self.prototype,
                self.accuracy_bits,
            ) {'''
new='''                monitors,
                input_row,
                self.components,
                &self.prototype,
                self.accuracy_bits,
                &mut self.monitor_estimate_cache,
            ) {'''
assert body.count(old)==1;body=body.replace(old,new,1);p.write_text(prefix+anchor+body)
rustfmt='/nix/store/12b271ipi4g995hlyfcp9ll5clz0na8f-rustfmt-preview-stable-2026-09-03/bin/rustfmt'
subprocess.run([rustfmt,'--edition','2024',str(OUT/'candidate/crates/iregi-rust/src/stability.rs'),str(p)],check=True)
manifest={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse',BASE_REVISION],cwd=ROOT,text=True).strip(),'scope':'isolated repeated successful local-monitor roundoff-estimate cache; production unmodified','sources':{}}
for variant in ['baseline','candidate']:
 base=OUT/variant;manifest['sources'][variant]={str(f.relative_to(base)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(base.rglob('*')) if f.is_file()}
(ROOT/'validation/monitor-roundoff-cache/source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(OUT)
