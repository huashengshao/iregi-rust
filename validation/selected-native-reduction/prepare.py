"""Freeze copied source and its narrow private changes; no compiler or runtime."""
from pathlib import Path
import datetime, hashlib, json, shutil, subprocess

ROOT = Path.cwd()
HERE = ROOT / 'target/selected-native-reduction'
sha = lambda p: hashlib.file_digest(Path(p).open('rb'), 'sha256').hexdigest()
save = lambda p, x: Path(p).write_text(json.dumps(x, indent=2)+'\n')
revision = subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()
base_revision = '06706e2a1e4f0082889a53187c80bbe97803340f'
assert subprocess.check_output(['git','diff',base_revision+'..'+revision,'--','crates/iregi-rust','crates/iregi-masters']) == b''
assert subprocess.check_output(['git','diff','--','crates/iregi-rust','crates/iregi-masters']) == b''
assert not (HERE/'copied').exists(), 'preserve prior source snapshot'
sources = {}
for crate in ['iregi-rust','iregi-masters']:
    for rel in subprocess.check_output(['git','ls-files',f'crates/{crate}'],text=True).splitlines():
        path = ROOT/rel
        if not path.is_file() or not (rel.endswith('.rs') or rel.endswith('Cargo.toml')):
            continue
        # Unselected generated D0/dB0 source cannot enter this compilation.
        if '/generated/' in rel and Path(rel).name not in ['a0.rs','b0.rs','c0.rs','constants.rs']:
            continue
        target = HERE/'copied'/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,target)
        sources[rel] = sha(path)

masters = HERE/'copied/crates/iregi-masters/src'
core = HERE/'copied/crates/iregi-rust/src'
def replace(path, old, new):
    text = path.read_text()
    assert text.count(old)==1, (path,old[:100],text.count(old))
    path.write_text(text.replace(old,new))

replace(masters/'lib.rs', 'mod exact_plan;', 'mod exact_plan;\nmod selected_batch;')
replace(masters/'lib.rs', 'enum PreparedMaster<T: NativeFloat> {', 'enum PreparedMaster<T: NativeFloat> {\n    SelectedF64(selected_batch::SelectedBatchEvaluator),')
replace(masters/'lib.rs', '    pub fn backend(&self) -> MasterBackend {', '''    /// Private experiment only: keep every other numeric/domain path intact.
    pub fn private_select_f64(mut self) -> Result<Self, MasterError> {
        if self.shape.is_none() && self.components == 1
            && std::any::TypeId::of::<T>() == std::any::TypeId::of::<f64>()
            && matches!(self.family, ScalarIntegral::A0 | ScalarIntegral::B0 | ScalarIntegral::C0)
        {
            self.evaluator = PreparedMaster::SelectedF64(
                selected_batch::SelectedBatchEvaluator::new(self.family)
                    .map_err(MasterError::Preparation)?,
            );
        }
        Ok(self)
    }

    pub fn backend(&self) -> MasterBackend {''')
replace(masters/'lib.rs', '            PreparedMaster::Symbolica(_) => MasterBackend::SymbolicaBatch,', '            PreparedMaster::Symbolica(_) => MasterBackend::SymbolicaBatch,\n            PreparedMaster::SelectedF64(_) => MasterBackend::RustBatch,')
replace(masters/'lib.rs', '        let _ = policy;\n        false', '''        if let PreparedMaster::SelectedF64(evaluator) = &mut self.evaluator {
            evaluator.set_policy(policy);
            return true;
        }
        let _ = policy;
        false''')
replace(masters/'lib.rs', '        match &mut self.evaluator {\n            PreparedMaster::Symbolica(evaluator)', '''        match &mut self.evaluator {
            PreparedMaster::SelectedF64(evaluator) => evaluator
                .evaluate_batch(&self.input_workspace, &mut self.output_workspace, valid)
                .map_err(MasterError::Evaluation)?,
            PreparedMaster::Symbolica(evaluator)''')
