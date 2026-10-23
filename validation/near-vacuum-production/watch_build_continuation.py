"""Finish a logged compilation continuation without changing numerical limits."""
from pathlib import Path
import datetime
import json
import os
import signal
import sys
import time

base = Path(sys.argv[1])
path = base / "build-continuation.json"
event = json.loads(path.read_text())
assert event["status"] == "build-continuation-active"


def stat(identity):
    process = Path("/proc") / str(identity["pid"])
    try:
        fields = (process / "stat").read_text().rsplit(")", 1)[1].split()
    except FileNotFoundError:
        return None
    assert fields[19] == identity["start_ticks"], "process identity changed"
    return fields


assert stat(event["wrapper"])[0] == "T"
start = time.monotonic()
try:
    while True:
        fields = stat(event["cargo"])
        if fields is None or fields[0] == "Z":
            event["compilation_process_finished"] = True
            break
        if time.monotonic() - start >= event["extra_compilation_timeout_seconds"]:
            os.killpg(event["cargo"]["pgid"], signal.SIGKILL)
            event["extra_compilation_timed_out"] = True
            break
        time.sleep(1)
finally:
    if stat(event["wrapper"]) is not None:
        os.kill(event["wrapper"]["pid"], signal.SIGCONT)
    event.update(status="continuation-finished", watcher_elapsed_seconds=time.monotonic() - start,
                 resumed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    print(json.dumps(event), flush=True)
    path.write_text(json.dumps(event, indent=2) + "\n")
