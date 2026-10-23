#!/usr/bin/env python3
"""Audit completed current-closure evidence without evaluating any integrals.

Run only after run_current.py has finished. Exact Fraction arithmetic below
checks serialized numerical certificates; it is not a polynomial/jet engine.
Missing completion records exit 2 without writing an audit report. Once those
records exist, missing referenced artifacts are audit failures, with exit 1.
Harmless serialized changes are recorded explicitly
and do not silently become either numerical failures or accuracy certificates.
"""

from __future__ import annotations

import datetime
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNS = HERE / "thin-lto"
OLD = ROOT / "validation/near-vacuum-adapter-v3"
CLOSURE = ROOT / "target/benchmark/dependency-closures/6b24c03-complete-kinds"
SCRATCH = ROOT / "target/near-vacuum-adapter-current-thin-lto"
KINDS = {"f64": (53, 40), "dd": (106, 80), "float128": (128, 100), "float256": (256, 128)}
CASES = [*KINDS, "contract", "contour"]
SHAPE = [[0, 0], [1, 0], [0, 1], [1, 1], [2, 0], [0, 2]]
NATIVE = [
    "build/blake3-be485904775d6e47/out",
    "build/gmp-mpfr-sys-575ed8ab5d02dcec/out/lib",
    "build/gmp-mpfr-sys-e9fd89ef30e561a9/out/lib",
    "build/psm-3e52beb8ea08afba/out",
    "build/psm-a698b6f3f5aee778/out",
]


class Audit:
    def __init__(self):
        self.checks = 0
        self.failures = []
        self.hashes = {}
        self.differences = {}
        self.observations = {}

    def check(self, condition, label):
        self.checks += 1
        if not condition:
            self.failures.append(label)

    def sha(self, path):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        key = str(path.relative_to(ROOT))
        if key not in self.hashes:
            with path.open("rb") as stream:
                self.hashes[key] = hashlib.file_digest(stream, "sha256").hexdigest()
        return self.hashes[key]

    def hash_check(self, path, expected, label=None):
        self.check(self.sha(path) == expected, label or f"SHA256: {path}")

    def read(self, path):
        self.sha(path)
        return json.loads(Path(path).read_text())

    def compare(self, name, actual, expected, excluded=()):
        actual = {k: v for k, v in actual.items() if k not in excluded}
        expected = {k: v for k, v in expected.items() if k not in excluded}
        differences = []

        def visit(a, b, path):
            if type(a) is not type(b):
                differences.append({"path": path, "current": a, "durable_v3": b})
            elif isinstance(a, dict):
                for key in sorted(a.keys() | b.keys()):
                    if key not in a or key not in b:
                        differences.append({"path": path + "/" + key, "current_present": key in a, "durable_v3_present": key in b})
                    else:
                        visit(a[key], b[key], path + "/" + key)
            elif isinstance(a, list):
                if len(a) != len(b):
                    differences.append({"path": path, "current_length": len(a), "durable_v3_length": len(b)})
                for i, (av, bv) in enumerate(zip(a, b)):
                    visit(av, bv, f"{path}/{i}")
            elif a != b:
                differences.append({"path": path, "current": a, "durable_v3": b})

        visit(actual, expected, "")
        self.differences[name] = differences


def flags(command, option):
    return [command[i + 1] for i, value in enumerate(command[:-1]) if value == option]


