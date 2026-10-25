"""Independent saved-byte audit. No producer imports, executables or integrals.

`audit(read_bytes)` accepts project-relative aliases, allowing a capsule to pass
restored bytes directly. The CLI reads those aliases below the current directory.
Fraction arithmetic checks represented numerical values; it is not tensor algebra.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from pathlib import PurePosixPath
import copy
import hashlib
import json
import re

BASE = "target/n6-rank6-generalized-quad/"
PINS = {
    "protocol.json": "277f4652434070e9b2d20cfa6be8f044b564e6ea88df35e32b314d66565c1b26",
    "source-review-002.json": "5027620916961267e45d7d171cd6b8cad213e6a0cf4925725aacefb5e6e78490",
    "root-authorization.json": "9228b5e54b9c5c4a3ecb0c7f9cca20c58967e52f71fb2ca8bddff82e7c7ff941",
    "capture-001/receipt.json": "97c94b550f1eb904d53a3fc075a7719a99417d20a0d947c415e432c4e3cd2d41",
    "comparison.json": "014c0a7394ccdd569a9cb08e42eeff6544497ebfbc01ecf8787714548bc61e10",
    "numerical-release.json": "11c1e22f5a2a3d76dac3153549f617d181190abab83fd3989c8eaefc89565785",
}
LAURENT = ["uv1", "ir1", "ir2", "finite"]
PRECISION = dict(dbl_kind=16, olo_kind=16, storage_bits=128,
                 binary_digits=113, decimal_digits=33)
DECIMAL = re.compile(r"\s*[+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\s*")
LIMIT = Q(1, 10**20)


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def parse(body):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def nonfinite(value):
        raise ValueError("nonfinite JSON token: " + value)
    return json.loads(body, object_pairs_hook=pairs, parse_float=Decimal,
                      parse_constant=nonfinite)


def native(body, ident, count):
    lines = body.decode("utf-8", errors="strict").splitlines()
    require([parse(x[10:]) for x in lines if x.startswith("PRECISION ")] == [PRECISION],
            "native precision witness")
    require(lines.count("READY IREGI_REFERENCE_QP_V1") == 1, "native READY witness")
    results = [parse(x[7:]) for x in lines if x.startswith("RESULT ")]
    require(len(results) == 1 and type(results[0]) is dict, "one complete RESULT")
    result = results[0]
    require(result.get("id") == ident and type(result.get("stable")) is bool,
            "native id/stability schema")
    require(result.get("poles") == LAURENT and result.get("error") is None,
            "native separated Laurent schema")
    moments = result.get("moments")
    require(type(moments) is list and len(moments) == count, "native moment count")
    values = []
    for moment in moments:
        require(type(moment) is list and len(moment) == 4, "native four-slot moment")
        row = []
        for value in moment:
            require(type(value) is list and len(value) == 2 and
                    all(type(x) is str and DECIMAL.fullmatch(x) for x in value),
                    "native finite quoted complex decimal")
            row.append(tuple(Q(x) for x in value))
        values.append(row)
    return result["stable"], values


def norm(z):
    return z[0]**2 + z[1]**2


def display(squared):
    with localcontext() as context:
        context.prec = 100
        return str((Decimal(squared.numerator) / Decimal(squared.denominator)).sqrt())


def controls():
    """Negative parser controls and the exact inclusive squared threshold."""
    result = dict(id="control", stable=True, poles=LAURENT,
                  moments=[[["0", "0"] for _ in range(4)]])
    def wire(value, precision=PRECISION):
        return ("PRECISION " + json.dumps(precision) +
                "\nREADY IREGI_REFERENCE_QP_V1\nRESULT " + json.dumps(value) + "\n").encode()
    valid = wire(result)
    native(valid, "control", 1)
    bad = [lambda: parse('{"x":1,"x":2}'), lambda: parse('{"x":NaN}'),
           lambda: native(valid, "wrong", 1), lambda: native(valid, "control", 2),
           lambda: native(valid + b'RESULT {}\n', "control", 1),
           lambda: native(valid.replace(b'READY IREGI_REFERENCE_QP_V1', b''), "control", 1)]
    for mutation in ["stable", "slots", "nan", "unquoted", "null"]:
        value = copy.deepcopy(result)
        if mutation == "stable": value["stable"] = "true"
        if mutation == "slots": value["moments"][0].pop()
        if mutation == "nan": value["moments"][0][0][0] = "NaN"
        if mutation == "unquoted": value["moments"][0][0][0] = 0
        if mutation == "null": value["moments"] = None
        bad.append(lambda value=value: native(wire(value), "control", 1))
    for action in bad:
        try:
            action()
        except (ValueError, TypeError):
            continue
        raise ValueError("negative parser control was accepted")
    require(Q(1, 10**10)**2 == LIMIT and Q(1, 10**10)**2 <= LIMIT,
            "inclusive threshold boundary")
    require((Q(1, 10**10) + Q(1, 10**30))**2 > LIMIT, "above-threshold rejection")
    return len(bad) + 2


def audit(read_bytes):
    """Recompute all arrays/controls using only a callback of saved-byte aliases."""
    loaded = {}
    def read(alias, expected=None):
        require(not PurePosixPath(alias).is_absolute() and ".." not in PurePosixPath(alias).parts,
                "unsafe saved alias")
        # No executable/tool/source-closure reads can be requested by this audit.
        require(alias.startswith(BASE) or alias in {
            "target/quad-iregi-source-audit/capture-v6-001/request-4.stdout",
            "validation/quad-original-iregi-rank7-adjudication/qualification.json"},
            "alias outside narrow saved-artifact audit")
        body = read_bytes(alias)
        require(type(body) is bytes, "reader must return bytes")
        digest = hashlib.sha256(body).hexdigest()
        require(expected is None or digest == expected, "saved hash mismatch: " + alias)
        loaded[alias] = dict(sha256=digest, bytes=len(body))
        return body
    objects = {name: parse(read(BASE + name, digest)) for name, digest in PINS.items()}
    p, source, grant, capture, comparison, release = (objects[name] for name in PINS)
    suffix = "/" + BASE + "capture-001"
    require(p["directory"].endswith(suffix), "saved project directory suffix")
    prefix = p["directory"][:-len(suffix)] + "/"
    def alias(path):
        require(path.startswith(prefix), "expected saved project path")
        return path[len(prefix):]
    require(source["status"] == "passed_independent_source_runner_comparator_review" and
            source["findings"] == [] and source["protocol_sha256"] == PINS["protocol.json"],
            "exact clear independent source review")
    require(grant["status"] == "granted" and grant["grantor"] == "/root" and
            grant["protocol_sha256"] == PINS["protocol.json"] and
            grant["review_sha256"] == PINS["source-review-002.json"], "exact root grant")
    ids = [c["id"] for c in p["cases"]]
    require(len(ids) == len(set(ids)) == 7 and grant["cases"] == ids, "seven granted cases")
    require(capture["status"] == "terminal_capture" and capture["inputs_unchanged"] is True and
            capture["cleanup_errors"] == [] and capture["cancellation"] is None,
            "terminal source/cleanup admission")
    require((capture["aggregate_seconds"], capture["cleanup_reserve_seconds"], capture["cpu"]) == (600, 60, 26)
            and Q(str(capture["elapsed_seconds"])) < 540 and
            capture["native_cases_executed"] == ids, "capture budget/order")
    require(all(capture[key] is False for key in
                ["automatic_retry", "performance_evidence", "finite_accuracy_qualified", "new_compilation"]),
            "native scope flags")
    require(capture["protocol_sha256"] == PINS["protocol.json"] and
            all(capture["inputs"].get(k) == v for k, v in p["bindings"].items()), "34 historical input bindings")
    for name in ["protocol.json", "source-review-002.json", "root-authorization.json"]:
        require(capture["inputs"].get(prefix + BASE + name) == PINS[name], "review/grant input binding")
    require(release["status"] == "terminal_successful_outer_controller_and_all_owned_groups_absent" and
            release["outer_session_id"] == 65118 and release["outer_exit_code"] == 0 and
            release["CPU26_released"] is True and release["no_UTC_overlap_claim"] is True and
            release["capture_receipt_sha256"] == PINS["capture-001/receipt.json"] and
            release["comparison_sha256"] == PINS["comparison.json"], "executor terminal attestation")
    basis = [(t, x, y, r-t-x-y) for r in range(7) for t in range(r, -1, -1)
             for x in range(r-t, -1, -1) for y in range(r-t-x, -1, -1)]
    require(len(basis) == 210 and basis[126] == (6, 0, 0, 0), "independent cumulative basis")
    expected_outputs = {f"{stem}-{i}.{extension}" for i in range(7)
                        for stem, extension in [("request", "stdout"), ("request", "stderr"), ("step", "log")]}
    require(set(capture["outputs"]) == expected_outputs and len(capture["steps"]) == 7 and
            len(release["groups"]) == 7, "complete output/step/group inventory")
    records, arrays, mappings = [], [], []
    def gate(kind, case, moment, slot, squared):
        records.append(dict(kind=kind, case=case["id"], moment=moment,
                            exponents=list(basis[moment]), slot=slot, squared_error=str(squared),
                            error=display(squared), limit_squared=str(LIMIT), passed=squared <= LIMIT))
    for i, case in enumerate(p["cases"]):
        step, group = capture["steps"][i], release["groups"][i]
        require(case["n"] == 6 and case["rank"] == 6 and case["moments"] == 210 and
                case["complex_slots"] == 840 and case["idim"] == 2*case["h"], "case dimensions")
        require(step["label"] == case["id"] == group["label"] and step["status"] == "exited" and
                step["returncode"] == 0 and step["owned_group_gone"] is True and
                not step.get("timeout") and "error" not in step and
                step["owned_process_group"] == group["owned_process_group"] and
                group["actually_absent"] is True and step["timeout_seconds"] == 60 and
                Q(str(step["elapsed_seconds"])) < 60, "clean bounded native attempt")
        request = alias(case["request"])
        read(request, case["request_sha256"])
        raw = {ext: read(BASE + f"capture-001/request-{i}.{ext}", capture["outputs"][f"request-{i}.{ext}"])
               for ext in ["stdout", "stderr"]}
        log_alias = BASE + f"capture-001/step-{i}.log"
        log = parse(read(log_alias, capture["outputs"][f"step-{i}.log"]))
        require(log == dict(binary_sha256=p["binary_sha256"], input_sha256=case["request_sha256"], returncode=0,
                            stdout_sha256=capture["outputs"][f"request-{i}.stdout"],
                            stderr_sha256=capture["outputs"][f"request-{i}.stderr"]), "native wrapper hash mapping")
        stable, values = native(raw["stdout"], case["id"], 210)
        require(stable is True and raw["stderr"] == b"", "stable finite native array")
        arrays.append(values)
        nonzero = [sum(norm(moment[slot]) != 0 for moment in values) for slot in range(4)]
        require(comparison["cases"][i]["id"] == case["id"] and
                comparison["cases"][i]["powers"] == case["powers"] and
                comparison["cases"][i]["idim"] == case["idim"] and
                comparison["cases"][i]["complete_complex_slots"] == 840 and
                comparison["cases"][i]["represented_nonzero_by_slot"] == nonzero and
                comparison["cases"][i]["eligible_reference"] is True and
                comparison["cases"][i]["native_stable"] is True, "per-case native flags/counts")
        mappings.append(dict(id=case["id"], powers=case["powers"], h=case["h"], idim=case["idim"],
                             request=request, request_sha256=case["request_sha256"],
                             stdout=BASE + f"capture-001/request-{i}.stdout",
                             stdout_sha256=capture["outputs"][f"request-{i}.stdout"],
                             native_stable=True, moments=210, complex_slots=840,
                             represented_nonzero_by_slot=nonzero))
        for j, exponents in enumerate(basis):
            delta = sum(exponents) + 4 + case["idim"] - 2*sum(case["powers"])
            for slot in [1, 2]:
                gate("positive_F_IR_zero", case, j, slot, norm(values[j][slot]) / Q(9)**delta)
            if delta < 0:
                gate("convergent_UV_zero", case, j, 0, norm(values[j][0]) / Q(9)**delta)
    require(len({g["owned_process_group"] for g in release["groups"]}) == 7, "distinct owned groups")
    anchor = p["ordinary_anchor"]
    stable, old = native(read(alias(anchor["path"]), anchor["sha256"]), anchor["response_id"], 330)
    qualification_alias = alias(anchor["qualification"])
    qualification = parse(read(qualification_alias, p["bindings"][anchor["qualification"]]))
    require(stable is True and any(x["id"] == "n6_base_mode0" and x["accepted"] is True
                                  for x in qualification["cases"]), "admitted ordinary anchor")
    exact_matches = 0
    for j, exponents in enumerate(basis):
        for slot in range(4):
            difference = tuple(a-b for a, b in zip(arrays[0][j][slot], old[j][slot]))
            squared = norm(difference) / max(Q(9)**(sum(exponents)-8), norm(old[j][slot]))
            gate("generalized_unit_vs_ordinary_quad_prefix", p["cases"][0], j, slot, squared)
            exact_matches += arrays[0][j][slot] == old[j][slot]
    require(len(records) == 5166 and records == comparison["records"] and
            all(x["passed"] is True for x in records) and comparison["failures"] == [],
            "all independently recomputed records including decimal display")
    counts = {kind: sum(x["kind"] == kind for x in records) for kind in
              ["positive_F_IR_zero", "convergent_UV_zero", "generalized_unit_vs_ordinary_quad_prefix"]}
    require(list(counts.values()) == [2940, 1386, 840] and exact_matches == 840,
            "complete gate counts/exact ordinary prefix")
    require(comparison["summary"] == dict(complete_arrays=7, eligible_arrays=7,
                complete_complex_slots=5880, records=5166, failures=0,
                IR_zero_gates=2940, UV_convergent_zero_gates=1386, unit_prefix_gates=840),
            "independently rebuilt producer summary")
    require(comparison["status"] == "passed_restricted_N6_rank6_generalized_reference_controls" and
            comparison["finite_generalized_coefficients_independently_certified"] is False and
            comparison["Rust_Dual_physical_or_performance_qualification"] is False and
            comparison["native_or_tool_executables_rehashed"] is False and
            comparison["current_process_state_probed"] is False and
            comparison["native_poles_projected_or_merged"] is False,
            "restricted comparison scope")
    d6 = arrays[6][126:]
    require(p["cases"][6]["idim"] == 2 and len(d6) == 84 and
            not any(x["case"] == ids[6] and x["kind"] == "convergent_UV_zero" and
                    x["moment"] >= 126 for x in records), "D6 rank6 UV residues retained")
    return dict(schema_version=1, status="passed_independent_saved_numeric_and_metadata_audit",
                reviewer="/root/dual_pilot_finish/complex_oracle_transport", findings=[],
                artifact_pins={BASE + name: digest for name, digest in PINS.items()},
                complete_arrays=7, complete_complex_slots=5880, exact_records=5166,
                gate_counts=counts, exact_unit_prefix_matches=exact_matches,
                maxima={kind: display(max(Q(x["squared_error"]) for x in records if x["kind"] == kind))
                        for kind in counts},
                records_sha256=hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                d6_degree6_UV_slots_retained=84,
                d6_degree6_UV_represented_nonzero=sum(norm(row[0]) != 0 for row in d6),
                negative_controls=controls(), case_raw_mapping=mappings, checked_saved_aliases=loaded,
                native_and_tool_hashes="historical receipt attestations; executable bytes not read",
                outer_completion_and_fresh_group_absence="executor-attested; no new process probe",
                chronology="ordered saved receipts plus reviewed serial controller; no UTC overlap proof",
                elapsed_scope="25.80733620200772s pre-final-I/O receipt snapshot; outer session65118 exit0 separately attested",
                execution=dict(producer_import=False, native=False, compiler=False, integral=False,
                               symbolic_algebra=False, process_probe=False, git=False),
                finite_generalized_coefficients_independently_certified=False,
                Rust_Dual_physical_or_performance_qualified=False,
                precision_caveat="113-bit/33-decimal storage witness; original approximately16-digit constants and stopping criteria retained")


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(lambda alias: (Path.cwd() / alias).read_bytes())
    report["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if args.output:
        with args.output.open("x") as stream:
            json.dump(report, stream, indent=2, allow_nan=False)
            stream.write("\n")
    print(json.dumps({key: report[key] for key in
                      ["status", "complete_arrays", "complete_complex_slots", "exact_records", "maxima", "negative_controls"]}))