replace(masters/'lib.rs', '''    pub fn row_count(&self) -> usize {
        self.errors.len()
    }

    pub fn component_count(&self) -> usize {''', '''    pub fn row_count(&self) -> usize {
        self.errors.len()
    }

    /// Private observational access to all six outputs, including discriminant.
    pub fn private_six_values(&self) -> &[Complex<T>] { &self.values }

    pub fn component_count(&self) -> usize {''')
shutil.copy2(HERE/'source/selected_batch.rs',masters/'selected_batch.rs')

replace(core/'execution.rs', 'Mutex<HashMap<Option<Vec<Vec<usize>>>, Arc<OnceLock<Result<Arc<PreparedExecution>, String>>>>>', 'Mutex<HashMap<(Option<Vec<Vec<usize>>>, bool), Arc<OnceLock<Result<Arc<PreparedExecution>, String>>>>>')
replace(core/'execution.rs', '        .entry(shape)', '        .entry((shape, cfg!(private_selected_native)))')
replace(core/'execution.rs', '''                        PreparedMasterPlan::Exact(plan) => plan
                            .instantiate(prototype.clone())
                            .map(ScalarMasterEvaluator::OneLoop),''', '''                        PreparedMasterPlan::Exact(plan) => plan
                            .instantiate(prototype.clone())
                            .and_then(|evaluator| {
                                #[cfg(private_selected_native)]
                                { evaluator.private_select_f64() }
                                #[cfg(not(private_selected_native))]
                                { Ok(evaluator) }
                            })
                            .map(ScalarMasterEvaluator::OneLoop),''')
replace(core/'execution.rs', '''                    let evaluated = evaluator.evaluate_batch(&group.input, rows);
                    record_time(started, &mut self.profile.scalar_masters);''', '''                    let evaluated = evaluator.evaluate_batch(&group.input, rows);
                    if crate::master_capture::enabled() {
                        crate::master_capture::record(family.name(), evaluator.backend(), self.components, &group.input, &group.requests, &self.valid_lanes, &evaluated);
                    }
                    record_time(started, &mut self.profile.scalar_masters);''')
with (core/'lib.rs').open('a') as out:
    out.write('\nmod master_capture;\npub use master_capture::{set_master_capture, take_master_captures};\npub const PRIVATE_SELECTED_NATIVE: bool = cfg!(private_selected_native);\n')
shutil.copy2(HERE/'source/master_capture.rs',core/'master_capture.rs')

closure = ROOT/'target/e6-direct-n2/preparation.json'
supplement = ROOT/'target/core-fused-cse-census/supplemental-deps.json'
records = {
    'status':'source_prepared_not_compiled',
    'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source_revision':revision,'production_revision':base_revision,
    'production_sources':sources,
    'private_sources':{str(p.relative_to(HERE)):sha(p) for p in (HERE/'copied').rglob('*') if p.is_file()},
    'closure_path':str(closure.relative_to(ROOT)),'closure_sha256':sha(closure),
    'supplemental_path':str(supplement.relative_to(ROOT)),'supplemental_sha256':sha(supplement),
    'private_selection':'exact f64, no Dual shape, A0/B0/C0 only, after unchanged ExactMasterPlan instantiation',
    'source_controls':['no native-batch feature','no generated D0/dB0 module imports','same private master crate for both cores','public adapter body only adds one dispatch arm','immutable policy bit in exact cache key'],
}
save(HERE/'source-manifest.json',records)
with (HERE/'private.patch').open('w') as out:
    for rel in ['crates/iregi-masters/src/lib.rs','crates/iregi-rust/src/lib.rs','crates/iregi-rust/src/execution.rs']:
        subprocess.run(['diff','-u',str(ROOT/rel),str(HERE/'copied'/rel)],stdout=out,check=False)
print(json.dumps({'status':records['status'],'copied_files':len(sources),'private_files':len(records['private_sources']),'manifest_sha256':sha(HERE/'source-manifest.json')}))
