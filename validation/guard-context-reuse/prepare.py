#!/usr/bin/env python3
"""Reconstruct isolated paired sources; production is never changed."""
from pathlib import Path
import subprocess, hashlib, json, shutil
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'target/guard-context-reuse'; E=ROOT/'validation/guard-context-reuse'
if OUT.exists(): raise SystemExit(f'refusing to replace {OUT}')
REV='80949db'
names=subprocess.check_output(['git','ls-tree','-r','--name-only',REV,'crates/iregi-rust/src'],cwd=ROOT,text=True).splitlines()
names+=['validation/reference/fixtures.json','validation/reference/snapping/reductions.json','validation/pv-high-rank/lightlike-feynman-parameters.json']
for variant in ['baseline','candidate']:
 for name in names:
  p=OUT/variant/name;p.parent.mkdir(parents=True,exist_ok=True)
  p.write_bytes(subprocess.check_output(['git','show',f'{REV}:{name}'],cwd=ROOT))
src=OUT/'candidate/crates/iregi-rust/src'
shutil.copyfile(E/'context.rs',src/'stability/context.rs')

def replace_once(text, old, new):
 assert text.count(old)==1, (old[:120],text.count(old))
 return text.replace(old,new,1)

def transform_method(text, name, args, scale_components, power_specs, enumerate_loop=None):
 start=text.index('    pub(crate) fn '+name+'<T: NativeFloat>')
 body_start=text.index(') -> Option<String> {',start)+len(') -> Option<String> ')
 depth=1; end=body_start+1
 while depth:
  if text[end]=='{': depth+=1
  elif text[end]=='}': depth-=1
  end+=1
 original=text[start:end]; signature=original[:original.index('{')]
 body=original[original.index('{'):]
 wrapper=signature+'{\n        self.'+name+'_impl::<T, false>('+args+', None)\n    }'
 cached_signature=signature.replace(name+'<',name+'_context<').replace('    ) -> Option<String>', '        context: &mut GuardContext<T>,\n    ) -> Option<String>')
 cached=cached_signature+'{\n        self.'+name+'_impl::<T, true>('+args+', Some(context))\n    }'
 impl_signature=signature.replace('pub(crate) fn '+name+'<T: NativeFloat>','fn '+name+'_impl<T: NativeFloat, const CACHED: bool>').replace('    ) -> Option<String>', '        mut context: Option<&mut GuardContext<T>>,\n    ) -> Option<String>')
 body=replace_once(body,'let mut roundoff = OperandRoundoff::new(prototype);','let mut roundoff = if CACHED { OperandRoundoff::with_unit(prototype, context.as_deref().unwrap().prototype_unit.clone()) } else { OperandRoundoff::new(prototype) };')
 body=replace_once(body,'let tolerance = dyadic(prototype, 19i64 - i64::from(accuracy_bits));','let tolerance = if CACHED { context.as_deref().unwrap().tolerance.clone() } else { dyadic(prototype, 19i64 - i64::from(accuracy_bits)) };')
 body=replace_once(body,f'let scale = self.kinematic_scale(input, {scale_components}, prototype);',f'let scale = if CACHED {{ None }} else {{ Some(self.kinematic_scale(input, {scale_components}, prototype)) }};')
 if enumerate_loop:
  body=replace_once(body,enumerate_loop[0],enumerate_loop[1])
 for expression,slot in power_specs:
  body=replace_once(body,'signed_power(&scale, '+expression+')',f'if CACHED {{ let context = context.as_deref_mut().unwrap(); context.natural({slot}, self, input, {scale_components}, prototype) }} else {{ signed_power(scale.as_ref().unwrap(), {expression}) }}')
 return text[:start]+wrapper+'\n\n'+cached+'\n\n'+impl_signature+body+text[end:]