def provenance(a):
    build = a.read(RUNS / "build.json")
    manifest = a.read(CLOSURE / "manifest.json")
    completion = a.read(CLOSURE / "workspace-completion.json")
    workspace = a.read(CLOSURE / "completed-workspace-build.json")
    events = a.read(CLOSURE / "cargo-library-events.json")
    durable = a.read(OLD / "qualification.json")
    a.check(build["status"] == "private_v3_current_closure_build_passed", "build status")
    a.check(build["production_changed"] is False, "private build scope")
    a.check(Path(build["dependency_closure"]) == CLOSURE.relative_to(ROOT), "exact complete-kinds closure")
    a.check(completion["cargo_returncode"] == 0 and completion["master_backend"] == "SymbolicaBatch", "completed default workspace backend")
    a.check(workspace["status"] == "complete" and workspace["provenance_qualified"], "workspace completion")
    a.check(build["rustc"] == workspace["rustc"].splitlines()[0], "same rustc version as completed workspace")
    a.check(len({manifest["source_revision"], completion["source_revision"], workspace["source_revision"]}) == 1, "closure source revision")
    a.hash_check(CLOSURE / "manifest.json", completion["dependency_closure_manifest_sha256"])
    a.hash_check(CLOSURE / "completed-workspace-build.json", completion["workspace_manifest_sha256"])
    snapshots = [a.read(RUNS / name) for name in ["closure-before.json", "closure-after-build.json", "closure-before-runs.json", "closure-after-runs.json"]]
    before = snapshots[0]
    for i, snapshot in enumerate(snapshots[1:], 1):
        a.check(snapshot == before, f"closure snapshot {i} unchanged")
    a.check(build["closure_files_verified"] == len(before), "closure inventory count")
    a.hash_check(RUNS / "closure-before.json", build["closure_before_sha256"])
    a.hash_check(RUNS / "closure-after-build.json", build["closure_after_build_sha256"])
    for row in manifest["files"] + manifest["native_files"]:
        retained = Path(row["retained"])
        a.check(retained.is_relative_to(CLOSURE), f"retained path: {retained.name}")
        key = str(retained.relative_to(ROOT))
        for i, snapshot in enumerate(snapshots):
            a.check(snapshot.get(key) == row["sha256"], f"manifest-bound file in snapshot {i}: {key}")
    for name in ["oneloop", "symbolica", "serde_json"]:
        selected = [e for e in events if e["target"]["name"] == name and e["profile"]["opt_level"] == "3" and e["profile"]["test"] is False]
        a.check(len(selected) == 1, f"unique opt3 non-test {name}")
        event = selected[0]
        record = build["selected"][name]
        a.check(record["event"] == event, f"selected {name} event")
        archives = [p for p in event["filenames"] if p.endswith(".rlib")]
        a.check(len(archives) == 1, f"one {name} archive")
        expected = CLOSURE / "deps" / Path(archives[0]).name
        a.check(ROOT / record["retained_archive"] == expected, f"retained {name} archive path")
        a.check(record["sha256"] == before[str(expected.relative_to(ROOT))], f"recorded {name} closure hash")
        a.hash_check(expected, record["sha256"])
    a.check(build["native_search_directories"] == [str((CLOSURE / p).relative_to(ROOT)) for p in NATIVE], "retained native directories")
    library = SCRATCH / "libiregi_masters_certified_v3.rlib"
    expected_builds = {
        "iregi_masters_certified_v3": ("source/lib.rs", library.name, None),
        "near_vacuum_adapter_validate_v3": ("adapter_validate.rs", "near_vacuum_adapter_validate_v3", "iregi_masters_certified_v3"),
        "near_vacuum_contract_current": ("contract_validate.rs", "near_vacuum_contract_current", "iregi_masters_certified_v3"),
        "five_pinch_compare_current": ("five_pinch_compare.rs", "five_pinch_compare_current", "iregi_masters_certified"),
    }
    a.check([row["crate_name"] for row in build["builds"]] == list(expected_builds), "four distinct ordered build outputs")
    expected_source_members = [name for name in durable["source_archive"]["members"] if name.startswith("source/")]
    expected_source_members += ["adapter_validate.rs", "contract_validate.rs", "five_pinch_compare.rs"]
    a.check(set(build["source_sha256"]) == {str((SCRATCH / name).relative_to(ROOT)) for name in expected_source_members}, "complete exact source inventory")
    a.check(set(build["output_sha256"]) == {str((SCRATCH / value[1]).relative_to(ROOT)) for value in expected_builds.values()}, "complete exact output inventory")
    for row in build["builds"]:
        command = row["command"]
        source, output, alias = expected_builds[row["crate_name"]]
        expected_command = ["taskset", "-c", "18", "rustc", "--edition=2024", "-C", "opt-level=3", "-C", "lto=thin", "-C", "embed-bitcode=yes", "-C", "codegen-units=1", "-L", f"dependency={CLOSURE}/deps"]
        for native in NATIVE:
            expected_command += ["-L", f"native={CLOSURE / native}"]
        if alias is None:
            expected_command += ["--crate-type", "lib"]
        expected_command += ["--crate-name", row["crate_name"], str(SCRATCH / source)]
        for name in ["oneloop", "symbolica"]:
            expected_command += ["--extern", f"{name}={ROOT / build['selected'][name]['retained_archive']}"]
        if alias is not None:
            expected_command += ["--extern", f"{alias}={library}", "--extern", f"serde_json={ROOT / build['selected']['serde_json']['retained_archive']}"]
        expected_command += ["-o", str(SCRATCH / output)]
        a.check(command == expected_command, f"exact source-to-output compile command: {row['crate_name']}")
        a.check(row["cwd"] == str(ROOT) and row["environment"] == {"CARGO_CRATE_NAME": row["crate_name"]}, f"compile cwd/environment: {row['crate_name']}")
        a.check(row["exit_code"] == 0, f"build exit: {row['crate_name']}")
        a.check(command[:4] == ["taskset", "-c", "18", "rustc"], f"build CPU/tool: {row['crate_name']}")
        a.check(set(flags(command, "-C")) == {"opt-level=3", "lto=thin", "embed-bitcode=yes", "codegen-units=1"}, f"ThinLTO release flags: {row['crate_name']}")
        a.check(set(flags(command, "-L")) == {f"dependency={CLOSURE}/deps", *[f"native={CLOSURE / p}" for p in NATIVE]}, f"retained-only search paths: {row['crate_name']}")
        external = dict(x.split("=", 1) for x in flags(command, "--extern"))
        for name in ["oneloop", "symbolica"]:
            a.check(external.get(name) == str(ROOT / build["selected"][name]["retained_archive"]), f"explicit {name}: {row['crate_name']}")
        if row["crate_name"] != "iregi_masters_certified_v3":
            alias = "iregi_masters_certified" if row["crate_name"] == "five_pinch_compare_current" else "iregi_masters_certified_v3"
            a.check(external.get(alias) == str(library), f"explicit private adapter: {row['crate_name']}")
            a.check(external.get("serde_json") == str(ROOT / build["selected"]["serde_json"]["retained_archive"]), f"explicit serde_json: {row['crate_name']}")
        a.sha(RUNS / f"{row['crate_name']}-build.log")
    a.hash_check(ROOT / durable["source_archive"]["path"], durable["source_archive"]["sha256"])
    for path, digest in build["source_sha256"].items():
        relative = Path(path).relative_to(SCRATCH.relative_to(ROOT)).as_posix()
        member = "contour/five_pinch_compare.rs" if relative == "five_pinch_compare.rs" else relative
        a.check(durable["source_archive"]["members"].get(member) == digest, f"source unchanged from durable v3: {relative}")
        a.hash_check(path, digest)
    for path, digest in build["output_sha256"].items():
        a.hash_check(path, digest)
    expected_inputs = build["source_sha256"] | build["output_sha256"]
    for path in [HERE / "run_current.py", HERE / "build_thin_lto.py", RUNS / "build.json", ROOT / "validation/near-vacuum-adapter/oracle/output.json"]:
        expected_inputs[str(path.relative_to(ROOT))] = a.sha(path)
    summaries = a.read(RUNS / "runs.json")
    a.check([x["case"] for x in summaries] == CASES, "complete ordered run suite")
    binaries = {**{kind: "near_vacuum_adapter_validate_v3" for kind in KINDS}, "contract": "near_vacuum_contract_current", "contour": "five_pinch_compare_current"}
    for summary in summaries:
        name = summary["case"]
        record_path = RUNS / f"{name}-run.json"
        run = a.read(record_path)
        a.hash_check(record_path, summary["record_sha256"])
        a.check(run["exit_code"] == summary["exit_code"] == 0 and not run["timed_out"] and not summary["timed_out"], f"run success: {name}")
        a.check(run["inputs_unchanged"] and summary["inputs_unchanged"], f"run unchanged flag: {name}")
        a.check(run["sha256_before"] == expected_inputs == run["sha256_after"], f"exact run input hashes: {name}")
        args = [name] if name in KINDS else ([str(ROOT / "validation/near-vacuum-adapter/oracle/output.json")] if name == "contour" else [])
        a.check(run["command"] == ["taskset", "-c", "18", str(SCRATCH / binaries[name]), *args, str(RUNS / f"{name}.json")], f"run command: {name}")
        a.check(run["timeout_seconds"] == 60 and run["cwd"] == str(ROOT), f"bounded run cwd: {name}")
        a.check(run["diagnostic_wall_seconds"] == summary["diagnostic_wall_seconds"], f"diagnostic time record: {name}")
        a.hash_check(RUNS / f"{name}.json", run["output_sha256"])
        a.hash_check(RUNS / f"{name}.log", run["log_sha256"])
    # Bind durable reports to their already archived qualification, not loose files.
    for case in durable["cases"]:
        for path, digest in case["artifacts"].items():
            a.hash_check(path, digest)
    for relative in ["contract.json", "contour/output.json"]:
        path = OLD / relative
        a.hash_check(path, durable["additional_artifacts"][str(path.relative_to(ROOT))])
    old_contour_build_path = OLD / "contour/build.json"
    a.hash_check(old_contour_build_path, durable["additional_artifacts"][str(old_contour_build_path.relative_to(ROOT))])
    old_contour_build = a.read(old_contour_build_path)
    frozen_oracle_hashes = [digest for path, digest in old_contour_build["sha256"].items() if path.endswith("/oracle/output.json")]
    a.check(len(frozen_oracle_hashes) == 1, "unique frozen independent oracle hash")
    a.hash_check(ROOT / "validation/near-vacuum-adapter/oracle/output.json", frozen_oracle_hashes[0], "independent oracle still equals durable v3 input")
    a.observations["closure"] = {"recorded_files": len(before), "native_manifest_rows": len(manifest["native_files"]), "live_hashing_scope": "Selected dependency archives, build sources/outputs, and evidence files; full closure integrity is checked through the builder/runner's four equal hash inventories."}


