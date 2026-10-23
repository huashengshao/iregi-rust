#!/usr/bin/env python3
"""Compile independent unit binaries from copies; original archives stay frozen."""
from pathlib import Path
import os,json,hashlib,subprocess,shutil,time,concurrent.futures,argparse
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'target/guard-context-reuse';E=ROOT/'validation/guard-context-reuse';D=ROOT/'target/stack-reuse-current-workspace/deps';S=ROOT/'target/cargo-build/debug/deps'
os.sched_setaffinity(0,{10,11})
parser=argparse.ArgumentParser();parser.add_argument('--variant',choices=['baseline','candidate']);parser.add_argument('--suffix',default='');args=parser.parse_args()
suffix=('-'+args.suffix) if args.suffix else ''
base=['rustc','--test','--edition=2024','-C','opt-level=0','-L',f'dependency={D}','-L',f'dependency={S}','-L',f'native={ROOT}/target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib']
for name,path in [('iregi_masters',D/'libiregi_masters-0d5459afd211649c.rlib'),('oneloop',D/'liboneloop-8562c3cbbf948c0e.rlib'),('symbolica',D/'libsymbolica-5cca42ee48491872.rlib'),('serde',S/'libserde-fc3dcd4b8c210596.rlib'),('serde_json',S/'libserde_json-3b583d0e8aa0facc.rlib'),('thiserror',S/'libthiserror-b877110d28821624.rlib')]:base+=['--extern',f'{name}={path}']
def build(variant):
 copy=OUT/(variant+'-tests-source'+suffix)
 if copy.exists():raise RuntimeError(f'refusing to replace {copy}; inspect previous build first')
 shutil.copytree(OUT/variant,copy)
 src=copy/'crates/iregi-rust/src/lib.rs'
 if variant=='candidate':
  stability=src.parent/'stability.rs';text=stability.read_text();assert text.rstrip().endswith('}')
  stability.write_text(text.rstrip()[:-1]+'\n'+(E/'context_tests.rs').read_text()+'\n}\n')
  execution=src.parent/'execution.rs';text=execution.read_text();assert text.rstrip().endswith('}')
  execution.write_text(text.rstrip()[:-1]+'\n'+(E/'execution_tests.rs').read_text()+'\n}\n')
  # Existing direct guard tests also compare the cached implementation.
  for relative,names in [('stability.rs',['inspect_lane_with_accuracy','inspect_primal_lane','inspect_output_precision_lane']),('stability/quadrature.rs',['inspect_quadrature_lane'])]:
   path=src.parent/relative;text=path.read_text()
   for name in names:
    start=text.index('    pub(crate) fn '+name+'<T: NativeFloat>')
    body=text.index(') -> Option<String> {',start)+len(') -> Option<String> ')
    end=text.index('\n    }',body)+6
    original=text[body+1:end-1].strip()
    call=original.replace('::<T, false>','::<T, true>')
    if '\n            None,' in call: call=call.replace('\n            None,','\n            Some(&mut context),')
    else: call=call.replace(', None)',', Some(&mut context))')
    assert 'Some(&mut context)' in call,(name,call)
    replacement='{\n        let expected = '+original+';\n        let mut context = GuardContext::new(self, prototype, accuracy_bits);\n        let actual = '+call+';\n        assert_eq!(actual, expected, "cached '+name+' differs");\n        expected\n    }'
    text=text[:body]+replacement+text[end:]
   path.write_text(text)
 binary=OUT/(variant+'-unit'+suffix);cmd=base+['--crate-name','guard_'+variant+'_unit',str(src),'-o',str(binary)]
 env=dict(os.environ,CARGO_CRATE_NAME='iregi_rust',CARGO_MANIFEST_DIR=str(src.parent.parent),CARGO_PKG_NAME='iregi-rust',CARGO_PKG_VERSION='0.1.0');start=time.monotonic()
 with (E/f'{variant}-unit{suffix}-compile.log').open('w') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 rec={'command':cmd,'exit_code':r.returncode,'seconds':time.monotonic()-start,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest() if r.returncode==0 else None,'source_sha256':{str(p.relative_to(copy)):hashlib.sha256(p.read_bytes()).hexdigest() for p in copy.rglob('*') if p.is_file()}};(E/f'{variant}-unit{suffix}-compile.json').write_text(json.dumps(rec,indent=2)+'\n');print(variant,r.returncode,flush=True);return r.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:codes=list(pool.map(build,[args.variant] if args.variant else ['baseline','candidate']))
raise SystemExit(max(codes))
