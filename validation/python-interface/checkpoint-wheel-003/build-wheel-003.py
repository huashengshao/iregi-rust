"""Root-authorized jobs-only wheel attempt with sampled resource bounds."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time


evidence = Path("target/python-interface-build")
previous = json.loads((evidence / "wheel-002.json").read_text())["command"]
command = list(previous)
jobs_index = command.index("--jobs") + 1
assert command[jobs_index] == "2"
command[jobs_index] = "8"
assert [(left, right) for left, right in zip(previous, command) if left != right] == [("2", "8")]
owner_guard = json.loads((evidence / "wheel-001-source-owners.json").read_text())
for name, row in owner_guard["files"].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == row["sha256"]
inputs = set(owner_guard["files"])
inputs.update(str(path) for path in Path("python/tirust").rglob("*") if path.is_file())
inputs.update(("Cargo.toml", "Cargo.lock", "pyproject.toml", "python/README.md", "dependencies/symbolica/IREGI_UPSTREAM_VERSION"))
before = {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in sorted(inputs)}
started = time.time()
monotonic_start = time.monotonic()
cap_seconds = 1800
rss_cap_bytes = 64 * 1024**3
start_receipt = {
    "scope": "root-authorized jobs-only change, same source/profile/features/cache/interpreter",
    "started_unix": started,
    "command": command,
    "only_command_difference": {"jobs": [2, 8]},
    "cap_seconds": cap_seconds,
    "sampled_whole_process_group_rss_cap_bytes": rss_cap_bytes,
    "sample_interval_seconds": 5,
    "source_owner_guard_sha256": hashlib.sha256((evidence / "wheel-001-source-owners.json").read_bytes()).hexdigest(),
    "source_owner_files": owner_guard["file_count"],
    "input_files": before,
    "lock_sha256": before["Cargo.lock"],
}
(evidence / "wheel-003-start.json").write_text(json.dumps(start_receipt, indent=2) + "\n")


def processes(pgid: int) -> list[dict[str, object]]:
    output = subprocess.run(
        ["ps", "-g", str(pgid), "-o", "pid=,ppid=,rss=,pcpu=,comm="],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    rows = []
    for line in output.splitlines():
        pid, parent, rss, cpu, name = line.split(maxsplit=4)
        rows.append({"pid": int(pid), "ppid": int(parent), "rss_bytes": int(rss) * 1024, "lifetime_cpu_percent": float(cpu), "name": name})
    return rows


def terminate(pgid: int) -> None:
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def compiler_snapshot(pgid: int, elapsed: float, rows: list[dict[str, object]]) -> dict[str, object]:
    compilers = []
    for row in rows:
        if row["name"] != "rustc":
            continue
        pid = int(row["pid"])
        directory = Path(f"/proc/{pid}")
        try:
            argv = [part.decode(errors="replace") for part in (directory / "cmdline").read_bytes().split(b"\0") if part]
            environment = {}
            for part in (directory / "environ").read_bytes().split(b"\0"):
                key, _, value = part.partition(b"=")
                if key in (b"CARGO_MAKEFLAGS", b"NUM_JOBS"):
                    environment[key.decode()] = value.decode(errors="replace")
            threads = subprocess.run(["ps", "-L", "-o", "pid,tid,pcpu,rss,stat,wchan:28,comm", "-p", str(pid)], capture_output=True, text=True, check=False).stdout
        except (FileNotFoundError, ProcessLookupError):
            continue
        compilers.append({"pid": pid, "argv": argv, "jobserver_environment_only": environment, "threads": threads})
    objects = []
    for path in Path("target/cargo-build/debug/deps").glob("symbolica-09563b0bee1a5a34.*.rcgu.o"):
        stat = path.stat()
        objects.append({"path": str(path), "bytes": stat.st_size, "mtime": stat.st_mtime, "new_since_start": stat.st_mtime >= started})
    return {"captured_unix": time.time(), "elapsed_seconds": elapsed, "pgid": pgid, "processes": rows, "compilers": compilers, "runtime_objects": objects}


status = "completed"
peak_rss_bytes = 0
peak_lifetime_cpu_percent_sum = 0.0
code = None
with (evidence / "wheel-003.log").open("w") as log, (evidence / "wheel-003-resource-samples.jsonl").open("w") as samples:
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    (evidence / "wheel-003-pgid.json").write_text(json.dumps({"pid": process.pid, "pgid": process.pid, "started_unix": started}, indent=2) + "\n")
    next_sample = 0.0
    checkpoints = iter((120, 300, 600))
    next_checkpoint = next(checkpoints, None)
    while process.poll() is None:
        elapsed = time.monotonic() - monotonic_start
        if elapsed >= cap_seconds:
            status = "timeout"
            terminate(process.pid)
            break
        if elapsed >= next_sample:
            rows = processes(process.pid)
            rss = sum(int(row["rss_bytes"]) for row in rows)
            cpu = sum(float(row["lifetime_cpu_percent"]) for row in rows)
            peak_rss_bytes = max(peak_rss_bytes, rss)
            peak_lifetime_cpu_percent_sum = max(peak_lifetime_cpu_percent_sum, cpu)
            samples.write(json.dumps({"elapsed_seconds": elapsed, "whole_pg_rss_bytes": rss, "active_process_lifetime_cpu_percent_sum": cpu, "processes": rows}) + "\n")
            samples.flush()
            if rss > rss_cap_bytes:
                status = "rss_limit"
                terminate(process.pid)
                break
            if next_checkpoint is not None and elapsed >= next_checkpoint:
                snapshot = compiler_snapshot(process.pid, elapsed, rows)
                (evidence / f"wheel-003-checkpoint-{next_checkpoint:04d}.json").write_text(json.dumps(snapshot, indent=2) + "\n")
                next_checkpoint = next(checkpoints, None)
            next_sample = elapsed + 5
        time.sleep(0.25)
    observed_code = process.wait()
    if status == "completed":
        code = observed_code
changed = [name for name, value in before.items() if not Path(name).exists() or hashlib.sha256(Path(name).read_bytes()).hexdigest() != value]
receipt = {
    "scope": start_receipt["scope"],
    "command": command,
    "seconds": time.monotonic() - monotonic_start,
    "status": status,
    "exit_code": code,
    "cap_seconds": cap_seconds,
    "jobs": 8,
    "whole_owned_process_group_bounded": True,
    "sampled_whole_pg_rss_cap_bytes": rss_cap_bytes,
    "peak_sampled_whole_pg_rss_bytes": peak_rss_bytes,
    "peak_active_process_lifetime_cpu_percent_sum": peak_lifetime_cpu_percent_sum,
    "cpu_statistic_note": "Sum of ps lifetime percentages for active processes, not an instantaneous CPU limit.",
    "source_owner_files": owner_guard["file_count"],
    "guarded_input_files": len(before),
    "changed_inputs": changed,
    "source_unchanged": not changed,
    "lock_sha256": hashlib.sha256(Path("Cargo.lock").read_bytes()).hexdigest(),
}
(evidence / "wheel-003.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt))