def typed(a):
    matched = changed = 0
    for kind, (working, requested) in KINDS.items():
        data = a.read(RUNS / f"{kind}.json")
        old = a.read(OLD / f"v3-{kind}.json")
        a.compare(kind, data, old)
        a.check(data["status"] == "isolated_adapter_checks_passed", f"typed status: {kind}")
        a.check((data["numeric"], data["working_bits"], data["requested_bits"]) == (kind, working, requested), f"typed precision: {kind}")
        a.check(data["shape"] == SHAPE and len(data["rows"]) == 7, f"typed shape/rows: {kind}")
        a.check(data["primary_components_matching_qualified_candidate"] == 24, f"typed asserted components: {kind}")
        for key in ["safe_primal_ordinary_uncertified_success", "empty_reverse_scale_only_impossible_accuracy_checks"]:
            a.check(data[key] is True, f"typed assertion {kind}/{key}")
        a.check(data["ordinary_rows"] == 1 and data["ordinary_overlap_error"] == old["ordinary_overlap_error"], f"typed ordinary domain guard: {kind}")
        changes = []
        for lane, row in enumerate(data["rows"]):
            a.check(row["lane"] == lane, f"lane order: {kind}/{lane}")
            a.check(row["error"] == old["rows"][lane]["error"], f"typed error contract: {kind}/{lane}")
            a.check(row["formula"] == old["rows"][lane]["formula"], f"typed formula: {kind}/{lane}")
            a.check(row["attempts"] == old["rows"][lane]["attempts"], f"typed recurrence attempts: {kind}/{lane}")
            if lane not in [0, 2, 5, 6]:
                a.check(row["values"] is None and row["formula"] == "Rejected" and row["error"] is not None, f"failure hides values: {kind}/{lane}")
                continue
            a.check(row["error"] is None and len(row["values"]) == 6, f"successful component count: {kind}/{lane}")
            for component, (value, previous) in enumerate(zip(row["values"], old["rows"][lane]["values"])):
                re, im = map(Q, value)
                old_re, old_im = map(Q, previous)
                if value == previous:
                    matched += 1
                else:
                    changed += 1
                    distance = (re - old_re) ** 2 + (im - old_im) ** 2
                    budget = Q(1, 2 ** (2 * requested)) * max(1, re * re + im * im)
                    old_budget = Q(1, 2 ** (2 * requested)) * max(1, old_re * old_re + old_im * old_im)
                    # Exact necessary compatibility of two claimed error disks:
                    # d <= sqrt(B_current)+sqrt(B_old), without floating roots.
                    excess = distance - budget - old_budget
                    compatible = excess <= 0 or excess * excess <= 4 * budget * old_budget
                    a.check(compatible, f"old/current requested accuracy claims compatible: {kind}/{lane}/{component}")
                    changes.append({"lane": lane, "component": component, "difference_squared": str(distance), "current_binary_budget_squared": str(budget), "durable_binary_budget_squared": str(old_budget), "difference_within_current_budget": distance <= budget, "old_current_accuracy_claims_compatible": compatible})
                if lane == 5 and component > 0:
                    a.check(re == im == 0, f"zero scale derivatives: {kind}/{component}")
        a.check(data["series_execution"] == old["series_execution"], f"typed batched execution: {kind}")
        a.observations[kind] = {"changed_value_components": changes, "certificate_verification": "The unchanged hashed driver checks all 24 complete rectangles against the direct candidate and exact requested budgets during the successful run; these rectangles are not serialized in this typed report."}
    a.observations["typed_totals"] = {"components": matched + changed, "exactly_equal_to_durable_v3": matched, "changed": changed, "comparison_limit": "Distance to a previous rounded value is diagnostic; it is not an independent oracle bound."}


