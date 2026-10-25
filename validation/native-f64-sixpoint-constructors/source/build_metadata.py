"""Eight private core metadata checks; import performs no execution."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import sys
from lifecycle import Budget, execute

PROJECT = Path.cwd()
HERE = PROJECT / "target/native-f64-sixpoint-port/qualification"
CAP = 180

def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")

def recipe(attempt, manifest):
    tools = manifest["tools"]
    core = HERE / "public-source/crates/iregi-rust"
    common = [tools["taskset"]["path"], "-c", "6,7", tools["rustc"]["path"],
              "--edition=2024", "-C", "opt-level=0", "-C", "debuginfo=0",
              "-C", "strip=debuginfo", "-C", "debug-assertions=yes",
              "-C", "overflow-checks=yes", "-C", f'linker={tools["cc"]["path"]}']
    for kind, directory in [("dependency", manifest["dependency_directory"]),
                            ("dependency", manifest["supplemental_directory"]),
                            ("native", manifest["native_directory"])]:
        common += ["-L", f"{kind}={PROJECT / directory}"]
    steps = []
    for configuration in ("default", "selective", "broad", "both"):
        master = manifest["reused_masters"][configuration]
        cfg = ["--cfg", 'feature="default"']
        if configuration in ("selective", "both"):
            cfg += ["--cfg", 'feature="native-f64-abc"']
        for tests in (False, True):
            label = configuration + ("-core-tests" if tests else "-core")
            output = attempt / configuration / ("core-tests.rmeta" if tests else "libiregi_rust.rmeta")
            command = common + ["-L", f'dependency={Path(master["path"]).parent}',
                                "--crate-name", "iregi_rust_tests" if tests else "iregi_rust",
                                "-C", "metadata=native_sixpoint_metadata_" + label.replace("-", "_")]
            command += ["--test"] if tests else ["--crate-type", "rlib"]
            command += ["--emit", "metadata"] + cfg + [str(core / "src/lib.rs"), "-o", str(output)]
            externs = ["symbolica", "iregi_masters", "serde", "thiserror"]
            if tests:
                externs += ["serde_json", "oneloop"]
            for name in externs:
                path = master["path"] if name == "iregi_masters" else str(PROJECT / manifest["externs"][name])
                command += ["--extern", f"{name}={path}"]
            steps.append({"label": label, "configuration": configuration, "command": command,
                          "output": str(output), "timeout_seconds": 60,
                          "reused_masters_sha256": master["sha256"],
                          "environment": {"CARGO_CRATE_NAME": "iregi_rust", "CARGO_MANIFEST_DIR": str(core)}})
    assert len(steps) == 8
    return steps

def main():
    assert len(sys.argv) == 2 and sys.argv[1] == "001", "one separately granted attempt: 001"
    attempt = HERE / "metadata-build-001"
    attempt.mkdir(exist_ok=False)
    budget = Budget(CAP)
    record = {"status": "preparing", "stage": "combined-core-metadata",
              "scope": "private core metadata only; exact prior masters reused; no runtime/Cargo/live mutation",
              "runtime_cap_seconds": CAP, "cleanup_reserve_seconds": 8, "compile_cpus": [6, 7],
              "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "input_sha256": {}, "steps": [], "outputs": {}, "cleanup_errors": []}
    save(attempt / "build.json", record)
    bindings = {}
    binding_setup_complete = False

    def verify():
        assert binding_setup_complete, "input binding setup did not complete"
        for path, expected in bindings.items():
            budget.remaining()
            assert sha(path) == expected, f"changed input: {path}"
        for output in record["outputs"].values():
            budget.remaining()
            assert sha(output["path"]) == output["sha256"], f'changed previous output: {output["path"]}'

    budget.arm()
    try:
        prep_path = HERE / "preparation.json"
        plan_path = HERE / "command-plan.json"
        grant_path = HERE / "metadata-execution-grant-001.json"
        manifest = read(prep_path)
        grant = read(grant_path)
        assert grant["preparation_sha256"] == sha(prep_path)
        assert grant["command_plan_sha256"] == sha(plan_path)
        assert grant["runner_sha256"] == sha(Path(__file__))
        assert grant["lifecycle_sha256"] == sha(HERE / "lifecycle.py")
        assert grant["aggregate_seconds"] == CAP and grant["compile_cpus"] == [6, 7]
        bindings = {Path(path): value for path, value in manifest["input_sha256"].items()}
        bindings[prep_path] = sha(prep_path)
        bindings[grant_path] = sha(grant_path)
        assert bindings[Path(__file__).resolve()] == sha(Path(__file__))
        assert bindings[plan_path] == sha(plan_path)
        steps = recipe(attempt, manifest)
        assert steps == read(plan_path)["steps"]
        record["steps"] = steps
        for step in steps:
            step["status"] = "unrun"
        record["input_sha256"] = {str(path): value for path, value in bindings.items()}
        binding_setup_complete = True
        save(attempt / "build.json", record)
        verify()
        for step in steps:
            budget.remaining()
            Path(step["output"]).parent.mkdir(exist_ok=True)
            environment = os.environ.copy()
            environment.update(step["environment"])

            def persist(result):
                step.update(result)
                save(attempt / "build.json", record)

            result = execute(step["command"], attempt / (step["label"] + ".log"), budget,
                             step["timeout_seconds"], record["cleanup_errors"], persist, environment)
            step["status"] = "compiled" if result["status"] == "exited" else "failed"
            save(attempt / "build.json", record)
            assert step["status"] == "compiled", step["label"] + " failed; stop without retry"
            verify()
            output = Path(step["output"])
            step["output_sha256"] = sha(output)
            step["status"] = "passed"
            record["outputs"][step["label"]] = {"path": str(output), "sha256": step["output_sha256"], "bytes": output.stat().st_size}
            save(attempt / "build.json", record)
        record["status"] = "completed-awaiting-guards"
    except Exception as error:
        record.update(status="failed", error=repr(error))

    # Terminal bookkeeping precedes final potentially failing hashes.
    record["elapsed_seconds"] = budget.elapsed()
    record["deadline_exceeded"] = record["elapsed_seconds"] > CAP
    save(attempt / "build.json", record)
    try:
        verify()
        record["inputs_unchanged"] = True
        record["compiler_logs_sha256"] = {str(path): sha(path) for path in sorted(attempt.glob("*.log"))}
    except Exception as error:
        record.update(inputs_unchanged=False, guard_error=repr(error))
    record["elapsed_seconds"] = budget.elapsed()
    record["deadline_exceeded"] |= record["elapsed_seconds"] > CAP
    record["status"] = "passed" if (len(record["steps"]) == 8
        and all(step["status"] == "passed" for step in record["steps"])
        and record["inputs_unchanged"] and not record["cleanup_errors"]
        and not record["deadline_exceeded"] and "error" not in record) else "failed"
    record["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save(attempt / "build.json", record)
    budget.disarm()
    print(json.dumps({"status": record["status"], "elapsed_seconds": record["elapsed_seconds"],
                      "steps": [{key: step.get(key) for key in ("label", "status", "returncode", "elapsed_seconds")}
                                for step in record["steps"]]}))
    return 0 if record["status"] == "passed" else 1

if __name__ == "__main__":
    sys.exit(main())
