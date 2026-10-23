"""One bounded installation of pinned browser tooling into project-owned paths."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent / "attempt001"
CAP = 300


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["PLAYWRIGHT_BROWSERS_PATH"] = str(ROOT / ".local/playwright-browsers")
    python = ROOT / ".local/notebooks-browser-env/bin/python"
    commands = [
        ("venv", [sys.executable, "-m", "venv", str(ROOT / ".local/notebooks-browser-env")]),
        ("package", [str(python), "-m", "pip", "--disable-pip-version-check", "install", "playwright==1.55.0"]),
        ("chromium", [str(python), "-m", "playwright", "install", "--only-shell", "chromium"]),
    ]
    start = time.monotonic()
    receipts = []
    for name, command in commands:
        began = time.monotonic()
        with (OUT / f"setup-{name}-stdout.log").open("w") as stdout, (OUT / f"setup-{name}-stderr.log").open("w") as stderr:
            child = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=stdout,
                                     stderr=stderr, start_new_session=True)
            try:
                code = child.wait(timeout=max(1, CAP - (time.monotonic() - start)))
                status = "completed"
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
                code = child.returncode
                status = "timeout"
        receipts.append({"name": name, "command": command, "status": status,
                         "exit_code": code, "seconds": time.monotonic() - began})
        record = {"recorded_utc": datetime.now(timezone.utc).isoformat(),
                  "total_cap_seconds": CAP, "total_seconds": time.monotonic() - start,
                  "commands": receipts, "browser_cache": environment["PLAYWRIGHT_BROWSERS_PATH"],
                  "manual_retries": 0, "Rust_or_native_wheel_operations": False}
        (OUT / "setup.json").write_text(json.dumps(record, indent=2) + "\n")
        print(json.dumps(receipts[-1]), flush=True)
        if code != 0 or status != "completed":
            break


if __name__ == "__main__":
    main()