def contracts(a):
    data = a.read(RUNS / "contract.json")
    old = a.read(OLD / "contract.json")
    a.compare("contract", data, old, ["diagnostic_seconds"])
    a.check(data["status"] == "private_v3_contract_checks_passed", "contract status")
    a.check((data["numeric"], data["working_bits"], data["requested_bits"]) == ("f64", 53, 40), "contract precision")
    unsupported = data["unsupported_native_shape"]
    a.check(unsupported["shape"] == [[i] for i in range(6)] and unsupported["prepared_series_orders"] == [], "unsupported shape prepares no series")
    for key in ["analytic_zero_derivative_and_pole_checks", "legacy_all_laurent_components_bitwise_equal", "reversed_batch_equal"]:
        a.check(unsupported[key] is True, f"unsupported assertion: {key}")
    for policy in ["required", "allowed"]:
        batch = unsupported[policy]
        a.check(batch["series_execution"] == [] and batch["ordinary_rows"] == (2 if policy == "allowed" else 0), f"unsupported scheduling: {policy}")
        a.check(len(batch["rows"]) == 4, f"unsupported row count: {policy}")
        for lane, row in enumerate(batch["rows"]):
            previous = old["unsupported_native_shape"][policy]["rows"][lane]
            a.check({k: v for k, v in row.items() if k != "finite_values"} == {k: v for k, v in previous.items() if k != "finite_values"}, f"unsupported status contract: {policy}/{lane}")
            a.check(not row["finite_certificate_present"], f"unsupported no certificate: {policy}/{lane}")
            if policy == "allowed" and lane in [0, 2]:
                values = row["finite_values"]
                a.check(len(values) == 6, f"degree-five result count: {lane}")
                a.check(Q(values[0]["real"]) == Q(6004799503160661, 36028797018963968) and Q(values[0]["imaginary"]) == 0, f"rounded exact vacuum: {lane}")
                a.check(all(Q(v["real"]) == Q(v["imaginary"]) == 0 for v in values[1:]), f"degree-five scale derivatives vanish: {lane}")
            else:
                a.check(row["finite_values"] is None, f"unsupported rejection hides values: {policy}/{lane}")
    outside = data["all_outside_domain"]
    a.check(outside["prepared_series_orders"] == [2] and outside["no_N4_preparation_or_execution"], "outside domain no N4")
    a.check(outside["legacy_all_laurent_components_bitwise_equal"], "ordinary exact legacy equality assertion")
    for policy in ["required", "allowed"]:
        batch = outside[policy]
        a.check(batch["ordinary_rows"] == (3 if policy == "allowed" else 0), f"outside ordinary rows: {policy}")
        a.check(batch["series_execution"] == [{"active_rows": 0, "enclosure_batch_calls": 0, "input_rows": 3, "numeric_batch_calls": 0, "order": 2, "tail_batch_calls": 0}], f"outside no active series: {policy}")
        a.check(len(batch["rows"]) == 3, f"outside row count: {policy}")
        for lane, row in enumerate(batch["rows"]):
            previous = old["all_outside_domain"][policy]["rows"][lane]
            a.check({k: v for k, v in row.items() if k != "finite_values"} == {k: v for k, v in previous.items() if k != "finite_values"}, f"outside status contract: {policy}/{lane}")
            if policy == "required":
                a.check(row["finite_values"] is None, f"outside rejection hides values: {lane}")
            else:
                a.check(len(row["finite_values"]) == 1 and row["finite_values"] == batch["rows"][0]["finite_values"], f"repeated ordinary lanes agree: {lane}")
                for v in row["finite_values"]:
                    Q(v["real"]), Q(v["imaginary"])


