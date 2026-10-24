"""Hash source/dependency inventories; never launches a compiler or evaluator."""
import ast,json,pathlib,shutil
import harness_common as h

def assignment(path,name):
    node=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
    return ast.literal_eval(node.value)

def main():
    h.require(not (h.HERE/'protocol.json').exists(),'protocol already exists')
    previous=h.ROOT/'target/public-highpoint/thin-n6-generic-fixed/compare.py'
    groups=assignment(previous,'EXACT_TESTS')
    groups['thin_n6::tests'].add('thin_n6::tests::malformed_dimensions_reset_before_any_row_sized_allocation')
    groups['types::primal_envelope_tests'].add('types::primal_envelope_tests::ordinary_destination_does_not_allocate_or_inspect_private_envelopes')
    groups['workspace_policy']={
        'execution::tests::workspace_policy_default_preserves_values_without_sidecar_allocation',
        'execution::tests::workspace_policy_isolates_retry_while_sharing_exact_arithmetic_cache',
        'execution::tests::workspace_policy_survives_dual_specialization_eager_and_lazy_children',
        'execution::tests::workspace_policy_certificate_totals_reset_before_empty_and_invalid_calls',
        'execution::tests::workspace_policy_counts_nested_analytic_work_without_changing_ordinary_counts',
    }
    groups['six_point::tests']={'six_point::tests::unsupported_domain_is_rejected_before_symbolic_preparation'}
    groups['cofactor_masks_remain_private']={'certified_planar::tests::cofactor_masks_remain_private_to_explicit_six_point_children'}
    h.require(sum(map(len,groups.values()))==34,'test count differs')
    inputs=h.closure_bindings()
    for root in [h.HERE/'core',h.PARENT/'production-baseline']:
        for p in sorted(root.rglob('*')):
            if p.is_file():h.bind(p,inputs)
    for name in ['source.json','sources.tar.gz','integration.patch','source-review.json','hardening.json',
                 'harness_common.py','build.py','run.py','compare.py','compare-lifecycle.py','prepare_protocol.py',
                 'protocol-initial.json','protocol-draft-initial.json','receipt-bound-hardening.json']:
        h.bind(h.HERE/name,inputs)
    for name in ['source.json','sources.tar.gz','baseline.json','math-reuse.json','fixture-closure.json',
                 'independent-review.json','independent-review-final.json','execution-independent-review.json','package-audit.json',
                 'ordinary-equivalence-driver.rs','ordinary-equivalence-source.json',
                 'public-lifecycle-driver.rs','public-lifecycle-source.json','lifecycle-driver-review.json']:
        h.bind(h.PARENT/name,inputs)
    for path in [previous,h.FIXTURE,h.REFERENCE,h.SHARED,h.ROOT/'validation/public-highpoint/qualification.json',
                 h.ROOT/'target/reference/iregi-reference-original',
                 h.ROOT/'target/public-highpoint/thin-n6-mask/compare-lifecycle.py',
                 h.ROOT/'validation/highpoint-thin-n6-generic/qualification.json']:
        h.bind(path,inputs)
    history=h.ROOT/'validation/highpoint-thin-n6-generic'
    qualified=h.load(history/'qualification.json')
    for bits in [128,256]:
        name=f'fixed/n6-rank3-{bits}-001/result.json';h.bind(history/name,inputs,qualified['files'][name])
    compiler=pathlib.Path(shutil.which('rustc')).resolve();h.bind(compiler,inputs)
    protocol={'schema_version':1,'revision':2,'status':'pending_root_source_review','reviewers':[],
        'source_manifest_sha256':h.sha(h.HERE/'source.json'),'source_patch_sha256':h.sha(h.HERE/'integration.patch'),
        'build_bound_seconds':180,'exact_expected_tests':34,
        'exact_groups':[{'filter':f,'names':sorted(names)} for f,names in groups.items()],
        'runtime_bounds_seconds':h.BOUNDS,'compiler_path':str(compiler),'inputs':inputs,
        'compile_profile':'Isolated native-object debug closure; opt0/debuginfo0/stripdebuginfo; distinct baseline/candidate rustc metadata; no dependency rebuild or live search fallback.',
        'required_build_products':h.OUTPUTS,
        'public_scope':{'propagators':6,'rank_limit':3,'powers':[1]*6,'h':0,'algorithm':'PV','invariants':'FromShifts','input_policy':'Preserve','convention':'IregiNative','weights':'Components','numerical_components':1},
        'numerical_gates':{'rank3':{'fixture_rows':[0],'working_bits':[128,256],'requested_bits':53,'native_complex_slots':140,'exact_zero_poles':105,'normalized_original_tolerance':'1e-10','convergence_tolerance':'2^-80'},
            'lifecycle':{'rank':2,'working_bits':128,'requested_bits':53,'calls':11,'successful_lanes':17,'rejected_lanes':7,'empty_calls':2,'native_complex_slots':1020,'contraction_slots':68,'normalized_original_singleton_contraction_tolerance':'1e-10'},
            'ordinary':{'paired_cases':12,'domains':['f64','DoubleFloat','Float128'],'variant_bound_seconds':120,'complete_exact_output_comparison':True}},
        'execution_sequence':['build.py','run.py exact','compare.py exact','run.py ordinary-baseline','run.py ordinary-candidate','compare.py ordinary','run.py 128','compare.py 128','ROOT coordinates256','run.py 256','compare.py 256','ROOT coordinates lifecycle','run.py lifecycle','compare-lifecycle.py'],
        'limits':['No live source application, production adoption, rank7 numerical execution, broader topology/domain qualification or performance gate.','Exact historical inputs/status/layout are preserved; historical private numerical arrays use unchanged1e-10 with complete precision/value difference inventory.','Every failed build/test/capture/comparator is retained; no automatic retry, timeout extension or threshold change.','This pending source protocol is not execution permission.']}
    h.save(h.HERE/'protocol-draft.json',protocol)
    protocol['inputs']=dict(inputs);h.bind(h.HERE/'protocol-draft.json',protocol['inputs'])
    h.save(h.HERE/'protocol.json',protocol)
    print({'protocol_sha256':h.sha(h.HERE/'protocol.json'),'inputs':len(protocol['inputs']),'tests':34,'status':protocol['status']})
if __name__=='__main__':main()