p=src/'stability.rs';s=p.read_text()
s=replace_once(s,'pub(crate) mod arguments;','pub(crate) mod arguments;\nmod context;\npub(crate) use context::GuardContext;')
s=transform_method(s,'inspect_lane_with_accuracy','values, input, components, prototype, accuracy_bits','components',[('check.dimension','context.local_slots[check_index]')],('for check in &self.checks {','for (check_index, check) in self.checks.iter().enumerate() {'))
s=transform_method(s,'inspect_primal_lane','values, input, prototype, accuracy_bits','1',[('check.dimension','context.primal_slots[check_index]')],('for check in &self.primal_checks {','for (check_index, check) in self.primal_checks.iter().enumerate() {'))
s=transform_method(s,'inspect_output_precision_lane','values, input, components, prototype, accuracy_bits','components',[('dimension','context.output_slots[output]')])
anchor="impl<'a, T: NativeFloat> OperandRoundoff<'a, T> {"
s=replace_once(s,anchor,anchor+'''\n    fn with_unit(prototype: &'a T, prototype_unit: T) -> Self {
        Self { prototype, prototype_bits: prototype.get_precision(), prototype_unit, units: HashMap::new() }
    }
''');p.write_text(s)
p=src/'stability/quadrature.rs';s=p.read_text();s=replace_once(s,'    OperandRoundoff, StabilityPlan,','    GuardContext, OperandRoundoff, StabilityPlan,')
s=transform_method(s,'inspect_quadrature_lane','quadrature, errors, moments, input, components, prototype, accuracy_bits, primal','components',[('check.dimension','context.output_slots[check.output]')]);p.write_text(s)
p=src/'execution.rs';s=p.read_text();s=replace_once(s,'        StabilityPlan, arguments::ArgumentStabilityPlan, master_argument_precision_failure,','        GuardContext, StabilityPlan, arguments::ArgumentStabilityPlan, master_argument_precision_failure,')
anchor='pub struct Workspace<T: NativeFloat> {';prefix,s=s.split(anchor,1)
s=replace_once(s,'    stability: Arc<StabilityPlan>,','    stability: Arc<StabilityPlan>,\n    guard_context: GuardContext<T>,')
s=replace_once(s,'        Ok(Self {\n            accuracy_bits: prototype.get_precision(),','        let guard_context = GuardContext::new(&exact.stability, &prototype, prototype.get_precision());\n        Ok(Self {\n            guard_context,\n            accuracy_bits: prototype.get_precision(),')
s=replace_once(s,'        self.accuracy_bits = bits;','        self.accuracy_bits = bits;\n        self.guard_context.set_accuracy(&self.prototype, bits);')
s=replace_once(s,'        for (compact, &lane) in self.successful_lanes.iter().enumerate() {','        for (compact, &lane) in self.successful_lanes.iter().enumerate() {\n            self.guard_context.begin_lane();')
for name in ['inspect_output_precision_lane','inspect_lane_with_accuracy','inspect_primal_lane','inspect_quadrature_lane']:
 s=replace_once(s,'self.stability.'+name+'(','self.stability.'+name+'_context(')
# Only the four post-reduction guards receive this additional argument.
start=s.index('} else if let Some(reason) = self.stability.inspect_output_precision_lane_context(')
end=s.index('        record_time(started, &mut self.profile.reduction);',start)
part=s[start:end]
part=part.replace('                self.accuracy_bits,\n            )','                self.accuracy_bits,\n                &mut self.guard_context,\n            )')
part=part.replace('                    self.accuracy_bits,\n                )','                    self.accuracy_bits,\n                    &mut self.guard_context,\n                )')
part=part.replace('                    primal_values,\n                )','                    primal_values,\n                    &mut self.guard_context,\n                )')
assert part.count('&mut self.guard_context')==4
s=s[:start]+part+s[end:];p.write_text(prefix+anchor+s)
rustfmt='/nix/store/12b271ipi4g995hlyfcp9ll5clz0na8f-rustfmt-preview-stable-2026-09-03/bin/rustfmt'
subprocess.run([rustfmt,'--edition','2024',str(src/'stability.rs'),str(src/'execution.rs')],check=True)
record={'revision':subprocess.check_output(['git','rev-parse',REV],cwd=ROOT,text=True).strip(),'scope':'isolated typed guard constants, lazy lane scale and distinct signed-dimension powers; production unchanged','sources':{}}
for variant in ['baseline','candidate']:
 record['sources'][variant]={str(p.relative_to(OUT/variant)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((OUT/variant).rglob('*')) if p.is_file()}
(E/'source-manifest.json').write_text(json.dumps(record,indent=2)+'\n')
print(OUT)
