#!/usr/bin/env python3
"""Portable integrity, source restoration, and saved-decimal replay only.

Uses the Python standard library. Never runs a compiler, native binary, process
probe, algebra system, reference integral, or producer comparator.
"""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, localcontext
import argparse
import hashlib
import io
import json
import re
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = "target/quad-iregi-source-audit"
PARENT = "validation/highpoint-thin-n6-rank7-phase"
HISTORICAL_PROJECT = "/shared/external/iregi/iregi-rust/"
HISTORICAL_WORKSPACE = "/shared/external/iregi/"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def description(body):
    return {"sha256": sha(body), "bytes": len(body)}


def safe(name):
    path = Path(name)
    require(name and not path.is_absolute() and ".." not in path.parts and str(path) == name, "unsafe path")


def load(body):
    return json.loads(body, parse_float=str)


def source_patch(base, body, reverse=False):
    """Strict line/context replay of the two preserved source patches."""
    result = dict(base)
    lines = body.decode().splitlines(keepends=True)
    position = 0
    changed = []
    while position < len(lines):
        require(lines[position].startswith("--- "), "patch old header")
        old = lines[position][4:].strip()
        position += 1
        require(position < len(lines) and lines[position].startswith("+++ "), "patch new header")
        new = lines[position][4:].strip()
        position += 1
        name = Path(new).name
        require(Path(old).name == name and name not in changed and name in result, "patch file identity")
        changed.append(name)
        previous = result[name].decode().splitlines(keepends=True)
        output = []
        cursor = 0
        hunks = 0
        while position < len(lines) and lines[position].startswith("@@ "):
            match = re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*\n", lines[position])
            require(match is not None, "patch hunk header")
            a, ac, b, bc = [int(v) if v is not None else 1 for v in match.groups()]
            if reverse:
                a, ac, b, bc = b, bc, a, ac
            position += 1
            start = max(0, a - 1)
            require(cursor <= start <= len(previous), "patch hunk range")
            output.extend(previous[cursor:start])
            cursor = start
            require(len(output) == max(0, b - 1), "patch new position")
            counts = [0, 0]
            while position < len(lines) and not lines[position].startswith(("@@ ", "--- ")):
                line = lines[position]
                position += 1
                require(line[:1] in [" ", "+", "-"], "patch body record")
                tag, text = line[0], line[1:]
                if reverse:
                    tag = {" ": " ", "+": "-", "-": "+"}[tag]
                if tag in " -":
                    require(cursor < len(previous) and previous[cursor] == text, "patch context")
                    cursor += 1
                    counts[0] += 1
                if tag in " +":
                    output.append(text)
                    counts[1] += 1
            require(counts == [ac, bc], "patch hunk counts")
            hunks += 1
        require(hunks > 0, "empty patch")
        output.extend(previous[cursor:])
        result[name] = "".join(output).encode()
    return result, changed


