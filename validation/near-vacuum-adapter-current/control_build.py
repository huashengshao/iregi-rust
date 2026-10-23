#!/usr/bin/env python3
"""Pause/resume this owned compile group only; never a bounded numeric run."""
import datetime
import json
import os
from pathlib import Path
import signal
import sys

ROOT = Path(__file__).resolve().parents[2]
PID = 3216966
START_TICKS = 81152928
EXPECTED = b'validation/near-vacuum-adapter-current/build_thin_lto.py'

def main():
    assert len(sys.argv) == 2 and sys.argv[1] in ['pause', 'resume']
    mode = sys.argv[1]
    proc = Path(f'/proc/{PID}')
    if not proc.exists():
        print(json.dumps({'status': 'owned_build_already_exited', 'pid': PID}))
        return
    command = (proc / 'cmdline').read_bytes().split(b'\0')
    assert EXPECTED in command, 'Refusing to signal an unrelated/reused PID'
    fields = (proc / 'stat').read_text().split(') ', 1)[1].split()
    assert int(fields[19]) == START_TICKS, 'Refusing a reused PID'
    assert (proc / 'cwd').resolve() == ROOT
    assert os.getpgid(PID) == PID and os.getsid(PID) == PID
    os.killpg(PID, signal.SIGSTOP if mode == 'pause' else signal.SIGCONT)
    event = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'pid': PID, 'process_group': PID, 'action': mode,
             'scope': 'Compiler process group only; no timeout-bounded runtime belongs to this group.'}
    with (Path(__file__).parent / 'build-control-events.jsonl').open('a') as stream:
        stream.write(json.dumps(event) + '\n')
    print(json.dumps(event))

if __name__ == '__main__':
    main()
