"""Independent saved numeric audit; standard library only, no producer imports.

audit(read_bytes) takes project-relative original-path aliases and returns a
deterministic receipt. No integral, kernel, native or package-tree work occurs.
The failed coarse catalogue remains failed. Only the separate fixed20/32/48
refinement can become a scoped empirical rank-six collinear anchor.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from itertools import product
import hashlib
import json
from pathlib import Path
import re

BASE = "target/collinear-rank6-parameter-oracle-refinement-v3"
OLD = "target/collinear-rank6-parameter-oracle"
CAPTURE = BASE+"/capture-001"
OLD_CAPTURE = OLD+"/capture-001"
PINS = {
    BASE+"/manifest.json":"d39224195a1c98f41185edfc40b1d19daf552f56a1f2a033b9a8e1ad60f6c94b",
    BASE+"/catalog.json":"4a4e79b2b41503aa912eba5ee5eef2f7404959e068d803822e6b7987f85dc36a",
    OLD+"/fixture.json":"60e28f3cd6d66276fca6c8cadae5876e232dec5e14a9bb9660acb1896e5d709e",
    CAPTURE+"/receipt.json":"2205034b7bfec5802709472a162cef09d938b98336b8f7b2c03aaa8832ecfc77",
    CAPTURE+"/comparison.json":"039814ebc2a9e8885f3057010c7067553ddc41de069a10d6fcd1145c13f0c2f3",
    BASE+"/numerical-release.json":"ba165080f4a588410c1f9c0b77d3d5a57b67fe0ca78ddb03e61387b9a09283ca",
    OLD_CAPTURE+"/receipt.json":"1efca87ea59aae202882a52af6729ed580bb99e3b642dd5fdabd3de125d0b91c",
    OLD_CAPTURE+"/comparison.json":"de56442c6e4018bac35eba136e0292f57d46e414fb2302840408a35009385a27",
    OLD+"/independent/receipt.json":"5ec5d4ede3bfab86492aae3cbe2f17b6dba0e1c6790d2b3016d9bc0044fb6693",
    BASE+"/source-review.json":"5084f57be80dd1c24bb5d2ce567aa90abd8607a4f11a9d07c7a367f5a778b7bc",
}
DECIMAL = re.compile(r"\s*[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\s*")
SLOTS = ["uv1","ir1","ir2","finite"]
LIMIT = Q(1,10**20)


def require(ok,message):
    if not ok:
        raise ValueError(message)


def decode(body):
    def pairs(items):
        value = {}
        for key,item in items:
            require(key not in value,"duplicate JSON key")
            value[key] = item
        return value
    def invalid(value):
        raise ValueError("nonfinite JSON constant "+value)
    return json.loads(body,object_pairs_hook=pairs,parse_constant=invalid,parse_float=Decimal)


def decimal(value):
    require(type(value) is str and DECIMAL.fullmatch(value),"quoted finite decimal required")
    return Q(value)


def tensor(raw):
    require(type(raw) is list and len(raw)==330,"all330 moment rows required")
    answer = []
    for row in raw:
        require(type(row) is list and len(row)==4,"four Laurent slots required")
        for z in row:
            require(type(z) is list and len(z)==2,"two complex components required")
            answer.append(tuple(decimal(v) for v in z))
    return answer


def positive_table(raw):
    require(type(raw) is list and len(raw)==330,"all330 scalar rows required")
    answer = []
    for row in raw:
        require(type(row) is list and len(row)==4,"four scalar slots required")
        answer.extend(decimal(v) for v in row)
    require(all(v>=0 for v in answer),"nonnegative magnitude witness required")
    return answer


def norm(z):
    return z[0]*z[0]+z[1]*z[1]


def discrepancy(a,b,unit_squared):
    require(unit_squared>0,"positive dimensional unit required")
    return norm((a[0]-b[0],a[1]-b[1]))/max(unit_squared,norm(b))


def display(square):
    with localcontext() as context:
        context.prec = 80
        return str((Decimal(square.numerator)/Decimal(square.denominator)).sqrt())


def identity(record):
    return tuple(record.get(k) for k in ("kind","grid","moment","slot","other"))


def controls():
    count = 0
    def rejects(function,*args):
        nonlocal count
        try:
            function(*args)
        except (ValueError,TypeError,KeyError):
            count += 1
            return
        raise ValueError("independent negative control unexpectedly accepted")
    for value in (None,True,0,"NaN","inf","1/3","1_0",""):
        rejects(decimal,value)
    rejects(decode,'{"a":1,"a":2}')
    rejects(decode,'{"a":Infinity}')
    rejects(tensor,[])
    rejects(tensor,[[["0","0"]]*3 for _ in range(330)])
    require(discrepancy((Q(0),Q(1)),(Q(0),Q(0)),Q(1))==1,"imaginary difference omitted")
    require(LIMIT<=LIMIT and LIMIT+Q(1,10**40)>LIMIT,"exact threshold boundary differs")
    return count


def audit(read_bytes):
    seen,cache = {},{}
    def read(alias,expected=None):
        require(type(alias) is str and not alias.startswith("/") and ".." not in Path(alias).parts,
                "safe relative saved alias required")
        require(Path(alias).suffix in {".json",".txt",".log"},"only saved data aliases admitted")
        if alias not in cache:
            body = read_bytes(alias)
            require(type(body) is bytes and len(body)<16000000,"bounded saved bytes required")
            cache[alias] = body
            seen[alias] = dict(sha256=hashlib.sha256(body).hexdigest(),bytes=len(body))
        require(expected is None or seen[alias]["sha256"]==expected,"saved input digest changed: "+alias)
        return cache[alias]
    def load(alias,expected=None):
        return decode(read(alias,expected))
    for alias,pin in PINS.items():
        read(alias,pin)
    manifest,catalogue,fixture,receipt,saved,release,old_receipt,old_comparison,old_audit,source_review = [load(alias) for alias in PINS]
    require(old_comparison["status"]=="failed_or_partial_fixed_grid_empirical_gates"
            and old_comparison["empirical_rank6_prefix_eligible_pending_independent_saved_audit"] is False
            and old_audit["empirical_catalogue_passed"] is False
            and old_audit["empirical_failures"]==old_comparison["failures"]
            and len(old_comparison["failures"])==6 and len(old_comparison["diagnostic_disagreements"])==5,
            "original failed catalogue or its prior independent audit was changed")
    require(source_review["status"]=="passed_independent_source_delta_review_no_numerical_execution"
            and source_review["blocking_findings"]==[]
            and source_review["manifest"]["sha256"]==PINS[BASE+"/manifest.json"],"final source admission differs")
    require(catalogue["orders"]==[48] and catalogue["empirical_comparison_orders"]==[20,32,48] and catalogue["maps"]==["identity","reverse"]
            and catalogue["acceptance_rank"]==6 and catalogue["acceptance_moments"]==210
            and catalogue["rank"]==7,"frozen catalogue rank/order differs")
    sample = fixture["samples"][0]
    require(fixture["rank"]==7 and len(fixture["samples"])==1 and sample["n"]==3
            and sample["id"]=="n3_collinear_zero_Gram" and Q(sample["mu"])==3,
            "exact frozen collinear fixture identity differs")
    props = sample["propagators"]
    require(len(props)==3 and [[Q(v) for v in p["shift"]] for p in props]==
        [[0,0,0,0],[0,1,0,0],[0,2,0,0]]
        and [[Q(v) for v in p["mass_squared"]] for p in props]==[[1,0],[2,0],[3,0]]
        and all(type(p["power"]) is int and p["power"]==1 for p in props),"fixed geometry/masses/powers differ")
    exponents = sorted((a for a in product(range(8),repeat=4) if sum(a)<=7),
                       key=lambda a:(sum(a),-a[0],-a[1],-a[2]))
    require(len(exponents)==330 and len([a for a in exponents if sum(a)<=6])==210
            and all(sum(a)==7 for a in exponents[210:]),"independent basis/prefix differs")
    expected_grid_keys = [(order,mapping) for order in (20,32,48) for mapping in ("identity","reverse")]
    require([(g["order"],g["map"]) for g in catalogue["comparison_grids"]]==expected_grid_keys
            and len({g["id"] for g in catalogue["comparison_grids"]})==6
            and [g["order"] for g in catalogue["grids"]]==[48,48],"exact six-grid membership/order differs")
    require(receipt["status"]=="complete_catalogue_pending_independent_saved_audit"
            and receipt["manifest_sha256"]==PINS[BASE+"/manifest.json"]
            and receipt["catalog_sha256"]==PINS[BASE+"/catalog.json"]
            and receipt["comparison_sha256"]==PINS[CAPTURE+"/comparison.json"]
            and receipt["inputs_unchanged"] is True and receipt["cleanup_errors"]==[]
            and receipt["cancellation"] is None and receipt["native_processes_started"]==1
            and receipt["total_worker_rows"]==4608 and receipt["empirical_gates_passed"] is True
            and receipt["comparison_status"]=="all_fixed_grid_empirical_gates_passed_independent_saved_audit_pending"
            and receipt["admitted_quadrature_orders"]==[12,20,32,48]
            and receipt["bound_seconds"]==300 and receipt["cleanup_reserve_seconds"]==30
            and Q(receipt["elapsed_seconds_validation_only"])<=300,"saved terminal/count/failure scope differs")
    worker, = receipt["workers"]
    require(worker["topology"]==3 and worker["status"]=="complete" and worker["grids_completed"]==2
            and worker["rows"]==4608 and worker["batches"]==18 and worker["returncode"]==0
            and worker["owned_group_gone"] is True,"saved owned worker counters/state differ")
    ready = worker["ready"]
    require(ready["max_rows"]==256 and ready["outputs"]==1320 and ready["moments"]==330
            and ready["native_slots"]==4 and ready["parameters"]==5
            and ready["instruction_major_symbolica_batch"] is True and ready["native_normalization_included"] is True
            and ready["ir_poles_proven_zero"] is True,"saved worker layout differs")
    require(release["capture_receipt_sha256"]==PINS[CAPTURE+"/receipt.json"]
            and release["comparison_sha256"]==PINS[CAPTURE+"/comparison.json"]
            and release["outer_exit_code"]==0 and release["no_retry_or_more_orders"] is True
            and release["new_order"]==48 and release["new_rows"]==4608
            and release["old_20_32_grids_untouched"] is True
            and release["old_failed_12_catalogue_remains_failed"] is True
            and release["groups"]==[dict(owned_process_group=worker["owned_process_group"],actually_absent=True)],
            "saved release chain differs; no fresh process probe performed")
    artifact = load(CAPTURE+"/n3-symbolica-coefficients.json",worker["artifact_sha256"])
    require(artifact["basis"]==[list(a) for a in exponents] and artifact["outputs"]==1320
            and all(artifact["expressions"][4*m+s]=="0" for m in range(330) for s in (1,2)),
            "saved coefficient layout/proved IR strings differ")
    spec = catalogue["references"]["3"]
    review = load(catalogue["independent_reference_review"],manifest["bindings"][catalogue["independent_reference_review"]])
    admission = next(c for c in review["cases"] if c["id"]==spec["id"]+"-quad-IBP-001")
    require(admission["eligible_for_subsequent_full_array_comparison"] is True
            and admission["finite_array_independently_qualified"] is False,"original reference identity-only admission differs")
    ref_receipt = load(spec["receipt"],manifest["bindings"][spec["receipt"]])
    lines = read(spec["stdout"],manifest["bindings"][spec["stdout"]]).decode().splitlines()
    require(lines.count("READY IREGI_REFERENCE_QP_V1")==1,"quad READY witness differs")
    require([decode(l[10:]) for l in lines if l.startswith("PRECISION ")]==
        [dict(dbl_kind=16,olo_kind=16,storage_bits=128,binary_digits=113,decimal_digits=33)],"quad precision witness differs")
    ref_rows = [decode(l[7:]) for l in lines if l.startswith("RESULT ")]
    require(len(ref_rows)==1 and ref_rows[0]["id"]==spec["response_id"] and ref_rows[0]["stable"] is True
            and ref_rows[0]["poles"]==SLOTS and ref_receipt["outputs"]["stdout.txt"]==seen[spec["stdout"]]["sha256"],
            "diagnostic original response identity differs")
    reference = tensor(ref_rows[0]["moments"])
    records = {}
    for record in saved["records"]:
        key = identity(record)
        require(key not in records and type(record.get("passed")) is bool
                and type(record.get("affects_empirical_eligibility")) is bool,"duplicate or untyped saved record")
        records[key] = record
    consumed,categories,failures,diagnostics = set(),Counter(),[],[]
    recomputed = {}
    maxima,pair_maxima = {},{}
    def verify(expected):
        key = identity(expected)
        require(key in records and key not in consumed and records[key]==expected,"independent record mismatch: "+str(key))
        recomputed[key] = expected
        consumed.add(key); categories[expected["kind"]] += 1
        if not expected["passed"]:
            (failures if expected["affects_empirical_eligibility"] else diagnostics).append(expected)
    def compare(kind,grid,m,s,squared,other=None,gate=True):
        record = dict(kind=kind,grid=grid,moment=m,slot=s,squared_error=str(squared),error=display(squared),
            limit_squared=str(LIMIT),passed=squared<=LIMIT,affects_empirical_eligibility=gate)
        if other is not None:
            record["other"] = other
        verify(record)
        if kind not in maxima or squared>maxima[kind][0]:
            maxima[kind] = (squared,record)
        return record
    arrays,grid_summaries = {},[]
    normalization_max = Q(0)
    row_offset = batch_offset = new_row_offset = new_batch_offset = 0
    normalization_components = 0
    old_offsets = {}
    old_rows = old_batches = 0
    for g in old_receipt["grids"]:
        old_offsets[g["id"]] = (old_rows,old_batches)
        old_rows += g["worker_rows"]; old_batches += g["worker_batches"]
    require((old_rows,old_batches)==(3136,14),"old worker aggregate differs")
    for grid in catalogue["comparison_grids"]:
        order,mapping = grid["order"],grid["map"]
        reused = "reused_result" in grid
        source_receipt = old_receipt if reused else receipt
        entry = next(g for g in source_receipt["grids"] if g["id"]==grid["id"])
        prefix = (OLD_CAPTURE if reused else CAPTURE)+"/grids/"+grid["id"]
        if reused:
            require(grid["reused_result"]==prefix+"/result.json"
                    and entry["result_sha256"]==grid["reused_result_sha256"]==manifest["bindings"][grid["reused_result"]],
                    "old grid read-only pin differs")
        data = load(prefix+"/result.json",entry["result_sha256"])
        progress_pin = old_audit["input_bindings"][prefix+"/progress.json"]["sha256"] if reused else None
        progress = load(prefix+"/progress.json",progress_pin)
        require(data["basis"]==[list(a) for a in exponents] and data["native_slot_order"]==SLOTS
                and data["moments"]==330 and data["tensor_rank"]==7 and data["topology"]==3
                and data["order"]==order and data["map_permutation"]==([0,1,2] if mapping=="identity" else [2,1,0]),
                "full-array saved grid identity differs")
        points,batches = order**2,(order**2+255)//256
        require(data["points"]==data["worker_rows"]==grid["points"]==points
                and data["worker_batches"]==batches and progress["points_completed"]==points
                and progress["worker_batches"]==batches
                and (entry["worker_rows_before"],entry["worker_batches_before"])==
                    (old_offsets[grid["id"]] if reused else (new_row_offset,new_batch_offset)),"grid/progress/cumulative counters differ")
        row_offset += points; batch_offset += batches
        if not reused:
            new_row_offset += points; new_batch_offset += batches
        require(Q(data["minimum_observed_real_F"])>=1
                and Q(data["minimum_observed_imaginary_F"])==Q(data["maximum_observed_imaginary_F"])==0
                and data["F_domain_rounding_tolerance"]==0,"real positive F witnesses differ")
        require(data["simplex_volume_exact"]=="1/2" and abs(decimal(data["weights_sum"])-Q(1,2))<=Q(1,10**14),
                "saved simplex normalization witness differs")
        require(data["normalization_scale_Q_exact"]=="3" and data["accumulator_mantissa_bits"]==64
                and data["managed_memory_bound_bytes"]<=268435456,"fixed units/accumulator/managed-memory cap differs")
        units = [Q(3)**(sum(a)-2) for a in exponents]
        require([Q(v) for v in data["normalization_units_exact"]]==units,"all330 exact dimensional units differ")
        accumulator_units = [decimal(v) for v in data["normalization_units_accumulator"]]
        require(len(accumulator_units)==330 and all(u>0 for u in accumulator_units),"all330 finite accumulator units required")
        values,normalized = tensor(data["native_laurent"]),tensor(data["normalized_native_laurent"])
        positive_table(data["normalized_absolute_weighted_sums"])
        positive_table(data["max_observed_abs_normalized_integrand"])
        # Representation consistency, not a new quadrature accuracy threshold.
        # Sixteen 64-bit-mantissa ulps cover formatting and rescaling roundoff.
        rounding = Q(16,2**64)
        for m,unit in enumerate(units):
            require(abs(accumulator_units[m]-unit)<=rounding*unit,"exact/accumulator unit correspondence differs")
            for s in range(4):
                offset = 4*m+s
                for raw,scaled in zip(values[offset],normalized[offset]):
                    expected = scaled*accumulator_units[m]
                    magnitude = max(abs(raw),abs(expected))
                    relative = abs(raw-expected)/magnitude if magnitude else Q(0)
                    require(relative<=rounding,"raw/normalized represented scaling exceeds roundoff allowance")
                    normalization_max = max(normalization_max,relative)
                    normalization_components += 1
                if m<210:
                    if s in (1,2):
                        squared = norm(values[offset])
                        verify(dict(kind="separate_IR_exact_zero",grid=grid["id"],moment=m,slot=s,
                            squared_norm=str(squared),required_exact_zero=True,passed=squared==0,affects_empirical_eligibility=True))
                    if s==0 and sum(exponents[m])<2:
                        compare("UV_convergent_zero",grid["id"],m,0,norm(values[offset])/(unit*unit))
                    compare("original_quad_diagnostic_only",grid["id"],m,s,
                            discrepancy(values[offset],reference[offset],unit*unit),gate=False)
        arrays[order,mapping] = values
        grid_summaries.append(dict(id=grid["id"],sha256=seen[prefix+"/result.json"]["sha256"],points=points,batches=batches,
            full_complex_slots=1320,acceptance_prefix_complex_slots=840,minimum_real_F=str(data["minimum_observed_real_F"])))
    require((row_offset,batch_offset)==(7456,30) and (new_row_offset,new_batch_offset)==(4608,18),
            "combined/new aggregate counter reconciliation differs")
    pairs = [((a,mapping),(b,mapping)) for mapping in ("identity","reverse") for a,b in ((20,32),(20,48),(32,48))]
    pairs += [((order,"identity"),(order,"reverse")) for order in (20,32,48)]
    for left,right in pairs:
        peak = None
        for m,alpha in enumerate(exponents[:210]):
            unit = Q(3)**(sum(alpha)-2)
            for s in range(4):
                square = discrepancy(arrays[left][4*m+s],arrays[right][4*m+s],unit*unit)
                record = compare("fixed_rule_convergence_indicator",str((3,*left)),m,s,square,str((3,*right)))
                if peak is None or square>peak[0]:
                    peak = (square,record)
        pair_maxima[str((left,right))] = peak
    require(len(consumed)==len(records)==15150 and categories=={
        "fixed_rule_convergence_indicator":7560,"separate_IR_exact_zero":2520,
        "UV_convergent_zero":30,"original_quad_diagnostic_only":5040},"complete record category coverage differs")
    require({identity(v):v for v in failures}=={identity(v):v for v in saved["failures"]}
            and {identity(v):v for v in diagnostics}=={identity(v):v for v in saved["diagnostic_disagreements"]},
            "failed/diagnostic record lists differ")
    require(len(failures)==0 and len(diagnostics)==0 and saved["summary"]==dict(complete_grids=6,
        reference_complex_slots=5040,convergence_complex_slots=7560,separate_IR_zero_checks=2520,
        UV_convergent_zero_checks=30,records=15150,failures=0,diagnostic_disagreements=0),"exact refinement catalogue summary differs")
    require(saved["status"]=="all_fixed_grid_empirical_gates_passed_independent_saved_audit_pending"
            and saved["empirical_rank6_prefix_eligible_pending_independent_saved_audit"] is True
            and saved["rank7_accuracy_qualified"] is False and saved["original_quad_comparisons_diagnostic_only"] is True
            and saved["rigorous_error_bounds"] is False and saved["performance_evidence"] is False,
            "original failed outcome/scope widened")
    def peak_summary(value):
        square,record = value
        return dict(squared_error=str(square),error=display(square),moment=record["moment"],
            exponents=list(exponents[record["moment"]]),slot=record["slot"],native_slot=SLOTS[record["slot"]],
            grid=record["grid"],other=record.get("other"),passed=square<=LIMIT)
    fine_keys = [((20,"identity"),(32,"identity")),((20,"reverse"),(32,"reverse")),
                 ((20,"identity"),(20,"reverse")),((32,"identity"),(32,"reverse"))]
    fine = {str(key):peak_summary(pair_maxima[str(key)]) for key in fine_keys}
    require(all(v["passed"] for v in fine.values()),"order20/32 diagnostic comparisons do not pass")
    require(all(v[0]<=LIMIT for v in pair_maxima.values()),"all fixed order/map pairs must pass")
    reconstructed = [recomputed[key] for key in sorted(consumed,key=repr)]
    return dict(status="passed_independent_saved_collinear_order48_refinement_numeric_replay",findings=[],
        input_bindings=seen,complete_grids=6,point_rows=7456,worker_batches=30,new_point_rows=4608,new_worker_batches=18,full_native_complex_slots=7920,
        acceptance_rank=6,acceptance_moments=210,acceptance_complex_slots=5040,
        comparison_records=15150,comparison_categories=dict(categories),record_reconstruction_failures=0,
        reconstructed_records_sha256=hashlib.sha256(json.dumps(reconstructed,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        empirical_catalogue_passed=True,empirical_failures=failures,original_quad_diagnostic_disagreements=diagnostics,
        old_failed_catalogue_preserved=True,old_failure_partition=old_audit["failure_partition"],
        old_empirical_failure_count=6,old_quad_diagnostic_disagreement_count=5,
        all_pair_maxima={k:peak_summary(v) for k,v in pair_maxima.items()},
        maxima={k:peak_summary(v) for k,v in maxima.items()},
        order20_32_diagnostics=dict(status="passed_subset_of_separately_admitted_refinement_original_coarse_catalogue_remains_failed",
            compared_complex_slots=3360,pair_maxima=fine,scope="rank6 prefix only; separate refined anchor, old coarse catalogue remains failed"),
        normalization_component_checks=normalization_components,
        maximum_raw_normalized_relative_rounding_difference=str(normalization_max),
        representation_consistency_allowance=str(Q(16,2**64)),grids=grid_summaries,negative_controls_passed=controls(),
        producer_imported=False,numerical_packages_imported=False,new_integrals_or_native_jobs=False,
        fresh_binary_package_or_PID_probe=False,thresholds_changed=False,rank7_accuracy_qualified=False,
        integrated_Float_or_Dual_accuracy=False,rigorous_error_bound=False,performance_evidence=False,
        limitations=["Exact represented-data replay, not a new integral or symbolic algebra calculation.",
            "Six original coarse empirical failures remain failures; the separately fixed20/32/48 rank-six refinement passes all order/map indicators.",
            "All330 rows are validated as saved data; acceptance comparisons stop at the first210 rank6 rows.",
            "Original quad comparisons are diagnostic and cannot supply independent finite-array certification.",
            "Binary64 nodes/worker with longdouble accumulation do not establish arbitrary-precision integral accuracy.",
            "Native identity, process release and resource/package assertions remain saved attestations without reenactment."])


if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    root = Path.cwd()
    result = audit(lambda alias:(root/alias).read_bytes())
    with args.output.open("x") as stream:
        json.dump(result,stream,indent=2,allow_nan=False)
        stream.write("\n")
    print(json.dumps(dict(status=result["status"],records=result["comparison_records"],
        refinement_empirical_failures=len(result["empirical_failures"]),old_coarse_failures=result["old_empirical_failure_count"])))