def read_archive(body, expected):
    files = {}
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as archive:
        for member in archive:
            safe(member.name)
            require(member.isfile() and member.name not in files, "archive member type/duplicate")
            value = archive.extractfile(member).read()
            require(not value.startswith((b"\x7fELF", b"!<arch>")), "compiled archive member")
            require(not re.search(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}", value), "license literal")
            require(Path(member.name).suffix not in [".o", ".mod", ".smod", ".pyc"], "compiled/cache member")
            files[member.name] = value
    require({n: description(b) for n, b in files.items()} == expected, "payload member inventory")
    return files


def restore(manifest):
    for name, expected in manifest["capsule_files"].items():
        safe(name)
        require(description((HERE / name).read_bytes()) == expected, "capsule file " + name)
    observed = {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    require(observed == set(manifest["capsule_files"]) | {"manifest.json"}, "capsule exact inventory")
    members = read_archive((HERE / "payload.tar.gz").read_bytes(), manifest["payload_members"])
    files = {}
    for name, record in manifest["preserved_files"].items():
        safe(name)
        value = members[record["member"]]
        require(description(value) == {k: record[k] for k in ["sha256", "bytes"]}, "preserved alias identity")
        files[name] = value
    for name, expected in manifest["parent_files"].items():
        safe(name)
        value = (ROOT / name).read_bytes()
        require(description(value) == expected, "parent " + name)
        require(name not in files, "parent duplicate")
        files[name] = value
    base = {Path(n).name: b for n, b in files.items() if n.startswith(PRIVATE + "/source-v2/")}
    require(len(base) == 22, "canonical source count")
    v2 = load(files[PRIVATE + "/source-v2.json"])
    require({n: sha(b) for n, b in base.items()} == v2["source_sha256"], "canonical source hashes")
    v1, changed = source_patch(base, files[PRIVATE + "/source-v2.patch"], reverse=True)
    require(changed == ["driver.f90"], "V1 driver-only restoration")
    require(source_patch(v1, files[PRIVATE + "/source-v2.patch"])[0] == base, "V2 patch round trip")
    v1_manifest = load(files[PRIVATE + "/source-v1.json"])
    require({n: sha(b) for n, b in v1.items()} == v1_manifest["source_sha256"], "V1 source hashes")
    for name, value in v1.items():
        files[PRIVATE + "/source-v1/" + name] = value
    original, changed = source_patch(v1, files[PRIVATE + "/source-v1.patch"], reverse=True)
    require(changed == ["global.f90", "avh_olo_foriregi.f90", "driver.f90"], "only original kind/observer changes")
    require(source_patch(original, files[PRIVATE + "/source-v1.patch"])[0] == v1, "V1 patch round trip")
    for name, origin in v2["origins"].items():
        require(sha(original[name]) == origin["sha256"], "reconstructed original " + name)
    for name, record in manifest["restored_original_files"].items():
        value = original[record["source_name"]]
        require(description(value) == {k: record[k] for k in ["sha256", "bytes"]}, "original reconstruction identity")
        require(name not in files or files[name] == value, "original collision")
        files[name] = value
    origin_records = load((HERE / "payload-origins.json").read_bytes())
    require(set(origin_records) == set(manifest["preserved_files"]) | set(manifest["reconstructed_v1_files"]) | set(manifest["restored_original_files"]), "origin exact inventory")
    for name, row in origin_records.items():
        require(description(files[name]) == {k: row[k] for k in ["sha256", "bytes"]}, "origin copy/reconstruction identity")
    inventory = load(files[PRIVATE + "/independent/inventory-final.json"])
    for origin, expected in inventory["sources"].items():
        require(description(files["reference-context/" + origin]) == expected, "61-file source audit context")
    license_key = "reference-context/references/madgraph/vendor/IREGI/src/oneloop/COPYING"
    require(manifest["upstream_license_texts_included"] == [license_key]
            and manifest["symbolica_license_literal_included"] is False
            and sha(files[license_key]) == "8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903", "upstream COPYING retained; literal Symbolica license excluded")
    parent_archive = load(files[PARENT + "/archive-manifest.json"])
    require(sha(files[PARENT + "/sources.tar.gz"]) == parent_archive["archive_sha256"], "parent source archive hash")
    with tarfile.open(fileobj=io.BytesIO(files[PARENT + "/sources.tar.gz"]), mode="r:gz") as archive:
        restored = {}
        for member in archive:
            safe(member.name)
            require(member.isfile() and member.name not in restored, "parent source type/duplicate")
            restored[member.name] = sha(archive.extractfile(member).read())
    require(restored == parent_archive["members"], "parent exact source archive inventory")
    return files


def slots(response, count, label):
    require(type(response.get("stable")) is bool and response.get("poles") == ["uv1", "ir1", "ir2", "finite"], label + " status/poles")
    values = response.get("moments")
    require(isinstance(values, list) and len(values) == count, label + " complete moments")
    result = []
    for moment in values:
        require(isinstance(moment, list) and len(moment) == 4, label + " complete poles")
        row = []
        for value in moment:
            require(isinstance(value, list) and len(value) == 2, label + " complex shape")
            require(all(isinstance(v, str) and Decimal(v).is_finite() for v in value), label + " finite quoted decimals")
            row.append(tuple(Fraction(v) for v in value))
        result.append(row)
    return result


def checked(left, right, unit):
    require(len(left) == len(right) == 2 and unit > 0, "complex normalization")
    squared = sum((a - b) ** 2 for a, b in zip(left, right)) / max(unit ** 2, sum(a ** 2 for a in right))
    with localcontext() as context:
        context.prec = 180
        display = str((Decimal(squared.numerator) / Decimal(squared.denominator)).sqrt())
    return {"error": display, "passed": squared <= Fraction(1, 10 ** 20)}


def scale2(sample, count):
    props = sample["propagators"][:count]
    result = max(Fraction(1), *(abs(Fraction(str(p["mass_squared"][0]))) for p in props))
    for index, a in enumerate(props):
        for b in props[:index]:
            delta = [Fraction(str(x)) - Fraction(str(y)) for x, y in zip(a["shift"], b["shift"])]
            result = max(result, abs(delta[0] ** 2 - sum(x ** 2 for x in delta[1:])))
    return result


def numeric_replay(files):
    recipe = load(files[PRIVATE + "/recipe-v6.json"])
    saved = load(files[PRIVATE + "/capture-v6-001/comparison.json"])
    basis = [[t, x, y, rank - t - x - y] for rank in range(8) for t in range(rank, -1, -1)
             for x in range(rank - t, -1, -1) for y in range(rank - t - x, -1, -1)]
    require(len(basis) == 330, "330 native moments")
    candidates = [load(files[PARENT + "/phase/" + name + "/result.json"])
                  for name in ["n6-rank7-128-001", "n6-rank7-256-diagnostic-001"]]
    expected_settings = {"propagators": 6, "rank": 7, "powers": [1] * 6, "dimension_shift": 0,
                         "algorithm": "PassarinoVeltman", "convention": "IregiNative", "tensor_weights": "Components",
                         "invariants": "FromShifts", "input_policy": "Preserve"}
    fixture = load(files[PARENT + "/reference/fixture-conditioned_masses.json"])["samples"][0]
    require(scale2(fixture, 6) == 4, "fixture natural scale Q=2")
    exact_inputs = [[str(Fraction(v)), "0"] for p in fixture["propagators"][:6] for v in p["shift"]]
    exact_inputs += [[str(Fraction(v)) for v in p["mass_squared"]] for p in fixture["propagators"][:6]]
    exact_inputs += [[str(Fraction(fixture["mu"])), "0"]]
    candidate_values = []
    for bits, candidate in zip([128, 256], candidates):
        require(candidate["basis"] == basis and candidate["settings"] == expected_settings, "candidate basis/settings")
        require(candidate["rows"] == candidate["components"] == 1 and candidate["requested_bits"] == 53
                and candidate["working_bits"] == bits and candidate["status"] == "all_lanes_success", "candidate precision/scope")
        require(candidate["input_exact_rational"] == [exact_inputs], "same exact candidate input")
        moments = candidate["lanes"][0]["moments"]
        require(len(moments) == 330 and all(len(m) == 4 for m in moments), "candidate all 1320 slots")
        values = []
        for moment in moments:
            values.append([tuple(Fraction(value[key]) for key in ["real", "imaginary"]) for value in moment])
        candidate_values.append(values)
    original = load(files[PARENT + "/reference/reference-conditioned_masses.json"])
    controls = {c["input"]["id"]: c for c in load(files["validation/reference/fixtures.json"])["cases"]}
    records = []
    cases = []
    old_real_bad = []
    old_imag_bad = []
    convergence = Fraction(0)
    for ordinal, case in enumerate(recipe["runtime"]["cases"]):
        raw = files[PRIVATE + f"/capture-v6-001/request-{ordinal}.stdout"].decode()
        precision = [load(line[10:]) for line in raw.splitlines() if line.startswith("PRECISION ")]
        require(precision == [{"dbl_kind": 16, "olo_kind": 16, "storage_bits": 128, "binary_digits": 113, "decimal_digits": 33}], "captured precision witness")
        require(raw.splitlines().count("READY IREGI_REFERENCE_QP_V1") == 1, "captured READY witness")
        responses = [load(line[7:]) for line in raw.splitlines() if line.startswith("RESULT ")]
        require(len(responses) == 1 and responses[0]["id"] == case["id"], "one correctly identified RESULT")
        response = responses[0]
        values = slots(response, case["moments"], case["id"])
        row = {"id": case["id"], "stable": response["stable"], "compared_complex_slots": case["moments"] * 4}
        passed = True
        maximum = Decimal(0)
        if case["class"] == "retained_reference_normalization_control":
            old = controls[case["original_control_id"]]
            q2 = max(Fraction(1), *(abs(Fraction(str(p["mass_squared"][0]))) for p in old["input"]["propagators"]))
            shifts = [[Fraction(str(v)) for v in p["shift"]] for p in old["input"]["propagators"]]
            for a in shifts:
                for b in shifts:
                    d = [x - y for x, y in zip(a, b)]
                    q2 = max(q2, abs(d[0] ** 2 - sum(x ** 2 for x in d[1:])))
            unit = q2 ** (2 - len(shifts))
            for pole in range(4):
                result = checked(values[0][pole], tuple(Fraction(v) for v in old["expected"]["moments"][0][pole]), unit)
                records.append({"id": case["id"], "moment": 0, "slot": pole, "reference": "retained_original_binary64_control", **result})
                passed &= result["passed"]
                maximum = max(maximum, Decimal(result["error"]))
        else:
            matches = [c for c in original["cases"] if c["id"] == case["id"]]
            require(len(matches) == 1 and matches[0]["status"] == "captured", "old complete mode")
            old_response = matches[0]["response"]
            request_path = case["input"].removeprefix(HISTORICAL_PROJECT)
            require(files[request_path].decode() == matches[0]["request"], "identical ordered binary64/quad numerical request")
            old_values = slots(old_response, 330, "old binary64")
            row["retained_original_stable"] = old_response["stable"]
            failures = {label: 0 for label in ["TIRust128", "TIRust256", "original_binary64", "zero_poles", "real_zero"]}
            for moment, monomial in enumerate(basis):
                unit = Fraction(2) ** (sum(monomial) - 8)
                for pole in range(4):
                    meta = {"id": case["id"], "moment": moment, "basis": monomial, "slot": pole}
                    for label, value in [("TIRust128", candidate_values[0][moment][pole]),
                                         ("TIRust256", candidate_values[1][moment][pole]),
                                         ("original_binary64", old_values[moment][pole])]:
                        result = checked(value, values[moment][pole], unit)
                        records.append({**meta, "candidate": label, "reference": "promoted_original_quad", **result})
                        failures[label] += not result["passed"]
                        if label != "original_binary64":
                            passed &= result["passed"]
                            maximum = max(maximum, Decimal(result["error"]))
                    if pole < 3:
                        result = checked(values[moment][pole], (Fraction(0), Fraction(0)), unit)
                        records.append({**meta, "reference": "independent_zero_poles", **result})
                        failures["zero_poles"] += not result["passed"]
                        passed &= result["passed"]
                    result = checked((values[moment][pole][0], Fraction(0)), (Fraction(0), Fraction(0)), unit)
                    records.append({**meta, "reference": "independent_real_zero", **result})
                    failures["real_zero"] += not result["passed"]
                    passed &= result["passed"]
                    if ordinal == 4:
                        difference = sum((a - b) ** 2 for a, b in zip(candidate_values[0][moment][pole], candidate_values[1][moment][pole]))
                        squared = difference / max(unit ** 2, sum(v ** 2 for v in candidate_values[1][moment][pole]))
                        convergence = max(convergence, squared)
                        if not checked((old_values[moment][pole][0], Fraction(0)), (Fraction(0), Fraction(0)), unit)["passed"]:
                            old_real_bad.append([moment, pole])
                        if not checked((Fraction(0), old_values[moment][pole][1]), (Fraction(0), values[moment][pole][1]), unit)["passed"]:
                            old_imag_bad.append([moment, pole])
            row["comparison_failures"] = failures
        row["accepted"] = response["stable"] and passed
        row["maximum_tirust_or_control_error"] = str(maximum)
        cases.append(row)
    require(len(records) == saved["record_count"] == 18826 and records == saved["records"], "all exact saved comparison records")
    require(len(cases) == len(saved["cases"]) == 7, "all seven captured cases")
    for computed, expected in zip(cases, saved["cases"]):
        require(all(expected[k] == v for k, v in computed.items()), "case status/failures/maxima")
    require([c["accepted"] for c in cases] == [True] * 5 + [False] * 2, "IBP accepted while PV/hybrid failures remain visible")
    require(cases[4]["comparison_failures"] == {"TIRust128": 0, "TIRust256": 0, "original_binary64": 90, "zero_poles": 0, "real_zero": 0}, "old DP failure preserved")
    require(cases[5]["stable"] is False and cases[5]["comparison_failures"]["TIRust128"] == 139
            and cases[6]["stable"] is True and cases[6]["comparison_failures"]["TIRust128"] == 19, "quad nonaccepted paths")
    independent = load(files[PRIVATE + "/independent/resume-auditor-v6-full-array-numeric-review.json"])
    require(independent["status"] == "passed_independent_retained_N6_rank7_stable_quad_IBP_full_array_review"
            and independent["findings"] == [] and independent["all_saved_gate_decisions_recomputed"] == 18826, "final independent audit admission")
    require(independent["old_binary64_failure_detail"] == {"real_zero_violations": old_real_bad, "imaginary_quad_disagreements": old_imag_bad}
            and len(old_real_bad) == 88 and len(old_imag_bad) == 19, "additive component witnesses preserve overlap")
    with localcontext() as context:
        context.prec = 180
        convergence_display = str((Decimal(convergence.numerator) / Decimal(convergence.denominator)).sqrt())
    require(convergence <= Fraction(1, 2 ** 160) and independent["maximum_candidate_convergence_error"] == convergence_display, "all 1320 saved precision pairs")
    return {"cases": cases, "records": len(records), "candidate_complex_slots_each": 1320,
            "same_exact_input_operands": len(exact_inputs) * 2,
            "candidate_precision_pairs": 1320, "observed_candidate_convergence_error": convergence_display,
            "original_real_zero_violations": len(old_real_bad), "original_imaginary_quad_disagreements": len(old_imag_bad),
            "old_binary64_gate": "failed_unchanged", "tolerance": "1e-10; exact squared Fraction gate <=1e-20"}


def receipt_replay(files, manifest):
    def read(name):
        return load(files[PRIVATE + "/" + name])
    protocol = read("recipe-v6.json")
    grant = read("root-execution-grant-v6.json")
    review = read("independent/resume-auditor-v6-resource-source-runner-comparator-review.json")
    require(grant["status"] == "granted" and grant["grantor"] == "/root" and grant["stages"] == ["cmatrix", "build", "runtime"], "root final grant")
    require(grant["recipe_sha256"] == sha(files[PRIVATE + "/recipe-v6.json"])
            and grant["review_sha256"] == sha(files[PRIVATE + "/independent/resume-auditor-v6-resource-source-runner-comparator-review.json"]), "grant bindings")
    require(review["status"] == "passed_independent_source_runner_comparator_review" and review["findings"] == []
            and review["recipe_sha256"] == grant["recipe_sha256"], "final source review")
    groups = []
    durations = {}
    admission = dict(protocol["bindings"])
    for name in ["recipe-v6.json", "root-execution-grant-v6.json", "independent/resume-auditor-v6-resource-source-runner-comparator-review.json"]:
        admission[HISTORICAL_PROJECT + PRIVATE + "/" + name] = sha(files[PRIVATE + "/" + name])
    for stage, sub, cap, reserve, count in [("cmatrix", "cmatrix-v6-001", 720, 90, 3), ("build", "build-v6-001", 180, 25, 17), ("runtime", "capture-v6-001", 150, 20, 7)]:
        name = sub + ("/run.json" if stage == "runtime" else "/build.json")
        value = read(name)
        require(value["status"] == "passed" and value["inputs_unchanged"] is True and value["changed_inputs"] == {}
                and value["cleanup_errors"] == [] and value["cancellation"] is None, "terminal stage status")
        require(value["bound_seconds"] == cap and value["cleanup_reserve_seconds"] == reserve
                and Fraction(0) <= Fraction(value["elapsed_seconds"]) <= cap and len(value["steps"]) == count, "finite stage budget/count")
        require(value["recipe_sha256"] == grant["recipe_sha256"] and value["performance_measurement"] is False
                and value["private_scope_only"] is True, "terminal source/scope")
        expected_inputs = dict(admission)
        if stage != "cmatrix":
            previous = "cmatrix-v6-001" if stage == "build" else "build-v6-001"
            old_name = previous + "/build.json"
            old = read(old_name)
            expected_inputs[HISTORICAL_PROJECT + PRIVATE + "/" + old_name] = sha(files[PRIVATE + "/" + old_name])
            expected_inputs.update({HISTORICAL_PROJECT + PRIVATE + "/" + previous + "/" + name: digest for name, digest in old["outputs"].items()})
        require(value["inputs"] == expected_inputs and len(expected_inputs) == {"cmatrix": 132, "build": 168, "runtime": 222}[stage], "complete exact saved admission union")
        for ordinal, step in enumerate(value["steps"]):
            require(step["status"] == "exited" and step["returncode"] == 0 and step["owned_group_gone"] is True, "terminal owned group")
            require(step["owned_process_group"] not in groups, "unique historical process group")
            groups.append(step["owned_process_group"])
            if stage != "runtime":
                expected = protocol[stage]["commands"][ordinal]
                require(step["label"] == expected["label"] and step["command"] == expected["command"]
                        and step["timeout_seconds"] == expected["cap_seconds"], "exact saved compiler/canary command")
            else:
                case = protocol["runtime"]["cases"][ordinal]
                expected = [protocol["tools"]["taskset"], "-c", str(protocol["runtime"]["cpu"]), protocol["tools"]["python"],
                            HISTORICAL_PROJECT + PRIVATE + "/capture_worker.py", "--binary", HISTORICAL_PROJECT + PRIVATE + "/" + sub + "/iregi-reference-quad",
                            "--input", case["input"], "--stdout", HISTORICAL_PROJECT + PRIVATE + "/" + sub + f"/request-{ordinal}.stdout",
                            "--stderr", HISTORICAL_PROJECT + PRIVATE + "/" + sub + f"/request-{ordinal}.stderr"]
                require(step["label"] == case["id"] and step["command"] == expected and step["timeout_seconds"] == case["cap_seconds"], "exact runtime command")
                transport = read(sub + f"/step-{ordinal}.log")
                request = case["input"].removeprefix(HISTORICAL_PROJECT)
                require(transport == {"binary_sha256": value["runtime_binary_sha256"], "input_sha256": sha(files[request]), "returncode": 0,
                                      "stdout_sha256": value["outputs"][f"request-{ordinal}.stdout"], "stderr_sha256": value["outputs"][f"request-{ordinal}.stderr"]}, "worker binary/input/output chain")
        for output, expected in value["outputs"].items():
            name = PRIVATE + "/" + sub + "/" + output
            if name in files:
                require(sha(files[name]) == expected, "saved output guard " + name)
            else:
                require(manifest["omitted_compiled_products"][name]["captured_sha256"] == expected, "omitted compiled output provenance")
        durations[stage] = value["elapsed_seconds"]
    canary = '{"double_kind":16,"selected_kind":16,"storage_bits":128,"binary_digits":113,"decimal_digits":33}'
    for sub, ordinal in [("build-v4-001", 1), ("build-v5-001", 1), ("cmatrix-v6-001", 1), ("build-v6-001", 1)]:
        text = files[PRIVATE + f"/{sub}/step-{ordinal}.log"].decode()
        require(text.splitlines().count("CANARY_QUAD_PASS") == 1 and json.loads(text.splitlines()[-1]) == json.loads(canary), "actual saved standalone precision canary")
    for sub in ["build-v4-001", "build-v5-001"]:
        value = read(sub + "/build.json")
        require(value["status"] == "failed" and value["executed_native_integral_requests"] == 0 and value["inputs_unchanged"] is True, "failed historical attempt preserved")
        require(value["steps"][-1]["label"] == "compile-cmatrix_base" and value["steps"][-1]["timeout"] is True
                and value["steps"][-1]["timeout_seconds"] == 60 and value["steps"][-1]["owned_group_gone"] is True, "historical 60s timeout")
        require(all(step["owned_group_gone"] is True for step in value["steps"]), "all failed-attempt saved cleanup flags")
        for output, expected in value["outputs"].items():
            name = PRIVATE + "/" + sub + "/" + output
            if name in files:
                require(sha(files[name]) == expected, "failed-attempt saved raw output")
            else:
                require(manifest["omitted_compiled_products"][name]["captured_sha256"] == expected, "failed-attempt omitted/partial product provenance")
    release = read("capture-v6-001/numerical-release.json")
    require(release["all27owned_groups_absent"] is True and release["integral_requests_executed"] == 7
            and len(release["owned_group_checks"]) == 27 and [r["group"] for r in release["owned_group_checks"]] == groups
            and all(r["absent"] is True for r in release["owned_group_checks"]), "saved cohort release")
    build = read("build-v6-001/build.json")
    capture = read("capture-v6-001/run.json")
    require(build["outputs"]["iregi-reference-quad"] == capture["runtime_binary_sha256"]
            == capture["outputs"]["iregi-reference-quad"], "saved original/frozen/runtime binary chain")
    resources = []
    for name, body in files.items():
        if name.startswith(PRIVATE + "/") and "/resource-" in name and name.endswith(".json"):
            value = load(body)
            require(value["status"] == "passed" and value["returncode"] == 0
                    and int(value["hard_per_process_address_space_bytes"]) == 8 * 1024 ** 3
                    and int(value["sampled_group_rss_cap_bytes"]) == 8 * 1024 ** 3
                    and int(value["peak_sampled_group_rss_bytes"]) <= 8 * 1024 ** 3, "saved resource limit/progress")
            resources.append(name)
    require(len(resources) == 16, "all compiler/link resource receipts")
    # Hash only preserved/reconstructed source and data. Native/toolchain paths
    # below remain historical hash attestations, never fresh local guards.
    by_origin = {}
    for name, row in load((HERE / "payload-origins.json").read_bytes()).items():
        by_origin.setdefault(row["origin"], set()).add(sha(files[name]))
    for name, body in files.items():
        if name.startswith("validation/"):
            by_origin.setdefault(HISTORICAL_PROJECT + name, set()).add(sha(body))
    checked_count = historical_count = 0
    for name in ["recipe-v1.json", "recipe-v2.json", "recipe-v3.json", "recipe-v4.json", "recipe-v5.json", "recipe-v6.json",
                 "build-v4-001/build.json", "build-v5-001/build.json", "cmatrix-v6-001/build.json", "build-v6-001/build.json", "capture-v6-001/run.json"]:
        value = read(name)
        for path, expected in value.get("bindings", value.get("inputs", {})).items():
            if path in by_origin:
                require(expected in by_origin[path], "preserved source/data input guard " + path)
                checked_count += 1
            else:
                historical_count += 1
    return {"saved_owned_group_attestations_checked": len(groups), "fresh_process_probes": False,
            "saved_resource_records": len(resources), "preserved_source_data_binding_occurrences_checked": checked_count,
            "omitted_native_or_external_binding_occurrences_historical_only": historical_count,
            "compiled_products_rehashed": False, "stage_elapsed_seconds_diagnostic_only": durations,
            "failed_60_second_build_attempts_preserved": 2, "historical_unrun_request_cohorts_preserved": 2}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct", type=Path)
    args = parser.parse_args()
    manifest = load((HERE / "manifest.json").read_bytes())
    files = restore(manifest)
    receipts = receipt_replay(files, manifest)
    numeric = numeric_replay(files)
    qualification = load((HERE / "qualification.json").read_bytes())
    require((HERE / "qualification.json").read_bytes() == files[PRIVATE + "/qualification-after-independent.json"], "exact final qualification copy")
    require(qualification["independent_saved_numeric_review_sha256"] == sha(files[PRIVATE + "/independent/resume-auditor-v6-full-array-numeric-review.json"])
            and qualification["independent_saved_build_review_sha256"] == sha(files[PRIVATE + "/independent/resume-auditor-v6-build-saved-review.json"]), "qualification independent audit bindings")
    for label, name in [("numeric", "audit_quad_v6_numeric_saved.py"), ("build", "audit_quad_v6_build_saved.py")]:
        review_name = "resume-auditor-v6-full-array-numeric-review.json" if label == "numeric" else "resume-auditor-v6-build-saved-review.json"
        review = load(files[PRIVATE + "/independent/" + review_name])
        require(review["checker_sha256"] == sha(files["target/resume-20261025-review/" + name]), "frozen independent checker identity")
    require(all(qualification.get(name) is False for name in ["complete_rank7_domain_qualified", "public_rank7_qualified", "current_main_or_cargo_qualified", "performance_qualified", "derivative_qualification"]), "no scope promotion")
    if args.reconstruct is not None:
        require(not args.reconstruct.exists(), "reconstruction destination exists")
        args.reconstruct.mkdir(parents=True)
        for name, value in sorted(files.items()):
            safe(name)
            path = args.reconstruct / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
    print(json.dumps({"status": "passed_portable_integrity_source_and_saved_value_replay", "capsule_manifest_sha256": sha((HERE / "manifest.json").read_bytes()),
                      "preserved_or_borrowed_files_restored": len(files), "canonical_source_files": 22, "restored_v1_source_files": 22,
                      "original_source_audit_context_files": 61, "receipts": receipts, "numeric": numeric,
                      "new_native_or_integral_execution": False, "full_rank7_or_current_cargo_or_performance_qualified": False}, indent=2))


if __name__ == "__main__":
    main()