def complex_exact(value):
    return Q(value["real_exact_rational"]), Q(value["imaginary_exact_rational"])


def contour(a):
    data = a.read(RUNS / "contour.json")
    old = a.read(OLD / "contour/output.json")
    oracle = a.read(ROOT / "validation/near-vacuum-adapter/oracle/output.json")
    a.compare("contour", data, old, ["diagnostic_seconds", "oracle_input"])
    a.check(data["status"] == "five_pinch_adapter_and_contraction_passed", "contour status")
    a.check((data["working_bits"], data["requested_bits"], data["ordinary_rows"]) == (256, 128, 0), "contour precision and no ordinary fallback")
    a.check(data["policy"] == "RequireFiniteCertificate" and data["contour_probe"] == oracle["fixture"], "contour policy and exact fixture")
    a.check(Path(data["oracle_input"]) == ROOT / "validation/near-vacuum-adapter/oracle/output.json", "durable oracle input")
    a.check(len(data["boxes"]) == 5 and data["series_execution"] == old["series_execution"], "five contour boxes in one N2 batch")
    typed_primal = a.read(RUNS / "float256.json")["rows"][5]["values"][0]
    contour_primal = data["boxes"][0]["comparison"]["numeric_value"]
    a.check(tuple(map(Q, typed_primal)) == complex_exact(contour_primal), "Float256 scale-only lane and contour pinch0 share exact N2 primal")
    pairs = []
    for i, box in enumerate(data["boxes"]):
        a.check(box["pinch"] == i and box["formula"] == "NearVacuum { order: 2 }" and box["requested_bits"] == 128, f"contour box formula: {i}")
        a.check(box["poles_exactly_zero"] and box["attempts"] == old["boxes"][i]["attempts"], f"contour zero poles and attempt: {i}")
        a.check(Q(box["truncation_radius"]) >= 0, f"contour nonnegative tail: {i}")
        pairs.append((box["comparison"], oracle["boxes"][i]["oracle"]))
    pairs.append((data["five_box_contraction_vs_independent_J5_D4"], oracle["independent_direct_J5_D4"]))
    for i, (c, reference) in enumerate(pairs):
        a.check(c["oracle_center"] == reference["center"] and Q(c["oracle_radius"]) == Q(reference["absolute_complex_remainder_bound_exact_rational"]), f"exact independent oracle: {i}")
        re, im = complex_exact(c["numeric_value"])
        cr, ci = complex_exact(c["oracle_center"])
        radius = Q(c["oracle_radius"])
        lo, hi = map(Q, c["candidate_rectangle"]["real"])
        li, ui = map(Q, c["candidate_rectangle"]["imaginary"])
        a.check(lo <= hi and li <= ui and radius >= 0, f"valid rectangle: {i}")
        numeric = (abs(re - cr) + radius) ** 2 + (abs(im - ci) + radius) ** 2
        whole = (max(abs(lo - cr), abs(hi - cr)) + radius) ** 2 + (max(abs(li - ci), abs(ui - ci)) + radius) ** 2
        certificate = max(abs(re - lo), abs(re - hi)) ** 2 + max(abs(im - li), abs(im - ui)) ** 2
        budget = Q(1, 2 ** 256) * max(1, re * re + im * im)
        for key, value in [("numeric_error_squared_upper", numeric), ("entire_candidate_rectangle_error_squared_upper", whole), ("numeric_to_candidate_rectangle_error_squared_upper", certificate), ("allowed_error_squared", budget)]:
            a.check(Q(c[key]) == value, f"exact {key}: {i}")
        a.check(max(numeric, whole, certificate) <= budget and c["all_bounds_within_requested_budget"], f"all contour bounds meet requested accuracy: {i}")
        overlap = lo <= cr + radius and cr - radius <= hi and li <= ci + radius and ci - radius <= ui
        contained = lo <= cr - radius and cr + radius <= hi and li <= ci - radius and ci + radius <= ui
        a.check(c["candidate_and_oracle_rectangles_overlap"] == overlap and overlap, f"contour oracle overlap: {i}")
        a.check(c["oracle_rectangle_contained_in_candidate"] == contained, f"truthful oracle containment flag: {i}")
    # The exact image of every candidate rectangle must fit the reported sum.
    sr = [Q(0), Q(0)]
    si = [Q(0), Q(0)]
    for coefficient, box in zip(oracle["geometry"]["C_i_at_t"], data["boxes"]):
        ar, ai = complex_exact(coefficient)
        rectangle = box["comparison"]["candidate_rectangle"]
        re = list(map(Q, rectangle["real"]))
        im = list(map(Q, rectangle["imaginary"]))
        rr, ii = sorted(ar * x for x in re), sorted(-ai * x for x in im)
        ri, ir = sorted(ar * x for x in im), sorted(ai * x for x in re)
        sr = [sr[j] + rr[j] + ii[j] for j in [0, 1]]
        si = [si[j] + ri[j] + ir[j] for j in [0, 1]]
    final = pairs[-1][0]["candidate_rectangle"]
    real, imag = list(map(Q, final["real"])), list(map(Q, final["imaginary"]))
    a.check(real[0] <= sr[0] <= sr[1] <= real[1] and imag[0] <= si[0] <= si[1] <= imag[1], "complete rectangle contraction encloses exact-C_i image")
    for name in ["contract", "contour"]:
        text = (RUNS / f"{name}.log").read_text()
        serialized = json.loads(text[text.index("{"):])
        a.check(serialized == a.read(RUNS / f"{name}.json"), f"stdout agrees with output: {name}")
    a.observations["contour"] = {"exact_comparisons": len(pairs), "all_oracle_rectangles_contained": all(c["oracle_rectangle_contained_in_candidate"] for c, _ in pairs), "scope": data["scope"]}


