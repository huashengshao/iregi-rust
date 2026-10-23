#!/usr/bin/env python3
"""Reconstruct the paired public protocol from the committed corpus."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'target/guard-context-reuse';E=ROOT/'validation/guard-context-reuse'
src=subprocess.check_output(['git','show','80949db:crates/iregi-rust/tests/concurrent_workspaces.rs'],cwd=ROOT,text=True)
src='\n'.join(line for line in src.splitlines() if not line.startswith('//!'))
tail=(E/'protocol_tail.rs').read_text()
output=''
for name in ['baseline','candidate']:
 output+=f'mod {name} {{\nuse iregi_guard_{name} as iregi_rust;\n'+src+'\n'+tail+'\n}\n'
output+='fn main() { let baseline = baseline::corpus_snapshots(); let candidate = candidate::corpus_snapshots(); assert_eq!(baseline, candidate, "all status/coefficient/precision/sign/statistics metadata must match"); println!("PASS {} sequential batch snapshots; no concurrent execution", baseline.len()); }\n'
p=OUT/'protocol.rs'
if p.exists() and p.read_text()!=output:raise SystemExit('existing protocol source differs; preserve and investigate before replacing')
p.write_text(output)
(E/'protocol-source.json').write_text(json.dumps({'source_revision':'80949db','corpus_source':'crates/iregi-rust/tests/concurrent_workspaces.rs','protocol_source_sha256':hashlib.sha256(output.encode()).hexdigest(),'tail_sha256':hashlib.sha256(tail.encode()).hexdigest(),'scope':'ordinary/Dual and Float128 mixed-success corpus; all coefficients represented exactly, precision metadata, signed zeros, diagnostics and work counts'},indent=2)+'\n')
