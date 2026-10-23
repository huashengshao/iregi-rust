"""Exercise actual pipe backpressure without starting numerical backends."""
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest

import run as benchmark


class TransportTests(unittest.TestCase):
    def process(self, code, timeout):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executable = directory / "adapter"
        executable.write_text(f"#!{sys.executable}\n" + code)
        executable.chmod(0o700)
        process = benchmark.Process(executable, "transport", directory, timeout)
        self.addCleanup(process.close)
        return process

    def test_timeout_includes_a_large_request_to_a_child_that_never_reads(self):
        process = self.process("import time\ntime.sleep(30)\n", 0.15)
        started = time.monotonic()
        with self.assertRaisesRegex(TimeoutError, "exceeded timeout"):
            process.request("x" * (4 * 1024 * 1024) + "\n")
        self.assertLess(time.monotonic() - started, 3)
        self.assertIsNotNone(process.process.poll(), "timed-out adapter must be reaped")

    def test_full_duplex_large_requests_and_persistent_replies(self):
        process = self.process(
            "import json, sys\n"
            "for _ in range(64):\n"
            "    sys.stdout.write('diagnostic ' + 'z' * 4096 + '\\n')\n"
            "sys.stdout.flush()\n"
            "for line in sys.stdin:\n"
            "    if line.strip() == 'QUIT': break\n"
            "    value = json.loads(line)\n"
            "    print('RESULT ' + json.dumps({'id': value['id'], 'length': len(value['data'])}), flush=True)\n",
            3,
        )
        for identity, size in [("large", 1024 * 1024), ("second", 17)]:
            with self.subTest(identity=identity):
                reply = process.request(json.dumps({"id": identity, "data": "x" * size}) + "\n")
                self.assertEqual(reply, {"id": identity, "length": size})

    def test_eof_without_a_reply_does_not_wait_until_the_deadline(self):
        process = self.process("import sys\nsys.stdin.readline()\n", 3)
        started = time.monotonic()
        with self.assertRaisesRegex(RuntimeError, "exited without RESULT"):
            process.request("request\n")
        self.assertLess(time.monotonic() - started, 2)


if __name__ == "__main__":
    unittest.main()
