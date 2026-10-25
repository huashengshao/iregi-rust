"""One separately granted cohort of exact tests; no build or automatic next stage."""
from pathlib import Path
import datetime
import os
import re
import sys
from build_metadata import read, save, sha
from lifecycle import Budget, execute, freeze_binary
import runtime_inventory as inventory

HERE = Path.cwd() / "target/native-f64-sixpoint-port/qualification"

def validate_listing(text, configuration):
    names = [line.removesuffix(": test") for line in text.splitlines() if line.endswith(": test")]
    assert len(names) == len(set(names)), "duplicate libtest listing"
    actual = sorted(name for name in names if inventory.tracked(name))
    expected = sorted(case["name"] for case in inventory.cases() if case["configuration"] == configuration)
    assert actual == expected, "tracked test inventory differs"

def validate_case_log(text, name):
    assert re.findall(r"^test ([A-Za-z0-9_:]+) \.\.\.", text, re.MULTILINE) == [name], "executed test name differs"
    assert re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured;", text) == [("1", "0", "0", "0")], "test failed, ignored, absent, or repeated"

def main():
    assert len(sys.argv) == 3 and sys.argv[1] in inventory.GROUPS and sys.argv[2] == "001"
    stage = sys.argv[1]
    cap = inventory.GROUPS[stage]["aggregate_seconds"]
    attempt = HERE / (stage + "-tests-001")
    attempt.mkdir(exist_ok=False)
    budget = Budget(cap)
    record = {"status": "preparing", "stage": stage, "runtime_cap_seconds": cap,
              "cleanup_reserve_seconds": 8, "runtime_cpu": 22,
              "scope": "private default/selective exact unit tests; no builds, whole-array/performance or production claim",
              "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "license_environment_present": any("SYMBOLICA" in key and "LICENSE" in key for key in os.environ),
              "input_sha256": {}, "cases": [], "listings": [], "executed_executables": {}, "cleanup_errors": []}
    save(attempt / "results.json", record)
    bindings = {}
    binding_setup_complete = False

    def verify():
        assert binding_setup_complete, "input binding setup did not complete"
        for path, expected in bindings.items():
            budget.remaining()
            assert sha(path) == expected, f"changed input: {path}"
        for executable in record["executed_executables"].values():
            budget.remaining()
            assert sha(executable["path"]) == executable["sha256"], "frozen executable changed"

    budget.arm()
    try:
        prep_path = HERE / "runtime-preparation.json"
        plan_path = HERE / "runtime-command-plan.json"
        grant_path = HERE / (stage + "-runtime-grant-001.json")
        manifest = read(prep_path)
        grant = read(grant_path)
        assert grant["preparation_sha256"] == sha(prep_path)
        assert grant["command_plan_sha256"] == sha(plan_path)
        assert grant["runner_sha256"] == sha(Path(__file__))
        assert grant["inventory_sha256"] == sha(HERE / "runtime_inventory.py")
        assert grant["lifecycle_sha256"] == sha(HERE / "lifecycle.py")
        assert grant["stage"] == stage and grant["aggregate_seconds"] == cap and grant["runtime_cpu"] == 22
        bindings = {Path(path): value for path, value in manifest["input_sha256"].items()}
        bindings[prep_path] = sha(prep_path)
        bindings[grant_path] = sha(grant_path)
        assert bindings[Path(__file__).resolve()] == sha(Path(__file__))
        assert bindings[plan_path] == sha(plan_path)
        plan = inventory.plan(stage, attempt, manifest)
        assert plan == read(plan_path)[stage]
        record["cases"] = plan["cases"]
        record["listings"] = plan["listings"]
        for entry in record["cases"] + record["listings"]:
            entry["status"] = "unrun"
        record["input_sha256"] = {str(path): value for path, value in bindings.items()}
        binding_setup_complete = True
        save(attempt / "results.json", record)
        verify()
        for configuration, artifact in manifest["test_binaries"].items():
            frozen = freeze_binary(artifact["path"], artifact["sha256"], attempt / (configuration + "-core-tests-frozen"), budget)
            record["executed_executables"][configuration] = {"path": str(frozen), "sha256": artifact["sha256"]}
            save(attempt / "results.json", record)
        for listing in record["listings"]:
            log = attempt / (listing["configuration"] + "-list.log")

            def persist(result):
                listing.update(result)
                save(attempt / "results.json", record)

            result = execute(listing["command"], log, budget, listing["timeout_seconds"], record["cleanup_errors"], persist)
            assert result["status"] == "exited", "listing process failed; stop without retry"
            listing["log_sha256"] = sha(log)
            save(attempt / "results.json", record)
            validate_listing(log.read_text(), listing["configuration"])
            listing["inventory_verified"] = True
            save(attempt / "results.json", record)
        verify()
        for index, case in enumerate(record["cases"]):
            log = attempt / f"case-{index:02d}.log"

            def persist(result):
                case.update(result)
                save(attempt / "results.json", record)

            result = execute(case["command"], log, budget, case["timeout_seconds"], record["cleanup_errors"], persist)
            assert result["status"] == "exited", case["name"] + " process failed; stop without retry"
            case["log_sha256"] = sha(log)
            save(attempt / "results.json", record)
            validate_case_log(log.read_text(), case["name"])
            case["status"] = "passed"
            save(attempt / "results.json", record)
            verify()
        record["status"] = "completed-awaiting-guards"
    except Exception as error:
        record.update(status="failed", error=repr(error))

    record["elapsed_seconds"] = budget.elapsed()
    record["deadline_exceeded"] = record["elapsed_seconds"] > cap
    save(attempt / "results.json", record)
    try:
        verify()
        record["inputs_unchanged"] = True
        record["log_sha256"] = {str(path): sha(path) for path in sorted(attempt.glob("*.log"))}
    except Exception as error:
        record.update(inputs_unchanged=False, guard_error=repr(error))
    record["elapsed_seconds"] = budget.elapsed()
    record["deadline_exceeded"] |= record["elapsed_seconds"] > cap
    record["status"] = "passed" if (len(record["cases"]) == inventory.GROUPS[stage]["count"]
        and all(case["status"] == "passed" for case in record["cases"])
        and len(record["listings"]) == 2 and all(item.get("inventory_verified") is True for item in record["listings"])
        and record["inputs_unchanged"] and not record["cleanup_errors"] and not record["deadline_exceeded"]
        and "error" not in record) else "failed"
    record["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save(attempt / "results.json", record)
    budget.disarm()
    print({"status": record["status"], "stage": stage, "cases": len(record["cases"]), "elapsed_seconds": record["elapsed_seconds"]})
    return 0 if record["status"] == "passed" else 1

if __name__ == "__main__":
    sys.exit(main())
