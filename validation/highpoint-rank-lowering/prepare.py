"""Apply an isolated Cartesian rank-lowering experiment to the frozen snapshot."""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path.cwd()
here = root / 'validation/highpoint-rank-lowering'
initial = json.loads((here / 'source-initial.json').read_text())
base = root / initial['baseline_root']
candidate = root / initial['candidate_root']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(base / n) == h for n, h in initial['source_hashes'].items())
assert all(sha(candidate / n) == h for n, h in initial['source_hashes'].items())
path = candidate / 'crates/iregi-rust/src/pv.rs'
text = path.read_text()
anchor = '    denominator_identities: HashMap<Vec<usize>, Vec<Atom>>,\n'
assert text.count(anchor) == 1
text = text.replace(anchor, anchor + '    highpoint_rank_lowering: bool,\n    highpoint_coordinate_identities: HashMap<Vec<usize>, Option<[Vec<Atom>; 4]>>,\n')
anchor = '            denominator_identities: HashMap::new(),\n'
assert text.count(anchor) == 1
text = text.replace(anchor, anchor + '            highpoint_rank_lowering: false,\n            highpoint_coordinate_identities: HashMap::new(),\n')
old = '''            let factors = self.denominator_identity(active)?;
            let mut result = zero();'''
new = '''            let lowered = if self.highpoint_rank_lowering && rank > 0 {
                self.highpoint_coordinate_identity(active)?
            } else {
                None
            };
            let (factors, child_exponents) = if let Some(directions) = lowered {
                let mu = exponents.iter().position(|&n| n > 0).unwrap();
                let mut rest = exponents;
                rest[mu] -= 1;
                (directions[mu].clone(), rest)
            } else {
                (self.denominator_identity(active)?, exponents)
            };
            let mut result = zero();'''
assert text.count(old) == 1
text = text.replace(old, new)
anchor = '                let value = self.moment(&child, exponents)?;'
assert text.count(anchor) == 1
text = text.replace(anchor, '                let value = self.moment(&child, child_exponents)?;')
anchor = '    pub(crate) fn denominator_identity('
assert text.count(anchor) == 1
text = text.replace(anchor, (here / 'coordinate_method.rs').read_text() + '\n' + anchor)
path.write_text(text)

path = candidate / 'crates/iregi-rust/src/plan.rs'
text = path.read_text()
for indent in [32, 24]:
    anchor = ' ' * indent + 'certified_planar_chart,\n' + ' ' * (indent - 4) + ')'
    assert text.count(anchor) == 1, (indent, text.count(anchor))
    text = text.replace(anchor, ' ' * indent + 'certified_planar_chart,\n' + ' ' * indent + 'settings.invariants == InvariantInput::FromShifts\n' + ' ' * (indent + 4) + '&& settings.input_policy == InputPolicy::Preserve\n' + ' ' * (indent + 4) + '&& (6..=7).contains(&n),\n' + ' ' * (indent - 4) + ')')
anchor = '    certified_planar_chart: Option<usize>,\n) -> Result<(Vec<[Atom; 4]>, Vec<MasterLeaf>, Vec<(Atom, Atom)>), ReductionError> {'
assert text.count(anchor) == 1
text = text.replace(anchor, anchor.replace('\n)', '\n    highpoint_rank_lowering: bool,\n)'))
anchor = '    if let Some(omitted) = certified_planar_chart {'
assert text.count(anchor) == 2
start = text.index('fn compile_pv(')
head, tail = text[:start], text[start:]
tail = tail.replace(anchor, '''    if highpoint_rank_lowering {
        compiler.enable_highpoint_rank_lowering().map_err(ReductionError::Preparation)?;
    }
''' + anchor, 1)
path.write_text(head + tail)

patch = subprocess.run(['diff', '-ru', str(base), str(candidate)], capture_output=True, text=True)
assert patch.returncode == 1
(here / 'candidate.patch').write_text(patch.stdout)
record = dict(initial, status='private_source_prepared_only',
              candidate_source_hashes={str(p.relative_to(candidate)): sha(p) for p in candidate.rglob('*') if p.is_file()},
              candidate_patch_sha256=sha(here / 'candidate.patch'),
              protected_input_hashes={str(p.relative_to(root)): sha(p) for p in [Path(__file__), here / 'coordinate_method.rs', here / 'source-initial.json']},
              scope='Only preserved ordinary FromShifts unit-power h0 N6/N7 PV tensor paths enable the independent structural policy. Rank zero and pentagon routing unchanged. Direct with_distances compilers retain the old default. Symbolica Matrix::inv plus Matrix multiplication computes four RHS at once per active chart. Structurally singular chart sets fall back to unchanged constant identity; numerical singular charts retain existing guards. No runtime global selector, no amplitude-variable fastpath, no production changes; uncompiled and unqualified.')
(here / 'source-prepared.json').write_text(json.dumps(record, indent=2) + '\n')
print(record['status'])
