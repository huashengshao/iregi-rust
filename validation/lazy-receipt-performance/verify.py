"""Verify the durable package without numerical evaluation, builds or timings."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
inventory = read(HERE / "files.json")
for name, digest in inventory.items():
    assert sha(HERE / name) == digest, name
sources = read(HERE / "source-archive-manifest.json")
with tarfile.open(HERE / "source-snapshots.tar.gz", "r:gz") as archive:
    members = archive.getmembers()
    assert len(members) == len(sources) == len({m.name for m in members})
    assert {m.name for m in members} == set(sources)
    for member in members:
        assert member.isfile()
        assert hashlib.sha256(archive.extractfile(member).read()).hexdigest() == sources[member.name]["sha256"]
run = read(HERE / "protocol/performance-run.json")
qualification = read(HERE / "qualification.json")
assert run["status"] == "passed" and run["provenance_qualified"]
assert sha(HERE / "protocol/performance.csv") == run["raw_csv_sha256"]
assert sha(HERE / "protocol/performance.log") == run["log_sha256"]
assert sha(HERE / "protocol/analyze.py") == run["analysis_source_sha256"]
assert sha(HERE / "protocol/protocol.py") == run["protocol_source_sha256"]
assert sha(HERE / "protocol/preregistration.json") == run["preregistration_sha256"]
assert sha(HERE / "quiet-window/window.json") == run["quiet_manifest_initial_sha256"] == run["quiet_manifest_final_sha256"]
assert sha(HERE / "review/statistics-review.json") == qualification["provenance"]["independent_statistics_review"]["sha256"]
sys.path.insert(0, str(HERE / "protocol"))
from protocol import parse_calibration, parse_measurements
groups = parse_measurements((HERE / "protocol/performance.csv").read_text(), parse_calibration((HERE / "protocol/performance.log").read_text()))
assert len(groups) == 14 and sum(len(x) * 2 for x in groups.values()) == 1148
analysis = read(HERE / "protocol/performance-analysis.json")
assert analysis["results"] == qualification["performance"]["results"]
print(json.dumps({"status": "passed", "payload_files": len(inventory), "source_archive_members": len(sources),
                  "cases": len(groups), "measurement_rows": 1148, "no_numerical_execution": True}))