def main():
    required = [RUNS / name for name in ["build.json", "runs.json", "closure-before.json", "closure-after-build.json", "closure-before-runs.json", "closure-after-runs.json"]]
    required += [RUNS / f"{case}{suffix}" for case in CASES for suffix in [".json", ".log", "-run.json"]]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        print(json.dumps({"status": "evidence_incomplete_audit_not_run", "missing": missing}, indent=2))
        return 2
    destination = RUNS / "audit.json"
    if destination.exists():
        print("Refusing to overwrite an existing audit report", file=sys.stderr)
        return 2
    audit = Audit()
    audit.sha(Path(__file__))
    try:
        provenance(audit)
        typed(audit)
        contracts(audit)
        contour(audit)
    except Exception as error:
        audit.failures.append(f"Audit exception: {type(error).__name__}: {error}")
    changed = sum(len(v) for v in audit.differences.values())
    report = {
        "status": "failed" if audit.failures else ("passed_with_serialized_differences" if changed else "passed"),
        "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "checks": audit.checks,
        "failures": audit.failures,
        "serialized_difference_count": changed,
        "serialized_differences": audit.differences,
        "observations": audit.observations,
        "sha256_verified_live": audit.hashes,
        "audit_script_sha256": audit.sha(Path(__file__)),
        "method": "Independent exact Fraction comparisons and SHA256 evidence audit; no Symbolica evaluation, scalar-master execution, compilation or timing benchmark.",
        "limitations": [
            "Typed complete-rectangle and Laurent assertions are source-bound runtime evidence; typed JSON serializes finite values, not the rectangles or all pole arrays.",
            "A difference from a durable rounded value is reported separately and does not establish an independent exact-oracle guarantee.",
            "Contour arithmetic checks cover exact represented shifted inputs at x=1/2, excluding upstream geometry/mass-shift rounding, Gauss weights and quadrature truncation.",
            "This private current-dependency repeat does not enable production reduction or qualify performance.",
        ],
    }
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "checks": audit.checks, "failures": audit.failures, "serialized_difference_count": changed, "report": str(destination.relative_to(ROOT)), "audit_script_sha256": report["audit_script_sha256"]}, indent=2))
    return int(bool(audit.failures))


if __name__ == "__main__":
    sys.exit(main())
