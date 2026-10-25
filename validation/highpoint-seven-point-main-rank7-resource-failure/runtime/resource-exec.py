"""Source-only proposed resource prelude; execs the one actual Cargo test binary.

The outer finite controller owns timeout, source guards and process-group cleanup.
No library/reference preparation or numerical operation occurs in this wrapper.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

ADDRESS_SPACE_BYTES = 32 * 1024**3
TEST_ARGS = ["--exact", "thin_n7::numeric_probe::capture_complete_moments_from_fixture",
             "--ignored", "--nocapture", "--test-threads=1"]


def main():
    assert len(sys.argv) == 4, "resource_exec actual_Cargo_test_binary expected_sha256 exec_prelude.json"
    executable, expected_sha, output = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    assert executable.is_absolute() and output.is_absolute()
    assert not output.exists()
    assert len(expected_sha) == 64 and all(c in "0123456789abcdef" for c in expected_sha)
    started = time.monotonic()
    # This only constrains the isolated numerical child. It never changes the
    # parent controller or Cargo build process, and never changes a math input.
    resource.setrlimit(resource.RLIMIT_AS, (ADDRESS_SPACE_BYTES, ADDRESS_SPACE_BYTES))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    with executable.open("rb") as stream:
        actual_sha = hashlib.file_digest(stream, "sha256").hexdigest()
    assert actual_sha == expected_sha, "actual Cargo test executable hash mismatch"
    stat = Path("/proc/self/stat").read_text()
    fields = stat[stat.rfind(")") + 2:].split()
    record = dict(status="resource_limits_set_before_exec", pid=os.getpid(),
        starttime_ticks=int(fields[19]), process_group=os.getpgrp(), session=os.getsid(0),
        executable=str(executable), executable_sha256=actual_sha, arguments=TEST_ARGS,
        address_space_soft_hard_bytes=list(resource.getrlimit(resource.RLIMIT_AS)),
        core_soft_hard_bytes=list(resource.getrlimit(resource.RLIMIT_CORE)),
        prelude_seconds=time.monotonic()-started,
        purpose="prospective resource bound; no numerical/performance qualification",
        environment_values_recorded=False, license_recorded=False)
    assert record["process_group"] == record["session"] == record["pid"], "outer supervisor must own a fresh session"
    # Exclusive write prevents replacing a prior attempt's kernel identity.
    with output.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.execv(str(executable), [str(executable), *TEST_ARGS])


if __name__ == "__main__":
    main()
