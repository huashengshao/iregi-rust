#!/usr/bin/env python3
"""Review frozen saved evidence only; no producer import or native/PID work."""
from pathlib import Path
from fractions import Fraction
import argparse
import ast
import hashlib
import importlib.util
import io
import json
import re
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAP = ROOT / 'validation/quad-original-iregi-small-n-rank7'
PRIVATE = 'target/quad-iregi-source-audit/rank7-n1-n5-corpus'
OLDROOT = '/shared/external/iregi/iregi-rust/'
PIN = '9b614c6567c28d23039053de390a7da5c665f4a57a978d54cd3148519fb3cb62'
checks = 0

def require(ok, message):
    global checks
    checks += 1
    if not ok:
        raise ValueError(message)

def sha(b): return hashlib.sha256(b).hexdigest()
def desc(b): return {'sha256':sha(b),'bytes':len(b)}
def load(b): return json.loads(b,parse_float=str)
def own_import(path, name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def archive(body):
    files = {}
    with tarfile.open(fileobj=io.BytesIO(body),mode='r:gz') as stream:
        for row in stream:
            require(row.isfile() and row.name not in files, 'regular unique archive members')
            p = Path(row.name)
            require(not p.is_absolute() and '..' not in p.parts, 'safe source/data archive path')
            files[row.name] = stream.extractfile(row).read()
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-live-copy-origins',action='store_true',help='Optionally compare preserved text/data copies with existing private origins; never reads omitted products.')
    parser.add_argument('--write-review',action='store_true',help='Explicitly regenerate the local review record; default replay writes nothing.')
    args = parser.parse_args()
    manifest_bytes = (CAP/'manifest.json').read_bytes()
    require(sha(manifest_bytes) == PIN,'frozen9b614 companion manifest')
    manifest = load(manifest_bytes)
    capbytes = {p.name:p.read_bytes() for p in CAP.iterdir() if p.is_file()}
    require(set(capbytes) == set(manifest['capsule_files']) | {'manifest.json'},'exact seven-file capsule inventory')
    for name,expected in manifest['capsule_files'].items():
        require(desc(capbytes[name]) == expected,'capsule bytes '+name)
    require(sha(capbytes['check.py']) == 'a202925e87ab6aef866563c42c3c39eda73f081b47d2ca72214013af8f12850b','exact inspected independent portable checker')
    parents = {}
    for name,expected in manifest['parent_files'].items():
        b = (ROOT/name).read_bytes()
        require(desc(b) == expected,'parent byte closure '+name)
        parents[name] = b
    require(len(parents) == 30,'all 30 declared parent files')
    packages = ['validation/quad-original-iregi-rank7-adjudication','validation/quad-original-iregi-positive-rank-anchors','validation/quad-original-iregi-small-n-rank7']
    expected_pins = ['7c27b1eded867c4373ee6111b54a1f88a1d944c61cd1a871c1403947c008fe07','6fbc3465f3e2ee54a789b0ea556a51616744437e18d53bff29cec177755d9ddb',PIN]
    imports = {}
    source_programs = {}
    for package,pin in zip(packages,expected_pins):
        base = ROOT/package
        require(sha((base/'manifest.json').read_bytes()) == pin,'pinned parent/capsule chain')
        src = (base/'check.py').read_bytes()
        tree = ast.parse(src)
        imported = [node.module if isinstance(node,ast.ImportFrom) else ','.join(n.name for n in node.names)
                    for node in ast.walk(tree) if isinstance(node,(ast.Import,ast.ImportFrom))]
        require(not any(n in imported for n in ['os','subprocess','ctypes','socket']),'no native/process interfaces in replay checker')
        imports[package+'/check.py'] = imported
        source_programs[package+'/check.py'] = sha(src)
    # Only these inspected independent, hash-pinned portable checkers execute.
    # Historical producers/comparators/native-hash/PID audit scripts remain bytes.
    portable = own_import(CAP/'check.py','independent_smallN_saved_capsule')
    files,helpers,inherited = portable.restore(manifest)
    portable_result = portable.replay(files,helpers,manifest)
    require(len(files) == 452,'full source/saved alias restoration')
    require(inherited['N6_records_replayed'] == 18826 and inherited['N6_old_binary64_gate'] == 'failed_unchanged'
            and inherited['positive_rank_reference_slots_replayed'] == 2720 and inherited['positive_rank_N7_pole_gates_replayed'] == 1050,'unchanged inherited saved proof/failures')
    members = archive(capbytes['payload.tar.gz'])
    require({n:desc(b) for n,b in members.items()} == manifest['payload_members'] and len(members) == 102,'all102 physical payload members')
    origins = load(capbytes['payload-origins.json'])
    require(set(origins) == set(manifest['preserved_files']) | set(manifest['inherited_aliases']) and len(origins) == 134,'all133 preserved plusonealias origins')
    live_origin_copies = 0
    for name,row in manifest['preserved_files'].items():
        b = members[row['member']]
        require(desc(b) == {k:row[k] for k in ('sha256','bytes')} == {k:origins[name][k] for k in ('sha256','bytes')}
                and b == files[name],'all preserved/origin/alias exact bytes')
        if args.check_live_copy_origins:
            origin = Path(origins[name]['origin'])
            require(origin.is_file() and origin.read_bytes() == b,'private text/data copy origin '+name)
            live_origin_copies += 1
    for name,row in manifest['inherited_aliases'].items():
        require(files[name] == files[row['inherited_source']] and desc(files[name]) == {k:row[k] for k in ('sha256','bytes')}
                == {k:origins[name][k] for k in ('sha256','bytes')},'exact inherited conditioned-fixture alias')
    require(len(manifest['omitted_compiled_products']) == 1 and manifest['symbolica_license_literal_included'] is False,'omitted copied product and literal-license policy')

    # Scan archived and restored data recursively, never load binary products.
    forbidden = {'.a','.o','.so','.dylib','.dll','.exe','.rlib','.rmeta','.mod','.smod','.pyc','.pyo'}
    literal = re.compile(rb'S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}')
    scanned = set()
    scan_stats = {'unique_content_layers':0,'archive_members':0,'bytes':0}
    def scan(name,body):
        require('__pycache__' not in Path(name).parts and Path(name).suffix not in forbidden,'no cache/product suffix '+name)
        require(not body.startswith((b'\x7fELF',b'!<arch>')) and not literal.search(body),'no native or literal-license content '+name)
        digest = sha(body)
        if digest in scanned:
            return
        scanned.add(digest)
        scan_stats['unique_content_layers'] += 1
        scan_stats['bytes'] += len(body)
        if body.startswith(b'\x1f\x8b'):
            nested = archive(body)
            scan_stats['archive_members'] += len(nested)
            for n,b in nested.items(): scan(name+'::'+n,b)
    for n,b in capbytes.items(): scan(n,b)
    for n,b in parents.items(): scan(n,b)
    for n,b in files.items(): scan(n,b)
    canonical = {Path(n).name:b for n,b in files.items() if n.startswith('target/quad-iregi-source-audit/source-v2/')}
    v2 = load(files['target/quad-iregi-source-audit/source-v2.json'])
    require(len(canonical) == 22 and {n:sha(b) for n,b in canonical.items()} == v2['source_sha256'],'full22 canonical source programs')
    require('cmatrix_base.f90' in canonical and 'cti_reduce.f90' in canonical and 'csi_reduce.f90' in canonical,'original complex matrix/tensor/scalar sources retained')
    require('reference-context/references/madgraph/vendor/IREGI/src/oneloop/COPYING' in files,'upstream OneLOop source license retained')

    protocol = load(files[PRIVATE+'/protocol.json'])
    saved = load(files[PRIVATE+'/capture-001/validation.json'])
    run = load(files[PRIVATE+'/capture-001/run.json'])
    qualification = load(capbytes['qualification.json'])
    require(sha(capbytes['qualification.json']) == '8148a0d7def644a722434e19c556d542b3ca33c547f8d1b3ad6afd2fd970bcbf'
            and capbytes['qualification.json'] == files[PRIVATE+'/qualification.json'],'exact scoped qualification copy')
    require(run['status'] == 'passed' and run['inputs_unchanged'] and len(run['inputs']) == 304 and len(run['steps']) == 26,'saved full admission and complete transport')
    expected = dict(protocol['bindings'])
    for name in ['protocol.json','independent-source-review.json','root-execution-grant.json']:
        expected[OLDROOT+PRIVATE+'/'+name] = sha(files[PRIVATE+'/'+name])
    require(expected == run['inputs'],'all304 exact declared bindings retained')
    by_origin = {}
    for package in packages:
        for name,row in load((ROOT/package/'payload-origins.json').read_bytes()).items():
            by_origin.setdefault(row['origin'],set()).add(sha(files[name]))
    for n,b in files.items():
        if n.startswith('validation/'):
            by_origin.setdefault(OLDROOT+n,set()).add(sha(b))
    available_guards = historical_guards = 0
    for origin,digest in expected.items():
        if origin in by_origin:
            require(digest in by_origin[origin],'available preserved source/data admission')
            available_guards += 1
        else:
            historical_guards += 1
    require((available_guards,historical_guards) == (184,120),'available versus historical source/tool guards explicit')
    raw_outputs = native_attestations = 0
    for name,digest in run['outputs'].items():
        key = PRIVATE+'/capture-001/'+name
        if key in files:
            require(sha(files[key]) == digest,'all present raw stream/worker bindings')
            raw_outputs += 1
        else:
            require(manifest['omitted_compiled_products'][key]['captured_sha256'] == digest,'omitted native digest is historical only')
            native_attestations += 1
    require((raw_outputs,native_attestations) == (78,1),'79 output bindings:78 raw files plusoneomitted native')
    fixture_key = protocol['conditioned_fixture'].removeprefix(OLDROOT)
    fixture = load(files[fixture_key])
    samples = {s['id']:s for s in fixture['samples']}
    for i,case in enumerate(protocol['runtime']['cases']):
        request_key = case['input'].removeprefix(OLDROOT)
        raw = files[request_key]
        lines = raw.decode().splitlines()
        require(sha(raw) == case['request_sha256'] and lines[0].split() == ['EVAL',case['id'],'tensor',str(case['mode']),str(case['propagators']),'7','0',case['exact_scale'],'0','1e-6']
                and lines[-1] == 'QUIT' and len(lines) == case['propagators']+2,'all26 explicit ordinary original-mode requests')
        props = samples[case['sample']]['propagators'][:case['propagators']]
        require(case['exact_propagators'] == props and case['exact_scale'] == samples[case['sample']]['mu'],'actual conditioned fixture family')
        for line,p in zip(lines[1:-1],props):
            require([Fraction(x)for x in line.split()] == [Fraction(x)for x in p['shift']+p['mass_squared']]+[Fraction(1)],'exact routing/mass/power serialization')
        step = run['steps'][i]
        require(step['status'] == 'exited' and step['returncode'] == 0 and step['owned_group_gone'] is True
                and step['timeout_seconds'] == (20 if case['propagators'] <= 4 else 45),'saved transport/budget/group receipt (notfreshPID)')
    require(run['bound_seconds'] == 300 and run['cleanup_reserve_seconds'] == 30,'aggregate/reserve retained')
    own = own_import(HERE/'math_replay.py','own_independent_complex_fraction_replay')
    result = own.replay(protocol,saved,[files[PRIVATE+f'/capture-001/request-{i}.stdout']for i in range(26)],
                        files[protocol['N5_base']['raw'].removeprefix(OLDROOT)],samples['base']['propagators'][:5])
    require(result['independently_rederived_records'] == manifest['saved_numerical_records'] == 42018,'own independent allrecord replay')
    require(qualification['N2_PV_no_RESULT_arrays'] == 3 and qualification['stable_but_rejected_N3_N4_PV_arrays'] == 6
            and qualification['PV_vs_IBP_failing_finite_slots'] == 486 and qualification['TIRust_compared_slots'] == 0,'failure partition/noTIRust comparison claim')
    for key in ['currentCargo_qualified','full_rank7_domain_qualified','finite_coefficients_independently_certified_by_identities','precision_convergence_qualified','performance_qualified']:
        require(qualification[key] is False,'no qualification promotion '+key)
    require(manifest['TIRust_or_currentCargo_qualified'] is False and manifest['full_rank7_domain_qualified'] is False and manifest['performance_qualified'] is False,'no manifest promotion')
    require(all((CAP/n).read_bytes() == b for n,b in capbytes.items()),'frozen capsule unchanged')
    report = {'status':'passed_independent_frozen_smallN_source_copy_and_saved_numeric_review','reviewer':'/root/dual_pilot_finish/timing_note','findings':[],
              'checks':checks,'manifest_sha256':PIN,'capsule_file_hashes':{n:sha(b)for n,b in capbytes.items()},
              'parent_manifest_hashes':dict(zip(packages,expected_pins)),'reviewer_script_sha256':sha(Path(__file__).read_bytes()),
              'own_math_module_sha256':sha((HERE/'math_replay.py').read_bytes()),'parent_files_verified':len(parents),
              'payload_members':len(members),'preserved_files':len(manifest['preserved_files']),'origin_records_verified':len(origins),
              'optional_existing_private_text_data_origin_copies_checked':live_origin_copies,'canonical_source_files_verified':len(canonical),
              'content_scan':scan_stats,'native_or_pycache_or_literal_license_found':False,'inspected_portable_checker_hashes':source_programs,
              'inspected_portable_checker_imports':imports,'portable_restore_files':len(files),'inherited_saved_proof':inherited,
              'portable_saved_replay':portable_result,'available_source_data_guards':available_guards,'historical_native_tool_guards':historical_guards,
              'raw_output_files_hashed':raw_outputs,'omitted_native_output_hashes_historical_only':native_attestations,
              'independent_numeric_result':result,'producer_comparator_or_original_native_PID_audit_imported_or_executed':False,
              'new_build_integral_native_hash_or_PID_work':False,'capsule_edited':False,
              'TIRust_or_currentCargo_or_full_rank7_or_performance_qualified':False,
              'limitations':['Native stability and independent pole/parity/scaling identities do not independently certify every finite coefficient or achieved33digit precision.',
                             'Three N2PV noRESULT arrays remain missing; six stable incorrect N3/N4PV arrays remain rejected diagnostics.',
                             'Omitted native/toolchain hashes and historical process absence are attestations, not refreshed native closure/PID checks.',
                             'No new TIRust/currentCargo/generalized/complexmass/Dual/physical/performance qualification.']}
    report_bytes = (json.dumps(report,indent=2)+'\n').encode()
    if args.write_review:
        (HERE/'review.json').write_bytes(report_bytes)
    print(json.dumps({'status':report['status'],'report_sha256':sha(report_bytes),'review_record_written':args.write_review,'checks':checks,
                      'arrays':result['complete_arrays'],'slots':result['complete_complex_slots'],'records':result['independently_rederived_records'],
                      'live_text_copy_origins':live_origin_copies,'content_scan':scan_stats},indent=2))

if __name__ == '__main__':
    main()
