"""Verify the compact capsule and rerun only independent saved-data arithmetic."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    here = Path(__file__).resolve().parent
    qualification = json.loads((here / "qualification.json").read_text())
    assert qualification["status"] == "passed-private-generalized-cayley-cohort"
    assert sha(__file__) == qualification["checker_sha256"]
    archive = here / "source-results.tar.gz"
    assert sha(archive) == qualification["archive_sha256"]
    with tempfile.TemporaryDirectory(prefix="tirust-cayley-saved-") as temporary:
        root = Path(temporary)
        with tarfile.open(archive, "r:gz") as stream:
            members = stream.getmembers()
            assert len(members) == len(qualification["files"])
            assert len({member.name for member in members}) == len(members)
            for member in members:
                assert member.isfile() and not Path(member.name).is_absolute() and ".." not in Path(member.name).parts
                assert member.name in qualification["files"]
                contents = stream.extractfile(member).read()
                assert hashlib.sha256(contents).hexdigest() == qualification["files"][member.name]
                target = root / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(contents)
        script = root / "target/routing-rational-cayley-full-core/independent_saved_numeric_audit.py"
        result = subprocess.run([sys.executable, str(script)], cwd=root, text=True,
            capture_output=True, timeout=30, check=True)
        report = json.loads(result.stdout)
        assert report["status"] == "passed-independent-saved-numeric-review" and report["checks"] == 7415
        assert report["totals"]["complex_output_slots"] == 240
        assert report["totals"]["exact_complex_input_slots"] == 2060
    print(json.dumps(dict(status="passed-capsule-and-independent-saved-arithmetic",
        payload_files=len(qualification["files"]), cases=3, complex_outputs=240,
        exact_complex_inputs=2060, retained_control_outputs=80,
        compiler_or_integral_execution=False, performance_qualified=False)))


if __name__ == "__main__":
    main()
